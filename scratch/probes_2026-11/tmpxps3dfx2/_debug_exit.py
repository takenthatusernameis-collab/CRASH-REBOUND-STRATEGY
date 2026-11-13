from __future__ import annotations
from scripts.run_portfolio import run_portfolio_simulation
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import _rsi
from src.backtest.engine import backtest_simple
from src.strategy.crash_rebound import generate_signal


def _bar(i, o, c, v=10_000_000.0):
    hi = max(o, c) * 1.001
    lo = min(o, c) * 0.999
    return {"timestamp": f"2026-01-01T{i:02d}:00:00Z", "open": o, "high": hi,
            "low": lo, "close": c, "volume": v}


def _make_rsi_series(step, n=60):
    candles = []
    p = 100.0
    for i in range(n):
        c = p * step
        candles.append(_bar(i, p, c))
        p = c
    candles.append(_bar(n, p, p * 1.05))
    return candles


deep = _make_rsi_series(0.97)
print("len:", len(deep), "last bar:", deep[-1])
print("RSI:", _rsi(deep, 21))

cfg = StrategyConfig(use_rsi_trigger=True, rsi_period=21, rsi_threshold=20.0,
                     avoid_downtrend=True, regime_min_price=0.0, min_daily_volume_usd=0.0,
                     enable_eth_hedge=False, enable_rebound_short=False,
                     enable_volume_based_sizing=False, gross_cap_pct=120.0, max_positions=1,
                     slippage_pct=0.0, commission_per_share=0.0, commission_min=0.0,
                     time_exit_max_bars=10, entry_next_bar=False, risk_per_trade_pct=1.0)
sig = generate_signal(deep, symbol="DEEP", config=cfg, capital=100000.0)
print("sig:", sig.entry_price, sig.stop_price, sig.target_price, sig.size_shares, sig.signal_index)
res = backtest_simple(deep, sig, config=cfg, capital=100000.0)
print("res:", res.exit_reason, res.entry_price, res.exit_price, res.shares, res.bars_held, res.total_pnl)