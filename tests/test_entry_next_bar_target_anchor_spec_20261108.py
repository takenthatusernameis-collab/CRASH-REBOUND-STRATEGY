"""Spec-fidelity regression (2026-11-08): target/stop must anchor to the ACTUAL
executed entry price, not the signal-bar close, when entry_next_bar=True.

Per crash-rebound-strategy.pdf / strategy_spec.md: the buy target is +9% and the
safety stop is 8x usual hourly range below entry. Those thresholds are relative to
the price at which the position is actually filled. When entry_next_bar=True the
engine fills at the next bar's open, which can differ from the signal-bar close.
Anchoring stop/target to the signal-bar close while executing at a different price
is a look-ahead-adjacent spec violation (the thresholds no longer describe the
executed trade's risk/reward).

Deterministic synthetic fixtures only; not market evidence; no look-ahead.
"""
from __future__ import annotations

from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.backtest.engine import backtest_simple


def _candle(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _base_cfg(**kw):
    base = dict(
        enable_eth_hedge=False,
        enable_rebound_short=False,
        entry_next_bar=True,
        avoid_downtrend=False,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
        funding_rate_pct_per_hour=0.0,
        time_exit_max_bars=1000,
        min_daily_volume_usd=0.0,
        enable_liquidation_checks=False,
        use_spec_safety_stop=True,   # spec ratio semantics: stop = entry*(1-8*range_ratio)
        stop_atr_mult=8.0,
        atr_period=14,
    )
    base.update(kw)
    return StrategyConfig(**base)


def test_target_anchors_to_executed_entry_when_next_bar_open_differs():
    # Signal fires at bar 5 (close 100, target 109). entry_next_bar=True => fill at
    # bar 6 open 110. Spec target +9% must apply to the executed entry 110 -> 119.9,
    # NOT to the signal close 100 -> 109.
    candles = [_candle(f"2025-01-01T{i:02d}:00:00", 100.0, 101.0, 99.0, 100.0) for i in range(6)]
    # Bar 6 open gaps up to 110; high reaches 120 so the +9%-from-executed target
    # (119.9) is touched but the +9%-from-signal-close target (109) is not.
    candles.append(_candle("2025-01-01T06:00:00", 110.0, 120.0, 109.0, 115.0))
    sig = Signal(symbol="T", side="long", reason="t", entry_price=100.0, stop_price=50.0,
                 target_price=109.0, risk_per_share=50.0, timestamp="2025-01-01T05:00:00",
                 size_shares=1.0, signal_index=5)
    res = backtest_simple(candles, sig, config=_base_cfg())
    assert res.exit_reason == "target", res.exit_reason
    # Executed entry is the next-bar open (110); +9% target => 119.9
    assert abs(res.entry_price - 110.0) < 1e-9, res.entry_price
    assert abs(res.exit_price - 119.9) < 1e-6, res.exit_price


def test_stop_anchors_to_executed_entry_when_next_bar_open_differs():
    # Signal fires at bar 5 (close 100, stop 84). entry_next_bar=True => fill at
    # bar 6 open 90. Spec safety stop is 8x usual hourly range below the executed
    # entry 90, not below the signal close 100.
    candles = [_candle(f"2025-01-01T{i:02d}:00:00", 100.0, 101.0, 99.0, 100.0) for i in range(6)]
    # Bar 6 open gaps down to 90; low reaches 70 so the executed-entry stop
    # (90*(1-8*0.02)=75.6) is touched but the signal-close stop (84) is not.
    candles.append(_candle("2025-01-01T06:00:00", 90.0, 95.0, 70.0, 92.0))
    sig = Signal(symbol="T", side="long", reason="t", entry_price=100.0, stop_price=84.0,
                 target_price=200.0, risk_per_share=16.0, timestamp="2025-01-01T05:00:00",
                 size_shares=1.0, signal_index=5)
    res = backtest_simple(candles, sig, config=_base_cfg())
    assert res.exit_reason == "stopped", res.exit_reason
    assert abs(res.entry_price - 90.0) < 1e-9, res.entry_price
    # stop anchored to executed entry: 90 * (1 - 8*0.02) = 75.6 (range ratio 0.02)
    assert abs(res.exit_price - 75.6) < 1e-6, res.exit_price