"""D-bypass hunt (2026-11-09): verified loader consumers must reject temp
per-symbol provenance paths, not just temp archive keys.

`_verify_loaded_candles` is the shared fail-closed choke point for
`load_hyperliquid_candles(require_verified=True)` and
`fetch_hyperliquid_candles._read_symbol_candles_from_file(require_verified=True)`,
and `load_multi_coin_data(require_verified=True)` funnels through it. Before this
fix a provenance_info / manifest symbol entry carrying clean synthetic_check +
matching sha256 but a temp `cache_path`/`source_path`/nested `source.input_archive`
was accepted as verified real-data evidence. Repro: 2 accepted (bypass) before fix.
"""
import json
import hashlib
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


# --- load_hyperliquid_candles verified boundary -------------------------------

def test_hl_candles_verified_rejects_temp_cache_path(tmp_path):
    from src.data.loader import load_hyperliquid_candles
    p = tmp_path / "BTC.json"
    sha = _write(p, _varied())
    with pytest.raises(ProvenanceError) as ei:
        load_hyperliquid_candles(str(p), symbol="BTC", require_verified=True,
                                 provenance_info=_clean_info(sha, cache_path="/tmp/kilo-tmp/BTC.json"))
    assert "temp" in str(ei.value).lower() or "unverified" in str(ei.value).lower()


def test_hl_candles_verified_rejects_temp_source_path(tmp_path):
    from src.data.loader import load_hyperliquid_candles
    p = tmp_path / "BTC.json"
    sha = _write(p, _varied())
    with pytest.raises(ProvenanceError):
        load_hyperliquid_candles(str(p), symbol="BTC", require_verified=True,
                                 provenance_info=_clean_info(sha, source_path="/var/tmp/kilo-tmp/btc.json"))


def test_hl_candles_verified_rejects_temp_nested_source_input_archive(tmp_path):
    from src.data.loader import load_hyperliquid_candles
    p = tmp_path / "BTC.json"
    sha = _write(p, _varied())
    info = _clean_info(sha, source={"input_archive": "_temp/kilo-tmp/btc.tar.gz"})
    with pytest.raises(ProvenanceError):
        load_hyperliquid_candles(str(p), symbol="BTC", require_verified=True, provenance_info=info)


def test_hl_candles_verified_rejects_temp_provenance_input_archives(tmp_path):
    from src.data.loader import load_hyperliquid_candles
    p = tmp_path / "BTC.json"
    sha = _write(p, _varied())
    info = _clean_info(sha, provenance={"input_archives": ["/tmp/kilo-tmp/btc.tar.gz"]})
    with pytest.raises(ProvenanceError):
        load_hyperliquid_candles(str(p), symbol="BTC", require_verified=True, provenance_info=info)


def test_hl_candles_verified_accepts_clean_non_temp_cache_path():
    from src.data.loader import load_hyperliquid_candles
    import tempfile
    # Use a repo-local dir: pytest tmp_path lives under the harness _temp/kilo-tmp
    # scratch tree, which the hardened temp-path marker must reject. Real verified
    # cache paths live repo-LOCAL (research_state/cache), so exercise that shape.
    with tempfile.TemporaryDirectory(dir=str(Path(__file__).resolve().parent.parent)) as d:
        p = Path(d) / "BTC.json"
        sha = _write(p, _varied())
        info = _clean_info(sha, cache_path=str(p), source_path=str(Path(d) / "src.json"))
        out = load_hyperliquid_candles(str(p), symbol="BTC", require_verified=True, provenance_info=info)
        assert len(out) == 24


# --- load_multi_coin_data verified boundary ----------------------------------

def test_multi_coin_verified_rejects_temp_manifest_cache_path(tmp_path):
    from src.data.loader import load_multi_coin_data
    p = tmp_path / "BTC.json"
    sha = _write(p, _varied())
    manifest = {"symbols": {"BTC": _clean_info(sha, cache_path="_temp/kilo-tmp/BTC.json")}}
    with pytest.raises(ProvenanceError):
        load_multi_coin_data(str(tmp_path), symbols=["BTC"], min_daily_volume_usd=0,
                             require_verified=True, manifest=manifest)


def test_multi_coin_verified_accepts_clean_manifest():
    from src.data.loader import load_multi_coin_data
    # Repo-local fixture dir: the hardened temp-path guard rejects any declared
    # cache/source path under the harness _temp/kilo-tmp scratch tree (pytest
    # tmp_path lives there), so a "clean" accepted manifest must point at a
    # repo-local verified cache shape, matching test_hl_candles_verified_accepts_clean_non_temp_cache_path.
    import tempfile
    with tempfile.TemporaryDirectory(dir=str(Path(__file__).resolve().parents[1])) as d:
        dpath = Path(d)
        p = dpath / "BTC.json"
        sha = _write(p, _varied())
        manifest = {"symbols": {"BTC": _clean_info(sha, cache_path=str(p))}}
        out = load_multi_coin_data(str(dpath), symbols=["BTC"], min_daily_volume_usd=0,
                                   require_verified=True, manifest=manifest)
        assert "BTC" in out and len(out["BTC"]) == 24


# --- fetch_hyperliquid_candles verified boundary (same choke point) -----------

def test_fetch_read_symbol_verified_rejects_temp_cache_path(tmp_path):
    from scripts.fetch_hyperliquid_candles import _read_symbol_candles_from_file
    p = tmp_path / "BTC.json"
    sha = _write(p, _varied())
    with pytest.raises(ProvenanceError):
        _read_symbol_candles_from_file(p, "BTC", require_verified=True,
                                       provenance_info=_clean_info(sha, cache_path="/tmp/kilo-tmp/BTC.json"))