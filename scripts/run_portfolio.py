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


def _crash_severity(candles, sig, config):
    try:
        from src.strategy.crash_rebound import _rsi
        rsi = _rsi(candles[: max(1, getattr(sig, "signal_index", len(candles)-1) + 1)],
                   period=getattr(config, "rsi_period", 21))
        if rsi is not None:
            return (-float(rsi), 0.0)  # lower RSI => more severe
    except Exception:
        pass
    try:
        idx = max(1, min(getattr(sig, "signal_index", len(candles)-1), len(candles)-1))
        cur = candles[idx]
        prev = candles[idx - 1]
        drops = []
        oo = cur.get("open"); cc = cur.get("close"); pc = prev.get("close")
        if oo and cc and float(oo) > 0:
            drops.append((float(cc) - float(oo)) / float(oo))
        if pc and cc and float(pc) > 0:
            drops.append((float(cc) - float(pc)) / float(pc))
        if drops:
            return (0.0, min(drops))
    except Exception:
        pass
    return (0.0, 0.0)


def run_portfolio_simulation(candles_by_symbol: Dict[str, List[Dict[str, Any]]],
                             config: StrategyConfig = None,
                             capital: float = 100000.0,
                             eth_candles: Dict[str, List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Run portfolio simulation across multiple coins with concurrent positions.

    Bar-by-bar scan over the full series (no look-ahead): at each decision bar, evaluate
    crash/rebound using history up to that bar; when multiple symbols fire at the same bar,
    process deepest crash first (spec). Enforces one position per coin (no overlapping entries
    for a symbol while its prior trade is open). Gross cap / equal-share cuts and max positions
    are enforced by backtest/risk_state.
    """
    if config is None:
        config = StrategyConfig(use_rsi_trigger=False)

    risk_state = RiskState(date="")
    eth_data = eth_candles.get('ETH') if eth_candles else None

    filtered_symbols = filter_universe(candles_by_symbol,
                                       min_daily_volume_usd=config.min_daily_volume_usd,
                                       regime_config=config)

    total_pnl = 0.0
    all_trades = []
    equity_curve = [{"timestamp": "", "equity": capital, "pnl": 0.0}]
    # symbol -> index of bar until which it is occupied (inclusive exit bar)
    occupied_until = {}

    max_len = max((len(v) for v in candles_by_symbol.values()), default=0)
    warmup = max(getattr(config, 'rsi_period', 21) + 2,
                 getattr(config, 'atr_period', 14) + 2,
                 getattr(config, 'crash_lookback', 5) + 2, 3)

    for i in range(warmup, max_len):
        # free symbols whose prior trade ended before/at i
        for sym in list(occupied_until.keys()):
            if occupied_until[sym] < i:
                del occupied_until[sym]

        candidates = []
        for symbol in filtered_symbols:
            if symbol in occupied_until:
                continue
            candles = candles_by_symbol.get(symbol)
            if not candles or i >= len(candles):
                continue
            try:
                hist = candles[:i + 1]
                sig = generate_signal(hist, symbol=symbol, config=config, capital=capital)
                if sig is not None:
                    # normalize signal_index to decision bar on full series
                    sig.signal_index = i
                    sev = _crash_severity(hist, sig, config)
                    candidates.append((sev, symbol, sig, candles))
            except Exception:
                continue

        if not candidates:
            continue
        # deepest crash first
        candidates.sort(key=lambda x: (x[0][0], x[0][1]))

        for sev, symbol, sig, candles in candidates:
            if symbol in occupied_until:
                continue
            try:
                res = backtest_simple(candles, sig, config=config, capital=capital,
                                      risk_state=risk_state, eth_candles=eth_data)
                if res.exit_reason not in ('blocked', 'no_signal'):
                    trade_pnl = getattr(res, 'total_pnl', res.pnl)
                    total_pnl += trade_pnl
                    bars_held = getattr(res, 'bars_held', 0) or 0
                    # start_idx in engine: signal_index or signal_index+1 if next bar entry
                    start_idx = getattr(sig, 'signal_index', i)
                    if getattr(config, 'entry_next_bar', True) and start_idx + 1 < len(candles):
                        start_idx = start_idx + 1
                    exit_idx = min(len(candles) - 1, max(start_idx, start_idx + max(1, bars_held) - 1))
                    occupied_until[symbol] = exit_idx
                    all_trades.append({
                        'symbol': symbol,
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
                    equity_curve.append({
                        'timestamp': getattr(res, 'exit_timestamp', ''),
                        'equity': capital + total_pnl,
                        'pnl': trade_pnl,
                    })
                elif res.exit_reason == 'blocked':
                    # blocked by risk/cap; symbol not occupied
                    pass
            except Exception:
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
