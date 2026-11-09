"""2b engine: rebound short STOP and 48h TIME-EXIT × missing-ETH-exit-fallback
× commission_min × cap-cut-implied executed notional (entry_next_bar).

Covers uncovered HANDOFF 2026-11-09T09:45:45Z 2a residual: rebound short
stop/48h terminals where the aligned ETH exit bar exists but close/open are
absent (missing-ETH fallback), under commission_min, in a cap-cut reservation
context (engine receives post-cut share count). commission_min is per-fill with
per-share adjustment (min/shares), so smaller cap-cut share counts materially
change fills/funding/notional vs the 1000-share missing-ETH locks.

Existing locks: stop/48h × hedge-present × commission_min × cap-cut shares
(2026-11-09T09:25:26Z); stop/48h × missing-ETH fallback × commission_min at
1000 shares. This lock uses 600 shares (cap-cut-implied) with concrete
expected values and funding reconciliation.

Spec: hourly funding on every leg/exit path (coin short + hedge long, full held
hours); rebound short stop +40% and 48h time-exit anchored to executed short
entry (slippage/commission-aware); ETH hedge every leg (336h vol ratio, cap 3x),
entry aligned to rebound-entry bar idx (no look-ahead); missing ETH exit bar
falls back to hedge entry for exit accounting with sell-side commission_min
applied; commission_min on all fills; entry_next_bar; liquidation disabled for
isolated path attribution. Synthetic fixtures.
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


class TestReboundShortStop48hMissingEthCommissionMinCapCutShares(unittest.TestCase):
    def _cfg(self):
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

    def _sig(self, shares=600.0):
        # Post-cap-cut share count (portfolio-reservation context).
        return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                      stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                      timestamp="t5", size_shares=shares, signal_index=5)

    def test_rebound_short_stop_missing_eth_exit_commission_min_cap_cut_shares(self):
        n = 30
        coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
        coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)   # long entry_next_bar
        coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)   # long target -> rebound short opens
        # short_entry ~108.998483 (600 shares, commission_min/shares=0.001666..)
        # stop = short_entry*(1+40%) ~152.597876...
        coin[11] = _c("e11", 110.0, 160.0, 109.0, 155.0)  # short stop breached
        eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
        eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
        eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)
        eth[11] = {"timestamp": "h11"}  # missing close/open — aligned bar present

        res = backtest_simple(coin, self._sig(600.0), config=self._cfg(),
                              risk_state=_NoCutRS(), capital=100000.0, eth_candles=eth)

        self.assertEqual(res.exit_reason, "target_rebound_short")
        self.assertEqual([t["reason"] for t in res.trades], ["target", "stopped"])
        long_leg, short_leg = res.trades
        # commission_min/shares = 1/600 = 0.001666... (materially different from 1000-share locks)
        self.assertAlmostEqual(long_leg["entry"], 100.00166666666667, places=9)
        self.assertAlmostEqual(long_leg["exit"], 109.00014999999999, places=9)
        self.assertAlmostEqual(long_leg["pnl"], 5381.089699999996, places=5)

        # Stop anchored to executed short entry (slippage/commission-aware, 600 shares)
        self.assertAlmostEqual(short_leg["entry"], 108.99848333333333, places=9)
        self.assertAlmostEqual(short_leg["exit"], 152.59954333333332, places=9)
        self.assertAlmostEqual(short_leg["pnl"], -26134.476363999995, places=5)

        self.assertEqual(res.rebound_hedge_side, "long")
        self.assertAlmostEqual(res.rebound_hedge_size, 98.098635, places=6)
        self.assertAlmostEqual(res.rebound_hedge_entry, 2000.010193821759, places=9)
        # Missing ETH exit fallback + sell commission_min => 2000.0
        self.assertAlmostEqual(res.rebound_hedge_exit, 2000.0, places=9)
        self.assertAlmostEqual(res.rebound_hedge_pnl, -79.47930799999152, places=6)
        self.assertAlmostEqual(res.hedge_pnl, res.rebound_hedge_pnl, places=9)

        # Authoritative for portfolio reservation: executed rebound-short coin notional.
        self.assertAlmostEqual(res.max_live_coin_notional, 65399.09, places=6)

        coin_total = sum(t["pnl"] for t in res.trades)
        self.assertAlmostEqual(coin_total, -20753.386663999998, places=5)
        self.assertAlmostEqual(res.total_pnl, -20832.86597199999, places=5)
        self.assertAlmostEqual(res.total_pnl, coin_total + res.hedge_pnl, places=6)
        self.assertEqual(res.bars_held, 6)

    def test_rebound_short_48h_time_exit_missing_eth_exit_commission_min_cap_cut_shares(self):
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
        # 48h time-exit triggers at first sidx where (sidx-short_start_idx+1)>=48.
        # short_start_idx=8 => sidx>=55, so exit bar is sidx=55 (timestamp s55).
        eth[55] = {"timestamp": "eh55"}  # missing close/open at actual 48h exit bar

        res = backtest_simple(coin, self._sig(600.0), config=self._cfg(),
                              risk_state=_NoCutRS(), capital=100000.0, eth_candles=eth)

        self.assertEqual(res.exit_reason, "target_rebound_short")
        self.assertEqual([t["reason"] for t in res.trades], ["target", "time_exit"])
        self.assertEqual(res.exit_timestamp, "s55")
        self.assertEqual(res.bars_held, 50)
        long_leg, short_leg = res.trades

        self.assertAlmostEqual(long_leg["entry"], 100.00166666666667, places=9)
        self.assertAlmostEqual(long_leg["exit"], 109.00014999999999, places=9)
        self.assertAlmostEqual(long_leg["pnl"], 5381.089699999996, places=5)

        self.assertAlmostEqual(short_leg["entry"], 108.99848333333333, places=9)
        self.assertAlmostEqual(short_leg["exit"], 107.00166666666667, places=9)
        self.assertAlmostEqual(short_leg["pnl"], 1512.0056319999962, places=5)

        self.assertEqual(res.rebound_hedge_side, "long")
        self.assertAlmostEqual(res.rebound_hedge_size, 98.098635, places=6)
        self.assertAlmostEqual(res.rebound_hedge_entry, 2000.010193821759, places=9)
        # Missing-bar fallback: hedge entry fallback + sell commission_min => 2000.0.
        self.assertAlmostEqual(res.rebound_hedge_exit, 2000.0, places=9)
        self.assertAlmostEqual(res.rebound_hedge_pnl, -942.7516959999915, places=5)
        self.assertAlmostEqual(res.hedge_pnl, res.rebound_hedge_pnl, places=9)

        self.assertAlmostEqual(res.max_live_coin_notional, 65399.09, places=6)

        coin_total = sum(t["pnl"] for t in res.trades)
        self.assertAlmostEqual(coin_total, 6893.095331999992, places=5)
        self.assertAlmostEqual(res.total_pnl, 5950.3436360000005, places=5)
        self.assertAlmostEqual(res.total_pnl, coin_total + res.hedge_pnl, places=6)


if __name__ == "__main__":
    unittest.main()
