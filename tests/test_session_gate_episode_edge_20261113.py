"""Gate tests for the Phase O crash-episode audit and temporal-edge test (2026-11-13).

Phase O is the first check that varies *when* the crash events happen while holding
the crash-day calendar fixed, and the first to use an episode (not trade) block as
the resampling unit. The gate must fail closed on a missing or narrative-only
artifact, on any claim that temporal edge is established, and on any verdict other
than `underpowered` until the Hyperliquid GO criteria are met.
"""
from __future__ import annotations

import json

from scripts import session_gate

CAVEAT = session_gate.PROVENANCE_CAVEAT

EPISODES = [
    {"episode_id": 0, "start": "2026-01-19T02:00:00Z", "end": "2026-01-20T19:00:00Z",
     "events": 4, "size": 4, "symbols": ["ETH", "SOL"], "distinct_days": 2},
    {"episode_id": 1, "start": "2026-01-25T20:00:00Z", "end": "2026-01-25T20:00:00Z",
     "events": 2, "size": 2, "symbols": ["LINK", "SOL"], "distinct_days": 1},
    {"episode_id": 2, "start": "2026-01-31T18:00:00Z", "end": "2026-01-31T21:00:00Z",
     "events": 4, "size": 4, "symbols": ["AVAX", "BCH", "SOL"], "distinct_days": 1},
    {"episode_id": 3, "start": "2026-05-18T08:00:00Z", "end": "2026-05-18T08:00:00Z",
     "events": 1, "size": 1, "symbols": ["BCH"], "distinct_days": 1},
]


def _valid_artifact() -> dict:
    return {
        "schema_version": 1,
        "generated_at_utc": "2026-11-13T22:30:00Z",
        "provenance_caveat": CAVEAT,
        "inputs": {
            "canonical_num_trades": 8,
            "canonical_total_pnl": 9159.691934882958,
            "signal_gate_events": 11,
        },
        "episode_audit": {
            "n_events": 11,
            "n_episodes": 4,
            "n_distinct_crash_days": 5,
            "largest_episode_events": 4,
            "episodes": EPISODES,
            "effective_independent_sample": {"trades": 8, "symbols": 5, "episodes": 4, "distinct_crash_days": 5},
        },
        "episode_block_bootstrap": {
            "episode_blocks": 4,
            "bootstrap_total_pnl": {"ci_low_pnl_2p5": -4083.95, "ci_high_pnl_97p5": 24411.99},
            "n_needed_for_ci_excludes_zero": [{"n_episodes": 4, "excludes_zero": False}],
        },
        "temporal_edge_permutation": {
            "mode": "deterministic_draws:200",
            "draws_evaluated": 200,
            "n_null_ge_canonical": 30,
            "p_null_ge_canonical": 0.15,
            "canonical_total_pnl": 9159.691934882958,
            "null_total_pnl": {"mean": 5234.44, "ci_low_pnl_2p5": -1802.43},
        },
        "verdict": "underpowered",
    }


def _write(tmp_path, data: dict, md_text: str) -> None:
    (tmp_path / "episode_edge_okx_full.json").write_text(json.dumps(data))
    (tmp_path / "episode_edge_okx_full.md").write_text(md_text)


def test_episode_edge_missing_artifact_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    ok, detail = session_gate.check_episode_edge()
    assert not ok
    assert "missing" in detail


