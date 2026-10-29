from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class TradeResult:
    pnl: float
    r_multiple: float
    exit_reason: str


def backtest_simple(candles: List[Dict[str, Any]], signal) -> TradeResult:
    if signal is None:
        return TradeResult(pnl=0.0, r_multiple=0.0, exit_reason='no_signal')
    entry = signal.entry_price
    stop = signal.stop_price
    target = signal.target_price
    risk = signal.risk_per_share
    # look ahead from signal point
    for c in candles:
        if c.get('low') and c['low'] <= stop:
            return TradeResult(pnl=-(entry - stop), r_multiple=-1.0, exit_reason='stopped')
        if c.get('high') and c['high'] >= target:
            return TradeResult(pnl=(target - entry), r_multiple=(target - entry) / risk if risk > 0 else 0.0, exit_reason='target')
    # time exit
    last = candles[-1]
    exit_px = last.get('close', entry)
    pnl = exit_px - entry
    r_mult = pnl / risk if risk > 0 else 0.0
    return TradeResult(pnl=pnl, r_multiple=r_mult, exit_reason='time_exit')
