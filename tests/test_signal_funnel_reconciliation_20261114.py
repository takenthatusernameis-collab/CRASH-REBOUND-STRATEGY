from __future__ import annotations

from scripts.reconcile_hyperliquid_signal_funnel import (
    reconcile_symbol,
    rolling_volume_24h,
)
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import _daily_volume_usd


def _candles(closes: list[float], volume: float = 100_000.0) -> list[dict]:
    out = []
    for i, close in enumerate(closes):
        open_ = closes[i - 1] if i else close
        out.append(
            {
                "timestamp": f"2026-01-01T{i:02d}:00:00+00:00",
                "open": open_,
                "high": max(open_, close) * 1.001,
                "low": min(open_, close) * 0.999,
                "close": close,
                "volume": volume,
            }
        )
    return out


def test_rolling_volume_matches_reference_helper() -> None:
    candles = _candles([100.0 - i * 0.5 for i in range(40)])
    rolling = rolling_volume_24h(candles)
    for i in range(len(candles)):
        assert rolling[i] == _daily_volume_usd(candles[: i + 1], lookback=24)


def test_funnel_counts_crash_volume_and_same_bar_confirmation() -> None:
    closes = [100.0 - i * 1.5 for i in range(24)]
    closes += [closes[-1] + 2.0]  # bullish rebound bar while RSI is still deeply oversold
    candles = _candles(closes)
    cfg = StrategyConfig(
        use_rsi_trigger=True,
        enable_rebound_short=True,
        enable_eth_hedge=True,
        enable_volume_based_sizing=True,
        min_daily_volume_usd=5_000_000.0,
    )

    _, summary = reconcile_symbol(candles, cfg)

    assert summary["rsi_crash_hours"] > 0
    assert summary["rsi_crash_hours_pass_volume"] == summary["rsi_crash_hours"]
    assert summary["same_bar_rebound_confirm"] >= 1
    assert summary["generate_signal_confirmed"] >= 1