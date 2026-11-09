"""Item 3 residual: raw/loader readers must have a fail-closed verified path.

load_hyperliquid_candles and load_multi_coin_data are raw cache readers that
historically did not consult manifest synthetic_check/sha256. Verified-data
consumers need a fail-closed option: when provenance/manifest info is supplied,
reject missing/non-dict/declared-synthetic synthetic_check, runtime-detect
synthetic/flat series, and verify sha256 when provided. Unverified data must
never pass the guarded path. Backward compatible: no provenance context => old
behavior unchanged (fixture/raw non-evidence use).
"""
import json
import hashlib
import tempfile
from pathlib import Path

import pytest

from src.data.provenance import ProvenanceError

REPO_ROOT = Path(__file__).resolve().parents[1]


def _varied(n=24):
    ts = 1766188800000
    return [{"timestamp_ms": ts + i * 3_600_000, "open": 100.0 + i, "high": 101.0 + i,
             "low": 99.0 + i, "close": 100.5 + i, "volume": 6000000.0 + i} for i in range(n)]


def _flat(n=24):
    ts = 1766188800000
    return [{"timestamp_ms": ts + i * 3_600_000, "open": 100.0, "high": 100.0,
             "low": 100.0, "close": 100.0, "volume": 6000000.0} for i in range(n)]


def _write(p, candles):
    payload = json.dumps(candles, separators=(",", ":"), ensure_ascii=False).encode()
    p.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def _repo_tmp():
    """Repo-local temp dir: pytest tmp_path lives under the harness _temp/kilo-tmp
    scratch tree, which the hardened temp-path marker must reject at the verified
    raw-ingress boundary. Real verified cache paths live repo-LOCAL."""
    return tempfile.TemporaryDirectory(dir=str(REPO_ROOT))


def test_load_hyperliquid_candles_verified_rejects_missing_synthetic_check():
    from src.data.loader import load_hyperliquid_candles
    with _repo_tmp() as d:
        p = Path(d) / "BTC.json"
        _write(p, _varied())
        with pytest.raises(ProvenanceError) as ei:
            load_hyperliquid_candles(str(p), symbol="BTC", require_verified=True, provenance_info={"status": "ok"})
        assert "synthetic_check" in str(ei.value)


def test_load_hyperliquid_candles_verified_rejects_declared_synthetic():
    from src.data.loader import load_hyperliquid_candles
    with _repo_tmp() as d:
        p = Path(d) / "BTC.json"
        _write(p, _varied())
        with pytest.raises(ProvenanceError):
            load_hyperliquid_candles(str(p), symbol="BTC", require_verified=True,
                                     provenance_info={"status": "ok", "synthetic_check": {"is_synthetic": True, "reason": "flat"}})


def test_load_hyperliquid_candles_verified_runtime_detects_flat():
    from src.data.loader import load_hyperliquid_candles
    with _repo_tmp() as d:
        p = Path(d) / "BTC.json"
        _write(p, _flat())
        with pytest.raises(ProvenanceError) as ei:
            load_hyperliquid_candles(str(p), symbol="BTC", require_verified=True,
                                     provenance_info={"status": "ok", "synthetic_check": {"is_synthetic": False}})
        assert "synthetic" in str(ei.value).lower() or "flat" in str(ei.value).lower()


def test_load_hyperliquid_candles_verified_rejects_sha256_mismatch():
    from src.data.loader import load_hyperliquid_candles
    with _repo_tmp() as d:
        p = Path(d) / "BTC.json"
        _write(p, _varied())
        with pytest.raises(ProvenanceError) as ei:
            load_hyperliquid_candles(str(p), symbol="BTC", require_verified=True,
                                     provenance_info={"status": "ok", "synthetic_check": {"is_synthetic": False}, "sha256": "0" * 64})
        assert "sha256" in str(ei.value).lower() or "checksum" in str(ei.value).lower()


def test_load_hyperliquid_candles_verified_accepts_clean():
    from src.data.loader import load_hyperliquid_candles
    with _repo_tmp() as d:
        p = Path(d) / "BTC.json"
        sha = _write(p, _varied())
        out = load_hyperliquid_candles(str(p), symbol="BTC", require_verified=True,
                                        provenance_info={"status": "ok", "synthetic_check": {"is_synthetic": False}, "sha256": sha})
        assert len(out) == 24


def test_load_hyperliquid_candles_backward_compat_no_provenance():
    from src.data.loader import load_hyperliquid_candles
    with _repo_tmp() as d:
        p = Path(d) / "BTC.json"
        _write(p, _varied())
        out = load_hyperliquid_candles(str(p), symbol="BTC")
        assert len(out) == 24
