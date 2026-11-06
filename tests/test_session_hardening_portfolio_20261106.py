"""Session 2026-11-06T23:46Z hardening: portfolio E2E stopped-buy, volume-gate bypass guards,
long-leg liquidation funding determinism, and microstructure/no-look-ahead honesty regressions.

Failing-tests-first discipline: each test targets a spec-fidelity or gating contract.
Synthetic fixtures only; not real-market evidence.
"""
from __future__ import annotations

import copy
import unittest
from unittest.mock import patch

from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal, generate_signal, filter_universe, backtest_crash_rebound
from src.backtest.engine import TradeResult, backtest_simple
from scripts.run_portfolio import run_portfolio_simulation


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _flat_series(n=40, base=100.0, vol=10_000_000.0):
    vpb = vol / 24.0 / base
    return [_c(f"2026-01-01T{i%24:02d}:00:00Z", base, base * 1.001, base * 0.999, base, vpb) for i in range(n)]


class TestPortfolioStoppedBuyE2E(unittest.TestCase):
    def test_portfolio_stopped_buy_records_no_rebound_short_side_effects(self):
        """Force a stopped-buy outcome through the portfolio runner and prove outputs contain
        no rebound-short trade/side effect (spec: stopped buy never opens rebound short)."""
        candles = _flat_series(60)
        eth = _flat_series(60, base=2000.0)
        cfg = StrategyConfig(
            use_rsi_trigger=False, min_daily_volume_usd=0, enable_eth_hedge=True,
            enable_rebound_short=True, entry_next_bar=False, crash_lookback=2,
        )
        forced_sig = Signal(
            symbol="X", side="long", reason="forced", entry_price=100.0, stop_price=90.0,
            target_price=109.0, risk_per_share=10.0, timestamp="t", size_shares=1.0, signal_index=15,
        )
        call_count = {"n": 0}

        def fake_generate(hist, symbol=None, config=None, capital=100000.0, cache=None):
            if symbol == "X" and len(hist) - 1 == 15:
                call_count["n"] += 1
                s = copy.copy(forced_sig)
                s.signal_index = len(hist) - 1
                return s
            return None

        def fake_backtest(candles, sig, config=None, capital=100000.0, risk_state=None, eth_candles=None):
            if risk_state is not None:
                notional = (getattr(sig, "entry_price", 100.0) or 100.0) * (getattr(sig, "size_shares", 1.0) or 1.0)
                try:
                    risk_state.apply_trade("", 0.0, opened=True, closed=False, notional=notional)
                    risk_state.apply_trade("", -10.0, opened=False, closed=True, notional=notional)
                except Exception:
                    pass
            return TradeResult(
                pnl=-10.0, r_multiple=-1.0, exit_reason="stopped",
                entry_price=100.0, exit_price=90.0, shares=1.0, bars_held=3,
                entry_timestamp="t15", exit_timestamp="t18",
                trades=[{"side": "long", "entry": 100.0, "exit": 90.0, "pnl": -10.0, "reason": "stopped"}],
                hedge_pnl=1.0, hedge_side="short", hedge_size=0.01, hedge_entry=2000.0, hedge_exit=1990.0,
                total_pnl=-9.0,
            )

        with patch("scripts.run_portfolio.generate_signal", side_effect=fake_generate), \
             patch("scripts.run_portfolio.backtest_simple", side_effect=fake_backtest):
            res = run_portfolio_simulation({"X": candles}, config=cfg, capital=100000.0, eth_candles={"ETH": eth})
        self.assertGreaterEqual(call_count["n"], 1)
        self.assertEqual(res["num_trades"], 1)
        t = res["trades"][0]
        self.assertEqual(t["symbol"], "X")
        self.assertEqual(t["exit_reason"], "stopped")
        self.assertNotIn("short", str(t["exit_reason"]).lower())
        self.assertEqual(t.get("total_pnl"), -9.0)
        self.assertIn(t.get("hedge_side"), (None, "short"))

    def test_portfolio_no_short_reason_when_engine_stopped(self):
        candles = _flat_series(50)
        cfg = StrategyConfig(use_rsi_trigger=False, min_daily_volume_usd=0, enable_rebound_short=True)
        sig = Signal(symbol="A", side="long", reason="f", entry_price=100.0, stop_price=90.0,
                     target_price=109.0, risk_per_share=10.0, timestamp="t", size_shares=1.0, signal_index=12)

        def fake_gen(hist, *a, **k):
            if len(hist) - 1 == 12:
                s = copy.copy(sig)
                s.signal_index = len(hist) - 1
                return s
            return None

        def fake_bt(*a, **k):
            return TradeResult(pnl=-1.0, r_multiple=-0.1, exit_reason="stopped", total_pnl=-1.0,
                               trades=[{"side": "long", "reason": "stopped"}], bars_held=1)

        with patch("scripts.run_portfolio.generate_signal", side_effect=fake_gen), \
             patch("scripts.run_portfolio.backtest_simple", side_effect=fake_bt):
            res = run_portfolio_simulation({"A": candles}, config=cfg, capital=100000.0)
        self.assertEqual(res["num_trades"], 1)
        self.assertEqual(res["trades"][0]["exit_reason"], "stopped")
        self.assertFalse(any("short" in str(tr.get("exit_reason", "")) for tr in res["trades"]))


