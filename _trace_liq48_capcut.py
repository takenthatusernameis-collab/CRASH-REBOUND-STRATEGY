"""TRACE PROBE (throwaway): rebound-short LIQUIDATION on exact 48th held bar
UNDER cap_cut (existing position 80k) + commission_min + entry_next_bar + aligned ETH.

short_start_idx = 8. 48th held bar: sidx - 8 + 1 == 48 => sidx = 55.
"""
from __future__ import annotations
from types import SimpleNamespace
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


class _RS:
    open_positions = 1
    gross_exposure = 80000.0
    open_position_notionals = [80000.0]

    def check_position(self, config, capital, shares, entry_price):
        return SimpleNamespace(allowed=True, size_shares=shares)

    def apply_cap_cuts(self, capital, config, open_notional=None):
        capv = capital * config.gross_cap_pct / 100.0
        n = len(open_notional or [])
        return [capv / n] * n if n else []

    def apply_trade(self, *a, **k):
        pass


def build():
    n = 80
    coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)   # long entry_next_bar fill
    coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)   # long target -> rebound short opens
    for i in range(9, n):
        coin[i] = _c(f"s{i}", 108.0, 115.0, 100.0, 107.0)
    coin[55] = _c("b55", 108.0, 120.0, 100.5, 107.0)  # liq on 48th held bar

    eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
    eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
    eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)  # rebound hedge entry idx 8
    for i in range(9, n):
        eth[i] = _c(f"eh{i}", 2030.0, 2050.0, 2020.0, 2040.0)
    eth[55] = _c("eh55", 2030.0, 2055.0, 2020.0, 2045.0)

    cfg = StrategyConfig(
        enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=1.0, funding_rate_pct_per_hour=0.01,
        min_daily_volume_usd=0.0, time_exit_max_bars=200,
        enable_liquidation_checks=True, liquidation_maint_margin_pct=5.0,
        liquidation_buffer_pct=1.0, liquidation_penalty_pct=0.5, gross_cap_pct=120.0,
        rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
    )
    sig = Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                 stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                 timestamp="t5", size_shares=1000.0, signal_index=5)
    return coin, eth, cfg, sig


if __name__ == "__main__":
    coin, eth, cfg, sig = build()
    res = backtest_simple(coin, sig, config=cfg, risk_state=_RS(),
                          capital=100000.0, eth_candles=eth)
    print("exit_reason=", res.exit_reason)
    print("exit_timestamp=", res.exit_timestamp, "bars_held=", res.bars_held)
    for t in res.trades:
        print("  trade", t)
    print("shares=", res.shares, "entry_price=", res.entry_price)
    print("rebound_hedge_side=", res.rebound_hedge_side)
    print("rebound_hedge_size=", res.rebound_hedge_size)
    print("rebound_hedge_entry=", res.rebound_hedge_entry)
    print("rebound_hedge_exit=", res.rebound_hedge_exit)
    print("rebound_hedge_pnl=", res.rebound_hedge_pnl)
    print("hedge_pnl=", res.hedge_pnl)
    print("max_live_coin_notional=", res.max_live_coin_notional)
    print("total_pnl=", res.total_pnl)
    print("rs.open_position_notionals=", _RS.open_position_notionals)