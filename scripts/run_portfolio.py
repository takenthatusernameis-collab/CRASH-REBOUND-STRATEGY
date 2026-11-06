#!/usr/bin/env python3
"""Portfolio/multi-trade simulation runner."""
import json
import os
import copy
from datetime import datetime
from typing import Dict, List, Any

from src.data.loader import make_fixture_crash_rebound_multi, make_fixture_crash_rebound, load_multi_coin_data
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import generate_signal, backtest_crash_rebound, filter_universe
from src.strategy.risk import RiskState
from src.backtest.engine import backtest_simple


def _crash_severity(candles, sig, config, cache=None):
    """Return a sort key where smaller means higher priority (deeper crash first).

    RSI trigger: lower RSI => more severe (use -RSI in first element? easier: (rsi, 0)).
    Drop trigger: most negative drop in the recent crash window => more severe.
    """
    try:
        from src.strategy.crash_rebound import _rsi
        rsi = _rsi(candles[: max(1, getattr(sig, "signal_index", len(candles)-1) + 1)],
                   period=getattr(config, "rsi_period", 21), cache=cache)
        if getattr(config, 'use_rsi_trigger', False) and rsi is not None:
            return (float(rsi), 0.0)  # lower RSI first
    except Exception:
        pass
    try:
        sig_idx = max(1, min(getattr(sig, "signal_index", len(candles)-1), len(candles)-1))
        lookback = max(1, int(getattr(config, "crash_lookback", 5)))
        start = max(1, sig_idx - lookback + 1)
        worst = 0.0
        for idx in range(start, sig_idx + 1):
            cur = candles[idx]
            prev = candles[idx - 1]
            oo = cur.get("open"); cc = cur.get("close"); pc = prev.get("close")
            if oo and cc and float(oo) > 0:
                worst = min(worst, (float(cc) - float(oo)) / float(oo))
            if pc and cc and float(pc) > 0:
                worst = min(worst, (float(cc) - float(pc)) / float(pc))
        return (0.0, worst)  # more negative first
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

    # Per-symbol RSI cache (length-keyed): the scanner advances one bar at a time
    # over each symbol's full series, so identical-length prefixes hit the cache.
    # This turns the scanner's O(n^2) RSI cost into O(n) per symbol. Caller-owned
    # (no global state); uncached callers (tests) are unaffected.
    rsi_cache = {sym: {} for sym in filtered_symbols}

    max_len = max((len(v) for v in candles_by_symbol.values()), default=0)
    # Bar-by-bar scan across the full series (no look-ahead): use history up to i.
    # Start as early as indicators can be meaningful while letting signal/indicator
    # guards reject insufficient history. RSI trigger needs RSI period history;
    # drop trigger only needs crash lookback.
    if getattr(config, 'use_rsi_trigger', False):
        warmup = max(2, getattr(config, 'rsi_period', 21))
    else:
        warmup = max(2, getattr(config, 'crash_lookback', 5))

    for i in range(warmup, max_len):
        # free symbols whose prior trade ended before/at i
        for sym in list(occupied_until.keys()):
            if occupied_until[sym] < i:
                del occupied_until[sym]
        # Reconcile same-bar admission placeholders: if nothing is occupied, no positions
        # are open across the portfolio at this bar boundary.
        if not occupied_until:
            risk_state.open_positions = 0
            risk_state.open_position_notionals = []
            risk_state.gross_exposure = 0.0

# Same-decision-bar reservation: candidates fired at decision bar i are probed
        # against a copy of risk_state, and each probe runs the trade to its exit.
        # Without reserving, a probe that exits within the decision bar frees
        # max_positions/gross-cap capacity for later same-bar candidates,
        # violating the spec's concurrent-cap intent. The committed state below
        # re-adds the candidate's entry notional so later same-bar probes see the
        # accumulated exposure and apply equal-share cuts across old+new.

        candidates = []
        for symbol in filtered_symbols:
            if symbol in occupied_until:
                continue
            candles = candles_by_symbol.get(symbol)
            if not candles or i >= len(candles):
                continue
            try:
                hist = candles[:i + 1]
                sig = generate_signal(hist, symbol=symbol, config=config, capital=capital,
                                      cache=rsi_cache.get(symbol))
                if sig is not None:
                    # normalize signal_index to decision bar on full series
                    sig.signal_index = i
                    sev = _crash_severity(hist, sig, config, cache=rsi_cache.get(symbol))
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
                # Probe admission in priority order (deepest first) so max_positions/gross-cap
                # decisions for the same decision bar reflect earlier accepted candidates.
                max_pos = getattr(config, 'max_positions', None)
                if max_pos is not None and risk_state.open_positions >= max_pos:
                    # Capacity for this decision bar is exhausted; later candidates
                    # (including ones that would exit within the bar) must wait.
                    continue
                probe_state = copy.deepcopy(risk_state)
                res = backtest_simple(candles, sig, config=config, capital=capital,
                                      risk_state=probe_state, eth_candles=eth_data)
                if res.exit_reason not in ('blocked', 'no_signal'):
                    # Commit probe state and record trade.
                    # The engine/backtest runs to completion on the probe state and applies
                    # its own risk_state accounting (cap cuts, opens/closes). We must not
                    # re-add notionals here (that double-counts). For same-decision-bar
                    # admission we need later probes to see that capacity was consumed by
                    # this accepted trade: if the probe finished with the position closed
                    # (exit within/at the probed window from the engine's perspective) we
                    # record a reserved notional placeholder derived from the executed
                    # trade so max_positions/gross-cap checks and equal-share cuts reflect
                    # concurrent admission intent. The placeholder is cleared when the
                    # symbol's occupancy ends.
                    risk_state = probe_state
                    trade_pnl = getattr(res, 'total_pnl', res.pnl)
                    total_pnl += trade_pnl
                    bars_held = getattr(res, 'bars_held', 0) or 0
                    start_idx = getattr(sig, 'signal_index', i)
                    if getattr(config, 'entry_next_bar', True) and start_idx + 1 < len(candles):
                        start_idx = start_idx + 1
                    exit_idx = min(len(candles) - 1, max(start_idx, start_idx + max(1, bars_held) - 1))
                    occupied_until[symbol] = exit_idx
                    entry_px = getattr(res, 'entry_price', 0.0)
                    executed_notional = float(res.shares) * float(entry_px) if entry_px > 0 and res.shares > 0 else 0.0
                    # If engine left risk_state consistent with an open position, trust it.
                    # Otherwise add a same-bar reservation placeholder (idempotent-ish: only
                    # when no notional was recorded for this admission).
                    if executed_notional > 0 and len(getattr(risk_state, 'open_position_notionals', [])) == 0 and getattr(risk_state, 'open_positions', 0) == 0:
                        cap_value = capital * getattr(config, 'gross_cap_pct', 120.0) / 100.0
                        risk_state.open_position_notionals = [min(executed_notional, cap_value)]
                        risk_state.gross_exposure = sum(risk_state.open_position_notionals)
                        risk_state.open_positions = len(risk_state.open_position_notionals)
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
        'rsi_cache': rsi_cache,
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
