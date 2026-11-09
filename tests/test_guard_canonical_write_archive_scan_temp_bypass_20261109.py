"""Fail-closed: guard_canonical_write must reject temp paths in archive_scan candidate metadata.

2026-11-09 D residual (failing-tests-first). guard_canonical_write scans
manifest/probe archive keys and per-symbol path keys, but did not scan
report.archive_scan.candidate_archives[*] path/metadata strings. A temp
candidate archive path can persist in the canonical report's archive_scan
payload without triggering the temp-source block, allowing a ready report to
carry temp/unverified candidate metadata. The guard must fail-closed.
"""
from __future__ import annotations

from scripts.generate_candle_coverage_gap_report import build_gap_report, guard_canonical_write
from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars

EXP = expected_hourly_bars(TARGET_START, TARGET_END)
CLEAN_ARCHIVE = "research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet"


def _clean_manifest():
    return {
        "schema_version": 1,
        "fabricated_data": False,
        "real_market_data_intended": True,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": EXP},
        "summary": {"all_complete": True, "ready_for_real_campaign": True,
                    "complete_symbols": ["BTC"], "symbols_complete": 1,
                    "synthetic_series_detected": []},
        "source": {"kind": "archive", "input_archive": CLEAN_ARCHIVE},
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


def _archive_scan_with_temp_candidate():
    return {
        "searched_paths": ["research_state/archives"],
        "candidate_archives": [
            {"path": "/tmp/kilo-tmp/probe/fake.parquet", "exists": True, "verified": False,
             "file_size_bytes": 123, "sha256": "deadbeef"},
        ],
        "verified_archives_found": [],
    }


def _archive_scan_clean():
    return {
        "searched_paths": ["research_state/archives"],
        "candidate_archives": [
            {"path": CLEAN_ARCHIVE, "exists": True, "verified": True,
             "file_size_bytes": 123, "sha256": "abc"},
        ],
        "verified_archives_found": [CLEAN_ARCHIVE],
    }


def _report(manifest, archive_scan):
    return build_gap_report(manifest=manifest, probe_evidence=None,
                            archive_scan=archive_scan)


def _assert_blocked(guarded):
    assert guarded["ready_for_real_campaign"] is False, guarded
    assert guarded["blocked"] is True
    assert guarded["blocker"]["item_6c_blocked"] is True
    reason = guarded["blocker"]["reason"].lower()
    assert "temp" in reason or "unverified" in reason or "provenance" in reason, guarded["blocker"]["reason"]


def test_guard_blocks_temp_candidate_archive_path_in_archive_scan():
    m = _clean_manifest()
    guarded = guard_canonical_write(_report(m, _archive_scan_with_temp_candidate()), m)
    _assert_blocked(guarded)


def test_guard_blocks_temp_candidate_archive_path_kilo_tmp_marker():
    m = _clean_manifest()
    scan = {
        "searched_paths": [],
        "candidate_archives": [{"path": "/home/runner/work/_temp/kilo-tmp/x.parquet", "verified": False}],
        "verified_archives_found": [],
    }
    guarded = guard_canonical_write(_report(m, scan), m)
    _assert_blocked(guarded)


def test_guard_allows_clean_archive_scan_candidate_paths():
    m = _clean_manifest()
    guarded = guard_canonical_write(_report(m, _archive_scan_clean()), m)
    assert guarded["ready_for_real_campaign"] is True, guarded
    assert guarded["blocked"] is False


def test_guard_blocks_temp_path_nested_in_candidate_metadata():
    m = _clean_manifest()
    scan = {
        "searched_paths": [],
        "candidate_archives": [{"path": CLEAN_ARCHIVE, "source_path": "/tmp/kilo-tmp/src.json", "verified": False}],
        "verified_archives_found": [],
    }
    guarded = guard_canonical_write(_report(m, scan), m)
    _assert_blocked(guarded)
