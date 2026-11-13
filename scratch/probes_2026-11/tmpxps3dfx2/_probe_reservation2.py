"""Probe: trace reservation overlay values through rebound max_live scenarios."""
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


def _mk_x_open():
    candles = []
    for i in range(90):
        ts = f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z"
        if i == 20:
            candles.append(_c(ts, 100.0, 90.0, 100.0, 88.0))
        else:
            candles.append(_c(ts, 100.0, 100.0, 101.0, 99.0))
    return candles


def _mk_a_rebound():
    candles = []
    for i in range(90):
        ts = f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z"
        if i == 25:
            candles.append(_c(ts, 100.0, 90.0, 100.0, 88.0))
        elif i == 26:
            candles.append(_c(ts, 100.0, 110.0, 111.0, 99.0))
        elif 27 <= i <= 74:
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


def main():
    cfg = _cfg()
    sig_x = Signal(symbol="X", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                   target_price=150.0, risk_per_share=20.0, size_shares=100.0, signal_index=20, timestamp="")
    sig_a = Signal(symbol="A", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                   target_price=109.0, risk_per_share=20.0, size_shares=100.0, signal_index=25, timestamp="")
    sig_b = Signal(symbol="B", side="long", reason="t", entry_price=100.0, stop_price=90.0,
                   target_price=130.0, risk_per_share=10.0, size_shares=15.0, signal_index=25, timestamp="")
    sig_c = Signal(symbol="C", side="long", reason="t", entry_price=100.0, stop_price=90.0,
                   target_price=130.0, risk_per_share=10.0, size_shares=100.0, signal_index=30, timestamp="")

    def fake(hist, symbol=None, config=None, capital=10000.0, cache=None):
        idx = len(hist) - 1
        if symbol == "X" and idx == 20:
            s = copy.copy(sig_x); s.signal_index = idx; return s
        if symbol == "A" and idx == 25:
            s = copy.copy(sig_a); s.signal_index = idx; return s
        if symbol == "B" and idx == 25:
            s = copy.copy(sig_b); s.signal_index = idx; return s
        if symbol == "C" and idx == 30:
            s = copy.copy(sig_c); s.signal_index = idx; return s
        return None

    x_candles = _mk_x_open()
    a_candles = _mk_a_rebound()
    b_candles = list(a_candles)
    for i in range(26, 90):
        b_candles[i] = _c(f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z", 100.0, 100.0, 100.5, 99.5)
    c_candles = list(a_candles)
    for i in range(31, 90):
        c_candles[i] = _c(f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z", 100.0, 100.0, 100.5, 99.5)

    with patch("scripts.run_portfolio.generate_signal", side_effect=fake):
        res = run_portfolio_simulation(
            {"X": x_candles, "A": a_candles, "B": b_candles, "C": c_candles},
            config=cfg, capital=10000.0,
        )

    by = {t["symbol"]: t for t in res["trades"]}
    for s in ("X", "A", "B", "C"):
        t = by.get(s)
        if t:
            print(f"{s}: shares={t['shares']:.1f} exit={t['exit_reason']} entry_ts={t['entry_timestamp']} exit_ts={t['exit_timestamp']}")
        else:
            print(f"{s}: NOT ADMITTED")
    print("final_open_positions:", res["final_open_positions"])
    print("final_gross_exposure:", res["final_gross_exposure"])


if __name__ == "__main__":
    main()