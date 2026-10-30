from dataclasses import dataclass, field
from typing import Optional


@dataclass
class StrategyConfig:
    """Configuration for the crash-rebound strategy. All values tunable.

    Defaults are aligned to the published crash-rebound strategy report
    (Hyperliquid hourly perps): 21h RSI<20 crash trigger, +9% target,
    50h time exit, 8x-ATR safety stop, 1.25% of daily volume position size,
    120% gross cap with equal-share cuts, ETH hedge on every leg.
    """

    # Universe
    universe: tuple = ("SPY", "QQQ", "IWM")

    # Crash trigger
    use_rsi_trigger: bool = True       # use RSI-based trigger (PDF primary) vs price-drop trigger
    rsi_period: int = 21               # RSI period (21h per spec)
    rsi_threshold: float = 20.0        # RSI < threshold triggers
    crash_pct_drop: float = -2.0       # % drop from open or prior close to trigger
    crash_lookback: int = 5            # bars to scan for crash trigger
    min_daily_volume_usd: float = 5_000_000.0  # minimum 24h volume per spec

    # Rebound confirmation
    rebound_lookback: int = 3
    rebound_min_body_ratio: float = 0.5  # close must be in upper half of range

    # Risk / sizing
    risk_per_trade_pct: float = 1.0      # % of capital risked per trade (fallback sizing)
    max_positions: int = 5               # max open positions
    max_daily_loss_pct: float = 3.0      # daily loss halt (%)
    gross_cap_pct: float = 120.0         # 120% gross cap per spec

    # Entry
    entry_next_bar: bool = True        # enter on next bar open (avoid look-ahead)
    entry_limit_offset_pct: float = 0.0  # limit offset from entry price

    # Exit
    reward_risk: float = 1.5           # target = entry + risk * reward_risk (fallback)
    target_pct: Optional[float] = 9.0  # target = entry * (1 + target_pct/100) when set
    stop_atr_mult: float = 8.0         # buy safety stop = entry - mult * ATR(14)
    atr_period: int = 14               # ATR lookback for safety stop
    time_exit_max_bars: int = 50       # max bars in trade before time exit

    # Rebound short (after buy hits +9% target)
    enable_rebound_short: bool = True
    rebound_short_target_pct: float = 9.0  # close short at entry_short * (1 - target_pct/100)
    rebound_short_time_exit_bars: int = 48  # max bars for rebound short
    rebound_short_stop_pct: float = 40.0   # wide stop per spec (close if up 40%)

    # Position sizing / caps (PDF)
    position_size_pct_of_daily_volume: float = 1.25  # 1.25% of coin's 24h volume
    enable_volume_based_sizing: bool = True  # if True, use volume-based sizing

    # ETH hedge
    enable_eth_hedge: bool = True
    hedge_vol_lookback_hours: int = 336  # ~14 days
    hedge_cap_multiplier: float = 3.0  # cap hedge at 3x position
    eth_symbol: str = "ETH"

    # Filters
    volume_spike_mult: float = 1.5     # volume must exceed avg * mult on crash bar
    regime_min_price: float = 5.0      # avoid penny stocks
    avoid_downtrend: bool = True       # require price above fast MA to avoid catching knife
    ma_fast_period: int = 20           # fast MA period for regime filter

    # Backtest realism
    slippage_pct: float = 0.0005       # 0.05% slippage per side
    commission_per_share: float = 0.001  # commission per share
    commission_min: float = 1.0        # minimum commission per trade
    funding_rate_pct_per_hour: float = 0.01  # hourly funding (0.01% = 0.0001)

    # Liquidation (execution realism)
    enable_liquidation_checks: bool = True
    liquidation_maint_margin_pct: float = 5.0  # maintenance margin % of notional (conservative)
    liquidation_buffer_pct: float = 1.0       # buffer before liquidation
    liquidation_penalty_pct: float = 0.5      # penalty % of notional on liquidation

    def __post_init__(self):
        if not 0 < self.risk_per_trade_pct <= 10:
            raise ValueError("risk_per_trade_pct must be in (0, 10]")
        if self.max_positions < 1:
            raise ValueError("max_positions must be >= 1")
        if self.reward_risk <= 0:
            raise ValueError("reward_risk must be > 0")
        if self.stop_atr_mult <= 0:
            raise ValueError("stop_atr_mult must be > 0")
        if self.atr_period < 1:
            raise ValueError("atr_period must be >= 1")
        if self.time_exit_max_bars < 1:
            raise ValueError("time_exit_max_bars must be >= 1")
        if not 0 < self.gross_cap_pct:
            raise ValueError("gross_cap_pct must be > 0")
        if self.rsi_period < 2:
            raise ValueError("rsi_period must be >= 2")
        if not 0 < self.rsi_threshold <= 100:
            raise ValueError("rsi_threshold must be in (0, 100]")
        if self.min_daily_volume_usd < 0:
            raise ValueError("min_daily_volume_usd must be >= 0")


DEFAULT_CONFIG = StrategyConfig()