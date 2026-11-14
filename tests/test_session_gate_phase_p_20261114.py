"""Gate tests for the Phase P retention probe and evidence verifier (2026-11-14).

The next session cannot be allowed to satisfy the handoff with prose. These tests
lock the gate so it fails closed unless:
  - a reproducible retention probe (derived counts, non-trivial missing bars)
    backs the 'API blocked' claim, and
  - the mechanical evidence verifier passes on the real artifacts.
"""
from __future__ import annotations

import json

from scripts import session_gate


def _probe(**summary_over):
    summary = {
        "full_window_served": False,
        "expected_hourly_bars": 6792,
        "max_bars_returned": 3898,
        "missing_early_bars_vs_expected": 2894,
        "earliest_served_start_utc": "2026-04-19T14:00:00Z",
    }
    summary.update(summary_over)
    return {
        "schema_version": 1,
        "generated_at_utc": "2026-11-14T00:00:00Z",
        "target_window": {"start": "2025-12-20T00:00:00Z",
                          "end": "2026-09-28T23:00:00Z",
                          "expected_hourly_bars": 6792},
        "universe": {"perps_total": 235, "perps_passing_volume_gate": 29, "probed": 6},
        "probe_summary": summary,
        "per_symbol": [{"symbol": s, "status": "ok", "bars_returned": 3898}
                       for s in ("BTC", "ETH", "HYPE", "ZEC", "SOL", "XRP")],
        "verdict": "FULL_283D_BLOCKED_BY_API_RETENTION",
    }


def _write_probe(tmp_path, data):
    (tmp_path / "hyperliquid_retention_probe.json").write_text(json.dumps(data))


def test_retention_probe_missing_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    ok, detail = session_gate.check_retention_probe()
    assert not ok
    assert "missing" in detail


def test_retention_probe_valid_block_passes(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    _write_probe(tmp_path, _probe())
    ok, detail = session_gate.check_retention_probe()
    assert ok, detail
    assert "6" in detail and "missing" in detail


def test_retention_probe_served_without_campaign_fails(tmp_path, monkeypatch):
    """If the API now serves the window, a blocker claim must be rejected."""
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    _write_probe(tmp_path, _probe(full_window_served=True,
                                  max_bars_returned=6792,
                                  missing_early_bars_vs_expected=0))
    ok, detail = session_gate.check_retention_probe()
    assert not ok
    assert "full campaign" in detail


def test_retention_probe_zero_bars_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    _write_probe(tmp_path, _probe(max_bars_returned=0,
                                  missing_early_bars_vs_expected=6792))
    ok, detail = session_gate.check_retention_probe()
    assert not ok
    assert "did not actually run" in detail


def test_retention_probe_wrong_window_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    data = _probe()
    data["probe_summary"]["expected_hourly_bars"] = 3900
    _write_probe(tmp_path, data)
    ok, detail = session_gate.check_retention_probe()
    assert not ok
    assert "6792" in detail


def test_retention_probe_is_wired_into_checks():
    names = [name for name, _ in session_gate.CHECKS]
    assert "phase_p_retention_probe" in names
    assert "phase_p_evidence_verifier" in names