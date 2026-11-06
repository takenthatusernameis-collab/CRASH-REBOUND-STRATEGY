"""Track-4(d) streaming ingest hardening: row-by-row archive readers + incremental checksums.

Validates src/data/streaming_ingest.py row-by-row readers (JSONL/NDJSON/CSV/Parquet),
incremental per-file/per-symbol sha256, and the streaming-safe contract that a reader
never buffers the whole archive in memory. Synthetic data only — no real market evidence.
Compatible with pytest and unittest.
"""
from __future__ import annotations
import json, os, tempfile, unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
START_MS = 1735689600000  # 2025-01-01T00:00:00Z


def _candles(close, vol, n=4):
    out = []
    for i in range(n):
        ts = START_MS + i * 3_600_000
        out.append({"timestamp_ms": ts, "open": close, "high": close * 1.01,
                    "low": close * 0.99, "close": close, "volume": vol})
    return out


class TestStreamingIngestHardening(unittest.TestCase):
    def _tmp(self):
        td = tempfile.TemporaryDirectory(); self.addCleanup(td.cleanup); return Path(td.name)

    def test_streaming_jsonl_reader_yields_rows_incrementally(self):
        from src.data.streaming_ingest import iter_jsonl_rows
        tmp = self._tmp()
        p = tmp / "all.jsonl"
        p.write_text("\n".join(json.dumps({"symbol": "AAA", **c}) for c in _candles(100.0, 100000.0)) + "\n")
        rows = list(iter_jsonl_rows(p))
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0]["symbol"], "AAA")
        self.assertIn("timestamp_ms", rows[0])

    def test_streaming_jsonl_reader_skips_malformed_lines(self):
        from src.data.streaming_ingest import iter_jsonl_rows
        tmp = self._tmp()
        p = tmp / "bad.jsonl"
        p.write_text("{not json}\n" + "\n".join(json.dumps({"symbol": "AAA", **c}) for c in _candles(100.0, 100000.0)) + "\n\n")
        rows = list(iter_jsonl_rows(p))
        self.assertEqual(len(rows), 4)

    def test_streaming_csv_reader_yields_rows(self):
        from src.data.streaming_ingest import iter_csv_rows
        tmp = self._tmp()
        p = tmp / "all.csv"
        import csv
        with p.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["symbol", "timestamp_ms", "open", "high", "low", "close", "volume"])
            w.writeheader()
            for c in _candles(100.0, 100000.0):
                w.writerow({"symbol": "AAA", **c})
        rows = list(iter_csv_rows(p))
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0]["symbol"], "AAA")

    def test_streaming_parquet_reader_yields_batches_not_full_file(self):
        from src.data.streaming_ingest import iter_parquet_batches
        try:
            import pyarrow as pa  # type: ignore
            import pyarrow.parquet as pq  # type: ignore
        except Exception:
            self.skipTest("pyarrow not installed")
        tmp = self._tmp()
        p = tmp / "all.parquet"
        rows = [{"symbol": "AAA", **c} for c in _candles(100.0, 100000.0, 2000)]
        tbl = pa.table({k: pa.array([r[k] for r in rows]) for k in rows[0]})
        pq.write_table(tbl, str(p), row_group_size=256)
        batches = list(iter_parquet_batches(p, batch_size=256))
        self.assertGreater(len(batches), 1)  # streaming: multiple batches, not one giant table
        total = sum(len(b.to_pylist()) for b in batches)
        self.assertEqual(total, 2000)

    def test_incremental_checksum_matches_whole_file_sha256(self):
        from src.data.streaming_ingest import sha256_file_streaming, sha256_bytes
        tmp = self._tmp()
        p = tmp / "data.bin"
        payload = b"streaming-checksum-test-payload" * 1000
        p.write_bytes(payload)
        self.assertEqual(sha256_file_streaming(p), sha256_bytes(payload))

    def test_streaming_reader_never_buffers_entire_file(self):
        """Contract: a streaming reader must expose an iterator, not a full in-memory list."""
        from src.data.streaming_ingest import iter_jsonl_rows, iter_csv_rows, iter_parquet_batches, iter_jsonl_rows as _ijr
        import inspect
        self.assertTrue(inspect.isgeneratorfunction(iter_jsonl_rows))
        self.assertTrue(inspect.isgeneratorfunction(iter_csv_rows))
        self.assertTrue(inspect.isgeneratorfunction(iter_parquet_batches))


if __name__ == "__main__":
    unittest.main()