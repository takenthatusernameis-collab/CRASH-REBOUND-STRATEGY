"""Probe (2026-11-11): RSI-trigger admission when existing open positions + new
same-bar RSI candidates exceed 120% gross cap. Verify cut propagation old+new,
no top-up, deepest-first ordering, and no-look-ahead."""
from __future__ import annotations

from scripts.run_portfolio import run_portfolio_simulation
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import _rsi


def _bar(i, o, c, v):
    hi = max(o, c) * 1.01
    lo = min(o, c) * 0.99
    return {
        "timestamp": f"2026-01-01T{i:02d}:00:00Z",
        "open": o, "high": hi, "low": lo, "close": c, "volume": v,
    }


def _make_rsi_series(step, volume, n=60):
    candles = []
    p = 100.0
    for i in range(n):
        c = p * step
        candles.append(_bar(i, p, c, volume))
        p = c
    candles.append(_bar(n, p, p * 1.05, volume))  # rebound confirmation decision bar
    return candles


def _cfg(**kw):
    d = dict(
        use_rsi_trigger=True, rsi_period=21, rsi_threshold=20.0,
        avoid_downtrend=True, regime_min_price=0.0, min_daily_volume_usd=0.0,
        enable_eth_hedge=False, enable_rebound_short=True,
        enable_volume_based_sizing=True, gross_cap_pct=120.0,
        max_positions=4, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=0.0, entry_next_bar=False,
        target_pct=200.0, rebound_short_target_pct=9.0,
        rebound_short_stop_pct=40.0, rebound_short_time_exit_bars=200,
        time_exit_max_bars=200,
    )
    d.update(kw)
    return StrategyConfig(**d)


# A,B fire at bar 60 (decision). Then C,D fire at a later bar while A,B still open.
def _series_with_signal_at(step, volume, signal_bar, n=120):
    candles = _make_rsi_series(step, volume)
    # pad to n bars, inserting a second signal at signal_bar
    while len(candles) < n:
        last = candles[-1]["close"]
        candles.append(_bar(len(candles), last, last * 0.999, volume))
    # rebuild a fresh RSI-trigger series ending at signal_bar
    candles = []
    p = 100.0
    for i in range(signal_bar):
        c = p * step
        candles.append(_bar(i, p, c, volume))
        p = c
    candles.append(_bar(signal_bar, p, p * 1.05, volume))
    while len(candles) < n:
        last = candles[-1]["close"]
        candles.append(_bar(len(candles), last, last * 0.999, volume))
    return candles


A = _series_with_signal_at(0.97, 5_000_000, signal_bar=60)
B = _series_with_signal_at(0.98, 8_000_000, signal_bar=60)
C = _series_with_signal_at(0.985, 6_000_000, signal_bar=65)
D = _series_with_signal_at(0.99, 7_000_000, signal_bar=65)

rsis_60 = [_rsi(A[:61], 21), _rsi(B[:61], 21)]
rsis_65 = [_rsi(C[:66], 21), _rsi(D[:66], 21)]
print("rsis@60:", rsis_60, "rsis@65:", rsis_65)

cfg = _cfg()
res = run_portfolio_simulation({"A": A, "B": B, "C": C, "D": D}, config=cfg, capital=100000.0)
print("num_trades:", res["num_trades"])
for t in res["trades"]:
    notional = float(t["shares"]) * float(t["entry_price"])
    print(f"  {t['symbol']}: shares={t['shares']} entry={t['entry_price']:.4f} notional={notional:.4f} exit={t['exit_reason']} entry_ts={t['entry_timestamp']}")
print("final_open:", res["final_open_positions"], "gross:", res["final_gross_exposure"])