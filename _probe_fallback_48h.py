"""Probe (2026-11-11): does the shipped truncated-ETH 48h lock actually exercise
the fallback-to-rebound_hedge_info['entry'] raw path, or is it a duplicate of the
aligned lock?

The in-loop 48h break fires when (sidx - short_start_idx + 1) >= 48.
short_start_idx == 8 (rebound short opens at coin idx 8). So the break fires at
sidx == 55 (55 - 8 + 1 == 48). The shipped truncated lock uses len(eth) == 56, so
sidx 55 is IN RANGE -> the engine reads eth_candles[55] (close 2040.0), NOT the
fallback. The fallback path (eth_exit_r = rebound_hedge_info['entry']) only
triggers when sidx >= len(eth_candles), i.e. len(eth) <= 55.

This probe confirms that and captures the distinct fallback outcome so the next
session can ship a genuine fallback lock.
"""
from __future__ import annotations

from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.strategy.risk import DailyRiskState


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _cfg(funding_rate_pct_per_hour=0.01):
    return StrategyConfig(
        enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=1.0, funding_rate_pct_per_hour=funding_rate_pct_per_hour,
        min_daily_volume_usd=0.0, time_exit_max_bars=200,
        enable_liquidation_checks=False,
        liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5, gross_cap_pct=120.0,
        rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
    )


def _sig(shares=600.0):
    return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                  stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                  timestamp="t5", size_shares=shares, signal_index=5)


def _candles(n=120, eth_len=None):
    coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
    coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)
    for i in range(9, n):
        coin[i] = _c(f"s{i}", 108.0, 115.0, 100.0, 107.0)
    if eth_len is None:
        eth_len = n
    eth = [_c(f"e{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(eth_len)]
    eth[6] = _c("e6", 2000.0, 2010.0, 1990.0, 2000.0)
    eth[8] = _c("e8", 2000.0, 2030.0, 1995.0, 2025.0)
    for i in range(9, eth_len):
        eth[i] = _c(f"eh{i}", 2030.0, 2050.0, 2020.0, 2040.0)
    return coin, eth


def run(eth_len, label):
    coin, eth = _candles(eth_len=eth_len)
    cfg = _cfg(0.01)
    rs = DailyRiskState()
    res = backtest_simple(coin, _sig(600.0), config=cfg,
                          risk_state=rs, capital=100000.0, eth_candles=eth)
    print(f"=== {label}: len(eth)={len(eth)} ===")
    print(f"  exit_reason={res.exit_reason} exit_ts={res.exit_timestamp} bars_held={res.bars_held}")
    print(f"  short exit={res.trades[-1]['exit'] if res.trades else None} reason={res.trades[-1]['reason'] if res.trades else None}")
    print(f"  rebound_hedge_entry={res.rebound_hedge_entry} rebound_hedge_exit={res.rebound_hedge_exit}")
    print(f"  rebound_hedge_pnl={res.rebound_hedge_pnl}")
    print(f"  total_pnl={res.total_pnl} max_live={res.max_live_coin_notional}")
    print(f"  rs.realized_pnl={rs.realized_pnl} open={rs.open_positions} gross={rs.gross_exposure}")
    return res


if __name__ == "__main__":
    # Shipped truncated lock: len 56 -> sidx 55 in range -> aligned bar (NOT fallback)
    run(56, "shipped-truncated-lock len56")
    # Genuinely truncated: len 55 -> sidx 55 == len -> fallback to entry
    run(55, "genuine-fallback len55")
    # Even shorter
    run(40, "genuine-fallback len40")
    # Aligned lock baseline
    run(120, "aligned-lock len120")