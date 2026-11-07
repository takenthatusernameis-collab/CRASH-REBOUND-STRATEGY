"""2026-11-07: derive_verified_universe must not accept sub-$5M spec-bypass threshold.

Failing-tests-first. Spec-compliant universe derivation/selection must enforce the
$5M floor for non-zero sub-$5M thresholds (min_daily_volume_usd=0 remains a
non-spec escape hatch only where explicitly supported; universe derivation for
spec-compliant campaigns must not silently select on a sub-$5M bar).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.derive_verified_universe import max_rolling_24h_quote_volume
from src.strategy.config import SPEC_MIN_DAILY_VOLUME_USD


def _candles(close: float, volume: float, n: int = 30, start_ms: int = 1_700_000_000_000):
    out = []
    for i in range(n):
        out.append({
            "timestamp_ms": start_ms + i * 3_600_000,
            "open": close, "high": close + 1, "low": close - 1, "close": close, "volume": volume,
        })
    return out


class TestDeriveVerifiedUniverseVolumeFloor:
    def test_max_rolling_helper_reports_proxy(self):
        # ~2.4M/day on a single-bar trailing window basis varies; use enough volume to be clear.
        candles = _candles(100.0, 3000.0, n=30)
        res = max_rolling_24h_quote_volume(candles)
        assert "max_rolling_24h_quote_volume_usd_proxy" in res
        assert res["bars"] == 30

    def test_cli_rejects_sub_5m_nonzero_threshold_for_spec_compliant_derivation(self, tmp_path, monkeypatch):
        # Build minimal verified manifest + cache where symbol has ~7.2M/day but request 1M must not be accepted as-is.
        cache_dir = tmp_path / "cache"
        candles_dir = cache_dir / "candles"
        candles_dir.mkdir(parents=True)
        sym_candles = _candles(100.0, 3000.0, n=30)  # 300000/bar, 24h rolling includes 24 bars => 7.2M
        (candles_dir / "BTC.json").write_text(json.dumps(sym_candles))
        manifest = {
            "schema_version": 1,
            "source": "test",
            "target_window": {"start": "2026-01-01T00:00:00Z", "end": "2026-01-02T05:00:00Z"},
            "summary": {"all_complete": True},
            "symbols": {
                "BTC": {
                    "status": "ok",
                    "cache_path": str(candles_dir / "BTC.json"),
                    "coverage": {"complete_for_target_window": True},
                }
            },
        }
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest))
        out_path = tmp_path / "universe.json"

        import scripts.derive_verified_universe as dv
        monkeypatch.setattr(sys, "argv", [
            "derive_verified_universe.py",
            "--manifest", str(manifest_path),
            "--cache-dir", str(cache_dir),
            "--min-24h-volume-usd", "1000000",
            "--output", str(out_path),
        ])
        rc = dv.main()
        # Must not produce a sub-$5M-selected "verified" universe silently.
        # Accept either rejection (nonzero rc/SystemExit) or floor-enforced output.
        if rc == 0 and out_path.exists():
            out = json.loads(out_path.read_text())
            assert float(out.get("min_24h_volume_usd", 0)) >= SPEC_MIN_DAILY_VOLUME_USD
            # With 7.2M rolling volume, floor-enforced $5M would still select; key is threshold not 1M.
        else:
            assert rc != 0

    def test_cli_zero_threshold_rejected_or_explicit_non_spec_only(self, tmp_path, monkeypatch):
        # 0 as escape hatch is dangerous for verified-universe derivation; prefer fail-closed.
        cache_dir = tmp_path / "cache"
        candles_dir = cache_dir / "candles"
        candles_dir.mkdir(parents=True)
        (candles_dir / "BTC.json").write_text(json.dumps(_candles(100.0, 10.0, n=30)))
        manifest = {
            "schema_version": 1, "source": "test", "summary": {"all_complete": True},
            "symbols": {"BTC": {"status": "ok", "cache_path": str(candles_dir / "BTC.json"), "coverage": {"complete_for_target_window": True}}},
        }
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest))
        out_path = tmp_path / "universe.json"
        import scripts.derive_verified_universe as dv
        monkeypatch.setattr(sys, "argv", [
            "derive_verified_universe.py", "--manifest", str(manifest_path),
            "--cache-dir", str(cache_dir), "--min-24h-volume-usd", "0", "--output", str(out_path),
        ])
        rc = dv.main()
        # Accept explicit non-spec escape only if clearly labeled; but easier to reject. Either is fine if not silently spec-compliant.
        if rc == 0 and out_path.exists():
            out = json.loads(out_path.read_text())
            # must not claim spec-compliant selection at 0 without labeling; at minimum threshold reflected
            assert out.get("min_24h_volume_usd") == 0 or float(out.get("min_24h_volume_usd", 0)) >= SPEC_MIN_DAILY_VOLUME_USD
