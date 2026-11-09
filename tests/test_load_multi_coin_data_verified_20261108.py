"""Item 3 residual: load_multi_coin_data raw cache reads bypass provenance.
Add fail-closed verified mode when manifest/provenance context is provided."""
import json, hashlib, tempfile
from pathlib import Path
import pytest
from src.data.provenance import ProvenanceError

REPO_ROOT = Path(__file__).resolve().parents[1]


def _repo_tmp():
    return tempfile.TemporaryDirectory(dir=str(REPO_ROOT))


def _varied(n=24):
    ts = 1766188800000
    return [{"timestamp_ms": ts + i * 3_600_000, "open": 100.0 + i, "high": 101.0 + i,
             "low": 99.0 + i, "close": 100.5 + i, "volume": 6000000.0 + i} for i in range(n)]


def _write(p, candles):
    payload = json.dumps(candles, separators=(",", ":"), ensure_ascii=False).encode()
    p.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def test_load_multi_coin_data_verified_rejects_missing_synthetic_check():
    from src.data.loader import load_multi_coin_data
    with _repo_tmp() as td:
        d = Path(td)
        sha = _write(d / "BTC.json", _varied())
        manifest = {"symbols": {"BTC": {"status": "ok", "sha256": sha}}}  # missing synthetic_check
        with pytest.raises(ProvenanceError):
            load_multi_coin_data(str(d), symbols=["BTC"], min_daily_volume_usd=0,
                                 require_verified=True, manifest=manifest)


def test_load_multi_coin_data_verified_accepts_clean():
    from src.data.loader import load_multi_coin_data
    with _repo_tmp() as td:
        d = Path(td)
        sha = _write(d / "BTC.json", _varied())
        manifest = {"symbols": {"BTC": {"status": "ok", "sha256": sha, "synthetic_check": {"is_synthetic": False}}}}
        out = load_multi_coin_data(str(d), symbols=["BTC"], min_daily_volume_usd=0,
                                   require_verified=True, manifest=manifest)
        assert "BTC" in out and len(out["BTC"]) == 24
