"""Regression lock (2026-11-12): FINAL EXIT (loop-else) with BOTH long-leg ETH hedge
AND rebound-short ETH hedge established and funded simultaneously under cap_cut +
commission_min + entry_next_bar — MISSING ETH bar at final coin exit index.

Gap proof (2026-11-12): `tests/test_both_hedges_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_20261112.py`
locks aligned final-exit only (ETH through final coin bar). Rebound-only missing-final-ETH
is covered elsewhere, but both-hedges missing-ETH-at-final-exit (rebound hedge exit bar
absent while long hedge exited aligned at target bar) was uncovered.

Locks: loop-else final exit at end of coin series when ETH series ends before final coin
index -> rebound ETH hedge exit falls back to hedge entry fill with exit
slippage/commission re-applied (engine fallback), long-leg ETH hedge exit remains aligned
at long target bar. Asserts per-leg PnL/funding reconciliation, total_pnl,
max_live_coin_notional, DailyRiskState settlement/release/close parity, funding on/off
deltas, strict no-look-ahead hedge sizing/entry alignment. Hourly bar-by-bar only.

Synthetic fixtures only; deterministic; not performance evidence.
"""
import math

from src.backtest.engine import backtest_simple, _apply_funding_pnl, _slippage_commission_per_share
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal, compute_eth_hedge_size
from src.strategy.risk import DailyRiskState


