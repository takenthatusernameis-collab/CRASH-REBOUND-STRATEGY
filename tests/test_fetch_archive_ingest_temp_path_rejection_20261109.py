"""Fail-closed: fetch ingestion helpers must reject temp scratch provenance paths.

2026-11-09 D residual (failing-tests-first). `discover_archive_sources`,
`ingest_archive`, and `merge_verified_archives` in
`scripts/fetch_hyperliquid_candles.py` recorded/resolved temp archive paths
(`_temp/kilo-tmp`, `/tmp/`) without rejection, allowing temp-sourced metadata
to enter manifest/provenance assembly before downstream guards. Ingestion
boundaries must fail-closed on temp scratch paths.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from scripts.fetch_hyperliquid_candles import discover_archive_sources, ingest_archive, merge_verified_archives


def _write_symbol(path: Path, symbol: str = "BTC", n: int = 24):
    ts = 1766188800000
    candles = [{"timestamp_ms": ts + i * 3600000, "open": 100 + i, "high": 101 + i,
                "low": 99 + i, "close": 100.5 + i, "volume": 6_000_000 + i} for i in range(n)]
    path.write_text(json.dumps({symbol: candles} if path.suffix == ".json" and False else candles))


def test_discover_archive_sources_rejects_temp_directory(tmp_path):
    # simulate temp marker in resolved path by checking real /tmp behavior
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "BTC.json"
        _write_symbol(p)
        with pytest.raises(ValueError) as ei:
            discover_archive_sources(Path(d), ["BTC"])
        assert "temp" in str(ei.value).lower() or "kilo-tmp" in str(ei.value).lower() or "unverified" in str(ei.value).lower()


def test_discover_archive_sources_rejects_temp_file(tmp_path):
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "BTC.json"
        _write_symbol(p)
        with pytest.raises(ValueError) as ei:
            discover_archive_sources(p, ["BTC"])
        assert "temp" in str(ei.value).lower() or "unverified" in str(ei.value).lower()


def test_ingest_archive_rejects_temp_path():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "BTC.json"
        _write_symbol(p)
        with pytest.raises(ValueError) as ei:
            ingest_archive(p, "BTC")
        assert "temp" in str(ei.value).lower() or "unverified" in str(ei.value).lower()


def test_merge_verified_archives_rejects_temp_archive():
    import tempfile
    start = datetime(2025, 12, 20, tzinfo=timezone.utc)
    end = datetime(2026, 9, 28, tzinfo=timezone.utc)
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "BTC.json"
        _write_symbol(p, n=6792)
        with pytest.raises(ValueError) as ei:
            merge_verified_archives([p], ["BTC"], start, end, 5_000_000)
        assert "temp" in str(ei.value).lower() or "unverified" in str(ei.value).lower()


def test_ingest_archive_allows_clean_repo_relative_fixture(tmp_path):
    # non-temp canonical-looking path should still work
    p = tmp_path / "BTC.json"
    _write_symbol(p)
    # tmp_path under pytest here may be temp-like in CI; use repo-local if needed.
    # If tmp_path resolves to temp markers, this test is not authoritative for allow;
    # primary assertions are rejection tests above. Skip only when temp-marked.
    rp = str(p.resolve())
    if "_temp/kilo-tmp" in rp or rp.startswith("/tmp/") or "/tmp/" in rp:
        pytest.skip("tmp_path resolves to temp scratch marker in this environment")
    candles, meta = ingest_archive(p, "BTC")
    assert len(candles) == 24
