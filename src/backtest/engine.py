from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from src.strategy.config import StrategyConfig, DEFAULT_CONFIG
from src.strategy.risk import DailyRiskState
from src.strategy.crash_rebound import compute_eth_hedge_size, confirm_rebound


@dataclass
class TradeResult:
    pnl: float
    r_multiple: float
    exit_reason: str
    entry_price: float = 0.0
    exit_price: float = 0.0
    shares: float = 0.0
    bars_held: int = 0
    entry_timestamp: str = ""
    exit_timestamp: str = ""
    trades: Optional[List[Dict[str, Any]]] = None  # For multi-leg trades (e.g., crash + rebound)
    hedge_pnl: float = 0.0
    hedge_side: Optional[str] = None
    hedge_size: float = 0.0
    hedge_entry: float = 0.0
    hedge_exit: float = 0.0
    rebound_short_pnl: float = 0.0
    rebound_hedge_pnl: float = 0.0
    rebound_hedge_side: Optional[str] = None
    rebound_hedge_size: float = 0.0
    rebound_hedge_entry: float = 0.0
    rebound_hedge_exit: float = 0.0
    total_pnl: float = 0.0  # includes hedge PnL
    # Primary leg of the trade for per-leg attribution: 'buy' (crash long only),
    # 'short' (rebound short fired after a target exit), or 'buy+short' when both
    # legs executed within one trade lifecycle. Metrics bucket on this field.
    leg: str = "buy"
    # Max live coin-position notional across long-entry and rebound-short-entry legs
    # (post cap-cut shares * executed entry price). Hedges are excluded from the coin
    # positions cap context; portfolio runners use this for occupancy/gross-cap reservation
    # without parsing trades-leg internals.
    max_live_coin_notional: float = 0.0

    def __init__(self, pnl=None, r_multiple=None, exit_reason=None, **kwargs):
        # Be flexible for different calling conventions
        self.pnl = pnl if pnl is not None else kwargs.get('pnl', 0.0)
        self.r_multiple = r_multiple if r_multiple is not None else kwargs.get('r_multiple', 0.0)
        self.exit_reason = exit_reason if exit_reason is not None else kwargs.get('exit_reason', '')
        self.entry_price = kwargs.get('entry_price', 0.0)
        self.exit_price = kwargs.get('exit_price', 0.0)
        self.shares = kwargs.get('shares', 0.0)
        self.bars_held = kwargs.get('bars_held', 0)
        self.entry_timestamp = kwargs.get('entry_timestamp', '')
        self.exit_timestamp = kwargs.get('exit_timestamp', '')
        self.trades = kwargs.get('trades', None)
        self.hedge_pnl = kwargs.get('hedge_pnl', 0.0)
        self.hedge_side = kwargs.get('hedge_side', None)
        self.hedge_size = kwargs.get('hedge_size', 0.0)
        self.hedge_entry = kwargs.get('hedge_entry', 0.0)
        self.hedge_exit = kwargs.get('hedge_exit', 0.0)
        self.rebound_short_pnl = kwargs.get('rebound_short_pnl', 0.0)
        self.rebound_hedge_pnl = kwargs.get('rebound_hedge_pnl', 0.0)
        self.rebound_hedge_side = kwargs.get('rebound_hedge_side', None)
        self.rebound_hedge_size = kwargs.get('rebound_hedge_size', 0.0)
        self.rebound_hedge_entry = kwargs.get('rebound_hedge_entry', 0.0)
        self.rebound_hedge_exit = kwargs.get('rebound_hedge_entry', 0.0) if False else kwargs.get('rebound_hedge_exit', 0.0)
        self.total_pnl = kwargs.get(
            'total_pnl',
            self.pnl + self.hedge_pnl + self.rebound_short_pnl + self.rebound_hedge_pnl,
        )
        # Primary leg label for per-leg attribution. 'buy' = crash long only;
        # 'short' = rebound short fired (buy+short combined lifecycle). Metrics
        # split 'short'-legged trades into buy/short constituents for the
        # spec's per-leg win-rate/profit-factor breakdown.
        self.leg = kwargs.get('leg', 'buy' if not self.rebound_short_pnl else 'short')
        # Max live coin-position notional across the long-entry leg and the
        # rebound-short-entry leg (hedges excluded from the 120% coin-positions
        # cap context). The engine runs the rebound short at the same share count
        # as the long entry, so the short leg's live notional is short_entry * shares,
        # which can exceed the long-entry notional (e.g. short opens at +9% target).
        # Callers without leg-log parsing (portfolio reservation overlay, future
        # paths) must not reserve only the long-entry notional while the short is live.
        _explicit_mln = kwargs.get('max_live_coin_notional', None)
        if _explicit_mln is not None:
            self.max_live_coin_notional = float(_explicit_mln)
        else:
            _max = self.entry_price * self.shares if self.entry_price > 0 and self.shares > 0 else 0.0
            for _leg in (self.trades or []):
                if not isinstance(_leg, dict):
                    continue
                # Coin legs only ('long' buy, 'short' rebound). Hedges are tracked
                # separately (hedge_* / rebound_hedge_*) and excluded from the cap.
                if _leg.get('side') in ('long', 'short'):
                    try:
                        _leg_not = float(_leg.get('entry', 0.0) or 0.0) * float(self.shares)
                    except Exception:
                        _leg_not = 0.0
                    if _leg_not > _max:
                        _max = _leg_not
            self.max_live_coin_notional = float(_max)







