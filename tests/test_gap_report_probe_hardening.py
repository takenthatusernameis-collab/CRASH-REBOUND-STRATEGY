"""Track-4e heavy hardening: gap report probe evidence is evidence-only and
must never allow optimistic readiness when probe shows missing bars.

Synthetic/non-evidence tests; failing-test-first guardrails for regressions.
"""
from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars
from scripts.generate_candle_coverage_gap_report import build_gap_report


def _complete_manifest():
    exp = expected_hourly_bars(TARGET_START, TARGET_END)
    synth = {"is_synthetic": False, "reason": "ok"}
    return {
        "generated_at_utc": "2026-11-06T00:00:00Z",
        "fabricated_data": False,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": exp},
        "summary": {"all_complete": True, "ready_for_real_campaign": True, "complete_symbols": ["BTC", "ETH"], "symbols_requested": 2},
        "symbols": {
            "BTC": {"status": "ok", "coverage": {"expected_hourly_bars": exp, "observed_in_window_bars": exp, "gap_count": 0, "complete_for_target_window": True}, "synthetic_check": synth},
            "ETH": {"status": "ok", "coverage": {"expected_hourly_bars": exp, "observed_in_window_bars": exp, "gap_count": 0, "complete_for_target_window": True}, "synthetic_check": synth},
        },
    }


def test_probe_gap_summary_reports_missing_bars_and_blocks_ready():
    exp = expected_hourly_bars(TARGET_START, TARGET_END)
    probe = {
        "ts": "2026-11-06T15:10:00Z",
        "source": "hyperliquid_info_api_candleSnapshot_1h",
        "symbols": {
            "BTC": {"count": 4074, "first_t_ms": 1775973600000, "last_t_ms": 1790636400000, "complete": False},
            "ETH": {"count": 4074, "first_t_ms": 1775973600000, "last_t_ms": 1790636400000, "complete": False},
        },
    }
    r = build_gap_report(manifest=_complete_manifest(), probe_evidence=probe, generated_at_utc="2026-11-06T15:10:49Z")
    assert r["ready_for_real_campaign"] is False
    assert r["all_complete"] is False
    assert r["blocked"] is True
    assert r["item_6c_blocked"] is True
    assert r["blocker"]["item_6c_blocked"] is True
    assert r["probe_gap_summary"]["BTC"]["count"] == 4074
    assert r["probe_gap_summary"]["BTC"]["expected"] == exp
    assert r["probe_gap_summary"]["BTC"]["missing_bars"] == exp - 4074
    assert r["probe_gap_summary"]["BTC"]["complete"] is False
    assert r["probe_gap_summary"]["BTC"]["first_t_ms"] == 1775973600000
    assert r["probe_summary"]["all_complete"] is False
    assert r["probe_summary"]["target_expected_bars"] == exp


def test_probe_list_form_supported_and_blocks():
    exp = expected_hourly_bars(TARGET_START, TARGET_END)
    probe = [{"symbol": "BTC", "count": 4074, "complete": False}]
    r = build_gap_report(manifest=_complete_manifest(), probe_evidence=probe, generated_at_utc="2026-11-06T15:10:49Z")
    assert r["ready_for_real_campaign"] is False
    assert r["blocker"]["item_6c_blocked"] is True
    assert r["probe_gap_summary"]["BTC"]["missing_bars"] == exp - 4074


def test_no_probe_preserves_manifest_consistency_without_optimism_bypass():
    # Without probe evidence, report follows manifest summary for this target window.
    # This does not create evidence; real campaign gate remains scripts/run_real_campaign/provenance.
    r = build_gap_report(manifest=_complete_manifest(), probe_evidence=None, generated_at_utc="2026-11-06T15:10:49Z")
    assert r["ready_for_real_campaign"] is True
    assert r["blocker"]["item_6c_blocked"] is False
    assert r["probe_gap_summary"] is None
