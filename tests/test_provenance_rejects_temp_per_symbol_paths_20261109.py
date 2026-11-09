"""Fail-closed: provenance consumers must reject temp/unverified per-symbol paths.

2026-11-09 D provenance-consumer bypass (failing-tests-first). guard_canonical_write
blocks canonical gap-report writes for temp per-symbol provenance, but
src/data/provenance.py consumers (validate_provenance, complete_symbol_subset,
require_verified_provenance/_complete_symbol_subset_safe) accepted temp
cache_path/source_path/source_paths/nested source/provenance metadata as
verified-complete evidence. A consumer accepting temp per-symbol paths can treat
unverified local scratch data as real campaign evidence.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.data.provenance import (
    TARGET_START,
    TARGET_END,
    complete_symbol_subset,
    expected_hourly_bars,
    require_verified_provenance,
    validate_provenance,
)

EXP = expected_hourly_bars(TARGET_START, TARGET_END)
TEMP = "/home/runner/work/_temp/kilo-tmp/fake.parquet"
CLEAN_REPO = "research_state/cache/hyperliquid/candles/BTC.json"


def _sym(extra=None):
    d = {
        "status": "ok",
        "synthetic_check": {"is_synthetic": False},
        "coverage": {
            "expected_hourly_bars": EXP,
            "observed_in_window_bars": EXP,
            "complete_for_target_window": True,
            "gap_count": 0,
        },
    }
    if extra:
        d.update(extra)
    return d


def _manifest(btc_extra=None, eth_extra=None):
    return {
        "fabricated_data": False,
        "real_market_data_intended": True,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": EXP},
        "symbols": {"BTC": _sym(btc_extra), "ETH": _sym(eth_extra)},
    }


def _has_temp_error(errs):
    joined = "\n".join(errs).lower()
    return "temp" in joined or "unverified" in joined or "kilo-tmp" in joined or "/tmp" in joined


def test_validate_provenance_rejects_temp_cache_path():
    ok, errs = validate_provenance(_manifest(btc_extra={"cache_path": "/tmp/fake/BTC.json"}))
    assert not ok
    assert _has_temp_error(errs), errs


def test_validate_provenance_rejects_temp_source_path():
    ok, errs = validate_provenance(_manifest(btc_extra={"source_path": TEMP}))
    assert not ok
    assert _has_temp_error(errs), errs


def test_validate_provenance_rejects_temp_source_paths_list():
    ok, errs = validate_provenance(_manifest(eth_extra={"source_paths": [CLEAN_REPO, "/tmp/other.parquet"]}))
    assert not ok
    assert _has_temp_error(errs), errs


def test_validate_provenance_rejects_temp_nested_source_archive():
    ok, errs = validate_provenance(_manifest(btc_extra={"source": {"input_archive": TEMP}}))
    assert not ok
    assert _has_temp_error(errs), errs


def test_validate_provenance_rejects_temp_nested_provenance_input_archives():
    ok, errs = validate_provenance(_manifest(btc_extra={"provenance": {"input_archives": [TEMP]}}))
    assert not ok
    assert _has_temp_error(errs), errs


def test_complete_symbol_subset_excludes_temp_per_symbol_paths():
    m = _manifest(btc_extra={"cache_path": "/tmp/fake/BTC.json"})
    out = complete_symbol_subset(m)
    assert "BTC" not in out["symbols"]
    assert out["summary"]["complete_symbols_subset"] == ["ETH"]


def test_require_verified_provenance_rejects_temp_per_symbol_paths(tmp_path: Path):
    p = tmp_path / "prov.json"
    p.write_text(json.dumps(_manifest(btc_extra={"cache_path": TEMP})))
    with pytest.raises(Exception) as ei:
        require_verified_provenance(p)
    assert _has_temp_error([str(ei.value)]), ei.value


def test_validate_provenance_allows_clean_repo_relative_paths():
    m = _manifest(
        btc_extra={"cache_path": CLEAN_REPO, "source_path": "/mnt/data/verified/btc.parquet",
                   "source": {"input_archive": "/mnt/data/verified/archive.parquet"}},
        eth_extra={"source_paths": ["/mnt/data/verified/eth.parquet"],
                   "provenance": {"input_archives": ["/mnt/data/verified/archive.parquet"]}},
    )
    ok, errs = validate_provenance(m)
    assert ok, errs


def test_complete_symbol_subset_keeps_clean_paths():
    m = _manifest(
        btc_extra={"cache_path": CLEAN_REPO, "source": {"input_archive": "/mnt/data/verified/archive.parquet"}},
    )
    out = complete_symbol_subset(m)
    assert set(out["symbols"].keys()) == {"BTC", "ETH"}
