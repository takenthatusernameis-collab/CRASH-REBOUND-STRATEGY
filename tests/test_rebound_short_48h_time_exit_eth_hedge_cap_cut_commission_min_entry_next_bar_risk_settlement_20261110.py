"""Regression lock: rebound short in-loop 48h TIME_EXIT (break inside rebound loop,
(sidx - short_start_idx + 1) >= rebound_short_time_exit_bars, reason 'time_exit')
× ALIGNED long ETH hedge established at rebound entry × cap-cut shares ×
commission_min × entry_next_bar × nonzero hourly funding on every leg, ETH exit
bar present/aligned at 48h exit index — with explicit DailyRiskState settlement
parity and funding-on/off delta.

Distinct from existing traced-value locks that use _NoCutRS stubs and do not
assert settlement: this locks the in-loop 48h break settlement path
(apply_trade with short_pnl + rebound_hedge_pnl, opened=False, closed=True,
notional=short_entry_px*short_shares), realized/exposure clearing, and nonzero
funding delta on every leg with real DailyRiskState under cap-cut shares +
commission_min + entry_next_bar + aligned ETH hedge.
"""
from __future__ import annotations

import unittest

from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.strategy.risk import DailyRiskState


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


class TestReboundShort48hTimeExitEthHedgeCapCutCommissionMinSettlement(unittest.TestCase):
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
        eth = [_c(f"e{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
        eth[6] = _c("e6", 2000.0, 2010.0, 1990.0, 2000.0)
        eth[8] = _c("e8", 2000.0, 2030.0, 1995.0, 2025.0)    # rebound hedge entry aligned idx 8
        for i in range(9, n):
            eth[i] = _c(f"eh{i}", 2030.0, 2050.0, 2020.0, 2040.0)
        eth[56] = _c("eh56", 2030.0, 2055.0, 2020.0, 2045.0)  # 48h exit bar (8+48=56), aligned
        return coin, eth

    def test_inloop_48h_time_exit_aligned_eth_hedge_cap_cut_commission_min_risk_settlement(self):
        coin, eth = self._candles()
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
        self.assertAlmostEqual(res.rebound_hedge_exit, 2039.989806178241, places=9)
        self.assertAlmostEqual(res.rebound_hedge_pnl, 2980.1937040000166, places=5)
        self.assertAlmostEqual(res.hedge_pnl, res.rebound_hedge_pnl, places=9)

        self.assertAlmostEqual(res.max_live_coin_notional, 65399.09, places=6)

        coin_total = sum(t["pnl"] for t in res.trades)
        self.assertAlmostEqual(coin_total, 6893.095331999992, places=5)
        self.assertAlmostEqual(res.total_pnl, 9873.28903600001, places=5)
        self.assertAlmostEqual(res.total_pnl, coin_total + res.hedge_pnl, places=6)

        # In-loop 48h break settlement: risk_state receives (short_pnl + rebound_hedge_pnl)
        # as the close delta at short exit, plus prior open/close legs. Realized therefore
        # includes rebound hedge pnl (distinct from loop-else final-exit settlement path).
        self.assertAlmostEqual(rs.realized_pnl, 4492.199336000012, places=6)
        self.assertEqual(rs.open_positions, 0)
        self.assertAlmostEqual(rs.gross_exposure, 0.0, places=9)
        self.assertEqual(rs.open_position_notionals, [])

    def test_inloop_48h_time_exit_settlement_and_funding_delta_parity(self):
        coin, eth = self._candles()
        sig = self._sig(600.0)

        rs_on = DailyRiskState()
        res_on = backtest_simple(coin, sig, config=self._cfg(funding_rate_pct_per_hour=0.01),
                                 risk_state=rs_on, capital=100000.0, eth_candles=eth)
        rs_off = DailyRiskState()
        res_off = backtest_simple(coin, sig, config=self._cfg(funding_rate_pct_per_hour=0.0),
                                  risk_state=rs_off, capital=100000.0, eth_candles=eth)

        # Funding affects every leg (long coin/hedge, rebound short coin/hedge): nonzero delta.
        self.assertAlmostEqual(res_off.total_pnl, 10519.125400000008, places=5)
        self.assertAlmostEqual(res_on.total_pnl - res_off.total_pnl, -645.8363639999989, places=6)
        self.assertNotAlmostEqual(res_on.total_pnl, res_off.total_pnl, places=6)

        # Settlement parity/delta: in-loop break credits rebound hedge pnl into realized close.
        self.assertAlmostEqual(rs_off.realized_pnl, 5120.035400000013, places=6)
        self.assertAlmostEqual(rs_on.realized_pnl - rs_off.realized_pnl, -627.836064000001, places=6)
        self.assertNotAlmostEqual(rs_on.realized_pnl, rs_off.realized_pnl, places=6)
        for rs in (rs_on, rs_off):
            self.assertEqual(rs.open_positions, 0)
            self.assertAlmostEqual(rs.gross_exposure, 0.0, places=9)
            self.assertEqual(rs.open_position_notionals, [])


if __name__ == "__main__":
    unittest.main()
