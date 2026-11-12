"""CELL 9: provenance volume evidence must be fail-closed when spec floor required.

Gap proof (2026-11-12): src/data/provenance.py::_validate_symbol_volume_evidence
accepted a symbol claiming complete+volume_filter_ok+spec-compliant requested/
effective floors even when observed_min_24h_usd_volume was missing/None/
non-numeric/bool under require_spec_volume_floor. That allowed
require_verified_provenance(..., require_spec_volume_floor=5_000_000) to pass
without concrete observed >= floor evidence, contradicting fail-closed real
evidence requirements. scripts/run_real_campaign.py already rejects missing
observed_min in its own validator; the shared provenance gate must not pass it.

Traced fixtures (EXP=expected_hourly_bars for target window):
  - observed_min absent/None/"n/a"/""/True/False + volume_filter_ok True +
    floors/intent 5e6 -> MUST reject (no concrete observed >= 5e6 evidence).
  - observed_min numeric 6e6 -> MUST accept.
  - observed_min numeric 4_999_999 -> MUST reject (< floor, existing behavior).
  - no require_spec_volume_floor arg -> legacy behavior preserved (no rejection
    solely for missing observed_min).
"""
import unittest

from src.data.provenance import validate_provenance, expected_hourly_bars, TARGET_START, TARGET_END

EXP = expected_hourly_bars(TARGET_START, TARGET_END)


def _base_manifest(observed_min=6_000_000, *, include_observed=True):
    vol = {
        "volume_filter_ok": True,
        "min_daily_volume_usd": 5_000_000,
        "min_daily_volume_usd_requested": 5_000_000,
        "min_daily_volume_usd_effective": 5_000_000,
    }
    if include_observed:
        vol["observed_min_24h_usd_volume"] = observed_min
    return {
        "fabricated_data": False,
        "real_market_data_intended": True,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": EXP},
        "symbols": {
            "BTC": {
                "status": "ok",
                "synthetic_check": {"is_synthetic": False, "reason": "varied_series_ok"},
                "coverage": {
                    "complete_for_target_window": True,
                    "expected_hourly_bars": EXP,
                    "observed_in_window_bars": EXP,
                    "gap_count": 0,
                },
                "volume_coverage": vol,
            }
        },
        "summary": {"all_complete": True, "ready_for_real_campaign": True, "synthetic_series_detected": []},
    }


class TestProvenanceObservedMinRequiredForSpecFloor(unittest.TestCase):
    def _assert_rejects_missing_or_invalid_observed(self, manifest):
        ok, errs = validate_provenance(manifest, require_complete=True, min_symbols=1,
                                       require_spec_volume_floor=5_000_000)
        self.assertFalse(ok, errs)
        self.assertTrue(any("observed_min_24h_usd_volume" in e for e in errs), errs)
        self.assertTrue(any("BTC" in e for e in errs), errs)

    def test_rejects_absent_observed_min_when_floor_required(self):
        m = _base_manifest(include_observed=False)
        self._assert_rejects_missing_or_invalid_observed(m)

    def test_rejects_none_observed_min_when_floor_required(self):
        m = _base_manifest(observed_min=None)
        self._assert_rejects_missing_or_invalid_observed(m)

    def test_rejects_nonnumeric_observed_min_when_floor_required(self):
        m = _base_manifest(observed_min="n/a")
        self._assert_rejects_missing_or_invalid_observed(m)

    def test_rejects_empty_string_observed_min_when_floor_required(self):
        m = _base_manifest(observed_min="")
        self._assert_rejects_missing_or_invalid_observed(m)

    def test_rejects_bool_true_observed_min_when_floor_required(self):
        # bool must not coerce to numeric evidence
        m = _base_manifest(observed_min=True)
        self._assert_rejects_missing_or_invalid_observed(m)

    def test_rejects_bool_false_observed_min_when_floor_required(self):
        m = _base_manifest(observed_min=False)
        self._assert_rejects_missing_or_invalid_observed(m)

    def test_rejects_observed_min_below_floor_when_floor_required(self):
        m = _base_manifest(observed_min=4_999_999)
        ok, errs = validate_provenance(m, require_complete=True, min_symbols=1,
                                       require_spec_volume_floor=5_000_000)
        self.assertFalse(ok, errs)
        joined = " ".join(errs)
        self.assertIn("observed_min_24h_usd_volume", joined)
        self.assertIn("required spec floor", joined)
        self.assertTrue(("4.999999e+06" in joined) or ("4.99999e+06" in joined) or ("4999999" in joined) or ("5e+06" in joined and "< required spec floor" in joined), errs)

    def test_accepts_numeric_observed_min_at_or_above_floor(self):
        m = _base_manifest(observed_min=6_000_000)
        ok, errs = validate_provenance(m, require_complete=True, min_symbols=1,
                                       require_spec_volume_floor=5_000_000)
        self.assertTrue(ok, errs)
        m2 = _base_manifest(observed_min=5_000_000)
        ok2, errs2 = validate_provenance(m2, require_complete=True, min_symbols=1,
                                         require_spec_volume_floor=5_000_000)
        self.assertTrue(ok2, errs2)

    def test_no_floor_requirement_preserves_legacy_absent_observed_behavior(self):
        # Without require_spec_volume_floor, volume evidence is not enforced by
        # this gate (existing behavior preserved).
        m = _base_manifest(include_observed=False)
        ok, errs = validate_provenance(m, require_complete=True, min_symbols=1)
        self.assertTrue(ok, errs)
        m2 = _base_manifest(observed_min=None)
        ok2, errs2 = validate_provenance(m2, require_complete=True, min_symbols=1)
        self.assertTrue(ok2, errs2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
