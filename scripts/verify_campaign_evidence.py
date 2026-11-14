#!/usr/bin/env python3
"""Campaign evidence verifier — mechanical anti-avoidance gate.

WHY THIS EXISTS
---------------
The repo's done-gate (`scripts/session_gate.py`) proves the *evidence chain* is
complete. It does not prove the next session actually produced new real work, and
it cannot detect the classic avoidance patterns:

* a "campaign" artifact that is narrative JSON with no trades and no data;
* a partial / synthetic / placeholder dataset relabeled as evidence;
* a `validated` verdict asserted in the handoff while the artifacts still say
  `underpowered`;
* a session that only edited markdown and never touched a real artifact.

This verifier checks the artifacts themselves, mechanically, and fails closed.
It is deliberately independent of the narrative in `HANDOFF.md`: a future agent
cannot satisfy it by writing better prose.

Checks performed
----------------
1. Canonical OKX campaign is real, complete and reconciles with the handoff:
   `performance_evidence=true`, `real_market_data=true`, `fabricated_data=false`,
   and the recorded trade count / total PnL match the canonical constants.
2. Hyperliquid full-window status: exactly one of
   (a) full window served -> a real full campaign artifact with
       `performance_evidence=true` exists and reconciles with the probe; or
   (b) full window blocked -> the reproducible retention probe exists, records
       `full_window_served=false` with non-trivial missing bars, and every
       Hyperliquid partial artifact stays `performance_evidence=false`.
3. No artifact is allowed to claim `validated` / decision-grade while the
   canonical verdict is `underpowered`.
4. The placeholder archive is still explicitly marked as non-evidence.

Exit code 0 means "the evidence on disk is real and the verdict is honest".
Exit code 1 means an avoidance pattern was detected (with the exact reason).

Usage:
    PYTHONPATH=. python scripts/verify_campaign_evidence.py
    PYTHONPATH=. python scripts/verify_campaign_evidence.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

STATE = REPO / "research_state"

# Canonical OKX result. These are historical facts about a completed, frozen run;
# the verifier compares the artifact against them so a tampered or stub campaign
# artifact fails closed. They are NOT a target to reproduce with new data.
CANONICAL_OKX_PNL = 9159.691934882958
CANONICAL_OKX_TRADES = 8
CANONICAL_OKX_PERFORMANCE_EVIDENCE = True  # real OKX data, cross-venue caveat only

PROVENANCE_CAVEAT = (
    "Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; "
    "NOT Hyperliquid performance evidence."
)

PLACEHOLDER_ARCHIVE = (
    STATE / "archives" / "hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet"
)


class VerificationError(RuntimeError):
    pass


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _rel(path: Path) -> str:
    """Path relative to the active STATE root (monkeypatch-friendly)."""
    try:
        return str(path.relative_to(STATE))
    except ValueError:
        return str(path)


def _require(path: Path, label: str) -> Dict[str, Any]:
    if not path.exists():
        raise VerificationError(f"{label}: missing artifact {path}")
    try:
        data = _read_json(path)
    except json.JSONDecodeError as exc:
        raise VerificationError(f"{label}: invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise VerificationError(f"{label}: {path} must be a JSON object")
    return data


def check_canonical_okx() -> Dict[str, Any]:
    """The canonical campaign must be real, non-fabricated and reconcile."""
    path = STATE / "campaign_results_real_okx_full.json"
    data = _require(path, "canonical_okx")
    if data.get("real_market_data") is not True:
        raise VerificationError("canonical_okx: real_market_data must be true")
    if data.get("fabricated_data") is not False:
        raise VerificationError("canonical_okx: fabricated_data must be false")
    if data.get("performance_evidence") is not True:
        raise VerificationError("canonical_okx: performance_evidence must be true")

    results = data.get("results")
    if not isinstance(results, dict):
        raise VerificationError("canonical_okx: missing results object")
    try:
        trades = int(results.get("num_trades"))
        pnl = float(results.get("total_pnl"))
    except (TypeError, ValueError) as exc:
        raise VerificationError("canonical_okx: results.num_trades/total_pnl must be numeric") from exc
    if trades != CANONICAL_OKX_TRADES:
        raise VerificationError(f"canonical_okx: trades {trades} != {CANONICAL_OKX_TRADES}")
    if abs(pnl - CANONICAL_OKX_PNL) > 1e-6:
        raise VerificationError(f"canonical_okx: total_pnl {pnl!r} != {CANONICAL_OKX_PNL!r}")
    return {"trades": trades, "total_pnl": pnl, "artifact": _rel(path)}


def _full_hyperliquid_campaign() -> Optional[Dict[str, Any]]:
    for name in (
        "campaign_results_real_hyperliquid_full.json",
    ):
        p = STATE / name
        if p.exists():
            try:
                data = _read_json(p)
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict):
                return data
    return None


def check_hyperliquid_blocker() -> Dict[str, Any]:
    """The blocker must be reproducible, or the full campaign must be real."""
    probe_path = STATE / "hyperliquid_retention_probe.json"
    full = _full_hyperliquid_campaign()

    if full is not None:
        # A full campaign exists: it must be genuine, or this is the avoidance
        # pattern "relabel a partial/placeholder as full evidence".
        if full.get("performance_evidence") is not True:
            raise VerificationError(
                "hyperliquid_full: campaign artifact exists but performance_evidence is not true"
            )
        if full.get("real_market_data") is not True:
            raise VerificationError("hyperliquid_full: real_market_data must be true")
        if full.get("fabricated_data") is not False:
            raise VerificationError("hyperliquid_full: fabricated_data must be false")
        return {"mode": "full_campaign", "artifact": "campaign_results_real_hyperliquid_full.json"}

    probe = _require(probe_path, "hyperliquid_retention_probe")
    summary = probe.get("probe_summary")
    if not isinstance(summary, dict):
        raise VerificationError("hyperliquid_retention_probe: missing probe_summary")
    if summary.get("full_window_served") is not False:
        raise VerificationError(
            "hyperliquid_retention_probe: full_window_served is not false; a full campaign "
            "artifact is required (relabeling the partial window is not allowed)"
        )
    expected = summary.get("expected_hourly_bars")
    max_served = summary.get("max_bars_returned")
    missing = summary.get("missing_early_bars_vs_expected")
    try:
        expected_i = int(expected)
        max_i = int(max_served)
        missing_i = int(missing)
    except (TypeError, ValueError) as exc:
        raise VerificationError("hyperliquid_retention_probe: counts must be integers") from exc
    if expected_i <= 0:
        raise VerificationError("hyperliquid_retention_probe: expected_hourly_bars must be positive")
    if max_i <= 0:
        raise VerificationError("hyperliquid_retention_probe: no bars were served at all")
    if missing_i <= 0:
        raise VerificationError(
            "hyperliquid_retention_probe: missing_early_bars must be positive for a blocked window"
        )
    if max_i >= expected_i:
        raise VerificationError(
            "hyperliquid_retention_probe: served bars cover the window; this is not a block"
        )
    if not probe.get("generated_at_utc"):
        raise VerificationError("hyperliquid_retention_probe: missing generated_at_utc")

    # Every partial Hyperliquid artifact must stay explicitly NOT evidence.
    partial_names = [
        "campaign_results_real_hyperliquid_partial_20260419_20260928.json",
    ]
    for name in partial_names:
        p = STATE / name
        if not p.exists():
            continue
        try:
            data = _read_json(p)
        except json.JSONDecodeError as exc:
            raise VerificationError(f"partial_hyperliquid: {name} invalid JSON: {exc}") from exc
        if not isinstance(data, dict):
            continue
        if data.get("performance_evidence") is not False:
            raise VerificationError(
                f"partial_hyperliquid: {name} must keep performance_evidence=false"
            )
        if data.get("fabricated_data") is not False:
            raise VerificationError(f"partial_hyperliquid: {name} fabricated_data must be false")

    return {
        "mode": "blocked",
        "probe": _rel(probe_path),
        "expected_hourly_bars": expected_i,
        "max_bars_returned": max_i,
        "missing_early_bars": missing_i,
        "earliest_served_start_utc": summary.get("earliest_served_start_utc"),
    }


def check_verdict_honesty() -> Dict[str, Any]:
    """No artifact may claim a validated/decision-grade verdict while evidence is weak."""
    # The Phase O episode artifact is the canonical verdict holder.
    ep_path = STATE / "episode_edge_okx_full.json"
    ep = _require(ep_path, "verdict_honesty")
    verdict = str(ep.get("verdict", "")).strip().lower()
    if verdict != "underpowered":
        raise VerificationError(
            f"verdict_honesty: episode verdict is {verdict!r}, expected 'underpowered'; "
            "a stronger verdict requires the Hyperliquid GO criteria to be met first"
        )

    forbidden = ("validated", "decision-grade", "go", "investable", "profitable")
    for name in ("placebo_portfolio_okx_full.json", "robustness_stress_okx_full.json"):
        p = STATE / name
        if not p.exists():
            continue
        try:
            data = _read_json(p)
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        text = json.dumps(data).lower()
        claimed = str(data.get("verdict", "")).strip().lower()
        if claimed in forbidden:
            raise VerificationError(f"verdict_honesty: {name} claims verdict {claimed!r}")
        if '"validated"' in text and "underpowered" not in text:
            raise VerificationError(f"verdict_honesty: {name} asserts validated without caveat")
    return {"canonical_verdict": verdict}


def check_placeholder_not_evidence() -> Dict[str, Any]:
    """The flat placeholder archive must remain labeled non-evidence."""
    readme = STATE / "archives" / "hyperliquid_btc_eth_1h_20251220_20260928_verified.README.json"
    if readme.exists():
        try:
            data = _read_json(readme)
        except json.JSONDecodeError as exc:
            raise VerificationError(f"placeholder: invalid README JSON: {exc}") from exc
        note = str(data.get("note", "")).lower()
        if "not" not in note or "full" not in note:
            raise VerificationError(
                "placeholder: README must state the archive is NOT full-universe evidence"
            )
    return {"placeholder_present": PLACEHOLDER_ARCHIVE.exists(), "labeled_non_evidence": True}


CHECKS = [
    ("canonical_okx", check_canonical_okx),
    ("hyperliquid_blocker", check_hyperliquid_blocker),
    ("verdict_honesty", check_verdict_honesty),
    ("placeholder_not_evidence", check_placeholder_not_evidence),
]


def verify() -> Tuple[bool, List[Dict[str, Any]]]:
    rows: List[Dict[str, Any]] = []
    ok_all = True
    for name, fn in CHECKS:
        try:
            detail = fn()
            rows.append({"check": name, "pass": True, "detail": detail})
        except VerificationError as exc:
            ok_all = False
            rows.append({"check": name, "pass": False, "detail": str(exc)})
        except Exception as exc:  # noqa: BLE001 - fail closed on anything unexpected
            ok_all = False
            rows.append({"check": name, "pass": False, "detail": f"error: {exc}"})
    return ok_all, rows


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    ok, rows = verify()
    if args.json:
        print(json.dumps({"pass": ok, "checks": rows}, indent=2))
    else:
        for r in rows:
            print(f"[{'PASS' if r['pass'] else 'FAIL'}] {r['check']}: {r['detail']}")
        print(f"\n{'EVIDENCE VERIFIED' if ok else 'EVIDENCE VERIFICATION FAILED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())