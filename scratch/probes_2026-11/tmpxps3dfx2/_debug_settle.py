"""Debug risk_state settlement for aligned-ETH liq-on-48th."""
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.strategy.risk import DailyRiskState


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def base_coin(n=80):
    coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
    coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)
    for i in range(9, n):
        coin[i] = _c(f"s{i}", 108.0, 115.0, 100.0, 107.0)
    return coin


def base_eth(n=80):
    eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
    eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
    eth[8] = _c("eh8", 2000.0, 2030.0, 1995.0, 2025.0)
    for i in range(9, n):
        eth[i] = _c(f"eh{i}", 2030.0, 2050.0, 2020.0, 2040.0)
    return eth


def cfg():
    return StrategyConfig(
        enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=1.0, funding_rate_pct_per_hour=0.01,
        min_daily_volume_usd=0.0, time_exit_max_bars=200,
        enable_liquidation_checks=True,
        liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5, gross_cap_pct=120.0,
        rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
    )


def sig(shares=600.0):
    return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                  stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                  timestamp="t5", size_shares=shares, signal_index=5)


# Patch apply_trade to log
import src.strategy.risk as R
_orig = R.RiskState.apply_trade
def _logged(self, *a, **k):
    before = (self.realized_pnl, self.open_positions, self.gross_exposure, list(self.open_position_notionals))
    _orig(self, *a, **k)
    print("apply_trade", a, k, "->", (self.realized_pnl, self.open_positions, self.gross_exposure, list(self.open_position_notionals)))
R.RiskState.apply_trade = _logged

coin = base_coin()
coin[55] = _c("b55", 108.0, 120.0, 100.5, 107.0)
eth = base_eth()
eth[55] = _c("eh55", 2030.0, 2055.0, 2020.0, 2045.0)
rs = DailyRiskState()
res = backtest_simple(coin, sig(), config=cfg(), risk_state=rs, capital=100000.0, eth_candles=eth)
print("FINAL realized:", rs.realized_pnl, "total_pnl:", res.total_pnl)
print("long+short+hedge =", 5381.089699999996 + (-6614.989818000004) + 3470.686879000017)