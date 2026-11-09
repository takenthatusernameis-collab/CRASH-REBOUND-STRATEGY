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
    """A: entry bar 1 (signal bar 0, entry_next_bar). Bar 1 closes at 110 => +10%,
    hits 109 target -> rebound short opens at 109 (entry_next_bar for rebound =>
    short entry at bar 2 open context per engine). Short holds flat until time exit."""
    candles = []
    for i in range(90):
        ts = f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z"
        if i == 1:
            # Entry executes here (open=100). Closes at 110, high reaches 110 >= 109 target.
            candles.append(_c(ts, 100.0, 110.0, 111.0, 99.5))
        elif 2 <= i <= 55:
            # Rebound short is live; hold flat (no stop/target) so max_live stays at short entry.
            candles.append(_c(ts, 108.0, 108.0, 108.5, 107.5))
        else:
            candles.append(_c(ts, 100.0, 100.0, 100.5, 99.5))
    return candles


def _mk_b_flat_admits_bar0():
    a = _mk_a_target_then_hold_short()
    out = []
    for i, c in enumerate(a):
        if i >= 2:
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
    B signals same bar as A (bar 0), wants 15 shares @100 = 1500.

    Wrong reservation (A at long-entry 10000): 10000+1500=11500 <= 12000 => B uncut (15).
    Correct reservation (A at max_live 10900): 10900+1500=12400 > 12000 => cap cut fires.
    B must NOT retain 15 uncut shares.
    """
    cfg = _cfg()
    sig_a = Signal(symbol="A", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                   target_price=109.0, risk_per_share=20.0, size_shares=100.0, signal_index=0, timestamp="")
    sig_b = Signal(symbol="B", side="long", reason="t", entry_price=100.0, stop_price=90.0,
                   target_price=130.0, risk_per_share=10.0, size_shares=15.0, signal_index=0, timestamp="")

    def fake(hist, symbol=None, config=None, capital=10000.0, cache=None):
        idx = len(hist) - 1
        # Both signal on decision bar 0 (deepest-first ordering handled by severity in real path;
        # we control by returning A/B signals only at idx==0).
        if symbol == "A" and idx == 0:
            s = copy.copy(sig_a); s.signal_index = idx; return s
        if symbol == "B" and idx == 0:
            s = copy.copy(sig_b); s.signal_index = idx; return s
        return None

    with patch("scripts.run_portfolio.generate_signal", side_effect=fake):
        res = run_portfolio_simulation(
            {"A": _mk_a_target_then_hold_short(), "B": _mk_b_flat_admits_bar0()},
            config=cfg, capital=10000.0,
        )

    by = {t["symbol"]: t for t in res["trades"]}
    assert "A" in by, f"A did not trade: {res['trades']}"
    assert "B" in by, f"B did not trade: {res['trades']}"
    # A should have completed its rebound short lifecycle.
    assert by["A"]["exit_reason"] in ("target_rebound_short", "rebound_time_exit", "rebound_target", "rebound_stop"), (
        f"unexpected A exit: {by['A']}"
    )
    # B must be cut (not uncut 15 shares) because A's rebound-short max_live (10900)
    # consumes most of the 12000 cap.
    assert abs(float(by["B"]["shares"]) - 15.0) > 1e-9, (
        "B admitted uncut — portfolio reserved A at long-entry notional instead of "
        f"A's rebound-short max_live_coin_notional. B.shares={by['B']['shares']} trades={res['trades']}"
    )
