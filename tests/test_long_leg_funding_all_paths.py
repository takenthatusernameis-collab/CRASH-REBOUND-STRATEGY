"""Deterministic regression: hourly funding must be applied on the LONG coin leg for
ALL exit paths, including the time-exit path (engine.py:538-574).

Spec (crash-rebound-strategy.pdf): "hourly funding on every leg". Prior coverage
verified funding on liquidation/stop/target/rebound-short paths; the long-leg
time-exit path (no target/stop hit, held to time_exit_max_bars) and the final-exit
fallback were missing the coin-leg funding application. Synthetic fixtures only;
not performance evidence; no real market data; no look-ahead.
"""
import pytest
from src.strategy.config import StrategyConfig
from src.backtest.engine import backtest_simple
from src.strategy.crash_rebound import Signal

ENTRY_PX = 100.0
SHARES = 1.0
SIGNAL_IDX = 5
RATE = 0.01  # 0.01% per hour


def _candle(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _flat_series(n, start_ts="2025-01-01T00:00:00"):
    out = []
    for i in range(n):
        out.append(_candle(f"2025-01-01T{i % 24:02d}:00:00", 100.0, 101.0, 99.0, 100.0))
    return out


def _signal():
    return Signal(
        symbol="TEST", side="long", reason="t",
        entry_price=ENTRY_PX, stop_price=ENTRY_PX * 0.5, target_price=ENTRY_PX * 1.09,
        risk_per_share=1.0, timestamp="2025-01-01T05:00:00", size_shares=SHARES,
        signal_index=SIGNAL_IDX,
    )


def _base_cfg(**kw):
    base = dict(
        enable_eth_hedge=False,
        enable_rebound_short=False,
        entry_next_bar=False,
        avoid_downtrend=False,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
        funding_rate_pct_per_hour=RATE,
        time_exit_max_bars=50,
        min_daily_volume_usd=0.0,
    )
    base.update(kw)
    return StrategyConfig(**base)


def _run(candles, cfg):
    return backtest_simple(candles, _signal(), config=cfg, capital=100000)


def test_long_leg_funding_applied_on_time_exit():
    """Long held to time_exit_max_bars: coin-leg funding must reduce PnL."""
    candles = _flat_series(60)  # idx 5 signal, entry at 5, time exit at idx 54 (50 bars held)
    res_on = _run(candles, _base_cfg(funding_rate_pct_per_hour=RATE))
    res_off = _run(candles, _base_cfg(funding_rate_pct_per_hour=0.0))
    held_hours = 50  # time_exit_max_bars=50 => idx 54 - start_idx 5 + 1 = 50
    expected_cost = ENTRY_PX * SHARES * held_hours * (RATE / 100.0)
    delta = (res_on.total_pnl or 0.0) - (res_off.total_pnl or 0.0)
    assert abs(delta - (-expected_cost)) < 1e-9, (
        f"time_exit: funding delta {delta} != expected {-expected_cost}; "
        "long-coin-leg funding may be missing on the time-exit path"
    )
    assert res_on.exit_reason == "time_exit"


def test_long_leg_funding_applied_on_final_exit():
    """Long held to end of series (no exit triggered): coin-leg funding must reduce PnL."""
    candles = _flat_series(20)
    res_on = _run(candles, _base_cfg(funding_rate_pct_per_hour=RATE, time_exit_max_bars=1000))
    res_off = _run(candles, _base_cfg(funding_rate_pct_per_hour=0.0, time_exit_max_bars=1000))
    held_hours = len(candles) - SIGNAL_IDX  # engine uses len(candles)-start_idx
    expected_cost = ENTRY_PX * SHARES * held_hours * (RATE / 100.0)
    delta = (res_on.total_pnl or 0.0) - (res_off.total_pnl or 0.0)
    assert abs(delta - (-expected_cost)) < 1e-9, (
        f"final_exit: funding delta {delta} != expected {-expected_cost}; "
        "long-coin-leg funding may be missing on the final-exit path"
    )


def test_long_leg_funding_scales_linearly_on_time_exit():
    """Funding delta scales linearly with rate on the time-exit path."""
    candles = _flat_series(60)
    def run(rate):
        return _run(candles, _base_cfg(funding_rate_pct_per_hour=rate)).total_pnl or 0.0
    d1 = run(0.01) - run(0.0)
    d2 = run(0.02) - run(0.0)
    assert abs(d2 - 2 * d1) < 1e-9, "funding delta should scale linearly with rate"
    assert d1 != 0.0, "funding must have a nonzero effect on the time-exit path"


def test_long_leg_funding_present_on_stop_path():
    """Stop path already applies coin funding; verify it still does (regression guard)."""
    # stop_px=50 triggers before liquidation threshold (94), so disable liquidation
    # checks to exercise the long-leg stop path cleanly.
    candles = _flat_series(10)
    candles[6] = _candle("2025-01-01T06:00:00", 100.0, 101.0, 49.0, 100.0)  # stop hit
    res_on = _run(candles, _base_cfg(funding_rate_pct_per_hour=RATE, enable_liquidation_checks=False))
    res_off = _run(candles, _base_cfg(funding_rate_pct_per_hour=0.0, enable_liquidation_checks=False))
    held_hours = 6 - SIGNAL_IDX + 1  # 2
    expected_cost = ENTRY_PX * SHARES * held_hours * (RATE / 100.0)
    delta = (res_on.total_pnl or 0.0) - (res_off.total_pnl or 0.0)
    assert abs(delta - (-expected_cost)) < 1e-9
    assert res_on.exit_reason == "stopped"