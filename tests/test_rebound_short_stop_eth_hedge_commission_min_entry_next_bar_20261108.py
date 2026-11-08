"""Priority B gap: rebound short STOP (+40%) under ETH hedge + commission_min
+ entry_next_bar.

Existing locks cover rebound-short LIQUIDATION (eth+commission_min+entry_next_bar)
and rebound-short STOP (no eth, no commission_min, no entry_next_bar). This test
covers the stop path with all Priority B dimensions enabled: ETH hedge (long),
commission_min-adjusted fills, entry_next_bar re-anchor, stop anchored to executed
short entry, hourly funding on coin + hedge legs, no look-ahead.

Spec: hourly funding on every leg; rebound stop +40% above executed short entry;
ETH hedge every leg (vol-ratio/cap 3x, 336h); liquidation disabled so the wide
40% stop is reachable before the +6% liquidation threshold. Synthetic fixtures.
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


class TestReboundShortStopEthHedgeCommissionMinEntryNextBar(unittest.TestCase):
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

    def _candles(self):
        n = 30
        coin = [_c(f"2025-01-01T{i % 24:02d}:00:00", 100.0, 101.0, 99.0, 100.0) for i in range(n)]
        coin[6] = _c("2025-01-01T06:00:00", 100.0, 100.5, 99.0, 100.0)   # entry_next_bar long fill
        coin[8] = _c("2025-01-01T08:00:00", 100.0, 110.0, 99.0, 109.0)   # long target -> rebound short opens
        coin[9] = _c("2025-01-01T09:00:00", 110.0, 112.0, 105.0, 110.0)   # low 105 > short target ~99.19 (no target hit)
        coin[10] = _c("2025-01-01T10:00:00", 110.0, 160.0, 109.0, 115.0)  # rebound short stop hit (+40%)
        eth = [_c(f"2025-01-01T{i % 24:02d}:00:00", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
        eth[6] = _c("2025-01-01T06:00:00", 2000.0, 2010.0, 1990.0, 2000.0)
        eth[8] = _c("2025-01-01T08:00:00", 2000.0, 2030.0, 1995.0, 2025.0)   # rebound hedge entry aligned to idx 8
        eth[10] = _c("2025-01-01T10:00:00", 2050.0, 2080.0, 2040.0, 2070.0)  # rebound hedge exit on stop bar
        return coin, eth

    def test_rebound_short_stop_with_eth_hedge_commission_min_entry_next_bar(self):
        coin, eth = self._candles()
        sig = Signal(symbol="T", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                     target_price=109.0, risk_per_share=20.0, timestamp="t5",
                     size_shares=1000.0, signal_index=5)
        res = backtest_simple(coin, sig, config=self._cfg(), risk_state=_NoCutRS(),
                              capital=100000.0, eth_candles=eth)

        self.assertEqual(res.exit_reason, "target_rebound_short")
        self.assertEqual(len(res.trades), 2)
        long_leg, short_leg = res.trades
        self.assertEqual(long_leg["reason"], "target")
        self.assertEqual(short_leg["reason"], "stopped")

        # Long leg: entry_next_bar fill at bar 6 open, target hit at bar 8.
        self.assertAlmostEqual(long_leg["entry"], 100.001, places=9)
        self.assertAlmostEqual(long_leg["exit"], 109.00009, places=9)
        self.assertAlmostEqual(long_leg["pnl"], 8969.089699999995, places=5)

        # Rebound short stop anchored to executed short entry (+40%).
        self.assertAlmostEqual(short_leg["entry"], 108.99909, places=9)
        self.assertAlmostEqual(short_leg["exit"], 152.59972599999998, places=9)
        self.assertAlmostEqual(short_leg["pnl"], -43567.93627299998, places=5)

        # Rebound hedge (long ETH) opened at rebound-entry bar idx (no look-ahead),
        # sized from aligned history, closed on stop bar with commission_min.
        self.assertEqual(res.rebound_hedge_side, "long")
        self.assertAlmostEqual(res.rebound_hedge_size, 163.498635, places=6)
        self.assertAlmostEqual(res.rebound_hedge_entry, 2000.0061162590134, places=9)
        self.assertAlmostEqual(res.rebound_hedge_exit, 2069.993883740987, places=9)
        self.assertAlmostEqual(res.rebound_hedge_pnl, 11344.804969000035, places=6)
        self.assertAlmostEqual(res.hedge_pnl, 11344.804969000035, places=6)

        # max_live_coin_notional tracks executed rebound-short notional (cap/reservation).
        self.assertAlmostEqual(res.max_live_coin_notional, 108999.09, places=6)

        # Funding on coin short leg + hedge long leg (hourly funding every leg).
        coin_total = sum(t["pnl"] for t in res.trades)
        self.assertAlmostEqual(res.total_pnl, -23254.041603999947, places=6)
        self.assertAlmostEqual(res.total_pnl, coin_total + res.hedge_pnl, places=6)


if __name__ == "__main__":
    unittest.main()
