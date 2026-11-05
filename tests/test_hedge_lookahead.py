"""Deterministic tests: ETH hedge sizing must not use future bars (no look-ahead)."""
import pytest
from src.strategy.config import StrategyConfig
from src.backtest.engine import backtest_simple
from src.strategy.crash_rebound import Signal
import src.backtest.engine as eng


def _candles(n, base=100.0, vol=0.001):
    out = []
    p = base
    for i in range(n):
        # deterministic small wiggle
        wig = vol * (1 if i % 2 == 0 else -1)
        o = p
        c = p * (1 + wig)
        h = max(o, c) * 1.001
        l = min(o, c) * 0.999
        out.append({"timestamp": f"2025-01-01T{i%24:02d}:00:00", "open": o, "high": h, "low": l, "close": c, "volume": 10_000_000})
        p = c
    return out


def _volatile_future(n, base=100.0):
    out = []
    p = base
    for i in range(n):
        o = p
        c = p * (1.2 if i % 2 == 0 else 0.8)
        h = max(o, c) * 1.01
        l = min(o, c) * 0.99
        out.append({"timestamp": f"2025-02-01T{i%24:02d}:00:00", "open": o, "high": h, "low": l, "close": c, "volume": 10_000_000})
        p = base
    return out


def test_initial_hedge_sizing_ignores_future_bars(monkeypatch):
    """Hedge vol sizing at entry must use only bars available at entry (no look-ahead)."""
    past = _candles(400, base=100.0, vol=0.001)
    future = _volatile_future(120, base=past[-1]['close'])
    full = past + future
    # Signal/entry at index 350 (entry_next_bar off for determinism)
    entry_idx = 350
    candles_past = full[: entry_idx + 60]  # enough for exits but same past
    candles_full = full

    seen = {}
    orig = eng.compute_eth_hedge_size

    def spy(coin_candles, eth_candles, coin_position_value, config):
        seen.setdefault('calls', []).append((len(coin_candles), len(eth_candles), coin_position_value))
        return orig(coin_candles, eth_candles, coin_position_value, config)

    monkeypatch.setattr(eng, 'compute_eth_hedge_size', spy)

    sig = Signal(symbol="TEST", side="long", reason="t", entry_price=past[entry_idx]['close'],
                 stop_price=past[entry_idx]['close'] * 0.5, target_price=past[entry_idx]['close'] * 2.0,
                 risk_per_share=1.0, timestamp=past[entry_idx]['timestamp'], size_shares=1.0,
                 signal_index=entry_idx)
    cfg = StrategyConfig(enable_eth_hedge=True, enable_rebound_short=False, entry_next_bar=False,
                         avoid_downtrend=False, enable_liquidation_checks=False,
                         slippage_pct=0.0, commission_per_share=0.0, commission_min=0.0,
                         time_exit_max_bars=30, min_daily_volume_usd=0.0)

    # run with truncated data (no crazy future beyond what we include) and with full future appended
    # Compare hedge sizes implied by calls; first call is initial hedge.
    seen['calls'] = []
    res_a = backtest_simple(candles_past, sig, config=cfg, eth_candles=candles_past)
    calls_a = list(seen.get('calls', []))
    seen['calls'] = []
    res_b = backtest_simple(candles_full, sig, config=cfg, eth_candles=candles_full)
    calls_b = list(seen.get('calls', []))

    assert calls_a, "expected hedge sizing call"
    assert calls_b, "expected hedge sizing call"
    # initial hedge call (first) must see identical history length regardless of future bars
    assert calls_a[0][0] == calls_b[0][0], f"coin look-ahead: {calls_a[0][0]} vs {calls_b[0][0]}"
    assert calls_a[0][1] == calls_b[0][1], f"eth look-ahead: {calls_a[0][1]} vs {calls_b[0][1]}"
    # and hedge result should be identical
    assert abs(res_a.hedge_pnl - res_b.hedge_pnl) < 1e-9
    assert abs(res_a.total_pnl - res_b.total_pnl) < 1e-9


def test_rebound_hedge_sizing_ignores_future_bars(monkeypatch):
    """Rebound-short hedge sizing must not use future bars."""
    # Build: long hits target quickly, then rebound short runs; append volatile future after.
    n = 420
    candles = []
    p = 100.0
    for i in range(n):
        # stable, then a move that hits target
        if i < 360:
            o, c = 100.0, 100.0
            h, l = 101.0, 99.0
        elif i == 360:
            o, c = 100.0, 110.0  # target hit area (we'll set target accordingly)
            h, l = 111.0, 99.0
        else:
            o, c = 110.0, 110.0
            h, l = 111.0, 109.0
        candles.append({"timestamp": f"2025-01-01T{i%24:02d}:00:00", "open": o, "high": h, "low": l, "close": c, "volume": 10_000_000})
    future = _volatile_future(120, base=110.0)
    full = candles + future

    orig = eng.compute_eth_hedge_size
    seen = []

    def spy(coin_candles, eth_candles, coin_position_value, config):
        seen.append(len(coin_candles))
        return orig(coin_candles, eth_candles, coin_position_value, config)

    monkeypatch.setattr(eng, 'compute_eth_hedge_size', spy)

    entry_idx = 359
    sig = Signal(symbol="TEST", side="long", reason="t", entry_price=100.0,
                 stop_price=90.0, target_price=109.0,
                 risk_per_share=10.0, timestamp=candles[entry_idx]['timestamp'], size_shares=1.0,
                 signal_index=entry_idx)
    cfg = StrategyConfig(enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=False,
                         avoid_downtrend=False, enable_liquidation_checks=False,
                         slippage_pct=0.0, commission_per_share=0.0, commission_min=0.0,
                         time_exit_max_bars=10, rebound_short_time_exit_bars=5,
                         rebound_short_target_pct=50.0, rebound_short_stop_pct=50.0,
                         min_daily_volume_usd=0.0)

    seen.clear()
    res_a = backtest_simple(candles[:400], sig, config=cfg, eth_candles=candles[:400])
    calls_a = list(seen)
    seen.clear()
    res_b = backtest_simple(full, sig, config=cfg, eth_candles=full)
    calls_b = list(seen)

    # may have 1 (initial) or 2 (initial+rebound) calls; rebound call must not see future
    assert len(calls_a) == len(calls_b)
    for i, (a, b) in enumerate(zip(calls_a, calls_b)):
        assert a == b, f"hedge call {i} look-ahead: {a} vs {b}"
    assert abs(res_a.total_pnl - res_b.total_pnl) < 1e-9
