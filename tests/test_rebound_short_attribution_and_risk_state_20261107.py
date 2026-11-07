"""Deterministic spec-fidelity regressions (2026-11-07): rebound-short TradeResult
attribution fields (rebound_short_pnl / rebound_hedge_pnl / rebound_hedge_*), risk_state
notional registration for the rebound short leg, and the same-bar stop-vs-target lock.

Synthetic fixtures only; not performance evidence; no real market data; no look-ahead.
Failing-tests-first: attribution fields did not surface the rebound legs before this session.
"""
import math

from src.backtest.engine import backtest_simple, TradeResult
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.strategy.risk import RiskState

ENTRY_PX = 100.0
SHORT_ENTRY_PX = 109.0  # long +9% target -> rebound short entry
SHORT_TARGET_PX = SHORT_ENTRY_PX * 0.91  # 99.19
SHORT_STOP_PX = SHORT_ENTRY_PX * 1.40  # 152.6
SHARES = 1.0
RATE = 0.01  # 0.01%/hour
SIGNAL_IDX = 5
SHORT_HOURS = 2  # bar 6 -> bar 7


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _eth_volatile(n, base=100.0):
    """ETH with oscillation so realized vol > 0 (hedge sizing requires eth_vol > 0)."""
    out = []
    for i in range(n):
        c = base + (1.0 if i % 2 == 0 else -1.0)
        out.append(_c(f"2025-01-01T{i % 24:02d}:00:00", c, c + 1.0, c - 1.0, c))
    return out


def _sig():
    return Signal(
        symbol="T", side="long", reason="t",
        entry_price=ENTRY_PX, stop_price=ENTRY_PX * 0.5, target_price=ENTRY_PX * 1.09,
        risk_per_share=1.0, timestamp="2025-01-01T05:00:00", size_shares=SHARES,
        signal_index=SIGNAL_IDX,
    )


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


def _long_target_then_short_target(*, n=40):
    """Long hits +9% target at bar 6 (entry 109), rebound short exits at target bar 7."""
    candles = [_c(f"2025-01-01T{i:02d}:00:00", 100.0, 101.0, 99.0, 100.0) for i in range(6)]
    candles.append(_c("2025-01-01T06:00:00", 100.0, 110.0, 99.0, 109.0))  # long target
    candles.append(_c("2025-01-01T07:00:00", 109.0, 110.0, 99.0, 99.19))  # short target
    for i in range(8, n):
        candles.append(_c(f"2025-01-01T{i:02d}:00:00", 100.0, 101.0, 99.0, 100.0))
    return candles, _eth_volatile(n)


def test_rebound_short_attribution_fields_populated():
    """rebound_short_pnl / rebound_hedge_pnl / rebound_hedge_* must surface each rebound leg."""
    candles, eth = _long_target_then_short_target()
    res = backtest_simple(candles, _sig(), config=_cfg(), eth_candles=eth)
    short_trades = [t for t in (res.trades or []) if t.get("side") == "short"]
    assert short_trades, "rebound short must open"
    assert short_trades[0]["reason"] == "target"
    # Short coin price PnL: (109 - 99.19) * 1 = 9.81; short receives funding benefit 109*2*0.0001=0.0218.
    expected_short_px_pnl = (SHORT_ENTRY_PX - SHORT_TARGET_PX) * SHARES
    short_funding_benefit = SHORT_ENTRY_PX * SHARES * SHORT_HOURS * (RATE / 100.0)
    expected_rebound_short_pnl = expected_short_px_pnl + short_funding_benefit
    assert abs(res.rebound_short_pnl - expected_rebound_short_pnl) < 1e-6, (
        res.rebound_short_pnl, expected_rebound_short_pnl
    )
    assert res.rebound_hedge_side == "long"
    assert res.rebound_hedge_size > 0.0
    assert res.rebound_hedge_entry > 0.0
    assert res.rebound_hedge_exit > 0.0
    # Rebound hedge is long ETH => pays funding (cost) when rate > 0.
    assert res.rebound_hedge_pnl <= 0.0
    assert res.exit_reason == "target_rebound_short"


def test_rebound_short_coin_leg_funding_isolated():
    """Isolate rebound short coin-leg funding: with no ETH hedge, on/off rebound_short_pnl
    delta equals exactly the short funding benefit (long leg funding cancels via total_pnl)."""
    candles, eth = _long_target_then_short_target()
    on = backtest_simple(candles, _sig(), config=_cfg(enable_eth_hedge=False), eth_candles=None)
    off = backtest_simple(candles, _sig(), config=_cfg(enable_eth_hedge=False, funding_rate_pct_per_hour=0.0), eth_candles=None)
    short_on = [t for t in (on.trades or []) if t.get("side") == "short"][0]
    short_off = [t for t in (off.trades or []) if t.get("side") == "short"][0]
    assert short_on["reason"] == "target" and short_off["reason"] == "target"
    short_funding_benefit = SHORT_ENTRY_PX * SHARES * SHORT_HOURS * (RATE / 100.0)
    assert abs((on.rebound_short_pnl or 0.0) - (off.rebound_short_pnl or 0.0) - short_funding_benefit) < 1e-6, (
        on.rebound_short_pnl, off.rebound_short_pnl, short_funding_benefit
    )
    # total_pnl delta = short funding benefit - long funding cost (long leg identical except funding).
    long_funding_cost = ENTRY_PX * SHARES * SHORT_HOURS * (RATE / 100.0)
    expected_total_delta = short_funding_benefit - long_funding_cost
    total_delta = (on.total_pnl or 0.0) - (off.total_pnl or 0.0)
    assert abs(total_delta - expected_total_delta) < 1e-6, (total_delta, expected_total_delta)


