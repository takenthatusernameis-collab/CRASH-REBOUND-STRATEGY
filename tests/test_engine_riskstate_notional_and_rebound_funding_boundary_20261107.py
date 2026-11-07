"""Material spec-fidelity hardening (2026-11-07): risk-state notional close
consistency on all long-leg terminal exits and rebound-short funding hours.

Failing-tests-first targets:
- Long final time-exit must close risk_state with the opened notional so
  gross_exposure/open_position_notionals cannot leak (parity with other exits).
- Rebound-short funding hours must remain consistent across loop exits and the
  no-break final fallback (contract lock).
"""
import math
from types import SimpleNamespace

from src.backtest.engine import _apply_funding_pnl, backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.risk import RiskState


def _bar(ts, o, h, l, c, v=1_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _signal(entry, stop, target, shares=2.0, signal_index=0):
    return SimpleNamespace(
        symbol="TEST",
        side="long",
        reason="t",
        entry_price=entry,
        stop_price=stop,
        target_price=target,
        risk_per_share=abs(entry - stop),
        timestamp="t0",
        size_shares=shares,
        signal_index=signal_index,
    )


def test_long_final_time_exit_closes_risk_state_with_notional():
    """Final-candle fallback time exit must release the opened notional."""
    cfg = StrategyConfig(
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
        time_exit_max_bars=999,
        entry_next_bar=False,
        enable_eth_hedge=False,
        enable_rebound_short=False,
        funding_rate_pct_per_hour=0.0,
    )
    candles = [
        _bar("t0", 100, 101, 99, 100),  # signal/entry
        _bar("t1", 100, 102, 99, 101),
        _bar("t2", 101, 102, 100, 101),  # final fallback exit
    ]
    sig = _signal(entry=100.0, stop=50.0, target=500.0, shares=2.0, signal_index=0)
    rs = RiskState()
    res = backtest_simple(candles, sig, config=cfg, risk_state=rs)
    assert res.exit_reason == "time_exit"
    assert rs.open_positions == 0
    assert math.isclose(rs.gross_exposure, 0.0, abs_tol=1e-9), (rs.gross_exposure, rs.open_position_notionals)
    assert list(rs.open_position_notionals) == [], rs.open_position_notionals


def test_rebound_short_no_break_fallback_funding_hours_consistent_with_loop():
    """No-break short fallback funding hours match loop path semantics."""
    cfg = StrategyConfig(
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
        entry_next_bar=False,
        enable_eth_hedge=False,
        enable_rebound_short=True,
        rebound_short_time_exit_bars=999,
        rebound_short_target_pct=9.0,
        rebound_short_stop_pct=40.0,
        funding_rate_pct_per_hour=0.1,
    )
    candles = [
        _bar("t0", 100, 101, 99, 100),  # long entry
        _bar("t1", 100, 110, 100, 109),  # long target -> rebound short opens at this bar
        _bar("t2", 109, 111, 108, 110),
        _bar("t3", 110, 111, 109, 110),  # no break, final fallback
    ]
    sig = _signal(entry=100.0, stop=50.0, target=109.0, shares=1.0, signal_index=0)
    res = backtest_simple(candles, sig, config=cfg)
    assert res.exit_reason == "target_rebound_short"
    short = [t for t in (res.trades or []) if t.get("side") == "short"]
    assert len(short) == 1
    short_entry = short[0]["entry"]
    # short_start_idx = 1 (long target bar). Loop would check 2,3 and exit at
    # 3 with hours 3-1+1=3. Fallback uses len(candles)-short_start_idx = 3.
    expected_hours = 3.0
    notional = short_entry * 1.0
    short_funding = _apply_funding_pnl(notional, expected_hours, cfg.funding_rate_pct_per_hour, side="short")
    gross_pnl = (short_entry - short[0]["exit"]) * 1.0
    assert math.isclose(short[0]["pnl"], gross_pnl - short_funding, rel_tol=0, abs_tol=1e-9), (
        short[0], gross_pnl, short_funding, expected_hours
    )
