"""Track-4(f) spec-fidelity hardening: per-leg attribution breakdown.

The PDF spec reports per-leg statistics explicitly:
  - "85 trades in test: 73 buys (71% profitable), 12 shorts (83% profitable)"
  - "Rebound short contributes ~27% of profit on Hyperlight"

The metrics module previously exposed only aggregate win_rate and a per-leg
pnl/trades summary, so a per-leg win rate / profit factor / profit-share
decomposition (the numbers the spec actually cites) was NOT machine-checkable.
These tests fail first against the unextended implementation, then pass once
`compute_metrics_from_trades` emits `leg_breakdown`.

Deterministic, synthetic, non-evidence. Compatible with pytest and unittest.
"""
from __future__ import annotations

import math

from src.metrics.campaign_metrics import compute_metrics_from_trades, compute_campaign_metrics


def _t(side, pnl, r=0.0, sym="BTC", leg=None):
    d = {"side": side, "total_pnl": pnl, "r_multiple": r, "symbol": sym}
    if leg is not None:
        d["leg"] = leg
    return d


def test_leg_breakdown_present_with_all_fields():
    trades = [
        _t("long", 10.0, r=1.0),
        _t("long", -4.0, r=-0.4),
        _t("long", 2.0, r=0.2),
        _t("short", 5.0, r=2.5),
        _t("short", -1.0, r=-0.5),
    ]
    m = compute_metrics_from_trades(trades)
    assert "leg_breakdown" in m, "leg_breakdown missing from metrics"
    legs = m["leg_breakdown"]
    assert isinstance(legs, list)
    by_leg = {l["leg"]: l for l in legs}
    assert set(by_leg.keys()) == {"long", "short"}

    longs = by_leg["long"]
    assert longs["trades"] == 3
    assert longs["wins"] == 2
    assert math.isclose(longs["win_rate"], 2 / 3, rel_tol=0, abs_tol=1e-12)
    assert math.isclose(longs["gross_profit"], 12.0)
    assert math.isclose(longs["gross_loss"], 4.0)
    assert math.isclose(longs["profit_factor"], 3.0)
    assert math.isclose(longs["total_pnl"], 8.0)
    assert math.isclose(longs["avg_r_multiple"], (1.0 - 0.4 + 0.2) / 3)
    assert math.isclose(longs["pnl_share_pct"], 8.0 / (8.0 + 4.0) * 100.0)

    shorts = by_leg["short"]
    assert shorts["trades"] == 2
    assert shorts["wins"] == 1
    assert math.isclose(shorts["win_rate"], 0.5)
    assert math.isclose(shorts["total_pnl"], 4.0)
    assert math.isclose(shorts["pnl_share_pct"], 4.0 / (8.0 + 4.0) * 100.0)


def test_leg_breakdown_prefers_explicit_leg_key():
    # explicit 'leg' overrides 'side' so spec terminology (buy/short) is preserved
    trades = [
        _t("long", 10.0, r=1.0, leg="buy"),
        _t("long", -4.0, r=-0.4, leg="buy"),
        _t("short", 5.0, r=2.5, leg="short"),
    ]
    m = compute_metrics_from_trades(trades)
    legs = {l["leg"]: l for l in m["leg_breakdown"]}
    assert set(legs.keys()) == {"buy", "short"}
    assert legs["buy"]["trades"] == 2
    assert legs["short"]["trades"] == 1


def test_leg_breakdown_uses_side_when_leg_key_absent():
    # trades without explicit 'leg' key must still attribute by side
    trades = [
        {"side": "long", "total_pnl": 5.0, "r_multiple": 1.0},
        {"side": "short", "total_pnl": -2.0, "r_multiple": -0.5},
    ]
    m = compute_metrics_from_trades(trades)
    legs = {l["leg"]: l for l in m["leg_breakdown"]}
    assert legs["long"]["trades"] == 1
    assert legs["short"]["trades"] == 1
    assert math.isclose(legs["long"]["total_pnl"], 5.0)
    assert math.isclose(legs["short"]["total_pnl"], -2.0)


def test_leg_breakdown_share_sums_to_one_when_pnl_nonzero():
    trades = [
        _t("long", 10.0, r=1.0),
        _t("short", -10.0, r=-1.0),
    ]
    m = compute_metrics_from_trades(trades)
    # total pnl is 0 -> share is undefined; must not crash and must be finite/zero
    for l in m["leg_breakdown"]:
        assert math.isfinite(l["pnl_share_pct"])
    # When total pnl != 0, shares sum to ~100
    trades2 = [
        _t("long", 30.0, r=1.0),
        _t("short", 10.0, r=1.0),
    ]
    m2 = compute_metrics_from_trades(trades2)
    total_share = sum(l["pnl_share_pct"] for l in m2["leg_breakdown"])
    assert math.isclose(total_share, 100.0, rel_tol=0, abs_tol=1e-9)


