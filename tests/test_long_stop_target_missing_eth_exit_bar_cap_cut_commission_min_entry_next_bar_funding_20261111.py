"""Regression lock (2026-11-11): long in-loop STOP and TARGET exits where
liquidation is NOT breached, aligned ETH hedge established at entry, but the ETH
bar is missing/unavailable at the exit index (fallback hedge-exit accounting to
hedge entry raw) under equal-share cap-cut shares (signal.size_shares) ×
commission_min × entry_next_bar × nonzero hourly funding.

Uncovered cell vs existing locks:
- `tests/test_funding_every_leg_missing_eth_audit_20261107.py` covers
  stop/target with missing ETH exit but no entry_next_bar, no commission_min,
  no cap-cut shares, different sizing/fixture.
- `tests/test_long_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_20261110.py`
  covers loop-else FINAL EXIT (aligned hedge, missing final ETH bar).
- `tests/test_long_liquidation_no_usable_eth_hedge_*` covers liquidation path
  with no usable hedge (different lifecycle and hedge state).
- `tests/test_portfolio_spec_eth_hedge_fail_closed_20261110.py` /
  engine `require_eth_hedge` is spec-compliant fail-closed for unusable hedge
  at establishment, not in-loop stop/target exits where hedge was established
  and only exit-bar data is missing.

Spec: hourly funding on every leg/exit (coin long, ETH hedge short); hedge entry
sized on eth_candles[:start_idx+1] and aligned to start_idx; missing aligned ETH
exit bar must fall back to hedge entry for exit-price accounting while still
applying hedge funding; 120% cap cuts old+new equally (shares pre-cut,
reservation/entry-notional cap semantics); commission_min per share; entry at
next bar open; liquidation checked before stop/target and must not fire here.

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


def _eth_base():
    return [
        _c("2025-01-01T00:00:00", 2000, 2060, 1940, 2000),
        _c("2025-01-01T01:00:00", 2040, 2100, 1980, 2040),
        _c("2025-01-01T02:00:00", 1960, 2020, 1900, 1960),
        _c("2025-01-01T03:00:00", 2000, 2060, 1940, 2000),
        _c("2025-01-01T04:00:00", 2040, 2100, 1980, 2040),
        _c("2025-01-01T05:00:00", 2000, 2060, 1940, 2000),  # aligned to start_idx=5
        {"timestamp": "2025-01-01T06:00:00"},               # missing exit bar (idx 6)
        _c("2025-01-01T07:00:00", 1980, 2040, 1920, 1980),
    ]


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
        enable_liquidation_checks=False,  # prove stop/target path, liq not breached
    )


def _trace_common(coin, sig, cfg, exit_raw, exit_reason):
    entry_raw = coin[sig.signal_index + 1]["open"]
    comm_ps = max(0.0, COMM_MIN / SHARES)
    entry_px = entry_raw + entry_raw * SLIP + comm_ps
    # spec safety stop/target re-anchored to executed entry when entry_next_bar
    ratio = entry_px / sig.entry_price
    stop_px = sig.stop_price * ratio
    target_px = sig.target_price * ratio
    # stop/target exits fill at threshold raw; caller passes executed threshold raw
    exit_px = exit_raw - exit_raw * SLIP - comm_ps
    bars_held = 2  # idx 6 - start_idx 5 + 1
    coin_gross = (exit_px - entry_px) * SHARES
    coin_notional = entry_px * SHARES
    funding_long = _apply_funding_pnl(coin_notional, bars_held, RATE, "long")
    coin_pnl = coin_gross - funding_long

    start_idx = sig.signal_index + 1
    hedge_value = compute_eth_hedge_size(coin[: start_idx + 1], _eth_base()[: start_idx + 1], coin_notional, cfg)
    eth_entry_raw = 2000.0
    hedge_shares = hedge_value / eth_entry_raw
    hedge_comm_ps = max(0.0, COMM_MIN / hedge_shares)
    hedge_entry_px = eth_entry_raw - eth_entry_raw * SLIP - hedge_comm_ps
    # ETH bar missing at exit idx 6 -> engine falls back to hedge_info['entry']
    # (stored executed hedge entry) as eth_exit_price, then buy-side close.
    hedge_exit_raw = hedge_entry_px
    hedge_exit_px = hedge_exit_raw + hedge_exit_raw * SLIP + hedge_comm_ps
    hedge_gross = (hedge_entry_px - hedge_exit_px) * hedge_shares
    hedge_notional = hedge_entry_px * hedge_shares
    hedge_funding_component = _apply_funding_pnl(hedge_notional, bars_held, RATE, "short")
    hedge_pnl = hedge_gross - hedge_funding_component
    return {
        "entry_px": entry_px,
        "stop_px": stop_px,
        "target_px": target_px,
        "exit_px": exit_px,
        "bars_held": bars_held,
        "coin_pnl": coin_pnl,
        "hedge_shares": hedge_shares,
        "hedge_entry_px": hedge_entry_px,
        "hedge_exit_px": hedge_exit_px,
        "hedge_pnl": hedge_pnl,
        "total_pnl": coin_pnl + hedge_pnl,
        "max_live": coin_notional,
        "funding_long": funding_long,
        "hedge_funding_component": hedge_funding_component,
        "exit_reason": exit_reason,
    }


def test_long_stopped_missing_eth_exit_bar_cap_cut_commission_min_entry_next_bar_traced():
    # Signal at 4, entry next bar 5 open=101. Bar 6 low breaches stop (95 re-anchored)
    # but is far above liquidation threshold (~94% of entry) so liquidation must not fire.
    coin = [
        _c("2025-01-01T00:00:00", 100, 103, 97, 100),
        _c("2025-01-01T01:00:00", 102, 105, 99, 102),
        _c("2025-01-01T02:00:00", 98, 101, 95, 98),
        _c("2025-01-01T03:00:00", 100, 103, 97, 100),
        _c("2025-01-01T04:00:00", 102, 105, 99, 102),  # signal bar idx 4
        _c("2025-01-01T05:00:00", 101, 104, 99, 100),  # entry bar idx 5
        _c("2025-01-01T06:00:00", 99, 100, 90, 92),    # stop hit idx 6, ETH missing
        _c("2025-01-01T07:00:00", 92, 95, 90, 93),
    ]
    sig = Signal(
        symbol="T", side="long", reason="t",
        entry_price=102.0, stop_price=95.0, target_price=120.0,
        risk_per_share=1.0, timestamp="2025-01-01T04:00:00",
        size_shares=SHARES, signal_index=4,
    )
    cfg = _cfg(RATE)
    eth = _eth_base()
    exp = _trace_common(coin, sig, cfg, exp_exit_raw := (95.0 * ((101.0 + 101.0 * SLIP + max(0.0, COMM_MIN / SHARES)) / 102.0)), "stopped")

    rs_on = DailyRiskState()
    on = backtest_simple(coin, sig, config=cfg, eth_candles=eth, risk_state=rs_on)
    off = backtest_simple(coin, sig, config=_cfg(0.0), eth_candles=eth)

    assert on.exit_reason == exp["exit_reason"] == "stopped"
    assert off.exit_reason == "stopped"
    assert on.bars_held == exp["bars_held"] == 2
    assert on.entry_timestamp == "2025-01-01T05:00:00"
    assert on.exit_timestamp == "2025-01-01T06:00:00"

    assert _close_to(on.entry_price, exp["entry_px"])
    assert _close_to(on.exit_price, exp["exit_px"])
    assert _close_to(on.shares, SHARES)
    assert _close_to(on.max_live_coin_notional, exp["max_live"])

    assert (on.hedge_size or 0.0) > 0.0
    assert _close_to(on.hedge_size, exp["hedge_shares"])
    assert _close_to(on.hedge_entry, exp["hedge_entry_px"])
    assert _close_to(on.hedge_exit, exp["hedge_exit_px"])
    assert on.hedge_side == "short"

    assert _close_to(on.pnl, exp["coin_pnl"])
    assert _close_to(on.hedge_pnl, exp["hedge_pnl"])
    assert _close_to(on.total_pnl, exp["total_pnl"])
    assert abs(exp["funding_long"]) > 1e-12
    assert abs(exp["hedge_funding_component"]) > 1e-12

    assert isinstance(on.trades, list) and len(on.trades) == 1
    leg = on.trades[0]
    assert leg["side"] == "long"
    assert leg["reason"] == "stopped"
    assert _close_to(leg["entry"], exp["entry_px"])
    assert _close_to(leg["exit"], exp["exit_px"])
    assert _close_to(leg["pnl"], exp["coin_pnl"])

    # Engine settlement parity on stop path: risk_state records total_pnl (coin +
    # hedge) close pnl on this path per CELL 14 (engine.py:402); TradeResult/leg
    # attribution expose the same totals separately; occupancy/notional released.
    assert rs_on.open_positions == 0
    assert _close_to(rs_on.gross_exposure, 0.0)
    assert rs_on.open_position_notionals == []
    assert _close_to(rs_on.realized_pnl, exp["total_pnl"])

    # Funding parity: stop path with missing ETH exit bar.
    delta = on.total_pnl - off.total_pnl
    expected_funding_effect = exp["funding_long"] + exp["hedge_funding_component"]
    assert _close_to(delta, -expected_funding_effect)
    assert abs(delta) > 1e-12


def test_long_target_no_rebound_missing_eth_exit_bar_cap_cut_commission_min_entry_next_bar_traced():
    # Target hit on bar 6 (high reaches re-anchored target), liquidation not breached
    # (low stays high), rebound short disabled. ETH bar at exit idx missing.
    coin = [
        _c("2025-01-01T00:00:00", 100, 103, 97, 100),
        _c("2025-01-01T01:00:00", 102, 105, 99, 102),
        _c("2025-01-01T02:00:00", 98, 101, 95, 98),
        _c("2025-01-01T03:00:00", 100, 103, 97, 100),
        _c("2025-01-01T04:00:00", 102, 105, 99, 102),  # signal bar idx 4
        _c("2025-01-01T05:00:00", 101, 104, 99, 100),  # entry bar idx 5
        _c("2025-01-01T06:00:00", 102, 120, 101, 115), # target hit idx 6, ETH missing
        _c("2025-01-01T07:00:00", 115, 116, 110, 112),
    ]
    sig = Signal(
        symbol="T", side="long", reason="t",
        entry_price=102.0, stop_price=80.0, target_price=110.0,
        risk_per_share=1.0, timestamp="2025-01-01T04:00:00",
        size_shares=SHARES, signal_index=4,
    )
    cfg = _cfg(RATE)
    eth = _eth_base()
    entry_px_for_target = 101.0 + 101.0 * SLIP + max(0.0, COMM_MIN / SHARES)
    target_raw = 110.0 * (entry_px_for_target / 102.0)
    exp = _trace_common(coin, sig, cfg, target_raw, "target")

    rs_on = DailyRiskState()
    on = backtest_simple(coin, sig, config=cfg, eth_candles=eth, risk_state=rs_on)
    off = backtest_simple(coin, sig, config=_cfg(0.0), eth_candles=eth)

    assert on.exit_reason == exp["exit_reason"] == "target"
    assert off.exit_reason == "target"
    assert on.bars_held == exp["bars_held"] == 2
    assert on.entry_timestamp == "2025-01-01T05:00:00"
    assert on.exit_timestamp == "2025-01-01T06:00:00"

    assert _close_to(on.entry_price, exp["entry_px"])
    assert _close_to(on.exit_price, exp["exit_px"])
    assert _close_to(on.shares, SHARES)
    assert _close_to(on.max_live_coin_notional, exp["max_live"])

    assert (on.hedge_size or 0.0) > 0.0
    assert _close_to(on.hedge_size, exp["hedge_shares"])
    assert _close_to(on.hedge_entry, exp["hedge_entry_px"])
    assert _close_to(on.hedge_exit, exp["hedge_exit_px"])
    assert on.hedge_side == "short"

    assert _close_to(on.pnl, exp["coin_pnl"])
    assert _close_to(on.hedge_pnl, exp["hedge_pnl"])
    assert _close_to(on.total_pnl, exp["total_pnl"])
    assert abs(exp["funding_long"]) > 1e-12
    assert abs(exp["hedge_funding_component"]) > 1e-12

    assert isinstance(on.trades, list) and len(on.trades) == 1
    leg = on.trades[0]
    assert leg["side"] == "long"
    assert leg["reason"] == "target"
    assert _close_to(leg["entry"], exp["entry_px"])
    assert _close_to(leg["exit"], exp["exit_px"])
    assert _close_to(leg["pnl"], exp["coin_pnl"])

    # No rebound short opened.
    assert (on.rebound_short_pnl or 0.0) == 0.0
    assert not any(t.get("side") == "short" for t in (on.trades or []))

    assert rs_on.open_positions == 0
    assert _close_to(rs_on.gross_exposure, 0.0)
    assert rs_on.open_position_notionals == []
    assert _close_to(rs_on.realized_pnl, exp["total_pnl"])

    delta = on.total_pnl - off.total_pnl
    expected_funding_effect = exp["funding_long"] + exp["hedge_funding_component"]
    assert _close_to(delta, -expected_funding_effect)
    assert abs(delta) > 1e-12
