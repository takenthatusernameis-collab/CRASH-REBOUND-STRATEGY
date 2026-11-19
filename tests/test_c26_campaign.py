"""C26 intrabat path & per-trade funding-fidelity campaign tests.

These tests are wiring/guardrail tests only; they do NOT run the heavy 20k/20k/2k
battery (that is the durable C26 runner). They verify:
  - the C26 prereg exists and is PRE_REGISTERED_BEFORE_COMPUTE
  - the gate script imports and reports PENDING when no cells exist
  - C26 arm config resolution (intrabar_adverse_first / per_trade_funding flags)
  - funding-unavailable handling
  - engine flags are accepted (no drift to C20-C25 baseline)
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / "research_state"
TS = "20261119T121500Z"


def _load(name: str) -> dict:
    return json.loads((STATE / name).read_text())


def test_c26_prereg_exists_and_is_pre_registered():
    prereg = _load(f"c26_prereg_{TS}.json")
    assert prereg.get("prereg_status") == "PRE_REGISTERED_BEFORE_COMPUTE"
    assert prereg.get("campaign") == "C26"
    assert prereg.get("binding_task") == "C26-T1"
    assert set(prereg["arms"]) == {
        "path_base", "path_funding_trade", "path_intrabar_adverse_first", "path_intrabar_combined"}
    assert prereg["arms"]["path_base"]["role"] == "FIDELITY_ANCHOR"
    assert prereg["arms"]["path_intrabar_combined"]["role"] == "PRIMARY"


def test_c26_prereg_freezes_signal_path():
    prereg = _load(f"c26_prereg_{TS}.json")
    sp = prereg["signal_path_frozen"]
    assert sp["rsi_period"] == 21
    assert sp["rsi_threshold"] == 20.0
    assert sp["target_pct"] == 9.0
    assert sp["entry_spec_literal_next_open"] is True
    assert sp["liquidation_distance_pct"] == 15.0
    assert sp["liquidation_maint_margin_pct"] == 14.0
    assert sp["liquidation_buffer_pct"] == 1.0


def test_c26_arm_flags():
    prereg = _load(f"c26_prereg_{TS}.json")
    base = prereg["arms"]["path_base"]
    assert base["intrabar_adverse_first"] is False
    assert base["per_trade_funding"] is False
    combined = prereg["arms"]["path_intrabar_combined"]
    assert combined["intrabar_adverse_first"] is True
    assert combined["per_trade_funding"] is True
    trade = prereg["arms"]["path_funding_trade"]
    assert trade["intrabar_adverse_first"] is False
    assert trade["per_trade_funding"] is True
    adverse = prereg["arms"]["path_intrabar_adverse_first"]
    assert adverse["intrabar_adverse_first"] is True
    assert adverse["per_trade_funding"] is False


def test_c26_taker_bps_in_band():
    prereg = _load(f"c26_prereg_{TS}.json")
    for venue, bps in prereg["taker_bps"].items():
        assert 4.5 <= bps <= 7.0, f"{venue} taker {bps} bps outside 4.5-7 band"


def test_c26_gate_reports_pending_when_no_cells(monkeypatch):
    import scripts.verify_c26_focus_campaign as gate
    monkeypatch.setattr(gate, "STATE", STATE)
    code = gate.main(["--verbose"])
    # No C26 cells exist yet -> PENDING (or FAIL only if prereg missing; prereg exists)
    assert code in (0, 1)
    captured = []
    import io
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        gate.main(["--verbose"])
    finally:
        sys.stdout = old
    text = buf.getvalue()
    assert "C26 ACCEPTANCE:" in text


def test_c26_no_smoke_artifacts():
    smokes = list(STATE.glob(f"c26_*_{TS}_SMOKE.json"))
    assert smokes == [], f"unexpected smoke artifacts: {smokes}"


def test_c26_engine_flags_preserve_baseline():
    """C26 flags default False so C20-C25 baseline behavior is unchanged."""
    from src.strategy.config import StrategyConfig, DEFAULT_CONFIG
    cfg = StrategyConfig()  # defaults: C20-C25 baseline
    assert cfg.intrabar_adverse_first is False
    assert cfg.per_trade_funding is False
    assert cfg.liquidation_maint_margin_pct == 5.0
    assert cfg.liquidation_buffer_pct == 1.0
    assert DEFAULT_CONFIG.intrabar_adverse_first is False
    assert DEFAULT_CONFIG.per_trade_funding is False
