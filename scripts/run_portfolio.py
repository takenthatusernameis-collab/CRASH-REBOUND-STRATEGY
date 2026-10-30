#!/usr/bin/env python3
"""Sequential final-bar signal screen; not a chronological portfolio backtest."""
import json
import os
from datetime import datetime
from typing import Dict, List, Any

from src.data.loader import make_fixture_crash_rebound_multi, make_fixture_crash_rebound, load_multi_coin_data
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import generate_signal, backtest_crash_rebound, filter_universe
from src.strategy.risk import RiskState
from src.backtest.engine import backtest_simple


def run_portfolio_simulation(candles_by_symbol: Dict[str, List[Dict[str, Any]]],
                             config: StrategyConfig = None,
                             capital: float = 100000.0,
                             eth_candles: Dict[str, List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Screen one final-bar signal per coin and simulate candidates sequentially.

    This prototype does not process every hourly bar as a shared event stream
    and does not maintain concurrently open positions across symbols. It is
    useful for fixture/integration checks only, not historical portfolio
    performance inference.
    """
    if config is None:
        config = StrategyConfig(use_rsi_trigger=False)

    risk_state = RiskState(date="")
    results = []
    eth_data = eth_candles.get('ETH') if eth_candles else None

    # Filter universe
    filtered_symbols = filter_universe(candles_by_symbol,
                                       min_daily_volume_usd=config.min_daily_volume_usd,
                                       regime_config=config)

    # Collect all potential signals with timestamps for ordering (deepest crash first per spec)
    signals_list = []
    for symbol in filtered_symbols:
        candles = candles_by_symbol[symbol]
        try:
            sig = generate_signal(candles, symbol=symbol, config=config, capital=capital)
            if sig is not None:
                signals_list.append({
                    'symbol': symbol,
                    'signal': sig,
                    'candles': candles,
                    'priority': 0  # Could compute crash depth
                })
        except Exception as e:
            continue

    # Sort by deepest crash first (higher priority = deeper crash) - simple heuristic
    # In practice, would look at magnitude of drop
    signals_list.sort(key=lambda x: x['signal'].entry_price, reverse=True)

    # Simulate with risk management
    total_pnl = 0.0
    all_trades = []

    for item in signals_list:
        if risk_state.open_positions >= config.max_positions:
            break
        try:
            res = backtest_simple(item['candles'], item['signal'],
                                 config=config, capital=capital,
                                 risk_state=risk_state,
                                 eth_candles=eth_data)
            if res.exit_reason != 'blocked' and res.exit_reason != 'no_signal':
                total_pnl += getattr(res, 'total_pnl', res.pnl)
                all_trades.append({
                    'symbol': item['symbol'],
                    'exit_reason': res.exit_reason,
                    'pnl': res.pnl,
                    'total_pnl': getattr(res, 'total_pnl', res.pnl),
                    'hedge_pnl': getattr(res, 'hedge_pnl', 0.0),
                    'shares': res.shares
                })
        except Exception as e:
            continue

    return {
        'simulation_mode': 'sequential_final_bar_screen',
        'historical_portfolio_validated': False,
        'performance_inference_permitted': False,
        'max_signals_per_symbol': 1,
        'total_pnl': total_pnl,
        'num_trades': len(all_trades),
        'trades': all_trades,
        'final_open_positions': risk_state.open_positions,
        'final_gross_exposure': risk_state.gross_exposure,
        'risk_state': risk_state
    }


def main():
    print("=" * 60)
    print("FIXTURE DEMO ONLY - NOT A HISTORICAL CONCURRENT PORTFOLIO BACKTEST")
    print("=" * 60)

    # Use fixtures for now
    fixtures = make_fixture_crash_rebound_multi()
    eth_candles = make_fixture_crash_rebound()  # Use as ETH proxy

    config = StrategyConfig(use_rsi_trigger=False, enable_rebound_short=True)
    results = run_portfolio_simulation(fixtures, config=config,
                                      eth_candles={'ETH': eth_candles})

    print(f"Total PnL: {results['total_pnl']:.4f}")
    print(f"Number of trades: {results['num_trades']}")
    print(f"Open positions: {results['final_open_positions']}")
    print(f"Gross exposure: {results['final_gross_exposure']:.2f}")
    print("\nTrades:")
    for t in results['trades']:
        print(f"  {t['symbol']}: {t['exit_reason']} | PnL={t['total_pnl']:.4f} | Hedge={t['hedge_pnl']:.4f}")
    print("=" * 60)


if __name__ == '__main__':
    main()