def test_risk_state_rebound_short_cleared_on_close():
    """After rebound short closes, risk_state must be fully cleared (flat, notional removed)."""
    candles, eth = _long_target_then_short_target()
    rs = RiskState()
    rs.date = "2025-01-01T05:00:00"
    res = backtest_simple(candles, _sig(), config=_cfg(), risk_state=rs, eth_candles=eth)
    short_trades = [t for t in (res.trades or []) if t.get("side") == "short"]
    assert short_trades and short_trades[0]["reason"] == "target"
    assert rs.open_positions == 0
    assert math.isclose(rs.gross_exposure, 0.0, abs_tol=1e-9)
    assert rs.open_position_notionals == []


def test_risk_state_rebound_short_notional_added_and_removed():
    """Direct risk_state contract: opened short notional is tracked and removed on close."""
    rs = RiskState()
    rs.date = "2025-01-01T05:00:00"
    notional = SHORT_ENTRY_PX * SHARES
    rs.apply_trade("2025-01-01T06:00:00", 0.0, opened=True, closed=False, notional=notional)
    assert rs.open_positions == 1
    assert math.isclose(rs.gross_exposure, notional, abs_tol=1e-9)
    assert rs.open_position_notionals == [notional]
    rs.apply_trade("2025-01-01T07:00:00", 5.0, opened=False, closed=True, notional=notional)
    assert rs.open_positions == 0
    assert math.isclose(rs.gross_exposure, 0.0, abs_tol=1e-9)
    assert rs.open_position_notionals == []
    assert math.isclose(rs.realized_pnl, 5.0, abs_tol=1e-9)


def test_same_bar_stop_before_target():
    """Short stop breached (high >= stop), target not breached. Stop is checked before
    target in the short loop, so stop must fire."""
    candles = [_c(f"2025-01-01T{i:02d}:00:00", 100.0, 101.0, 99.0, 100.0) for i in range(6)]
    candles.append(_c("2025-01-01T06:00:00", 100.0, 110.0, 99.0, 109.0))  # long target
    # Bar 7: high 160 >= stop 152.6; low 108 > target 99.19 (target NOT breached).
    candles.append(_c("2025-01-01T07:00:00", 109.0, 160.0, 108.0, 109.0))
    cfg = _cfg(enable_liquidation_checks=False)
    res = backtest_simple(candles, _sig(), config=cfg)
    short_trades = [t for t in (res.trades or []) if t.get("side") == "short"]
    assert short_trades, "rebound short must open and exit"
    assert short_trades[0]["reason"] == "stopped", short_trades[0]["reason"]
    assert res.exit_reason == "target_rebound_short"


def test_same_bar_stop_and_target_both_breached_stop_first():
    """Same bar: short stop (high 160 >= 152.6) and target (low 99 <= 99.19) both breached,
    no liquidation. Stop is checked before target in the short loop, so stop must fire."""
    candles = [_c(f"2025-01-01T{i:02d}:00:00", 100.0, 101.0, 99.0, 100.0) for i in range(6)]
    candles.append(_c("2025-01-01T06:00:00", 100.0, 110.0, 99.0, 109.0))  # long target
    # Bar 7: high 160 (>= stop) AND low 99.0 (<= target). Stop checked first.
    candles.append(_c("2025-01-01T07:00:00", 109.0, 160.0, 99.0, 109.0))
    cfg = _cfg(enable_liquidation_checks=False)
    res = backtest_simple(candles, _sig(), config=cfg)
    short_trades = [t for t in (res.trades or []) if t.get("side") == "short"]
    assert short_trades, "rebound short must exit"
    assert short_trades[0]["reason"] == "stopped", short_trades[0]["reason"]


def test_trade_result_defaults_are_zero_without_rebound():
    """TradeResult rebound fields default to 0.0 / None when no rebound short occurs."""
    candles = [_c(f"2025-01-01T{i:02d}:00:00", 100.0, 101.0, 99.0, 109.0) for i in range(3)]
    res = backtest_simple(candles, _sig(), config=_cfg(enable_rebound_short=False, enable_eth_hedge=False))
    assert res.rebound_short_pnl == 0.0
    assert res.rebound_hedge_pnl == 0.0
    assert res.rebound_hedge_side is None
    assert res.rebound_hedge_size == 0.0
    assert isinstance(res, TradeResult)
