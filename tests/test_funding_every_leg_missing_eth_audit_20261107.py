"""Deterministic audit (2026-11-07): hourly funding must apply on every leg
(long coin, long-leg ETH hedge, rebound short coin, rebound long-ETH hedge)
even when ETH exit price data is missing on the exit bar. Fallback uses hedge
entry for exit accounting but funding is still owed per spec.

Spec: "hourly funding on every leg" (crash-rebound-strategy.pdf). Synthetic
fixtures only; not performance evidence; no real market data; no look-ahead.
"""
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal

ENTRY_PX = 100.0
SHARES = 1.0
RATE = 0.01  # 0.01%/hour
SIGNAL_IDX = 5


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _coin_var(n):
    return [_c(f"2025-01-01T{i % 24:02d}:00:00", 100 + i % 3, 102 + i % 3, 98 + i % 3, 100 + i % 3) for i in range(n)]


def _eth_var(n):
    return [_c(f"2025-01-01T{i % 24:02d}:00:00", 100 + i % 4, 102 + i % 4, 98 + i % 4, 100 + i % 4) for i in range(n)]


def _sig(target=109.0):
    return Signal(symbol="T", side="long", reason="t", entry_price=ENTRY_PX, stop_price=50.0,
                  target_price=target, risk_per_share=1.0, timestamp="2025-01-01T05:00:00",
                  size_shares=SHARES, signal_index=SIGNAL_IDX)


def _base(**kw):
    d = dict(enable_eth_hedge=True, enable_rebound_short=False, entry_next_bar=False,
             avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
             commission_min=0.0, funding_rate_pct_per_hour=RATE, min_daily_volume_usd=0.0,
             time_exit_max_bars=50, enable_liquidation_checks=False)
    d.update(kw)
    return StrategyConfig(**d)


def _funding_delta(candles, sig, eth_missing, **cfg_kw):
    on = backtest_simple(candles, sig, config=_base(funding_rate_pct_per_hour=RATE, **cfg_kw), eth_candles=eth_missing)
    off = backtest_simple(candles, sig, config=_base(funding_rate_pct_per_hour=0.0, **cfg_kw), eth_candles=eth_missing)
    return on, off, (on.total_pnl or 0.0) - (off.total_pnl or 0.0)


def test_long_leg_stop_with_missing_eth_exit_applies_hedge_funding():
    candles = _coin_var(40)
    candles[6] = _c("2025-01-01T06:00:00", 100.0, 101.0, 49.0, 100.0)
    eth = _eth_var(40)
    eth_missing = [dict(x) for x in eth]
    eth_missing[6] = {"timestamp": "2025-01-01T06:00:00"}
    on, off, delta = _funding_delta(candles, _sig(), eth_missing)
    assert on.exit_reason == "stopped"
    assert on.hedge_side == "short" and (on.hedge_size or 0) > 0
    hours = 6 - SIGNAL_IDX + 1  # 2
    coin_cost = ENTRY_PX * SHARES * hours * (RATE / 100.0)
    hedge_benefit = on.hedge_entry * on.hedge_size * hours * (RATE / 100.0)
    assert abs(delta - (-coin_cost + hedge_benefit)) < 1e-6


def test_long_leg_target_with_missing_eth_exit_applies_hedge_funding():
    candles = _coin_var(40)
    candles[6] = _c("2025-01-01T06:00:00", 100.0, 110.0, 99.0, 109.0)
    eth = _eth_var(40)
    eth_missing = [dict(x) for x in eth]
    eth_missing[6] = {"timestamp": "2025-01-01T06:00:00"}
    on, off, delta = _funding_delta(candles, _sig(), eth_missing)
    assert on.exit_reason == "target"
    assert on.hedge_side == "short" and (on.hedge_size or 0) > 0
    hours = 6 - SIGNAL_IDX + 1
    coin_cost = ENTRY_PX * SHARES * hours * (RATE / 100.0)
    hedge_benefit = on.hedge_entry * on.hedge_size * hours * (RATE / 100.0)
    assert abs(delta - (-coin_cost + hedge_benefit)) < 1e-6


