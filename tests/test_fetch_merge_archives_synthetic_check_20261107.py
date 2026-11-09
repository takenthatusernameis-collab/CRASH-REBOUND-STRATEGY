"""Campaign item 4: merge_verified_archives / multi-source manifest emission must
compute synthetic_check and fail-close synthetic series, same as single-archive
ingest path. Legacy/optimistic merge entries without synthetic_check are
unverified and unsafe for provenance consumers."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.fetch_hyperliquid_candles import merge_verified_archives, _parse_iso


def _make_rows(n=48, start="2025-12-20T00:00:00Z", close=100.0, vol=1_000_000.0, varied=True):
    s = _parse_iso(start)
    rows = []
    for i in range(n):
        ts = (s + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
        c = (close + (i % 5) * 0.1) if varied else close
        v = (vol + i * 1000) if varied else vol
        rows.append({"timestamp": ts, "open": c, "high": c + 1, "low": c - 1, "close": c, "volume": v})
    return rows


class TestMergeVerifiedArchivesSyntheticCheck(unittest.TestCase):
    def _run_merge(self, rows, symbols=("BTC",)):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            a = td / "a.json"
            a.write_text(json.dumps(rows))
            start = _parse_iso("2025-12-20T00:00:00Z")
            end = _parse_iso((_parse_iso("2025-12-20T00:00:00Z") + timedelta(hours=len(rows) - 1)).strftime("%Y-%m-%dT%H:%M:%SZ"))
            return merge_verified_archives([a], list(symbols), start, end, 5_000_000.0, allow_temp_paths=True)


    def test_varied_series_emits_synthetic_check_false(self):
        merged = self._run_merge(_make_rows(varied=True))
        entry = merged["symbols"]["BTC"]
        self.assertIn("synthetic_check", entry)
        self.assertIsInstance(entry["synthetic_check"], dict)
        self.assertFalse(entry["synthetic_check"].get("is_synthetic"))
        self.assertEqual(entry["status"], "ok")

    def test_flat_series_emits_synthetic_check_true_and_fails_closed(self):
        merged = self._run_merge(_make_rows(varied=False, close=100.0, vol=1.0))
        entry = merged["symbols"]["BTC"]
        self.assertIn("synthetic_check", entry)
        self.assertTrue(entry["synthetic_check"].get("is_synthetic"))
        self.assertEqual(entry["status"], "error")
        err = (entry.get("error") or "").lower()
        self.assertTrue("flat" in err or "synthetic" in err or "distinct" in err, err)

    def test_identical_archive_merge_preserves_synthetic_check(self):
        rows = _make_rows(varied=True)
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            a1 = td / "a1.json"; a1.write_text(json.dumps(rows))
            a2 = td / "a2.json"; a2.write_text(json.dumps(rows))
            start = _parse_iso("2025-12-20T00:00:00Z")
            end = _parse_iso((_parse_iso("2025-12-20T00:00:00Z") + timedelta(hours=len(rows) - 1)).strftime("%Y-%m-%dT%H:%M:%SZ"))
            merged = merge_verified_archives([a1, a2], ["BTC"], start, end, 5_000_000.0, allow_temp_paths=True)
            entry = merged["symbols"]["BTC"]
            self.assertIn("synthetic_check", entry)
            self.assertFalse(entry["synthetic_check"].get("is_synthetic"))
            self.assertEqual(entry.get("status"), "ok")


if __name__ == "__main__":
    unittest.main()
