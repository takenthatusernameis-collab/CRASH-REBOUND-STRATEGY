"""API/gating guardrails (2026-11-07): prevent misreading backtest_simple as spec-compliant.

backtest_simple is a LOW-LEVEL executor (signal assumed). It must not be treated as a
volume-gated/spec-compliant entrypoint by production callers. Gated paths:
generate_signal/filter_universe/strategy/portfolio/real-campaign validators.
"""
from __future__ import annotations

import inspect
import unittest

import scripts.run_backtest as run_backtest
import scripts.run_campaign as run_campaign
import scripts.run_portfolio as run_portfolio
import scripts.run_real_campaign as run_real_campaign
from src.backtest.engine import backtest_simple
from src.strategy.crash_rebound import backtest_crash_rebound


class TestBacktestApiGuardrails(unittest.TestCase):
    def test_backtest_simple_docstring_marks_low_level_non_gated(self):
        doc = inspect.getdoc(backtest_simple) or ""
        low = doc.lower()
        self.assertIn("low-level", low)
        self.assertTrue("not" in low and ("volume" in low or "gated" in low or "spec-compliant" in low))

    def test_strategy_wrapper_contract_is_gated_then_executes(self):
        # backtest_crash_rebound delegates through generate_signal (gated) before execution.
        src = inspect.getsource(backtest_crash_rebound)
        self.assertIn("generate_signal", src)
        self.assertIn("backtest_simple", src)

    def test_production_portfolio_and_real_campaign_use_gated_paths(self):
        # run_portfolio gates via filter_universe/generate_signal before backtest_simple.
        psrc = inspect.getsource(run_portfolio)
        self.assertIn("filter_universe", psrc)
        self.assertIn("generate_signal", psrc)
        self.assertIn("backtest_simple", psrc)
        # run_real_campaign must not call backtest_simple directly; it uses portfolio simulation.
        rsrc = inspect.getsource(run_real_campaign)
        self.assertNotIn("backtest_simple", rsrc)
        self.assertIn("run_portfolio_simulation", rsrc)

    def test_run_backtest_is_explicitly_low_level(self):
        src = inspect.getsource(run_backtest)
        low = src.lower()
        self.assertTrue("low-level" in low or "low level" in low or "not volume-gated" in low or "non-gated" in low)

    def test_fixture_campaign_not_claimed_as_real_evidence(self):
        src = inspect.getsource(run_campaign)
        self.assertIn("fixture", src.lower())
        self.assertIn("smoke", src.lower())


if __name__ == "__main__":
    unittest.main()
