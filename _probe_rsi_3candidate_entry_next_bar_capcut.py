"""Probe (2026-11-11): RSI-trigger 3 same-bar candidates, entry_next_bar=True,
max_positions=3, 120% gross cap equal-share cuts, deepest-first admission.

Fills the gap between the locked 2-candidate/max_positions=1 RSI test and the
entry_next_bar=False 3-candidate probe: this exercises the RSI severity path
with next-bar-open execution AND cap pressure simultaneously.
"""
from __future__ import annotations

from scripts.run_portfolio import run_portfolio_simulation
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import _rsi


def _bar(i, o, c, v=10_000_000.0):
    hi = max(o, c) * 1.0001
    lo = min(o, c) * 0.9999
    return {
        "timestamp": f"2026-01-01T{i:02d}:00:00Z",
        "open": o, "high": hi, "low": lo, "close": c, "volume": v,
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
        use_rsi_trigger=True, rsi_period=21, rsi_threshold=20.0,
        avoid_downtrend=True, regime_min_price=0.0, min_daily_volume_usd=0.0,
        enable_eth_hedge=False, enable_rebound_short=False,
        enable_volume_based_sizing=False, gross_cap_pct=120.0, max_positions=3,
        risk_per_trade_pct=10.0, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=0.0, time_exit_max_bars=10,
    )
    d.update(kw)
    return StrategyConfig(**d)


capital = 100000.0
cap_value = capital * 120.0 / 100.0  # 120000

deep = _make_rsi_series(0.97)
mid = _make_rsi_series(0.985)
mild = _make_rsi_series(0.99)
# Append one extra bar so entry_next_bar can execute after the decision bar.
for series in (deep, mid, mild):
    last = series[-1]["close"]
    series.append(_bar(len(series), last * 1.01, last * 1.005))

rsi_by_sym = {"DEEP": _rsi(deep, 21), "MID": _rsi(mid, 21), "MILD": _rsi(mild, 21)}
print("RSI:", {k: round(v, 4) for k, v in rsi_by_sym.items()})
assert rsi_by_sym["DEEP"] < rsi_by_sym["MID"] < rsi_by_sym["MILD"] < 20.0

res = run_portfolio_simulation({"DEEP": deep, "MID": mid, "MILD": mild},
                               config=_cfg(entry_next_bar=True), capital=capital)

print(f"num_trades={res['num_trades']} final_open={res['final_open_positions']} "
      f"gross={res['final_gross_exposure']:.6f} total_pnl={res['total_pnl']:.6f}")
for t in res['trades']:
    notional = t['entry_price'] * t['shares']
    print(f"  {t['symbol']}: exit={t['exit_reason']} entry_ts={t['entry_timestamp']} "
          f"entry_px={t['entry_price']:.6f} shares={t['shares']:.6f} notional={notional:.4f} "
          f"pnl={t['total_pnl']:.6f}")

# Deepest-first admission order preserved
assert [t['symbol'] for t in res['trades']] == ['DEEP', 'MID', 'MILD'], [t['symbol'] for t in res['trades']]
assert res['num_trades'] == 3, res['num_trades']
# Equal-share cut: each notional <= cap/3 (cuts only, never topped up above desired)
equal_share = cap_value / 3.0
for t in res['trades']:
    notional = t['entry_price'] * t['shares']
    assert notional <= equal_share + 1e-6, (t['symbol'], notional, equal_share)
    assert notional > 0, t['symbol']
# entry_next_bar: entry executes at next bar open after decision bar (index 60 -> 61)
for t in res['trades']:
    assert t['entry_timestamp'] == deep[61]["timestamp"], (t['symbol'], t['entry_timestamp'])
    assert abs(float(t['entry_price']) - float(deep[61]["open"])) < 1e-12, t['symbol']
# Final reconciliation
assert res['final_open_positions'] == 0
assert abs(res['final_gross_exposure']) < 1e-9
print(f"\nEqual-share cut target per position: {equal_share:.4f}")
print("ALL PROBE ASSERTIONS PASSED")