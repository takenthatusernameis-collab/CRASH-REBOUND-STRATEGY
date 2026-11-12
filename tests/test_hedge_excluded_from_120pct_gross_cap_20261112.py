"""2026-11-12 CELL 11: ETH hedge is NOT counted toward the 120% gross-positions cap.

Spec (crash-rebound-strategy.pdf): "Buys/shorts together capped at 120% of vault
(coin positions cap context); hedges on top". The 120% gross cap applies to COIN
positions only; the ETH hedge sits on top and may push gross exposure including
hedges to high multiples (the PDF explicitly allows ~4.8x in busy hours). A hedge
folded into the 120% cap forces equal-share cuts against hedge notional and can
starve the coin book of its spec-entitled share.

Failing-tests-first. This test pins the invariant at the portfolio runner level by
comparing the SAME two-candidate crash book once WITH hedges established and once
WITHOUT: the admitted COIN notional per trade must be identical in both runs. If a
bug folded the hedge notional into the 120% cap, the hedged run would cut coin
notionals differently from the unhedged run.
"""
from __future__ import annotations

import copy
import unittest
from unittest.mock import patch

from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from scripts.run_portfolio import run_portfolio_simulation


def _series(n: int = 80, base: float = 100.0, vol: float = 10_000_000.0, drift: float = 0.0):
    """Series with non-zero realized volatility so ETH hedge can size."""
    vpb = vol / 24.0 / max(base, 1.0)
    candles = []
    price = base
    for i in range(n):
        move = 0.01 if i % 2 == 0 else -0.009
        o = price
        c = price * (1.0 + move + drift)
        h = max(o, c) * 1.002
        l = min(o, c) * 0.998
        candles.append({
            "timestamp": f"2026-01-01T{i % 24:02d}:00:00Z",
            "open": o, "high": h, "low": l, "close": c, "volume": vpb,
        })
        price = c
    return candles


def _forced_signal(symbol: str, i: int = 15, size_shares: float = 600.0):
    return Signal(
        symbol=symbol, side="long", reason="forced", entry_price=100.0, stop_price=90.0,
        target_price=109.0, risk_per_share=10.0, timestamp="t", size_shares=size_shares,
        signal_index=i,
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
        gross_cap_pct=120.0,
    )
    defaults.update(kw)
    return StrategyConfig(**defaults)


def _patch_two_candidates():
    emitted = {}

    def fake_generate(hist, symbol=None, config=None, capital=100000.0, cache=None):
        if symbol in ("BTC", "SOL") and len(hist) - 1 == 15:
            s = copy.copy(_forced_signal(symbol, i=15, size_shares=600.0))
            s.symbol = symbol
            s.signal_index = len(hist) - 1
            emitted[symbol] = s
            return s
        return None

    return fake_generate


def _coin_notionals(res):
    """Admitted coin notional per symbol (entry_price * shares), keyed by symbol."""
    out = {}
    for t in res["trades"]:
        px = float(t.get("entry_price") or 0.0)
        sh = float(t.get("shares") or 0.0)
        out[t["symbol"]] = px * sh
    return out


class TestHedgeExcludedFrom120PctGrossCap(unittest.TestCase):
    def test_hedged_coin_notional_matches_unhedged_coin_notional(self):
        """Same two-candidate crash book: WITH vs WITHOUT hedges, admitted COIN
        notionals must be identical. A hedge folded into the 120% cap would cut the
        hedged book harder (or starve it) and break this parity."""
        cfg = _cfg()
        gen = _patch_two_candidates()
        candles_by_symbol = {"BTC": _series(), "SOL": _series()}

        # Unhedged baseline: no ETH candles, hedge disabled.
        with patch("scripts.run_portfolio.generate_signal", side_effect=gen):
            unhedged = run_portfolio_simulation(
                dict(candles_by_symbol), config=_cfg(enable_eth_hedge=False),
                capital=100000.0, eth_candles=None, require_eth_hedge=False,
            )
        self.assertEqual(unhedged["num_trades"], 2, "both candidates must be admitted")
        base = _coin_notionals(unhedged)

        # Hedged: ETH candles present under the runner's canonical 'ETH' key,
        # hedge enabled. Coin notionals must not move.
        with patch("scripts.run_portfolio.generate_signal", side_effect=gen):
            hedged = run_portfolio_simulation(
                candles_by_symbol, config=cfg,
                capital=100000.0,
                eth_candles={"ETH": _series(n=80, base=2000.0)},
                require_eth_hedge=False,
            )
        self.assertEqual(hedged["num_trades"], 2)
        hedged_coin = _coin_notionals(hedged)

        for sym in base:
            self.assertIn(sym, hedged_coin)
            self.assertAlmostEqual(hedged_coin[sym], base[sym], places=2,
                                   msg=f"coin notional for {sym} changed when hedges were added")

        # Hedges were actually established on every leg (hedge_side set, size>0).
        for t in hedged["trades"]:
            self.assertEqual(t.get("hedge_side"), "short")
            self.assertGreater(float(t.get("hedge_size") or 0.0), 0.0)

        # Coin positions fill the 120% cap (2 x 60k = 120k); hedge sits on top.
        total_coin = sum(base.values())
        self.assertGreaterEqual(total_coin, 119_000.0)
        self.assertLessEqual(total_coin, 121_000.0)


if __name__ == "__main__":
    unittest.main()