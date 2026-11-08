"""Item 3 residual: load_multi_coin_data raw cache reads bypass provenance.
Add fail-closed verified mode when manifest/provenance context is provided."""
import json, hashlib
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


def test_load_multi_coin_data_verified_rejects_missing_synthetic_check(tmp_path):
    from src.data.loader import load_multi_coin_data
    sha = _write(tmp_path / "BTC.json", _varied())
    manifest = {"symbols": {"BTC": {"status": "ok", "sha256": sha}}}  # missing synthetic_check
    with pytest.raises(ProvenanceError):
        load_multi_coin_data(str(tmp_path), symbols=["BTC"], min_daily_volume_usd=0,
                             require_verified=True, manifest=manifest)


def test_load_multi_coin_data_verified_accepts_clean(tmp_path):
    from src.data.loader import load_multi_coin_data
    sha = _write(tmp_path / "BTC.json", _varied())
    manifest = {"symbols": {"BTC": {"status": "ok", "sha256": sha, "synthetic_check": {"is_synthetic": False}}}}
    out = load_multi_coin_data(str(tmp_path), symbols=["BTC"], min_daily_volume_usd=0,
                               require_verified=True, manifest=manifest)
    assert "BTC" in out and len(out["BTC"]) == 24
