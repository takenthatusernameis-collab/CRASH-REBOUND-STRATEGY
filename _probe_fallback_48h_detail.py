"""Detailed trace of the genuine fallback path for the in-loop 48h TIME_EXIT
rebound-short cell. ETH series truncated so sidx (55) >= len(eth_candles) at the
48h break -> engine falls back to rebound_hedge_info['entry'] raw for the hedge
close, then applies sell-side slippage/commission_min. Prints every leg so the
next session can hand-verify expected values before shipping the regression lock.
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


def _candles(n=120, eth_len=55):
    coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
    coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)
    for i in range(9, n):
        coin[i] = _c(f"s{i}", 108.0, 115.0, 100.0, 107.0)
    eth = [_c(f"e{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(eth_len)]
    eth[6] = _c("e6", 2000.0, 2010.0, 1990.0, 2000.0)
    eth[8] = _c("e8", 2000.0, 2030.0, 1995.0, 2025.0)
    for i in range(9, eth_len):
        eth[i] = _c(f"eh{i}", 2030.0, 2050.0, 2020.0, 2040.0)
    return coin, eth


def run(funding, label):
    coin, eth = _candles(eth_len=55)
    cfg = _cfg(funding)
    rs = DailyRiskState()
    res = backtest_simple(coin, _sig(600.0), config=cfg,
                          risk_state=rs, capital=100000.0, eth_candles=eth)
    print(f"=== {label} funding={funding} ===")
    for i, t in enumerate(res.trades):
        print(f"  trade[{i}] side={t['side']} entry={t['entry']} exit={t['exit']} pnl={t['pnl']} reason={t['reason']}")
    print(f"  hedge_side={res.hedge_side} hedge_size={res.hedge_size} hedge_entry={res.hedge_entry} hedge_exit={res.hedge_exit} hedge_pnl={res.hedge_pnl}")
    print(f"  rebound_hedge_side={res.rebound_hedge_side} size={res.rebound_hedge_size} entry={res.rebound_hedge_entry} exit={res.rebound_hedge_exit} pnl={res.rebound_hedge_pnl}")
    print(f"  total_pnl={res.total_pnl} max_live={res.max_live_coin_notional}")
    print(f"  rs.realized_pnl={rs.realized_pnl} open={rs.open_positions} gross={rs.gross_exposure} notionals={rs.open_position_notionals}")
    return res


if __name__ == "__main__":
    on = run(0.01, "FUNDING-ON")
    off = run(0.0, "FUNDING-OFF")
    print()
    print(f"total_pnl delta (on-off) = {on.total_pnl - off.total_pnl}")
    print(f"realized_pnl delta (on-off) = {on.realized_pnl - off.realized_pnl}")
    print(f"rebound_hedge_pnl delta (on-off) = {on.rebound_hedge_pnl - off.rebound_hedge_pnl}")