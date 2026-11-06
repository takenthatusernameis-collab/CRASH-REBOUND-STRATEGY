"""Track-4e hardening: provenance cache SHA-256 verification + gating edge cases.

Deterministic, synthetic, non-evidence. Failing-test-first targets for
`verify_cache_sha256`, `sha256_file`, `complete_symbol_subset`, and
`require_verified_provenance`/`validate_provenance` gating semantics. Never
fabricates data; never substitutes fixtures for real market evidence.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import pytest

from src.data.provenance import (
    ProvenanceError,
    TARGET_START,
    TARGET_END,
    complete_symbol_subset,
    expected_hourly_bars,
    require_verified_provenance,
    sha256_file,
    validate_provenance,
    verify_cache_sha256,
)

EXP = expected_hourly_bars(TARGET_START, TARGET_END)


def _complete_entry(observed: int = EXP, status: str = "ok", gap_count: int = 0) -> dict:
    return {
        "status": status,
        "coverage": {
            "complete_for_target_window": status == "ok" and observed == EXP and gap_count == 0,
            "expected_hourly_bars": EXP,
            "observed_in_window_bars": observed,
            "gap_count": gap_count,
        },
    }


def _base_manifest() -> dict:
    return {
        "fabricated_data": False,
        "real_market_data_intended": True,
        "target_window": {
            "start": TARGET_START,
            "end": TARGET_END,
            "expected_hourly_bars": EXP,
        },
        "symbols": {
            "BTC": _complete_entry(EXP, "ok", 0),
            "ETH": _complete_entry(4082, "incomplete", 0),
        },
        "summary": {
            "all_complete": False,
            "ready_for_real_campaign": False,
            "complete_symbols": ["BTC"],
        },
    }


# --------------------------------------------------------------------------- #
# sha256_file / verify_cache_sha256
# --------------------------------------------------------------------------- #
def test_sha256_file_deterministic_matches_hashlib(tmp_path):
    p = tmp_path / "candle.json"
    payload = b'{"symbol":"BTC","bars":[]}'
    p.write_bytes(payload)
    assert sha256_file(p) == hashlib.sha256(payload).hexdigest()


def test_verify_cache_sha256_noop_when_expected_none(tmp_path):
    p = tmp_path / "candle.json"
    p.write_bytes(b"{}")
    verify_cache_sha256(p, None, "BTC")  # must not raise


def test_verify_cache_sha256_noop_when_expected_empty(tmp_path):
    p = tmp_path / "candle.json"
    p.write_bytes(b"{}")
    verify_cache_sha256(p, "", "BTC")  # must not raise


def test_verify_cache_sha256_passes_when_match(tmp_path):
    p = tmp_path / "candle.json"
    payload = b'{"symbol":"BTC","close":50000}'
    p.write_bytes(payload)
    verify_cache_sha256(p, hashlib.sha256(payload).hexdigest(), "BTC")  # must not raise


def test_verify_cache_sha256_raises_concrete_evidence_on_mismatch(tmp_path):
    p = tmp_path / "candle.json"
    p.write_bytes(b'{"symbol":"BTC","tampered":true}')
    expected = hashlib.sha256(b'{"symbol":"BTC","clean":true}').hexdigest()
    with pytest.raises(ProvenanceError) as ei:
        verify_cache_sha256(p, expected, "BTC")
    msg = str(ei.value)
    assert "Cache checksum mismatch for BTC" in msg
    assert f"file={p}" in msg
    assert "expected_sha256=" in msg
    assert "actual_sha256=" in msg
    assert "Refusing to use tampered/corrupted cache" in msg


# --------------------------------------------------------------------------- #
# complete_symbol_subset
# --------------------------------------------------------------------------- #
def test_complete_symbol_subset_filters_only_verified_complete():
    m = _base_manifest()
    sub = complete_symbol_subset(m)
    assert sorted(sub["symbols"].keys()) == ["BTC"]
    assert sub["symbols"]["BTC"]["status"] == "ok"
    assert sub["summary"]["complete_symbols_subset"] == ["BTC"]
    assert sub["summary"]["complete_symbols_subset_count"] == 1


def test_complete_symbol_subset_excludes_incomplete_even_if_status_ok_bars_short():
    m = _base_manifest()
    # BTC ok but short bars -> not complete
    m["symbols"]["BTC"]["coverage"]["observed_in_window_bars"] = EXP - 1
    sub = complete_symbol_subset(m)
    assert sub["symbols"] == {}
    assert sub["summary"]["complete_symbols_subset_count"] == 0


def test_complete_symbol_subset_excludes_non_zero_gap():
    m = _base_manifest()
    m["symbols"]["BTC"]["coverage"]["gap_count"] = 3
    sub = complete_symbol_subset(m)
    assert sub["symbols"] == {}


def test_complete_symbol_subset_excludes_wrong_window_expected_bars():
    m = _complete_entry(EXP, "ok", 0)
    manifest = {"symbols": {"BTC": m, "ETH": _complete_entry(EXP, "ok", 0)}}
    sub = complete_symbol_subset(manifest, start="2025-12-20T00:00:00Z", end="2025-12-21T00:00:00Z")
    # expected bars for 24h != EXP, so nothing matches
    assert sub["symbols"] == {}


def test_complete_symbol_subset_handles_none_and_malformed():
    assert complete_symbol_subset(None)["symbols"] == {}
    assert complete_symbol_subset({"symbols": "not-a-dict"})["symbols"] == {}
    assert complete_symbol_subset({})["symbols"] == {}


# --------------------------------------------------------------------------- #
# validate_provenance / require_verified_provenance gating
# --------------------------------------------------------------------------- #
def test_validate_provenance_rejects_fabricated_data():
    m = _base_manifest()
    m["fabricated_data"] = True
    ok, errs = validate_provenance(m, require_complete=False, min_symbols=1)
    assert ok is False
    assert any("fabricated_data" in e for e in errs)


def test_validate_provenance_require_complete_true_rejects_incomplete_symbol():
    m = _base_manifest()  # ETH incomplete
    ok, errs = validate_provenance(m, require_complete=True, min_symbols=1)
    assert ok is False
    assert any("ETH" in e for e in errs)


def test_validate_provenance_require_complete_false_accepts_sufficient_complete():
    m = _base_manifest()  # BTC complete >= min_symbols=1
    ok, errs = validate_provenance(m, require_complete=False, min_symbols=1)
    assert ok is True, errs


def test_validate_provenance_require_complete_false_rejects_below_min_symbols():
    m = _base_manifest()
    m["symbols"]["BTC"]["status"] = "error"
    m["symbols"]["BTC"]["coverage"]["complete_for_target_window"] = False
    ok, errs = validate_provenance(m, require_complete=False, min_symbols=1)
    assert ok is False
    assert any("complete symbols" in e for e in errs)


def test_validate_provenance_rejects_target_window_mismatch():
    m = _base_manifest()
    m["target_window"]["start"] = "2025-01-01T00:00:00Z"
    ok, errs = validate_provenance(m, require_complete=False, min_symbols=1)
    assert ok is False
    assert any("start mismatch" in e for e in errs)


def test_validate_provenance_rejects_expected_bars_mismatch():
    m = _base_manifest()
    m["target_window"]["expected_hourly_bars"] = 9999
    ok, errs = validate_provenance(m, require_complete=False, min_symbols=1)
    assert ok is False
    assert any("expected_hourly_bars mismatch" in e for e in errs)


def test_require_verified_provenance_raises_on_missing_manifest(tmp_path):
    missing = tmp_path / "does_not_exist.json"
    with pytest.raises(ProvenanceError):
        require_verified_provenance(missing, require_complete=True, min_symbols=1)


def test_require_verified_provenance_raises_on_invalid_json(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json")
    with pytest.raises(ProvenanceError):
        require_verified_provenance(bad, require_complete=False, min_symbols=1)


def test_require_verified_provenance_raises_when_incomplete_default():
    m = _base_manifest()
    p = Path("/tmp/_prov_gate_bad.json")
    p.write_text(json.dumps(m))
    try:
        with pytest.raises(ProvenanceError):
            require_verified_provenance(p, require_complete=True, min_symbols=1)
    finally:
        p.unlink(missing_ok=True)


def test_expected_hourly_bars_matches_spec_6792():
    assert EXP == 6792
    assert expected_hourly_bars() == 6792
    assert expected_hourly_bars(TARGET_START, TARGET_END) == 6792
    # sanity: 283 days * 24 = 6792
    assert EXP == 283 * 24
