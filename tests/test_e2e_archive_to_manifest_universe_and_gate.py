"""Deterministic end-to-end pipeline test (synthetic, sandboxed, NON-EVIDENCE).

Proves pipeline correctness only — NOT market performance, NOT real campaign evidence.
Covers: archive -> manifest/provenance (fetch script) -> derive_verified_universe
from verified local caches -> provenance/gate refusal on incomplete data and
gate acceptance on complete verified manifest. All data is synthetic, generated
in tmp paths, clearly marked performance_evidence=false / fabricated_data=false
where scripts compute flags. No real market data is used or claimed.

Compatible with pytest and unittest (no pytest-only fixtures required).
"""
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"

# Small synthetic hourly window (4 bars) for fast deterministic tests.
# NOT the 283-day spec window; validates pipeline mechanics only.
START = "2025-01-01T00:00:00+00:00"
END = "2025-01-01T03:00:00+00:00"
EXPECTED_BARS = 4
START_MS = 1735689600000
END_MS = 1735700400000


def _make_candles(symbol: str, n: int, start_ms: int, close: float, base_vol: float):
    out = []
    for i in range(n):
        ts = start_ms + i * 3_600_000
        iso = f"2025-01-01T{i:02d}:00:00+00:00"
        # Varied (non-flat) bars so the synthetic/flat-series guard does not reject
        # this non-evidence pipeline fixture. Keeps volume comfortably above/below
        # the 5M threshold per symbol class.
        c = close * (1.0 + 0.002 * i)
        v = base_vol * (1.0 + 0.05 * (i % 3))
        out.append({
            "timestamp": iso,
            "timestamp_ms": ts,
            "open": c,
            "high": c * 1.01,
            "low": c * 0.99,
            "close": c,
            "volume": v,
        })
    return out


def _write_archive(archive_dir: Path, symbols):
    archive_dir.mkdir(parents=True, exist_ok=True)
    for sym, candles in symbols.items():
        (archive_dir / f"{sym}.json").write_text(json.dumps(candles))


def _run(cmd, cwd=None, env=None):
    e = os.environ.copy()
    e["PYTHONPATH"] = str(REPO_ROOT)
    if env:
        e.update(env)
    p = subprocess.run(
        [sys.executable] + cmd,
        cwd=str(cwd or REPO_ROOT),
        env=e,
        capture_output=True,
        text=True,
    )
    return p


