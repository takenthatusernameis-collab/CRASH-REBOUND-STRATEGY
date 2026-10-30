from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from src.strategy.config import StrategyConfig, DEFAULT_CONFIG
from src.strategy.risk import atr, safety_stop_price, size_by_risk


def _realized_vol(candles: List[Dict[str, Any]], period: int = 336) -> Optional[float]:
    """Realized volatility (std of hourly returns) over period."""
    if len(candles) < period + 1:
        period_use = max(2, len(candles) - 1)
    else:
        period_use = period
    returns = []
    for i in range(len(candles) - period_use, len(candles)):
        if i == 0:
            continue
        close = _close(candles[i])
        prev_close = _close(candles[i - 1])
        if close is None or prev_close is None or prev_close == 0:
            continue
        returns.append((close - prev_close) / prev_close)
    if len(returns) < 2:
        return None
    mean = sum(returns) / len(returns)
    var = sum((r - mean) ** 2 for r in returns) / len(returns)
    vol = var ** 0.5
    return vol


def compute_eth_hedge_size(
    coin_candles: List[Dict[str, Any]],
    eth_candles: Optional[List[Dict[str, Any]]],
    coin_position_value: float,
    config: StrategyConfig = DEFAULT_CONFIG,
) -> float:
    """Compute hedge size: coin_vol / eth_vol * position_value, capped at 3x."""
    coin_vol = _realized_vol(coin_candles, period=config.hedge_vol_lookback_hours)
    eth_vol = _realized_vol(eth_candles, period=config.hedge_vol_lookback_hours) if eth_candles else None
    if coin_vol is None or eth_vol is None or eth_vol == 0 or coin_position_value <= 0:
        return 0.0
    hedge_ratio = coin_vol / eth_vol
    hedge_value = coin_position_value * hedge_ratio
    cap = coin_position_value * config.hedge_cap_multiplier
    if hedge_value > cap:
        hedge_value = cap
    if hedge_value < 0:
        hedge_value = 0.0
    return hedge_value


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


def _rsi(candles: List[Dict[str, Any]], period: int = 21) -> Optional[float]:
    """Calculate RSI using Wilder's smoothing method."""
    if len(candles) < period + 1:
        return None
    gains = []
    losses = []
    for i in range(1, len(candles)):
        close = _close(candles[i])
        prev_close = _close(candles[i - 1])
        if close is None or prev_close is None:
            continue
        change = close - prev_close
        if change >= 0:
            gains.append(change)
            losses.append(0.0)
        else:
            gains.append(0.0)
            losses.append(abs(change))
    if len(gains) < period:
        return None
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi


def _daily_volume_usd(candles: List[Dict[str, Any]], lookback: int = 24) -> Optional[float]:
    """Estimate daily USD volume from the last `lookback` candles.

    The raw `volume` field is treated as base-coin volume (the standard
    Hyperliquid perp convention), so quote volume = sum(volume * close).
    Returns None if no usable bars exist.
    """
    total = 0.0
    has_data = False
    for c in candles[-lookback:]:
        v = _volume(c)
        close = _close(c)
        if v is not None and close is not None and close > 0:
            total += v * close
            has_data = True
    return total if has_data else None


def detect_crash_rsi(
    candles: List[Dict[str, Any]],
    rsi_period: int = 21,
    rsi_threshold: float = 20.0,
    min_daily_volume_usd: float = 5_000_000.0,
) -> bool:
    """Detect crash via RSI(21) < threshold with optional volume filter.

    Per the PDF spec the primary trigger is a 21-hour RSI closing below 20,
    and only coins trading >= $5M in the last 24 hours are considered.
    """
    rsi = _rsi(candles, period=rsi_period)
    if rsi is None:
        return False
    if rsi >= rsi_threshold:
        return False
    if min_daily_volume_usd > 0:
        daily_vol_usd = _daily_volume_usd(candles, lookback=24)
        if daily_vol_usd is None or daily_vol_usd < min_daily_volume_usd:
            return False
    return True


def detect_crash(
    candles: List[Dict[str, Any]],
    pct_drop: float = -2.0,
    lookback: int = 5,
    volume_spike_mult: float = 1.5,
    use_rsi_trigger: bool = False,
    rsi_period: int = 21,
    rsi_threshold: float = 20.0,
    min_daily_volume_usd: float = 5_000_000.0,
) -> bool:
    if use_rsi_trigger:
        return detect_crash_rsi(candles, rsi_period=rsi_period,
                                rsi_threshold=rsi_threshold,
                                min_daily_volume_usd=min_daily_volume_usd)
    if len(candles) < 2:
        return False
    # Enforce minimum daily volume across all trigger paths per spec
    if min_daily_volume_usd > 0:
        daily_vol_usd = _daily_volume_usd(candles, lookback=24)
        if daily_vol_usd is None or daily_vol_usd < min_daily_volume_usd:
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




def _sma(candles: List[Dict[str, Any]], period: int) -> Optional[float]:
    if period <= 0 or len(candles) < period:
        return None
    closes = []
    for c in candles[-period:]:
        cl = _close(c)
        if cl is None:
            return None
        closes.append(cl)
    if not closes:
        return None
    return sum(closes) / len(closes)


