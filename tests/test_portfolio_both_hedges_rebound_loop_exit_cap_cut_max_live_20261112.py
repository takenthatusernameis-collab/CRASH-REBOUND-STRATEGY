"""Regression lock (2026-11-12): PORTFOLIO/RUNNER-LEVEL both-hedged rebound loop-else
FINAL EXIT under same-bar batch cap-cut pressure, tracing per-leg PnL/funding and the
max_live_coin_notional reservation basis.

Gap proof (2026-11-12): `find tests -maxdepth 1 -name '*both_hedges*'` shows the
both-hedges engine terminal family (final-exit aligned + missing-final-ETH rebound
fallback, STOP/TARGET/TIME_EXIT/LIQUIDATION) is locked under
`cap_cut + commission_min + entry_next_bar`, but ONLY via low-level `backtest_simple`
fixtures. No portfolio/runner test covers BOTH ETH hedges through a rebound loop-else
final exit under batch equal-share cut pressure, with per-leg funding reconciliation,
`max_live_coin_notional` reservation basis, and risk_state settlement parity.
Existing portfolio rebound tests (`test_portfolio_cap_liquidation_rebound_interaction`,
`test_portfolio_risk_reconciliation`) use rebound TARGET exits and assert only clean
final-state zeroing, not traced per-leg values. `test_portfolio_rebound_max_live_inflation`
covers max_live reservation but WITHOUT ETH hedges. This cell is therefore uncovered.

Cell (b) of the HANDOFF next campaign: portfolio/runner-level traced cross-bar
reconciliation where both-hedged rebound meets cap-cut/reservation/settlement/
max_live_coin_notional semantics.

Scenario: capital=10000, 120% cap=12000. Symbols A and B fire the same decision bar
(bar 20, entry bar 21 @100) with size_shares=100 -> desired 10000 each, total 20000 >
cap -> batch equal-share cut to 6000 entry notional = 60 shares each (cuts only, no
top-up). Both hit +9% target at bar 22 -> rebound short opens at 109 (max_live
coin notional = 109*60 = 6540, rebound-inflated vs 6000 entry notional). ETH hedge on
every leg (coin and ETH moves mirror -> hedge ratio exactly 1.0 -> hedge value =
position value). Rebound shorts hold to series end (bar 59) -> loop-else FINAL EXIT
(short-leg reason time_exit, overall target_rebound_short). ETH series spans the final
coin bar -> both hedge exits aligned (no fallback).

Locked expectations (traced via real engine functions):
- equal-share entry-notional cut: 60 shares each, entry notional 6000 = cap/2,
  concurrent entry-notional gross = 12000 = cap, never exceeded.
- max_live_coin_notional = 6540 (rebound short entry at +9% target) — the runner
  records this as executed_notional; entry-notional cap binds at admission, max_live
  may exceed it at rebound pressure (known spec behavior, NOT a defect).
- per-trade total_pnl = long_coin + long_hedge + short_coin + rebound_hedge = 583.2.
- risk_state realized_pnl reconciles to sum of per-trade total_pnl = 1166.4.
- final state: open_positions=0, gross_exposure=0, open_position_notionals=[] (no leak).

Synthetic fixtures only; deterministic; not performance evidence. Hourly bar-by-bar only.
"""

from __future__ import annotations

import copy
from unittest.mock import patch

from src.backtest.engine import backtest_simple, _apply_funding_pnl
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal, compute_eth_hedge_size
from scripts.run_portfolio import run_portfolio_simulation


def _c(i, o, h, l, cl, v=1_000_000.0):
    return {"timestamp": f"t{i:04d}", "open": o, "high": h, "low": l, "close": cl, "volume": v}


def _close_to(x, y, tol=1e-9):
    return abs(float(x) - float(y)) <= tol


FUNDING_RATE = 0.01  # pct per hour
CAPITAL = 10000.0
CAP_VALUE = CAPITAL * 120.0 / 100.0  # 12000.0
SHARES_REQUESTED = 100.0
SHARES_ADMITTED = 60.0  # equal-share batch cut: cap/2 / 100 = 60
ENTRY_PX = 100.0
TARGET_PX = 109.0
SHORT_ENTRY_PX = 109.0
SHORT_EXIT_PX = 108.0
ETH_ENTRY_PX = 2000.0  # ETH mirrors coin x20; bar 21 open = 100 -> 2000