def test_long_leg_liquidation_with_missing_eth_exit_applies_hedge_funding():
    candles = _coin_var(40)
    candles[6] = _c("2025-01-01T06:00:00", 100.0, 101.0, 93.0, 100.0)  # liq threshold 94
    eth = _eth_var(40)
    eth_missing = [dict(x) for x in eth]
    eth_missing[6] = {"timestamp": "2025-01-01T06:00:00"}
    on, off, delta = _funding_delta(candles, _sig(), eth_missing, enable_liquidation_checks=True)
    assert on.exit_reason == "liquidated"
    assert on.hedge_side == "short" and (on.hedge_size or 0) > 0
    # liquidation delta includes penalty; compare funded vs unfunded on same missing-eth path
    assert abs(delta) > 1e-12, "liquidation with missing ETH exit must still apply leg/hedge funding"


def test_rebound_short_stop_with_missing_eth_exit_applies_all_leg_funding():
    candles = _coin_var(40)
    candles[6] = _c("2025-01-01T06:00:00", 100.0, 110.0, 99.0, 109.0)
    candles[7] = _c("2025-01-01T07:00:00", 109.0, 160.0, 108.0, 109.0)  # short stop 152.6
    eth = _eth_var(40)
    eth_missing = [dict(x) for x in eth]
    eth_missing[6] = {"timestamp": "2025-01-01T06:00:00"}  # long hedge exit bar
    eth_missing[7] = {"timestamp": "2025-01-01T07:00:00"}  # rebound hedge exit bar
    on, off, delta = _funding_delta(candles, _sig(), eth_missing, enable_rebound_short=True)
    assert any(t.get("side") == "short" and t.get("reason") == "stopped" for t in (on.trades or []))
    assert abs(delta) > 1e-9, "rebound stop with missing ETH exit must apply all leg/hedge funding"


def test_rebound_short_target_with_missing_eth_exit_applies_all_leg_funding():
    candles = _coin_var(40)
    candles[6] = _c("2025-01-01T06:00:00", 100.0, 110.0, 99.0, 109.0)
    candles[7] = _c("2025-01-01T07:00:00", 109.0, 110.0, 99.0, 100.0)  # short target 99.19
    eth = _eth_var(40)
    eth_missing = [dict(x) for x in eth]
    eth_missing[6] = {"timestamp": "2025-01-01T06:00:00"}
    eth_missing[7] = {"timestamp": "2025-01-01T07:00:00"}
    on, off, delta = _funding_delta(candles, _sig(), eth_missing, enable_rebound_short=True)
    assert any(t.get("side") == "short" and t.get("reason") == "target" for t in (on.trades or []))
    assert abs(delta) > 1e-9, "rebound target with missing ETH exit must apply all leg/hedge funding"


def test_rebound_short_final_exit_loop_else_with_missing_eth_exit_applies_all_leg_funding():
    candles = _coin_var(12)
    candles[6] = _c("2025-01-01T06:00:00", 100.0, 110.0, 99.0, 109.0)
    for i in range(7, 12):
        candles[i] = _c(f"2025-01-01T{i:02d}:00:00", 109.0, 110.0, 108.0, 109.0)
    eth = _eth_var(12)
    eth_missing = [dict(x) for x in eth]
    eth_missing[6] = {"timestamp": "2025-01-01T06:00:00"}
    eth_missing[-1] = {"timestamp": "2025-01-01T11:00:00"}
    on, off, delta = _funding_delta(candles, _sig(), eth_missing, enable_rebound_short=True,
                                    rebound_short_time_exit_bars=100)
    assert any(t.get("side") == "short" for t in (on.trades or []))
    assert abs(delta) > 1e-9, "rebound final-exit (loop else) with missing ETH exit must apply all leg/hedge funding"
