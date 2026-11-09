"""Regression (2026-11-09): multiple concurrent cross-bar rebound shorts with
commission_min + cap-cut. Each rebound short's max_live_coin_notional must
reserve capacity while live. Later admissions must see the sum of all
max_live notionals.

Failing-tests-first. Synthetic fixtures only (non-evidence). Hourly only.

Scenario:
- Capital 10000, cap 12000.
- X: enters bar 20, hits target bar 21 -> rebound short at 109, time exit bar 70.
  max_live = 109 * shares. No cut initially (single position).
- Y: enters bar 25, hits target bar 26 -> rebound short at 109, time exit bar 75.
  X's rebound short still live. X(10900) + Y(10000) = 20900 > 12000 -> cut!
  Equal share: X cut to 6000, Y cut to 6000.
  Y's rebound short max_live = 109 * 60 = 6540.
- Z: enters bar 30, while X and Y rebound shorts both live.
  X reservation: 6000 (cut long-entry? No, X's long was cut at Y's entry, but X's rebound short is at 109 * original_shares?
  Wait: X entered uncut at 100 shares. When Y enters, X is cut to 60 shares (6000).
  But X's rebound short already opened at 100 shares (10900)!
  This is a problem: the cut happens at Y's entry (bar 25), but X's rebound short opened at bar 21 (before cut).
  The engine doesn't retroactively cut X's rebound short shares.

  So X's max_live stays at 10900 (100 shares * 109), but reservation for X is cut to 6000.
  Y enters cut to 60 shares, rebound short max_live = 6540.
  Reservation: X at 6000, Y at 6540 (max_live). Total = 12540.

  Z enters bar 30: sees X(6000) + Y(6540) = 12540 > 12000 -> Z cut.

  The key test: X's reservation is at CUT notional (6000) even though its rebound short
  max_live is 10900. The reservation uses the cut notional for existing positions,
  but max_live for the new admission's rebound short.

  This is the correct behavior: cuts apply to existing positions' reservations,
  but new admissions reserve at their max_live.
"""
from __future__ import annotations

import copy
from unittest.mock import patch

from scripts.run_portfolio import run_portfolio_simulation
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(ts, o, c, h=None, l=None, v=1_500_000.0):
    h = max(o, c) * 1.002 if h is None else h
    l = min(o, c) * 0.998 if l is None else l
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _make_x_candles():
    """X: signal bar 20, entry bar 21, hits target 109 bar 21, flat until bar 70."""
    candles = []
    for i in range(100):
        ts = f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z"
        if i == 20:
            candles.append(_c(ts, 100.0, 90.0, 100.0, 88.0))
        elif i == 21:
            candles.append(_c(ts, 100.0, 110.0, 111.0, 99.0))
        elif 22 <= i <= 70:
            candles.append(_c(ts, 108.0, 108.0, 108.5, 107.5))
        else:
            candles.append(_c(ts, 100.0, 100.0, 101.0, 99.0))
    return candles


def _make_y_candles():
    """Y: signal bar 25, entry bar 26, hits target 109 bar 26, flat until bar 75."""
    candles = []
    for i in range(100):
        ts = f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z"
        if i == 25:
            candles.append(_c(ts, 100.0, 90.0, 100.0, 88.0))
        elif i == 26:
            candles.append(_c(ts, 100.0, 110.0, 111.0, 99.0))
        elif 27 <= i <= 75:
            candles.append(_c(ts, 108.0, 108.0, 108.5, 107.5))
        else:
            candles.append(_c(ts, 100.0, 100.0, 101.0, 99.0))
    return candles


def _make_z_candles():
    """Z: signal bar 30, flat."""
    candles = []
    for i in range(100):
        ts = f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z"
        if i == 30:
            candles.append(_c(ts, 100.0, 90.0, 100.0, 88.0))
        else:
            candles.append(_c(ts, 100.0, 100.0, 101.0, 99.0))
    return candles


def _cfg():
    return StrategyConfig(
        use_rsi_trigger=False,
        enable_rebound_short=True,
        enable_eth_hedge=False,
        entry_next_bar=True,
        min_daily_volume_usd=1_000_000,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=50.0,
        funding_rate_pct_per_hour=0.0,
        avoid_downtrend=False,
        gross_cap_pct=120.0,
        max_positions=10,
        rebound_short_time_exit_bars=48,
        rebound_short_stop_pct=40.0,
        rebound_short_target_pct=9.0,
        time_exit_max_bars=200,
        max_daily_loss_pct=100.0,
    )