def _slippage_commission_per_share(price: float, config: StrategyConfig, side: str, shares: float = 0.0) -> float:
    slip = price * config.slippage_pct
    comm = config.commission_per_share
    if config.commission_min > 0 and shares > 0:
        comm = max(comm, config.commission_min / shares)
    return price + slip + comm if side == "buy" else price - slip - comm


def _close_or_fallback(candle: Dict[str, Any], fallback: float) -> float:
    """Return the bar's close, falling back when the field is missing OR explicitly None.

    Spec-fidelity: a candle whose close field is missing/None cannot be used as an
    exit price. `dict.get(key, default)` only supplies the default when the key is
    absent; an explicit None value passes through and later `float(None)` raises
    TypeError mid-simulation. Normalize here so the engine fails closed to a safe
    fallback (prior bar close / entry) instead of crashing on malformed input.
    """
    v = candle.get("close")
    if v is None:
        return float(fallback)
    try:
        return float(v)
    except (TypeError, ValueError):
        return float(fallback)


def _apply_funding_pnl(notional: float, hours_held: float, funding_rate_pct_per_hour: float, side: str = 'long') -> float:
    """Funding cost/profit on a position.
    Convention: positive funding rate means longs pay shorts -> cost to long, benefit to short.
    Returns a signed funding component where positive = cost to the position holder (reduces PnL),
    negative = benefit to the holder (increases PnL). Apply as: pnl -= _apply_funding_pnl(...).
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
    require_eth_hedge: bool = False,
) -> TradeResult:
    """Low-level execution engine (signal assumed). NOT volume-gated/spec-compliant
    universe gating. Callers must not treat this as a gated production entrypoint.
    Spec-compliant gating belongs in generate_signal/filter_universe and gated
    wrappers/runners (e.g. portfolio/real-campaign paths) before execution.

    ``require_eth_hedge`` is a fail-closed contract for SPEC-COMPLIANT callers only.
    When True and ``config.enable_eth_hedge`` is True, the engine refuses to run
    unless a usable ETH hedge was actually established (hedge_side set, hedge_size>0).
    Missing/flat/insufficient ETH data must surface as a hard error rather than
    silently running unhedged. It does NOT affect low-level/fixture callers that
    intentionally omit hedges (default False)."""
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
    entry_px = _slippage_commission_per_share(entry_px, config, 'buy', shares=shares)
    entry_timestamp = str(candles[start_idx].get('timestamp', '')) if candles else ''

    stop_px = stop
    target_px = target
    # Spec-fidelity re-anchor (2026-11-08): when entry_next_bar=True the fill price
    # is the next bar's open, which may differ from the signal-bar close used to
    # derive stop/target. The PDF defines thresholds relative to the executed
    # entry (target = +9% of entry; safety stop = entry * (1 - 8 * range_ratio)),
    # so stop/target must move with the fill price. Ratio semantics (spec safety
    # stop, +9% target, and reward_risk = entry + risk * reward_risk) are preserved
    # exactly by scaling both by entry_px/entry. The legacy absolute ATR-offset
    # stop form (use_spec_safety_stop=False) shifts additively instead.
    if config.entry_next_bar and entry > 0 and entry_px != entry:
        _ratio = entry_px / entry
        if getattr(config, 'use_spec_safety_stop', True):
            stop_px = stop * _ratio
        else:
            stop_px = stop + (entry_px - entry)
        target_px = target * _ratio
        risk = entry_px - stop_px

    # Risk gate before entry: max positions and daily-loss halt.
    if risk_state is not None:
        entry_date = str(candles[start_idx].get('timestamp', ''))
        check = risk_state.check_position(config, capital, shares, entry_px)
        if not check.allowed:
            return TradeResult(
                pnl=0.0, r_multiple=0.0, exit_reason='blocked',
                entry_price=entry, exit_price=entry, shares=0.0, bars_held=0,
                entry_timestamp=entry_timestamp,
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
                    new_notional_cut = min(cuts[-1], notional)
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
            # No look-ahead: hedge sizing uses only history available at entry decision.
            hedge_hist_end = min(start_idx + 1, len(candles))
            coin_hist = candles[:hedge_hist_end]
            eth_hist = eth_candles[:min(hedge_hist_end, len(eth_candles))]
            hedge_value = compute_eth_hedge_size(coin_hist, eth_hist, coin_position_value, config)
            if hedge_value > 0:
                # Get ETH entry price at hedge open (use bar aligned to start/entry)
                eth_entry_price = None
                eth_ref_idx = min(start_idx, len(eth_candles) - 1)
                if eth_ref_idx >= 0:
                    eth_entry_price = eth_candles[eth_ref_idx].get('open') or eth_candles[eth_ref_idx].get('close')
                if eth_entry_price and float(eth_entry_price) > 0:
                    hedge_shares = hedge_value / float(eth_entry_price)
                    hedge_entry_px = _slippage_commission_per_share(float(eth_entry_price), config, 'sell', shares=hedge_shares)  # short hedge
                    hedge_info = {'side': 'short', 'size': hedge_shares, 'entry': hedge_entry_px, 'exit': hedge_entry_px}
        except Exception:
            pass  # Skip hedge on error
    # Fail-closed ETH-hedge contract (spec: every trade hedged with ETH).
    # When a SPEC-COMPLIANT caller opts into require_eth_hedge=True AND the config
    # requests an ETH hedge, the engine MUST NOT silently run unhedged. Missing,
    # flat, or insufficient ETH data must surface as a hard error instead of a
    # phantom unhedged execution. Low-level/fixture callers that intentionally
    # omit hedges are unaffected (require_eth_hedge defaults False).
    if getattr(config, 'enable_eth_hedge', True) and require_eth_hedge:
        if hedge_info.get('side') is None or hedge_info.get('size', 0.0) <= 0:
            raise ValueError(
                "Spec-compliant ETH hedge required (require_eth_hedge=True) but no usable "
                "ETH hedge was established: eth_candles missing/flat/insufficient for "
                f"{symbol if (symbol := getattr(signal, 'symbol', None)) else 'trade'} "
                "(compute_eth_hedge_size returned 0 / hedge open failed). Provide verified "
                "ETH candles aligned to the coin series or disable the hedge contract."
            )
    # Look-ahead guard: only inspect candles at or after the entry point.
    for idx in range(start_idx, len(candles)):
        c = candles[idx]
        low = c.get('low')
        high = c.get('high')
        # Check liquidation first (hourly worst price)
        liq_px = _check_liquidation(c, side='long', entry_px=entry_px, notional=entry_px * shares if entry_px > 0 and shares > 0 else 0.0, config=config)
        if liq_px is not None:
            exit_px = _slippage_commission_per_share(float(liq_px), config, 'sell', shares=shares)
            pnl = (exit_px - entry_px) * shares
            penalty = getattr(config, 'liquidation_penalty_pct', 0.5) / 100.0 * (entry_px * shares)
            pnl -= penalty
            # Funding on the long leg (spec: hourly funding on every leg).
            # Positive rate => longs pay (cost). Apply per held hour.
            hours_held_liq = idx - start_idx + 1
            long_funding = _apply_funding_pnl(entry_px * shares, hours_held_liq,
                                              config.funding_rate_pct_per_hour, side='long')
            pnl -= long_funding
            # Close hedge if exists
            if hedge_info['side'] == 'short' and hedge_info['size'] > 0:
                eth_exit_price = None
                if eth_candles and idx < len(eth_candles):
                    eth_exit_price = eth_candles[idx].get('close') or eth_candles[idx].get('open')
                if eth_exit_price is None:
                    eth_exit_price = hedge_info['entry']
                hedge_exit_px = _slippage_commission_per_share(float(eth_exit_price), config, 'buy', shares=hedge_info['size'])
                hedge_pnl_total = (hedge_info['entry'] - hedge_exit_px) * hedge_info['size']
                hours_held = idx - start_idx + 1
                hedge_notional = hedge_info['entry'] * hedge_info['size']
                funding_cost = _apply_funding_pnl(hedge_notional, hours_held, config.funding_rate_pct_per_hour, side=hedge_info['side'])
                hedge_pnl_total -= funding_cost
                hedge_info['exit'] = hedge_exit_px
            r_mult = pnl / (risk * shares) if risk > 0 and shares > 0 else 0.0
            if risk_state is not None:
                try:
                    _not = entry_px * shares if ('entry_px' in locals() and entry_px > 0 and shares > 0) else 0.0
                except Exception:
                    _not = 0.0
                risk_state.apply_trade(str(c.get('timestamp', '')), pnl + hedge_pnl_total, opened=False, closed=True, notional=_not)
            trades_log.append({'side': 'long', 'entry': entry_px, 'exit': exit_px, 'pnl': pnl, 'reason': 'liquidated'})
            total_pnl_result = pnl + hedge_pnl_total
            return TradeResult(
                pnl=pnl, r_multiple=r_mult, exit_reason='liquidated',
                entry_price=entry_px, exit_price=exit_px, shares=shares,
                bars_held=idx - start_idx + 1,
                entry_timestamp=entry_timestamp,
                exit_timestamp=str(c.get('timestamp', '')),
                trades=trades_log,
                hedge_pnl=hedge_pnl_total,
                hedge_side=hedge_info['side'],
                hedge_size=hedge_info['size'],
                hedge_entry=hedge_info['entry'],
                hedge_exit=hedge_info['exit'],
                total_pnl=total_pnl_result,
            )
        # Spec-fidelity: the safety stop fires when the coin falls below the stop
        # threshold. When the bar's low field is missing/None we cannot assume the
        # price never reached the stop — fall back to the bar's close as the worst
        # available price proxy (fail-closed), consistent with _close_or_fallback.
        _stop_low = low if low is not None else _close_or_fallback(c, entry_px)
        if _stop_low <= stop_px:
            exit_px = _slippage_commission_per_share(stop_px, config, 'sell', shares=shares)
            pnl = (exit_px - entry_px) * shares
            # Funding on the long leg (spec: hourly funding on every leg).
            hours_held_stop = idx - start_idx + 1
            long_funding = _apply_funding_pnl(entry_px * shares, hours_held_stop,
                                              config.funding_rate_pct_per_hour, side='long')
            pnl -= long_funding
            # Close hedge if exists
            if hedge_info['side'] == 'short' and hedge_info['size'] > 0:
                # Get ETH exit price
                eth_exit_price = None
                if eth_candles and idx < len(eth_candles):
                    eth_exit_price = eth_candles[idx].get('close') or eth_candles[idx].get('open')
                if eth_exit_price is None:
                    eth_exit_price = hedge_info['entry']  # fallback
                hedge_exit_px = _slippage_commission_per_share(float(eth_exit_price), config, 'buy', shares=hedge_info['size'])
                hedge_pnl_total = (hedge_info['entry'] - hedge_exit_px) * hedge_info['size']  # short profit if price down
                # Apply funding on hedge (short hedge - short pays? Or receives funding)
                hours_held = idx - start_idx + 1
                hedge_notional = hedge_info['entry'] * hedge_info['size']
                funding_cost = _apply_funding_pnl(hedge_notional, hours_held, config.funding_rate_pct_per_hour, side=hedge_info['side'])
                hedge_pnl_total -= funding_cost
                hedge_info['exit'] = hedge_exit_px
            r_mult = pnl / (risk * shares) if risk > 0 and shares > 0 else 0.0
            if risk_state is not None:
                try:
                    _not = entry_px * shares if ('entry_px' in locals() and entry_px > 0 and shares > 0) else 0.0
                except Exception:
                    _not = 0.0
                risk_state.apply_trade(str(c.get('timestamp', '')), pnl + hedge_pnl_total, opened=False, closed=True, notional=_not)
            trades_log.append({'side': 'long', 'entry': entry_px, 'exit': exit_px, 'pnl': pnl, 'reason': 'stopped'})
            total_pnl_result = pnl + hedge_pnl_total
            return TradeResult(
                pnl=pnl, r_multiple=r_mult, exit_reason='stopped',
                entry_price=entry_px, exit_price=exit_px, shares=shares,
                bars_held=idx - start_idx + 1,
                entry_timestamp=entry_timestamp,
                exit_timestamp=str(c.get('timestamp', '')),
                trades=trades_log,
                hedge_pnl=hedge_pnl_total,
                hedge_side=hedge_info['side'],
                hedge_size=hedge_info['size'],
                hedge_entry=hedge_info['entry'],
                hedge_exit=hedge_info['exit'],
                total_pnl=total_pnl_result,
            )
        # Spec-fidelity: +9% target. When the bar's high field is missing/None, fall
        # back to the bar's close as the best available price proxy (fail-closed):
        # if close is at/above target the target was reached.
        _target_high = high if high is not None else _close_or_fallback(c, entry_px)
        if _target_high >= target_px:
            exit_px = _slippage_commission_per_share(target_px, config, 'sell', shares=shares)
            pnl = (exit_px - entry_px) * shares
            # Funding on the long leg (spec: hourly funding on every leg).
            hours_held_target = idx - start_idx + 1
            long_funding = _apply_funding_pnl(entry_px * shares, hours_held_target,
                                              config.funding_rate_pct_per_hour, side='long')
            pnl -= long_funding
            # Close hedge for long leg
            if hedge_info['side'] == 'short' and hedge_info['size'] > 0:
                eth_exit_price = None
                if eth_candles and idx < len(eth_candles):
                    eth_exit_price = eth_candles[idx].get('close') or eth_candles[idx].get('open')
                if eth_exit_price is None:
                    eth_exit_price = hedge_info['entry']
                hedge_exit_px = _slippage_commission_per_share(float(eth_exit_price), config, 'buy', shares=hedge_info['size'])
                hedge_pnl_total = (hedge_info['entry'] - hedge_exit_px) * hedge_info['size']
                hours_held = idx - start_idx + 1
                hedge_notional = hedge_info['entry'] * hedge_info['size']
                funding_cost = _apply_funding_pnl(hedge_notional, hours_held, config.funding_rate_pct_per_hour, side=hedge_info['side'])
                hedge_pnl_total -= funding_cost
                hedge_info['exit'] = hedge_exit_px
            r_mult = pnl / (risk * shares) if risk > 0 and shares > 0 else 0.0
            # Spec/portfolio attribution: risk_state realizes the full long-leg
            # settlement (coin + hedge) on close, consistent with liquidation/
            # stop/time-exit paths. Compute before the (separate) rebound short leg
            # opens so the long-leg close does not include the rebound leg PnL.
            long_coin_net = pnl
            total_pnl = pnl + hedge_pnl_total
            if risk_state is not None:
                try:
                    _not = entry_px * shares if ('entry_px' in locals() and entry_px > 0 and shares > 0) else 0.0
                except Exception:
                    _not = 0.0
                risk_state.apply_trade(str(c.get('timestamp', '')), total_pnl, opened=False, closed=True, notional=_not)
            trades_log.append({'side': 'long', 'entry': entry_px, 'exit': exit_px, 'pnl': long_coin_net, 'reason': 'target'})
            total_r_mult = r_mult
            total_bars = idx - start_idx + 1
            rebound_hedge_pnl = 0.0
            rebound_hedge_info = {'side': None, 'size': 0.0, 'entry': 0.0, 'exit': 0.0}
            short_exit_ts = str(c.get('timestamp', ''))
            short_exit_price_final = exit_px
            # Spec gate: "Only coins that already bounced hard are worth shorting"
            # (crash-rebound-strategy.pdf). When rebound_short_require_bounce_confirm
            # is set, the rebound short may only open when the target bar itself is
            # a confirming rebound bar (close > open, close in the upper half of its
            # range), evaluated over candles[:idx + 1] — history available at the
            # target bar only, no look-ahead. Default False preserves the legacy
            # behavior (short on any +9% fill) and every existing anchor.
            _rebound_confirmed = (
                not getattr(config, 'rebound_short_require_bounce_confirm', False)
                or confirm_rebound(
                    candles[:idx + 1],
                    lookback=getattr(config, 'rebound_lookback', 3),
                    min_body_ratio=getattr(config, 'rebound_min_body_ratio', 0.5),
                )
            )
            # Rebound short logic when buy hits +9% target
            if getattr(config, 'enable_rebound_short', True) and _rebound_confirmed:
                short_entry_px = _slippage_commission_per_share(exit_px, config, 'sell', shares=shares)  # enter short
                # Add hedge for rebound short leg (long hedge)
                if getattr(config, 'enable_eth_hedge', True) and eth_candles:
                    try:
                        short_coin_value = short_entry_px * shares
                        # No look-ahead: size hedge using history available at rebound entry decision.
                        r_hist_end = min(idx + 1, len(candles))
                        r_coin_hist = candles[:r_hist_end]
                        r_eth_hist = eth_candles[:min(r_hist_end, len(eth_candles))]
                        r_hedge_value = compute_eth_hedge_size(r_coin_hist, r_eth_hist, short_coin_value, config)
                        if r_hedge_value > 0:
                            eth_entry_r = None
                            # Spec no-look-ahead: hedge sizing above already uses
                            # eth_candles[:idx+1] (bars 0..idx), so the rebound hedge
                            # entry price must come from the SAME aligned bar idx.
                            # Previously r_entry_idx = min(idx+1, ...) read the next bar
                            # (look-ahead / misaligned vs the sizing window) and only
                            # fell back to idx when idx+1 was out of range.
                            r_entry_idx = min(idx, len(eth_candles) - 1)
                            if r_entry_idx >= 0:
                                eth_entry_r = eth_candles[r_entry_idx].get('open') or eth_candles[r_entry_idx].get('close')
                            if eth_entry_r and float(eth_entry_r) > 0:
                                r_hedge_shares = r_hedge_value / float(eth_entry_r)
                                r_hedge_entry_px = _slippage_commission_per_share(float(eth_entry_r), config, 'buy', shares=r_hedge_shares)  # long hedge
                                rebound_hedge_info = {'side': 'long', 'size': r_hedge_shares, 'entry': r_hedge_entry_px, 'exit': r_hedge_entry_px}
                    except Exception:
                        pass
                short_target = short_entry_px * (1.0 - getattr(config, 'rebound_short_target_pct', 9.0) / 100.0)
                short_stop = short_entry_px * (1.0 + getattr(config, 'rebound_short_stop_pct', 40.0) / 100.0)
                short_start_idx = idx
                short_shares = shares
                if risk_state is not None:
                    risk_state.apply_trade(str(c.get('timestamp', '')), 0.0, opened=True, closed=False, notional=short_entry_px * short_shares)
                short_bars_max = getattr(config, 'rebound_short_time_exit_bars', 48)
                short_pnl = 0.0
                for sidx in range(short_start_idx + 1, len(candles)):
                    sc = candles[sidx]
                    slow = sc.get('low')
                    shigh = sc.get('high')
                    # Check liquidation for short
                    sliq = _check_liquidation(sc, side='short', entry_px=short_entry_px, notional=short_entry_px * short_shares if short_entry_px > 0 and short_shares > 0 else 0.0, config=config)
                    if sliq is not None:
                        short_exit = _slippage_commission_per_share(float(sliq), config, 'buy', shares=short_shares)
                        short_pnl = (short_entry_px - short_exit) * short_shares
                        s_pen = getattr(config, 'liquidation_penalty_pct', 0.5) / 100.0 * (short_entry_px * short_shares)
                        short_pnl -= s_pen
                        # Funding on rebound short coin leg (spec: hourly funding on every leg).
                        hours_held_short = sidx - short_start_idx + 1
                        short_funding = _apply_funding_pnl(short_entry_px * short_shares, hours_held_short,
                                                           config.funding_rate_pct_per_hour, side='short')
                        short_pnl -= short_funding
                        if rebound_hedge_info['side'] == 'long' and rebound_hedge_info['size'] > 0:
                            eth_exit_r = None
                            if eth_candles and sidx < len(eth_candles):
                                eth_exit_r = eth_candles[sidx].get('close') or eth_candles[sidx].get('open')
                            if eth_exit_r is None:
                                eth_exit_r = rebound_hedge_info['entry']
                            r_hedge_exit_px = _slippage_commission_per_share(float(eth_exit_r), config, 'sell', shares=rebound_hedge_info['size'])
                            rebound_hedge_pnl = (r_hedge_exit_px - rebound_hedge_info['entry']) * rebound_hedge_info['size']
                            hours_held_r = sidx - short_start_idx + 1
                            rh_notional = rebound_hedge_info['entry'] * rebound_hedge_info['size']
                            rh_funding = _apply_funding_pnl(rh_notional, hours_held_r, config.funding_rate_pct_per_hour, side=rebound_hedge_info['side'])
                            rebound_hedge_pnl -= rh_funding
                            rebound_hedge_info['exit'] = r_hedge_exit_px
                        if risk_state is not None:
                            risk_state.apply_trade(str(sc.get('timestamp', '')), short_pnl + rebound_hedge_pnl, opened=False, closed=True, notional=short_entry_px * short_shares)
                        trades_log.append({'side': 'short', 'entry': short_entry_px, 'exit': short_exit, 'pnl': short_pnl, 'reason': 'liquidated'})
                        short_exit_ts = str(sc.get('timestamp', ''))
                        short_exit_price_final = short_exit
                        total_pnl += short_pnl + rebound_hedge_pnl
                        total_bars = max(total_bars, (sidx - start_idx + 1))
                        break
                    # Spec-fidelity: rebound short stop fires when the coin rises above the stop
                    # threshold. When the bar's high field is missing/None, fall back
                    # to the bar's close as the best available price proxy (fail-closed).
                    _stop_high = shigh if shigh is not None else _close_or_fallback(sc, short_entry_px)
                    if _stop_high >= short_stop:
                        short_exit = _slippage_commission_per_share(short_stop, config, 'buy', shares=short_shares)
                        short_pnl = (short_entry_px - short_exit) * short_shares
                        # Funding on rebound short coin leg (spec: hourly funding on every leg).
                        hours_held_short = sidx - short_start_idx + 1
                        short_funding = _apply_funding_pnl(short_entry_px * short_shares, hours_held_short,
                                                           config.funding_rate_pct_per_hour, side='short')
                        short_pnl -= short_funding
                        # Close rebound hedge
                        if rebound_hedge_info['side'] == 'long' and rebound_hedge_info['size'] > 0:
                            eth_exit_r = None
                            if eth_candles and sidx < len(eth_candles):
                                eth_exit_r = eth_candles[sidx].get('close') or eth_candles[sidx].get('open')
                            if eth_exit_r is None:
                                eth_exit_r = rebound_hedge_info['entry']
                            r_hedge_exit_px = _slippage_commission_per_share(float(eth_exit_r), config, 'sell', shares=rebound_hedge_info['size'])
                            rebound_hedge_pnl = (r_hedge_exit_px - rebound_hedge_info['entry']) * rebound_hedge_info['size']
                            hours_held_r = sidx - short_start_idx + 1
                            rh_notional = rebound_hedge_info['entry'] * rebound_hedge_info['size']
                            rh_funding = _apply_funding_pnl(rh_notional, hours_held_r, config.funding_rate_pct_per_hour, side=rebound_hedge_info['side'])
                            rebound_hedge_pnl -= rh_funding
                            rebound_hedge_info['exit'] = r_hedge_exit_px
                        if risk_state is not None:
                            risk_state.apply_trade(str(sc.get('timestamp', '')), short_pnl + rebound_hedge_pnl, opened=False, closed=True, notional=short_entry_px * short_shares)
                        trades_log.append({'side': 'short', 'entry': short_entry_px, 'exit': short_exit, 'pnl': short_pnl, 'reason': 'stopped'})
                        short_exit_ts = str(sc.get('timestamp', ''))
                        short_exit_price_final = short_exit
                        total_pnl += short_pnl + rebound_hedge_pnl
                        total_bars = max(total_bars, (sidx - start_idx + 1))
                        break
                    # Spec-fidelity: rebound short -9% target. When the bar's low field is
                    # missing/None, fall back to the bar's close (fail-closed).
                    _target_low = slow if slow is not None else _close_or_fallback(sc, short_entry_px)
                    if _target_low <= short_target:
                        short_exit = _slippage_commission_per_share(short_target, config, 'buy', shares=short_shares)
                        short_pnl = (short_entry_px - short_exit) * short_shares
                        # Funding on rebound short coin leg (spec: hourly funding on every leg).
                        hours_held_short = sidx - short_start_idx + 1
                        short_funding = _apply_funding_pnl(short_entry_px * short_shares, hours_held_short,
                                                           config.funding_rate_pct_per_hour, side='short')
                        short_pnl -= short_funding
                        if rebound_hedge_info['side'] == 'long' and rebound_hedge_info['size'] > 0:
                            eth_exit_r = None
                            if eth_candles and sidx < len(eth_candles):
                                eth_exit_r = eth_candles[sidx].get('close') or eth_candles[sidx].get('open')
                            if eth_exit_r is None:
                                eth_exit_r = rebound_hedge_info['entry']
                            r_hedge_exit_px = _slippage_commission_per_share(float(eth_exit_r), config, 'sell', shares=rebound_hedge_info['size'])
                            rebound_hedge_pnl = (r_hedge_exit_px - rebound_hedge_info['entry']) * rebound_hedge_info['size']
                            hours_held_r = sidx - short_start_idx + 1
                            rh_notional = rebound_hedge_info['entry'] * rebound_hedge_info['size']
                            rh_funding = _apply_funding_pnl(rh_notional, hours_held_r, config.funding_rate_pct_per_hour, side=rebound_hedge_info['side'])
                            rebound_hedge_pnl -= rh_funding
                            rebound_hedge_info['exit'] = r_hedge_exit_px
                        if risk_state is not None:
                            risk_state.apply_trade(str(sc.get('timestamp', '')), short_pnl + rebound_hedge_pnl, opened=False, closed=True, notional=short_entry_px * short_shares)
                        trades_log.append({'side': 'short', 'entry': short_entry_px, 'exit': short_exit, 'pnl': short_pnl, 'reason': 'target'})
                        short_exit_ts = str(sc.get('timestamp', ''))
                        short_exit_price_final = short_exit
                        total_pnl += short_pnl + rebound_hedge_pnl
                        total_bars = max(total_bars, (sidx - start_idx + 1))
                        break
                    if (sidx - short_start_idx + 1) >= short_bars_max:
                        sclose = _close_or_fallback(sc, short_entry_px)
                        short_exit = _slippage_commission_per_share(float(sclose), config, 'buy', shares=short_shares)
                        short_pnl = (short_entry_px - short_exit) * short_shares
                        # Funding on rebound short coin leg (spec: hourly funding on every leg).
                        # Consistent with long-leg: N bars max hold = N hours of funding.
                        hours_held_short = sidx - short_start_idx + 1
                        short_funding = _apply_funding_pnl(short_entry_px * short_shares, hours_held_short,
                                                           config.funding_rate_pct_per_hour, side='short')
                        short_pnl -= short_funding
                        if rebound_hedge_info['side'] == 'long' and rebound_hedge_info['size'] > 0:
                            eth_exit_r = None
                            if eth_candles and sidx < len(eth_candles):
                                eth_exit_r = eth_candles[sidx].get('close') or eth_candles[sidx].get('open')
                            if eth_exit_r is None:
                                eth_exit_r = rebound_hedge_info['entry']
                            r_hedge_exit_px = _slippage_commission_per_share(float(eth_exit_r), config, 'sell', shares=rebound_hedge_info['size'])
                            rebound_hedge_pnl = (r_hedge_exit_px - rebound_hedge_info['entry']) * rebound_hedge_info['size']
                            hours_held_r = sidx - short_start_idx + 1
                            rh_notional = rebound_hedge_info['entry'] * rebound_hedge_info['size']
                            rh_funding = _apply_funding_pnl(rh_notional, hours_held_r, config.funding_rate_pct_per_hour, side=rebound_hedge_info['side'])
                            rebound_hedge_pnl -= rh_funding
                            rebound_hedge_info['exit'] = r_hedge_exit_px
                        if risk_state is not None:
                            risk_state.apply_trade(str(sc.get('timestamp', '')), short_pnl + rebound_hedge_pnl, opened=False, closed=True, notional=short_entry_px * short_shares)
                        trades_log.append({'side': 'short', 'entry': short_entry_px, 'exit': short_exit, 'pnl': short_pnl, 'reason': 'time_exit'})
                        short_exit_ts = str(sc.get('timestamp', ''))
                        short_exit_price_final = short_exit
                        total_pnl += short_pnl + rebound_hedge_pnl
                        total_bars = max(total_bars, (sidx - start_idx + 1))
                        break
                else:
                    # No break occurred - exit short at last available bar
                    last_sc = candles[-1]
                    sclose = _close_or_fallback(last_sc, short_entry_px)
                    short_exit = _slippage_commission_per_share(float(sclose), config, 'buy', shares=short_shares)
                    short_pnl = (short_entry_px - short_exit) * short_shares
                    # Funding on rebound short coin leg (spec: hourly funding on every leg).
                    hours_held_short = len(candles) - short_start_idx
                    short_funding = _apply_funding_pnl(short_entry_px * short_shares, hours_held_short,
                                                       config.funding_rate_pct_per_hour, side='short')
                    short_pnl -= short_funding
                    if rebound_hedge_info['side'] == 'long' and rebound_hedge_info['size'] > 0:
                        eth_exit_r = None
                        final_coin_idx = len(candles) - 1
                        if eth_candles and final_coin_idx < len(eth_candles):
                            eth_exit_r = eth_candles[final_coin_idx].get('close') or eth_candles[final_coin_idx].get('open')
                        if eth_exit_r is None:
                            eth_exit_r = rebound_hedge_info['entry']
                        r_hedge_exit_px = _slippage_commission_per_share(float(eth_exit_r), config, 'sell', shares=rebound_hedge_info['size'])
                        rebound_hedge_pnl = (r_hedge_exit_px - rebound_hedge_info['entry']) * rebound_hedge_info['size']
                        hours_held_r = len(candles) - short_start_idx
                        rh_notional = rebound_hedge_info['entry'] * rebound_hedge_info['size']
                        rh_funding = _apply_funding_pnl(rh_notional, hours_held_r, config.funding_rate_pct_per_hour, side=rebound_hedge_info['side'])
                        rebound_hedge_pnl -= rh_funding
                        rebound_hedge_info['exit'] = r_hedge_exit_px
                    if risk_state is not None:
                        risk_state.apply_trade(str(last_sc.get('timestamp', '')), short_pnl, opened=False, closed=True, notional=short_entry_px * short_shares)
                    trades_log.append({'side': 'short', 'entry': short_entry_px, 'exit': short_exit, 'pnl': short_pnl, 'reason': 'time_exit'})
                    short_exit_ts = str(last_sc.get('timestamp', ''))
                    short_exit_price_final = short_exit
                    total_pnl += short_pnl + rebound_hedge_pnl
                    total_bars = max(total_bars, len(candles) - start_idx)

            # recompute r_mult for total
            if getattr(config, 'enable_rebound_short', True) and len(trades_log) > 1 and trades_log[-1].get('side') == 'short':
                total_risk = risk * shares * 2.0
                total_r_mult = total_pnl / total_risk if total_risk > 0 else total_r_mult
            else:
                total_r_mult = r_mult
            _has_rebound_short = len(trades_log) > 1 and any(t.get('side') == 'short' for t in trades_log)
            if _has_rebound_short:
                _pnl_out = pnl + hedge_pnl_total
            else:
                _pnl_out = long_coin_net
            return TradeResult(
                pnl=_pnl_out,
                r_multiple=total_r_mult if 'total_r_mult' in locals() else r_mult,
                exit_reason='target_rebound_short' if _has_rebound_short else 'target',
                entry_price=entry_px, exit_price=short_exit_price_final if _has_rebound_short else exit_px, shares=shares,
                bars_held=total_bars if 'total_bars' in locals() else (idx - start_idx + 1),
                entry_timestamp=entry_timestamp,
                exit_timestamp=short_exit_ts if _has_rebound_short else str(c.get('timestamp', '')),
                trades=trades_log,
                hedge_pnl=hedge_pnl_total + rebound_hedge_pnl,
                hedge_side=hedge_info['side'],
                hedge_size=hedge_info['size'],
                hedge_entry=hedge_info['entry'],
                hedge_exit=hedge_info['exit'],
                rebound_short_pnl=short_pnl if _has_rebound_short else 0.0,
                rebound_hedge_pnl=rebound_hedge_pnl if _has_rebound_short else 0.0,
                rebound_hedge_side=rebound_hedge_info['side'] if _has_rebound_short else None,
                rebound_hedge_size=rebound_hedge_info['size'] if _has_rebound_short else 0.0,
                rebound_hedge_entry=rebound_hedge_info['entry'] if _has_rebound_short else 0.0,
                rebound_hedge_exit=rebound_hedge_info['exit'] if _has_rebound_short else 0.0,
                total_pnl=total_pnl,
            )
        # Time exit: hard cap on bars held per trade.
        if config.time_exit_max_bars and (idx - start_idx + 1) >= config.time_exit_max_bars:
            exit_px = _slippage_commission_per_share(_close_or_fallback(c, entry), config, 'sell', shares=shares)
            pnl = (exit_px - entry_px) * shares
            # Funding on the long coin leg (spec: hourly funding on every leg).
            hours_held_time = idx - start_idx + 1
            long_funding = _apply_funding_pnl(entry_px * shares, hours_held_time,
                                              config.funding_rate_pct_per_hour, side='long')
            pnl -= long_funding
            if hedge_info['side'] == 'short' and hedge_info['size'] > 0:
                eth_exit_price = None
                if eth_candles and idx < len(eth_candles):
                    eth_exit_price = eth_candles[idx].get('close') or eth_candles[idx].get('open')
                if eth_exit_price is None:
                    eth_exit_price = hedge_info['entry']
                hedge_exit_px = _slippage_commission_per_share(float(eth_exit_price), config, 'buy', shares=hedge_info['size'])
                hedge_pnl_total = (hedge_info['entry'] - hedge_exit_px) * hedge_info['size']
                hours_held = idx - start_idx + 1
                hedge_notional = hedge_info['entry'] * hedge_info['size']
                funding_cost = _apply_funding_pnl(hedge_notional, hours_held, config.funding_rate_pct_per_hour, side=hedge_info['side'])
                hedge_pnl_total -= funding_cost
                hedge_info['exit'] = hedge_exit_px
            total_pnl_result = pnl + hedge_pnl_total
            r_mult = pnl / (risk * shares) if risk > 0 and shares > 0 else 0.0
            if risk_state is not None:
                try:
                    _not = entry_px * shares if ('entry_px' in locals() and entry_px > 0 and shares > 0) else 0.0
                except Exception:
                    _not = 0.0
                # Spec/portfolio attribution: risk_state realizes the full leg
                # settlement (coin + hedge) on close, consistent with other exits.
                risk_state.apply_trade(str(c.get('timestamp', '')), total_pnl_result, opened=False, closed=True, notional=_not)
            trades_log.append({'side': 'long', 'entry': entry_px, 'exit': exit_px, 'pnl': pnl, 'reason': 'time_exit'})
            return TradeResult(
                pnl=pnl, r_multiple=r_mult, exit_reason='time_exit',
                entry_price=entry_px, exit_price=exit_px, shares=shares,
                bars_held=idx - start_idx + 1,
                entry_timestamp=entry_timestamp,
                exit_timestamp=str(c.get('timestamp', '')),
                trades=trades_log,
                hedge_pnl=hedge_pnl_total,
                hedge_side=hedge_info['side'],
                hedge_size=hedge_info['size'],
                hedge_entry=hedge_info['entry'],
                hedge_exit=hedge_info['exit'],
                total_pnl=total_pnl_result,
            )

    # Time exit at last close.
    last = candles[-1]
    exit_px = _slippage_commission_per_share(_close_or_fallback(last, entry), config, 'sell', shares=shares)
    pnl = (exit_px - entry_px) * shares
    # Funding on the long leg (spec: hourly funding on every leg).
    hours_held_final = len(candles) - start_idx
    long_funding = _apply_funding_pnl(entry_px * shares, hours_held_final,
                                      config.funding_rate_pct_per_hour, side='long')
    pnl -= long_funding
    if hedge_info['side'] == 'short' and hedge_info['size'] > 0:
        eth_exit_price = None
        final_coin_idx = len(candles) - 1
        if eth_candles and final_coin_idx < len(eth_candles):
            eth_exit_price = eth_candles[final_coin_idx].get('close') or eth_candles[final_coin_idx].get('open')
        if eth_exit_price is None:
            eth_exit_price = hedge_info['entry']
        hedge_exit_px = _slippage_commission_per_share(float(eth_exit_price), config, 'buy', shares=hedge_info['size'])
        hedge_pnl_total = (hedge_info['entry'] - hedge_exit_px) * hedge_info['size']
        hours_held = len(candles) - start_idx
        hedge_notional = hedge_info['entry'] * hedge_info['size']
        funding_cost = _apply_funding_pnl(hedge_notional, hours_held, config.funding_rate_pct_per_hour, side=hedge_info['side'])
        hedge_pnl_total -= funding_cost
        hedge_info['exit'] = hedge_exit_px
    total_pnl_result = pnl + hedge_pnl_total
    r_mult = pnl / (risk * shares) if risk > 0 and shares > 0 else 0.0
    if risk_state is not None:
        try:
            _not = entry_px * shares if ('entry_px' in locals() and entry_px > 0 and shares > 0) else 0.0
        except Exception:
            _not = 0.0
        # Spec/portfolio attribution: risk_state realizes the full leg settlement
        # (coin + hedge) on close, consistent with other exits.
        risk_state.apply_trade(str(last.get('timestamp', '')), total_pnl_result, opened=False, closed=True, notional=_not)
    trades_log.append({'side': 'long', 'entry': entry_px, 'exit': exit_px, 'pnl': pnl, 'reason': 'time_exit'})
    return TradeResult(
        pnl=pnl, r_multiple=r_mult, exit_reason='time_exit',
        entry_price=entry_px, exit_price=exit_px, shares=shares,
        bars_held=len(candles) - start_idx,
        entry_timestamp=entry_timestamp,
        exit_timestamp=str(last.get('timestamp', '')),
        trades=trades_log,
        hedge_pnl=hedge_pnl_total,
        hedge_side=hedge_info['side'],
        hedge_size=hedge_info['size'],
        hedge_entry=hedge_info['entry'],
        hedge_exit=hedge_info['exit'],
        total_pnl=total_pnl_result,
    )
