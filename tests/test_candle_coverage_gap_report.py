"""Track-4 hardening: canonical candle coverage gap report generation.

Deterministic, synthetic (non-evidence). Failing-test-first target.
Report must be correct for the 283d target window, include blocker status,
per-symbol coverage, and never claim readiness when incomplete.
"""
from __future__ import annotations

import json
from pathlib import Path

from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars


def _incomplete_manifest():
    exp = expected_hourly_bars(TARGET_START, TARGET_END)
    return {
        "generated_at_utc": "2026-11-06T05:35:00Z",
        "fabricated_data": False,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": exp},
        "summary": {"all_complete": False, "ready_for_real_campaign": False, "complete_symbols": [], "symbols_requested": 2},
        "symbols": {
            "BTC": {"status": "incomplete", "coverage": {"expected_hourly_bars": exp, "observed_in_window_bars": 4082, "gap_count": 0, "complete_for_target_window": False, "first_timestamp": "2026-04-11T22:00:00Z", "last_timestamp": "2026-09-28T23:00:00Z"}},
            "ETH": {"status": "incomplete", "coverage": {"expected_hourly_bars": exp, "observed_in_window_bars": 4082, "gap_count": 0, "complete_for_target_window": False, "first_timestamp": "2026-04-11T22:00:00Z", "last_timestamp": "2026-09-28T23:00:00Z"}},
        },
    }


def test_generate_gap_report_marks_blocked_and_includes_evidence(tmp_path):
    from scripts.generate_candle_coverage_gap_report import build_gap_report, write_gap_report
    manifest = _incomplete_manifest()
    probe = [{"symbol": "BTC", "count": 4082, "first_t": 1775944800000, "last_t": 1790636400000, "complete": False}]
    report = build_gap_report(manifest=manifest, probe_evidence=probe, generated_at_utc="2026-11-06T05:41:00Z", archive_scan={"searched_paths": ["/tmp"], "verified_archives_found": []})
    assert report["target_window"]["expected_hourly_bars"] == expected_hourly_bars()
    assert report["ready_for_real_campaign"] is False
    assert report["all_complete"] is False
    assert report["blocker"]["item_6c_blocked"] is True
    assert "BTC" in report["symbols"] and report["symbols"]["BTC"]["observed_in_window_bars"] == 4082
    assert report["probe_evidence"] == probe
    assert report["archive_scan"]["verified_archives_found"] == []
    out = tmp_path / "report.json"
    write_gap_report(out, report)
    loaded = json.loads(out.read_text())
    assert loaded["blocker"]["item_6c_blocked"] is True


def test_generate_gap_report_not_ready_when_manifest_missing(tmp_path):
    from scripts.generate_candle_coverage_gap_report import build_gap_report
    report = build_gap_report(manifest=None, probe_evidence=None, generated_at_utc="2026-11-06T05:41:00Z")
    assert report["ready_for_real_campaign"] is False
    assert report["blocker"]["item_6c_blocked"] is True


