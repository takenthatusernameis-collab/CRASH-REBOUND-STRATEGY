from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from src.strategy.config import StrategyConfig, DEFAULT_CONFIG


@dataclass
class RiskCheck:
    allowed: bool
    reason: str
    size_shares: float = 0.0


@dataclass
class DailyRiskState:
    date: str = ""
    realized_pnl: float = 0.0
    open_positions: int = 0
    daily_loss_limit_hit: bool = False

    def daily_loss_pct(self, capital: float) -> float:
        if capital <= 0:
            return 0.0
        return abs(self.realized_pnl) / capital * 100.0

    def check_position(
        self,
        config: StrategyConfig,
        capital: float,
        size_shares: float,
    ) -> RiskCheck:
        if self.daily_loss_limit_hit:
            return RiskCheck(False, "daily_loss_limit_hit", 0.0)
        if self.open_positions >= config.max_positions:
            return RiskCheck(False, "max_positions_reached", 0.0)
        if capital > 0 and self.daily_loss_pct(capital) >= config.max_daily_loss_pct:
            return RiskCheck(False, "daily_loss_pct_limit", 0.0)
        return RiskCheck(True, "ok", size_shares)

    def apply_trade(self, date: str, pnl: float, opened: bool, closed: bool):
        if self.date != date:
            self.date = date
            self.realized_pnl = 0.0
            self.daily_loss_limit_hit = False
        if opened:
            self.open_positions += 1
        if closed:
            self.open_positions = max(0, self.open_positions - 1)
        self.realized_pnl += pnl
        if self.realized_pnl < 0 and abs(self.realized_pnl) > 0:
            pass


def check_daily_loss_halt(state: DailyRiskState, config: StrategyConfig, capital: float) -> bool:
    """Return True if trading should be halted for the day."""
    if state.daily_loss_limit_hit:
        return True
    if capital <= 0:
        return False
    return state.daily_loss_pct(capital) >= config.max_daily_loss_pct


def size_by_risk(
    entry_price: float,
    stop_price: float,
    capital: float,
    risk_pct: float,
) -> float:
    """Shares to trade given risk % of capital. 0.0 when risk per share <= 0."""
    risk_per_share = entry_price - stop_price
    if risk_per_share <= 0:
        return 0.0
    risk_amount = capital * risk_pct / 100.0
    return risk_amount / risk_per_share


def apply_slippage_commission(
    price: float,
    shares: float,
    config: StrategyConfig,
    side: str = "buy",
) -> float:
    """Round-trip aware per-share cost including slippage and commission."""
    slip = price * config.slippage_pct
    comm = config.commission_per_share
    if config.commission_min > 0 and shares > 0:
        comm = max(comm, config.commission_min / shares)
    return price + slip + comm if side == "buy" else price - slip - comm
