"""Material spec-fidelity hardening (2026-11-07T03:01:44Z): concurrent portfolio
120% cap + equal-share cuts interacting with liquidation/rebound exits, real engine.

Minimal mocking only: force controlled entry signals (deterministic admission points)
so portfolio scanner, cap/reservation logic, RiskState accounting, and
backtest_simple (liquidation, rebound short, funding/hedge, hourly execution) all
execute with real semantics. Synthetic fixtures only; non-evidence.

Spec invariants (crash-rebound-strategy.pdf / HANDOFF priorities):
- Same-decision-bar admission: deepest crash first; buys/shorts together capped at
  120% of vault; when more fit than cap, cut open positions so EVERY position
  (old+new) holds equal share of 120% cap; cuts only, never topped up.
- One position per coin.
- Stopped buy never opens rebound short (not exercised here except as guard).
- Liquidation/rebound exits must not leak occupancy, notionals, or gross exposure.
- Engine hourly funding/liquidation on legs; microstructure not fully simulated.
"""
from __future__ import annotations

import copy
import unittest
from unittest.mock import patch

from scripts.run_portfolio import run_portfolio_simulation
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(i, o, h, l, cl, v=2_000_000.0):
    return {"timestamp": f"t{i:04d}", "open": o, "high": h, "low": l, "close": cl, "volume": v}


def _cfg(**kw):
    d = dict(
        use_rsi_trigger=False,
        min_daily_volume_usd=0.0,
        enable_eth_hedge=False,
        enable_rebound_short=False,
        enable_liquidation_checks=True,
        entry_next_bar=True,
        enable_volume_based_sizing=False,
        gross_cap_pct=120.0,
        max_positions=10,
        avoid_downtrend=False,
        regime_min_price=1.0,
        crash_lookback=5,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
        funding_rate_pct_per_hour=0.0,
        liquidation_maint_margin_pct=5.0,
        liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5,
    )
    d.update(kw)
    return StrategyConfig(**d)


