"""Deterministic spec-fidelity regressions (2026-11-07): long-leg liquidation
sequencing/notional/timing/penalty completeness, including hedge close on the
same liquidation bar and risk_state reconciliation. Extends coverage to the
missing-ETH-exit fallback path for long liquidation hedge close (engine fallback
present; this locks behavior). Synthetic fixtures only; not performance evidence;
no real market data; no look-ahead.
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
# liq: maint 5% + buffer 1% => 6% against long; threshold = 100*(1-0.06)=94.0


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _coin_base(n):
    # Varying closes produce coin realized vol so ETH hedge sizing is nonzero.
    return [_c(f"2025-01-01T{i % 24:02d}:00:00", 100 + (i % 5) * 0.2, 101.8, 98.2, 100 + (i % 5) * 0.2) for i in range(n)]


def _eth_var(n):
    return [_c(f"2025-01-01T{i % 24:02d}:00:00", 2000 + i % 7 * 3, 2008 + i % 7 * 3, 1992 + i % 7 * 3, 2000 + i % 7 * 3) for i in range(n)]


def _sig():
    return Signal(symbol="T", side="long", reason="t", entry_price=ENTRY_PX, stop_price=50.0,
                  target_price=150.0, risk_per_share=1.0, timestamp="2025-01-01T05:00:00",
                  size_shares=SHARES, signal_index=SIGNAL_IDX)


def _cfg(**kw):
    d = dict(
        enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=False,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=0.0, funding_rate_pct_per_hour=RATE, min_daily_volume_usd=0.0,
        time_exit_max_bars=200, enable_liquidation_checks=True,
        liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5,
    )
    d.update(kw)
    return StrategyConfig(**d)


def _make_liquidation_scenario(*, eth_missing=False, liq_bar=8):
    candles = _coin_base(40)
    # Long liquidated at liq_bar (hourly worst price = low). threshold 94.0
    candles[liq_bar] = _c(f"2025-01-01T{liq_bar % 24:02d}:00:00", 96.0, 96.5, 93.0, 93.5)
    eth = _eth_var(40)
    if eth_missing:
        eth[liq_bar] = {"timestamp": f"2025-01-01T{liq_bar % 24:02d}:00:00"}
    return candles, eth, liq_bar


def test_long_liquidation_closes_short_eth_hedge_same_bar_with_correct_funding():
    candles, eth, liq_bar = _make_liquidation_scenario(eth_missing=False, liq_bar=8)
    on = backtest_simple(candles, _sig(), config=_cfg(funding_rate_pct_per_hour=RATE), eth_candles=eth)
    off = backtest_simple(candles, _sig(), config=_cfg(funding_rate_pct_per_hour=0.0), eth_candles=eth)

    assert on.exit_reason == "liquidated"
    assert on.bars_held == liq_bar - SIGNAL_IDX + 1  # 4 hours
    assert all((t.get("side") != "short" or t.get("reason") == "stopped") for t in (on.trades or [])
               if t.get("reason") in ("short_target", "short_stop", "short_time_exit"))
    assert not any(t.get("side") == "short" and "rebound" in str(t.get("reason", "")).lower() for t in (on.trades or []))
    # Only the liquidated long leg trade log expected (no rebound short)
    assert len(on.trades or []) == 1 and on.trades[0]["side"] == "long" and on.trades[0]["reason"] == "liquidated"

    assert on.hedge_side == "short" and (on.hedge_size or 0) > 0
    assert on.hedge_entry and on.hedge_entry > 0
    # Same-bar close: hedge_exit corresponds to ETH bar at liq_bar (close/open)
    eth_exit_ref = eth[liq_bar].get("close") or eth[liq_bar].get("open")
    assert on.hedge_exit == float(eth_exit_ref)  # no slippage/commission

    hours = on.bars_held
    coin_notional = ENTRY_PX * SHARES
    coin_cost = coin_notional * hours * (RATE / 100.0)
    hedge_notional = on.hedge_entry * on.hedge_size
    hedge_benefit = hedge_notional * hours * (RATE / 100.0)
    expected_net_funding = -coin_cost + hedge_benefit
    actual_net = (on.total_pnl or 0.0) - (off.total_pnl or 0.0)
    assert abs(actual_net - expected_net_funding) < 1e-6, (actual_net, expected_net_funding)

    # Liquidation penalty applied once to liquidated leg (long coin notional).
    penalty = 0.5 / 100.0 * coin_notional
    # Long PnL components: (exit-entry)*shares - penalty - coin_funding; exit at low 93.0
    expected_long_pnl = (93.0 - 100.0) * SHARES - penalty - coin_cost
    assert abs((on.pnl or 0.0) - expected_long_pnl) < 1e-6, (on.pnl, expected_long_pnl)


def test_long_liquidation_no_rebound_short_opened():
    candles, eth, liq_bar = _make_liquidation_scenario(eth_missing=False, liq_bar=8)
    on = backtest_simple(candles, _sig(), config=_cfg(funding_rate_pct_per_hour=RATE, enable_rebound_short=True), eth_candles=eth)
    assert on.exit_reason == "liquidated"
    sides = [t.get("side") for t in (on.trades or [])]
    reasons = [t.get("reason") for t in (on.trades or [])]
    assert "short" not in sides, (sides, reasons)
    assert all("rebound" not in str(r).lower() and "short" not in str(r).lower() for r in reasons), reasons


def test_long_liquidation_missing_eth_exit_fallback_still_applies_hedge_funding_and_reconciles():
    candles, eth_missing, liq_bar = _make_liquidation_scenario(eth_missing=True, liq_bar=8)
    eth_valid = _eth_var(40)
    on = backtest_simple(candles, _sig(), config=_cfg(funding_rate_pct_per_hour=RATE), eth_candles=eth_missing)
    off = backtest_simple(candles, _sig(), config=_cfg(funding_rate_pct_per_hour=0.0), eth_candles=eth_missing)
    valid = backtest_simple(candles, _sig(), config=_cfg(funding_rate_pct_per_hour=RATE), eth_candles=eth_valid)

    assert on.exit_reason == "liquidated"
    assert on.hedge_side == "short" and (on.hedge_size or 0) > 0
    # Fallback: exit accounting uses entry when ETH exit data absent
    assert on.hedge_exit == on.hedge_entry

    hours = on.bars_held
    coin_notional = ENTRY_PX * SHARES
    coin_cost = coin_notional * hours * (RATE / 100.0)
    hedge_notional = on.hedge_entry * on.hedge_size
    hedge_benefit = hedge_notional * hours * (RATE / 100.0)
    expected_net = -coin_cost + hedge_benefit
    actual_net = (on.total_pnl or 0.0) - (off.total_pnl or 0.0)
    assert abs(actual_net - expected_net) < 1e-6, (actual_net, expected_net)
    assert abs((on.total_pnl or 0.0) - (off.total_pnl or 0.0)) > 1e-12
    # Sanity: valid ETH exit path also applies funding (may differ by hedge price pnl)
    assert abs((valid.total_pnl or 0.0) - (backtest_simple(candles, _sig(), config=_cfg(funding_rate_pct_per_hour=0.0), eth_candles=eth_valid).total_pnl or 0.0) - expected_net) < 1e-6


def test_long_liquidation_risk_state_exposure_notional_reconciled():
    candles, eth, liq_bar = _make_liquidation_scenario(eth_missing=False, liq_bar=8)
    rs = RiskState()
    rs.date = "2025-01-01T05:00:00"
    res = backtest_simple(candles, _sig(), config=_cfg(funding_rate_pct_per_hour=RATE), risk_state=rs, eth_candles=eth)
    assert res.exit_reason == "liquidated"
    assert rs.open_positions == 0
    assert math.isclose(rs.gross_exposure, 0.0, abs_tol=1e-9)
    assert rs.open_position_notionals == []
    # realized pnl updated by long-leg pnl (engine applies pnl arg)
    assert rs.realized_pnl == res.pnl


def test_long_liquidation_hedge_notional_and_hours_deterministic():
    candles, eth, liq_bar = _make_liquidation_scenario(eth_missing=False, liq_bar=10)
    on = backtest_simple(candles, _sig(), config=_cfg(funding_rate_pct_per_hour=RATE), eth_candles=eth)
    hours = liq_bar - SIGNAL_IDX + 1
    assert on.bars_held == hours
    assert on.exit_timestamp == candles[liq_bar]["timestamp"]
    assert on.hedge_side == "short"
    assert on.hedge_size > 0 and on.hedge_entry > 0
    # hedge sizing is coin_vol/eth_vol * coin_value capped 3x, computed from history at entry (no look-ahead)
    assert on.hedge_entry * on.hedge_size <= ENTRY_PX * SHARES * 3.0 + 1e-9
