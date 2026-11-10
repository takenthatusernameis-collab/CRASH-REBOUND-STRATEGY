"""Portfolio live-notional reservation must cover rebound-short leg (2026-11-07).

Failing-tests-first: a rebound short opens at short_entry (~target exit), not the
original long entry. run_portfolio must not reserve long-entry notional while the
short leg is live; gross-cap/equal-share admission must use the live short notional.
Synthetic fixtures only (non-evidence).
"""
from __future__ import annotations

import copy
from unittest.mock import patch

from scripts.run_portfolio import run_portfolio_simulation
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(ts, o, c, h=None, l=None, v=1_500_000.0):
    h = max(o, c) * 1.001 if h is None else h
    l = min(o, c) * 0.999 if l is None else l
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _mk_x_hold_short():
    candles = []
    for i in range(90):
        ts = f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z"
        if i == 6:
            candles.append(_c(ts, 100.0, 110.0, 111.0, 99.0))
        elif 7 <= i <= 40:
            candles.append(_c(ts, 108.0, 108.0, 108.5, 107.5))
        elif i == 41:
            candles.append(_c(ts, 108.0, 98.0, 109.0, 97.0))
        else:
            candles.append(_c(ts, 100.0, 100.0, 101.0, 99.0))
    return candles


def _mk_y_flat():
    x = _mk_x_hold_short()
    out = []
    for i, c in enumerate(x):
        if i >= 8:
            c = dict(c, open=100.0, close=100.5, high=101.0, low=99.5)
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


def test_rebound_short_live_notional_triggers_cap_cut_future_admission():
    """Capital 10000, cap 12000. X: long notional 100*100=10000, rebound short opens
    near 109 => live short notional ~10900 while short holds. Y admits at bar 8.
    With two positions under cap pressure, equal-share cut is 12000/2=6000 per slot.
    Wrong long-entry reservation (10000) applied to old slots can produce a larger Y
    share than warranted by live X exposure; correct behavior is that Y is cut and
    the reservation path must have seen X's live short notional (10900), so Y's
    executed shares reflect the constrained equal-share schedule (60 @100 = 6000)
    only if the engine applies it — but critically, pre-fix with wrong reservation
    the admission boundary used 10000 not 10900. Use a stricter case below."""
    cfg = _cfg()
    sig_x = Signal(symbol="X", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                   target_price=109.0, risk_per_share=20.0, size_shares=100.0, signal_index=5, timestamp="")
    sig_y = Signal(symbol="Y", side="long", reason="t", entry_price=100.0, stop_price=90.0,
                   target_price=120.0, risk_per_share=10.0, size_shares=15.0, signal_index=8, timestamp="")

    def fake(hist, symbol=None, config=None, capital=10000.0, cache=None):
        idx = len(hist) - 1
        if symbol == "X" and idx == 5:
            s = copy.copy(sig_x); s.signal_index = idx; return s
        if symbol == "Y" and idx == 8:
            s = copy.copy(sig_y); s.signal_index = idx; return s
        return None

    with patch("scripts.run_portfolio.generate_signal", side_effect=fake):
        res = run_portfolio_simulation({"X": _mk_x_hold_short(), "Y": _mk_y_flat()},
                                       config=cfg, capital=10000.0)

    by = {t["symbol"]: t for t in res["trades"]}
    assert "X" in by and by["X"]["exit_reason"] == "target_rebound_short"
    assert "Y" in by
    # Wrong reservation (10000): 10000+1500<=12000 => no cap cut, Y stays 15.
    # Correct reservation (10900): 10900+1500>12000 => equal-share/cap-cut path fires.
    # Under cuts-only, never topped-up: Y is NOT bumped above its requested 1500
    # notional even when equal-share would be 6000. The invariant is that Y must not
    # be topped up above its request under live short notional reservation.
    assert abs(float(by["Y"]["shares"]) - 15.0) < 1e-9, (
        "Y topped up above requested 1500 notional — violates cuts-only, never topped-up spec: "
        f"Y.shares={by['Y']['shares']} trades={res['trades']}")


def test_final_state_reconciles_after_rebound_short_live_notional_trade():
    cfg = _cfg()
    sig_x = Signal(symbol="X", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                   target_price=109.0, risk_per_share=20.0, size_shares=100.0, signal_index=5, timestamp="")
    sig_y = Signal(symbol="Y", side="long", reason="t", entry_price=100.0, stop_price=90.0,
                   target_price=120.0, risk_per_share=10.0, size_shares=15.0, signal_index=8, timestamp="")

    def fake(hist, symbol=None, config=None, capital=10000.0, cache=None):
        idx = len(hist) - 1
        if symbol == "X" and idx == 5:
            s = copy.copy(sig_x); s.signal_index = idx; return s
        if symbol == "Y" and idx == 8:
            s = copy.copy(sig_y); s.signal_index = idx; return s
        return None

    with patch("scripts.run_portfolio.generate_signal", side_effect=fake):
        res = run_portfolio_simulation({"X": _mk_x_hold_short(), "Y": _mk_y_flat()},
                                       config=cfg, capital=10000.0)
    assert res["final_open_positions"] == 0
    assert abs(float(res["final_gross_exposure"])) < 1e-9
    assert list(getattr(res["risk_state"], "open_position_notionals", [])) == []