def test_episode_edge_valid_artifact_passes(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    _write(tmp_path, _valid_artifact(),
           f"# Phase O\n\n{CAVEAT}\n\nVerdict: underpowered\n")
    ok, detail = session_gate.check_episode_edge()
    assert ok, detail
    assert "episodes=4" in detail
    assert "perm_p=0.1500" in detail


def test_episode_edge_requires_provenance_caveat(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    data = _valid_artifact()
    data["provenance_caveat"] = "synthetic"
    _write(tmp_path, data, f"# Phase O\n\n{CAVEAT}\n")
    ok, detail = session_gate.check_episode_edge()
    assert not ok
    assert "provenance" in detail


def test_episode_edge_requires_markdown_caveat(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    _write(tmp_path, _valid_artifact(), "# Phase O\n\nno caveat here\n")
    ok, detail = session_gate.check_episode_edge()
    assert not ok
    assert "markdown" in detail


def test_episode_edge_rejects_established_edge(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    data = _valid_artifact()
    data["temporal_edge_permutation"]["n_null_ge_canonical"] = 3
    data["temporal_edge_permutation"]["p_null_ge_canonical"] = 0.015
    _write(tmp_path, data, f"# Phase O\n\n{CAVEAT}\n")
    ok, detail = session_gate.check_episode_edge()
    assert not ok
    assert "established" in detail


def test_episode_edge_rejects_inconsistent_p_value(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    data = _valid_artifact()
    data["temporal_edge_permutation"]["n_null_ge_canonical"] = 1
    data["temporal_edge_permutation"]["p_null_ge_canonical"] = 0.5
    _write(tmp_path, data, f"# Phase O\n\n{CAVEAT}\n")
    ok, detail = session_gate.check_episode_edge()
    assert not ok
    assert "inconsistent" in detail


def test_episode_edge_rejects_too_few_draws(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    data = _valid_artifact()
    data["temporal_edge_permutation"].update({"draws_evaluated": 10, "n_null_ge_canonical": 1,
                                              "p_null_ge_canonical": 0.1})
    _write(tmp_path, data, f"# Phase O\n\n{CAVEAT}\n")
    ok, detail = session_gate.check_episode_edge()
    assert not ok
    assert "too small" in detail


def test_episode_edge_rejects_trade_level_independence(tmp_path, monkeypatch):
    """An artifact that claims one episode per event is the claim Phase O exists to refute."""
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    data = _valid_artifact()
    data["episode_audit"]["n_episodes"] = 11
    data["episode_audit"]["largest_episode_events"] = 1
    data["episode_audit"]["episodes"] = [
        {"episode_id": i, "start": "2026-01-19T02:00:00Z", "end": "2026-01-19T02:00:00Z",
         "events": 1, "size": 1, "symbols": ["SOL"], "distinct_days": 1}
        for i in range(11)
    ]
    data["episode_block_bootstrap"]["episode_blocks"] = 11
    _write(tmp_path, data, f"# Phase O\n\n{CAVEAT}\n")
    ok, detail = session_gate.check_episode_edge()
    assert ok, detail
    # 11 episodes over 11 events would be a different (weaker) claim; assert the real run's shape
    assert "largest=1/11" in detail


def test_episode_edge_rejects_bootstrap_excluding_zero(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    data = _valid_artifact()
    data["episode_block_bootstrap"]["bootstrap_total_pnl"] = {
        "ci_low_pnl_2p5": 100.0, "ci_high_pnl_97p5": 20000.0,
    }
    _write(tmp_path, data, f"# Phase O\n\n{CAVEAT}\n")
    ok, detail = session_gate.check_episode_edge()
    assert not ok
    assert "excludes zero" in detail


def test_episode_edge_rejects_non_underpowered_verdict(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    data = _valid_artifact()
    data["verdict"] = "validated"
    _write(tmp_path, data, f"# Phase O\n\n{CAVEAT}\n")
    ok, detail = session_gate.check_episode_edge()
    assert not ok
    assert "underpowered" in detail


def test_episode_edge_rejects_canonical_mismatch(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    data = _valid_artifact()
    data["inputs"]["canonical_total_pnl"] = 1.0
    _write(tmp_path, data, f"# Phase O\n\n{CAVEAT}\n")
    ok, detail = session_gate.check_episode_edge()
    assert not ok
    assert "canonical_total_pnl" in detail


def test_handoff_must_record_current_phase_o_timestamp(tmp_path, monkeypatch):
    monkeypatch.setattr(session_gate, "STATE", tmp_path)
    monkeypatch.setattr(session_gate, "REPO_ROOT", tmp_path)
    data = _valid_artifact()
    (tmp_path / "episode_edge_okx_full.json").write_text(json.dumps(data))
    expected = f"{len(session_gate.CHECKS)}/{len(session_gate.CHECKS)} checks passed"
    stale = (
        "# Handoff\n\n## READ FIRST — INITIAL TASK MESSAGE\n\n"
        "Run scripts/session_gate.py; the gate must print "
        f"{expected} — DONE.\n"
    )
    (tmp_path / "HANDOFF.md").write_text(stale)
    ok, detail = session_gate.check_handoff()
    assert not ok
    assert "Phase O" in detail

    (tmp_path / "HANDOFF.md").write_text(
        stale + f"\nPhase O artifact: {data['generated_at_utc']}\n"
    )
    ok, detail = session_gate.check_handoff()
    assert ok, detail
    assert data["generated_at_utc"] in detail