"""Track-4e hardening: verify cached candle file checksums against provenance manifest.

Deterministic, synthetic, non-evidence. Ensures verified-data pipelines refuse
tampered/corrupted caches when manifest provides sha256, and remain backward
compatible when sha256 is absent.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"


def _parse_iso(s: str):
    from datetime import datetime, timezone
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


START = "2025-01-01T00:00:00+00:00"
END = "2025-01-01T03:00:00+00:00"
START_MS = 1735689600000
EXP = 4


def _make_candles(n=EXP, start_ms=START_MS, close=100.0, vol=100000.0):
    out = []
    for i in range(n):
        ts = start_ms + i * 3600000
        # Varied per-bar signatures: the runtime synthetic/flat guard re-detects
        # constant OHLCV at load time, so fixtures must carry distinct signatures.
        c = close + (i % 7) * 0.5
        out.append({
            "timestamp_ms": ts,
            "timestamp": f"2025-01-01T{i:02d}:00:00+00:00",
            "open": c, "high": c * 1.01 + (i % 3), "low": c * 0.99 - (i % 2),
            "close": c, "volume": vol + (i % 5),
        })
    return out


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _manifest(cache_dir: Path, sym: str, sha256: str | None, status="ok", complete=True):
    rel = f"research_state/cache/hyperliquid/candles/{sym}.json"
    return {
        "schema_version": 1, "generated_at_utc": "x",
        "run_type": "data_acquisition_provenance",
        "real_market_data_intended": True, "fabricated_data": False,
        "target_window": {"start": START, "end": END, "expected_hourly_bars": EXP},
        "source": {"kind": "user_supplied_archive"},
        "symbols": {
            sym: {
                "symbol": sym, "status": status, "source": "user_supplied_archive",
                "sha256": sha256,
                "synthetic_check": {"is_synthetic": False, "reason": "varied_series_ok"},
                "cache_path": None,
                "coverage": {
                    "expected_hourly_bars": EXP, "observed_in_window_bars": EXP if complete else 2,
                    "coverage_pct": 100.0 if complete else 50.0, "gap_count": 0,
                    "complete_for_target_window": complete,
                    "start": START, "end": END,
                },
                "volume_coverage": {
                    "min_daily_volume_usd": 5_000_000, "observed_min_24h_usd_volume": 1e10,
                    "observed_mean_24h_usd_volume": 1e10, "bars_checked": EXP,
                    "bars_passing": EXP, "volume_filter_ok": True,
                },
            }
        },
        "summary": {
            "symbols_requested": 1, "symbols_complete": 1 if complete else 0,
            "symbols_incomplete_or_error": 0 if complete else 1,
            "all_complete": complete, "ready_for_real_campaign": complete,
            "complete_symbols": [sym] if complete else [],
        },
    }


def _run(cmd, cwd=None, env_extra=None):
    e = os.environ.copy()
    e["PYTHONPATH"] = str(REPO_ROOT)
    if env_extra:
        e.update(env_extra)
    return subprocess.run([sys.executable] + cmd, cwd=str(cwd or REPO_ROOT), env=e,
                          capture_output=True, text=True)


class TestCacheSha256Verification(unittest.TestCase):
    def _tmp(self):
        td = tempfile.TemporaryDirectory(dir=str(REPO_ROOT))
        self.addCleanup(td.cleanup)
        return Path(td.name)

    def _setup_cache(self, td: Path, sym="AAA", tamper=False, omit_sha=False):
        cache = td / "cache"
        (cache / "candles").mkdir(parents=True)
        candles = _make_candles()
        payload = json.dumps(candles).encode()
        good_sha = _sha(payload)
        if tamper:
            # keep OHLC valid but change content so sha256 differs
            candles[0]["volume"] = 999999.0
            payload = json.dumps(candles).encode()
        (cache / "candles" / f"{sym}.json").write_bytes(payload)
        manifest = _manifest(cache, sym, None if omit_sha else good_sha)
        (cache / "provenance.json").write_text(json.dumps(manifest))
        return cache

    def test_derive_universe_rejects_sha_mismatch_when_verify_enabled(self):
        td = self._tmp()
        cache = self._setup_cache(td, tamper=True)
        r = _run([
            str(SCRIPTS / "derive_verified_universe.py"),
            "--manifest", str(cache / "provenance.json"),
            "--cache-dir", str(cache),
            "--output", str(td / "u.json"),
            "--verify-cache-sha256",
        ])
        self.assertNotEqual(r.returncode, 0, f"must reject tampered cache:\n{r.stdout}\n{r.stderr}")
        out = (r.stdout + r.stderr).lower()
        self.assertTrue("sha" in out or "checksum" in out or "mismatch" in out or "hash" in out,
                        f"error must mention checksum mismatch: {out}")

    def test_derive_universe_accepts_matching_sha_when_verify_enabled(self):
        td = self._tmp()
        cache = self._setup_cache(td, tamper=False)
        r = _run([
            str(SCRIPTS / "derive_verified_universe.py"),
            "--manifest", str(cache / "provenance.json"),
            "--cache-dir", str(cache),
            "--output", str(td / "u.json"),
            "--verify-cache-sha256",
        ])
        self.assertEqual(r.returncode, 0, f"must accept matching cache:\n{r.stdout}\n{r.stderr}")
        self.assertTrue((td / "u.json").exists())

    def test_derive_universe_backward_compat_no_verify_flag(self):
        """Without --verify-cache-sha256, existing behavior preserved (no breakage)."""
        td = self._tmp()
        cache = self._setup_cache(td, tamper=True)
        r = _run([
            str(SCRIPTS / "derive_verified_universe.py"),
            "--manifest", str(cache / "provenance.json"),
            "--cache-dir", str(cache),
            "--output", str(td / "u.json"),
        ])
        # current behavior: no verification -> succeeds (backward compat)
        self.assertEqual(r.returncode, 0, f"backward compat broken:\n{r.stdout}\n{r.stderr}")

    def test_derive_universe_verify_skips_when_manifest_sha_absent(self):
        td = self._tmp()
        cache = self._setup_cache(td, tamper=False, omit_sha=True)
        r = _run([
            str(SCRIPTS / "derive_verified_universe.py"),
            "--manifest", str(cache / "provenance.json"),
            "--cache-dir", str(cache),
            "--output", str(td / "u.json"),
            "--verify-cache-sha256",
        ])
        self.assertEqual(r.returncode, 0, f"missing manifest sha should not block:\n{r.stdout}\n{r.stderr}")

    def test_run_real_campaign_rejects_tampered_cache_sha(self):
        """run_real_campaign load_verified_cache must verify sha256 when present."""
        td = self._tmp()
        cache = self._setup_cache(td, tamper=True)
        fake_repo = td / "repo"
        (fake_repo / "research_state").mkdir(parents=True)
        e = os.environ.copy()
        e["PYTHONPATH"] = str(REPO_ROOT)
        # patch REPO_ROOT via env? easier: run as module with monkeypatch isn't possible in subprocess.
        # Use a small wrapper script.
        wrapper = td / "run.py"
        wrapper.write_text(
            "import sys\n"
            "from pathlib import Path\n"
            f"sys.path.insert(0,{str(REPO_ROOT)!r})\n"
            "import scripts.run_real_campaign as rrc\n"
            f"rrc.REPO_ROOT=Path({str(fake_repo)!r})\n"
            f"sys.argv=['x','--cache-dir',{str(cache)!r},'--manifest',{str(cache/'provenance.json')!r},"
            f"'--output-prefix','out','--min-symbols','1','--allow-partial-not-evidence',"
            f"'--window-start',{START!r},'--window-end',{END!r}]\n"
            "raise SystemExit(rrc.main())\n"
        )
        r = subprocess.run([sys.executable, str(wrapper)], cwd=str(REPO_ROOT), env=e,
                           capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0, f"must reject tampered cache:\n{r.stdout}\n{r.stderr}")
        out = (r.stdout + r.stderr).lower()
        self.assertTrue("sha" in out or "checksum" in out or "mismatch" in out or "hash" in out,
                        f"error must mention checksum mismatch: {out}")

    def test_run_real_campaign_accepts_matching_cache_sha(self):
        td = self._tmp()
        cache = self._setup_cache(td, tamper=False)
        fake_repo = td / "repo"
        (fake_repo / "research_state").mkdir(parents=True)
        e = os.environ.copy()
        e["PYTHONPATH"] = str(REPO_ROOT)
        wrapper = td / "run.py"
        wrapper.write_text(
            "import sys\n"
            "from pathlib import Path\n"
            f"sys.path.insert(0,{str(REPO_ROOT)!r})\n"
            "import scripts.run_real_campaign as rrc\n"
            f"rrc.REPO_ROOT=Path({str(fake_repo)!r})\n"
            f"sys.argv=['x','--cache-dir',{str(cache)!r},'--manifest',{str(cache/'provenance.json')!r},"
            f"'--output-prefix','out','--min-symbols','1','--allow-partial-not-evidence',"
            f"'--window-start',{START!r},'--window-end',{END!r}]\n"
            "raise SystemExit(rrc.main())\n"
        )
        r = subprocess.run([sys.executable, str(wrapper)], cwd=str(REPO_ROOT), env=e,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, f"must accept matching cache:\n{r.stdout}\n{r.stderr}")

    def test_verify_cache_sha256_helper(self):
        from src.data.provenance import verify_cache_sha256, ProvenanceError
        td = self._tmp()
        p = td / "x.json"
        p.write_bytes(b"hello")
        good = _sha(b"hello")
        verify_cache_sha256(p, good, "X")  # no raise
        with self.assertRaises(ProvenanceError):
            verify_cache_sha256(p, "bad", "X")
        verify_cache_sha256(p, None, "X")  # no raise
        verify_cache_sha256(p, "", "X")  # no raise


if __name__ == "__main__":
    unittest.main()
