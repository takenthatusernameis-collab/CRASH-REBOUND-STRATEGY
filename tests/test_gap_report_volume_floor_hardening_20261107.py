"""Fail-closed hardening: gap report must not treat sub-$5M/misaligned volume
coverage as spec-compliant readiness evidence (campaign item 3/4)."""
from __future__ import annotations

import unittest

from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars
from scripts.generate_candle_coverage_gap_report import build_gap_report


def _complete_manifest(*, vol):
    exp = expected_hourly_bars(TARGET_START, TARGET_END)
    return {
        "generated_at_utc": "2026-11-07T00:00:00Z",
        "fabricated_data": False,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": exp},
        "summary": {"all_complete": True, "ready_for_real_campaign": True, "complete_symbols": ["BTC"], "symbols_requested": 1},
        "symbols": {"BTC": {"status": "ok", "coverage": {
            "expected_hourly_bars": exp, "observed_in_window_bars": exp,
            "gap_count": 0, "complete_for_target_window": True,
        }, "volume_coverage": vol}},
    }


class TestGapReportVolumeFloorHardening(unittest.TestCase):
    def _scan(self):
        return {"searched_paths": [], "verified_archives_found": []}

    def test_sub_spec_numeric_volume_blocks_ready(self):
        m = _complete_manifest(vol={"volume_filter_ok": True, "min_daily_volume_usd": 1_000_000, "bars_checked": 6792, "bars_passing": 6792})
        r = build_gap_report(manifest=m, probe_evidence=None, archive_scan=self._scan())
        self.assertFalse(r["ready_for_real_campaign"])
        self.assertTrue(r["blocker"]["item_6c_blocked"])
        self.assertTrue(r.get("volume_floor_compliant") is False)

    def test_missing_volume_coverage_blocks_ready(self):
        m = _complete_manifest(vol=None)
        m["symbols"]["BTC"]["volume_coverage"] = None
        r = build_gap_report(manifest=m, probe_evidence=None, archive_scan=self._scan())
        self.assertFalse(r["ready_for_real_campaign"])
        self.assertTrue(r["blocker"]["item_6c_blocked"])

    def test_requested_effective_mismatch_blocks_ready(self):
        m = _complete_manifest(vol={
            "volume_filter_ok": True,
            "min_daily_volume_usd_requested": 0,
            "min_daily_volume_usd_effective": 5_000_000,
            "min_daily_volume_usd": 5_000_000,
            "spec_floor_enforced": True,
            "bars_checked": 6792, "bars_passing": 6792,
        })
        r = build_gap_report(manifest=m, probe_evidence=None, archive_scan=self._scan())
        # effective meets spec, but requested<floor means manifest was produced by
        # non-compliant request intent; report must surface this as not spec-floor-
        # compliant evidence for "ready" unless explicitly understood. Fail closed.
        self.assertFalse(r["ready_for_real_campaign"])
        self.assertTrue(r["blocker"]["item_6c_blocked"])

    def test_effective_below_floor_blocks_ready(self):
        m = _complete_manifest(vol={
            "volume_filter_ok": True,
            "min_daily_volume_usd_requested": 1_000_000,
            "min_daily_volume_usd_effective": 1_000_000,
            "min_daily_volume_usd": 1_000_000,
            "bars_checked": 6792, "bars_passing": 6792,
        })
        r = build_gap_report(manifest=m, probe_evidence=None, archive_scan=self._scan())
        self.assertFalse(r["ready_for_real_campaign"])
        self.assertTrue(r["blocker"]["item_6c_blocked"])

    def test_spec_compliant_volume_allows_ready_when_manifest_ready(self):
        m = _complete_manifest(vol={
            "volume_filter_ok": True,
            "min_daily_volume_usd_requested": 5_000_000,
            "min_daily_volume_usd_effective": 5_000_000,
            "min_daily_volume_usd": 5_000_000,
            "spec_floor_enforced": False,
            "bars_checked": 6792, "bars_passing": 6792,
        })
        r = build_gap_report(manifest=m, probe_evidence=None, archive_scan=self._scan())
        self.assertTrue(r["ready_for_real_campaign"])
        self.assertFalse(r["blocker"]["item_6c_blocked"])
        self.assertTrue(r.get("volume_floor_compliant") is True)


if __name__ == "__main__":
    unittest.main()
