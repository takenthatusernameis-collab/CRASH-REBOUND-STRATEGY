"""Gate tests for the Phase Q full-universe Hyperliquid coverage check (2026-11-14).

The next session cannot claim "data unavailable" from a 6-symbol probe. These
tests lock the gate so it fails closed unless the whole qualifying universe was
probed, a real partial-window snapshot was captured for every served symbol, a
cross-sectional crash census was run over the complete symbols, and a
NOT_EVIDENCE partial campaign was executed.
"""
from __future__ import annotations

import json

from scripts import session_gate


def _valid():
    return {
        "schema_version": 1,
        "generated_at_utc": "2026-11-14T02:00:00Z",
        "api_retention_probe": {
            "perps_total": 235,
            "perps_passing_volume_gate": 29,
            "probed": 29,
        },
        "universe_snapshot": {
            "symbols_requested": 29,
            "symbols_complete": 27,
            "symbols_incomplete_or_error": 2,
            "complete_symbols": [f"S{i}" for i in range(27)],
        },
        "crash_census": {
            "symbols": 27,
            "bars": 105138,
            "rsi_crash_events": 13,
            "confirmed_signals": 0,
        },
        "partial_campaign": {"performance_evidence": False, "num_trades": 0},
        "verdict": "PARTIAL_WINDOW_DECAYING; FULL_283D_BLOCKED_BY_API_RETENTION; STRATEGY_UNDERPOWERED",
    }


def _write(tmp_path, data):
    (tmp_path / "hyperliquid_universe_coverage.json").write_text(json.dumps(data))


def test_missing_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    ok, detail = session_gate.check_universe_coverage()
    assert not ok
    assert "missing" in detail


def test_valid_passes(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    _write(tmp_path, _valid())
    ok, detail = session_gate.check_universe_coverage()
    assert ok, detail
    assert "27" in detail and "13" in detail


def test_partial_universe_probe_fails(tmp_path, monkeypatch):
    """A 6-symbol probe of a 29-symbol universe must be rejected."""
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    data = _valid()
    data["api_retention_probe"]["probed"] = 6
    _write(tmp_path, data)
    ok, detail = session_gate.check_universe_coverage()
    assert not ok
    assert "not probed" in detail


def test_census_symbol_mismatch_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    data = _valid()
    data["crash_census"]["symbols"] = 12
    _write(tmp_path, data)
    ok, detail = session_gate.check_universe_coverage()
    assert not ok
    assert "must equal complete" in detail


def test_performance_claim_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    data = _valid()
    data["partial_campaign"]["performance_evidence"] = True
    _write(tmp_path, data)
    ok, detail = session_gate.check_universe_coverage()
    assert not ok
    assert "performance_evidence" in detail


def test_verdict_must_record_block(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    data = _valid()
    data["verdict"] = "ALL GOOD"
    _write(tmp_path, data)
    ok, detail = session_gate.check_universe_coverage()
    assert not ok
    assert "block" in detail.lower()


def test_check_is_wired_into_checks():
    names = [name for name, _ in session_gate.CHECKS]
    assert "phase_q_universe_coverage" in names