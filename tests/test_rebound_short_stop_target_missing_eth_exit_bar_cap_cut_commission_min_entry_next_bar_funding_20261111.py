"""Material regression lock (2026-11-11, #4 uncovered combo reconciliation).

Uncovered reconciliation proof: rebound-short STOP and TARGET exits with ETH hedge
enabled, commission_min-adjusted fills, cap-cut-implied executed shares (600),
entry_next_bar, hourly funding on BOTH legs (rebound short coin + long ETH hedge),
and ETH bar MISSING/UNAVAILABLE at the rebound-short exit index.

Locked behavior (traced from engine math, deterministic synthetic fixtures):
- Long fills at next-bar open, exits at +9% target to open rebound short; rebound
  hedge (long ETH) sized/aligned to rebound-entry bar with no look-ahead.
- Rebound-short STOP/TARGET evaluated on executed short entry; at exit index the
  aligned ETH candle exists but close/open are absent -> hedge exit falls back to
  hedge_info['entry'] raw reference then applies sell-side commission_min.
- STOP case: short held 4 bars (idx 8->11), long held 3 bars (idx 6->8), so funding
  reconciles as delta = -(long_coin_cost_3h + short_coin_cost_4h + hedge_long_cost_4h)
  vs funding-off (long coin funding is realized in the target leg at idx 8).
- TARGET case: short held 3 bars (idx 8->10), long held 3 bars (idx 6->8), funding
  reconciles as delta = -(long_coin_cost_3h + short_coin_cost_3h + hedge_long_cost_3h).
- No liquidation; entry_next_bar; stopped buy never opens rebound short.
- risk_state realizes full settlement (coin legs + hedge total_pnl) and releases.

Spec: hourly funding on every leg/exit; ETH hedge every leg (336h vol ratio, cap 3x,
no look-ahead sizing/alignment); missing aligned ETH exit bar must not fabricate a
market exit price while still applying hedge funding/settlement; commission_min
parity; cap-cut executed notional/max_live_coin_notional authoritative. Synthetic
fixtures only (non-evidence).
"""
from __future__ import annotations

import unittest

from src.backtest.engine import backtest_simple, _apply_funding_pnl
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.strategy.risk import DailyRiskState


RATE = 0.01
SHARES = 600.0


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _cfg(rate=RATE):
    return StrategyConfig(
        enable_eth_hedge=True,
        enable_rebound_short=True,
        entry_next_bar=True,
        avoid_downtrend=False,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=1.0,
        funding_rate_pct_per_hour=rate,
        min_daily_volume_usd=0.0,
        time_exit_max_bars=200,
        enable_liquidation_checks=False,
        liquidation_maint_margin_pct=5.0,
        liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5,
        gross_cap_pct=120.0,
        rebound_short_target_pct=9.0,
        rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
    )


def _sig(shares=SHARES):
    # Post-cap-cut share count (portfolio-reservation context).
    return Signal(
        symbol="T", side="long", reason="t",
        entry_price=100.0, stop_price=80.0, target_price=109.0,
        risk_per_share=20.0, timestamp="t5",
        size_shares=shares, signal_index=5,
    )


def _stop_scenario():
    n = 30
    coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)    # long entry_next_bar
    coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)    # long target -> rebound short opens
    coin[11] = _c("e11", 110.0, 160.0, 109.0, 155.0)  # short stop breached
    eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
    eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
    eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)
    eth[11] = {"timestamp": "h11"}  # missing close/open at rebound-short exit idx
    return coin, eth


def _target_scenario():
    n = 30
    coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)    # long entry_next_bar
    coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)    # long target -> rebound short opens
    coin[9] = _c("b9", 110.0, 115.0, 109.0, 110.0)   # short holds
    coin[10] = _c("e10", 108.0, 109.0, 98.0, 107.0)   # rebound short target
    eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
    eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
    eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)
    eth[10] = {"timestamp": "h10"}  # missing close/open at rebound-short exit idx
    return coin, eth


