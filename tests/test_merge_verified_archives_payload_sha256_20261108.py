"""merge_verified_archives must emit normalized payload sha256 + fail-closed
synthetic_check evidence so standalone merged manifests carry cache-integrity
metadata (not only archive_sha256). Main may overwrite sha256 after cache write;
the merge output must still be self-consistent and non-empty."""
import json
import hashlib
from pathlib import Path

from scripts.fetch_hyperliquid_candles import merge_verified_archives, _parse_iso


def _varied(symbol="BTC", n=5):
    ts = 1734652800000
    return [
        {"timestamp_ms": ts + i * 3_600_000, "open": 100 + i, "high": 101 + i,
         "low": 99 + i, "close": 100.5 + i, "volume": 1000 + i}
        for i in range(n)
    ]


def test_merge_emits_payload_sha256_and_archive_sha256(tmp_path):
    p = tmp_path / "BTC.json"
    rows = _varied()
    p.write_text(json.dumps({"BTC": rows}))
    start = _parse_iso("2025-12-20T00:00:00Z")
    end = _parse_iso("2025-12-20T04:00:00Z")
    merged = merge_verified_archives([p], ["BTC"], start, end, min_daily_volume_usd=0)
    e = merged["symbols"]["BTC"]
    assert isinstance(e.get("archive_sha256"), str) and len(e["archive_sha256"]) == 64
    # payload sha256 of normalized candle JSON (stable separators) for cache integrity
    assert isinstance(e.get("sha256"), str) and len(e["sha256"]) == 64
    expected_payload = hashlib.sha256(
        json.dumps(rows, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    # merge reads via ingest_archive path which normalizes; accept either raw-normalized
    # equivalence check by recomputing from returned normalized count? easier: recompute
    # from the candles merge would produce - but merge doesn't return candles. So just
    # assert sha256 present and differs/equals archive sha as appropriate; main contract
    # is non-empty payload hash. Stricter: reload and compare.
    from scripts.fetch_hyperliquid_candles import ingest_archive
    candles, _ = ingest_archive(p, "BTC")
    expected = hashlib.sha256(
        json.dumps(candles, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    assert e["sha256"] == expected
    assert isinstance(e.get("synthetic_check"), dict)
    assert e["synthetic_check"].get("is_synthetic") is False
