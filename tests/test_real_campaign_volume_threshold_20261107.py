"""HANDOFF 2026-11-07T02:53Z priority (1)/(3): $5M gating/provenance hardening
at scripts.run_real_campaign boundary.

Failing-tests-first. Ensures validate_symbol_volume_coverage enforces the
requested min_daily_volume_usd threshold even if manifest volume_filter_ok is
stale/incorrect, and rejects missing observed_min when threshold gating is
required. Synthetic manifest fixtures only (non-evidence).
"""
from __future__ import annotations

import pytest

from scripts.run_real_campaign import validate_symbol_volume_coverage
from src.data.provenance import ProvenanceError


def _manifest(sym: str, *, status="ok", complete=True, volume_filter_ok=True,
              observed_min=6_000_000.0, observed_mean=7_000_000.0, bars_passing=10,
              bars_checked=10):
    return {
        "symbols": {
            sym: {
                "status": status,
                "coverage": {"complete_for_target_window": complete,
                             "expected_hourly_bars": 6792, "observed_in_window_bars": 6792 if complete else 0},
                "volume_coverage": {
                    "volume_filter_ok": volume_filter_ok,
                    "observed_min_24h_usd_volume": observed_min,
                    "observed_mean_24h_usd_volume": observed_mean,
                    "bars_passing": bars_passing,
                    "bars_checked": bars_checked,
                },
            }
        }
    }


def test_rejects_when_observed_min_below_requested_threshold_even_if_flag_true():
    m = _manifest("BTC", volume_filter_ok=True, observed_min=1_000_000.0)
    with pytest.raises(ProvenanceError) as ei:
        validate_symbol_volume_coverage(m, ["BTC"], 5_000_000.0)
    msg = str(ei.value)
    assert "BTC" in msg
    assert "volume" in msg.lower() or "5" in msg


def test_rejects_missing_observed_min_when_threshold_required():
    m = _manifest("BTC", volume_filter_ok=True, observed_min=None)
    with pytest.raises(ProvenanceError):
        validate_symbol_volume_coverage(m, ["BTC"], 5_000_000.0)


def test_accepts_when_observed_min_meets_threshold():
    m = _manifest("BTC", volume_filter_ok=True, observed_min=5_000_000.0)
    assert validate_symbol_volume_coverage(m, ["BTC"], 5_000_000.0) == ["BTC"]


def test_rejects_when_flag_false_even_if_observed_min_missing_legacy_shape_is_blocked():
    # Conservative: flag false blocks regardless.
    m = _manifest("BTC", volume_filter_ok=False, observed_min=9_000_000.0)
    with pytest.raises(ProvenanceError):
        validate_symbol_volume_coverage(m, ["BTC"], 5_000_000.0)
