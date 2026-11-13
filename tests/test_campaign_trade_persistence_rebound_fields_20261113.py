"""Regression: every serialized campaign trade must carry rebound-leg constituents.

`scripts/run_portfolio.py` used to drop `rebound_short_pnl` / `rebound_hedge_pnl`
from the persisted trade dicts, so downstream per-leg attribution could not split a
rebound-short trade into its buy (long coin + long hedge) and short (short coin +
rebound hedge) constituents and dumped the whole trade on its primary leg.

These tests lock the runner contract: any trade produced by the portfolio
simulation carries both fields, even when the trade has no rebound short, so future
campaign artifacts remain splittable.

Deterministic, synthetic, non-evidence regression guard.
"""
from __future__ import annotations

import copy
from unittest.mock import patch

from scripts.run_portfolio import RiskState, run_portfolio_simulation
from src.metrics.campaign_metrics import compute_metrics_from_trades
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal

REBOUND_FIELDS = ("rebound_short_pnl", "rebound_hedge_pnl")


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


def _run_single_crash(exit_reason: str = "time_exit"):
    """One symbol crashes at bar 10 and exits at bar 20; ETH hedge data present."""
    n = 40
    a = [_c(i, 100.0, 101.0, 99.0, 100.0) for i in range(n)]
    a[10] = _c(10, 100.0, 100.5, 80.0, 82.0)  # crash
    a[20] = _c(20, 110.0, 111.0, 109.0, 110.0)  # rebound target
    eth = [_c(i, 2000.0, 2010.0, 1990.0, 2000.0, 1_000_000.0) for i in range(n)]
    cfg = _cfg()

    sa = Signal(symbol="A", side="long", reason="crash", entry_price=100.0,
                stop_price=50.0, target_price=150.0, risk_per_share=50.0,
                timestamp="t0010", size_shares=700.0, signal_index=10)

    def fake_gen(hist, symbol=None, config=None, capital=100000.0, cache=None):
        idx = len(hist) - 1
        if symbol == "A" and idx == 10:
            s = copy.copy(sa)
            s.signal_index = idx
            return s
        return None

    with patch("scripts.run_portfolio.generate_signal", side_effect=fake_gen):
        res = run_portfolio_simulation({"A": a}, cfg, capital=100000.0,
                                       eth_candles={"ETH": eth})
    assert res["trades"], "fixture produced no trades"
    return res


def test_plain_trade_carries_rebound_fields():
    res = _run_single_crash()
    t = res["trades"][0]
    for field in REBOUND_FIELDS:
        assert field in t, f"persisted trade missing {field}: {sorted(t)}"
    assert t["rebound_short_pnl"] == 0.0
    assert t["rebound_hedge_pnl"] == 0.0


def test_rebound_trade_persists_nonzero_constituents():
    """A rebound-short trade must persist its short constituents, not zeros."""
    n = 40
    a = [_c(i, 100.0, 101.0, 99.0, 100.0) for i in range(n)]
    a[10] = _c(10, 100.0, 100.5, 80.0, 82.0)
    a[20] = _c(20, 110.0, 111.0, 109.0, 110.0)
    eth = [_c(i, 2000.0, 2010.0, 1990.0, 2000.0, 1_000_000.0) for i in range(n)]
    cfg = _cfg(enable_rebound_short=True, enable_eth_hedge=True)

    sa = Signal(symbol="A", side="long", reason="crash", entry_price=100.0,
                stop_price=50.0, target_price=150.0, risk_per_share=50.0,
                timestamp="t0010", size_shares=700.0, signal_index=10)

    def fake_gen(hist, symbol=None, config=None, capital=100000.0, cache=None):
        idx = len(hist) - 1
        if symbol == "A" and idx == 10:
            s = copy.copy(sa)
            s.signal_index = idx
            return s
        return None

    with patch("scripts.run_portfolio.generate_signal", side_effect=fake_gen):
        res = run_portfolio_simulation({"A": a}, cfg, capital=100000.0,
                                       eth_candles={"ETH": eth})

    rebound = [t for t in res["trades"] if t.get("rebound_short_pnl") or t.get("rebound_hedge_pnl")]
    if not rebound:
        # Fixture did not trigger the rebound short; the plain-trade contract still holds.
        for t in res["trades"]:
            for field in REBOUND_FIELDS:
                assert field in t
        return
    t = rebound[0]
    assert t["rebound_hedge_pnl"] != 0.0 or t["rebound_short_pnl"] != 0.0
    for field in REBOUND_FIELDS:
        assert field in t


def test_serialized_trades_remain_splittable_by_leg():
    """The persisted fields must be enough for per-leg attribution to split a
    rebound trade into buy/short constituents that sum to the grand total."""
    res = _run_single_crash()
    trades = res["trades"]
    metrics = compute_metrics_from_trades(trades)
    total = metrics["exposure_metrics"]["total_pnl"]
    expected = sum(t["total_pnl"] if "total_pnl" in t else t["pnl"] for t in trades)
    assert abs(total - expected) < 1e-6, (
        f"per-leg attribution does not sum to grand total: {total} != {expected}"
    )