"""HANDOFF 2026-11-07 priority: $5M volume gating integrity audit.

Failing-tests-first: spec-compliant gating paths must not silently accept a
sub-$5M (non-zero) min_daily_volume_usd threshold. The spec requires >= $5M
24h volume in ALL required spec-compliant gating paths. A caller passing 1M
must not bypass the $5M filter.

Enforcement: StrategyConfig.validate/enforce_spec_volume_floor() and all
spec-compliant gating functions (detect_crash, detect_crash_rsi,
passes_universe_filter, filter_universe, generate_signal path) raise the floor
to $5M for any non-zero sub-$5M input. min_daily_volume_usd=0 remains an
explicit non-spec fixture escape hatch.

Synthetic fixtures only (non-evidence).
"""
from __future__ import annotations

import copy
import pytest

from src.strategy.config import StrategyConfig, enforce_spec_volume_floor
from src.strategy.crash_rebound import (
    detect_crash_rsi,
    detect_crash,
    passes_universe_filter,
    filter_universe,
    generate_signal,
)


def _mid_vol_candles(n=40, base=100.0):
    # ~2.4M/day - above 1M, below 5M
    return [{"timestamp": f"2026-01-01T{i%24:02d}:00:00Z", "open": base, "high": base*1.01,
             "low": base*0.94, "close": base*0.95, "volume": 1000.0} for i in range(n)]


def _crash_rebound_candles(vol=10_000.0):
    c = []
    for i in range(30):
        o = 100.0 - i * 0.3
        c.append({"timestamp": f"2026-01-{i//24+1:02d}T{i%24:02d}:00:00Z",
                  "open": o, "high": o+0.5, "low": o-2.0, "close": o-1.5, "volume": vol})
    c[-1] = {"timestamp": "2026-01-02T05:00:00Z", "open": 90, "high": 95, "low": 89, "close": 94, "volume": vol}
    return c


class TestEnforceSpecVolumeFloor:
    def test_raises_sub5m_nonzero_to_5m(self):
        assert enforce_spec_volume_floor(1_000_000) == 5_000_000.0

    def test_preserves_5m(self):
        assert enforce_spec_volume_floor(5_000_000) == 5_000_000.0

    def test_preserves_above_5m(self):
        assert enforce_spec_volume_floor(10_000_000) == 10_000_000.0

    def test_preserves_zero_escape_hatch(self):
        assert enforce_spec_volume_floor(0) == 0.0


class TestGatingFunctionsEnforceSpecFloor:
    def test_passes_universe_filter_enforces_5m_floor_for_sub5m_nonzero(self):
        mid = _mid_vol_candles()  # ~2.4M/day
        assert passes_universe_filter(mid, min_daily_volume_usd=1_000_000) is False

    def test_filter_universe_enforces_5m_floor_for_sub5m_nonzero(self):
        mid = _mid_vol_candles()
        passed = filter_universe({"MID": mid}, min_daily_volume_usd=1_000_000)
        assert "MID" not in passed

    def test_detect_crash_rsi_enforces_5m_floor_for_sub5m_nonzero(self):
        mid = _mid_vol_candles()
        oversold = copy.deepcopy(mid)
        for i, c in enumerate(oversold):
            c["close"] = 100 - i * 0.5
            c["open"] = c["close"] + 0.1
            c["high"] = c["open"] + 0.2
            c["low"] = c["close"] - 0.2
        assert detect_crash_rsi(oversold, rsi_threshold=99, min_daily_volume_usd=1_000_000) is False

    def test_detect_crash_enforces_5m_floor_for_sub5m_nonzero(self):
        oversold = []
        for i in range(30):
            o = 100 - i
            oversold.append({"timestamp": f"t{i}", "open": o, "high": o+1, "low": o-5, "close": o-4, "volume": 1000.0})
        assert detect_crash(oversold, pct_drop=-1.0, use_rsi_trigger=False, min_daily_volume_usd=1_000_000) is False

    def test_generate_signal_enforces_5m_floor_even_with_sub5m_config_value(self):
        candles = _crash_rebound_candles(vol=1000.0)  # ~2.4M/day
        # Force a sub-5M value past config validation to simulate a bypass attempt.
        cfg = StrategyConfig(use_rsi_trigger=False, min_daily_volume_usd=0, crash_pct_drop=-1.0, crash_lookback=30)
        object.__setattr__(cfg, 'min_daily_volume_usd', 1_000_000)
        assert generate_signal(candles, config=cfg) is None


class TestZeroEscapeHatchPreserved:
    def test_zero_allows_fixture_path(self):
        # Zero is non-spec fixture escape hatch only.
        assert enforce_spec_volume_floor(0) == 0.0
        cfg = StrategyConfig(min_daily_volume_usd=0)
        assert cfg.min_daily_volume_usd == 0
