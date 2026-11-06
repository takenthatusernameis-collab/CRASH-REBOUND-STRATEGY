"""Track-4(d) ingest hardening: NDJSON/JSONL archive ingestion (synthetic, non-evidence).
Validates multi-symbol NDJSON container parsing, checksum/provenance fields, and
manifest volume_coverage integration via fetch script. No real market data/perf evidence.
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

def _candles(close, vol, n=EXPECTED_BARS):
    out=[]
    for i in range(n):
        ts=START_MS+i*3_600_000
        # Varied (non-flat) bars so the synthetic/flat-series guard does not reject
        # this non-evidence pipeline fixture.
        c=close*(1.0+0.002*i); v=vol*(1.0+0.05*(i%3))
        out.append({"timestamp":f"2025-01-01T{i:02d}:00:00+00:00","timestamp_ms":ts,
                    "open":c,"high":c*1.01,"low":c*0.99,"close":c,"volume":v})
    return out

def _run(cmd):
    e=os.environ.copy(); e["PYTHONPATH"]=str(REPO_ROOT)
    return subprocess.run([sys.executable]+cmd,cwd=str(REPO_ROOT),env=e,capture_output=True,text=True)

class TestNDJSONIngestHardening(unittest.TestCase):
    def _tmp(self):
        td=tempfile.TemporaryDirectory(); self.addCleanup(td.cleanup); return Path(td.name)

    def test_read_symbol_candles_from_ndjson_multi_symbol_container(self):
        from scripts.fetch_hyperliquid_candles import _read_symbol_candles_from_file
        tmp=self._tmp(); p=tmp/"all.ndjson"
        rows=[]
        for sym,close,vol in [("AAA",100.0,100000.0),("ETH",2000.0,5000.0)]:
            for c in _candles(close,vol): rows.append({"symbol":sym, **c})
        p.write_text("\n".join(json.dumps(r) for r in rows)+"\n")
        candles, meta = _read_symbol_candles_from_file(p, "AAA")
        self.assertEqual(len(candles), EXPECTED_BARS)
        self.assertAlmostEqual(candles[0]["close"], 100.0)
        self.assertEqual(meta.get("format"), "ndjson")
        self.assertTrue(meta.get("multi_symbol_container"))

    def test_read_symbol_candles_from_ndjson_per_symbol_lines(self):
        from scripts.fetch_hyperliquid_candles import _read_symbol_candles_from_file
        tmp=self._tmp(); p=tmp/"AAA.ndjson"
        p.write_text("\n".join(json.dumps(c) for c in _candles(100.0,100000.0))+"\n")
        candles, meta = _read_symbol_candles_from_file(p, "AAA")
        self.assertEqual(len(candles), EXPECTED_BARS)
        self.assertEqual(meta.get("format"), "ndjson")
        self.assertFalse(meta.get("multi_symbol_container"))

    def test_ingest_archive_ndjson_directory_discovery(self):
        from scripts.fetch_hyperliquid_candles import ingest_archive
        tmp=self._tmp(); (tmp/"ETH.ndjson").write_text("\n".join(json.dumps(c) for c in _candles(2000.0,5000.0))+"\n")
        candles, meta = ingest_archive(tmp, "ETH")
        self.assertEqual(len(candles), EXPECTED_BARS)
        self.assertEqual(meta.get("source"), "user_supplied_archive")
        self.assertEqual(len(meta.get("sha256") or ""), 64)

    def test_fetch_script_ndjson_container_manifest_volume_fields(self):
        tmp=self._tmp(); container=tmp/"all.jsonl"; cache=tmp/"cache_hl"
        rows=[]
        for sym,close,vol in [("AAA",100.0,100000.0),("LOW",1.0,1.0)]:
            for c in _candles(close,vol): rows.append({"symbol":sym, **c})
        container.write_text("\n".join(json.dumps(r) for r in rows)+"\n")
        r=_run([str(SCRIPTS/"fetch_hyperliquid_candles.py"),"--source","archive","--input-archive",str(container),
                "--symbols","AAA,LOW","--start",START,"--end",END,"--cache-dir",str(cache),
                "--min-daily-volume-usd","5000000"])
        self.assertEqual(r.returncode, 0, f"ndjson container ingest failed:\nstdout={r.stdout}\nstderr={r.stderr}")
        manifest=json.loads((cache/"provenance.json").read_text())
        self.assertTrue(manifest["summary"]["all_complete"])
        self.assertTrue(manifest["symbols"]["AAA"]["volume_coverage"]["volume_filter_ok"])
        self.assertFalse(manifest["symbols"]["LOW"]["volume_coverage"]["volume_filter_ok"])
        self.assertEqual(len(manifest["symbols"]["AAA"].get("sha256") or ""), 64)

if __name__ == "__main__":
    unittest.main()
