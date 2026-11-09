"""Material regression lock (2026-11-09T08:22:00Z, 2b engine uncovered combo).

Uncovered interaction: long-leg liquidation with ETH hedge enabled under
commission_min-adjusted fills + equal-share cap-cut + entry_next_bar + funding.
Locks: liquidation check/settlement at worst hourly price with correct
sequencing/notional/timing/penalty on executed (cap-cut, commission_min)
notional; short ETH hedge sizing from no-look-ahead history (hedge_vol_lookback,
capped by hedge_cap_multiplier), hedge entry aligned to long entry bar idx,
commission_min on all coin/hedge fills; hourly funding on coin long and hedge
short legs; hedge closed same liquidation bar; no rebound short opened;
max_live_coin_notional reserved at executed long-entry notional (hedges excluded);
coin+hedge attribution and total reconciliation.

Spec: hourly liquidation at worst price, correct sequencing/notional/timing/
penalty; hourly funding on every leg and every exit path; ETH hedge every leg
(336h vol ratio, cap 3x); commission_min fill parity; equal-share cuts
(cuts only) old+new; entry_next_bar fill/threshold re-anchor semantics preserved
by engine; stopped buy never opens rebound short (liquidation is distinct but
must not open rebound). Synthetic fixtures only (non-evidence); hourly only.
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

    def check_position(self, config, capital, shares, entry_price):
        from types import SimpleNamespace

        return SimpleNamespace(allowed=True, size_shares=shares)

    def apply_cap_cuts(self, capital, config, open_notional=None):
        capv = capital * config.gross_cap_pct / 100.0
        n = len(open_notional or [])
        return [capv / n] * n if n else []

    def apply_trade(self, *a, **k):
        pass


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
        stop_price=80.0,
        target_price=109.0,
        risk_per_share=20.0,
        timestamp="t5",
        size_shares=1000.0,
        signal_index=5,
    )


def _scenario():
    """Coin/ETH histories with nonzero realized-vol ratio => ETH hedge opens.
    entry_next_bar long fill at bar 6 (open 100). Liquidation at bar 8:
    threshold = entry_px*(1-0.06); executed entry_px includes commission_min
    after cap-cut, so low 93.0 breaches. ETH hedge closed same bar.
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
        cp, ec_p = cc, ec
        ep = ec_p
    # Deterministic entry/liquidation bars.
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
    eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
    coin[8] = _c("e8", 100.0, 101.0, 93.0, 99.0)    # long liquidation
    eth[8] = _c("h8", 2050.0, 2100.0, 2000.0, 2070.0)  # hedge exit
    return coin, eth


class TestLongLiquidationCapCutEthHedgeCommissionMinEntryNextBar(unittest.TestCase):
    def test_long_liquidation_closes_short_eth_hedge_cap_cut_commission_min_funding(self):
        """Long liquidation (worst hourly price) with short ETH hedge, cap-cut
        equal-share reservation, commission_min on all fills, entry_next_bar,
        and hourly funding on coin+hedge. Hedge sized from no-look-ahead history
        and closed same liquidation bar. No rebound short. Coin/hedge attribution
        and total reconcile."""
        coin, eth = _scenario()
        res = backtest_simple(
            coin, _sig(), config=_cfg(), risk_state=_CapCutRS(),
            capital=100000.0, eth_candles=eth,
        )

        self.assertEqual(res.exit_reason, "liquidated")
        self.assertEqual(len(res.trades), 1)
        long_leg = res.trades[0]
        self.assertEqual(long_leg["side"], "long")
        self.assertEqual(long_leg["reason"], "liquidated")
        # No rebound short / rebound hedge on liquidated long.
        self.assertEqual(res.rebound_short_pnl, 0.0)
        self.assertEqual(res.rebound_hedge_pnl, 0.0)
        self.assertIsNone(res.rebound_hedge_side)
        self.assertNotIn("short", [t.get("side") for t in (res.trades or [])])

        # Cap-cut equal-share (old 80k + new 100k requested-equivalent share path
        # -> engine applies cap cuts across notionals): shares = 60k / 100 = 600,
        # but engine uses requested shares/cut result yielding 599.994... here
        # because commission_min buy fill is applied to the cut share count.
        self.assertAlmostEqual(res.shares, 599.9940000599994, places=9)
        self.assertAlmostEqual(res.entry_price, 100.001, places=9)
        self.assertAlmostEqual(long_leg["entry"], 100.001, places=9)
        # Liquidation at worst hourly low 93.0, commission_min sell fill.
        self.assertAlmostEqual(res.exit_price, 92.99833331666666, places=9)
        self.assertAlmostEqual(long_leg["exit"], 92.99833331666666, places=9)
        # bars_held = liq_idx(8) - start_idx(6) + 1 = 3 (hourly funding hours)
        self.assertEqual(res.bars_held, 3)

        # Short ETH hedge (long crash leg) — opened at aligned entry bar, sized
        # from no-look-ahead history, closed same liquidation bar.
        self.assertEqual(res.hedge_side, "short")
        self.assertAlmostEqual(res.hedge_size, 56.29769666891872, places=9)
        self.assertAlmostEqual(res.hedge_entry, 1999.9822372839535, places=9)
        self.assertAlmostEqual(res.hedge_exit, 2070.0177627160465, places=9)

        # Executed-notional penalty base + coin/hedge funding + commission_min fills.
        self.assertAlmostEqual(res.pnl, -4519.557994420063, places=6)
        self.assertAlmostEqual(long_leg["pnl"], -4519.557994420063, places=6)
        self.assertAlmostEqual(res.hedge_pnl, -3909.060448822962, places=6)
        self.assertAlmostEqual(res.total_pnl, -8428.618443243024, places=6)
        coin_total = sum(t["pnl"] for t in (res.trades or []))
        self.assertAlmostEqual(res.total_pnl, coin_total + res.hedge_pnl, places=6)

        # Coin-position reservation tracks executed long notional (hedges excluded).
        self.assertAlmostEqual(res.max_live_coin_notional, 60000.0, places=6)
        self.assertGreaterEqual(res.max_live_coin_notional, res.entry_price * res.shares - 1e-6)

    def test_funding_reconciles_coin_long_and_short_eth_hedge_on_liquidation(self):
        """Net funding effect on liquidation (coin long cost + ETH short benefit)
        reconciles as total_pnl(funding_on) - total_pnl(funding_off) with identical
        fill/penalty mechanics under commission_min+cap-cut."""
        coin, eth = _scenario()
        on = backtest_simple(
            coin, _sig(), config=_cfg(funding_rate_pct_per_hour=0.01),
            risk_state=_CapCutRS(), capital=100000.0, eth_candles=eth,
        )
        off = backtest_simple(
            coin, _sig(), config=_cfg(funding_rate_pct_per_hour=0.0),
            risk_state=_CapCutRS(), capital=100000.0, eth_candles=eth,
        )
        self.assertEqual(on.exit_reason, "liquidated")
        self.assertEqual(off.exit_reason, "liquidated")
        self.assertEqual(on.bars_held, 3)
        hours = on.bars_held
        rate = 0.01
        coin_cost = (on.entry_price * on.shares) * hours * (rate / 100.0)
        hedge_benefit = (on.hedge_entry * on.hedge_size) * hours * (rate / 100.0)
        expected_net = -coin_cost + hedge_benefit
        actual_net = on.total_pnl - off.total_pnl
        self.assertAlmostEqual(actual_net, expected_net, places=6)


if __name__ == "__main__":
    unittest.main()
