#!/usr/bin/env python3
"""Full campaign validation runner for the test window."""
import json
import os
from datetime import datetime

from src.data.loader import make_fixture_crash_rebound_multi, get_hyperliquid_universe
from src.strategy.config import StrategyConfig
from scripts.run_portfolio import run_portfolio_simulation


def main():
    print("=" * 70)
    print("FULL CAMPAIGN VALIDATION - CRASH-REBOUND STRATEGY")
    print("=" * 70)
    print(f"Test window: 2025-12-20 to 2026-09-28 (283 days) - per spec")
    print(f"Start time: {datetime.now().isoformat()}")
    print()

    # Get universe
    universe = get_hyperliquid_universe(min_daily_volume_usd=5_000_000.0)
    print(f"Universe size: {len(universe)} coins")
    print(f"Universe: {', '.join(universe[:10])}..." if len(universe) > 10 else f"Universe: {', '.join(universe)}")
    print()

    # Use fixtures for validation
    fixtures = make_fixture_crash_rebound_multi()
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

    export_data = {
        'timestamp': datetime.now().isoformat(),
        'config': {
            'use_rsi_trigger': config.use_rsi_trigger,
            'enable_rebound_short': config.enable_rebound_short,
            'enable_eth_hedge': config.enable_eth_hedge,
            'min_daily_volume_usd': config.min_daily_volume_usd,
            'gross_cap_pct': config.gross_cap_pct,
        },
        'results': {
            'total_pnl': results['total_pnl'],
            'num_trades': results['num_trades'],
            'final_open_positions': results['final_open_positions'],
            'final_gross_exposure': results['final_gross_exposure'],
            'trades': results['trades']
        }
    }

    with open(os.path.join(output_dir, 'campaign_results.json'), 'w') as f:
        json.dump(export_data, f, indent=2)

    print(f"\nResults exported to research_state/campaign_results.json")


if __name__ == '__main__':
    main()
