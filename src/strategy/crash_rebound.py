from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from src.strategy.config import StrategyConfig, DEFAULT_CONFIG
from src.strategy.risk import atr, safety_stop_price


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
    size_shares: float = 0.0
    config_used: Optional[dict] = None
    signal_index: int = -1



def _close(c: Dict[str, Any]) -> Optional[float]:
    v = c.get("close")
    return float(v) if v is not None else None


def _open(c: Dict[str, Any]) -> Optional[float]:
    v = c.get("open")
    return float(v) if v is not None else None


def _low(c: Dict[str, Any]) -> Optional[float]:
    v = c.get("low")
    return float(v) if v is not None else None


def _high(c: Dict[str, Any]) -> Optional[float]:
    v = c.get("high")
    return float(v) if v is not None else None


def _volume(c: Dict[str, Any]) -> Optional[float]:
    v = c.get("volume")
    return float(v) if v is not None else None


def detect_crash(
    candles: List[Dict[str, Any]],
    pct_drop: float = -2.0,
    lookback: int = 5,
    volume_spike_mult: float = 1.5,
) -> bool:
    """Detect a crash: a candle with large drop from open or prior close.

    Optional volume confirmation: crash bar volume must exceed the average
    of the preceding bars by volume_spike_mult when volume data is present.
    """
    if len(candles) < 2:
        return False
    start = max(0, len(candles) - lookback)
    for i in range(len(candles) - 1, start - 1, -1):
        prev = candles[i - 1]
        cur = candles[i]
        cur_open = _open(cur)
        cur_close = _close(cur)
        prev_close = _close(prev)
        triggered = False
        if cur_open is not None and cur_close is not None and cur_open > 0:
            drop_from_open = (cur_close - cur_open) / cur_open * 100.0
            if drop_from_open <= pct_drop:
                triggered = True
        if prev_close is not None and cur_close is not None and prev_close > 0:
            drop_from_prev_close = (cur_close - prev_close) / prev_close * 100.0
            if drop_from_prev_close <= pct_drop:
                triggered = True
        if not triggered:
            continue
        # Volume confirmation when data available
        cur_vol = _volume(cur)
        if cur_vol is not None:
            prior_vols = [_volume(c) for c in candles[start:i]]
            prior_vols = [v for v in prior_vols if v is not None]
            if prior_vols:
                avg_vol = sum(prior_vols) / len(prior_vols)
                if avg_vol > 0 and cur_vol < avg_vol * volume_spike_mult:
                    continue
        return True
    return False


def confirm_rebound(
    candles: List[Dict[str, Any]],
    lookback: int = 3,
    min_body_ratio: float = 0.5,
) -> bool:
    """Confirm rebound: most recent candle shows bullish reversal in upper range."""
    if len(candles) < 1:
        return False
    cur = candles[-1]
    cur_open = _open(cur)
    cur_close = _close(cur)
    cur_high = _high(cur)
    cur_low = _low(cur)
    if None in (cur_open, cur_close, cur_high, cur_low):
        return False
    if cur_close <= cur_open:
        return False
    rng = cur_high - cur_low
    if rng <= 0:
        return False
    return (cur_close - cur_low) / rng >= min_body_ratio


def regime_ok(candles: List[Dict[str, Any]], config: StrategyConfig) -> bool:
    """Regime filter: avoid catching a falling knife in a downtrend.

    Requires the most recent close to be above the fast MA when avoid_downtrend
    is set, and price above regime_min_price.
    """
    if not config.avoid_downtrend:
        return True
    closes = [_close(c) for c in candles]
    closes = [c for c in closes if c is not None]
    if len(closes) < config.ma_fast_period:
        return True  # not enough history; do not block
    ma = sum(closes[-config.ma_fast_period:]) / config.ma_fast_period
    cur_close = closes[-1]
    if cur_close < config.regime_min_price:
        return False
    if cur_close < ma:
        return False
    return True


def position_size_shares(
    entry_price: float,
    stop_price: float,
    capital: float,
    risk_pct: float,
) -> float:
    """Position size in shares by risk % of capital.

    risk_amount = capital * risk_pct / 100; shares = risk_amount / (entry - stop).
    Returns 0.0 when risk per share is non-positive.
    """
    risk_per_share = entry_price - stop_price
    if risk_per_share <= 0:
        return 0.0
    risk_amount = capital * risk_pct / 100.0
    return risk_amount / risk_per_share


def generate_signal(
    candles: List[Dict[str, Any]],
    symbol: str = "TEST",
    config: StrategyConfig = DEFAULT_CONFIG,
    capital: float = 100000.0,
) -> Optional[Signal]:
    if not detect_crash(
        candles,
        pct_drop=config.crash_pct_drop,
        lookback=config.crash_lookback,
        volume_spike_mult=config.volume_spike_mult,
    ):
        return None
    if not confirm_rebound(
        candles,
        lookback=config.rebound_lookback,
        min_body_ratio=config.rebound_min_body_ratio,
    ):
        return None
    if not regime_ok(candles, config):
        return None
    cur = candles[-1]
    entry = _close(cur)
    low = _low(cur)
    if entry is None or low is None or entry <= 0:
        return None
    # ATR-based stop per PDF (8x ATR(14)); fallback to low*0.999 if ATR unavailable
    atr_value = atr(candles, period=config.atr_period)
    if atr_value is not None and atr_value > 0:
        stop = safety_stop_price(entry, atr_value, config.stop_atr_mult, side='long')
    else:
        stop = low * 0.999
    risk = entry - stop
    if risk <= 0:
        return None
    # Target: prefer explicit target_pct (+9%) if set, else risk*reward_risk
    if getattr(config, 'target_pct', None) is not None and config.target_pct > 0:
        target = entry * (1.0 + config.target_pct / 100.0)
    else:
        target = entry + risk * config.reward_risk
    size = position_size_shares(entry, stop, capital, config.risk_per_trade_pct)
def backtest_crash_rebound(
    candles: List[Dict[str, Any]],
    symbol: str = "TEST",
    config: StrategyConfig = DEFAULT_CONFIG,
    capital: float = 100000.0,
    risk_state: Optional[Any] = None,
):
    """Convenience function for crash-rebound backtest with rebound-short support."""
    from src.backtest.engine import backtest_simple
    sig = generate_signal(candles, symbol=symbol, config=config, capital=capital)
    if sig is None:
        return backtest_simple(candles, None, config=config, capital=capital, risk_state=risk_state)
    return backtest_simple(candles, sig, config=config, capital=capital, risk_state=risk_state)
