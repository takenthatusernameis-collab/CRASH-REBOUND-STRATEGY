from dataclasses import dataclass, field


@dataclass
class StrategyConfig:
    """Configuration for the crash-rebound strategy. All values tunable."""

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
    reward_risk: float = 1.5           # target = entry + risk * reward_risk
    stop_atr_mult: float = 1.5         # stop = low * (1 - atr_mult) placeholder
    time_exit_max_bars: int = 20       # max bars in trade before time exit

    # Risk
    risk_per_trade_pct: float = 1.0    # % of capital risked per trade
    max_positions: int = 5             # max concurrent positions
    max_daily_loss_pct: float = 3.0    # max daily loss before halt

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


DEFAULT_CONFIG = StrategyConfig()


@dataclass
class RiskState:
    """Tracks per-day risk exposure for risk management."""

    date: str = ""
    realized_pnl: float = 0.0
    open_positions: int = 0
    daily_loss_limit_hit: bool = False

    def daily_loss_pct(self, capital: float) -> float:
        if capital <= 0:
            return 0.0
        return abs(self.realized_pnl) / capital * 100.0

    def can_open_position(self, config: StrategyConfig, capital: float) -> bool:
        if self.open_positions >= config.max_positions:
            return False
        if self.daily_loss_limit_hit:
            return False
        if capital > 0 and self.daily_loss_pct(capital) >= config.max_daily_loss_pct:
            return True  # signal halt externally
        return True


DEFAULT_RISK_STATE = RiskState()
