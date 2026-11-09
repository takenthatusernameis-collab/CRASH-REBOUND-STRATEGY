"""Fail-closed: synthetic_check must explicitly assert is_synthetic=False.

A manifest with synthetic_check present but missing/None is_synthetic is
unverified (not proven clean). build_gap_report and guard_canonical_write
must treat it as not-ready/blocked — never as verified-clean.

Failing-tests-first 2026-11-09.
"""
from __future__ import annotations

import copy

from scripts.generate_candle_coverage_gap_report import (
    build_gap_report,
    guard_canonical_write,
)
from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars

TW = {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": expected_hourly_bars(TARGET_START, TARGET_END)}
EXP = TW["expected_hourly_bars"]


def _base(archive="/verified/data/archive.parquet"):
    return {
        "generated_at_utc": "2026-11-09T00:00:00Z",
        "fabricated_data": False,
        "target_window": TW,
        "source": {"kind": "archive", "input_archive": archive},
        "summary": {
            "all_complete": True, "ready_for_real_campaign": True,
            "complete_symbols": ["BTC"], "complete_symbol_count": 1,
            "synthetic_series_detected": [],
        },
        "symbols": {
            "BTC": {
                "status": "ok",
                "coverage": {
                    "expected_hourly_bars": EXP,
                    "observed_in_window_bars": EXP,
                    "complete_for_target_window": True,
                    "gap_count": 0,
                    "first_timestamp_utc": TARGET_START,
                    "last_timestamp_utc": TARGET_END,
                },
                "synthetic_check": None,  # overridden
                "volume_floor_24h_usd": 10_000_000,
            }
        },
    }


def _assert_blocked(report):
    assert report["ready_for_real_campaign"] is False
    assert report["blocked"] is True
    assert report["item_6c_blocked"] is True


def test_build_gap_report_blocks_when_is_synthetic_key_missing():
    m = _base()
    m["symbols"]["BTC"]["synthetic_check"] = {"unique_close_values": 5000}
    r = build_gap_report(manifest=m, probe_evidence=None, generated_at_utc="2026-11-09T00:01:00Z")
    _assert_blocked(r)


def test_build_gap_report_blocks_when_is_synthetic_is_none():
    m = _base()
    m["symbols"]["BTC"]["synthetic_check"] = {"is_synthetic": None}
    r = build_gap_report(manifest=m, probe_evidence=None, generated_at_utc="2026-11-09T00:01:00Z")
    _assert_blocked(r)


def test_guard_canonical_write_blocks_when_is_synthetic_key_missing():
    m = _base()
    m["symbols"]["BTC"]["synthetic_check"] = {"unique_close_values": 5000}
    # Simulate a report that (incorrectly) slipped through as ready
    r = {
        "ready_for_real_campaign": True, "all_complete": True, "blocked": False,
        "item_6c_blocked": False,
        "blocker": {"item_6c_blocked": False, "reason": "ok"},
        "probe_evidence": None,
    }
    g = guard_canonical_write(dict(r), m)
    _assert_blocked(g)


def test_guard_canonical_write_blocks_when_is_synthetic_is_none():
    m = _base()
    m["symbols"]["BTC"]["synthetic_check"] = {"is_synthetic": None}
    r = {
        "ready_for_real_campaign": True, "all_complete": True, "blocked": False,
        "item_6c_blocked": False,
        "blocker": {"item_6c_blocked": False, "reason": "ok"},
        "probe_evidence": None,
    }
    g = guard_canonical_write(dict(r), m)
    _assert_blocked(g)


def test_explicit_is_synthetic_false_still_allows_verified_clean_ready():
    m = _base()
    m["symbols"]["BTC"]["synthetic_check"] = {"is_synthetic": False, "unique_close_values": 5000}
    r = build_gap_report(manifest=m, probe_evidence=None, generated_at_utc="2026-11-09T00:01:00Z")
    assert r["ready_for_real_campaign"] is True
    assert r["blocked"] is False
    g = guard_canonical_write(copy.deepcopy(r), m)
    assert g["ready_for_real_campaign"] is True
    assert g["blocked"] is False
