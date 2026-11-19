"""C24 margin-fidelity campaign: prereg integrity, arm freeze, and acceptance-gate tests."""
from __future__ import annotations

import hashlib
import importlib
import json
import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import scripts.build_c24_prereg as prereg_mod  # noqa: E402
import scripts.verify_c24_focus_campaign as verify  # noqa: E402

TS = verify.TS
PREREG = REPO / "research_state" / f"c24_prereg_{TS}.json"
PROBE = REPO / "research_state" / f"c24_liquidation_fidelity_probe_{TS}.json"

LIQUIDATION_KEYS = {"liquidation_maint_margin_pct", "liquidation_buffer_pct",
                    "enable_liquidation_checks"}
SIGNAL_SENTINEL = {
    "use_rsi_trigger": True, "rsi_period": 21, "rsi_threshold": 20.0,
    "target_pct": 9.0, "rebound_short_target_pct": 9.0,
    "rebound_short_time_exit_bars": 48, "enable_rebound_short": True,
    "enable_eth_hedge": True, "enable_volume_based_sizing": True,
    "min_daily_volume_usd": 5_000_000.0, "gross_cap_pct": 120.0,
    "entry_spec_literal_next_open": True,
}


def test_prereg_exists_and_is_pre_registered_before_compute():
    assert PREREG.exists(), "C24 prereg must exist before the campaign runs"
    d = json.loads(PREREG.read_text())
    assert d["prereg_status"] == "PRE_REGISTERED_BEFORE_COMPUTE"
    assert d["campaign"] == "C24"
    assert d["binding_task"] == "C24-T1"


def test_prereg_arms_vary_only_liquidation_distance():
    d = json.loads(PREREG.read_text())
    arms = d["arms"]
    assert set(arms) == {"base_6", "d10", "d15", "d30", "noliq"}
    assert arms["d15"]["role"] == "PRIMARY"
    assert arms["base_6"]["role"] == "FIDELITY_ANCHOR"
    assert arms["d15"]["liquidation_distance_pct"] == 15.0
    assert arms["base_6"]["liquidation_distance_pct"] == 6.0


def test_prereg_freezes_signal_path_and_draw_floors():
    d = json.loads(PREREG.read_text())
    frozen = d["signal_path_frozen"]
    for k, want in SIGNAL_SENTINEL.items():
        assert frozen[k] == want, f"signal path {k} must stay frozen at {want}"
    inf = d["inference"]
    assert inf["episode_block_bootstrap_draws"] == 20000
    assert inf["permutation_draws"] == 20000
    assert inf["placebo_portfolio_runs"] == 2000
    assert inf["strata_permutation_draws"] == 2000


def test_prereg_inference_scope_limits_heavy_arm_to_d15():
    d = json.loads(PREREG.read_text())
    scope = d["inference_scope"]
    assert scope["d15"]["full_inference"] is True
    for arm in ("base_6", "d10", "d30", "noliq"):
        assert scope[arm]["full_inference"] is False


def test_stage0_probe_is_descriptive_and_cannot_emit_go():
    assert PROBE.exists()
    d = json.loads(PROBE.read_text())
    assert d["may_emit_go"] is False
    assert d["fidelity_anchor_reproduced"] is True
    assert d["evidence_class"] == "DESCRIPTIVE_NO_INFERENCE"


def test_probe_pooled_sign_flip_is_recorded():
    d = json.loads(PROBE.read_text())
    assert d["pooled"]["base_6"]["all_venue_sum"] < 0
    assert d["pooled"]["d15"]["all_venue_sum"] > 0


def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def _populate_fake_pass(state: Path, prereg_sha: str) -> None:
    for arm in verify.ARMS:
        for v in verify.VENUES:
            for f in verify.FOLDS:
                cfg = dict(SIGNAL_SENTINEL)
                cfg.update({"arm": arm, "liquidation_maint_margin_pct": 5.0,
                            "liquidation_buffer_pct": 1.0})
                pnl = verify.RECORDED_POOLED[v] / 4.0 if arm == "base_6" else 1000.0
                ck = {
                    "campaign": "C24", "arm": arm, "mode": "inference" if arm == "d15" else "anchor",
                    "prereg_sha256": prereg_sha,
                    "campaign_artifact": {"config": cfg,
                                          "results": {"total_pnl": pnl, "num_trades": 10}},
                }
                if arm == "d15":
                    ck["episode"] = {
                        "episode_block_bootstrap": {"resamples": 20000},
                        "temporal_edge_permutation": {"draws_evaluated": 20000,
                                                      "p_null_ge_canonical": 0.01},
                    }
                    ck["placebo"] = {"placebo": {"runs": 2000}, "p_ge_canonical": 0.01}
                _write_json(state / f"c24_ckpt_{arm}_{v}_{f}_{TS}.json", ck)

        token = "FIDELITY_ANCHOR_REPRODUCED" if arm == "base_6" else "C24_REOPENS_C1_C23"
        _write_json(state / f"c24_decision_verdict_{arm}_{TS}.json",
                    {"arm": arm, "token": token, "pooled": {"observed_total": 1.0}})
    _write_json(state / f"c24_decision_verdict_CONSOLIDATED_{TS}.json",
                {"consolidated_verdict": "C24_REOPENS_C1_C23",
                 "arm_pooled_totals": {"d15": 1.0}})


