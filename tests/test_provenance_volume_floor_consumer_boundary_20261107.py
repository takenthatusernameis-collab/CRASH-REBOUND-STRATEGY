import unittest, tempfile, json
from pathlib import Path
from src.data.provenance import validate_provenance, expected_hourly_bars, TARGET_START, TARGET_END

EXP = expected_hourly_bars(TARGET_START, TARGET_END)

def _manifest(**sym_overrides):
    sym = {
        "status": "ok",
        "cache_path": "x.json",
        "sha256": "a"*64,
        "synthetic_check": {"is_synthetic": False, "reason": "varied_series_ok"},
        "coverage": {
            "complete_for_target_window": True,
            "expected_hourly_bars": EXP,
            "observed_in_window_bars": EXP,
            "gap_count": 0,
        },
    }
    sym.update(sym_overrides)
    return {
        "generated_at_utc": "2026-11-07T00:00:00Z",
        "fabricated_data": False,
        "real_market_data_intended": True,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": EXP},
        "summary": {"all_complete": True, "ready_for_real_campaign": True},
        "symbols": {"BTC": sym},
    }

class T(unittest.TestCase):
    def test_rejects_volume_filter_not_ok_when_floor_required(self):
        m = _manifest(volume_coverage={"volume_filter_ok": False, "min_daily_volume_usd": 5_000_000, "observed_min_24h_usd_volume": 1_000_000})
        ok, errs = validate_provenance(m, require_complete=True, min_symbols=1, require_spec_volume_floor=5_000_000)
        self.assertFalse(ok)
        self.assertTrue(any("volume" in e.lower() for e in errs), errs)

    def test_rejects_subspec_floor_when_floor_required(self):
        m = _manifest(volume_coverage={"volume_filter_ok": True, "min_daily_volume_usd": 1_000_000, "observed_min_24h_usd_volume": 6_000_000})
        ok, errs = validate_provenance(m, require_complete=True, min_symbols=1, require_spec_volume_floor=5_000_000)
        self.assertFalse(ok)

    def test_rejects_subspec_intent_when_present(self):
        m = _manifest(volume_coverage={"volume_filter_ok": True, "min_daily_volume_usd_effective": 5_000_000, "min_daily_volume_usd_requested": 0, "observed_min_24h_usd_volume": 6_000_000})
        ok, errs = validate_provenance(m, require_complete=True, min_symbols=1, require_spec_volume_floor=5_000_000)
        self.assertFalse(ok)

    def test_accepts_spec_compliant_volume_when_floor_required(self):
        m = _manifest(volume_coverage={"volume_filter_ok": True, "min_daily_volume_usd_effective": 5_000_000, "min_daily_volume_usd_requested": 5_000_000, "observed_min_24h_usd_volume": 6_000_000})
        ok, errs = validate_provenance(m, require_complete=True, min_symbols=1, require_spec_volume_floor=5_000_000)
        self.assertTrue(ok, errs)

    def test_legacy_manifest_without_volume_coverage_rejected_when_floor_required(self):
        m = _manifest()  # no volume_coverage
        ok, errs = validate_provenance(m, require_complete=True, min_symbols=1, require_spec_volume_floor=5_000_000)
        self.assertFalse(ok)

    def test_default_no_volume_floor_requirement_unchanged(self):
        m = _manifest(volume_coverage={"volume_filter_ok": False, "min_daily_volume_usd": 1})
        ok, errs = validate_provenance(m, require_complete=True, min_symbols=1)
        self.assertTrue(ok, errs)

if __name__ == '__main__':
    unittest.main(verbosity=2)
