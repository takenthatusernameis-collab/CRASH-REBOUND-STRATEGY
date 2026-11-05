from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from src.strategy.config import StrategyConfig, DEFAULT_CONFIG


@dataclass
class RiskCheck:
    allowed: bool
    reason: str
    size_shares: float = 0.0


@dataclass
class RiskState:
    """Tracks per-day risk exposure for risk management.

    Single consolidated risk state used by both the strategy and the
    backtester. Renamed from DailyRiskState for the public API; the old
    name is re-exported for backwards compatibility.
    """

    date: str = ""
    realized_pnl: float = 0.0
    open_positions: int = 0
    daily_loss_limit_hit: bool = False
    gross_exposure: float = 0.0  # notional value of open positions
    open_position_notionals: List[float] = field(default_factory=list)  # track each position's notional

    def daily_loss_pct(self, capital: float) -> float:
        if capital <= 0:
            return 0.0
        return abs(self.realized_pnl) / capital * 100.0

    def check_position(
        self,
        config: StrategyConfig,
        capital: float,
        size_shares: float,
        entry_price: float = 0.0,
    ) -> RiskCheck:
        if self.daily_loss_limit_hit:
            return RiskCheck(False, "daily_loss_limit_hit", 0.0)
        if self.open_positions >= config.max_positions:
            return RiskCheck(False, "max_positions_reached", 0.0)
        if capital > 0 and self.daily_loss_pct(capital) >= config.max_daily_loss_pct:
            return RiskCheck(False, "daily_loss_pct_limit", 0.0)
        if capital > 0 and size_shares > 0 and entry_price > 0:
            notional = size_shares * entry_price
            cap_value = capital * config.gross_cap_pct / 100.0
            if (self.gross_exposure + notional) > cap_value:
                # With equal-share cuts, we don't block - we signal need to cut
                # But to maintain backward compat, we'll allow and let caller handle cutting
                pass  # Don't block; cutting will be handled by cut_positions_to_cap
        return RiskCheck(True, "ok", size_shares)

    def apply_trade(self, date: str, pnl: float, opened: bool, closed: bool,
                    notional: float = 0.0):
        if self.date != date:
            self.date = date
            self.realized_pnl = 0.0
            self.daily_loss_limit_hit = False
            self.open_position_notionals = []
        if opened and notional > 0:
            self.open_positions += 1
            self.gross_exposure += notional
            self.open_position_notionals.append(notional)
        if closed and notional > 0 and self.open_position_notionals:
            self.open_positions = max(0, self.open_positions - 1)
            self.gross_exposure = max(0.0, self.gross_exposure - notional)
            # Remove one occurrence of this notional (or just pop)
            try:
                self.open_position_notionals.remove(notional)
            except ValueError:
                if self.open_position_notionals:
                    self.open_position_notionals.pop()
        elif closed:
            self.open_positions = max(0, self.open_positions - 1)
            self.gross_exposure = max(0.0, self.gross_exposure - notional)
        self.realized_pnl += pnl

    def cut_positions_to_cap(self, capital: float, config: StrategyConfig,
                             open_notional: List[float] = None) -> List[float]:
        """Reduce open position notionals so the total fits under gross_cap_pct.

        Returns the new per-position notional list. Positions are cut
        equally (the vault never tops up; it only cuts).
        """
        if open_notional is None:
            open_notional = list(self.open_position_notionals) if self.open_position_notionals else []
        cap_value = capital * config.gross_cap_pct / 100.0
        total = sum(open_notional)
        if total <= cap_value or total <= 0:
            return list(open_notional)
        # Equal share across all positions
        if len(open_notional) > 0:
            equal_share = cap_value / len(open_notional)
            return [equal_share for _ in open_notional]
        factor = cap_value / total
        return [n * factor for n in open_notional]

    def apply_cap_cuts(self, capital: float, config: StrategyConfig,
                       open_notional: List[float] = None) -> List[float]:
        """Apply equal-share cuts to all positions and update internal state."""
        if open_notional is None:
            open_notional = list(self.open_position_notionals) if self.open_position_notionals else []
        cap_value = capital * config.gross_cap_pct / 100.0
        total = sum(open_notional)
        if total <= cap_value or total <= 0:
            if open_notional and len(open_notional) == len(self.open_position_notionals):
                self.open_position_notionals = list(open_notional)
                self.gross_exposure = sum(self.open_position_notionals)
            elif open_notional:
                self.open_position_notionals = list(open_notional)
                self.gross_exposure = sum(self.open_position_notionals)
                self.open_positions = len(self.open_position_notionals)
            return list(open_notional)
        # Equal share across all positions
        if len(open_notional) > 0:
            equal_share = cap_value / len(open_notional)
            cut_list = [equal_share for _ in open_notional]
        else:
            factor = cap_value / total
            cut_list = [n * factor for n in open_notional]
        self.open_position_notionals = list(cut_list)
        self.gross_exposure = sum(self.open_position_notionals)
        self.open_positions = len(self.open_position_notionals)
        return cut_list