def test_multiple_cross_bar_rebound_shorts_max_live_reservation():
    """X enters bar 21 (100 shares, rebound short 10900 max_live).
    Y enters bar 26 (cut to 60 shares, rebound short 6540 max_live).
    Z enters bar 30 must see X(6000 cut) + Y(6540 max_live) = 12540 > 12000 -> cut.
    """
    cfg = _cfg()

    candles_x = _make_x_candles()
    candles_y = _make_y_candles()
    candles_z = _make_z_candles()

    # X: 100 shares @100 = 10000, target 109
    sig_x = Signal(symbol="X", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                   target_price=109.0, risk_per_share=20.0, size_shares=100.0, signal_index=20, timestamp="")
    # Y: 100 shares @100 = 10000, target 109
    sig_y = Signal(symbol="Y", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                   target_price=109.0, risk_per_share=20.0, size_shares=100.0, signal_index=25, timestamp="")
    # Z: 55 shares @100 = 5500
    sig_z = Signal(symbol="Z", side="long", reason="t", entry_price=100.0, stop_price=90.0,
                   target_price=130.0, risk_per_share=10.0, size_shares=55.0, signal_index=30, timestamp="")

    def fake(hist, symbol=None, config=None, capital=10000.0, cache=None):
        idx = len(hist) - 1
        if symbol == "X" and idx == 20:
            s = copy.copy(sig_x); s.signal_index = idx; return s
        if symbol == "Y" and idx == 25:
            s = copy.copy(sig_y); s.signal_index = idx; return s
        if symbol == "Z" and idx == 30:
            s = copy.copy(sig_z); s.signal_index = idx; return s
        return None

    with patch("scripts.run_portfolio.generate_signal", side_effect=fake):
        res = run_portfolio_simulation(
            {"X": candles_x, "Y": candles_y, "Z": candles_z},
            config=cfg, capital=10000.0,
        )

    by = {t["symbol"]: t for t in res["trades"]}

    assert "X" in by, f"X did not trade: {res['trades']}"
    assert "Y" in by, f"Y did not trade: {res['trades']}"
    assert "Z" in by, f"Z did not trade: {res['trades']}"

    # X: entered uncut at 100 shares (no prior positions), rebound short at 100 shares
    assert abs(float(by["X"]["shares"]) - 100.0) < 1e-9, f"X shares wrong: {by['X']['shares']}"

    # Y: cut at entry because X's reservation (10000) + Y(10000) > 12000
    # But wait: X's reservation at bar 25 is max_live_coin_notional = 10900!
    # So X(10900) + Y(10000) = 20900 > 12000 -> cut to 6000 each.
    # Y's shares cut to ~60.
    assert float(by["Y"]["shares"]) < 100.0, f"Y not cut at entry: {by['Y']['shares']}"
    # Y should be cut to ~60 shares (6000 notional at entry)
    # But Y's rebound short max_live = 109 * 60 = 6540
    assert abs(float(by["Y"]["shares"]) - 60.0) < 5.0, f"Y shares not ~60: {by['Y']['shares']}"

    # Z: enters bar 30, sees X reservation and Y reservation
    # X reservation: after Y's cut, X cut to 6000 (long-entry cut).
    # But X's rebound short is still live at 10900 max_live!
    # The reservation overlay should use CUT notional for existing positions (6000)
    # and max_live for new admission's rebound short (6540 for Y).
    # Total = 6000 + 6540 = 12540 > 12000 -> Z cut.
    # Equal share 12000/3 = 4000 each -> Z ~40 shares.
    assert float(by["Z"]["shares"]) < 55.0, (
        f"Z admitted uncut — reservation not reflecting Y's max_live. "
        f"Z.shares={by['Z']['shares']}"
    )
    assert abs(float(by["Z"]["shares"]) - 40.0) < 5.0, (
        f"Z shares not ~40: {by['Z']['shares']}"
    )

    # Verify exit reasons
    for sym in ("X", "Y"):
        assert by[sym]["exit_reason"] in ("target_rebound_short", "rebound_time_exit", "rebound_target", "rebound_stop")


if __name__ == "__main__":
    test_multiple_cross_bar_rebound_shorts_max_live_reservation()
    print("Test passed!")