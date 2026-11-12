"""Regression lock (2026-11-12): REBOUND-SHORT TARGET exit with BOTH long-leg ETH
hedge AND rebound-short ETH hedge established and funded simultaneously × cap-cut
shares × commission_min × entry_next_bar × nonzero hourly funding on every leg/exit.

Uncovered cell (gap proof 2026-11-12): no `tests/*both*hedge*target*` exists.
Single-hedge rebound-short target coverage exists in
`tests/test_rebound_short_target_aligned_eth_commission_min_cap_cut_shares_20261109.py`
and missing-ETH/fallback variants, but not both hedges together. This locks the
primary target: both-leg simultaneous ETH hedges through the rebound-short TARGET
path (target precedence only when liquidation/+40% stop not triggered first),
per-leg reconciliation, `total_pnl`, `max_live_coin_notional`, `DailyRiskState`
settlement/release parity, funding on/off deltas — in (1) aligned ETH exits and
(2) missing/absent ETH bar at the target exit index for the rebound hedge while the
long-leg hedge exit remains aligned, and (3) both hedge exits absent (ETH series
ends before the long target bar).

Spec: hourly funding on every leg/exit (coin long, long-leg short ETH hedge,
rebound short coin, rebound-leg long ETH hedge). Hedge sizing uses
eth_candles[:idx+1] (no look-ahead), aligned entries. Entry at next bar open when
entry_next_bar=True. commission_min applied per share. 120% cap cuts shares
(signal.size_shares pre-cut). Rebound -9%/48h/+40% anchored to executed short
entry; strict no-look-ahead.

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


RATE = 0.01  # pct per hour
SLIP = 0.001
COMM_MIN = 0.5
SHARES = 10.0  # cap-cut shares

# 15 bars 0..14.
# - idx 3: signal bar (close 102)
# - idx 4: long entry bar (open 100.0) via entry_next_bar; signal_index=3 -> start_idx=4
# - idx 5..7: coin climbs but stays below re-anchored target (high 103/105/107)
# - idx 8: long +9% target hit (high 110 >= target_px) -> long closes target,
#          rebound short opens at idx 8, both ETH hedges established at bar 8 aligned
# - idx 9: coin drops below rebound short target (low 95 <= short_target) -> TARGET fires
#          at sidx=9 (target precedence only when liquidation/+40% stop not triggered first)
# - idx 10..14: unreachable after target break
COIN = [_c(f"2025-01-01T{i:02d}:00:00", 100.0, 101.0, 99.0, 100.0) for i in range(15)]
COIN[3] = _c("2025-01-01T03:00:00", 102.0, 105.0, 97.0, 102.0)   # signal bar idx 3
COIN[4] = _c("2025-01-01T04:00:00", 100.0, 101.0, 98.0, 100.0)   # long entry bar idx 4
COIN[5] = _c("2025-01-01T05:00:00", 102.5, 103.0, 102.0, 102.5)
COIN[6] = _c("2025-01-01T06:00:00", 104.0, 105.0, 103.5, 104.0)
COIN[7] = _c("2025-01-01T07:00:00", 106.0, 107.0, 105.5, 106.0)
COIN[8] = _c("2025-01-01T08:00:00", 109.5, 110.0, 109.0, 109.5)  # long target hit idx 8
COIN[9] = _c("2025-01-01T09:00:00", 108.0, 112.0, 95.0, 108.0)   # rebound short target hit idx 9
for i in range(10, 15):
    COIN[i] = _c(f"2025-01-01T{i:02d}:00:00", 108.0, 112.0, 105.0, 108.0)

# ETH aligned/available through all coin bars by default.
ETH_FULL = [_c(f"2025-01-01T{i:02d}:00:00", 2000.0 + i * 5, 2020.0 + i * 5, 1980.0 + i * 5, 2005.0 + i * 5) for i in range(15)]


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
        rebound_short_time_exit_bars=48,  # target at idx 9 fires well before 48h
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
        timestamp="2025-01-01T03:00:00",
        size_shares=SHARES,  # cap-cut shares
        signal_index=3,
    )


def _trace(eth_len=len(COIN), rate=RATE):
    """Hand-traced expected values from engine math for COIN/ETH/_sig/_cfg.

    Mirrors src/backtest/engine.py sequencing: entry_next_bar re-anchors stop/target
    to the slippage-adjusted fill; long target hit at idx 8; rebound short loop
    checks liquidation > stop > target > time-exit from sidx=9; target fires at sidx=9
    (low 95 <= short_target); hedge exit uses ETH[sidx]/ETH[idx] when available, else
    falls back to hedge_info['entry'] (engine re-applies exit slippage/commission on
    that adjusted entry fill on the fallback path).
    `hours_held_short = sidx - short_start_idx + 1`.
    """
    cfg = _cfg(rate)
    eth = ETH_FULL[:eth_len]
    entry_raw = 100.0  # signal.entry_price
    next_open = 100.0  # COIN[4].open
    entry_px = _slippage_commission_per_share(next_open, cfg, 'buy', shares=SHARES)

    # entry_next_bar re-anchor scales stop/target.
    ratio = entry_px / entry_raw
    target_px = 109.0 * ratio

    # Long target hit at idx 8 (high 110 >= target_px).
    long_exit_px = _slippage_commission_per_share(target_px, cfg, 'sell', shares=SHARES)
    long_coin_gross = (long_exit_px - entry_px) * SHARES
    hours_held_long = 8 - 4 + 1  # 5
    funding_long = _apply_funding_pnl(entry_px * SHARES, hours_held_long, rate, 'long')
    long_coin_pnl = long_coin_gross - funding_long

    # Long-leg ETH hedge (short), established at entry idx 4, aligned to ETH[4].open,
    # sized on history candles[:5] / ETH[:5] (no look-ahead).
    hedge_value_l = compute_eth_hedge_size(COIN[:5], eth[:5], entry_px * SHARES, cfg)
    eth_entry_raw_l = eth[4]["open"]
    hedge_shares_l = hedge_value_l / eth_entry_raw_l
    hedge_entry_px = _slippage_commission_per_share(eth_entry_raw_l, cfg, 'sell', shares=hedge_shares_l)
    # Exit at target bar idx 8: aligned ETH bar iff eth_len > 8; otherwise engine
    # fallback to hedge_info['entry'] with exit slippage/commission re-applied.
    if eth_len > 8:
        eth_exit_raw_l = eth[8]["close"]
        hedge_exit_px = _slippage_commission_per_share(eth_exit_raw_l, cfg, 'buy', shares=hedge_shares_l)
    else:
        hedge_exit_px = _slippage_commission_per_share(hedge_entry_px, cfg, 'buy', shares=hedge_shares_l)
    hedge_pnl_l = (hedge_entry_px - hedge_exit_px) * hedge_shares_l
    hours_held_l = 5
    hedge_notional_l = hedge_entry_px * hedge_shares_l
    hedge_funding_l = _apply_funding_pnl(hedge_notional_l, hours_held_l, rate, 'short')
    hedge_pnl_l -= hedge_funding_l

    # Rebound short opens at idx 8 at sell-side of long target exit fill.
    short_entry_px = _slippage_commission_per_share(long_exit_px, cfg, 'sell', shares=SHARES)
    short_start_idx = 8
    short_target = short_entry_px * (1.0 - 9.0 / 100.0)
    # Target fires at sidx=9 (low 95 <= short_target).
    sidx = 9
    short_exit = _slippage_commission_per_share(short_target, cfg, 'buy', shares=SHARES)
    short_coin_gross = (short_entry_px - short_exit) * SHARES
    hours_held_short = sidx - short_start_idx + 1  # 2
    short_funding = _apply_funding_pnl(short_entry_px * SHARES, hours_held_short, rate, 'short')
    short_pnl = short_coin_gross - short_funding

    # Rebound-leg ETH hedge (long), established at rebound idx 8, aligned to ETH[8].open,
    # sized on history candles[:9] / ETH[:9] (no look-ahead; eth history truncated by eth_len).
    r_hedge_value = compute_eth_hedge_size(COIN[:min(9, len(COIN))], eth[:min(9, len(eth))], short_entry_px * SHARES, cfg)
    eth_entry_raw_r = eth[min(8, eth_len - 1)]["open"]
    r_hedge_shares = r_hedge_value / eth_entry_raw_r
    r_hedge_entry_px = _slippage_commission_per_share(eth_entry_raw_r, cfg, 'buy', shares=r_hedge_shares)
    # Exit at target sidx=9: aligned ETH bar iff eth_len > 9; otherwise fallback.
    if eth_len > 9:
        eth_exit_raw_r = eth[9]["close"]
        r_hedge_exit_px = _slippage_commission_per_share(eth_exit_raw_r, cfg, 'sell', shares=r_hedge_shares)
    else:
        r_hedge_exit_px = _slippage_commission_per_share(r_hedge_entry_px, cfg, 'sell', shares=r_hedge_shares)
    rebound_hedge_pnl = (r_hedge_exit_px - r_hedge_entry_px) * r_hedge_shares
    hours_held_r = sidx - short_start_idx + 1  # 2
    rh_notional = r_hedge_entry_px * r_hedge_shares
    rh_funding = _apply_funding_pnl(rh_notional, hours_held_r, rate, 'long')
    rebound_hedge_pnl -= rh_funding

    total_pnl = long_coin_pnl + hedge_pnl_l + short_pnl + rebound_hedge_pnl
    max_live = max(entry_px * SHARES, short_entry_px * SHARES)

    return {
        "eth_len": eth_len,
        "entry_px": entry_px,
        "long_exit_px": long_exit_px,
        "long_coin_pnl": long_coin_pnl,
        "funding_long": funding_long,
        "hedge_shares_l": hedge_shares_l,
        "hedge_entry_px": hedge_entry_px,
        "hedge_exit_px": hedge_exit_px,
        "hedge_pnl_l": hedge_pnl_l,
        "hedge_funding_l": hedge_funding_l,
        "hedge_notional_l": hedge_notional_l,
        "short_entry_px": short_entry_px,
        "short_target": short_target,
        "short_exit": short_exit,
        "short_pnl": short_pnl,
        "short_funding": short_funding,
        "r_hedge_shares": r_hedge_shares,
        "r_hedge_entry_px": r_hedge_entry_px,
        "r_hedge_exit_px": r_hedge_exit_px,
        "rebound_hedge_pnl": rebound_hedge_pnl,
        "rh_funding": rh_funding,
        "rh_notional": rh_notional,
        "total_pnl": total_pnl,
        "max_live": max_live,
        "expected_realized": total_pnl,
        "expected_funding_effect": funding_long + hedge_funding_l + short_funding + rh_funding,
        "bars_held": sidx - 4 + 1,  # 6
    }


EXP_ALIGNED = _trace(len(COIN))
EXP_MISSING_REBOUND_ETH = _trace(9)  # ETH ends at idx 8: rebound hedge exit at sidx=9 falls back
EXP_MISSING_BOTH_ETH = _trace(8)     # ETH ends at idx 7: both hedge exits fall back


def test_both_hedges_rebound_short_target_aligned_eth_exits_traced():
    res = backtest_simple(COIN, _sig(), config=_cfg(RATE), eth_candles=ETH_FULL)

    assert res.exit_reason == "target_rebound_short"
    assert res.bars_held == EXP_ALIGNED["bars_held"]
    assert res.entry_timestamp == "2025-01-01T04:00:00"
    assert res.exit_timestamp == "2025-01-01T09:00:00"

    assert _close_to(res.entry_price, EXP_ALIGNED["entry_px"])
    assert _close_to(res.exit_price, EXP_ALIGNED["short_exit"])
    assert _close_to(res.shares, SHARES)
    assert _close_to(res.max_live_coin_notional, EXP_ALIGNED["max_live"])

    # Both ETH hedges established simultaneously and funded.
    assert res.hedge_side == "short" and (res.hedge_size or 0.0) > 0.0
    assert _close_to(res.hedge_size, EXP_ALIGNED["hedge_shares_l"])
    assert _close_to(res.hedge_entry, EXP_ALIGNED["hedge_entry_px"])
    assert _close_to(res.hedge_exit, EXP_ALIGNED["hedge_exit_px"])
    assert res.rebound_hedge_side == "long" and (res.rebound_hedge_size or 0.0) > 0.0
    assert _close_to(res.rebound_hedge_size, EXP_ALIGNED["r_hedge_shares"])
    assert _close_to(res.rebound_hedge_entry, EXP_ALIGNED["r_hedge_entry_px"])
    assert _close_to(res.rebound_hedge_exit, EXP_ALIGNED["r_hedge_exit_px"])

    # Per-leg PnL reconciliation.
    assert _close_to(res.pnl, EXP_ALIGNED["long_coin_pnl"] + EXP_ALIGNED["hedge_pnl_l"])
    assert _close_to(res.hedge_pnl, EXP_ALIGNED["hedge_pnl_l"] + EXP_ALIGNED["rebound_hedge_pnl"])
    assert _close_to(res.rebound_short_pnl, EXP_ALIGNED["short_pnl"])
    assert _close_to(res.rebound_hedge_pnl, EXP_ALIGNED["rebound_hedge_pnl"])
    assert _close_to(res.total_pnl, EXP_ALIGNED["total_pnl"])

    assert isinstance(res.trades, list) and len(res.trades) == 2
    long_leg, short_leg = res.trades
    assert long_leg["side"] == "long" and long_leg["reason"] == "target"
    assert _close_to(long_leg["entry"], EXP_ALIGNED["entry_px"])
    assert _close_to(long_leg["exit"], EXP_ALIGNED["long_exit_px"])
    assert _close_to(long_leg["pnl"], EXP_ALIGNED["long_coin_pnl"])
    assert short_leg["side"] == "short" and short_leg["reason"] == "target"
    assert _close_to(short_leg["entry"], EXP_ALIGNED["short_entry_px"])
    assert _close_to(short_leg["exit"], EXP_ALIGNED["short_exit"])
    assert _close_to(short_leg["pnl"], EXP_ALIGNED["short_pnl"])


def test_both_hedges_rebound_short_target_missing_rebound_eth_at_exit_fallback():
    """ETH series ends at idx 8: long-leg hedge exit at target bar idx 8 is aligned,
    rebound-leg hedge exit at target sidx=9 is ABSENT -> engine falls back to its
    entry fill price (re-applied exit slippage/commission)."""
    eth = ETH_FULL[:9]
    res = backtest_simple(COIN, _sig(), config=_cfg(RATE), eth_candles=eth)
    exp = EXP_MISSING_REBOUND_ETH

    assert res.exit_reason == "target_rebound_short"
    assert res.bars_held == exp["bars_held"]
    assert res.entry_timestamp == "2025-01-01T04:00:00"
    assert res.exit_timestamp == "2025-01-01T09:00:00"

    assert _close_to(res.entry_price, exp["entry_px"])
    assert _close_to(res.exit_price, exp["short_exit"])
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
    assert short_leg["side"] == "short" and short_leg["reason"] == "target"
    assert _close_to(short_leg["entry"], exp["short_entry_px"])
    assert _close_to(short_leg["exit"], exp["short_exit"])
    assert _close_to(short_leg["pnl"], exp["short_pnl"])


def test_both_hedges_rebound_short_target_missing_both_eth_at_exit_fallback():
    """ETH series ends at idx 7: both hedge exits (long-leg at target bar idx 8,
    rebound-leg at target sidx=9) are ABSENT -> both fall back to their entry fill
    prices (re-applied exit slippage/commission)."""
    eth = ETH_FULL[:8]
    res = backtest_simple(COIN, _sig(), config=_cfg(RATE), eth_candles=eth)
    exp = EXP_MISSING_BOTH_ETH

    assert res.exit_reason == "target_rebound_short"
    assert res.bars_held == exp["bars_held"]
    assert res.entry_timestamp == "2025-01-01T04:00:00"
    assert res.exit_timestamp == "2025-01-01T09:00:00"

    assert _close_to(res.entry_price, exp["entry_px"])
    assert _close_to(res.exit_price, exp["short_exit"])
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
    assert short_leg["side"] == "short" and short_leg["reason"] == "target"
    assert _close_to(short_leg["entry"], exp["short_entry_px"])
    assert _close_to(short_leg["exit"], exp["short_exit"])
    assert _close_to(short_leg["pnl"], exp["short_pnl"])


def test_both_hedges_rebound_short_target_aligned_risk_state_and_funding_parity():
    rs_on = DailyRiskState()
    on = backtest_simple(COIN, _sig(), config=_cfg(RATE), eth_candles=ETH_FULL, risk_state=rs_on)
    off = backtest_simple(COIN, _sig(), config=_cfg(0.0), eth_candles=ETH_FULL)

    assert on.exit_reason == "target_rebound_short"
    assert off.exit_reason == "target_rebound_short"
    assert _close_to(on.total_pnl, EXP_ALIGNED["total_pnl"])

    # Risk state fully released: no open positions/exposure/notionals.
    assert rs_on.open_positions == 0
    assert _close_to(rs_on.gross_exposure, 0.0)
    assert rs_on.open_position_notionals == []
    # Realized = full long-leg settlement (coin + long hedge) + (short + rebound hedge).
    assert _close_to(rs_on.realized_pnl, EXP_ALIGNED["expected_realized"])

    # Funding parity: delta equals negative total funding effect across all four legs.
    delta = on.total_pnl - off.total_pnl
    assert _close_to(delta, -EXP_ALIGNED["expected_funding_effect"])
    assert abs(delta) > 1e-9
    assert (on.rebound_hedge_size or 0.0) > 0.0  # both-leg hedge presence guard
