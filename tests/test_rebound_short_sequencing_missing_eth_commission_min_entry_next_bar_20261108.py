"""B-rem3/B-rem4 regression locks (2026-11-08): rebound short exit paths with
uncovered interactions — missing-ETH-bar (bar present, close/open absent, not
truncated series) on liquidation/time-exit under ETH hedge + commission_min +
entry_next_bar; and conservative same-bar sequencing (liquidation > stop >
target) when multiple short-exit thresholds breach on one hourly bar.

Hourly engine only; synthetic fixtures (non-evidence); no look-ahead. Failing-
tests-first derivation; concrete expected values verified against engine.

Spec: hourly funding on every leg (including fallback hedge exit accounting),
hourly liquidation at worst price, commission_min fill parity, entry_next_bar,
stopped buy never opens rebound short.
"""
from __future__ import annotations

import unittest

from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


class _NoCutRS:
    def check_position(self, config, capital, shares, entry_price):
        from types import SimpleNamespace
        return SimpleNamespace(allowed=True, size_shares=shares)

    def apply_cap_cuts(self, capital, config, open_notional=None):
        return []

    def apply_trade(self, *a, **k):
        pass


def _cfg(**ov):
    d = dict(
        enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=1.0, funding_rate_pct_per_hour=0.01,
        min_daily_volume_usd=0.0, time_exit_max_bars=200,
        enable_liquidation_checks=True,
        liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5, gross_cap_pct=120.0,
        rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
    )
    d.update(ov)
    return StrategyConfig(**d)


def _sig():
    return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                  stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                  timestamp="t5", size_shares=1000.0, signal_index=5)


