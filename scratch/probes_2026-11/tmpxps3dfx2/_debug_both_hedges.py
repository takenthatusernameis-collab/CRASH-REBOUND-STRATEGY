"""Debug trace details for both-hedges final-exit."""
import math
from src.backtest.engine import backtest_simple, _apply_funding_pnl, _slippage_commission_per_share
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal, compute_eth_hedge_size


def _c(ts, o, h, l, cl, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": cl, "volume": v}


RATE = 0.01
SLIP = 0.001
COMM_MIN = 0.5
SHARES = 10.0

COIN = [
    _c("2025-01-01T00:00:00", 100.0, 104.0, 96.0, 102.0),
    _c("2025-01-01T01:00:00", 102.0, 106.0, 98.0, 100.0),
    _c("2025-01-01T02:00:00", 100.0, 104.0, 96.0, 98.0),
    _c("2025-01-01T03:00:00", 98.0, 102.0, 94.0, 100.0),
    _c("2025-01-01T04:00:00", 100.0, 104.0, 96.0, 102.0),
    _c("2025-01-01T05:00:00", 102.0, 106.0, 98.0, 100.0),
    _c("2025-01-01T06:00:00", 100.0, 101.0, 99.0, 100.0),
    _c("2025-01-01T07:00:00", 100.0, 110.0, 99.0, 109.0),
]
for i in range(8, 12):
    COIN.append(_c(f"2025-01-01T{i:02d}:00:00", 108.0, 112.0, 105.0, 108.0))

ETH = []
for i in range(12):
    px = 2000.0 + (i % 2) * 100.0
    ETH.append(_c(f"2025-01-01T{i:02d}:00:00", px, px + 20.0, px - 20.0, px + 50.0 * (i % 3 - 1)))
for i in range(8, 12):
    ETH[i] = _c(f"2025-01-01T{i:02d}:00:00", 2100.0, 2120.0, 2080.0, 2110.0)

print("ETH[6]:", ETH[6])
print("ETH[7]:", ETH[7])
print("ETH[7].close:", ETH[7].get('close'))

cfg = StrategyConfig(
    enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
    avoid_downtrend=False, slippage_pct=SLIP, commission_per_share=0.0,
    commission_min=COMM_MIN, funding_rate_pct_per_hour=RATE,
    min_daily_volume_usd=0.0, time_exit_max_bars=50, rebound_short_time_exit_bars=100,
    enable_liquidation_checks=False,
)
sig = Signal(symbol="T", side="long", reason="t", entry_price=100.0, stop_price=50.0,
             target_price=109.0, risk_per_share=1.0, timestamp="2025-01-01T05:00:00",
             size_shares=SHARES, signal_index=5)

# Long leg hedge sizing
entry_px = 100.15
coin_position_value = entry_px * SHARES
long_hedge_value = compute_eth_hedge_size(COIN[:7], ETH[:7], coin_position_value, cfg)
print("\nlong_hedge_value:", repr(long_hedge_value))
hedge_shares = long_hedge_value / 2000.0
print("hedge_shares:", repr(hedge_shares))
hedge_entry_px = _slippage_commission_per_share(2000.0, cfg, 'sell', shares=hedge_shares)
print("hedge_entry_px:", repr(hedge_entry_px))
# Exit at idx 7 close 2110
hedge_exit_px = _slippage_commission_per_share(2110.0, cfg, 'buy', shares=hedge_shares)
print("hedge_exit_px (close 2110):", repr(hedge_exit_px))
hedge_exit_px2 = _slippage_commission_per_share(2100.0, cfg, 'buy', shares=hedge_shares)
print("hedge_exit_px (close 2100):", repr(hedge_exit_px2))

res = backtest_simple(COIN, sig, config=cfg, eth_candles=ETH)
print("\nres.hedge_exit:", repr(res.hedge_exit))
print("res.hedge_pnl:", repr(res.hedge_pnl))