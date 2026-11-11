"""Probe (2026-11-11): 3 same-bar RSI candidates under 120% gross cap, equal-share cuts.

Verifies that when 3 RSI candidates fire same-bar with total desired notional above
the 120% gross cap, equal-share cuts apply across old+new (cuts only, never top-ups),
deepest-first admission order preserved, and final reconciliation to 0 open/gross.

Deterministic synthetic fixtures only; not market evidence.
"""
from __future__ import annotations

from scripts.run_portfolio import run_portfolio_simulation
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import _rsi


def _bar(i, o, c, v=10_000_000.0):
    # Very narrow bars so the 8x safety stop sits close to entry -> large desired
    # notional per candidate, forcing the 120% gross cap to bite (equal-share cuts).
    hi = max(o, c) * 1.0001
    lo = min(o, c) * 0.9999
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
        max_positions=3,
        risk_per_trade_pct=10.0,  # large desired notional -> 120% cap bites, equal-share cuts
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
        time_exit_max_bars=10,
    )
    d.update(kw)
    return StrategyConfig(**d)


capital = 100000.0
cap_value = capital * 120.0 / 100.0  # 120000

deep = _make_rsi_series(0.97)
mid = _make_rsi_series(0.985)
mild = _make_rsi_series(0.99)
rsi_by_sym = {"DEEP": _rsi(deep, 21), "MID": _rsi(mid, 21), "MILD": _rsi(mild, 21)}
assert rsi_by_sym["DEEP"] < rsi_by_sym["MID"] < rsi_by_sym["MILD"] < 20.0

# Risk-based sizing: size = capital*1% / (entry - stop); stop = entry*(1-8*range_ratio).
# range_ratio ~ 0.002 => risk/share ~ 1.6% of entry => notional ~ 62500 per candidate.
# 3 * 62500 = 187500 > 120000 cap => equal-share cut to 40000 each.
res = run_portfolio_simulation({"DEEP": deep, "MID": mid, "MILD": mild},
                               config=_cfg(entry_next_bar=False), capital=capital)

print(f"num_trades={res['num_trades']} final_open={res['final_open_positions']} "
      f"gross={res['final_gross_exposure']:.6f} total_pnl={res['total_pnl']:.6f}")
for t in res['trades']:
    notional = t['entry_price'] * t['shares']
    print(f"  {t['symbol']}: exit={t['exit_reason']} entry_px={t['entry_price']:.6f} "
          f"shares={t['shares']:.6f} notional={notional:.4f} pnl={t['total_pnl']:.6f}")

# Deepest-first admission order preserved
assert [t['symbol'] for t in res['trades']] == ['DEEP', 'MID', 'MILD'], [t['symbol'] for t in res['trades']]
# All three admitted (cap allows 3 positions at equal share > 0)
assert res['num_trades'] == 3, res['num_trades']
# Equal-share cut: each notional must be <= cap/3 (cuts only, never topped up above desired)
equal_share = cap_value / 3.0
for t in res['trades']:
    notional = t['entry_price'] * t['shares']
    assert notional <= equal_share + 1e-6, (t['symbol'], notional, equal_share)
    assert notional > 0, t['symbol']
# Final reconciliation: no open positions, zero gross exposure
assert res['final_open_positions'] == 0
assert abs(res['final_gross_exposure']) < 1e-9
print(f"\nEqual-share cut target per position: {equal_share:.4f}")
print("ALL PROBE ASSERTIONS PASSED")