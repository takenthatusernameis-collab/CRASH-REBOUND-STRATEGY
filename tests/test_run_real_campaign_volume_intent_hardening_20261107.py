"""Failing-tests-first: run_real_campaign consumer must fail-closed on stale
or sub-$5M volume-intent evidence in manifests (requested/effective fields).

Campaign item 3/4 follow-up to gap-report hardening: a manifest that records
non-spec volume intent (requested < $5M) or effective < $5M is not trustworthy
spec-compliant evidence, even if observed_min and volume_filter_ok look fine.
Legacy manifests lacking intent fields remain subject to existing checks only.
"""
from __future__ import annotations

import unittest

from scripts.run_real_campaign import validate_symbol_volume_coverage
from src.data.provenance import ProvenanceError


def _manifest(sym="BTC", *, status="ok", complete=True, volume_filter_ok=True,
              observed_min=6_000_000.0, volcov_extra=None, request_params=None):
    volcov = {
        "volume_filter_ok": volume_filter_ok,
        "observed_min_24h_usd_volume": observed_min,
        "observed_mean_24h_usd_volume": 7_000_000.0,
        "bars_passing": 6792,
        "bars_checked": 6792,
        "min_daily_volume_usd": 5_000_000,
    }
    if volcov_extra:
        volcov.update(volcov_extra)
    m = {
        "symbols": {
            sym: {
                "status": status,
                "coverage": {
                    "complete_for_target_window": complete,
                    "expected_hourly_bars": 6792,
                    "observed_in_window_bars": 6792 if complete else 0,
                },
                "volume_coverage": volcov,
            }
        }
    }
    if request_params is not None:
        m["request_params"] = request_params
    return m


class RunRealCampaignVolumeIntentHardeningTests(unittest.TestCase):
    SPEC = 5_000_000.0

    def test_rejects_per_symbol_requested_below_floor_even_if_effective_and_observed_ok(self):
        m = _manifest(volcov_extra={
            "min_daily_volume_usd_requested": 1.0,
            "min_daily_volume_usd_effective": 5_000_000.0,
        })
        with self.assertRaises(ProvenanceError) as ctx:
            validate_symbol_volume_coverage(m, ["BTC"], self.SPEC)
        msg = str(ctx.exception)
        self.assertIn("BTC", msg)
        self.assertTrue(
            "requested" in msg.lower() or "intent" in msg.lower() or "5" in msg,
            msg,
        )

    def test_rejects_per_symbol_effective_below_floor_when_field_present(self):
        m = _manifest(volcov_extra={
            "min_daily_volume_usd_effective": 4_999_999.0,
            "min_daily_volume_usd": 4_999_999.0,
        })
        with self.assertRaises(ProvenanceError) as ctx:
            validate_symbol_volume_coverage(m, ["BTC"], self.SPEC)
        self.assertIn("BTC", str(ctx.exception))

    def test_rejects_manifest_request_params_requested_below_floor_when_present(self):
        m = _manifest(request_params={
            "min_daily_volume_usd_requested": 0.0,
            "min_daily_volume_usd_effective": 5_000_000.0,
            "min_daily_volume_usd": 5_000_000.0,
        })
        with self.assertRaises(ProvenanceError) as ctx:
            validate_symbol_volume_coverage(m, ["BTC"], self.SPEC)
        self.assertTrue(
            "request" in str(ctx.exception).lower() or "requested" in str(ctx.exception).lower()
            or "manifest" in str(ctx.exception).lower(),
            str(ctx.exception),
        )

    def test_accepts_legacy_manifest_without_intent_fields_when_existing_checks_pass(self):
        m = _manifest()  # no requested/effective extras, no request_params
        self.assertEqual(validate_symbol_volume_coverage(m, ["BTC"], self.SPEC), ["BTC"])

    def test_accepts_spec_compliant_intent_fields(self):
        m = _manifest(volcov_extra={
            "min_daily_volume_usd_requested": 5_000_000.0,
            "min_daily_volume_usd_effective": 5_000_000.0,
        }, request_params={
            "min_daily_volume_usd_requested": 5_000_000.0,
            "min_daily_volume_usd_effective": 5_000_000.0,
        })
        self.assertEqual(validate_symbol_volume_coverage(m, ["BTC"], self.SPEC), ["BTC"])


if __name__ == "__main__":
    unittest.main()