class TestE2EArchiveManifestUniverseGate(unittest.TestCase):
    def _tmp(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        return Path(td.name)

    def test_e2e_archive_to_manifest_complete_pipeline(self):
        """Archive (per-symbol JSON) -> fetch script produces complete manifest + caches."""
        tmp_path = self._tmp()
        archive = tmp_path / "archive"
        cache = tmp_path / "cache_hl"
        symbols = {
            "AAA": _make_candles("AAA", EXPECTED_BARS, START_MS, close=100.0, base_vol=100_000.0),
            "ETH": _make_candles("ETH", EXPECTED_BARS, START_MS, close=2000.0, base_vol=5_000.0),
        }
        _write_archive(archive, symbols)

        r = _run([
            str(SCRIPTS / "fetch_hyperliquid_candles.py"),
            "--source", "archive",
            "--input-archive", str(archive),
            "--symbols", "AAA", "ETH",
            "--start", START, "--end", END,
            "--cache-dir", str(cache),
            "--min-daily-volume-usd", "5000000",
        ])
        self.assertEqual(r.returncode, 0, f"fetch failed:\nstdout={r.stdout}\nstderr={r.stderr}")

        manifest_path = cache / "provenance.json"
        self.assertTrue(manifest_path.exists(), "provenance manifest not written")
        manifest = json.loads(manifest_path.read_text())
        self.assertIs(manifest.get("fabricated_data"), False)
        self.assertEqual(manifest.get("run_type"), "data_acquisition_provenance")
        self.assertEqual(manifest["target_window"]["expected_hourly_bars"], EXPECTED_BARS)
        self.assertTrue(manifest["summary"]["all_complete"])
        self.assertTrue(manifest["summary"]["ready_for_real_campaign"])
        self.assertEqual(set(manifest["summary"]["complete_symbols"]), {"AAA", "ETH"})
        for sym in ("AAA", "ETH"):
            info = manifest["symbols"][sym]
            self.assertEqual(info["status"], "ok")
            cov = info["coverage"]
            self.assertTrue(cov["complete_for_target_window"])
            self.assertEqual(cov["observed_in_window_bars"], EXPECTED_BARS)
            self.assertEqual(cov["expected_hourly_bars"], EXPECTED_BARS)
            self.assertEqual(cov["gap_count"], 0)
            self.assertTrue(info.get("sha256"))
            self.assertTrue((cache / "candles" / f"{sym}.json").exists(), f"cache for {sym} missing")

    def test_e2e_incomplete_archive_refused_by_fetch_gate(self):
        """Incomplete archive (missing bars) -> fetch script returns non-zero and marks incomplete."""
        tmp_path = self._tmp()
        archive = tmp_path / "archive"
        cache = tmp_path / "cache_hl"
        symbols = {"AAA": _make_candles("AAA", 2, START_MS, close=100.0, base_vol=100_000.0)}
        _write_archive(archive, symbols)

        r = _run([
            str(SCRIPTS / "fetch_hyperliquid_candles.py"),
            "--source", "archive", "--input-archive", str(archive),
            "--symbols", "AAA", "--start", START, "--end", END, "--cache-dir", str(cache),
        ])
        self.assertNotEqual(r.returncode, 0, f"incomplete archive must be refused by default gate:\n{r.stdout}\n{r.stderr}")
        manifest = json.loads((cache / "provenance.json").read_text())
        self.assertFalse(manifest["summary"]["all_complete"])
        self.assertFalse(manifest["summary"]["ready_for_real_campaign"])
        self.assertEqual(manifest["symbols"]["AAA"]["status"], "incomplete")
        self.assertFalse(manifest["symbols"]["AAA"]["coverage"]["complete_for_target_window"])
        self.assertEqual(manifest["symbols"]["AAA"]["coverage"]["observed_in_window_bars"], 2)

    def test_e2e_derive_verified_universe_from_verified_caches(self):
        """Complete manifest+caches -> derive_verified_universe selects by volume threshold."""
        tmp_path = self._tmp()
        archive = tmp_path / "archive"
        cache = tmp_path / "cache_hl"
        symbols = {
            "AAA": _make_candles("AAA", EXPECTED_BARS, START_MS, close=100.0, base_vol=100_000.0),
            "LOW": _make_candles("LOW", EXPECTED_BARS, START_MS, close=1.0, base_vol=1.0),
            "ETH": _make_candles("ETH", EXPECTED_BARS, START_MS, close=2000.0, base_vol=5_000.0),
        }
        _write_archive(archive, symbols)
        r = _run([
            str(SCRIPTS / "fetch_hyperliquid_candles.py"),
            "--source", "archive", "--input-archive", str(archive),
            "--symbols", "AAA", "LOW", "ETH",
            "--start", START, "--end", END, "--cache-dir", str(cache),
        ])
        self.assertEqual(r.returncode, 0, r.stderr)

        universe_out = tmp_path / "universe_verified.json"
        r2 = _run([
            str(SCRIPTS / "derive_verified_universe.py"),
            "--manifest", str(cache / "provenance.json"),
            "--cache-dir", str(cache),
            "--min-24h-volume-usd", "5000000",
            "--output", str(universe_out),
        ])
        self.assertEqual(r2.returncode, 0, f"derive failed:\n{r2.stdout}\n{r2.stderr}")
        uni = json.loads(universe_out.read_text())
        self.assertEqual(uni["run_type"], "verified_universe_derivation")
        self.assertIs(uni["performance_evidence"], False)
        self.assertIs(uni["fabricated_data"], False)
        self.assertIn("AAA", uni["selected_symbols"])
        self.assertIn("ETH", uni["selected_symbols"])
        self.assertNotIn("LOW", uni["selected_symbols"])
        self.assertFalse(uni["report"]["LOW"]["selected"])

    def test_e2e_provenance_gate_refuses_incomplete_manifest(self):
        """Provenance validator/run_real gate must refuse incomplete or mismatched manifests."""
        from src.data.provenance import validate_provenance, require_verified_provenance, ProvenanceError

        tmp_path = self._tmp()
        incomplete = {
            "fabricated_data": False,
            "real_market_data_intended": True,
            "target_window": {"start": START, "end": END, "expected_hourly_bars": EXPECTED_BARS},
            "symbols": {
                "AAA": {
                    "status": "incomplete",
                    "coverage": {
                        "expected_hourly_bars": EXPECTED_BARS,
                        "observed_in_window_bars": 2,
                        "gap_count": 0,
                        "complete_for_target_window": False,
                    },
                }
            },
        }
        ok, errs = validate_provenance(incomplete, require_complete=True, start=START, end=END)
        self.assertFalse(ok)
        self.assertTrue(any("incomplete" in e.lower() or "not all" in e.lower() or "complete" in e.lower() for e in errs))

        mpath = tmp_path / "prov.json"
        mpath.write_text(json.dumps(incomplete))
        with self.assertRaises(ProvenanceError):
            require_verified_provenance(mpath, require_complete=True, start=START, end=END)

        bad = dict(incomplete)
        bad["fabricated_data"] = True
        bad["symbols"]["AAA"]["status"] = "ok"
        bad["symbols"]["AAA"]["coverage"]["complete_for_target_window"] = True
        bad["symbols"]["AAA"]["coverage"]["observed_in_window_bars"] = EXPECTED_BARS
        ok2, errs2 = validate_provenance(bad, require_complete=True, start=START, end=END)
        self.assertFalse(ok2)
        self.assertTrue(any("fabricated" in e.lower() for e in errs2))

    def test_e2e_provenance_gate_accepts_complete_small_window_manifest(self):
        """A complete, non-fabricated small-window manifest passes validation (pipeline correctness)."""
        from src.data.provenance import validate_provenance

        complete = {
            "fabricated_data": False,
            "real_market_data_intended": True,
            "target_window": {"start": START, "end": END, "expected_hourly_bars": EXPECTED_BARS},
            "symbols": {
                "AAA": {
                    "status": "ok",
                    "synthetic_check": {"is_synthetic": False, "reason": "varied_series_ok"},
                    "coverage": {
                        "expected_hourly_bars": EXPECTED_BARS,
                        "observed_in_window_bars": EXPECTED_BARS,
                        "gap_count": 0,
                        "complete_for_target_window": True,
                    },
                }
            },
            "summary": {"all_complete": True, "ready_for_real_campaign": True, "complete_symbols": ["AAA"]},
        }
        ok, errs = validate_provenance(complete, require_complete=True, start=START, end=END)
        self.assertTrue(ok, errs)

    def test_e2e_multi_symbol_archive_discovery(self):
        """Archive directory discovery finds per-symbol files; fetch ingests them."""
        tmp_path = self._tmp()
        archive = tmp_path / "archive"
        cache = tmp_path / "cache_hl"
        _write_archive(archive, {
            "BTC": _make_candles("BTC", EXPECTED_BARS, START_MS, close=50000.0, base_vol=200.0),
            "ETH": _make_candles("ETH", EXPECTED_BARS, START_MS, close=3000.0, base_vol=3000.0),
            "SOL": _make_candles("SOL", EXPECTED_BARS, START_MS, close=100.0, base_vol=100000.0),
        })
        r = _run([
            str(SCRIPTS / "fetch_hyperliquid_candles.py"),
            "--source", "archive", "--input-archive", str(archive),
            "--symbols", "BTC,ETH,SOL",
            "--start", START, "--end", END, "--cache-dir", str(cache),
        ])
        self.assertEqual(r.returncode, 0, f"{r.stdout}\n{r.stderr}")
        manifest = json.loads((cache / "provenance.json").read_text())
        self.assertEqual(manifest["summary"]["symbols_complete"], 3)
        self.assertTrue(manifest["summary"]["all_complete"])

    def test_e2e_multi_symbol_single_json_container_volume_coverage_fields(self):
        """Single JSON container holding multiple symbols -> manifest has volume_coverage + volume_filter_ok.

        Track-4 expansion (synthetic non-evidence): validates container ingest path and
        per-symbol volume coverage manifest fields without claiming performance evidence.
        """
        tmp_path = self._tmp()
        container = tmp_path / "all.json"
        cache = tmp_path / "cache_hl"
        payload = {
            "AAA": _make_candles("AAA", EXPECTED_BARS, START_MS, close=100.0, base_vol=100_000.0),
            "LOW": _make_candles("LOW", EXPECTED_BARS, START_MS, close=1.0, base_vol=1.0),
            "ETH": _make_candles("ETH", EXPECTED_BARS, START_MS, close=2000.0, base_vol=5_000.0),
        }
        container.write_text(json.dumps(payload))
        r = _run([
            str(SCRIPTS / "fetch_hyperliquid_candles.py"),
            "--source", "archive", "--input-archive", str(container),
            "--symbols", "AAA,LOW,ETH",
            "--start", START, "--end", END, "--cache-dir", str(cache),
            "--min-daily-volume-usd", "5000000",
        ])
        self.assertEqual(r.returncode, 0, f"container ingest failed:\nstdout={r.stdout}\nstderr={r.stderr}")
        manifest = json.loads((cache / "provenance.json").read_text())
        self.assertIs(manifest.get("fabricated_data"), False)
        self.assertTrue(manifest["summary"]["all_complete"])
        for sym in ("AAA", "LOW", "ETH"):
            info = manifest["symbols"][sym]
            self.assertIn("volume_coverage", info, f"{sym} missing volume_coverage")
            vc = info["volume_coverage"]
            self.assertEqual(vc.get("min_daily_volume_usd"), 5000000)
            self.assertIn("volume_filter_ok", vc)
            self.assertEqual(vc.get("bars_checked"), EXPECTED_BARS)
        self.assertTrue(manifest["symbols"]["AAA"]["volume_coverage"]["volume_filter_ok"])
        self.assertTrue(manifest["symbols"]["ETH"]["volume_coverage"]["volume_filter_ok"])
        self.assertFalse(manifest["symbols"]["LOW"]["volume_coverage"]["volume_filter_ok"])

    def test_e2e_multi_symbol_single_csv_container_volume_coverage_fields(self):
        """Single CSV container with symbol column -> manifest has volume_coverage fields."""
        tmp_path = self._tmp()
        container = tmp_path / "all.csv"
        cache = tmp_path / "cache_hl"
        rows = []
        for sym, close, base_vol in (("AAA", 100.0, 100_000.0), ("ETH", 2000.0, 5_000.0)):
            for c in _make_candles(sym, EXPECTED_BARS, START_MS, close=close, base_vol=base_vol):
                rows.append({
                    "symbol": sym,
                    "timestamp": c["timestamp"],
                    "open": c["open"], "high": c["high"], "low": c["low"], "close": c["close"], "volume": c["volume"],
                })
        with container.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["symbol", "timestamp", "open", "high", "low", "close", "volume"])
            w.writeheader()
            w.writerows(rows)
        r = _run([
            str(SCRIPTS / "fetch_hyperliquid_candles.py"),
            "--source", "archive", "--input-archive", str(container),
            "--symbols", "AAA,ETH",
            "--start", START, "--end", END, "--cache-dir", str(cache),
            "--min-daily-volume-usd", "5000000",
        ])
        self.assertEqual(r.returncode, 0, f"CSV container ingest failed:\nstdout={r.stdout}\nstderr={r.stderr}")
        manifest = json.loads((cache / "provenance.json").read_text())
        self.assertTrue(manifest["summary"]["all_complete"])
        for sym in ("AAA", "ETH"):
            vc = manifest["symbols"][sym]["volume_coverage"]
            self.assertTrue(vc["volume_filter_ok"], f"{sym} should pass volume filter")
            self.assertIsNotNone(vc.get("observed_min_24h_usd_volume"))

    def test_e2e_run_real_campaign_partial_not_evidence_tmp_repo(self):
        """Sandboxed run_real_campaign --allow-partial-not-evidence marks performance_evidence=false.

        Pipeline correctness only (synthetic 4-bar subset window). NOT spec evidence, NOT a 283-day
        campaign, NOT performance evidence. Uses tmp repo layout to avoid mutating real artifacts.
        Overrides TARGET_START/END in the sandboxed wrapper for small-window pipeline validation;
        production spec-window safety remains enforced in run_real_campaign.py.
        """
        tmp_path = self._tmp()
        archive = tmp_path / "archive"
        cache = tmp_path / "cache_hl"
        _write_archive(archive, {
            "AAA": _make_candles("AAA", EXPECTED_BARS, START_MS, close=100.0, base_vol=100_000.0),
            "ETH": _make_candles("ETH", EXPECTED_BARS, START_MS, close=2000.0, base_vol=5_000.0),
        })
        r = _run([
            str(SCRIPTS / "fetch_hyperliquid_candles.py"),
            "--source", "archive", "--input-archive", str(archive),
            "--symbols", "AAA,ETH", "--start", START, "--end", END, "--cache-dir", str(cache),
        ])
        self.assertEqual(r.returncode, 0, r.stderr)
        manifest = json.loads((cache / "provenance.json").read_text())
        partial_manifest = dict(manifest)
        partial_manifest["summary"] = dict(manifest.get("summary") or {})
        partial_manifest["summary"]["all_complete"] = False
        partial_manifest["summary"]["ready_for_real_campaign"] = False
        partial_manifest["symbols"]["BBB"] = {
            "status": "incomplete",
            "synthetic_check": {"is_synthetic": False, "reason": "varied_series_ok"},
            "coverage": {"expected_hourly_bars": EXPECTED_BARS, "observed_in_window_bars": 1, "gap_count": 0, "complete_for_target_window": False},
        }
        pmanifest = cache / "partial_provenance.json"
        pmanifest.write_text(json.dumps(partial_manifest, indent=2))

        fake_repo = tmp_path / "repo"
        (fake_repo / "research_state").mkdir(parents=True)
        wrapper = tmp_path / "run_partial.py"
        wrapper.write_text(
            "import sys; "
            "sys.path.insert(0, r'" + str(REPO_ROOT).replace("'", "\\'") + "'); "
            "import scripts.run_real_campaign as r; "
            "from pathlib import Path; "
            "r.REPO_ROOT = Path(r'" + str(fake_repo).replace("'", "\\'") + "'); "
            "sys.argv=['x','--cache-dir',r'" + str(cache).replace("'", "\\'") + "',"
            "'--manifest',r'" + str(pmanifest).replace("'", "\\'") + "',"
            "'--output-prefix','campaign_results_partial_debug','--min-symbols','1',"
            "'--allow-partial-not-evidence',"
            "'--window-start',r'" + START + "','--window-end',r'" + END + "']; "
            "raise SystemExit(r.main())"
        )

        e = os.environ.copy(); e["PYTHONPATH"] = str(REPO_ROOT)
        p = subprocess.run([sys.executable, str(wrapper)], cwd=str(REPO_ROOT), env=e, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, f"partial run failed:\nstdout={p.stdout}\nstderr={p.stderr}")
        out = fake_repo / "research_state" / "campaign_results_partial_debug.json"
        self.assertTrue(out.exists(), f"partial artifact missing; stdout={p.stdout} stderr={p.stderr}")
        art = json.loads(out.read_text())
        self.assertIs(art.get("performance_evidence"), False)
        self.assertIs(art.get("real_market_data"), True)
        self.assertIs(art.get("fabricated_data"), False)
        self.assertTrue(art.get("partial_universe_not_evidence"))
        self.assertEqual(art.get("research_status"), "NOT_EVIDENCE_PARTIAL_UNIVERSE")
        self.assertIn("NOT performance evidence", art.get("evidence_warning") or "")
        self.assertIn("AAA", art.get("data_provenance", {}).get("symbols_loaded", []))



if __name__ == "__main__":
    unittest.main()
