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


def check_sensitivity() -> Tuple[bool, str]:
    path = STATE / "sensitivity_sweep_real_okx_full.json"
    md = STATE / "sensitivity_sweep_real_okx_full.md"
    if not path.exists() or not md.exists():
        return False, "json and/or md missing"
    try:
        data = _read_json(path)
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON: {exc}"
    runs = data.get("runs")
    if not isinstance(runs, list) or len(runs) < 16:
        return False, "need baseline + >= 15 sweep runs"
    for run in runs:
        if "params" not in run or "metrics" not in run:
            return False, "a run is missing params/metrics"
        metrics = run["metrics"]
        for key in ("total_return_pct", "trade_count"):
            if key not in metrics:
                return False, f"a run is missing metrics.{key}"
    return True, f"{len(runs)} runs"


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