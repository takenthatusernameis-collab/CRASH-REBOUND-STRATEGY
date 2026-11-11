"""Regression lock (2026-11-11T23:44:38Z): rebound-short TARGET on the
exact 48th held bar (sidx=55, short_start_idx=8, target -9% precedence
over 48h time-exit) UNDER cap-cut-implied executed shares (600, gross_cap
120% context) + commission_min + entry_next_bar, for (a) aligned/usable ETH
hedge and (b) ETH hedge entirely absent/unusable at the exit index
(sidx >= len(eth_candles), fallback to rebound hedge entry).

Coverage-gap evidence (see HANDOFF 2026-11-11T23:08:51Z): existing
`tests/test_rebound_short_target_wins_on_48th_bar_boundary_20261108.py`
covers 48th-bar target precedence with _NoCutRS + 1000 shares and only
aligned ETH; `tests/test_rebound_short_48h_time_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_missing_eth_bar_fallback_raw_risk_settlement_20261111.py`
covers 48h time-exit (not target) under cap_cut+commission_min+entry_next_bar
with absent ETH. No existing test combines 48th-bar TARGET hit + cap_cut
shares + commission_min + entry_next_bar + (aligned and ETH-absent-at-exit)
+ full traced per-leg reconciliation.

Engine-traced expected values (capital=100000, 600 shares, entry_next_bar,
commission_min=1.0 per-share-adjusted, funding 0.01%/h, liq checks on,
maint=5%, buffer=1%, penalty=0.5%, 48h short_bars_max, stop 40%, target 9%):
  aligned ETH (exit bar 55 present):
    long:   entry 100.00166666666667 exit 109.00014999999999 pnl 5381.089699999996 (target)
    short:  entry 108.99848333333333 exit 99.1902865 pnl 6198.833731999996 (target)
    r-hedge long size 98.098635 entry 2000.010193821759 exit 2044.989806178241 pnl 3470.686879000017
    max_live_coin_notional 65399.09; total_pnl 15050.610311000011
    risk_state (funding on): realized 9669.520611000014, open 0, gross 0, notionals []
    funding-off: total 15696.44667500001, rs realized 10297.356675000014, r-hedge pnl 4412.438575000017
  ETH entirely absent at exit (len(eth)=10 < exit index 55, fallback to hedge entry):
    short pnl same 6198.833731999996 (target)
    r-hedge exit 2000.0 pnl -942.7516959999915 (sell commission_min + 48h funding on fallback exit)
    total_pnl 10637.171736
    risk_state: realized 5256.082036000005, open 0, gross 0, notionals []
    funding-off: total 11283.0081, rs realized 5883.918100000004, r-hedge pnl -0.9999999999915115
  Funding deltas (aligned and absent): total -645.8363640000025, rs -627.8360640000028.

Spec: hourly funding on every leg/exit path; TARGET precedence over time-exit
on exact 48th held bar; ETH hedge every leg (336h vol ratio cap 3x), entry
aligned to rebound-entry bar idx (no look-ahead); missing/unusable ETH exit
falls back to hedge entry with sell-side commission_min; commission_min on all
fills; entry_next_bar; risk_state in-loop target close settles
(short_pnl + rebound_hedge_pnl).

Hourly engine only; synthetic fixture (non-evidence); no look-ahead; never
fabricate market data.
"""
from __future__ import annotations

import unittest

from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.strategy.risk import DailyRiskState


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


