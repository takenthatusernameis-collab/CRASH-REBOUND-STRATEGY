"""Debug: trace batch-cut pre-adjustment for 3 RSI candidates."""
from __future__ import annotations
import copy
from scripts.run_portfolio import run_portfolio_simulation
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import _rsi, generate_signal


def _bar(i, o, c, v=10_000_000.0):
    hi = max(o, c) * 1.0001
    lo = min(o, c) * 0.9999
    return {"timestamp": f"2026-01-01T{i:02d}:00:00Z", "open": o, "high": hi,
            "low": lo, "close": c, "volume": v}


def _make_rsi_series(step, n=60):
    candles, p = [], 100.0
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


capital = 100000.0
deep = _make_rsi_series(0.97)
mid = _make_rsi_series(0.985)
mild = _make_rsi_series(0.99)
for s in (deep, mid, mild):
    last = s[-1]["close"]
    s.append(_bar(len(s), last * 1.01, last * 1.005))

cfg = _cfg(entry_next_bar=True)
# Inspect generate_signal sizing per symbol at decision bar 60
for name, candles in (("DEEP", deep), ("MID", mid), ("MILD", mild)):
    sig = generate_signal(candles[:61], symbol=name, config=cfg, capital=capital)
    print(f"{name}: sig.entry_price={sig.entry_price:.6f} size_shares={sig.size_shares:.4f} "
          f"next_open={candles[61]['open']:.6f} desired={sig.entry_price*sig.size_shares:.2f}")