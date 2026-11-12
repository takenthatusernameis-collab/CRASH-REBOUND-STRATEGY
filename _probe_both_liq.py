"""Probe: both-hedges + rebound-short liquidation fixture."""
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(ts, o, h, l, cl, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": cl, "volume": v}


SHARES = 10.0
COIN = [_c(f"2025-01-01T{i:02d}:00:00", 100.0, 101.0, 99.0, 100.0) for i in range(15)]
COIN[3] = _c("2025-01-01T03:00:00", 102.0, 105.0, 97.0, 102.0)
COIN[4] = _c("2025-01-01T04:00:00", 100.0, 101.0, 98.0, 100.0)
COIN[5] = _c("2025-01-01T05:00:00", 102.5, 103.0, 102.0, 102.5)
COIN[6] = _c("2025-01-01T06:00:00", 104.0, 105.0, 103.5, 104.0)
COIN[7] = _c("2025-01-01T07:00:00", 106.0, 107.0, 105.5, 106.0)
COIN[8] = _c("2025-01-01T08:00:00", 109.5, 110.0, 109.0, 109.5)
# idx 9: rebound short liquidation (high >= liq threshold, low > target, high < stop)
COIN[9] = _c("2025-01-01T09:00:00", 108.0, 150.0, 107.0, 108.0)
for i in range(10, 15):
    COIN[i] = _c(f"2025-01-01T{i:02d}:00:00", 108.0, 112.0, 105.0, 108.0)

ETH_FULL = [_c(f"2025-01-01T{i:02d}:00:00", 2000.0 + i * 5, 2020.0 + i * 5, 1980.0 + i * 5, 2005.0 + i * 5) for i in range(15)]


def _cfg(rate=0.01):
    return StrategyConfig(
        enable_eth_hedge=True,
        enable_rebound_short=True,
        entry_next_bar=True,
        avoid_downtrend=False,
        slippage_pct=0.001,
        commission_per_share=0.0,
        commission_min=0.5,
        funding_rate_pct_per_hour=rate,
        min_daily_volume_usd=0.0,
        time_exit_max_bars=1000,
        rebound_short_time_exit_bars=48,
        enable_liquidation_checks=True,
        liquidation_maint_margin_pct=5.0,
        liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5,
    )


def _sig():
    return Signal(
        symbol="T", side="long", reason="t", entry_price=100.0,
        stop_price=50.0, target_price=109.0, risk_per_share=1.0,
        timestamp="2025-01-01T03:00:00", size_shares=SHARES, signal_index=3,
    )


res = backtest_simple(COIN, _sig(), config=_cfg(0.01), eth_candles=ETH_FULL)
print("exit_reason:", res.exit_reason)
print("exit_timestamp:", res.exit_timestamp)
print("bars_held:", res.bars_held)
print("entry_price:", res.entry_price)
print("exit_price:", res.exit_price)
print("shares:", res.shares)
print("max_live_coin_notional:", res.max_live_coin_notional)
print("hedge_side:", res.hedge_side, "size:", res.hedge_size, "entry:", res.hedge_entry, "exit:", res.hedge_exit)
print("hedge_pnl:", res.hedge_pnl)
print("rebound_hedge_side:", res.rebound_hedge_side, "size:", res.rebound_hedge_size, "entry:", res.rebound_hedge_entry, "exit:", res.rebound_hedge_exit)
print("rebound_hedge_pnl:", res.rebound_hedge_pnl)
print("rebound_short_pnl:", res.rebound_short_pnl)
print("pnl:", res.pnl, "total_pnl:", res.total_pnl)
print("trades:", res.trades)