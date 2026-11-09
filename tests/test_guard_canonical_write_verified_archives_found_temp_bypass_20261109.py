"""Fail-closed: guard_canonical_write must reject temp paths in archive_scan.verified_archives_found.

2026-11-09 D residual (failing-tests-first). guard_canonical_write scans
candidate_archives[*] path/metadata strings for temp markers, but it does NOT
scan archive_scan.verified_archives_found (a list of archive path strings) nor
archive_scan.searched_paths. A precomputed archive_scan whose
verified_archives_found list carries a temp scratch path (e.g.
/tmp/kilo-tmp/... or _temp/kilo-tmp/...) passes the guard as clean and the
canonical report is published ready_for_real_campaign=true citing a
temp-sourced "verified archive". That is a provenance bypass: downstream
consumers (fetch main(), run_real_campaign provenance, gap-report readers) read
verified_archives_found as trusted verified-archive evidence.

Repro (confirmed before fix): a clean manifest + precomputed archive_scan with
verified_archives_found=['/tmp/kilo-tmp/fake_verified.parquet'] yields
ready_for_real_campaign=True, blocked=False.

Fix: guard_canonical_write must temp-scan verified_archives_found AND
searched_paths; any temp marker blocks the canonical write.
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


def _report(manifest, archive_scan):
    return build_gap_report(manifest=manifest, probe_evidence=None,
                            archive_scan=archive_scan)


def _assert_blocked(guarded):
    assert guarded["ready_for_real_campaign"] is False, guarded
    assert guarded["blocked"] is True
    assert guarded["blocker"]["item_6c_blocked"] is True
    reason = guarded["blocker"]["reason"].lower()
    assert "temp" in reason or "unverified" in reason or "provenance" in reason, guarded["blocker"]["reason"]


def test_guard_blocks_temp_path_in_verified_archives_found():
    m = _clean_manifest()
    scan = {
        "searched_paths": ["research_state/archives"],
        "candidate_archives": [],
        "verified_archives_found": ["/tmp/kilo-tmp/fake_verified.parquet"],
    }
    guarded = guard_canonical_write(_report(m, scan), m)
    _assert_blocked(guarded)


def test_guard_blocks_temp_path_in_verified_archives_found_kilo_tmp_marker():
    m = _clean_manifest()
    scan = {
        "searched_paths": [],
        "candidate_archives": [],
        "verified_archives_found": ["/home/runner/work/_temp/kilo-tmp/x.parquet"],
    }
    guarded = guard_canonical_write(_report(m, scan), m)
    _assert_blocked(guarded)


def test_guard_blocks_temp_path_in_searched_paths():
    m = _clean_manifest()
    scan = {
        "searched_paths": ["/tmp/kilo-tmp/scan_root"],
        "candidate_archives": [],
        "verified_archives_found": [],
    }
    guarded = guard_canonical_write(_report(m, scan), m)
    _assert_blocked(guarded)


def test_guard_allows_clean_verified_archives_found():
    m = _clean_manifest()
    scan = {
        "searched_paths": ["research_state/archives"],
        "candidate_archives": [],
        "verified_archives_found": [CLEAN_ARCHIVE],
    }
    guarded = guard_canonical_write(_report(m, scan), m)
    assert guarded["ready_for_real_campaign"] is True, guarded
    assert guarded["blocked"] is False


def test_guard_blocks_mixed_clean_and_temp_verified_archives_found():
    m = _clean_manifest()
    scan = {
        "searched_paths": [],
        "candidate_archives": [],
        "verified_archives_found": [CLEAN_ARCHIVE, "/tmp/kilo-tmp/bad.parquet"],
    }
    guarded = guard_canonical_write(_report(m, scan), m)
    _assert_blocked(guarded)