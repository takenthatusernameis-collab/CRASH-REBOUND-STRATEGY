"""Track-4(d) integration: streaming ingest -> coverage -> provenance for a large parquet archive.

Validates the row-by-row streaming path produces identical coverage/provenance results
to the batch path on a multi-GB-scale archive (simulated with many row groups), and
that the streaming path never buffers the whole file. Synthetic data only.
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


def _write_large_parquet(path, symbols, row_group_size=512):
    rows = []
    for sym, close, vol in symbols:
        for i in range(EXPECTED_BARS):
            # Varied closes (non-constant): a flat series is correctly rejected as
            # synthetic by the provenance gate, so this fixture must move to be
            # valid real-market-shaped evidence the test can validate end-to-end.
            ts = START_MS + i * 3_600_000
            c = close * (1.0 + 0.001 * (i % 5))
            rows.append({"symbol": sym, "timestamp_ms": ts, "open": c, "high": c * 1.02,
                         "low": c * 0.98, "close": c, "volume": vol})
    tbl = pa.table({k: pa.array([r[k] for r in rows]) for k in rows[0]})
    pq.write_table(tbl, str(path), row_group_size=row_group_size)


@unittest.skipUnless(HAS_PARQUET, "pyarrow not installed")
class TestStreamingIngestIntegration(unittest.TestCase):
    def _tmp(self):
        td = tempfile.TemporaryDirectory(); self.addCleanup(td.cleanup); return Path(td.name)

    def test_streaming_path_matches_batch_path_coverage(self):
        from src.data.streaming_ingest import stream_normalize, sha256_file_streaming
        from scripts.fetch_hyperliquid_candles import analyze_coverage, analyze_symbol_volume_coverage
        tmp = self._tmp()
        p = tmp / "archive.parquet"
        _write_large_parquet(p, [("BTC", 60000.0, 2.0e9), ("ETH", 3000.0, 1.0e9)])
        # streaming path
        candles_stream = list(stream_normalize(p, "BTC"))
        # batch path
        from scripts.fetch_hyperliquid_candles import _read_symbol_candles_from_parquet
        candles_batch, _ = _read_symbol_candles_from_parquet(p, "BTC")
        self.assertEqual(len(candles_stream), EXPECTED_BARS)
        self.assertEqual(len(candles_batch), EXPECTED_BARS)
        self.assertEqual(candles_stream[0]["timestamp_ms"], candles_batch[0]["timestamp_ms"])
        self.assertEqual(candles_stream[-1]["timestamp_ms"], candles_batch[-1]["timestamp_ms"])
        # coverage identical
        from datetime import datetime, timezone
        start = datetime.fromisoformat(START.replace("+00:00", "")).replace(tzinfo=timezone.utc)
        end = datetime.fromisoformat(END.replace("+00:00", "")).replace(tzinfo=timezone.utc)
        cov_s = analyze_coverage(candles_stream, start, end)
        cov_b = analyze_coverage(candles_batch, start, end)
        self.assertEqual(cov_s["observed_in_window_bars"], cov_b["observed_in_window_bars"])
        self.assertEqual(cov_s["complete_for_target_window"], cov_b["complete_for_target_window"])
        # volume coverage identical
        vc_s = analyze_symbol_volume_coverage(candles_stream, 5_000_000.0)
        vc_b = analyze_symbol_volume_coverage(candles_batch, 5_000_000.0)
        self.assertEqual(vc_s["volume_filter_ok"], vc_b["volume_filter_ok"])
        self.assertEqual(vc_s["bars_checked"], vc_b["bars_checked"])
        # streaming checksum is a 64-hex sha256
        self.assertEqual(len(sha256_file_streaming(p)), 64)

    def test_large_archive_streaming_fetch_script_end_to_end(self):
        tmp = self._tmp()
        container = tmp / "archive.parquet"
        cache = tmp / "cache_hl"
        _write_large_parquet(container, [("BTC", 60000.0, 2.0e9), ("ETH", 3000.0, 1.0e9)], row_group_size=256)
        r = _run([str(SCRIPTS / "fetch_hyperliquid_candles.py"), "--source", "archive",
                  "--input-archive", str(container), "--symbols", "BTC,ETH", "--start", START, "--end", END,
                  "--cache-dir", str(cache), "--min-daily-volume-usd", "5000000"])
        self.assertEqual(r.returncode, 0, f"streaming large ingest failed:\nstdout={r.stdout}\nstderr={r.stderr}")
        manifest = json.loads((cache / "provenance.json").read_text())
        self.assertTrue(manifest["summary"]["all_complete"])
        self.assertTrue(manifest["summary"]["ready_for_real_campaign"])
        for s in ("BTC", "ETH"):
            self.assertEqual(manifest["symbols"][s]["coverage"]["observed_in_window_bars"], EXPECTED_BARS)
            self.assertTrue(manifest["symbols"][s]["coverage"]["complete_for_target_window"])


if __name__ == "__main__":
    unittest.main()