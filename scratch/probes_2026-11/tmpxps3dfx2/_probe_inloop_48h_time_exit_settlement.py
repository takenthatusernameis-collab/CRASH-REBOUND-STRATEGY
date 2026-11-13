"""Probe: in-loop 48h TIME_EXIT × aligned long ETH hedge × cap-cut shares ×
commission_min × entry_next_bar with a REAL DailyRiskState to derive exact
settlement parity and funding-on/off delta for the new regression lock.

Run: PYTHONPATH=. python3 _probe_inloop_48h_time_exit_settlement.py
"""
from __future__ import annotations

from src.backtest.engine import backtest_simple, _apply_funding_pnl
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal, compute_eth_hedge_size
from src.strategy.risk import DailyRiskState


def _c(ts, o, h, l, cl, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": cl, "volume": v}


RATE = 0.01  # pct per hour
SLIP = 0.001
COMM_MIN = 0.5
SHARES = 10.0  # cap-cut shares


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


def build():
    n = 120
    coin = [_c(f"2025-01-01T{i:02d}:00:00", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
    coin[6] = _c("2025-01-01T06:00:00", 100.0, 100.5, 99.5, 100.0)
    coin[7] = _c("2025-01-01T07:00:00", 100.0, 110.0, 99.5, 109.0)
    for i in range(8, n):
        coin[i] = _c(f"2025-01-01T{i:02d}:00:00", 108.0, 115.0, 100.0, 107.0)
    eth = [_c(f"2025-01-01T{i:02d}:00:00", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
    eth[6] = _c("2025-01-01T06:00:00", 2000.0, 2010.0, 1990.0, 2000.0)
    eth[7] = _c("2025-01-01T07:00:00", 2000.0, 2030.0, 1995.0, 2025.0)
    for i in range(8, n):
        eth[i] = _c(f"2025-01-01T{i:02d}:00:00", 2030.0, 2050.0, 2020.0, 2040.0)
    eth[55] = _c("2025-01-01T55:00:00", 2030.0, 2055.0, 2020.0, 2045.0)
    return coin, eth


def main():
    coin, eth = build()
    rs_on = DailyRiskState()
    on = backtest_simple(coin, _sig(), config=_cfg(RATE), eth_candles=eth, risk_state=rs_on)
    off = backtest_simple(coin, _sig(), config=_cfg(0.0), eth_candles=eth)

    print("== in-loop 48h TIME_EXIT (aligned ETH present at exit idx 55) ==")
    print("exit_reason:", on.exit_reason)
    print("exit_timestamp:", on.exit_timestamp, "bars_held:", on.bars_held)
    print("trades:", [(t["side"], t["reason"], t["entry"], t["exit"], t["pnl"]) for t in on.trades])
    print("long entry/exit/pnl:", on.entry_price, on.exit_price, on.pnl)
    print("short entry/exit/pnl:", on.rebound_short_pnl)
    print("hedge side/size/entry/exit:", on.rebound_hedge_side, on.rebound_hedge_size,
          on.rebound_hedge_entry, on.rebound_hedge_exit)
    print("rebound_hedge_pnl:", on.rebound_hedge_pnl, "hedge_pnl:", on.hedge_pnl)
    print("total_pnl:", on.total_pnl)
    print("max_live_coin_notional:", on.max_live_coin_notional)
    print()
    print("== risk_state settlement (REAL DailyRiskState) ==")
    print("open_positions:", rs_on.open_positions)
    print("gross_exposure:", rs_on.gross_exposure)
    print("open_position_notionals:", rs_on.open_position_notionals)
    print("realized_pnl:", rs_on.realized_pnl)
    print()
    print("== funding parity ==")
    delta = on.total_pnl - off.total_pnl
    print("delta on/off:", delta)
    print("off.total_pnl:", off.total_pnl)
    print()
    # Hand-trace decomposition
    long_leg, short_leg = on.trades
    print("== hand-trace ==")
    print("long_leg pnl:", long_leg["pnl"])
    print("short_leg pnl:", short_leg["pnl"])
    print("coin_total:", long_leg["pnl"] + short_leg["pnl"])
    print("total_pnl == coin_total + hedge_pnl:", on.total_pnl, long_leg["pnl"] + short_leg["pnl"] + on.hedge_pnl)
    print("realized_pnl == coin_total + hedge_pnl (in-loop credits hedge):", rs_on.realized_pnl,
          long_leg["pnl"] + short_leg["pnl"] + on.hedge_pnl)
    print("realized_pnl == coin_total only:", rs_on.realized_pnl, long_leg["pnl"] + short_leg["pnl"])


if __name__ == "__main__":
    main()