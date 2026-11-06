"""Track-4 hardening: canonical candle coverage gap report generation.

Deterministic, synthetic (non-evidence). Failing-test-first target.
Report must be correct for the 283d target window, include blocker status,
per-symbol coverage, and never claim readiness when incomplete.
"""
from __future__ import annotations

import json
from pathlib import Path

from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars


def _incomplete_manifest():
    exp = expected_hourly_bars(TARGET_START, TARGET_END)
    return {
        "generated_at_utc": "2026-11-06T05:35:00Z",
        "fabricated_data": False,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": exp},
        "summary": {"all_complete": False, "ready_for_real_campaign": False, "complete_symbols": [], "symbols_requested": 2},
        "symbols": {
            "BTC": {"status": "incomplete", "coverage": {"expected_hourly_bars": exp, "observed_in_window_bars": 4082, "gap_count": 0, "complete_for_target_window": False, "first_timestamp": "2026-04-11T22:00:00Z", "last_timestamp": "2026-09-28T23:00:00Z"}},
            "ETH": {"status": "incomplete", "coverage": {"expected_hourly_bars": exp, "observed_in_window_bars": 4082, "gap_count": 0, "complete_for_target_window": False, "first_timestamp": "2026-04-11T22:00:00Z", "last_timestamp": "2026-09-28T23:00:00Z"}},
        },
    }


def test_generate_gap_report_marks_blocked_and_includes_evidence(tmp_path):
    from scripts.generate_candle_coverage_gap_report import build_gap_report, write_gap_report
    manifest = _incomplete_manifest()
    probe = [{"symbol": "BTC", "count": 4082, "first_t": 1775944800000, "last_t": 1790636400000, "complete": False}]
    report = build_gap_report(manifest=manifest, probe_evidence=probe, generated_at_utc="2026-11-06T05:41:00Z", archive_scan={"searched_paths": ["/tmp"], "verified_archives_found": []})
    assert report["target_window"]["expected_hourly_bars"] == expected_hourly_bars()
    assert report["ready_for_real_campaign"] is False
    assert report["all_complete"] is False
    assert report["blocker"]["item_6c_blocked"] is True
    assert "BTC" in report["symbols"] and report["symbols"]["BTC"]["observed_in_window_bars"] == 4082
    assert report["probe_evidence"] == probe
    assert report["archive_scan"]["verified_archives_found"] == []
    out = tmp_path / "report.json"
    write_gap_report(out, report)
    loaded = json.loads(out.read_text())
    assert loaded["blocker"]["item_6c_blocked"] is True


def test_generate_gap_report_not_ready_when_manifest_missing(tmp_path):
    from scripts.generate_candle_coverage_gap_report import build_gap_report
    report = build_gap_report(manifest=None, probe_evidence=None, generated_at_utc="2026-11-06T05:41:00Z")
    assert report["ready_for_real_campaign"] is False
    assert report["blocker"]["item_6c_blocked"] is True


def test_gap_report_flags_stale_target_window_mismatch(tmp_path):
    from scripts.generate_candle_coverage_gap_report import build_gap_report, write_gap_report
    exp = expected_hourly_bars(TARGET_START, TARGET_END)
    # Simulates the stale wrong-window report that was previously on disk.
    stale_manifest = {
        "generated_at_utc": "2026-11-06T00:00:00Z",
        "fabricated_data": False,
        "target_window": {"start": "2025-01-01T00:00:00Z", "end": "2025-01-01T03:00:00Z", "expected_hourly_bars": 4},
        "summary": {"all_complete": False, "ready_for_real_campaign": False, "complete_symbols": [], "symbols_requested": 1},
        "symbols": {
            "BTC": {"status": "ok", "coverage": {"expected_hourly_bars": 4, "observed_in_window_bars": 4, "gap_count": 0, "complete_for_target_window": True}}
        },
    }
    report = build_gap_report(manifest=stale_manifest, probe_evidence=None, generated_at_utc="2026-11-06T05:41:00Z")
    assert report["target_window"] == {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": exp}
    assert report["target_window"] != stale_manifest["target_window"]
    assert report["target_window_consistent_with_spec"] is False
    assert report["ready_for_real_campaign"] is False
    assert report["all_complete"] is False
    assert report["blocker"]["item_6c_blocked"] is True
    assert report["blocker"].get("target_window_mismatch") is True
    out = tmp_path / "report.json"
    write_gap_report(out, report)
    loaded = json.loads(out.read_text())
    assert loaded["target_window_consistent_with_spec"] is False
    assert loaded["blocker"]["target_window_mismatch"] is True
import json
from pathlib import Path
from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars

def test_gap_report_includes_volume_coverage_evidence(tmp_path):
    from scripts.generate_candle_coverage_gap_report import build_gap_report
    exp = expected_hourly_bars(TARGET_START, TARGET_END)
    manifest = {
        "generated_at_utc": "2026-11-06T05:35:00Z",
        "fabricated_data": False,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": exp},
        "summary": {"all_complete": False, "ready_for_real_campaign": False, "complete_symbols": [], "symbols_requested": 1},
        "symbols": {
            "BTC": {"status": "incomplete", "coverage": {"expected_hourly_bars": exp, "observed_in_window_bars": 4082, "gap_count": 0, "complete_for_target_window": False},
                    "volume_coverage": {"min_daily_volume_usd": 5000000, "observed_min_24h_usd_volume": 42891961.89, "bars_checked": 4082, "bars_passing": 4082, "volume_filter_ok": True}},
        },
    }
    report = build_gap_report(manifest=manifest, probe_evidence=None, generated_at_utc="2026-11-06T08:30:00Z")
    vc = report["symbols"]["BTC"]["volume_coverage"]
    assert vc["min_daily_volume_usd"] == 5000000
    assert vc["volume_filter_ok"] is True
    assert vc["observed_min_24h_usd_volume"] == 42891961.89
    assert vc["bars_passing"] == 4082
