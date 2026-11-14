"""Opt-in spec-literal next-open entry flag (2026-11-14).

The spec's entry rule is "buy at next hourly open" after the RSI(21)<20 crash
close; it has no same-bar rebound confirmation candle. The canonical path keeps
`confirm_rebound` (default), and the new opt-in flag must bypass ONLY that gate.
"""
from __future__ import annotations

import copy

from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import generate_signal


def _candles():
    # 30 down bars -> RSI(21) below 20, then a crash bar that is NOT a rebound
    # candle (close below open), so the canonical gate rejects it.
    candles = []
    price = 100.0
    for i in range(30):
        price *= 0.97
        candles.append({
            "timestamp": f"2026-01-01T{i:02d}:00:00Z",
            "open": price * 1.001,
            "high": price * 1.002,
            "low": price * 0.998,
            "close": price,
            "volume": 10_000_000.0,
        })
    return candles


def test_default_path_keeps_same_bar_confirm_gate():
    cfg = StrategyConfig(use_rsi_trigger=True, min_daily_volume_usd=0)
    candles = _candles()
    assert cfg.entry_spec_literal_next_open is False
    assert generate_signal(candles, symbol="TEST", config=cfg) is None


def test_opt_in_bypasses_only_same_bar_confirm():
    cfg = StrategyConfig(use_rsi_trigger=True, min_daily_volume_usd=0,
                         entry_spec_literal_next_open=True)
    candles = _candles()
    sig = generate_signal(candles, symbol="TEST", config=cfg)
    assert sig is not None
    assert sig.side == "long"
    assert sig.signal_index == len(candles) - 1


def test_opt_in_still_enforces_volume_floor():
    cfg = StrategyConfig(use_rsi_trigger=True, min_daily_volume_usd=5_000_000.0,
                         entry_spec_literal_next_open=True)
    candles = _candles()
    for c in candles:
        c["volume"] = 1.0  # far below the $5M trailing-24h floor
    assert generate_signal(candles, symbol="TEST", config=cfg) is None


def test_opt_in_does_not_mutate_shared_default_config():
    before = copy.deepcopy(StrategyConfig())
    StrategyConfig(use_rsi_trigger=True, entry_spec_literal_next_open=True)
    after = StrategyConfig()
    assert after.entry_spec_literal_next_open is False
    assert before.entry_spec_literal_next_open is False