class TestReboundShortMissingEthBarAndSequencing(unittest.TestCase):
    def test_rebound_short_liquidated_missing_eth_bar_commission_min_entry_next_bar(self):
        """ETH bar exists at rebound liquidation index but close/open are absent.
        Hedge exit must fall back to hedge entry (aligned fallback) while still
        charging hourly funding on both coin short and hedge long legs."""
        n = 30
        coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
        coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
        coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)
        coin[11] = _c("e11", 110.0, 116.0, 109.0, 115.0)  # short liq (maint 5% + buf 1% => 6% above entry)
        eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
        eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
        eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)
        eth[11] = {"timestamp": "h11"}  # missing close/open — aligned bar present

        res = backtest_simple(coin, _sig(), config=_cfg(), risk_state=_NoCutRS(),
                              capital=100000.0, eth_candles=eth)

        self.assertEqual(res.exit_reason, "target_rebound_short")
        self.assertEqual([t["reason"] for t in res.trades], ["target", "liquidated"])
        short_leg = res.trades[1]
        self.assertEqual(res.rebound_hedge_side, "long")
        self.assertAlmostEqual(res.rebound_hedge_size, 163.498635, places=6)
        self.assertAlmostEqual(res.rebound_hedge_entry, 2000.0061162590134, places=9)
        # Missing ETH exit: engine falls back to rebound_hedge_info['entry']
        # (commission-adjusted entry 2000.006116...) then applies sell-side
        # slippage/commission on that fallback => 2000.006116 - 1/163.498635 = 2000.0.
        self.assertAlmostEqual(res.rebound_hedge_exit, 2000.0, places=9)
        # 3 hours short hold (8->11), funding on coin short + hedge long.
        self.assertAlmostEqual(short_leg["pnl"], -7503.305814000009, places=5)
        self.assertAlmostEqual(res.rebound_hedge_pnl, -131.7993080000014, places=6)
        self.assertAlmostEqual(res.hedge_pnl, res.rebound_hedge_pnl, places=9)
        coin_total = sum(t["pnl"] for t in res.trades)
        self.assertAlmostEqual(res.total_pnl, coin_total + res.hedge_pnl, places=6)
        self.assertAlmostEqual(res.max_live_coin_notional, 108999.09, places=6)

    def test_rebound_short_48h_time_exit_missing_eth_bar_commission_min_entry_next_bar(self):
        """ETH bar exists at 48h time-exit index but close/open absent. Funding
        charged on coin short and hedge long; hedge exit falls back to hedge entry."""
        n = 120
        coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
        coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
        coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)
        for i in range(9, n):
            coin[i] = _c(f"s{i}", 108.0, 115.0, 100.0, 107.0)
        eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
        eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
        eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)
        for i in range(9, n):
            eth[i] = _c(f"eh{i}", 2030.0, 2050.0, 2020.0, 2040.0)
        # 48h time-exit triggers at first sidx where (sidx-short_start_idx+1)>=48.
        # short_start_idx=8 => sidx>=55, so exit bar is sidx=55 (timestamp s55).
        eth[55] = {"timestamp": "eh55"}  # missing close/open at actual 48h exit bar

        res = backtest_simple(coin, _sig(), config=_cfg(enable_liquidation_checks=False),
                              risk_state=_NoCutRS(), capital=100000.0, eth_candles=eth)

        self.assertEqual([t["reason"] for t in res.trades], ["target", "time_exit"])
        self.assertEqual(res.exit_timestamp, "s55")
        self.assertEqual(res.bars_held, 50)
        short_leg = res.trades[1]
        self.assertEqual(res.rebound_hedge_side, "long")
        self.assertAlmostEqual(res.rebound_hedge_entry, 2000.0061162590134, places=9)
        # Missing-bar fallback: entry-price fallback + sell commission_min => 2000.0.
        self.assertAlmostEqual(res.rebound_hedge_exit, 2000.0, places=9)
        self.assertAlmostEqual(short_leg["pnl"], 2521.2856319999905, places=5)
        self.assertAlmostEqual(res.rebound_hedge_pnl, -1570.5916960000018, places=5)
        coin_total = sum(t["pnl"] for t in res.trades)
        self.assertAlmostEqual(res.total_pnl, coin_total + res.hedge_pnl, places=6)

    def test_rebound_short_same_bar_stop_and_target_both_breach_stop_wins(self):
        """Same hourly bar breaches rebound short stop (high >= +40%) and target
        (low <= -9%). Liquidation disabled. Engine checks liq (off), then stop,
        then target => conservative deterministic 'stopped'."""
        n = 30
        coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
        coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
        coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)  # rebound short opens
        # short_entry ~108.99909, target ~99.189 (low breach), stop ~152.599 (high breach)
        coin[10] = _c("e10", 108.0, 160.0, 98.0, 120.0)
        eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
        eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
        eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)
        eth[10] = _c("h10", 2040.0, 2060.0, 2030.0, 2050.0)

        res = backtest_simple(coin, _sig(), config=_cfg(enable_liquidation_checks=False),
                              risk_state=_NoCutRS(), capital=100000.0, eth_candles=eth)

        self.assertEqual([t["reason"] for t in res.trades], ["target", "stopped"])
        self.assertAlmostEqual(res.trades[1]["exit"], 152.599726, places=6)
        self.assertAlmostEqual(res.trades[1]["pnl"], -43567.936273, places=3)
        self.assertAlmostEqual(res.rebound_hedge_pnl, 8074.832269000035, places=6)

    def test_rebound_short_same_bar_liquidation_precedes_stop_and_target(self):
        """Liquidation (worst-price, spec-explicit) must win when liq, stop, and
        target thresholds are all breached on the same hourly bar. Exit uses the
        liquidation/worst price (candle high for short), not the stop threshold."""
        n = 30
        coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
        coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
        coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)
        # short liq threshold = entry*(1+0.06) ~115.539; high 160 breaches liq,
        # stop (~152.599), and low 98 breaches target (~99.189).
        coin[10] = _c("e10", 108.0, 160.0, 98.0, 120.0)
        eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
        eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
        eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)
        eth[10] = _c("h10", 2040.0, 2060.0, 2030.0, 2050.0)

        res = backtest_simple(coin, _sig(), config=_cfg(enable_liquidation_checks=True),
                              risk_state=_NoCutRS(), capital=100000.0, eth_candles=eth)

        self.assertEqual([t["reason"] for t in res.trades], ["target", "liquidated"])
        # Worst-price liquidation exit for short = candle high + buy-side commission_min.
        self.assertAlmostEqual(res.trades[1]["exit"], 160.001, places=6)
        self.assertAlmostEqual(res.trades[1]["pnl"], -51514.205723, places=3)
        self.assertAlmostEqual(res.rebound_hedge_pnl, 8074.832269000035, places=6)


if __name__ == "__main__":
    unittest.main()
