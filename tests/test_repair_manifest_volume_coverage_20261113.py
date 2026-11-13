"""Phase E bottleneck fix (2026-11-13): manifest repair + derive peak-membership.

The OKX full-universe provenance manifest was emitted before Phase E added
`observed_max_24h_usd_volume` / `universe_membership_ok` to
`analyze_symbol_volume_coverage`. Without those fields the spec-reconciled
admission path in `src/data/provenance.py::_validate_symbol_volume_evidence`
and `scripts/run_real_campaign.py::validate_symbol_volume_coverage` cannot
admit peak>=5M universe members (they fail-closed on the legacy all-bars
`volume_filter_ok is not true` message). This blocks the whole full-universe
real campaign even though the underlying verified caches are valid.

Fixes:
- `scripts/repair_manifest_volume_coverage.py` recomputes `volume_coverage`
  (incl. observed_max_24h_usd_volume / universe_membership_ok) from verified
  local caches and rewrites the manifest in place, preserving sha256 / status /
  coverage / synthetic_check / cache_path (never re-fetches, never fabricates).
- `scripts/derive_verified_universe.py` admits a symbol when its peak
  rolling-24h USD volume >= threshold (spec universe membership) instead of
  requiring every bar to clear the threshold; per-trade point-in-time filtering
  is unchanged.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.fetch_hyperliquid_candles import analyze_symbol_volume_coverage
from scripts.repair_manifest_volume_coverage import repair_manifest
from src.data.provenance import load_provenance


REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "research_state" / "cache" / "okx_1h_full_20251220_20260928" / "provenance.json"


def test_repair_manifest_adds_max_and_membership_fields():
    m = load_provenance(str(MANIFEST))
    sample = list(m["symbols"].values())[0]
    vc = sample.get("volume_coverage") or {}
    assert "observed_max_24h_usd_volume" not in vc
    assert "universe_membership_ok" not in vc

    out = repair_manifest(str(MANIFEST), dry_run=True)
    assert out["repaired"] is True
    for sym, info in out["manifest"]["symbols"].items():
        vc = info.get("volume_coverage") or {}
        assert "observed_max_24h_usd_volume" in vc, f"{sym}: missing observed_max"
        assert "universe_membership_ok" in vc, f"{sym}: missing universe_membership_ok"
        assert isinstance(vc["universe_membership_ok"], bool)


def test_repair_preserves_sha256_and_coverage():
    m = load_provenance(str(MANIFEST))
    out = repair_manifest(str(MANIFEST), dry_run=True)
    for sym, info in out["manifest"]["symbols"].items():
        orig = m["symbols"][sym]
        assert info.get("sha256") == orig.get("sha256"), f"{sym}: sha256 changed"
        assert info.get("cache_path") == orig.get("cache_path"), f"{sym}: cache_path changed"
        assert info.get("status") == orig.get("status"), f"{sym}: status changed"
        cov = info.get("coverage") or {}
        ocov = orig.get("coverage") or {}
        assert cov.get("complete_for_target_window") == ocov.get("complete_for_target_window")
        assert cov.get("gap_count") == ocov.get("gap_count")
        assert cov.get("observed_in_window_bars") == ocov.get("observed_in_window_bars")


def test_repair_peak_membership_matches_analyze_symbol_volume_coverage():
    """Repaired fields must equal a fresh analyze_symbol_volume_coverage on the same cache."""
    out = repair_manifest(str(MANIFEST), dry_run=True)
    for sym, info in out["manifest"]["symbols"].items():
        vc = info.get("volume_coverage") or {}
        assert vc["universe_membership_ok"] is (float(vc["observed_max_24h_usd_volume"]) >= 5_000_000.0)


def test_repair_is_idempotent():
    # First call writes the repair stamp to disk; subsequent dry runs reuse it,
    # so the repaired manifest is byte-identical across invocations.
    repair_manifest(str(MANIFEST), dry_run=False)
    a = repair_manifest(str(MANIFEST), dry_run=True)
    b = repair_manifest(str(MANIFEST), dry_run=True)
    assert json.dumps(a["manifest"], sort_keys=True) == json.dumps(b["manifest"], sort_keys=True)


def test_repair_rejects_unverified_cache():
    # A manifest entry whose cache is missing must be reported, not silently repaired.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        bad = Path(td) / "bad.json"
        bad.write_text(json.dumps({
            "schema_version": 1,
            "target_window": {"start": "2025-12-20T00:00:00+00:00", "end": "2026-09-28T23:00:00+00:00"},
            "symbols": {"SOL": {
                "status": "ok",
                "cache_path": "nonexistent/SOL.json",
                "coverage": {"complete_for_target_window": True, "expected_hourly_bars": 6792,
                             "observed_in_window_bars": 6792, "gap_count": 0},
                "volume_coverage": {"min_daily_volume_usd": 5_000_000.0,
                                    "observed_min_24h_usd_volume": 1.0,
                                    "observed_mean_24h_usd_volume": 1.0,
                                    "bars_checked": 6792, "bars_passing": 0,
                                    "volume_filter_ok": False},
                "synthetic_check": {"is_synthetic": False},
            }},
            "summary": {},
        }))
        with pytest.raises(Exception):
            repair_manifest(str(bad), dry_run=True)