def _c(ts, o, h, l, cl, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": cl, "volume": v}


def _close_to(x, y, tol=1e-9):
    return math.isclose(float(x), float(y), rel_tol=0.0, abs_tol=tol)


RATE = 0.01
SLIP = 0.001
COMM_MIN = 0.5
SHARES = 10.0

# 12 bars 0..11.
# - idx 4: signal bar
# - idx 5: long entry bar (open 100.0) via entry_next_bar; signal_index=4 -> start_idx=5
# - idx 6: long +9% target hit -> long closes, rebound short opens, both ETH hedges established
# - idx 7..11: rebound short holds (no stop/target/liq/48h), loop exhausts ->
#          FINAL EXIT (loop-else) at idx 11 close=108.0
COIN = [_c(f"2025-01-01T{i:02d}:00:00", 100.0, 101.0, 99.0, 100.0) for i in range(12)]
COIN[4] = _c("2025-01-01T04:00:00", 102.0, 105.0, 97.0, 102.0)
COIN[5] = _c("2025-01-01T05:00:00", 100.0, 101.0, 98.0, 99.0)
COIN[6] = _c("2025-01-01T06:00:00", 109.0, 110.0, 108.0, 109.0)
for i in range(7, 12):
    COIN[i] = _c(f"2025-01-01T{i:02d}:00:00", 108.0, 112.0, 105.0, 108.0)

ETH_FULL = [_c(f"2025-01-01T{i:02d}:00:00", 2000.0 + i * 5, 2020.0 + i * 5, 1980.0 + i * 5, 2005.0 + i * 5) for i in range(12)]


def _cfg(rate=RATE):
    return StrategyConfig(
        enable_eth_hedge=True,
        enable_rebound_short=True,
        entry_next_bar=True,
        avoid_downtrend=False,
        slippage_pct=SLIP,
        commission_per_share=0.0,
        commission_min=COMM_MIN,
        funding_rate_pct_per_hour=rate,
        min_daily_volume_usd=0.0,
        time_exit_max_bars=1000,
        rebound_short_time_exit_bars=100,
        enable_liquidation_checks=False,
    )


def _sig():
    return Signal(
        symbol="T",
        side="long",
        reason="t",
        entry_price=100.0,
        stop_price=50.0,
        target_price=109.0,
        risk_per_share=1.0,
        timestamp="2025-01-01T04:00:00",
        size_shares=SHARES,
        signal_index=4,
    )


def _trace(eth_len=len(COIN), rate=RATE):
    cfg = _cfg(rate)
    eth = ETH_FULL[:eth_len]
    entry_raw = 100.0
    next_open = 100.0
    entry_px = _slippage_commission_per_share(next_open, cfg, 'buy', shares=SHARES)

    ratio = entry_px / entry_raw
    target_px = 109.0 * ratio

    # Long target hit at idx 6
    long_exit_px = _slippage_commission_per_share(target_px, cfg, 'sell', shares=SHARES)
    long_coin_gross = (long_exit_px - entry_px) * SHARES
    hours_held_long = 6 - 5 + 1  # 2
    funding_long = _apply_funding_pnl(entry_px * SHARES, hours_held_long, rate, 'long')
    long_coin_pnl = long_coin_gross - funding_long

    # Long-leg ETH hedge (short), established at entry idx 5, exits aligned at idx 6
    hedge_value_l = compute_eth_hedge_size(COIN[:6], eth[:6], entry_px * SHARES, cfg)
    eth_entry_raw_l = eth[5]["open"]
    hedge_shares_l = hedge_value_l / eth_entry_raw_l
    hedge_entry_px = _slippage_commission_per_share(eth_entry_raw_l, cfg, 'sell', shares=hedge_shares_l)
    if eth_len > 6:
        eth_exit_raw_l = eth[6]["close"]
        hedge_exit_px = _slippage_commission_per_share(eth_exit_raw_l, cfg, 'buy', shares=hedge_shares_l)
    else:
        hedge_exit_px = _slippage_commission_per_share(hedge_entry_px, cfg, 'buy', shares=hedge_shares_l)
    hedge_pnl_l = (hedge_entry_px - hedge_exit_px) * hedge_shares_l
    hours_held_l = 2
    hedge_notional_l = hedge_entry_px * hedge_shares_l
    hedge_funding_l = _apply_funding_pnl(hedge_notional_l, hours_held_l, rate, 'short')
    hedge_pnl_l -= hedge_funding_l

    # Rebound short opens at idx 6, loop-else final exit at idx 11
    short_entry_px = _slippage_commission_per_share(long_exit_px, cfg, 'sell', shares=SHARES)
    short_start_idx = 6
    short_exit_px = _slippage_commission_per_share(COIN[11]["close"], cfg, 'buy', shares=SHARES)
    short_coin_gross = (short_entry_px - short_exit_px) * SHARES
    hours_held_short = len(COIN) - short_start_idx  # 6
    short_funding = _apply_funding_pnl(short_entry_px * SHARES, hours_held_short, rate, 'short')
    short_pnl = short_coin_gross - short_funding

    # Rebound-leg ETH hedge (long), established at idx 6
    r_hedge_value = compute_eth_hedge_size(COIN[:7], eth[:7], short_entry_px * SHARES, cfg)
    eth_entry_raw_r = eth[6]["open"]
    r_hedge_shares = r_hedge_value / eth_entry_raw_r
    r_hedge_entry_px = _slippage_commission_per_share(eth_entry_raw_r, cfg, 'buy', shares=r_hedge_shares)
    # Final exit at idx 11: aligned iff eth_len > 11
    if eth_len > 11:
        eth_exit_raw_r = eth[11]["close"]
        r_hedge_exit_px = _slippage_commission_per_share(eth_exit_raw_r, cfg, 'sell', shares=r_hedge_shares)
    else:
        # engine fallback: uses hedge_info['entry'] and re-applies exit fill
        r_hedge_exit_px = _slippage_commission_per_share(r_hedge_entry_px, cfg, 'sell', shares=r_hedge_shares)
    rebound_hedge_pnl = (r_hedge_exit_px - r_hedge_entry_px) * r_hedge_shares
    hours_held_r = len(COIN) - short_start_idx  # 6
    rh_notional = r_hedge_entry_px * r_hedge_shares
    rh_funding = _apply_funding_pnl(rh_notional, hours_held_r, rate, 'long')
    rebound_hedge_pnl -= rh_funding

    total_pnl = long_coin_pnl + hedge_pnl_l + short_pnl + rebound_hedge_pnl
    max_live = max(entry_px * SHARES, short_entry_px * SHARES)

    return {
        "entry_px": entry_px,
        "long_exit_px": long_exit_px,
        "long_coin_pnl": long_coin_pnl,
        "funding_long": funding_long,
        "hedge_shares_l": hedge_shares_l,
        "hedge_entry_px": hedge_entry_px,
        "hedge_exit_px": hedge_exit_px,
        "hedge_pnl_l": hedge_pnl_l,
        "hedge_funding_l": hedge_funding_l,
        "short_entry_px": short_entry_px,
        "short_exit_px": short_exit_px,
        "short_pnl": short_pnl,
        "short_funding": short_funding,
        "r_hedge_shares": r_hedge_shares,
        "r_hedge_entry_px": r_hedge_entry_px,
        "r_hedge_exit_px": r_hedge_exit_px,
        "rebound_hedge_pnl": rebound_hedge_pnl,
        "rh_funding": rh_funding,
        "total_pnl": total_pnl,
        "max_live": max_live,
        # Engine/risk behavior locked by aligned both-hedges final-exit test:
        # realized = long-leg settlement (coin+long hedge) + rebound-short coin pnl only.
        "expected_realized": long_coin_pnl + hedge_pnl_l + short_pnl,
        "expected_funding_effect": funding_long + hedge_funding_l + short_funding + rh_funding,
        "bars_held": 7,
    }


EXP_ALIGNED = _trace(len(COIN))
EXP_MISSING_FINAL_ETH = _trace(11)  # final coin idx 11 absent in ETH -> rebound hedge fallback


def _assert_common(res, exp):
    assert res.exit_reason == "target_rebound_short"
    assert res.bars_held == exp["bars_held"]
    assert res.entry_timestamp == "2025-01-01T05:00:00"
    assert res.exit_timestamp == "2025-01-01T11:00:00"

    assert _close_to(res.entry_price, exp["entry_px"])
    assert _close_to(res.exit_price, exp["short_exit_px"])
    assert _close_to(res.shares, SHARES)
    assert _close_to(res.max_live_coin_notional, exp["max_live"])

    assert res.hedge_side == "short" and (res.hedge_size or 0.0) > 0.0
    assert _close_to(res.hedge_size, exp["hedge_shares_l"])
    assert _close_to(res.hedge_entry, exp["hedge_entry_px"])
    assert _close_to(res.hedge_exit, exp["hedge_exit_px"])
    assert res.rebound_hedge_side == "long" and (res.rebound_hedge_size or 0.0) > 0.0
    assert _close_to(res.rebound_hedge_size, exp["r_hedge_shares"])
    assert _close_to(res.rebound_hedge_entry, exp["r_hedge_entry_px"])
    assert _close_to(res.rebound_hedge_exit, exp["r_hedge_exit_px"])

    assert _close_to(res.pnl, exp["long_coin_pnl"] + exp["hedge_pnl_l"])
    assert _close_to(res.hedge_pnl, exp["hedge_pnl_l"] + exp["rebound_hedge_pnl"])
    assert _close_to(res.rebound_short_pnl, exp["short_pnl"])
    assert _close_to(res.rebound_hedge_pnl, exp["rebound_hedge_pnl"])
    assert _close_to(res.total_pnl, exp["total_pnl"])

    assert isinstance(res.trades, list) and len(res.trades) == 2
    long_leg, short_leg = res.trades
    assert long_leg["side"] == "long" and long_leg["reason"] == "target"
    assert _close_to(long_leg["entry"], exp["entry_px"])
    assert _close_to(long_leg["exit"], exp["long_exit_px"])
    assert _close_to(long_leg["pnl"], exp["long_coin_pnl"])
    assert short_leg["side"] == "short" and short_leg["reason"] == "time_exit"
    assert _close_to(short_leg["entry"], exp["short_entry_px"])
    assert _close_to(short_leg["exit"], exp["short_exit_px"])
    assert _close_to(short_leg["pnl"], exp["short_pnl"])


def test_both_hedges_final_exit_missing_eth_at_final_bar_rebound_fallback_traced():
    eth = ETH_FULL[:11]  # missing final coin idx 11
    res = backtest_simple(COIN, _sig(), config=_cfg(RATE), eth_candles=eth)
    _assert_common(res, EXP_MISSING_FINAL_ETH)
    # rebound hedge exit must differ from aligned real-bar exit and follow fallback
    assert not _close_to(res.rebound_hedge_exit, EXP_ALIGNED["r_hedge_exit_px"])
    assert _close_to(res.rebound_hedge_exit, EXP_MISSING_FINAL_ETH["r_hedge_exit_px"])
    # long-leg hedge exit remains aligned at target bar idx 6
    assert _close_to(res.hedge_exit, EXP_ALIGNED["hedge_exit_px"])


def test_both_hedges_final_exit_missing_eth_at_final_bar_risk_state_and_funding_parity():
    rs_on = DailyRiskState()
    eth = ETH_FULL[:11]
    on = backtest_simple(COIN, _sig(), config=_cfg(RATE), eth_candles=eth, risk_state=rs_on)
    off = backtest_simple(COIN, _sig(), config=_cfg(0.0), eth_candles=eth)

    assert on.exit_reason == "target_rebound_short"
    assert off.exit_reason == "target_rebound_short"
    assert _close_to(on.total_pnl, EXP_MISSING_FINAL_ETH["total_pnl"])

    assert rs_on.open_positions == 0
    assert _close_to(rs_on.gross_exposure, 0.0)
    assert rs_on.open_position_notionals == []
    assert _close_to(rs_on.realized_pnl, EXP_MISSING_FINAL_ETH["expected_realized"])

    delta = on.total_pnl - off.total_pnl
    assert _close_to(delta, -EXP_MISSING_FINAL_ETH["expected_funding_effect"])
    assert abs(delta) > 1e-9
    assert (on.rebound_hedge_size or 0.0) > 0.0
