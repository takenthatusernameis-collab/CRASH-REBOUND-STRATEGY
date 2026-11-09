"""Material regression lock (2026-11-09T10:05:00Z, 2b engine item 2a).

Uncovered interaction: rebound-short LIQUIDATION × missing-ETH-exit-fallback ×
commission_min × cap-cut-implied executed shares (600).

Existing locks: stop/48h × missing-ETH fallback × commission_min × 600 shares
(2026-11-09T09:53:20Z); liquidation × ETH-hedge-present × commission_min ×
cap-cut (2026-11-08T16:22:46Z). This lock covers the unrepaired cell where the
aligned ETH exit bar exists but close/open are absent (missing-ETH fallback) at
LIQUIDATION, under commission_min, with cap-cut-implied share count (600).

Spec: hourly liquidation at worst price (candle high for short) with penalty on
executed rebound-short notional; hourly funding on coin short + hedge long for
full held hours; missing-ETH fallback sell applies sell-side commission_min (no
look-ahead, aligned fallback); max_live_coin_notional = executed rebound-short
coin notional; entry_next_bar; rebound -9%/+40% anchored to executed short entry.
Synthetic fixtures.
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


class TestReboundShortLiquidationMissingEthCommissionMinCapCutShares(unittest.TestCase):
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
        # Post-cap-cut share count (portfolio-reservation context).
        return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                      stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                      timestamp="t5", size_shares=shares, signal_index=5)

    def test_rebound_short_liquidation_missing_eth_exit_commission_min_cap_cut_shares(self):
        n = 30
        coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
        coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)   # long entry_next_bar fill
        coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)   # long target -> rebound short opens
        coin[9] = _c("b9", 110.0, 115.0, 109.0, 110.0)  # below liq threshold
        coin[10] = _c("e10", 110.0, 116.0, 109.0, 115.0)  # rebound short liquidation (high)
        eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
        eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
        eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)  # rebound hedge entry aligned to idx 8
        eth[10] = {"timestamp": "h10"}  # missing close/open at liq bar -> fallback

        res = backtest_simple(coin, self._sig(600.0), config=self._cfg(),
                              risk_state=_NoCutRS(), capital=100000.0, eth_candles=eth)

        self.assertEqual(res.exit_reason, "target_rebound_short")
        self.assertEqual([t["reason"] for t in res.trades], ["target", "liquidated"])
        long_leg, short_leg = res.trades

        # Long leg: entry_next_bar fill + target exit (unchanged by short path).
        self.assertAlmostEqual(long_leg["entry"], 100.00166666666667, places=9)
        self.assertAlmostEqual(long_leg["exit"], 109.00014999999999, places=9)
        self.assertAlmostEqual(long_leg["pnl"], 5381.089699999996, places=5)

        # Rebound short: worst-price liquidation at candle high, commission_min buy fill.
        self.assertAlmostEqual(short_leg["entry"], 108.99848333333333, places=9)
        self.assertAlmostEqual(short_leg["exit"], 116.00166666666667, places=9)
        self.assertAlmostEqual(short_leg["pnl"], -4509.285723000002, places=5)

        # Rebound hedge (long ETH): entry aligned to rebound bar idx, missing-ETH
        # exit fallback + sell commission_min => exit 2000.0.
        self.assertEqual(res.rebound_hedge_side, "long")
        self.assertAlmostEqual(res.rebound_hedge_size, 98.098635, places=6)
        self.assertAlmostEqual(res.rebound_hedge_entry, 2000.010193821759, places=9)
        self.assertAlmostEqual(res.rebound_hedge_exit, 2000.0, places=9)
        self.assertAlmostEqual(res.rebound_hedge_pnl, -59.85948100000001, places=6)
        self.assertAlmostEqual(res.hedge_pnl, res.rebound_hedge_pnl, places=9)

        # Authoritative for portfolio reservation: executed rebound-short coin notional.
        self.assertAlmostEqual(res.max_live_coin_notional, 65399.09, places=6)

        coin_total = sum(t["pnl"] for t in res.trades)
        self.assertAlmostEqual(coin_total, 871.803976999994, places=5)
        self.assertAlmostEqual(res.total_pnl, 811.944495999994, places=5)
        self.assertAlmostEqual(res.total_pnl, coin_total + res.hedge_pnl, places=6)


if __name__ == "__main__":
    unittest.main()
