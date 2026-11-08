"""Regression locks (2026-11-08): hourly funding applied on ETH hedge legs on ALL
exit paths when ETH exit-price data is missing (fallback to hedge entry for exit
accounting; funding still owed per spec "hourly funding on every leg").

Covers uncovered spec paths (HANDOFF 2a/2b): long hedge on stopped/liquidated;
rebound long-ETH hedge on stopped/target — all with missing ETH at exit bar.
Existing coverage: long time/final, rebound liq/time/final, long target (audit).

Synthetic fixtures only; not performance evidence; no real market data; no look-ahead.
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
    d = dict(enable_eth_hedge=True, enable_rebound_short=False, entry_next_bar=False,
             avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
             commission_min=0.0, funding_rate_pct_per_hour=RATE, min_daily_volume_usd=0.0,
             time_exit_max_bars=1000, enable_liquidation_checks=False)
    d.update(kw)
    return StrategyConfig(**d)


def _missing_eth_at(eth, idx):
    out = [dict(x) for x in eth]
    out[idx] = {"timestamp": f"2025-01-01T{idx:02d}:00:00"}  # no close/open
    return out


def _assert_funding_delta_present(on, off, label):
    assert (on.hedge_size or 0) > 0, f"{label}: expected hedge"
    delta = (on.total_pnl or 0.0) - (off.total_pnl or 0.0)
    assert abs(delta) > 1e-9, f"{label}: funding missing when ETH exit absent (delta={delta})"
    return delta


def test_long_hedge_funding_on_stopped_when_eth_exit_missing():
    candles = _var_coin(20)
    candles[6] = _c("2025-01-01T06:00:00", 100.0, 101.0, 49.0, 55.0)  # hits stop 50
    eth = _eth_var(20)
    eth_m = _missing_eth_at(eth, 6)
    on = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=RATE), eth_candles=eth_m)
    off = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=0.0), eth_candles=eth_m)
    assert on.exit_reason == "stopped"
    _assert_funding_delta_present(on, off, "long_stopped_missing_eth")


def test_long_hedge_funding_on_liquidated_when_eth_exit_missing():
    candles = _var_coin(20)
    # liq threshold for long at entry 100, maint 5%, buffer 1% => 94%
    candles[6] = _c("2025-01-01T06:00:00", 100.0, 101.0, 93.0, 95.0)
    eth = _eth_var(20)
    eth_m = _missing_eth_at(eth, 6)
    on = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=RATE, enable_liquidation_checks=True), eth_candles=eth_m)
    off = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=0.0, enable_liquidation_checks=True), eth_candles=eth_m)
    assert on.exit_reason == "liquidated"
    _assert_funding_delta_present(on, off, "long_liquidated_missing_eth")


def _rebound_base_candles(n=20):
    candles = _var_coin(n)
    candles[6] = _c("2025-01-01T06:00:00", 100.0, 110.0, 99.0, 109.0)  # long target -> rebound short at 109
    for i in range(7, n):
        candles[i] = _c(f"2025-01-01T{i:02d}:00:00", 109.0, 110.0, 108.0, 109.0)
    return candles


def test_rebound_hedge_funding_on_stopped_when_eth_exit_missing():
    candles = _rebound_base_candles(20)
    # short stop 109*1.40=152.6
    candles[8] = _c("2025-01-01T08:00:00", 109.0, 160.0, 108.0, 109.0)
    eth = _eth_var(20)
    eth_m = _missing_eth_at(eth, 8)
    cfg_on = _base(enable_rebound_short=True, funding_rate_pct_per_hour=RATE)
    cfg_off = _base(enable_rebound_short=True, funding_rate_pct_per_hour=0.0)
    on = backtest_simple(candles, _sig(), config=cfg_on, eth_candles=eth_m)
    off = backtest_simple(candles, _sig(), config=cfg_off, eth_candles=eth_m)
    assert any(t.get("side") == "short" and t.get("reason") == "stopped" for t in (on.trades or [])), on.trades
    delta = (on.total_pnl or 0.0) - (off.total_pnl or 0.0)
    assert abs(delta) > 1e-9, f"rebound_stopped_missing_eth: funding delta missing ({delta})"


def test_rebound_hedge_funding_on_target_when_eth_exit_missing():
    candles = _rebound_base_candles(20)
    # short target 109*0.91=99.19
    candles[8] = _c("2025-01-01T08:00:00", 109.0, 110.0, 99.0, 100.0)
    eth = _eth_var(20)
    eth_m = _missing_eth_at(eth, 8)
    cfg_on = _base(enable_rebound_short=True, funding_rate_pct_per_hour=RATE)
    cfg_off = _base(enable_rebound_short=True, funding_rate_pct_per_hour=0.0)
    on = backtest_simple(candles, _sig(), config=cfg_on, eth_candles=eth_m)
    off = backtest_simple(candles, _sig(), config=cfg_off, eth_candles=eth_m)
    assert any(t.get("side") == "short" and t.get("reason") == "target" for t in (on.trades or [])), on.trades
    delta = (on.total_pnl or 0.0) - (off.total_pnl or 0.0)
    assert abs(delta) > 1e-9, f"rebound_target_missing_eth: funding delta missing ({delta})"
