"""B-rem2: same-decision-bar multi-admission where a prior probe's rebound-short
max_live_coin_notional must reserve portfolio capacity (not long-entry notional).

Failing-tests-first (2026-11-09). Synthetic fixtures only (non-evidence).

Scenario: A and B both signal on the same decision bar. A is deeper (probed first).
A's long hits +9% target on the entry bar and opens a rebound short at ~109 (held
for time exit). A's max_live_coin_notional = 10900 > long-entry 10000. B admits
on the same decision bar after A's probe returns. The portfolio reservation for A
must use max_live_coin_notional (10900), so B's admission sees gross pressure
(10900 + 1500 > 12000 cap) and is cut — not admitted uncut as if A were reserved
at 10000.
"""
from __future__ import annotations

import copy
from unittest.mock import patch

from scripts.run_portfolio import run_portfolio_simulation
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(ts, o, c, h=None, l=None, v=1_500_000.0):
    h = max(o, c) * 1.002 if h is None else h
    l = min(o, c) * 0.998 if l is None else l
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _mk_a_target_then_hold_short():
    """A: signal at decision bar 25, entry at bar 26 open=100. Bar 26 closes at 110,
    high reaches 111 >= 109 target -> rebound short opens at 109 (entry_next_bar).
    Short holds flat until time exit."""
    candles = []
    for i in range(90):
        ts = f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z"
        if i == 25:
            candles.append(_c(ts, 100.0, 90.0, 100.0, 88.0))
        elif i == 26:
            candles.append(_c(ts, 100.0, 110.0, 111.0, 99.0))
        elif 27 <= i <= 74:
            candles.append(_c(ts, 108.0, 108.0, 108.5, 107.5))
        else:
            candles.append(_c(ts, 100.0, 100.0, 101.0, 99.0))
    return candles


def _mk_b_flat_admits_bar25():
    a = _mk_a_target_then_hold_short()
    out = []
    for i, c in enumerate(a):
        if i >= 26:
            c = dict(c, open=100.0, close=100.0, high=100.5, low=99.5)
        out.append(c)
    return out


def _cfg():
    return StrategyConfig(
        use_rsi_trigger=False,
        enable_rebound_short=True,
        enable_eth_hedge=False,
        entry_next_bar=True,
        min_daily_volume_usd=1_000_000,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
        funding_rate_pct_per_hour=0.0,
        avoid_downtrend=False,
        gross_cap_pct=120.0,
        max_positions=10,
        rebound_short_time_exit_bars=48,
        rebound_short_stop_pct=40.0,
        time_exit_max_bars=10,
    )


def test_same_bar_admission_sees_prior_probes_rebound_short_max_live_notional():
    """Capital 10000, cap 12000. A: 100 shares @100 long entry = 10000 notional;
    hits +9% target same entry bar -> rebound short opens at 109, max_live = 10900.
    B signals same bar as A (bar 25), wants 15 shares @100 = 1500.

    Wrong reservation (A at long-entry 10000): 10000+1500=11500 <= 12000 => B uncut (15).
    Correct reservation (A at max_live 10900): 10900+1500=12400 > 12000 => cap cut fires.
    B must NOT retain 15 uncut shares.
    """
    cfg = _cfg()
    sig_a = Signal(symbol="A", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                   target_price=109.0, risk_per_share=20.0, size_shares=100.0, signal_index=25, timestamp="")
    sig_b = Signal(symbol="B", side="long", reason="t", entry_price=100.0, stop_price=90.0,
                   target_price=130.0, risk_per_share=10.0, size_shares=15.0, signal_index=25, timestamp="")

    def fake(hist, symbol=None, config=None, capital=10000.0, cache=None):
        idx = len(hist) - 1
        if symbol == "A" and idx == 25:
            s = copy.copy(sig_a); s.signal_index = idx; return s
        if symbol == "B" and idx == 25:
            s = copy.copy(sig_b); s.signal_index = idx; return s
        return None

    with patch("scripts.run_portfolio.generate_signal", side_effect=fake):
        res = run_portfolio_simulation(
            {"A": _mk_a_target_then_hold_short(), "B": _mk_b_flat_admits_bar25()},
            config=cfg, capital=10000.0,
        )

    by = {t["symbol"]: t for t in res["trades"]}
    assert "A" in by, f"A did not trade: {res['trades']}"
    assert "B" in by, f"B did not trade: {res['trades']}"
    assert by["A"]["exit_reason"] in ("target_rebound_short", "rebound_time_exit", "rebound_target", "rebound_stop"), (
        f"unexpected A exit: {by['A']}"
    )
    assert abs(float(by["B"]["shares"]) - 15.0) > 1e-9, (
        "B admitted uncut — portfolio reserved A at long-entry notional instead of "
        f"A's rebound-short max_live_coin_notional. B.shares={by['B']['shares']} trades={res['trades']}"
    )


