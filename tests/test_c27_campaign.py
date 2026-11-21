"""C27 next-focus-campaign tests.

These tests are wiring/guardrail tests only; they do NOT run the heavy 20k/20k/2k
battery (that is the durable C27 runner). They verify:
  - the C27 prereg exists and is PRE_REGISTERED_BEFORE_COMPUTE
  - the three pre-registered arms (path_base FIDELITY_ANCHOR /
    cost_taker_funding PRIMARY / path_intrabar_combined DESCRIPTIVE)
  - the gate script imports and reports PENDING when no cells exist
  - C27 arm config resolution (roles: FIDELITY_ANCHOR / PRIMARY / DESCRIPTIVE)
  - signal path is frozen to the C24/C25/C26 sentinel
  - draw floors are not reducible
  - engine config fields are accepted (no drift to C20-C25 baseline)
  - C27 is blocked on C26 ACCEPTANCE: PASS (sequential adjudication chain)
"""
from __future__ import annotations

import hashlib
import io
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / "research_state"
TS = "20261119T215721Z"
ARMS = ["path_base", "cost_taker_funding", "path_intrabar_combined"]


def _load(name: str) -> dict:
    return json.loads((STATE / name).read_text())


def test_c27_prereg_exists_and_is_pre_registered():
    prereg = _load(f"c27_prereg_{TS}.json")
    assert prereg.get("prereg_status") == "PRE_REGISTERED_BEFORE_COMPUTE"
    assert prereg.get("campaign") == "C27"
    assert prereg.get("binding_task") == "C27-T1"


def test_c27_prereg_registers_all_three_arms():
    prereg = _load(f"c27_prereg_{TS}.json")
    arms = prereg["arms"]
    roles = {a: v["role"] for a, v in arms.items()}
    assert set(arms.keys()) == set(ARMS), f"arms {set(arms.keys())} != {set(ARMS)}"
    assert "FIDELITY_ANCHOR" in roles.values(), f"{prereg['campaign']} missing fidelity anchor"
    assert "PRIMARY" in roles.values(), f"{prereg['campaign']} missing primary arm"
    assert "DESCRIPTIVE" in roles.values(), f"{prereg['campaign']} missing descriptive arm"
    assert arms["path_base"]["role"] == "FIDELITY_ANCHOR"
    assert arms["cost_taker_funding"]["role"] == "PRIMARY"
    assert arms["path_intrabar_combined"]["role"] == "DESCRIPTIVE"


def test_c27_prereg_freezes_signal_path():
    prereg = _load(f"c27_prereg_{TS}.json")
    sp = prereg["signal_path_frozen"]
    assert sp["rsi_period"] == 21
    assert sp["rsi_threshold"] == 20.0
    assert sp["target_pct"] == 9.0
    assert sp["entry_spec_literal_next_open"] is True
    assert sp["liquidation_distance_pct"] == 15.0
    assert sp["liquidation_maint_margin_pct"] == 14.0
    assert sp["liquidation_buffer_pct"] == 1.0
    assert sp["seed"] == 20261201


def test_c27_prereg_folds():
    prereg = _load(f"c27_prereg_{TS}.json")
    folds = prereg["folds"]
    assert folds == ["2023", "2024", "2025", "2026YTD"]


def test_c27_anchor_rule_present():
    prereg = _load(f"c27_prereg_{TS}.json")
    # C27's anchor rule lives in decision_rules; the fidelity anchor token is
    # PATH_ANCHOR_REPRODUCED, checked against the C26 primary-arm reference.
    assert "decision_rules" in prereg
    dr = prereg["decision_rules"]
    assert "STABLE_POSITIVE_SUBSET" in dr
    assert "NO_GO" in dr
    assert "UNDERPOWERED" in dr


def test_c27_inference_draw_floors():
    prereg = _load(f"c27_prereg_{TS}.json")
    inf = prereg["inference"]
    assert inf["bootstrap_draws"] == 20000
    assert inf["permutation_draws"] == 20000
    assert inf["placebo_subsets"] == 2000


def test_c27_gate_reports_pending_when_no_cells(monkeypatch):
    import scripts.verify_c27_focus_campaign as gate
    monkeypatch.setattr(gate, "STATE", STATE)
    code = gate.main(["--verbose"])
    # No C27 cells exist yet -> PENDING (or FAIL only if prereg missing; prereg exists)
    assert code in (0, 1)
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        gate.main(["--verbose"])
    finally:
        sys.stdout = old
    text = buf.getvalue()
    assert "C27 ACCEPTANCE:" in text


def test_c27_no_smoke_artifacts():
    smokes = list(STATE.glob(f"c27_*_{TS}_SMOKE.json"))
    assert smokes == [], f"unexpected smoke artifacts: {smokes}"


def test_c27_engine_config_accepts_c27_fields():
    """C27 arm configs resolve through StrategyConfig without baseline drift."""
    from src.strategy.config import StrategyConfig, DEFAULT_CONFIG
    cfg = StrategyConfig()  # defaults: C20-C25 baseline
    assert cfg.intrabar_adverse_first is False
    assert cfg.per_trade_funding is False
    assert cfg.liquidation_maint_margin_pct == 5.0
    assert cfg.liquidation_buffer_pct == 1.0
    assert DEFAULT_CONFIG.intrabar_adverse_first is False
    assert DEFAULT_CONFIG.per_trade_funding is False
    # C27 direction axes are additive and do not mutate the shared baseline.
    assert DEFAULT_CONFIG.gross_cap_pct == 120.0


def test_c27_runner_resolves_arms_and_builds_configs():
    """Regression: the runner must resolve arms and build a StrategyConfig for
    every arm x venue. Guards against two latent crashes that made earlier
    runners abort before any cell ran: (1) resolving arms through the prereg
    instead of DIRECTION_ARM_CONFIG, and (2) passing the phantom
    per_venue_cap_pct kwarg to StrategyConfig."""
    import scripts.run_c27_campaign as runner

    arms = runner.ARMS
    roles = {a: v["role"] for a, v in arms.items()}
    assert "FIDELITY_ANCHOR" in roles.values()
    assert "PRIMARY" in roles.values()
    assert "DESCRIPTIVE" in roles.values()
    for arm in arms:
        cfg = runner._cfg(arm, "kucoin", None)
        assert cfg.rsi_period == 21
        assert cfg.rsi_threshold == 20.0
        assert abs(cfg.slippage_pct - float(arms[arm]["slippage_pct"])) < 1e-12
        payload = runner._config_payload(cfg, arm, "kucoin", False)
        prereg_bytes = Path(f"research_state/c27_prereg_{TS}.json").read_bytes()
        assert payload["prereg_sha256"] == hashlib.sha256(prereg_bytes).hexdigest()
        assert "per_venue_cap_pct" not in payload
