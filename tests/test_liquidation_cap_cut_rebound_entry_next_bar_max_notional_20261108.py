"""Material 2b regression lock (2026-11-08T11:56:46Z, failing-tests-first).

Covers the unproven interaction: liquidation worst-price + sequencing under
entry_next_bar × cap-cut-adjusted shares/notional × rebound short where short
entry notional > long entry notional (slippage/commission active). Verifies
TradeResult.max_live_coin_notional captures the larger rebound-short leg and
portfolio reservation/exposure reconciles to zero after terminal liquidation.

Synthetic fixtures only; not performance evidence; no real market data; no look-ahead.
Hourly engine only (no 20s slicing / explicit spread / L2).
"""
from __future__ import annotations

import copy
import unittest
from unittest.mock import patch

from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _coin(n):
    return [_c(f"2025-01-01T{i % 24:02d}:00:00", 100.0, 101.0, 99.0, 100.0) for i in range(n)]


class TestLiquidationCapCutReboundEntryNextBarMaxNotional(unittest.TestCase):
    def _cfg(self, **kw):
        d = dict(
            enable_eth_hedge=False,
            enable_rebound_short=True,
            entry_next_bar=True,
            avoid_downtrend=False,
            slippage_pct=0.01,  # 1% fraction => 100 bps; makes short entry notional > long
            commission_per_share=0.0,
            commission_min=0.0,
            funding_rate_pct_per_hour=0.0,
            min_daily_volume_usd=0.0,
            time_exit_max_bars=200,
            enable_liquidation_checks=True,
            liquidation_maint_margin_pct=5.0,
            liquidation_buffer_pct=1.0,
            liquidation_penalty_pct=0.5,
            gross_cap_pct=120.0,
            rebound_short_time_exit_bars=48,
        )
        d.update(kw)
        return StrategyConfig(**d)

    def test_cap_cut_entry_next_bar_rebound_short_liquidation_max_live_notional_and_penalty(self):
        """Cap cuts reduce long shares at admission (entry_next_bar). Long hits target
        (re-anchored to executed entry), rebound short opens at executed short entry
        (sell slip). Short notional can exceed long notional; rebound short then
        liquidates at worst high. Verify: post-cut shares used throughout, short
        liquidation penalty base is executed short notional (post-cut shares),
        max_live_coin_notional == max(long notional, short notional), sequencing
        (liq checked first) holds, and portfolio reservation reconciles to zero."""
        candles = _coin(60)
        # signal at idx 5, fill at idx 6 open=100 => long entry 101 (1% buy slip)
        candles[6] = _c("2025-01-01T06:00:00", 100.0, 100.5, 99.0, 99.5)
        # target 109 from signal; re-anchored to 109 * (101/100) = 110.09
        # bar 10 high must breach 110.09
        candles[10] = _c("2025-01-01T10:00:00", 100.0, 112.0, 99.0, 109.0)
        # short entry: sell slip on 110.09 => 110.09 * 0.99 = 108.9891
        # liq threshold short: 108.9891 * 1.06 = 115.528446
        candles[13] = _c("2025-01-01T13:00:00", 115.0, 118.0, 114.0, 117.0)

        sig = Signal(
            symbol="T", side="long", reason="t", entry_price=100.0, stop_price=80.0,
            target_price=109.0, risk_per_share=20.0, timestamp="t5",
            size_shares=1000.0, signal_index=5,
        )

        # Existing 80k notional; new wants 101k (1000 shares * 101 fill) => total 181k > 120k cap.
        # Equal share old+new => 60k each. Post-cut shares = 60000/101.
        class RS:
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

        cfg = self._cfg()
        res = backtest_simple(candles, sig, config=cfg, risk_state=RS(), capital=100000.0)

        long_leg = next((t for t in (res.trades or []) if t.get("side") == "long"), None)
        short_leg = next((t for t in (res.trades or []) if t.get("side") == "short"), None)
        self.assertIsNotNone(long_leg, res.trades)
        self.assertIsNotNone(short_leg, res.trades)
        self.assertEqual(long_leg["reason"], "target")
        self.assertEqual(short_leg["reason"], "liquidated")

        # Post-cut shares: 60000 / 101
        expected_shares = 60000.0 / 101.0
        self.assertAlmostEqual(res.shares, expected_shares, places=9)
        self.assertAlmostEqual(res.entry_price, 101.0, places=9)

        # Re-anchored target exit: 109 * (101/100) = 110.09, sell slip => 108.9891
        expected_long_exit = 110.09 * 0.99
        self.assertAlmostEqual(long_leg["exit"], expected_long_exit, places=9)

        # Short entry = sell slip on long target-exit price
        expected_short_entry = expected_long_exit * 0.99
        self.assertAlmostEqual(short_leg["entry"], expected_short_entry, places=9)
        # Short liq at worst high 118, buy slip => 118 * 1.01
        expected_short_exit = 118.0 * 1.01
        self.assertAlmostEqual(short_leg["exit"], expected_short_exit, places=9)

        # Penalty base is executed short notional (post-cut shares)
        expected_short_notional = expected_short_entry * expected_shares
        expected_long_notional = 101.0 * expected_shares
        expected_penalty = 0.005 * expected_short_notional
        gross_short = (expected_short_entry - expected_short_exit) * expected_shares
        self.assertAlmostEqual(short_leg["pnl"], gross_short - expected_penalty, places=9)

        # max_live_coin_notional must capture the larger leg (compare short vs long executed notionals)
        self.assertAlmostEqual(
            res.max_live_coin_notional,
            max(expected_long_notional, expected_short_notional),
            places=9,
        )

    def test_portfolio_reconciles_cap_cut_entry_next_bar_rebound_short_liquidation(self):
        """Portfolio reservation/exposure reconciles after cap-cut admission with
        entry_next_bar where position hits target, opens rebound short (larger notional
        possible via executed pricing), then rebound short liquidates. Real engine."""
        from scripts.run_portfolio import run_portfolio_simulation
        import scripts.run_portfolio as rp
        from src.strategy.risk import RiskState as Base

        recorded = []

        class Rec(Base):
            def apply_cap_cuts(self, capital, config, open_notional=None):
                incoming = list(open_notional) if open_notional is not None else list(self.open_position_notionals)
                out = super().apply_cap_cuts(capital, config, open_notional)
                recorded.append((incoming, list(out)))
                return out

        n = 140
        a = [_c(f"t{i:04d}", 100.0, 101.0, 99.0, 100.0) for i in range(n)]
        b = [_c(f"t{i:04d}", 100.0, 101.0, 99.0, 100.0) for i in range(n)]
        # A: fill idx21, target idx25, rebound short liq idx28
        a[21] = _c("t0021", 100.0, 100.5, 99.0, 99.5)
        a[25] = _c("t0025", 100.0, 112.0, 99.0, 109.0)
        a[28] = _c("t0028", 115.0, 118.0, 114.0, 117.0)
        # B: fill idx21, time-ish target later but make it liquidate as long to force mixed path? keep simple: liquidate
        b[25] = _c("t0025", 96.0, 97.0, 93.0, 93.5)

        cfg = StrategyConfig(
            use_rsi_trigger=False, min_daily_volume_usd=0.0, enable_eth_hedge=False,
            enable_rebound_short=True, enable_liquidation_checks=True, entry_next_bar=True,
            enable_volume_based_sizing=False, gross_cap_pct=120.0, max_positions=10,
            avoid_downtrend=False, regime_min_price=1.0, crash_lookback=5,
            slippage_pct=0.01, commission_per_share=0.0, commission_min=0.0,
            funding_rate_pct_per_hour=0.0, liquidation_maint_margin_pct=5.0,
            liquidation_buffer_pct=1.0, liquidation_penalty_pct=0.5,
            rebound_short_time_exit_bars=48,
        )
        signals = {
            "A": Signal(symbol="A", side="long", reason="a", entry_price=100.0, stop_price=80.0,
                        target_price=109.0, risk_per_share=20.0, timestamp="t0020",
                        size_shares=700.0, signal_index=20),
            "B": Signal(symbol="B", side="long", reason="b", entry_price=100.0, stop_price=80.0,
                        target_price=150.0, risk_per_share=20.0, timestamp="t0020",
                        size_shares=700.0, signal_index=20),
        }

        def fake_gen(hist, symbol=None, config=None, capital=100000.0, cache=None):
            if symbol in signals and len(hist) - 1 == 20:
                s = copy.copy(signals[symbol])
                s.signal_index = len(hist) - 1
                return s
            return None

        with patch.object(rp, "RiskState", Rec), patch("scripts.run_portfolio.generate_signal", side_effect=fake_gen):
            res = run_portfolio_simulation({"A": a, "B": b}, config=cfg, capital=100000.0)

        self.assertEqual(res["num_trades"], 2)
        self.assertEqual(res["final_open_positions"], 0)
        self.assertAlmostEqual(float(res["final_gross_exposure"]), 0.0, places=9)
        self.assertEqual(list(getattr(res["risk_state"], "open_position_notionals", ["leak"])), [])
        by = {t["symbol"]: t for t in res["trades"]}
        self.assertEqual(by["B"]["exit_reason"], "liquidated")
        # A completed target->rebound path and rebound short liquidated (terminal reconciliation is the key)
        self.assertIn("rebound", by["A"].get("exit_reason", ""))
        self.assertTrue(any(len(o) == 2 for _, o in recorded), recorded)


if __name__ == "__main__":
    unittest.main()
