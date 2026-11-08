"""Campaign item 4 residual (failing-tests-first, 2026-11-08): gap report must
not trust contradictory per-symbol coverage labels over recomputed coverage facts.

A symbol is complete only when validated facts prove: status==ok,
coverage.complete_for_target_window is true, expected/observed bars match the
target-window expected count, gap_count==0, and synthetic_check is present and
clean. Missing synthetic_check is unverified (not complete).
"""
from __future__ import annotations

import unittest

from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars
from scripts.generate_candle_coverage_gap_report import build_gap_report


EXP = expected_hourly_bars(TARGET_START, TARGET_END)


def _ok():
    return {
        "status": "ok",
        "synthetic_check": {"is_synthetic": False, "reason": "varied_series_ok"},
        "coverage": {
            "complete_for_target_window": True,
            "expected_hourly_bars": EXP,
            "observed_in_window_bars": EXP,
            "gap_count": 0,
        },
        "volume_coverage": {
            "min_daily_volume_usd": 5_000_000,
            "observed_min_24h_usd_volume": 6_000_000,
            "bars_checked": EXP,
            "bars_passing": EXP,
            "volume_filter_ok": True,
            "min_daily_volume_usd_requested": 5_000_000,
            "min_daily_volume_usd_effective": 5_000_000,
        },
    }


def _manifest():
    return {
        "fabricated_data": False,
        "real_market_data_intended": True,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": EXP},
        "symbols": {"BTC": _ok()},
        "request_params": {"min_daily_volume_usd_requested": 5_000_000, "min_daily_volume_usd_effective": 5_000_000},
        "summary": {
            "all_complete": True,
            "ready_for_real_campaign": True,
            "synthetic_series_detected": [],
            "complete_symbols": ["BTC"],
            "symbols_complete": 1,
        },
    }


class TestGapReportCoverageFactAuthority(unittest.TestCase):
    def _scan(self):
        return {"searched_paths": [], "verified_archives_found": []}

    def _assert_blocked(self, m, msg=""):
        r = build_gap_report(manifest=m, probe_evidence=None, archive_scan=self._scan())
        self.assertFalse(r.get("ready_for_real_campaign"), (msg, r.get("ready_for_real_campaign"), r.get("blocker")))
        self.assertFalse(r.get("all_complete"), (msg, r.get("all_complete"), r))
        self.assertTrue(r["blocker"]["item_6c_blocked"], (msg, r))
        return r

    def test_complete_flag_true_but_gaps_blocks(self):
        m = _manifest()
        m["symbols"]["BTC"]["coverage"]["gap_count"] = 5
        m["symbols"]["BTC"]["coverage"]["observed_in_window_bars"] = EXP - 5
        self._assert_blocked(m, "gaps")

    def test_complete_flag_true_but_observed_mismatch_blocks(self):
        m = _manifest()
        m["symbols"]["BTC"]["coverage"]["observed_in_window_bars"] = EXP - 1
        self._assert_blocked(m, "observed")

    def test_complete_flag_true_but_expected_mismatch_blocks(self):
        m = _manifest()
        m["symbols"]["BTC"]["coverage"]["expected_hourly_bars"] = EXP - 1
        self._assert_blocked(m, "expected")

    def test_complete_flag_true_but_status_not_ok_blocks(self):
        m = _manifest()
        m["symbols"]["BTC"]["status"] = "error"
        self._assert_blocked(m, "status")

    def test_missing_synthetic_check_unverified_blocks(self):
        m = _manifest()
        del m["symbols"]["BTC"]["synthetic_check"]
        self._assert_blocked(m, "synthetic_missing")

    def test_validated_facts_still_ready(self):
        m = _manifest()
        r = build_gap_report(manifest=m, probe_evidence=None, archive_scan=self._scan())
        self.assertTrue(r.get("ready_for_real_campaign"), r)
        self.assertTrue(r.get("all_complete"), r)
        self.assertFalse(r["blocker"]["item_6c_blocked"], r)


if __name__ == "__main__":
    unittest.main()
