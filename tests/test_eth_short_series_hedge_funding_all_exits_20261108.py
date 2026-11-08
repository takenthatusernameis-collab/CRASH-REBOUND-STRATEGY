"""Regression locks (2026-11-08): hourly funding applied on ETH hedge legs on ALL
exit paths when the ETH candle series is too short at the exit index (no bar
available: idx >= len(eth_candles)). This is distinct from a bar present with
missing close/open fields. Engine must fall back to hedge entry for exit-price
accounting while still charging/paying funding per spec "hourly funding on
every leg".

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


def _short_eth(eth, exit_idx):
    """Truncate ETH so no bar exists at exit_idx (series ends at exit_idx)."""
    return eth[:exit_idx]


def _assert_funding_delta(on, off, label):
    assert (on.hedge_size or 0) > 0, f"{label}: expected hedge (size={on.hedge_size})"
    delta = (on.total_pnl or 0.0) - (off.total_pnl or 0.0)
    assert abs(delta) > 1e-9, f"{label}: funding missing when ETH series short (delta={delta})"
    return delta


# --- Long leg exits, short ETH series ---

def test_long_stopped_funding_when_eth_series_short():
    candles = _var_coin(20)
    candles[6] = _c("2025-01-01T06:00:00", 100.0, 101.0, 49.0, 55.0)
    eth = _short_eth(_eth_var(20), 6)
    on = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=RATE), eth_candles=eth)
    off = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=0.0), eth_candles=eth)
    assert on.exit_reason == "stopped"
    _assert_funding_delta(on, off, "long_stopped_short_eth")


def test_long_liquidated_funding_when_eth_series_short():
    candles = _var_coin(20)
    candles[6] = _c("2025-01-01T06:00:00", 100.0, 101.0, 93.0, 95.0)
    eth = _short_eth(_eth_var(20), 6)
    on = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=RATE, enable_liquidation_checks=True), eth_candles=eth)
    off = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=0.0, enable_liquidation_checks=True), eth_candles=eth)
    assert on.exit_reason == "liquidated"
    _assert_funding_delta(on, off, "long_liquidated_short_eth")


def test_long_time_exit_funding_when_eth_series_short():
    candles = _var_coin(20)
    exit_idx = 8  # 3 bars held from signal_idx 5 => exits at 8 via time_exit_max_bars=3
    eth = _short_eth(_eth_var(20), exit_idx)
    on = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=RATE, time_exit_max_bars=3), eth_candles=eth)
    off = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=0.0, time_exit_max_bars=3), eth_candles=eth)
    assert on.exit_reason == "time_exit"
    _assert_funding_delta(on, off, "long_time_exit_short_eth")


def test_long_target_path_funding_when_eth_series_short():
    # Target exit at bar 6; rebound disabled to isolate long hedge.
    candles = _var_coin(20)
    candles[6] = _c("2025-01-01T06:00:00", 100.0, 110.0, 99.0, 109.0)
    eth = _short_eth(_eth_var(20), 6)
    on = backtest_simple(candles, _sig(target_price=109.0), config=_base(funding_rate_pct_per_hour=RATE), eth_candles=eth)
    off = backtest_simple(candles, _sig(target_price=109.0), config=_base(funding_rate_pct_per_hour=0.0), eth_candles=eth)
    assert on.exit_reason in ("target", "target_rebound_short")
    _assert_funding_delta(on, off, "long_target_short_eth")


# --- Rebound exits, short ETH series at rebound exit ---

def _rebound_base_candles(n=20):
    candles = _var_coin(n)
    candles[6] = _c("2025-01-01T06:00:00", 100.0, 110.0, 99.0, 109.0)
    for i in range(7, n):
        candles[i] = _c(f"2025-01-01T{i:02d}:00:00", 109.0, 110.0, 108.0, 109.0)
    return candles


def test_rebound_liquidated_funding_when_eth_series_short():
    candles = _rebound_base_candles(20)
    # short liq threshold 109*1.06=115.54
    candles[8] = _c("2025-01-01T08:00:00", 109.0, 116.0, 108.0, 109.0)
    eth = _short_eth(_eth_var(20), 8)
    cfg_on = _base(enable_rebound_short=True, funding_rate_pct_per_hour=RATE, enable_liquidation_checks=True)
    cfg_off = _base(enable_rebound_short=True, funding_rate_pct_per_hour=0.0, enable_liquidation_checks=True)
    on = backtest_simple(candles, _sig(), config=cfg_on, eth_candles=eth)
    off = backtest_simple(candles, _sig(), config=cfg_off, eth_candles=eth)
    assert any(t.get("side") == "short" and t.get("reason") == "liquidated" for t in (on.trades or [])), on.trades
    delta = (on.total_pnl or 0.0) - (off.total_pnl or 0.0)
    assert abs(delta) > 1e-9, f"rebound_liquidated_short_eth: funding delta missing ({delta})"


def test_rebound_stopped_funding_when_eth_series_short():
    candles = _rebound_base_candles(20)
    candles[8] = _c("2025-01-01T08:00:00", 109.0, 160.0, 108.0, 109.0)
    eth = _short_eth(_eth_var(20), 8)
    cfg_on = _base(enable_rebound_short=True, funding_rate_pct_per_hour=RATE)
    cfg_off = _base(enable_rebound_short=True, funding_rate_pct_per_hour=0.0)
    on = backtest_simple(candles, _sig(), config=cfg_on, eth_candles=eth)
    off = backtest_simple(candles, _sig(), config=cfg_off, eth_candles=eth)
    assert any(t.get("side") == "short" and t.get("reason") == "stopped" for t in (on.trades or [])), on.trades
    delta = (on.total_pnl or 0.0) - (off.total_pnl or 0.0)
    assert abs(delta) > 1e-9, f"rebound_stopped_short_eth: funding delta missing ({delta})"


def test_rebound_target_funding_when_eth_series_short():
    candles = _rebound_base_candles(20)
    candles[8] = _c("2025-01-01T08:00:00", 109.0, 110.0, 99.0, 100.0)
    eth = _short_eth(_eth_var(20), 8)
    cfg_on = _base(enable_rebound_short=True, funding_rate_pct_per_hour=RATE)
    cfg_off = _base(enable_rebound_short=True, funding_rate_pct_per_hour=0.0)
    on = backtest_simple(candles, _sig(), config=cfg_on, eth_candles=eth)
    off = backtest_simple(candles, _sig(), config=cfg_off, eth_candles=eth)
    assert any(t.get("side") == "short" and t.get("reason") == "target" for t in (on.trades or [])), on.trades
    delta = (on.total_pnl or 0.0) - (off.total_pnl or 0.0)
    assert abs(delta) > 1e-9, f"rebound_target_short_eth: funding delta missing ({delta})"


def test_rebound_time_exit_funding_when_eth_series_short():
    candles = _rebound_base_candles(30)
    # time exit at 2 bars: exits on sidx where (sidx - short_start_idx + 1) >= 2
    # short starts at idx 6 (target bar), first short check is 7: 7-6+1=2 >=2
    eth = _short_eth(_eth_var(30), 7)
    cfg_on = _base(enable_rebound_short=True, funding_rate_pct_per_hour=RATE, rebound_short_time_exit_bars=2)
    cfg_off = _base(enable_rebound_short=True, funding_rate_pct_per_hour=0.0, rebound_short_time_exit_bars=2)
    on = backtest_simple(candles, _sig(), config=cfg_on, eth_candles=eth)
    off = backtest_simple(candles, _sig(), config=cfg_off, eth_candles=eth)
    assert any(t.get("side") == "short" and t.get("reason") == "time_exit" for t in (on.trades or [])), on.trades
    delta = (on.total_pnl or 0.0) - (off.total_pnl or 0.0)
    assert abs(delta) > 1e-9, f"rebound_time_exit_short_eth: funding delta missing ({delta})"
