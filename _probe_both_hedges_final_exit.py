"""Probe: can we construct a fixture where BOTH the long-leg short ETH hedge AND
the rebound long ETH hedge are established, exiting via loop-else final exit?

The existing final-exit locks (2026-11-10) assert `res.hedge_side is None` for the
rebound path because the long-leg hedge sizing returned 0 (insufficient/low
relative vol path at entry). This probe finds ETH series variation that yields
nonzero long-leg hedge value so the "both hedges present" cell is reachable.
"""
import math
from src.backtest.engine import backtest_simple, _apply_funding_pnl
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal, compute_eth_hedge_size
from src.strategy.risk import DailyRiskState


def _c(ts, o, h, l, cl, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": cl, "volume": v}


RATE = 0.01
SLIP = 0.001
COMM_MIN = 0.5
SHARES = 10.0

# COIN with nonzero realized vol (so long-leg hedge sizing returns > 0).
# Bars 0..6: alternating +/- 3% closes; bar 7: target hit; bars 8..11: flat.
COIN = []
for i in range(7):
    cl = 100.0 * (1.0 + (0.03 if i % 2 else -0.03))
    COIN.append(_c(f"2025-01-01T{i:02d}:00:00", cl * 0.99, cl * 1.02, cl * 0.98, cl))
COIN.append(_c("2025-01-01T07:00:00", 100.0, 110.0, 99.0, 109.0))
for i in range(8, 12):
    COIN.append(_c(f"2025-01-01T{i:02d}:00:00", 108.0, 112.0, 105.0, 108.0))


def _cfg(rate=RATE):
    return StrategyConfig(
        enable_eth_hedge=True,
        enable_rebound_short=True,
        entry_next_bar=True,
        avoid_downtrend=False,
        slippage_pct=SLIP,
        commission_per_share=0.0,
        commission_min=COMM_MIN,
        funding_rate_pct_per_hour=rate,
        min_daily_volume_usd=0.0,
        time_exit_max_bars=50,
        rebound_short_time_exit_bars=100,
        enable_liquidation_checks=False,
    )


def _sig():
    return Signal(
        symbol="T", side="long", reason="t", entry_price=100.0, stop_price=50.0,
        target_price=109.0, risk_per_share=1.0, timestamp="2025-01-01T05:00:00",
        size_shares=SHARES, signal_index=5,
    )


# ETH series with strong variation so both long-leg and rebound hedge sizing
# return nonzero values. Coin vol must be > ETH vol (ratio > 1) for a short hedge
# on the long leg; for the rebound leg the coin is shorted and the hedge is long.
def make_eth():
    eth = []
    for i in range(12):
        px = 2000.0 + (i % 2) * 100.0
        eth.append(_c(f"2025-01-01T{i:02d}:00:00", px, px + 20.0, px - 20.0, px + 50.0 * (i % 3 - 1)))
    for i in range(8, 12):
        eth[i] = _c(f"2025-01-01T{i:02d}:00:00", 2100.0, 2120.0, 2080.0, 2110.0)
    return eth


ETH = make_eth()
cfg = _cfg()

# Long-leg hedge sizing window: candles[:7], eth[:7]
coin_pos = (100.0 + 100.0 * SLIP + COMM_MIN / SHARES) * SHARES
lv = compute_eth_hedge_size(COIN[:7], ETH[:7], coin_pos, cfg)
print("LONG-LEG hedge value:", lv)

# Rebound-leg hedge sizing window: candles[:8], eth[:8] at idx 7
short_entry = 108.84533216349999
short_pos = short_entry * SHARES
rv = compute_eth_hedge_size(COIN[:8], ETH[:8], short_pos, cfg)
print("REBOUND hedge value:", rv)

res = backtest_simple(COIN, _sig(), config=cfg, eth_candles=ETH)
print("hedge_side:", res.hedge_side, "hedge_size:", res.hedge_size)
print("rebound_hedge_side:", res.rebound_hedge_side, "rebound_hedge_size:", res.rebound_hedge_size)
print("exit_reason:", res.exit_reason, "total_pnl:", res.total_pnl)