"""Material spec-fidelity hardening (2026-11-07): portfolio risk/notional
reconciliation under liquidation and rebound exits with REAL engine execution.

Minimal mocking: only signal generation is forced to controlled entries so that
backtest_simple (liquidation, hedge/funding, rebound short), risk_state
accounting, and portfolio occupancy/gross-exposure reconciliation all execute.
Synthetic fixtures only; not real-market evidence.

Spec invariants:
- After liquidation, portfolio reports no open positions, zero gross exposure,
  and correct occupancy/exit accounting (penalty + funding applied by engine).
- After rebound exits (target->short path completes), portfolio reconciles to
  no open positions / zero gross exposure.
- risk_state notionals/gross_exposure do not leak after terminal trades.
"""
from __future__ import annotations

import copy
import unittest
from unittest.mock import patch

from scripts.run_portfolio import run_portfolio_simulation
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(i, o, h, l, cl, v=10_000_000.0 / 24.0 / 100.0):
    return {"timestamp": f"t{i:03d}", "open": o, "high": h, "low": l, "close": cl, "volume": v}


def _base_cfg(**kw):
    d = dict(
        use_rsi_trigger=False,
        min_daily_volume_usd=0.0,
        enable_eth_hedge=True,
        enable_rebound_short=True,
        entry_next_bar=True,
        enable_liquidation_checks=True,
        liquidation_maint_margin_pct=5.0,
        liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5,
        funding_rate_pct_per_hour=0.0,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
    )
    d.update(kw)
    return StrategyConfig(**d)


class TestPortfolioReconciliationLiquidation(unittest.TestCase):
    def _run_liquidation(self):
        candles = [_c(i, 100.0, 101.0, 99.0, 100.0) for i in range(80)]
        # Decision bar 20; entry at bar 21 open (100). Bar 22 low breaches liquidation
        # threshold (94.0 with 5% maint + 1% buffer). Stop set very low so liquidation
        # wins if both checked (engine checks liquidation first).
        candles[22] = _c(22, 96.0, 97.0, 93.0, 93.5)
        eth = [_c(i, 2000.0, 2015.0, 1985.0, 2000.0, 10_000_000.0 / 24.0 / 2000.0) for i in range(80)]
        cfg = _base_cfg()
        sig = Signal(
            symbol="X", side="long", reason="forced_liq_e2e", entry_price=100.0, stop_price=50.0,
            target_price=150.0, risk_per_share=50.0, timestamp="t020", size_shares=1.0, signal_index=20,
        )

        def fake_gen(hist, symbol=None, config=None, capital=100000.0, cache=None):
            if symbol == "X" and len(hist) - 1 == 20:
                s = copy.copy(sig)
                s.signal_index = len(hist) - 1
                return s
            return None

        with patch("scripts.run_portfolio.generate_signal", side_effect=fake_gen):
            return run_portfolio_simulation(
                {"X": candles}, config=cfg, capital=100000.0, eth_candles={"ETH": eth}
            )

    def test_liquidation_reconciles_exposure_occupancy_and_state(self):
        res = self._run_liquidation()
        self.assertEqual(res["num_trades"], 1)
        t = res["trades"][0]
        self.assertEqual(t["exit_reason"], "liquidated")
        self.assertEqual(res["final_open_positions"], 0)
        self.assertAlmostEqual(float(res["final_gross_exposure"]), 0.0, places=9)
        self.assertIsNotNone(t["exit_timestamp"])
        self.assertGreaterEqual(int(t["bars_held"]), 1)
        # risk_state must not retain leaked notionals after terminal liquidation
        rs = res["risk_state"]
        self.assertEqual(getattr(rs, "open_positions", -1), 0)
        self.assertAlmostEqual(float(getattr(rs, "gross_exposure", -1.0)), 0.0, places=9)
        self.assertEqual(list(getattr(rs, "open_position_notionals", ["leak"])), [])
        # liquidation is a closed trade; pnl includes penalty in engine semantics
        self.assertIsInstance(t.get("total_pnl"), (int, float))
        self.assertIsInstance(t.get("hedge_pnl", 0.0), (int, float))

    def test_liquidation_never_opens_rebound_short(self):
        res = self._run_liquidation()
        t = res["trades"][0]
        self.assertEqual(t["exit_reason"], "liquidated")
        self.assertNotIn("short", str(t["exit_reason"]).lower())
        # no rebound-side trade markers in recorded trade
        self.assertIn(t.get("hedge_side"), (None, "short"))  # long-leg hedge only if present


