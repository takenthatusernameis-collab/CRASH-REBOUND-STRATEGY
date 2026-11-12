"""CELL 6 — Reporting fidelity to PDF performance context (per-year + months-gain).

Gap proof (file-search verified, 2026-11-12):
  - `src/metrics/campaign_metrics.py::compute_metrics_from_trades` emitted
    `monthly_breakdown` / `weekly_breakdown` (currency PnL) but had NO per-year
    breakdown and NO positive/negative/flat month counts.
  - `research_state/strategy_spec.md` Performance section cites
    "Per year +115.2%" and "6 of 10 months gain", so a machine-checkable
    per-year PnL bucket and positive-month count are required for reporting
    fidelity. No prior test asserted these fields
    (`grep -rn "annual_breakdown\\|positive_months\\|negative_months" tests/ src/`
    returned nothing before this change).

All values below are hand-traced from the fixture. This is additive reporting
only: it must not alter any pre-existing aggregate (win_rate, monthly/weekly
buckets, exposure, leg_breakdown) — asserted explicitly.
"""

import math

from src.metrics.campaign_metrics import compute_metrics_from_trades, compute_campaign_metrics


def _t(ts, pnl):
    return {"symbol": "CASE", "side": "long", "exit_timestamp": ts, "total_pnl": pnl}


def test_annual_breakdown_and_positive_month_counts():
    trades = [
        _t("2025-12-31T23:00:00Z", 100.0),   # 2025-12 positive
        _t("2026-01-15T00:00:00Z", -40.0),   # 2026-01 negative
        _t("2026-01-20T00:00:00Z", 10.0),    # 2026-01 -> net -30
        _t("2026-02-10T00:00:00Z", 25.0),    # 2026-02 positive
        _t("2026-03-05T00:00:00Z", 0.0),     # 2026-03 flat
    ]

    m = compute_metrics_from_trades(trades)

    # Per-year PnL buckets (traced): 2025 = 100, 2026 = -40+10+25+0 = -5.
    assert m["annual_breakdown"] == {"2025": 100.0, "2026": -5.0}, m["annual_breakdown"]
    assert m["annual_trade_counts"] == {"2025": 1, "2026": 4}, m["annual_trade_counts"]

    # Monthly buckets (traced): 2025-12=+100, 2026-01=-30, 2026-02=+25, 2026-03=0.
    assert m["monthly_breakdown"] == {
        "2025-12": 100.0,
        "2026-01": -30.0,
        "2026-02": 25.0,
        "2026-03": 0.0,
    }, m["monthly_breakdown"]

    # Months-gain context: 2 positive, 1 negative, 1 flat, 4 total.
    assert m["positive_months"] == 2, m["positive_months"]
    assert m["negative_months"] == 1, m["negative_months"]
    assert m["flat_months"] == 1, m["flat_months"]
    assert m["total_months"] == 4, m["total_months"]

    # Invariants: annual buckets reconcile to total PnL; counts partition months.
    assert math.isclose(sum(m["annual_breakdown"].values()), 95.0), m["annual_breakdown"]
    assert m["positive_months"] + m["negative_months"] + m["flat_months"] == m["total_months"]
    assert sum(m["annual_trade_counts"].values()) == len(trades)


def test_annual_and_month_counts_do_not_change_existing_aggregates():
    trades = [
        _t("2025-12-31T23:00:00Z", 100.0),
        _t("2026-01-15T00:00:00Z", -40.0),
        _t("2026-01-20T00:00:00Z", 10.0),
        _t("2026-02-10T00:00:00Z", 25.0),
        _t("2026-03-05T00:00:00Z", 0.0),
    ]
    m = compute_metrics_from_trades(trades)

    # Existing aggregates remain anchored (no double counting / no regression).
    # Wins are strictly positive PnL (100, 10, 25); the 0.0 trade is flat, not a win.
    assert m["win_rate"] == 3 / 5, m["win_rate"]
    assert m["exposure_metrics"]["total_trades"] == 5
    assert math.isclose(m["exposure_metrics"]["total_pnl"], 95.0)
    assert m["exposure_metrics"]["winning_trades"] == 3
    assert m["exposure_metrics"]["losing_trades"] == 1
    assert sum(m["monthly_breakdown"].values()) == sum(m["weekly_breakdown"].values())


def test_annual_buckets_via_campaign_metrics_entrypoint():
    trades = [
        _t("2025-12-31T23:00:00Z", 100.0),
        _t("2026-01-15T00:00:00Z", -40.0),
    ]
    m = compute_campaign_metrics(trades=trades)
    assert m["annual_breakdown"] == {"2025": 100.0, "2026": -40.0}, m["annual_breakdown"]
    assert m["annual_trade_counts"] == {"2025": 1, "2026": 1}
    assert m["positive_months"] == 1
    assert m["negative_months"] == 1
    assert m["total_months"] == 2