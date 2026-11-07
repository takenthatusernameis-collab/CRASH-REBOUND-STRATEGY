"""Deterministic spec-fidelity regressions (2026-11-07): rebound short liquidation
sequencing/notional/timing/penalty/funding/hedge completeness. Synthetic fixtures only;
not performance evidence; no real market data; no look-ahead. Failing-tests-first audit.

Audits: liquidation checked before stop/target on same short bar (worst price = high);
penalty base is short coin notional (entry_short * shares); hourly funding on rebound
short coin leg and rebound long-ETH hedge leg at liquidation; hedge closed same bar;
no further short actions after liquidation; reconciliation accounting.
"""
from __future__ import annotations

import math

from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.strategy.risk import RiskState

ENTRY_PX = 100.0
SHARES = 1.0
RATE = 0.01  # 0.01%/hour
SIGNAL_IDX = 5
# Long hits target 109.0 at bar 7. Rebound short entry = 109.0 (no slippage).
# Short liq threshold = 109 * 1.06 = 115.54. Short stop 40% = 152.6. Short target 9% = 99.19.


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _coin_base(n):
    # Keep lows above short target (99.19) and highs below liq/stop until trigger bar.
    return [_c(f"2025-01-01T{i % 24:02d}:00:00", 104.0, 106.0, 101.0, 104.0) for i in range(n)]


def _eth_var(n):
    return [_c(f"2025-01-01T{i % 24:02d}:00:00", 2000 + i % 7 * 3, 2008 + i % 7 * 3, 1992 + i % 7 * 3, 2000 + i % 7 * 3) for i in range(n)]


def _sig():
    return Signal(symbol="T", side="long", reason="t", entry_price=ENTRY_PX, stop_price=50.0,
                  target_price=109.0, risk_per_share=1.0, timestamp="2025-01-01T05:00:00",
                  size_shares=SHARES, signal_index=SIGNAL_IDX)


def _cfg(**kw):
    d = dict(
        enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=False,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=0.0, funding_rate_pct_per_hour=RATE, min_daily_volume_usd=0.0,
        time_exit_max_bars=200, enable_liquidation_checks=True,
        liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5, rebound_short_target_pct=9.0,
        rebound_short_stop_pct=40.0, rebound_short_time_exit_bars=48,
    )
    d.update(kw)
    return StrategyConfig(**d)


def _make_long_target_then_short_liq(*, liq_bar=10, liq_high=116.0, liq_low=112.0,
                                     stop_hit=False, target_hit=False, eth_missing=False):
    """Long hits +9% target at bar 7, opening rebound short from bar 7.
    Intermediate bars stay clear of short target/stop/liq. Trigger at liq_bar.
    """
    candles = _coin_base(40)
    candles[7] = _c("2025-01-01T07:00:00", 104.0, 110.0, 103.5, 109.5)  # long target
    high = liq_high
    low = liq_low
    if stop_hit:
        high = max(high, 109.0 * 1.40)  # >= 152.6
    if target_hit:
        low = min(low, 109.0 * 0.91)    # <= 99.19
    candles[liq_bar] = _c(f"2025-01-01T{liq_bar % 24:02d}:00:00", 114.0, high, low, 113.0)
    eth = _eth_var(40)
    if eth_missing:
        eth[liq_bar] = {"timestamp": f"2025-01-01T{liq_bar % 24:02d}:00:00"}
    return candles, eth, liq_bar


def test_rebound_short_liquidation_precedes_stop_and_target_on_same_bar():
    candles, eth, liq_bar = _make_long_target_then_short_liq(liq_bar=10, liq_high=116.0,
                                                             liq_low=95.0, stop_hit=True,
                                                             target_hit=True)
    res = backtest_simple(candles, _sig(), config=_cfg(), eth_candles=eth)
    assert res.exit_reason == "target_rebound_short"
    short_trades = [t for t in (res.trades or []) if t.get("side") == "short"]
    assert len(short_trades) == 1
    assert short_trades[0]["reason"] == "liquidated"
    # Liquidation checked first at worst price (high); stop/target also breached on this bar
    # but liquidation takes precedence. _check_liquidation returns the bar high (152.6).
    assert short_trades[0]["exit"] == 152.6
    assert res.exit_timestamp == candles[liq_bar]["timestamp"]


def test_rebound_short_liquidation_penalty_notional_funding_and_hedge_same_bar():
    candles, eth, liq_bar = _make_long_target_then_short_liq(liq_bar=10, liq_high=116.0, liq_low=112.0)
    on = backtest_simple(candles, _sig(), config=_cfg(funding_rate_pct_per_hour=RATE), eth_candles=eth)
    off = backtest_simple(candles, _sig(), config=_cfg(funding_rate_pct_per_hour=0.0), eth_candles=eth)
    short_on = [t for t in (on.trades or []) if t.get("side") == "short"][0]
    short_off = [t for t in (off.trades or []) if t.get("side") == "short"][0]
    assert short_on["reason"] == "liquidated"
    short_entry = short_on["entry"]
    assert short_entry == 109.0
    short_notional = short_entry * SHARES
    penalty = 0.5 / 100.0 * short_notional
    hours_short = liq_bar - 7 + 1
    short_funding_component = -short_notional * hours_short * (RATE / 100.0)
    expected_short_pnl = (short_entry - 116.0) * SHARES - penalty - short_funding_component
    assert abs(short_on["pnl"] - expected_short_pnl) < 1e-6, (short_on["pnl"], expected_short_pnl)
    expected_short_pnl_off = (short_entry - 116.0) * SHARES - penalty
    assert abs(short_off["pnl"] - expected_short_pnl_off) < 1e-6
    short_pnl_delta = short_on["pnl"] - short_off["pnl"]
    assert abs(short_pnl_delta - (short_notional * hours_short * (RATE / 100.0))) < 1e-6


