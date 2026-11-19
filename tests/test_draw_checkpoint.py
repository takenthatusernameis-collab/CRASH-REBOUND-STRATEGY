"""Durability tests for the intra-cell draw checkpoint layer.

These tests never run the portfolio engine. They verify the two properties the
fix relies on:
  1. chunked evaluation is element-for-element identical to a monolithic run
     (same order, same draw count, same values), and
  2. an interrupted run resumes from the completed chunks instead of restarting.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import scripts.draw_checkpoint as dc  # noqa: E402
import scripts.run_c20_cross_venue_campaign as c20  # noqa: E402


def _subsets(n: int):
    return [("S", i) for i in range(n)]


def _draw_many_from_value(chunk):
    return [{"num_trades": 1, "total_pnl": float(s[1])} for s in chunk]


def test_chunked_equals_monolithic(monkeypatch, tmp_path):
    monkeypatch.setenv("C25_DRAW_CHUNK", "7")
    monkeypatch.setenv("C25_DRAW_RESUME", "1")
    sizes = []

    def draw_many(chunk):
        sizes.append(len(chunk))
        return _draw_many_from_value(chunk)

    results = dc.run_chunked(
        state_dir=tmp_path, campaign="TST", tag="T1", stage="perm",
        arm="a", venue="v", fold="f", subsets=_subsets(25), jobs=1,
        prereg_sha256="sha-abc", seed=1, draw_many=draw_many)

    assert [r["total_pnl"] for r in results] == [float(i) for i in range(25)]
    assert sum(sizes) == 25
    assert sizes == [7, 7, 7, 4]


def test_resume_after_interruption_keeps_completed_chunks(monkeypatch, tmp_path):
    monkeypatch.setenv("C25_DRAW_CHUNK", "5")
    monkeypatch.setenv("C25_DRAW_RESUME", "1")
    evaluated = []

    def interrupted(chunk):
        evaluated.extend(s[1] for s in chunk)
        if len(evaluated) > 5:  # die during the second chunk
            raise RuntimeError("simulated environment loss")
        return _draw_many_from_value(chunk)

    with pytest.raises(RuntimeError):
        dc.run_chunked(
            state_dir=tmp_path, campaign="TST", tag="T2", stage="perm",
            arm="a", venue="v", fold="f", subsets=_subsets(12), jobs=1,
            prereg_sha256="sha-abc", seed=1, draw_many=interrupted)
    assert evaluated == list(range(10))  # second chunk evaluated then discarded

    resumed = []
    results = dc.run_chunked(
        state_dir=tmp_path, campaign="TST", tag="T2", stage="perm",
        arm="a", venue="v", fold="f", subsets=_subsets(12), jobs=1,
        prereg_sha256="sha-abc", seed=1,
        draw_many=lambda chunk: resumed.extend([s[1] for s in chunk]) or
        _draw_many_from_value(chunk))

    assert resumed == [5, 6, 7, 8, 9, 10, 11]  # only the unfinished tail is re-run
    assert [r["total_pnl"] for r in results] == [float(i) for i in range(12)]


def test_prereg_change_invalidates_partials(monkeypatch, tmp_path):
    monkeypatch.setenv("C25_DRAW_CHUNK", "4")
    monkeypatch.setenv("C25_DRAW_RESUME", "1")
    dc.run_chunked(
        state_dir=tmp_path, campaign="TST", tag="T3", stage="perm",
        arm="a", venue="v", fold="f", subsets=_subsets(8), jobs=1,
        prereg_sha256="sha-old", seed=1, draw_many=_draw_many_from_value)

    seen = []
    results = dc.run_chunked(
        state_dir=tmp_path, campaign="TST", tag="T3", stage="perm",
        arm="a", venue="v", fold="f", subsets=_subsets(8), jobs=1,
        prereg_sha256="sha-new", seed=1,
        draw_many=lambda chunk: seen.extend([s[1] for s in chunk]) or
        _draw_many_from_value(chunk))

    assert seen == list(range(8))
    assert [r["total_pnl"] for r in results] == [float(i) for i in range(8)]


def test_resume_disabled_reevaluates_everything(monkeypatch, tmp_path):
    monkeypatch.setenv("C25_DRAW_CHUNK", "4")
    monkeypatch.setenv("C25_DRAW_RESUME", "1")
    dc.run_chunked(
        state_dir=tmp_path, campaign="TST", tag="T4", stage="perm",
        arm="a", venue="v", fold="f", subsets=_subsets(8), jobs=1,
        prereg_sha256="sha", seed=1, draw_many=_draw_many_from_value)

    monkeypatch.setenv("C25_DRAW_RESUME", "0")
    seen = []
    dc.run_chunked(
        state_dir=tmp_path, campaign="TST", tag="T4", stage="perm",
        arm="a", venue="v", fold="f", subsets=_subsets(8), jobs=1,
        prereg_sha256="sha", seed=1,
        draw_many=lambda chunk: seen.extend([s[1] for s in chunk]) or
        _draw_many_from_value(chunk))
    assert seen == list(range(8))


def test_permutation_subset_generation_is_deterministic_and_exact_branch():
    rows = [
        {"symbol": "S1", "bar_index": 0, "rsi": 10.0},
        {"symbol": "S1", "bar_index": 1, "rsi": 11.0},
        {"symbol": "S1", "bar_index": 2, "rsi": 12.0},
        {"symbol": "S1", "bar_index": 3, "rsi": 55.0},
    ]
    vd = {"candles": {}}
    keys = [("S1", 0)]
    spec = c20.permutation_draw_subsets(vd, rows, keys, draws=20000, seed=7)
    assert spec["exact"] is True
    assert spec["unique"] == [(("S1", 0),), (("S1", 1),), (("S1", 2),)]

    rows2 = [
        {"symbol": "S1", "bar_index": i, "rsi": 10.0} for i in range(120)
    ]
    a = c20.permutation_draw_subsets(vd, rows2, [("S1", 0), ("S1", 1)], draws=50, seed=11)
    b = c20.permutation_draw_subsets(vd, rows2, [("S1", 0), ("S1", 1)], draws=50, seed=11)
    c = c20.permutation_draw_subsets(vd, rows2, [("S1", 0), ("S1", 1)], draws=50, seed=12)
    assert a["exact"] is False
    assert a["unique"] == b["unique"]
    assert a["unique"] != c["unique"]
    assert len(a["unique"]) == 50