def test_gap_report_flags_stale_target_window_mismatch(tmp_path):
    from scripts.generate_candle_coverage_gap_report import build_gap_report, write_gap_report
    exp = expected_hourly_bars(TARGET_START, TARGET_END)
    # Simulates the stale wrong-window report that was previously on disk.
    stale_manifest = {
        "generated_at_utc": "2026-11-06T00:00:00Z",
        "fabricated_data": False,
        "target_window": {"start": "2025-01-01T00:00:00Z", "end": "2025-01-01T03:00:00Z", "expected_hourly_bars": 4},
        "summary": {"all_complete": False, "ready_for_real_campaign": False, "complete_symbols": [], "symbols_requested": 1},
        "symbols": {
            "BTC": {"status": "ok", "coverage": {"expected_hourly_bars": 4, "observed_in_window_bars": 4, "gap_count": 0, "complete_for_target_window": True}}
        },
    }
    report = build_gap_report(manifest=stale_manifest, probe_evidence=None, generated_at_utc="2026-11-06T05:41:00Z")
    assert report["target_window"] == {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": exp}
    assert report["target_window"] != stale_manifest["target_window"]
    assert report["target_window_consistent_with_spec"] is False
    assert report["ready_for_real_campaign"] is False
    assert report["all_complete"] is False
    assert report["blocker"]["item_6c_blocked"] is True
    assert report["blocker"].get("target_window_mismatch") is True
    out = tmp_path / "report.json"
    write_gap_report(out, report)
    loaded = json.loads(out.read_text())
    assert loaded["target_window_consistent_with_spec"] is False
    assert loaded["blocker"]["target_window_mismatch"] is True
import json
from pathlib import Path
from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars

def test_gap_report_includes_volume_coverage_evidence(tmp_path):
    from scripts.generate_candle_coverage_gap_report import build_gap_report
    exp = expected_hourly_bars(TARGET_START, TARGET_END)
    manifest = {
        "generated_at_utc": "2026-11-06T05:35:00Z",
        "fabricated_data": False,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": exp},
        "summary": {"all_complete": False, "ready_for_real_campaign": False, "complete_symbols": [], "symbols_requested": 1},
        "symbols": {
            "BTC": {"status": "incomplete", "coverage": {"expected_hourly_bars": exp, "observed_in_window_bars": 4082, "gap_count": 0, "complete_for_target_window": False},
                    "volume_coverage": {"min_daily_volume_usd": 5000000, "observed_min_24h_usd_volume": 42891961.89, "bars_checked": 4082, "bars_passing": 4082, "volume_filter_ok": True}},
        },
    }
    report = build_gap_report(manifest=manifest, probe_evidence=None, generated_at_utc="2026-11-06T08:30:00Z")
    vc = report["symbols"]["BTC"]["volume_coverage"]
    assert vc["min_daily_volume_usd"] == 5000000
    assert vc["volume_filter_ok"] is True
    assert vc["observed_min_24h_usd_volume"] == 42891961.89
    assert vc["bars_passing"] == 4082


def test_canonical_gap_report_always_retains_blocker_fields():
    """Heavy guardrail: the canonical gap report must always carry blocker/provenance
    fields (never degenerate to a simplified gaps-only form), and an incomplete manifest
    must never report ready_for_real_campaign=true."""
    from scripts.generate_candle_coverage_gap_report import build_gap_report
    exp = expected_hourly_bars(TARGET_START, TARGET_END)
    incomplete = {
        "generated_at_utc": "2026-11-06T00:00:00Z",
        "fabricated_data": False,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": exp},
        "summary": {"all_complete": False, "ready_for_real_campaign": False, "complete_symbols": [], "symbols_requested": 2},
        "symbols": {
            "BTC": {"status": "incomplete", "coverage": {"expected_hourly_bars": exp, "observed_in_window_bars": 4082, "gap_count": 0, "complete_for_target_window": False}},
            "ETH": {"status": "incomplete", "coverage": {"expected_hourly_bars": exp, "observed_in_window_bars": 4082, "gap_count": 0, "complete_for_target_window": False}},
        },
    }
    report = build_gap_report(manifest=incomplete, probe_evidence=None, generated_at_utc="2026-11-06T00:00:00Z")
    for key in ("blocker", "ready_for_real_campaign", "all_complete", "target_window_consistent_with_spec", "probe_evidence", "archive_scan"):
        assert key in report, f"missing canonical field {key}"
    assert report["blocker"]["item_6c_blocked"] is True
    assert report["ready_for_real_campaign"] is False
    assert report["all_complete"] is False
    assert report["target_window"] == {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": exp}

def test_gap_report_includes_probe_missing_bars_evidence():
    from scripts.generate_candle_coverage_gap_report import build_gap_report
    exp = expected_hourly_bars(TARGET_START, TARGET_END)
    manifest = _incomplete_manifest()
    probe = [{"symbol": "BTC", "count": 4074, "expected": exp, "first_t_ms": 1775973600000, "last_t_ms": 1790636400000, "complete": False, "probed_at_utc": "2026-11-06T13:24:30Z"}]
    report = build_gap_report(manifest=manifest, probe_evidence=probe, generated_at_utc="2026-11-06T13:25:00Z")
    pgs = report.get("probe_gap_summary")
    assert isinstance(pgs, dict)
    assert pgs["BTC"]["missing_bars"] == exp - 4074
    assert pgs["BTC"]["count"] == 4074
    assert pgs["BTC"]["complete"] is False
    assert report["ready_for_real_campaign"] is False
    assert report["blocker"]["item_6c_blocked"] is True


def test_gap_report_probe_evidence_full_key_generates_gap_summary():
    """Track-4(e): probe_evidence from fetch_hyperliquid_candles.py uses a "full"
    key (dict of symbol->coverage) instead of "symbols". _probe_symbols must handle
    both shapes so probe_gap_summary is never None when probe evidence exists."""
    from scripts.generate_candle_coverage_gap_report import build_gap_report
    exp = expected_hourly_bars(TARGET_START, TARGET_END)
    manifest = _incomplete_manifest()
    probe = {
        "ts": "2026-11-06T14:06:31Z",
        "window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": exp},
        "full": {
            "BTC": {"coin": "BTC", "count": 4074, "first_t": 1775973600000, "last_t": 1790636400000, "complete": False},
            "ETH": {"coin": "ETH", "count": 4074, "first_t": 1775973600000, "last_t": 1790636400000, "complete": False},
        },
        "source": {"kind": "hyperliquid_info_api"},
    }
    report = build_gap_report(manifest=manifest, probe_evidence=probe, generated_at_utc="2026-11-06T14:07:00Z")
    pgs = report.get("probe_gap_summary")
    assert isinstance(pgs, dict), "probe_gap_summary must be a dict when probe evidence exists"
    assert pgs["BTC"]["missing_bars"] == exp - 4074
    assert pgs["BTC"]["count"] == 4074
    assert pgs["BTC"]["complete"] is False
    assert pgs["ETH"]["missing_bars"] == exp - 4074
    assert pgs["ETH"]["count"] == 4074
    assert report["ready_for_real_campaign"] is False
    assert report["blocker"]["item_6c_blocked"] is True


def test_canonical_gap_report_fail_closed_on_verified_provenance():
    """Regression lock (2026-11-08): the canonical gap report must never be
    ready_for_real_campaign when derived from the canonical verified provenance
    whose BTC/ETH series are synthetic placeholders (flat_series_all_bars_identical).
    build_gap_report(manifest=canonical_verified) must fail-closed, and the on-disk
    canonical report must match (not ready, not blocked-cleared, not sourced from a
    /tmp or _temp/kilo-tmp probe archive)."""
    import json
    from pathlib import Path
    from scripts.generate_candle_coverage_gap_report import build_gap_report, write_gap_report

    manifest = json.loads(
        Path("research_state/cache/hyperliquid_verified_283d_btceth/provenance.json").read_text()
    )
    report = build_gap_report(
        manifest=manifest,
        probe_evidence=None,
        generated_at_utc="2026-11-08T22:10:00Z",
        archive_scan={"searched_paths": [], "verified_archives_found": []},
    )
    assert report["ready_for_real_campaign"] is False
    assert report["blocked"] is True
    assert report["item_6c_blocked"] is True
    assert report["real_market_data"] is True  # report field; readiness is the gate
    assert ["BTC", "ETH"] == report.get("summary_contradiction_actual_synthetic_symbols")
    assert "synthetic symbols present" in report["blocker"]["reason"]

    # On-disk canonical artifact must mirror the fail-closed truth and must not be
    # produced from a temp/unverified probe archive claiming readiness.
    canonical = Path("research_state/candle_coverage_gap_report.json")
    loaded = json.loads(canonical.read_text())
    assert loaded["ready_for_real_campaign"] is False
    assert loaded["blocked"] is True
    assert loaded["item_6c_blocked"] is True
    src = (loaded.get("probe_evidence") or {}).get("source") or {}
    ia = src.get("input_archive") or ""
    assert "_temp/kilo-tmp" not in ia and "/tmp/" not in ia, \
        f"canonical report cites temp probe archive: {ia}"
    assert loaded.get("archive_scan", {}).get("verified_archives_found") == []


def test_canonical_gap_report_write_guarded_from_temp_archive():
    """Regression lock (2026-11-09): the CLI/main regeneration path must never
    write the canonical gap report as ready_for_real_campaign when provenance is
    sourced from a temp/unverified archive, even if coverage looks complete.
    build_gap_report alone marks clean coverage ready (the drift vector);
    guard_canonical_write must force it blocked. A verified-clean manifest
    (non-temp source, clean synthetic_check) passes through unchanged."""
    from scripts.generate_candle_coverage_gap_report import build_gap_report, guard_canonical_write

    exp = expected_hourly_bars(TARGET_START, TARGET_END)

    def _clean_symbol_block(sym):
        return {
            "status": "ok",
            "synthetic_check": {"is_synthetic": False},
            "coverage": {
                "expected_hourly_bars": exp,
                "observed_in_window_bars": exp,
                "complete_for_target_window": True,
                "gap_count": 0,
            },
        }

    temp_manifest = {
        "generated_at_utc": "2026-11-09T00:00:00Z",
        "fabricated_data": False,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": exp},
        "source": {"kind": "archive", "input_archive": "/home/runner/work/_temp/kilo-tmp/tmp8tn6l77l/archive.parquet"},
        "summary": {"all_complete": True, "ready_for_real_campaign": True,
                    "complete_symbols": ["BTC", "ETH"], "symbols_requested": 2},
        "symbols": {
            "BTC": _clean_symbol_block("BTC"),
            "ETH": _clean_symbol_block("ETH"),
        },
    }
    report = build_gap_report(manifest=temp_manifest, probe_evidence=None, generated_at_utc="2026-11-09T00:01:00Z")
    assert report["ready_for_real_campaign"] is True, "build_gap_report alone marks clean temp coverage ready"
    guarded = guard_canonical_write(dict(report), temp_manifest)
    assert guarded["ready_for_real_campaign"] is False
    assert guarded["blocked"] is True
    assert guarded["item_6c_blocked"] is True
    assert "provenance not verified-clean" in guarded["blocker"]["reason"]

    # Verified-clean manifest (non-temp source, clean synthetic_check) passes through.
    clean_manifest = json.loads(json.dumps(temp_manifest))
    clean_manifest["source"] = {"kind": "archive", "input_archive": "/mnt/data/verified/archive.parquet"}
    clean_report = build_gap_report(manifest=clean_manifest, probe_evidence=None, generated_at_utc="2026-11-09T00:01:00Z")
    assert clean_report["ready_for_real_campaign"] is True
    guarded_clean = guard_canonical_write(dict(clean_report), clean_manifest)
    assert guarded_clean["ready_for_real_campaign"] is True
    assert guarded_clean["blocked"] is False
