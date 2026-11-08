"""B-rem8 probe (2026-11-08): compute exact engine values for rebound-short
liquidation/stop on the exact 48th held bar (sidx=55, short_start_idx=8).

Sequencing under test: liquidation > stop > target > time-exit, evaluated BEFORE
the 48h boundary time-exit check. A liquidation or stop hit on the 48th held bar
must win over time-exit with 48h hourly funding on coin short + ETH hedge long.
"""
from __future__ import annotations

from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


class _NoCutRS:
    def check_position(self, config, capital, shares, entry_price):
        from types import SimpleNamespace
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
        enable_liquidation_checks=True, liquidation_maint_margin_pct=5.0,
        liquidation_buffer_pct=1.0, liquidation_penalty_pct=0.5, gross_cap_pct=120.0,
        rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
    )


def _base(coin_b55, eth_b55):
    n = 80
    coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
    coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)
    for i in range(9, n):
        coin[i] = _c(f"s{i}", 108.0, 115.0, 100.0, 107.0)
    coin[55] = coin_b55
    eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
    eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
    eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)
    for i in range(9, n):
        eth[i] = _c(f"eh{i}", 2030.0, 2050.0, 2020.0, 2040.0)
    eth[55] = eth_b55
    return coin, eth


def _sig():
    return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                  stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                  timestamp="t5", size_shares=1000.0, signal_index=5)


def _probe(name, coin_b55, eth_b55):
    coin, eth = _base(coin_b55, eth_b55)
    res = backtest_simple(coin, _sig(), config=_cfg(), risk_state=_NoCutRS(),
                          capital=100000.0, eth_candles=eth)
    print(f"=== {name} ===")
    print(f"  exit_reason            : {res.exit_reason}")
    print(f"  exit_timestamp         : {res.exit_timestamp}")
    print(f"  bars_held              : {res.bars_held}")
    print(f"  trades                 : {[(t['reason'], t['entry'], t['exit'], t['pnl']) for t in res.trades]}")
    print(f"  short leg entry/exit   : {res.trades[1]['entry']} / {res.trades[1]['exit']}")
    print(f"  short pnl              : {res.trades[1]['pnl']}")
    print(f"  rebound_hedge_side     : {res.rebound_hedge_side}")
    print(f"  rebound_hedge_size     : {res.rebound_hedge_size}")
    print(f"  rebound_hedge_entry    : {res.rebound_hedge_entry}")
    print(f"  rebound_hedge_exit     : {res.rebound_hedge_exit}")
    print(f"  rebound_hedge_pnl      : {res.rebound_hedge_pnl}")
    print(f"  hedge_pnl              : {res.hedge_pnl}")
    print(f"  max_live_coin_notional : {res.max_live_coin_notional}")
    print(f"  total_pnl              : {res.total_pnl}")
    print()


if __name__ == "__main__":
    # short_entry ~108.99909; liq threshold = entry*(1+0.06)=115.5395; stop=152.599; target=99.190
    # B-rem8a: LIQUIDATION on 48th bar (high >= 115.5395, low > 99.19, high < 152.599)
    _probe("B-rem8a LIQUIDATION on 48th bar",
           _c("b55", 108.0, 116.0, 100.5, 107.0),
           _c("eh55", 2030.0, 2055.0, 2020.0, 2045.0))
    # B-rem8b: STOP on 48th bar (high >= 152.599, low > 99.19)
    _probe("B-rem8b STOP on 48th bar",
           _c("b55", 108.0, 153.0, 100.5, 107.0),
           _c("eh55", 2030.0, 2055.0, 2020.0, 2045.0))