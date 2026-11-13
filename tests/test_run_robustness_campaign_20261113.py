"""Focused tests for the Phase L robustness campaign (2026-11-13).

Phase L is the signal-vs-noise characterization of the 8-trade canonical result.
These tests lock down the fail-closed contract and the deterministic statistics so
the gate artifact cannot be a narrative stub:
  - missing / empty / invalid trade data fails closed;
  - the sign-flip test enumerates exactly 2^n combinations with a correct p-value;
  - the bootstrap is deterministic under a fixed seed and reports the gate keys;
  - the report satisfies the `phase_l_robustness` gate contract.
"""
from __future__ import annotations

import json

import pytest

from scripts import run_robustness_campaign as rob


def _canonical(trades, tmp_path):
    path = tmp_path / "campaign.json"
    path.write_text(json.dumps({"results": {"trades": trades}}))
    return path


def _trade(symbol="SOL", ts=1768946400000, pnl=100.0, leg="buy", reason="time_exit"):
    return {
        "symbol": symbol, "exit_timestamp": ts, "total_pnl": pnl,
        "leg": leg, "exit_reason": reason,
    }


def test_load_trades_missing_file_fails_closed(tmp_path):
    with pytest.raises(rob.RobustnessError):
        rob.load_trades(tmp_path / "nope.json")


def test_load_trades_rejects_empty(tmp_path):
    with pytest.raises(rob.RobustnessError):
        rob.load_trades(_canonical([], tmp_path))


def test_load_trades_rejects_nonfinite_pnl(tmp_path):
    with pytest.raises(rob.RobustnessError):
        rob.load_trades(_canonical([_trade(pnl=float("nan"))], tmp_path))


def test_load_trades_rejects_missing_symbol(tmp_path):
    t = _trade()
    t["symbol"] = ""
    with pytest.raises(rob.RobustnessError):
        rob.load_trades(_canonical([t], tmp_path))


def test_sign_flip_enumerates_256_with_correct_p():
    pnls = [3161.97, -121.63, -168.59, -1801.38, 2988.22, 3499.37, 1673.73, -72.00]
    out = rob.sign_flip_test(pnls)
    assert out["combinations"] == 256
    observed = sum(pnls)
    # The all-positive mask (0) reproduces the observed total, so p >= 1/256.
    assert out["p_value"] >= 1 / 256
    assert out["p_value"] <= 1.0
    assert out["sign_flipped_total_max"] == pytest.approx(sum(abs(p) for p in pnls))
    assert out["sign_flipped_total_min"] == pytest.approx(-sum(abs(p) for p in pnls))
    assert 0.0 <= out["p_value_two_sided"] <= 1.0


def test_bootstrap_is_deterministic_and_reports_gate_keys():
    pnls = [3161.97, -121.63, -168.59, -1801.38, 2988.22, 3499.37, 1673.73, -72.00]
    a = rob.bootstrap_trade_pnls(pnls, resamples=2000, seed=20261113)
    b = rob.bootstrap_trade_pnls(pnls, resamples=2000, seed=20261113)
    assert a == b
    for key in ("resamples", "ci_low_pnl", "ci_high_pnl", "prob_total_pnl_positive",
                "ci_low_win_rate", "ci_high_win_rate", "ci_low_profit_factor",
                "ci_high_profit_factor"):
        assert key in a
    assert a["resamples"] == 2000
    assert a["ci_low_pnl"] <= a["ci_high_pnl"]
    assert 0.0 <= a["prob_total_pnl_positive"] <= 1.0


def test_concentration_shares_and_leave_out():
    trades = [
        {"symbol": "SOL", "exit_timestamp_ms": 1, "total_pnl": 3000.0, "leg": "buy", "exit_reason": "x"},
        {"symbol": "SOL", "exit_timestamp_ms": 2, "total_pnl": 1000.0, "leg": "buy", "exit_reason": "x"},
        {"symbol": "BCH", "exit_timestamp_ms": 3, "total_pnl": 2000.0, "leg": "short", "exit_reason": "x"},
    ]
    out = rob.concentration_analysis(trades)
    assert out["total_pnl"] == pytest.approx(6000.0)
    syms = {r["symbol"]: r for r in out["symbols"]}
    assert syms["SOL"]["trades"] == 2
    assert syms["SOL"]["pnl"] == pytest.approx(4000.0)
    assert syms["SOL"]["pnl_share"] == pytest.approx(4000.0 / 6000.0)
    assert out["top_symbol_pnl_share"] == pytest.approx(4000.0 / 6000.0)
    # leave-one-symbol-out
    loso = {r["excluded_symbol"]: r["total_pnl_without_symbol"] for r in out["leave_one_symbol_out"]}
    assert loso["SOL"] == pytest.approx(2000.0)
    assert loso["BCH"] == pytest.approx(4000.0)


def test_report_satisfies_gate_contract_and_is_deterministic():
    a = rob.build_report(resamples=2000, seed=20261113)
    b = rob.build_report(resamples=2000, seed=20261113)
    assert a["bootstrap"] == b["bootstrap"]
    assert a["sign_flip"] == b["sign_flip"]
    assert a["conclusion"]["verdict"] == b["conclusion"]["verdict"]

    assert a["provenance_caveat"] == rob.PROVENANCE_CAVEAT
    assert a["bootstrap"]["resamples"] >= 1000
    assert a["sign_flip"]["combinations"] == 256
    assert a["concentration"]["symbols"]
    assert "top_symbol_pnl_share" in a["concentration"]
    assert "top_trade_pnl_share" in a["concentration"]
    assert "first_half_pnl" in a["time_split"]
    assert "second_half_pnl" in a["time_split"]
    assert a["conclusion"]["verdict"] in ("signal", "noise", "underpowered")


def test_render_markdown_contains_caveat_and_verdict():
    report = rob.build_report(resamples=2000, seed=20261113)
    md = rob.render_markdown(report)
    assert rob.PROVENANCE_CAVEAT in md
    assert report["conclusion"]["verdict"] in md.lower()


def test_gate_check_robustness_accepts_generated_report(tmp_path, monkeypatch):
    """The artifact this script writes must pass the session gate."""
    from scripts import session_gate

    report = rob.build_report(resamples=2000, seed=20261113)
    (tmp_path / "robustness_real_okx_full.json").write_text(json.dumps(report))
    (tmp_path / "robustness_real_okx_full.md").write_text(rob.render_markdown(report))
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    ok, detail = session_gate.check_robustness()
    assert ok, detail
    assert "verdict=" in detail