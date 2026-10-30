from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from src.strategy.config import StrategyConfig, DEFAULT_CONFIG
from src.strategy.risk import DailyRiskState


@dataclass
class TradeResult:
    pnl: float
    r_multiple: float
    exit_reason: str
    entry_price: float = 0.0
    exit_price: float = 0.0
    shares: float = 0.0
    bars_held: int = 0
    trades: Optional[List[Dict[str, Any]]] = None  # For multi-leg trades (e.g., crash + rebound)



def _slippage_commission_per_share(price: float, config: StrategyConfig, side: str) -> float:
    slip = price * config.slippage_pct
    comm = config.commission_per_share
    return price + slip + comm if side == "buy" else price - slip - comm


def backtest_simple(
    candles: List[Dict[str, Any]],
    signal,
    config: StrategyConfig = DEFAULT_CONFIG,
    capital: float = 100000.0,
    risk_state: Optional[DailyRiskState] = None,
) -> TradeResult:
    if signal is None:
        return TradeResult(pnl=0.0, r_multiple=0.0, exit_reason='no_signal')
    entry = signal.entry_price
    stop = signal.stop_price
    target = signal.target_price
    risk = signal.risk_per_share
    shares = signal.size_shares if getattr(signal, 'size_shares', 0) > 0 else 1.0

    signal_index = getattr(signal, 'signal_index', -1)
    if signal_index < 0 or signal_index >= len(candles):
        signal_index = len(candles) - 1

    # Entry price: next-bar open when enabled and a next bar exists; else signal close.
    entry_px = entry
    start_idx = signal_index
    if config.entry_next_bar and signal_index + 1 < len(candles):
        next_open = candles[signal_index + 1].get('open')
        if next_open is not None:
            entry_px = float(next_open)
            start_idx = signal_index + 1
    entry_px = _slippage_commission_per_share(entry_px, config, 'buy')

    stop_px = stop
    target_px = target

    # Risk gate before entry: max positions and daily-loss halt.
    if risk_state is not None:
        entry_date = str(candles[start_idx].get('timestamp', ''))
        check = risk_state.check_position(config, capital, shares, entry_px)
        if not check.allowed:
            return TradeResult(
                pnl=0.0, r_multiple=0.0, exit_reason='blocked',
                entry_price=entry, exit_price=entry, shares=0.0, bars_held=0,
            )
        if check.size_shares > 0:
            shares = check.size_shares
        risk_state.apply_trade(entry_date, 0.0, opened=True, closed=False)

    trades_log = []
    # Look-ahead guard: only inspect candles at or after the entry point.
    for idx in range(start_idx, len(candles)):
        c = candles[idx]
        low = c.get('low')
        high = c.get('high')
        if low is not None and low <= stop_px:
            exit_px = _slippage_commission_per_share(stop_px, config, 'sell')
            pnl = (exit_px - entry_px) * shares
            r_mult = pnl / (risk * shares) if risk > 0 and shares > 0 else 0.0
            if risk_state is not None:
                risk_state.apply_trade(str(c.get('timestamp', '')), pnl, opened=False, closed=True)
            trades_log.append({'side': 'long', 'entry': entry_px, 'exit': exit_px, 'pnl': pnl, 'reason': 'stopped'})
            return TradeResult(
                pnl=pnl, r_multiple=r_mult, exit_reason='stopped',
                entry_price=entry_px, exit_price=exit_px, shares=shares,
                bars_held=idx - start_idx + 1,
                trades=trades_log,
            )
        if high is not None and high >= target_px:
            exit_px = _slippage_commission_per_share(target_px, config, 'sell')
            pnl = (exit_px - entry_px) * shares
            r_mult = pnl / (risk * shares) if risk > 0 and shares > 0 else 0.0
            if risk_state is not None:
                risk_state.apply_trade(str(c.get('timestamp', '')), pnl, opened=False, closed=True)
            trades_log.append({'side': 'long', 'entry': entry_px, 'exit': exit_px, 'pnl': pnl, 'reason': 'target'})
            total_pnl = pnl
            total_r_mult = r_mult
            total_bars = idx - start_idx + 1
            # Rebound short logic when buy hits +9% target fast
            if getattr(config, 'enable_rebound_short', True):
                short_entry_px = _slippage_commission_per_share(exit_px, config, 'short')  # enter short at/near target exit
                # For short, slippage is adverse when going up? _slippage_commission_per_share: if side=='buy' add costs; else subtract costs? Wait look:
                # "slip = price * config.slippage_pct; comm = config.commission_per_share; return price + slip + comm if side == 'buy' else price - slip - comm"
                # So for sell side (closing long) they subtract slip/comm (get less). For short entry, selling short - but function takes side parameter; better to be explicit.
                # Actually better use same convention: for short entry (sell to open), treat as sell side costs? Or just apply sell-side slippage/commission
                short_entry_px = _slippage_commission_per_share(exit_px, config, 'sell')  # enter short
                short_target = short_entry_px * (1.0 - getattr(config, 'rebound_short_target_pct', 9.0) / 100.0)
                short_stop = short_entry_px * (1.0 + getattr(config, 'rebound_short_stop_pct', 40.0) / 100.0)
                short_start_idx = idx
                short_shares = shares  # use same size
                short_bars_max = getattr(config, 'rebound_short_time_exit_bars', 48)
                for sidx in range(short_start_idx + 1, len(candles)):
                    sc = candles[sidx]
                    slow = sc.get('low')
                    shigh = sc.get('high')
                    # For short: stop if price rises above short_stop; target if price falls to short_target
                    if shigh is not None and shigh >= short_stop:
                        short_exit = _slippage_commission_per_share(short_stop, config, 'buy')  # cover
                        short_pnl = (short_entry_px - short_exit) * short_shares
                        if risk_state is not None:
                            risk_state.apply_trade(str(sc.get('timestamp', '')), short_pnl, opened=False, closed=True)
                        trades_log.append({'side': 'short', 'entry': short_entry_px, 'exit': short_exit, 'pnl': short_pnl, 'reason': 'stopped'})
                        total_pnl += short_pnl
                        total_bars = max(total_bars, (sidx - start_idx + 1))
                        break
                    if slow is not None and slow <= short_target:
                        short_exit = _slippage_commission_per_share(short_target, config, 'buy')
                        short_pnl = (short_entry_px - short_exit) * short_shares
                        if risk_state is not None:
                            risk_state.apply_trade(str(sc.get('timestamp', '')), short_pnl, opened=False, closed=True)
                        trades_log.append({'side': 'short', 'entry': short_entry_px, 'exit': short_exit, 'pnl': short_pnl, 'reason': 'target'})
                        total_pnl += short_pnl
                        total_bars = max(total_bars, (sidx - start_idx + 1))
                        break
                    if (sidx - short_start_idx) >= short_bars_max:
                        sclose = sc.get('close', short_entry_px)
                        short_exit = _slippage_commission_per_share(float(sclose), config, 'buy')
                        short_pnl = (short_entry_px - short_exit) * short_shares
                        if risk_state is not None:
                            risk_state.apply_trade(str(sc.get('timestamp', '')), short_pnl, opened=False, closed=True)
                        trades_log.append({'side': 'short', 'entry': short_entry_px, 'exit': short_exit, 'pnl': short_pnl, 'reason': 'time_exit'})
                        total_pnl += short_pnl
                        total_bars = max(total_bars, (sidx - start_idx + 1))
                        break
                else:
                    # If short not exited in loop (ran to end)
                    if len(candles) > short_start_idx + 1:  # might have started but not broken
                        pass  # will be handled if broken
                    # If no break occurred and we went through all bars
                    if 'short_pnl' not in locals() or trades_log and trades_log[-1].get('side') != 'short':
                        # try to exit at last bar
                        last_sc = candles[-1]
                        sclose = last_sc.get('close', short_entry_px)
                        short_exit = _slippage_commission_per_share(float(sclose), config, 'buy')
                        short_pnl = (short_entry_px - short_exit) * short_shares
                        if risk_state is not None:
                            risk_state.apply_trade(str(last_sc.get('timestamp', '')), short_pnl, opened=False, closed=True)
                        trades_log.append({'side': 'short', 'entry': short_entry_px, 'exit': short_exit, 'pnl': short_pnl, 'reason': 'time_exit'})
                        total_pnl += short_pnl
                        total_bars = max(total_bars, len(candles) - start_idx)
            if risk_state is not None and 'total_pnl' in locals() and abs(total_pnl - pnl) > 1e-18:  # we added short
                pass  # already applied above
            # recompute r_mult for total if short added
            if getattr(config, 'enable_rebound_short', True) and len(trades_log) > 1 and trades_log[-1].get('side') == 'short':
                # Total risk across both legs: long risk + short risk (each leg sized same)
                total_risk = risk * shares * 2.0
                if total_risk > 0:
                    total_r_mult = total_pnl / total_risk
                else:
                    total_r_mult = total_r_mult
            else:
                total_r_mult = r_mult
            return TradeResult(
                pnl=total_pnl if 'total_pnl' in locals() else pnl,
                r_multiple=total_r_mult if 'total_r_mult' in locals() else r_mult,
                exit_reason='target_rebound_short' if (len(trades_log) > 1 and any(t.get('side') == 'short' for t in trades_log)) else 'target',
                entry_price=entry_px, exit_price=exit_px, shares=shares,
                bars_held=total_bars if 'total_bars' in locals() else (idx - start_idx + 1),
                trades=trades_log,
            )
        # Time exit: hard cap on bars held per trade.
        if config.time_exit_max_bars and (idx - start_idx + 1) >= config.time_exit_max_bars:
            exit_px = _slippage_commission_per_share(float(c.get('close', entry)), config, 'sell')
            pnl = (exit_px - entry_px) * shares
            r_mult = pnl / (risk * shares) if risk > 0 and shares > 0 else 0.0
            if risk_state is not None:
                risk_state.apply_trade(str(c.get('timestamp', '')), pnl, opened=False, closed=True)
            return TradeResult(
                pnl=pnl, r_multiple=r_mult, exit_reason='time_exit',
                entry_price=entry_px, exit_price=exit_px, shares=shares,
                bars_held=idx - start_idx + 1,
            )

    # Time exit at last close.
    last = candles[-1]
    exit_px = last.get('close', entry)
    if exit_px is None:
        exit_px = entry
    exit_px = _slippage_commission_per_share(float(exit_px), config, 'sell')
    pnl = (exit_px - entry_px) * shares
    r_mult = pnl / (risk * shares) if risk > 0 and shares > 0 else 0.0
    if risk_state is not None:
        risk_state.apply_trade(str(last.get('timestamp', '')), pnl, opened=False, closed=True)
    return TradeResult(
        pnl=pnl, r_multiple=r_mult, exit_reason='time_exit',
        entry_price=entry_px, exit_price=exit_px, shares=shares,
        bars_held=len(candles) - start_idx,
    )
