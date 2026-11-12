#!/usr/bin/env python3
"""Full campaign validation runner for the test window."""
import argparse
import json
import os
import sys
from datetime import datetime

from src.data.loader import make_fixture_crash_rebound_multi
from src.strategy.config import StrategyConfig
from scripts.run_portfolio import run_portfolio_simulation
from src.metrics import (
    compute_campaign_metrics,
    metrics_to_dict,
    metrics_to_csv_rows,
)


def _execution_realism_metadata(config):
    """Explicit spec-vs-implementation execution realism markers (no microstructure claims)."""
    return {
        "execution_model": getattr(config, "execution_model", "hourly_bar_simplified"),
        "order_slicing_simulated": bool(getattr(config, "order_slicing_simulated", False)),
        "order_book_impact_model": getattr(config, "order_book_impact_model", "slippage_proxy"),
        "spread_bps_assumed": getattr(config, "spread_bps_assumed", 0.0),
        "slippage_pct": getattr(config, "slippage_pct", None),
        "funding_rate_pct_per_hour": getattr(config, "funding_rate_pct_per_hour", None),
        "enable_liquidation_checks": bool(getattr(config, "enable_liquidation_checks", False)),
        "liquidation_maint_margin_pct": getattr(config, "liquidation_maint_margin_pct", None),
        "limitation_note": (
            "Hourly bar simulation only. Per spec the strategy uses 20s order slicing and "
            "order-book-aware impact; this implementation does NOT simulate sub-hourly 20s "
            "slicing, explicit spread, or live L2 order-book impact. Fees/funding/hourly "
            "worst-price liquidation checks and slippage proxy may be modeled, but results "
            "must not be interpreted as evidence that 20s slicing/market impact were reproduced."
        ),
    }


def build_campaign_export(results, config, fixtures, timestamp, metrics=None):
    """Build an explicitly non-economic fixture smoke-test artifact."""
    export = {
        "timestamp": timestamp,
        "run_type": "fixture_smoke_test",
        "research_status": "SMOKE_TEST_ONLY",
        "data_provenance": {
            "source": "make_fixture_crash_rebound_multi",
            "kind": "synthetic_fixture",
            "real_market_data": False,
            "fabricated_data": True,
            "performance_evidence": False,
            "target_historical_window": {
                "start": "2025-12-20",
                "end": "2026-09-28",
                "status": "NOT_RUN",
                "days": 283,
            },
        },
        "execution_realism": _execution_realism_metadata(config),
        "symbols": sorted(fixtures),
        "candle_counts_by_symbol": {symbol: len(candles) for symbol, candles in fixtures.items()},
        "config": {
            "use_rsi_trigger": config.use_rsi_trigger,
            "rsi_period": config.rsi_period,
            "rsi_threshold": config.rsi_threshold,
            "enable_rebound_short": config.enable_rebound_short,
            "enable_eth_hedge": config.enable_eth_hedge,
            "hedge_cap_multiplier": config.hedge_cap_multiplier,
            "enable_volume_based_sizing": config.enable_volume_based_sizing,
            "position_size_pct_of_daily_volume": config.position_size_pct_of_daily_volume,
            "min_daily_volume_usd": config.min_daily_volume_usd,
            "gross_cap_pct": config.gross_cap_pct,
            "execution_model": getattr(config, "execution_model", "hourly_bar_simplified"),
            "order_slicing_simulated": bool(getattr(config, "order_slicing_simulated", False)),
            "order_book_impact_model": getattr(config, "order_book_impact_model", "slippage_proxy"),
            "spread_bps_assumed": getattr(config, "spread_bps_assumed", 0.0),
            "slippage_pct": getattr(config, "slippage_pct", None),
            "funding_rate_pct_per_hour": getattr(config, "funding_rate_pct_per_hour", None),
            "enable_liquidation_checks": bool(getattr(config, "enable_liquidation_checks", False)),
        },
        "results": {
            "total_pnl": results["total_pnl"],
            "num_trades": results["num_trades"],
            "final_open_positions": results["final_open_positions"],
            "final_gross_exposure": results["final_gross_exposure"],
            "trades": results["trades"],
        },
    }
    if metrics is not None:
        export["metrics"] = metrics
    return export


