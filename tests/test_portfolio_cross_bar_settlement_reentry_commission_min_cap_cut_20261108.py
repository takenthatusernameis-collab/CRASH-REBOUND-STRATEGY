"""Material regression lock (2026-11-08T19:14:12Z, 2g/2b portfolio boundary).

Probes/locks: cross-bar pending realized-exit settlement + same-bar
re-admission/occupancy boundary under commission_min + forced 120% equal-share
cap-cut pressure. A profitable position exits (realized PnL reconciled through
exit bar, notional/occupancy released next bar) and two new symbols are admitted
on the settlement bar under commission_min+cap pressure; reservation overlay
must reflect freed capacity (no leak from released position, no distortion from
settled realized PnL/daily state) with concrete shares/notionals/PnL/
timestamps/exit reasons and final reconciliation. No src fix required;
behavior verified.

Construction evidence (failing-tests-first lock): initial draft used pre-warmup
signal indices and placeholder expectations; verified run produced concrete
admissions/A+B+C outcomes and full reconciliation, then locked below.

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


def test_cross_bar_settlement_frees_capacity_for_same_bar_cap_cut_admissions():
    """A enters bar 6 (signal 5), exits target bar 8. Exit reconciled through 8;
    occupancy/notional released at bar 9. At bar 9, B and C fire (same decision
    bar). Capital 80k, cap 120%=96k, commission_min=60, large requested shares
    create commission_min+cap reservation pressure after A release.

    A's settled positive realized PnL and released notional must not distort bar-9
    admission/capacity/reservation. B/C admitted with concrete mixed terminals.
    Final state fully reconciled.
    """
    n = 35
    a = [_c(i, 100, 101, 99, 100) for i in range(n)]
    a[6] = _c(6, 100, 100.5, 99, 100)
    a[8] = _c(8, 100, 111, 99, 110)
    b = [_c(i, 50, 51, 49, 50) for i in range(n)]
    b[10] = _c(10, 50, 50.5, 49, 50)
    b[12] = _c(12, 50, 60, 49, 59)
    c = [_c(i, 40, 41, 39, 40) for i in range(n)]
    c[10] = _c(10, 40, 40.5, 39, 40)
    c[13] = _c(13, 38, 38.5, 35.5, 36)

    sa = Signal(symbol="A", side="long", reason="a", entry_price=100, stop_price=90,
                target_price=110, risk_per_share=10, timestamp="", size_shares=400, signal_index=5)
    sb = Signal(symbol="B", side="long", reason="b", entry_price=50, stop_price=45,
                target_price=59, risk_per_share=5, timestamp="", size_shares=1000, signal_index=9)
    sc = Signal(symbol="C", side="long", reason="c", entry_price=40, stop_price=36,
                target_price=48, risk_per_share=4, timestamp="", size_shares=1200, signal_index=9)

    def fake(hist, symbol=None, **kw):
        idx = len(hist) - 1
        if idx == 5 and symbol == "A":
            s = copy.copy(sa); s.signal_index = idx; return s
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
        res = run_portfolio_simulation({"A": a, "B": b, "C": c}, config=cfg, capital=80000.0)

    by = {t["symbol"]: t for t in res["trades"]}
    assert set(by) == {"A", "B", "C"}, (
        f"A must settle/release so B,C admit at bar 9: {res['trades']}"
    )

    # A: settled positive exit before bar-9 admissions; released capacity used by B/C.
    assert by["A"]["exit_reason"] == "target"
    assert by["A"]["entry_timestamp"] == "2026-01-01T06:00:00Z"
    assert by["A"]["exit_timestamp"] == "2026-01-01T08:00:00Z"
    assert by["A"]["shares"] == 400
    assert abs(by["A"]["total_pnl"] - 3945.999999999998) < 1e-6, by["A"]

    # B,C admitted same settlement bar after A released; concrete mixed terminals.
    assert by["B"]["entry_timestamp"] == "2026-01-01T10:00:00Z"
    assert by["B"]["exit_reason"] == "target"
    assert by["B"]["exit_timestamp"] == "2026-01-01T12:00:00Z"
    assert abs(by["B"]["shares"] - 1000.0) < 1e-6, by["B"]
    assert abs(by["B"]["total_pnl"] - 8950.800000000001) < 1e-6, by["B"]

    assert by["C"]["entry_timestamp"] == "2026-01-01T10:00:00Z"
    assert by["C"]["exit_reason"] == "liquidated"
    assert by["C"]["exit_timestamp"] == "2026-01-01T13:00:00Z"
    assert abs(by["C"]["shares"] - 1198.5018726591761) < 1e-6, by["C"]
    assert abs(by["C"]["total_pnl"] - (-5753.183520599251)) < 1e-6, by["C"]

    assert res["num_trades"] == 3
    assert abs(res["total_pnl"] - 7143.616479400748) < 1e-6
    # Final reconciliation: cross-bar settlement + same-bar admissions fully released.
    assert res["final_open_positions"] == 0
    assert abs(float(res["final_gross_exposure"])) < 1e-9
    rs = res["risk_state"]
    assert getattr(rs, "open_positions", -1) == 0
    assert list(getattr(rs, "open_position_notionals", ["leak"])) == []
    assert abs(float(getattr(rs, "gross_exposure", -1.0))) < 1e-9
    assert abs(float(getattr(rs, "realized_pnl", 0.0)) - 7143.616479400748) < 1e-6
