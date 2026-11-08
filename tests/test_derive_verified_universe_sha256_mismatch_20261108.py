"""Item 3 residual: derive_verified_universe --verify-cache-sha256 exists but
must be enforced; and missing synthetic_check/runtime synthetic must block
selection (already partially done). Add explicit sha mismatch block test."""
import json, hashlib
from pathlib import Path
import pytest


def _varied(n=24):
    ts = 1766188800000
    return [{"timestamp_ms": ts + i * 3_600_000, "open": 100.0 + i, "high": 101.0 + i,
             "low": 99.0 + i, "close": 100.5 + i, "volume": 6000000.0 + i} for i in range(n)]


def _write(p, candles):
    payload = json.dumps(candles, separators=(",", ":"), ensure_ascii=False).encode()
    p.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def test_derive_refuses_sha256_mismatch_when_verified(tmp_path, monkeypatch):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from scripts import derive_verified_universe as dvu
    from src.data.provenance import ProvenanceError
    cache = tmp_path / "cache" / "candles"
    cache.mkdir(parents=True)
    sha = _write(cache / "BTC.json", _varied())
    manifest = {"target_window": {"start": "2025-12-20T00:00:00Z", "end": "2025-12-20T23:00:00Z"},
                "symbols": {"BTC": {"status": "ok", "sha256": "0" * 64,
                                    "synthetic_check": {"is_synthetic": False},
                                    "coverage": {"complete_for_target_window": True, "expected_hourly_bars": 24, "observed_in_window_bars": 24, "gap_count": 0}}},
                "summary": {"all_complete": True, "ready_for_real_campaign": True}}
    mp = tmp_path / "prov.json"; mp.write_text(json.dumps(manifest))
    monkeypatch.setattr("sys.argv", ["x", "--manifest", str(mp), "--cache-dir", str(tmp_path / "cache"), "--verify-cache-sha256", "--output", str(tmp_path / "u.json")])
    with pytest.raises((ProvenanceError, SystemExit)):
        dvu.main()