def regime_ok(candles: List[Dict[str, Any]], config: StrategyConfig = DEFAULT_CONFIG) -> bool:
    """Regime filter: avoid trading in downtrends / below minimum price."""
    if candles is None or len(candles) == 0:
        return False
    cur_close = _close(candles[-1])
    if cur_close is None:
        return False
    if hasattr(config, 'regime_min_price') and config.regime_min_price is not None:
        if cur_close < config.regime_min_price:
            return False
    if getattr(config, 'avoid_downtrend', False):
        ma_period = getattr(config, 'ma_fast_period', 20)
        ma = _sma(candles, ma_period)
        if ma is not None and cur_close < ma:
            return False
    return True


def passes_universe_filter(
    candles: List[Dict[str, Any]],
    min_daily_volume_usd: float = 5_000_000.0,
    regime_config: Optional[StrategyConfig] = None,
) -> bool:
    """Check if a symbol passes universe filters (volume + regime)."""
    if min_daily_volume_usd > 0:
        daily_vol_usd = _daily_volume_usd(candles, lookback=24)
        if daily_vol_usd is None or daily_vol_usd < min_daily_volume_usd:
            return False
    if regime_config is not None:
        if not regime_ok(candles, regime_config):
            return False
    return True


def filter_universe(
    candles_by_symbol: Dict[str, List[Dict[str, Any]]],
    min_daily_volume_usd: float = 5_000_000.0,
    regime_config: Optional[StrategyConfig] = None,
) -> List[str]:
    """Return symbols passing universe filters."""
    passed = []
    for symbol, candles in candles_by_symbol.items():
        if passes_universe_filter(candles, min_daily_volume_usd=min_daily_volume_usd,
                                  regime_config=regime_config):
            passed.append(symbol)
    return passed


def position_size_by_volume(
    entry_price: float,
    daily_volume_usd: float,
    pct_of_daily_volume: float = 1.25,
) -> float:
    """Size position to pct_of_daily_volume of daily volume."""
    if entry_price <= 0 or daily_volume_usd <= 0:
        return 0.0
    position_value = daily_volume_usd * (pct_of_daily_volume / 100.0)
    return position_value / entry_price


def generate_signal(
    candles: List[Dict[str, Any]],
    symbol: str = "TEST",
    config: StrategyConfig = DEFAULT_CONFIG,
    capital: float = 100000.0,
    risk_state: Optional[Any] = None,
) -> Optional[Signal]:
    if not detect_crash(
        candles,
        pct_drop=config.crash_pct_drop,
        lookback=config.crash_lookback,
        volume_spike_mult=config.volume_spike_mult,
        use_rsi_trigger=getattr(config, 'use_rsi_trigger', False),
        rsi_period=getattr(config, 'rsi_period', 21),
        rsi_threshold=getattr(config, 'rsi_threshold', 20.0),
        min_daily_volume_usd=getattr(config, 'min_daily_volume_usd', 5_000_000.0),
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
    atr_value = atr(candles, period=config.atr_period)
    if atr_value is not None and atr_value > 0:
        stop = safety_stop_price(entry, atr_value, config.stop_atr_mult, side='long')
    else:
        stop = low * 0.999
    risk = entry - stop
    if risk <= 0:
        return None
    if getattr(config, 'target_pct', None) is not None and config.target_pct > 0:
        target = entry * (1.0 + config.target_pct / 100.0)
    else:
        target = entry + risk * config.reward_risk
    size = size_by_risk(entry, stop, capital, config.risk_per_trade_pct)
    # Volume-based sizing if enabled
    if getattr(config, 'enable_volume_based_sizing', False):
        try:
            daily_vol_usd = _daily_volume_usd(candles, lookback=24)
            if daily_vol_usd is not None and daily_vol_usd > 0 and entry > 0:
                vol_size = position_size_by_volume(
                    entry,
                    daily_vol_usd,
                    getattr(config, 'position_size_pct_of_daily_volume', 1.25),
                )
                if vol_size and vol_size > 0:
                    size = vol_size
        except Exception:
            pass  # fall back to risk-based sizing
    return Signal(
        symbol=symbol,
        side='long',
        reason='crash_then_rebound',
        entry_price=entry,
        stop_price=stop,
        target_price=target,
        risk_per_share=risk,
        timestamp=str(cur.get('timestamp', '')),
        size_shares=size,
        config_used={
            "crash_pct_drop": config.crash_pct_drop,
            "crash_lookback": config.crash_lookback,
            "volume_spike_mult": config.volume_spike_mult,
            "rebound_min_body_ratio": config.rebound_min_body_ratio,
            "stop_atr_mult": config.stop_atr_mult,
            "atr_period": config.atr_period,
            "target_pct": config.target_pct,
            "time_exit_max_bars": config.time_exit_max_bars,
            "use_rsi_trigger": getattr(config, 'use_rsi_trigger', False),
            "rsi_period": getattr(config, 'rsi_period', 21),
            "rsi_threshold": getattr(config, 'rsi_threshold', 20.0),
        },
        signal_index=len(candles) - 1,
    )


def backtest_crash_rebound(
    candles: List[Dict[str, Any]],
    symbol: str = "TEST",
    config: StrategyConfig = DEFAULT_CONFIG,
    capital: float = 100000.0,
    risk_state: Optional[Any] = None,
):
    from src.backtest.engine import backtest_simple
    sig = generate_signal(candles, symbol=symbol, config=config, capital=capital)
    if sig is None:
        return backtest_simple(candles, None, config=config, capital=capital, risk_state=risk_state)
    return backtest_simple(candles, sig, config=config, capital=capital, risk_state=risk_state)
