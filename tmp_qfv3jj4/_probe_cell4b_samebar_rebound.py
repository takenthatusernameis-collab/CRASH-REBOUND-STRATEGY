"""Trace probe (2026-11-12, cell 4b): same-bar stop-vs-target sequencing with
enable_rebound_short=True. NOT a test file; scratch trace only.
"""
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _coin(n):
    return [_c(f"2025-01-01T{i % 24:02d}:00:00", 100.2, 101.5, 99.0, 100.2) for i in range(n)]


def _cfg(**kw):
    d = dict(
        enable_eth_hedge=False, enable_rebound_short=True, entry_next_bar=False,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=0.0, funding_rate_pct_per_hour=0.0, min_daily_volume_usd=0.0,
        time_exit_max_bars=200, enable_liquidation_checks=False,
        liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5,
    )
    d.update(kw)
    return StrategyConfig(**d)


def _sig():
    return Signal(symbol="T", side="long", reason="t", entry_price=100.0, stop_price=90.0,
                  target_price=110.0, risk_per_share=10.0, timestamp="2025-01-01T05:00:00",
                  size_shares=1.0, signal_index=5)


# Case A: both stop and target breached on bar 8, rebound_short ON
c = _coin(30)
c[8] = _c("2025-01-01T08:00:00", 100.0, 111.0, 89.0, 100.0)
r = backtest_simple(c, _sig(), config=_cfg())
print("CASE A (both breach, rebound ON):")
print("  exit_reason:", r.exit_reason)
print("  exit_price:", r.exit_price)
print("  entry_price:", r.entry_price)
print("  shares:", r.shares)
print("  bars_held:", r.bars_held)
print("  pnl:", r.pnl)
print("  rebound_short_pnl:", r.rebound_short_pnl)
print("  trades:", r.trades)
print("  total_pnl:", r.total_pnl)

# Case B: target only breached on bar 8, rebound_short ON -> rebound short opens
c = _coin(30)
c[8] = _c("2025-01-01T08:00:00", 100.0, 111.0, 91.0, 100.0)
r = backtest_simple(c, _sig(), config=_cfg())
print("CASE B (target only, rebound ON):")
print("  exit_reason:", r.exit_reason)
print("  exit_price:", r.exit_price)
print("  entry_price:", r.entry_price)
print("  shares:", r.shares)
print("  bars_held:", r.bars_held)
print("  pnl:", r.pnl)
print("  rebound_short_pnl:", r.rebound_short_pnl)
print("  trades:", r.trades)
print("  total_pnl:", r.total_pnl)