"""Track-4e hardening: validate_provenance require_complete semantics.

Deterministic, non-evidence. Ensures require_complete=False permits mixed manifests
when min_symbols complete symbols exist, without flag being ignored.
"""
from __future__ import annotations

from src.data.provenance import validate_provenance, expected_hourly_bars, _complete_symbol_subset_safe


def _base_manifest():
    exp = expected_hourly_bars()
    return {
        "fabricated_data": False,
        "real_market_data_intended": True,
        "target_window": {
            "start": "2025-12-20T00:00:00Z",
            "end": "2026-09-28T23:00:00Z",
            "expected_hourly_bars": exp,
        },
        "symbols": {
            "BTC": {
                "status": "ok",
                "coverage": {
                    "complete_for_target_window": True,
                    "expected_hourly_bars": exp,
                    "observed_in_window_bars": exp,
                    "gap_count": 0,
                },
            },
            "ETH": {
                "status": "error",
                "coverage": {
                    "complete_for_target_window": False,
                    "observed_in_window_bars": 4082,
                    "expected_hourly_bars": exp,
                    "gap_count": 0,
                },
            },
        },
    }


def test_require_complete_false_accepts_mixed_manifest_with_sufficient_complete():
    m = _base_manifest()
    ok, errs = validate_provenance(m, require_complete=False, min_symbols=1)
    assert ok is True, errs
    assert errs == []


def test_require_complete_true_rejects_mixed_manifest():
    m = _base_manifest()
    ok, errs = validate_provenance(m, require_complete=True, min_symbols=1)
    assert ok is False
    assert any("ETH" in e or "complete" in e.lower() for e in errs)


def test_require_complete_false_still_enforces_min_symbols():
    m = _base_manifest()
    m["symbols"]["BTC"]["status"] = "error"
    m["symbols"]["BTC"]["coverage"]["complete_for_target_window"] = False
    ok, errs = validate_provenance(m, require_complete=False, min_symbols=1)
    assert ok is False
    assert any("complete symbols" in e for e in errs)


def test_require_complete_false_still_rejects_bad_complete_symbol():
    m = _base_manifest()
    exp = expected_hourly_bars()
    m["symbols"]["BTC"]["coverage"]["gap_count"] = 5
    ok, errs = validate_provenance(m, require_complete=False, min_symbols=1)
    assert ok is False
    assert any("gap_count" in e for e in errs)


def test_complete_symbol_subset_safe_filters_only_verified_complete():
    m = _base_manifest()
    sub = _complete_symbol_subset_safe(m)
    assert sorted(sub["symbols"].keys()) == ["BTC"]
    assert sub["summary"]["complete_symbols_subset_count"] == 1
    assert sub["symbols"]["BTC"]["coverage"]["complete_for_target_window"] is True
