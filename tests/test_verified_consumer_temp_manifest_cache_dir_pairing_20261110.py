"""#1 D residual consumer/provenance pairing (2026-11-10, failing-tests-first).

Fail-closed: temp/non-canonical manifest paths, temp cache_dir, and
temp dir-backed data sources must not be accepted as verified real-data
evidence by provenance gates or verified loader consumers.

Covers:
- require_verified_provenance / load_provenance reject temp manifest paths
  (blocks run_real_campaign, derive_verified_universe, gap-report consumers
  that treat the manifest as verified evidence).
- load_multi_coin_data(require_verified=True) rejects temp data_source dir
  and temp cache_dir (defense-in-depth over file-level checks).
- run_real_campaign.load_verified_cache rejects temp cache_dir root path
  (even when content checks would otherwise run).
"""
import hashlib
import json
from pathlib import Path

import pytest

from src.data.provenance import (
    ProvenanceError,
    load_provenance,
    require_verified_provenance,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _varied(n=24):
    ts = 1766188800000
    return [{"timestamp_ms": ts + i * 3_600_000, "open": 100.0 + i, "high": 101.0 + i,
             "low": 99.0 + i, "close": 100.5 + i, "volume": 6000000.0 + i} for i in range(n)]


def _write(p, candles):
    payload = json.dumps(candles, separators=(",", ":"), ensure_ascii=False).encode()
    p.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def _kilo_tmp(prefix):
    """A path that carries kilo-tmp temp markers (same class as harness scratch)."""
    import tempfile
    return tempfile.TemporaryDirectory(prefix=prefix)


# --- provenance manifest path must not be temp --------------------------------

def test_load_provenance_rejects_kilo_tmp_manifest_path():
    with _kilo_tmp("kilo-tmp-man-") as td:
        mp = Path(td) / "provenance.json"
        mp.write_text(json.dumps({"fabricated_data": False}))
        with pytest.raises(ProvenanceError) as ei:
            load_provenance(mp)
        assert "temp" in str(ei.value).lower() or "unverified" in str(ei.value).lower()


def test_require_verified_provenance_rejects_kilo_tmp_manifest_path():
    with _kilo_tmp("kilo-tmp-man-") as td:
        mp = Path(td) / "provenance.json"
        mp.write_text(json.dumps({"fabricated_data": False}))
        with pytest.raises(ProvenanceError) as ei:
            require_verified_provenance(mp, require_complete=False, min_symbols=0)
        assert "temp" in str(ei.value).lower() or "unverified" in str(ei.value).lower()


def test_load_provenance_accepts_repo_local_manifest():
    # Repo-local non-temp path is acceptable (content errors are separate).
    # Do not use pytest tmp_path: it lives under harness _temp/kilo-tmp and is
    # correctly rejected by the temp-path guard (same class as other repo tests).
    import tempfile
    with tempfile.TemporaryDirectory(dir=str(REPO_ROOT)) as d:
        p = Path(d) / "provenance.json"
        p.write_text(json.dumps({"ok": True}))
        out = load_provenance(p)
        assert out == {"ok": True}


# --- load_multi_coin_data verified: temp data_source/cache_dir ----------------

def test_load_multi_coin_data_verified_rejects_kilo_tmp_data_source_dir():
    from src.data.loader import load_multi_coin_data
    with _kilo_tmp("kilo-tmp-src-") as td:
        cd = Path(td)
        p = cd / "BTC.json"
        sha = _write(p, _varied())
        manifest = {"symbols": {"BTC": {"status": "ok", "synthetic_check": {"is_synthetic": False}, "sha256": sha}}}
        with pytest.raises(ProvenanceError) as ei:
            load_multi_coin_data(str(cd), symbols=["BTC"], min_daily_volume_usd=0,
                                 require_verified=True, manifest=manifest)
        assert "temp" in str(ei.value).lower() or "unverified" in str(ei.value).lower()


def test_load_multi_coin_data_verified_rejects_kilo_tmp_cache_dir():
    import tempfile
    from src.data.loader import load_multi_coin_data
    # clean data source, but temp cache_dir passed in verified mode
    with tempfile.TemporaryDirectory(dir=str(REPO_ROOT)) as clean:
        cd = Path(clean)
        p = cd / "BTC.json"
        sha = _write(p, _varied())
        manifest = {"symbols": {"BTC": {"status": "ok", "synthetic_check": {"is_synthetic": False},
                                        "sha256": sha, "cache_path": str(p)}}}
        with _kilo_tmp("kilo-tmp-xcache-") as tc:
            with pytest.raises(ProvenanceError) as ei:
                load_multi_coin_data(str(cd), symbols=["BTC"], min_daily_volume_usd=0,
                                     cache_dir=tc, require_verified=True, manifest=manifest)
            assert "temp" in str(ei.value).lower() or "unverified" in str(ei.value).lower() or "cache_dir" in str(ei.value).lower()


# --- run_real_campaign.load_verified_cache: temp cache_dir root ---------------

def test_run_real_campaign_load_verified_cache_rejects_kilo_tmp_cache_dir(monkeypatch):
    from scripts import run_real_campaign as rrc
    with _kilo_tmp("kilo-tmp-rc-") as td:
        cache = Path(td)
        (cache / "candles").mkdir()
        p = cache / "candles" / "BTC.json"
        sha = _write(p, _varied())
        manifest = {"symbols": {"BTC": {"status": "ok", "sha256": sha, "synthetic_check": {"is_synthetic": False}}}}
        monkeypatch.setattr(rrc, "REPO_ROOT", Path(td))
        with pytest.raises(ProvenanceError) as ei:
            rrc.load_verified_cache(cache, manifest)
        assert "temp" in str(ei.value).lower() or "unverified" in str(ei.value).lower()