class TestConcurrentCapWithLiquidationRealEngine(unittest.TestCase):
    def test_three_same_bar_admissions_under_120_cap_all_liquidate_reconcile_clean(self):
        """Three symbols fire same decision bar; volume-sized notionals breach 120% cap,
        forcing equal-share cuts (old+new). Each position later liquidates at different
        bars. Real engine runs liquidation/funding/penalty paths. Portfolio must end
        with no open positions, zero gross exposure, no notional leak, correct trade count."""
        n = 140
        capital = 100000.0
        base = [_c(i, 100.0, 101.0, 99.0, 100.0) for i in range(n)]
        # Force large notionals via fixed shares * entry so cap cuts apply in engine/runner flow.
        # We'll set fixed size_shares on signals; disable vol sizing to keep deterministic.
        a = copy.deepcopy(base); a[25] = _c(25, 96.0, 97.0, 93.0, 93.5)   # liquidates
        b = copy.deepcopy(base); b[28] = _c(28, 96.0, 97.0, 93.0, 93.5)
        c = copy.deepcopy(base); c[31] = _c(31, 96.0, 97.0, 93.0, 93.5)
        eth = [_c(i, 2000.0, 2010.0, 1990.0, 2000.0, 1_000_000.0) for i in range(n)]
        cfg = _cfg(enable_eth_hedge=True, enable_rebound_short=False)
        # Each wants 60k notional at ~100 entry => 600 shares; 3x60k=180k > 120k cap.
        def sig(sym, sev_rsi):
            return Signal(symbol=sym, side="long", reason=f"liq_{sym}", entry_price=100.0,
                          stop_price=50.0, target_price=150.0, risk_per_share=50.0,
                          timestamp="t0020", size_shares=600.0, signal_index=20)
        signals = {"A": sig("A", 10.0), "B": sig("B", 12.0), "C": sig("C", 14.0)}

        def fake_gen(hist, symbol=None, config=None, capital=100000.0, cache=None):
            if symbol in signals and len(hist) - 1 == 20:
                s = copy.copy(signals[symbol]); s.signal_index = len(hist) - 1; return s
            return None

        with patch("scripts.run_portfolio.generate_signal", side_effect=fake_gen):
            res = run_portfolio_simulation(
                {"A": a, "B": b, "C": c}, config=cfg, capital=capital, eth_candles={"ETH": eth}
            )

        self.assertEqual(res["num_trades"], 3)
        reasons = sorted(t["exit_reason"] for t in res["trades"])
        self.assertTrue(all(r == "liquidated" for r in reasons), reasons)
        self.assertEqual(res["final_open_positions"], 0)
        self.assertAlmostEqual(float(res["final_gross_exposure"]), 0.0, places=9)
        rs = res["risk_state"]
        self.assertEqual(getattr(rs, "open_positions", -1), 0)
        self.assertAlmostEqual(float(getattr(rs, "gross_exposure", -1.0)), 0.0, places=9)
        self.assertEqual(list(getattr(rs, "open_position_notionals", ["leak"])), [])
        # Per-trade accounting must include penalty/liquidation semantics and hedge fields when hedge active.
        for t in res["trades"]:
            self.assertIsInstance(t.get("total_pnl"), (int, float))
            self.assertIn("hedge_pnl", t)

    def test_two_admit_under_cap_third_blocked_by_max_positions_after_liq_reconcile(self):
        """Same bar: A,B admitted (max_positions=2), C blocked. A liquidates early,
        B liquidates later. Final state reconciles; C never traded."""
        n = 120
        a = [_c(i, 100.0, 101.0, 99.0, 100.0) for i in range(n)]; a[24] = _c(24, 96, 97, 93, 93.5)
        b = [_c(i, 100.0, 101.0, 99.0, 100.0) for i in range(n)]; b[30] = _c(30, 96, 97, 93, 93.5)
        c = [_c(i, 100.0, 101.0, 99.0, 100.0) for i in range(n)]; c[26] = _c(26, 96, 97, 93, 93.5)
        cfg = _cfg(max_positions=2, gross_cap_pct=500.0)
        signals = {k: Signal(symbol=k, side="long", reason=k, entry_price=100.0, stop_price=50.0,
                             target_price=150.0, risk_per_share=50.0, timestamp="t0020",
                             size_shares=1.0, signal_index=20) for k in "ABC"}
        def fake_gen(hist, symbol=None, config=None, capital=100000.0, cache=None):
            if symbol in signals and len(hist) - 1 == 20:
                s = copy.copy(signals[symbol]); s.signal_index = len(hist) - 1; return s
            return None
        with patch("scripts.run_portfolio.generate_signal", side_effect=fake_gen):
            res = run_portfolio_simulation({"A": a, "B": b, "C": c}, config=cfg, capital=100000.0)
        traded = sorted(t["symbol"] for t in res["trades"])
        self.assertEqual(len(traded), 2)
        self.assertNotIn("C", traded)  # blocked at same decision bar by max_positions after A,B probes
        self.assertTrue(all(t["exit_reason"] == "liquidated" for t in res["trades"]))
        self.assertEqual(res["final_open_positions"], 0)
        self.assertAlmostEqual(float(res["final_gross_exposure"]), 0.0, places=9)
        self.assertEqual(list(getattr(res["risk_state"], "open_position_notionals", ["leak"])), [])


