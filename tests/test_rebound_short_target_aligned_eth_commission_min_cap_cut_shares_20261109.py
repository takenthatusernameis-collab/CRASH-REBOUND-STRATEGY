"""Material regression lock (2026-11-09): rebound short TARGET (-9%) ×
commission_min × cap-cut-implied executed shares (600) × ALIGNED ETH hedge exit.

Counterpart to missing-ETH fallback lock
`test_rebound_short_target_missing_eth_commission_min_cap_cut_shares_20261109.py`.
Covers cross-leg boundary: long target closes and opens rebound short under
commission_min with cap-cut share count; rebound hedge entry aligns to rebound
bar (spec no-look-ahead) and exits at ALIGNED ETH bar close/open with sell-side
commission_min; short exits on target (low breach).

Spec: rebound -9% target anchored to executed short entry (slippage/commission-
aware sell fill on short open); hourly funding on coin short + hedge long for
full held hours; aligned ETH hedge sizing/exit pricing and funding; max_live_coin_notional = executed rebound-short coin notional; entry_next_bar;
stopped buy never opens rebound short. Synthetic fixtures.
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


class TestReboundShortTargetAlignedEthCommissionMinCapCutShares(unittest.TestCase):
    def _cfg(self):
        return StrategyConfig(
            enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
            avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
            commission_min=1.0, funding_rate_pct_per_hour=0.01,
            min_daily_volume_usd=0.0, time_exit_max_bars=200,
            enable_liquidation_checks=True,
            liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0,
            liquidation_penalty_pct=0.5, gross_cap_pct=120.0,
            rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
            rebound_short_time_exit_bars=48,
        )

    def _sig(self, shares=600.0):
        return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                      stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                      timestamp="t5", size_shares=shares, signal_index=5)

    def test_rebound_short_target_aligned_eth_commission_min_cap_cut_shares(self):
        n = 30
        coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
        coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)   # long entry_next_bar fill
        coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)   # long target -> rebound short opens
        coin[9] = _c("b9", 110.0, 115.0, 109.0, 110.0)  # short holds
        coin[10] = _c("e10", 108.0, 109.0, 98.0, 107.0)  # rebound short target
        eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
        eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
        eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)  # rebound hedge entry aligned idx 8
        eth[10] = _c("h10", 2010.0, 2015.0, 2005.0, 2010.0)  # ALIGNED exit

        res = backtest_simple(coin, self._sig(600.0), config=self._cfg(),
                              risk_state=_NoCutRS(), capital=100000.0, eth_candles=eth)

        self.assertEqual(res.exit_reason, "target_rebound_short")
        self.assertEqual([t["reason"] for t in res.trades], ["target", "target"])
        long_leg, short_leg = res.trades

        self.assertAlmostEqual(long_leg["entry"], 100.00166666666667, places=9)
        self.assertAlmostEqual(long_leg["exit"], 109.00014999999999, places=9)
        self.assertAlmostEqual(long_leg["pnl"], 5381.089699999996, places=5)

        # Rebound short opens at sell fill of long-target exit_px (same cross-leg
        # transition as missing-ETH case); target anchored to executed short entry.
        self.assertAlmostEqual(short_leg["entry"], 108.99848333333333, places=9)
        self.assertAlmostEqual(short_leg["exit"], 99.1902865, places=7)
        self.assertAlmostEqual(short_leg["pnl"], 5904.5378269999965, places=5)

        # Rebound hedge (long ETH): sized from coin/ETH history at rebound bar,
        # entry aligned to idx 8 open with buy commission_min; ALIGNED exit at
        # eth[10].close (2010) with sell commission_min; 3 held hours long funding.
        self.assertEqual(res.rebound_hedge_side, "long")
        self.assertAlmostEqual(res.rebound_hedge_size, 98.098635, places=6)
        self.assertAlmostEqual(res.rebound_hedge_entry, 2000.010193821759, places=9)
        self.assertAlmostEqual(res.rebound_hedge_exit, 2009.989806178241, places=9)
        self.assertAlmostEqual(res.rebound_hedge_pnl, 920.126869000017, places=6)
        self.assertAlmostEqual(res.hedge_pnl, res.rebound_hedge_pnl, places=9)

        # Executed rebound-short coin notional (authoritative reservation).
        self.assertAlmostEqual(res.max_live_coin_notional, 65399.09, places=6)

        coin_total = sum(t["pnl"] for t in res.trades)
        self.assertAlmostEqual(coin_total, 11285.627526999993, places=5)
        self.assertAlmostEqual(res.total_pnl, 12205.75439600001, places=5)
        self.assertAlmostEqual(res.total_pnl, coin_total + res.hedge_pnl, places=6)
        self.assertEqual(res.bars_held, 5)


if __name__ == "__main__":
    unittest.main()
