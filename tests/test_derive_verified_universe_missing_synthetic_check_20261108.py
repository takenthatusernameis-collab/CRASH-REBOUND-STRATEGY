"""Failing-test-first regression: derive_verified_universe must fail-closed on
missing manifest synthetic_check (unverified provenance entry).

Campaign item 3 residual (2026-11-08): a symbol whose manifest entry lacks
synthetic_check is unverified evidence. The per-symbol selection path must
exclude it explicitly (not select it and later trip an inconsistent refusal),
matching validate_provenance / complete_symbol_subset / gap-report semantics.

Deterministic, synthetic temp fixtures, non-evidence.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _varied_candles(start_iso: str, n: int) -> list:
    # Hourly ISO timestamps starting at start_iso; varied OHLCV so runtime
    # synthetic detection does not mask the manifest-guardrail defect.
    import math
    from datetime import datetime, timedelta, timezone

    dt = datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
    out = []
    for i in range(n):
        ts = dt + timedelta(hours=i)
        px = 60000.0 + 1000.0 * math.sin(i / 2.0) + i
        out.append({
            "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "timestamp_ms": int(ts.timestamp() * 1000),
            "open": px, "high": px + 60, "low": px - 60,
            "close": px + 15, "volume": float(3_000_000_000 + (i % 10) * 10_000_000),
        })
    return out


def _write_manifest(path: Path, *, include_synthetic_check: bool, start: str, end: str, n: int, cache_path: str) -> None:
    entry = {
        "status": "ok",
        "cache_path": cache_path,
        "coverage": {
            "expected_hourly_bars": n,
            "observed_in_window_bars": n,
            "gap_count": 0,
            "complete_for_target_window": True,
        },
        "volume_coverage": {
            "volume_filter_ok": True,
            "min_daily_volume_usd": 5_000_000.0,
            "observed_min_24h_usd_volume": 10_000_000.0,
        },
    }
    if include_synthetic_check:
        entry["synthetic_check"] = {"is_synthetic": False, "reason": "varied_series_ok"}
    manifest = {
        "real_market_data_intended": True,
        "fabricated_data": False,
        "target_window": {"start": start, "end": end, "expected_hourly_bars": n},
        "symbols": {"BTC": entry},
        "summary": {"all_complete": False, "ready_for_real_campaign": False},
    }
    path.write_text(json.dumps(manifest, indent=2) + "\n")


def test_missing_manifest_synthetic_check_excluded_fail_closed(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    start, end, n = "2025-12-20T00:00:00Z", "2025-12-20T02:00:00Z", 3
    cache_dir = tmp_path / "cache"
    candles_dir = cache_dir / "candles"
    candles_dir.mkdir(parents=True)
    candle_path = candles_dir / "BTC.json"
    candle_path.write_text(json.dumps(_varied_candles(start, n)) + "\n")
    manifest_path = tmp_path / "provenance.json"
    _write_manifest(manifest_path, include_synthetic_check=False, start=start, end=end, n=n,
                    cache_path=str(candle_path.relative_to(root)) if False else str(candle_path))
    out_path = tmp_path / "universe.json"

    proc = subprocess.run(
        [sys.executable, str(root / "scripts" / "derive_verified_universe.py"),
         "--manifest", str(manifest_path), "--cache-dir", str(cache_dir),
         "--min-24h-volume-usd", "5000000", "--output", str(out_path)],
        cwd=str(root), capture_output=True, text=True,
    )
    # Must not emit a selected verified symbol; missing synthetic_check is unverified.
    assert proc.returncode == 0, proc.stdout + "\n" + proc.stderr
    data = json.loads(out_path.read_text())
    rec = data["report"]["BTC"]
    assert rec.get("selected") is False
    assert "synthetic_check" in (rec.get("excluded_reason") or "") or "unverified" in (rec.get("excluded_reason") or ""), rec
    assert data.get("selected_symbols") == []
    assert data.get("real_market_data") is False
    assert "0 selected symbols" in proc.stdout or data.get("selected_count") == 0


def test_present_clean_synthetic_check_allows_selection_with_full_evidence(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    start, end, n = "2025-12-20T00:00:00Z", "2025-12-20T02:00:00Z", 3
    cache_dir = tmp_path / "cache"
    candles_dir = cache_dir / "candles"
    candles_dir.mkdir(parents=True)
    candle_path = candles_dir / "BTC.json"
    candle_path.write_text(json.dumps(_varied_candles(start, n)) + "\n")
    manifest_path = tmp_path / "provenance.json"
    _write_manifest(manifest_path, include_synthetic_check=True, start=start, end=end, n=n,
                    cache_path=str(candle_path))
    out_path = tmp_path / "universe.json"

    proc = subprocess.run(
        [sys.executable, str(root / "scripts" / "derive_verified_universe.py"),
         "--manifest", str(manifest_path), "--cache-dir", str(cache_dir),
         "--min-24h-volume-usd", "5000000", "--output", str(out_path)],
        cwd=str(root), capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stdout + "\n" + proc.stderr
    data = json.loads(out_path.read_text())
    rec = data["report"]["BTC"]
    assert rec.get("selected") is True, rec
    assert data.get("selected_symbols") == ["BTC"]
    assert data.get("real_market_data") is True
