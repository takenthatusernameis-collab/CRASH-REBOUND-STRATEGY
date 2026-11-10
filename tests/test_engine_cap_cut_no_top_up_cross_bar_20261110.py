"""Regression lock (2026-11-10): ENGINE CAP-CUT TOP-UP VIOLATION.

src/backtest/engine.py:231 applies equal-share cuts to ALL positions when
total_exposure > cap, but top-ups the new position if its requested notional
< equal_share. Violates spec "cuts only, never topped up".

Scenario (capital=10000, cap=12000):
  X: enters bar 21, 100 shares @100 = 10000 notional, hits +9% target ->
     rebound short at 109 (max_live coin reservation 10900) live through
     time-exit window.
  Y: enters bar 26 under cap pressure (X rebound reservation 10900 + Y
     requested 10000 > 12000) -> equal-share cut to 60 shares (6000 notional).
     Y hits target -> rebound short max_live 6540.
  Z: enters bar 30 requesting ONLY 10 shares @100 = 1000 notional while X/Y
     rebound legs still live. equal_share = 12000/3 = 4000.
     EXPECTED: Z gets 10 shares (capped at requested 1000, no top-up).
     ACTUAL (defect): Z gets 40 shares (topped up to equal_share 4000).

Spec refs: 120% gross cap, equal-share cuts old+new, cuts only never topped up,
one position/coin, strict no-look-ahead. Synthetic fixtures (non-evidence).
Hourly only.
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
    return {"timestamp": ts, "open": o, "high": c, "low": l, "close": c, "volume": v}


def _flat(price, n=120, start=1):
    out = []
    for i in range(start, start + n):
        ts = f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z"
        out.append(_c(ts, price, price, price * 1.001, price * 0.999))
    return out


def _x_candles():
    """X: signal bar 21, crash then +9% target on entry-next bar -> rebound short
    at 109 (max_live coin reservation 109*100=10900) live to time exit."""
    out = _flat(100.0)
    out[20] = _c("2026-01-01T22:00:00Z", 100.0, 90.0, 100.0, 88.0)  # signal bar crash
    out[21] = _c("2026-01-01T23:00:00Z", 100.0, 110.0, 111.0, 99.0)  # +9% target hit
    for i in range(22, 120):
        out[i] = _c(f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z", 108.0, 108.0, 109.0, 107.0)
    return out


def _y_candles():
    """Y: signal bar 26, crash then +9% target -> rebound short max_live 6540."""
    out = _flat(100.0)
    out[25] = _c("2026-01-02T02:00:00Z", 100.0, 90.0, 100.0, 88.0)
    out[26] = _c("2026-01-02T03:00:00Z", 100.0, 110.0, 111.0, 99.0)
    for i in range(27, 120):
        out[i] = _c(f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z", 108.0, 108.0, 109.0, 107.0)
    return out


def _z_candles():
    """Z: signal bar 30, entry next bar open=100, flat after -> time exit."""
    out = _flat(100.0)
    out[29] = _c("2026-01-02T06:00:00Z", 100.0, 90.0, 100.0, 88.0)
    out[30] = _c("2026-01-02T07:00:00Z", 100.0, 100.0, 101.0, 99.0)
    return out


def _cfg():
    return StrategyConfig(
        use_rsi_trigger=False,
        enable_rebound_short=True,
        enable_eth_hedge=False,
        entry_next_bar=True,
        min_daily_volume_usd=1_000_000,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
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


SIGS = {
    "X": Signal(symbol="X", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                target_price=109.0, risk_per_share=20.0, size_shares=100.0,
                signal_index=21, timestamp=""),
    "Y": Signal(symbol="Y", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                target_price=109.0, risk_per_share=20.0, size_shares=100.0,
                signal_index=26, timestamp=""),
    "Z": Signal(symbol="Z", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                target_price=109.0, risk_per_share=20.0, size_shares=10.0,
                signal_index=30, timestamp=""),
}


def _fake(hist, symbol=None, config=None, capital=10000.0, cache=None):
    idx = len(hist) - 1
    if idx == 21 and symbol == "X":
        s = copy.copy(SIGS["X"]); s.signal_index = 21; return s
    if idx == 26 and symbol == "Y":
        s = copy.copy(SIGS["Y"]); s.signal_index = 26; return s
    if idx == 30 and symbol == "Z":
        s = copy.copy(SIGS["Z"]); s.signal_index = 30; return s
    return None


def test_engine_cap_cut_no_top_up_new_position():
    """Z requesting only 1000 notional must NOT be topped up to equal_share 4000.

    X rebound reservation 10900 + Y requested 10000 > cap 12000 -> cut pressure.
    Y cut to 6000. Z requests only 1000; equal_share=4000 but Z must be capped
    at requested 1000 (10 shares) — cuts only, never topped up.
    """
    with patch("scripts.run_portfolio.generate_signal", side_effect=_fake):
        res = run_portfolio_simulation(
            {"X": _x_candles(), "Y": _y_candles(), "Z": _z_candles()},
            config=_cfg(), capital=10000.0,
        )

    by = {t["symbol"]: t for t in res["trades"]}
    assert set(("X", "Y", "Z")).issubset(by), res["trades"]

    # X: 100 shares requested, but cut under pressure with Y. Check admitted.
    # Y: equal-share cut under pressure.
    # Z: requested 10 shares (1000 notional) — must NOT be topped up to 40 shares.
    z = by["Z"]
    assert abs(float(z["shares"]) - 10.0) < 1e-6, (
        f"Z top-up violation: Z requested 10 shares (1000 notional) but got "
        f"{z['shares']} shares ({float(z['shares']) * 100.0} notional). "
        f"Spec requires cuts only, never topped up to equal_share."
    )
    assert abs(float(z["shares"]) * 100.0 - 1000.0) < 1e-6, z
