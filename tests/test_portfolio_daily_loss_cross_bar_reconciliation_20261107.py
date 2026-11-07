"""Failing-tests-first: portfolio must reconcile realized daily PnL/capacity across bars
without look-ahead. Master risk_state/probe base must reflect closes only when realized
(at exit bar), so later same-day admissions are blocked by max_daily_loss_pct. Same-bar
probe future exits must not leak into sibling admission decisions via master daily state.

Synthetic fixtures only (non-evidence).
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
        max_daily_loss_pct=0.5,
        gross_cap_pct=500.0,
        max_positions=10,
        avoid_downtrend=False,
        enable_liquidation_checks=False,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
    )
    d.update(kw)
    return StrategyConfig(**d)


def test_realized_daily_loss_blocks_future_same_day_admission_after_exit_bar():
    n = 40
    a = [_c(i, 100, 101, 99, 100) for i in range(n)]
    a[6] = _c(6, 100, 101, 80, 80)  # A stopped at bar 6 (entry bar 3->start 4)
    b = [_c(i, 50, 51, 49, 50) for i in range(n)]
    cfg = _cfg(max_daily_loss_pct=0.5)
    sa = Signal(symbol="A", side="long", reason="a", entry_price=100, stop_price=90,
                target_price=120, risk_per_share=10, timestamp="", size_shares=200, signal_index=5)
    sb = Signal(symbol="B", side="long", reason="b", entry_price=50, stop_price=45,
                target_price=60, risk_per_share=5, timestamp="", size_shares=10, signal_index=12)

    def fake(hist, symbol=None, **kw):
        idx = len(hist) - 1
        if idx == 5 and symbol == "A":
            s = copy.copy(sa); s.signal_index = idx; return s
        if idx == 12 and symbol == "B":
            s = copy.copy(sb); s.signal_index = idx; return s
        return None

    with patch("scripts.run_portfolio.generate_signal", side_effect=fake):
        res = run_portfolio_simulation({"A": a, "B": b}, config=cfg, capital=100000.0)
    by = {t["symbol"]: t for t in res["trades"]}
    assert "A" in by, f"A should admit/exit: {res['trades']}"
    assert by["A"]["pnl"] < 0
    assert "B" not in by, f"B admitted after realized daily loss halt: {res['trades']}"
    assert res["risk_state"].realized_pnl < 0
    assert res["risk_state"].daily_loss_limit_hit is True


def test_same_bar_probe_future_loss_does_not_block_sibling_via_master_state():
    """Probe runs to completion for execution realism; a future same-day loss realized by
    the probe must not mutate master daily state used for same-bar sibling admission.
    Both symbols fire at bar 5: A will lose later, B has no loss; B must not be blocked
    by A's probe-exit PnL leaking into master (reservation/cap still applies separately)."""
    n = 40
    a = [_c(i, 100, 101, 99, 100) for i in range(n)]
    a[8] = _c(8, 100, 101, 80, 80)  # A loses later (after decision bar 5)
    b = [_c(i, 50, 51, 49, 50) for i in range(n)]
    b[7] = _c(7, 50, 60, 49, 60)  # B profits
    cfg = _cfg(max_daily_loss_pct=0.5, gross_cap_pct=500.0, max_positions=10)
    sa = Signal(symbol="A", side="long", reason="a", entry_price=100, stop_price=90,
                target_price=120, risk_per_share=10, timestamp="", size_shares=200, signal_index=5)
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
    assert "A" in by and "B" in by, f"same-bar sibling blocked by probe future loss leak: {res['trades']}"


def test_daily_loss_resets_on_new_day_with_timestamp_normalization():
    n = 60
    a = [_c(i, 100, 101, 99, 100, day=1) for i in range(30)] + [_c(i, 100, 101, 99, 100, day=2) for i in range(30, 60)]
    a[6] = _c(6, 100, 101, 80, 80, day=1)   # day 1 loss
    b = copy.deepcopy(a)
    b[6] = _c(6, 100, 101, 99, 100, day=1)  # B no day1 trade from this signal
    cfg = _cfg(max_daily_loss_pct=0.5)
    sa = Signal(symbol="A", side="long", reason="a", entry_price=100, stop_price=90,
                target_price=120, risk_per_share=10, timestamp="", size_shares=200, signal_index=5)
    sc = Signal(symbol="B", side="long", reason="c", entry_price=100, stop_price=90,
                target_price=120, risk_per_share=10, timestamp="", size_shares=1, signal_index=36)
    b[38] = _c(38, 100, 120, 99, 120, day=2)

    def fake(hist, symbol=None, **kw):
        idx = len(hist) - 1
        if idx == 5 and symbol == "A":
            s = copy.copy(sa); s.signal_index = idx; return s
        if idx == 36 and symbol == "B":
            s = copy.copy(sc); s.signal_index = idx; return s
        return None

    with patch("scripts.run_portfolio.generate_signal", side_effect=fake):
        res = run_portfolio_simulation({"A": a, "B": b}, config=cfg, capital=100000.0)
    by = {t["symbol"]: t for t in res["trades"]}
    assert "A" in by
    assert "B" in by, f"day 2 admission blocked after day 1 loss/reset issue: {res['trades']}"
