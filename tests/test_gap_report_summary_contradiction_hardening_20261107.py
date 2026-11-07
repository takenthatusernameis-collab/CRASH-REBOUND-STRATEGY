"""Campaign item 4: gap report must not trust contradictory manifest summary
booleans over validated symbol facts (fail-closed)."""
from __future__ import annotations

import unittest

from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars
from scripts.generate_candle_coverage_gap_report import build_gap_report


def _manifest(summary_overrides=None, *, symbol_synthetic=False, volume_ok=True):
    exp = expected_hourly_bars(TARGET_START, TARGET_END)
    summary = {
        "all_complete": True,
        "ready_for_real_campaign": True,
        "complete_symbols": ["BTC"],
        "symbols_requested": 1,
    }
    if summary_overrides:
        summary.update(summary_overrides)
    vol = {
        "volume_filter_ok": volume_ok,
        "min_daily_volume_usd_requested": 5_000_000,
        "min_daily_volume_usd_effective": 5_000_000,
        "min_daily_volume_usd": 5_000_000,
        "bars_checked": exp,
        "bars_passing": exp,
    } if volume_ok else {"volume_filter_ok": False, "min_daily_volume_usd": 0}
    return {
        "generated_at_utc": "2026-11-07T00:00:00Z",
        "fabricated_data": False,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": exp},
        "summary": summary,
        "symbols": {
            "BTC": {
                "status": "ok",
                "coverage": {
                    "expected_hourly_bars": exp,
                    "observed_in_window_bars": exp,
                    "gap_count": 0,
                    "complete_for_target_window": True,
                },
                "volume_coverage": vol,
                "synthetic_check": {"is_synthetic": symbol_synthetic, "reason": "x" if symbol_synthetic else "ok"},
            }
        },
    }


class TestGapReportSummaryContradictionHardening(unittest.TestCase):
    def _scan(self):
        return {"searched_paths": [], "verified_archives_found": []}

    def test_synthetic_symbol_overrides_ready_summary(self):
        r = build_gap_report(manifest=_manifest(symbol_synthetic=True), probe_evidence=None, archive_scan=self._scan())
        self.assertFalse(r["ready_for_real_campaign"])
        self.assertTrue(r["blocker"]["item_6c_blocked"])
        self.assertTrue(r.get("manifest_summary_contradiction") or r.get("summary_contradiction"))

    def test_all_complete_summary_contradicting_incomplete_symbol_blocks(self):
        exp = expected_hourly_bars(TARGET_START, TARGET_END)
        m = _manifest()
        m["symbols"]["BTC"]["coverage"]["complete_for_target_window"] = False
        m["symbols"]["BTC"]["coverage"]["observed_in_window_bars"] = exp - 1
        m["symbols"]["BTC"]["coverage"]["gap_count"] = 1
        r = build_gap_report(manifest=m, probe_evidence=None, archive_scan=self._scan())
        self.assertFalse(r["all_complete"])
        self.assertFalse(r["ready_for_real_campaign"])
        self.assertTrue(r["blocker"]["item_6c_blocked"])

    def test_consistent_spec_compliant_summary_still_ready(self):
        r = build_gap_report(manifest=_manifest(), probe_evidence=None, archive_scan=self._scan())
        self.assertTrue(r["ready_for_real_campaign"])
        self.assertFalse(r["blocker"]["item_6c_blocked"])

    def test_missing_summary_fields_fail_closed_when_symbols_incomplete(self):
        # Legacy-ish but contradictory: summary absent/empty must not become ready from nothing.
        exp = expected_hourly_bars(TARGET_START, TARGET_END)
        m = _manifest(summary_overrides={})
        m["summary"] = {}
        m["symbols"]["BTC"]["coverage"]["complete_for_target_window"] = False
        r = build_gap_report(manifest=m, probe_evidence=None, archive_scan=self._scan())
        self.assertFalse(r["ready_for_real_campaign"])
        self.assertTrue(r["blocker"]["item_6c_blocked"])


if __name__ == "__main__":
    unittest.main()
