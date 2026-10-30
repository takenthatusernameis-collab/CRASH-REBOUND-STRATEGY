from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from src.strategy.config import StrategyConfig, DEFAULT_CONFIG
from src.strategy.risk import DailyRiskState
from src.strategy.crash_rebound import compute_eth_hedge_size


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
    hedge_pnl: float = 0.0
    hedge_side: Optional[str] = None
    hedge_size: float = 0.0
    hedge_entry: float = 0.0
    hedge_exit: float = 0.0
    total_pnl: float = 0.0  # includes hedge PnL

    def __init__(self, pnl=None, r_multiple=None, exit_reason=None, **kwargs):
        # Be flexible for different calling conventions
        self.pnl = pnl if pnl is not None else kwargs.get('pnl', 0.0)
        self.r_multiple = r_multiple if r_multiple is not None else kwargs.get('r_multiple', 0.0)
        self.exit_reason = exit_reason if exit_reason is not None else kwargs.get('exit_reason', '')
        self.entry_price = kwargs.get('entry_price', 0.0)
        self.exit_price = kwargs.get('exit_price', 0.0)
        self.shares = kwargs.get('shares', 0.0)
        self.bars_held = kwargs.get('bars_held', 0)
        self.trades = kwargs.get('trades', None)
        self.hedge_pnl = kwargs.get('hedge_pnl', 0.0)
        self.hedge_side = kwargs.get('hedge_side', None)
        self.hedge_size = kwargs.get('hedge_size', 0.0)
        self.hedge_entry = kwargs.get('hedge_entry', 0.0)
        self.hedge_exit = kwargs.get('hedge_exit', 0.0)
        self.total_pnl = kwargs.get('total_pnl', self.pnl + self.hedge_pnl)







def _slippage_commission_per_share(price: float, config: StrategyConfig, side: str) -> float:
    slip = price * config.slippage_pct
    comm = config.commission_per_share
    if config.commission_min > 0:
        # Apply minimum commission if it results in higher cost per share? Or just per trade - but we work per share
        pass
    return price + slip + comm if side == "buy" else price - slip - comm


def _apply_funding_pnl(notional: float, hours_held: float, funding_rate_pct_per_hour: float, side: str = 'long') -> float:
    """Funding cost/profit on a position.
    Convention: positive funding rate means longs pay shorts -> cost to long, profit to short.
    Returns the funding cost to add to pnl (positive = cost/reduces pnl).
    For long: funding is a cost (+). For short: funding is received (- cost / benefit).
    """
    if notional == 0 or hours_held <= 0:
        return 0.0
    rate = funding_rate_pct_per_hour / 100.0
    funding_amt = abs(notional) * rate * hours_held
    if side == 'long':
        return funding_amt  # long pays -> cost
    elif side == 'short':
        return -funding_amt  # short receives -> benefit
    return funding_amt





def _check_liquidation(candle: Dict[str, Any], side: str, entry_px: float, notional: float,
                       config: StrategyConfig) -> Optional[float]:
    """Check for liquidation based on worst price of hour. Returns liquidation price or None."""
    if not getattr(config, 'enable_liquidation_checks', True):
        return None
    if notional <= 0 or entry_px <= 0:
        return None
    maint_margin_pct = getattr(config, 'liquidation_maint_margin_pct', 5.0)
    buffer_pct = getattr(config, 'liquidation_buffer_pct', 1.0)
    # Conservative: liquidation if price moves against position beyond (1 - maint_margin - buffer)% for long
    if side == 'long':
        low = candle.get('low')
        if low is None:
            return None
        liq_threshold = entry_px * (1.0 - (maint_margin_pct + buffer_pct) / 100.0)
        if float(low) <= liq_threshold:
            return float(low)
    elif side == 'short':
        high = candle.get('high')
        if high is None:
            return None
        liq_threshold = entry_px * (1.0 + (maint_margin_pct + buffer_pct) / 100.0)
        if float(high) >= liq_threshold:
            return float(high)
    return None

