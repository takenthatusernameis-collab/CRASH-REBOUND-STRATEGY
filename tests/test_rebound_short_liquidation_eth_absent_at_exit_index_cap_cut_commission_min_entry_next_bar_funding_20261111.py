"""Regression lock (2026-11-11T05:29:28Z): rebound-short LIQUIDATION where the
ETH bar is ENTIRELY ABSENT at the exit index (sidx >= len(eth_candles), ETH
series shorter than the coin series at the short-liquidation bar), under
cap-cut regime (gross_cap 120%) + commission_min + entry_next_bar + nonzero
hourly funding on every leg.

Distinct from existing "bar present but close/open absent" fallback locks:
- tests/test_rebound_short_liquidation_missing_eth_commission_min_cap_cut_shares_20261109.py
  (eth[liq_bar] = {"timestamp": ...} -> bar present, close/open absent)
- tests/test_rebound_short_liquidation_missing_eth_exit_fallback_funding_applied
  in tests/test_rebound_short_liquidation_audit_20261107.py (same cell).

Here the ETH bar itself is out of range at the liquidation exit index, so the
engine must resolve the rebound-hedge exit via the fallback to
rebound_hedge_info['entry'] (aligned fallback, sell-side commission_min, no
look-ahead) and still apply hourly funding on the long-ETH hedge leg.

Engine-traced expected values (capital=100000, 600 shares, entry_next_bar,
commission_min=1.0/share-adjusted, funding 0.01%/h):
  long  leg: entry 100.00166666666667, exit 109.00014999999999, pnl 5381.089699999996, target
  short leg: entry 108.99848333333333, exit 116.00166666666667, pnl -4509.285723000004, liquidated
  rebound hedge (long ETH): size 98.098635, entry 2000.010193821759, exit 2000.0, pnl -59.85948099999151
  max_live_coin_notional = 65399.09 (executed rebound-short coin notional)
  total_pnl = 811.944496000001 = coin_total 871.8039769999923 + hedge_pnl -59.85948099999151
  risk_state settlement: in-loop liquidation close credits (short_pnl +
  rebound_hedge_pnl) = -4569.145203999995 as realized close (synthetic per-bar
  day strings wipe earlier legs), open_positions 0, gross 0.0, notionals []
  Funding on/off delta: total 811.944496000001 vs 869.184550000000 (funding 0.0).
No look-ahead: hedge sized on eth_candles[:idx+1] at rebound entry bar 8; exit
bar 10 is beyond eth length 10 -> fallback path.
Synthetic fixture only; not performance evidence; no real market data.
"""
from __future__ import annotations

import unittest

from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.strategy.risk import DailyRiskState


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


