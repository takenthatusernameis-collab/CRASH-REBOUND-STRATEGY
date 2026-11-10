"""Material regression lock (2026-11-10T15:XX:XXZ): long-leg TARGET exit (no rebound short)
with ETH hedge enabled under commission_min-adjusted fills + equal-share cap-cut
+ entry_next_bar + hourly funding. Locks: exit_reason 'target', long leg closed
at +9% target bar (no liq/stop/time_exit/rebound), short ETH hedge sized from
no-look-ahead history (hedge_vol_lookback, capped), hedge entry aligned to long
entry bar idx, hedge closed on target bar, commission_min on coin/hedge fills,
hourly funding on coin long and hedge short legs, no rebound short opened,
max_live_coin_notional reserved at executed long-entry notional (hedges excluded),
coin/hedge attribution and total reconciliation, trades log populated with
long/target, and risk_state settled with the full leg settlement (coin+hedge)
consistent with liquidation/stop/time-exit exits.

Spec: hourly funding on every leg and every exit path; ETH hedge every leg (336h
vol ratio, cap 3x, no look-ahead sizing/alignment); commission_min fill parity;
equal-share cuts (cuts only) old+new; entry_next_bar semantics; stopped buy never
opens rebound short (target with rebound disabled must not open rebound). Synthetic
fixtures only (non-evidence); hourly only.
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


class _RecordingRS(_CapCutRS):
    def __init__(self):
        super().__init__()
        self.events = []

    def apply_trade(self, *a, **k):
        self.events.append((a, k))


def _cfg(**ov):
    d = dict(
        enable_eth_hedge=True,
        enable_rebound_short=False,
        entry_next_bar=True,
        avoid_downtrend=False,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=1.0,
        funding_rate_pct_per_hour=0.01,
        min_daily_volume_usd=0.0,
        time_exit_max_bars=50,
        enable_liquidation_checks=True,
        liquidation_maint_margin_pct=5.0,
        liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5,
        gross_cap_pct=120.0,
        hedge_vol_lookback_hours=336,
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
    entry_next_bar long fill at bar 6 (open 100). Hits +9% target on bar 8,
    no rebound. Hedge closes same target bar.
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
        cp = cc
        ep = ec
    # Deterministic entry / hold / target bars.
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
    eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
    coin[7] = _c("e7", 100.0, 101.0, 99.0, 100.2)
    eth[7] = _c("h7", 2010.0, 2020.0, 2000.0, 2015.0)
    coin[8] = _c("e8", 108.0, 110.0, 107.5, 109.5)  # target hit
    eth[8] = _c("h8", 2030.0, 2040.0, 2020.0, 2035.0)  # hedge exit
    return coin, eth


class TestLongTargetEthHedgeCapCutCommissionMinEntryNextBar(unittest.TestCase):
    def test_long_target_closes_short_eth_hedge_cap_cut_commission_min_funding_no_rebound(self):
        """Long target (+9%) with short ETH hedge, cap-cut equal-share reservation,
        commission_min on all fills, entry_next_bar, hourly funding on coin+hedge.
        Hedge sized from no-look-ahead history and closed on target bar. No rebound
        short opened. Coin/hedge attribution, trade log, and total reconcile;
        risk_state settled with full (coin+hedge) pnl."""
        coin, eth = _scenario()
        rs = _RecordingRS()
        res = backtest_simple(
            coin, _sig(), config=_cfg(), risk_state=rs,
            capital=100000.0, eth_candles=eth,
        )

        self.assertEqual(res.exit_reason, "target")
        self.assertEqual(res.bars_held, 3)
        self.assertEqual(len(res.trades), 1)
        long_leg = res.trades[0]
        self.assertEqual(long_leg["side"], "long")
        self.assertEqual(long_leg["reason"], "target")
        # No rebound short / rebound hedge.
        self.assertEqual(res.rebound_short_pnl, 0.0)
        self.assertEqual(res.rebound_hedge_pnl, 0.0)
        self.assertIsNone(res.rebound_hedge_side)
        self.assertNotIn("short", [t.get("side") for t in (res.trades or [])])

        # Cap-cut + commission_min execution (engine-traced deterministic values).
        self.assertAlmostEqual(res.shares, 599.9940000599994, places=9)
        self.assertAlmostEqual(res.entry_price, 100.001, places=9)
        self.assertAlmostEqual(long_leg["entry"], 100.001, places=9)
        self.assertAlmostEqual(res.exit_price, 108.99942331666666, places=9)
        self.assertAlmostEqual(long_leg["exit"], 108.99942331666666, places=9)

        # Short ETH hedge (long crash leg) — aligned entry, closed on target bar.
        self.assertEqual(res.hedge_side, "short")
        self.assertAlmostEqual(res.hedge_size, 56.29769666891872, places=9)
        self.assertAlmostEqual(res.hedge_entry, 1999.9822372839535, places=9)
        self.assertAlmostEqual(res.hedge_exit, 2035.0177627160465, places=9)

        # Coin net (after 3h funding) / hedge pnl / total reconciliation.
        self.assertAlmostEqual(res.pnl, 5380.999999999995, places=6)
        self.assertAlmostEqual(long_leg["pnl"], 5380.999999999995, places=6)  # coin leg pnl stored in trades
        self.assertAlmostEqual(res.hedge_pnl, -1938.641065410807, places=6)
        self.assertAlmostEqual(res.total_pnl, 3442.3589345891887, places=6)
        coin_total = sum(t["pnl"] for t in (res.trades or []))
        self.assertAlmostEqual(res.total_pnl, coin_total + res.hedge_pnl, places=6)

        # Coin-position reservation tracks executed long notional (hedges excluded).
        self.assertAlmostEqual(res.max_live_coin_notional, 60000.0, places=6)
        self.assertGreaterEqual(res.max_live_coin_notional, res.entry_price * res.shares - 1e-6)

        # risk_state must realize the full leg settlement (coin+hedge), consistent
        # with liquidation/stop/target exits.
        self.assertTrue(rs.events, "expected risk_state.apply_trade close event")
        close_args, close_kw = rs.events[-1]
        self.assertEqual(close_args[0], "e8")  # timestamp
        self.assertAlmostEqual(close_args[1], res.total_pnl, places=6)
        self.assertFalse(close_kw.get("opened"))
        self.assertTrue(close_kw.get("closed"))
        self.assertAlmostEqual(close_kw.get("notional", 0.0), res.entry_price * res.shares, places=6)

    def test_funding_reconciles_coin_long_and_short_eth_hedge_on_target_exit_no_rebound(self):
        """Net funding effect on target exit (coin long + short ETH hedge) reconciles
        as total_pnl(funding_on) - total_pnl(funding_off) with identical fill
        mechanics under commission_min+cap-cut."""
        coin, eth = _scenario()
        on = backtest_simple(
            coin, _sig(), config=_cfg(funding_rate_pct_per_hour=0.01),
            risk_state=_CapCutRS(), capital=100000.0, eth_candles=eth,
        )
        off = backtest_simple(
            coin, _sig(), config=_cfg(funding_rate_pct_per_hour=0.0),
            risk_state=_CapCutRS(), capital=100000.0, eth_candles=eth,
        )
        self.assertEqual(on.exit_reason, "target")
        self.assertEqual(off.exit_reason, "target")
        self.assertEqual(on.bars_held, 3)
        hours = on.bars_held
        rate = 0.01
        coin_cost = (on.entry_price * on.shares) * hours * (rate / 100.0)
        hedge_funding = (on.hedge_entry * on.hedge_size) * hours * (rate / 100.0)
        expected_net = -coin_cost + hedge_funding
        actual_net = on.total_pnl - off.total_pnl
        self.assertAlmostEqual(actual_net, expected_net, places=6)
        self.assertAlmostEqual(on.pnl - off.pnl, -coin_cost, places=6)
        self.assertAlmostEqual(on.hedge_pnl - off.hedge_pnl, hedge_funding, places=6)


if __name__ == "__main__":
    unittest.main()
