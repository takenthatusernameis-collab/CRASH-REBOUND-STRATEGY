from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from src.strategy.config import StrategyConfig, DEFAULT_CONFIG


@dataclass
class TradeResult:
    pnl: float
    r_multiple: float
    exit_reason: str
    entry_price: float = 0.0
    exit_price: float = 0.0
    shares: float = 0.0
    bars_held: int = 0


def _slippage_commission_per_share(price: float, config: StrategyConfig, side: str) -> float:
    slip = price * config.slippage_pct
    comm = config.commission_per_share
    return price + slip + comm if side == "buy" else price - slip - comm


def backtest_simple(
    candles: List[Dict[str, Any]],
    signal,
    config: StrategyConfig = DEFAULT_CONFIG,
    capital: float = 100000.0,
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

    # Look-ahead guard: only inspect candles at or after the entry point.
    for idx in range(start_idx, len(candles)):
        c = candles[idx]
        low = c.get('low')
        high = c.get('high')
        if low is not None and low <= stop_px:
            exit_px = _slippage_commission_per_share(stop_px, config, 'sell')
            pnl = (exit_px - entry_px) * shares
            r_mult = pnl / (risk * shares) if risk > 0 and shares > 0 else 0.0
            return TradeResult(
                pnl=pnl, r_multiple=r_mult, exit_reason='stopped',
                entry_price=entry_px, exit_price=exit_px, shares=shares,
                bars_held=idx - start_idx + 1,
            )
        if high is not None and high >= target_px:
            exit_px = _slippage_commission_per_share(target_px, config, 'sell')
            pnl = (exit_px - entry_px) * shares
            r_mult = pnl / (risk * shares) if risk > 0 and shares > 0 else 0.0
            return TradeResult(
                pnl=pnl, r_multiple=r_mult, exit_reason='target',
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
    return TradeResult(
        pnl=pnl, r_multiple=r_mult, exit_reason='time_exit',
        entry_price=entry_px, exit_price=exit_px, shares=shares,
        bars_held=len(candles) - start_idx,
    )
