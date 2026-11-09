"""Probe: 48h TIME-EXIT × missing-ETH-exit-fallback × commission_min × cap-cut shares (600)."""
from __future__ import annotations
from types import SimpleNamespace
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


class _NoCutRS:
    def check_position(self, config, capital, shares, entry_price):
        return SimpleNamespace(allowed=True, size_shares=shares)

    def apply_cap_cuts(self, capital, config, open_notional=None):
        return []

    def apply_trade(self, *a, **k):
        pass


def _cfg():
    return StrategyConfig(
        enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=1.0, funding_rate_pct_per_hour=0.01,
        min_daily_volume_usd=0.0, time_exit_max_bars=200,
        enable_liquidation_checks=False,
        liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5, gross_cap_pct=120.0,
        rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
    )


def _sig(shares=600.0):
    return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                  stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                  timestamp="t5", size_shares=shares, signal_index=5)


n = 120
coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)
for i in range(9, n):
    coin[i] = _c(f"s{i}", 108.0, 115.0, 100.0, 107.0)
eth = [_c(f"e{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
eth[6] = _c("e6", 2000.0, 2010.0, 1990.0, 2000.0)
eth[8] = _c("e8", 2000.0, 2030.0, 1995.0, 2025.0)
for i in range(9, n):
    eth[i] = _c(f"eh{i}", 2030.0, 2050.0, 2020.0, 2040.0)
# Time exit fires at sidx=55 (short_start_idx 8 + 48 => sidx 55). Place missing
# ETH bar at the actual exit index to trigger the fallback.
eth[55] = {"timestamp": "eh55"}  # missing close/open at time-exit bar

res = backtest_simple(coin, _sig(600.0), config=_cfg(), risk_state=_NoCutRS(),
                      capital=100000.0, eth_candles=eth)
print("=== 48h TIME-EXIT (missing ETH at idx 56, 600 shares) ===")
print("exit_reason:", res.exit_reason)
print("trade reasons:", [t["reason"] for t in res.trades])
print("exit_timestamp:", res.exit_timestamp)
print("bars_held:", res.bars_held)
long_leg, short_leg = res.trades
print("long entry:", repr(long_leg["entry"]))
print("long exit:", repr(long_leg["exit"]))
print("long pnl:", repr(long_leg["pnl"]))
print("short entry:", repr(short_leg["entry"]))
print("short exit:", repr(short_leg["exit"]))
print("short pnl:", repr(short_leg["pnl"]))
print("rebound_hedge_side:", res.rebound_hedge_side)
print("rebound_hedge_size:", repr(res.rebound_hedge_size))
print("rebound_hedge_entry:", repr(res.rebound_hedge_entry))
print("rebound_hedge_exit:", repr(res.rebound_hedge_exit))
print("rebound_hedge_pnl:", repr(res.rebound_hedge_pnl))
print("hedge_pnl:", repr(res.hedge_pnl))
print("max_live_coin_notional:", repr(res.max_live_coin_notional))
coin_total = sum(t["pnl"] for t in res.trades)
print("coin_total:", repr(coin_total))
print("total_pnl:", repr(res.total_pnl))
print("total_pnl == coin_total + hedge_pnl:", abs(res.total_pnl - (coin_total + res.hedge_pnl)) < 1e-9)