"""Spec-fidelity regression (2026-11-08): `passes_universe_filter` / `filter_universe`
must not silently reject every RSI-trigger crash coin.

Why this is a defect
--------------------
`generate_signal` skips the non-spec `avoid_downtrend` fast-MA filter when the crash
was detected via the spec-primary RSI trigger (RSI<20 IS the downtrend confirmation
per crash-rebound-strategy.pdf). But `passes_universe_filter` and `filter_universe`
call `regime_ok(candles, regime_config)` with no `skip_downtrend_filter`, so any
regime_config built with the default `avoid_downtrend=True` rejects every RSI-trigger
coin at the universe-gating boundary. That boundary is on the spec-compliant path:
`src/data/loader.py:347-351` filters via `filter_universe(..., regime_config=DEFAULT_CONFIG)`
and DEFAULT_CONFIG has `use_rsi_trigger=True, avoid_downtrend=True`. A coin whose
RSI(21)<20 crash was detected would therefore be dropped from the universe before
`generate_signal` ever sees it — the same silent no-op the RSI fix removed from
generate_signal, just one layer down.

Fix: `passes_universe_filter`/`filter_universe` must honor `skip_downtrend_filter`
when the caller's regime_config uses the spec-primary RSI trigger (the RSI trigger
already IS the downtrend confirmation). `regime_min_price` and the volume floor
remain enforced in all paths.

Deterministic synthetic fixtures only; not market evidence; no look-ahead.
"""
from __future__ import annotations

from src.strategy.config import StrategyConfig, DEFAULT_CONFIG
from src.strategy.crash_rebound import (
    passes_universe_filter,
    filter_universe,
    detect_crash_rsi,
    generate_signal,
)


def _bar(i, o, c, v=10_000_000.0):
    hi = max(o, c) * 1.001
    lo = min(o, c) * 0.999
    return {"timestamp": f"t{i:02d}:00:00", "open": o, "high": hi, "low": lo,
            "close": c, "volume": v}


def _sustained_downtrend(n=60, start=100.0, step=0.985):
    """Strong sustained sell-off -> RSI(21) well below 20. Final bar is a bullish
    rebound confirmation so confirm_rebound() passes (spec: RSI<20 crash THEN a
    rebound before buying)."""
    candles = []
    p = start
    for i in range(n):
        c = p * step
        candles.append(_bar(i, p, c))
        p = c
    candles.append(_bar(n, p, p * 1.03))
    return candles


def test_rsi_crash_coin_passes_universe_filter_with_default_config():
    """A coin whose 21h RSI closed below 20 must pass the universe filter under the
    DEFAULT config (use_rsi_trigger=True, avoid_downtrend=True), because the RSI
    trigger IS the downtrend confirmation per spec."""
    candles = _sustained_downtrend()
    assert detect_crash_rsi(candles) is True
    assert passes_universe_filter(candles, min_daily_volume_usd=0.0,
                                  regime_config=DEFAULT_CONFIG) is True


def test_rsi_crash_coin_passes_universe_filter_with_explicit_rsi_config():
    candles = _sustained_downtrend()
    cfg = StrategyConfig(use_rsi_trigger=True, avoid_downtrend=True,
                        min_daily_volume_usd=0.0)
    assert passes_universe_filter(candles, min_daily_volume_usd=0.0,
                                  regime_config=cfg) is True


def test_filter_universe_keeps_rsi_crash_coin_with_default_config():
    candles = _sustained_downtrend()
    out = filter_universe({"RSI_COIN": candles}, min_daily_volume_usd=0.0,
                          regime_config=DEFAULT_CONFIG)
    assert "RSI_COIN" in out, (
        "filter_universe dropped an RSI-trigger crash coin under the default config; "
        "the spec-primary RSI trigger IS the downtrend confirmation and must not be "
        "nullified by the non-spec avoid_downtrend fast-MA filter at the universe "
        "gating boundary"
    )


def test_rsi_crash_coin_passes_filter_then_produces_signal():
    """End-to-end: a coin that passes the universe filter under the RSI config must
    then actually produce a long signal from generate_signal."""
    candles = _sustained_downtrend()
    cfg = StrategyConfig(use_rsi_trigger=True, avoid_downtrend=True,
                        min_daily_volume_usd=0.0)
    assert passes_universe_filter(candles, min_daily_volume_usd=0.0,
                                  regime_config=cfg) is True
    sig = generate_signal(candles, config=cfg)
    assert sig is not None and sig.side == "long"


def test_regime_min_price_still_enforced_on_rsi_path_in_universe_filter():
    """regime_min_price is a legitimate floor and must still apply to the RSI path
    at the universe-filter boundary."""
    candles = _sustained_downtrend()
    for c in candles:
        c["close"] *= 0.01
        c["open"] *= 0.01
        c["high"] *= 0.01
        c["low"] *= 0.01
    cfg = StrategyConfig(use_rsi_trigger=True, avoid_downtrend=True,
                        regime_min_price=5.0, min_daily_volume_usd=0.0)
    assert passes_universe_filter(candles, min_daily_volume_usd=0.0,
                                  regime_config=cfg) is False


def test_drop_trigger_coin_still_gated_by_avoid_downtrend_in_universe_filter():
    """The non-spec drop trigger may still be gated by avoid_downtrend when the
    crash bar happens inside an uptrend (price above fast MA)."""
    candles = []
    p = 100.0
    for i in range(40):
        c = p * 1.002  # slow uptrend, price above MA
        candles.append(_bar(i, p, c))
        p = c
    # Crash bar: -2% drop from open, but price still above the 20-bar MA.
    candles.append(_bar(40, p, p * 0.978))
    cfg = StrategyConfig(use_rsi_trigger=False, avoid_downtrend=True,
                        crash_pct_drop=-2.0, crash_lookback=5,
                        min_daily_volume_usd=0.0)
    assert passes_universe_filter(candles, min_daily_volume_usd=0.0,
                                  regime_config=cfg) is False