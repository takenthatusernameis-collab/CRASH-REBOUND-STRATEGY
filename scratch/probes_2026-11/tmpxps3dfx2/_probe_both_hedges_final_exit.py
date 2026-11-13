"""Trace probe: final-exit (loop-else) path with BOTH long-leg short ETH hedge AND
rebound-long ETH hedge established and funded, under cap_cut + commission_min +
entry_next_bar. Find a fixture where both hedges exist, then hand-trace.
"""
import math
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal, compute_eth_hedge_size

RATE = 0.01
SLIP = 0.001
COMM_MIN = 0.5
SHARES = 10.0


def _c(ts, o, h, l, cl, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": cl, "volume": v}


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
        time_exit_max_bars=1000,
        rebound_short_time_exit_bars=1000,  # > bars until series end -> loop-else final exit
        enable_liquidation_checks=False,
    )


# 12 bars 0..11. Signal idx 4 -> entry_next_bar enters idx 5 open=100.
# Long target 109 hit at idx 7 (high=110). Rebound short opens at idx 7,
# holds idx 8..11, loop exhausts -> FINAL EXIT at idx 11 close.
# Bars 0..4 are a declining crash so the long-leg realized-vol hedge sizes > 0.
COIN = [
    _c("2025-01-01T00:00:00", 100.0, 102.0, 98.0, 100.0),
    _c("2025-01-01T01:00:00", 100.0, 101.0, 96.0, 97.0),
    _c("2025-01-01T02:00:00", 97.0, 98.0, 93.0, 94.0),
    _c("2025-01-01T03:00:00", 94.0, 95.0, 90.0, 91.0),
    _c("2025-01-01T04:00:00", 91.0, 92.0, 87.0, 88.0),   # signal bar
    _c("2025-01-01T05:00:00", 100.0, 104.0, 96.0, 100.0),  # entry bar
    _c("2025-01-01T06:00:00", 100.0, 103.0, 97.0, 100.0),
    _c("2025-01-01T07:00:00", 100.0, 110.0, 99.0, 109.0),  # target hit
    _c("2025-01-01T08:00:00", 108.0, 109.5, 106.5, 108.0),
    _c("2025-01-01T09:00:00", 108.0, 109.5, 106.5, 108.0),
    _c("2025-01-01T10:00:00", 108.0, 109.5, 106.5, 108.0),
    _c("2025-01-01T11:00:00", 108.0, 109.5, 106.5, 108.0),  # final exit
]

# ETH: variation so both hedges size > 0. Aligned 0..11.
ETH = []
for i in range(12):
    px = 2000.0 + (i % 2) * 80.0
    ETH.append(_c(f"2025-01-01T{i:02d}:00:00", px, px + 30.0, px - 30.0, px + 40.0 * (i % 3 - 1)))
for i in range(8, 12):
    ETH[i] = _c(f"2025-01-01T{i:02d}:00:00", 2080.0, 2120.0, 2040.0, 2100.0)


def _sig():
    return Signal(
        symbol="T",
        side="long",
        reason="t",
        entry_price=100.0,
        stop_price=50.0,
        target_price=109.0,
        risk_per_share=1.0,
        timestamp="2025-01-01T04:00:00",
        size_shares=SHARES,
        signal_index=4,
    )


cfg = _cfg()
# Pre-check hedge sizing at long entry (start_idx=5 -> hist end 6, coins[:6], eth[:6])
coin_notional_long = None
# emulate engine entry px
entry_raw = 100.0
comm_ps = max(0.0, COMM_MIN / SHARES)
entry_px = entry_raw + entry_raw * SLIP + comm_ps
coin_notional_long = entry_px * SHARES
hv_long = compute_eth_hedge_size(COIN[:6], ETH[:6], coin_notional_long, cfg)
print("LONG hedge_value:", hv_long, "notional:", coin_notional_long)
if hv_long > 0:
    eth_ref = min(5, len(ETH) - 1)
    print("  eth entry open:", ETH[eth_ref].get('open'))

res = backtest_simple(COIN, _sig(), config=cfg, eth_candles=ETH)
print("exit_reason:", res.exit_reason)
print("entry_price:", res.entry_price)
print("exit_price:", res.exit_price)
print("shares:", res.shares)
print("hedge_side:", res.hedge_side, "hedge_size:", res.hedge_size, "hedge_entry:", res.hedge_entry, "hedge_exit:", res.hedge_exit)
print("rebound_hedge_side:", res.rebound_hedge_side, "rebound_hedge_size:", res.rebound_hedge_size,
      "rebound_hedge_entry:", res.rebound_hedge_entry, "rebound_hedge_exit:", res.rebound_hedge_exit)
print("pnl:", res.pnl, "hedge_pnl:", res.hedge_pnl, "rebound_short_pnl:", res.rebound_short_pnl,
      "rebound_hedge_pnl:", res.rebound_hedge_pnl, "total_pnl:", res.total_pnl)
print("max_live_coin_notional:", res.max_live_coin_notional)
print("bars_held:", res.bars_held, "entry_ts:", res.entry_timestamp, "exit_ts:", res.exit_timestamp)
for t in (res.trades or []):
    print("  trade:", t)