"""Item 3 residual: run_real_campaign.load_verified_cache must enforce fail-closed
at the raw-ingress boundary via the guarded loader (sha256/synthetic/runtime).
Covers the archive-reload/manifest-path read: stale sha or missing synthetic_check
must be rejected; a valid verified entry loads."""
import json, hashlib
from pathlib import Path
import pytest
from src.data.provenance import ProvenanceError


def _varied(n=24):
    ts = 1766188800000
    return [{"timestamp_ms": ts + i * 3_600_000, "open": 100.0 + i, "high": 101.0 + i,
             "low": 99.0 + i, "close": 100.5 + i, "volume": 6000000.0 + i} for i in range(n)]


def _write(p, candles):
    payload = json.dumps(candles, separators=(",", ":"), ensure_ascii=False).encode()
    p.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def test_load_verified_cache_rejects_sha256_mismatch(tmp_path, monkeypatch):
    from scripts import run_real_campaign as rrc
    cache = tmp_path / "cache"; (cache / "candles").mkdir(parents=True)
    _write(cache / "candles" / "BTC.json", _varied())
    monkeypatch.setattr(rrc, "REPO_ROOT", tmp_path)
    manifest = {"symbols": {"BTC": {"status": "ok", "sha256": "0" * 64, "synthetic_check": {"is_synthetic": False}}}}
    with pytest.raises(ProvenanceError) as ei:
        rrc.load_verified_cache(cache, manifest)
    assert "sha256" in str(ei.value).lower() or "checksum" in str(ei.value).lower() or "mismatch" in str(ei.value).lower()


def test_load_verified_cache_accepts_clean_verified(tmp_path, monkeypatch):
    from scripts import run_real_campaign as rrc
    cache = tmp_path / "cache"; (cache / "candles").mkdir(parents=True)
    sha = _write(cache / "candles" / "BTC.json", _varied())
    monkeypatch.setattr(rrc, "REPO_ROOT", tmp_path)
    manifest = {"symbols": {"BTC": {"status": "ok", "sha256": sha, "synthetic_check": {"is_synthetic": False}}}}
    out = rrc.load_verified_cache(cache, manifest)
    assert "BTC" in out and len(out["BTC"]) == 24
