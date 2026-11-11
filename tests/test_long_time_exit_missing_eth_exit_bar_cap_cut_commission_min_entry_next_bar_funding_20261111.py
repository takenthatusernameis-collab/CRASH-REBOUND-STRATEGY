"""Material regression lock (2026-11-11, #4 uncovered combo).

Uncovered interaction: long-leg TIME_EXIT (time_exit_max_bars) with ETH hedge
enabled, commission_min-adjusted fills, cap-cut-style shares, entry_next_bar,
hourly funding, and ETH bar MISSING/UNAVAILABLE at the exit index.

Locked behavior (traced from engine math, deterministic synthetic fixture):
- entry_next_bar long fill at signal_index+1 open with sell/buy slippage+commission_min.
- Short ETH hedge sized from no-look-ahead history (hedge_vol_lookback) at entry bar,
  aligned to start_idx; established at start_idx open.
- Time exit after 3 bars (idx == start_idx+2, bars_held==3). ETH candle at exit idx
  has no usable price -> hedge exit falls back to hedge_info['entry'] (executed hedge
  entry px) as raw reference then applies buy-side slippage+commission_min for close.
- Hourly funding on coin long and hedge short legs for bars_held hours.
- No liquidation/stop/target/rebound path. trades log has single long time_exit leg.
- risk_state realizes full leg settlement (coin+hedge total_pnl), position closed.
- Reservation/max_live_coin_notional tracks executed coin-entry notional (hedges excluded).

Spec: hourly funding on every leg/exit; ETH hedge every leg (336h vol ratio, cap 3x,
no look-ahead sizing/alignment); missing aligned ETH exit bar must not fabricate a
market exit price (fallback path) while still applying hedge funding/settlement;
commission_min parity; entry_next_bar semantics. Synthetic fixtures only (non-evidence).
"""
from __future__ import annotations

import math
import unittest

from src.backtest.engine import backtest_simple, _apply_funding_pnl
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal, compute_eth_hedge_size
from src.strategy.risk import DailyRiskState


RATE = 0.001  # pct per hour
SLIP = 0.01
COMM_MIN = 0.5
SHARES = 2.0  # cap-cut/equal-share executed shares


