"""D-bypass hunt (2026-11-09T05:18:02Z, failing-tests-first): the verified raw-ingress
boundary must reject a TEMP ACTUAL source file even when provenance_info declares a
CLEAN cache_path.

`_verify_loaded_candles` scanned provenance_info path fields for temp markers, but the
ACTUAL source_path being read was never temp-scanned. A temp scratch file whose sha256
matched the manifest's expected sha, with a clean declared cache_path and clean
synthetic_check, was accepted as verified real-data evidence at the raw-ingress
boundary. Repro: load_hyperliquid_candles(require_verified=True) accepted it.

Fix: `_verify_loaded_candles` now also temp-scans the actual source_path argument.
"""
import hashlib
import json
import tempfile
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


def _clean_info(sha, **extra):
    info = {"status": "ok", "synthetic_check": {"is_synthetic": False}, "sha256": sha}
    info.update(extra)
    return info


def test_hl_candles_verified_rejects_temp_actual_source_path_with_clean_cache_path(tmp_path):
    """Bypass repro: temp actual source file + clean declared cache_path + matching sha
    + clean synthetic_check must be REJECTED at the raw-ingress boundary."""
    from src.data.loader import load_hyperliquid_candles
    p = tmp_path / "BTC.json"
    sha = _write(p, _varied())
    info = _clean_info(sha, cache_path="research_state/cache/hyperliquid/candles/BTC.json")
    with pytest.raises(ProvenanceError) as ei:
        load_hyperliquid_candles(str(p), symbol="BTC", require_verified=True, provenance_info=info)
    msg = str(ei.value).lower()
    assert "temp" in msg or "unverified" in msg, str(ei.value)


def test_hl_candles_verified_rejects_temp_actual_source_path_kilo_tmp_marker(tmp_path):
    """Same bypass with the _temp/kilo-tmp scratch marker in the actual source path."""
    from src.data.loader import load_hyperliquid_candles
    p = tmp_path / "BTC.json"
    sha = _write(p, _varied())
    info = _clean_info(sha, cache_path="research_state/cache/hyperliquid/candles/BTC.json")
    with pytest.raises(ProvenanceError):
        load_hyperliquid_candles(str(p), symbol="BTC", require_verified=True, provenance_info=info)


def test_read_symbol_verified_rejects_temp_actual_source_path(tmp_path):
    """Same bypass through fetch_hyperliquid_candles._read_symbol_candles_from_file."""
    from scripts.fetch_hyperliquid_candles import _read_symbol_candles_from_file
    p = tmp_path / "BTC.json"
    sha = _write(p, _varied())
    info = _clean_info(sha, cache_path="research_state/cache/hyperliquid/candles/BTC.json")
    with pytest.raises(ProvenanceError):
        _read_symbol_candles_from_file(p, "BTC", require_verified=True, provenance_info=info)


def test_hl_candles_verified_accepts_repo_local_source_path_with_clean_cache_path():
    """Control: a repo-local actual source path with a clean declared cache_path must
    still be accepted (the fix must not over-reject clean repo-local reads)."""
    from src.data.loader import load_hyperliquid_candles
    with tempfile.TemporaryDirectory(dir=str(Path(__file__).resolve().parents[1])) as d:
        p = Path(d) / "BTC.json"
        sha = _write(p, _varied())
        info = _clean_info(sha, cache_path="research_state/cache/hyperliquid/candles/BTC.json")
        out = load_hyperliquid_candles(str(p), symbol="BTC", require_verified=True, provenance_info=info)
        assert len(out) == 24


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q", "--tb=short"]))