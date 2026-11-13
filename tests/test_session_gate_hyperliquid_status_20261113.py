"""Gate tests for the Hyperliquid acquisition-status and partial-campaign checks (2026-11-13).

The full 283-day Hyperliquid window is blocked by public API retention. The gate must
still fail closed unless the block, the NOT_EVIDENCE partial run, and the crash census
are all documented with real artifact paths.
"""
from __future__ import annotations

import json

from scripts import session_gate

PARTIAL_CAMPAIGN = "campaign_results_real_hyperliquid_partial_20260419_20260928.json"
CRASH_CENSUS = "hyperliquid_partial_crash_census_20260419_20260928.json"


def _valid_status() -> dict:
    return {
        "schema_version": 1,
        "generated_at_utc": "2026-11-13T21:46:36Z",
        "run_type": "hyperliquid_acquisition_status",
        "target_window": {
            "start": "2025-12-20T00:00:00+00:00",
            "end": "2026-09-28T23:00:00+00:00",
            "expected_hourly_bars": 6792,
        },
        "full_window_available": False,
        "api_probe": {
            "returned_bars": 3900,
            "missing_early_bars": 2892,
            "available_start": "2026-04-19T12:00:00+00:00",
            "available_end": "2026-09-28T23:00:00+00:00",
            "conclusion": "public API retains only the latest ~3900 hourly bars",
        },
        "partial_window": {
            "start": "2026-04-19T12:00:00+00:00",
            "end": "2026-09-28T23:00:00+00:00",
            "expected_hourly_bars": 3900,
            "symbols_complete": ["ADA", "ALGO", "ARB", "ATOM", "AVAX", "BTC", "ETH", "LTC", "NEAR", "OP", "SOL", "TIA"],
            "all_complete": False,
        },
        "partial_campaign": {
            "artifact": PARTIAL_CAMPAIGN,
            "performance_evidence": False,
            "fabricated_data": False,
            "num_trades": 0,
        },
        "crash_census": {
            "artifact": CRASH_CENSUS,
            "symbols": 12,
            "bars": 46800,
            "rsi_crash_events": 8,
            "confirmed_signals": 0,
        },
        "verdict": "FULL_283D_BLOCKED_BY_API_RETENTION; PARTIAL_NOT_EVIDENCE",
        "next_actions": ["obtain operator archive", "extend partial cross-section"],
    }


def _write_status(tmp_path, data: dict) -> None:
    (tmp_path / "hyperliquid_acquisition_status.json").write_text(json.dumps(data))
    (tmp_path / PARTIAL_CAMPAIGN).write_text(json.dumps({"real_market_data": True}))
    (tmp_path / CRASH_CENSUS).write_text(json.dumps({"totals": {}}))


def test_hyperliquid_status_missing_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    ok, detail = session_gate.check_hyperliquid_status()
    assert not ok
    assert "missing" in detail


def test_hyperliquid_status_valid_blocked_run_passes(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    _write_status(tmp_path, _valid_status())
    ok, detail = session_gate.check_hyperliquid_status()
    assert ok, detail
    assert "3900" in detail and "12" in detail


def test_hyperliquid_status_requires_full_campaign_when_available(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    data = _valid_status()
    data["full_window_available"] = True
    _write_status(tmp_path, data)
    ok, detail = session_gate.check_hyperliquid_status()
    assert not ok
    assert "full_campaign" in detail


def test_hyperliquid_status_rejects_performance_evidence_partial(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    data = _valid_status()
    data["partial_campaign"]["performance_evidence"] = True
    _write_status(tmp_path, data)
    ok, detail = session_gate.check_hyperliquid_status()
    assert not ok
    assert "performance_evidence" in detail


def _valid_partial_campaign() -> dict:
    return {
        "real_market_data": True,
        "performance_evidence": False,
        "partial_universe_not_evidence": True,
        "fabricated_data": False,
        "results": {"num_trades": 0, "total_pnl": 0.0},
        "data_provenance": {
            "target_window": {"expected_hourly_bars": 3900},
            "symbols_complete": ["ADA", "ALGO", "ARB", "ATOM", "AVAX", "BTC", "ETH", "LTC", "NEAR", "OP", "SOL", "TIA"],
        },
    }


def test_partial_campaign_missing_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    ok, detail = session_gate.check_hyperliquid_partial_campaign()
    assert not ok
    assert "missing" in detail


def test_partial_campaign_valid_not_evidence_passes(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    (tmp_path / PARTIAL_CAMPAIGN).write_text(json.dumps(_valid_partial_campaign()))
    ok, detail = session_gate.check_hyperliquid_partial_campaign()
    assert ok, detail
    assert "0 trades" in detail


def test_partial_campaign_rejects_performance_claim(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    data = _valid_partial_campaign()
    data["performance_evidence"] = True
    (tmp_path / PARTIAL_CAMPAIGN).write_text(json.dumps(data))
    ok, detail = session_gate.check_hyperliquid_partial_campaign()
    assert not ok
    assert "performance_evidence" in detail


def test_partial_campaign_allows_future_nonzero_run(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    data = _valid_partial_campaign()
    data["results"]["num_trades"] = 2
    data["results"]["total_pnl"] = 123.4
    (tmp_path / PARTIAL_CAMPAIGN).write_text(json.dumps(data))
    ok, detail = session_gate.check_hyperliquid_partial_campaign()
    assert ok, detail
    assert "2 trades" in detail


def test_hyperliquid_checks_are_wired_into_checks():
    names = [name for name, _ in session_gate.CHECKS]
    assert "phase_j3_hyperliquid_status" in names
    assert "phase_j3_hyperliquid_partial_campaign" in names