# Backwards-compatible alias.
DailyRiskState = RiskState


def check_daily_loss_halt(state: RiskState, config: StrategyConfig, capital: float) -> bool:
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


def atr(candles: List[Dict[str, Any]], period: int = 14) -> Optional[float]:
    """True Average Range over the last `period` bars (high-low ranges).

    Returns None when there is insufficient data.
    """
    if len(candles) < 2:
        return None
    ranges = []
    for i in range(max(1, len(candles) - period), len(candles)):
        c = candles[i]
        high = c.get("high")
        low = c.get("low")
        prev_close = candles[i - 1].get("close")
        if high is None or low is None or prev_close is None:
            continue
        rng = max(float(high) - float(low), abs(float(high) - float(prev_close)),
                  abs(float(low) - float(prev_close)))
        ranges.append(rng)
    if not ranges:
        return None
    return sum(ranges) / len(ranges)


def usual_hourly_range_ratio(candles: List[Dict[str, Any]], period: int = 14) -> Optional[float]:
    """Average hourly range ratio over last `period` bars, per crash-rebound spec.

    Spec: "hourly range = avg distance high-low/prev close over last 14 hours".
    Returns the mean of (high-low)/prev_close across the last `period` bars that
    have valid high/low/prev_close with prev_close > 0. Returns None if
    insufficient data.
    """
    if not candles or len(candles) < 2 or period < 1:
        return None
    ratios = []
    start = max(1, len(candles) - period)
    for i in range(start, len(candles)):
        c = candles[i]
        prev = candles[i - 1]
        high = c.get("high")
        low = c.get("low")
        prev_close = prev.get("close")
        if high is None or low is None or prev_close is None:
            continue
        prev_close_f = float(prev_close)
        if prev_close_f <= 0:
            continue
        ratios.append((float(high) - float(low)) / prev_close_f)
    if not ratios:
        return None
    return sum(ratios) / len(ratios)


def safety_stop_price(entry_price: float, range_value: Optional[float] = None,
                      mult: float = 8.0, side: str = "long",
                      atr_value: Optional[float] = None,
                      use_ratio: Optional[bool] = None,
                      avg_range_ratio: Optional[float] = None) -> float:
    """Buy/short safety stop price.

    Spec (primary): stop = entry * (1 - mult * avg_range_ratio) for long, where
    avg_range_ratio is the mean (high-low)/prev_close over the last 14 hours.

    Backward-compatible with legacy ATR-absolute form:
      safety_stop_price(entry, atr_absolute, mult, side='long')
    """
    if avg_range_ratio is not None and range_value is None:
        range_value = avg_range_ratio
        if use_ratio is None:
            use_ratio = True
    if atr_value is not None:
        if side == "long":
            return entry_price - mult * atr_value
        return entry_price + mult * atr_value
    if range_value is None:
        return entry_price
    if use_ratio is True:
        if side == "long":
            return entry_price * (1.0 - mult * range_value)
        return entry_price * (1.0 + mult * range_value)
    if use_ratio is False:
        if side == "long":
            return entry_price - mult * range_value
        return entry_price + mult * range_value
    # Default: spec ratio semantics
    if side == "long":
        return entry_price * (1.0 - mult * range_value)
    return entry_price * (1.0 + mult * range_value)


DEFAULT_RISK_STATE = RiskState()
