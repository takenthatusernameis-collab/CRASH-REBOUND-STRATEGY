"""Fail-closed: run_real_campaign.load_verified_cache must not treat a manifest
entry as verified when synthetic_check is missing/non-dict, even if status==ok
and runtime candle re-detection would run. Missing synthetic_check means
provenance was never computed (unverified). Item 3 residual hardening."""
import json
from pathlib import Path

import pytest

from src.data.provenance import ProvenanceError


def _varied_candles(n=10):
    out = []
    ts = 1734652800000
    for i in range(n):
        base = 100.0 + i
        out.append({
            "timestamp_ms": ts + i * 3_600_000,
            "timestamp": f"2025-12-20T{i:02d}:00:00+00:00",
            "open": base, "high": base + 1, "low": base - 1,
            "close": base + 0.5, "volume": 1000 + i,
        })
    return out


def _manifest(sym="BTC", synthetic_check=...):
    info = {
        "status": "ok",
        "cache_path": f"research_state/cache/test/candles/{sym}.json",
        "coverage": {"complete_for_target_window": True},
    }
    if synthetic_check is not ...:
        info["synthetic_check"] = synthetic_check
    return {"symbols": {sym: info}, "summary": {}}


def test_load_verified_cache_rejects_missing_synthetic_check(tmp_path, monkeypatch):
    from scripts import run_real_campaign as rrc

    cache = tmp_path / "cache"
    (cache / "candles").mkdir(parents=True)
    (cache / "candles" / "BTC.json").write_text(json.dumps(_varied_candles()))
    # point REPO_ROOT-relative resolution to tmp
    monkeypatch.setattr(rrc, "REPO_ROOT", tmp_path)
    manifest = _manifest(synthetic_check=...)
    with pytest.raises(ProvenanceError) as ei:
        rrc.load_verified_cache(cache, manifest)
    msg = str(ei.value)
    assert "synthetic_check" in msg
    assert "BTC" in msg


def test_load_verified_cache_rejects_non_dict_synthetic_check(tmp_path, monkeypatch):
    from scripts import run_real_campaign as rrc

    cache = tmp_path / "cache"
    (cache / "candles").mkdir(parents=True)
    (cache / "candles" / "BTC.json").write_text(json.dumps(_varied_candles()))
    monkeypatch.setattr(rrc, "REPO_ROOT", tmp_path)
    manifest = _manifest(synthetic_check="bad")
    with pytest.raises(ProvenanceError) as ei:
        rrc.load_verified_cache(cache, manifest)
    assert "synthetic_check" in str(ei.value)


def test_load_verified_cache_rejects_declared_synthetic(tmp_path, monkeypatch):
    from scripts import run_real_campaign as rrc

    cache = tmp_path / "cache"
    (cache / "candles").mkdir(parents=True)
    (cache / "candles" / "BTC.json").write_text(json.dumps(_varied_candles()))
    monkeypatch.setattr(rrc, "REPO_ROOT", tmp_path)
    manifest = _manifest(synthetic_check={"is_synthetic": True, "reason": "flat"})
    with pytest.raises(ProvenanceError):
        rrc.load_verified_cache(cache, manifest)


def test_load_verified_cache_accepts_present_clean_synthetic_check(tmp_path, monkeypatch):
    from scripts import run_real_campaign as rrc

    cache = tmp_path / "cache"
    (cache / "candles").mkdir(parents=True)
    (cache / "candles" / "BTC.json").write_text(json.dumps(_varied_candles()))
    monkeypatch.setattr(rrc, "REPO_ROOT", tmp_path)
    manifest = _manifest(synthetic_check={"is_synthetic": False, "reason": "varied_series_ok"})
    out = rrc.load_verified_cache(cache, manifest)
    assert "BTC" in out
    assert len(out["BTC"]) == 10
