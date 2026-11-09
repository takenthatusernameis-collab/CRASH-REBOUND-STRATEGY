"""D-bypass hunt (2026-11-09): guard_canonical_write must reject temp
per-symbol provenance paths hiding inside probe_evidence symbol entries.

`guard_canonical_write()` scans probe_evidence.source / manifest.source /
top-level manifest for archive keys (input_archive(s), archive_path(s)) and
scans manifest symbols for per-symbol cache/source/archive paths. What it did
NOT scan: per-symbol path keys (cache_path, source_path, archive_path,
file_path, input_archive) nested under probe_evidence["symbols"][SYM]. A probe
whose symbol entries carry temp cache_path/source_path metadata could coexist
with a clean manifest and still pass the guard as ready_for_real_campaign.

Repro: a clean manifest (all_complete, clean synthetic_check, spec volume
floor) plus a probe_evidence dict whose BTC entry declares
cache_path="/tmp/kilo-tmp/BTC.json" was accepted as ready. Failing-tests-first
lock: the guard must fail-closed on probe symbol temp paths.
"""
import json
from pathlib import Path

import pytest

from scripts.generate_candle_coverage_gap_report import build_gap_report, guard_canonical_write
from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars


EXP = expected_hourly_bars(TARGET_START, TARGET_END)


def _clean_manifest():
    return {
        "schema_version": 1,
        "fabricated_data": False,
        "real_market_data_intended": True,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": EXP},
        "summary": {"all_complete": True, "ready_for_real_campaign": True,
                    "complete_symbols": ["BTC"], "symbols_complete": 1,
                    "synthetic_series_detected": []},
        "source": {"kind": "archive", "input_archive": "research_state/archives/verified.tar.gz"},
        "request_params": {"min_daily_volume_usd_requested": 5_000_000.0,
                           "min_daily_volume_usd_effective": 5_000_000.0},
        "symbols": {
            "BTC": {
                "status": "ok",
                "cache_path": "research_state/cache/hyperliquid/candles/BTC.json",
                "synthetic_check": {"is_synthetic": False, "reason": "varied_series_ok"},
                "coverage": {"expected_hourly_bars": EXP, "observed_in_window_bars": EXP,
                             "gap_count": 0, "complete_for_target_window": True,
                             "first_timestamp_ms": 0, "last_timestamp_ms": 0},
                "volume_coverage": {"volume_filter_ok": True, "min_daily_volume_usd": 5_000_000.0,
                                    "observed_min_24h_usd_volume": 10_000_000.0,
                                    "bars_checked": EXP, "bars_passing": EXP},
            }
        },
    }


def _probe_with_temp_symbol_path():
    return {
        "generated_at_utc": "2026-11-09T00:00:00Z",
        "symbols": {
            "BTC": {
                "count": EXP, "expected": EXP, "complete": True,
                "cache_path": "/tmp/kilo-tmp/probe/BTC.json",
                "source_path": "_temp/kilo-tmp/probe/src.json",
            }
        },
    }


def _probe_clean():
    return {
        "generated_at_utc": "2026-11-09T00:00:00Z",
        "symbols": {
            "BTC": {"count": EXP, "expected": EXP, "complete": True,
                    "cache_path": "research_state/cache/hyperliquid/candles/BTC.json"}
        },
    }


def _report(manifest, probe):
    return build_gap_report(manifest=manifest, probe_evidence=probe,
                            archive_scan={"searched_paths": [],
                                          "candidate_archives": [],
                                          "verified_archives_found": []})


def test_guard_blocks_when_probe_symbol_carries_temp_cache_path():
    r = _report(_clean_manifest(), _probe_with_temp_symbol_path())
    guarded = guard_canonical_write(r, _clean_manifest())
    assert guarded["ready_for_real_campaign"] is False, guarded
    assert guarded["blocked"] is True
    assert guarded["blocker"]["item_6c_blocked"] is True
    reason = guarded["blocker"]["reason"].lower()
    assert "temp" in reason or "unverified" in reason, guarded["blocker"]["reason"]


def test_guard_allows_clean_probe_symbol_paths():
    r = _report(_clean_manifest(), _probe_clean())
    guarded = guard_canonical_write(r, _clean_manifest())
    assert guarded["ready_for_real_campaign"] is True, guarded
    assert guarded["blocked"] is False


def test_guard_blocks_when_probe_symbol_carries_temp_nested_source():
    probe = {
        "symbols": {
            "BTC": {"count": EXP, "expected": EXP, "complete": True,
                    "source": {"input_archive": "/tmp/kilo-tmp/probe/btc.tar.gz"}}
        }
    }
    r = _report(_clean_manifest(), probe)
    guarded = guard_canonical_write(r, _clean_manifest())
    assert guarded["ready_for_real_campaign"] is False, guarded
    assert guarded["blocked"] is True