"""Probe: rebound-short FINAL EXIT (loop-else) with BOTH hedges funded.
Long-leg short ETH hedge (aligned at long entry) AND rebound-leg long ETH hedge
(aligned at rebound entry). Existing coverage only has single-hedge cases.
"""
import math
from src.backtest.engine import backtest_simple, _apply_funding_pnl
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal, compute_eth_hedge_size


def _c(ts, o, h, l, cl, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": cl, "volume": v}


def _close_to(x, y, tol=1e-9):
    return math.isclose(float(x), float(y), rel_tol=0.0, abs_tol=tol)


RATE = 0.01
SLIP = 0.001
COMM_MIN = 0.5
SHARES = 10.0

# 12 bars 0..11
# Coin has meaningful variation at entry (bars 0..6) so long-leg hedge sizes > 0.
COIN = [
    _c("2025-01-01T00:00:00", 100.0, 104.0, 96.0, 102.0),
    _c("2025-01-01T01:00:00", 102.0, 106.0, 98.0, 100.0),
    _c("2025-01-01T02:00:00", 100.0, 104.0, 96.0, 98.0),
    _c("2025-01-01T03:00:00", 98.0, 102.0, 94.0, 100.0),
    _c("2025-01-01T04:00:00", 100.0, 104.0, 96.0, 102.0),
    _c("2025-01-01T05:00:00", 102.0, 106.0, 98.0, 100.0),  # signal bar (idx 5)
    _c("2025-01-01T06:00:00", 100.0, 101.0, 99.0, 100.0),  # long entry bar (idx 6)
    _c("2025-01-01T07:00:00", 100.0, 110.0, 99.0, 109.0),  # long target hit (idx 7)
]
for i in range(8, 12):
    COIN.append(_c(f"2025-01-01T{i:02d}:00:00", 108.0, 112.0, 105.0, 108.0))

# ETH with high realized vol so BOTH hedges size > 0.
ETH = []
for i in range(12):
    px = 2000.0 + (i % 2) * 100.0
    ETH.append(_c(f"2025-01-01T{i:02d}:00:00", px, px + 20.0, px - 20.0, px + 50.0 * (i % 3 - 1)))
for i in range(8, 12):
    ETH[i] = _c(f"2025-01-01T{i:02d}:00:00", 2100.0, 2120.0, 2080.0, 2110.0)


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
        symbol="T", side="long", reason="t",
        entry_price=100.0, stop_price=50.0, target_price=109.0,
        risk_per_share=1.0, timestamp="2025-01-01T05:00:00",
        size_shares=SHARES, signal_index=5,
    )


res = backtest_simple(COIN, _sig(), config=_cfg(RATE), eth_candles=ETH)
print("exit_reason:", res.exit_reason)
print("entry_price:", repr(res.entry_price))
print("exit_price:", repr(res.exit_price))
print("shares:", repr(res.shares))
print("bars_held:", res.bars_held)
print("entry_ts:", res.entry_timestamp)
print("exit_ts:", res.exit_timestamp)
print("pnl:", repr(res.pnl))
print("hedge_pnl:", repr(res.hedge_pnl))
print("hedge_side:", res.hedge_side, "size:", repr(res.hedge_size),
      "entry:", repr(res.hedge_entry), "exit:", repr(res.hedge_exit))
print("rebound_short_pnl:", repr(res.rebound_short_pnl))
print("rebound_hedge_pnl:", repr(res.rebound_hedge_pnl))
print("rebound_hedge_side:", res.rebound_hedge_side, "size:", repr(res.rebound_hedge_size),
      "entry:", repr(res.rebound_hedge_entry), "exit:", repr(res.rebound_hedge_exit))
print("total_pnl:", repr(res.total_pnl))
print("max_live_coin_notional:", repr(res.max_live_coin_notional))
print("trades:")
for t in res.trades:
    print("  ", t)

# Check long-leg hedge presence
coin_position_value = 100.15 * SHARES  # approx entry_px * shares
long_hedge_value = compute_eth_hedge_size(COIN[:7], ETH[:7], coin_position_value, _cfg(RATE))
print("\nlong_hedge_value (approx):", long_hedge_value)