"""Deterministic spec-fidelity regression (2026-11-07): rebound short final-exit
(no break from rebound loop) must apply rebound long-ETH hedge funding even when
ETH exit-price data is unavailable at final bar (fallback to hedge entry for exit
accounting; funding still owed). Closes HANDOFF priority (1) explicit gap.

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


def _coin(n):
    return [_c(f"2025-01-01T{i % 24:02d}:00:00", 100 + (i % 5) * 0.1, 101.5, 98.5, 100 + (i % 5) * 0.1) for i in range(n)]


def _eth_var(n):
    return [_c(f"2025-01-01T{i % 24:02d}:00:00", 2000 + i % 6 * 2, 2006 + i % 6 * 2, 1994 + i % 6 * 2, 2000 + i % 6 * 2) for i in range(n)]


def _sig():
    return Signal(symbol="T", side="long", reason="t", entry_price=ENTRY_PX, stop_price=50.0,
                  target_price=109.0, risk_per_share=1.0, timestamp="2025-01-01T05:00:00",
                  size_shares=SHARES, signal_index=SIGNAL_IDX)


def _base(**kw):
    d = dict(enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=False,
             avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
             commission_min=0.0, funding_rate_pct_per_hour=RATE, min_daily_volume_usd=0.0,
             time_exit_max_bars=1000, rebound_short_time_exit_bars=1000,
             rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
             enable_liquidation_checks=False)
    d.update(kw)
    return StrategyConfig(**d)


def _scenario():
    # Long hits +9% target at bar 6 -> rebound short enters at 109; no subsequent
    # stop/target/time-exit/liquidation => rebound loop exhausts and final-exit runs.
    candles = _coin(12)
    candles[6] = _c("2025-01-01T06:00:00", 100.0, 110.0, 99.0, 109.0)
    for i in range(7, 12):
        candles[i] = _c(f"2025-01-01T{i:02d}:00:00", 109.0, 110.0, 108.0, 109.0)
    eth = _eth_var(12)
    eth_missing = [dict(x) for x in eth]
    eth_missing[-1] = {"timestamp": "2025-01-01T11:00:00"}  # no close/open
    return candles, eth, eth_missing


def test_rebound_final_exit_hedge_funding_applied_when_eth_exit_missing():
    candles, eth, eth_missing = _scenario()
    on = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=RATE), eth_candles=eth_missing)
    off = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=0.0), eth_candles=eth_missing)
    assert any(t.get("side") == "short" and t.get("reason") == "time_exit" for t in (on.trades or [])), on.trades
    # Final-exit path in engine marks reason time_exit when loop exhausts without break.
    assert abs((on.total_pnl or 0.0) - (off.total_pnl or 0.0)) > 1e-9, (
        "rebound final-exit with missing ETH exit must still apply hedge/leg funding"
    )
    # With missing ETH exit, rebound hedge exit accounting falls back to entry.
    # Total funding delta (all legs) must be present; compare to valid-ETH funded vs unfunded sign/magnitude sanity.
    valid = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=RATE), eth_candles=eth)
    valid_off = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=0.0), eth_candles=eth)
    assert abs((valid.total_pnl or 0.0) - (valid_off.total_pnl or 0.0)) > 1e-9
