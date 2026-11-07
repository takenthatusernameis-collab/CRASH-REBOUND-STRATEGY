from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.data.provenance import (
    TARGET_START,
    TARGET_END,
    expected_hourly_bars,
    validate_provenance,
    require_verified_provenance,
    ProvenanceError,
)


def _complete_manifest():
    exp = expected_hourly_bars(TARGET_START, TARGET_END)
    return {
        "fabricated_data": False,
        "real_market_data_intended": True,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": exp},
        "symbols": {
            "BTC": {"status": "ok", "coverage": {"expected_hourly_bars": exp, "observed_in_window_bars": exp, "gap_count": 0, "complete_for_target_window": True}, "synthetic_check": {"is_synthetic": False, "reason": "varied_series_ok"}},
            "ETH": {"status": "ok", "coverage": {"expected_hourly_bars": exp, "observed_in_window_bars": exp, "gap_count": 0, "complete_for_target_window": True}, "synthetic_check": {"is_synthetic": False, "reason": "varied_series_ok"}},
        },
    }


def test_provenance_rejects_missing_manifest(tmp_path):
    with pytest.raises(ProvenanceError):
        require_verified_provenance(tmp_path / "missing.json")


def test_provenance_rejects_fabricated_flag():
    m = _complete_manifest()
    m["fabricated_data"] = True
    ok, errs = validate_provenance(m)
    assert not ok
    assert any("fabricated" in e for e in errs)


def test_provenance_rejects_incomplete_coverage():
    m = _complete_manifest()
    exp = expected_hourly_bars()
    m["symbols"]["BTC"]["coverage"]["observed_in_window_bars"] = exp - 1
    m["symbols"]["BTC"]["coverage"]["complete_for_target_window"] = False
    ok, errs = validate_provenance(m)
    assert not ok


def test_provenance_rejects_gap():
    m = _complete_manifest()
    m["symbols"]["ETH"]["coverage"]["gap_count"] = 1
    m["symbols"]["ETH"]["coverage"]["complete_for_target_window"] = False
    ok, errs = validate_provenance(m)
    assert not ok


def test_provenance_accepts_complete_verified_manifest(tmp_path):
    m = _complete_manifest()
    p = tmp_path / "provenance.json"
    p.write_text(json.dumps(m))
    out = require_verified_provenance(p)
    assert out["real_market_data_intended"] is True


def test_expected_hourly_bars_target_window():
    # 283 days inclusive hourly: 6791 hours between endpoints? actual computed from bounds.
    exp = expected_hourly_bars(TARGET_START, TARGET_END)
    assert exp > 0
    # sanity: roughly 283*24 bars
    assert 6700 <= exp <= 6900