def test_gate_pending_on_empty_state(tmp_path, monkeypatch, capsys):
    (tmp_path / PREREG.name).write_bytes(PREREG.read_bytes())
    (tmp_path / PROBE.name).write_bytes(PROBE.read_bytes())
    monkeypatch.setattr(verify, "STATE", tmp_path)
    rc = verify.main([])
    out = capsys.readouterr().out
    assert rc == 0
    assert "C24 ACCEPTANCE: PENDING" in out


def test_gate_pass_on_complete_consistent_state(tmp_path, monkeypatch, capsys):
    (tmp_path / PREREG.name).write_bytes(PREREG.read_bytes())
    (tmp_path / PROBE.name).write_bytes(PROBE.read_bytes())
    sha = hashlib.sha256((tmp_path / PREREG.name).read_bytes()).hexdigest()
    _populate_fake_pass(tmp_path, sha)
    monkeypatch.setattr(verify, "STATE", tmp_path)
    rc = verify.main([])
    out = capsys.readouterr().out
    assert rc == 0
    assert "C24 ACCEPTANCE: PASS" in out


def test_gate_fails_on_signal_path_drift(tmp_path, monkeypatch, capsys):
    (tmp_path / PREREG.name).write_bytes(PREREG.read_bytes())
    (tmp_path / PROBE.name).write_bytes(PROBE.read_bytes())
    sha = hashlib.sha256((tmp_path / PREREG.name).read_bytes()).hexdigest()
    _populate_fake_pass(tmp_path, sha)
    p = tmp_path / f"c24_ckpt_d15_mexc_2024_{TS}.json"
    ck = json.loads(p.read_text())
    ck["campaign_artifact"]["config"]["rsi_threshold"] = 25.0
    _write_json(p, ck)
    monkeypatch.setattr(verify, "STATE", tmp_path)
    rc = verify.main([])
    out = capsys.readouterr().out
    assert rc == 1
    assert "C24 ACCEPTANCE: FAIL" in out
    assert "signal-path drift" in out


def test_gate_fails_on_fidelity_anchor_mismatch(tmp_path, monkeypatch, capsys):
    (tmp_path / PREREG.name).write_bytes(PREREG.read_bytes())
    (tmp_path / PROBE.name).write_bytes(PROBE.read_bytes())
    sha = hashlib.sha256((tmp_path / PREREG.name).read_bytes()).hexdigest()
    _populate_fake_pass(tmp_path, sha)
    p = tmp_path / f"c24_ckpt_base_6_okx_2023_{TS}.json"
    ck = json.loads(p.read_text())
    ck["campaign_artifact"]["results"]["total_pnl"] += 5000.0
    _write_json(p, ck)
    monkeypatch.setattr(verify, "STATE", tmp_path)
    rc = verify.main([])
    out = capsys.readouterr().out
    assert rc == 1
    assert "fidelity anchor mismatch" in out


def test_gate_fails_on_reduced_draw_counts(tmp_path, monkeypatch, capsys):
    (tmp_path / PREREG.name).write_bytes(PREREG.read_bytes())
    (tmp_path / PROBE.name).write_bytes(PROBE.read_bytes())
    sha = hashlib.sha256((tmp_path / PREREG.name).read_bytes()).hexdigest()
    _populate_fake_pass(tmp_path, sha)
    p = tmp_path / f"c24_ckpt_d15_bitget_2025_{TS}.json"
    ck = json.loads(p.read_text())
    ck["episode"]["temporal_edge_permutation"]["draws_evaluated"] = 500
    _write_json(p, ck)
    monkeypatch.setattr(verify, "STATE", tmp_path)
    rc = verify.main([])
    out = capsys.readouterr().out
    assert rc == 1
    assert "permutation draws 500 < 20000" in out
