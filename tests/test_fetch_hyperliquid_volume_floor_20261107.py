"""2026-11-07: fetch_hyperliquid_candles CLI must enforce $5M volume floor.

Failing-tests-first. Provenance/volume-coverage acquisition for spec-compliant
campaigns must not silently accept sub-$5M thresholds; 0 is not a valid
spec-compliant provenance threshold. Effective threshold and requested value
must be recorded for auditability.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
sys.path.insert(0, str(REPO_ROOT))


def _parse_iso(s: str):
    from datetime import datetime, timezone
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _make_rows(n=48, start="2025-12-20T00:00:00Z", close=100.0, vol=1_000_000.0):
    from datetime import timedelta
    s = _parse_iso(start)
    rows = []
    for i in range(n):
        ts = (s + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
        c = close + (i % 5) * 0.1
        rows.append({"timestamp": ts, "open": c, "high": c + 1, "low": c - 1, "close": c, "volume": vol + i})
    return rows


class TestFetchHyperliquidVolumeFloor(unittest.TestCase):
    def test_analyze_symbol_volume_coverage_floors_sub_5m(self):
        from scripts.fetch_hyperliquid_candles import analyze_symbol_volume_coverage
        candles = [{"timestamp_ms": i * 3600000, "open": 1, "high": 1, "low": 1, "close": 100, "volume": 500} for i in range(30)]
        r = analyze_symbol_volume_coverage(candles, 1_000_000)
        self.assertEqual(r["min_daily_volume_usd"], 5_000_000.0)
        self.assertFalse(r["volume_filter_ok"])

    def test_cli_records_requested_and_effective_volume_threshold(self):
        import subprocess
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            archive = td / "btc.json"
            archive.write_text(json.dumps(_make_rows()))
            cache_dir = td / "cache"
            cache_dir.mkdir()
            r = subprocess.run(
                [sys.executable, str(SCRIPTS / "fetch_hyperliquid_candles.py"),
                 "--source", "archive", "--input-archive", str(archive),
                 "--symbols", "BTC",
                 "--start", "2025-12-20T00:00:00Z", "--end", "2025-12-21T23:00:00Z",
                 "--cache-dir", str(cache_dir),
                 "--min-daily-volume-usd", "1000000",
                 "--allow-partial", "--allow-temp-archive-paths"],
                capture_output=True, text=True, cwd=str(REPO_ROOT),
            )

            # CLI must not silently treat 1M as the effective spec threshold.
            manifest = json.loads((cache_dir / "provenance.json").read_text())
            req = manifest.get("request_params") or {}
            self.assertEqual(req.get("min_daily_volume_usd_requested"), 1_000_000.0)
            self.assertGreaterEqual(float(req.get("min_daily_volume_usd_effective", 0)), 5_000_000.0)
            vc = ((manifest.get("symbols") or {}).get("BTC") or {}).get("volume_coverage") or {}
            self.assertGreaterEqual(float(vc.get("min_daily_volume_usd", 0)), 5_000_000.0)
            # Must not claim spec-compliant at sub-$5M request.
            self.assertTrue(req.get("spec_floor_enforced"))

    def test_cli_zero_volume_threshold_floored_for_provenance(self):
        import subprocess
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            archive = td / "btc.json"
            archive.write_text(json.dumps(_make_rows(vol=10.0)))
            cache_dir = td / "cache"
            cache_dir.mkdir()
            r = subprocess.run(
                [sys.executable, str(SCRIPTS / "fetch_hyperliquid_candles.py"),
                 "--source", "archive", "--input-archive", str(archive),
                 "--symbols", "BTC",
                 "--start", "2025-12-20T00:00:00Z", "--end", "2025-12-21T23:00:00Z",
                 "--cache-dir", str(cache_dir),
                 "--min-daily-volume-usd", "0",
                 "--allow-partial", "--allow-temp-archive-paths"],
                capture_output=True, text=True, cwd=str(REPO_ROOT),
            )
            manifest = json.loads((cache_dir / "provenance.json").read_text())
            req = manifest.get("request_params") or {}
            self.assertEqual(req.get("min_daily_volume_usd_requested"), 0.0)
            self.assertGreaterEqual(float(req.get("min_daily_volume_usd_effective", 0)), 5_000_000.0)
            vc = ((manifest.get("symbols") or {}).get("BTC") or {}).get("volume_coverage") or {}
            self.assertFalse(vc.get("volume_filter_ok"))


if __name__ == "__main__":
    unittest.main()
