"""Track-4 hardening: probe evidence must never override manifest/readiness gate.

Deterministic synthetic (non-evidence). Failing-test-first target.
"""
from __future__ import annotations

from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars


def _complete_manifest():
    exp = expected_hourly_bars(TARGET_START, TARGET_END)
    synth = {"is_synthetic": False, "reason": "ok"}
    return {
        "generated_at_utc": "2026-11-06T00:00:00Z",
        "fabricated_data": False,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": exp},
        "summary": {"all_complete": True, "ready_for_real_campaign": True, "complete_symbols": ["BTC"], "symbols_requested": 1},
        "symbols": {"BTC": {"status": "ok", "synthetic_check": synth, "coverage": {"expected_hourly_bars": exp, "observed_in_window_bars": exp, "gap_count": 0, "complete_for_target_window": True}}},
    }


def _incomplete_manifest():
    exp = expected_hourly_bars(TARGET_START, TARGET_END)
    m = _complete_manifest()
    m["summary"] = {"all_complete": False, "ready_for_real_campaign": False, "complete_symbols": [], "symbols_requested": 1}
    m["symbols"]["BTC"] = {"status": "incomplete", "coverage": {"expected_hourly_bars": exp, "observed_in_window_bars": exp - 100, "gap_count": 0, "complete_for_target_window": False}}
    return m


def test_complete_probe_does_not_unblock_incomplete_manifest():
    from scripts.generate_candle_coverage_gap_report import build_gap_report
    probe = {"symbols": {"BTC": {"count": 6792, "expected": 6792, "complete": True}}}
    report = build_gap_report(manifest=_incomplete_manifest(), probe_evidence=probe, generated_at_utc="2026-11-06T13:30:00Z")
    assert report["ready_for_real_campaign"] is False
    assert report["blocker"]["item_6c_blocked"] is True
    assert report["probe_summary"]["all_complete"] is True


def test_incomplete_probe_blocks_even_if_manifest_complete():
    from scripts.generate_candle_coverage_gap_report import build_gap_report
    probe = {"symbols": {"BTC": {"count": 4078, "expected": 6792, "complete": False}}}
    report = build_gap_report(manifest=_complete_manifest(), probe_evidence=probe, generated_at_utc="2026-11-06T13:30:00Z")
    assert report["ready_for_real_campaign"] is False
    assert report["blocker"]["item_6c_blocked"] is True
    assert report["probe_summary"]["all_complete"] is False


def test_probe_expected_mismatch_flagged_in_summary():
    from scripts.generate_candle_coverage_gap_report import build_gap_report
    exp = expected_hourly_bars(TARGET_START, TARGET_END)
    probe = {"symbols": {"BTC": {"count": 4078, "expected": 5000, "complete": False}}}
    report = build_gap_report(manifest=_incomplete_manifest(), probe_evidence=probe, generated_at_utc="2026-11-06T13:30:00Z")
    ps = report["probe_summary"]
    assert ps["symbols_probed"] == 1
    assert ps.get("expected_mismatch_symbols", 0) >= 1 or ps.get("target_expected_bars") == exp
