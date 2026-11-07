"""Regression: reservation overlay must carry open-position exposure across bars so
a symbol admitted while another is still open sees the gross cap and equal-share
cuts (mixed timings). Synthetic fixtures only; non-evidence.

Covers HANDOFF item 2: "reservation overlay vs engine-applied cut schedules" and
"mixed timings" under max_positions + 120% gross cap.
"""
from __future__ import annotations

import copy
from unittest.mock import patch

from scripts.run_portfolio import run_portfolio_simulation, RiskState
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(i, o, h, l, cl, v=2_000_000.0):
    return {"timestamp": f"t{i:04d}", "open": o, "high": h, "low": l, "close": cl, "volume": v}


def _cfg(**kw):
    d = dict(
        use_rsi_trigger=False,
        min_daily_volume_usd=0.0,
        enable_eth_hedge=False,
        enable_rebound_short=False,
        enable_liquidation_checks=True,
        entry_next_bar=True,
        enable_volume_based_sizing=False,
        gross_cap_pct=120.0,
        max_positions=10,
        avoid_downtrend=False,
        regime_min_price=1.0,
        crash_lookback=5,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
        funding_rate_pct_per_hour=0.0,
        liquidation_maint_margin_pct=5.0,
        liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5,
    )
    d.update(kw)
    return StrategyConfig(**d)


def test_reservation_overlay_carries_exposure_across_bars_equal_share_cut():
    """A enters bar 20 (70k, liquidates bar 25); B enters bar 22 while A still
    open (70k, liquidates bar 30). 70k + 70k = 140k > 120k cap -> equal-share cut
    to 60k each. The reservation overlay must carry A's exposure into B's
    same-capacity admission; otherwise the gross cap is silently breached."""
    n = 140
    capital = 100000.0
    a = [_c(i, 100.0, 101.0, 99.0, 100.0) for i in range(n)]
    a[25] = _c(25, 96.0, 97.0, 93.0, 93.5)  # A liquidates at bar 25
    b = [_c(i, 100.0, 101.0, 99.0, 100.0) for i in range(n)]
    b[22] = _c(22, 94.0, 95.0, 93.0, 93.5)  # B crash at bar 22 (A still open)
    b[30] = _c(30, 96.0, 97.0, 93.0, 93.5)  # B liquidates at bar 30
    eth = [_c(i, 2000.0, 2010.0, 1990.0, 2000.0, 1_000_000.0) for i in range(n)]
    cfg = _cfg()

    recorded = []

    class Rec(RiskState):
        def apply_cap_cuts(self, capital, config, open_notional=None):
            incoming = list(open_notional) if open_notional is not None else list(self.open_position_notionals)
            out = super().apply_cap_cuts(capital, config, open_notional)
            recorded.append((list(incoming), list(out)))
            return out

    sa = Signal(symbol="A", side="long", reason="a", entry_price=100.0, stop_price=50.0,
                target_price=150.0, risk_per_share=50.0, timestamp="t0020",
                size_shares=700.0, signal_index=20)
    sb = Signal(symbol="B", side="long", reason="b", entry_price=100.0, stop_price=50.0,
                target_price=150.0, risk_per_share=50.0, timestamp="t0020",
                size_shares=700.0, signal_index=22)

    def fake_gen(hist, symbol=None, config=None, capital=100000.0, cache=None):
        idx = len(hist) - 1
        if symbol == "A" and idx == 20:
            s = copy.copy(sa); s.signal_index = idx; return s
        if symbol == "B" and idx == 22:
            s = copy.copy(sb); s.signal_index = idx; return s
        return None

    with patch("scripts.run_portfolio.RiskState", Rec), patch("scripts.run_portfolio.generate_signal", side_effect=fake_gen):
        res = run_portfolio_simulation(
            {"A": a, "B": b}, config=cfg, capital=capital, eth_candles={"ETH": eth}
        )

    assert res["num_trades"] == 2, res["trades"]
    by = {t["symbol"]: t for t in res["trades"]}
    assert by["A"]["exit_reason"] == "liquidated"
    assert by["B"]["exit_reason"] == "liquidated"
    # B must be equal-share cut (shares < 700) because A's 70k is still open.
    assert by["B"]["shares"] < 700.0, f"B not cut while A open: {by['B']}"
    # Equal-share cut recorded across old+new, total == cap.
    assert recorded, "expected apply_cap_cuts to fire for cross-bar admission"
    for incoming, out in recorded:
        assert len(out) == len(incoming), f"cut must cover old+new: {out} vs {incoming}"
        first = out[0]
        assert all(abs(n - first) < 1e-6 for n in out), f"unequal cut schedule: {out}"
        assert abs(sum(out) - 120000.0) < 1e-6, f"cut total must equal cap: {out}"
    # Final state reconciles to no open exposure / occupancy.
    assert res["final_open_positions"] == 0
    assert abs(res["final_gross_exposure"]) < 1e-9
    assert list(res["risk_state"].open_position_notionals) == []
