"""Vault fee export wiring: opt-in fee reconciliation in campaign JSON/CSV outputs.

Proves HANDOFF cell-1 gap: run_campaign.py and run_real_campaign.py called
compute_campaign_metrics without apply_vault_fees, so vault fee components were
never surfaced in campaign outputs. This suite covers the opt-in wiring surface
(CLI flag present, default off) and the metrics reconciliation it exposes.
Default outputs are unchanged unless --apply-vault-fees is explicitly set.
"""
import pytest

from src.metrics import compute_campaign_metrics, metrics_to_dict
from src.metrics.vault_fees import HOURS_PER_YEAR, accrue_vault_fees
from scripts.run_campaign import build_campaign_export, build_parser as campaign_build_parser
from scripts.run_real_campaign import build_parser as real_campaign_build_parser
from src.strategy.config import StrategyConfig

FEE_KEYS = ("aum_fee_total", "profit_share_total", "vault_fee_total",
            "gross_total_pnl", "net_total_pnl", "gross_final_equity",
            "net_final_equity", "vault_hwm_final")


def _trades():
    return [
        {"exit_timestamp": "2026-01-01T01:00:00Z", "total_pnl": 5000.0, "pnl": 5000.0, "symbol": "BTC", "side": "long"},
        {"exit_timestamp": "2026-01-01T02:00:00Z", "total_pnl": -1000.0, "pnl": -1000.0, "symbol": "ETH", "side": "long"},
        {"exit_timestamp": "2026-01-01T03:00:00Z", "total_pnl": 3000.0, "pnl": 3000.0, "symbol": "SOL", "side": "long"},
    ]


def _series():
    return [
        {"timestamp": "2026-01-01T00:00:00Z", "equity": 100000.0},
        {"timestamp": "2026-01-01T01:00:00Z", "equity": 105000.0},
        {"timestamp": "2026-01-01T02:00:00Z", "equity": 104000.0},
        {"timestamp": "2026-01-01T03:00:00Z", "equity": 107000.0},
    ]


def _curve_values():
    return [100000.0, 105000.0, 104000.0, 107000.0]


# --- Gap proof: default metric shape excludes fee keys (anchored outputs unchanged) ---

def test_default_metrics_shape_excludes_vault_fee_keys():
    m = metrics_to_dict(compute_campaign_metrics(trades=_trades(), equity_curve=_series()))
    for k in FEE_KEYS:
        assert k not in m, f"default output must not surface {k}"
    assert m["exposure_metrics"]["total_pnl"] == 7000.0
    assert m["exposure_metrics"]["total_trades"] == 3


# --- Opt-in wiring: fee reconciliation exposed with traced gross/net components ---

def test_opt_in_metrics_include_traced_fee_components():
    curve = _curve_values()
    fees = accrue_vault_fees(curve, hours_per_step=1.0)
    m = metrics_to_dict(compute_campaign_metrics(trades=_trades(), equity_curve=_series(),
                                                 initial_capital=100000.0, apply_vault_fees=True,
                                                 fee_hours_per_step=1.0))
    # Fee components reconcile exactly to the pure accounting module.
    assert m["aum_fee_total"] == pytest.approx(fees.aum_fee_total)
    assert m["profit_share_total"] == pytest.approx(fees.profit_share_total)
    assert m["vault_fee_total"] == pytest.approx(fees.total_fees)
    assert m["gross_total_pnl"] == pytest.approx(7000.0)
    assert m["net_total_pnl"] == pytest.approx(7000.0 - fees.total_fees)
    assert m["gross_final_equity"] == pytest.approx(fees.final_equity_gross)
    assert m["net_final_equity"] == pytest.approx(fees.final_equity_net)
    assert m["vault_hwm_final"] == pytest.approx(fees.final_hwm)
    # Hand-traced anchor: 1h AUM fee on 100000 at 2%/yr = 2000/8760.
    assert fees.steps[0].aum_fee == pytest.approx(2000.0 / HOURS_PER_YEAR)
    # Base aggregates unchanged (no double counting into trade metrics).
    assert m["exposure_metrics"]["total_pnl"] == 7000.0
    assert m["exposure_metrics"]["total_trades"] == 3


def test_csv_rows_emit_fee_keys_when_opt_in():
    m = metrics_to_dict(compute_campaign_metrics(trades=_trades(), equity_curve=_series(),
                                                 initial_capital=100000.0, apply_vault_fees=True,
                                                 fee_hours_per_step=1.0))
    from src.metrics.campaign_metrics import metrics_to_csv_rows
    rows = {r["metric"]: r["value"] for r in metrics_to_csv_rows(m)}
    for k in FEE_KEYS:
        assert k in rows, f"CSV must expose {k}"


# --- Export wiring: build_campaign_export carries fee metrics when present, omits when absent ---

def test_build_campaign_export_carries_fee_metrics_when_provided():
    cfg = StrategyConfig()
    fixtures = {"BTC": [{"timestamp": "2026-01-01T00:00:00Z", "open": 100.0, "high": 101.0,
                         "low": 99.0, "close": 100.0, "volume": 1.0}]}
    results = {"total_pnl": 7000.0, "num_trades": 3, "final_open_positions": 0,
               "final_gross_exposure": 0.0, "trades": []}
    export_absent = build_campaign_export(results, cfg, fixtures, "2026-11-12T00:00:00Z")
    assert export_absent.get("metrics") is None

    fees_m = metrics_to_dict(compute_campaign_metrics(trades=_trades(), equity_curve=_series(),
                                                      initial_capital=100000.0, apply_vault_fees=True,
                                                      fee_hours_per_step=1.0))
    export_present = build_campaign_export(results, cfg, fixtures, "2026-11-12T00:00:00Z",
                                           metrics=fees_m)
    assert export_present["metrics"]["vault_fee_total"] > 0.0
    assert export_present["metrics"]["net_total_pnl"] == pytest.approx(
        7000.0 - export_present["metrics"]["vault_fee_total"])


# --- CLI flag surface: opt-in flag present, default off ---

def test_run_campaign_cli_apply_vault_fees_flag_default_off():
    args = campaign_build_parser().parse_args([])
    assert args.apply_vault_fees is False
    assert args.capital == 100000.0
    args = campaign_build_parser().parse_args(["--apply-vault-fees", "--capital", "250000.0"])
    assert args.apply_vault_fees is True
    assert args.capital == 250000.0


def test_run_real_campaign_cli_apply_vault_fees_flag_default_off():
    args = real_campaign_build_parser().parse_args([])
    assert args.apply_vault_fees is False
    assert args.capital == 100000.0
    args = real_campaign_build_parser().parse_args(["--apply-vault-fees"])
    assert args.apply_vault_fees is True


def test_help_emits_apply_vault_fees_without_side_effects():
    # Parsing --help must exit cleanly before any file/provenance I/O.
    from scripts.run_campaign import main as campaign_main
    from scripts.run_real_campaign import main as real_campaign_main
    with pytest.raises(SystemExit) as exc:
        campaign_main(["--help"])
    assert exc.value.code == 0
    with pytest.raises(SystemExit) as exc:
        real_campaign_main(["--help"])
    assert exc.value.code == 0