class TestReboundShortTarget48thBarCapCutCommissionMin(unittest.TestCase):
    def _cfg(self, funding_rate_pct_per_hour=0.01):
        return StrategyConfig(
            enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
            avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
            commission_min=1.0, funding_rate_pct_per_hour=funding_rate_pct_per_hour,
            min_daily_volume_usd=0.0, time_exit_max_bars=200,
            enable_liquidation_checks=True,
            liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0,
            liquidation_penalty_pct=0.5, gross_cap_pct=120.0,
            rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
            rebound_short_time_exit_bars=48,
        )

    def _sig(self, shares=600.0):
        # Post-cap-cut share count (portfolio-reservation context).
        return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                      stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                      timestamp="t5", size_shares=shares, signal_index=5)

    def _coin(self):
        """long entry idx6, long target idx8 -> rebound short opens idx8.
        short_start_idx=8 => 48th held bar: sidx - 8 + 1 == 48 => sidx=55.
        Bar 55: low hits -9% target (99.19...), high stays below liquidation/stop.
        """
        n = 80
        coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
        coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
        coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)
        for i in range(9, n):
            coin[i] = _c(f"s{i}", 108.0, 115.0, 100.0, 107.0)
        # 48th held bar: low hits -9% target, high stays below stop/liq
        coin[55] = _c("b55", 108.0, 115.0, 99.0, 107.0)
        return coin

    def _eth_aligned(self):
        n = 80
        eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
        eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
        eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)  # rebound hedge entry idx8
        for i in range(9, n):
            eth[i] = _c(f"eh{i}", 2030.0, 2050.0, 2020.0, 2040.0)
        eth[55] = _c("eh55", 2030.0, 2055.0, 2020.0, 2045.0)  # hedge exit on 48th bar
        return eth

    def _eth_absent_at_exit(self):
        # ETH series ends at index 9 so exit index 55 is entirely absent.
        eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(10)]
        eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
        eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)
        self.assertEqual(len(eth), 10)
        return eth

    def _assert_common_legs(self, res):
        self.assertEqual(res.exit_reason, "target_rebound_short")
        self.assertEqual(res.exit_timestamp, "b55")
        self.assertEqual(res.bars_held, 50)
        self.assertEqual([t["reason"] for t in res.trades], ["target", "target"])
        self.assertEqual(len(res.trades), 2)
        long_leg, short_leg = res.trades

        self.assertAlmostEqual(long_leg["entry"], 100.00166666666667, places=9)
        self.assertAlmostEqual(long_leg["exit"], 109.00014999999999, places=9)
        self.assertAlmostEqual(long_leg["pnl"], 5381.089699999996, places=5)

        self.assertAlmostEqual(short_leg["entry"], 108.99848333333333, places=9)
        self.assertAlmostEqual(short_leg["exit"], 99.1902865, places=9)
        self.assertAlmostEqual(short_leg["pnl"], 6198.833731999996, places=5)

        self.assertEqual(res.rebound_hedge_side, "long")
        self.assertAlmostEqual(res.rebound_hedge_size, 98.098635, places=6)
        self.assertAlmostEqual(res.rebound_hedge_entry, 2000.010193821759, places=9)
        self.assertAlmostEqual(res.max_live_coin_notional, 65399.09, places=6)

    def test_target_on_48th_bar_aligned_eth_cap_cut_commission_min(self):
        coin, eth = self._coin(), self._eth_aligned()
        rs = DailyRiskState()
        res = backtest_simple(coin, self._sig(600.0), config=self._cfg(0.01),
                              risk_state=rs, capital=100000.0, eth_candles=eth)
        self._assert_common_legs(res)

        self.assertAlmostEqual(res.rebound_hedge_exit, 2044.989806178241, places=9)
        self.assertAlmostEqual(res.rebound_hedge_pnl, 3470.686879000017, places=6)
        self.assertAlmostEqual(res.hedge_pnl, res.rebound_hedge_pnl, places=9)

        coin_total = sum(t["pnl"] for t in res.trades)
        self.assertAlmostEqual(coin_total, 11579.923431999992, places=5)
        self.assertAlmostEqual(res.total_pnl, 15050.610311000011, places=6)
        self.assertAlmostEqual(res.total_pnl, coin_total + res.hedge_pnl, places=6)

        self.assertAlmostEqual(rs.realized_pnl, 9669.520611000014, places=6)
        self.assertEqual(rs.open_positions, 0)
        self.assertAlmostEqual(rs.gross_exposure, 0.0, places=9)
        self.assertEqual(rs.open_position_notionals, [])

    def test_target_on_48th_bar_eth_entirely_absent_at_exit_cap_cut(self):
        coin, eth = self._coin(), self._eth_absent_at_exit()
        rs = DailyRiskState()
        res = backtest_simple(coin, self._sig(600.0), config=self._cfg(0.01),
                              risk_state=rs, capital=100000.0, eth_candles=eth)
        self._assert_common_legs(res)

        # ETH bar entirely absent at exit -> fallback to rebound hedge entry,
        # sell-side commission_min cancels entry commission (same shares) + 48h funding.
        self.assertAlmostEqual(res.rebound_hedge_exit, 2000.0, places=9)
        self.assertAlmostEqual(res.rebound_hedge_pnl, -942.7516959999915, places=5)
        self.assertAlmostEqual(res.hedge_pnl, res.rebound_hedge_pnl, places=9)

        coin_total = sum(t["pnl"] for t in res.trades)
        self.assertAlmostEqual(coin_total, 11579.923431999992, places=5)
        self.assertAlmostEqual(res.total_pnl, 10637.171736, places=6)
        self.assertAlmostEqual(res.total_pnl, coin_total + res.hedge_pnl, places=6)

        # In-loop target close settles (short_pnl + rebound_hedge_pnl).
        self.assertAlmostEqual(rs.realized_pnl, 5256.082036000005, places=6)
        self.assertEqual(rs.open_positions, 0)
        self.assertAlmostEqual(rs.gross_exposure, 0.0, places=9)
        self.assertEqual(rs.open_position_notionals, [])

    def test_target_on_48th_bar_funding_delta_aligned_and_absent(self):
        coin = self._coin()
        sig = self._sig(600.0)

        # Aligned ETH
        rs_on = DailyRiskState()
        res_on = backtest_simple(coin, sig, config=self._cfg(0.01),
                                 risk_state=rs_on, capital=100000.0, eth_candles=self._eth_aligned())
        rs_off = DailyRiskState()
        res_off = backtest_simple(coin, sig, config=self._cfg(0.0),
                                  risk_state=rs_off, capital=100000.0, eth_candles=self._eth_aligned())

        self.assertAlmostEqual(res_off.total_pnl, 15696.44667500001, places=6)
        self.assertAlmostEqual(res_off.rebound_hedge_pnl, 4412.438575000017, places=6)
        self.assertAlmostEqual(res_on.total_pnl - res_off.total_pnl, -645.8363640000025, places=6)
        self.assertAlmostEqual(rs_off.realized_pnl, 10297.356675000014, places=6)
        self.assertAlmostEqual(rs_on.realized_pnl - rs_off.realized_pnl, -627.8360640000028, places=6)
        for rs in (rs_on, rs_off):
            self.assertEqual(rs.open_positions, 0)
            self.assertAlmostEqual(rs.gross_exposure, 0.0, places=9)
            self.assertEqual(rs.open_position_notionals, [])

        # ETH entirely absent at exit
        rs_on = DailyRiskState()
        res_on = backtest_simple(self._coin(), sig, config=self._cfg(0.01),
                                 risk_state=rs_on, capital=100000.0, eth_candles=self._eth_absent_at_exit())
        rs_off = DailyRiskState()
        res_off = backtest_simple(self._coin(), sig, config=self._cfg(0.0),
                                  risk_state=rs_off, capital=100000.0, eth_candles=self._eth_absent_at_exit())

        self.assertAlmostEqual(res_off.total_pnl, 11283.0081, places=6)
        self.assertAlmostEqual(res_off.rebound_hedge_pnl, -0.9999999999915115, places=6)
        self.assertAlmostEqual(res_on.total_pnl - res_off.total_pnl, -645.8363640000025, places=6)
        self.assertAlmostEqual(rs_off.realized_pnl, 5883.918100000004, places=6)
        self.assertAlmostEqual(rs_on.realized_pnl - rs_off.realized_pnl, -627.8360640000028, places=6)
        for rs in (rs_on, rs_off):
            self.assertEqual(rs.open_positions, 0)
            self.assertAlmostEqual(rs.gross_exposure, 0.0, places=9)
            self.assertEqual(rs.open_position_notionals, [])


if __name__ == "__main__":
    unittest.main()