#!/usr/bin/env python3
"""Full campaign validation runner for the test window."""
import json
import os
from datetime import datetime

from src.data.loader import make_fixture_crash_rebound_multi
from src.strategy.config import StrategyConfig
from scripts.run_portfolio import run_portfolio_simulation


def build_campaign_export(results, config, fixtures, timestamp):
    """Build an explicitly non-economic fixture smoke-test artifact."""
    return {
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
        },
        "results": {
            "total_pnl": results["total_pnl"],
            "num_trades": results["num_trades"],
            "final_open_positions": results["final_open_positions"],
            "final_gross_exposure": results["final_gross_exposure"],
            "trades": results["trades"],
        },
    }


def main():
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

    export_data = build_campaign_export(results, config, fixtures, datetime.now().isoformat())

    with open(os.path.join(output_dir, 'campaign_results.json'), 'w') as f:
        json.dump(export_data, f, indent=2)

    print(f"\nResults exported to research_state/campaign_results.json")


if __name__ == '__main__':
    main()
