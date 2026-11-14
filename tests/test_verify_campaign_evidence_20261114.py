"""Tests for the campaign evidence verifier (mechanical anti-avoidance gate).

These lock the avoidance patterns the verifier must reject:
  - a canonical campaign that is a stub or has been tampered with;
  - a Hyperliquid blocker claim that is not backed by a reproducible probe;
  - a "full campaign" artifact that is not genuine (relabeling the partial run);
  - a validated/decision-grade verdict asserted while evidence is underpowered;
  - a partial Hyperliquid artifact promoted to performance evidence.
"""
from __future__ import annotations

import json

import pytest

from scripts import verify_campaign_evidence as ver


def _write_state(tmp_path, monkeypatch, **artifacts):
    for name, data in artifacts.items():
        p = tmp_path / "research_state"
        p.mkdir(parents=True, exist_ok=True)
        (p / name).write_text(json.dumps(data))
    monkeypatch.setattr(ver, "STATE", tmp_path / "research_state")
    return tmp_path / "research_state"


def _canonical(trades=8, pnl=ver.CANONICAL_OKX_PNL, **over):
    data = {
        "real_market_data": True,
        "fabricated_data": False,
        "performance_evidence": True,
        "results": {"num_trades": trades, "total_pnl": pnl},
    }
    data.update(over)
    return data


def _probe(full_served=False, max_bars=3898, missing=2894, expected=6792):
    return {
        "schema_version": 1,
        "generated_at_utc": "2026-11-14T00:00:00Z",
        "probe_summary": {
            "full_window_served": full_served,
            "max_bars_returned": max_bars,
            "missing_early_bars_vs_expected": missing,
            "expected_hourly_bars": expected,
            "earliest_served_start_utc": "2026-04-19T14:00:00Z",
        },
        "verdict": "FULL_283D_BLOCKED_BY_API_RETENTION",
    }


def _episode(verdict="underpowered"):
    return {"verdict": verdict}


def _partial(**over):
    data = {
        "real_market_data": True,
        "performance_evidence": False,
        "fabricated_data": False,
        "results": {"num_trades": 0, "total_pnl": 0.0},
    }
    data.update(over)
    return data


def _placeholder_readme():
    return {"note": "Verified 283d BTC/ETH slice only; NOT full spec-relevant universe."}


def _base(tmp_path, monkeypatch, **over):
    artifacts = {
        "campaign_results_real_okx_full.json": _canonical(),
        "hyperliquid_retention_probe.json": _probe(),
        "episode_edge_okx_full.json": _episode(),
        "campaign_results_real_hyperliquid_partial_20260419_20260928.json": _partial(),
    }
    artifacts.update(over)
    state = _write_state(tmp_path, monkeypatch, **artifacts)
    arch = state / "archives"
    arch.mkdir(parents=True, exist_ok=True)
    (arch / "hyperliquid_btc_eth_1h_20251220_20260928_verified.README.json").write_text(
        json.dumps(_placeholder_readme())
    )
    return state


def test_valid_state_passes(tmp_path, monkeypatch):
    _base(tmp_path, monkeypatch)
    ok, rows = ver.verify()
    assert ok, rows


def test_canonical_missing_fails(tmp_path, monkeypatch):
    _base(tmp_path, monkeypatch)
    (tmp_path / "research_state" / "campaign_results_real_okx_full.json").unlink()
    ok, rows = ver.verify()
    assert not ok
    assert any(r["check"] == "canonical_okx" and not r["pass"] for r in rows)


def test_canonical_pnl_tampered_fails(tmp_path, monkeypatch):
    _base(tmp_path, monkeypatch,
          **{"campaign_results_real_okx_full.json": _canonical(pnl=1.0)})
    ok, rows = ver.verify()
    assert not ok


def test_canonical_fabricated_flag_fails(tmp_path, monkeypatch):
    _base(tmp_path, monkeypatch,
          **{"campaign_results_real_okx_full.json": _canonical(fabricated_data=True)})
    ok, _ = ver.verify()
    assert not ok


def test_missing_probe_fails(tmp_path, monkeypatch):
    _base(tmp_path, monkeypatch)
    (tmp_path / "research_state" / "hyperliquid_retention_probe.json").unlink()
    ok, rows = ver.verify()
    assert not ok
    assert any(r["check"] == "hyperliquid_blocker" and not r["pass"] for r in rows)


def test_probe_claiming_full_but_no_campaign_fails(tmp_path, monkeypatch):
    """A stale/lying probe that says 'served' without a real campaign must fail."""
    _base(tmp_path, monkeypatch,
          **{"hyperliquid_retention_probe.json": _probe(full_served=True, missing=0)})
    ok, _ = ver.verify()
    assert not ok


def test_probe_zero_missing_fails(tmp_path, monkeypatch):
    _base(tmp_path, monkeypatch,
          **{"hyperliquid_retention_probe.json": _probe(max_bars=6792, missing=0)})
    ok, _ = ver.verify()
    assert not ok


def test_partial_promoted_to_evidence_fails(tmp_path, monkeypatch):
    _base(tmp_path, monkeypatch,
          **{"campaign_results_real_hyperliquid_partial_20260419_20260928.json":
             _partial(performance_evidence=True)})
    ok, _ = ver.verify()
    assert not ok


def test_full_campaign_must_be_genuine(tmp_path, monkeypatch):
    """If a full campaign artifact exists it must be real; a stub is rejected."""
    _base(tmp_path, monkeypatch,
          **{"campaign_results_real_hyperliquid_full.json":
             {"real_market_data": True, "fabricated_data": False,
              "performance_evidence": False, "results": {"num_trades": 0}}})
    ok, _ = ver.verify()
    assert not ok


def test_full_campaign_genuine_passes(tmp_path, monkeypatch):
    _base(tmp_path, monkeypatch,
          **{"campaign_results_real_hyperliquid_full.json":
             {"real_market_data": True, "fabricated_data": False,
              "performance_evidence": True, "results": {"num_trades": 10}}})
    ok, rows = ver.verify()
    assert ok, rows


def test_validated_verdict_fails(tmp_path, monkeypatch):
    _base(tmp_path, monkeypatch,
          **{"episode_edge_okx_full.json": _episode(verdict="validated")})
    ok, rows = ver.verify()
    assert not ok
    assert any(r["check"] == "verdict_honesty" and not r["pass"] for r in rows)


def test_placeholder_readme_must_label_non_evidence(tmp_path, monkeypatch):
    state = _base(tmp_path, monkeypatch)
    (state / "archives" /
     "hyperliquid_btc_eth_1h_20251220_20260928_verified.README.json").write_text(
        json.dumps({"note": "this is full evidence"}))
    ok, _ = ver.verify()
    assert not ok


def test_verifier_checks_are_registered():
    names = [n for n, _ in ver.CHECKS]
    assert names == ["canonical_okx", "hyperliquid_blocker",
                     "verdict_honesty", "placeholder_not_evidence"]