"""Deterministic spec-fidelity regressions (2026-11-07): hourly funding must be
applied on every hedge leg even when ETH exit-price data is unavailable for the
exit bar (fallback to hedge entry price for exit accounting; funding still owed).

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
    return [_c(f"2025-01-01T{i % 24:02d}:00:00", 100 + i % 3, 102 + i % 3, 98 + i % 3, 100 + i % 3) for i in range(n)]


def _eth_var(n):
    # variance for hedge sizing; varying close
    return [_c(f"2025-01-01T{i % 24:02d}:00:00", 100 + i % 4, 102 + i % 4, 98 + i % 4, 100 + i % 4) for i in range(n)]


def _sig():
    return Signal(symbol="T", side="long", reason="t", entry_price=ENTRY_PX, stop_price=50.0,
                  target_price=109.0, risk_per_share=1.0, timestamp="2025-01-01T05:00:00",
                  size_shares=SHARES, signal_index=SIGNAL_IDX)


def _base(**kw):
    d = dict(enable_eth_hedge=True, enable_rebound_short=False, entry_next_bar=False,
             avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
             commission_min=0.0, funding_rate_pct_per_hour=RATE, min_daily_volume_usd=0.0,
             time_exit_max_bars=50, enable_liquidation_checks=False)
    d.update(kw)
    return StrategyConfig(**d)


def _assert_hedge_funding_present(*, missing_result, valid_result, zero_rate_result, coin_notional, hours, hedge_side_expected):
    assert missing_result.hedge_side == hedge_side_expected and (missing_result.hedge_size or 0) > 0
    # coin funding component
    coin_cost = coin_notional * hours * (RATE / 100.0)  # long coin pays
    # hedge funding component (short hedge receives)
    hedge_notional = missing_result.hedge_entry * missing_result.hedge_size
    hedge_benefit = hedge_notional * hours * (RATE / 100.0)
    expected_net = -coin_cost + hedge_benefit
    # Compare missing-exit funded vs zero-rate: price PnL identical (missing fallback=entry, valid has varying price)
    # so use zero-rate on same missing-exit candles for exact coin+hedge price parity.
    actual_net = (missing_result.total_pnl or 0.0) - (zero_rate_result.total_pnl or 0.0)
    assert abs(actual_net - expected_net) < 1e-6, (
        f"hedge funding missing when ETH exit absent: net {actual_net} vs expected {expected_net}"
    )
    # And missing-exit funded must NOT equal zero-rate (funding had effect)
    assert abs((missing_result.total_pnl or 0.0) - (zero_rate_result.total_pnl or 0.0)) > 1e-12


def test_long_hedge_funding_applied_on_time_exit_when_eth_exit_missing():
    candles = _coin(60)
    eth = _eth_var(60)
    eth_missing = [dict(x) for x in eth]
    exit_idx = SIGNAL_IDX + 50 - 1  # 54
    eth_missing[exit_idx] = {"timestamp": f"2025-01-01T{exit_idx % 24:02d}:00:00"}
    on = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=RATE), eth_candles=eth_missing)
    off = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=0.0), eth_candles=eth_missing)
    valid = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=RATE), eth_candles=eth)
    assert on.exit_reason == "time_exit"
    _assert_hedge_funding_present(missing_result=on, valid_result=valid, zero_rate_result=off,
                                  coin_notional=ENTRY_PX * SHARES, hours=50, hedge_side_expected="short")


def test_long_hedge_funding_applied_on_final_exit_when_eth_exit_missing():
    candles = _coin(20)
    eth = _eth_var(20)
    eth_missing = [dict(x) for x in eth]
    eth_missing[-1] = {"timestamp": "2025-01-01T19:00:00"}
    on = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=RATE, time_exit_max_bars=1000),
                         eth_candles=eth_missing)
    off = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=0.0, time_exit_max_bars=1000),
                          eth_candles=eth_missing)
    valid = backtest_simple(candles, _sig(), config=_base(funding_rate_pct_per_hour=RATE, time_exit_max_bars=1000),
                            eth_candles=eth)
    hours = len(candles) - SIGNAL_IDX
    _assert_hedge_funding_present(missing_result=on, valid_result=valid, zero_rate_result=off,
                                  coin_notional=ENTRY_PX * SHARES, hours=hours, hedge_side_expected="short")


def test_rebound_hedge_funding_applied_on_liquidation_when_eth_exit_missing():
    """Rebound short coin liquidated; rebound long-ETH hedge funding must apply
    even if ETH exit bar has no price data."""
    candles = _coin(40)
    candles[6] = _c("2025-01-01T06:00:00", 100.0, 110.0, 99.0, 109.0)
    candles[7] = _c("2025-01-01T07:00:00", 109.0, 110.0, 108.0, 109.0)
    candles[8] = _c("2025-01-01T08:00:00", 109.0, 130.0, 108.0, 125.0)
    eth = _eth_var(40)
    eth_missing = [dict(x) for x in eth]
    eth_missing[8] = {"timestamp": "2025-01-01T08:00:00"}
    cfg = dict(funding_rate_pct_per_hour=RATE, enable_rebound_short=True, enable_liquidation_checks=True)
    on = backtest_simple(candles, _sig(), config=_base(**cfg), eth_candles=eth_missing)
    off = backtest_simple(candles, _sig(), config=_base(**{**cfg, 'funding_rate_pct_per_hour': 0.0}), eth_candles=eth_missing)
    assert any(t.get("side") == "short" and t.get("reason") == "liquidated" for t in (on.trades or []))
    # Funding-enabled must differ from zero-rate even when ETH exit missing (all leg funding applied).
    assert abs((on.total_pnl or 0.0) - (off.total_pnl or 0.0)) > 1e-9, (
        "rebound liquidation with missing ETH exit must still apply hedge/leg funding"
    )


def test_rebound_hedge_funding_applied_on_time_exit_when_eth_exit_missing():
    candles = _coin(40)
    candles[6] = _c("2025-01-01T06:00:00", 100.0, 110.0, 99.0, 109.0)
    for i in range(7, 14):
        candles[i] = _c(f"2025-01-01T{i:02d}:00:00", 109.0, 110.0, 108.0, 109.0)
    eth = _eth_var(40)
    eth_missing = [dict(x) for x in eth]
    eth_missing[12] = {"timestamp": "2025-01-01T12:00:00"}  # sidx 12 = short time exit
    cfg = dict(funding_rate_pct_per_hour=RATE, enable_rebound_short=True, rebound_short_time_exit_bars=6)
    on = backtest_simple(candles, _sig(), config=_base(**cfg), eth_candles=eth_missing)
    off = backtest_simple(candles, _sig(), config=_base(**{**cfg, 'funding_rate_pct_per_hour': 0.0}), eth_candles=eth_missing)
    assert any(t.get("side") == "short" and t.get("reason") == "time_exit" for t in (on.trades or []))
    assert abs((on.total_pnl or 0.0) - (off.total_pnl or 0.0)) > 1e-9, (
        "rebound time-exit with missing ETH exit must still apply hedge/leg funding"
    )
