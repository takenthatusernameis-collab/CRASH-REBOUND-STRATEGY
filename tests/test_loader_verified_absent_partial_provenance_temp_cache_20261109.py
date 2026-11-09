"""D guardrail locks (HANDOFF 2a probes): loader/consumer fail-closed boundaries.

- load_hyperliquid_candles(require_verified=True) rejects absent provenance_info.
- load_hyperliquid_candles(require_verified=True) rejects partial/mismatched
  provenance_info and rejects temp cache_path / temp actual source paths.
- run_real_campaign/loader consumer pairing must not admit temp-manifest cache paths
  (covered via provenance/loader checks here; run_real_campaign uses same gates).
"""
import hashlib
import json
import tempfile
from pathlib import Path

import pytest

from src.data.loader import load_hyperliquid_candles
from src.data.provenance import ProvenanceError, validate_provenance


def _candles(n=30):
    import datetime
    base = datetime.datetime(2025, 12, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
    out = []
    for i in range(n):
        out.append({
            "timestamp": (base + datetime.timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "open": 100.0 + i, "high": 101.0 + i, "low": 99.0 + i,
            "close": 100.5 + i, "volume": 1000.0 + i,
        })
    return out


def _write(path: Path, candles):
    payload = json.dumps(candles).encode()
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def test_loader_require_verified_rejects_absent_provenance_info(tmp_path):
    p = tmp_path / "BTC.json"
    _write(p, _candles())
    with pytest.raises(ProvenanceError):
        load_hyperliquid_candles(str(p), symbol="BTC", require_verified=True, provenance_info=None)


def test_loader_require_verified_rejects_missing_synthetic_check(tmp_path):
    p = tmp_path / "BTC.json"
    sha = _write(p, _candles())
    with pytest.raises(ProvenanceError):
        load_hyperliquid_candles(str(p), symbol="BTC", require_verified=True,
                                 provenance_info={"sha256": sha, "cache_path": str(p)})


def test_loader_require_verified_rejects_temp_cache_path_in_provenance(tmp_path):
    p = tmp_path / "BTC.json"
    sha = _write(p, _candles())
    with pytest.raises(ProvenanceError):
        load_hyperliquid_candles(str(p), symbol="BTC", require_verified=True,
                                 provenance_info={
                                     "sha256": sha,
                                     "cache_path": "/tmp/kilo-tmp/fake-cache/BTC.json",
                                     "synthetic_check": {"is_synthetic": False, "reason": "varied_series_ok"},
                                 })


def test_loader_require_verified_rejects_temp_actual_source_path():
    with tempfile.TemporaryDirectory(dir="/tmp") as td:
        p = Path(td) / "BTC.json"
        sha = _write(p, _candles())
        with pytest.raises(ProvenanceError):
            load_hyperliquid_candles(str(p), symbol="BTC", require_verified=True,
                                     provenance_info={
                                         "sha256": sha,
                                         "cache_path": str(p),
                                         "source_path": str(p),
                                         "synthetic_check": {"is_synthetic": False, "reason": "varied_series_ok"},
                                     })


def test_validate_provenance_rejects_temp_cache_path_manifest():
    with tempfile.TemporaryDirectory(dir="/tmp") as td:
        cp = Path(td) / "BTC.json"
        sha = _write(cp, _candles())
        manifest = {
            "schema_version": 1, "generated_at_utc": "2026-01-01T00:00:00Z",
            "target_window": {"start": "2025-12-20T00:00:00Z", "end": "2026-09-28T23:00:00Z", "expected_hourly_bars": 6792},
            "source": {"kind": "hyperliquid_api", "hl_url": "https://api.hyperliquid.xyz/info", "input_archive": None},
            "symbols": {"BTC": {"symbol": "BTC", "status": "ok", "cache_path": str(cp), "sha256": sha,
                "synthetic_check": {"is_synthetic": False, "reason": "varied_series_ok", "distinct_signatures": 30, "bars_checked": 30},
                "coverage": {"complete_for_target_window": True, "expected_hourly_bars": 6792, "observed_in_window_bars": 6792}}},
            "summary": {"all_complete": True, "complete_symbols": 1, "total_symbols": 1},
        }
        ok, reasons = validate_provenance(manifest, require_complete=True)
        assert not ok
        assert any("temp" in str(r).lower() or "kilo-tmp" in str(r).lower() or "scratch" in str(r).lower() for r in reasons)
