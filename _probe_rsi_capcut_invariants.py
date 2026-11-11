"""Probe (2026-11-11): verify 3-candidate cap-cut respects cap, cuts-only (no top-up).

Instruments RiskState.apply_cap_cuts / apply_trade to record the engine's own
notional schedule during the portfolio scan, then asserts:
  - equal-share cuts fired when total desired > 120% cap,
  - no position is ever topped up above its entry fill notional,
  - overlay gross never exceeds the cap,
  - deepest-first admission order preserved,
  - final reconciliation to 0 open / 0 gross.

Deterministic synthetic fixtures only; not market evidence.
"""
from __future__ import annotations

import scripts.run_portfolio as rp
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import _rsi
from src.strategy.risk import RiskState


def _bar(i, o, c, v=10_000_000.0):
    hi = max(o, c) * 1.0001
    lo = min(o, c) * 0.9999
    return {"timestamp": f"2026-01-01T{i:02d}:00:00Z", "open": o, "high": hi,
            "low": lo, "close": c, "volume": v}


def _make_rsi_series(step: float, n: int = 60):
    candles = []
    p = 100.0
    for i in range(n):
        c = p * step
        candles.append(_bar(i, p, c))
        p = c
    candles.append(_bar(n, p, p * 1.05))
    return candles


def _cfg(**kw):
    d = dict(use_rsi_trigger=True, rsi_period=21, rsi_threshold=20.0,
             avoid_downtrend=True, regime_min_price=0.0, min_daily_volume_usd=0.0,
             enable_eth_hedge=False, enable_rebound_short=False,
             enable_volume_based_sizing=False, gross_cap_pct=120.0, max_positions=3,
             risk_per_trade_pct=10.0, slippage_pct=0.0, commission_per_share=0.0,
             commission_min=0.0, time_exit_max_bars=10)
    d.update(kw)
    return StrategyConfig(**d)


cap_events = []   # (symbol, all_notionals_before_cut, cuts_after)
open_events = []  # (symbol, notional_at_open)


_orig_apply_cap_cuts = RiskState.apply_cap_cuts
_orig_apply_trade = RiskState.apply_trade


def _cap_cuts(self, capital, config, open_notional=None):
    res = _orig_apply_cap_cuts(self, capital, config, open_notional)
    if open_notional and sum(open_notional) > capital * config.gross_cap_pct / 100.0:
        cap_events.append((list(open_notional), list(res)))
    return res


def _apply_trade(self, date, pnl, opened, closed, notional=0.0):
    if opened and notional > 0:
        open_events.append(notional)
    return _orig_apply_trade(self, date, pnl, opened, closed, notional)


RiskState.apply_cap_cuts = _cap_cuts
RiskState.apply_trade = _apply_trade
try:
    capital = 100000.0
    cap_value = capital * 120.0 / 100.0
    deep = _make_rsi_series(0.97)
    mid = _make_rsi_series(0.985)
    mild = _make_rsi_series(0.99)
    res = rp.run_portfolio_simulation({"DEEP": deep, "MID": mid, "MILD": mild},
                                      config=_cfg(entry_next_bar=False), capital=capital)
finally:
    RiskState.apply_cap_cuts = _orig_apply_cap_cuts
    RiskState.apply_trade = _orig_apply_trade

print(f"num_trades={res['num_trades']} final_open={res['final_open_positions']} "
      f"gross={res['final_gross_exposure']}")
for t in res['trades']:
    print(f"  {t['symbol']}: fill_notional={t['entry_price']*t['shares']:.4f}")

print("\nCap-cut events (before, after equal-share):")
for b, a in cap_events:
    print(f"  before={[round(x,2) for x in b]} after={[round(x,2) for x in a]} "
          f"sum_before={sum(b):.2f} sum_after={sum(a):.2f} cap={cap_value}")

print("\nOpen notional registrations (per admission):", [round(x,2) for x in open_events])

# Assertions
assert [t['symbol'] for t in res['trades']] == ['DEEP', 'MID', 'MILD']
assert res['num_trades'] == 3
assert res['final_open_positions'] == 0
assert abs(res['final_gross_exposure']) < 1e-9
# A cap cut must have fired (total desired > cap)
assert cap_events, "expected at least one equal-share cap cut"
# Cuts only: every post-cut notional <= its pre-cut notional (no top-up)
for b, a in cap_events:
    for bn, an in zip(b, a):
        assert an <= bn + 1e-9, (bn, an)
# Equal-share: post-cut notionals all equal to cap/n
for b, a in cap_events:
    n = len(a)
    expected = cap_value / n
    for an in a:
        assert abs(an - expected) < 1e-6, (a, expected)
# No single fill exceeds the cap
for t in res['trades']:
    assert t['entry_price'] * t['shares'] <= cap_value + 1e-6
print("\nALL PROBE ASSERTIONS PASSED")