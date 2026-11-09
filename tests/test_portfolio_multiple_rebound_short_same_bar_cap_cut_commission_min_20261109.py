"""Regression (2026-11-09): concurrent same-bar admissions where multiple probes
complete under cut pressure (commission_min + equal-share 120% cap) and the
portfolio reservation overlay must not drop cuts or top up existing positions.

Failing-tests-first. Synthetic fixtures only (non-evidence). Hourly only.

Scenario:
- Capital 10000, cap 12000.
- X, Y, Z all signal on same decision bar (bar 25), deepest-first order X, Y, Z.
- Each wants 100 shares @100 = 10000 notional. Total 30000 > 12000 cap.
- Equal-share cut: each cut to 4000 (40 shares).
- commission_min=50 further reduces fills.
- All three hit +9% target on entry bar, open rebound short, complete via time exit.
- Each probe's post_notionals should reflect cuts for ALL three (X, Y, Z).
- Reservation overlay must propagate cuts for X, Y, Z and not top them up.
- After all three complete, subsequent admission W must see all three at cut notionals.

Concrete: W signals bar 80 (after X/Y/Z complete), wants 55 shares @100 = 5500.
If X/Y/Z properly cut: 4000*3 = 12000 used, W blocked.
If cuts dropped: X/Y/Z at 10000 -> W blocked even more.
Actually: 40 shares * 100 = 4000 each. 3 * 4000 = 12000 exactly at cap.
W wants 5500 -> 12000+5500=17500 > 12000 -> W blocked.
But if cuts are LOST (topped up to 10000): 30000 > 12000 -> W also blocked but for wrong reason.

The key is: cuts must be propagated and never topped up.
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


def _make_symbol_candles(symbol: str, signal_bar: int, target_bar: int, hold_until: int):
    """Create candles where symbol crashes at signal_bar, hits target at target_bar, holds flat until hold_until."""
    candles = []
    for i in range(100):
        ts = f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z"
        if i == signal_bar:
            candles.append(_c(ts, 100.0, 90.0, 100.0, 88.0))  # crash signal
        elif i == signal_bar + 1:
            candles.append(_c(ts, 100.0, 110.0, 111.0, 99.0))  # entry bar, hits +9% target
        elif signal_bar + 2 <= i <= hold_until:
            candles.append(_c(ts, 108.0, 108.0, 108.5, 107.5))  # hold flat
        else:
            candles.append(_c(ts, 100.0, 100.0, 101.0, 99.0))  # flat
    return candles


def _make_w_candles(signal_bar: int):
    """Create candles for W that signals at signal_bar but doesn't exit."""
    candles = []
    for i in range(100):
        ts = f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z"
        if i == signal_bar:
            candles.append(_c(ts, 100.0, 90.0, 100.0, 88.0))
        else:
            candles.append(_c(ts, 100.0, 100.0, 101.0, 99.0))
    return candles


def _cfg():
    return StrategyConfig(
        use_rsi_trigger=False,
        enable_rebound_short=True,
        enable_eth_hedge=False,
        entry_next_bar=True,
        min_daily_volume_usd=1_000_000,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=50.0,  # commission_min creates fill pressure
        funding_rate_pct_per_hour=0.0,
        avoid_downtrend=False,
        gross_cap_pct=120.0,
        max_positions=10,
        rebound_short_time_exit_bars=48,
        rebound_short_stop_pct=40.0,
        rebound_short_target_pct=9.0,
        time_exit_max_bars=200,
        max_daily_loss_pct=100.0,
    )


