"""Fail-closed: guard_canonical_write must reject temp-sourced archives at manifest top-level.

2026-11-09 D-bypass hunt (failing-tests-first). guard_canonical_write scans
probe_evidence.source and manifest.source for temp paths (input_archive /
input_archives), but must also scan manifest top-level input_archive /
input_archives and probe_evidence top-level archive keys. A temp archive path
placed outside the .source nesting must not bypass the canonical-write guard.
"""
from __future__ import annotations

import copy

from scripts.generate_candle_coverage_gap_report import (
    build_gap_report,
    guard_canonical_write,
)
from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars

EXP = expected_hourly_bars(TARGET_START, TARGET_END)


def _clean_symbol_block():
    return {
        "status": "ok",
        "synthetic_check": {"is_synthetic": False},
        "coverage": {
            "expected_hourly_bars": EXP,
            "observed_in_window_bars": EXP,
            "complete_for_target_window": True,
            "gap_count": 0,
        },
    }


def _base_manifest():
    return {
        "generated_at_utc": "2026-11-09T00:00:00Z",
        "fabricated_data": False,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": EXP},
        "source": {"kind": "archive", "input_archive": "/mnt/data/verified/clean.parquet"},
        "summary": {"all_complete": True, "ready_for_real_campaign": True,
                    "complete_symbols": ["BTC", "ETH"], "symbols_requested": 2},
        "symbols": {"BTC": _clean_symbol_block(), "ETH": _clean_symbol_block()},
    }


def _assert_blocked(report):
    assert report["ready_for_real_campaign"] is False
    assert report["blocked"] is True
    assert report["item_6c_blocked"] is True
    assert "provenance not verified-clean" in report["blocker"]["reason"]


def test_guard_blocks_temp_in_manifest_toplevel_input_archive():
    m = _base_manifest()
    m["input_archive"] = "/tmp/fake.parquet"
    report = build_gap_report(manifest=m, probe_evidence=None, generated_at_utc="2026-11-09T00:01:00Z")
    assert report["ready_for_real_campaign"] is True
    guarded = guard_canonical_write(dict(report), m)
    _assert_blocked(guarded)


def test_guard_blocks_temp_in_manifest_toplevel_input_archives():
    m = _base_manifest()
    m["input_archives"] = ["/mnt/clean/a.parquet", "/tmp/fake.parquet"]
    report = build_gap_report(manifest=m, probe_evidence=None, generated_at_utc="2026-11-09T00:01:00Z")
    guarded = guard_canonical_write(dict(report), m)
    _assert_blocked(guarded)


def test_guard_blocks_temp_in_probe_evidence_toplevel_input_archive():
    m = _base_manifest()
    probe = {"input_archive": "/home/runner/work/_temp/kilo-tmp/x.parquet",
             "source": {"input_archive": "/mnt/clean/a.parquet"}}
    report = build_gap_report(manifest=m, probe_evidence=probe, generated_at_utc="2026-11-09T00:01:00Z")
    assert report["ready_for_real_campaign"] is True
    guarded = guard_canonical_write(dict(report), m)
    _assert_blocked(guarded)


def test_guard_blocks_temp_in_probe_evidence_toplevel_input_archives():
    m = _base_manifest()
    probe = {"input_archives": ["/tmp/a.parquet"],
             "source": {"input_archive": "/mnt/clean/a.parquet"}}
    report = build_gap_report(manifest=m, probe_evidence=probe, generated_at_utc="2026-11-09T00:01:00Z")
    guarded = guard_canonical_write(dict(report), m)
    _assert_blocked(guarded)


def test_guard_allows_clean_toplevel_archive_keys():
    m = _base_manifest()
    m["input_archive"] = "/mnt/data/verified/clean.parquet"
    m["input_archives"] = ["/mnt/data/verified/a.parquet"]
    probe = {"input_archive": "/mnt/data/verified/b.parquet"}
    report = build_gap_report(manifest=m, probe_evidence=probe, generated_at_utc="2026-11-09T00:01:00Z")
    guarded = guard_canonical_write(dict(report), m)
    assert guarded["ready_for_real_campaign"] is True
    assert guarded["blocked"] is False