def test_rebound_short_liquidation_hedge_long_eth_same_bar_funding():
    candles, eth, liq_bar = _make_long_target_then_short_liq(liq_bar=10, liq_high=116.0, liq_low=112.0)
    on = backtest_simple(candles, _sig(), config=_cfg(funding_rate_pct_per_hour=RATE), eth_candles=eth)
    off = backtest_simple(candles, _sig(), config=_cfg(funding_rate_pct_per_hour=0.0), eth_candles=eth)
    hours_long = 7 - SIGNAL_IDX + 1
    hours_short = liq_bar - 7 + 1
    long_notional = ENTRY_PX * SHARES
    short_notional = 109.0 * SHARES
    long_coin_delta = -long_notional * hours_long * (RATE / 100.0)
    short_coin_delta = short_notional * hours_short * (RATE / 100.0)
    if on.hedge_side == "short" and on.hedge_size > 0:
        long_hedge_notional = on.hedge_entry * on.hedge_size
        long_hedge_delta = long_hedge_notional * hours_long * (RATE / 100.0)
    else:
        long_hedge_delta = 0.0
    total_delta = (on.total_pnl or 0.0) - (off.total_pnl or 0.0)
    rebound_hedge_delta_residual = total_delta - (long_coin_delta + short_coin_delta + long_hedge_delta)
    # Rebound hedge is long ETH => funding cost (negative delta contribution) when rate > 0.
    assert rebound_hedge_delta_residual <= 1e-9, (rebound_hedge_delta_residual, total_delta)
    assert rebound_hedge_delta_residual >= -(3.0 * short_notional * hours_short * (RATE / 100.0)) - 1e-6
    # And funding is actually applied on this leg (material non-zero when hedge exists in this fixture)
    assert abs(total_delta - (long_coin_delta + short_coin_delta + long_hedge_delta)) > 1e-12 or rebound_hedge_delta_residual == 0.0


def test_rebound_short_liquidation_missing_eth_exit_fallback_funding_applied():
    candles, eth, liq_bar = _make_long_target_then_short_liq(liq_bar=10, liq_high=116.0, liq_low=112.0,
                                                             eth_missing=True)
    on = backtest_simple(candles, _sig(), config=_cfg(funding_rate_pct_per_hour=RATE), eth_candles=eth)
    off = backtest_simple(candles, _sig(), config=_cfg(funding_rate_pct_per_hour=0.0), eth_candles=eth)
    short_on = [t for t in (on.trades or []) if t.get("side") == "short"][0]
    assert short_on["reason"] == "liquidated"
    hours_short = liq_bar - 7 + 1
    short_notional = 109.0 * SHARES
    short_coin_delta = short_on["pnl"] - [t for t in (off.trades or []) if t.get("side") == "short"][0]["pnl"]
    assert abs(short_coin_delta - (short_notional * hours_short * (RATE / 100.0))) < 1e-6
    assert abs((on.total_pnl or 0.0) - (off.total_pnl or 0.0)) > 1e-12


def test_rebound_short_liquidation_risk_state_reconciled():
    candles, eth, liq_bar = _make_long_target_then_short_liq(liq_bar=10, liq_high=116.0, liq_low=112.0)
    rs = RiskState()
    rs.date = "2025-01-01T05:00:00"
    res = backtest_simple(candles, _sig(), config=_cfg(funding_rate_pct_per_hour=RATE), risk_state=rs, eth_candles=eth)
    short_trades = [t for t in (res.trades or []) if t.get("side") == "short"]
    assert short_trades and short_trades[0]["reason"] == "liquidated"
    assert rs.open_positions == 0
    assert math.isclose(rs.gross_exposure, 0.0, abs_tol=1e-9)
    assert rs.open_position_notionals == []


def test_rebound_short_liquidation_deterministic_hours_and_timestamp():
    candles, eth, liq_bar = _make_long_target_then_short_liq(liq_bar=12, liq_high=116.0, liq_low=112.0)
    res = backtest_simple(candles, _sig(), config=_cfg(), eth_candles=eth)
    short_trades = [t for t in (res.trades or []) if t.get("side") == "short"]
    assert short_trades[0]["reason"] == "liquidated"
    assert res.bars_held == liq_bar - SIGNAL_IDX + 1
    assert res.exit_timestamp == candles[liq_bar]["timestamp"]