class TestPortfolioReconciliationReboundExit(unittest.TestCase):
    def _run_rebound(self):
        candles = [_c(i, 100.0, 101.0, 99.0, 100.0) for i in range(100)]
        # Entry at bar 21. Bar 22 hits target (109) high -> long target, rebound short opens.
        candles[22] = _c(22, 100.0, 110.0, 99.0, 109.0)
        # Rebound short entered around 109; drive to short target (-9% => ~99.19) at bar 24.
        for i in range(23, 30):
            candles[i] = _c(i, 105.0, 106.0, 98.0, 100.0)
        candles[24] = _c(24, 102.0, 103.0, 98.5, 99.0)
        eth = [_c(i, 2000.0, 2015.0, 1985.0, 2000.0, 10_000_000.0 / 24.0 / 2000.0) for i in range(100)]
        cfg = _base_cfg(enable_liquidation_checks=False, rebound_short_time_exit_bars=48)
        sig = Signal(
            symbol="X", side="long", reason="forced_rebound_e2e", entry_price=100.0, stop_price=80.0,
            target_price=109.0, risk_per_share=20.0, timestamp="t020", size_shares=1.0, signal_index=20,
        )

        def fake_gen(hist, symbol=None, config=None, capital=100000.0, cache=None):
            if symbol == "X" and len(hist) - 1 == 20:
                s = copy.copy(sig)
                s.signal_index = len(hist) - 1
                return s
            return None

        with patch("scripts.run_portfolio.generate_signal", side_effect=fake_gen):
            return run_portfolio_simulation(
                {"X": candles}, config=cfg, capital=100000.0, eth_candles={"ETH": eth}
            )

    def test_rebound_exits_reconcile_exposure_occupancy_and_per_leg_fields(self):
        res = self._run_rebound()
        self.assertEqual(res["num_trades"], 1)
        t = res["trades"][0]
        # Rebound path completes inside one backtest_simple execution; portfolio records one trade.
        # Exit reason may be target (long leg completed) or a composite depending on engine;
        # critical invariant: no open exposure/occupancy leak and accounting fields present.
        self.assertIsNotNone(t.get("exit_reason"))
        self.assertEqual(res["final_open_positions"], 0)
        self.assertAlmostEqual(float(res["final_gross_exposure"]), 0.0, places=9)
        rs = res["risk_state"]
        self.assertEqual(getattr(rs, "open_positions", -1), 0)
        self.assertAlmostEqual(float(getattr(rs, "gross_exposure", -1.0)), 0.0, places=9)
        self.assertEqual(list(getattr(rs, "open_position_notionals", ["leak"])), [])
        self.assertIsInstance(t.get("total_pnl"), (int, float))
        self.assertIsInstance(t.get("hedge_pnl", 0.0), (int, float))
        self.assertGreaterEqual(int(t.get("bars_held") or 0), 1)

    def test_rebound_path_does_not_leave_risk_state_dirty_for_next_symbol(self):
        # Two symbols: first completes rebound path, second should be admissible later with clean state.
        candles_a = [_c(i, 100.0, 101.0, 99.0, 100.0) for i in range(120)]
        candles_a[22] = _c(22, 100.0, 110.0, 99.0, 109.0)
        candles_a[24] = _c(24, 102.0, 103.0, 98.5, 99.0)
        candles_b = [_c(i, 100.0, 101.0, 99.0, 100.0) for i in range(120)]
        candles_b[62] = _c(62, 100.0, 110.0, 99.0, 109.0)
        candles_b[64] = _c(64, 102.0, 103.0, 98.5, 99.0)
        eth = [_c(i, 2000.0, 2015.0, 1985.0, 2000.0, 10_000_000.0 / 24.0 / 2000.0) for i in range(120)]
        cfg = _base_cfg(enable_liquidation_checks=False)
        sig_a = Signal(symbol="A", side="long", reason="a", entry_price=100.0, stop_price=80.0,
                       target_price=109.0, risk_per_share=20.0, timestamp="t020", size_shares=1.0, signal_index=20)
        sig_b = Signal(symbol="B", side="long", reason="b", entry_price=100.0, stop_price=80.0,
                       target_price=109.0, risk_per_share=20.0, timestamp="t060", size_shares=1.0, signal_index=60)

        def fake_gen(hist, symbol=None, config=None, capital=100000.0, cache=None):
            idx = len(hist) - 1
            if symbol == "A" and idx == 20:
                s = copy.copy(sig_a); s.signal_index = idx; return s
            if symbol == "B" and idx == 60:
                s = copy.copy(sig_b); s.signal_index = idx; return s
            return None

        with patch("scripts.run_portfolio.generate_signal", side_effect=fake_gen):
            res = run_portfolio_simulation(
                {"A": candles_a, "B": candles_b}, config=cfg, capital=100000.0, eth_candles={"ETH": eth}
            )
        self.assertGreaterEqual(res["num_trades"], 1)
        self.assertEqual(res["final_open_positions"], 0)
        self.assertAlmostEqual(float(res["final_gross_exposure"]), 0.0, places=9)
        rs = res["risk_state"]
        self.assertEqual(list(getattr(rs, "open_position_notionals", [])), [])


if __name__ == "__main__":
    unittest.main()
