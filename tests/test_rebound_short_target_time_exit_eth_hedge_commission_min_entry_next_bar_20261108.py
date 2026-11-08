"""B-rem regression lock (2026-11-08): rebound short TARGET (-9%) and 48h
TIME-EXIT under ETH hedge + commission_min + entry_next_bar.

Covers the highest remaining unlocked Priority B path from HANDOFF. Failing-
tests-first derivation with concrete expected values against current engine.

Spec non-negotiables locked:
- Rebound short target anchored to executed short entry (-9%, slippage/
  commission-aware): short opens from long target-bar exit context; target is
  short_entry * (1 - 9%).
- Rebound short 48h time-exit: no target/stop/liquidation for 48 bars after
  rebound short entry => exit at short_start_idx + 48 (sidx-start+1 >= 48).
- ETH hedge (long) for rebound short leg, entry aligned to rebound-entry bar
  idx (no look-ahead), sized from aligned history, hourly funding on hedge long.
- Hourly funding on coin short leg for every included bar (liquidation disabled
  so funding/path attribution is isolated; funding semantics verified).
- commission_min applied on all fills (long entry/exit, short entry/exit, hedge
  entry/exit).
- entry_next_bar re-anchor for long leg; rebound short shares/notional tracked
  via max_live_coin_notional.
- Stopped buy never opens rebound short (this path reaches long target).
Synthetic fixtures only (non-evidence); hourly engine only.
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


class TestReboundShortTargetTimeExitEthHedgeCommissionMinEntryNextBar(unittest.TestCase):
    def _cfg(self, **ov):
        d = dict(
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
        d.update(ov)
        return StrategyConfig(**d)

    def _sig(self):
        return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                      stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                      timestamp="t5", size_shares=1000.0, signal_index=5)

    def test_rebound_short_target_minus9_with_eth_hedge_commission_min_entry_next_bar(self):
        n = 80
        coin = [_c(f"b{i}", 100.0, 101.0, 99.0, 100.0) for i in range(n)]
        coin[6] = _c("e6", 100.0, 100.5, 99.0, 100.0)    # entry_next_bar long fill
        coin[8] = _c("e8", 100.0, 110.0, 99.0, 109.0)    # long target -> rebound short opens
        coin[10] = _c("e10", 108.0, 109.0, 98.0, 107.0)  # rebound short -9% target hit (low <= target)
        eth = [_c(f"e{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
        eth[6] = _c("e6", 2000.0, 2010.0, 1990.0, 2000.0)
        eth[8] = _c("e8", 2000.0, 2030.0, 1995.0, 2025.0)    # rebound hedge entry aligned to idx 8
        eth[10] = _c("e10", 2040.0, 2060.0, 2030.0, 2050.0)  # rebound hedge exit on target bar

        res = backtest_simple(coin, self._sig(), config=self._cfg(),
                              risk_state=_NoCutRS(), capital=100000.0, eth_candles=eth)

        self.assertEqual(res.exit_reason, "target_rebound_short")
        self.assertEqual(len(res.trades), 2)
        long_leg, short_leg = res.trades
        self.assertEqual(long_leg["reason"], "target")
        self.assertEqual(short_leg["reason"], "target")

        # Long: entry_next_bar fill bar 6 open + commission_min; target bar 8.
        self.assertAlmostEqual(long_leg["entry"], 100.001, places=9)
        self.assertAlmostEqual(long_leg["exit"], 109.00009, places=9)
        self.assertAlmostEqual(long_leg["pnl"], 8969.089699999995, places=5)

        # Rebound short: entry anchored to executed long-exit fill context (sell-side
        # commission_min), target = executed short entry * 0.91 (-9%), exit buy-side.
        self.assertAlmostEqual(short_leg["entry"], 108.99909, places=9)
        self.assertAlmostEqual(short_leg["exit"], 99.19017190000001, places=9)
        self.assertAlmostEqual(short_leg["pnl"], 9830.717917999986, places=5)

        # Rebound hedge (long ETH): sized from aligned history, entry at bar idx 8
        # (no look-ahead), commission_min on both fills, hourly funding on long hedge.
        self.assertEqual(res.rebound_hedge_side, "long")
        self.assertAlmostEqual(res.rebound_hedge_size, 163.498635, places=6)
        self.assertAlmostEqual(res.rebound_hedge_entry, 2000.0061162590134, places=9)
        self.assertAlmostEqual(res.rebound_hedge_exit, 1999.9938837409866, places=9)
        self.assertAlmostEqual(res.rebound_hedge_pnl, -67.39965400000271, places=6)
        self.assertAlmostEqual(res.hedge_pnl, -67.39965400000271, places=6)

        # Reservation/notional tracks executed rebound short.
        self.assertAlmostEqual(res.max_live_coin_notional, 108999.09, places=6)

        coin_total = sum(t["pnl"] for t in res.trades)
        self.assertAlmostEqual(coin_total, 18799.80761799998, places=5)
        self.assertAlmostEqual(res.total_pnl, 18732.407963999976, places=5)
        self.assertAlmostEqual(res.total_pnl, coin_total + res.hedge_pnl, places=6)

    def test_rebound_short_48h_time_exit_with_eth_hedge_commission_min_entry_next_bar(self):
        n = 120
        coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
        coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)    # entry_next_bar long fill
        coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)    # long target -> rebound short opens
        # short_entry ~108.99909, target ~99.189, stop ~152.599: keep in bounds for 48 bars.
        for i in range(9, n):
            coin[i] = _c(f"s{i}", 108.0, 115.0, 100.0, 107.0)
        eth = [_c(f"e{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
        eth[6] = _c("e6", 2000.0, 2010.0, 1990.0, 2000.0)
        eth[8] = _c("e8", 2000.0, 2030.0, 1995.0, 2025.0)    # rebound hedge entry idx 8
        for i in range(9, n):
            eth[i] = _c(f"eh{i}", 2030.0, 2050.0, 2020.0, 2040.0)
        eth[56] = _c("eh56", 2030.0, 2055.0, 2020.0, 2045.0)  # 48h exit bar (8+48=56)

        res = backtest_simple(coin, self._sig(), config=self._cfg(),
                              risk_state=_NoCutRS(), capital=100000.0, eth_candles=eth)

        self.assertEqual(res.exit_reason, "target_rebound_short")
        self.assertEqual(len(res.trades), 2)
        long_leg, short_leg = res.trades
        self.assertEqual(long_leg["reason"], "target")
        self.assertEqual(short_leg["reason"], "time_exit")
        # 48 bars after short_start_idx=8 => sidx 56 (56-8+1==48), timestamp "s55"
        self.assertEqual(res.exit_timestamp, "s55")
        self.assertEqual(res.bars_held, 50)

        self.assertAlmostEqual(long_leg["entry"], 100.001, places=9)
        self.assertAlmostEqual(long_leg["exit"], 109.00009, places=9)
        self.assertAlmostEqual(long_leg["pnl"], 8969.089699999995, places=5)

        self.assertAlmostEqual(short_leg["entry"], 108.99909, places=9)
        self.assertAlmostEqual(short_leg["exit"], 107.001, places=9)
        self.assertAlmostEqual(short_leg["pnl"], 2521.2856319999905, places=5)

        self.assertEqual(res.rebound_hedge_side, "long")
        self.assertAlmostEqual(res.rebound_hedge_size, 163.498635, places=6)
        self.assertAlmostEqual(res.rebound_hedge_entry, 2000.0061162590134, places=9)
        self.assertAlmostEqual(res.rebound_hedge_exit, 2039.9938837409866, places=9)
        self.assertAlmostEqual(res.rebound_hedge_pnl, 4968.353703999997, places=5)
        self.assertAlmostEqual(res.hedge_pnl, res.rebound_hedge_pnl, places=9)

        self.assertAlmostEqual(res.max_live_coin_notional, 108999.09, places=6)

        coin_total = sum(t["pnl"] for t in res.trades)
        self.assertAlmostEqual(coin_total, 11490.375331999985, places=5)
        self.assertAlmostEqual(res.total_pnl, 16458.729035999982, places=5)
        self.assertAlmostEqual(res.total_pnl, coin_total + res.hedge_pnl, places=6)


if __name__ == "__main__":
    unittest.main()
