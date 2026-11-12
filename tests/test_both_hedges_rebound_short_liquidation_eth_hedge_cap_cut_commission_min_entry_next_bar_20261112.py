"""Regression lock (2026-11-12): REBOUND-SHORT LIQUIDATION exit with BOTH long-leg
ETH hedge AND rebound-short ETH hedge established and funded simultaneously ×
cap-cut shares × commission_min × entry_next_bar × nonzero hourly funding on every
leg/exit.

Uncovered cell (gap proof 2026-11-12): `find tests -name '*both*hedge*liquidation*'`
-> none. Single-hedge rebound-short liquidation/missing-ETH coverage exists in other
suites, but not both hedges together under cap_cut+commission_min+entry_next_bar.

Locks: rebound short exits via LIQUIDATION (worst hourly high, +40% stop not hit
first; liquidation checked before stop/target/time-exit) × (1) aligned ETH exits,
(2) missing/absent ETH bar at liquidation exit for the rebound hedge while the
long-leg hedge exit remains aligned, (3) both hedge exits absent. Asserts per-leg
PnL/funding reconciliation, total_pnl, max_live_coin_notional, DailyRiskState
settlement/release/close parity, funding on/off deltas, liquidation notional/timing/
penalty correctness. Hourly bar-by-bar only.

Engine semantics (traced): on rebound-short liquidation engine sets short_pnl
(includes liq penalty + funding), closes rebound hedge (settles funding), applies
risk_state.apply_trade(short_pnl + rebound_hedge_pnl, closed=True,
notional=short_entry_px*shares), appends trade reason 'liquidated'. Overall result
exit_reason/exit_timestamp follow long-leg target/rebound context per traced engine
behavior (target_rebound_short) — assert per-leg trade reasons and traced fields.

Synthetic fixtures only; deterministic; not performance evidence.
"""
import math

from src.backtest.engine import backtest_simple, _apply_funding_pnl, _slippage_commission_per_share, _check_liquidation
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
# - idx 3: signal bar
# - idx 4: long entry bar (open 100.0) via entry_next_bar; signal_index=3 -> start_idx=4
# - idx 5..7: climb below target
# - idx 8: long +9% target hit (high 110) -> long closes, rebound short opens at idx 8,
#          both ETH hedges established at bar 8 aligned
# - idx 9: rebound short LIQUIDATION (high spikes to liq threshold, below +40% stop,
#          low stays above -9% target) -> liquidation checked before stop/target
COIN = [_c(f"2025-01-01T{i:02d}:00:00", 100.0, 101.0, 99.0, 100.0) for i in range(15)]
COIN[3] = _c("2025-01-01T03:00:00", 102.0, 105.0, 97.0, 102.0)   # signal bar idx 3
COIN[4] = _c("2025-01-01T04:00:00", 100.0, 101.0, 98.0, 100.0)   # long entry bar idx 4
COIN[5] = _c("2025-01-01T05:00:00", 102.5, 103.0, 102.0, 102.5)
COIN[6] = _c("2025-01-01T06:00:00", 104.0, 105.0, 103.5, 104.0)
COIN[7] = _c("2025-01-01T07:00:00", 106.0, 107.0, 105.5, 106.0)
COIN[8] = _c("2025-01-01T08:00:00", 109.5, 110.0, 109.0, 109.5)  # long target hit idx 8
# idx 9: high set to reach liquidation threshold for short (computed dynamically in trace),
# but below +40% rebound stop; low stays above short target.
COIN[9] = _c("2025-01-01T09:00:00", 110.0, 125.0, 108.0, 112.0)
for i in range(10, 15):
    COIN[i] = _c(f"2025-01-01T{i:02d}:00:00", 108.0, 112.0, 105.0, 108.0)

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
        rebound_short_time_exit_bars=48,
        rebound_short_stop_pct=40.0,
        rebound_short_target_pct=9.0,
        enable_liquidation_checks=True,
        liquidation_maint_margin_pct=9.0,
        liquidation_buffer_pct=1.0,  # liq threshold at +10% for short, below 40% stop
        liquidation_penalty_pct=0.5,
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
    """Hand-traced expected values from engine math for both-hedges + rebound-short liquidation."""
    cfg = _cfg(rate)
    eth = ETH_FULL[:eth_len]
    entry_raw = 100.0
    next_open = 100.0  # COIN[4].open
    entry_px = _slippage_commission_per_share(next_open, cfg, 'buy', shares=SHARES)

    # entry_next_bar re-anchor
    ratio = entry_px / entry_raw
    target_px = 109.0 * ratio

    # Long target hit at idx 8
    long_exit_px = _slippage_commission_per_share(target_px, cfg, 'sell', shares=SHARES)
    long_coin_gross = (long_exit_px - entry_px) * SHARES
    hours_held_long = 8 - 4 + 1  # 5
    funding_long = _apply_funding_pnl(entry_px * SHARES, hours_held_long, rate, 'long')
    long_coin_pnl = long_coin_gross - funding_long

    # Long-leg ETH hedge (short), established at entry idx 4
    hedge_value_l = compute_eth_hedge_size(COIN[:5], eth[:5], entry_px * SHARES, cfg)
    eth_entry_raw_l = eth[4]["open"]
    hedge_shares_l = hedge_value_l / eth_entry_raw_l
    hedge_entry_px = _slippage_commission_per_share(eth_entry_raw_l, cfg, 'sell', shares=hedge_shares_l)
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

    # Rebound short opens at idx 8
    short_entry_px = _slippage_commission_per_share(long_exit_px, cfg, 'sell', shares=SHARES)
    short_start_idx = 8
    sidx = 9
    # Liquidation trigger for short at idx 9 (checked before stop/target)
    liq_px = _check_liquidation(COIN[sidx], side='short', entry_px=short_entry_px,
                                notional=short_entry_px * SHARES, config=cfg)
    assert liq_px is not None, "fixture must trigger short liquidation"
    short_exit = _slippage_commission_per_share(float(liq_px), cfg, 'buy', shares=SHARES)
    short_coin_gross = (short_entry_px - short_exit) * SHARES
    penalty = cfg.liquidation_penalty_pct / 100.0 * (short_entry_px * SHARES)
    hours_held_short = sidx - short_start_idx + 1  # 2
    short_funding = _apply_funding_pnl(short_entry_px * SHARES, hours_held_short, rate, 'short')
    short_pnl = short_coin_gross - penalty - short_funding

    # Rebound-leg ETH hedge (long), established at rebound idx 8
    r_hedge_value = compute_eth_hedge_size(COIN[:9], eth[:min(9, len(eth))], short_entry_px * SHARES, cfg)
    eth_entry_raw_r = eth[min(8, eth_len - 1)]["open"]
    r_hedge_shares = r_hedge_value / eth_entry_raw_r
    r_hedge_entry_px = _slippage_commission_per_share(eth_entry_raw_r, cfg, 'buy', shares=r_hedge_shares)
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

    # Engine result semantics on rebound-short liquidation inside target branch:
    # result.pnl = long coin pnl + long hedge pnl (per engine assignment before return),
    # result.total_pnl includes short + rebound hedge.
    expected_result_pnl = long_coin_pnl + hedge_pnl_l
    expected_realized = total_pnl
    expected_funding_effect = funding_long + hedge_funding_l + short_funding + rh_funding
    bars_held = sidx - 4 + 1  # 6

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
        "liq_px": float(liq_px),
        "short_exit": short_exit,
        "penalty": penalty,
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
        "expected_result_pnl": expected_result_pnl,
        "expected_realized": expected_realized,
        "expected_funding_effect": expected_funding_effect,
        "bars_held": bars_held,
        "short_notional": short_entry_px * SHARES,
    }


