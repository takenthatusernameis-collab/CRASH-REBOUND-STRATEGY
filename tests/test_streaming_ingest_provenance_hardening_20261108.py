"""Item 3 residual: streaming_ingest must not be a bypass for fail-closed gates.

stream_normalize yields normalized rows row-by-row and has no provenance/synthetic
checks — any verified-data consumer using it directly bypasses gates. Provide a
guarded path: stream_normalize_verified (or normalize_with_provenance) that
materializes with bounded semantics? Or a helper that validates after streaming.
We add load/normalize helpers that enforce synthetic_check + runtime detection +
sha256 when manifest context is provided. Low-level stream_normalize remains for
raw parsing but callers needing verified evidence must use the guarded API.
"""
import json
import hashlib

import pytest

from src.data.provenance import ProvenanceError


def _varied(n=24):
    ts = 1766188800000
    return [{"timestamp_ms": ts + i * 3_600_000, "symbol": "BTC",
             "open": 100.0 + i, "high": 101.0 + i, "low": 99.0 + i,
             "close": 100.5 + i, "volume": 6000000.0 + i} for i in range(n)]


def _write_ndjson(p, rows):
    payload = ("\n".join(json.dumps(r) for r in rows) + "\n").encode()
    p.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def test_stream_normalize_verified_rejects_missing_synthetic_check(tmp_path):
    from src.data.streaming_ingest import stream_normalize_verified
    p = tmp_path / "x.jsonl"
    _write_ndjson(p, _varied())
    with pytest.raises(ProvenanceError) as ei:
        stream_normalize_verified(p, "BTC", provenance_info={"status": "ok"})
    assert "synthetic_check" in str(ei.value)


def test_stream_normalize_verified_rejects_sha256_mismatch(tmp_path):
    from src.data.streaming_ingest import stream_normalize_verified
    p = tmp_path / "x.jsonl"
    _write_ndjson(p, _varied())
    with pytest.raises(ProvenanceError):
        stream_normalize_verified(p, "BTC", provenance_info={"status": "ok", "synthetic_check": {"is_synthetic": False}, "sha256": "0" * 64})


def test_stream_normalize_verified_accepts_clean(tmp_path):
    from src.data.streaming_ingest import stream_normalize_verified
    p = tmp_path / "x.jsonl"
    sha = _write_ndjson(p, _varied())
    out = stream_normalize_verified(p, "BTC", provenance_info={"status": "ok", "synthetic_check": {"is_synthetic": False}, "sha256": sha})
    assert len(out) == 24


def test_stream_normalize_low_level_unchanged(tmp_path):
    from src.data.streaming_ingest import stream_normalize
    p = tmp_path / "x.jsonl"
    _write_ndjson(p, _varied())
    out = list(stream_normalize(p, "BTC"))
    assert len(out) == 24
