"""Probe (2026-11-11): 3+ same-bar RSI candidates where max_positions < candidates.

Spec: admit deepest RSI crashes first, apply equal-share cuts across 120% cap
(old+new, cuts only). When max_positions < candidates, only the deepest subset
should be admitted (by RSI severity), and the admitted ones should be cut to
equal share of the cap.

This probe is scratch — it prints observed behavior so we can hand-trace
expected values and decide whether a defect exists.
"""
from __future__ import annotations

from scripts.run_portfolio import run_portfolio_simulation
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import _rsi


def _bar(i, o, c, v):
    hi = max(o, c) * 1.01
    lo = min(o, c) * 0.99
    return {
        "timestamp": f"2026-01-01T{i:02d}:00:00Z",
        "open": o,
        "high": hi,
        "low": lo,
        "close": c,
        "volume": v,
    }


def _make_rsi_series(step: float, volume: float, n: int = 60):
    candles = []
    p = 100.0
    for i in range(n):
        c = p * step
        candles.append(_bar(i, p, c, volume))
        p = c
    candles.append(_bar(n, p, p * 1.05, volume))
    return candles


def _cfg(**kw):
    d = dict(
        use_rsi_trigger=True,
        rsi_period=21,
        rsi_threshold=20.0,
        avoid_downtrend=True,
        regime_min_price=0.0,
        min_daily_volume_usd=0.0,
        enable_eth_hedge=False,
        enable_rebound_short=True,
        enable_volume_based_sizing=True,
        gross_cap_pct=120.0,
        max_positions=2,  # < 4 candidates
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
        entry_next_bar=False,
        target_pct=200.0,
        rebound_short_target_pct=9.0,
        rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=5,
        time_exit_max_bars=5,
    )
    d.update(kw)
    return StrategyConfig(**d)


def main():
    A = _make_rsi_series(0.97, 5_000_000)
    B = _make_rsi_series(0.98, 8_000_000)
    C = _make_rsi_series(0.985, 6_000_000)
    D = _make_rsi_series(0.99, 7_000_000)
    rsis = [_rsi(x, 21) for x in (A, B, C, D)]
    print("RSI:", dict(zip("ABCD", rsis)))
    print("sorted deepest-first:", sorted(zip(rsis, "ABCD")))

    cfg = _cfg()
    res = run_portfolio_simulation({"A": A, "B": B, "C": C, "D": D}, config=cfg, capital=100000.0)
    print("num_trades:", res["num_trades"])
    print("symbols:", [t["symbol"] for t in res["trades"]])
    cap = 100000.0 * 120.0 / 100.0
    print("cap:", cap, "equal_share(2):", cap / 2)
    for t in res["trades"]:
        notional = float(t["shares"]) * float(t["entry_price"])
        print(f"  {t['symbol']}: shares={t['shares']} entry_px={t['entry_price']} notional={notional} exit={t['exit_reason']}")
    print("final_open_positions:", res["final_open_positions"])
    print("final_gross_exposure:", res["final_gross_exposure"])


if __name__ == "__main__":
    main()