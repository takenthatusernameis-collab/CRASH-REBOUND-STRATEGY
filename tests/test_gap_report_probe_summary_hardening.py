"""Unittest hardening: probe evidence must never mark ITEM 6c ready.

Track-4/6c gate guardrail. Deterministic synthetic (non-evidence).
"""
from __future__ import annotations

import unittest

from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars


class TestGapReportProbeSummaryHardening(unittest.TestCase):
    def test_incomplete_probe_forces_blocked_even_if_manifest_missing(self):
        from scripts.generate_candle_coverage_gap_report import build_gap_report
        probe = {"probed_at_utc": "2026-11-06T13:13:13Z", "symbols": {
            "BTC": {"count": 4078, "expected": 6792, "complete": False},
            "ETH": {"count": 4078, "expected": 6792, "complete": False},
        }}
        report = build_gap_report(manifest=None, probe_evidence=probe, generated_at_utc="2026-11-06T13:15:00Z")
        self.assertFalse(report["ready_for_real_campaign"])
        self.assertTrue(report["blocker"]["item_6c_blocked"])
        self.assertEqual(report["probe_summary"]["symbols_probed"], 2)
        self.assertFalse(report["probe_summary"]["all_complete"])

    def test_incomplete_probe_keeps_blocked_with_manifest(self):
        from scripts.generate_candle_coverage_gap_report import build_gap_report
        exp = expected_hourly_bars(TARGET_START, TARGET_END)
        manifest = {
            "generated_at_utc": "2026-11-06T00:00:00Z", "fabricated_data": False,
            "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": exp},
            "summary": {"all_complete": False, "ready_for_real_campaign": False, "complete_symbols": [], "symbols_requested": 2},
            "symbols": {"BTC": {"status": "incomplete", "coverage": {"expected_hourly_bars": exp, "observed_in_window_bars": 4082, "gap_count": 0, "complete_for_target_window": False}}},
        }
        probe = {"symbols": {"BTC": {"count": 4078, "expected": 6792, "complete": False}, "SOL": {"count": 4078, "expected": 6792, "complete": False}}}
        report = build_gap_report(manifest=manifest, probe_evidence=probe, generated_at_utc="2026-11-06T13:15:00Z")
        self.assertFalse(report["ready_for_real_campaign"])
        self.assertTrue(report["blocker"]["item_6c_blocked"])
        self.assertEqual(report["probe_summary"]["symbols_probed"], 2)

    def test_no_probe_no_probe_summary_crash(self):
        from scripts.generate_candle_coverage_gap_report import build_gap_report
        report = build_gap_report(manifest=None, probe_evidence=None, generated_at_utc="2026-11-06T13:15:00Z")
        self.assertNotIn("probe_summary", report)


if __name__ == "__main__":
    unittest.main()