def build_parser():
    """CLI parser for the fixture campaign runner.

    Default outputs are unchanged (anchored result shape). Vault fee
    reconciliation is opt-in via --apply-vault-fees so existing artifacts
    and consumers are not silently altered.

    Explicit fee knobs (--aum-rate-annual, --profit-share-rate,
    --fee-hours-per-step) are validated fail-closed via
    src.metrics.vault_fees.validate_fee_config: negative/NaN/non-finite
    values are rejected with VaultFeeConfigError (no silent substitution).
    """
    ap = argparse.ArgumentParser(description="Fixture smoke-test campaign runner for CRASH-REBOUND-STRATEGY.")
    ap.add_argument("--apply-vault-fees", action="store_true", default=False,
                    help="Opt in: attach vault fee reconciliation (2%%/yr AUM + 10%% profit above HWM) "
                    "to campaign metrics/CSV/JSON outputs. Default off preserves anchored result shape.")
    ap.add_argument("--capital", type=float, default=100000.0,
                    help="Starting capital used for fee accrual (default 100000.0).")
    ap.add_argument("--aum-rate-annual", type=float, default=None,
                    help="Explicit AUM fee rate (default 0.02 = 2%%/yr when --apply-vault-fees). "
                         "Must be >= 0; negative/NaN/non-finite rejected fail-closed.")
    ap.add_argument("--profit-share-rate", type=float, default=None,
                    help="Explicit profit-share rate (default 0.10 = 10%% when --apply-vault-fees). "
                         "Must be >= 0; negative/NaN/non-finite rejected fail-closed.")
    ap.add_argument("--fee-hours-per-step", type=float, default=None,
                    help="Explicit fee accrual hours per step (default 1.0 when --apply-vault-fees). "
                         "Must be >= 0; negative/NaN/non-finite rejected fail-closed.")
    ap.add_argument("--fee-hours-from-timestamps", action="store_true", default=False,
                    help="Derive fee accrual hours from equity-curve timestamps (true elapsed hours "
                         "between points) instead of a flat hours-per-step. Use for exit-event equity "
                         "curves with multi-hour gaps so AUM fees are not under-charged. Default off.")
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    # Fail-closed fee-config validation: explicit knobs must be valid or the
    # run is rejected before any I/O. Unspecified knobs (None) are absent so
    # the module defaults apply (2%/yr, 10%, 1h).
    from src.metrics.vault_fees import fee_config_from_args, VaultFeeConfigError
    try:
        fee_kwargs = fee_config_from_args(args)
    except VaultFeeConfigError as e:
        print(f"BLOCKER: invalid vault fee config: {e}", file=sys.stderr)
        return 2
    print("=" * 70)
    print("FIXTURE SMOKE TEST ONLY - CRASH-REBOUND STRATEGY")
    print("=" * 70)
    print("Synthetic fixture data only. This is NOT a Hyperliquid historical backtest.")
    print("The 2025-12-20 to 2026-09-28 (283-day) research window has NOT been evaluated.")
    print(f"Start time: {datetime.now().isoformat()}")
    print()

    # Keep this runner explicitly fixture-only. The real historical campaign
    # requires an independently verified, complete hourly OHLCV cache and must
    # not silently substitute toy fixtures or a static candidate-symbol list.
    fixtures = make_fixture_crash_rebound_multi()
    print(f"Fixture symbols: {', '.join(sorted(fixtures))}")
    print(f"Fixture candle counts: { {k: len(v) for k, v in fixtures.items()} }")
    print()
    from src.data.loader import make_fixture_crash_rebound
    eth_candles = make_fixture_crash_rebound()

    config = StrategyConfig(
        use_rsi_trigger=True,
        enable_rebound_short=True,
        enable_eth_hedge=True,
        enable_volume_based_sizing=True,
        min_daily_volume_usd=5_000_000.0
    )

    results = run_portfolio_simulation(fixtures, config=config,
                                      capital=args.capital,
                                      eth_candles={'ETH': eth_candles})

    print("=" * 70)
    print("CAMPAIGN RESULTS")
    print("=" * 70)
    print(f"Total PnL: {results['total_pnl']:.4f}")
    print(f"Number of trades: {results['num_trades']}")
    print(f"Final open positions: {results['final_open_positions']}")
    print(f"Final gross exposure: {results['final_gross_exposure']:.2f}")
    print()
    print("Trade Details:")
    for t in results['trades']:
        print(f"  {t['symbol']:6s} | {t['exit_reason']:18s} | Total PnL: {t['total_pnl']:+.4f} | "
              f"Coin: {t['pnl']:+.4f} | Hedge: {t['hedge_pnl']:+.4f}")
    print("=" * 70)

    # Export results
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'research_state')
    os.makedirs(output_dir, exist_ok=True)

    # Compute full metrics suite from the trade list (robust to no-trade runs).
    # Vault fee reconciliation is opt-in; default off keeps anchored metric shape.
    # Explicit fee knobs (validated above) pass through to compute_campaign_metrics
    # so the AUM rate / profit-share rate / hours-per-step are honored.
    #
    # The portfolio simulation's equity_curve (one point per trade EXIT, with
    # exit timestamps) is passed through so --fee-hours-from-timestamps derives
    # the TRUE elapsed hours between exit points instead of a flat 1h step
    # (symmetric with run_real_campaign.py; without this the flag was silently
    # inert in this runner). When the flag is off, flat fee_hours_per_step applies
    # and the default result shape is unchanged.
    metrics = compute_campaign_metrics(trades=results["trades"],
                                       equity_curve=results.get("equity_curve"),
                                       initial_capital=args.capital,
                                       apply_vault_fees=args.apply_vault_fees,
                                       fee_use_timestamp_hours=args.fee_hours_from_timestamps,
                                       **fee_kwargs)
    metrics = metrics_to_dict(metrics)

    export_data = build_campaign_export(results, config, fixtures, datetime.now().isoformat(),
                                        metrics=metrics)

    with open(os.path.join(output_dir, 'campaign_results.json'), 'w') as f:
        json.dump(export_data, f, indent=2)

    # Export dedicated metrics artifacts
    with open(os.path.join(output_dir, 'campaign_metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=2, default=str)

    import csv
    with open(os.path.join(output_dir, 'campaign_metrics.csv'), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "value"])
        writer.writeheader()
        for row in metrics_to_csv_rows(metrics):
            writer.writerow(row)

    print(f"\nResults exported to research_state/campaign_results.json")
    print(f"Metrics exported to research_state/campaign_metrics.json and campaign_metrics.csv")


if __name__ == '__main__':
    main()