def _coin(i):
    if i < 21:
        close = 100.0 if i % 2 == 0 else 100.5
        return _c(i, close, close * 1.001, close * 0.999, close)
    if i == 21:  # long entry bar (entry next bar from signal bar 20)
        return _c(21, 100.0, 101.0, 99.0, 100.0)
    if i == 22:  # long +9% target hit -> rebound short opens
        return _c(22, 100.0, 110.0, 99.0, 109.0)
    return _c(i, 108.0, 109.0, 107.0, 108.0)  # flat rebound range, no stop/target/liq


def _eth(i):
    c = _coin(i)
    return {
        "timestamp": c["timestamp"],
        "open": 20.0 * c["open"],
        "high": 20.0 * c["high"],
        "low": 20.0 * c["low"],
        "close": 20.0 * c["close"],
        "volume": c["volume"],
    }


COIN = [_coin(i) for i in range(60)]
ETH = [_eth(i) for i in range(60)]


def _cfg():
    return StrategyConfig(
        use_rsi_trigger=False,
        enable_rebound_short=True,
        enable_eth_hedge=True,
        enable_liquidation_checks=False,
        entry_next_bar=True,
        min_daily_volume_usd=0.0,
        max_positions=10,
        gross_cap_pct=120.0,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
        funding_rate_pct_per_hour=FUNDING_RATE,
        rebound_short_time_exit_bars=1000,  # > series -> loop-else final exit
        time_exit_max_bars=2000,
        avoid_downtrend=False,
        regime_min_price=0.0,
        enable_volume_based_sizing=False,
        target_pct=9.0,
        rebound_short_target_pct=9.0,
        rebound_short_stop_pct=40.0,
        stop_atr_mult=8.0,
        hedge_vol_lookback_hours=336,
        hedge_cap_multiplier=3.0,
    )


def _sig(symbol):
    return Signal(
        symbol=symbol,
        side="long",
        reason="crash_then_rebound",
        entry_price=ENTRY_PX,
        stop_price=50.0,
        target_price=TARGET_PX,
        risk_per_share=20.0,
        size_shares=SHARES_REQUESTED,
        signal_index=20,
        timestamp="t0020",
    )


SIGNALS = {"A": _sig("A"), "B": _sig("B")}


def _fake_gen(hist, symbol=None, config=None, capital=100000.0, cache=None):
    idx = len(hist) - 1
    if idx == 20 and symbol in SIGNALS:
        s = copy.copy(SIGNALS[symbol])
        s.signal_index = idx
        return s
    return None


