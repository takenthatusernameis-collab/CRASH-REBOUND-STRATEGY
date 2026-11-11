"""Regression lock (2026-11-11): rebound short in-loop 48h TIME_EXIT (break inside
rebound loop, (sidx - short_start_idx + 1) >= rebound_short_time_exit_bars,
reason 'time_exit') × ALIGNED long ETH hedge established at rebound entry ×
cap-cut shares × commission_min × entry_next_bar × nonzero hourly funding on
every leg, with ETH series truncated so the 48h exit index is out of range and
the rebound hedge close resolves via the fallback-to-`rebound_hedge_info['entry']`
RAW path (sidx >= len(eth_candles) -> eth_exit_r = rebound_hedge_info['entry'],
sell-side commission_min close) — with explicit DailyRiskState settlement parity
and funding-on/off delta.

Distinct from:
- tests/test_rebound_short_48h_time_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_risk_settlement_20261110.py
  (aligned ETH bar present at 48h exit index; market-close hedge exit).
- tests/test_rebound_short_48h_time_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_missing_eth_bar_risk_settlement_20261110.py
  (truncated-boundary RESOLVED exit: ETH len 56, sidx=55 < 56 so engine resolves
  via eth[55] market close, not raw fallback entry).
- rebound-short loop-else/final-exit missing-final-ETH-bar locks and
  _NoCutRS missing-ETH-field 48h tests (different path/cell; no DailyRiskState
  settlement+funding-delta lock for this in-loop truncated-to-fallback-raw case).

Engine-traced expected values for this synthetic fixture (ETH len 55, exit idx 55
OOR -> raw fallback). Settlement: in-loop 48h break credits (short_pnl +
rebound_hedge_pnl) into realized close.
"""
from __future__ import annotations

import unittest

from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.strategy.risk import DailyRiskState


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


