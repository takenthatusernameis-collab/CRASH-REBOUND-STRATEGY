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

    # Do NOT prefilter by full-series universe/volume/regime here: that leaks
    # future bars (end-of-series state) into historical admission decisions.
    # Spec-compliant gating is applied per decision bar via generate_signal on
    # hist[:i+1], which enforces volume/regime/trigger without look-ahead.
    filtered_symbols = list(candles_by_symbol.keys())

    total_pnl = 0.0
    all_trades = []
    equity_curve = [{"timestamp": "", "equity": capital, "pnl": 0.0}]
    # symbol -> index of bar until which it is occupied (inclusive exit bar)
    occupied_until = {}
    # symbol -> reserved notional of a currently-open position (post-cut). Carried
    # across bars so an open position counts toward gross cap / max_positions for
    # later same-bar and future-bar admissions (no look-ahead into future bars).
    open_notionals = {}
    # Realized exits reconciled into master risk_state only when exit_idx <= i (no look-ahead).
    # Tuple: (exit_idx, exit_timestamp, trade_pnl). Master exposure is managed by overlay.
    pending_realized_exits = []

    def _sync_master_overlay(bar_date: str):
        risk_state.open_position_notionals = list(open_notionals.values())
        risk_state.gross_exposure = float(sum(risk_state.open_position_notionals))
        risk_state.open_positions = len(risk_state.open_position_notionals)
        if bar_date:
            day = str(bar_date)[:10]
            cur = str(getattr(risk_state, 'date', '') or '')[:10]
            if day and day != cur:
                risk_state.date = day
                risk_state.realized_pnl = 0.0
                risk_state.daily_loss_limit_hit = False
            elif not cur:
                risk_state.date = day

    def _reconcile_realized_through(bar_idx: int, max_len_local: int):
        if not pending_realized_exits:
            return
        # Apply in exit order; only exits known at/through bar_idx.
        pending_realized_exits.sort(key=lambda x: (x[0], str(x[1])))
        keep = []
        for exit_idx, exit_ts, trade_pnl in pending_realized_exits:
            if exit_idx <= bar_idx:
                day = str(exit_ts)[:10] if exit_ts else ''
                cur = str(getattr(risk_state, 'date', '') or '')[:10]
                if day and day != cur:
                    risk_state.date = day
                    risk_state.realized_pnl = 0.0
                    risk_state.daily_loss_limit_hit = False
                elif day and not cur:
                    risk_state.date = day
                risk_state.realized_pnl = float(getattr(risk_state, 'realized_pnl', 0.0) or 0.0) + float(trade_pnl)
                if capital > 0:
                    try:
                        if risk_state.daily_loss_pct(capital) >= getattr(config, 'max_daily_loss_pct', 3.0):
                            risk_state.daily_loss_limit_hit = True
                    except Exception:
                        pass
            else:
                keep.append((exit_idx, exit_ts, trade_pnl))
        pending_realized_exits[:] = keep

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
        # Reconcile exits realized at or before this decision bar (no look-ahead), then
        # sync master exposure from the reservation overlay.
        _reconcile_realized_through(i, max_len)
        # infer bar date from any symbol with this bar
        _bar_ts = ''
        for _s in filtered_symbols:
            _cd = candles_by_symbol.get(_s)
            if _cd and i < len(_cd):
                _bar_ts = str(_cd[i].get('timestamp', '') or '')
                if _bar_ts:
                    break
        _sync_master_overlay(_bar_ts)
        # free symbols whose prior trade ended before/at i, releasing their reserved notional
        for sym in list(occupied_until.keys()):
            if occupied_until[sym] < i:
                del occupied_until[sym]
                open_notionals.pop(sym, None)
        _sync_master_overlay(_bar_ts)
        # Persistent same-bar reservation overlay (symbol -> reserved notional), carried
        # across bars so an open position counts toward gross cap / max_positions for
        # later same-bar and future-bar admissions. Derived from open_notionals, not from
        # the stale risk_state, so cross-bar exposure is never dropped.

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

        # Same-bar admission reservation overlay (deepest crash first). Real-engine probe
        # runs to completion for execution realism, but sibling admission/capacity uses only
        # reservation state — a probe's future exit/daily PnL must not distort same-bar
        # concurrent 120% cap / max_positions / equal-share-cut decisions. Master realized
        # PnL/halt reflect only exits reconciled at/through bar i (no look-ahead).
        _bar_notionals = list(open_notionals.values())
        _bar_gross = float(sum(_bar_notionals))
        _bar_open_positions = len(_bar_notionals)
        _bar_realized = float(getattr(risk_state, 'realized_pnl', 0.0) or 0.0)
        _bar_daily_hit = bool(getattr(risk_state, 'daily_loss_limit_hit', False))
        _bar_date = getattr(risk_state, 'date', '')

        for sev, symbol, sig, candles in candidates:
            if symbol in occupied_until:
                continue
            try:
                max_pos = getattr(config, 'max_positions', None)
                if max_pos is not None and _bar_open_positions >= max_pos:
                    continue
                probe_state = copy.deepcopy(risk_state)
                probe_state.open_positions = _bar_open_positions
                probe_state.open_position_notionals = list(_bar_notionals)
                probe_state.gross_exposure = _bar_gross
                probe_state.realized_pnl = _bar_realized
                probe_state.daily_loss_limit_hit = _bar_daily_hit
                probe_state.date = _bar_date
                res = backtest_simple(candles, sig, config=config, capital=capital,
                                      risk_state=probe_state, eth_candles=eth_data)
                if res.exit_reason not in ('blocked', 'no_signal'):
                    # total_pnl is authoritative (engine always sets it on TradeResult).
                    # If ever absent, compute the grand total from all legs rather
                    # than falling back to bare `pnl`, which would silently drop
                    # rebound_short_pnl / rebound_hedge_pnl.
                    trade_pnl = getattr(res, 'total_pnl', None)
                    if trade_pnl is None:
                        trade_pnl = (
                            float(getattr(res, 'pnl', 0.0) or 0.0)
                            + float(getattr(res, 'hedge_pnl', 0.0) or 0.0)
                            + float(getattr(res, 'rebound_short_pnl', 0.0) or 0.0)
                            + float(getattr(res, 'rebound_hedge_pnl', 0.0) or 0.0)
                        )
                    total_pnl += trade_pnl
                    bars_held = getattr(res, 'bars_held', 0) or 0
                    start_idx = getattr(sig, 'signal_index', i)
                    if getattr(config, 'entry_next_bar', True) and start_idx + 1 < len(candles):
                        start_idx = start_idx + 1
                    exit_idx = min(len(candles) - 1, max(start_idx, start_idx + max(1, bars_held) - 1))
                    occupied_until[symbol] = exit_idx
                    _exit_ts = getattr(res, 'exit_timestamp', '') or (candles[exit_idx].get('timestamp', '') if exit_idx < len(candles) else '')
                    pending_realized_exits.append((int(exit_idx), str(_exit_ts), float(trade_pnl)))
                    entry_px = getattr(res, 'entry_price', 0.0)
                    # TradeResult.max_live_coin_notional is authoritative: it is the
                    # max live coin-position notional across the long-entry leg and the
                    # rebound-short-entry leg (hedges excluded from the 120% cap
                    # context). No leg-log parsing needed here.
                    executed_notional = float(getattr(res, 'max_live_coin_notional', 0.0) or 0.0)
                    if executed_notional <= 0 and entry_px > 0 and res.shares > 0:
                        executed_notional = float(res.shares) * float(entry_px)
                    if executed_notional > 0:
                        cap_value = capital * getattr(config, 'gross_cap_pct', 120.0) / 100.0
                        # Reconcile the reservation overlay from the engine's ACTUAL
                        # post-run position schedule (probe_state.open_position_notionals),
                        # which is authoritative for both the cut and no-cut cases:
                        #   - cut fired: equal shares of the cap across old+new (cuts only,
                        #     never top-ups — the engine never inflates an open position);
                        #   - no cut:    old positions unchanged, this admission reserved
                        #     at its executed notional.
                        # Mapping is positional: the engine appends the new position after
                        # the existing open positions in overlay order, so the first
                        # len(open_notionals) entries are the existing symbols and the
                        # last entry is this admission. NEVER recompute an equal share
                        # unconditionally — that tops up open positions to the cap even
                        # when no cut fired, inflating reserved exposure and distorting
                        # future admissions (spec: cuts only, never top-ups).
                        post_notionals = list(getattr(probe_state, 'open_position_notionals', []) or [])
                        existing_syms = list(open_notionals.keys())
                        if post_notionals and len(post_notionals) == len(existing_syms) + 1:
                            for _sym, _not in zip(existing_syms, post_notionals[:len(existing_syms)]):
                                open_notionals[_sym] = float(_not)
                            open_notionals[symbol] = float(post_notionals[-1])
                        else:
                            # Fallback: reserve this admission at its executed notional
                            # (capped); leave existing open positions unchanged.
                            open_notionals[symbol] = min(executed_notional, cap_value)
                        _bar_notionals = list(open_notionals.values())
                        _bar_gross = float(sum(_bar_notionals))
                        _bar_open_positions = len(_bar_notionals)
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

    # Reconcile any exits realized at/after the final scanned bar (no future bars exist).
    _reconcile_realized_through(max_len - 1 if max_len > 0 else 0, max_len)
    _sync_master_overlay('')
    risk_state.open_position_notionals = list(open_notionals.values())
    risk_state.gross_exposure = float(sum(open_notionals.values()))
    risk_state.open_positions = len(open_notionals)
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
