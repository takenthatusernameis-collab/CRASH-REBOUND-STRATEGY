"""Material regression lock (2026-11-08T16:22:46Z, 2g/2b ii).

Uncovered interaction: rebound-short liquidation with ETH hedge enabled under
commission_min-adjusted fills + equal-share cap-cut + entry_next_bar. Locks
rebound hedge sizing/entry alignment (no look-ahead, bar idx), commission_min on
hedge/coin fills, executed-short notional penalty base, max_live_coin_notional
coin-leg reservation, rebound hedge funding/PnL sequencing, and coin+hedge
attribution. Synthetic fixtures only (non-evidence); hourly only.

Spec non-negotiables: ETH hedge every leg (vol-ratio/cap 3x, 336h lookback
available history), hourly funding on every leg, hourly liquidation at worst
price with correct sequencing/notional/timing/penalty, commission_min fill
parity, equal-share cuts (cuts only), entry_next_bar, stopped buy never opens
rebound short (this path hits target).
"""
from __future__ import annotations

import unittest

from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


class _CapCutRS:
    open_positions = 1
    gross_exposure = 80000.0
    open_position_notionals = [80000.0]

    def check_position(self, config, capital, shares, entry_price):
        from types import SimpleNamespace
        return SimpleNamespace(allowed=True, size_shares=shares)

    def apply_cap_cuts(self, capital, config, open_notional=None):
        capv = capital * config.gross_cap_pct / 100.0
        n = len(open_notional or [])
        return [capv / n] * n if n else []

    def apply_trade(self, *a, **k):
        pass


class TestReboundShortLiquidationEthHedgeCommissionMinCapCutEntryNextBar(unittest.TestCase):
    def _cfg(self):
        return StrategyConfig(
            enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
            avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
            commission_min=1.0, funding_rate_pct_per_hour=0.0, min_daily_volume_usd=0.0,
            time_exit_max_bars=200, enable_liquidation_checks=True,
            liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0,
            liquidation_penalty_pct=0.5, gross_cap_pct=120.0,
            rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
        )

    def _candles(self):
        n = 30
        coin = [_c(f"2025-01-01T{i % 24:02d}:00:00", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
        coin[6] = _c("2025-01-01T06:00:00", 100.0, 100.5, 99.5, 100.0)   # entry_next_bar long fill
        coin[8] = _c("2025-01-01T08:00:00", 100.0, 110.0, 99.5, 109.0)   # long target -> rebound short opens
        coin[10] = _c("2025-01-01T10:00:00", 110.0, 112.0, 106.0, 110.0)
        coin[11] = _c("2025-01-01T11:00:00", 110.0, 116.0, 109.0, 115.0)  # rebound short liquidation
        eth = [_c(f"2025-01-01T{i % 24:02d}:00:00", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
        eth[6] = _c("2025-01-01T06:00:00", 2000.0, 2010.0, 1990.0, 2000.0)
        eth[8] = _c("2025-01-01T08:00:00", 2000.0, 2030.0, 1995.0, 2025.0)   # rebound hedge entry aligned to idx 8
        eth[11] = _c("2025-01-01T11:00:00", 2050.0, 2080.0, 2040.0, 2070.0)  # rebound hedge exit
        return coin, eth

    def test_rebound_short_liquidation_with_eth_hedge_cap_cut_commission_min(self):
        """Rebound hedge (long ETH) + rebound short liquidation under cap-cut and
        commission_min: hedge entry aligned to rebound-entry bar idx (no look-ahead),
        commission_min on all fills, short penalty on executed notional, coin leg
        reservation covers executed short, hedge/coin attribution consistent."""
        coin, eth = self._candles()
        sig = Signal(symbol="T", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                     target_price=109.0, risk_per_share=20.0, timestamp="t5",
                     size_shares=1000.0, signal_index=5)
        res = backtest_simple(coin, sig, config=self._cfg(), risk_state=_CapCutRS(),
                              capital=100000.0, eth_candles=eth)

        self.assertEqual(res.exit_reason, "target_rebound_short")
        self.assertEqual(len(res.trades), 2)
        long_leg, short_leg = res.trades
        self.assertEqual(long_leg["reason"], "target")
        self.assertEqual(short_leg["reason"], "liquidated")

        # Cap-cut + commission_min execution (matches no-hedge invariant path).
        self.assertAlmostEqual(res.shares, 599.9940000599994, places=9)
        self.assertAlmostEqual(res.entry_price, 100.001, places=9)
        # max_live_coin_notional tracks coin legs (cap/reservation), not hedges.
        self.assertAlmostEqual(res.max_live_coin_notional, 65397.99999999999, places=6)
        self.assertAlmostEqual(long_leg["entry"], 100.001, places=9)
        self.assertAlmostEqual(long_leg["exit"], 108.99942331666666, places=9)
        self.assertAlmostEqual(long_leg["pnl"], 5398.999999999995, places=5)
        self.assertAlmostEqual(short_leg["entry"], 108.99775663333332, places=9)
        self.assertAlmostEqual(short_leg["exit"], 116.00166668333334, places=9)
        self.assertAlmostEqual(short_leg["pnl"], -4529.29400695994, places=5)

        # Penalty base: executed rebound-short notional (commission_min-adjusted).
        recomputed_short_notional = short_leg["entry"] * res.shares
        self.assertAlmostEqual(recomputed_short_notional, 65397.99999999999, places=6)
        raw_short = (short_leg["entry"] - short_leg["exit"]) * res.shares
        expected_pen = 0.005 * recomputed_short_notional
        self.assertAlmostEqual(short_leg["pnl"], raw_short - expected_pen, places=5)
        self.assertGreaterEqual(res.max_live_coin_notional, recomputed_short_notional - 1e-6)

        # Rebound hedge (long ETH) — opened at rebound-entry bar idx (no look-ahead),
        # sized from aligned history, closed on liquidation with commission_min.
        self.assertIsNone(res.hedge_side)  # long-leg hedge not opened in this short fixture
        self.assertAlmostEqual(res.hedge_size, 0.0, places=9)
        self.assertEqual(res.rebound_hedge_side, "long")
        self.assertAlmostEqual(res.rebound_hedge_size, 98.09699999999998, places=9)
        # Commission_min-adjusted hedge fills (buy at entry, sell at exit).
        self.assertAlmostEqual(res.rebound_hedge_entry, 2000.0101939916613, places=9)
        self.assertAlmostEqual(res.rebound_hedge_exit, 2069.9898060083387, places=9)
        self.assertAlmostEqual(res.rebound_hedge_pnl, 6864.790000000011, places=6)
        # hedge_pnl field aggregates long+rebound hedge pnl (long is 0 here).
        self.assertAlmostEqual(res.hedge_pnl, 6864.790000000011, places=6)

        coin_total = sum(t["pnl"] for t in res.trades)
        self.assertAlmostEqual(coin_total, 869.7059930400555, places=5)
        self.assertAlmostEqual(res.total_pnl, 7734.495993040066, places=6)
        self.assertAlmostEqual(res.total_pnl, coin_total + res.hedge_pnl, places=6)


if __name__ == "__main__":
    unittest.main()
