"""2026-11-12 CELL 12: bounce-confirmation gate for rebound-short entry.

Spec (crash-rebound-strategy.pdf): "Only coins that already bounced hard are
worth shorting". `generate_signal` already confirms the crash entry bar via
`confirm_rebound()` (crash_rebound.py:238, called at crash_rebound.py:387), but
the engine's rebound-short entry opened a short on ANY +9% long-target fill with
no bounce confirmation (src/backtest/engine.py:466).

`StrategyConfig.rebound_short_require_bounce_confirm` (src/strategy/config.py:116,
default False) was added as the opt-in gate; the engine never consulted it.
CELL 12 wires the gate: when True, the rebound short may only open when the
target bar itself is a confirming rebound bar (close > open, close in the upper
half of its range) over candles[:idx+1] — no look-ahead. Default False preserves
all existing anchors.

Gap proof: grep showed no test and no engine path consulted
`rebound_short_require_bounce_confirm` or called `confirm_rebound` around the
rebound-short entry; `confirm_rebound` was only used at signal generation.

Failing-tests-first, red->green, traced fixtures, mutation-verified non-vacuous
(mocking confirm_rebound to False must flip the confirming case back to
long-only, proving the gate is actually consulted).
"""
from __future__ import annotations

import unittest
from unittest.mock import patch

from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _cfg(confirm: bool = False) -> StrategyConfig:
    return StrategyConfig(
        enable_eth_hedge=False,
        enable_rebound_short=True,
        entry_next_bar=True,
        avoid_downtrend=False,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
        funding_rate_pct_per_hour=0.0,
        min_daily_volume_usd=0.0,
        time_exit_max_bars=48,
        enable_liquidation_checks=False,
        stop_atr_mult=8.0,
        use_spec_safety_stop=True,
        atr_period=14,
        rebound_short_target_pct=9.0,
        rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
        rebound_lookback=3,
        rebound_min_body_ratio=0.5,
        rebound_short_require_bounce_confirm=confirm,
    )


def _candles(bar2):
    """Bar 0 = signal, bar 1 = entry fill (open 100), bar 2 = long +9% target
    bar (high 110 >= target 109), bar 3 = post-target bar (close 108.5)."""
    return [
        _c("2025-01-01T00:00:00", 101.0, 101.0, 99.0, 99.0),   # signal bar
        _c("2025-01-01T01:00:00", 100.0, 100.5, 99.5, 100.0),  # entry fill bar
        bar2,                                                    # target bar
        _c("2025-01-01T03:00:00", 108.5, 109.0, 108.0, 108.5), # post-target bar
    ]


# Traced values (slippage/commission/funding all 0):
#   signal_index=0 -> entry_next_bar fill at bar 1 open = 100.0
#   target_px = 109.0; bar 2 high 110 >= 109 -> long target hit at idx 2
#   long leg: entry 100.0, exit 109.0, pnl = (109-100)*1000 = 9000.0
#   short entry = 109.0; short exits at bar 3 close 108.5 (time exit),
#   short pnl = (109-108.5)*1000 = +500.0, reason 'time_exit'
_CONFIRMING_BAR = _c("2025-01-01T02:00:00", 108.0, 110.0, 108.0, 109.5)
# close > open and (close-low)/(high-low) = 1.5/2.0 = 0.75 >= 0.5 -> confirms
_NONCONFIRMING_CLOSE_DOWN_BAR = _c("2025-01-01T02:00:00", 109.5, 110.0, 108.5, 109.0)
# close <= open -> does not confirm
_NONCONFIRMING_LOWER_HALF_BAR = _c("2025-01-01T02:00:00", 108.0, 110.0, 108.0, 108.1)
# close > open but (close-low)/(high-low) = 0.1/2.0 = 0.05 < 0.5 -> does not confirm


class _NoCutRS:
    def check_position(self, config, capital, shares, entry_price):
        from types import SimpleNamespace
        return SimpleNamespace(allowed=True, size_shares=shares)

    def apply_cap_cuts(self, capital, config, open_notional=None):
        return []

    def apply_trade(self, *a, **k):
        pass


