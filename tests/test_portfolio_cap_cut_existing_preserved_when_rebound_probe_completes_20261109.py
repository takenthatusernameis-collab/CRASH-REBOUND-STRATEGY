"""Regression (2026-11-09): when a same-bar/cross-bar admission triggers an
equal-share cap cut (old+new) and the admitted probe completes (e.g. rebound-short
time exit) so probe_state.open_position_notionals ends shorter than existing+1,
the portfolio reservation overlay must still propagate the engine's cap cuts to
existing open positions. Failing to do so leaves existing positions reserved at
their pre-cut notionals, inflating gross exposure and blocking/over-cutting future
admissions (violates equal-share cuts, "cuts only, never topped up" is preserved
but the cut itself is lost).

Failing-tests-first. Synthetic fixtures only (non-evidence). Hourly only.
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
        max_daily_loss_pct=100.0,  # isolate cap-cut reservation propagation
    )


def test_existing_cap_cut_persists_after_rebounding_admission_completes():
    """Capital 10000, cap 12000.
    X: enters bar 10, 80 shares @100 = 8000, stays open (no target/stop).
    Y: signals bar 25, 50 shares @100 = 5000. Hits +9% target on entry bar 26,
       opens rebound short at 109 -> max_live 5450. Cap pressure 8000+5450=13450>12000
       forces equal-share cut: X cut to 6000 (60 shares effective reservation context
       for portfolio), Y cut to 6000 max? Engine applies cuts to notionals; Y's
       executed shares/cut and max_live follow engine logic. Y completes via rebound
       time exit at bar ~74.
    Z: signals bar 80 (after Y exit). X should remain cut to 6000 (cuts never topped up).
       Z requests 55 shares @100 = 5500. Correct: 6000+5500=11500 <= 12000 => Z uncut.
       Buggy (X left at 8000): 8000+5500=13500 > 12000 => Z blocked or cap-cut.

    Concrete: Z must be admitted with 55 shares (uncut).
    """
    cfg = _cfg()
    candles_x = []
    for i in range(100):
        ts = f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z"
        if i == 9:
            candles_x.append(_c(ts, 100.0, 90.0, 100.0, 88.0))
        else:
            candles_x.append(_c(ts, 100.0, 100.0, 101.0, 99.0))
    candles_y = []
    for i in range(100):
        ts = f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z"
        if i == 25:
            candles_y.append(_c(ts, 100.0, 90.0, 100.0, 88.0))
        elif i == 26:
            candles_y.append(_c(ts, 100.0, 110.0, 111.0, 99.0))
        elif 27 <= i <= 74:
            candles_y.append(_c(ts, 108.0, 108.0, 108.5, 107.5))
        else:
            candles_y.append(_c(ts, 100.0, 100.0, 101.0, 99.0))
    candles_z = []
    for i in range(100):
        ts = f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z"
        if i == 80:
            candles_z.append(_c(ts, 100.0, 90.0, 100.0, 88.0))
        else:
            candles_z.append(_c(ts, 100.0, 100.0, 101.0, 99.0))

    sig_x = Signal(symbol="X", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                   target_price=130.0, risk_per_share=20.0, size_shares=80.0, signal_index=9, timestamp="")
    sig_y = Signal(symbol="Y", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                   target_price=109.0, risk_per_share=20.0, size_shares=50.0, signal_index=25, timestamp="")
    sig_z = Signal(symbol="Z", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                   target_price=130.0, risk_per_share=20.0, size_shares=55.0, signal_index=80, timestamp="")

    def fake(hist, symbol=None, config=None, capital=10000.0, cache=None):
        idx = len(hist) - 1
        if symbol == "X" and idx == 9:
            s = copy.copy(sig_x); s.signal_index = idx; return s
        if symbol == "Y" and idx == 25:
            s = copy.copy(sig_y); s.signal_index = idx; return s
        if symbol == "Z" and idx == 80:
            s = copy.copy(sig_z); s.signal_index = idx; return s
        return None

    with patch("scripts.run_portfolio.generate_signal", side_effect=fake):
        res = run_portfolio_simulation(
            {"X": candles_x, "Y": candles_y, "Z": candles_z},
            config=cfg, capital=10000.0,
        )

    by = {t["symbol"]: t for t in res["trades"]}
    assert "Y" in by, f"Y did not trade: {res['trades']}"
    assert by["Y"]["exit_reason"] in ("target_rebound_short", "rebound_time_exit", "rebound_target", "rebound_stop"), by["Y"]
    assert "Z" in by, (
        f"Z blocked after Y completed — portfolio failed to propagate X's cap cut from Y's "
        f"admission (reservation overlay left X at pre-cut notional). trades={res['trades']}"
    )
    assert abs(float(by["Z"]["shares"]) - 55.0) < 1e-9, (
        f"Z should be uncut (55 shares): X must stay cut to 6000 after Y's cap-cut admission "
        f"completed (cuts only, never topped up). Z.shares={by['Z']['shares']} trades={res['trades']}"
    )
