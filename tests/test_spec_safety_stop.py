"""Spec-fidelity tests: buy safety stop = 8x usual hourly range below entry.
Spec (crash-rebound-strategy.pdf / strategy_spec.md): "hourly range = avg distance
high-low/prev close over last 14 hours". Stop fires at entry - 8 * entry * avg_range_ratio.
Median ~15% below entry on Hyperliquid. Stopped buy never opens rebound short.
"""
from src.strategy.config import StrategyConfig
from src.strategy.risk import usual_hourly_range_ratio, safety_stop_price
from src.strategy.crash_rebound import generate_signal, Signal
from src.backtest.engine import backtest_simple


def _candles_with_range(n, base=100.0, range_ratio=0.02):
    """Synthetic candles with stable (high-low)/prev_close ~= range_ratio."""
    candles = []
    prev_close = base
    for i in range(n):
        o = prev_close
        h = o * (1.0 + range_ratio / 2.0)
        l = o * (1.0 - range_ratio / 2.0)
        c = o
        candles.append({
            "timestamp": f"2026-01-01T{i:02d}:00:00Z",
            "open": o, "high": h, "low": l, "close": c, "volume": 1_000_000.0,
        })
        prev_close = c
    return candles


def test_usual_hourly_range_ratio_matches_spec_formula():
    # (high-low)/prev_close = 0.02 for each bar
    candles = _candles_with_range(20, base=100.0, range_ratio=0.02)
    r = usual_hourly_range_ratio(candles, period=14)
    assert r is not None
    assert abs(r - 0.02) < 1e-9


def test_safety_stop_price_uses_8x_range_ratio_below_entry():
    # avg ratio 0.02, mult 8 => 16% below entry
    entry = 100.0
    stop = safety_stop_price(entry, avg_range_ratio=0.02, mult=8.0, side='long')
    assert abs(stop - 84.0) < 1e-9  # 100 * (1 - 0.16)


def test_safety_stop_price_short_above_entry():
    entry = 100.0
    stop = safety_stop_price(entry, avg_range_ratio=0.02, mult=8.0, side='short')
    assert abs(stop - 116.0) < 1e-9


def test_generate_signal_stop_matches_spec_8x_range():
    # Deterministic drop-trigger crash+rebound with spec safety stop.
    candles = _candles_with_range(32, base=100.0, range_ratio=0.01)
    for c in candles[-24:]:
        c["volume"] = 200_000.0
    # Crash bar (index -3): >=2% drop from open
    candles[-3] = {**candles[-3], "open": 100.0, "close": 97.0, "high": 100.2, "low": 96.8, "volume": 300_000.0}
    # Rebound confirmation bar is the LAST candle scanned by confirm_rebound
    candles[-2] = {**candles[-2], "open": 97.2, "close": 97.5, "high": 97.6, "low": 97.1, "volume": 250_000.0}
    candles[-1] = {**candles[-1], "open": 97.6, "close": 98.8, "high": 98.9, "low": 97.5, "volume": 250_000.0}
    config = StrategyConfig(
        use_rsi_trigger=False, avoid_downtrend=False, entry_next_bar=False,
        enable_liquidation_checks=False, stop_atr_mult=8.0, atr_period=14,
        use_spec_safety_stop=True, min_daily_volume_usd=5_000_000.0,
        volume_spike_mult=1.0, crash_pct_drop=-2.0,
    )
    sig = generate_signal(candles, config=config)
    assert sig is not None, "expected signal from deterministic crash+rebound fixture"
    r = usual_hourly_range_ratio(candles, period=14)
    assert r is not None and r > 0
    expected = sig.entry_price * (1.0 - 8.0 * r)
    assert abs(sig.stop_price - expected) < 1e-6, (sig.stop_price, expected, r, sig.entry_price)


def test_stopped_buy_never_opens_rebound_short_spec():
    # If buy is stopped out, rebound short must NOT open (spec rule).
    sig = Signal(
        symbol="TEST", side="long", reason="crash_then_rebound",
        entry_price=100.0, stop_price=90.0, target_price=109.0,
        risk_per_share=10.0, timestamp="2026-01-01T00:00:00Z",
        size_shares=1.0, signal_index=0,
    )
    candles = [
        {"timestamp": "2026-01-01T00:00:00Z", "open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0, "volume": 1.0},
        {"timestamp": "2026-01-01T01:00:00Z", "open": 95.0, "high": 96.0, "low": 80.0, "close": 85.0, "volume": 1.0},
    ]
    config = StrategyConfig(
        entry_next_bar=False, enable_liquidation_checks=False,
        enable_rebound_short=True, use_spec_safety_stop=True,
    )
    res = backtest_simple(candles, sig, config=config)
    assert res.exit_reason == 'stopped'
    assert res.trades is None or not any(t.get('side') == 'short' for t in (res.trades or []))
