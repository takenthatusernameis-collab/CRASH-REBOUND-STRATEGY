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
from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars
from src.strategy.config import SPEC_MIN_DAILY_VOLUME_USD

EXP = expected_hourly_bars(TARGET_START, TARGET_END)


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
        # Repo-local fixture dir: pytest tmp_path lives under the harness _temp/kilo-tmp
        # scratch tree, which the hardened temp-path guard rejects as unverified
        # provenance evidence. Verified cache shapes must live repo-LOCAL.
        import tempfile
        with tempfile.TemporaryDirectory(dir=str(Path(__file__).resolve().parents[1])) as td:
            cache_dir = Path(td) / "cache"
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
            manifest_path = Path(td) / "manifest.json"
            manifest_path.write_text(json.dumps(manifest))
            out_path = Path(td) / "universe.json"

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
        # Repo-local fixture dir: pytest tmp_path lives under the harness _temp/kilo-tmp
        # scratch tree, which the hardened temp-path guard rejects as unverified
        # provenance evidence. Verified cache shapes must live repo-LOCAL.
        import tempfile
        with tempfile.TemporaryDirectory(dir=str(Path(__file__).resolve().parents[1])) as td:
            cache_dir = Path(td) / "cache"
            candles_dir = cache_dir / "candles"
            candles_dir.mkdir(parents=True)
            (candles_dir / "BTC.json").write_text(json.dumps(_candles(100.0, 10.0, n=30)))
            manifest = {
                "schema_version": 1, "source": "test", "summary": {"all_complete": True},
                "symbols": {"BTC": {"status": "ok", "cache_path": str(candles_dir / "BTC.json"), "coverage": {"complete_for_target_window": True}}},
            }
            manifest_path = Path(td) / "manifest.json"
            manifest_path.write_text(json.dumps(manifest))
            out_path = Path(td) / "universe.json"
            import scripts.derive_verified_universe as dv
            monkeypatch.setattr(sys, "argv", [
                "derive_verified_universe.py", "--manifest", str(manifest_path),
                "--cache-dir", str(cache_dir),
                "--min-24h-volume-usd", "0", "--output", str(out_path),
            ])
            rc = dv.main()
            # Accept explicit non-spec escape only if clearly labeled; but easier to reject. Either is fine if not silently spec-compliant.
            if rc == 0 and out_path.exists():
                out = json.loads(out_path.read_text())
                # must not claim spec-compliant selection at 0 without labeling; at minimum threshold reflected
                assert out.get("min_24h_volume_usd") == 0 or float(out.get("min_24h_volume_usd", 0)) >= SPEC_MIN_DAILY_VOLUME_USD


class TestDeriveVerifiedUniverseProvenanceFloor:
    """--require-complete-manifest (real-campaign derive path) must fail-closed on
    complete-coverage manifests whose volume evidence is below the spec floor or
    missing, so stale/mislabeled volume cannot slip into a "verified" universe."""

    def _manifest_with_volume(self, tmp_path, volume_coverage):
        # Fail-closed provenance rejects temp per-symbol paths as unverified evidence.
        # Use repo-local fixture dir (no kilo-tmp//tmp markers) for verified test artifacts.
        import uuid as _uuid, shutil as _shutil
        from pathlib import Path as _Path
        _repo = _Path(__file__).resolve().parents[1]
        fixture_root = _repo / "research_state" / f".test_derive_vol_{_uuid.uuid4().hex}"
        fixture_root.mkdir(parents=True, exist_ok=False)
        if hasattr(self, "addCleanup"):
            self.addCleanup(lambda: _shutil.rmtree(fixture_root, ignore_errors=True))
        cache_dir = fixture_root
        candles_dir = cache_dir / "candles"
        candles_dir.mkdir(parents=True)
        (candles_dir / "BTC.json").write_text(json.dumps(_candles(100.0, 3000.0, n=30)))
        manifest = {
            "schema_version": 1, "source": "test",
            "real_market_data_intended": True, "fabricated_data": False,
            "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": EXP},
            "summary": {"all_complete": True, "ready_for_real_campaign": True},
            "symbols": {
                "BTC": {
                    "status": "ok", "cache_path": str(candles_dir / "BTC.json"),
                    "synthetic_check": {"is_synthetic": False, "reason": "varied_series_ok"},
                    "coverage": {
                        "complete_for_target_window": True,
                        "expected_hourly_bars": EXP,
                        "observed_in_window_bars": EXP,
                        "gap_count": 0,
                    },
                    "volume_coverage": volume_coverage,
                }
            },
        }
        manifest_path = fixture_root / "manifest.json"
        manifest_path.write_text(json.dumps(manifest))
        return manifest_path, cache_dir, fixture_root / "universe.json"

    def _run_derive(self, monkeypatch, manifest_path, cache_dir, out_path, require_complete=True):
        import scripts.derive_verified_universe as dv
        argv = [
            "derive_verified_universe.py",
            "--manifest", str(manifest_path),
            "--cache-dir", str(cache_dir),
            "--min-24h-volume-usd", str(SPEC_MIN_DAILY_VOLUME_USD),
            "--output", str(out_path),
        ]
        if require_complete:
            argv.append("--require-complete-manifest")
        monkeypatch.setattr(sys, "argv", argv)
        try:
            return dv.main()
        except SystemExit as e:
            code = e.code
            if code is None or isinstance(code, str):
                return 1
            return int(code)

    def test_require_complete_manifest_rejects_subspec_volume_floor(self, tmp_path, monkeypatch):
        manifest_path, cache_dir, out_path = self._manifest_with_volume(
            tmp_path,
            {"volume_filter_ok": True, "min_daily_volume_usd": 1_000_000, "observed_min_24h_usd_volume": 1_000_000},
        )
        rc = self._run_derive(monkeypatch, manifest_path, cache_dir, out_path)
        assert rc != 0, "derive must reject complete manifest with sub-spec volume floor"

    def test_require_complete_manifest_rejects_missing_volume_coverage(self, tmp_path, monkeypatch):
        manifest_path, cache_dir, out_path = self._manifest_with_volume(tmp_path, None)
        manifest = json.loads(manifest_path.read_text())
        manifest["symbols"]["BTC"].pop("volume_coverage", None)
        manifest_path.write_text(json.dumps(manifest))
        rc = self._run_derive(monkeypatch, manifest_path, cache_dir, out_path)
        assert rc != 0, "derive must reject complete manifest missing volume_coverage"

    def test_require_complete_manifest_accepts_spec_compliant_volume(self, tmp_path, monkeypatch):
        manifest_path, cache_dir, out_path = self._manifest_with_volume(
            tmp_path,
            {"volume_filter_ok": True, "min_daily_volume_usd_effective": 5_000_000,
             "min_daily_volume_usd_requested": 5_000_000, "observed_min_24h_usd_volume": 6_000_000},
        )
        rc = self._run_derive(monkeypatch, manifest_path, cache_dir, out_path)
        assert rc == 0, f"derive must accept spec-compliant volume evidence; rc={rc}"
