"""Debug: full detail on long hedge + risk_state for aligned target cell."""
from __future__ import annotations
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.strategy.risk import DailyRiskState

def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}

cfg = StrategyConfig(
    enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
    avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
    commission_min=1.0, funding_rate_pct_per_hour=0.01,
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
eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)
for i in range(9, n):
    eth[i] = _c(f"eh{i}", 2030.0, 2050.0, 2020.0, 2040.0)
eth[55] = _c("eh55", 2030.0, 2055.0, 2020.0, 2045.0)

sig = Signal(symbol="T", side="long", reason="t", entry_price=100.0,
             stop_price=80.0, target_price=109.0, risk_per_share=20.0,
             timestamp="t5", size_shares=600.0, signal_index=5)
rs = DailyRiskState()
res = backtest_simple(coin, sig, config=cfg, risk_state=rs, capital=100000.0, eth_candles=eth)
print("hedge_side:", res.hedge_side, "hedge_size:", res.hedge_size)
print("hedge_entry:", res.hedge_entry, "hedge_exit:", res.hedge_exit)
print("hedge_pnl:", res.hedge_pnl)
print("rebound_hedge_pnl:", res.rebound_hedge_pnl)
print("total_pnl:", res.total_pnl)
print("realized:", rs.realized_pnl)
print("long coin pnl:", res.trades[0]["pnl"])
print("short coin pnl:", res.trades[1]["pnl"])
print("sum trades:", sum(t["pnl"] for t in res.trades))
print("max_live_coin_notional:", res.max_live_coin_notional)
print("short entry notional:", 108.99848333333333 * 600)
print("long entry notional:", 100.00166666666667 * 600)