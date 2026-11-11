"""Probe (2026-11-11): 3+ same-bar RSI-trigger candidates, max_positions/cap, equal-share.

Deterministic synthetic fixtures only; not market evidence.
"""
from __future__ import annotations

from scripts.run_portfolio import run_portfolio_simulation
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import _rsi


def _bar(i, o, c, v=10_000_000.0):
    hi = max(o, c) * 1.001
    lo = min(o, c) * 0.999
    return {
        "timestamp": f"2026-01-01T{i:02d}:00:00Z",
        "open": o,
        "high": hi,
        "low": lo,
        "close": c,
        "volume": v,
    }


def _make_rsi_series(step: float, n: int = 60):
    candles = []
    p = 100.0
    for i in range(n):
        c = p * step
        candles.append(_bar(i, p, c))
        p = c
    candles.append(_bar(n, p, p * 1.05))  # rebound confirmation at decision bar
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
        enable_rebound_short=False,
        enable_volume_based_sizing=False,
        gross_cap_pct=120.0,
        max_positions=1,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
        time_exit_max_bars=10,
    )
    d.update(kw)
    return StrategyConfig(**d)


def _report(label, res, rsi_by_sym):
    print(f"\n=== {label} ===")
    print(f"  num_trades={res['num_trades']} final_open={res['final_open_positions']} "
          f"gross={res['final_gross_exposure']:.4f} total_pnl={res['total_pnl']:.6f}")
    for t in res['trades']:
        print(f"    {t['symbol']}: exit={t['exit_reason']} entry_ts={t['entry_timestamp']} "
              f"entry_px={t['entry_price']:.6f} shares={t['shares']:.6f} pnl={t['total_pnl']:.6f}")
    print(f"  RSI: " + ", ".join(f"{k}={v:.4f}" for k, v in rsi_by_sym.items()))


deep = _make_rsi_series(0.97)
mid = _make_rsi_series(0.985)
mild = _make_rsi_series(0.99)
rsi_by_sym = {
    "DEEP": _rsi(deep, 21),
    "MID": _rsi(mid, 21),
    "MILD": _rsi(mild, 21),
}
print("RSI values:", {k: round(v, 4) for k, v in rsi_by_sym.items()})
assert all(v is not None and v < 20.0 for v in rsi_by_sym.values())
assert rsi_by_sym["DEEP"] < rsi_by_sym["MID"] < rsi_by_sym["MILD"]

# Case A: max_positions=1 -> only DEEP admitted
res = run_portfolio_simulation({"DEEP": deep, "MID": mid, "MILD": mild},
                               config=_cfg(entry_next_bar=False), capital=100000.0)
_report("A: 3 candidates, max_positions=1, entry_next_bar=False", res, rsi_by_sym)
assert res['num_trades'] == 1, res['num_trades']
assert res['trades'][0]['symbol'] == 'DEEP'

# Case B: max_positions=2 -> DEEP + MID admitted
res = run_portfolio_simulation({"DEEP": deep, "MID": mid, "MILD": mild},
                               config=_cfg(max_positions=2, entry_next_bar=False), capital=100000.0)
_report("B: 3 candidates, max_positions=2, entry_next_bar=False", res, rsi_by_sym)
assert res['num_trades'] == 2, res['num_trades']
assert res['trades'][0]['symbol'] == 'DEEP'
assert res['trades'][1]['symbol'] == 'MID'

# Case C: max_positions=3 -> all three admitted
res = run_portfolio_simulation({"DEEP": deep, "MID": mid, "MILD": mild},
                               config=_cfg(max_positions=3, entry_next_bar=False), capital=100000.0)
_report("C: 3 candidates, max_positions=3, entry_next_bar=False", res, rsi_by_sym)
assert res['num_trades'] == 3, res['num_trades']
assert [t['symbol'] for t in res['trades']] == ['DEEP', 'MID', 'MILD']

print("\nALL PROBE ASSERTIONS PASSED")