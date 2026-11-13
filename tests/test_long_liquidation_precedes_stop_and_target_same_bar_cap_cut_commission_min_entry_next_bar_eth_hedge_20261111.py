"""Material regression lock (2026-11-11T02:52:32Z, uncovered precedence cell).

Uncovered interaction: on the same hourly bar the long liquidation threshold is
breached (worst-price low) while the bar is ALSO at/below the 8x safety stop and
at/above the +9% target, under equal-share cap-cut + commission_min +
entry_next_bar + aligned ETH hedge + nonzero funding.

Engine/spec ordering must hold: liquidation is checked before stop before target.
The long coin and ETH hedge close on the liquidation bar at worst hourly prices,
liquidation penalty and per-leg hourly funding settle on executed (cap-cut,
commission_min-adjusted) notionals, DailyRiskState realizes the net long-leg
settlement, `max_live_coin_notional` reflects executed coin entry notional, and
no rebound short is opened (liquidation distinct from target-hit stop).

Distinct from `test_long_liquidation_vs_stop_ordering.py` (simple liq-vs-stop,
no cap/commission/entry_next_bar/hedge/funding/reconciliation) and
`test_long_liquidation_cap_cut_eth_hedge_commission_min_entry_next_bar_20261109.py`
/ `...no_usable_eth_hedge...` (cap-cut+commission_min+entry_next_bar liquidation
but stop/target not touchable on liquidation bar).

Synthetic fixtures only (non-evidence); hourly engine only.
"""
from __future__ import annotations

import unittest

from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


class _CapCutRS:
    open_positions = 1
    gross_exposure = 80000.0
    open_position_notionals = [80000.0]

    def __init__(self):
        self.calls = []
        self._last_open = None

    def check_position(self, config, capital, shares, entry_price):
        from types import SimpleNamespace

        return SimpleNamespace(allowed=True, size_shares=shares)

    def apply_cap_cuts(self, capital, config, open_notional=None):
        capv = capital * config.gross_cap_pct / 100.0
        n = len(open_notional or [])
        cuts = [capv / n] * n if n else []
        # Mirror real risk_state contract: engine treats a cap-cut application as
        # having recorded/persisted the (cut) open position, so it skips a separate
        # opened apply_trade. Record the open here to make close-settlement observable.
        if cuts and self._last_open is not None:
            ts, notional = self._last_open
            self.calls.append((ts, 0.0, True, False, cuts[-1]))
            self._last_open = None
        return cuts

    def apply_trade(self, ts, pnl, opened=False, closed=False, notional=0.0):
        if opened and not closed:
            # Stash until apply_cap_cuts resolves the executed (possibly cut) notional.
            self._last_open = (ts, notional)
            return
        self.calls.append((ts, pnl, opened, closed, notional))


def _cfg(**ov):
    d = dict(
        enable_eth_hedge=True,
        enable_rebound_short=True,
        entry_next_bar=True,
        avoid_downtrend=False,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=1.0,
        funding_rate_pct_per_hour=0.01,
        min_daily_volume_usd=0.0,
        time_exit_max_bars=200,
        enable_liquidation_checks=True,
        liquidation_maint_margin_pct=5.0,
        liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5,
        gross_cap_pct=120.0,
        hedge_vol_lookback_hours=336,
        rebound_short_target_pct=9.0,
        rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
    )
    d.update(ov)
    return StrategyConfig(**d)


def _sig():
    return Signal(
        symbol="T",
        side="long",
        reason="t",
        entry_price=100.0,
        stop_price=95.0,      # touchable on liq bar low (93.0 <= 95.0)
        target_price=109.0,   # touchable on liq bar high (110.0 >= 109.0)
        risk_per_share=5.0,
        timestamp="t5",
        size_shares=1000.0,
        signal_index=5,
    )


def _scenario():
    """Deterministic coin/ETH histories yielding nonzero ETH hedge and a single
    liquidation bar (8) that simultaneously breaches liquidation and is also
    at/below stop and at/above target.
    """
    n = 40
    coin = []
    eth = []
    cp = 100.0
    ep = 2000.0
    for i in range(n):
        cm = 1.015 if i % 2 == 0 else 0.985
        em = 1.008 if i % 2 == 0 else 0.992
        co, cc = cp, cp * cm
        ch, cl = max(co, cc) * 1.002, min(co, cc) * 0.998
        eo, ec = ep, ep * em
        eh, el = max(eo, ec) * 1.001, min(eo, ec) * 0.999
        coin.append(_c(f"b{i}", co, ch, cl, cc))
        eth.append(_c(f"h{i}", eo, eh, el, ec))
        cp, ep = cc, ec
    # Entry fills next bar (6) with commission_min + cap-cut.
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
    eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
    # Bar 8: low breaches liq (93.0 < ~94.0 threshold), low <= stop (95.0),
    # high >= target (109.0). Liquidation must win.
    coin[8] = _c("e8", 100.0, 110.0, 93.0, 99.0)
    eth[8] = _c("h8", 2050.0, 2100.0, 2000.0, 2070.0)
    return coin, eth


