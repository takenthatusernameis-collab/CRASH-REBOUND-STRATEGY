"""Debug: print intermediate values for the short target path."""
from __future__ import annotations
import src.backtest.engine as eng
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal

orig = eng._slippage_commission_per_share
def traced(price, config, side, shares=0.0):
    r = orig(price, config, side, shares)
    print(f"  slip_comm: price={price!r} side={side} shares={shares} -> {r!r}")
    return r
eng._slippage_commission_per_share = traced

from src.backtest.engine import backtest_simple
from src.strategy.risk import DailyRiskState

def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}

cfg = StrategyConfig(
    enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
    avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
    commission_min=1.0, funding_rate_pct_per_hour=0.0,
    min_daily_volume_usd=0.0, time_exit_max_bars=200,
    enable_liquidation_checks=True, gross_cap_pct=120.0,
    rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
    rebound_short_time_exit_bars=48,
)
n = 80
coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)
for i in range(9, n):
    coin[i] = _c(f"s{i}", 108.0, 115.0, 100.0, 107.0)
coin[55] = _c("b55", 108.0, 115.0, 99.0, 107.0)
sig = Signal(symbol="T", side="long", reason="t", entry_price=100.0,
             stop_price=80.0, target_price=109.0, risk_per_share=20.0,
             timestamp="t5", size_shares=600.0, signal_index=5)
res = backtest_simple(coin, sig, config=cfg, risk_state=DailyRiskState(),
                      capital=100000.0, eth_candles=None)
print("short leg:", res.trades[1])
print("short_target should be:", 108.99848333333333 * 0.91)