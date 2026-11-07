"""Fail-closed provenance summary consistency (campaign item 4 hardening).

Manifest `summary` fields (all_complete, ready_for_real_campaign,
synthetic_series_detected) are evidence labels. When present, they must not
contradict symbol-level facts; optimistic summary labels must fail validation
so consumers cannot trust stale/optimistic summary booleans over recomputed
facts. Legacy manifests lacking summary/fields remain compatible.
"""
import json
import unittest

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
        },
    }


def base_manifest():
    return {
        "fabricated_data": False,
        "real_market_data_intended": True,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": EXP},
        "symbols": {"BTC": _ok_sym()},
        "summary": {"all_complete": True, "ready_for_real_campaign": True, "synthetic_series_detected": []},
    }


class TestProvenanceSummaryConsistency(unittest.TestCase):
    def test_rejects_ready_for_real_campaign_true_when_any_symbol_synthetic(self):
        m = base_manifest()
        m["symbols"]["BTC"]["synthetic_check"] = {"is_synthetic": True, "reason": "flat"}
        m["symbols"]["BTC"]["status"] = "error"
        m["symbols"]["BTC"]["coverage"]["complete_for_target_window"] = False
        # summary lies
        m["summary"]["ready_for_real_campaign"] = True
        m["summary"]["all_complete"] = False
        ok, errs = validate_provenance(m, require_complete=False, min_symbols=0,
                                       require_spec_volume_floor=5_000_000)
        self.assertFalse(ok)
        self.assertTrue(any("ready_for_real_campaign" in e for e in errs), errs)

    def test_rejects_all_complete_true_when_not_all_symbols_complete(self):
        m = base_manifest()
        m["symbols"]["ETH"] = _ok_sym(observed=100)
        m["symbols"]["ETH"]["status"] = "incomplete"
        m["symbols"]["ETH"]["coverage"]["complete_for_target_window"] = False
        m["symbols"]["ETH"]["coverage"]["observed_in_window_bars"] = 100
        m["summary"]["all_complete"] = True
        m["summary"]["ready_for_real_campaign"] = False
        ok, errs = validate_provenance(m, require_complete=False, min_symbols=1,
                                       require_spec_volume_floor=5_000_000)
        self.assertFalse(ok)
        self.assertTrue(any("summary.all_complete" in e or "all_complete" in e for e in errs), errs)

    def test_rejects_synthetic_series_detected_missing_actual_synthetic_symbol(self):
        m = base_manifest()
        m["symbols"]["ETH"] = _ok_sym()
        m["symbols"]["ETH"]["synthetic_check"] = {"is_synthetic": True, "reason": "flat"}
        m["symbols"]["ETH"]["status"] = "error"
        m["symbols"]["ETH"]["coverage"]["complete_for_target_window"] = False
        m["summary"]["synthetic_series_detected"] = []  # omission
        m["summary"]["ready_for_real_campaign"] = False
        m["summary"]["all_complete"] = False
        ok, errs = validate_provenance(m, require_complete=False, min_symbols=1,
                                       require_spec_volume_floor=5_000_000)
        self.assertFalse(ok)
        self.assertTrue(any("synthetic_series_detected" in e for e in errs), errs)

    def test_rejects_synthetic_series_detected_listing_non_synthetic_symbol(self):
        m = base_manifest()
        m["summary"]["synthetic_series_detected"] = ["BTC"]  # BTC is not synthetic
        ok, errs = validate_provenance(m, require_complete=True, min_symbols=1,
                                       require_spec_volume_floor=5_000_000)
        self.assertFalse(ok)
        self.assertTrue(any("synthetic_series_detected" in e for e in errs), errs)

    def test_legacy_manifest_without_summary_fields_still_valid(self):
        m = base_manifest()
        del m["summary"]
        ok, errs = validate_provenance(m, require_complete=True, min_symbols=1,
                                       require_spec_volume_floor=5_000_000)
        self.assertTrue(ok, errs)

    def test_consistent_summary_with_synthetic_symbol_fails_closed_not_ready(self):
        m = base_manifest()
        m["symbols"]["ETH"] = _ok_sym()
        m["symbols"]["ETH"]["synthetic_check"] = {"is_synthetic": True, "reason": "flat"}
        m["symbols"]["ETH"]["status"] = "error"
        m["symbols"]["ETH"]["coverage"]["complete_for_target_window"] = False
        m["summary"] = {
            "all_complete": False,
            "ready_for_real_campaign": False,
            "synthetic_series_detected": ["ETH"],
        }
        ok, errs = validate_provenance(m, require_complete=False, min_symbols=1,
                                       require_spec_volume_floor=5_000_000)
        # ETH is synthetic -> validate_provenance already rejects ETH synthetic at symbol level.
        self.assertFalse(ok)
        self.assertTrue(any("synthetic" in e.lower() for e in errs), errs)


if __name__ == "__main__":
    unittest.main(verbosity=2)
