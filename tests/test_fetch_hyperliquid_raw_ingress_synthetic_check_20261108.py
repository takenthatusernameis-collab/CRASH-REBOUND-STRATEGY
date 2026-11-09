"""Fail-closed provenance emission on raw archive ingestion paths.

Item 3 residual: ingest_archive/merge_verified_archives must compute and emit
synthetic_check for every symbol entry they produce, so downstream verified
consumers never receive a manifest entry without synthetic_check (unverified).
"""
import json

from scripts.fetch_hyperliquid_candles import (
    ingest_archive,
    merge_verified_archives,
    _parse_iso,
)


def _write_varied(path, symbol="BTC", n=5):
    ts = 1734652800000
    rows = []
    for i in range(n):
        base = 100.0 + i
        rows.append({
            "timestamp_ms": ts + i * 3_600_000,
            "open": base, "high": base + 1, "low": base - 1,
            "close": base + 0.5, "volume": 1000 + i,
        })
    path.write_text(json.dumps({symbol: rows}))
    return rows


def _write_flat(path, symbol="BTC", n=5):
    ts = 1734652800000
    rows = []
    for i in range(n):
        rows.append({
            "timestamp_ms": ts + i * 3_600_000,
            "open": 1, "high": 1, "low": 1, "close": 1, "volume": 1,
        })
    path.write_text(json.dumps({symbol: rows}))
    return rows


def test_ingest_archive_emits_synthetic_check_for_raw_file(tmp_path):
    p = tmp_path / "BTC.json"
    _write_varied(p)
    candles, meta = ingest_archive(p, "BTC", allow_temp_paths=True)
    assert candles
    assert isinstance(meta.get("synthetic_check"), dict)
    assert meta["synthetic_check"].get("is_synthetic") is False


def test_ingest_archive_emits_synthetic_check_for_flat_raw_file(tmp_path):
    p = tmp_path / "BTC.json"
    _write_flat(p)
    candles, meta = ingest_archive(p, "BTC", allow_temp_paths=True)
    assert isinstance(meta.get("synthetic_check"), dict)
    assert meta["synthetic_check"].get("is_synthetic") is True


def test_merge_verified_archives_emits_synthetic_check_per_symbol(tmp_path):
    p = tmp_path / "BTC.json"
    _write_varied(p)
    start = _parse_iso("2025-12-20T00:00:00Z")
    end = _parse_iso("2025-12-20T04:00:00Z")
    merged = merge_verified_archives([p], ["BTC"], start, end, min_daily_volume_usd=0, allow_temp_paths=True)
    btc = merged["symbols"]["BTC"]
    assert isinstance(btc.get("synthetic_check"), dict)
    assert btc["synthetic_check"].get("is_synthetic") is False