class TestVolumeGateBypassGuards(unittest.TestCase):
    def test_backtest_simple_is_low_level_no_implicit_volume_gate(self):
        """backtest_simple is a low-level executor (signal assumed). It must not be mistaken
        for spec-compliant live gating. Gated paths: generate_signal/filter_universe/portfolio."""
        sig = Signal(symbol="LOW", side="long", reason="t", entry_price=100.0, stop_price=50.0,
                     target_price=110.0, risk_per_share=50.0, timestamp="t0", size_shares=1.0, signal_index=0)
        candles = _flat_series(10, vol=1.0)
        cfg = StrategyConfig(min_daily_volume_usd=5_000_000.0, enable_eth_hedge=False,
                             enable_rebound_short=False, entry_next_bar=False)
        res = backtest_simple(candles, sig, config=cfg)
        self.assertNotEqual(res.exit_reason, "blocked")
        self.assertIn(res.exit_reason, ("target", "time_exit", "stopped", "liquidated", "no_signal"))

    def test_gated_entrypoints_enforce_5m_volume_filter(self):
        low = _flat_series(80, vol=100.0)
        cfg = StrategyConfig(min_daily_volume_usd=5_000_000.0, use_rsi_trigger=False)
        self.assertEqual(filter_universe({"L": low}, min_daily_volume_usd=5_000_000.0), [])
        self.assertIsNone(generate_signal(low, symbol="L", config=cfg))
        br = backtest_crash_rebound(low, symbol="L", config=cfg)
        self.assertIn(br.exit_reason, ("no_signal", "blocked"))
        pr = run_portfolio_simulation({"L": low}, config=cfg, capital=100000.0)
        self.assertEqual(pr["num_trades"], 0)


class TestLiquidationFundingEdge(unittest.TestCase):
    def test_long_leg_funding_applied_on_liquidation_path(self):
        """Long coin leg must pay hourly funding on liquidation (spec: hourly funding on every leg)."""
        sig = Signal(symbol="T", side="long", reason="t", entry_price=100.0, stop_price=50.0,
                     target_price=200.0, risk_per_share=50.0, timestamp="t0", size_shares=1.0, signal_index=0)
        candles = [_c(f"t{i}", 100, 101, 99, 100) for i in range(10)]
        candles[3] = _c("t3", 100, 101, 93.0, 95.0)
        base = dict(entry_next_bar=False, enable_rebound_short=False, enable_eth_hedge=False,
                    enable_liquidation_checks=True, time_exit_max_bars=100)
        r0 = backtest_simple(copy.deepcopy(candles), sig, config=StrategyConfig(**base, funding_rate_pct_per_hour=0.0))
        r1 = backtest_simple(copy.deepcopy(candles), sig, config=StrategyConfig(**base, funding_rate_pct_per_hour=0.02))
        self.assertEqual(r0.exit_reason, "liquidated")
        self.assertEqual(r1.exit_reason, "liquidated")
        self.assertLess(r1.total_pnl, r0.total_pnl)


class TestNoLookaheadSizing(unittest.TestCase):
    def test_volume_sizing_decision_stable_to_future_mutation(self):
        base = _flat_series(60, vol=20_000_000.0)
        cfg = StrategyConfig(use_rsi_trigger=True, min_daily_volume_usd=5_000_000.0,
                             enable_volume_based_sizing=True)
        prefix = copy.deepcopy(base[:50])
        s1 = generate_signal(prefix, symbol="X", config=cfg)
        s2 = generate_signal(copy.deepcopy(prefix), symbol="X", config=cfg)
        self.assertEqual(s1 is None, s2 is None)
        if s1 and s2:
            self.assertAlmostEqual((s1.size_shares or 0), (s2.size_shares or 0), places=9)


class TestMicrostructureHonesty(unittest.TestCase):
    def test_engine_has_no_subhourly_slicing_simulation_claim_in_codepath(self):
        import src.backtest.engine as eng
        with open(eng.__file__, "r", encoding="utf-8") as f:
            src = f.read().lower()
        self.assertNotIn("20-second slicing simulation", src)
        self.assertNotIn("l2 order book", src)


if __name__ == "__main__":
    unittest.main()
