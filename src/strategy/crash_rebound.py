from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class Signal:
    symbol: str
    side: str  # 'long'
    reason: str
    entry_price: float
    stop_price: float
    target_price: float
    risk_per_share: float
    timestamp: str = ""


def detect_crash(candles: List[Dict[str, Any]], pct_drop: float = -2.0) -> bool:
    """Detect a crash: look for a candle with large drop."""
    if len(candles) < 2:
        return False
    # check last pair and also previous pair
    for i in range(len(candles) - 1, max(0, len(candles) - 5), -1):
        prev = candles[i - 1]
        cur = candles[i]
        if prev.get('close') and cur.get('open') and cur.get('close'):
            drop_from_open = (cur['close'] - cur['open']) / cur['open'] * 100.0
            if drop_from_open <= pct_drop:
                return True
        if prev.get('close') and cur.get('close'):
            drop_from_prev_close = (cur['close'] - prev['close']) / prev['close'] * 100.0
            if drop_from_prev_close <= pct_drop:
                return True
    return False


def confirm_rebound(candles: List[Dict[str, Any]], lookback: int = 3) -> bool:
    """Confirm rebound: recent candle shows bullish reversal (close > open and above mid)."""
    if len(candles) < 1:
        return False
    cur = candles[-1]
    if cur.get('open') and cur.get('close') and cur.get('high') and cur.get('low'):
        if cur['close'] > cur['open']:
            rng = cur['high'] - cur['low']
            if rng > 0 and (cur['close'] - cur['low']) / rng >= 0.5:
                return True
    return False


def generate_signal(candles: List[Dict[str, Any]], symbol: str = "TEST") -> Optional[Signal]:
    if not detect_crash(candles):
        return None
    if not confirm_rebound(candles):
        return None
    cur = candles[-1]
    entry = cur['close']
    stop = cur['low'] * 0.999
    risk = entry - stop
    if risk <= 0:
        return None
    target = entry + risk * 1.5
    return Signal(
        symbol=symbol,
        side='long',
        reason='crash_then_rebound',
        entry_price=entry,
        stop_price=stop,
        target_price=target,
        risk_per_share=risk,
        timestamp=str(cur.get('timestamp', ''))
    )
