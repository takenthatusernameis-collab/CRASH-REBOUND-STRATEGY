#!/usr/bin/env python3
"""Regression tests for fetch_hyperliquid_candles._summary_from_symbols strict validated-facts path.

Campaign item 4 residual: fetch emission-path summary labels must be recomputed
from validated symbol facts for the CURRENT target window (belt-and-suspenders
over complete_for_target_window), matching the strict validated-facts path used
by derive_verified_universe and provenance.complete_symbol_subset. Fetch must
never declare all_complete/ready_for_real_campaign for a symbol the real-campaign
gate would reject (stale window mismatch, gap_count != 0, synthetic, or missing
synthetic_check).

Failing-tests-first: these tests assert fail-closed behavior; they must fail
against a lenient summary and pass against the hardened _summary_from_symbols.
"""
import unittest

from scripts.fetch_hyperliquid_candles import _summary_from_symbols  # noqa: E402

EXPECTED_BARS = 48


def _complete_entry(exp=EXPECTED_BARS, obs=None, gap_count=0, synthetic=False, status="ok", complete=True):
    return {
        "status": status,
        "synthetic_check": {"is_synthetic": synthetic, "reason": "varied_series_ok" if not synthetic else "flat_series"},
        "coverage": {
            "complete_for_target_window": complete,
            "observed_in_window_bars": exp if obs is None else obs,
            "expected_hourly_bars": exp,
            "gap_count": gap_count,
        },
    }


class TestFetchSummaryStrictValidatedFacts(unittest.TestCase):
    def test_all_strict_complete_symbols_ready(self):
        symbols = {
            "BTC": _complete_entry(),
            "ETH": _complete_entry(),
        }
        summary = _summary_from_symbols(symbols, expected_bars=EXPECTED_BARS)
        self.assertTrue(summary["all_complete"], summary)
        self.assertTrue(summary["ready_for_real_campaign"], summary)
        self.assertEqual(set(summary["complete_symbols"]), {"BTC", "ETH"})
        self.assertEqual(summary["symbols_complete"], 2)

    def test_stale_window_mismatch_is_fail_closed(self):
        # complete_for_target_window=True but computed against a different window
        # (expected_hourly_bars != current exp) must NOT be counted complete.
        symbols = {
            "BTC": _complete_entry(exp=EXPECTED_BARS, obs=EXPECTED_BARS),
            "ETH": _complete_entry(exp=EXPECTED_BARS + 1, obs=EXPECTED_BARS + 1),  # stale window
        }
        summary = _summary_from_symbols(symbols, expected_bars=EXPECTED_BARS)
        self.assertFalse(summary["all_complete"], summary)
        self.assertFalse(summary["ready_for_real_campaign"], summary)
        self.assertNotIn("ETH", summary["complete_symbols"], summary)
        self.assertIn("BTC", summary["complete_symbols"], summary)

    def test_nonzero_gap_count_is_fail_closed(self):
        # complete_for_target_window=True but gap_count != 0 must not be counted complete.
        symbols = {
            "BTC": _complete_entry(gap_count=3),
        }
        summary = _summary_from_symbols(symbols, expected_bars=EXPECTED_BARS)
        self.assertFalse(summary["all_complete"], summary)
        self.assertFalse(summary["ready_for_real_campaign"], summary)
        self.assertEqual(summary["symbols_complete"], 0, summary)

    def test_observed_below_expected_is_fail_closed(self):
        symbols = {
            "BTC": _complete_entry(obs=EXPECTED_BARS - 1),
        }
        summary = _summary_from_symbols(symbols, expected_bars=EXPECTED_BARS)
        self.assertFalse(summary["all_complete"], summary)
        self.assertFalse(summary["ready_for_real_campaign"], summary)

    def test_missing_synthetic_check_is_fail_closed(self):
        symbols = {
            "BTC": {
                "status": "ok",
                "coverage": {
                    "complete_for_target_window": True,
                    "observed_in_window_bars": EXPECTED_BARS,
                    "expected_hourly_bars": EXPECTED_BARS,
                    "gap_count": 0,
                },
            },
        }
        summary = _summary_from_symbols(symbols, expected_bars=EXPECTED_BARS)
        self.assertFalse(summary["all_complete"], summary)
        self.assertFalse(summary["ready_for_real_campaign"], summary)

    def test_backward_compatible_without_expected_bars(self):
        # Legacy single-arg callers keep previous synthetic-exclusion behavior.
        symbols = {
            "BTC": {"status": "ok", "synthetic_check": {"is_synthetic": True},
                    "coverage": {"complete_for_target_window": True, "observed_in_window_bars": EXPECTED_BARS,
                                 "expected_hourly_bars": EXPECTED_BARS, "gap_count": 0}},
            "ETH": {"status": "ok", "synthetic_check": {"is_synthetic": False},
                    "coverage": {"complete_for_target_window": True, "observed_in_window_bars": EXPECTED_BARS,
                                 "expected_hourly_bars": EXPECTED_BARS, "gap_count": 0}},
        }
        summary = _summary_from_symbols(symbols)
        self.assertNotIn("BTC", summary["complete_symbols"])
        self.assertEqual(summary["symbols_complete"], 1)
        self.assertFalse(summary["all_complete"])


if __name__ == "__main__":
    unittest.main()
