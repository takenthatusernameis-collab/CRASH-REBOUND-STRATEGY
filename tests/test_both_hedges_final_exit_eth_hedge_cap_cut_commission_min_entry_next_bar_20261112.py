"""Regression lock (2026-11-12): FINAL EXIT (loop-else, end of coin series) with BOTH
long-leg ETH hedge AND rebound-short ETH hedge established and funded simultaneously
× cap-cut shares (signal.size_shares) × commission_min × entry_next_bar × nonzero
hourly funding on every leg/exit.

Uncovered cell vs existing coverage: the rebound-only final-exit locks
`tests/test_rebound_short_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_20261110.py`
(rebound-only aligned) and `..._missing_final_eth_20261110.py` (rebound-only missing-final-ETH);
`tests/test_long_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_20261110.py`
covers long-only. NONE cover both hedges together (no `tests/test*both*hedge*` exists). This
locks the primary target: both-leg simultaneous ETH hedges through the final-exit loop-else,
per-leg reconciliation, `DailyRiskState` close accounting parity, and funding on/off deltas.

Spec: hourly funding on every leg/exit (coin long, long-leg short ETH hedge, rebound short
coin, rebound-leg long ETH hedge). Hedge sizing uses eth_candles[:idx+1] (no look-ahead),
aligned entries. Entry at next bar open when entry_next_bar=True. commission_min applied
per share. 120% cap cuts shares (signal.size_shares pre-cut). Rebound -9%/48h/+40% anchored
to executed short entry; strict no-look-ahead.

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

# 12 bars 0..11.
# - idx 4: signal bar (close 102)
# - idx 5: long entry bar (open 100.0) via entry_next_bar; signal_index=4 -> start_idx=5
# - idx 6: long +9% target hit (high 110 >= re-anchored target) -> long closes target,
#          rebound short opens at idx 6, both ETH hedges established at bar 6 aligned
# - idx 7..11: rebound short holds (no stop/target/liq/48h), loop exhausts ->
#          FINAL EXIT (loop-else) at idx 11 close=108.0
COIN = [_c(f"2025-01-01T{i:02d}:00:00", 100.0, 101.0, 99.0, 100.0) for i in range(12)]
COIN[4] = _c("2025-01-01T04:00:00", 102.0, 105.0, 97.0, 102.0)   # signal bar idx 4
COIN[5] = _c("2025-01-01T05:00:00", 100.0, 101.0, 98.0, 99.0)    # long entry bar idx 5
COIN[6] = _c("2025-01-01T06:00:00", 109.0, 110.0, 108.0, 109.0)  # target hit idx 6
for i in range(7, 12):
    COIN[i] = _c(f"2025-01-01T{i:02d}:00:00", 108.0, 112.0, 105.0, 108.0)

# ETH aligned/available through final coin idx 11; enough variation for nonzero
# realized-vol hedge sizing on both legs (sized on eth_candles[:idx+1]).
ETH = [_c(f"2025-01-01T{i:02d}:00:00", 2000.0 + i * 5, 2020.0 + i * 5, 1980.0 + i * 5, 2005.0 + i * 5) for i in range(12)]


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
        rebound_short_time_exit_bars=100,  # > bars until series end -> loop-else final exit
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
        size_shares=SHARES,  # cap-cut shares
        signal_index=4,
    )


def _trace(rate=RATE):
    """Hand-traced expected values from engine math for COIN/ETH/_sig/_cfg(rate).

    Mirrors src/backtest/engine.py sequencing: entry_next_bar re-anchors stop/target to
    the slippage-adjusted fill; rebound-short checks liquidation > stop > target > time-exit;
    loop-else final exit at last bar; hedge exit falls back to hedge_info['entry'] when the
    final coin index is beyond eth_candles (here aligned, so the real bar is used).
    """
    cfg = _cfg(rate)
    entry_raw = 100.0  # signal.entry_price
    next_open = 100.0  # COIN[5].open
    comm_ps = max(0.0, COMM_MIN / SHARES)  # 0.05
    entry_px = next_open + next_open * SLIP + comm_ps  # buy-side fill, bar 5 open
    entry_px = _slippage_commission_per_share(next_open, cfg, 'buy', shares=SHARES)

    # entry_next_bar re-anchor (entry_px slippage-adjusted != raw entry) scales stop/target.
    ratio = entry_px / entry_raw
    target_px = 109.0 * ratio
    stop_px = 50.0 * ratio

    # Long target hit at idx 6 (high 110 >= target_px).
    long_exit_px = _slippage_commission_per_share(target_px, cfg, 'sell', shares=SHARES)
    long_coin_gross = (long_exit_px - entry_px) * SHARES
    hours_held_long = 6 - 5 + 1  # 2
    funding_long = _apply_funding_pnl(entry_px * SHARES, hours_held_long, rate, 'long')
    long_coin_pnl = long_coin_gross - funding_long

    # Long-leg ETH hedge (short), established at entry idx 5, aligned to ETH[5].open,
    # sized on history candles[:6] / ETH[:6] (no look-ahead).
    hedge_value_l = compute_eth_hedge_size(COIN[:6], ETH[:6], entry_px * SHARES, cfg)
    eth_entry_raw_l = ETH[5]["open"]
    hedge_shares_l = hedge_value_l / eth_entry_raw_l
    hedge_comm_ps_l = max(0.0, COMM_MIN / hedge_shares_l)
    hedge_entry_px = _slippage_commission_per_share(eth_entry_raw_l, cfg, 'sell', shares=hedge_shares_l)
    # Exit at idx 6 (aligned ETH bar available): close of ETH[6].
    eth_exit_raw_l = ETH[6]["close"]
    hedge_exit_px = _slippage_commission_per_share(eth_exit_raw_l, cfg, 'buy', shares=hedge_shares_l)
    hedge_pnl_l = (hedge_entry_px - hedge_exit_px) * hedge_shares_l
    hours_held_l = 2
    hedge_notional_l = hedge_entry_px * hedge_shares_l
    hedge_funding_l = _apply_funding_pnl(hedge_notional_l, hours_held_l, rate, 'short')
    hedge_pnl_l -= hedge_funding_l

    # Rebound short opens at idx 6 at sell-side of long target exit fill.
    short_entry_px = _slippage_commission_per_share(long_exit_px, cfg, 'sell', shares=SHARES)
    short_start_idx = 6
    # Loop-else final exit at last coin bar idx 11 close=108.0 (buy-side).
    short_exit_px = _slippage_commission_per_share(COIN[11]["close"], cfg, 'buy', shares=SHARES)
    short_coin_gross = (short_entry_px - short_exit_px) * SHARES
    hours_held_short = len(COIN) - short_start_idx  # 6
    short_funding = _apply_funding_pnl(short_entry_px * SHARES, hours_held_short, rate, 'short')
    short_pnl = short_coin_gross - short_funding

    # Rebound-leg ETH hedge (long), established at rebound idx 6, aligned to ETH[6].open,
    # sized on history candles[:7] / ETH[:7] (no look-ahead).
    r_hedge_value = compute_eth_hedge_size(COIN[:7], ETH[:7], short_entry_px * SHARES, cfg)
    eth_entry_raw_r = ETH[6]["open"]
    r_hedge_shares = r_hedge_value / eth_entry_raw_r
    r_hedge_comm_ps = max(0.0, COMM_MIN / r_hedge_shares)
    r_hedge_entry_px = _slippage_commission_per_share(eth_entry_raw_r, cfg, 'buy', shares=r_hedge_shares)
    # Exit at final coin idx 11 (aligned ETH bar available): close of ETH[11].
    eth_exit_raw_r = ETH[11]["close"]
    r_hedge_exit_px = _slippage_commission_per_share(eth_exit_raw_r, cfg, 'sell', shares=r_hedge_shares)
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
        "hedge_notional_l": hedge_notional_l,
        "short_entry_px": short_entry_px,
        "short_exit_px": short_exit_px,
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
        # Risk state realizes full long-leg settlement (coin + long hedge) at target close,
        # then only the rebound-short coin PnL at loop-else close (rebound hedge PnL excluded
        # from that apply_trade call) while total_pnl includes rebound_hedge_pnl.
        "expected_realized": long_coin_pnl + hedge_pnl_l + short_pnl,
        # Engine convention: pnl -= funding_component. Delta(on - off) = -(sum of all funding
        # components): long coin (cost), long short-hedge (benefit), short coin (benefit),
        # rebound long-hedge (cost).
        "expected_funding_effect": funding_long + hedge_funding_l + short_funding + rh_funding,
        "bars_held": 7,
    }


EXP = _trace(RATE)


def test_both_hedges_final_exit_loop_else_traced():
    res = backtest_simple(COIN, _sig(), config=_cfg(RATE), eth_candles=ETH)

    assert res.exit_reason == "target_rebound_short"
    assert res.bars_held == EXP["bars_held"]
    assert res.entry_timestamp == "2025-01-01T05:00:00"
    assert res.exit_timestamp == "2025-01-01T11:00:00"

    assert _close_to(res.entry_price, EXP["entry_px"])
    assert _close_to(res.exit_price, EXP["short_exit_px"])
    assert _close_to(res.shares, SHARES)
    assert _close_to(res.max_live_coin_notional, EXP["max_live"])

    # Both ETH hedges established simultaneously and funded.
    assert res.hedge_side == "short" and (res.hedge_size or 0.0) > 0.0
    assert _close_to(res.hedge_size, EXP["hedge_shares_l"])
    assert _close_to(res.hedge_entry, EXP["hedge_entry_px"])
    assert _close_to(res.hedge_exit, EXP["hedge_exit_px"])
    assert res.rebound_hedge_side == "long" and (res.rebound_hedge_size or 0.0) > 0.0
    assert _close_to(res.rebound_hedge_size, EXP["r_hedge_shares"])
    assert _close_to(res.rebound_hedge_entry, EXP["r_hedge_entry_px"])
    assert _close_to(res.rebound_hedge_exit, EXP["r_hedge_exit_px"])

    # Per-leg PnL reconciliation.
    assert _close_to(res.pnl, EXP["long_coin_pnl"] + EXP["hedge_pnl_l"])
    assert _close_to(res.hedge_pnl, EXP["hedge_pnl_l"] + EXP["rebound_hedge_pnl"])
    assert _close_to(res.rebound_short_pnl, EXP["short_pnl"])
    assert _close_to(res.rebound_hedge_pnl, EXP["rebound_hedge_pnl"])
    assert _close_to(res.total_pnl, EXP["total_pnl"])

    assert isinstance(res.trades, list) and len(res.trades) == 2
    long_leg, short_leg = res.trades
    assert long_leg["side"] == "long" and long_leg["reason"] == "target"
    assert _close_to(long_leg["entry"], EXP["entry_px"])
    assert _close_to(long_leg["exit"], EXP["long_exit_px"])
    assert _close_to(long_leg["pnl"], EXP["long_coin_pnl"])
    assert short_leg["side"] == "short" and short_leg["reason"] == "time_exit"
    assert _close_to(short_leg["entry"], EXP["short_entry_px"])
    assert _close_to(short_leg["exit"], EXP["short_exit_px"])
    assert _close_to(short_leg["pnl"], EXP["short_pnl"])


def test_both_hedges_final_exit_loop_else_risk_state_and_funding_parity():
    rs_on = DailyRiskState()
    on = backtest_simple(COIN, _sig(), config=_cfg(RATE), eth_candles=ETH, risk_state=rs_on)
    off = backtest_simple(COIN, _sig(), config=_cfg(0.0), eth_candles=ETH)

    assert on.exit_reason == "target_rebound_short"
    assert off.exit_reason == "target_rebound_short"
    assert _close_to(on.total_pnl, EXP["total_pnl"])

    # Risk state fully released: no open positions/exposure/notionals.
    assert rs_on.open_positions == 0
    assert _close_to(rs_on.gross_exposure, 0.0)
    assert rs_on.open_position_notionals == []
    # Realized = full long-leg settlement (coin + long hedge) + rebound-short coin PnL;
    # rebound-leg ETH hedge PnL excluded from risk_state apply_trade (locked engine behavior).
    assert _close_to(rs_on.realized_pnl, EXP["expected_realized"])

    # Funding parity: delta equals negative total funding effect across all four legs.
    delta = on.total_pnl - off.total_pnl
    assert _close_to(delta, -EXP["expected_funding_effect"])
    assert abs(delta) > 1e-9
    assert (on.rebound_hedge_size or 0.0) > 0.0  # both-leg hedge presence guard
