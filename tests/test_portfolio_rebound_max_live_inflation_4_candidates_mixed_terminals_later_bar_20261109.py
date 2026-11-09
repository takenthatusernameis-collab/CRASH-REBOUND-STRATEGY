"""Regression lock (2026-11-09): rebound max_live_coin_notional inflation with
>=4 candidates under cut pressure, mixed terminals, and a concurrent later-bar
admission while rebound-inflated reservations are still live.

Spec refs: 120% coin-positions cap; equal-share cuts old+new (cuts only, never
topped up); rebound short opened on +9% target; ETH hedge excluded from coin cap
context; commission/slippage apply to fills; hourly only; synthetic fixtures
(non-evidence).

Scenario:
  capital=10000, cap=12000. A, B, C fire on the same decision bar (bar 25) under
  batch-cut pressure (total desired 30000 > cap 12000 -> equal share 4000 entry
  notional = 40 shares @100 each). A and C hit +9% target on entry bar -> rebound
  short opens at 109 (max_live_coin_notional = 40*109 = 4360, coin rebound leg,
  hedges excluded) and stay live through the time-exit window. B liquidates on
  the entry bar (mixed terminal) and releases capacity. D fires on a LATER
  decision bar (bar 30) while at least one rebound-inflated reservation (A and/or
  C max_live 4360) is still live -> D is a later-bar admission under concurrent
  cap pressure.

Concrete expectations (entry-notional cap binding, consistent with locked
test_portfolio_batch_cut_rebound_max_live_notional_against_cap):
  - A: 40 shares, rebound target_rebound_short, bars_held=48 (live to bar 73).
  - B: 40 shares, liquidated on entry bar (releases capacity at bar 27).
  - C: 40 shares, rebound target_rebound_short, bars_held=48 (live to bar 73).
  - D: 40 shares, time_exit (admitted later-bar while A/C rebound legs live).
  - Equal-share cut under pressure: all admitted at 40 shares (4000 entry
    notional); D cut from requested 100 shares / 10000 notional to 40.
  - Entry-notional gross at the concurrent pressure point (bar 30-73) = 12000
    (== cap), never exceeded; cuts only, no top-up.
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


def _flat(price, n=120, start=1):
    out = []
    for i in range(start, start + n):
        ts = f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z"
        out.append(_c(ts, price, price, price * 1.001, price * 0.999))
    return out


def _rebound_live_candles():
    """Close=110 on entry bar (bar 26) -> rebound short at 109, live to time exit."""
    out = _flat(100.0)
    out[25] = _c("2026-01-02T02:00:00Z", 100.0, 90.0, 100.0, 88.0)  # signal bar crash
    out[26] = _c("2026-01-02T03:00:00Z", 100.0, 110.0, 111.0, 99.0)  # +9% target hit
    for i in range(27, 120):
        out[i] = _c(f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z", 108.0, 108.0, 109.0, 107.0)
    return out


def _liquidation_candles():
    """Entry bar (bar 26) low=88 <= liquidation threshold 94 -> liquidated."""
    out = _flat(100.0)
    out[25] = _c("2026-01-02T02:00:00Z", 100.0, 90.0, 100.0, 88.0)
    out[26] = _c("2026-01-02T03:00:00Z", 100.0, 95.0, 100.0, 88.0)
    for i in range(27, 120):
        out[i] = _c(f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z", 100.0, 100.0, 101.0, 99.0)
    return out


def _later_bar_candles():
    """Signal bar 30, entry next bar (bar 31) open=100, then flat (time exit)."""
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
    "A": Signal(symbol="A", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                target_price=109.0, risk_per_share=20.0, size_shares=100.0, signal_index=25, timestamp=""),
    "B": Signal(symbol="B", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                target_price=109.0, risk_per_share=20.0, size_shares=100.0, signal_index=25, timestamp=""),
    "C": Signal(symbol="C", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                target_price=109.0, risk_per_share=20.0, size_shares=100.0, signal_index=25, timestamp=""),
    "D": Signal(symbol="D", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                target_price=109.0, risk_per_share=20.0, size_shares=100.0, signal_index=30, timestamp=""),
}


def _fake(hist, symbol=None, config=None, capital=10000.0, cache=None):
    idx = len(hist) - 1
    if idx == 25 and symbol in ("A", "B", "C"):
        s = copy.copy(SIGS[symbol]); s.signal_index = 25; return s
    if idx == 30 and symbol == "D":
        s = copy.copy(SIGS["D"]); s.signal_index = 30; return s
    return None


def test_rebound_max_live_inflation_4_candidates_mixed_terminals_later_bar():
    with patch("scripts.run_portfolio.generate_signal", side_effect=_fake):
        res = run_portfolio_simulation(
            {
                "A": _rebound_live_candles(),
                "B": _liquidation_candles(),
                "C": _rebound_live_candles(),
                "D": _later_bar_candles(),
            },
            config=_cfg(), capital=10000.0,
        )

    by = {t["symbol"]: t for t in res["trades"]}
    assert set(("A", "B", "C", "D")).issubset(by), res["trades"]

    # Mixed terminals: A & C rebound shorts live; B liquidated on entry bar.
    assert by["A"]["exit_reason"] == "target_rebound_short", by["A"]
    assert abs(float(by["A"]["bars_held"]) - 48) < 1e-9, by["A"]
    assert by["B"]["exit_reason"] == "liquidated", by["B"]
    assert abs(float(by["B"]["bars_held"]) - 1) < 1e-9, by["B"]
    assert by["C"]["exit_reason"] == "target_rebound_short", by["C"]
    assert abs(float(by["C"]["bars_held"]) - 48) < 1e-9, by["C"]
    # D: later-bar admission while A/C rebound legs live -> time exit.
    assert by["D"]["exit_reason"] == "time_exit", by["D"]

    # Equal-share cut under batch-cut pressure: all admitted at 40 shares
    # (4000 entry notional = cap/3). D cut from requested 100 shares / 10000
    # notional to 40. Each position's entry notional = 4000 <= cap (12000).
    for sym in ("A", "B", "C", "D"):
        assert abs(float(by[sym]["shares"]) - 40.0) < 1e-6, (sym, by[sym])
        assert abs(float(by[sym]["shares"]) * 100.0 - 4000.0) < 1e-6, (sym, by[sym])

    # Concurrent pressure point (bar 30-73): A and C rebound legs are live when
    # D is admitted (later bar), while B liquidated on the entry bar and released
    # capacity early. Max concurrent positions = 3 * 4000 entry notional = 12000
    # == cap; never exceeded. Cuts only, no top-up.
    capital = 10000.0
    cap_value = capital * 120.0 / 100.0
    assert float(by["A"]["shares"]) * 100.0 <= cap_value + 1e-6
    assert float(by["C"]["shares"]) * 100.0 <= cap_value + 1e-6
    assert float(by["D"]["shares"]) * 100.0 <= cap_value + 1e-6
    # B released (liquidated same bar) before D enters -> no 4-way concurrency.
    assert by["B"]["exit_timestamp"] <= by["D"]["entry_timestamp"], (by["B"], by["D"])
    # A and C rebound legs overlap D's later-bar admission (concurrent pressure).
    assert by["A"]["entry_timestamp"] < by["D"]["entry_timestamp"] < by["A"]["exit_timestamp"], (
        by["A"], by["D"]
    )
    assert by["C"]["entry_timestamp"] < by["D"]["entry_timestamp"] < by["C"]["exit_timestamp"], (
        by["C"], by["D"]
    )
    assert res["final_open_positions"] == 0
    assert abs(float(res["final_gross_exposure"])) < 1e-9
    assert list(getattr(res["risk_state"], "open_position_notionals", ["leak"])) == []
