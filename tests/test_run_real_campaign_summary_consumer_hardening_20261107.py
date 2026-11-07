"""Failing-tests-first (campaign item 4 residual, 2026-11-07):
run_real_campaign must not trust manifest.summary.complete_symbols for provenance
output labels; validate_provenance must fail-closed when summary.complete_symbols
/ summary.symbols_complete contradict recomputed symbol facts.

Consumers (run_real_campaign data_provenance, reporting labels) must derive
symbol completeness facts from validated symbol coverage/synthetic evidence.
Optimistic/stale summary labels are not evidence.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.run_real_campaign import _validated_complete_symbols
from src.data.provenance import expected_hourly_bars, validate_provenance, TARGET_START, TARGET_END

EXP = expected_hourly_bars(TARGET_START, TARGET_END)


def _ok_sym(observed=EXP):
    return {
        "status": "ok",
        "synthetic_check": {"is_synthetic": False, "reason": "varied_series_ok"},
        "coverage": {
            "complete_for_target_window": True,
            "expected_hourly_bars": EXP,
            "observed_in_window_bars": observed,
            "gap_count": 0,
        },
        "volume_coverage": {
            "min_daily_volume_usd": 5_000_000,
            "observed_min_24h_usd_volume": 6_000_000,
            "bars_checked": observed,
            "bars_passing": observed,
            "volume_filter_ok": True,
            "min_daily_volume_usd_requested": 5_000_000,
            "min_daily_volume_usd_effective": 5_000_000,
        },
    }


def base_manifest():
    return {
        "fabricated_data": False,
        "real_market_data_intended": True,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": EXP},
        "symbols": {"BTC": _ok_sym()},
        "request_params": {"min_daily_volume_usd_requested": 5_000_000, "min_daily_volume_usd_effective": 5_000_000},
        "summary": {
            "all_complete": True,
            "ready_for_real_campaign": True,
            "synthetic_series_detected": [],
            "complete_symbols": ["BTC"],
            "symbols_complete": 1,
        },
    }


class TestSummaryCompleteSymbolsValidation(unittest.TestCase):
    def test_validate_provenance_rejects_complete_symbols_listing_incomplete_symbol(self):
        m = base_manifest()
        m["symbols"]["ETH"] = _ok_sym(observed=100)
        m["symbols"]["ETH"]["status"] = "incomplete"
        m["symbols"]["ETH"]["coverage"]["complete_for_target_window"] = False
        m["symbols"]["ETH"]["coverage"]["observed_in_window_bars"] = 100
        m["summary"]["complete_symbols"] = ["BTC", "ETH"]
        m["summary"]["symbols_complete"] = 2
        m["summary"]["all_complete"] = True  # also contradictory
        ok, errs = validate_provenance(m, require_complete=False, min_symbols=1,
                                       require_spec_volume_floor=5_000_000)
        self.assertFalse(ok, errs)
        self.assertTrue(
            any("complete_symbols" in e or "symbols_complete" in e for e in errs),
            errs,
        )

    def test_validate_provenance_rejects_complete_symbols_omitting_actual_complete_symbol(self):
        m = base_manifest()
        m["symbols"]["ETH"] = _ok_sym()
        m["summary"]["complete_symbols"] = ["BTC"]  # omits ETH
        m["summary"]["symbols_complete"] = 1
        m["summary"]["all_complete"] = True
        ok, errs = validate_provenance(m, require_complete=False, min_symbols=1,
                                       require_spec_volume_floor=5_000_000)
        self.assertFalse(ok, errs)
        self.assertTrue(
            any("complete_symbols" in e or "symbols_complete" in e for e in errs),
            errs,
        )

    def test_validate_provenance_rejects_symbols_complete_count_mismatch(self):
        m = base_manifest()
        m["summary"]["complete_symbols"] = ["BTC"]
        m["summary"]["symbols_complete"] = 99
        ok, errs = validate_provenance(m, require_complete=True, min_symbols=1,
                                       require_spec_volume_floor=5_000_000)
        self.assertFalse(ok, errs)
        self.assertTrue(any("symbols_complete" in e for e in errs), errs)

    def test_validate_provenance_accepts_consistent_complete_symbols(self):
        m = base_manifest()
        m["symbols"]["ETH"] = _ok_sym()
        m["summary"]["complete_symbols"] = ["BTC", "ETH"]
        m["summary"]["symbols_complete"] = 2
        ok, errs = validate_provenance(m, require_complete=True, min_symbols=1,
                                       require_spec_volume_floor=5_000_000)
        self.assertTrue(ok, errs)

    def test_legacy_manifest_without_complete_symbols_fields_still_valid(self):
        m = base_manifest()
        del m["summary"]["complete_symbols"]
        del m["summary"]["symbols_complete"]
        ok, errs = validate_provenance(m, require_complete=True, min_symbols=1,
                                       require_spec_volume_floor=5_000_000)
        self.assertTrue(ok, errs)


class TestRunRealCampaignOutputRecomputesCompleteSymbols(unittest.TestCase):
    def test_validated_complete_symbols_recomputes_from_symbol_facts(self):
        m = base_manifest()
        m["symbols"]["ETH"] = _ok_sym()
        m["symbols"]["BAD"] = _ok_sym(observed=100)
        m["symbols"]["BAD"]["status"] = "incomplete"
        m["symbols"]["BAD"]["coverage"]["complete_for_target_window"] = False
        m["summary"]["complete_symbols"] = ["BTC", "BAD", "GHOST"]  # stale/wrong
        m["summary"]["symbols_complete"] = 3
        got = _validated_complete_symbols(m)
        self.assertEqual(got, ["BTC", "ETH"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
