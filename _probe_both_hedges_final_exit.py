"""Probe: can we get BOTH long-leg short ETH hedge AND rebound-leg long ETH hedge
in a final-exit (loop-else) path under cap_cut+commission_min+entry_next_bar?

Goal: design a fixture where compute_eth_hedge_size > 0 at long entry AND at
rebound entry, loop exhausts (no in-loop break), and assert full traced values.
"""
import math

from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal, compute_eth_hedge_size
from src.strategy.risk import DailyRiskState


def _c(ts, o, h, l, cl, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": cl, "volume": v}


def _close_to(x, y, tol=1e-9):
    return math.isclose(float(x), float(y), rel_tol=0.0, abs_tol=tol)


RATE = 0.01
SLIP = 0.001
COMM_MIN = 0.5
SHARES = 10.0

# 12 bars 0..11.
# idx 5: signal bar
# idx 6: long entry bar (entry_next_bar=True, open=100.0)
# idx 7: long target hit (high=110 >= target 109) -> long closes, rebound short opens
# idx 8..11: rebound short stays open, loop exhausts -> FINAL EXIT at idx 11 close=108.0
COIN = [_c(f"2025-01-01T{i:02d}:00:00", 100.0, 101.0, 99.0, 100.0) for i in range(12)]
COIN[7] = _c("2025-01-01T07:00:00", 100.0, 110.0, 99.0, 109.0)
for i in range(8, 12):
    COIN[i] = _c(f"2025-01-01T{i:02d}:00:00", 108.0, 112.0, 105.0, 108.0)

# ETH with strong variation so BOTH hedges size > 0.
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
        symbol="T",
        side="long",
        reason="t",
        entry_price=100.0,
        stop_price=50.0,
        target_price=109.0,
        risk_per_share=1.0,
        timestamp="2025-01-01T05:00:00",
        size_shares=SHARES,
        signal_index=5,
    )


# Check hedge sizing at long entry (start_idx=6, hedge_hist_end=7)
cfg = _cfg()
long_coin_value = 100.15 * SHARES
long_hedge_value = compute_eth_hedge_size(COIN[:7], ETH[:7], long_coin_value, cfg)
print("LONG-LEG hedge value:", long_hedge_value)

# Check hedge sizing at rebound entry (idx=7, r_hist_end=8)
short_entry_px = 108.84533216349999  # approx from existing test
short_coin_value = short_entry_px * SHARES
reb_hedge_value = compute_eth_hedge_size(COIN[:8], ETH[:8], short_coin_value, cfg)
print("REBOUND-LEG hedge value:", reb_hedge_value)

res = backtest_simple(COIN, _sig(), config=_cfg(RATE), eth_candles=ETH)
print("exit_reason:", res.exit_reason)
print("hedge_side:", res.hedge_side, "hedge_size:", res.hedge_size)
print("rebound_hedge_side:", res.rebound_hedge_side, "rebound_hedge_size:", res.rebound_hedge_size)
print("hedge_pnl:", res.hedge_pnl, "rebound_hedge_pnl:", res.rebound_hedge_pnl)
print("total_pnl:", res.total_pnl)
print("pnl:", res.pnl, "rebound_short_pnl:", res.rebound_short_pnl)
print("trades:", res.trades)
print("max_live_coin_notional:", res.max_live_coin_notional)