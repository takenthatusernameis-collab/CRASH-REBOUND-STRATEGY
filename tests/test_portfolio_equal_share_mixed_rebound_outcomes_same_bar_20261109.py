"""Regression (2026-11-09): concurrent same-bar admissions with
enable_rebound_short=True, NO existing positions, and total desired exceeding the
120% gross cap MUST apply equal-share cuts old+new regardless of whether individual
candidates hit target on the entry bar.

Failing-tests-first: the batch-cut trigger previously required ALL candidates to
hit target on the entry bar (to address rebound-short probe-future-exit concerns).
That let mixed/no-target-hit cases fall through to sequential admission, giving
earlier candidates preferential uncapped fills — a spec violation (equal-share
cuts old+new).

Spec refs: 120% gross cap, equal-share cuts old+new; one position/coin;
strict no-look-ahead (decision-time admission). Synthetic fixtures (non-evidence).
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
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _make(signal_bar: int, *, hit_target_on_entry: bool):
    candles = []
    for i in range(100):
        ts = f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z"
        if i == signal_bar:
            candles.append(_c(ts, 100.0, 90.0, 100.0, 88.0))
        elif i == signal_bar + 1:
            if hit_target_on_entry:
                candles.append(_c(ts, 100.0, 110.0, 111.0, 99.0))
            else:
                candles.append(_c(ts, 100.0, 101.0, 102.0, 99.0))
        elif signal_bar + 2 <= i <= signal_bar + 49:
            candles.append(_c(ts, 108.0, 108.0, 108.5, 107.5))
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


def _mk(sym: str, idx: int = 25):
    return Signal(
        symbol=sym, side="long", reason="t", entry_price=100.0, stop_price=80.0,
        target_price=109.0, risk_per_share=20.0, size_shares=100.0,
        signal_index=idx, timestamp="",
    )


def test_equal_share_mixed_target_hit_rebound_short_enabled():
    """X completes via rebound short on entry bar; Y does not. Both same-bar, cap
    exceeded (2 * 10000 > 12000). Equal-share => 60 shares each (6000 notional)."""
    cfg = _cfg()
    cx = _make(25, hit_target_on_entry=True)
    cy = _make(25, hit_target_on_entry=False)

    def fake(hist, symbol=None, config=None, capital=10000.0, cache=None):
        if len(hist) - 1 == 25 and symbol in ("X", "Y"):
            return _mk(symbol)
        return None

    with patch("scripts.run_portfolio.generate_signal", side_effect=fake):
        res = run_portfolio_simulation({"X": cx, "Y": cy}, config=cfg, capital=10000.0)

    by = {t["symbol"]: t for t in res["trades"]}
    assert "X" in by and "Y" in by, res["trades"]
    assert abs(by["X"]["shares"] - 60.0) < 1e-6, (
        f"X (rebound-completing probe) must get equal-share cut: got {by['X']['shares']}"
    )
    assert abs(by["Y"]["shares"] - 60.0) < 1e-6, (
        f"Y (no entry-bar target) must get equal-share cut: got {by['Y']['shares']}"
    )
    assert res["final_open_positions"] == 0
    assert abs(float(res["final_gross_exposure"])) < 1e-9


def test_equal_share_both_no_target_hit_rebound_short_enabled():
    """Neither hits target on entry bar, but enable_rebound_short=True and same-bar
    concurrent admissions exceed cap. Equal-share cuts old+new still apply."""
    cfg = _cfg()
    cx = _make(25, hit_target_on_entry=False)
    cy = _make(25, hit_target_on_entry=False)

    def fake(hist, symbol=None, config=None, capital=10000.0, cache=None):
        if len(hist) - 1 == 25 and symbol in ("X", "Y"):
            return _mk(symbol)
        return None

    with patch("scripts.run_portfolio.generate_signal", side_effect=fake):
        res = run_portfolio_simulation({"X": cx, "Y": cy}, config=cfg, capital=10000.0)

    by = {t["symbol"]: t for t in res["trades"]}
    assert "X" in by and "Y" in by, res["trades"]
    assert abs(by["X"]["shares"] - 60.0) < 1e-6, f"X not equal-share: {by['X']['shares']}"
    assert abs(by["Y"]["shares"] - 60.0) < 1e-6, f"Y not equal-share: {by['Y']['shares']}"