class TestLongLiquidationPrecedesStopAndTargetSameBar(unittest.TestCase):
    def test_liquidation_wins_and_settles_fully_with_aligned_hedge(self):
        coin, eth = _scenario()
        rs = _CapCutRS()
        res = backtest_simple(coin, _sig(), config=_cfg(), risk_state=rs, eth_candles=eth, capital=100000.0)

        # Ordering/exit identity: liquidation must beat stop and target on same bar.
        self.assertEqual(res.exit_reason, "liquidated")
        self.assertEqual(res.bars_held, 3)  # idx 8 - start_idx 6 + 1
        self.assertIsNotNone(res.trades)
        self.assertEqual(len(res.trades), 1)
        long_leg = res.trades[0]
        self.assertEqual(long_leg["side"], "long")
        self.assertEqual(long_leg["reason"], "liquidated")
        self.assertEqual(res.rebound_short_pnl, 0.0)
        self.assertEqual(res.rebound_hedge_pnl, 0.0)

        # Traced expected (cap-cut 60k, commission_min 1.0, entry_next_bar open e6).
        self.assertAlmostEqual(res.entry_price, 100.001, places=12)
        self.assertAlmostEqual(res.shares, 599.9940000599994, places=12)
        self.assertAlmostEqual(res.exit_price, 92.99833331666666, places=12)
        self.assertAlmostEqual(res.max_live_coin_notional, 60000.0, places=9)

        # Long liquidation settlement: gross + penalty + hourly funding (3h, 0.01%/h).
        self.assertAlmostEqual(res.pnl, -4519.557994420063, places=9)

        # Aligned short ETH hedge (sized from [:start_idx+1] no-look-ahead history),
        # closed same liquidation bar at ETH bar 8 close with sell/buy commission_min.
        self.assertEqual(res.hedge_side, "short")
        self.assertAlmostEqual(res.hedge_size, 56.29769666891872, places=12)
        self.assertAlmostEqual(res.hedge_entry, 1999.9822372839535, places=12)
        self.assertAlmostEqual(res.hedge_exit, 2070.0177627160465, places=12)
        self.assertAlmostEqual(res.hedge_pnl, -3909.060448822962, places=9)

        self.assertAlmostEqual(res.total_pnl, -8428.618443243024, places=9)
        self.assertAlmostEqual(res.pnl + res.hedge_pnl, res.total_pnl, places=12)
        self.assertAlmostEqual(long_leg["pnl"], res.pnl, places=12)

        # Engine realizes close settlement on liquidation path (total_pnl = coin +
        # hedge) at liquidation bar; risk_state settles the full long-leg
        # settlement per CELL 14 (engine.py:350). TradeResult.hedge_pnl/total_pnl
        # expose the same totals separately. Assert executed close accounting.
        closes = [c for c in rs.calls if c[3]]
        self.assertEqual(len(closes), 1)
        close = closes[0]
        self.assertEqual(close[0], "e8")
        self.assertFalse(close[2])
        self.assertTrue(close[3])
        self.assertAlmostEqual(close[1], res.total_pnl, places=9)
        self.assertAlmostEqual(close[4], res.entry_price * res.shares, places=9)

    def test_funding_on_vs_off_delta_reconciles_both_legs(self):
        coin, eth = _scenario()
        on = backtest_simple(coin, _sig(), config=_cfg(funding_rate_pct_per_hour=0.01),
                             risk_state=_CapCutRS(), eth_candles=eth, capital=100000.0)
        off = backtest_simple(coin, _sig(), config=_cfg(funding_rate_pct_per_hour=0.0),
                              risk_state=_CapCutRS(), eth_candles=eth, capital=100000.0)
        self.assertEqual(on.exit_reason, "liquidated")
        self.assertEqual(off.exit_reason, "liquidated")
        # Long pays funding (cost) and short hedge receives funding (benefit).
        # hours=3, coin_notional=60000 => -18.0; hedge_notional~112595.39333783743 => +33.77831800135123
        expected_delta = -18.0 + 33.77831800135123
        self.assertAlmostEqual(on.total_pnl - off.total_pnl, expected_delta, places=9)


if __name__ == "__main__":
    unittest.main()
