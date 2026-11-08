"""Regression lock (2026-11-08, 2g): same-bar probe runs to completion for
execution realism, but its LATER-EXIT *positive* realized PnL and capacity
release must NOT leak into sibling admission decisions. Reservation overlay only
governs same-bar concurrent 120% cap / max_positions / equal-share cuts. Master
realized PnL/halt reflect only exits reconciled at/through bar i.

Extends test_portfolio_daily_loss_cross_bar_reconciliation_20261107.py (loss/halt)
to the positive-PnL/capacity-release side. Synthetic fixtures only (non-evidence).
"""
from __future__ import annotations

import copy
from unittest.mock import patch

from scripts.run_portfolio import run_portfolio_simulation
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(i, o, h, l, cl, v=5_000_000.0, day=1):
    return {"timestamp": f"2026-01-{day:02d}T{i % 24:02d}:00:00Z", "open": o, "high": h, "low": l, "close": cl, "volume": v}


def _cfg(**kw):
    d = dict(
        use_rsi_trigger=False,
        enable_rebound_short=False,
        enable_eth_hedge=False,
        min_daily_volume_usd=0.0,
        entry_next_bar=True,
        max_daily_loss_pct=5.0,  # non-blocking for these scenarios
        gross_cap_pct=120.0,
        max_positions=2,  # tight: third sibling tests capacity-reservation behavior
        avoid_downtrend=False,
        enable_liquidation_checks=False,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
    )
    d.update(kw)
    return StrategyConfig(**d)


def test_same_bar_probe_later_positive_exit_does_not_free_capacity_for_sibling():
    """A,B,C fire same decision bar. max_positions=2, gross cap tight. A and B admit
    in deepest-crash order; A's probe exits later with PROFIT (capacity would free in
    naive probe-committed model). C must be blocked by reservation overlay (A,B still
    reserved for same-bar admission), not admitted because A's future profit/exit
    leaked. Final state must reconcile occupancy/notional/capacity cleanly."""
    n = 50
    a = [_c(i, 100, 101, 99, 100) for i in range(n)]
    a[8] = _c(8, 100, 120, 99, 120)  # A hits target later (profit), exits bar 8
    b = [_c(i, 50, 51, 49, 50) for i in range(n)]
    b[12] = _c(12, 50, 60, 49, 60)   # B exits later
    c = [_c(i, 30, 31, 29, 30) for i in range(n)]
    c[9] = _c(9, 30, 36, 29, 36)    # C would profit if admitted — must be blocked
    sa = Signal(symbol="A", side="long", reason="a", entry_price=100, stop_price=90,
                target_price=120, risk_per_share=10, timestamp="", size_shares=10, signal_index=5)
    sb = Signal(symbol="B", side="long", reason="b", entry_price=50, stop_price=45,
                target_price=60, risk_per_share=5, timestamp="", size_shares=10, signal_index=5)
    sc = Signal(symbol="C", side="long", reason="c", entry_price=30, stop_price=27,
                target_price=36, risk_per_share=3, timestamp="", size_shares=10, signal_index=5)

    def fake(hist, symbol=None, **kw):
        idx = len(hist) - 1
        if idx == 5 and symbol == "A":
            s = copy.copy(sa); s.signal_index = idx; return s
        if idx == 5 and symbol == "B":
            s = copy.copy(sb); s.signal_index = idx; return s
        if idx == 5 and symbol == "C":
            s = copy.copy(sc); s.signal_index = idx; return s
        return None

    with patch("scripts.run_portfolio.generate_signal", side_effect=fake):
        res = run_portfolio_simulation({"A": a, "B": b, "C": c}, config=_cfg(), capital=100000.0)
    by = {t["symbol"]: t for t in res["trades"]}
    assert "A" in by and "B" in by, f"expected A,B admitted: {res['trades']}"
    assert "C" not in by, (
        f"C admitted despite max_positions reservation (probe positive-exit/capacity leak?): {res['trades']}"
    )
    assert by["A"]["pnl"] > 0, f"A should be profitable for this scenario: {by['A']}"
    assert res["final_open_positions"] == 0
    assert abs(float(res["final_gross_exposure"])) < 1e-9
    rs = res["risk_state"]
    assert getattr(rs, "open_positions", -1) == 0
    assert list(getattr(rs, "open_position_notionals", ["leak"])) == []
    assert abs(float(getattr(rs, "gross_exposure", -1.0))) < 1e-9


def test_same_bar_probe_positive_pnl_does_not_distort_sibling_admission_or_master_state():
    """Probe positive PnL from future exit must not distort master realized state in a
    way that affects siblings. A profits later (large), B has small loss later — both
    fire same bar; both should admit under non-binding cap/positions. Reservation
    overlay governs admission; probe future PnL is not committed to master for
    same-bar sibling decisions."""
    n = 50
    a = [_c(i, 100, 101, 99, 100) for i in range(n)]
    a[9] = _c(9, 100, 150, 99, 150)
    b = [_c(i, 50, 51, 49, 50) for i in range(n)]
    b[9] = _c(9, 50, 51, 45, 45)
    cfg = _cfg(max_positions=10, gross_cap_pct=500.0, max_daily_loss_pct=0.5)
    sa = Signal(symbol="A", side="long", reason="a", entry_price=100, stop_price=90,
                target_price=150, risk_per_share=10, timestamp="", size_shares=100, signal_index=5)
    sb = Signal(symbol="B", side="long", reason="b", entry_price=50, stop_price=45,
                target_price=60, risk_per_share=5, timestamp="", size_shares=10, signal_index=5)

    def fake(hist, symbol=None, **kw):
        idx = len(hist) - 1
        if idx == 5 and symbol == "A":
            s = copy.copy(sa); s.signal_index = idx; return s
        if idx == 5 and symbol == "B":
            s = copy.copy(sb); s.signal_index = idx; return s
        return None

    with patch("scripts.run_portfolio.generate_signal", side_effect=fake):
        res = run_portfolio_simulation({"A": a, "B": b}, config=cfg, capital=100000.0)
    by = {t["symbol"]: t for t in res["trades"]}
    assert "A" in by and "B" in by, f"same-bar sibling affected by probe PnL/state leak: {res['trades']}"
    assert by["A"]["pnl"] > 0 and by["B"]["pnl"] < 0
    assert res["final_open_positions"] == 0
    assert abs(float(res["final_gross_exposure"])) < 1e-9
