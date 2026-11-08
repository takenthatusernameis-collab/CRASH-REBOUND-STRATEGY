"""Material regression lock (2026-11-08T15:06:30Z, 2b narrowed gap).

Uncovered interaction: liquidation worst-price + sequencing under entry_next_bar
with cap-cut-adjusted shares/notional AND commission_min active on fills.
Existing liquidation cap-cut tests use commission_min=0.0; commission_min fill
accounting is separately locked but not combined with cap-cut/liquidation penalty.

Spec non-negotiables exercised: hourly liquidation at worst price with correct
sequencing/notional/timing/penalty; equal-share cuts old+new across 120% gross
cap (cuts only); entry_next_bar fill; fail-closed fee accounting parity
(engine honors commission_min per risk model).

Concrete expected values are pinned to the current spec-consistent behavior:
fills apply max(commission_per_share, commission_min/shares) on post-cut shares;
penalty base is liquidation_penalty_pct% of executed notional (entry_px*shares);
max_live_coin_notional is executed entry notional.

Synthetic fixtures only; not performance evidence; no real market data; no
look-ahead. Hourly engine only (no 20s slicing / explicit spread / L2).
"""
from __future__ import annotations

import unittest

from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _coin(n):
    return [_c(f"2025-01-01T{i % 24:02d}:00:00", 100.0, 101.0, 99.0, 100.0) for i in range(n)]


class _CapCutRS:
    """Minimal risk state: existing open position forces equal-share cap cut."""
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


class TestLiquidationCommissionMinCapCutEntryNextBar(unittest.TestCase):
    def _cfg(self, **kw):
        d = dict(
            enable_eth_hedge=False, enable_rebound_short=False, entry_next_bar=True,
            avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
            commission_min=1.0, funding_rate_pct_per_hour=0.0, min_daily_volume_usd=0.0,
            time_exit_max_bars=200, enable_liquidation_checks=True,
            liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0,
            liquidation_penalty_pct=0.5, gross_cap_pct=120.0,
        )
        d.update(kw)
        return StrategyConfig(**d)

    def test_long_liquidation_commission_min_no_cap_cut_entry_next_bar(self):
        """Control: commission_min with fixed shares (no cap cut) — fee-aware fills
        and penalty on executed notional."""
        candles = _coin(30)
        candles[6] = _c("2025-01-01T06:00:00", 100.0, 100.5, 99.0, 99.5)
        candles[8] = _c("2025-01-01T08:00:00", 96.0, 96.5, 93.0, 93.5)
        sig = Signal(symbol="T", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                     target_price=150.0, risk_per_share=20.0, timestamp="t5",
                     size_shares=10.0, signal_index=5)
        res = backtest_simple(candles, sig, config=self._cfg())
        self.assertEqual(res.exit_reason, "liquidated")
        self.assertAlmostEqual(res.shares, 10.0, places=9)
        # fill open 100, buy commission_min 1.0/10 = 0.1/share
        self.assertAlmostEqual(res.entry_price, 100.1, places=9)
        # liq worst low 93, sell commission_min 0.1/share
        self.assertAlmostEqual(res.exit_price, 92.9, places=9)
        exp_pen = 0.005 * 100.1 * 10.0
        exp_pnl = (92.9 - 100.1) * 10.0 - exp_pen
        self.assertAlmostEqual(res.pnl, exp_pnl, places=9)
        self.assertAlmostEqual(res.max_live_coin_notional, 1001.0, places=9)

    def test_long_liquidation_commission_min_with_cap_cut_entry_next_bar(self):
        """2b gap: cap-cut-adjusted shares + commission_min fills + liquidation
        penalty/notional/reservation consistency under entry_next_bar.

        Existing 80k open + new 100k desired on 100k capital / 120% cap =>
        equal share 60k each (cuts only). Fills/fees/penalty use post-cut shares.
        """
        candles = _coin(30)
        candles[8] = _c("2025-01-01T08:00:00", 96.0, 96.5, 93.0, 93.5)
        sig = Signal(symbol="T", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                     target_price=150.0, risk_per_share=20.0, timestamp="t5",
                     size_shares=1000.0, signal_index=5)
        res = backtest_simple(candles, sig, config=self._cfg(), risk_state=_CapCutRS(), capital=100000.0)
        self.assertEqual(res.exit_reason, "liquidated")
        # Post-cut notional 60k at entry fill 100 (idx6 open), buy commission_min 1.0/shares.
        # Engine applies cap cuts to shares; fill pricing uses resulting share count.
        self.assertAlmostEqual(res.entry_price, 100.001, places=9)
        self.assertAlmostEqual(res.shares, 599.9940000599994, places=9)
        self.assertAlmostEqual(res.exit_price, 92.99833331666666, places=9)
        self.assertAlmostEqual(res.max_live_coin_notional, 60000.0, places=6)
        exp_pen = 0.005 * res.entry_price * res.shares
        exp_pnl = (res.exit_price - res.entry_price) * res.shares - exp_pen
        self.assertAlmostEqual(res.pnl, exp_pnl, places=6)
        # Penalty base remains executed notional (post-cut/post-fee), not pre-cut.
        self.assertAlmostEqual(exp_pen, 0.005 * res.max_live_coin_notional, places=6)

    def test_liquidation_precedes_stop_with_commission_min_and_cap_cut_entry_next_bar(self):
        """Sequencing invariant preserved under commission_min + cap cut."""
        candles = _coin(30)
        candles[8] = _c("2025-01-01T08:00:00", 96.0, 96.5, 93.0, 93.5)
        sig = Signal(symbol="T", side="long", reason="t", entry_price=100.0, stop_price=95.0,
                     target_price=150.0, risk_per_share=5.0, timestamp="t5",
                     size_shares=1000.0, signal_index=5)
        res = backtest_simple(candles, sig, config=self._cfg(), risk_state=_CapCutRS(), capital=100000.0)
        self.assertEqual(res.exit_reason, "liquidated")
        self.assertGreater(res.entry_price, 100.0)  # commission_min applied
        self.assertLess(res.exit_price, 93.0)       # sell commission_min applied


if __name__ == "__main__":
    unittest.main()
