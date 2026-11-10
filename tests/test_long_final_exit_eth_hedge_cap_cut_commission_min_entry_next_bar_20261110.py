"""Regression lock (2026-11-10): long-leg FINAL EXIT (loop-else, end of coin series)
with ALIGNED ETH hedge established at entry but NO aligned ETH bar at the final coin
exit index (eth_candles shorter than coin series) × equal-share cap-cut shares
(signal.size_shares) × commission_min × entry_next_bar × nonzero hourly funding.

Uncovered cell: existing final-exit short-ETH-series tests cover hedge-exit fallback
and funding presence but not this combination's traced fills, commission_min, cap-cut
shares, entry_next_bar execution, coin/hedge funding+PnL decomposition, risk_state
settlement (pnl/total_pnl) parity, trades-log attribution, and max_live_coin_notional.

Spec: hourly funding on every leg/exit (coin long, ETH hedge short); hedge entry sized
on eth_candles[:start_idx+1] / aligned to start_idx; final-exit with missing aligned
ETH bar must fall back to hedge entry for exit-price accounting (no misaligned last
bar) while still applying hedge funding; 120% cap cuts old+new equally (shares pre-cut,
reservation/entry-notional cap semantics); commission_min applied per share; entry at
next bar open; no look-ahead.

Synthetic fixtures only; deterministic; not performance evidence.
"""
import math

from src.backtest.engine import backtest_simple, _apply_funding_pnl
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal, compute_eth_hedge_size
from src.strategy.risk import DailyRiskState


RATE = 0.001  # pct per hour
SLIP = 0.01
COMM_MIN = 0.5
SHARES = 2.0  # cap-cut shares


def _c(ts, o, h, l, cl, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": cl, "volume": v}


def _close_to(x, y, tol=1e-9):
    return math.isclose(float(x), float(y), rel_tol=0.0, abs_tol=tol)


# 7 bars 0..6. Signal at 4 (close 102) -> entry_next_bar enters bar 5 open=101.
# Trade holds through bar 5 and bar 6; loop exhausts -> final-exit (loop-else) at
# bar 6 close=98 (no stop/target/liquidation/time_exit_max_bars hit). ETH series
# has bars 0..5 only: hedge entry aligns to start_idx=5 (available), but final coin
# idx 6 has no aligned ETH bar -> must fall back to hedge entry for hedge exit raw,
# while still applying hedge funding for the full hold.
COIN = [
    _c("2025-01-01T00:00:00", 100, 103, 97, 100),
    _c("2025-01-01T01:00:00", 102, 105, 99, 102),
    _c("2025-01-01T02:00:00", 98, 101, 95, 98),
    _c("2025-01-01T03:00:00", 100, 103, 97, 100),
    _c("2025-01-01T04:00:00", 102, 105, 99, 102),  # signal bar (idx 4)
    _c("2025-01-01T05:00:00", 101, 104, 98, 100),  # entry bar (idx 5)
    _c("2025-01-01T06:00:00", 98, 101, 95, 98),    # final exit bar (idx 6), no ETH bar
]
ETH = [
    _c("2025-01-01T00:00:00", 2000, 2060, 1940, 2000),
    _c("2025-01-01T01:00:00", 2040, 2100, 1980, 2040),
    _c("2025-01-01T02:00:00", 1960, 2020, 1900, 1960),
    _c("2025-01-01T03:00:00", 2000, 2060, 1940, 2000),
    _c("2025-01-01T04:00:00", 2040, 2100, 1980, 2040),
    _c("2025-01-01T05:00:00", 2000, 2060, 1940, 2000),  # aligned to start_idx=5
]


def _sig():
    # Stop/target wide so no stop/target fires; time_exit_max_bars large so exit
    # occurs via final loop-else path at series end.
    return Signal(
        symbol="T",
        side="long",
        reason="t",
        entry_price=102.0,   # signal-bar reference; entry_next_bar uses next open
        stop_price=50.0,
        target_price=200.0,
        risk_per_share=1.0,
        timestamp="2025-01-01T04:00:00",
        size_shares=SHARES,  # cap-cut equal-share shares
        signal_index=4,
    )


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
        time_exit_max_bars=1000,
        enable_liquidation_checks=False,
    )


