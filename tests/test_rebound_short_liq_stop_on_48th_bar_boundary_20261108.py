"""B-rem8 regression lock (2026-11-08): rebound short liquidation/stop on the exact 48th held bar.

Spec: "close short at -9% (profit target) OR after 48 hours at latest"
(crash-rebound-strategy.pdf / strategy_spec.md).

Engine semantics (locked here): on the 48th held bar of the rebound short
(`sidx - short_start_idx + 1 == 48`), exit checks evaluate in order
liquidation > stop > target > time-exit. A liquidation or stop reached on
that same 48th bar must exit as `liquidated`/`stopped` (not `time_exit`),
with correct funding for 48 hours, ETH hedge exit on that bar, commission_min,
and entry_next_bar.

Hourly engine only; synthetic fixture (non-evidence); no look-ahead.
"""
from __future__ import annotations

import unittest

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


class TestReboundShortLiqStopOn48thBarBoundary(unittest.TestCase):
    def _base_setup(self):
        """Common setup: long at idx 6, long target at idx 8 -> rebound short opens at idx 8.
        short_start_idx = 8. 48th held bar: sidx - 8 + 1 == 48 => sidx = 55.
        """
        n = 80
        coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
        coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)    # entry_next_bar long fill
        coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)    # long target -> rebound short opens
        for i in range(9, n):
            coin[i] = _c(f"s{i}", 108.0, 115.0, 100.0, 107.0)
        return coin

    def _eth_base(self):
        n = 80
        eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
        eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
        eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)    # rebound hedge entry idx 8
        for i in range(9, n):
            eth[i] = _c(f"eh{i}", 2030.0, 2050.0, 2020.0, 2040.0)
        return eth

    def _cfg_liq(self):
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

    def _cfg_stop(self):
        return StrategyConfig(
            enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
            avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
            commission_min=1.0, funding_rate_pct_per_hour=0.01,
            min_daily_volume_usd=0.0, time_exit_max_bars=200,
            enable_liquidation_checks=False, gross_cap_pct=120.0,
            rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
            rebound_short_time_exit_bars=48,
        )

    def _sig(self):
        return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                      stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                      timestamp="t5", size_shares=1000.0, signal_index=5)

    def test_rebound_short_liquidation_on_48th_bar_beats_time_exit(self):
        """LIQUIDATION on exact 48th held bar (sidx=55) wins over 48h time-exit."""
        coin = self._base_setup()
        # 48th held bar (sidx=55): high=120.0 triggers liq (threshold ~115.54), low=100.5 > target (99.19)
        coin[55] = _c("b55", 108.0, 120.0, 100.5, 107.0)

        eth = self._eth_base()
        eth[55] = _c("eh55", 2030.0, 2055.0, 2020.0, 2045.0)  # hedge exit on 48th bar

        cfg = self._cfg_liq()
        sig = self._sig()

        res = backtest_simple(coin, sig, config=cfg, risk_state=_NoCutRS(),
                              capital=100000.0, eth_candles=eth)

        # Overall exit_reason is target_rebound_short (long leg hit target at idx 8),
        # but short leg reason must be 'liquidated' (NOT time_exit)
        self.assertEqual(res.exit_reason, "target_rebound_short")
        self.assertEqual(len(res.trades), 2)
        self.assertEqual(res.trades[0]["reason"], "target")   # long leg
        self.assertEqual(res.trades[1]["reason"], "liquidated")  # short leg
        self.assertEqual(res.exit_timestamp, "b55")
        # bars_held = short_exit_idx(55) - long_start_idx(6) + 1 = 50
        self.assertEqual(res.bars_held, 50)

        short_leg = res.trades[1]
        # short_entry ~108.99909, liq at high=120.0 -> exit=120.001 (slippage=0, commission_min=1.0)
        self.assertAlmostEqual(short_leg["entry"], 108.99909, places=5)
        self.assertAlmostEqual(short_leg["exit"], 120.001, places=5)
        # 48 hours of funding on short (sidx=55, short_start=8 => 48h)
        # short pnl = (entry - exit) * shares - penalty + funding_benefit
        # penalty = 0.5% * notional; funding_benefit = notional * 0.01% * 48
        self.assertAlmostEqual(short_leg["pnl"], -11023.709818000008, places=3)

        self.assertEqual(res.rebound_hedge_side, "long")
        self.assertAlmostEqual(res.rebound_hedge_size, 163.498635, places=6)
        self.assertAlmostEqual(res.rebound_hedge_entry, 2000.0061162590134, places=9)
        self.assertAlmostEqual(res.rebound_hedge_exit, 2044.9938837409866, places=9)
        self.assertAlmostEqual(res.rebound_hedge_pnl, 5785.846878999997, places=6)
        self.assertAlmostEqual(res.hedge_pnl, res.rebound_hedge_pnl, places=9)
        self.assertAlmostEqual(res.max_live_coin_notional, 108999.09, places=6)
        coin_total = sum(t["pnl"] for t in res.trades)
        self.assertAlmostEqual(coin_total, -2054.6201180000135, places=3)
        self.assertAlmostEqual(res.total_pnl, coin_total + res.hedge_pnl, places=6)
        self.assertAlmostEqual(res.total_pnl, 3731.2267609999835, places=3)

    def test_rebound_short_stop_on_48th_bar_beats_time_exit(self):
        """STOP on exact 48th held bar (sidx=55) wins over 48h time-exit."""
        coin = self._base_setup()
        # 48th held bar (sidx=55): high=152.599 triggers stop (threshold ~152.5987), low=100.5 > target (99.19)
        coin[55] = _c("b55", 108.0, 152.599, 100.5, 107.0)

        eth = self._eth_base()
        eth[55] = _c("eh55", 2030.0, 2055.0, 2020.0, 2045.0)  # hedge exit on 48th bar

        cfg = self._cfg_stop()
        sig = self._sig()

        res = backtest_simple(coin, sig, config=cfg, risk_state=_NoCutRS(),
                              capital=100000.0, eth_candles=eth)

        self.assertEqual(res.exit_reason, "target_rebound_short")
        self.assertEqual(len(res.trades), 2)
        self.assertEqual(res.trades[0]["reason"], "target")   # long leg
        self.assertEqual(res.trades[1]["reason"], "stopped")  # short leg
        self.assertEqual(res.exit_timestamp, "b55")
        self.assertEqual(res.bars_held, 50)

        short_leg = res.trades[1]
        # short_entry ~108.99909, stop at ~152.5987 -> exit=152.599726 (slippage=0, commission_min=1.0)
        self.assertAlmostEqual(short_leg["entry"], 108.99909, places=5)
        self.assertAlmostEqual(short_leg["exit"], 152.59972599999998, places=5)
        # 48 hours of funding on short (sidx=55, short_start=8 => 48h)
        self.assertAlmostEqual(short_leg["pnl"], -43077.440367999974, places=3)

        self.assertEqual(res.rebound_hedge_side, "long")
        self.assertAlmostEqual(res.rebound_hedge_size, 163.498635, places=6)
        self.assertAlmostEqual(res.rebound_hedge_entry, 2000.0061162590134, places=9)
        self.assertAlmostEqual(res.rebound_hedge_exit, 2044.9938837409866, places=9)
        self.assertAlmostEqual(res.rebound_hedge_pnl, 5785.846878999997, places=6)
        self.assertAlmostEqual(res.hedge_pnl, res.rebound_hedge_pnl, places=9)
        self.assertAlmostEqual(res.max_live_coin_notional, 108999.09, places=6)
        coin_total = sum(t["pnl"] for t in res.trades)
        self.assertAlmostEqual(coin_total, -34108.35066799998, places=3)
        self.assertAlmostEqual(res.total_pnl, coin_total + res.hedge_pnl, places=6)
        self.assertAlmostEqual(res.total_pnl, -28322.50378899998, places=3)


if __name__ == "__main__":
    unittest.main()