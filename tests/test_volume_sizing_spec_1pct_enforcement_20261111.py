"""HANDOFF 2026-11-11T04:30Z #1 campaign: 1.25% volume sizing enforcement audit.

Failing-tests-first regression locks. The spec requires position sizing to be
1.25% of the coin's 24h USD volume in ALL spec-compliant signal paths. Prior to
this audit, `position_size_pct_of_daily_volume` was a free parameter: a caller
could mutate it (e.g. 0.5%) or disable volume sizing (`enable_volume_based_sizing=False`)
and silently bypass the spec sizing in generate_signal — a concrete bypass with
no failing test. This locks the bypass shut at two surfaces:

  1) StrategyConfig.__post_init__ rejects a non-1.25 pct when volume-based
     sizing is enabled (catches config-construction bypasses, including
     object.__setattr__ mutations that skip __post_init__ — see the
     object.__setattr__ test which is the reason the generate_signal guard below
     is a SECOND, independent line of defense).
  2) generate_signal enforces the pct at signal time (catches any config that
     reaches the signal path with a mutated pct).

min_daily_volume_usd=0 / enable_volume_based_sizing=False remain the only
explicit non-spec escape hatches (low-level/fixture callers).

Synthetic fixtures only (non-evidence).
"""
from __future__ import annotations

import copy
import pytest

from src.strategy.config import (
    StrategyConfig,
    SPEC_POSITION_SIZE_PCT_OF_DAILY_VOLUME,
    enforce_spec_position_size_pct,
)
from src.strategy.crash_rebound import generate_signal, position_size_by_volume, _daily_volume_usd


def _crash_rebound_candles(vol=50000.0, n=40):
    c = []
    for i in range(n):
        o = 100.0 - i * 0.3
        c.append({"timestamp": f"2026-01-{i//24+1:02d}T{i%24:02d}:00:00Z",
                  "open": o, "high": o + 0.5, "low": o - 2.0, "close": o - 1.5, "volume": vol})
    c[-1] = {"timestamp": "2026-01-02T05:00:00Z", "open": 90, "high": 95, "low": 80,
             "close": 94, "volume": vol}
    return c


def _spec_cfg(**kw):
    base = dict(use_rsi_trigger=False, enable_volume_based_sizing=True,
                position_size_pct_of_daily_volume=1.25, min_daily_volume_usd=5_000_000.0,
                crash_pct_drop=-1.0, crash_lookback=30)
    base.update(kw)
    return StrategyConfig(**base)


class TestEnforceSpecPositionSizePct:
    def test_spec_value_preserved(self):
        assert enforce_spec_position_size_pct(1.25) == 1.25

    def test_rejects_mutated_pct_below_spec(self):
        with pytest.raises(ValueError):
            enforce_spec_position_size_pct(0.5)

    def test_rejects_mutated_pct_above_spec(self):
        with pytest.raises(ValueError):
            enforce_spec_position_size_pct(2.0)

    def test_zero_is_escape_hatch(self):
        assert enforce_spec_position_size_pct(0.0) == 0.0

    def test_non_numeric_rejected(self):
        with pytest.raises(ValueError):
            enforce_spec_position_size_pct(["1.25"])


class TestConfigConstructionRejectsMutatedSizingPct:
    def test_mutated_pct_rejected_at_construction(self):
        with pytest.raises(ValueError):
            StrategyConfig(use_rsi_trigger=False, enable_volume_based_sizing=True,
                           position_size_pct_of_daily_volume=0.5)

    def test_spec_pct_accepted(self):
        cfg = _spec_cfg()
        assert cfg.position_size_pct_of_daily_volume == 1.25

    def test_disabled_sizing_allows_any_pct(self):
        # Disabled sizing is the only non-spec escape hatch.
        cfg = StrategyConfig(use_rsi_trigger=False, enable_volume_based_sizing=False,
                             position_size_pct_of_daily_volume=0.5)
        assert cfg.position_size_pct_of_daily_volume == 0.5

    def test_object_setattr_mutation_caught_by_generate_signal_guard(self):
        """object.__setattr__ skips __post_init__; the generate_signal guard is the
        independent second line of defense and must reject the mutation."""
        cfg = _spec_cfg()
        object.__setattr__(cfg, 'position_size_pct_of_daily_volume', 0.5)
        candles = _crash_rebound_candles()
        with pytest.raises(ValueError):
            generate_signal(candles, config=cfg)


class TestGenerateSignalSizingIsSpecCompliant:
    def test_size_shares_equals_1pct_of_24h_volume(self):
        candles = _crash_rebound_candles()
        dv = _daily_volume_usd(candles, 24)
        cfg = _spec_cfg()
        sig = generate_signal(candles, config=cfg)
        assert sig is not None
        expected = position_size_by_volume(sig.entry_price, dv, 1.25)
        assert abs(sig.size_shares - expected) < 1e-6

    def test_disabled_sizing_falls_back_to_risk_based(self):
        candles = _crash_rebound_candles()
        cfg = _spec_cfg(enable_volume_based_sizing=False)
        sig = generate_signal(candles, config=cfg)
        assert sig is not None
        # risk-based sizing, not volume sizing
        assert sig.size_shares != position_size_by_volume(
            sig.entry_price, _daily_volume_usd(candles, 24), 1.25)

    def test_mutated_pct_in_signal_path_rejected(self):
        candles = _crash_rebound_candles()
        cfg = _spec_cfg()
        object.__setattr__(cfg, 'position_size_pct_of_daily_volume', 2.0)
        with pytest.raises(ValueError):
            generate_signal(candles, config=cfg)