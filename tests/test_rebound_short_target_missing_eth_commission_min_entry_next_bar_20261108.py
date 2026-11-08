"""B-rem6 regression lock (2026-11-08): rebound short TARGET (-9%) exit when ETH
bar exists at exit index but close/open are absent (aligned fallback to hedge
entry for exit accounting) under ETH hedge + commission_min + entry_next_bar.

Closes the last uncovered Priority B missing-ETH path: liquidation, stop, and
48h time-exit missing-ETH-bar variants were already locked; target parity was
unverified. Failing-tests-first derivation with concrete expected values.

Spec: hourly funding on every leg (including fallback hedge exit accounting),
rebound short -9% target anchored to executed short entry, commission_min fill
parity, entry_next_bar, stopped buy never opens rebound short.

Hourly engine only; synthetic fixture (non-evidence); no look-ahead.
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
        enable_liquidation_checks=False,
        gross_cap_pct=120.0,
        rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
    )
    d.update(ov)
    return StrategyConfig(**d)


def _sig():
    return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                  stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                  timestamp="t5", size_shares=1000.0, signal_index=5)


class TestReboundShortTargetMissingEthCommissionMinEntryNextBar(unittest.TestCase):
    def test_rebound_short_target_minus9_missing_eth_bar_commission_min_entry_next_bar(self):
        """ETH bar exists at rebound target index but close/open absent. Hedge
        exit falls back to hedge entry (commission-adjusted baseline) then
        sell-side commission_min is applied; hourly funding charged on coin
        short and hedge long legs. Target = executed short entry * 0.91."""
        n = 30
        coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
        coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)   # long entry_next_bar
        coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)   # long target -> rebound short opens
        # short_entry ~108.99909; target = entry*0.91 ~99.189 (low breach)
        coin[10] = _c("e10", 108.0, 109.0, 98.0, 107.0)
        eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
        eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
        eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)
        eth[10] = {"timestamp": "h10"}  # missing close/open — aligned bar present

        res = backtest_simple(coin, _sig(), config=_cfg(), risk_state=_NoCutRS(),
                              capital=100000.0, eth_candles=eth)

        self.assertEqual(res.exit_reason, "target_rebound_short")
        self.assertEqual([t["reason"] for t in res.trades], ["target", "target"])
        short_leg = res.trades[1]
        self.assertEqual(res.rebound_hedge_side, "long")
        self.assertAlmostEqual(res.rebound_hedge_size, 163.498635, places=6)
        self.assertAlmostEqual(res.rebound_hedge_entry, 2000.0061162590134, places=9)
        # Missing ETH exit fallback + sell commission_min => 2000.0
        self.assertAlmostEqual(res.rebound_hedge_exit, 2000.0, places=9)
        # 3 hours short hold (8->10), funding on coin short + hedge long.
        self.assertAlmostEqual(short_leg["pnl"], 9841.617826999985, places=5)
        self.assertAlmostEqual(res.rebound_hedge_pnl, -99.09948100000138, places=6)
        self.assertAlmostEqual(res.hedge_pnl, res.rebound_hedge_pnl, places=9)
        coin_total = sum(t["pnl"] for t in res.trades)
        self.assertAlmostEqual(res.total_pnl, coin_total + res.hedge_pnl, places=6)
        self.assertAlmostEqual(res.max_live_coin_notional, 108999.09, places=6)
        # Target anchored to executed short entry (slippage/commission-aware)
        self.assertAlmostEqual(short_leg["entry"], 108.99909, places=6)
        self.assertAlmostEqual(short_leg["exit"], 99.19017190000001, places=6)
        # total_bars = short_exit_idx(10) - long_start_idx(6) + 1 = 5
        self.assertEqual(res.bars_held, 5)


if __name__ == "__main__":
    unittest.main()