"""Unittest-runnable smoke tests for canonical candle coverage gap report.

Complements pytest-style tests/test_candle_coverage_gap_report.py (tmp_path fixture)
so core guardrails are verifiable in environments without pytest.
Deterministic, synthetic (non-evidence).
"""
from __future__ import annotations

import json
import tempfile
import unittest
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


class TestCandleCoverageGapReportUnittest(unittest.TestCase):
    def test_incomplete_manifest_never_ready(self):
        from scripts.generate_candle_coverage_gap_report import build_gap_report, write_gap_report
        report = build_gap_report(manifest=_incomplete_manifest(), probe_evidence={"probed_at_utc": "2026-11-06T11:13:09Z", "symbols": {"BTC": {"count": 4078, "complete": False}}}, generated_at_utc="2026-11-06T11:14:00Z", archive_scan={"searched_paths": ["/tmp"], "verified_archives_found": []})
        self.assertEqual(report["target_window"]["expected_hourly_bars"], expected_hourly_bars())
        self.assertFalse(report["ready_for_real_campaign"])
        self.assertFalse(report["all_complete"])
        self.assertTrue(report["blocker"]["item_6c_blocked"])
        self.assertTrue(report["target_window_consistent_with_spec"])
        self.assertEqual(report["symbols"]["BTC"]["observed_in_window_bars"], 4082)
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "report.json"
            write_gap_report(out, report)
            loaded = json.loads(out.read_text())
        self.assertTrue(loaded["blocker"]["item_6c_blocked"])

    def test_missing_manifest_blocked(self):
        from scripts.generate_candle_coverage_gap_report import build_gap_report
        report = build_gap_report(manifest=None, probe_evidence=None, generated_at_utc="2026-11-06T11:14:00Z")
        self.assertFalse(report["ready_for_real_campaign"])
        self.assertTrue(report["blocker"]["item_6c_blocked"])

    def test_stale_window_mismatch_blocked(self):
        from scripts.generate_candle_coverage_gap_report import build_gap_report
        exp = expected_hourly_bars(TARGET_START, TARGET_END)
        stale_manifest = {
            "generated_at_utc": "2026-11-06T00:00:00Z",
            "fabricated_data": False,
            "target_window": {"start": "2025-01-01T00:00:00Z", "end": "2025-01-01T03:00:00Z", "expected_hourly_bars": 4},
            "summary": {"all_complete": True, "ready_for_real_campaign": True, "complete_symbols": ["BTC"], "symbols_requested": 1},
            "symbols": {"BTC": {"status": "ok", "coverage": {"expected_hourly_bars": 4, "observed_in_window_bars": 4, "gap_count": 0, "complete_for_target_window": True}}},
        }
        report = build_gap_report(manifest=stale_manifest, probe_evidence=None, generated_at_utc="2026-11-06T11:14:00Z")
        self.assertEqual(report["target_window"], {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": exp})
        self.assertFalse(report["target_window_consistent_with_spec"])
        self.assertFalse(report["ready_for_real_campaign"])
        self.assertFalse(report["all_complete"])
        self.assertTrue(report["blocker"]["item_6c_blocked"])
        self.assertTrue(report["blocker"].get("target_window_mismatch"))


if __name__ == "__main__":
    unittest.main()
