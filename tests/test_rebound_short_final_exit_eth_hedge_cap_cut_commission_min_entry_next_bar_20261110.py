"""Regression lock (2026-11-10): rebound-short FINAL EXIT (loop-else, end of coin
series, no in-loop target/stop/liquidation/48h break) with ALIGNED long ETH hedge
established at rebound entry × cap-cut shares (signal.size_shares) × commission_min
× entry_next_bar × nonzero hourly funding on every leg.

Uncovered cell vs existing coverage: rebound final-exit/48h locks exercise in-loop
breaks; `test_funding_every_leg_missing_eth_audit_20261107.py` covers loop-else only
with missing ETH (no aligned hedge, no traced commission_min/cap-cut/entry_next_bar
fills/PnL decomposition). This locks aligned-hedge traced fills, coin/hedge funding
and PnL decomposition, trades-log/risk_state settlement, and bars attribution.

Spec: hourly funding on every leg/exit (long coin, long-leg ETH hedge if any,
rebound short coin, rebound long ETH hedge). Hedge sizing uses eth_candles[:idx+1]
(no look-ahead) and rebound hedge entry aligns to the same bar idx. Entry at next
bar open when entry_next_bar=True. commission_min applied per share. 120% cap cuts
shares (signal.size_shares pre-cut). Equal-share/cap semantics represented via
cap-cut shares.

Synthetic fixtures only; deterministic; not performance evidence.
"""
import math

from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
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
# - idx 5: signal bar (close context not used as entry because entry_next_bar=True)
# - idx 6: long entry bar (open=100.0)
# - idx 7: long target hit (high=110 >= target 109) -> long closes, rebound short opens
#          rebound hedge entry aligned to idx 7 (no look-ahead)
# - idx 8..11: rebound short stays open (no stop/target/liq/48h), loop exhausts ->
#          FINAL EXIT (loop-else) at idx 11 close=108.0
COIN = [_c(f"2025-01-01T{i:02d}:00:00", 100.0, 101.0, 99.0, 100.0) for i in range(12)]
COIN[7] = _c("2025-01-01T07:00:00", 100.0, 110.0, 99.0, 109.0)
for i in range(8, 12):
    COIN[i] = _c(f"2025-01-01T{i:02d}:00:00", 108.0, 112.0, 105.0, 108.0)

# ETH series aligned/available through final coin idx 11 with enough variation for
# nonzero realized-vol hedge sizing.
ETH = []
for i in range(12):
    px = 2000.0 + (i % 2) * 100.0
    ETH.append(_c(f"2025-01-01T{i:02d}:00:00", px, px + 20.0, px - 20.0, px + 50.0 * (i % 3 - 1)))
for i in range(8, 12):
    ETH[i] = _c(f"2025-01-01T{i:02d}:00:00", 2100.0, 2120.0, 2080.0, 2110.0)


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
        time_exit_max_bars=50,
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
        timestamp="2025-01-01T05:00:00",
        size_shares=SHARES,  # cap-cut shares
        signal_index=5,
    )


# Engine-traced expected values for COIN/ETH/_sig/_cfg(RATE).
# Long leg: entry_next_bar -> idx6 open 100.0, buy-side fill with comm_min/share 0.05.
EXP_LONG_ENTRY = 100.14999999999999
EXP_LONG_EXIT = 109.0043365          # target 109, sell-side
EXP_LONG_COIN_PNL = 88.34306500000002  # gross - long funding (2h)
EXP_LONG_BARS = 2

# Rebound short (starts at idx7, exits loop-else at idx11):
# entry = sell-side fill of long target exit raw/px path per engine.
EXP_SHORT_ENTRY = 108.84533216349999
EXP_SHORT_EXIT = 108.158             # idx11 close 108.0, buy-side
EXP_SHORT_COIN_PNL = 7.417548295817383  # gross - short funding (5h)
EXP_SHORT_REASON = "time_exit"       # loop-else appends time_exit in current engine
EXP_SHORT_EXIT_TS = "2025-01-01T11:00:00"

# Rebound long ETH hedge (aligned to idx7, sized on history up to idx7 inclusive),
# exited at final coin idx11 (aligned ETH bar available).
EXP_REB_HEDGE_SIDE = "long"
EXP_REB_HEDGE_SIZE = 0.2669283957115514
EXP_REB_HEDGE_ENTRY = 2103.9731615220894
EXP_REB_HEDGE_EXIT = 2106.0168384779104
EXP_REB_HEDGE_PNL = 0.2647103208573288