def test_existing_position_cut_when_rebound_short_opens_same_bar():
    """B-rem2 extension: X is an existing open position (entered bar 20, 10000 notional).
    A and B signal same decision bar (bar 25). A triggers cap cuts (X+A exceed 12000)
    AND opens a rebound short (extra entry in probe_state.open_position_notionals).
    The fix propagates X's post-cut notional (6000) into the reservation overlay
    instead of leaving X at its pre-cut value (10000). B must be cut, not uncut.

    Without fix: post_notionals=[6000,6000,6540], len=3, existing_syms=["X"], len=1.
    3 != 2 -> fallback skips X update. X stays 10000 in overlay.
    With fix: len >= 2 -> X updated to 6000, A reserved at executed_notional.
    """
    cfg = _cfg()
    sig_x = Signal(symbol="X", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                   target_price=150.0, risk_per_share=20.0, size_shares=100.0, signal_index=20, timestamp="")
    sig_a = Signal(symbol="A", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                   target_price=109.0, risk_per_share=20.0, size_shares=100.0, signal_index=25, timestamp="")
    sig_b = Signal(symbol="B", side="long", reason="t", entry_price=100.0, stop_price=90.0,
                   target_price=130.0, risk_per_share=10.0, size_shares=15.0, signal_index=25, timestamp="")

    def _mk_x_open_through_bar25():
        """X: signal bar 20, entry bar 21 open=100, stays flat (no exit) through bar 25+."""
        candles = []
        for i in range(90):
            ts = f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z"
            if i == 20:
                candles.append(_c(ts, 100.0, 90.0, 100.0, 88.0))  # crash signal
            elif i == 21:
                candles.append(_c(ts, 100.0, 100.0, 101.0, 99.0))  # entry bar, no exit
            else:
                candles.append(_c(ts, 100.0, 100.0, 101.0, 99.0))  # flat, time-exits at bar 31
        return candles

    def mk_flat_from(i_start, o=100.0, cl=100.0):
        candles = []
        for i in range(90):
            ts = f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z"
            if i < i_start:
                candles.append(_c(ts, o, cl, o + 1.0, o - 1.0))
            else:
                candles.append(_c(ts, o, cl, o + 1.0, o - 1.0))
        return candles

    x_candles = _mk_x_open_through_bar25()
    a_candles = list(x_candles)
    for i in range(90):
        ts = f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z"
        if i == 25:
            a_candles[i] = _c(ts, 100.0, 90.0, 100.0, 88.0)
        elif i == 26:
            a_candles[i] = _c(ts, 100.0, 110.0, 111.0, 99.0)
        elif 27 <= i <= 74:
            a_candles[i] = _c(ts, 108.0, 108.0, 108.5, 107.5)
        else:
            a_candles[i] = _c(ts, 100.0, 100.0, 101.0, 99.0)
    b_candles = list(a_candles)
    for i in range(26, 90):
        b_candles[i] = _c(f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z", 100.0, 100.0, 100.5, 99.5)

    def fake(hist, symbol=None, config=None, capital=10000.0, cache=None):
        idx = len(hist) - 1
        if symbol == "X" and idx == 20:
            s = copy.copy(sig_x); s.signal_index = idx; return s
        if symbol == "A" and idx == 25:
            s = copy.copy(sig_a); s.signal_index = idx; return s
        if symbol == "B" and idx == 25:
            s = copy.copy(sig_b); s.signal_index = idx; return s
        return None

    with patch("scripts.run_portfolio.generate_signal", side_effect=fake):
        res = run_portfolio_simulation(
            {"X": x_candles, "A": a_candles, "B": b_candles},
            config=cfg, capital=10000.0,
        )

    by = {t["symbol"]: t for t in res["trades"]}
    assert "X" in by, f"X did not trade: {res['trades']}"
    assert "A" in by, f"A did not trade: {res['trades']}"
    assert "B" in by, f"B did not trade: {res['trades']}"
    # X entered at bar 21 (100 shares @100 = 10000), no cut at admission (single position).
    assert abs(float(by["X"]["shares"]) - 100.0) < 1e-9, f"X shares wrong: {by['X']['shares']}"
    # A triggered cap cuts with X (10000+10000>12000) -> cut to 6000 -> 60 shares.
    assert abs(float(by["A"]["shares"]) - 60.0) < 1e-9, (
        f"A not cut by existing X position. A.shares={by['A']['shares']} trades={res['trades']}"
    )
    assert by["A"]["exit_reason"] in ("target_rebound_short", "rebound_time_exit", "rebound_target", "rebound_stop"), (
        f"unexpected A exit: {by['A']}"
    )
    # B must be cut (not uncut 15) because overlay includes X's post-cut notional.
    assert abs(float(by["B"]["shares"]) - 15.0) > 1e-9, (
        f"B admitted uncut — existing X not propagated at post-cut notional. B.shares={by['B']['shares']}"
    )
    # Clean reconciliation.
    assert res["final_open_positions"] == 0
    assert abs(float(res["final_gross_exposure"])) < 1e-9
    assert list(getattr(res["risk_state"], "open_position_notionals", ["leak"])) == []
