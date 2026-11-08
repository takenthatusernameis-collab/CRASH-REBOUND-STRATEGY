"""B-rem8 probe (throwaway): rebound short LIQUIDATION or STOP on the exact 48th held bar boundary.

Engine semantics: on the 48th held bar (`sidx - short_start_idx + 1 == 48`), exit checks evaluate in
order liquidation > stop > target > time-exit. B-rem7 locked TARGET wins. This probe verifies
LIQUIDATION and STOP also win over time-exit at the boundary with ETH hedge + commission_min +
entry_next_bar + concrete 48h funding/hours. Non-evidence synthetic fixture; probe only.
"""
from __future__ import annotations

import unittest
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


def _build(liquidation_on_48th=False, stop_on_48th=False):
    n = 80
    coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
    coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)
    for i in range(9, n):
        coin[i] = _c(f"s{i}", 108.0, 115.0, 100.0, 107.0)
    if liquidation_on_48th:
        coin[55] = _c("b55", 108.0, 115.4791, 100.0, 107.0)
    elif stop_on_48th:
        coin[55] = _c("b55", 108.0, 152.599, 100.0, 107.0)
    else:
        coin[55] = _c("b55", 108.0, 115.0, 99.0, 107.0)

    eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
    eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
    eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)
    for i in range(9, n):
        eth[i] = _c(f"eh{i}", 2030.0, 2050.0, 2020.0, 2040.0)
    eth[55] = _c("eh55", 2030.0, 2055.0, 2020.0, 2045.0)

    cfg = StrategyConfig(
        enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=1.0, funding_rate_pct_per_hour=0.01,
        min_daily_volume_usd=0.0, time_exit_max_bars=200,
        enable_liquidation_checks=True, gross_cap_pct=120.0,
        rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
    )
    sig = Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                 stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                 timestamp="t5", size_shares=1000.0, signal_index=5)
    return coin, eth, cfg, sig


class TestBrem8Probe(unittest.TestCase):
    def test_report(self):
        for label, liq, stop in [
            ("LIQ on 48th bar", True, False),
            ("STOP on 48th bar", False, True),
            ("TARGET on 48th bar (B-rem7 control)", False, False),
        ]:
            coin, eth, cfg, sig = _build(liq, stop)
            res = backtest_simple(coin, sig, config=cfg, risk_state=_NoCutRS(),
                                  capital=100000.0, eth_candles=eth)
            short_leg = res.trades[1] if len(res.trades) > 1 else None
            print(f"\n=== {label} ===")
            print(f"  exit_reason={res.exit_reason}")
            print(f"  exit_timestamp={res.exit_timestamp}  (expect b55)")
            print(f"  bars_held={res.bars_held}  (expect 50)")
            if short_leg:
                print(f"  short leg reason={short_leg['reason']}")
                print(f"  short entry={short_leg['entry']:.6f} exit={short_leg['exit']:.6f} pnl={short_leg['pnl']:.6f}")
            print(f"  total_pnl={res.total_pnl:.6f}")
            print(f"  max_live_coin_notional={res.max_live_coin_notional:.6f}")


if __name__ == "__main__":
    unittest.main()