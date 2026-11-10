"""Spec-compliant ETH-hedge fail-closed: portfolio/real-gated path must not silently run unhedged.

Spec (crash-rebound-strategy.pdf): every trade hedged with ETH. When a
spec-compliant caller opts into ETH hedging, missing/insufficient ETH data must
surface as a hard error (fail-closed) rather than producing a phantom unhedged
execution. Low-level/fixture callers that intentionally omit hedges remain
unaffected (require_eth_hedge defaults False).
"""
from __future__ import annotations

import copy
import unittest
from unittest.mock import patch

from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from scripts.run_portfolio import run_portfolio_simulation


def _series(n=60, base=100.0, vol=10_000_000.0, drift=0.0):
    """Series with non-zero realized volatility (close varies) so ETH hedge can size."""
    vpb = vol / 24.0 / max(base, 1.0)
    candles = []
    price = base
    for i in range(n):
        # alternate up/down to create realized volatility
        move = 0.01 if i % 2 == 0 else -0.009
        o = price
        c = price * (1.0 + move + drift)
        h = max(o, c) * 1.002
        l = min(o, c) * 0.998
        candles.append({
            "timestamp": f"2026-01-01T{i%24:02d}:00:00Z",
            "open": o, "high": h, "low": l, "close": c, "volume": vpb,
        })
        price = c
    return candles


def _forced_signal(i=15):
    return Signal(
        symbol="BTC", side="long", reason="forced", entry_price=100.0, stop_price=90.0,
        target_price=109.0, risk_per_share=10.0, timestamp="t", size_shares=1.0, signal_index=i,
    )


def _cfg(**kw):
    defaults = dict(
        use_rsi_trigger=False,
        crash_pct_drop=-2.0,
        crash_lookback=5,
        enable_rebound_short=False,
        enable_eth_hedge=True,
        enable_volume_based_sizing=False,
        min_daily_volume_usd=0,
        avoid_downtrend=False,
        regime_min_price=0.0,
        entry_next_bar=False,
        max_positions=5,
    )
    defaults.update(kw)
    return StrategyConfig(**defaults)


class TestPortfolioSpecEthHedgeFailClosed(unittest.TestCase):
    def _patch_generate(self, idx=15):
        def fake_generate(hist, symbol=None, config=None, capital=100000.0, cache=None):
            if symbol == "BTC" and len(hist) - 1 == idx:
                s = copy.copy(_forced_signal(idx))
                s.symbol = symbol
                s.signal_index = len(hist) - 1
                return s
            return None
        return fake_generate

    def test_portfolio_requires_eth_hedge_raises_when_eth_missing(self):
        candles = _series()
        cfg = _cfg()
        with patch("scripts.run_portfolio.generate_signal", side_effect=self._patch_generate()):
            with self.assertRaises(ValueError) as ctx:
                run_portfolio_simulation(
                    {"BTC": candles},
                    config=cfg,
                    capital=100000.0,
                    eth_candles=None,
                    require_eth_hedge=True,
                )
        self.assertIn("Spec-compliant ETH hedge required", str(ctx.exception))

    def test_portfolio_requires_eth_hedge_raises_when_eth_insufficient(self):
        candles = _series()
        # Flat/zero-vol ETH -> compute_eth_hedge_size returns 0 (insufficient)
        eth_flat = [{"timestamp": c["timestamp"], "open": 1.0, "high": 1.0, "low": 1.0,
                     "close": 1.0, "volume": 0.0} for c in candles]
        cfg = _cfg()
        with patch("scripts.run_portfolio.generate_signal", side_effect=self._patch_generate()):
            with self.assertRaises(ValueError) as ctx:
                run_portfolio_simulation(
                    {"BTC": candles},
                    config=cfg,
                    capital=100000.0,
                    eth_candles={"ETH": eth_flat},
                    require_eth_hedge=True,
                )
        self.assertIn("Spec-compliant ETH hedge required", str(ctx.exception))

    def test_portfolio_default_does_not_require_eth_hedge(self):
        """Default require_eth_hedge=False preserves low-level/fixture behavior."""
        candles = _series()
        cfg = _cfg()
        with patch("scripts.run_portfolio.generate_signal", side_effect=self._patch_generate()):
            res = run_portfolio_simulation(
                {"BTC": candles},
                config=cfg,
                capital=100000.0,
                eth_candles=None,
            )
        self.assertIsInstance(res, dict)
        self.assertIn("trades", res)
        self.assertEqual(res["num_trades"], 1)

    def test_portfolio_require_eth_hedge_false_explicit_ok(self):
        candles = _series()
        cfg = _cfg()
        with patch("scripts.run_portfolio.generate_signal", side_effect=self._patch_generate()):
            res = run_portfolio_simulation(
                {"BTC": candles},
                config=cfg,
                capital=100000.0,
                eth_candles=None,
                require_eth_hedge=False,
            )
        self.assertIsInstance(res, dict)
        self.assertEqual(res["num_trades"], 1)

    def test_portfolio_require_eth_hedge_ok_when_hedge_established(self):
        """Spec-compliant path succeeds when usable ETH data allows hedge."""
        candles = _series()
        eth = _series(60, base=2000.0)
        cfg = _cfg()
        with patch("scripts.run_portfolio.generate_signal", side_effect=self._patch_generate()):
            res = run_portfolio_simulation(
                {"BTC": candles},
                config=cfg,
                capital=100000.0,
                eth_candles={"ETH": eth},
                require_eth_hedge=True,
            )
        self.assertIsInstance(res, dict)
        self.assertIn("trades", res)
        self.assertEqual(res["num_trades"], 1)


if __name__ == "__main__":
    unittest.main()
