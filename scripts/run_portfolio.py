#!/usr/bin/env python3
"""Portfolio/multi-trade simulation runner."""
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
    """Run portfolio simulation across multiple coins with concurrent positions."""
    if config is None:
        config = StrategyConfig(use_rsi_trigger=False)

    risk_state = RiskState(date="")
    results = []
    eth_data = eth_candles.get('ETH') if eth_candles else None

    # Filter universe
    filtered_symbols = filter_universe(candles_by_symbol,
                                       min_daily_volume_usd=config.min_daily_volume_usd,
                                       regime_config=config)

    # Collect all potential signals; deepest crash first per spec.
    # Severity proxy: prefer lower RSI(21) at signal (deeper oversold). Fallback to
    # largest recent drop magnitude when RSI unavailable.
    def _crash_severity(candles, sig, config):
        try:
            from src.strategy.crash_rebound import _rsi
            rsi = _rsi(candles[: max(1, getattr(sig, "signal_index", len(candles)-1) + 1)],
                       period=getattr(config, "rsi_period", 21))
            if rsi is not None:
                # lower RSI => more severe; sort descending by (-rsi)
                return (-float(rsi), 0.0)
        except Exception:
            pass
        try:
            idx = max(1, min(getattr(sig, "signal_index", len(candles)-1), len(candles)-1))
            cur = candles[idx]
            prev = candles[idx - 1]
            co, cc, pc = cur.get("close"), cur.get("close"), prev.get("close")
            oo = cur.get("open")
            drops = []
            if oo and cc and oo > 0:
                drops.append((float(cc) - float(oo)) / float(oo))
            if pc and cc and pc > 0:
                drops.append((float(cc) - float(pc)) / float(pc))
            if drops:
                return (0.0, min(drops))  # more negative = deeper
        except Exception:
            pass
        return (0.0, 0.0)

    signals_list = []
    for symbol in filtered_symbols:
        candles = candles_by_symbol[symbol]
        try:
            sig = generate_signal(candles, symbol=symbol, config=config, capital=capital)
            if sig is not None:
                sev = _crash_severity(candles, sig, config)
                signals_list.append({
                    'symbol': symbol,
                    'signal': sig,
                    'candles': candles,
                    'severity': sev,
                })
        except Exception:
            continue

    # Sort deepest crash first: lower RSI first, then more negative drop.
    signals_list.sort(key=lambda x: (x['severity'][0], x['severity'][1]))

    # Simulate with risk management
    total_pnl = 0.0
    all_trades = []
    # Build a timestamped equity curve: cumulative PnL keyed by exit timestamp.
    # We start at capital and walk through trades in chronological exit order.
    equity_curve = [{"timestamp": "", "equity": capital, "pnl": 0.0}]

    for item in signals_list:
        if risk_state.open_positions >= config.max_positions:
            break
        try:
            res = backtest_simple(item['candles'], item['signal'],
                                 config=config, capital=capital,
                                 risk_state=risk_state,
                                 eth_candles=eth_data)
            if res.exit_reason != 'blocked' and res.exit_reason != 'no_signal':
                trade_pnl = getattr(res, 'total_pnl', res.pnl)
                total_pnl += trade_pnl
                all_trades.append({
                    'symbol': item['symbol'],
                    'exit_reason': res.exit_reason,
                    'pnl': res.pnl,
                    'total_pnl': trade_pnl,
                    'hedge_pnl': getattr(res, 'hedge_pnl', 0.0),
                    'shares': res.shares,
                    'entry_timestamp': getattr(res, 'entry_timestamp', ''),
                    'exit_timestamp': getattr(res, 'exit_timestamp', ''),
                    'r_multiple': getattr(res, 'r_multiple', 0.0),
                    'bars_held': getattr(res, 'bars_held', 0),
                    'hedge_side': getattr(res, 'hedge_side', None),
                    'hedge_size': getattr(res, 'hedge_size', 0.0),
                })
                # Append to equity curve at exit timestamp
                equity_curve.append({
                    'timestamp': getattr(res, 'exit_timestamp', ''),
                    'equity': capital + total_pnl,
                    'pnl': trade_pnl,
                })
        except Exception as e:
            continue

    return {
        'total_pnl': total_pnl,
        'num_trades': len(all_trades),
        'trades': all_trades,
        'final_open_positions': risk_state.open_positions,
        'final_gross_exposure': risk_state.gross_exposure,
        'risk_state': risk_state,
        'equity_curve': equity_curve,
        'starting_capital': capital,
    }


def main():
    print("=" * 60)
    print("PORTFOLIO SIMULATION - CRASH-REBOUND STRATEGY")
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