def backtest_simple(
    candles: List[Dict[str, Any]],
    signal,
    config: StrategyConfig = DEFAULT_CONFIG,
    capital: float = 100000.0,
    risk_state: Optional[DailyRiskState] = None,
    eth_candles: Optional[List[Dict[str, Any]]] = None,
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
        # Track notional
        notional = entry_px * shares if entry_px > 0 and shares > 0 else 0.0
        # Apply gross cap with equal-share cuts across ALL positions (old + new).
        # apply_cap_cuts persists the cuts to risk_state (old positions cut too),
        # so when it runs we skip the separate opened-trade registration below.
        position_recorded = False
        try:
            cap_value = capital * getattr(config, 'gross_cap_pct', 120.0) / 100.0
            total_exposure = getattr(risk_state, 'gross_exposure', 0.0) + notional
            if total_exposure > cap_value and hasattr(risk_state, 'open_position_notionals'):
                all_notionals = list(getattr(risk_state, 'open_position_notionals', [])) + [notional]
                cuts = risk_state.apply_cap_cuts(capital, config, all_notionals)
                if cuts and len(cuts) == len(all_notionals):
                    new_notional_cut = cuts[-1]
                    if new_notional_cut <= 0 or entry_px <= 0:
                        return TradeResult(
                            pnl=0.0, r_multiple=0.0, exit_reason='blocked',
                            entry_price=entry, exit_price=entry, shares=0.0, bars_held=0,
                        )
                    shares = new_notional_cut / entry_px
                    notional = new_notional_cut
                    position_recorded = True
        except Exception:
            pass
        if risk_state is not None and not position_recorded:
            risk_state.apply_trade(entry_date, 0.0, opened=True, closed=False, notional=notional)


    trades_log = []
    hedge_pnl_total = 0.0
    hedge_info = {'side': None, 'size': 0.0, 'entry': 0.0, 'exit': 0.0}

    # Setup ETH hedge for long crash leg if enabled
    coin_position_value = entry_px * shares
    if getattr(config, 'enable_eth_hedge', True) and eth_candles:
        try:
            hedge_value = compute_eth_hedge_size(candles, eth_candles, coin_position_value, config)
            if hedge_value > 0:
                # Get ETH entry price (use first available ETH price near start)
                eth_entry_price = None
                for ec in eth_candles:
                    ec_open = ec.get('open')
                    if ec_open is not None:
                        eth_entry_price = float(ec_open)
                        break
                if eth_entry_price and eth_entry_price > 0:
                    hedge_shares = hedge_value / eth_entry_price
                    hedge_entry_px = _slippage_commission_per_share(eth_entry_price, config, 'sell')  # short hedge
                    hedge_info = {'side': 'short', 'size': hedge_shares, 'entry': hedge_entry_px, 'exit': hedge_entry_px}
        except Exception:
            pass  # Skip hedge on error
    # Look-ahead guard: only inspect candles at or after the entry point.
    for idx in range(start_idx, len(candles)):
        c = candles[idx]
        low = c.get('low')
        high = c.get('high')
        # Check liquidation first (hourly worst price)
        liq_px = _check_liquidation(c, side='long', entry_px=entry_px, notional=entry_px * shares if entry_px > 0 and shares > 0 else 0.0, config=config)
        if liq_px is not None:
            exit_px = _slippage_commission_per_share(float(liq_px), config, 'sell')
            pnl = (exit_px - entry_px) * shares
            penalty = getattr(config, 'liquidation_penalty_pct', 0.5) / 100.0 * (entry_px * shares)
            pnl -= penalty
            # Close hedge if exists
            if hedge_info['side'] == 'short' and hedge_info['size'] > 0:
                eth_exit_price = None
                if eth_candles and idx < len(eth_candles):
                    eth_exit_price = eth_candles[idx].get('close') or eth_candles[idx].get('open')
                if eth_exit_price is None:
                    eth_exit_price = hedge_info['entry']
                hedge_exit_px = _slippage_commission_per_share(float(eth_exit_price), config, 'buy')
                hedge_pnl_total = (hedge_info['entry'] - hedge_exit_px) * hedge_info['size']
                hours_held = idx - start_idx + 1
                hedge_notional = hedge_info['entry'] * hedge_info['size']
                funding_cost = _apply_funding_pnl(hedge_notional, hours_held, config.funding_rate_pct_per_hour, side=hedge_info['side'])
                hedge_pnl_total += funding_cost
                hedge_info['exit'] = hedge_exit_px
            r_mult = pnl / (risk * shares) if risk > 0 and shares > 0 else 0.0
            if risk_state is not None:
                try:
                    _not = entry_px * shares if ('entry_px' in locals() and entry_px > 0 and shares > 0) else 0.0
                except Exception:
                    _not = 0.0
                risk_state.apply_trade(str(c.get('timestamp', '')), pnl, opened=False, closed=True, notional=_not)
            trades_log.append({'side': 'long', 'entry': entry_px, 'exit': exit_px, 'pnl': pnl, 'reason': 'liquidated'})
            total_pnl_result = pnl + hedge_pnl_total
            return TradeResult(
                pnl=pnl, r_multiple=r_mult, exit_reason='liquidated',
                entry_price=entry_px, exit_price=exit_px, shares=shares,
                bars_held=idx - start_idx + 1,
                trades=trades_log,
                hedge_pnl=hedge_pnl_total,
                hedge_side=hedge_info['side'],
                hedge_size=hedge_info['size'],
                hedge_entry=hedge_info['entry'],
                hedge_exit=hedge_info['exit'],
                total_pnl=total_pnl_result,
            )
        if low is not None and low <= stop_px:
            exit_px = _slippage_commission_per_share(stop_px, config, 'sell')
            pnl = (exit_px - entry_px) * shares
            # Close hedge if exists
            if hedge_info['side'] == 'short' and hedge_info['size'] > 0:
                # Get ETH exit price
                eth_exit_price = None
                if eth_candles and idx < len(eth_candles):
                    eth_exit_price = eth_candles[idx].get('close') or eth_candles[idx].get('open')
                if eth_exit_price is None:
                    eth_exit_price = hedge_info['entry']  # fallback
                hedge_exit_px = _slippage_commission_per_share(float(eth_exit_price), config, 'buy')
                hedge_pnl_total = (hedge_info['entry'] - hedge_exit_px) * hedge_info['size']  # short profit if price down
                # Apply funding on hedge (short hedge - short pays? Or receives funding)
                hours_held = idx - start_idx + 1
                hedge_notional = hedge_info['entry'] * hedge_info['size']
                funding_cost = _apply_funding_pnl(hedge_notional, hours_held, config.funding_rate_pct_per_hour, side=hedge_info['side'])
                hedge_pnl_total += funding_cost
                hedge_info['exit'] = hedge_exit_px
            r_mult = pnl / (risk * shares) if risk > 0 and shares > 0 else 0.0
            if risk_state is not None:
                try:
                    _not = entry_px * shares if ('entry_px' in locals() and entry_px > 0 and shares > 0) else 0.0
                except Exception:
                    _not = 0.0
                risk_state.apply_trade(str(c.get('timestamp', '')), pnl, opened=False, closed=True, notional=_not)
            trades_log.append({'side': 'long', 'entry': entry_px, 'exit': exit_px, 'pnl': pnl, 'reason': 'stopped'})
            total_pnl_result = pnl + hedge_pnl_total
            return TradeResult(
                pnl=pnl, r_multiple=r_mult, exit_reason='stopped',
                entry_price=entry_px, exit_price=exit_px, shares=shares,
                bars_held=idx - start_idx + 1,
                trades=trades_log,
                hedge_pnl=hedge_pnl_total,
                hedge_side=hedge_info['side'],
                hedge_size=hedge_info['size'],
                hedge_entry=hedge_info['entry'],
                hedge_exit=hedge_info['exit'],
                total_pnl=total_pnl_result,
            )
        if high is not None and high >= target_px:
            exit_px = _slippage_commission_per_share(target_px, config, 'sell')
            pnl = (exit_px - entry_px) * shares
            # Close hedge for long leg
            if hedge_info['side'] == 'short' and hedge_info['size'] > 0:
                eth_exit_price = None
                if eth_candles and idx < len(eth_candles):
                    eth_exit_price = eth_candles[idx].get('close') or eth_candles[idx].get('open')
                if eth_exit_price is None:
                    eth_exit_price = hedge_info['entry']
                hedge_exit_px = _slippage_commission_per_share(float(eth_exit_price), config, 'buy')
                hedge_pnl_total = (hedge_info['entry'] - hedge_exit_px) * hedge_info['size']
                hours_held = idx - start_idx + 1
                hedge_notional = hedge_info['entry'] * hedge_info['size']
                funding_cost = _apply_funding_pnl(hedge_notional, hours_held, config.funding_rate_pct_per_hour, side=hedge_info['side'])
                hedge_pnl_total += funding_cost
                hedge_info['exit'] = hedge_exit_px
            r_mult = pnl / (risk * shares) if risk > 0 and shares > 0 else 0.0
            if risk_state is not None:
                try:
                    _not = entry_px * shares if ('entry_px' in locals() and entry_px > 0 and shares > 0) else 0.0
                except Exception:
                    _not = 0.0
                risk_state.apply_trade(str(c.get('timestamp', '')), pnl, opened=False, closed=True, notional=_not)
            trades_log.append({'side': 'long', 'entry': entry_px, 'exit': exit_px, 'pnl': pnl, 'reason': 'target'})
            total_pnl = pnl + hedge_pnl_total
            total_r_mult = r_mult
            total_bars = idx - start_idx + 1
            rebound_hedge_pnl = 0.0
            rebound_hedge_info = {'side': None, 'size': 0.0, 'entry': 0.0, 'exit': 0.0}
            # Rebound short logic when buy hits +9% target fast
            if getattr(config, 'enable_rebound_short', True):
                short_entry_px = _slippage_commission_per_share(exit_px, config, 'sell')  # enter short
                # Add hedge for rebound short leg (long hedge)
                if getattr(config, 'enable_eth_hedge', True) and eth_candles:
                    try:
                        short_coin_value = short_entry_px * shares
                        r_hedge_value = compute_eth_hedge_size(candles, eth_candles, short_coin_value, config)
                        if r_hedge_value > 0:
                            eth_entry_r = None
                            if idx + 1 < len(eth_candles):
                                eth_entry_r = eth_candles[idx + 1].get('open') or eth_candles[idx + 1].get('close')
                            elif idx < len(eth_candles):
                                eth_entry_r = eth_candles[idx].get('open') or eth_candles[idx].get('close')
                            if eth_entry_r and eth_entry_r > 0:
                                r_hedge_shares = r_hedge_value / eth_entry_r
                                r_hedge_entry_px = _slippage_commission_per_share(float(eth_entry_r), config, 'buy')  # long hedge
                                rebound_hedge_info = {'side': 'long', 'size': r_hedge_shares, 'entry': r_hedge_entry_px, 'exit': r_hedge_entry_px}
                    except Exception:
                        pass
                short_target = short_entry_px * (1.0 - getattr(config, 'rebound_short_target_pct', 9.0) / 100.0)
                short_stop = short_entry_px * (1.0 + getattr(config, 'rebound_short_stop_pct', 40.0) / 100.0)
                short_start_idx = idx
                short_shares = shares
                short_bars_max = getattr(config, 'rebound_short_time_exit_bars', 48)
                short_pnl = 0.0
                for sidx in range(short_start_idx + 1, len(candles)):
                    sc = candles[sidx]
                    slow = sc.get('low')
                    shigh = sc.get('high')
                    # Check liquidation for short
                    sliq = _check_liquidation(sc, side='short', entry_px=short_entry_px, notional=short_entry_px * short_shares if short_entry_px > 0 and short_shares > 0 else 0.0, config=config)
                    if sliq is not None:
                        short_exit = _slippage_commission_per_share(float(sliq), config, 'buy')
                        short_pnl = (short_entry_px - short_exit) * short_shares
                        s_pen = getattr(config, 'liquidation_penalty_pct', 0.5) / 100.0 * (short_entry_px * short_shares)
                        short_pnl -= s_pen
                        if rebound_hedge_info['side'] == 'long' and rebound_hedge_info['size'] > 0:
                            eth_exit_r = None
                            if eth_candles and sidx < len(eth_candles):
                                eth_exit_r = eth_candles[sidx].get('close') or eth_candles[sidx].get('open')
                            if eth_exit_r:
                                r_hedge_exit_px = _slippage_commission_per_share(float(eth_exit_r), config, 'sell')
                                rebound_hedge_pnl = (r_hedge_exit_px - rebound_hedge_info['entry']) * rebound_hedge_info['size']
                                hours_held_r = sidx - short_start_idx + 1
                                rh_notional = rebound_hedge_info['entry'] * rebound_hedge_info['size']
                                rh_funding = _apply_funding_pnl(rh_notional, hours_held_r, config.funding_rate_pct_per_hour, side=rebound_hedge_info['side'])
                                rebound_hedge_pnl += rh_funding
                                rebound_hedge_info['exit'] = r_hedge_exit_px
                        if risk_state is not None:
                            risk_state.apply_trade(str(sc.get('timestamp', '')), short_pnl, opened=False, closed=True)
                        trades_log.append({'side': 'short', 'entry': short_entry_px, 'exit': short_exit, 'pnl': short_pnl, 'reason': 'liquidated'})
                        total_pnl += short_pnl + rebound_hedge_pnl
                        total_bars = max(total_bars, (sidx - start_idx + 1))
                        break
                    if shigh is not None and shigh >= short_stop:
                        short_exit = _slippage_commission_per_share(short_stop, config, 'buy')
                        short_pnl = (short_entry_px - short_exit) * short_shares
                        # Close rebound hedge
                        if rebound_hedge_info['side'] == 'long' and rebound_hedge_info['size'] > 0:
                            eth_exit_r = None
                            if eth_candles and sidx < len(eth_candles):
                                eth_exit_r = eth_candles[sidx].get('close') or eth_candles[sidx].get('open')
                            if eth_exit_r:
                                r_hedge_exit_px = _slippage_commission_per_share(float(eth_exit_r), config, 'sell')
                                rebound_hedge_pnl = (r_hedge_exit_px - rebound_hedge_info['entry']) * rebound_hedge_info['size']
                                hours_held_r = sidx - short_start_idx + 1
                                rh_notional = rebound_hedge_info['entry'] * rebound_hedge_info['size']
                                rh_funding = _apply_funding_pnl(rh_notional, hours_held_r, config.funding_rate_pct_per_hour, side=rebound_hedge_info['side'])
                                rebound_hedge_pnl += rh_funding
                                rebound_hedge_info['exit'] = r_hedge_exit_px
                        if risk_state is not None:
                            risk_state.apply_trade(str(sc.get('timestamp', '')), short_pnl, opened=False, closed=True)
                        trades_log.append({'side': 'short', 'entry': short_entry_px, 'exit': short_exit, 'pnl': short_pnl, 'reason': 'stopped'})
                        total_pnl += short_pnl + rebound_hedge_pnl
                        total_bars = max(total_bars, (sidx - start_idx + 1))
                        break
                    if slow is not None and slow <= short_target:
                        short_exit = _slippage_commission_per_share(short_target, config, 'buy')
                        short_pnl = (short_entry_px - short_exit) * short_shares
                        if rebound_hedge_info['side'] == 'long' and rebound_hedge_info['size'] > 0:
                            eth_exit_r = None
                            if eth_candles and sidx < len(eth_candles):
                                eth_exit_r = eth_candles[sidx].get('close') or eth_candles[sidx].get('open')
                            if eth_exit_r:
                                r_hedge_exit_px = _slippage_commission_per_share(float(eth_exit_r), config, 'sell')
                                rebound_hedge_pnl = (r_hedge_exit_px - rebound_hedge_info['entry']) * rebound_hedge_info['size']
                                hours_held_r = sidx - short_start_idx + 1
                                rh_notional = rebound_hedge_info['entry'] * rebound_hedge_info['size']
                                rh_funding = _apply_funding_pnl(rh_notional, hours_held_r, config.funding_rate_pct_per_hour, side=rebound_hedge_info['side'])
                                rebound_hedge_pnl += rh_funding
                                rebound_hedge_info['exit'] = r_hedge_exit_px
                        if risk_state is not None:
                            risk_state.apply_trade(str(sc.get('timestamp', '')), short_pnl, opened=False, closed=True)
                        trades_log.append({'side': 'short', 'entry': short_entry_px, 'exit': short_exit, 'pnl': short_pnl, 'reason': 'target'})
                        total_pnl += short_pnl + rebound_hedge_pnl
                        total_bars = max(total_bars, (sidx - start_idx + 1))
                        break
                    if (sidx - short_start_idx) >= short_bars_max:
                        sclose = sc.get('close', short_entry_px)
                        short_exit = _slippage_commission_per_share(float(sclose), config, 'buy')
                        short_pnl = (short_entry_px - short_exit) * short_shares
                        if rebound_hedge_info['side'] == 'long' and rebound_hedge_info['size'] > 0:
                            eth_exit_r = None
                            if eth_candles and sidx < len(eth_candles):
                                eth_exit_r = eth_candles[sidx].get('close') or eth_candles[sidx].get('open')
                            if eth_exit_r:
                                r_hedge_exit_px = _slippage_commission_per_share(float(eth_exit_r), config, 'sell')
                                rebound_hedge_pnl = (r_hedge_exit_px - rebound_hedge_info['entry']) * rebound_hedge_info['size']
                                hours_held_r = sidx - short_start_idx + 1
                                rh_notional = rebound_hedge_info['entry'] * rebound_hedge_info['size']
                                rh_funding = _apply_funding_pnl(rh_notional, hours_held_r, config.funding_rate_pct_per_hour, side=rebound_hedge_info['side'])
                                rebound_hedge_pnl += rh_funding
                                rebound_hedge_info['exit'] = r_hedge_exit_px
                        if risk_state is not None:
                            risk_state.apply_trade(str(sc.get('timestamp', '')), short_pnl, opened=False, closed=True)
                        trades_log.append({'side': 'short', 'entry': short_entry_px, 'exit': short_exit, 'pnl': short_pnl, 'reason': 'time_exit'})
                        total_pnl += short_pnl + rebound_hedge_pnl
                        total_bars = max(total_bars, (sidx - start_idx + 1))
                        break
                else:
                    # No break occurred - exit short at last available bar
                    last_sc = candles[-1]
                    sclose = last_sc.get('close', short_entry_px)
                    short_exit = _slippage_commission_per_share(float(sclose), config, 'buy')
                    short_pnl = (short_entry_px - short_exit) * short_shares
                    if rebound_hedge_info['side'] == 'long' and rebound_hedge_info['size'] > 0:
                        eth_exit_r = None
                        if eth_candles and len(eth_candles) > 0:
                            eth_exit_r = eth_candles[-1].get('close') or eth_candles[-1].get('open')
                        if eth_exit_r:
                            r_hedge_exit_px = _slippage_commission_per_share(float(eth_exit_r), config, 'sell')
                            rebound_hedge_pnl = (r_hedge_exit_px - rebound_hedge_info['entry']) * rebound_hedge_info['size']
                            hours_held_r = len(candles) - short_start_idx
                            rh_notional = rebound_hedge_info['entry'] * rebound_hedge_info['size']
                            rh_funding = _apply_funding_pnl(rh_notional, hours_held_r, config.funding_rate_pct_per_hour)
                            rebound_hedge_pnl -= rh_funding
                            rebound_hedge_info['exit'] = r_hedge_exit_px
                    if risk_state is not None:
                        risk_state.apply_trade(str(last_sc.get('timestamp', '')), short_pnl, opened=False, closed=True)
                    trades_log.append({'side': 'short', 'entry': short_entry_px, 'exit': short_exit, 'pnl': short_pnl, 'reason': 'time_exit'})
                    total_pnl += short_pnl + rebound_hedge_pnl
                    total_bars = max(total_bars, len(candles) - start_idx)

            # recompute r_mult for total
            if getattr(config, 'enable_rebound_short', True) and len(trades_log) > 1 and trades_log[-1].get('side') == 'short':
                total_risk = risk * shares * 2.0
                total_r_mult = total_pnl / total_risk if total_risk > 0 else total_r_mult
            else:
                total_r_mult = r_mult
            return TradeResult(
                pnl=pnl + hedge_pnl_total,
                r_multiple=total_r_mult if 'total_r_mult' in locals() else r_mult,
                exit_reason='target_rebound_short' if (len(trades_log) > 1 and any(t.get('side') == 'short' for t in trades_log)) else 'target',
                entry_price=entry_px, exit_price=exit_px, shares=shares,
                bars_held=total_bars if 'total_bars' in locals() else (idx - start_idx + 1),
                trades=trades_log,
                hedge_pnl=hedge_pnl_total + rebound_hedge_pnl,
                hedge_side=hedge_info['side'],
                hedge_size=hedge_info['size'],
                hedge_entry=hedge_info['entry'],
                hedge_exit=hedge_info['exit'],
                total_pnl=total_pnl,
            )
        # Time exit: hard cap on bars held per trade.
        if config.time_exit_max_bars and (idx - start_idx + 1) >= config.time_exit_max_bars:
            exit_px = _slippage_commission_per_share(float(c.get('close', entry)), config, 'sell')
            pnl = (exit_px - entry_px) * shares
            if hedge_info['side'] == 'short' and hedge_info['size'] > 0:
                eth_exit_price = None
                if eth_candles and idx < len(eth_candles):
                    eth_exit_price = eth_candles[idx].get('close') or eth_candles[idx].get('open')
                if eth_exit_price:
                    hedge_exit_px = _slippage_commission_per_share(float(eth_exit_price), config, 'buy')
                    hedge_pnl_total = (hedge_info['entry'] - hedge_exit_px) * hedge_info['size']
                    hours_held = idx - start_idx + 1
                    hedge_notional = hedge_info['entry'] * hedge_info['size']
                    funding_cost = _apply_funding_pnl(hedge_notional, hours_held, config.funding_rate_pct_per_hour)
                    hedge_pnl_total += funding_cost
                    hedge_info['exit'] = hedge_exit_px
            r_mult = pnl / (risk * shares) if risk > 0 and shares > 0 else 0.0
            if risk_state is not None:
                try:
                    _not = entry_px * shares if ('entry_px' in locals() and entry_px > 0 and shares > 0) else 0.0
                except Exception:
                    _not = 0.0
                risk_state.apply_trade(str(c.get('timestamp', '')), pnl, opened=False, closed=True, notional=_not)
            return TradeResult(
                pnl=pnl + hedge_pnl_total, r_multiple=r_mult, exit_reason='time_exit',
                entry_price=entry_px, exit_price=exit_px, shares=shares,
                bars_held=idx - start_idx + 1,
                trades=trades_log,
                hedge_pnl=hedge_pnl_total,
                hedge_side=hedge_info['side'],
                hedge_size=hedge_info['size'],
                hedge_entry=hedge_info['entry'],
                hedge_exit=hedge_info['exit'],
                total_pnl=pnl + hedge_pnl_total,
            )

    # Time exit at last close.
    last = candles[-1]
    exit_px = last.get('close', entry)
    if exit_px is None:
        exit_px = entry
    exit_px = _slippage_commission_per_share(float(exit_px), config, 'sell')
    pnl = (exit_px - entry_px) * shares
    if hedge_info['side'] == 'short' and hedge_info['size'] > 0:
        eth_exit_price = None
        if eth_candles and len(eth_candles) > 0:
            eth_exit_price = eth_candles[-1].get('close') or eth_candles[-1].get('open')
        if eth_exit_price:
            hedge_exit_px = _slippage_commission_per_share(float(eth_exit_price), config, 'buy')
            hedge_pnl_total = (hedge_info['entry'] - hedge_exit_px) * hedge_info['size']
            hours_held = len(candles) - start_idx
            hedge_notional = hedge_info['entry'] * hedge_info['size']
            funding_cost = _apply_funding_pnl(hedge_notional, hours_held, config.funding_rate_pct_per_hour)
            hedge_pnl_total += funding_cost
            hedge_info['exit'] = hedge_exit_px
    r_mult = pnl / (risk * shares) if risk > 0 and shares > 0 else 0.0
    if risk_state is not None:
        risk_state.apply_trade(str(last.get('timestamp', '')), pnl, opened=False, closed=True)
    return TradeResult(
        pnl=pnl + hedge_pnl_total, r_multiple=r_mult, exit_reason='time_exit',
        entry_price=entry_px, exit_price=exit_px, shares=shares,
        bars_held=len(candles) - start_idx,
        trades=trades_log,
        hedge_pnl=hedge_pnl_total,
        hedge_side=hedge_info['side'],
        hedge_size=hedge_info['size'],
        hedge_entry=hedge_info['entry'],
        hedge_exit=hedge_info['exit'],
        total_pnl=pnl + hedge_pnl_total,
    )