def _c(ts, o, h, l, cl, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": cl, "volume": v}


def _close_to(x, y, tol=1e-9):
    return math.isclose(float(x), float(y), rel_tol=0.0, abs_tol=tol)


def _cfg(rate=RATE):
    return StrategyConfig(
        enable_eth_hedge=True,
        enable_rebound_short=False,
        entry_next_bar=True,
        avoid_downtrend=False,
        slippage_pct=SLIP,
        commission_per_share=0.0,
        commission_min=COMM_MIN,
        funding_rate_pct_per_hour=rate,
        min_daily_volume_usd=0.0,
        time_exit_max_bars=3,
        enable_liquidation_checks=False,
        hedge_vol_lookback_hours=336,
    )


def _sig():
    # signal at idx 4; entry_next_bar => start_idx 5
    return Signal(
        symbol="T", side="long", reason="t",
        entry_price=102.0, stop_price=80.0, target_price=120.0,
        risk_per_share=1.0, timestamp="c4",
        size_shares=SHARES, signal_index=4,
    )


def _scenario():
    # Coin: no liq/stop/target; time exit at idx 7 (start 5, bars_held 3).
    coin = [
        _c("c0", 100, 103, 97, 100),
        _c("c1", 102, 105, 99, 102),
        _c("c2", 98, 101, 95, 98),
        _c("c3", 100, 103, 97, 100),
        _c("c4", 102, 105, 99, 102),  # signal bar
        _c("c5", 101, 104, 99, 100),  # entry bar (next-bar open)
        _c("c6", 100, 101, 99, 100),
        _c("c7", 100, 101, 99, 100),  # time-exit bar, ETH missing here
        _c("c8", 100, 101, 99, 100),
    ]
    # ETH has usable history through start_idx 5 for hedge sizing/entry; missing at exit idx 7.
    eth = [
        _c("e0", 2000, 2060, 1940, 2000),
        _c("e1", 2040, 2100, 1980, 2040),
        _c("e2", 1960, 2020, 1900, 1960),
        _c("e3", 2000, 2060, 1940, 2000),
        _c("e4", 2040, 2100, 1980, 2040),
        _c("e5", 2000, 2060, 1940, 2000),  # hedge entry aligned to start_idx 5
        _c("e6", 2020, 2080, 1960, 2020),
        {"timestamp": "e7"},               # MISSING/unusable at time-exit idx 7
        _c("e8", 1980, 2040, 1920, 1980),
    ]
    return coin, eth


class TestLongTimeExitMissingEthExitBarCapCutCommissionMinFunding(unittest.TestCase):
    def test_long_time_exit_missing_eth_exit_bar_fallback_traced(self):
        """Long TIME_EXIT, short ETH hedge present at entry, ETH bar missing at exit idx:
        fallback hedge-exit raw to hedge_info['entry'] with buy-side slippage+commission_min,
        hourly funding on coin+hedge, cap-cut shares, entry_next_bar, no rebound. Traced values."""
        coin, eth = _scenario()
        cfg = _cfg(RATE)
        rs = DailyRiskState()
        on = backtest_simple(coin, _sig(), config=cfg, eth_candles=eth, risk_state=rs)

        self.assertEqual(on.exit_reason, "time_exit")
        self.assertEqual(on.bars_held, 3)
        self.assertEqual(on.entry_timestamp, "c5")
        self.assertEqual(on.exit_timestamp, "c7")

        # Coin execution (commission_min per share => 0.25/share at 2 shares).
        self.assertAlmostEqual(on.shares, 2.0, places=12)
        self.assertAlmostEqual(on.entry_price, 102.26, places=9)
        self.assertAlmostEqual(on.exit_price, 98.75, places=9)

        # Hedge: sized/aligned at entry; exit idx 7 missing => fallback close.
        self.assertEqual(on.hedge_side, "short")
        self.assertGreater(on.hedge_size or 0.0, 0.0)
        self.assertAlmostEqual(on.hedge_size, 0.10226, places=9)
        self.assertAlmostEqual(on.hedge_entry, 1975.1105026403286, places=9)
        # Missing aligned ETH exit bar: engine uses hedge_info['entry'] as raw ref then
        # applies buy-side slippage+commission_min (not a fresh market price).
        self.assertAlmostEqual(on.hedge_exit, 1999.7511050264034, places=9)

        # PnL/funding reconciliation (engine-traced deterministic).
        self.assertAlmostEqual(on.pnl, -7.026135600000011, places=9)
        self.assertAlmostEqual(on.hedge_pnl, -2.5136887560000054, places=9)
        self.assertAlmostEqual(on.total_pnl, -9.539824356000016, places=9)
        self.assertAlmostEqual(on.max_live_coin_notional, 204.52, places=9)

        self.assertEqual(len(on.trades or []), 1)
        leg = on.trades[0]
        self.assertEqual(leg["side"], "long")
        self.assertEqual(leg["reason"], "time_exit")
        self.assertAlmostEqual(leg["entry"], 102.26, places=9)
        self.assertAlmostEqual(leg["exit"], 98.75, places=9)
        self.assertAlmostEqual(leg["pnl"], -7.026135600000011, places=9)
        self.assertEqual(on.rebound_short_pnl, 0.0)
        self.assertEqual(on.rebound_hedge_pnl, 0.0)
        self.assertIsNone(on.rebound_hedge_side)

        # risk_state: full leg settlement (coin+hedge) realized and position released.
        self.assertEqual(rs.open_positions, 0)
        self.assertAlmostEqual(rs.gross_exposure, 0.0, places=9)
        self.assertEqual(rs.open_position_notionals, [])
        self.assertAlmostEqual(rs.realized_pnl, -9.539824356000016, places=9)

    def test_funding_reconciles_with_missing_eth_exit_bar_time_exit(self):
        """Funding parity with missing ETH exit bar: delta(total) == (coin long funding
        + hedge short funding component) effect vs funding-off, traced from engine math."""
        coin, eth = _scenario()
        on = backtest_simple(coin, _sig(), config=_cfg(RATE), eth_candles=eth)
        off = backtest_simple(coin, _sig(), config=_cfg(0.0), eth_candles=eth)

        self.assertEqual(on.exit_reason, "time_exit")
        self.assertEqual(off.exit_reason, "time_exit")
        self.assertEqual(on.bars_held, 3)

        hours = on.bars_held
        coin_cost = _apply_funding_pnl(on.entry_price * on.shares, hours, RATE, side="long")
        hedge_component = _apply_funding_pnl(on.hedge_entry * on.hedge_size, hours, RATE, side="short")
        # Engine applies: pnl -= coin_cost (long), hedge_pnl_total -= hedge_component.
        expected_delta = -coin_cost - hedge_component
        actual_delta = on.total_pnl - off.total_pnl
        self.assertAlmostEqual(actual_delta, expected_delta, places=9)
        self.assertAlmostEqual(on.pnl - off.pnl, -coin_cost, places=9)
        self.assertAlmostEqual(on.hedge_pnl - off.hedge_pnl, -hedge_component, places=9)
        self.assertAlmostEqual(actual_delta, -7.635600000099885e-05, places=15)

        # Sanity: hedge exit still reflects missing-bar fallback even with funding off.
        self.assertAlmostEqual(off.hedge_entry, on.hedge_entry, places=12)
        self.assertAlmostEqual(off.hedge_exit, on.hedge_exit, places=12)
        self.assertAlmostEqual(off.hedge_size, on.hedge_size, places=12)


if __name__ == "__main__":
    unittest.main()
