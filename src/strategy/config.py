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
    crash_pct_drop: float = -2.0       # % drop from open or prior close to trigger
    crash_lookback: int = 5            # bars to scan for crash trigger

    # Rebound confirmation
    rebound_lookback: int = 3
    rebound_min_body_ratio: float = 0.5  # close must be in upper half of range

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

    # Risk
    risk_per_trade_pct: float = 1.0    # % of capital risked per trade
    max_positions: int = 5             # max concurrent positions
    max_daily_loss_pct: float = 3.0    # max daily loss before halt
    gross_cap_pct: float = 120.0       # gross exposure cap (% of capital) with equal-share cuts

    # Filters
    volume_spike_mult: float = 1.5     # volume must exceed avg * mult on crash bar
    regime_min_price: float = 5.0      # avoid penny stocks
    avoid_downtrend: bool = True       # require price above fast MA to avoid catching knife
    ma_fast_period: int = 20           # fast MA period for regime filter

    # Backtest realism
    slippage_pct: float = 0.0005       # 0.05% slippage per side
    commission_per_share: float = 0.001  # commission per share
    commission_min: float = 1.0        # minimum commission per trade

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


DEFAULT_CONFIG = StrategyConfig()