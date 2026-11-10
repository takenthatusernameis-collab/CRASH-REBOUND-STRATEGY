"""Probe #3 uncovered combo: rebound short 48h boundary + ETH divergence +
cap-cut + commission_min. Derives expected values by tracing engine math.
"""
import sys
sys.path.insert(0, '.')
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.strategy.risk import RiskState

ENTRY_PX = 100.0
SHARES = 1000.0
RATE = 0.01  # 0.01%/hour
SIGNAL_IDX = 5
COMM_MIN = 1.0


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _coin(n):
    return [_c(f"2025-01-01T{i:02d}:00:00", 100 + i % 3, 102 + i % 3, 98 + i % 3, 100 + i % 3) for i in range(n)]


def _eth(n):
    return [_c(f"2025-01-01T{i:02d}:00:00", 2000 + i % 5, 2005 + i % 5, 1995 + i % 5, 2000 + i % 5) for i in range(n)]


def _sig():
    return Signal(symbol="T", side="long", reason="t", entry_price=ENTRY_PX, stop_price=50.0,
                  target_price=109.0, risk_per_share=1.0, timestamp="2025-01-01T05:00:00",
                  size_shares=SHARES, signal_index=SIGNAL_IDX)


def _base(**kw):
    d = dict(enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=False,
             avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
             commission_min=COMM_MIN, funding_rate_pct_per_hour=RATE, min_daily_volume_usd=0.0,
             time_exit_max_bars=1000, enable_liquidation_checks=False,
             rebound_short_time_exit_bars=48)
    d.update(kw)
    return StrategyConfig(**d)


# --- CASE B: cap-cut + commission_min + ETH divergence + 48h boundary ---
# Pre-existing 100000 + new 100000 (shares=1000 @100) = 200000 > cap 120000
# -> equal share 60000 each. new_notional_cut = min(60000, 100000) = 60000 -> shares=600.
rs = RiskState()
rs.apply_trade("2025-01-01T00:00:00", 0.0, opened=True, closed=False, notional=100000.0)

candles = _coin(60)
candles[6] = _c("2025-01-01T06:00:00", 100.0, 110.0, 99.0, 109.0)
for i in range(7, 60):
    candles[i] = _c(f"2025-01-01T{i:02d}:00:00", 109.0, 110.0, 108.0, 109.0)
eth = _eth(60)
for i in range(7, 60):
    eth[i] = _c(f"2025-01-01T{i:02d}:00:00", 2000 + (i - 7), 2005 + (i - 7), 1995 + (i - 7), 2000 + (i - 7))

res = backtest_simple(candles, _sig(), config=_base(), eth_candles=eth, risk_state=rs)
print("=== CASE B: cap-cut + commission_min + ETH divergence + 48h boundary ===")
print("exit_reason:", res.exit_reason)
print("shares:", res.shares)
print("total_pnl:", res.total_pnl)
print("rebound_short_pnl:", res.rebound_short_pnl)
print("rebound_hedge_pnl:", res.rebound_hedge_pnl)
print("rebound_hedge_side:", res.rebound_hedge_side)
print("rebound_hedge_size:", res.rebound_hedge_size)
print("rebound_hedge_entry:", res.rebound_hedge_entry)
print("rebound_hedge_exit:", res.rebound_hedge_exit)
print("trades:", res.trades)
print("risk_state gross_exposure:", rs.gross_exposure, "open_position_notionals:", rs.open_position_notionals)
