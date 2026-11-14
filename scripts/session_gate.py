#!/usr/bin/env python3
"""Machine-checkable done-gate for the crash-rebound handoff campaign.

The next agentic session must run this at the start (to see the work) and at the
end (to prove it). It fails closed: a missing, stub, or schema-invalid artifact
is a failure, not a warning. No artifact is created by this script.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
STATE = REPO_ROOT / "research_state"

PROVENANCE_CAVEAT = (
    "Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; "
    "NOT Hyperliquid performance evidence."
)

REQUIRED_METRIC_TERMS = [
    "total return",
    "annualized",
    "drawdown",
    "month",
    "trade",
    "win rate",
    "universe",
    "short",
]


def _read_text(path: Path) -> str:
    return path.read_text()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def check_spec_comparison_md() -> Tuple[bool, str]:
    path = STATE / "real_okx_full_spec_comparison.md"
    if not path.exists():
        return False, "missing"
    text = _read_text(path).lower()
    if len(text) < 4000:
        return False, f"too small ({len(text)} bytes) — decision-grade report required"
    missing = [t for t in REQUIRED_METRIC_TERMS if t not in text]
    if missing:
        return False, f"missing required terms: {missing}"
    if PROVENANCE_CAVEAT.lower() not in text:
        return False, "missing provenance caveat sentence"
    return True, f"{len(text)} bytes"


def check_spec_comparison_json() -> Tuple[bool, str]:
    path = STATE / "real_okx_full_spec_comparison_summary.json"
    if not path.exists():
        return False, "missing"
    try:
        data = _read_json(path)
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON: {exc}"
    if not isinstance(data, dict):
        return False, "top level must be an object"
    for key in ("generated_at_utc", "spec", "actual", "divergences"):
        if key not in data:
            return False, f"missing key {key!r}"
    if not isinstance(data["divergences"], list) or len(data["divergences"]) < 5:
        return False, "divergences must be a list with >= 5 entries"
    return True, f"{len(data['divergences'])} divergences"


def check_census() -> Tuple[bool, str]:
    path = STATE / "crash_event_census_real_okx_full.json"
    md = STATE / "crash_event_census_real_okx_full.md"
    if not path.exists() or not md.exists():
        return False, "json and/or md missing"
    try:
        data = _read_json(path)
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON: {exc}"
    rec = data.get("reconciliation") or {}
    events = data.get("events") or []
    if not events:
        return False, "no events"
    if rec.get("blocking_reasons_sum") != rec.get("events_total"):
        return False, "blocking reasons do not sum to events_total"
    if rec.get("unexplained_signal_gate_events") != 0:
        return False, "unexplained signal-gate events remain"
    if any(not e.get("blocking_reason") for e in events):
        return False, "an event has no blocking_reason"
    return True, f"{rec.get('events_total')} events, {rec.get('trades_matched_to_events')} trades matched"


def _check_sweep_artifacts(prefix: str, min_runs: int) -> Tuple[bool, str]:
    path = STATE / f"{prefix}.json"
    md = STATE / f"{prefix}.md"
    if not path.exists() or not md.exists():
        return False, "json and/or md missing"
    try:
        data = _read_json(path)
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON: {exc}"
    if PROVENANCE_CAVEAT.lower() not in _read_text(md).lower():
        return False, "markdown missing provenance caveat"
    if PROVENANCE_CAVEAT.lower() not in str(data.get("provenance_caveat", "")).lower():
        return False, "json missing provenance caveat"
    runs = data.get("runs")
    if not isinstance(runs, list) or len(runs) < min_runs:
        got = len(runs) if isinstance(runs, list) else "non-list"
        return False, f"need baseline + {min_runs - 1} sweep runs (got {got})"
    if runs[0].get("tag") != "baseline_spec":
        return False, "first run must be baseline_spec"
    tags = [r.get("tag") for r in runs]
    if len(tags) != len(set(tags)):
        return False, "duplicate run tags"
    runs_dir = STATE / "sweep_runs"
    for run in runs:
        tag = run.get("tag")
        if "params" not in run or "metrics" not in run:
            return False, f"{tag}: missing params/metrics"
        metrics = run["metrics"]
        if not isinstance(metrics, dict):
            return False, f"{tag}: metrics must be an object"
        for key in ("total_return_pct", "trade_count"):
            if key not in metrics:
                return False, f"{tag}: missing metrics.{key}"
        try:
            runtime = float(run.get("runtime_seconds") or 0.0)
        except (TypeError, ValueError):
            runtime = 0.0
        if runtime <= 0:
            return False, f"{tag}: non-positive runtime (artifact not executed)"
        if not (runs_dir / f"{tag}.json").exists():
            return False, f"{tag}: per-run evidence file missing"
    conclusions = data.get("conclusions")
    if not isinstance(conclusions, dict) or not isinstance(conclusions.get("ranked"), list):
        return False, "missing conclusions.ranked"
    if not data.get("rejected_runs"):
        return False, "missing spec-locked rejection evidence"
    return True, f"{len(runs)} runs, {len(conclusions['ranked'])} ranked knobs"


def check_sensitivity() -> Tuple[bool, str]:
    return _check_sweep_artifacts("sensitivity_sweep_real_okx_full", 17)


def check_interaction() -> Tuple[bool, str]:
    return _check_sweep_artifacts("interaction_sweep_real_okx_full", 9)


def check_robustness() -> Tuple[bool, str]:
    """Phase L: signal-vs-noise evidence for the 8-trade canonical result.

    The sweep gates prove the evidence chain; this proves the result is not
    obviously luck. It fails closed on a missing or narrative-only artifact.
    """
    path = STATE / "robustness_real_okx_full.json"
    md = STATE / "robustness_real_okx_full.md"
    if not path.exists() or not md.exists():
        return False, "json and/or md missing"
    try:
        data = _read_json(path)
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON: {exc}"
    if not isinstance(data, dict):
        return False, "top level must be an object"
    if PROVENANCE_CAVEAT.lower() not in str(data.get("provenance_caveat", "")).lower():
        return False, "json missing provenance caveat"
    if PROVENANCE_CAVEAT.lower() not in _read_text(md).lower():
        return False, "markdown missing provenance caveat"
    for key in ("generated_at_utc", "bootstrap", "sign_flip", "concentration",
                "time_split", "conclusion"):
        if key not in data:
            return False, f"missing {key!r}"

    boot = data["bootstrap"]
    if not isinstance(boot, dict):
        return False, "bootstrap must be an object"
    try:
        resamples = int(boot.get("resamples") or 0)
    except (TypeError, ValueError):
        resamples = 0
    if resamples < 1000:
        return False, f"bootstrap.resamples must be >= 1000 (got {resamples})"
    for key in ("ci_low_pnl", "ci_high_pnl", "prob_total_pnl_positive"):
        if key not in boot:
            return False, f"missing bootstrap.{key}"

    flip = data["sign_flip"]
    if not isinstance(flip, dict):
        return False, "sign_flip must be an object"
    try:
        combos = int(flip.get("combinations") or 0)
    except (TypeError, ValueError):
        combos = 0
    if combos != 256:
        return False, f"sign_flip.combinations must be 256 (2^8) (got {combos})"
    if "p_value" not in flip:
        return False, "missing sign_flip.p_value"

    conc = data["concentration"]
    if not isinstance(conc, dict):
        return False, "concentration must be an object"
    symbols = conc.get("symbols")
    if not isinstance(symbols, list) or not symbols:
        return False, "concentration.symbols must be a non-empty list"
    for key in ("top_symbol_pnl_share", "top_trade_pnl_share"):
        if key not in conc:
            return False, f"missing concentration.{key}"

    split = data["time_split"]
    if not isinstance(split, dict):
        return False, "time_split must be an object"
    for key in ("first_half_pnl", "second_half_pnl"):
        if key not in split:
            return False, f"missing time_split.{key}"

    conclusion = data["conclusion"]
    verdict = str((conclusion or {}).get("verdict", "")).lower() if isinstance(conclusion, dict) else ""
    if verdict not in ("signal", "noise", "underpowered"):
        return False, "conclusion.verdict must be signal, noise, or underpowered"
    if verdict not in _read_text(md).lower():
        return False, "markdown missing the verdict"
    return True, (f"verdict={verdict}, resamples={resamples}, "
                  f"sign-flip p={flip.get('p_value')}, symbols={len(symbols)}")


def check_robustness_stress() -> Tuple[bool, str]:
    """Phase N: exact robustness stress / power analysis must exist and stay underpowered.

    This is the fallback heavy-work gate. It re-runs the real full-portfolio
    engine under leave-one-symbol-out and leave-one-trade-out, concentration
    adjustment, bootstrap power projection, and an expanding-window refit. A
    missing or narrative-only artifact fails closed.
    """
    path = STATE / "robustness_stress_okx_full.json"
    md = STATE / "robustness_stress_okx_full.md"
    if not path.exists() or not md.exists():
        return False, "json and/or md missing"
    try:
        data = _read_json(path)
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON: {exc}"
    if not isinstance(data, dict):
        return False, "top level must be an object"
    if PROVENANCE_CAVEAT.lower() not in str(data.get("provenance_caveat", "")).lower():
        return False, "json missing provenance caveat"
    if PROVENANCE_CAVEAT.lower() not in _read_text(md).lower():
        return False, "markdown missing provenance caveat"
    for key in ("generated_at_utc", "canonical", "leave_one_symbol_out",
                "leave_one_trade_out", "concentration", "power", "walkforward",
                "verdict"):
        if key not in data:
            return False, f"missing {key!r}"

    can = data["canonical"]
    if not isinstance(can, dict):
        return False, "canonical must be an object"
    try:
        if int(can.get("trades")) != 8 or abs(float(can.get("total_pnl")) - 9159.691934882958) > 1e-6:
            return False, "canonical trades/total_pnl mismatch"
    except (TypeError, ValueError):
        return False, "canonical trades/total_pnl must be numeric"

    if str(data.get("verdict", "")).lower() != "underpowered":
        return False, "verdict must remain underpowered until Hyperliquid GO criteria are met"

    loo = data["leave_one_symbol_out"]
    if not isinstance(loo, dict) or not isinstance(loo.get("runs"), list) or len(loo["runs"]) < 5:
        return False, "leave_one_symbol_out.runs must be a list with >= 5 runs"
    if loo.get("all_positive") is not True:
        return False, "leave_one_symbol_out.all_positive must be true"
    for key in ("min_total_pnl", "max_total_pnl"):
        try:
            float(loo.get(key))
        except (TypeError, ValueError):
            return False, f"leave_one_symbol_out.{key} must be numeric"

    loto = data["leave_one_trade_out"]
    if not isinstance(loto, dict) or not isinstance(loto.get("runs"), list) or len(loto["runs"]) < 8:
        return False, "leave_one_trade_out.runs must be a list with >= 8 runs"
    if loto.get("all_positive") is not True:
        return False, "leave_one_trade_out.all_positive must be true"

    conc = data["concentration"]
    if not isinstance(conc, dict) or not conc.get("symbols"):
        return False, "concentration.symbols must be a non-empty list"
    for key in ("herfindahl_hhi_abs", "effective_symbol_count_abs"):
        try:
            float(conc.get(key))
        except (TypeError, ValueError):
            return False, f"concentration.{key} must be numeric"

    power = data["power"]
    if not isinstance(power, dict):
        return False, "power must be an object"
    for level in ("trade_level", "symbol_level"):
        row = power.get(level)
        if not isinstance(row, dict):
            return False, f"power.{level} must be an object"
        try:
            if int(row.get("observed_n")) < (8 if level == "trade_level" else 5):
                return False, f"power.{level}.observed_n too small"
        except (TypeError, ValueError):
            return False, f"power.{level}.observed_n must be an integer"

    wf = data["walkforward"]
    if not isinstance(wf, dict):
        return False, "walkforward must be an object"
    for key in ("evaluable_blocks", "refit_out_of_sample_total_pnl"):
        if key not in wf:
            return False, f"missing walkforward.{key}"
    try:
        if int(wf.get("evaluable_blocks")) < 1:
            return False, "walkforward.evaluable_blocks must be >= 1"
        float(wf.get("refit_out_of_sample_total_pnl"))
    except (TypeError, ValueError):
        return False, "walkforward counts/PnL must be numeric"

    return True, (f"verdict={data.get('verdict')}, LOO={len(loo['runs'])}, "
                  f"LOTO={len(loto['runs'])}, evaluable_blocks={wf.get('evaluable_blocks')}")


def check_episode_edge() -> Tuple[bool, str]:
    """Phase O: crash-episode dependence audit + conditional temporal-edge test.

    The trade-level and event-level statistics assume independent observations.
    Phase O measures how many *crash episodes* the 11 gate-passing events actually
    form, tests event timing against crash-day-conditioned alternatives, and gives
    a dependence-aware (episode-block) power floor. A missing or narrative-only
    artifact fails closed, and so does any claim that temporal edge is established.
    """
    path = STATE / "episode_edge_okx_full.json"
    md = STATE / "episode_edge_okx_full.md"
    if not path.exists() or not md.exists():
        return False, "json and/or md missing"
    try:
        data = _read_json(path)
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON: {exc}"
    if not isinstance(data, dict):
        return False, "top level must be an object"
    if PROVENANCE_CAVEAT.lower() not in str(data.get("provenance_caveat", "")).lower():
        return False, "json missing provenance caveat"
    if PROVENANCE_CAVEAT.lower() not in _read_text(md).lower():
        return False, "markdown missing provenance caveat"
    for key in ("generated_at_utc", "inputs", "episode_audit",
                "episode_block_bootstrap", "temporal_edge_permutation", "verdict"):
        if key not in data:
            return False, f"missing {key!r}"

    try:
        if int(data["inputs"]["canonical_num_trades"]) != 8:
            return False, "inputs.canonical_num_trades must be 8"
        if abs(float(data["inputs"]["canonical_total_pnl"]) - 9159.691934882958) > 1e-6:
            return False, "inputs.canonical_total_pnl mismatch"
    except (KeyError, TypeError, ValueError):
        return False, "inputs.canonical_* must be present and numeric"

    ep = data["episode_audit"]
    if not isinstance(ep, dict):
        return False, "episode_audit must be an object"
    for key in ("n_events", "n_episodes", "n_distinct_crash_days",
                "largest_episode_events", "effective_independent_sample"):
        if key not in ep:
            return False, f"missing episode_audit.{key}"
    try:
        n_events = int(ep["n_events"])
        n_episodes = int(ep["n_episodes"])
        n_days = int(ep["n_distinct_crash_days"])
        largest = int(ep["largest_episode_events"])
    except (TypeError, ValueError):
        return False, "episode_audit counts must be integers"
    if n_events != 11:
        return False, f"episode_audit.n_events must be 11 (got {n_events})"
    if n_episodes < 2 or n_episodes > n_events:
        return False, "episode_audit.n_episodes out of range"
    if n_days < 2 or n_days > n_events:
        return False, "episode_audit.n_distinct_crash_days out of range"
    if largest < 1 or largest > n_events:
        return False, "episode_audit.largest_episode_events out of range"
    if not isinstance(ep.get("episodes"), list) or len(ep["episodes"]) != n_episodes:
        return False, "episode_audit.episodes must list every episode"

    perm = data["temporal_edge_permutation"]
    if not isinstance(perm, dict):
        return False, "temporal_edge_permutation must be an object"
    for key in ("mode", "draws_evaluated", "null_total_pnl", "canonical_total_pnl",
                "p_null_ge_canonical", "n_null_ge_canonical"):
        if key not in perm:
            return False, f"missing temporal_edge_permutation.{key}"
    try:
        draws = int(perm["draws_evaluated"])
        ge = int(perm["n_null_ge_canonical"])
        p_value = float(perm["p_null_ge_canonical"])
    except (TypeError, ValueError):
        return False, "temporal_edge_permutation counts/p must be numeric"
    if draws < 30:
        return False, f"temporal_edge_permutation.draws_evaluated too small ({draws})"
    if ge < 0 or ge > draws:
        return False, "temporal_edge_permutation.n_null_ge_canonical out of range"
    if abs(p_value - ge / draws) > 1e-9:
        return False, "temporal_edge_permutation.p_null_ge_canonical inconsistent with counts"
    if p_value < 0.05:
        return False, "temporal edge would be established; verdict/handoff must be revisited"

    boot = data["episode_block_bootstrap"]
    if not isinstance(boot, dict) or int(boot.get("episode_blocks", 0)) != n_episodes:
        return False, "episode_block_bootstrap.episode_blocks must equal episode_audit.n_episodes"
    summary = boot.get("bootstrap_total_pnl") if isinstance(boot.get("bootstrap_total_pnl"), dict) else {}
    try:
        lo = float(summary["ci_low_pnl_2p5"])
        hi = float(summary["ci_high_pnl_97p5"])
    except (KeyError, TypeError, ValueError):
        return False, "episode_block_bootstrap.bootstrap_total_pnl CI must be numeric"
    if lo > 0 or hi < 0:
        return False, "episode-block bootstrap CI excludes zero; verdict must be revisited"

    if str(data.get("verdict", "")).lower() != "underpowered":
        return False, "verdict must remain underpowered until Hyperliquid GO criteria are met"

    return True, (f"episodes={n_episodes} events={n_events} crash_days={n_days} "
                  f"largest={largest}/{n_events} perm_p={p_value:.4f} "
                  f"boot_CI=[{lo:.2f},{hi:.2f}]")


def check_hyperliquid_status() -> Tuple[bool, str]:
    """Phase J3: record the exact Hyperliquid acquisition state and the partial evidence.

    The full 283-day Hyperliquid window is the only decision-grade path. If the
    public API cannot serve it, this check requires an explicit probe artifact,
    a NOT_EVIDENCE partial campaign, and a crash census. If the full window is
    marked available, it requires a full-window campaign with
    performance_evidence=true.
    """
    path = STATE / "hyperliquid_acquisition_status.json"
    if not path.exists():
        return False, "missing"
    try:
        data = _read_json(path)
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON: {exc}"
    if not isinstance(data, dict):
        return False, "top level must be an object"
    for key in ("generated_at_utc", "target_window", "full_window_available",
                "api_probe", "partial_window", "partial_campaign", "crash_census",
                "verdict", "next_actions"):
        if key not in data:
            return False, f"missing {key!r}"

    full_available = data.get("full_window_available")
    if not isinstance(full_available, bool):
        return False, "full_window_available must be a boolean"

    if full_available:
        campaign = data.get("full_campaign") or {}
        art = campaign.get("artifact")
        if not art or not (STATE / Path(art).name).exists():
            return False, "full_window_available=true requires full_campaign.artifact"
        try:
            cd = _read_json(STATE / Path(art).name)
        except json.JSONDecodeError as exc:
            return False, f"full campaign invalid JSON: {exc}"
        if cd.get("performance_evidence") is not True:
            return False, "full campaign must set performance_evidence=true"
        return True, f"full window available: {art}"

    probe = data["api_probe"]
    if not isinstance(probe, dict):
        return False, "api_probe must be an object"
    try:
        returned = int(probe.get("returned_bars"))
        missing = int(probe.get("missing_early_bars"))
    except (TypeError, ValueError):
        return False, "api_probe.returned_bars/missing_early_bars must be integers"
    if returned < 1000 or missing <= 0:
        return False, "api_probe must document a materially incomplete API window"
    for key in ("available_start", "available_end", "conclusion"):
        if not probe.get(key):
            return False, f"api_probe.{key} missing"

    partial = data["partial_window"]
    if not isinstance(partial, dict):
        return False, "partial_window must be an object"
    comp = partial.get("symbols_complete")
    if not isinstance(comp, list) or len(comp) < 12:
        return False, "partial_window.symbols_complete must list >= 12 symbols"
    if partial.get("all_complete") is not False:
        return False, "partial_window.all_complete must remain false"
    if int(partial.get("expected_hourly_bars") or 0) != 3900:
        return False, "partial_window.expected_hourly_bars must be 3900"

    pc = data["partial_campaign"]
    if not isinstance(pc, dict):
        return False, "partial_campaign must be an object"
    art = pc.get("artifact")
    if not art or not (STATE / Path(art).name).exists():
        return False, "partial_campaign.artifact missing"
    if pc.get("performance_evidence") is not False:
        return False, "partial_campaign.performance_evidence must be false"
    if pc.get("fabricated_data") is not False:
        return False, "partial_campaign.fabricated_data must be false"
    try:
        if int(pc.get("num_trades")) < 0:
            return False, "partial_campaign.num_trades must be >= 0"
    except (TypeError, ValueError):
        return False, "partial_campaign.num_trades must be an integer"

    cc = data["crash_census"]
    if not isinstance(cc, dict):
        return False, "crash_census must be an object"
    art = cc.get("artifact")
    if not art or not (STATE / Path(art).name).exists():
        return False, "crash_census.artifact missing"
    try:
        if int(cc.get("confirmed_signals")) < 0:
            return False, "crash_census.confirmed_signals must be >= 0"
        if int(cc.get("rsi_crash_events")) < 1:
            return False, "crash_census.rsi_crash_events must be >= 1"
        if int(cc.get("symbols")) < 12 or int(cc.get("bars")) < 46800:
            return False, "crash_census must cover >= 12 symbols and >= 46800 bars"
    except (TypeError, ValueError):
        return False, "crash_census counts must be integers"

    if "BLOCKED" not in str(data.get("verdict", "")).upper():
        return False, "verdict must record the full-window block"
    return True, (f"API partial {returned} bars; {len(comp)} complete symbols; "
                  f"{cc.get('rsi_crash_events')} RSI crashes, {cc.get('confirmed_signals')} signals")


def check_portfolio_placebo() -> Tuple[bool, str]:
    """Phase M: exact full-portfolio placebo must exist and reconcile with canonical.

    Fails closed on a missing, stub, or non-reconciling artifact. The per-event null
    alone is not sufficient: it is uncapped and not a portfolio test.
    """
    path = STATE / "placebo_portfolio_okx_full.json"
    md = STATE / "placebo_portfolio_okx_full.md"
    if not path.exists() or not md.exists():
        return False, "json and/or md missing"
    try:
        data = _read_json(path)
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON: {exc}"
    if not isinstance(data, dict):
        return False, "top level must be an object"
    if PROVENANCE_CAVEAT.lower() not in str(data.get("provenance_caveat", "")).lower():
        return False, "json missing provenance caveat"
    if PROVENANCE_CAVEAT.lower() not in _read_text(md).lower():
        return False, "markdown missing provenance caveat"

    mode = str(data.get("mode", ""))
    if "exact_enumeration" not in mode and "random_draws" not in mode:
        return False, f"mode must be exact_enumeration or random_draws (got {mode!r})"
    if str(data.get("verdict", "")).lower() != "underpowered":
        return False, "verdict must be underpowered"

    can = data.get("canonical")
    if not isinstance(can, dict):
        return False, "missing canonical"
    try:
        can_trades = int(can.get("trades"))
        can_pnl = float(can.get("total_pnl"))
    except (TypeError, ValueError):
        return False, "canonical trades/total_pnl must be numeric"
    if can_trades != 8:
        return False, f"canonical.trades must be 8 (got {can_trades})"
    if abs(can_pnl - 9159.691934882958) > 1e-6:
        return False, f"canonical.total_pnl mismatch ({can_pnl!r})"
    replay = can.get("replay")
    if not isinstance(replay, dict):
        return False, "missing canonical.replay"
    try:
        if int(replay.get("num_trades")) != 8 or abs(float(replay.get("total_pnl")) - can_pnl) > 1e-6:
            return False, "canonical.replay does not reproduce canonical"
    except (TypeError, ValueError):
        return False, "canonical.replay must be numeric"

    pl = data.get("placebo")
    if not isinstance(pl, dict):
        return False, "missing placebo"
    try:
        runs = int(pl.get("runs"))
    except (TypeError, ValueError):
        return False, "placebo.runs must be an integer"
    if runs < 60:
        return False, f"placebo.runs must be >= 60 (got {runs})"
    summary = pl.get("summary")
    if not isinstance(summary, dict) or int(summary.get("n", 0)) != runs:
        return False, "placebo.summary.n must equal placebo.runs"
    for key in ("p_ge_canonical", "canonical_percentile_le", "prob_total_pnl_positive"):
        try:
            v = float(pl.get(key))
        except (TypeError, ValueError):
            return False, f"missing/invalid placebo.{key}"
        if not 0.0 <= v <= 1.0:
            return False, f"placebo.{key} out of [0,1]: {v}"
    rows = data.get("runs")
    if not isinstance(rows, list) or len(rows) != runs:
        return False, "placebo.runs list length mismatch"
    for r in rows:
        if not isinstance(r, dict) or "total_pnl" not in r or "num_trades" not in r:
            return False, "placebo run missing total_pnl/num_trades"
    if "underpowered" not in _read_text(md).lower():
        return False, "markdown missing underpowered verdict"
    return True, (f"exact portfolio placebo: {runs} runs, "
                  f"p_ge_canon={pl.get('p_ge_canonical')}, "
                  f"canon_pct={pl.get('canonical_percentile_le')}")


def check_hyperliquid_partial_campaign() -> Tuple[bool, str]:
    """Phase J3: the partial Hyperliquid run must exist and stay explicitly NOT_EVIDENCE."""
    path = STATE / "campaign_results_real_hyperliquid_partial_20260419_20260928.json"
    if not path.exists():
        return False, "missing"
    try:
        data = _read_json(path)
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON: {exc}"
    if not isinstance(data, dict):
        return False, "top level must be an object"
    if data.get("real_market_data") is not True:
        return False, "real_market_data must be true"
    if data.get("performance_evidence") is not False:
        return False, "performance_evidence must be false"
    if data.get("partial_universe_not_evidence") is not True:
        return False, "partial_universe_not_evidence must be true"
    if data.get("fabricated_data") is not False:
        return False, "fabricated_data must be false"
    results = data.get("results")
    if not isinstance(results, dict):
        return False, "missing results"
    try:
        if int(results.get("num_trades")) < 0:
            return False, "partial run must report a non-negative trade count"
        float(results.get("total_pnl"))
    except (TypeError, ValueError):
        return False, "results.num_trades/total_pnl must be numeric"
    prov = data.get("data_provenance")
    if not isinstance(prov, dict):
        return False, "missing data_provenance"
    tw = prov.get("target_window") or {}
    if tw.get("expected_hourly_bars") != 3900:
        return False, "partial target window must be the 3900-bar API window"
    if len(prov.get("symbols_complete") or []) < 12:
        return False, "partial run must load >= 12 complete symbols"
    return True, (f"partial Hyperliquid NOT_EVIDENCE run: {results.get('num_trades')} trades, "
                  f"{len(prov.get('symbols_complete') or [])} symbols")


def check_decision_memo() -> Tuple[bool, str]:
    """Phase M: decision memo must synthesize the verdict and stop/go criteria."""
    path = STATE / "decision_memo_okx_full.md"
    if not path.exists():
        return False, "missing"
    text = _read_text(path)
    if len(text) < 3000:
        return False, f"too small ({len(text)} bytes) — decision memo required"
    if PROVENANCE_CAVEAT.lower() not in text.lower():
        return False, "missing provenance caveat"
    missing = [t for t in ("underpowered", "not decision-grade", "stop", "go only if",
                           "hyperliquid", "9159.691934882958") if t not in text.lower()]
    if missing:
        return False, f"missing required terms: {missing}"
    return True, f"{len(text)} bytes"


def check_runbook() -> Tuple[bool, str]:
    path = STATE / "DATA_REQUEST_283D_HYPERLIQUID.md"
    if not path.exists():
        return False, "missing"
    text = _read_text(path)
    if "HYPERLIQUID NATIVE ACQUISITION RUNBOOK" not in text:
        return False, "runbook section missing"
    for token in ("fetch_hyperliquid_candles.py", "run_real_campaign.py", "NOT_RUN"):
        if token not in text:
            return False, f"runbook missing {token!r}"
    return True, "runbook present"


def check_exploratory_next_open() -> Tuple[bool, str]:
    """Step 3 heavy-work gate: the spec-literal next-open path must be a real-engine run.

    The structural 0-trade canonical funnel is only explained (not hand-waved) by
    executing the spec's own entry rule ("buy at next hourly open", no same-bar
    rebound candle) through the real portfolio engine on the retained chain. This
    check fails closed unless a timestamped artifact exists that:
      - is labeled NOT_EVIDENCE_EXPLORATORY_FANOUT with performance_evidence=false,
      - was produced by the real engine on real candles (fabricated_data=false),
      - reports integer num_trades and a numeric total_pnl,
      - records the structural funnel counts that explain the canonical 0,
      - confirms the canonical baseline was not changed.
    A prose note or an upper-bound count alone is not acceptance.
    """
    path = STATE / "hyperliquid_exploratory_next_open_latest.json"
    if not path.exists():
        return False, (
            "missing hyperliquid_exploratory_next_open_latest.json — run "
            "scripts/run_hyperliquid_exploratory_next_open.py (Step 3 heavy work)"
        )
    try:
        data = _read_json(path)
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON: {exc}"
    if not isinstance(data, dict):
        return False, "top level must be an object"
    if data.get("label") != "NOT_EVIDENCE_EXPLORATORY_FANOUT":
        return False, "label must be NOT_EVIDENCE_EXPLORATORY_FANOUT"
    if data.get("performance_evidence") is not False:
        return False, "performance_evidence must be false (exploratory, not evidence)"
    if data.get("fabricated_data") is not False:
        return False, "fabricated_data must be false (real candles only)"
    if data.get("real_market_data") is not True:
        return False, "real_market_data must be true"
    if data.get("canonical_baseline_changed") is not False:
        return False, "canonical_baseline_changed must be false"
    results = data.get("results")
    if not isinstance(results, dict):
        return False, "missing results"
    try:
        num_trades = int(results["num_trades"])
        total_pnl = float(results["total_pnl"])
    except (KeyError, TypeError, ValueError):
        return False, "results.num_trades/total_pnl must be numeric"
    if num_trades < 0:
        return False, "results.num_trades must be >= 0"
    funnel = data.get("funnel")
    if not isinstance(funnel, dict) or not isinstance(funnel.get("totals"), dict):
        return False, "missing funnel.totals"
    totals = funnel["totals"]
    for key in ("rsi_crash_hours_passing_trailing_24h_5m_volume",
                "same_bar_rebound_confirm_implementation",
                "generate_signal_canonical_same_bar_confirm",
                "generate_signal_spec_literal_next_open"):
        try:
            if int(totals[key]) < 0:
                raise ValueError
        except (KeyError, TypeError, ValueError):
            return False, f"funnel.totals.{key} must be a non-negative integer"
    canonical = int(totals["generate_signal_canonical_same_bar_confirm"])
    spec_literal = int(totals["generate_signal_spec_literal_next_open"])
    if spec_literal <= canonical:
        return False, (
            "spec-literal signal count must exceed the canonical same-bar count; "
            "the artifact does not demonstrate the structural funnel"
        )
    return True, (
        f"exploratory real-engine run: {num_trades} trades, total_pnl={total_pnl}; "
        f"funnel canonical={canonical} vs spec_literal={spec_literal}"
    )


def check_retention_probe() -> Tuple[bool, str]:
    """Phase P: the Hyperliquid full-window block must be reproducible, not prose.

    The handoff's central claim is that the public API cannot serve the 283-day
    window. That claim is only trustworthy if it can be re-derived: this check
    requires a live-probe artifact with derived counts (no hardcoded numbers), a
    non-trivial missing-bar count, and a verdict consistent with a real block.
    A probe that says 'served' without a genuine full campaign fails closed.
    """
    path = STATE / "hyperliquid_retention_probe.json"
    if not path.exists():
        return False, "missing hyperliquid_retention_probe.json (run scripts/probe_hyperliquid_blocker.py)"
    try:
        data = _read_json(path)
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON: {exc}"
    if not isinstance(data, dict):
        return False, "top level must be an object"
    for key in ("generated_at_utc", "target_window", "universe", "probe_summary", "verdict"):
        if key not in data:
            return False, f"missing {key!r}"

    summary = data["probe_summary"]
    if not isinstance(summary, dict):
        return False, "probe_summary must be an object"
    for key in ("full_window_served", "max_bars_returned",
                "missing_early_bars_vs_expected", "expected_hourly_bars"):
        if key not in summary:
            return False, f"missing probe_summary.{key}"

    try:
        expected = int(summary["expected_hourly_bars"])
        max_served = int(summary["max_bars_returned"])
        missing = int(summary["missing_early_bars_vs_expected"])
    except (TypeError, ValueError):
        return False, "probe_summary counts must be integers"
    if expected != 6792:
        return False, f"expected_hourly_bars must be the 6792-bar spec window (got {expected})"
    if max_served <= 0:
        return False, "no bars were served; the probe did not actually run"
    if max_served >= expected or missing <= 0:
        return False, (
            "the public API now serves the full window; a real full campaign artifact "
            "is required instead of the blocker claim"
        )
    if summary.get("full_window_served") is not False:
        return False, "full_window_served must be false when the window is incomplete"

    universe = data["universe"]
    if not isinstance(universe, dict):
        return False, "universe must be an object"
    try:
        perps = int(universe.get("perps_total", 0))
        passing = int(universe.get("perps_passing_volume_gate", 0))
        probed = int(universe.get("probed", 0))
    except (TypeError, ValueError):
        return False, "universe counts must be integers"
    if perps <= 0 or probed <= 0:
        return False, "probe must record a non-empty live universe and probe set"
    if passing < probed:
        return False, "passing_gate must be >= probed symbols"

    per_symbol = data.get("per_symbol")
    if not isinstance(per_symbol, list) or len(per_symbol) != probed:
        return False, "per_symbol must list every probed symbol"

    if "BLOCKED" not in str(data.get("verdict", "")).upper():
        return False, "verdict must record the full-window block"
    return True, (f"API serves {max_served}/{expected} bars; {missing} missing; "
                  f"universe {perps} perps / {passing} pass gate / {probed} probed")


def check_universe_coverage() -> Tuple[bool, str]:
    """Phase Q: the full live Hyperliquid universe must be probed, snapshotted, and censused.

    The binding constraint is independent crash episodes, and the public API only
    serves a decaying partial window. A prose 'data unavailable' claim is not
    enough: this check fails closed unless the *whole* qualifying universe was
    probed (not a 6-symbol sample), a real partial-window snapshot was captured
    for every served symbol, a cross-sectional crash census was run over the
    complete symbols, and a NOT_EVIDENCE partial campaign was executed. This is
    the achievable heavy-work floor; an agent cannot satisfy the handoff without
    producing it.
    """
    path = STATE / "hyperliquid_universe_coverage.json"
    if not path.exists():
        return False, "missing hyperliquid_universe_coverage.json (run probe + snapshot + census + partial campaign)"
    try:
        data = _read_json(path)
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON: {exc}"
    if not isinstance(data, dict):
        return False, "top level must be an object"
    for key in ("generated_at_utc", "api_retention_probe", "universe_snapshot",
                "crash_census", "partial_campaign", "verdict"):
        if key not in data:
            return False, f"missing {key!r}"

    probe = data["api_retention_probe"]
    if not isinstance(probe, dict):
        return False, "api_retention_probe must be an object"
    try:
        perps = int(probe["perps_total"])
        passing = int(probe["perps_passing_volume_gate"])
        probed = int(probe["probed"])
    except (KeyError, TypeError, ValueError):
        return False, "api_retention_probe universe counts must be integers"
    if perps <= 0 or passing <= 0:
        return False, "api_retention_probe universe must be non-empty"
    if probed < passing:
        return False, (
            f"full universe not probed: probed={probed} < passing_gate={passing}; "
            "run scripts/probe_hyperliquid_blocker.py with --limit >= passing gate"
        )

    snap = data["universe_snapshot"]
    if not isinstance(snap, dict):
        return False, "universe_snapshot must be an object"
    try:
        complete = int(snap["symbols_complete"])
        requested = int(snap["symbols_requested"])
    except (KeyError, TypeError, ValueError):
        return False, "universe_snapshot.symbols_complete/requested must be integers"
    if complete < 12:
        return False, f"universe_snapshot.symbols_complete must be >= 12 (got {complete})"
    if requested < complete:
        return False, "universe_snapshot.symbols_requested must be >= complete"
    if not isinstance(snap.get("complete_symbols"), list) or len(snap["complete_symbols"]) != complete:
        return False, "universe_snapshot.complete_symbols must list every complete symbol"

    census = data["crash_census"]
    if not isinstance(census, dict):
        return False, "crash_census must be an object"
    try:
        c_symbols = int(census["symbols"])
        c_bars = int(census["bars"])
        c_crashes = int(census["rsi_crash_events"])
        c_signals = int(census["confirmed_signals"])
    except (KeyError, TypeError, ValueError):
        return False, "crash_census counts must be integers"
    if c_symbols != complete:
        return False, f"crash_census.symbols ({c_symbols}) must equal complete symbols ({complete})"
    if c_bars < complete * 3000:
        return False, f"crash_census.bars ({c_bars}) too small for {complete} symbols"
    if c_crashes < 1:
        return False, "crash_census.rsi_crash_events must be >= 1"
    if c_signals < 0:
        return False, "crash_census.confirmed_signals must be >= 0"

    camp = data["partial_campaign"]
    if not isinstance(camp, dict):
        return False, "partial_campaign must be an object"
    if camp.get("performance_evidence") is not False:
        return False, "partial_campaign.performance_evidence must be false (NOT_EVIDENCE)"
    try:
        if int(camp.get("num_trades", -1)) < 0:
            return False, "partial_campaign.num_trades must be >= 0"
    except (TypeError, ValueError):
        return False, "partial_campaign.num_trades must be an integer"

    if "BLOCKED" not in str(data.get("verdict", "")).upper():
        return False, "verdict must record the full-window block"
    if "UNDERPOWERED" not in str(data.get("verdict", "")).upper():
        return False, "verdict must record the underpowered strategy state"
    return True, (f"full universe probed {probed}/{passing}; snapshot {complete} complete; "
                  f"census {c_symbols} symbols/{c_bars} bars/{c_crashes} crashes/{c_signals} signals")


def check_evidence_verifier() -> Tuple[bool, str]:
    """Phase P: the mechanical anti-avoidance verifier must pass on real artifacts.

    session_gate proves the evidence chain is complete; this proves the chain is
    *real* — canonical OKX reconciles, the Hyperliquid blocker is backed by the
    probe, no artifact claims a validated verdict, and the placeholder archive is
    still labeled non-evidence. It is narrative-independent.
    """
    # session_gate is in scripts/ so verify_campaign_evidence needs REPO in sys.path
    sys.path.insert(0, str(REPO_ROOT))
    try:
        from scripts import verify_campaign_evidence as ver
    except Exception as exc:  # noqa: BLE001
        return False, f"cannot import verify_campaign_evidence: {exc}"
    # The verifier reads STATE; keep it pointed at this gate's STATE.
    original = ver.STATE
    ver.STATE = STATE
    try:
        ok, rows = ver.verify()
    finally:
        ver.STATE = original
    if not ok:
        failed = [r["check"] for r in rows if not r["pass"]]
        return False, f"evidence verification failed: {failed}"
    return True, f"evidence verified ({len(rows)} checks)"


def check_handoff() -> Tuple[bool, str]:
    path = REPO_ROOT / "HANDOFF.md"
    if not path.exists():
        return False, "missing"
    text = _read_text(path)
    if "INITIAL TASK MESSAGE" not in text:
        return False, "missing INITIAL TASK MESSAGE block"
    if "session_gate.py" not in text:
        return False, "does not reference the done-gate"
    expected = f"{len(CHECKS)}/{len(CHECKS)} checks passed"
    if expected not in text:
        return False, f"handoff must record the current gate result ({expected})"
    try:
        generated_at = str(_read_json(STATE / "episode_edge_okx_full.json").get("generated_at_utc", ""))
    except (OSError, json.JSONDecodeError, AttributeError):
        generated_at = ""
    if not generated_at or generated_at not in text:
        return False, "handoff must record the current Phase O artifact timestamp"
    # The handoff is the single durable initial task message: it must tell the
    # next session which gate to run and which evidence is binding, or a future
    # agent can "read the handoff" and still do nothing verifiable.
    for token in ("probe_hyperliquid_blocker.py", "verify_campaign_evidence.py"):
        if token not in text:
            return False, f"handoff must reference {token} in the initial task message"
    return True, f"{len(text)} bytes; Phase O {generated_at}"


CHECKS: List[Tuple[str, Callable[[], Tuple[bool, str]]]] = [
    ("phase_g_spec_comparison_md", check_spec_comparison_md),
    ("phase_g_spec_comparison_json", check_spec_comparison_json),
    ("phase_j1_crash_event_census", check_census),
    ("phase_j2_sensitivity_sweep", check_sensitivity),
    ("phase_k_interaction_sweep", check_interaction),
    ("phase_l_robustness", check_robustness),
    ("phase_n_robustness_stress", check_robustness_stress),
    ("phase_o_episode_edge", check_episode_edge),
    ("phase_m_portfolio_placebo", check_portfolio_placebo),
    ("phase_m_decision_memo", check_decision_memo),
    ("phase_j3_hyperliquid_status", check_hyperliquid_status),
    ("phase_j3_hyperliquid_partial_campaign", check_hyperliquid_partial_campaign),
    ("phase_j3_acquisition_runbook", check_runbook),
    ("phase_p_retention_probe", check_retention_probe),
    ("phase_q_universe_coverage", check_universe_coverage),
    ("phase_r_exploratory_next_open", check_exploratory_next_open),
    ("phase_p_evidence_verifier", check_evidence_verifier),
    ("durable_handoff", check_handoff),
]


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable result")
    args = parser.parse_args(argv)

    results = []
    for name, fn in CHECKS:
        try:
            ok, detail = fn()
        except Exception as exc:  # fail closed on any unexpected error
            ok, detail = False, f"error: {exc}"
        results.append({"check": name, "pass": ok, "detail": detail})

    passed = sum(1 for r in results if r["pass"])
    total = len(results)
    overall = passed == total

    if args.json:
        print(json.dumps({"pass": overall, "passed": passed, "total": total, "checks": results}, indent=2))
    else:
        for r in results:
            print(f"[{'PASS' if r['pass'] else 'FAIL'}] {r['check']}: {r['detail']}")
        print(f"\n{passed}/{total} checks passed — {'DONE' if overall else 'NOT DONE'}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())