def _trace(rate=RATE):
    """Hand-traced expected values for COIN/ETH/_sig/_cfg (engine-math)."""
    entry_raw = 101.0  # bar 5 open
    comm_ps = max(0.0, COMM_MIN / SHARES)  # 0.25
    entry_px = entry_raw + entry_raw * SLIP + comm_ps  # 102.26
    exit_raw = 98.0    # bar 6 close (final exit)
    exit_px = exit_raw - exit_raw * SLIP - comm_ps      # 96.77
    bars_held = 2      # len(candles)-start_idx = 7-5 = 2
    coin_gross = (exit_px - entry_px) * SHARES
    coin_notional = entry_px * SHARES
    funding_long = _apply_funding_pnl(coin_notional, bars_held, rate, 'long')
    coin_pnl = coin_gross - funding_long

    # Hedge sizing: no-look-ahead history at entry = candles[:start_idx+1]=[:6], eth[:6]
    hedge_value = compute_eth_hedge_size(COIN[:6], ETH[:6], coin_notional, _cfg(rate))
    eth_entry_raw = 2000.0  # ETH bar 5 open (aligned to start_idx=5)
    hedge_shares = hedge_value / eth_entry_raw
    hedge_comm_ps = max(0.0, COMM_MIN / hedge_shares)
    # Short ETH hedge opened on long entry -> sell-side execution on open
    hedge_entry_px = eth_entry_raw - eth_entry_raw * SLIP - hedge_comm_ps
    # Final coin idx 6 >= len(ETH)=6 -> fallback eth exit raw to hedge_info['entry'],
    # then buy-side execution closes short hedge.
    hedge_exit_px = hedge_entry_px + hedge_entry_px * SLIP + hedge_comm_ps
    hedge_gross = (hedge_entry_px - hedge_exit_px) * hedge_shares
    hedge_notional = hedge_entry_px * hedge_shares
    # Engine: funding component = _apply_funding_pnl(...,'short') (negative=benefit),
    # applied as hedge_pnl -= funding_component.
    hedge_funding_component = _apply_funding_pnl(hedge_notional, bars_held, rate, 'short')
    hedge_pnl = hedge_gross - hedge_funding_component
    return {
        "entry_px": entry_px,
        "exit_px": exit_px,
        "bars_held": bars_held,
        "coin_pnl": coin_pnl,
        "hedge_value": hedge_value,
        "hedge_shares": hedge_shares,
        "hedge_entry_px": hedge_entry_px,
        "hedge_exit_px": hedge_exit_px,
        "hedge_pnl": hedge_pnl,
        "total_pnl": coin_pnl + hedge_pnl,
        "max_live": coin_notional,
        "funding_long": funding_long,
        "hedge_funding_component": hedge_funding_component,
    }


def test_long_final_exit_missing_eth_bar_at_end_cap_cut_commission_min_entry_next_bar_funding_traced():
    exp = _trace(RATE)
    res = backtest_simple(COIN, _sig(), config=_cfg(RATE), eth_candles=ETH)

    # Final loop-else exit (end of coin series), not in-loop time_exit_max_bars.
    assert res.exit_reason == "time_exit"
    assert res.bars_held == exp["bars_held"] == 2
    assert res.entry_timestamp == "2025-01-01T05:00:00"
    assert res.exit_timestamp == "2025-01-01T06:00:00"

    assert _close_to(res.entry_price, exp["entry_px"])
    assert _close_to(res.exit_price, exp["exit_px"])
    assert _close_to(res.shares, SHARES)
    assert _close_to(res.max_live_coin_notional, exp["max_live"])

    # Hedge established at aligned entry bar 5 and must exist.
    assert (res.hedge_size or 0.0) > 0.0
    assert _close_to(res.hedge_size, exp["hedge_shares"])
    assert _close_to(res.hedge_entry, exp["hedge_entry_px"])
    # Final coin idx 6 has no aligned ETH bar (ETH covers 0..5 only): fallback must
    # close hedge at hedge_info['entry'] raw (not a misaligned bar), yielding traced exit.
    assert _close_to(res.hedge_exit, exp["hedge_exit_px"])
    assert res.hedge_side == "short"

    # Traced coin/hedge PnL including hourly funding on every leg.
    assert _close_to(res.pnl, exp["coin_pnl"])
    assert _close_to(res.hedge_pnl, exp["hedge_pnl"])
    assert _close_to(res.total_pnl, exp["total_pnl"])
    assert abs(exp["funding_long"]) > 1e-12
    assert abs(exp["hedge_funding_component"]) > 1e-12

    assert isinstance(res.trades, list) and len(res.trades) == 1
    leg = res.trades[0]
    assert leg["side"] == "long"
    assert leg["reason"] == "time_exit"
    assert _close_to(leg["entry"], exp["entry_px"])
    assert _close_to(leg["exit"], exp["exit_px"])
    assert _close_to(leg["pnl"], exp["coin_pnl"])


def test_long_final_exit_missing_eth_bar_at_end_risk_state_settlement_and_funding_parity():
    exp = _trace(RATE)
    rs_on = DailyRiskState()
    on = backtest_simple(COIN, _sig(), config=_cfg(RATE), eth_candles=ETH, risk_state=rs_on)
    off = backtest_simple(COIN, _sig(), config=_cfg(0.0), eth_candles=ETH)

    assert on.exit_reason == "time_exit"
    assert off.exit_reason == "time_exit"
    assert _close_to(on.total_pnl, exp["total_pnl"])

    # Risk state must realize FULL long-leg settlement (coin + hedge) on close and
    # release occupancy/notional.
    assert rs_on.open_positions == 0
    assert _close_to(rs_on.gross_exposure, 0.0)
    assert rs_on.open_position_notionals == []
    assert _close_to(rs_on.realized_pnl, exp["total_pnl"])

    # Funding parity: difference equals total (coin long + short hedge) funding effect.
    # engine applies pnl -= funding_component: long component positive(cost),
    # short component negative(benefit) => delta = -(funding_long + hedge_funding_component).
    delta = on.total_pnl - off.total_pnl
    expected_funding_effect = exp["funding_long"] + exp["hedge_funding_component"]
    assert _close_to(delta, -expected_funding_effect)
    assert abs(delta) > 1e-12
