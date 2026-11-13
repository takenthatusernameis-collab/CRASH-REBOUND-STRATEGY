"""Scratch trace (not a test, not a handoff) for CELL 4 candidate (a):
hedge-leg funding accrual at the 48h time-exit boundary with aligned ETH.
Run with: PYTHONPATH=. python3 _trace_cell4a.py
"""
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _cfg(rate):
    return StrategyConfig(
        enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=1.0, funding_rate_pct_per_hour=rate,
        min_daily_volume_usd=0.0, time_exit_max_bars=200,
        enable_liquidation_checks=False,
        liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5, gross_cap_pct=120.0,
        rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
    )


def _sig():
    return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                  stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                  timestamp="t5", size_shares=600.0, signal_index=5)


def _coin():
    n = 120
    coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
    coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)
    for i in range(9, n):
        coin[i] = _c(f"s{i}", 108.0, 115.0, 100.0, 107.0)
    eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
    eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
    eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)
    for i in range(9, n):
        eth[i] = _c(f"eh{i}", 2030.0, 2050.0, 2020.0, 2040.0)
    eth[55] = _c("eh55", 2030.0, 2055.0, 2020.0, 2045.0)
    return coin, eth


if __name__ == "__main__":
    coin, eth = _coin()
    sig = _sig()
    on = backtest_simple(coin, sig, config=_cfg(0.01), capital=100000.0, eth_candles=eth)
    off = backtest_simple(coin, sig, config=_cfg(0.0), capital=100000.0, eth_candles=eth)
    print("ON  total_pnl:", on.total_pnl)
    print("OFF total_pnl:", off.total_pnl)
    print("delta total:", on.total_pnl - off.total_pnl)
    print("ON  hedge_pnl:", on.hedge_pnl, "rebound_hedge_pnl:", on.rebound_hedge_pnl)
    print("OFF hedge_pnl:", off.hedge_pnl, "rebound_hedge_pnl:", off.rebound_hedge_pnl)
    print("delta hedge:", on.hedge_pnl - off.hedge_pnl)
    print("delta r-hedge:", on.rebound_hedge_pnl - off.rebound_hedge_pnl)
    print("r-hedge entry:", on.rebound_hedge_entry, "size:", on.rebound_hedge_size)
    print("exit_reason:", on.exit_reason, "bars_held:", on.bars_held)
    print("trades:", [(t["reason"], t["side"], t["pnl"]) for t in on.trades])