class TestReboundShortLiquidationEthAbsentAtExitIndex(unittest.TestCase):
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

    def _candles(self):
        n = 30
        coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
        coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)   # long entry_next_bar fill bar 6
        coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)   # long target bar 8 -> rebound short opens
        coin[10] = _c("e10", 110.0, 116.0, 109.0, 115.0)  # short liquidation bar 10 (high >= liq threshold)
        # ETH: volatile so both hedges establish; length 10 (indices 0..9) so the
        # liquidation exit index sidx=10 is ENTIRELY ABSENT (out of range).
        eth = [_c(f"h{i}", 2000.0 + (i % 2) * 10.0, 2010.0 + (i % 2) * 10.0,
                  1990.0 + (i % 2) * 10.0, 2000.0 + (i % 2) * 10.0) for i in range(10)]
        self.assertEqual(len(eth), 10)  # exit index 10 >= len(eth) -> absent
        return coin, eth

    def test_rebound_short_liquidation_eth_entirely_absent_at_exit_index(self):
        coin, eth = self._candles()
        cfg = self._cfg(funding_rate_pct_per_hour=0.01)
        rs = DailyRiskState()
        res = backtest_simple(coin, self._sig(600.0), config=cfg,
                              risk_state=rs, capital=100000.0, eth_candles=eth)

        self.assertEqual(res.exit_reason, "target_rebound_short")
        self.assertEqual(res.exit_timestamp, "e10")
        self.assertEqual(res.bars_held, 5)
        self.assertEqual([t["reason"] for t in res.trades], ["target", "liquidated"])
        self.assertEqual(len(res.trades), 2)
        long_leg, short_leg = res.trades

        # Long leg: entry_next_bar fill + target exit.
        self.assertAlmostEqual(long_leg["entry"], 100.00166666666667, places=9)
        self.assertAlmostEqual(long_leg["exit"], 109.00014999999999, places=9)
        self.assertAlmostEqual(long_leg["pnl"], 5381.089699999996, places=5)

        # Rebound short: worst-price liquidation at candle high (bar 10 high 116).
        self.assertAlmostEqual(short_leg["entry"], 108.99848333333333, places=9)
        self.assertAlmostEqual(short_leg["exit"], 116.00166666666667, places=9)
        self.assertAlmostEqual(short_leg["pnl"], -4509.285723000004, places=5)
        self.assertEqual(short_leg["reason"], "liquidated")

        # Rebound hedge (long ETH) established aligned at rebound entry bar 8.
        self.assertEqual(res.rebound_hedge_side, "long")
        self.assertAlmostEqual(res.rebound_hedge_size, 98.098635, places=6)
        self.assertAlmostEqual(res.rebound_hedge_entry, 2000.010193821759, places=9)
        # ETH bar entirely absent at exit -> fallback to rebound hedge entry,
        # sell-side commission_min cancels entry commission exactly (same shares).
        self.assertAlmostEqual(res.rebound_hedge_exit, 2000.0, places=9)
        self.assertAlmostEqual(res.rebound_hedge_pnl, -59.85948099999151, places=5)
        self.assertAlmostEqual(res.hedge_pnl, res.rebound_hedge_pnl, places=9)

        # Authoritative for portfolio reservation: executed rebound-short coin notional.
        self.assertAlmostEqual(res.max_live_coin_notional, 65399.09, places=6)

        coin_total = sum(t["pnl"] for t in res.trades)
        self.assertAlmostEqual(coin_total, 871.8039769999923, places=5)
        self.assertAlmostEqual(res.total_pnl, 811.944496000001, places=5)
        self.assertAlmostEqual(res.total_pnl, coin_total + res.hedge_pnl, places=6)

        # In-loop liquidation close settlement: risk_state receives
        # (short_pnl + rebound_hedge_pnl) as realized close at the exit bar.
        self.assertAlmostEqual(rs.realized_pnl, -4569.145203999995, places=6)
        self.assertEqual(rs.open_positions, 0)
        self.assertAlmostEqual(rs.gross_exposure, 0.0, places=9)
        self.assertEqual(rs.open_position_notionals, [])

    def test_rebound_short_liquidation_eth_absent_funding_delta(self):
        coin, eth = self._candles()
        sig = self._sig(600.0)

        rs_on = DailyRiskState()
        res_on = backtest_simple(coin, sig, config=self._cfg(funding_rate_pct_per_hour=0.01),
                                 risk_state=rs_on, capital=100000.0, eth_candles=eth)
        rs_off = DailyRiskState()
        res_off = backtest_simple(coin, sig, config=self._cfg(funding_rate_pct_per_hour=0.0),
                                  risk_state=rs_off, capital=100000.0, eth_candles=eth)

        # Hourly funding applies to every leg (long coin/hedge, rebound short coin,
        # rebound long-ETH hedge): nonzero funding delta.
        self.assertAlmostEqual(res_off.total_pnl, 869.184550000000, places=6)
        self.assertAlmostEqual(res_on.total_pnl - res_off.total_pnl, -57.240053999999, places=6)
        self.assertNotAlmostEqual(res_on.total_pnl, res_off.total_pnl, places=6)

        # Hedge funding on the long-ETH rebound leg is applied on the fallback exit too.
        self.assertAlmostEqual(res_off.rebound_hedge_pnl, -1.0, places=6)
        self.assertAlmostEqual(res_on.rebound_hedge_pnl - res_off.rebound_hedge_pnl, -58.85948099999151, places=6)

        # Settlement delta carries the funding delta into the realized close.
        self.assertAlmostEqual(rs_off.realized_pnl, -4529.905449999996, places=6)
        self.assertAlmostEqual(rs_on.realized_pnl - rs_off.realized_pnl, -39.239754000001, places=6)
        self.assertNotAlmostEqual(rs_on.realized_pnl, rs_off.realized_pnl, places=6)
        for rs in (rs_on, rs_off):
            self.assertEqual(rs.open_positions, 0)
            self.assertAlmostEqual(rs.gross_exposure, 0.0, places=9)
            self.assertEqual(rs.open_position_notionals, [])


if __name__ == "__main__":
    unittest.main()