class TestReboundShortRequiresBounceConfirmation(unittest.TestCase):
    def _sig(self, signal_index=0):
        return Signal(
            symbol="T", side="long", reason="t", entry_price=100.0, stop_price=50.0,
            target_price=109.0, risk_per_share=20.0, timestamp="t0",
            size_shares=1000.0, signal_index=signal_index,
        )

    def test_legacy_default_opens_short_on_any_fill(self):
        """Default (flag False): short opens even on a non-confirming target bar
        — all existing anchors preserved."""
        res = backtest_simple(
            _candles(_NONCONFIRMING_CLOSE_DOWN_BAR), self._sig(),
            config=_cfg(confirm=False), risk_state=_NoCutRS(), capital=100000.0,
        )
        self.assertEqual(res.exit_reason, "target_rebound_short")
        sides = [t["side"] for t in res.trades]
        self.assertEqual(sides, ["long", "short"])
        self.assertEqual(res.trades[0]["reason"], "target")
        self.assertEqual(res.trades[1]["reason"], "time_exit")
        self.assertAlmostEqual(res.trades[0]["entry"], 100.0, places=9)
        self.assertAlmostEqual(res.trades[0]["exit"], 109.0, places=9)
        self.assertAlmostEqual(res.trades[0]["pnl"], 9000.0, places=9)
        self.assertAlmostEqual(res.trades[1]["entry"], 109.0, places=9)
        self.assertAlmostEqual(res.trades[1]["exit"], 108.5, places=9)
        self.assertAlmostEqual(res.trades[1]["pnl"], 500.0, places=9)

    def test_confirmed_bar_opens_short(self):
        """Flag True + confirming target bar: short opens (gate passes)."""
        res = backtest_simple(
            _candles(_CONFIRMING_BAR), self._sig(),
            config=_cfg(confirm=True), risk_state=_NoCutRS(), capital=100000.0,
        )
        self.assertEqual(res.exit_reason, "target_rebound_short")
        sides = [t["side"] for t in res.trades]
        self.assertEqual(sides, ["long", "short"])
        self.assertEqual(res.trades[1]["reason"], "time_exit")
        self.assertAlmostEqual(res.trades[1]["entry"], 109.0, places=9)
        self.assertAlmostEqual(res.trades[1]["exit"], 108.5, places=9)
        self.assertAlmostEqual(res.trades[1]["pnl"], 500.0, places=9)

    def test_non_confirmed_close_down_bar_no_short(self):
        """Flag True + close <= open target bar: NO short, long closes at target."""
        res = backtest_simple(
            _candles(_NONCONFIRMING_CLOSE_DOWN_BAR), self._sig(),
            config=_cfg(confirm=True), risk_state=_NoCutRS(), capital=100000.0,
        )
        self.assertEqual(res.exit_reason, "target")
        self.assertEqual([t["side"] for t in res.trades], ["long"])
        self.assertEqual(res.trades[0]["reason"], "target")
        self.assertAlmostEqual(res.trades[0]["entry"], 100.0, places=9)
        self.assertAlmostEqual(res.trades[0]["exit"], 109.0, places=9)
        self.assertAlmostEqual(res.trades[0]["pnl"], 9000.0, places=9)

    def test_non_confirmed_lower_half_bar_no_short(self):
        """Flag True + close in lower half of range: NO short, long-only target exit."""
        res = backtest_simple(
            _candles(_NONCONFIRMING_LOWER_HALF_BAR), self._sig(),
            config=_cfg(confirm=True), risk_state=_NoCutRS(), capital=100000.0,
        )
        self.assertEqual(res.exit_reason, "target")
        self.assertEqual([t["side"] for t in res.trades], ["long"])

    def test_no_look_ahead_future_confirm_bar_ignored(self):
        """Flag True: a confirming bar AFTER the target bar cannot confirm the
        short — decision uses candles[:idx+1] only (no look-ahead)."""
        confirming_after = _c("2025-01-01T03:00:00", 100.0, 110.0, 109.9, 110.0)
        # bar 2 non-confirming; bar 3 strongly confirming but outside the window
        candles = [
            _c("2025-01-01T00:00:00", 101.0, 101.0, 99.0, 99.0),
            _c("2025-01-01T01:00:00", 100.0, 100.5, 99.5, 100.0),
            _NONCONFIRMING_CLOSE_DOWN_BAR,
            confirming_after,
        ]
        res = backtest_simple(
            candles, self._sig(), config=_cfg(confirm=True),
            risk_state=_NoCutRS(), capital=100000.0,
        )
        self.assertEqual(res.exit_reason, "target")
        self.assertEqual([t["side"] for t in res.trades], ["long"])

    def test_gate_is_actually_consulted_mock_confirm_false(self):
        """Mutation check: if confirm_rebound is stubbed to False, the
        confirming case collapses to long-only — proves the gate is consulted,
        not dead code."""
        with patch("src.backtest.engine.confirm_rebound", return_value=False):
            res = backtest_simple(
                _candles(_CONFIRMING_BAR), self._sig(),
                config=_cfg(confirm=True), risk_state=_NoCutRS(), capital=100000.0,
            )
        self.assertEqual(res.exit_reason, "target")
        self.assertEqual([t["side"] for t in res.trades], ["long"])


if __name__ == "__main__":
    unittest.main()
