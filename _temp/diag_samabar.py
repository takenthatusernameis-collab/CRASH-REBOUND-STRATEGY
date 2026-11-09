"""Diagnostic: same-bar multi-admission (X existing + A + B) to check whether
_bar_notionals is refreshed between candidates so later probes see prior admissions."""
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
        use_rsi_trigger=False, enable_rebound_short=True, enable_eth_hedge=False,
        entry_next_bar=True, min_daily_volume_usd=1_000_000, slippage_pct=0.0,
        commission_per_share=0.0, commission_min=0.0, funding_rate_pct_per_hour=0.0,
        avoid_downtrend=False, gross_cap_pct=120.0, max_positions=10,
        rebound_short_time_exit_bars=48, rebound_short_stop_pct=40.0,
        rebound_short_target_pct=9.0, time_exit_max_bars=10, max_daily_loss_pct=100.0,
    )


def mk_x_open():
    cs = []
    for i in range(90):
        ts = f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z"
        if i == 20:
            cs.append(_c(ts, 100.0, 90.0, 100.0, 88.0))
        else:
            cs.append(_c(ts, 100.0, 100.0, 101.0, 99.0))
    return cs


def mk_a():
    cs = []
    for i in range(90):
        ts = f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z"
        if i == 25:
            cs.append(_c(ts, 100.0, 90.0, 100.0, 88.0))
        elif i == 26:
            cs.append(_c(ts, 100.0, 110.0, 111.0, 99.0))
        elif 27 <= i <= 74:
            cs.append(_c(ts, 108.0, 108.0, 108.5, 107.5))
        else:
            cs.append(_c(ts, 100.0, 100.0, 101.0, 99.0))
    return cs


def mk_b():
    cs = []
    for i in range(90):
        ts = f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z"
        if i == 25:
            cs.append(_c(ts, 100.0, 90.0, 100.0, 88.0))
        else:
            cs.append(_c(ts, 100.0, 100.0, 101.0, 99.0))
    return cs


def main():
    cfg = _cfg()
    sig_x = Signal(symbol="X", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                   target_price=150.0, risk_per_share=20.0, size_shares=100.0, signal_index=20, timestamp="")
    sig_a = Signal(symbol="A", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                   target_price=109.0, risk_per_share=20.0, size_shares=100.0, signal_index=25, timestamp="")
    sig_b = Signal(symbol="B", side="long", reason="t", entry_price=100.0, stop_price=90.0,
                   target_price=130.0, risk_per_share=10.0, size_shares=15.0, signal_index=25, timestamp="")

    def fake(hist, symbol=None, config=None, capital=10000.0, cache=None):
        idx = len(hist) - 1
        if symbol == "X" and idx == 20:
            s = copy.copy(sig_x); s.signal_index = idx; return s
        if symbol == "A" and idx == 25:
            s = copy.copy(sig_a); s.signal_index = idx; return s
        if symbol == "B" and idx == 25:
            s = copy.copy(sig_b); s.signal_index = idx; return s
        return None

    with patch("scripts.run_portfolio.generate_signal", side_effect=fake):
        res = run_portfolio_simulation(
            {"X": mk_x_open(), "A": mk_a(), "B": mk_b()},
            config=cfg, capital=10000.0,
        )

    by = {t["symbol"]: t for t in res["trades"]}
    print("trades:", res["trades"])
    for s in ("X", "A", "B"):
        if s in by:
            print(f"{s}: shares={by[s]['shares']}, exit={by[s]['exit_reason']}")
    print("final_open_positions:", res["final_open_positions"])
    print("final_gross_exposure:", res["final_gross_exposure"])


if __name__ == "__main__":
    main()