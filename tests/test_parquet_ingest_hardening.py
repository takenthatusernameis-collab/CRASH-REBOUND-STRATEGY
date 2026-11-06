"""Track-4(d) ingest hardening: Parquet archive ingestion (synthetic, non-evidence).

Validates that the fetch script's archive reader accepts `.parquet` files
(single- and multi-symbol containers), that checksum/provenance fields are
populated, and that the manifest volume_coverage integration works end-to-end.
No real market data/perf evidence.
Compatible with pytest and unittest.
"""
from __future__ import annotations
import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
START = "2025-01-01T00:00:00+00:00"
END = "2025-01-01T03:00:00+00:00"
EXPECTED_BARS = 4
START_MS = 1735689600000

try:
    import pyarrow as pa  # type: ignore
    import pyarrow.parquet as pq  # type: ignore
    HAS_PARQUET = True
except Exception:  # pragma: no cover
    HAS_PARQUET = False


def _candles(close, vol, n=EXPECTED_BARS):
    out = []
    for i in range(n):
        ts = START_MS + i * 3_600_000
        out.append({"timestamp": f"2025-01-01T{i:02d}:00:00+00:00", "timestamp_ms": ts,
                    "open": close, "high": close * 1.01, "low": close * 0.99,
                    "close": close, "volume": vol})
    return out


def _run(cmd):
    e = os.environ.copy(); e["PYTHONPATH"] = str(REPO_ROOT)
    return subprocess.run([sys.executable] + cmd, cwd=str(REPO_ROOT), env=e, capture_output=True, text=True)


@unittest.skipUnless(HAS_PARQUET, "pyarrow not installed")
class TestParquetIngestHardening(unittest.TestCase):
    def _tmp(self):
        td = tempfile.TemporaryDirectory(); self.addCleanup(td.cleanup); return Path(td.name)

    def _write_per_symbol_parquet(self, tmp, sym, close, vol):
        p = tmp / f"{sym}.parquet"
        table = pa.table({
            "symbol": pa.array([sym] * EXPECTED_BARS),
            "timestamp": pa.array([c["timestamp"] for c in _candles(close, vol)]),
            "timestamp_ms": pa.array([c["timestamp_ms"] for c in _candles(close, vol)]),
            "open": pa.array([c["open"] for c in _candles(close, vol)]),
            "high": pa.array([c["high"] for c in _candles(close, vol)]),
            "low": pa.array([c["low"] for c in _candles(close, vol)]),
            "close": pa.array([c["close"] for c in _candles(close, vol)]),
            "volume": pa.array([c["volume"] for c in _candles(close, vol)]),
        })
        pq.write_table(table, str(p))
        return p

    def test_read_symbol_candles_from_parquet_per_symbol_file(self):
        from scripts.fetch_hyperliquid_candles import _read_symbol_candles_from_file
        tmp = self._tmp()
        self._write_per_symbol_parquet(tmp, "AAA", 100.0, 100000.0)
        candles, meta = _read_symbol_candles_from_file(tmp / "AAA.parquet", "AAA")
        self.assertEqual(len(candles), EXPECTED_BARS)
        self.assertAlmostEqual(candles[0]["close"], 100.0)
        self.assertEqual(meta.get("format"), "parquet")
        self.assertFalse(meta.get("multi_symbol_container"))

    def test_read_symbol_candles_from_parquet_multi_symbol_container(self):
        from scripts.fetch_hyperliquid_candles import _read_symbol_candles_from_file
        tmp = self._tmp()
        rows = []
        for sym, close, vol in [("AAA", 100.0, 100000.0), ("ETH", 2000.0, 5000.0)]:
            for c in _candles(close, vol):
                rows.append({"symbol": sym, **c})
        table = pa.table({k: pa.array([r[k] for r in rows]) for k in rows[0]})
        pq.write_table(table, str(tmp / "all.parquet"))
        candles, meta = _read_symbol_candles_from_file(tmp / "all.parquet", "AAA")
        self.assertEqual(len(candles), EXPECTED_BARS)
        self.assertAlmostEqual(candles[0]["close"], 100.0)
        self.assertEqual(meta.get("format"), "parquet")
        self.assertTrue(meta.get("multi_symbol_container"))

    def test_ingest_archive_parquet_directory_discovery(self):
        from scripts.fetch_hyperliquid_candles import ingest_archive
        tmp = self._tmp()
        self._write_per_symbol_parquet(tmp, "ETH", 2000.0, 5000.0)
        candles, meta = ingest_archive(tmp, "ETH")
        self.assertEqual(len(candles), EXPECTED_BARS)
        self.assertEqual(meta.get("source"), "user_supplied_archive")
        self.assertEqual(len(meta.get("sha256") or ""), 64)

    def test_fetch_script_parquet_container_manifest_volume_fields(self):
        tmp = self._tmp()
        container = tmp / "all.parquet"
        cache = tmp / "cache_hl"
        rows = []
        for sym, close, vol in [("AAA", 100.0, 100000.0), ("LOW", 1.0, 1.0)]:
            for c in _candles(close, vol):
                rows.append({"symbol": sym, **c})
        table = pa.table({k: pa.array([r[k] for r in rows]) for k in rows[0]})
        pq.write_table(table, str(container))
        r = _run([str(SCRIPTS / "fetch_hyperliquid_candles.py"), "--source", "archive",
                  "--input-archive", str(container), "--symbols", "AAA,LOW", "--start", START,
                  "--end", END, "--cache-dir", str(cache), "--min-daily-volume-usd", "5000000"])
        self.assertEqual(r.returncode, 0, f"parquet container ingest failed:\nstdout={r.stdout}\nstderr={r.stderr}")
        manifest = json.loads((cache / "provenance.json").read_text())
        self.assertTrue(manifest["summary"]["all_complete"])
        self.assertTrue(manifest["symbols"]["AAA"]["volume_coverage"]["volume_filter_ok"])
        self.assertFalse(manifest["symbols"]["LOW"]["volume_coverage"]["volume_filter_ok"])
        self.assertEqual(len(manifest["symbols"]["AAA"].get("sha256") or ""), 64)


if __name__ == "__main__":
    unittest.main()