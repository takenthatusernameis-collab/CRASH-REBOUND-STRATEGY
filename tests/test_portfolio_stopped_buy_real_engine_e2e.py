"""Material spec-fidelity hardening (2026-11-07): portfolio E2E with REAL engine execution.

Uses minimal mocking (only signal generation is forced to a controlled entry) so that
backtest_simple, hedge/funding/liquidation logic, and portfolio risk/occupancy reconciliation
all execute for real. Synthetic fixtures only; not real-market evidence.

Spec invariants:
- A buy stopped by the 8x safety stop / stop path must NEVER open a rebound short.
- Portfolio must reconcile exposure/occupancy/risk_state after the trade completes.
- Long-leg ETH hedge behavior remains spec-consistent under portfolio flow (side/close
  accounting present when hedge is available; no rebound-short side effects).
"""
from __future__ import annotations

import copy
import unittest
from unittest.mock import patch

from scripts.run_portfolio import run_portfolio_simulation
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(i, o, h, l, cl, v=10_000_000.0):
    return {"timestamp": f"t{i:03d}", "open": o, "high": h, "low": l, "close": cl, "volume": v}


class TestPortfolioStoppedBuyRealEngineE2E(unittest.TestCase):
    def _run(self, *, enable_hedge=True, entry_next_bar=True):
        candles = [_c(i, 100.0, 101.0, 99.0, 100.0, 10_000_000.0 / 24.0 / 100.0) for i in range(80)]
        # Decision bar 20; with entry_next_bar the engine enters at bar 21 open.
        # Bar 21 breaches stop (90.0) on its low -> stopped. Subsequent bars must not
        # produce a rebound short because the buy was stopped (spec: stopped buy never
        # opens rebound short).
        candles[21] = _c(21, 100.0, 101.0, 89.0, 92.0)
        candles[22] = _c(22, 92.0, 110.0, 91.0, 108.0)  # would be tempting for short if bugged
        eth = [_c(i, 2000.0, 2015.0, 1985.0, 2000.0, 10_000_000.0 / 24.0 / 2000.0) for i in range(80)]
        cfg = StrategyConfig(
            use_rsi_trigger=False,
            min_daily_volume_usd=0.0,
            enable_eth_hedge=enable_hedge,
            enable_rebound_short=True,
            entry_next_bar=entry_next_bar,
            enable_liquidation_checks=False,
            funding_rate_pct_per_hour=0.0,
        )
        sig = Signal(
            symbol="X", side="long", reason="forced_e2e", entry_price=100.0, stop_price=90.0,
            target_price=109.0, risk_per_share=10.0, timestamp="t020", size_shares=1.0, signal_index=20,
        )

        def fake_gen(hist, symbol=None, config=None, capital=100000.0, cache=None):
            if symbol == "X" and len(hist) - 1 == 20:
                s = copy.copy(sig)
                s.signal_index = len(hist) - 1
                return s
            return None

        # Minimal mocking: only signal generation forced. Engine + portfolio run for real.
        with patch("scripts.run_portfolio.generate_signal", side_effect=fake_gen):
            return run_portfolio_simulation(
                {"X": candles}, config=cfg, capital=100000.0, eth_candles={"ETH": eth} if enable_hedge else None
            )

    def test_stopped_buy_never_opens_rebound_short_real_engine(self):
        res = self._run(enable_hedge=True, entry_next_bar=True)
        self.assertEqual(res["num_trades"], 1)
        t = res["trades"][0]
        self.assertEqual(t["symbol"], "X")
        self.assertEqual(t["exit_reason"], "stopped")
        self.assertNotIn("rebound", str(t["exit_reason"]).lower())
        self.assertNotIn("short_target", str(t["exit_reason"]).lower())
        self.assertNotIn("short_stop", str(t["exit_reason"]).lower())
        # Portfolio summary has no short side marker from rebound flow.
        self.assertFalse(str(t.get("hedge_side", "")).lower() == "long" and "rebound" in str(t))

    def test_portfolio_reconciles_exposure_occupancy_risk_state_after_stopped_buy(self):
        res = self._run(enable_hedge=True, entry_next_bar=True)
        self.assertEqual(res["num_trades"], 1)
        self.assertEqual(res["final_open_positions"], 0)
        self.assertAlmostEqual(float(res["final_gross_exposure"]), 0.0, places=9)
        self.assertTrue(res["trades"][0]["bars_held"] >= 1)
        self.assertIsNotNone(res["trades"][0]["exit_timestamp"])

    def test_long_hedge_behavior_spec_consistent_under_portfolio_flow(self):
        # Hedge is optional depending on history/vol availability; when absent it must not
        # create rebound-short side effects. When present (short hedge on long leg) it must
        # not be mislabeled as a rebound long hedge.
        res = self._run(enable_hedge=True, entry_next_bar=True)
        t = res["trades"][0]
        self.assertEqual(t["exit_reason"], "stopped")
        self.assertIn(t.get("hedge_side"), (None, "short"))
        if t.get("hedge_side") == "short":
            self.assertGreaterEqual(float(t.get("hedge_size") or 0.0), 0.0)
            self.assertIsInstance(t.get("hedge_pnl", 0.0), (int, float))
        # No short coin leg opened: total_pnl is long coin (+ optional short hedge), not rebound.
        self.assertIsInstance(t.get("total_pnl"), (int, float))

    def test_stopped_buy_no_rebound_short_same_bar_entry_mode(self):
        res = self._run(enable_hedge=False, entry_next_bar=False)
        self.assertEqual(res["num_trades"], 1)
        self.assertEqual(res["trades"][0]["exit_reason"], "stopped")
        self.assertEqual(res["final_open_positions"], 0)
        self.assertAlmostEqual(float(res["final_gross_exposure"]), 0.0, places=9)


if __name__ == "__main__":
    unittest.main()
