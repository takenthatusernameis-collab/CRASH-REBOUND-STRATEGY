"""2026-11-07 failing-tests-first: derive_verified_universe must not select/label
synthetic, error, or incomplete symbols as verified real-market universe evidence.

Campaign item 4 / provenance hardening. The committed universe_verified.json was
produced from a manifest whose BTC/ETH entries are status=error +
synthetic_check.is_synthetic=true; selecting those symbols or labeling
real_market_data=true is a false provenance claim. Derivation must fail closed on
manifest synthetic/error/incomplete evidence and on runtime-detected synthetic
candles, and must never emit real_market_data=true from a non-complete/synthetic
source.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.derive_verified_universe import main as derive_main
from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars

EXP = expected_hourly_bars(TARGET_START, TARGET_END)


def _flat_candles(n=30, start_ms=1_700_000_000_000):
    # Constant OHLCV => runtime synthetic.
    return [
        {"timestamp_ms": start_ms + i * 3_600_000, "open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0, "volume": 1_000_000.0}
        for i in range(n)
    ]


def _varied_candles(n=30, start_ms=1_700_000_000_000):
    out = []
    for i in range(n):
        px = 100.0 + i * 0.5
        out.append({"timestamp_ms": start_ms + i * 3_600_000, "open": px, "high": px + 1, "low": px - 1, "close": px + 0.2, "volume": 3000.0})
    return out


def _run(argv, monkeypatch):
    import scripts.derive_verified_universe as dv
    monkeypatch.setattr(sys, "argv", argv)
    try:
        return dv.main()
    except SystemExit as e:
        code = e.code
        return 1 if (code is None or isinstance(code, str)) else int(code)


class TestDeriveRejectsSyntheticManifestSymbols:
    def _setup(self, tmp_path, *, symbol_status="error", synthetic=True, candles=None, summary_all_complete=False):
        cache_dir = tmp_path / "cache"
        candles_dir = cache_dir / "candles"
        candles_dir.mkdir(parents=True)
        (candles_dir / "BTC.json").write_text(json.dumps(candles or _varied_candles()))
        manifest = {
            "schema_version": 1, "source": "test", "fabricated_data": False,
            "summary": {"all_complete": summary_all_complete, "ready_for_real_campaign": False},
            "target_window": {"start": "2026-01-01T00:00:00Z", "end": "2026-01-02T05:00:00Z"},
            "symbols": {
                "BTC": {
                    "status": symbol_status,
                    "cache_path": str(candles_dir / "BTC.json"),
                    "synthetic_check": {"is_synthetic": synthetic, "reason": "flat_series_all_bars_identical" if synthetic else "varied_series_ok"},
                    "coverage": {"complete_for_target_window": symbol_status == "ok" and not synthetic},
                }
            },
        }
        mp = tmp_path / "manifest.json"
        mp.write_text(json.dumps(manifest))
        return mp, cache_dir, tmp_path / "universe.json"

    def test_non_require_complete_does_not_select_synthetic_manifest_symbol(self, tmp_path, monkeypatch):
        mp, cache_dir, out = self._setup(tmp_path, symbol_status="error", synthetic=True)
        rc = _run(["derive_verified_universe.py", "--manifest", str(mp), "--cache-dir", str(cache_dir), "--output", str(out)], monkeypatch)
        assert out.exists() or rc == 0
        if out.exists():
            d = json.loads(out.read_text())
            assert "BTC" not in (d.get("selected_symbols") or []), d
            assert d.get("real_market_data") is False

    def test_runtime_flat_candles_excluded_even_if_manifest_claims_ok(self, tmp_path, monkeypatch):
        mp, cache_dir, out = self._setup(tmp_path, symbol_status="ok", synthetic=False, candles=_flat_candles(), summary_all_complete=False)
        # manifest lies (says non-synthetic) but runtime candles are flat
        rc = _run(["derive_verified_universe.py", "--manifest", str(mp), "--cache-dir", str(cache_dir), "--output", str(out)], monkeypatch)
        if out.exists():
            d = json.loads(out.read_text())
            assert "BTC" not in (d.get("selected_symbols") or []), d
            assert d.get("real_market_data") is False

    def test_incomplete_coverage_not_selected(self, tmp_path, monkeypatch):
        mp, cache_dir, out = self._setup(tmp_path, symbol_status="incomplete", synthetic=False)
        _run(["derive_verified_universe.py", "--manifest", str(mp), "--cache-dir", str(cache_dir), "--output", str(out)], monkeypatch)
        if out.exists():
            d = json.loads(out.read_text())
            assert "BTC" not in (d.get("selected_symbols") or []), d

    def test_real_market_data_never_true_without_complete_verified_non_synthetic_source(self, tmp_path, monkeypatch):
        mp, cache_dir, out = self._setup(tmp_path, symbol_status="ok", synthetic=False, candles=_varied_candles(), summary_all_complete=False)
        # even if symbol looks ok locally, summary_all_complete false means manifest not fully verified complete
        _run(["derive_verified_universe.py", "--manifest", str(mp), "--cache-dir", str(cache_dir), "--output", str(out)], monkeypatch)
        if out.exists():
            d = json.loads(out.read_text())
            # A truthful derivation must not claim real_market_data=true when source summary is incomplete/unverified.
            assert d.get("real_market_data") is False or d.get("selected_count", 0) == 0