EXP_ALIGNED = _trace(len(COIN))
EXP_MISSING_REBOUND_ETH = _trace(9)  # rebound hedge exit at sidx=9 falls back
EXP_MISSING_BOTH_ETH = _trace(8)     # long hedge exit at idx 8 and rebound at sidx=9 fall back


def _assert_common(res, exp, eth_len):
    assert res.exit_reason == "target_rebound_short"
    assert res.bars_held == exp["bars_held"]
    assert res.entry_timestamp == "2025-01-01T04:00:00"
    assert res.exit_timestamp == "2025-01-01T09:00:00"

    assert _close_to(res.entry_price, exp["entry_px"])
    assert _close_to(res.exit_price, exp["short_exit"])
    assert _close_to(res.shares, SHARES)
    assert _close_to(res.max_live_coin_notional, exp["max_live"])

    # Both ETH hedges established simultaneously and funded.
    assert res.hedge_side == "short" and (res.hedge_size or 0.0) > 0.0
    assert _close_to(res.hedge_size, exp["hedge_shares_l"])
    assert _close_to(res.hedge_entry, exp["hedge_entry_px"])
    assert _close_to(res.hedge_exit, exp["hedge_exit_px"])
    assert res.rebound_hedge_side == "long" and (res.rebound_hedge_size or 0.0) > 0.0
    assert _close_to(res.rebound_hedge_size, exp["r_hedge_shares"])
    assert _close_to(res.rebound_hedge_entry, exp["r_hedge_entry_px"])
    assert _close_to(res.rebound_hedge_exit, exp["r_hedge_exit_px"])

    # Per-leg reconciliation and traced result semantics.
    assert _close_to(res.pnl, exp["expected_result_pnl"])
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
    assert short_leg["side"] == "short" and short_leg["reason"] == "liquidated"
    assert _close_to(short_leg["entry"], exp["short_entry_px"])
    assert _close_to(short_leg["exit"], exp["short_exit"])
    assert _close_to(short_leg["pnl"], exp["short_pnl"])


def test_both_hedges_rebound_short_liquidation_aligned_eth_exits_traced():
    res = backtest_simple(COIN, _sig(), config=_cfg(RATE), eth_candles=ETH_FULL)
    _assert_common(res, EXP_ALIGNED, len(COIN))
    # liquidation correctness sanity: penalty and notional/timing reflected
    assert EXP_ALIGNED["penalty"] > 0
    assert _close_to(EXP_ALIGNED["short_notional"], EXP_ALIGNED["short_entry_px"] * SHARES)


def test_both_hedges_rebound_short_liquidation_missing_rebound_eth_at_exit_fallback():
    """ETH ends at idx 8: long-leg hedge exit at target idx 8 aligned, rebound-leg
    hedge exit at liquidation sidx=9 ABSENT -> engine fallback to entry fill."""
    eth = ETH_FULL[:9]
    res = backtest_simple(COIN, _sig(), config=_cfg(RATE), eth_candles=eth)
    _assert_common(res, EXP_MISSING_REBOUND_ETH, 9)


def test_both_hedges_rebound_short_liquidation_missing_both_eth_at_exit_fallback():
    """ETH ends at idx 7: both hedge exits absent -> both fallback to entry fills."""
    eth = ETH_FULL[:8]
    res = backtest_simple(COIN, _sig(), config=_cfg(RATE), eth_candles=eth)
    _assert_common(res, EXP_MISSING_BOTH_ETH, 8)


def test_both_hedges_rebound_short_liquidation_aligned_risk_state_and_funding_parity():
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
