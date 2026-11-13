"""Quick probe (scratch): confirm both-hedges rebound-short TARGET exit path."""
import math
from src.backtest.engine import backtest_simple, _slippage_commission_per_share
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal, compute_eth_hedge_size
from src.strategy.risk import DailyRiskState


def _c(ts, o, h, l, cl, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": cl, "volume": v}


RATE = 0.01
SLIP = 0.001
COMM_MIN = 0.5
SHARES = 10.0

COIN = [_c(f"2025-01-01T{i:02d}:00:00", 100.0, 101.0, 99.0, 100.0) for i in range(15)]
COIN[3] = _c("2025-01-01T03:00:00", 102.0, 105.0, 97.0, 102.0)
COIN[4] = _c("2025-01-01T04:00:00", 100.0, 101.0, 98.0, 100.0)
COIN[5] = _c("2025-01-01T05:00:00", 102.5, 103.0, 102.0, 102.5)
COIN[6] = _c("2025-01-01T06:00:00", 104.0, 105.0, 103.5, 104.0)
COIN[7] = _c("2025-01-01T07:00:00", 106.0, 107.0, 105.5, 106.0)
COIN[8] = _c("2025-01-01T08:00:00", 109.5, 110.0, 109.0, 109.5)  # long target hit
COIN[9] = _c("2025-01-01T09:00:00", 108.0, 110.0, 98.5, 100.0)   # rebound short TARGET hit
for i in range(10, 15):
    COIN[i] = _c(f"2025-01-01T{i:02d}:00:00", 108.0, 112.0, 105.0, 108.0)

ETH_FULL = [_c(f"2025-01-01T{i:02d}:00:00", 2000.0 + i * 5, 2020.0 + i * 5, 1980.0 + i * 5, 2005.0 + i * 5) for i in range(15)]


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
        rebound_short_time_exit_bars=48,
        enable_liquidation_checks=False,
    )


def _sig():
    return Signal(
        symbol="T", side="long", reason="t", entry_price=100.0, stop_price=50.0,
        target_price=109.0, risk_per_share=1.0, timestamp="2025-01-01T03:00:00",
        size_shares=SHARES, signal_index=3,
    )


for elen in (15, 9, 8):
    res = backtest_simple(COIN, _sig(), config=_cfg(RATE), eth_candles=ETH_FULL[:elen])
    print(f"eth_len={elen}: exit_reason={res.exit_reason} bars_held={res.bars_held} "
          f"exit_ts={res.exit_timestamp} pnl={res.pnl} hedge_pnl={res.hedge_pnl} "
          f"short_pnl={res.rebound_short_pnl} rh_pnl={res.rebound_hedge_pnl} "
          f"total={res.total_pnl} max_live={res.max_live_coin_notional}")
    print(f"  entry={res.entry_price} exit={res.exit_price} hedge_sz={res.hedge_size} "
          f"hedge_entry={res.hedge_entry} hedge_exit={res.hedge_exit} "
          f"rh_sz={res.rebound_hedge_size} rh_entry={res.rebound_hedge_entry} rh_exit={res.rebound_hedge_exit}")
    print(f"  trades={res.trades}")