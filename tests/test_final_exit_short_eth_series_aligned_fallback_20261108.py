"""Regression locks (2026-11-08): long/rebound final-exit (end of coin series)
must not use a misaligned ETH bar (eth_candles[-1]) when the ETH series is
shorter than the coin exit index. Spec requires aligned hourly hedge accounting;
if no aligned bar exists at the exit index, fall back to hedge entry for
exit-price accounting while still applying funding (hourly funding on every leg).

Distinct from idx>=len(eth_candles) mid-series exits (covered elsewhere): this is
the final-bar path that previously read eth_candles[-1] unconditionally.

Synthetic fixtures only; not performance evidence; no real market data; no look-ahead.
"""
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal

ENTRY_PX = 100.0
SHARES = 1.0
RATE = 0.01
SIGNAL_IDX = 5


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _var_coin(n):
    return [_c(f"2025-01-01T{i:02d}:00:00", 100 + i % 3, 102 + i % 3, 98 + i % 3, 100 + i % 3) for i in range(n)]


def _eth_var(n):
    return [_c(f"2025-01-01T{i:02d}:00:00", 2000 + i % 5, 2005 + i % 5, 1995 + i % 5, 2000 + i % 5) for i in range(n)]


def _sig(**kw):
    d = dict(symbol="T", side="long", reason="t", entry_price=ENTRY_PX, stop_price=50.0,
             target_price=150.0, risk_per_share=1.0, timestamp="2025-01-01T05:00:00",
             size_shares=SHARES, signal_index=SIGNAL_IDX)
    d.update(kw)
    return Signal(**d)


def _base(**kw):
    d = dict(enable_eth_hedge=True, enable_rebound_short=False, entry_next_bar=False,
             avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
             commission_min=0.0, funding_rate_pct_per_hour=RATE, min_daily_volume_usd=0.0,
             time_exit_max_bars=1000, enable_liquidation_checks=False)
    d.update(kw)
    return StrategyConfig(**d)


def _rebound_base_candles(n=20):
    candles = _var_coin(n)
    candles[6] = _c("2025-01-01T06:00:00", 100.0, 110.0, 99.0, 109.0)
    for i in range(7, n):
        candles[i] = _c(f"2025-01-01T{i:02d}:00:00", 109.0, 110.0, 108.0, 109.0)
    return candles


def test_long_final_exit_short_eth_series_uses_aligned_fallback_not_misaligned_last():
    """Coin ends at 19, ETH ends at 7. Engine must not use eth_candles[-1] (bar 7)
    as exit price for coin bar 19; must fall back to hedge entry."""
    candles = _var_coin(20)
    eth_short = _eth_var(8)
    eth_short[-1] = _c("2025-01-01T07:00:00", 9999.0, 9999.0, 9999.0, 9999.0)
    on = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=RATE), eth_candles=eth_short)
    off = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=0.0), eth_candles=eth_short)
    assert on.exit_reason == "time_exit"
    assert (on.hedge_size or 0) > 0
    assert on.hedge_exit == on.hedge_entry, f"misaligned eth_candles[-1] used: hedge_exit={on.hedge_exit} entry={on.hedge_entry}"
    delta = (on.total_pnl or 0.0) - (off.total_pnl or 0.0)
    assert abs(delta) > 1e-9, f"funding missing on final-exit short ETH series (delta={delta})"


def test_long_final_exit_aligned_eth_uses_correct_bar():
    candles = _var_coin(20)
    eth = _eth_var(20)
    eth[19] = _c("2025-01-01T19:00:00", 2100.0, 2100.0, 2100.0, 2100.0)
    on = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=0.0), eth_candles=eth)
    assert (on.hedge_size or 0) > 0
    assert on.hedge_exit == 2100.0, f"aligned final bar not used: {on.hedge_exit}"


def test_rebound_final_exit_short_eth_series_uses_aligned_fallback():
    """Rebound short runs to end of coin series with ETH shorter."""
    candles = _rebound_base_candles(20)
    eth_short = _eth_var(8)
    eth_short[-1] = _c("2025-01-01T07:00:00", 9999.0, 9999.0, 9999.0, 9999.0)
    cfg_on = _base(enable_rebound_short=True, funding_rate_pct_per_hour=RATE)
    cfg_off = _base(enable_rebound_short=True, funding_rate_pct_per_hour=0.0)
    on = backtest_simple(candles, _sig(target_price=109.0), config=cfg_on, eth_candles=eth_short)
    off = backtest_simple(candles, _sig(target_price=109.0), config=cfg_off, eth_candles=eth_short)
    assert on.exit_reason in ("target_rebound_short", "time_exit")
    assert (on.rebound_hedge_size or 0) > 0, f"expected rebound hedge (size={on.rebound_hedge_size})"
    assert on.rebound_hedge_exit == on.rebound_hedge_entry, (
        f"misaligned rebound eth_candles[-1] used: exit={on.rebound_hedge_exit} entry={on.rebound_hedge_entry}"
    )
    delta = (on.total_pnl or 0.0) - (off.total_pnl or 0.0)
    assert abs(delta) > 1e-9, f"funding missing on rebound final-exit short ETH series (delta={delta})"


def test_rebound_final_exit_aligned_eth_uses_correct_bar():
    candles = _rebound_base_candles(20)
    eth = _eth_var(20)
    eth[19] = _c("2025-01-01T19:00:00", 2100.0, 2100.0, 2100.0, 2100.0)
    on = backtest_simple(candles, _sig(target_price=109.0),
                         config=_base(enable_rebound_short=True, funding_rate_pct_per_hour=0.0), eth_candles=eth)
    assert (on.rebound_hedge_size or 0) > 0
    assert on.rebound_hedge_exit == 2100.0, f"aligned rebound final bar not used: {on.rebound_hedge_exit}"
