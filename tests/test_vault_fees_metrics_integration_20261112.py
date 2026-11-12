"""Integration/reconciliation: vault fees surfaced in campaign metrics.

Covers HANDOFF campaign cells 3-4 at metrics boundary: gross vs net exposure,
fee components present, CSV rows emitted, no double counting on base metrics.
"""
import csv
import math

from src.metrics.campaign_metrics import compute_campaign_metrics, metrics_to_csv_rows, metrics_to_dict
from src.metrics.vault_fees import HOURS_PER_YEAR, accrue_vault_fees


def _equity_series_from_trades(initial, trades):
    eq = float(initial)
    series = [eq]
    for t in trades:
        pnl = float(t.get("total_pnl", t.get("pnl", 0.0)) or 0.0)
        # include hedge legs if total_pnl not authoritative in fixture
        if "total_pnl" not in t:
            pnl += float(t.get("hedge_pnl", 0.0) or 0.0)
            pnl += float(t.get("rebound_short_pnl", 0.0) or 0.0)
            pnl += float(t.get("rebound_hedge_pnl", 0.0) or 0.0)
        eq += pnl
        series.append(eq)
    return series


def test_compute_campaign_metrics_includes_vault_fee_reconciliation():
    trades = [
        {"exit_timestamp": "2026-01-01T01:00:00Z", "total_pnl": 5000.0, "pnl": 5000.0, "symbol": "BTC", "side": "long"},
        {"exit_timestamp": "2026-01-01T02:00:00Z", "total_pnl": -1000.0, "pnl": -1000.0, "symbol": "ETH", "side": "long"},
        {"exit_timestamp": "2026-01-01T03:00:00Z", "total_pnl": 3000.0, "pnl": 3000.0, "symbol": "SOL", "side": "long"},
    ]
    initial = 100000.0
    m = metrics_to_dict(compute_campaign_metrics(
        trades=trades, initial_capital=initial, apply_vault_fees=True, fee_hours_per_step=1.0,
    ))

    # Base trade metrics unchanged (no double counting)
    assert m["exposure_metrics"]["total_pnl"] == 7000.0
    assert m["exposure_metrics"]["total_trades"] == 3
    assert m["win_rate"] == 2.0 / 3.0

    eq = _equity_series_from_trades(initial, trades)
    fees = accrue_vault_fees(eq, hours_per_step=1.0)
    assert m["gross_total_pnl"] == 7000.0
    assert m["aum_fee_total"] == fees.aum_fee_total
    assert m["profit_share_total"] == fees.profit_share_total
    assert m["vault_fee_total"] == fees.total_fees
    assert m["net_total_pnl"] == 7000.0 - fees.total_fees
    assert m["gross_final_equity"] == fees.final_equity_gross
    assert m["net_final_equity"] == fees.final_equity_net
    assert m["vault_hwm_final"] == fees.final_hwm

    rows = {r["metric"]: r["value"] for r in metrics_to_csv_rows(m)}
    for k in ("aum_fee_total", "profit_share_total", "vault_fee_total", "net_total_pnl", "gross_total_pnl"):
        assert k in rows


def test_vault_fees_disabled_by_default_preserves_existing_shape():
    trades = [{"exit_timestamp": "2026-01-01T00:00:00Z", "total_pnl": 100.0, "pnl": 100.0, "symbol": "BTC", "side": "long"}]
    m = metrics_to_dict(compute_campaign_metrics(trades=trades))
    assert "aum_fee_total" not in m
    assert "net_total_pnl" not in m
    assert "vault_fee_total" not in m
    assert m["exposure_metrics"]["total_pnl"] == 100.0


def test_empty_trades_with_fees_enabled():
    m = metrics_to_dict(compute_campaign_metrics(trades=[], initial_capital=100000.0, apply_vault_fees=True, fee_hours_per_step=1.0))
    # equity series is [initial] only
    expected_aum = 100000.0 * 0.02 / HOURS_PER_YEAR
    assert m["aum_fee_total"] == expected_aum
    assert m["profit_share_total"] == 0.0
    assert m["gross_total_pnl"] == 0.0
    assert m["net_total_pnl"] == -expected_aum
    assert m["gross_final_equity"] == 100000.0
    assert m["net_final_equity"] == 100000.0 - expected_aum


def test_equity_curve_based_fee_reconciliation():
    curve = [
        {"timestamp": "2026-01-01T00:00:00Z", "equity": 100000.0},
        {"timestamp": "2026-01-01T01:00:00Z", "equity": 110000.0},
        {"timestamp": "2026-01-01T02:00:00Z", "equity": 105000.0},
    ]
    m = metrics_to_dict(compute_campaign_metrics(trades=[], equity_curve=curve, apply_vault_fees=True, fee_hours_per_step=1.0))
    fees = accrue_vault_fees([100000.0, 110000.0, 105000.0], hours_per_step=1.0)
    assert m["aum_fee_total"] == fees.aum_fee_total
    assert m["profit_share_total"] == fees.profit_share_total
    assert m["gross_total_pnl"] == 5000.0
    assert m["net_total_pnl"] == 5000.0 - fees.total_fees


def test_loss_only_campaign_zero_profit_share_in_metrics():
    trades = [
        {"exit_timestamp": "2026-01-01T01:00:00Z", "total_pnl": -2000.0, "pnl": -2000.0, "symbol": "BTC", "side": "long"},
        {"exit_timestamp": "2026-01-01T02:00:00Z", "total_pnl": -3000.0, "pnl": -3000.0, "symbol": "ETH", "side": "long"},
    ]
    m = metrics_to_dict(compute_campaign_metrics(trades=trades, initial_capital=100000.0, apply_vault_fees=True, fee_hours_per_step=1.0))
    assert m["profit_share_total"] == 0.0
    assert m["aum_fee_total"] > 0.0
    assert m["gross_total_pnl"] == -5000.0
    assert m["net_total_pnl"] == -5000.0 - m["aum_fee_total"]
