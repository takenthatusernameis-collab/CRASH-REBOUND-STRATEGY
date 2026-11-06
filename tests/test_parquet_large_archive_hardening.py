"""Track-4(d) ingest hardening: large multi-row-group Parquet archive ingestion.

Validates the streaming parquet reader on archives that are too large to fit in
memory comfortably: multiple row groups, per-symbol filtering in a single pass,
column projection, and full-window (6792-bar) coverage/provenance gating through
the fetch script. Synthetic data only — no real market evidence.
Compatible with pytest and unittest.
"""
from __future__ import annotations
import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
START = "2025-12-20T00:00:00+00:00"
END = "2026-09-28T23:00:00+00:00"
EXPECTED_BARS = 6792
START_MS = 1766188800000

try:
    import pyarrow as pa  # type: ignore
    import pyarrow.parquet as pq  # type: ignore
    HAS_PARQUET = True
except Exception:  # pragma: no cover
    HAS_PARQUET = False


def _run(cmd):
    e = os.environ.copy(); e["PYTHONPATH"] = str(REPO_ROOT)
    return subprocess.run([sys.executable] + cmd, cwd=str(REPO_ROOT), env=e, capture_output=True, text=True)


def _multi_rowgroup_parquet(path, symbols, row_group_size=1024):
    rows = []
    for sym, close, vol in symbols:
        for i in range(EXPECTED_BARS):
            ts = START_MS + i * 3_600_000
            rows.append({"symbol": sym, "timestamp_ms": ts, "open": close, "high": close * 1.02,
                         "low": close * 0.98, "close": close, "volume": vol})
    tbl = pa.table({k: pa.array([r[k] for r in rows]) for k in rows[0]})
    pq.write_table(tbl, str(path), row_group_size=row_group_size)
    return pq.ParquetFile(str(path)).metadata.num_row_groups


@unittest.skipUnless(HAS_PARQUET, "pyarrow not installed")
class TestParquetLargeArchiveHardening(unittest.TestCase):
    def _tmp(self):
        td = tempfile.TemporaryDirectory(); self.addCleanup(td.cleanup); return Path(td.name)

    def test_streaming_multi_rowgroup_reads_full_window(self):
        from scripts.fetch_hyperliquid_candles import _read_symbol_candles_from_parquet
        tmp = self._tmp()
        p = tmp / "archive.parquet"
        nrg = _multi_rowgroup_parquet(p, [("BTC", 60000.0, 2.0e9), ("ETH", 3000.0, 1.0e9)], row_group_size=1024)
        self.assertGreater(nrg, 1)
        candles, meta = _read_symbol_candles_from_parquet(p, "BTC")
        self.assertEqual(len(candles), EXPECTED_BARS)
        self.assertEqual(candles[0]["timestamp_ms"], START_MS)
        self.assertEqual(candles[-1]["timestamp_ms"], START_MS + (EXPECTED_BARS - 1) * 3_600_000)
        self.assertTrue(meta["multi_symbol_container"])
        self.assertGreater(meta["row_groups"], 1)
        self.assertEqual(meta["distinct_symbols_seen"], 2)

    def test_streaming_multi_rowgroup_per_symbol_file_single_symbol(self):
        from scripts.fetch_hyperliquid_candles import _read_symbol_candles_from_parquet
        tmp = self._tmp()
        p = tmp / "BTC.parquet"
        _multi_rowgroup_parquet(p, [("BTC", 60000.0, 2.0e9)], row_group_size=512)
        candles, meta = _read_symbol_candles_from_parquet(p, "BTC")
        self.assertEqual(len(candles), EXPECTED_BARS)
        self.assertFalse(meta["multi_symbol_container"])
        self.assertEqual(meta["distinct_symbols_seen"], 1)

    def test_large_archive_fetch_script_full_window_provenance(self):
        tmp = self._tmp()
        container = tmp / "archive.parquet"
        cache = tmp / "cache_hl"
        _multi_rowgroup_parquet(container, [("BTC", 60000.0, 2.0e9), ("ETH", 3000.0, 1.0e9)], row_group_size=1024)
        r = _run([str(SCRIPTS / "fetch_hyperliquid_candles.py"), "--source", "archive",
                  "--input-archive", str(container), "--symbols", "BTC,ETH", "--start", START, "--end", END,
                  "--cache-dir", str(cache), "--min-daily-volume-usd", "5000000"])
        self.assertEqual(r.returncode, 0, f"large parquet ingest failed:\nstdout={r.stdout}\nstderr={r.stderr}")
        manifest = json.loads((cache / "provenance.json").read_text())
        self.assertTrue(manifest["summary"]["all_complete"])
        self.assertTrue(manifest["summary"]["ready_for_real_campaign"])
        for s in ("BTC", "ETH"):
            cov = manifest["symbols"][s]["coverage"]
            self.assertEqual(cov["observed_in_window_bars"], EXPECTED_BARS)
            self.assertEqual(cov["expected_hourly_bars"], EXPECTED_BARS)
            self.assertTrue(cov["complete_for_target_window"])
            self.assertEqual(len(manifest["symbols"][s].get("sha256") or ""), 64)
            self.assertTrue(manifest["symbols"][s]["volume_coverage"]["volume_filter_ok"])

    def test_large_archive_missing_symbol_raises(self):
        from scripts.fetch_hyperliquid_candles import _read_symbol_candles_from_parquet
        tmp = self._tmp()
        p = tmp / "archive.parquet"
        _multi_rowgroup_parquet(p, [("BTC", 60000.0, 2.0e9)], row_group_size=512)
        with self.assertRaises(ValueError):
            _read_symbol_candles_from_parquet(p, "SOL")


if __name__ == "__main__":
    unittest.main()