def _trace():
    """Hand-traced expected values mirroring src/backtest/engine.py math.

    entry_next_bar, entry_px == signal entry (100) -> no stop/target re-anchor.
    Long target hit bar 22 (high 110 >= 109). Rebound short opens bar 22 @109.
    Rebound holds bars 23..59 (low 107 > short_target 99.19; high 109 < short_stop
    152.6; liquidation off; 1000-bar time cap not reached) -> loop-else final exit
    bar 59 @108. ETH mirrors coin x20 -> hedge ratio exactly 1.0 -> hedge value =
    position value; both hedge exits aligned (ETH through final bar 59).
    """
    cfg = _cfg()
    shares = SHARES_ADMITTED

    # Long leg: entry bar 21 @100, target bar 22 @109, 2 hours held.
    long_coin_gross = (TARGET_PX - ENTRY_PX) * shares  # 540
    funding_long = _apply_funding_pnl(ENTRY_PX * shares, 2, FUNDING_RATE, "long")  # 1.2
    long_coin_pnl = long_coin_gross - funding_long  # 538.8

    # Long-leg ETH hedge (short), entry bar 21 @2000, exit bar 22 @2180, 2 hours.
    hedge_value_l = compute_eth_hedge_size(COIN[:22], ETH[:22], ENTRY_PX * shares, cfg)
    hedge_shares_l = hedge_value_l / ETH_ENTRY_PX  # 3.0
    hedge_exit_px = 20.0 * COIN[22]["close"]  # 2180
    hedge_pnl_l_gross = (ETH_ENTRY_PX - hedge_exit_px) * hedge_shares_l  # -540
    hedge_funding_l = _apply_funding_pnl(ETH_ENTRY_PX * hedge_shares_l, 2, FUNDING_RATE, "short")  # -1.2
    hedge_pnl_l = hedge_pnl_l_gross - hedge_funding_l  # -538.8

    # Rebound short: entry bar 22 @109, loop-else final exit bar 59 @108, 38 hours.
    short_coin_gross = (SHORT_ENTRY_PX - SHORT_EXIT_PX) * shares  # 60
    hours_held_short = len(COIN) - 22  # 38
    short_funding = _apply_funding_pnl(SHORT_ENTRY_PX * shares, hours_held_short, FUNDING_RATE, "short")  # -24.852
    short_pnl = short_coin_gross - short_funding  # 84.852

    # Rebound-leg ETH hedge (long), entry bar 22 @2000, exit bar 59 @2160, 38 hours.
    r_hedge_value = compute_eth_hedge_size(COIN[:23], ETH[:23], SHORT_ENTRY_PX * shares, cfg)
    r_hedge_shares = r_hedge_value / ETH_ENTRY_PX  # 3.27
    r_hedge_exit_px = 20.0 * COIN[59]["close"]  # 2160
    rebound_hedge_pnl_gross = (r_hedge_exit_px - ETH_ENTRY_PX) * r_hedge_shares  # 523.2
    rh_funding = _apply_funding_pnl(ETH_ENTRY_PX * r_hedge_shares, hours_held_short, FUNDING_RATE, "long")  # 24.852
    rebound_hedge_pnl = rebound_hedge_pnl_gross - rh_funding  # 498.348

    total_pnl = long_coin_pnl + hedge_pnl_l + short_pnl + rebound_hedge_pnl  # 583.2
    max_live = max(ENTRY_PX * shares, SHORT_ENTRY_PX * shares)  # 6540 (rebound-inflated)

    return {
        "shares": shares,
        "entry_px": ENTRY_PX,
        "long_exit_px": TARGET_PX,
        "short_entry_px": SHORT_ENTRY_PX,
        "short_exit_px": SHORT_EXIT_PX,
        "long_coin_pnl": long_coin_pnl,
        "funding_long": funding_long,
        "hedge_shares_l": hedge_shares_l,
        "hedge_entry_px": ETH_ENTRY_PX,
        "hedge_exit_px": hedge_exit_px,
        "hedge_pnl_l": hedge_pnl_l,
        "hedge_funding_l": hedge_funding_l,
        "short_pnl": short_pnl,
        "short_funding": short_funding,
        "r_hedge_shares": r_hedge_shares,
        "r_hedge_entry_px": ETH_ENTRY_PX,
        "r_hedge_exit_px": r_hedge_exit_px,
        "rebound_hedge_pnl": rebound_hedge_pnl,
        "rh_funding": rh_funding,
        "total_pnl": total_pnl,
        "max_live": max_live,
        "bars_held": len(COIN) - 21,  # 39
    }


EXP = _trace()


def test_portfolio_both_hedges_rebound_loop_exit_traced_per_trade():
    with patch("scripts.run_portfolio.generate_signal", side_effect=_fake_gen):
        res = run_portfolio_simulation(
            {"A": COIN, "B": COIN},
            config=_cfg(),
            capital=CAPITAL,
            eth_candles={"ETH": ETH},
            require_eth_hedge=True,
        )

    assert res["num_trades"] == 2, res["trades"]
    by = {t["symbol"]: t for t in res["trades"]}
    assert set(by) == {"A", "B"}

    for sym in ("A", "B"):
        t = by[sym]
        # Batch equal-share entry-notional cut under cap pressure: 6000 each = cap/2,
        # concurrent entry-notional gross = 12000 = cap, cuts only no top-up.
        assert _close_to(t["shares"], EXP["shares"]), (sym, t)
        assert _close_to(t["entry_price"], EXP["entry_px"]), (sym, t)
        assert _close_to(float(t["shares"]) * float(t["entry_price"]), 6000.0), (sym, t)
        # Rebound loop-else final exit: overall target_rebound_short, short leg time_exit.
        assert t["exit_reason"] == "target_rebound_short", (sym, t)
        assert _close_to(t["bars_held"], EXP["bars_held"]), (sym, t)
        assert t["entry_timestamp"] == "t0021", (sym, t)
        assert t["exit_timestamp"] == "t0059", (sym, t)
        # Long-leg ETH hedge established (short hedge), aligned entry/exit.
        assert t["hedge_side"] == "short", (sym, t)
        assert _close_to(t["hedge_size"], EXP["hedge_shares_l"]), (sym, t)
        # Long-leg settlement (coin + long hedge) is res.pnl; total_pnl adds both rebound legs.
        assert _close_to(t["pnl"], EXP["long_coin_pnl"] + EXP["hedge_pnl_l"]), (sym, t)  # 0.0
        assert _close_to(t["hedge_pnl"], EXP["hedge_pnl_l"] + EXP["rebound_hedge_pnl"]), (sym, t)
        assert _close_to(t["total_pnl"], EXP["total_pnl"]), (sym, t)  # 583.2

    # Portfolio-level entry-notional cap binds at admission (equal share, cuts only).
    total_entry_notional = sum(float(by[s]["shares"]) * float(by[s]["entry_price"]) for s in by)
    assert _close_to(total_entry_notional, CAP_VALUE), total_entry_notional
    assert _close_to(float(res["total_pnl"]), 2.0 * EXP["total_pnl"])  # 1166.4

    # Final state fully released: no occupancy, exposure, or notional leak.
    assert res["final_open_positions"] == 0
    assert _close_to(float(res["final_gross_exposure"]), 0.0)
    rs = res["risk_state"]
    assert getattr(rs, "open_positions", -1) == 0
    assert _close_to(float(getattr(rs, "gross_exposure", -1.0)), 0.0)
    assert list(getattr(rs, "open_position_notionals", ["leak"])) == []
    # Settlement reconciliation: master risk_state realizes sum of per-trade total_pnl.
    assert _close_to(float(getattr(rs, "realized_pnl", 0.0)), 2.0 * EXP["total_pnl"])  # 1166.4