class TestReboundShort48hTimeExitMissingEthBarFallbackRawRiskSettlement(unittest.TestCase):
    def _cfg(self, funding_rate_pct_per_hour=0.01):
        return StrategyConfig(
            enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
            avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
            commission_min=1.0, funding_rate_pct_per_hour=funding_rate_pct_per_hour,
            min_daily_volume_usd=0.0, time_exit_max_bars=200,
            enable_liquidation_checks=False,
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

    def _candles(self):
        n = 120
        coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
        coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)    # entry_next_bar long fill
        coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)    # long target -> rebound short opens
        # short_entry ~108.998483, target ~99.189, stop ~152.598: stay in bounds for 48 bars.
        for i in range(9, n):
            coin[i] = _c(f"s{i}", 108.0, 115.0, 100.0, 107.0)

        # ETH: hedge established/aligned at idx 8 (no look-ahead). Series truncated
        # to 55 bars total (indices 0..54) so 48h exit index 55 (sidx=8+47, bars_held
        # 48 => short_start_idx 8 -> sidx 55) is out of range -> engine takes
        # fallback-to-rebound_hedge_info['entry'] RAW path at in-loop 48h break.
        eth = [_c(f"e{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(55)]
        eth[6] = _c("e6", 2000.0, 2010.0, 1990.0, 2000.0)
        eth[8] = _c("e8", 2000.0, 2030.0, 1995.0, 2025.0)    # rebound hedge entry aligned idx 8
        for i in range(9, 55):
            eth[i] = _c(f"eh{i}", 2030.0, 2050.0, 2020.0, 2040.0)
        return coin, eth

    def test_inloop_48h_time_exit_truncated_eth_fallback_raw_cap_cut_commission_min_risk_settlement(self):
        coin, eth = self._candles()
        self.assertEqual(len(eth), 55)  # exit index 55 missing -> raw fallback
        cfg = self._cfg(funding_rate_pct_per_hour=0.01)
        rs = DailyRiskState()
        res = backtest_simple(coin, self._sig(600.0), config=cfg,
                              risk_state=rs, capital=100000.0, eth_candles=eth)

        self.assertEqual(res.exit_reason, "target_rebound_short")
        self.assertEqual([t["reason"] for t in res.trades], ["target", "time_exit"])
        self.assertEqual(res.exit_timestamp, "s55")
        self.assertEqual(res.bars_held, 50)
        self.assertEqual(len(res.trades), 2)
        long_leg, short_leg = res.trades

        # Traced fills/PnL (cap-cut 600 shares, commission_min=1/share-adjusted, entry_next_bar).
        self.assertAlmostEqual(long_leg["entry"], 100.00166666666667, places=9)
        self.assertAlmostEqual(long_leg["exit"], 109.00014999999999, places=9)
        self.assertAlmostEqual(long_leg["pnl"], 5381.089699999996, places=5)

        self.assertAlmostEqual(short_leg["entry"], 108.99848333333333, places=9)
        self.assertAlmostEqual(short_leg["exit"], 107.00166666666667, places=9)
        self.assertAlmostEqual(short_leg["pnl"], 1512.0056319999962, places=5)

        self.assertEqual(res.rebound_hedge_side, "long")
        self.assertAlmostEqual(res.rebound_hedge_size, 98.098635, places=6)
        self.assertAlmostEqual(res.rebound_hedge_entry, 2000.010193821759, places=9)
        # Truncated ETH (sidx >= len): raw fallback to hedge entry, sell-side commission_min close.
        self.assertAlmostEqual(res.rebound_hedge_exit, 2000.0, places=9)
        self.assertAlmostEqual(res.rebound_hedge_pnl, -942.7516959999915, places=5)
        self.assertAlmostEqual(res.hedge_pnl, res.rebound_hedge_pnl, places=9)

        self.assertAlmostEqual(res.max_live_coin_notional, 65399.09, places=6)

        coin_total = sum(t["pnl"] for t in res.trades)
        self.assertAlmostEqual(coin_total, 6893.095331999992, places=5)
        self.assertAlmostEqual(res.total_pnl, 5950.3436360000005, places=5)
        self.assertAlmostEqual(res.total_pnl, coin_total + res.hedge_pnl, places=6)

        # In-loop 48h break settlement: risk_state receives (short_pnl + rebound_hedge_pnl)
        # as close delta at short exit, plus prior open/close legs.
        self.assertAlmostEqual(rs.realized_pnl, 569.2539360000047, places=6)
        self.assertEqual(rs.open_positions, 0)
        self.assertAlmostEqual(rs.gross_exposure, 0.0, places=9)
        self.assertEqual(rs.open_position_notionals, [])

    def test_inloop_48h_time_exit_truncated_eth_fallback_raw_settlement_and_funding_delta_parity(self):
        coin, eth = self._candles()
        sig = self._sig(600.0)

        rs_on = DailyRiskState()
        res_on = backtest_simple(coin, sig, config=self._cfg(funding_rate_pct_per_hour=0.01),
                                 risk_state=rs_on, capital=100000.0, eth_candles=eth)
        rs_off = DailyRiskState()
        res_off = backtest_simple(coin, sig, config=self._cfg(funding_rate_pct_per_hour=0.0),
                                  risk_state=rs_off, capital=100000.0, eth_candles=eth)

        # Funding affects every leg (long coin/hedge, rebound short coin/hedge): nonzero delta.
        self.assertAlmostEqual(res_off.total_pnl, 6596.18, places=5)
        self.assertAlmostEqual(res_on.total_pnl - res_off.total_pnl, -645.8363639999998, places=6)
        self.assertNotAlmostEqual(res_on.total_pnl, res_off.total_pnl, places=6)

        # Settlement parity/delta: in-loop break credits rebound hedge pnl into realized close.
        self.assertAlmostEqual(rs_off.realized_pnl, 1197.0900000000047, places=6)
        self.assertAlmostEqual(rs_on.realized_pnl - rs_off.realized_pnl, -627.836064, places=6)
        self.assertNotAlmostEqual(rs_on.realized_pnl, rs_off.realized_pnl, places=6)
        for rs in (rs_on, rs_off):
            self.assertEqual(rs.open_positions, 0)
            self.assertAlmostEqual(rs.gross_exposure, 0.0, places=9)
            self.assertEqual(rs.open_position_notionals, [])


if __name__ == "__main__":
    unittest.main()
