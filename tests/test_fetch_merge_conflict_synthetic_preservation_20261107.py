"""Campaign item 4 residual (fetch emission hardening): multi-archive merge must
fail-close when conflicting archives disagree about a symbol's coverage/synthetic
truth, and the emitted manifest summary must recompute complete_symbols from
validated symbol facts (status ok + coverage complete + synthetic_check clean) —
never from a stale/optimistic upstream label.

Specific regression covered here: when two verified archives supply the same
symbol with DIFFERENT coverage evidence and one of them is synthetic/flat, the
merge previously recorded the conflict but kept the first archive's `ok` entry
unchanged, dropping the synthetic evidence and letting an optimistic
`complete_symbols`/`symbols_complete` summary through the emission path.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.fetch_hyperliquid_candles import merge_verified_archives, _parse_iso  # noqa: E402


def _varied_rows(n=48, start="2025-12-20T00:00:00Z", close=100.0, vol=1_000_000.0):
    s = _parse_iso(start)
    rows = []
    for i in range(n):
        ts = (s + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
        c = close + (i % 5) * 0.1
        v = vol + i * 1000.0
        rows.append({"timestamp": ts, "open": c, "high": c + 1, "low": c - 1, "close": c, "volume": v})
    return rows


def _flat_rows(n=40, start="2025-12-20T00:00:00Z", close=100.0, vol=1.0):
    s = _parse_iso(start)
    rows = []
    for i in range(n):
        ts = (s + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
        rows.append({"timestamp": ts, "open": close, "high": close, "low": close, "close": close, "volume": vol})
    return rows


def _window_for(rows, start="2025-12-20T00:00:00Z"):
    s = _parse_iso(start)
    e = s + timedelta(hours=len(rows) - 1)
    return s, e


class TestMergeConflictSyntheticPreservation(unittest.TestCase):
    def _write(self, td, name, rows):
        p = td / name
        p.write_text(json.dumps(rows))
        return p

    def test_conflicting_synthetic_archive_does_not_leave_symbol_ok(self):
        """Different-coverage merge where one archive is synthetic must fail-close."""
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            # Archive A: varied, complete for its own (shorter) window.
            a_rows = _varied_rows(n=48)
            a = self._write(td, "a.json", a_rows)
            # Archive B: flat/synthetic, DIFFERENT bar count -> coverage evidence differs.
            b_rows = _flat_rows(n=40)
            b = self._write(td, "b.json", b_rows)
            start, end = _window_for(a_rows)
            merged = merge_verified_archives([a, b], ["BTC"], start, end, 5_000_000.0, allow_temp_paths=True)
            entry = merged["symbols"]["BTC"]
            # The conflict must be recorded...
            self.assertTrue(merged.get("conflicts"), "expected a coverage conflict to be recorded")
            # ...AND the kept symbol entry must NOT be labeled ok/complete: a
            # conflicting synthetic source is not trustworthy evidence.
            self.assertNotEqual(
                entry.get("status"), "ok",
                f"merge left symbol ok despite conflicting synthetic archive: {entry}",
            )
            synth = entry.get("synthetic_check") or {}
            # Synthetic evidence from either source must be preserved in the
            # emitted entry (never dropped because the archives disagreed).
            self.assertTrue(
                synth.get("is_synthetic"),
                f"synthetic evidence from conflicting archive was dropped: {synth}",
            )

    def test_conflict_without_synthetic_still_fail_closes_complete_label(self):
        """Even when neither archive is synthetic, divergent coverage evidence must
        not let the summary label the symbol complete."""
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            a_rows = _varied_rows(n=48)
            a = self._write(td, "a.json", a_rows)
            b_rows = _varied_rows(n=40)  # different count, varied (non-synthetic)
            b = self._write(td, "b.json", b_rows)
            start, end = _window_for(a_rows)
            merged = merge_verified_archives([a, b], ["BTC"], start, end, 5_000_000.0, allow_temp_paths=True)
            entry = merged["symbols"]["BTC"]
            self.assertTrue(merged.get("conflicts"), "expected a coverage conflict")
            self.assertNotEqual(
                entry.get("status"), "ok",
                f"merge left symbol ok despite divergent coverage evidence: {entry}",
            )

    def test_summary_recomputes_complete_symbols_from_validated_facts(self):
        """Emission-path guard: an entry with status=ok but synthetic_check.is_synthetic
        true must never be counted in complete_symbols / symbols_complete."""
        from scripts.fetch_hyperliquid_candles import _summary_from_symbols  # noqa: E402

        # Simulate a stale/optimistic upstream entry: status ok but synthetic.
        symbols = {
            "BTC": {"status": "ok", "synthetic_check": {"is_synthetic": True, "reason": "flat_series"},
                    "coverage": {"complete_for_target_window": True, "observed_in_window_bars": 48,
                                 "expected_hourly_bars": 48, "gap_count": 0}},
            "ETH": {"status": "ok", "synthetic_check": {"is_synthetic": False, "reason": "varied_series_ok"},
                    "coverage": {"complete_for_target_window": True, "observed_in_window_bars": 48,
                                 "expected_hourly_bars": 48, "gap_count": 0}},
        }
        summary = _summary_from_symbols(symbols)
        # BTC is synthetic -> must be excluded from complete_symbols despite status=ok.
        self.assertNotIn("BTC", summary["complete_symbols"])
        self.assertEqual(summary["symbols_complete"], 1)
        self.assertFalse(summary["all_complete"])
        self.assertFalse(summary["ready_for_real_campaign"])


if __name__ == "__main__":
    unittest.main()