def test_leg_breakdown_empty_trades_is_safe():
    m = compute_metrics_from_trades([])
    assert m["leg_breakdown"] == []


def test_leg_breakdown_survives_nonfinite_r_multiple():
    trades = [
        {"side": "long", "total_pnl": 1.0, "r_multiple": float("nan")},
        {"side": "long", "total_pnl": 2.0, "r_multiple": float("inf")},
    ]
    m = compute_metrics_from_trades(trades)
    leg = m["leg_breakdown"][0]
    assert math.isfinite(leg["avg_r_multiple"])
    assert math.isclose(leg["trades"], 2)


def test_leg_breakdown_in_campaign_metrics_dict():
    trades = [_t("long", 5.0), _t("short", 1.0)]
    m = compute_campaign_metrics(trades=trades)
    assert "leg_breakdown" in m
    assert len(m["leg_breakdown"]) == 2


def test_leg_breakdown_splits_rebound_short_constituents():
    # Engine records the buy-leg total in `pnl` (long coin + long hedge) and the
    # rebound short's coin/hedge PnL in rebound_* fields. A short-legged trade
    # that actually fired the rebound short must split into buy/short constituents
    # WITHOUT double-counting the buy hedge (which `pnl` already includes).
    t = {
        "symbol": "BTC", "leg": "short",
        "pnl": 100.0,               # buy-leg total (long coin + long hedge)
        "hedge_pnl": 20.0,          # buy hedge + rebound hedge (informational)
        "rebound_short_pnl": 30.0,  # rebound short coin leg
        "rebound_hedge_pnl": -5.0,  # rebound hedge leg
        "total_pnl": 125.0,         # authoritative grand total
        "r_multiple": 0.5,
    }
    m = compute_metrics_from_trades([t])
    by_leg = {l["leg"]: l for l in m["leg_breakdown"]}
    assert set(by_leg) == {"buy", "short"}
    assert math.isclose(by_leg["buy"]["total_pnl"], 100.0)
    assert math.isclose(by_leg["short"]["total_pnl"], 25.0)
    assert math.isclose(sum(l["pnl_share_pct"] for l in m["leg_breakdown"]), 100.0,
                        rel_tol=0, abs_tol=1e-9)


def test_leg_breakdown_short_without_rebound_fields_not_split():
    # Legacy/partial serialization: leg='short' but no rebound_* fields (e.g. the
    # real OKX campaign artifact). Must be attributed in full to the short leg,
    # never split into a phantom buy + zero short constituent.
    t = {"symbol": "BCH", "leg": "short", "pnl": 4625.0, "hedge_pnl": -3343.0,
         "total_pnl": 2988.0, "r_multiple": 0.16}
    m = compute_metrics_from_trades([t])
    by_leg = {l["leg"]: l for l in m["leg_breakdown"]}
    assert set(by_leg) == {"short"}
    assert math.isclose(by_leg["short"]["total_pnl"], 2988.0)


def test_trade_attribution_by_leg_matches_leg_breakdown_split():
    # The by-leg summary and the per-leg breakdown must use the same split so a
    # rebound-short trade is never double-reported (full total on 'short' in one
    # structure and a buy/short split in the other).
    t = {
        "symbol": "BTC", "leg": "short",
        "pnl": 100.0, "hedge_pnl": 20.0,
        "rebound_short_pnl": 30.0, "rebound_hedge_pnl": -5.0,
        "total_pnl": 125.0, "r_multiple": 0.5,
    }
    m = compute_metrics_from_trades([t])
    by_leg = {l["leg"]: l for l in m["trade_attribution_by_leg"]}
    lb = {l["leg"]: l for l in m["leg_breakdown"]}
    assert set(by_leg) == {"buy", "short"} == set(lb)
    for leg in ("buy", "short"):
        assert math.isclose(by_leg[leg]["pnl"], lb[leg]["total_pnl"])
    assert math.isclose(sum(l["pnl"] for l in m["trade_attribution_by_leg"]),
                        m["exposure_metrics"]["total_pnl"])


def test_leg_breakdown_csv_rows_flatten_per_leg():
    from src.metrics.campaign_metrics import metrics_to_csv_rows
    trades = [_t("long", 10.0, r=1.0), _t("long", -4.0, r=-0.4), _t("short", 5.0, r=2.5)]
    m = compute_metrics_from_trades(trades)
    rows = metrics_to_csv_rows(m)
    by_metric = {r["metric"]: r["value"] for r in rows}
    assert by_metric["leg_breakdown.long.trades"] == 2
    assert math.isclose(float(by_metric["leg_breakdown.long.win_rate"]), 0.5)
    assert by_metric["leg_breakdown.short.trades"] == 1
    assert math.isclose(float(by_metric["leg_breakdown.short.total_pnl"]), 5.0)


if __name__ == "__main__":
    import sys
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))