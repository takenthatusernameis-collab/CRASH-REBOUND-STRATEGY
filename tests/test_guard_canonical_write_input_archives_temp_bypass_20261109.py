"""Fail-closed: guard_canonical_write must reject temp-sourced input_archives (plural).

2026-11-09 D-bypass hunt (failing-tests-first). The multi-archive merge path in
scripts/fetch_hyperliquid_candles.py emits a manifest whose source carries both
`input_archive` (singular, may be clean) and `input_archives` (plural list, the
actual merged sources). guard_canonical_write previously inspected ONLY
input_archive for temp/unverified provenance, so a manifest whose singular
input_archive was clean but whose plural input_archives pointed at /tmp or
_temp/kilo-tmp passed through as ready_for_real_campaign=true — a temp-source
optimism bypass of the canonical write guard.

The guard must reject ANY temp-sourced archive path across both keys.
"""
from __future__ import annotations

import copy

from scripts.generate_candle_coverage_gap_report import (
    build_gap_report,
    guard_canonical_write,
)
from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars

EXP = expected_hourly_bars(TARGET_START, TARGET_END)


def _clean_symbol_block(sym):
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


def _manifest_with(archive=None, archives=None):
    src = {"kind": "archive"}
    if archive is not None:
        src["input_archive"] = archive
    if archives is not None:
        src["input_archives"] = archives
    return {
        "generated_at_utc": "2026-11-09T00:00:00Z",
        "fabricated_data": False,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": EXP},
        "source": src,
        "summary": {"all_complete": True, "ready_for_real_campaign": True,
                    "complete_symbols": ["BTC", "ETH"], "symbols_requested": 2},
        "symbols": {"BTC": _clean_symbol_block("BTC"), "ETH": _clean_symbol_block("ETH")},
    }


def _assert_blocked(report):
    assert report["ready_for_real_campaign"] is False
    assert report["blocked"] is True
    assert report["item_6c_blocked"] is True
    assert "provenance not verified-clean" in report["blocker"]["reason"]


def test_guard_blocks_when_input_archives_contains_temp_kilo_tmp():
    m = _manifest_with(
        archive="/mnt/data/verified/archive.parquet",
        archives=["/home/runner/work/_temp/kilo-tmp/tmp8tn6l77l/archive.parquet",
                  "/mnt/data/verified/other.parquet"],
    )
    report = build_gap_report(manifest=m, probe_evidence=None, generated_at_utc="2026-11-09T00:01:00Z")
    assert report["ready_for_real_campaign"] is True, "build_gap_report alone marks clean coverage ready"
    guarded = guard_canonical_write(dict(report), m)
    _assert_blocked(guarded)


def test_guard_blocks_when_input_archives_contains_tmp_prefix():
    m = _manifest_with(
        archive="/mnt/data/verified/archive.parquet",
        archives=["/tmp/fake1/archive.parquet", "/tmp/fake2/archive.parquet"],
    )
    report = build_gap_report(manifest=m, probe_evidence=None, generated_at_utc="2026-11-09T00:01:00Z")
    guarded = guard_canonical_write(dict(report), m)
    _assert_blocked(guarded)


def test_guard_blocks_when_only_input_archives_is_temp_and_singular_is_clean():
    # The drift vector: singular input_archive looks clean, plural list is the
    # actual (temp) merged source. Must still block.
    m = _manifest_with(
        archive="/mnt/data/verified/archive.parquet",
        archives=["/tmp/fake1/archive.parquet"],
    )
    report = build_gap_report(manifest=m, probe_evidence=None, generated_at_utc="2026-11-09T00:01:00Z")
    guarded = guard_canonical_write(dict(report), m)
    _assert_blocked(guarded)


def test_guard_allows_when_all_input_archives_are_clean():
    m = _manifest_with(
        archive="/mnt/data/verified/archive.parquet",
        archives=["/mnt/data/verified/a.parquet", "/mnt/data/verified/b.parquet"],
    )
    report = build_gap_report(manifest=m, probe_evidence=None, generated_at_utc="2026-11-09T00:01:00Z")
    guarded = guard_canonical_write(dict(report), m)
    assert guarded["ready_for_real_campaign"] is True
    assert guarded["blocked"] is False


def test_guard_allows_when_no_source_keys_present():
    # No source provenance at all: not temp-sourced, so the guard must not
    # fabricate a temp block; build_gap_report already refused (no manifest
    # symbols would be clean-ready here). With clean symbols and no source, the
    # guard must pass through unchanged (ready stays as build_gap_report set it).
    m = _manifest_with()
    report = build_gap_report(manifest=m, probe_evidence=None, generated_at_utc="2026-11-09T00:01:00Z")
    assert report["ready_for_real_campaign"] is True
    guarded = guard_canonical_write(dict(report), m)
    assert guarded["ready_for_real_campaign"] is True
    assert guarded["blocked"] is False