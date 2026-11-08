"""Spec-fidelity regression (2026-11-08): the spec's PRIMARY crash trigger
(21-hour RSI closes below 20) must not be silently nullified by the non-spec
`avoid_downtrend` fast-MA filter.

Why this is a defect
--------------------
The PDF crash trigger is literally "coin's 21-hour RSI closes below 20 (last day
almost all selling)". A crash trigger therefore BY DEFINITION occurs during a
downtrend: price has been falling for ~a day. `regime_ok()` applies
`avoid_downtrend` (price must be above the fast MA) AFTER `detect_crash()` and
`confirm_rebound()`, so with the DEFAULT config (`avoid_downtrend=True`) combined
with the spec-primary trigger (`use_rsi_trigger=True`), `generate_signal` rejects
every legitimate RSI crash signal. The strategy fires nothing — a silent no-op.

The real-campaign wiring (`scripts/run_real_campaign.py`) constructs
`StrategyConfig(use_rsi_trigger=True, ...)` and inherits the default
`avoid_downtrend=True`, so the spec-compliant evidence path would produce zero
trades on real data. The `avoid_downtrend` / `ma_fast_period` fast-MA filter is an
implementation extra NOT present in crash-rebound-strategy.pdf; it is only
meaningful for the non-spec price-drop trigger (a single -2% bar can occur inside
an uptrend, where price is still above the fast MA). It must not gate the RSI
trigger, which already IS the downtrend confirmation.

Fix: when the crash was detected via the RSI trigger, the fast-MA downtrend
filter is skipped (RSI<20 is the downtrend signal per spec). `regime_min_price`
and the volume floor remain enforced in all paths.

Deterministic synthetic fixtures only; not market evidence; no look-ahead.
"""
from __future__ import annotations

from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import generate_signal, detect_crash_rsi


def _bar(i, o, c, v=10_000_000.0):
    hi = max(o, c) * 1.001
    lo = min(o, c) * 0.999
    return {"timestamp": f"t{i:02d}:00:00", "open": o, "high": hi, "low": lo,
            "close": c, "volume": v}


def _sustained_downtrend(n=60, start=100.0, step=0.985):
    """Strong sustained sell-off -> RSI(21) well below 20. Price ends far below
    any 20-bar SMA, so the non-spec fast-MA downtrend filter would reject it.
    A final bullish-rebound confirmation bar is appended so confirm_rebound()
    passes (spec requires RSI<20 crash THEN a rebound before buying)."""
    candles = []
    p = start
    for i in range(n):
        c = p * step
        candles.append(_bar(i, p, c))
        p = c
    # Rebound confirmation: close in the upper half of the bar's range, above open.
    candles.append(_bar(n, p, p * 1.03))
    return candles


def test_rsi_trigger_fires_on_sustained_downtrend():
    candles = _sustained_downtrend()
    assert detect_crash_rsi(candles) is True, "RSI(21)<20 must fire on a sustained sell-off"


def test_rsi_trigger_signal_not_killed_by_default_avoid_downtrend():
    """Spec primary trigger must produce a signal even with the DEFAULT config
    (avoid_downtrend=True), because RSI<20 already implies a downtrend."""
    candles = _sustained_downtrend()
    cfg = StrategyConfig(use_rsi_trigger=True, avoid_downtrend=True, min_daily_volume_usd=0.0)
    sig = generate_signal(candles, config=cfg)
    assert sig is not None, (
        "generate_signal rejected the spec-primary RSI crash signal because the non-spec "
        "fast-MA avoid_downtrend filter fired during the very downtrend the RSI trigger "
        "detected. The RSI trigger IS the downtrend confirmation per crash-rebound-strategy.pdf."
    )
    assert sig.side == "long"


def test_rsi_trigger_signal_fires_with_explicit_ma_filter_also_disabled():
    candles = _sustained_downtrend()
    cfg = StrategyConfig(use_rsi_trigger=True, avoid_downtrend=False, min_daily_volume_usd=0.0)
    assert generate_signal(candles, config=cfg) is not None


def test_drop_trigger_still_respects_avoid_downtrend_when_price_above_ma():
    """The non-spec drop trigger may still be gated by avoid_downtrend when the
    crash bar happens inside an uptrend (price above fast MA). This preserves the
    filter's intended use without nullifying the RSI trigger."""
    candles = []
    p = 100.0
    for i in range(40):
        c = p * 1.002  # slow uptrend, price above MA
        candles.append(_bar(i, p, c))
        p = c
    # Crash bar: -2% drop from open, but price still above the 20-bar MA.
    candles.append(_bar(40, p, p * 0.978))
    cfg = StrategyConfig(use_rsi_trigger=False, avoid_downtrend=True,
                        crash_pct_drop=-2.0, crash_lookback=5, min_daily_volume_usd=0.0)
    sig = generate_signal(candles, config=cfg)
    assert sig is None, (
        "drop-trigger crash inside an uptrend must still be gated by the non-spec "
        "avoid_downtrend fast-MA filter (price above MA => no knife-catching)"
    )


def test_regime_min_price_still_enforced_on_rsi_path():
    """regime_min_price is a legitimate floor and must still apply to the RSI path."""
    candles = _sustained_downtrend()
    # Force closes below the price floor by scaling the whole series down.
    for c in candles:
        c["close"] *= 0.01
        c["open"] *= 0.01
        c["high"] *= 0.01
        c["low"] *= 0.01
    cfg = StrategyConfig(use_rsi_trigger=True, avoid_downtrend=True,
                        regime_min_price=5.0, min_daily_volume_usd=0.0)
    assert generate_signal(candles, config=cfg) is None, (
        "regime_min_price must still reject the RSI path when price is below the floor"
    )