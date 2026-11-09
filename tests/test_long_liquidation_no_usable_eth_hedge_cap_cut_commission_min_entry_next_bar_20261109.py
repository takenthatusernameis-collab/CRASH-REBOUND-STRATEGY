"""Material regression lock (2026-11-09T08:40:00Z, 2b engine uncovered combo 2a(i)).

Uncovered interaction: long-leg liquidation with enable_eth_hedge=True but NO
usable ETH hedge (flat/zero realized-vol ETH history => compute_eth_hedge_size
returns 0 / hedge open fails) under commission_min-adjusted fills + equal-share
cap-cut + entry_next_bar + hourly funding.

Locks: liquidation settles at worst hourly price with correct sequencing/
notional/timing/penalty on executed (cap-cut, commission_min) notional; no ETH
hedge is opened (hedge_side/size/pnl all zero/None), no hedge pnl leakage, no
funding on a non-existent hedge; hourly funding on coin long leg only; no
rebound short opened; max_live_coin_notional reserves executed long-entry
notional (hedges excluded). Coin-only attribution equals total.

Spec: hourly liquidation at worst price, correct sequencing/notional/timing/
penalty; hourly funding on every leg (coin long present, no hedge leg); ETH
hedge attempted but absent when no usable vol-ratio/ETH data => must not create
phantom hedge; commission_min fill parity; equal-share cuts old+new; stopped buy
never opens rebound short (liquidation distinct). Synthetic fixtures only.
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
        timestamp="t0",
        size_shares=1000.0,
        signal_index=0,
    )


class TestLongLiquidationNoUsableEthHedgeCapCutCommissionMin(unittest.TestCase):
    def test_long_liquidation_no_usable_eth_hedge_cap_cut_commission_min_funding(self):
        """Long liquidation with enable_eth_hedge=True but flat ETH (zero
        realized vol => no hedge). Cap-cut equal-share reservation, commission_min
        on coin fills, entry_next_bar, hourly funding on coin long only.

        Concrete expected values (failing-tests-first probe 2026-11-09T08:40Z):
        - cap 120k, open 80k, requested-equivalent path => executed notional 60k
        - commission_min buy: 100 + 0 + max(0, 1/shares) on pre-cut shares path;
          engine yields shares 599.9940000599994, entry 100.001
        - liq threshold 100.001*(1-0.06)=94.00094; bar2 low 93.0 breaches
        - liq exit commission_min sell: 93.0 - 0 - max(0,1/shares)=92.99833331666666
        - bars_held = liq_idx(2) - start_idx(1) + 1 = 2
        - price pnl (92.99833331666666-100.001)*599.9940000599994 = -4201.557994420063
        - coin funding (long cost) 60000*2*(0.01/100)=12.0
        - liq penalty 60000*0.005=300.0
        - total -4513.557994420063, no hedge pnl, no rebound short
        """
        coin = [
            _c("t0000", 100, 101, 99, 100),
            _c("t0001", 100, 101, 99, 100),   # entry_next_bar open fill
            _c("t0002", 100, 101, 93.0, 93.5),  # liquidation (worst hourly low)
            _c("t0003", 94, 95, 93, 94),
        ]
        # Flat ETH => zero realized vol => compute_eth_hedge_size returns 0.
        eth = [
            _c("t0000", 2000, 2000, 2000, 2000),
            _c("t0001", 2000, 2000, 2000, 2000),
            _c("t0002", 2000, 2000, 2000, 2000),
            _c("t0003", 2000, 2000, 2000, 2000),
        ]
        res = backtest_simple(
            coin, _sig(), config=_cfg(), risk_state=_CapCutRS(),
            capital=100000.0, eth_candles=eth,
        )

        self.assertEqual(res.exit_reason, "liquidated")
        self.assertEqual(len(res.trades), 1)
        long_leg = res.trades[0]
        self.assertEqual(long_leg["side"], "long")
        self.assertEqual(long_leg["reason"], "liquidated")

        # No hedge opened — flat ETH => no usable vol ratio.
        self.assertIn(res.hedge_side, (None, "none", ""))
        self.assertAlmostEqual(float(res.hedge_size or 0.0), 0.0, places=12)
        self.assertAlmostEqual(float(res.hedge_pnl or 0.0), 0.0, places=12)

        # No rebound short / rebound hedge on liquidated long.
        self.assertAlmostEqual(float(res.rebound_short_pnl or 0.0), 0.0, places=12)
        self.assertAlmostEqual(float(res.rebound_hedge_pnl or 0.0), 0.0, places=12)
        self.assertIn(res.rebound_hedge_side, (None, "none", ""))
        self.assertNotIn("short", [t.get("side") for t in (res.trades or [])])

        # Executed cap-cut + commission_min fills.
        self.assertAlmostEqual(res.shares, 599.9940000599994, places=9)
        self.assertAlmostEqual(res.entry_price, 100.001, places=9)
        self.assertAlmostEqual(long_leg["entry"], 100.001, places=9)
        self.assertAlmostEqual(res.exit_price, 92.99833331666666, places=9)
        self.assertAlmostEqual(long_leg["exit"], 92.99833331666666, places=9)
        self.assertEqual(res.bars_held, 2)

        # Coin-only pnl includes funding + penalty, no hedge leakage.
        self.assertAlmostEqual(res.pnl, -4513.557994420063, places=6)
        self.assertAlmostEqual(long_leg["pnl"], -4513.557994420063, places=6)
        coin_attr = res.pnl - float(res.hedge_pnl or 0.0)
        self.assertAlmostEqual(coin_attr, -4513.557994420063, places=6)
        self.assertAlmostEqual(res.max_live_coin_notional, 60000.0, places=6)

    def test_no_usable_eth_hedge_funding_reconciles_coin_only(self):
        """Funding reconciliation: funding on/off delta is coin-long cost only
        (no hedge funding) with identical fills/penalty mechanics."""
        coin = [
            _c("t0000", 100, 101, 99, 100),
            _c("t0001", 100, 101, 99, 100),
            _c("t0002", 100, 101, 93.0, 93.5),
            _c("t0003", 94, 95, 93, 94),
        ]
        eth = [_c(f"t{i:04d}", 2000, 2000, 2000, 2000) for i in range(4)]
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
        self.assertAlmostEqual(on.shares, off.shares, places=12)
        self.assertAlmostEqual(on.entry_price, off.entry_price, places=12)
        self.assertAlmostEqual(on.exit_price, off.exit_price, places=12)
        self.assertEqual(on.bars_held, 2)
        hours = on.bars_held
        coin_notional = on.entry_price * on.shares
        coin_cost = coin_notional * hours * (0.01 / 100.0)
        # on.pnl = off.pnl - coin_cost (no hedge)
        self.assertAlmostEqual(on.pnl - off.pnl, -coin_cost, places=6)
        self.assertAlmostEqual(float(on.hedge_pnl or 0.0), 0.0, places=12)
        self.assertAlmostEqual(float(off.hedge_pnl or 0.0), 0.0, places=12)
