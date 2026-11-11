"""Probe (2026-11-11): rebound-short LIQUIDATION where the ETH bar is ENTIRELY
ABSENT at the exit index (eth_candles shorter than coin candles at that index),
distinct from existing 'bar present but close/open absent' fallback locks.

Goal: determine the CURRENT engine behavior so we can write a failing-tests-first
regression lock with hand-traced expected values, OR prove the cell is already
covered by concrete evidence.
"""
from __future__ import annotations

from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _cfg():
    return StrategyConfig(
        enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=1.0, funding_rate_pct_per_hour=0.01,
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


def build():
    n = 30
    coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)   # long entry_next_bar fill
    coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)   # long target -> rebound short opens
    coin[9] = _c("b9", 110.0, 115.0, 109.0, 110.0)  # below liq threshold
    coin[10] = _c("e10", 110.0, 116.0, 109.0, 115.0)  # rebound short liquidation (high)
    # ETH: present through idx 9, then ABSENT at idx 10 (shorter than coin candles).
    eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(10)]  # indices 0..9
    return coin, eth


def main():
    coin, eth = build()
    res = backtest_simple(coin, _sig(600.0), config=_cfg(),
                          risk_state=None, capital=100000.0, eth_candles=eth)
    print("exit_reason:", res.exit_reason)
    print("trades:", res.trades)
    print("rebound_hedge_side:", res.rebound_hedge_side)
    print("rebound_hedge_size:", res.rebound_hedge_size)
    print("rebound_hedge_entry:", res.rebound_hedge_entry)
    print("rebound_hedge_exit:", res.rebound_hedge_exit)
    print("rebound_hedge_pnl:", res.rebound_hedge_pnl)
    print("hedge_pnl:", res.hedge_pnl)
    print("max_live_coin_notional:", res.max_live_coin_notional)
    print("total_pnl:", res.total_pnl)
    print("exit_timestamp:", res.exit_timestamp)
    print("bars_held:", res.bars_held)

    # Compare with the existing lock fixture (bar present but close/open absent)
    eth2 = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(11)]
    eth2[10] = {"timestamp": "h10"}  # present but close/open absent -> fallback
    res2 = backtest_simple(coin, _sig(600.0), config=_cfg(),
                           risk_state=None, capital=100000.0, eth_candles=eth2)
    print("\n--- compare: bar present but close/open absent ---")
    print("rebound_hedge_exit:", res2.rebound_hedge_exit)
    print("rebound_hedge_pnl:", res2.rebound_hedge_pnl)
    print("total_pnl:", res2.total_pnl)
    print("SAME exit as entirely-absent?", res.rebound_hedge_exit == res2.rebound_hedge_exit)


if __name__ == "__main__":
    main()