class TestReboundShortStopTargetMissingEthCapCutCommissionMinFunding(unittest.TestCase):
    def test_rebound_short_stop_missing_eth_exit_bar_cap_cut_commission_min_funding_reconciles(self):
        """STOP with missing ETH at exit idx, cap-cut shares, commission_min, entry_next_bar:
        traced fills/pnls + per-leg funding reconciliation (long 3h, short 4h, hedge 4h)."""
        coin, eth = _stop_scenario()
        rs_on = DailyRiskState()
        rs_off = DailyRiskState()
        on = backtest_simple(coin, _sig(), config=_cfg(RATE), risk_state=rs_on,
                             capital=100000.0, eth_candles=eth)
        off = backtest_simple(coin, _sig(), config=_cfg(0.0), risk_state=rs_off,
                              capital=100000.0, eth_candles=eth)

        self.assertEqual(on.exit_reason, "target_rebound_short")
        self.assertEqual(off.exit_reason, "target_rebound_short")
        self.assertEqual([t["reason"] for t in on.trades], ["target", "stopped"])
        self.assertEqual(on.exit_timestamp, "e11")
        self.assertEqual(on.bars_held, 6)

        long_leg, short_leg = on.trades
        self.assertAlmostEqual(long_leg["entry"], 100.00166666666667, places=9)
        self.assertAlmostEqual(long_leg["exit"], 109.00014999999999, places=9)
        self.assertAlmostEqual(long_leg["pnl"], 5381.089699999996, places=5)

        self.assertAlmostEqual(short_leg["entry"], 108.99848333333333, places=9)
        self.assertAlmostEqual(short_leg["exit"], 152.59954333333332, places=9)
        self.assertAlmostEqual(short_leg["pnl"], -26134.476363999995, places=5)

        self.assertEqual(on.rebound_hedge_side, "long")
        self.assertAlmostEqual(on.rebound_hedge_size, 98.098635, places=6)
        self.assertAlmostEqual(on.rebound_hedge_entry, 2000.010193821759, places=9)
        # Missing aligned ETH exit bar: fallback to hedge entry raw ref + sell commission_min.
        self.assertAlmostEqual(on.rebound_hedge_exit, 2000.0, places=9)
        self.assertAlmostEqual(on.rebound_hedge_pnl, -79.47930799999152, places=6)
        self.assertAlmostEqual(on.hedge_pnl, on.rebound_hedge_pnl, places=9)
        self.assertAlmostEqual(on.max_live_coin_notional, 65399.09, places=6)

        coin_total = sum(t["pnl"] for t in on.trades)
        self.assertAlmostEqual(coin_total, -20753.386663999998, places=5)
        self.assertAlmostEqual(on.total_pnl, -20832.86597199999, places=5)
        self.assertAlmostEqual(on.total_pnl, coin_total + on.hedge_pnl, places=6)

        # Funding reconciliation: long coin 3h (target at idx 8), short coin 4h, hedge 4h.
        long_hours, short_hours, hedge_hours = 3, 4, 4
        long_cost = _apply_funding_pnl(long_leg["entry"] * SHARES, long_hours, RATE, side="long")
        short_cost = _apply_funding_pnl(short_leg["entry"] * SHARES, short_hours, RATE, side="short")
        hedge_cost = _apply_funding_pnl(on.rebound_hedge_entry * on.rebound_hedge_size, hedge_hours, RATE, side="long")
        expected_delta = -long_cost - short_cost - hedge_cost
        actual_delta = on.total_pnl - off.total_pnl
        self.assertAlmostEqual(actual_delta, expected_delta, places=9)
        self.assertAlmostEqual(long_leg["pnl"] - off.trades[0]["pnl"], -long_cost, places=9)
        self.assertAlmostEqual(short_leg["pnl"] - off.trades[1]["pnl"], -short_cost, places=9)
        self.assertAlmostEqual(on.rebound_hedge_pnl - off.rebound_hedge_pnl, -hedge_cost, places=9)

        # Fallback hedge exit is accounting-only (no fresh market price) even with funding off.
        self.assertAlmostEqual(off.rebound_hedge_entry, on.rebound_hedge_entry, places=12)
        self.assertAlmostEqual(off.rebound_hedge_exit, on.rebound_hedge_exit, places=12)
        self.assertAlmostEqual(off.rebound_hedge_size, on.rebound_hedge_size, places=12)

        # risk_state: rebound-leg settlement realized at close and position released.
        # (Long target leg pnl was realized at the target/rebound transition.)
        self.assertEqual(rs_on.open_positions, 0)
        self.assertAlmostEqual(rs_on.gross_exposure, 0.0, places=9)
        self.assertEqual(rs_on.open_position_notionals, [])
        self.assertAlmostEqual(rs_on.realized_pnl, short_leg["pnl"] + on.rebound_hedge_pnl, places=9)
        self.assertAlmostEqual(rs_on.realized_pnl, on.rebound_short_pnl + on.rebound_hedge_pnl, places=9)

    def test_rebound_short_target_missing_eth_exit_bar_cap_cut_commission_min_funding_reconciles(self):
        """TARGET with missing ETH at exit idx, cap-cut shares, commission_min, entry_next_bar:
        traced fills/pnls + per-leg funding reconciliation (long 3h, short 3h, hedge 3h)."""
        coin, eth = _target_scenario()
        rs_on = DailyRiskState()
        rs_off = DailyRiskState()
        on = backtest_simple(coin, _sig(), config=_cfg(RATE), risk_state=rs_on,
                             capital=100000.0, eth_candles=eth)
        off = backtest_simple(coin, _sig(), config=_cfg(0.0), risk_state=rs_off,
                              capital=100000.0, eth_candles=eth)

        self.assertEqual(on.exit_reason, "target_rebound_short")
        self.assertEqual(off.exit_reason, "target_rebound_short")
        self.assertEqual([t["reason"] for t in on.trades], ["target", "target"])
        self.assertEqual(on.exit_timestamp, "e10")
        self.assertEqual(on.bars_held, 5)

        long_leg, short_leg = on.trades
        self.assertAlmostEqual(long_leg["entry"], 100.00166666666667, places=9)
        self.assertAlmostEqual(long_leg["exit"], 109.00014999999999, places=9)
        self.assertAlmostEqual(long_leg["pnl"], 5381.089699999996, places=5)

        self.assertAlmostEqual(short_leg["entry"], 108.99848333333333, places=9)
        self.assertAlmostEqual(short_leg["exit"], 99.1902865, places=9)
        self.assertAlmostEqual(short_leg["pnl"], 5904.5378269999965, places=5)

        self.assertEqual(on.rebound_hedge_side, "long")
        self.assertAlmostEqual(on.rebound_hedge_size, 98.098635, places=6)
        self.assertAlmostEqual(on.rebound_hedge_entry, 2000.010193821759, places=9)
        self.assertAlmostEqual(on.rebound_hedge_exit, 2000.0, places=9)
        self.assertAlmostEqual(on.rebound_hedge_pnl, -59.85948099999151, places=6)
        self.assertAlmostEqual(on.hedge_pnl, on.rebound_hedge_pnl, places=9)
        self.assertAlmostEqual(on.max_live_coin_notional, 65399.09, places=6)

        coin_total = sum(t["pnl"] for t in on.trades)
        self.assertAlmostEqual(coin_total, 11285.627526999993, places=5)
        self.assertAlmostEqual(on.total_pnl, 11225.768046000001, places=5)
        self.assertAlmostEqual(on.total_pnl, coin_total + on.hedge_pnl, places=6)

        # Funding reconciliation: long coin 3h, short coin 3h, hedge 3h.
        long_hours, short_hours, hedge_hours = 3, 3, 3
        long_cost = _apply_funding_pnl(long_leg["entry"] * SHARES, long_hours, RATE, side="long")
        short_cost = _apply_funding_pnl(short_leg["entry"] * SHARES, short_hours, RATE, side="short")
        hedge_cost = _apply_funding_pnl(on.rebound_hedge_entry * on.rebound_hedge_size, hedge_hours, RATE, side="long")
        expected_delta = -long_cost - short_cost - hedge_cost
        actual_delta = on.total_pnl - off.total_pnl
        self.assertAlmostEqual(actual_delta, expected_delta, places=9)
        self.assertAlmostEqual(long_leg["pnl"] - off.trades[0]["pnl"], -long_cost, places=9)
        self.assertAlmostEqual(short_leg["pnl"] - off.trades[1]["pnl"], -short_cost, places=9)
        self.assertAlmostEqual(on.rebound_hedge_pnl - off.rebound_hedge_pnl, -hedge_cost, places=9)

        self.assertAlmostEqual(off.rebound_hedge_entry, on.rebound_hedge_entry, places=12)
        self.assertAlmostEqual(off.rebound_hedge_exit, on.rebound_hedge_exit, places=12)
        self.assertAlmostEqual(off.rebound_hedge_size, on.rebound_hedge_size, places=12)

        # risk_state: rebound-leg settlement realized at close and position released.
        # (Long target leg pnl was realized at the target/rebound transition.)
        self.assertEqual(rs_on.open_positions, 0)
        self.assertAlmostEqual(rs_on.gross_exposure, 0.0, places=9)
        self.assertEqual(rs_on.open_position_notionals, [])
        self.assertAlmostEqual(rs_on.realized_pnl, short_leg["pnl"] + on.rebound_hedge_pnl, places=9)
        self.assertAlmostEqual(rs_on.realized_pnl, on.rebound_short_pnl + on.rebound_hedge_pnl, places=9)


if __name__ == "__main__":
    unittest.main()