def test_portfolio_both_hedges_rebound_loop_exit_risk_state_parity():
    with patch("scripts.run_portfolio.generate_signal", side_effect=_fake_gen):
        res = run_portfolio_simulation(
            {"A": COIN, "B": COIN},
            config=_cfg(),
            capital=CAPITAL,
            eth_candles={"ETH": ETH},
            require_eth_hedge=True,
        )

    rs = res["risk_state"]
    assert _close_to(float(getattr(rs, "realized_pnl", 0.0)), 2.0 * EXP["total_pnl"])
    assert _close_to(float(res["total_pnl"]), 2.0 * EXP["total_pnl"])


def test_engine_rebound_max_live_coin_notional_reservation_basis():
    """Engine-level lock: TradeResult.max_live_coin_notional is the rebound-inflated
    short-entry notional (6540), not the 6000 entry notional. This is the value the
    portfolio runner records as executed_notional for the reservation overlay, so the
    max_live basis may exceed the entry-notional cap at rebound pressure (known spec
    behavior, preserved, not a defect)."""
    cfg = _cfg()
    sig = _sig("A")
    sig.size_shares = SHARES_ADMITTED  # mirror runner's post-batch-cut admission (60 shares)
    res = backtest_simple(COIN, sig, config=cfg, capital=CAPITAL, eth_candles=ETH)

    assert res.exit_reason == "target_rebound_short"
    assert _close_to(res.entry_price, EXP["entry_px"])
    assert _close_to(res.shares, EXP["shares"])
    assert _close_to(res.exit_price, EXP["short_exit_px"])
    assert _close_to(res.total_pnl, EXP["total_pnl"])  # 583.2 all four legs
    assert _close_to(res.pnl, EXP["long_coin_pnl"] + EXP["hedge_pnl_l"])  # long-leg settlement only
    assert _close_to(res.rebound_short_pnl, EXP["short_pnl"])  # 84.852
    assert _close_to(res.rebound_hedge_pnl, EXP["rebound_hedge_pnl"])  # 498.348
    assert _close_to(res.max_live_coin_notional, EXP["max_live"])  # 6540 rebound-inflated
    assert _close_to(res.hedge_size, EXP["hedge_shares_l"])
    assert _close_to(res.rebound_hedge_size, EXP["r_hedge_shares"])
    assert _close_to(res.hedge_exit, EXP["hedge_exit_px"])  # aligned, no fallback
    assert _close_to(res.rebound_hedge_exit, EXP["r_hedge_exit_px"])  # aligned, no fallback
    # Short-leg trade reason is time_exit (loop-else) while overall reason stays target_rebound_short.
    long_leg, short_leg = res.trades
    assert short_leg["side"] == "short" and short_leg["reason"] == "time_exit"
    assert _close_to(short_leg["pnl"], EXP["short_pnl"])


if __name__ == "__main__":
    import unittest
    unittest.main()
