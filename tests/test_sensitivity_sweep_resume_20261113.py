"""Regression tests for the Phase J2 sweep hardening (2026-11-13).

The sweep is a ~70 minute job. Two failure modes made prior sessions lose all of
that work, so both are locked down here:
  1. A session killed mid-sweep had to restart from zero (no resume).
  2. A variant whose equity-curve horizon is not derivable returns a null
     total_return_pct, which used to crash the final aggregate render after every
     run had already completed.
"""
from __future__ import annotations

import json

from scripts.run_sensitivity_sweep import (
    GRID,
    INTERACTION_GRID,
    _reusable_record,
    build_conclusions,
    build_jobs,
    render_markdown,
)


def _job(tag: str, **kwargs) -> dict:
    return {"tag": tag, "config_kwargs": dict(kwargs)}


def _ok_record(tag: str, params: dict, trades: int, ret, pnl: float) -> dict:
    return {
        "tag": tag,
        "label": tag,
        "params": params,
        "status": "ok",
        "metrics": {
            "total_return_pct": ret,
            "annualized_return_pct": ret,
            "max_drawdown_pct": -1.0,
            "win_rate": 0.5,
            "profit_factor": 1.0,
            "trade_count": trades,
            "total_pnl": pnl,
            "by_leg": {},
            "exit_reasons": {},
        },
        "runtime_seconds": 1.0,
    }


def test_reusable_record_reuses_matching_run(tmp_path):
    path = tmp_path / "baseline_spec.json"
    rec = _ok_record("baseline_spec", {}, 8, 9.16, 9159.7)
    path.write_text(json.dumps(rec))
    assert _reusable_record(path, _job("baseline_spec")) == rec


def test_reusable_record_rejects_knob_mismatch(tmp_path):
    path = tmp_path / "rsi_threshold_15.json"
    path.write_text(json.dumps(_ok_record("rsi_threshold_15", {"rsi_threshold": 15.0}, 2, None, 1.0)))
    assert _reusable_record(path, _job("rsi_threshold_15", rsi_threshold=18.0)) is None


def test_reusable_record_rejects_tag_mismatch_and_corruption(tmp_path):
    path = tmp_path / "baseline_spec.json"
    path.write_text(json.dumps(_ok_record("rsi_threshold_15", {"rsi_threshold": 15.0}, 2, None, 1.0)))
    assert _reusable_record(path, _job("baseline_spec")) is None

    path.write_text("{not json")
    assert _reusable_record(path, _job("rsi_threshold_15", rsi_threshold=15.0)) is None


def test_conclusions_tolerate_null_return_and_still_rank():
    runs = [
        _ok_record("baseline_spec", {}, 8, 9.16, 9159.7),
        _ok_record("rsi_threshold_15", {"rsi_threshold": 15.0}, 2, None, 5911.0),
        _ok_record("rsi_threshold_25", {"rsi_threshold": 25.0}, 30, 17.13, 20000.0),
    ]
    md, summary = build_conclusions(runs)
    tags = {r["tag"] for r in summary["material_knobs"]}
    assert "rsi_threshold_15" in tags
    assert "rsi_threshold_25" in tags
    assert summary["ranked"][0]["delta_total_return_pp"] is None or isinstance(
        summary["ranked"][0]["delta_total_return_pp"], float
    )


def test_render_markdown_tolerates_null_return():
    runs = [
        _ok_record("baseline_spec", {}, 8, 9.16, 9159.7),
        _ok_record("buy_target_12pct", {"target_pct": 12.0}, 8, None, 8000.0),
    ]
    md, summary = build_conclusions(runs)
    report = {
        "generated_at_utc": "2026-11-13T00:00:00Z",
        "provenance_caveat": "caveat",
        "inputs": {
            "manifest": "m",
            "universe": "u",
            "universe_size": 54,
            "canonical_campaign": "c",
        },
        "workers": 4,
        "resumed_runs": 1,
        "wall_clock_seconds": 1.0,
        "sequential_equivalent_seconds": 2.0,
        "canonical": {},
        "runs": runs,
        "rejected_runs": [],
        "conclusions": summary,
        "caveats": ["caveat"],
        "conclusions_md": md,
    }
    out = render_markdown(report)
    assert "buy_target_12pct" in out
    assert "n/a" in out

def test_ofat_grid_is_baseline_plus_sixteen_variants():
    jobs = build_jobs("ofat", None)
    assert len(jobs) == 1 + len(GRID) == 17
    assert jobs[0]["tag"] == "baseline_spec"
    assert jobs[0]["config_kwargs"] == {}
    assert [j["tag"] for j in jobs[1:]] == [g[0] for g in GRID]


def test_interaction_grid_is_baseline_plus_two_factor_runs():
    jobs = build_jobs("interaction", None)
    assert len(jobs) == 1 + len(INTERACTION_GRID) == 9
    assert jobs[0]["tag"] == "baseline_spec"
    tags = [j["tag"] for j in jobs]
    assert len(tags) == len(set(tags))
    for job in jobs[1:]:
        assert len(job["config_kwargs"]) >= 2, job["tag"]
    assert all(job["capital"] == 100000.0 for job in jobs)


def test_only_subset_and_unknown_tag():
    jobs = build_jobs("ofat", ["rsi_threshold_25"])
    assert [j["tag"] for j in jobs] == ["baseline_spec", "rsi_threshold_25"]
    try:
        build_jobs("ofat", ["does_not_exist"])
    except SystemExit:
        pass
    else:  # pragma: no cover
        raise AssertionError("unknown --only tag should fail closed")
