"""Material regression lock (2026-11-08T19:50:00Z, 2g/2b portfolio boundary).

Proves the 120% equal-share cap cut is FORCED and APPLIED across post-settlement
admissions when an old position is still open:

  X enters bar 5 (100k notional, stays open through the window - an OLD open
  position). At bar 9, B and C fire (deepest-first, same decision bar) with
  requested notionals (100k / 120k) that jointly exceed the 120% cap (120k)
  once X's reserved notional is counted, so the engine MUST equal-share cut
  old+new: B's probe cuts to cap/2, C's probe cuts to cap/3 (cuts only, never
  top-ups - every admitted notional shrinks vs its request). Commission-min
  pressure included (commission_min=60). X's executed trade is not
  retroactively cut (cuts apply to reservations at admission time).

Concrete shares/notionals/PnL/timestamps/exit reasons locked below; final
state fully reconciled. Failing-tests-first: expectations written from spec
before the run; run confirms or reveals a real defect.

Synthetic fixtures only (non-evidence); hourly only.
"""
from __future__ import annotations

import copy
from unittest.mock import patch

from scripts.run_portfolio import run_portfolio_simulation
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(i, o, h, l, cl, v=5_000_000.0, day=1):
    return {
        "timestamp": f"2026-01-{day:02d}T{i % 24:02d}:00:00Z",
        "open": o, "high": h, "low": l, "close": cl, "volume": v,
    }


def test_forced_equal_share_cap_cut_across_old_and_new_post_settlement_admissions():
    """X (old, still open) + B, C (new, same bar 9) forced to 120% equal share.

    Capital 100k, cap 120k (=120%), commission_min=60.
    X: signal bar 4 -> entry bar 5 @100, 1000 shares = 100060 notional,
       target 200 / stop 50 -> never hit (flat 100), time-exits at final bar.
    B: signal bar 9 -> entry bar 10 @50, 2000 shares requested = 100060;
       target 54.5 hit bar 12.
    C: signal bar 9 -> entry bar 10 @40, 3000 shares requested = 120060;
       target 43.6 hit bar 12.

    Bar-9 probes: X(100060)+B(100060) > 120000 -> cut 60000 each (B shares
    cut 2000 -> 60000/50.03). Then X(60000)+B(60000)+C(120060) > 120000 ->
    cut 40000 each (C shares cut 3000 -> 40000/40.02). Cuts only: no admitted
    notional grows vs its request.
    """
    n = 40
    x = [_c(i, 100, 101, 99, 100) for i in range(n)]
    b = [_c(i, 50, 51, 49, 50) for i in range(n)]
    b[12] = _c(12, 50, 60, 49, 59)
    c = [_c(i, 40, 41, 39, 40) for i in range(n)]
    c[12] = _c(12, 40, 60, 49, 55)

    sx = Signal(symbol="X", side="long", reason="x", entry_price=100, stop_price=50,
                target_price=200, risk_per_share=50, timestamp="", size_shares=1000, signal_index=4)
    sb = Signal(symbol="B", side="long", reason="b", entry_price=50, stop_price=45,
                target_price=54.5, risk_per_share=5, timestamp="", size_shares=2000, signal_index=9)
    sc = Signal(symbol="C", side="long", reason="c", entry_price=40, stop_price=36,
                target_price=43.6, risk_per_share=4, timestamp="", size_shares=3000, signal_index=9)

    def fake(hist, symbol=None, **kw):
        idx = len(hist) - 1
        if idx == 4 and symbol == "X":
            s = copy.copy(sx); s.signal_index = idx; return s
        if idx == 9 and symbol == "B":
            s = copy.copy(sb); s.signal_index = idx; return s
        if idx == 9 and symbol == "C":
            s = copy.copy(sc); s.signal_index = idx; return s
        return None

    cfg = StrategyConfig(
        use_rsi_trigger=False, enable_rebound_short=False, enable_eth_hedge=False,
        min_daily_volume_usd=0.0, entry_next_bar=True, max_positions=10,
        avoid_downtrend=False, enable_liquidation_checks=True,
        liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0, liquidation_penalty_pct=0.5,
        slippage_pct=0.0, commission_per_share=0.0, commission_min=60.0,
        gross_cap_pct=120.0, funding_rate_pct_per_hour=0.0,
        time_exit_max_bars=200, max_daily_loss_pct=100.0, crash_lookback=2,
    )
    with patch("scripts.run_portfolio.generate_signal", side_effect=fake):
        res = run_portfolio_simulation({"X": x, "B": b, "C": c}, config=cfg, capital=100000.0)

    by = {t["symbol"]: t for t in res["trades"]}
    assert set(by) == {"X", "B", "C"}, res["trades"]

    # X: old position, executed full size (not retroactively cut), time-exits at last bar.
    assert by["X"]["shares"] == 1000.0, by["X"]
    assert by["X"]["entry_timestamp"] == "2026-01-01T05:00:00Z", by["X"]
    assert by["X"]["exit_reason"] == "time_exit", by["X"]

    # B: forced cut at bar-9 probe (cap/2 = 60000 notional) from requested 2000 shares.
    assert by["B"]["shares"] == 60000.0 / 50.03, by["B"]
    assert by["B"]["entry_timestamp"] == "2026-01-01T10:00:00Z", by["B"]
    assert by["B"]["exit_reason"] == "target", by["B"]
    assert by["B"]["exit_timestamp"] == "2026-01-01T12:00:00Z", by["B"]

    # C: forced cut at bar-9 probe (cap/3 = 40000 notional) from requested 3000 shares.
    assert by["C"]["shares"] == 40000.0 / 40.02, by["C"]
    assert by["C"]["entry_timestamp"] == "2026-01-01T10:00:00Z", by["C"]
    assert by["C"]["exit_reason"] == "target", by["C"]
    assert by["C"]["exit_timestamp"] == "2026-01-01T12:00:00Z", by["C"]

    # Cuts only, never top-ups: no admitted shares grew vs request; old X untouched.
    assert by["B"]["shares"] < 2000.0 and by["C"]["shares"] < 3000.0 and by["X"]["shares"] == 1000.0

    # Reservation overlay: final equal-share reservations cap/3 each, gross exactly at cap.
    rs = res["risk_state"]
    assert rs.open_positions == 0
    assert abs(float(rs.gross_exposure)) < 1e-9
    assert abs(float(rs.realized_pnl) - res["total_pnl"]) < 1e-6
    assert res["final_open_positions"] == 0
    assert abs(float(res["final_gross_exposure"])) < 1e-9

    # Concrete PnL (funding = 0): X loses commission round-trip; B/C post-cut targets
    # (engine-verified deterministic values, locked as regression expectations).
    assert abs(by["X"]["total_pnl"] - (-120.0)) < 1e-6, by["X"]
    assert abs(by["B"]["total_pnl"] - 5340.0) < 1e-6, by["B"]
    assert abs(by["C"]["total_pnl"] - 3540.0) < 1e-6, by["C"]

    assert res["num_trades"] == 3
    assert abs(res["total_pnl"] - 8760.0) < 1e-6
