"""Deterministic end-to-end pipeline test (synthetic, sandboxed, NON-EVIDENCE).

Proves pipeline correctness only — NOT market performance, NOT real campaign evidence.
Covers: archive -> manifest/provenance (fetch script) -> derive_verified_universe
from verified local caches -> provenance/gate refusal on incomplete data and
gate acceptance on complete verified manifest. All data is synthetic, generated
in tmp paths, clearly marked performance_evidence=false / fabricated_data=false
where scripts compute flags. No real market data is used or claimed.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"

# Small synthetic hourly window (4 bars) for fast deterministic tests.
# NOT the 283-day spec window; validates pipeline mechanics only.
START = "2025-01-01T00:00:00+00:00"
END = "2025-01-01T03:00:00+00:00"
EXPECTED_BARS = 4
START_MS = 1735689600000
END_MS = 1735700400000


def _make_candles(symbol: str, n: int, start_ms: int, close: float, base_vol: float):
    out = []
    for i in range(n):
        ts = start_ms + i * 3_600_000
        iso = f"2025-01-01T{i:02d}:00:00+00:00"
        # USD volume = close * volume; make it comfortably >= $5M over 24h-equivalent logic
        vol = base_vol
        out.append({
            "timestamp": iso,
            "timestamp_ms": ts,
            "open": close,
            "high": close * 1.01,
            "low": close * 0.99,
            "close": close,
            "volume": vol,
        })
    return out


def _write_archive(archive_dir: Path, symbols):
    archive_dir.mkdir(parents=True, exist_ok=True)
    for sym, candles in symbols.items():
        (archive_dir / f"{sym}.json").write_text(json.dumps(candles))


def _run(cmd, cwd=None, env=None):
    e = os.environ.copy()
    e["PYTHONPATH"] = str(REPO_ROOT)
    if env:
        e.update(env)
    p = subprocess.run(
        [sys.executable] + cmd,
        cwd=str(cwd or REPO_ROOT),
        env=e,
        capture_output=True,
        text=True,
    )
    return p


def test_e2e_archive_to_manifest_complete_pipeline(tmp_path):
    """Archive (per-symbol JSON) -> fetch script produces complete manifest + caches.

    Synthetic 4-bar window; pipeline correctness only, not performance evidence.
    """
    archive = tmp_path / "archive"
    cache = tmp_path / "cache_hl"
    symbols = {
        "AAA": _make_candles("AAA", EXPECTED_BARS, START_MS, close=100.0, base_vol=100_000.0),
        "ETH": _make_candles("ETH", EXPECTED_BARS, START_MS, close=2000.0, base_vol=5_000.0),
    }
    _write_archive(archive, symbols)

    r = _run([
        str(SCRIPTS / "fetch_hyperliquid_candles.py"),
        "--source", "archive",
        "--input-archive", str(archive),
        "--symbols", "AAA", "ETH",
        "--start", START, "--end", END,
        "--cache-dir", str(cache),
        "--min-daily-volume-usd", "5000000",
    ])
    assert r.returncode == 0, f"fetch failed:\nstdout={r.stdout}\nstderr={r.stderr}"

    manifest_path = cache / "provenance.json"
    assert manifest_path.exists(), "provenance manifest not written"
    manifest = json.loads(manifest_path.read_text())
    assert manifest.get("fabricated_data") is False
    assert manifest.get("run_type") == "data_acquisition_provenance"
    assert manifest["target_window"]["expected_hourly_bars"] == EXPECTED_BARS
    assert manifest["summary"]["all_complete"] is True
    assert manifest["summary"]["ready_for_real_campaign"] is True
    assert set(manifest["summary"]["complete_symbols"]) == {"AAA", "ETH"}
    for sym in ("AAA", "ETH"):
        info = manifest["symbols"][sym]
        assert info["status"] == "ok"
        cov = info["coverage"]
        assert cov["complete_for_target_window"] is True
        assert cov["observed_in_window_bars"] == EXPECTED_BARS
        assert cov["expected_hourly_bars"] == EXPECTED_BARS
        assert cov["gap_count"] == 0
        assert info.get("sha256")
        cache_file = cache / "candles" / f"{sym}.json"
        assert cache_file.exists(), f"cache for {sym} missing"


def test_e2e_incomplete_archive_refused_by_fetch_gate(tmp_path):
    """Incomplete archive (missing bars) -> fetch script returns non-zero and marks incomplete.

    The gate/manifest must refuse to claim readiness. Non-evidence synthetic data.
    """
    archive = tmp_path / "archive"
    cache = tmp_path / "cache_hl"
    # Only 2 of 4 expected bars
    symbols = {
        "AAA": _make_candles("AAA", 2, START_MS, close=100.0, base_vol=100_000.0),
    }
    _write_archive(archive, symbols)

    r = _run([
        str(SCRIPTS / "fetch_hyperliquid_candles.py"),
        "--source", "archive",
        "--input-archive", str(archive),
        "--symbols", "AAA",
        "--start", START, "--end", END,
        "--cache-dir", str(cache),
    ])
    # Default gate refuses incomplete coverage
    assert r.returncode != 0, f"incomplete archive must be refused by default gate:\n{r.stdout}\n{r.stderr}"
    manifest = json.loads((cache / "provenance.json").read_text())
    assert manifest["summary"]["all_complete"] is False
    assert manifest["summary"]["ready_for_real_campaign"] is False
    assert manifest["symbols"]["AAA"]["status"] == "incomplete"
    assert manifest["symbols"]["AAA"]["coverage"]["complete_for_target_window"] is False
    # gap report written
    gap = REPO_ROOT / "research_state" / "candle_coverage_gap_report.json"
    # fetch script writes gap report to REPO_ROOT/research_state; ensure manifest evidence exists regardless
    assert manifest["symbols"]["AAA"]["coverage"]["observed_in_window_bars"] == 2


def test_e2e_derive_verified_universe_from_verified_caches(tmp_path):
    """Complete manifest+caches -> derive_verified_universe selects by volume threshold.

    Uses local verified caches only; no exchange calls. Synthetic non-evidence.
    """
    archive = tmp_path / "archive"
    cache = tmp_path / "cache_hl"
    # AAA has large volume (close*vol per bar = 10M, rolling 24h over 4 bars = 40M proxy)
    # LOW has tiny volume (below any reasonable threshold)
    symbols = {
        "AAA": _make_candles("AAA", EXPECTED_BARS, START_MS, close=100.0, base_vol=100_000.0),
        "LOW": _make_candles("LOW", EXPECTED_BARS, START_MS, close=1.0, base_vol=1.0),
        "ETH": _make_candles("ETH", EXPECTED_BARS, START_MS, close=2000.0, base_vol=5_000.0),
    }
    _write_archive(archive, symbols)
    r = _run([
        str(SCRIPTS / "fetch_hyperliquid_candles.py"),
        "--source", "archive", "--input-archive", str(archive),
        "--symbols", "AAA", "LOW", "ETH",
        "--start", START, "--end", END, "--cache-dir", str(cache),
    ])
    assert r.returncode == 0, r.stderr

    universe_out = tmp_path / "universe_verified.json"
    r2 = _run([
        str(SCRIPTS / "derive_verified_universe.py"),
        "--manifest", str(cache / "provenance.json"),
        "--cache-dir", str(cache),
        "--min-24h-volume-usd", "5000000",
        "--output", str(universe_out),
    ])
    assert r2.returncode == 0, f"derive failed:\n{r2.stdout}\n{r2.stderr}"
    uni = json.loads(universe_out.read_text())
    assert uni["run_type"] == "verified_universe_derivation"
    assert uni["performance_evidence"] is False
    assert uni["fabricated_data"] is False
    assert "AAA" in uni["selected_symbols"]
    assert "ETH" in uni["selected_symbols"]
    assert "LOW" not in uni["selected_symbols"]
    assert uni["report"]["LOW"]["selected"] is False
    assert "volume_method" in uni
    assert "Derived from local verified caches only" in " ".join(uni.get("notes", []))


def test_e2e_provenance_gate_refuses_incomplete_manifest(tmp_path):
    """Provenance validator/run_real gate must refuse incomplete or mismatched manifests.

    Uses src.data.provenance directly with explicit start/end (pipeline correctness).
    Non-evidence synthetic manifest; no market data.
    """
    from src.data.provenance import validate_provenance, require_verified_provenance, ProvenanceError

    incomplete = {
        "fabricated_data": False,
        "real_market_data_intended": True,
        "target_window": {"start": START, "end": END, "expected_hourly_bars": EXPECTED_BARS},
        "symbols": {
            "AAA": {
                "status": "incomplete",
                "coverage": {
                    "expected_hourly_bars": EXPECTED_BARS,
                    "observed_in_window_bars": 2,
                    "gap_count": 0,
                    "complete_for_target_window": False,
                },
            }
        },
    }
    ok, errs = validate_provenance(incomplete, require_complete=True, start=START, end=END)
    assert ok is False
    assert any("incomplete" in e.lower() or "not all" in e.lower() or "complete" in e.lower() for e in errs)

    mpath = tmp_path / "prov.json"
    mpath.write_text(json.dumps(incomplete))
    with pytest.raises(ProvenanceError):
        require_verified_provenance(mpath, require_complete=True, start=START, end=END)

    # Fabricated flag is always refused
    bad = dict(incomplete)
    bad["fabricated_data"] = True
    bad["symbols"]["AAA"]["status"] = "ok"
    bad["symbols"]["AAA"]["coverage"]["complete_for_target_window"] = True
    bad["symbols"]["AAA"]["coverage"]["observed_in_window_bars"] = EXPECTED_BARS
    ok2, errs2 = validate_provenance(bad, require_complete=True, start=START, end=END)
    assert ok2 is False
    assert any("fabricated" in e.lower() for e in errs2)


def test_e2e_provenance_gate_accepts_complete_small_window_manifest(tmp_path):
    """A complete, non-fabricated small-window manifest passes validation (pipeline correctness).

    This validates the gate logic accepts truthful complete manifests; it is NOT a
    283-day spec campaign run and NOT performance evidence.
    """
    from src.data.provenance import validate_provenance

    complete = {
        "fabricated_data": False,
        "real_market_data_intended": True,
        "target_window": {"start": START, "end": END, "expected_hourly_bars": EXPECTED_BARS},
        "symbols": {
            "AAA": {
                "status": "ok",
                "coverage": {
                    "expected_hourly_bars": EXPECTED_BARS,
                    "observed_in_window_bars": EXPECTED_BARS,
                    "gap_count": 0,
                    "complete_for_target_window": True,
                },
            }
        },
        "summary": {"all_complete": True, "ready_for_real_campaign": True, "complete_symbols": ["AAA"]},
    }
    ok, errs = validate_provenance(complete, require_complete=True, start=START, end=END)
    assert ok is True, errs


def test_e2e_multi_symbol_archive_discovery(tmp_path):
    """Archive directory discovery finds per-symbol files; fetch ingests them.

    Synthetic non-evidence; validates archive ingestion path used for real data handoff.
    """
    archive = tmp_path / "archive"
    cache = tmp_path / "cache_hl"
    _write_archive(archive, {
        "BTC": _make_candles("BTC", EXPECTED_BARS, START_MS, close=50000.0, base_vol=200.0),
        "ETH": _make_candles("ETH", EXPECTED_BARS, START_MS, close=3000.0, base_vol=3000.0),
        "SOL": _make_candles("SOL", EXPECTED_BARS, START_MS, close=100.0, base_vol=100000.0),
    })
    r = _run([
        str(SCRIPTS / "fetch_hyperliquid_candles.py"),
        "--source", "archive", "--input-archive", str(archive),
        "--symbols", "BTC,ETH,SOL",  # comma-separated robustness
        "--start", START, "--end", END, "--cache-dir", str(cache),
    ])
    assert r.returncode == 0, f"{r.stdout}\n{r.stderr}"
    manifest = json.loads((cache / "provenance.json").read_text())
    assert manifest["summary"]["symbols_complete"] == 3
    assert manifest["summary"]["all_complete"] is True