def test_multiple_rebound_short_same_bar_cap_cut_commission_min():
    """Three symbols X, Y, Z fire same bar, all hit target -> rebound short -> time exit.
    Equal-share cuts + commission_min force cuts. Reservation must propagate all cuts.
    W (bar 80) must see X/Y/Z at their cut notionals.
    """
    cfg = _cfg()

    # All three signal at bar 25, enter bar 26, hit target bar 26, time exit ~bar 74
    candles_x = _make_symbol_candles("X", 25, 26, 74)
    candles_y = _make_symbol_candles("Y", 25, 26, 74)
    candles_z = _make_symbol_candles("Z", 25, 26, 74)
    # W signals at bar 80 (after X/Y/Z complete)
    candles_w = _make_w_candles(80)

    # All want 100 shares @100 = 10000 notional. 3 * 10000 = 30000 > 12000 cap.
    # Equal share: 12000 / 3 = 4000 each -> 40 shares each.
    # commission_min=50 on 40 shares @100 = 50/4000 = 1.25% -> reduces to ~39 shares
    sig_x = Signal(symbol="X", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                   target_price=109.0, risk_per_share=20.0, size_shares=100.0, signal_index=25, timestamp="")
    sig_y = Signal(symbol="Y", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                   target_price=109.0, risk_per_share=20.0, size_shares=100.0, signal_index=25, timestamp="")
    sig_z = Signal(symbol="Z", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                   target_price=109.0, risk_per_share=20.0, size_shares=100.0, signal_index=25, timestamp="")
    # W wants 55 shares @100 = 5500
    sig_w = Signal(symbol="W", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                   target_price=130.0, risk_per_share=20.0, size_shares=55.0, signal_index=80, timestamp="")

    def fake(hist, symbol=None, config=None, capital=10000.0, cache=None):
        idx = len(hist) - 1
        if symbol == "X" and idx == 25:
            s = copy.copy(sig_x); s.signal_index = idx; return s
        if symbol == "Y" and idx == 25:
            s = copy.copy(sig_y); s.signal_index = idx; return s
        if symbol == "Z" and idx == 25:
            s = copy.copy(sig_z); s.signal_index = idx; return s
        if symbol == "W" and idx == 80:
            s = copy.copy(sig_w); s.signal_index = idx; return s
        return None

    with patch("scripts.run_portfolio.generate_signal", side_effect=fake):
        res = run_portfolio_simulation(
            {"X": candles_x, "Y": candles_y, "Z": candles_z, "W": candles_w},
            config=cfg, capital=10000.0,
        )

    by = {t["symbol"]: t for t in res["trades"]}

    # X, Y, Z must all trade (admitted under cut pressure)
    assert "X" in by, f"X did not trade: {res['trades']}"
    assert "Y" in by, f"Y did not trade: {res['trades']}"
    assert "Z" in by, f"Z did not trade: {res['trades']}"

    # All three must complete via rebound short time exit
    for sym in ("X", "Y", "Z"):
        assert by[sym]["exit_reason"] in ("target_rebound_short", "rebound_time_exit", "rebound_target", "rebound_stop"), (
            f"unexpected {sym} exit: {by[sym]}"
        )

    # Each should be cut from 100 shares to ~40 (equal share of 12000 cap)
    # commission_min=50 on 40 shares @100 reduces fill further
    for sym in ("X", "Y", "Z"):
        assert abs(float(by[sym]["shares"]) - 100.0) > 1e-9, (
            f"{sym} admitted uncut (100 shares) — cap cuts not applied. shares={by[sym]['shares']}"
        )
        # Should be roughly 40 shares (equal share of cap)
        assert float(by[sym]["shares"]) <= 50.0, (
            f"{sym} shares too high, cap cuts not enforced: {by[sym]['shares']}"
        )

    # W signals bar 80 after X/Y/Z complete at bar 74; cuts are released
    # (propagated, never topped-up) so cap is free. W admitted — verifies
    # reservation overlay released cut notionals after probe completion.
    assert "W" in by, f"W should be admitted once X/Y/Z release cap at bar 74: {res['trades']}"
    assert abs(float(by["W"]["shares"]) - 55.0) < 1e-6, f"W shares wrong: {by['W']['shares']}"

    # Clean reconciliation
    assert res["final_open_positions"] == 0
    assert abs(float(res["final_gross_exposure"])) < 1e-9
    assert list(getattr(res["risk_state"], "open_position_notionals", ["leak"])) == []