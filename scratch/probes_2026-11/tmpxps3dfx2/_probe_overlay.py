"""Probe (2026-11-11): inspect portfolio overlay notionals during 3-candidate cap-cut."""
from __future__ import annotations

import scripts.run_portfolio as rp
from src.backtest.engine import backtest_simple as orig_bs
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import _rsi


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


snapshots = []
def spy(candles, sig, config=None, capital=100000.0, risk_state=None,
        eth_candles=None, require_eth_hedge=False):
    res = orig_bs(candles, sig, config=config, capital=capital, risk_state=risk_state,
                  eth_candles=eth_candles, require_eth_hedge=require_eth_hedge)
    if res.exit_reason not in ('blocked', 'no_signal') and risk_state is not None:
        snapshots.append((getattr(sig, 'symbol', '?'),
                          list(risk_state.open_position_notionals),
                          float(getattr(risk_state, 'gross_exposure', 0.0))))
    return res


rp.backtest_simple = spy
try:
    capital = 100000.0
    deep = _make_rsi_series(0.97)
    mid = _make_rsi_series(0.985)
    mild = _make_rsi_series(0.99)
    res = rp.run_portfolio_simulation({"DEEP": deep, "MID": mid, "MILD": mild},
                                      config=_cfg(entry_next_bar=False), capital=capital)
finally:
    rp.backtest_simple = orig_bs

print(f"num_trades={res['num_trades']} final_open={res['final_open_positions']} "
      f"gross={res['final_gross_exposure']}")
for t in res['trades']:
    print(f"  {t['symbol']}: shares={t['shares']:.4f} entry_px={t['entry_price']:.4f} "
          f"fill_notional={t['entry_price']*t['shares']:.4f}")
print("Post-admission overlay notionals (symbol, [notionals], gross):")
for s in snapshots:
    print("  ", s)
print("\nExpected: after all 3 admitted, overlay = [40000, 40000, 40000] (equal share of 120k cap)")
print("Actual final overlay gross from last snapshot:", snapshots[-1][2] if snapshots else None)