# Aggregates
EXP_HEDGE_PNL_TOTAL = 0.2647103208573288  # no long-leg hedge + rebound hedge
EXP_PNL_FIELD = 88.34306500000002         # engine returns long coin pnl in target_rebound_short branch
EXP_TOTAL_PNL = 96.02532361667474         # long coin + short coin + rebound hedge
EXP_BARS_HELD = 6                         # max(total_bars over legs) = 11-5 = 6
# max_live_coin_notional tracks max live coin notional across legs in this path;
# rebound short entry notional exceeds long entry notional here.
EXP_MAX_LIVE_COIN_NOTIONAL = 1088.4533216349998  # short_entry * SHARES (engine-traced)


def test_rebound_short_final_exit_loop_else_aligned_eth_hedge_cap_cut_commission_min_entry_next_bar_traced():
    res = backtest_simple(COIN, _sig(), config=_cfg(RATE), eth_candles=ETH)

    assert res.exit_reason == "target_rebound_short"
    assert res.bars_held == EXP_BARS_HELD
    assert res.entry_timestamp == "2025-01-01T06:00:00"
    assert res.exit_timestamp == EXP_SHORT_EXIT_TS

    assert _close_to(res.entry_price, EXP_LONG_ENTRY)
    # With rebound short present, exit_price is the final short exit fill.
    assert _close_to(res.exit_price, EXP_SHORT_EXIT)
    assert _close_to(res.shares, SHARES)
    assert _close_to(res.max_live_coin_notional, EXP_MAX_LIVE_COIN_NOTIONAL)

    # No long-leg hedge in this fixture (insufficient/low relative vol path at entry);
    # rebound establishes an aligned long ETH hedge.
    assert res.hedge_side is None
    assert _close_to(res.hedge_size or 0.0, 0.0)
    assert res.rebound_hedge_side == EXP_REB_HEDGE_SIDE
    assert _close_to(res.rebound_hedge_size, EXP_REB_HEDGE_SIZE)
    assert _close_to(res.rebound_hedge_entry, EXP_REB_HEDGE_ENTRY)
    assert _close_to(res.rebound_hedge_exit, EXP_REB_HEDGE_EXIT)

    assert _close_to(res.pnl, EXP_PNL_FIELD)
    assert _close_to(res.hedge_pnl, EXP_HEDGE_PNL_TOTAL)
    assert _close_to(res.rebound_short_pnl, EXP_SHORT_COIN_PNL)
    assert _close_to(res.rebound_hedge_pnl, EXP_REB_HEDGE_PNL)
    assert _close_to(res.total_pnl, EXP_TOTAL_PNL)

    assert isinstance(res.trades, list) and len(res.trades) == 2
    long_leg, short_leg = res.trades
    assert long_leg["side"] == "long" and long_leg["reason"] == "target"
    assert _close_to(long_leg["entry"], EXP_LONG_ENTRY)
    assert _close_to(long_leg["exit"], EXP_LONG_EXIT)
    assert _close_to(long_leg["pnl"], EXP_LONG_COIN_PNL)

    assert short_leg["side"] == "short" and short_leg["reason"] == EXP_SHORT_REASON
    assert _close_to(short_leg["entry"], EXP_SHORT_ENTRY)
    assert _close_to(short_leg["exit"], EXP_SHORT_EXIT)
    assert _close_to(short_leg["pnl"], EXP_SHORT_COIN_PNL)


def test_rebound_short_final_exit_loop_else_risk_state_settlement_and_funding_parity():
    rs_on = DailyRiskState()
    on = backtest_simple(COIN, _sig(), config=_cfg(RATE), eth_candles=ETH, risk_state=rs_on)
    off = backtest_simple(COIN, _sig(), config=_cfg(0.0), eth_candles=ETH)

    assert on.exit_reason == "target_rebound_short"
    assert off.exit_reason == "target_rebound_short"
    assert _close_to(on.total_pnl, EXP_TOTAL_PNL)

    # Engine loop-else closes rebound short via risk_state with coin short_pnl only
    # (rebound hedge pnl not included in that apply_trade call) while total_pnl
    # includes rebound_hedge_pnl. This locks current settlement accounting behavior.
    assert rs_on.open_positions == 0
    assert _close_to(rs_on.gross_exposure, 0.0)
    assert rs_on.open_position_notionals == []
    expected_realized = EXP_LONG_COIN_PNL + EXP_SHORT_COIN_PNL
    assert _close_to(rs_on.realized_pnl, expected_realized)

    delta = (on.total_pnl or 0.0) - (off.total_pnl or 0.0)
    assert abs(delta) > 1e-9
    # Funding applies across all legs present: long coin, rebound short coin, rebound long ETH hedge.
    assert (on.rebound_hedge_size or 0.0) > 0.0
