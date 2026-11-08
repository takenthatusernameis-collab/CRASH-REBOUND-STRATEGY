"""Material spec-fidelity regression locks (2026-11-08T11:07:49Z, 2b).

Covers liquidation worst-price + sequencing under entry_next_bar with
cap-cut-adjusted shares/notional, penalty base with commission/slippage active,
and TradeResult.max_live_coin_notional / portfolio reservation reconciliation.

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


class TestLiquidationEntryNextBarCapCutPenalty(unittest.TestCase):
    def _base_cfg(self, **kw):
        d = dict(
            enable_eth_hedge=False, enable_rebound_short=False, entry_next_bar=True,
            avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
            commission_min=0.0, funding_rate_pct_per_hour=0.0, min_daily_volume_usd=0.0,
            time_exit_max_bars=200, enable_liquidation_checks=True,
            liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0,
            liquidation_penalty_pct=0.5, gross_cap_pct=120.0,
        )
        d.update(kw)
        return StrategyConfig(**d)

    def test_long_liquidation_entry_next_bar_uses_fill_bar_worst_price_and_post_slip_notional_penalty(self):
        """entry_next_bar fills at next open (post slippage/commission). Liquidation
        checked first each bar (worst low) using executed entry; penalty base is
        executed notional (entry_px*shares) consistent with spec 'penalty % of notional'."""
        candles = _coin(30)
        # signal at idx 5, fill at idx 6 open=100. buy slippage 1% (0.01 fraction) => entry 101
        candles[6] = _c("2025-01-01T06:00:00", 100.0, 100.5, 99.0, 99.5)
        # liq threshold for long: entry*(1 - (5+1)/100)=entry*0.94. entry 101 => 94.94
        candles[8] = _c("2025-01-01T08:00:00", 96.0, 96.5, 93.0, 93.5)
        sig = Signal(symbol="T", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                     target_price=150.0, risk_per_share=20.0, timestamp="t5",
                     size_shares=10.0, signal_index=5)
        cfg = self._base_cfg(slippage_pct=0.01)
        res = backtest_simple(candles, sig, config=cfg)
        self.assertEqual(res.exit_reason, "liquidated")
        self.assertEqual(res.shares, 10.0)
        self.assertAlmostEqual(res.entry_price, 101.0, places=9)
        # exit at worst low 93.0 with sell slippage 1% => 92.07
        self.assertAlmostEqual(res.exit_price, 92.07, places=9)
        expected_penalty = 0.005 * 101.0 * 10.0
        gross = (92.07 - 101.0) * 10.0
        self.assertAlmostEqual(res.pnl, gross - expected_penalty, places=9)
        self.assertAlmostEqual(res.max_live_coin_notional, 101.0 * 10.0, places=9)

    def test_cap_cut_reduces_shares_and_liquidation_notional_penalty_entry_next_bar(self):
        """apply_cap_cuts runs at admission (old+new equal share). Liquidation penalty
        and max_live_coin_notional must use post-cut shares/notional."""
        candles = _coin(30)
        candles[8] = _c("2025-01-01T08:00:00", 96.0, 96.5, 93.0, 93.5)
        sig = Signal(symbol="T", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                     target_price=150.0, risk_per_share=20.0, timestamp="t5",
                     size_shares=1000.0, signal_index=5)
        # Existing open position 80k notional; new wants 100k; cap 120k => equal 60k each.
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
        cfg = self._base_cfg()
        res = backtest_simple(candles, sig, config=cfg, risk_state=RS(), capital=100000.0)
        self.assertEqual(res.exit_reason, "liquidated")
        # post-cut notional 60k at entry fill 100 (idx6 open) => 600 shares
        self.assertAlmostEqual(res.shares, 600.0, places=9)
        self.assertAlmostEqual(res.entry_price, 100.0, places=9)
        expected_penalty = 0.005 * 100.0 * 600.0
        gross = (93.0 - 100.0) * 600.0
        self.assertAlmostEqual(res.pnl, gross - expected_penalty, places=9)
        self.assertAlmostEqual(res.max_live_coin_notional, 60000.0, places=9)

    def test_liquidation_precedes_stop_on_same_bar_entry_next_bar(self):
        """Sequencing lock under entry_next_bar: liquidation checked before stop."""
        candles = _coin(30)
        candles[8] = _c("2025-01-01T08:00:00", 96.0, 96.5, 93.0, 93.5)
        sig = Signal(symbol="T", side="long", reason="t", entry_price=100.0, stop_price=95.0,
                     target_price=150.0, risk_per_share=5.0, timestamp="t5",
                     size_shares=1.0, signal_index=5)
        res = backtest_simple(candles, sig, config=self._base_cfg())
        self.assertEqual(res.exit_reason, "liquidated")
        self.assertEqual(res.exit_price, 93.0)

    def test_rebound_short_liquidation_penalty_uses_executed_short_notional_with_slippage(self):
        """Rebound short liquidation after target: penalty/notional based on executed
        short entry (post slippage) and max_live_coin_notional reflects max across legs."""
        candles = _coin(60)
        candles[6] = _c("2025-01-01T06:00:00", 100.0, 100.5, 99.0, 99.5)   # fill
        candles[10] = _c("2025-01-01T10:00:00", 100.0, 112.0, 99.0, 109.0)  # target
        # short starts bar11 from executed short entry ~106.8309 (sell slip on 107.91 long target exit)
        # liq threshold ~113.24; bar 13 high 118 breaches.
        candles[13] = _c("2025-01-01T13:00:00", 115.0, 118.0, 114.0, 117.0)
        sig = Signal(symbol="T", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                     target_price=109.0, risk_per_share=20.0, timestamp="t5",
                     size_shares=10.0, signal_index=5)
        cfg = self._base_cfg(enable_rebound_short=True, slippage_pct=0.01, rebound_short_time_exit_bars=48)
        res = backtest_simple(candles, sig, config=cfg)
        long_leg = next((t for t in (res.trades or []) if t.get('side') == 'long'), None)
        short_leg = next((t for t in (res.trades or []) if t.get('side') == 'short'), None)
        self.assertIsNotNone(long_leg, res.trades)
        self.assertIsNotNone(short_leg, res.trades)
        self.assertEqual(long_leg['reason'], 'target')
        self.assertEqual(short_leg['reason'], 'liquidated')
        self.assertAlmostEqual(res.entry_price, 101.0, places=9)
        # entry_next_bar re-anchors target to executed entry: 109.0 * (101.0/100.0) = 110.09, sell slip => 108.9891
        self.assertAlmostEqual(long_leg['exit'], 108.98910000000001, places=9)
        short_entry_expected = 108.98910000000001 * 0.99  # sell slip on long target-exit px
        self.assertAlmostEqual(short_leg['entry'], short_entry_expected, places=9)
        exit_expected = 118.0 * 1.01  # buy slip on worst-high liq price
        self.assertAlmostEqual(short_leg['exit'], exit_expected, places=9)
        expected_pen = 0.005 * short_entry_expected * 10.0
        gross_short = (short_entry_expected - exit_expected) * 10.0
        self.assertAlmostEqual(short_leg['pnl'], gross_short - expected_pen, places=9)
        self.assertAlmostEqual(res.max_live_coin_notional,
                               max(res.entry_price * 10.0, short_entry_expected * 10.0), places=9)


class TestPortfolioReservationLiquidationCapCutEntryNextBar(unittest.TestCase):
    def test_portfolio_reconciles_after_cap_cut_liquidation_entry_next_bar(self):
        """Portfolio reservation/exposure reconciles to zero after cap-cut admission
        that later liquidates under entry_next_bar (real engine + reservation overlay)."""
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

        n = 120
        a = [_c(f"t{i:04d}", 100.0, 101.0, 99.0, 100.0) for i in range(n)]
        b = [_c(f"t{i:04d}", 100.0, 101.0, 99.0, 100.0) for i in range(n)]
        a[25] = _c("t0025", 96.0, 97.0, 93.0, 93.5)
        b[28] = _c("t0028", 96.0, 97.0, 93.0, 93.5)
        cfg = StrategyConfig(
            use_rsi_trigger=False, min_daily_volume_usd=0.0, enable_eth_hedge=False,
            enable_rebound_short=False, enable_liquidation_checks=True, entry_next_bar=True,
            enable_volume_based_sizing=False, gross_cap_pct=120.0, max_positions=10,
            avoid_downtrend=False, regime_min_price=1.0, crash_lookback=5,
            slippage_pct=0.0, commission_per_share=0.0, commission_min=0.0,
            funding_rate_pct_per_hour=0.0, liquidation_maint_margin_pct=5.0,
            liquidation_buffer_pct=1.0, liquidation_penalty_pct=0.5,
        )
        signals = {k: Signal(symbol=k, side="long", reason=k, entry_price=100.0, stop_price=50.0,
                             target_price=150.0, risk_per_share=50.0, timestamp="t0020",
                             size_shares=700.0, signal_index=20) for k in "AB"}
        def fake_gen(hist, symbol=None, config=None, capital=100000.0, cache=None):
            if symbol in signals and len(hist) - 1 == 20:
                s = copy.copy(signals[symbol]); s.signal_index = len(hist) - 1; return s
            return None
        with patch.object(rp, "RiskState", Rec), patch("scripts.run_portfolio.generate_signal", side_effect=fake_gen):
            res = run_portfolio_simulation({"A": a, "B": b}, config=cfg, capital=100000.0)
        self.assertEqual(res["num_trades"], 2)
        self.assertTrue(all(t["exit_reason"] == "liquidated" for t in res["trades"]))
        self.assertEqual(res["final_open_positions"], 0)
        self.assertAlmostEqual(float(res["final_gross_exposure"]), 0.0, places=9)
        self.assertEqual(list(getattr(res["risk_state"], "open_position_notionals", ["leak"])), [])
        self.assertTrue(any(len(o) == 2 and abs(o[0]-o[1]) < 1e-6 for i, o in recorded), recorded)


if __name__ == "__main__":
    unittest.main()
