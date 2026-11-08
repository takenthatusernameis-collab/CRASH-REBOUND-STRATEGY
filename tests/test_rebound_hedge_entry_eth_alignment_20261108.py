"""Regression lock (2026-11-08, 2a/e): rebound-short ETH hedge *entry* price must
use the SAME aligned bar `idx` as the coin target bar and the hedge sizing window
(eth_candles[:idx+1] / bars 0..idx). It must NOT read eth_candles[idx+1]
(look-ahead / misalignment). When ETH series is shorter than idx+1, it must fall
back to bar idx (or last available) without look-ahead and still charge hourly
funding on the rebound long-ETH hedge leg (spec: hourly funding on every leg).

Synthetic fixtures only; not performance evidence; no real market data; no look-ahead.
"""
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal

ENTRY_PX = 100.0
SHARES = 1.0
SIGNAL_IDX = 5
RATE = 0.01  # 0.01%/hour


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _var_coin(n):
    return [_c(f"2025-01-01T{i:02d}:00:00", 100 + i % 3, 102 + i % 3, 98 + i % 3, 100 + i % 3) for i in range(n)]


def _eth_var(n):
    return [_c(f"2025-01-01T{i:02d}:00:00", 2000 + i % 5, 2005 + i % 5, 1995 + i % 5, 2000 + i % 5) for i in range(n)]


def _sig(**kw):
    d = dict(symbol="T", side="long", reason="t", entry_price=ENTRY_PX, stop_price=50.0,
             target_price=109.0, risk_per_share=1.0, timestamp="2025-01-01T05:00:00",
             size_shares=SHARES, signal_index=SIGNAL_IDX)
    d.update(kw)
    return Signal(**d)


def _base(**kw):
    d = dict(enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=False,
             avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
             commission_min=0.0, funding_rate_pct_per_hour=0.0, min_daily_volume_usd=0.0,
             time_exit_max_bars=1000, enable_liquidation_checks=False)
    d.update(kw)
    return StrategyConfig(**d)


def _rebound_candles(target_idx=6, n=20):
    candles = _var_coin(n)
    # Long hits target at target_idx (open 100, high 110 >= 109 target)
    candles[target_idx] = _c(f"2025-01-01T{target_idx:02d}:00:00", 100.0, 110.0, 99.0, 109.0)
    # Keep rebound short alive until end without hitting stop/target
    for i in range(target_idx + 1, n):
        candles[i] = _c(f"2025-01-01T{i:02d}:00:00", 109.0, 110.0, 108.0, 109.0)
    return candles


def test_rebound_hedge_entry_uses_eth_bar_idx_not_idx_plus_one():
    """Coin target fires at bar 6 (idx=6). ETH bar 6 open is 2600 (aligned, in sizing
    window 0..6). ETH bar 7 open is 9999 (next bar, must NOT be used). The previous
    bug read eth_candles[min(idx+1,...)] => bar 7."""
    candles = _rebound_candles(target_idx=6)
    eth = _eth_var(20)
    eth[6] = _c("2025-01-01T06:00:00", 2600.0, 2605.0, 2595.0, 2600.0)  # aligned bar idx
    eth[7] = _c("2025-01-01T07:00:00", 9999.0, 9999.0, 9999.0, 9999.0)  # idx+1 look-ahead bar
    r = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=0.0), eth_candles=eth)
    assert (r.rebound_hedge_size or 0) > 0, f"expected rebound hedge, got {r.rebound_hedge_size}"
    assert r.rebound_hedge_entry == 2600.0, (
        f"rebound hedge entry must use eth bar idx=6 (2600), not idx+1 (9999); got {r.rebound_hedge_entry}"
    )


def test_rebound_hedge_entry_short_eth_series_falls_back_to_idx_without_lookahead():
    """ETH series ends at bar 6 (len 7). Target fires at idx=6. There is no idx+1 bar.
    Must fall back to bar 6 (aligned/last available) without look-ahead, not crash,
    and still size/open the rebound hedge."""
    candles = _rebound_candles(target_idx=6)
    eth = _eth_var(7)  # bars 0..6 only; no idx+1
    eth[6] = _c("2025-01-01T06:00:00", 2600.0, 2605.0, 2595.0, 2600.0)
    r = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=0.0), eth_candles=eth)
    assert (r.rebound_hedge_size or 0) > 0, f"expected rebound hedge with short ETH series, got {r.rebound_hedge_size}"
    assert r.rebound_hedge_entry == 2600.0, (
        f"short ETH series must fall back to idx=6 (2600) without look-ahead; got {r.rebound_hedge_entry}"
    )


def test_rebound_hedge_entry_short_eth_series_still_charges_funding():
    """Even when ETH series is short at/after rebound entry, hourly funding on the
    rebound long-ETH hedge leg must still apply on exits (spec: every leg, all exits)."""
    candles = _rebound_candles(target_idx=6, n=20)
    eth = _eth_var(7)  # short: bars 0..6
    eth[6] = _c("2025-01-01T06:00:00", 2600.0, 2605.0, 2595.0, 2600.0)
    on = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=RATE), eth_candles=eth)
    off = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=0.0), eth_candles=eth)
    assert (on.rebound_hedge_size or 0) > 0, "expected rebound hedge"
    delta = (on.total_pnl or 0.0) - (off.total_pnl or 0.0)
    assert abs(delta) > 1e-9, f"rebound hedge funding missing with short ETH series at entry (delta={delta})"


def test_rebound_hedge_entry_eth_shorter_than_idx_falls_back_to_last():
    """If ETH ends before idx (edge: len(eth)==idx), fall back to last available
    without look-ahead; hedge should still open if possible and funding still applies."""
    candles = _rebound_candles(target_idx=6, n=20)
    eth = _eth_var(6)  # bars 0..5, ends before idx=6
    eth[5] = _c("2025-01-01T05:00:00", 2500.0, 2505.0, 2495.0, 2500.0)
    on = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=RATE), eth_candles=eth)
    off = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=0.0), eth_candles=eth)
    assert (on.rebound_hedge_size or 0) > 0, "expected rebound hedge with ETH ending before idx"
    assert on.rebound_hedge_entry == 2500.0, f"expected fallback to last ETH bar 5 (2500), got {on.rebound_hedge_entry}"
    delta = (on.total_pnl or 0.0) - (off.total_pnl or 0.0)
    assert abs(delta) > 1e-9, f"funding missing when ETH ends before rebound idx (delta={delta})"