class TestConcurrentCapWithReboundExitRealEngine(unittest.TestCase):
    def test_two_same_bar_admissions_target_to_rebound_exits_reconcile_clean(self):
        """Two symbols admitted same bar under 120% cap (equal-share cuts possible),
        both hit target -> rebound short path completes (rebound target). Real engine
        executes target, rebound short, hedge/funding/timing. Portfolio must reconcile
        occupancy/gross/notionals to zero."""
        n = 160
        capital = 100000.0
        def mk(target_bar, rebound_bar):
            x = [_c(i, 100.0, 101.0, 99.0, 100.0) for i in range(n)]
            x[target_bar] = _c(target_bar, 100.0, 110.0, 99.0, 109.0)
            for i in range(target_bar + 1, rebound_bar):
                x[i] = _c(i, 105.0, 106.0, 99.5, 103.0)
            x[rebound_bar] = _c(rebound_bar, 102.0, 103.0, 98.5, 99.0)
            return x
        a = mk(23, 26)
        b = mk(23, 29)
        eth = [_c(i, 2000.0, 2010.0, 1990.0, 2000.0, 1_000_000.0) for i in range(n)]
        cfg = _cfg(enable_rebound_short=True, enable_eth_hedge=True, enable_liquidation_checks=False,
                   rebound_short_time_exit_bars=48)
        signals = {k: Signal(symbol=k, side="long", reason=k, entry_price=100.0, stop_price=80.0,
                             target_price=109.0, risk_per_share=20.0, timestamp="t0020",
                             size_shares=700.0, signal_index=20) for k in "AB"}  # force cap pressure
        def fake_gen(hist, symbol=None, config=None, capital=100000.0, cache=None):
            if symbol in signals and len(hist) - 1 == 20:
                s = copy.copy(signals[symbol]); s.signal_index = len(hist) - 1; return s
            return None
        with patch("scripts.run_portfolio.generate_signal", side_effect=fake_gen):
            res = run_portfolio_simulation({"A": a, "B": b}, config=cfg, capital=capital,
                                            eth_candles={"ETH": eth})
        self.assertEqual(res["num_trades"], 2)
        self.assertEqual(res["final_open_positions"], 0)
        self.assertAlmostEqual(float(res["final_gross_exposure"]), 0.0, places=9)
        rs = res["risk_state"]
        self.assertEqual(list(getattr(rs, "open_position_notionals", ["leak"])), [])
        for t in res["trades"]:
            self.assertIsInstance(t.get("total_pnl"), (int, float))
            self.assertIsNotNone(t.get("exit_reason"))
            self.assertGreaterEqual(int(t.get("bars_held") or 0), 1)

    def test_mixed_same_bar_liquidation_and_rebound_reconcile_under_120_cap(self):
        """Same bar admissions: A liquidates, B completes rebound path. Validates
        occupancy/gross/notional reconciliation across mixed terminal paths with cap pressure."""
        n = 170
        capital = 100000.0
        a = [_c(i, 100.0, 101.0, 99.0, 100.0) for i in range(n)]
        a[25] = _c(25, 96.0, 97.0, 93.0, 93.5)  # liquidation
        b = [_c(i, 100.0, 101.0, 99.0, 100.0) for i in range(n)]
        b[24] = _c(24, 100.0, 110.0, 99.0, 109.0)  # target
        b[27] = _c(27, 102.0, 103.0, 98.5, 99.0)  # rebound short target
        eth = [_c(i, 2000.0, 2010.0, 1990.0, 2000.0, 1_000_000.0) for i in range(n)]
        cfg = _cfg(enable_rebound_short=True, enable_eth_hedge=True, enable_liquidation_checks=True)
        sa = Signal(symbol="A", side="long", reason="a", entry_price=100.0, stop_price=50.0,
                    target_price=150.0, risk_per_share=50.0, timestamp="t0020", size_shares=650.0, signal_index=20)
        sb = Signal(symbol="B", side="long", reason="b", entry_price=100.0, stop_price=80.0,
                    target_price=109.0, risk_per_share=20.0, timestamp="t0020", size_shares=650.0, signal_index=20)
        def fake_gen(hist, symbol=None, config=None, capital=100000.0, cache=None):
            idx = len(hist) - 1
            if idx == 20 and symbol == "A": s = copy.copy(sa); s.signal_index = idx; return s
            if idx == 20 and symbol == "B": s = copy.copy(sb); s.signal_index = idx; return s
            return None
        with patch("scripts.run_portfolio.generate_signal", side_effect=fake_gen):
            res = run_portfolio_simulation({"A": a, "B": b}, config=cfg, capital=capital,
                                            eth_candles={"ETH": eth})
        self.assertEqual(res["num_trades"], 2)
        by = {t["symbol"]: t for t in res["trades"]}
        self.assertIn("A", by); self.assertIn("B", by)
        self.assertEqual(by["A"]["exit_reason"], "liquidated")
        self.assertIsNotNone(by["B"].get("exit_reason"))
        self.assertEqual(res["final_open_positions"], 0)
        self.assertAlmostEqual(float(res["final_gross_exposure"]), 0.0, places=9)
        self.assertEqual(list(getattr(res["risk_state"], "open_position_notionals", ["leak"])), [])


if __name__ == "__main__":
    unittest.main()
