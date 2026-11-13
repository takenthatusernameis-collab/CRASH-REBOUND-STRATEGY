"""Instrument: trace long-leg hedge close path."""
import math
from src.backtest import engine
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal, compute_eth_hedge_size

RATE = 0.01
SLIP = 0.001
COMM_MIN = 0.5
SHARES = 10.0


def _c(ts, o, h, l, cl, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": cl, "volume": v}


COIN = [
    _c("2025-01-01T00:00:00", 100.0, 102.0, 98.0, 100.0),
    _c("2025-01-01T01:00:00", 100.0, 101.0, 96.0, 97.0),
    _c("2025-01-01T02:00:00", 97.0, 98.0, 93.0, 94.0),
    _c("2025-01-01T03:00:00", 94.0, 95.0, 90.0, 91.0),
    _c("2025-01-01T04:00:00", 91.0, 92.0, 87.0, 88.0),
    _c("2025-01-01T05:00:00", 100.0, 104.0, 96.0, 100.0),
    _c("2025-01-01T06:00:00", 100.0, 103.0, 97.0, 100.0),
    _c("2025-01-01T07:00:00", 100.0, 110.0, 99.0, 109.0),
    _c("2025-01-01T08:00:00", 108.0, 109.5, 106.5, 108.0),
    _c("2025-01-01T09:00:00", 108.0, 109.5, 106.5, 108.0),
    _c("2025-01-01T10:00:00", 108.0, 109.5, 106.5, 108.0),
    _c("2025-01-01T11:00:00", 108.0, 109.5, 106.5, 108.0),
]
ETH = []
for i in range(12):
    px = 2000.0 + (i % 2) * 80.0
    ETH.append(_c(f"2025-01-01T{i:02d}:00:00", px, px + 30.0, px - 30.0, px + 40.0 * (i % 3 - 1)))
for i in range(8, 12):
    ETH[i] = _c(f"2025-01-01T{i:02d}:00:00", 2080.0, 2120.0, 2040.0, 2100.0)

print("len ETH:", len(ETH))
print("ETH[7]:", ETH[7])
print("ETH[5]:", ETH[5])

cfg = StrategyConfig(
    enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
    avoid_downtrend=False, slippage_pct=SLIP, commission_per_share=0.0,
    commission_min=COMM_MIN, funding_rate_pct_per_hour=RATE,
    min_daily_volume_usd=0.0, time_exit_max_bars=1000,
    rebound_short_time_exit_bars=1000, enable_liquidation_checks=False,
)

# Monkeypatch _slippage_commission to log
orig = engine._slippage_commission_per_share
def logged(price, config, side, shares=0.0):
    r = orig(price, config, side, shares)
    print(f"  slip_comm: price={price} side={side} shares={shares} -> {r}")
    return r
engine._slippage_commission_per_share = logged

sig = Signal(symbol="T", side="long", reason="t", entry_price=100.0, stop_price=50.0,
             target_price=109.0, risk_per_share=1.0, timestamp="2025-01-01T04:00:00",
             size_shares=SHARES, signal_index=4)

res = engine.backtest_simple(COIN, sig, config=cfg, eth_candles=ETH)
print("RESULT hedge_exit:", res.hedge_exit, "rebound_hedge_exit:", res.rebound_hedge_exit)
print("RESULT hedge_pnl:", res.hedge_pnl, "rebound_hedge_pnl:", res.rebound_hedge_pnl)
print("RESULT total_pnl:", res.total_pnl)
print("RESULT trades:", res.trades)