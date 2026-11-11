"""Scratch trace for the 48th-bar target cell (not a handoff)."""
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
        enable_liquidation_checks=True,
        liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5, gross_cap_pct=120.0,
        rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
    )


def _sig(shares=600.0):
    return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                  stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                  timestamp="t5", size_shares=shares, signal_index=5)


def _coin():
    n = 80
    coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
    coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)
    for i in range(9, n):
        coin[i] = _c(f"s{i}", 108.0, 115.0, 100.0, 107.0)
    # 48th held bar: sidx=55. low 99.0 -> target hit (target ~99.189)
    coin[55] = _c("b55", 108.0, 115.0, 99.0, 107.0)
    return coin


def _eth_aligned():
    n = 80
    eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
    eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
    eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)
    for i in range(9, n):
        eth[i] = _c(f"eh{i}", 2030.0, 2050.0, 2020.0, 2040.0)
    eth[55] = _c("eh55", 2030.0, 2055.0, 2020.0, 2045.0)
    return eth


def _eth_absent_at_exit():
    eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(10)]
    eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
    eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)
    return eth


def run(label, eth, funding):
    rs = DailyRiskState()
    res = backtest_simple(_coin(), _sig(600.0), config=_cfg(funding),
                          risk_state=rs, capital=100000.0, eth_candles=eth)
    print(f"--- {label} (funding={funding}) ---")
    print("exit_reason", res.exit_reason)
    print("exit_timestamp", res.exit_timestamp)
    print("bars_held", res.bars_held)
    for t in res.trades:
        print("leg", t)
    print("rebound_hedge_side", res.rebound_hedge_side)
    print("rebound_hedge_size", res.rebound_hedge_size)
    print("rebound_hedge_entry", res.rebound_hedge_entry)
    print("rebound_hedge_exit", res.rebound_hedge_exit)
    print("rebound_hedge_pnl", res.rebound_hedge_pnl)
    print("hedge_pnl", res.hedge_pnl)
    print("max_live_coin_notional", res.max_live_coin_notional)
    print("total_pnl", res.total_pnl)
    print("rs.realized_pnl", rs.realized_pnl)
    print("rs.open_positions", rs.open_positions)
    print("rs.gross_exposure", rs.gross_exposure)
    print("rs.open_position_notionals", rs.open_position_notionals)
    print()


if __name__ == "__main__":
    run("aligned-on", _eth_aligned(), 0.01)
    run("aligned-off", _eth_aligned(), 0.0)
    run("absent-on", _eth_absent_at_exit(), 0.01)
    run("absent-off", _eth_absent_at_exit(), 0.0)