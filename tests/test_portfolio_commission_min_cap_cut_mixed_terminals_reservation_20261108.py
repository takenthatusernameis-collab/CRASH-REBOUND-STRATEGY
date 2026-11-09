"""Material regression lock (2026-11-08T15:53:00Z, 2g/2b portfolio cross-path).
Updated 2026-11-09T17:06Z: expected values corrected to spec-compliant equal-share
cuts old+new for concurrent same-bar rebound_short admissions with no existing
positions (cap 84000, 3 candidates, A desired 500*100=50000 > 28000 equal-share ->
A cut to 280 shares; B 25000 < 28000 and C 15000 < 28000 unchanged at 500). Prior
sequential admission gave A preferential uncapped fill — spec violation.

Uncovered branch (evidence-backed): same-bar multi-symbol admissions under forced
120% equal-share cap cuts with `commission_min`-adjusted fills and mixed terminals
(rebound-short completion, liquidation, and final-exit) where post-probe
notionals/reservations interact with pending realized exits across bars.

Locks: admission/capacity under reservation overlay (probe future exits do not leak
into sibling admission), commission_min fill-adjusted execution under cap pressure,
deterministic mixed terminal paths, spec-compliant equal-share distribution, and
final occupancy/gross/notional reconciliation after all exits. Synthetic fixtures
only (non-evidence); hourly only.
"""
from __future__ import annotations

import copy
from unittest.mock import patch

from scripts.run_portfolio import run_portfolio_simulation
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(i, o, h, l, cl, v=5_000_000.0, day=1):
    return {"timestamp": f"2026-01-{day:02d}T{i % 24:02d}:00:00Z", "open": o, "high": h, "low": l, "close": cl, "volume": v}


def test_commission_min_forced_cap_cut_mixed_terminals_reservation_reconciles():
    """A,B,C fire same decision bar 5 (equal severity). Capital 70k, cap 120%=84k.
    commission_min=50 on 500-share requests creates fill/cap pressure (>84k total),
    forcing equal-share cap cuts in probes; reservation overlay governs same-bar
    sibling admission (probe future exits/capacity must not leak).
    Mixed terminals across bars: A target->rebound short; B liquidation; C final exit.
    Final state must reconcile occupancy/gross/notionals to zero."""
    n = 40
    a = [_c(i, 100, 101, 99, 100) for i in range(n)]
    a[6] = _c(6, 100, 100.5, 99, 100)
    a[8] = _c(8, 100, 110, 99, 109)
    a[12] = _c(12, 99, 100, 90, 91)
    b = [_c(i, 50, 51, 49, 50) for i in range(n)]
    b[6] = _c(6, 50, 50.5, 49, 50)
    b[9] = _c(9, 48, 48.5, 46, 46.5)  # liq: 50*(1-0.06)=47
    c_cand = [_c(i, 30, 31, 29, 30) for i in range(n)]
    c_cand[6] = _c(6, 30, 30.5, 29, 30)
    c_cand[15] = _c(15, 30, 36, 29, 36)

    sa = Signal(symbol="A", side="long", reason="a", entry_price=100, stop_price=90,
                target_price=109, risk_per_share=10, timestamp="", size_shares=500, signal_index=5)
    sb = Signal(symbol="B", side="long", reason="b", entry_price=50, stop_price=45,
                target_price=60, risk_per_share=5, timestamp="", size_shares=500, signal_index=5)
    sc = Signal(symbol="C", side="long", reason="c", entry_price=30, stop_price=27,
                target_price=36, risk_per_share=3, timestamp="", size_shares=500, signal_index=5)

    def fake(hist, symbol=None, **kw):
        idx = len(hist) - 1
        if idx == 5 and symbol == "A":
            s = copy.copy(sa); s.signal_index = idx; return s
        if idx == 5 and symbol == "B":
            s = copy.copy(sb); s.signal_index = idx; return s
        if idx == 5 and symbol == "C":
            s = copy.copy(sc); s.signal_index = idx; return s
        return None

    cfg = StrategyConfig(
        use_rsi_trigger=False, enable_rebound_short=True, enable_eth_hedge=False,
        min_daily_volume_usd=0.0, entry_next_bar=True, max_positions=10,
        avoid_downtrend=False, enable_liquidation_checks=True,
        liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0, liquidation_penalty_pct=0.5,
        slippage_pct=0.0, commission_per_share=0.0, commission_min=50.0,
        gross_cap_pct=120.0, funding_rate_pct_per_hour=0.0,
        rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
        time_exit_max_bars=200, max_daily_loss_pct=100.0,
    )
    with patch("scripts.run_portfolio.generate_signal", side_effect=fake):
        res = run_portfolio_simulation({"A": a, "B": b, "C": c_cand}, config=cfg, capital=70000.0)

    by = {t["symbol"]: t for t in res["trades"]}
    assert set(by) == {"A", "B", "C"}, f"all three must admit under reservation/cap-cut: {res['trades']}"

    # Mixed terminals under spec-compliant equal-share cuts (cap 84000, 3 candidates):
    # A desired 500*100=50000 > 28000 equal-share => 280 shares; B 25000 <= 28000, C 15000 <= 28000.
    assert by["A"]["exit_reason"] == "target_rebound_short"
    assert abs(by["A"]["shares"] - 280.0) < 1e-6
    assert abs(by["A"]["total_pnl"] - 5167.2049999999945) < 1e-6
    assert by["A"]["entry_timestamp"] == "2026-01-01T06:00:00Z"
    assert by["A"]["exit_timestamp"] == "2026-01-01T09:00:00Z"

    assert by["B"]["exit_reason"] == "liquidated"
    assert by["B"]["shares"] == 500
    assert abs(by["B"]["total_pnl"] - (-2225.2500000000014)) < 1e-6
    assert by["B"]["entry_timestamp"] == "2026-01-01T06:00:00Z"
    assert by["B"]["exit_timestamp"] == "2026-01-01T09:00:00Z"

    assert by["C"]["exit_reason"] == "time_exit"
    assert by["C"]["shares"] == 500
    assert abs(by["C"]["total_pnl"] - (-100.00000000000142)) < 1e-6
    assert by["C"]["entry_timestamp"] == "2026-01-01T06:00:00Z"
    assert by["C"]["exit_timestamp"] == "2026-01-01T15:00:00Z"

    assert abs(res["total_pnl"] - 2841.9549999999917) < 1e-6
    assert res["num_trades"] == 3
    # Final reconciliation: mixed terminals (rebound/liquidation/time) release all
    # occupancy, reserved notionals, and gross exposure; pending realized exits settled.
    assert res["final_open_positions"] == 0
    assert abs(float(res["final_gross_exposure"])) < 1e-9
    rs = res["risk_state"]
    assert getattr(rs, "open_positions", -1) == 0
    assert list(getattr(rs, "open_position_notionals", ["leak"])) == []
    assert abs(float(getattr(rs, "gross_exposure", -1.0))) < 1e-9
    assert abs(float(getattr(rs, "realized_pnl", 0.0)) - 2841.9549999999917) < 1e-6
