"""Failing-tests-first: metrics grand-total consumer must not silently drop rebound legs.

`_trade_pnl` fell back to bare `pnl` when `total_pnl` was missing from a trade dict,
silently dropping `rebound_short_pnl` and `rebound_hedge_pnl` (and `hedge_pnl`).
Per `TradeResult.__init__` semantics, omitted `total_pnl` = pnl + hedge_pnl +
rebound_short_pnl + rebound_hedge_pnl; explicit `total_pnl` stays authoritative.

Deterministic, synthetic, non-evidence regression guard.
"""
from __future__ import annotations

from src.metrics.campaign_metrics import compute_metrics_from_trades


def _trade(total_pnl=None, pnl=0.0, hedge_pnl=0.0, rebound_short_pnl=0.0,
           rebound_hedge_pnl=0.0, **kwargs):
    t = {"pnl": pnl, "hedge_pnl": hedge_pnl,
         "rebound_short_pnl": rebound_short_pnl,
         "rebound_hedge_pnl": rebound_hedge_pnl}
    t.update(kwargs)
    if total_pnl is not None:
        t["total_pnl"] = total_pnl
    return t


def test_trade_pnl_without_total_pnl_includes_all_legs():
    # total_pnl key absent: consumer must compute grand total from all legs,
    # not fall back to bare coin `pnl`.
    t = _trade(pnl=100.0, hedge_pnl=-10.0, rebound_short_pnl=50.0, rebound_hedge_pnl=-5.0)
    m = compute_metrics_from_trades([t])
    assert m["exposure_metrics"]["total_pnl"] == 135.0, (
        f"grand total dropped rebound legs: got {m['exposure_metrics']['total_pnl']}, expected 135.0"
    )


def test_trade_pnl_total_pnl_authoritative_overrides_leg_sum():
    # explicit total_pnl wins even if the leg sum differs (engine/runtime authoritative).
    t = _trade(total_pnl=999.0, pnl=100.0, hedge_pnl=-10.0, rebound_short_pnl=50.0, rebound_hedge_pnl=-5.0)
    m = compute_metrics_from_trades([t])
    assert m["exposure_metrics"]["total_pnl"] == 999.0


def test_trade_pnl_without_rebound_legs_matches_existing_behavior():
    t = _trade(pnl=100.0, hedge_pnl=-10.0)
    m = compute_metrics_from_trades([t])
    assert m["exposure_metrics"]["total_pnl"] == 90.0


def test_trade_pnl_leg_summary_uses_grand_total_not_bare_pnl():
    # trade_attribution pnl (per-symbol) must reflect grand total incl. rebound legs.
    t = _trade(symbol="BTC", pnl=100.0, hedge_pnl=-10.0, rebound_short_pnl=50.0, rebound_hedge_pnl=-5.0)
    m = compute_metrics_from_trades([t])
    by_sym = {a["symbol"]: a for a in m["trade_attribution"]}
    assert by_sym["BTC"]["pnl"] == 135.0, (
        f"attribution pnl dropped rebound legs: got {by_sym['BTC']['pnl']}, expected 135.0"
    )
