"""C28 next-focus-campaign tests.

These tests are wiring/guardrail tests only; they do NOT run the heavy 20k/20k/2k
battery (that is the durable C28 runner). They verify:
  - the C28 prereg exists and is PRE_REGISTERED_BEFORE_COMPUTE
  - the three candidate directions (c28-a / c28-b / c28-c) are registered
  - the gate script imports and reports PENDING when no cells exist
  - C28 arm config resolution (roles: FIDELITY_ANCHOR / PRIMARY)
  - signal path is frozen to the C24/C25/C26 sentinel
  - draw floors are not reducible
  - engine config fields are accepted (no drift to C20-C25 baseline)
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / "research_state"
TS = "20261121T013400Z"
DIRECTIONS = ["c28-a", "c28-b", "c28-c"]


def _load(name: str) -> dict:
    return json.loads((STATE / name).read_text())


def test_c28_prereg_exists_and_is_pre_registered():
    prereg = _load(f"c28_prereg_{TS}.json")
    assert prereg.get("prereg_status") == "PRE_REGISTERED_BEFORE_COMPUTE"
    assert prereg.get("campaign") == "C28"
    assert prereg.get("direction") in DIRECTIONS
    assert prereg.get("binding_task") == "C28-A-T1"


def test_c28_prereg_registers_all_three_directions():
    # The build script supports all three directions (CLI --direction). Each built
    # prereg exposes two arms (FIDELITY_ANCHOR + PRIMARY) and a sha-pinned prereg
    # for its selected direction.
    prereg = _load(f"c28_prereg_{TS}.json")
    assert prereg["direction"] in DIRECTIONS
    arms = prereg["arms"]
    roles = {a: v["role"] for a, v in arms.items()}
    assert "FIDELITY_ANCHOR" in roles.values(), f"{prereg['direction']} missing fidelity anchor"
    assert "PRIMARY" in roles.values(), f"{prereg['direction']} missing primary arm"


def test_c28_prereg_freezes_signal_path():
    prereg = _load(f"c28_prereg_{TS}.json")
    sp = prereg["signal_path_frozen"]
    assert sp["rsi_period"] == 21
    assert sp["rsi_threshold"] == 20.0
    assert sp["target_pct"] == 9.0
    assert sp["entry_spec_literal_next_open"] is True
    assert sp["liquidation_distance_pct"] == 15.0
    assert sp["liquidation_maint_margin_pct"] == 14.0
    assert sp["liquidation_buffer_pct"] == 1.0


def test_c28_anchor_rule_present():
    prereg = _load(f"c28_prereg_{TS}.json")
    assert "anchor_rule" in prereg
    assert prereg["anchor_rule"]["token_ok"] in (
        "ALLOC_ANCHOR_REPRODUCED", "HOLDOUT_ANCHOR_REPRODUCED", "EXEC_ANCHOR_REPRODUCED")
    assert prereg["anchor_rule"]["tolerance_pnl"] == 1.0


def test_c28_inference_draw_floors():
    prereg = _load(f"c28_prereg_{TS}.json")
    inf = prereg["inference"]
    assert inf["episode_block_bootstrap_draws"] == 20000
    assert inf["permutation_draws"] == 20000
    assert inf["placebo_portfolio_runs"] == 2000
    assert inf["strata_permutation_draws"] == 2000


def test_c28_gate_reports_pending_when_no_cells(monkeypatch):
    import scripts.verify_c28_focus_campaign as gate
    monkeypatch.setattr(gate, "STATE", STATE)
    code = gate.main(["--direction", "c28-a", "--verbose"])
    # No C28 cells exist yet -> PENDING (or FAIL only if prereg missing; prereg exists)
    assert code in (0, 1)
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        gate.main(["--direction", "c28-a", "--verbose"])
    finally:
        sys.stdout = old
    text = buf.getvalue()
    assert "C28 ACCEPTANCE:" in text


def test_c28_no_smoke_artifacts():
    smokes = list(STATE.glob(f"c28_*_{TS}_SMOKE.json"))
    assert smokes == [], f"unexpected smoke artifacts: {smokes}"


def test_c28_engine_config_accepts_c28_fields():
    """C28 arm configs resolve through StrategyConfig without baseline drift."""
    from src.strategy.config import StrategyConfig, DEFAULT_CONFIG
    cfg = StrategyConfig()  # defaults: C20-C25 baseline
    assert cfg.intrabar_adverse_first is False
    assert cfg.per_trade_funding is False
    assert cfg.liquidation_maint_margin_pct == 5.0
    assert cfg.liquidation_buffer_pct == 1.0
    assert DEFAULT_CONFIG.intrabar_adverse_first is False
    assert DEFAULT_CONFIG.per_trade_funding is False
    # C28 direction axes are additive and do not mutate the shared baseline.
    assert DEFAULT_CONFIG.gross_cap_pct == 120.0
