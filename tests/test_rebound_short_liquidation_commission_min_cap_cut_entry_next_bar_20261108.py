"""Material regression lock (2026-11-08T16:11:03Z, 2b narrowed gap).

Uncovered interaction: rebound-short liquidation penalty base / reservation /
notional under commission_min-adjusted fills + equal-share cap-cut-adjusted
shares + entry_next_bar. Existing locks cover (a) commission_min fill parity,
(b) long liquidation + cap-cut + commission_min + entry_next_bar, and (c)
portfolio cap-cut/mixed terminals; this locks the engine cross-leg path where a
cap-cut long hits target, opens a rebound short at commission_min-adjusted fill,
and the rebound short is liquidated — exercising executed-short notional,
penalty base, max_live_coin_notional (max across long/rebound-short coin legs),
and commission_min on every fill.

Spec non-negotiables: hourly liquidation at worst price with correct
sequencing/notional/timing/penalty; commission_min fill parity; equal-share cuts
(cuts only) reflected in executed shares; entry_next_bar; stopped buy never opens
rebound short (this path reaches target). Hourly only; synthetic fixtures; not
performance evidence.

Concrete expected values pinned to current spec-consistent behavior.
"""
from __future__ import annotations

import unittest

from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _coin(n):
    return [_c(f"2025-01-01T{i % 24:02d}:00:00", 100.0, 101.0, 99.5, 100.0) for i in range(n)]


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


class TestReboundShortLiquidationCommissionMinCapCutEntryNextBar(unittest.TestCase):
    def _cfg(self):
        return StrategyConfig(
            enable_eth_hedge=False, enable_rebound_short=True, entry_next_bar=True,
            avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
            commission_min=1.0, funding_rate_pct_per_hour=0.0, min_daily_volume_usd=0.0,
            time_exit_max_bars=200, enable_liquidation_checks=True,
            liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0,
            liquidation_penalty_pct=0.5, gross_cap_pct=120.0,
            rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
        )

    def test_rebound_short_liquidation_commission_min_cap_cut_penalty_notional(self):
        """Rebound short liquidation uses executed (commission_min-adjusted) short
        notional for penalty base; max_live_coin_notional tracks max across coin
        legs (rebound short notional may exceed long entry) under cap-cut shares.

        Setup: existing 80k + desired 100k on 100k capital @120% cap => 60k equal
        share each (cuts only). entry_next_bar buy fills at bar 6 open 100 with
        commission_min. Long target hits bar 8; rebound short opens (sell fill with
        commission_min). Bar 11 liquidates short (high >= entry_short*(1+6%)).
        """
        candles = _coin(30)
        candles[6] = _c("2025-01-01T06:00:00", 100.0, 100.5, 99.5, 100.0)   # entry_next_bar fill
        candles[8] = _c("2025-01-01T08:00:00", 100.0, 110.0, 99.5, 109.0)   # long target
        candles[10] = _c("2025-01-01T10:00:00", 110.0, 112.0, 106.0, 110.0)
        candles[11] = _c("2025-01-01T11:00:00", 110.0, 116.0, 109.0, 115.0)  # short liq
        sig = Signal(symbol="T", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                     target_price=109.0, risk_per_share=20.0, timestamp="t5",
                     size_shares=1000.0, signal_index=5)
        res = backtest_simple(candles, sig, config=self._cfg(), risk_state=_CapCutRS(), capital=100000.0)
        self.assertEqual(res.exit_reason, "target_rebound_short")
        self.assertEqual(len(res.trades), 2)
        long_leg, short_leg = res.trades
        self.assertEqual(long_leg["reason"], "target")
        self.assertEqual(short_leg["reason"], "liquidated")

        # Cap-cut shares: 60k / (long entry fill ~100.001666...) => ~599.994 shares
        self.assertAlmostEqual(res.shares, 599.9940000599994, places=9)
        self.assertAlmostEqual(res.entry_price, 100.001, places=9)
        # max_live_coin_notional is max across coin legs (long + rebound short);
        # short opens at higher executed notional than long entry under this path.
        self.assertAlmostEqual(res.max_live_coin_notional, 65397.99999999999, places=6)
        # Long: buy at 100 + comm_min/share, sell target 109 - comm_min/share
        self.assertAlmostEqual(long_leg["entry"], 100.001, places=9)
        self.assertAlmostEqual(long_leg["exit"], 108.99942331666666, places=9)
        self.assertAlmostEqual(long_leg["pnl"], 5398.999999999995, places=5)
        # Rebound short: opened from long exit fill with sell commission_min applied;
        # liquidated at worst high 116 with buy commission_min; penalty on executed
        # short notional (short_entry * shares).
        self.assertAlmostEqual(short_leg["entry"], 108.99775663333332, places=9)
        self.assertAlmostEqual(short_leg["exit"], 116.00166668333334, places=9)
        self.assertAlmostEqual(short_leg["pnl"], -4529.29400695994, places=5)
        self.assertAlmostEqual(res.total_pnl, 869.7059930400555, places=5)
        # Penalty base invariant: liquidation penalty charged on executed rebound-short
        # notional (post cap-cut, commission_min-adjusted fill), not pre-cut/legacy.
        recomputed_penalty_base = short_leg["entry"] * res.shares
        self.assertGreater(recomputed_penalty_base, 0.0)
        raw_short = (short_leg["entry"] - short_leg["exit"]) * res.shares
        expected_pen = 0.005 * recomputed_penalty_base
        self.assertAlmostEqual(short_leg["pnl"], raw_short - expected_pen, places=5)
        # Reservation/notional: max live coin notional must cover executed short leg.
        self.assertGreaterEqual(res.max_live_coin_notional, recomputed_penalty_base - 1e-6)
        self.assertGreaterEqual(res.max_live_coin_notional, res.entry_price * res.shares - 1e-6)


if __name__ == "__main__":
    unittest.main()
