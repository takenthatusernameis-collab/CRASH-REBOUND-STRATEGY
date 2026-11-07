"""Deterministic spec-fidelity regression (2026-11-07): on the same bar where
both liquidation (worst-price threshold) and stop could be relevant, liquidation
is checked first and takes precedence. This documents deterministic ordering used
by the hourly engine; spec requires liquidation at worst price — liquidation
check must not be skipped by stop evaluation.

Synthetic fixtures only; not performance evidence; no real market data; no look-ahead.
"""
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal

ENTRY_PX = 100.0
SHARES = 1.0
SIGNAL_IDX = 5


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _coin(n):
    return [_c(f"2025-01-01T{i % 24:02d}:00:00", 100.2, 101.5, 99.0, 100.2) for i in range(n)]


def _eth(n):
    return [_c(f"2025-01-01T{i % 24:02d}:00:00", 2000.0, 2005.0, 1995.0, 2000.0 + (i % 3)) for i in range(n)]


def _sig(stop_price):
    return Signal(symbol="T", side="long", reason="t", entry_price=ENTRY_PX, stop_price=stop_price,
                  target_price=150.0, risk_per_share=1.0, timestamp="2025-01-01T05:00:00",
                  size_shares=SHARES, signal_index=SIGNAL_IDX)


def _cfg():
    return StrategyConfig(
        enable_eth_hedge=True, enable_rebound_short=False, entry_next_bar=False,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=0.0, funding_rate_pct_per_hour=0.0, min_daily_volume_usd=0.0,
        time_exit_max_bars=200, enable_liquidation_checks=True,
        liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5,
    )


def test_liquidation_precedes_stop_on_same_bar():
    candles = _coin(30)
    # Bar 8: low breaches liquidation threshold (94.0). Stop placed above threshold
    # (e.g. 95.0) would also trigger by low, but liquidation is checked first.
    candles[8] = _c("2025-01-01T08:00:00", 96.0, 96.5, 93.0, 93.5)
    res = backtest_simple(candles, _sig(stop_price=95.0), config=_cfg(), eth_candles=_eth(30))
    assert res.exit_reason == "liquidated"
    assert res.bars_held == 8 - SIGNAL_IDX + 1
    assert res.exit_price == 93.0  # worst price / low, no slippage


def test_stop_triggers_when_liquidation_not_breached():
    candles = _coin(30)
    # Low hits stop (95.0) but stays above liquidation threshold (94.0).
    candles[8] = _c("2025-01-01T08:00:00", 96.0, 96.5, 94.5, 94.8)
    res = backtest_simple(candles, _sig(stop_price=95.0), config=_cfg(), eth_candles=_eth(30))
    assert res.exit_reason == "stopped"
    assert res.exit_price == 95.0
