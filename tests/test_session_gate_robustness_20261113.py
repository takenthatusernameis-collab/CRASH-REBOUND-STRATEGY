"""Gate tests for the Phase L robustness artifact (2026-11-13).

Phase L is the signal-vs-noise check for the 8-trade canonical result. The gate
must fail closed on a missing or narrative-only artifact, and must accept the
documented schema with an explicit verdict.
"""
from __future__ import annotations

import json

from scripts import session_gate

CAVEAT = session_gate.PROVENANCE_CAVEAT


def _valid_artifact() -> dict:
    return {
        "generated_at_utc": "2026-11-13T18:00:00Z",
        "provenance_caveat": CAVEAT,
        "bootstrap": {
            "resamples": 10000,
            "ci_low_pnl": -5000.0,
            "ci_high_pnl": 20000.0,
            "prob_total_pnl_positive": 0.93,
        },
        "sign_flip": {"combinations": 256, "p_value": 0.035},
        "concentration": {
            "symbols": ["SOL", "BCH", "ETH", "LINK", "AVAX"],
            "top_symbol_pnl_share": 0.42,
            "top_trade_pnl_share": 0.31,
        },
        "time_split": {"first_half_pnl": 5000.0, "second_half_pnl": 4159.0},
        "conclusion": {"verdict": "signal"},
    }


def _write(tmp_path, data: dict, md_text: str) -> None:
    (tmp_path / "robustness_real_okx_full.json").write_text(json.dumps(data))
    (tmp_path / "robustness_real_okx_full.md").write_text(md_text)


def test_robustness_missing_artifact_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    ok, detail = session_gate.check_robustness()
    assert not ok
    assert "missing" in detail


def test_robustness_valid_artifact_passes(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    _write(
        tmp_path,
        _valid_artifact(),
        f"# Robustness\n\n{CAVEAT}\n\nVerdict: signal\n",
    )
    ok, detail = session_gate.check_robustness()
    assert ok, detail
    assert "verdict=signal" in detail


def test_robustness_narrative_only_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    data = _valid_artifact()
    del data["sign_flip"]
    _write(tmp_path, data, f"# Robustness\n\n{CAVEAT}\n\nVerdict: signal\n")
    ok, detail = session_gate.check_robustness()
    assert not ok
    assert "sign_flip" in detail


def test_robustness_rejects_unknown_verdict(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    data = _valid_artifact()
    data["conclusion"]["verdict"] = "probably"
    _write(tmp_path, data, f"# Robustness\n\n{CAVEAT}\n\nVerdict: probably\n")
    ok, detail = session_gate.check_robustness()
    assert not ok
    assert "verdict" in detail


def test_robustness_is_wired_into_checks():
    names = [name for name, _ in session_gate.CHECKS]
    assert "phase_l_robustness" in names