"""Gate tests for the Step 3 spec-literal next-open heavy-work check (2026-11-14).

The structural 0-trade canonical funnel must be explained by a REAL-ENGINE run of
the spec's own entry rule, not by prose or an upper-bound count. These tests lock
the gate so it fails closed unless a labeled, non-evidence, real-candle artifact
exists with integer trade/PnL counts and a funnel that demonstrates the gap.
"""
from __future__ import annotations

import json

from scripts import session_gate


def _valid():
    return {
        "label": "NOT_EVIDENCE_EXPLORATORY_FANOUT",
        "performance_evidence": False,
        "fabricated_data": False,
        "real_market_data": True,
        "canonical_baseline_changed": False,
        "results": {"num_trades": 2, "total_pnl": -2670.76},
        "funnel": {"totals": {
            "rsi_crash_hours_passing_trailing_24h_5m_volume": 11,
            "same_bar_rebound_confirm_implementation": 0,
            "generate_signal_canonical_same_bar_confirm": 0,
            "generate_signal_spec_literal_next_open": 8,
        }},
    }


def _write(tmp_path, data):
    (tmp_path / "hyperliquid_exploratory_next_open_latest.json").write_text(json.dumps(data))


def test_missing_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    ok, detail = session_gate.check_exploratory_next_open()
    assert not ok
    assert "missing" in detail


def test_valid_passes(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    _write(tmp_path, _valid())
    ok, detail = session_gate.check_exploratory_next_open()
    assert ok, detail
    assert "2 trades" in detail and "canonical=0" in detail


def test_prose_only_upper_bound_fails(tmp_path, monkeypatch):
    """An artifact with no real-engine trades/PnL must be rejected."""
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    data = _valid()
    data["results"] = {}
    _write(tmp_path, data)
    ok, detail = session_gate.check_exploratory_next_open()
    assert not ok
    assert "num_trades" in detail


def test_performance_evidence_claim_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    data = _valid()
    data["performance_evidence"] = True
    _write(tmp_path, data)
    ok, detail = session_gate.check_exploratory_next_open()
    assert not ok
    assert "performance_evidence" in detail


def test_funnel_gap_not_demonstrated_fails(tmp_path, monkeypatch):
    """If the spec-literal path does not beat the canonical gate, the run proves nothing."""
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    data = _valid()
    data["funnel"]["totals"]["generate_signal_spec_literal_next_open"] = 0
    _write(tmp_path, data)
    ok, detail = session_gate.check_exploratory_next_open()
    assert not ok
    assert "structural funnel" in detail


def test_check_is_wired_into_checks():
    names = [name for name, _ in session_gate.CHECKS]
    assert "phase_r_exploratory_next_open" in names