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


def check_handoff() -> Tuple[bool, str]:
    path = REPO_ROOT / "HANDOFF.md"
    if not path.exists():
        return False, "missing"
    text = _read_text(path)
    if "INITIAL TASK MESSAGE" not in text:
        return False, "missing INITIAL TASK MESSAGE block"
    if "session_gate.py" not in text:
        return False, "does not reference the done-gate"
    return True, f"{len(text)} bytes"


CHECKS: List[Tuple[str, Callable[[], Tuple[bool, str]]]] = [
    ("phase_g_spec_comparison_md", check_spec_comparison_md),
    ("phase_g_spec_comparison_json", check_spec_comparison_json),
    ("phase_j1_crash_event_census", check_census),
    ("phase_j2_sensitivity_sweep", check_sensitivity),
    ("phase_k_interaction_sweep", check_interaction),
    ("phase_l_robustness", check_robustness),
    ("phase_m_portfolio_placebo", check_portfolio_placebo),
    ("phase_m_decision_memo", check_decision_memo),
    ("phase_j3_acquisition_runbook", check_runbook),
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