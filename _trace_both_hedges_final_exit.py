"""Trace both-hedges final-exit fixture to hand-derive expected values."""
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

COIN = []
for i in range(7):
    cl = 100.0 * (1.0 + (0.03 if i % 2 else -0.03))
    COIN.append(_c(f"2025-01-01T{i:02d}:00:00", cl * 0.99, cl * 1.02, cl * 0.98, cl))
COIN.append(_c("2025-01-01T07:00:00", 100.0, 110.0, 99.0, 109.0))
for i in range(8, 12):
    COIN.append(_c(f"2025-01-01T{i:02d}:00:00", 108.0, 112.0, 105.0, 108.0))

ETH = []
for i in range(12):
    px = 2000.0 + (i % 2) * 100.0
    ETH.append(_c(f"2025-01-01T{i:02d}:00:00", px, px + 20.0, px - 20.0, px + 50.0 * (i % 3 - 1)))
for i in range(8, 12):
    ETH[i] = _c(f"2025-01-01T{i:02d}:00:00", 2100.0, 2120.0, 2080.0, 2110.0)


def _cfg(rate=RATE):
    return StrategyConfig(
        enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
        avoid_downtrend=False, slippage_pct=SLIP, commission_per_share=0.0,
        commission_min=COMM_MIN, funding_rate_pct_per_hour=rate,
        min_daily_volume_usd=0.0, time_exit_max_bars=50,
        rebound_short_time_exit_bars=100, enable_liquidation_checks=False,
    )


def _sig():
    return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                  stop_price=50.0, target_price=109.0, risk_per_share=1.0,
                  timestamp="2025-01-01T05:00:00", size_shares=SHARES, signal_index=5)


cfg = _cfg(RATE)
res = backtest_simple(COIN, _sig(), config=cfg, eth_candles=ETH)
for attr in ["exit_reason","entry_price","exit_price","shares","bars_held","entry_timestamp",
             "exit_timestamp","pnl","hedge_pnl","hedge_side","hedge_size","hedge_entry",
             "hedge_exit","rebound_short_pnl","rebound_hedge_pnl","rebound_hedge_side",
             "rebound_hedge_size","rebound_hedge_entry","rebound_hedge_exit","total_pnl",
             "max_live_coin_notional"]:
    print(f"{attr} = {repr(getattr(res, attr))}")
print("trades:")
for t in res.trades:
    print("  ", t)

rs_on = DailyRiskState()
on = backtest_simple(COIN, _sig(), config=cfg, eth_candles=ETH, risk_state=rs_on)
off = backtest_simple(COIN, _sig(), config=_cfg(0.0), eth_candles=ETH)
print("---risk_state---")
print("open_positions:", rs_on.open_positions, "gross_exposure:", rs_on.gross_exposure)
print("open_position_notionals:", rs_on.open_position_notionals)
print("realized_pnl:", repr(rs_on.realized_pnl))
print("delta:", repr(on.total_pnl - off.total_pnl))
print("on.rebound_hedge_size:", repr(on.rebound_hedge_size))
print("on.hedge_size:", repr(on.hedge_size))