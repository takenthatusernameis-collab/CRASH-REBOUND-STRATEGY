"""Regression locks (2026-11-08): engine-level 8x spec safety stop semantics and
ETH hedge vol-ratio/336h/cap behavior.

Spec (crash-rebound-strategy.pdf / strategy_spec.md):
- Safety stop (buy): 8x usual hourly range below entry, where hourly range =
  avg (high-low)/prev_close over last 14 hours. Median ~15% below entry.
- ETH hedge every leg: coin_vol/eth_vol over 336h lookback, capped at 3x position.
- Stopped buy never opens rebound short.
- Hourly engine only; synthetic fixtures only; not performance evidence.

Failing-tests-first intent: these lock currently-correct engine behavior against
regression. If a spec defect is found later, replace/extend with a failing test
that demonstrates it.
"""
from __future__ import annotations

import copy
import math

from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal, compute_eth_hedge_size, generate_signal
from src.strategy.risk import usual_hourly_range_ratio


def _c(ts, o, h, l, cl, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": cl, "volume": v}


def _cfg(**kw):
    d = dict(
        use_rsi_trigger=False,
        min_daily_volume_usd=0.0,
        enable_eth_hedge=True,
        enable_rebound_short=True,
        enable_liquidation_checks=False,
        entry_next_bar=True,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
        funding_rate_pct_per_hour=0.0,
        use_spec_safety_stop=True,
        stop_atr_mult=8.0,
        atr_period=14,
        hedge_vol_lookback_hours=336,
        hedge_cap_multiplier=3.0,
        avoid_downtrend=False,
    )
    d.update(kw)
    return StrategyConfig(**d)


def _signal(entry=100.0, stop=None, target=109.0, size=1.0, idx=20):
    if stop is None:
        stop = 84.0
    return Signal(
        symbol="T", side="long", reason="t", entry_price=entry, stop_price=stop,
        target_price=target, risk_per_share=entry - stop, timestamp=f"t{idx:03d}",
        size_shares=size, signal_index=idx,
    )


def _range_candles(n, base=100.0, ratio=0.02, start=0):
    out = []
    px = base
    for i in range(n):
        o = px
        h = o * (1.0 + ratio / 2.0)
        l = o * (1.0 - ratio / 2.0)
        c = o
        out.append(_c(f"t{start+i:04d}", o, h, l, c))
        px = c
    return out


def test_engine_entry_next_bar_reanchors_spec_safety_stop_by_ratio():
    """Engine-level lock: entry_next_bar re-anchors spec safety stop using ratio
    semantics (stop * entry_px/entry), preserving 8x range distance relative to the
    executed entry."""
    candles = _range_candles(40, base=100.0, ratio=0.02)
    # Decision at 20; next bar opens at 102 (gap up). Stop should scale with fill.
    candles[21] = _c("t0021", 102.0, 103.0, 101.0, 102.0)
    candles[22] = _c("t0022", 102.0, 103.0, 70.0, 80.0)  # breach scaled stop
    eth = _range_candles(40, base=2000.0, ratio=0.01)
    cfg = _cfg(entry_next_bar=True, enable_eth_hedge=False, enable_rebound_short=True)
    sig = _signal(entry=100.0, stop=84.0, target=109.0, idx=20)
    res = backtest_simple(candles, sig, config=cfg, eth_candles=eth)
    # Ratio scaling: 84 * 102/100 = 85.68, so low 70 breaches.
    assert res.exit_reason == "stopped", res.exit_reason
    assert not any(t.get("side") == "short" for t in (res.trades or [])), (
        "stopped buy must never open rebound short"
    )
    # Executed entry is next open (102) with no slippage/commission.
    assert abs(res.entry_price - 102.0) < 1e-9, res.entry_price


def test_engine_entry_next_bar_target_reanchor_ratio_semantics():
    """Engine-level lock: entry_next_bar re-anchors target by ratio so +9% target
    remains relative to executed entry."""
    candles = _range_candles(40, base=100.0, ratio=0.01)
    candles[21] = _c("t0021", 102.0, 103.0, 101.0, 102.0)  # fill
    candles[22] = _c("t0022", 102.0, 112.0, 101.0, 111.0)  # must hit scaled target
    cfg = _cfg(entry_next_bar=True, enable_eth_hedge=False, enable_rebound_short=False)
    # Signal target 109 from 100; scaled to 111.18 from 102.
    sig = _signal(entry=100.0, stop=84.0, target=109.0, idx=20)
    res = backtest_simple(candles, sig, config=cfg)
    assert res.exit_reason == "target", (res.exit_reason, res.exit_price, res.entry_price)
    assert abs(res.entry_price - 102.0) < 1e-9
    assert abs(res.exit_price - 111.18) < 1e-9, res.exit_price


def test_generate_signal_exercises_engine_8x_stop_via_spec_path():
    """End-to-end signal->engine lock: spec safety stop from generate_signal is
    exercised by engine and a stopped buy never opens rebound short."""
    candles = _range_candles(40, base=100.0, ratio=0.01)
    # Ensure volume passes spec floor if enforced in this path; config disables it.
    for c in candles:
        c["volume"] = 10_000_000.0
    # Make a deterministic crash + rebound trigger for drop mode.
    candles[-3] = {**candles[-3], "open": 100.0, "close": 97.0, "high": 100.2, "low": 96.8, "volume": 20_000_000.0}
    candles[-2] = {**candles[-2], "open": 97.2, "close": 97.5, "high": 97.6, "low": 97.1, "volume": 20_000_000.0}
    candles[-1] = {**candles[-1], "open": 97.6, "close": 98.8, "high": 98.9, "low": 97.5, "volume": 20_000_000.0}
    cfg = _cfg(
        entry_next_bar=False, use_rsi_trigger=False, min_daily_volume_usd=0.0,
        avoid_downtrend=False, enable_liquidation_checks=False,
        enable_rebound_short=True, volume_spike_mult=1.0, crash_pct_drop=-2.0,
    )
    sig = generate_signal(candles, config=cfg)
    assert sig is not None, "expected crash+rebound signal"
    r = usual_hourly_range_ratio(candles, period=14)
    assert r is not None and r > 0
    expected_stop = sig.entry_price * (1.0 - 8.0 * r)
    assert abs(sig.stop_price - expected_stop) < 1e-6, (sig.stop_price, expected_stop)
    # Execute with the signal and force stop breach on next bar.
    exec_candles = copy.deepcopy(candles)
    breach = {**exec_candles[-1], "timestamp": "t_breach", "open": sig.entry_price, "high": sig.entry_price,
              "low": sig.stop_price - 1.0, "close": sig.stop_price - 0.5}
    exec_candles.append(breach)
    res = backtest_simple(exec_candles, sig, config=cfg)
    assert res.exit_reason == "stopped", res.exit_reason
    assert not any(t.get("side") == "short" for t in (res.trades or [])), (
        "stopped buy must never open rebound short"
    )


def _vol_series(n, base, sigma, seed=1):
    # Deterministic pseudo-random walk with fixed sigma to create target realized vol.
    import random
    rng = random.Random(seed)
    out = []
    px = base
    for i in range(n):
        # lognormal-ish step scaled to approximate sigma
        step = rng.gauss(0.0, sigma)
        px = max(0.01, px * (1.0 + step))
        o = px
        h = px * 1.001
        l = px * 0.999
        out.append(_c(f"v{i:04d}", o, h, l, px))
    return out


def test_compute_eth_hedge_size_uses_336h_lookback_and_3x_cap():
    """Regression lock: hedge sizing uses 336h realized-vol lookback and caps at 3x."""
    coin = _vol_series(380, base=100.0, sigma=0.02, seed=11)
    eth = _vol_series(380, base=2000.0, sigma=0.005, seed=13)  # lower vol -> large ratio
    cfg = _cfg(hedge_vol_lookback_hours=336, hedge_cap_multiplier=3.0)
    pos = 10000.0
    h = compute_eth_hedge_size(coin, eth, pos, config=cfg)
    assert 0.0 <= h <= pos * 3.0 + 1e-9
    # With ETH vol much lower than coin vol, ratio should hit the 3x cap.
    assert abs(h - pos * 3.0) < 1e-6, h


def test_compute_eth_hedge_size_vol_ratio_respects_lookback_window():
    """Regression lock: changing early history outside the 336h lookback must not
    change the hedge size (lookback-bounded realized vol)."""
    coin = _vol_series(400, base=100.0, sigma=0.01, seed=21)
    eth = _vol_series(400, base=2000.0, sigma=0.01, seed=22)
    cfg = _cfg(hedge_vol_lookback_hours=336, hedge_cap_multiplier=3.0)
    pos = 10000.0
    base_h = compute_eth_hedge_size(coin, eth, pos, config=cfg)
    coin2 = copy.deepcopy(coin)
    # Mutate bars far before the 336h window; last 337 bars used for returns.
    for c in coin2[:40]:
        c["open"] *= 5.0
        c["high"] *= 5.0
        c["low"] *= 0.2
        c["close"] *= 5.0
    h2 = compute_eth_hedge_size(coin2, eth, pos, config=cfg)
    assert abs(base_h - h2) < 1e-9, (base_h, h2)
