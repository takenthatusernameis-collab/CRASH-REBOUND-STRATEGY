#!/usr/bin/env python3
"""C13 acceptance gate — config-matched decision-grade follow-up (fail-closed).

This gate is the machine-checkable acceptance test for C13: the pre-registered,
config-matched (RSI 25 / target 9) decision-grade validation of the C12 lead on
Hyperliquid-native evidence. It refuses to pass on planning-only turns, handoff
rewrites, canonical-only reruns, missing prereg, non-config-matched inference,
compute that predates the prereg, or verdicts that contradict their evidence.

It is intentionally separate from session_gate.py (21-check evidence chain) and
verify_next_focus_campaign.py (C6 cross-venue acceptance): those stay green on
retained canonical state, while this gate measures the NEW C13 work and is RED
until C13 is actually executed.

Requirements (all must pass; exit 0 only then):
  1. C13 prereg exists BEFORE compute: research_state/hyperliquid_native_c13_prereg_*.json
     (+ .md sibling) with provenance caveat, lead hypothesis rsi 25 / target 9,
     decision rules and power targets.
  2. Config-matched real-engine inference artifacts exist and were generated at
     or after the prereg: BOTH an episode-edge-style artifact (temporal_edge_permutation)
     and a placebo-style artifact (placebo section) whose `config` block records
     rsi_threshold 25, target_pct 9, config_matched=true, with node-derived
     provenance (no cross-venue relabeling, no synthetic data).
  3. Native C13 verdict research_state/decision_verdict_hyperliquid_native_c13_*.md
     exists, states a verdict token, references dependence-aware evidence, and
     does not contradict itself (no GO claim alongside underpowered/spans-0 text).
  4. HANDOFF.md references C13 and this gate.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / "research_state"
HANDOFF = REPO / "HANDOFF.md"

LEAD_RSI = 25.0
LEAD_TARGET = 9.0
NO_GO_TOKENS = ("NO_DECISION_GRADE_GO", "NO_GO", "UNDERPOWERED", "FRAGILE")
UNDERPOWERED_TOKENS = ("underpowered", "spans 0", "not decision-grade", "not validated", "hypothesis-generating")


def _check(label: str, ok: bool, detail: str = "") -> bool:
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f": {detail}" if detail else ""))
    return ok


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _parse_ts(text: str) -> Optional[dt.datetime]:
    try:
        cleaned = str(text).strip()
        if cleaned.endswith("Z"):
            cleaned = cleaned[:-1] + "+00:00"
        return dt.datetime.fromisoformat(cleaned).astimezone(dt.timezone.utc)
    except Exception:
        return None


def _latest(pattern: str) -> Optional[Path]:
    matches = sorted(STATE.glob(pattern))
    return matches[-1] if matches else None


def check_prereg() -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    prereg = _latest("hyperliquid_native_c13_prereg_*.json")
    if prereg is None:
        return False, "missing research_state/hyperliquid_native_c13_prereg_*.json", None
    md = prereg.with_suffix(".md")
    if not md.exists():
        return False, f"missing prereg markdown sibling {md.name}", None
    data = _load_json(prereg)
    if data is None:
        return False, f"unreadable prereg JSON {prereg.name}", None
    text = json.dumps(data)
    problems: List[str] = []
    if data.get("fabricated_data") is not False and data.get("synthetic_data") is not False:
        problems.append("prereg must declare fabricated_data/synthetic_data false")
    caveat = str(data.get("provenance_caveat", ""))
    if "node-derived" not in caveat.lower() or "candleSnapshot" not in caveat:
        problems.append("provenance_caveat must record node-derived (Ironflow) NOT venue candleSnapshot")
    if "rsi_threshold" not in text or not re.search(r"\b25\b", text):
        problems.append("lead hypothesis must specify rsi_threshold 25")
    if "target_pct" not in text or not re.search(r"\b9\b", text):
        problems.append("lead hypothesis must specify target_pct 9")
    if not any(k in text for k in ("decision_rules", "pass_fail", "stop_go", "pass/fail")):
        problems.append("prereg must define explicit pass/fail/insufficient decision rules")
    if "power" not in text.lower():
        problems.append("prereg must state power/episode targets")
    ts = _parse_ts(data.get("generated_at_utc", ""))
    if ts is None:
        problems.append("prereg missing parseable generated_at_utc")
    if problems:
        return False, f"{prereg.name}: " + "; ".join(problems), data
    return True, f"{prereg.name} ({data.get('generated_at_utc')})", data


def _is_config_matched_inference(data: Dict[str, Any]) -> bool:
    cfg = data.get("config") or {}
    if cfg.get("config_matched") is not True:
        return False
    try:
        if float(cfg.get("rsi_threshold")) != LEAD_RSI:
            return False
        if float(cfg.get("target_pct")) != LEAD_TARGET:
            return False
    except (TypeError, ValueError):
        return False
    caveat = str(data.get("provenance_caveat", "")).lower()
    if "node-derived" not in caveat:
        return False
    venue = str(data.get("venue_label", "")).lower()
    if data.get("is_hyperliquid_evidence") is not True and "hyperliquid" not in venue:
        return False
    if data.get("fabricated_data") is True:
        return False
    return True


def check_inference(prereg_ts: Optional[dt.datetime]) -> Tuple[bool, str]:
    episode_edge: Optional[Path] = None
    placebo: Optional[Path] = None
    for path in sorted(STATE.glob("*.json")):
        data = _load_json(path)
        if not isinstance(data, dict) or not _is_config_matched_inference(data):
            continue
        gen = _parse_ts(data.get("generated_at_utc", ""))
        if prereg_ts is not None and (gen is None or gen < prereg_ts):
            continue
        if "temporal_edge_permutation" in data and episode_edge is None:
            episode_edge = path
        if isinstance(data.get("placebo"), dict) and (data.get("canonical") or {}).get("trades") and placebo is None:
            placebo = path
    problems: List[str] = []
    if episode_edge is None:
        problems.append("no config-matched episode-edge artifact (config rsi25/t9, generated after prereg)")
    if placebo is None:
        problems.append("no config-matched portfolio-placebo artifact (config rsi25/t9, generated after prereg)")
    if problems:
        return False, "; ".join(problems)
    return True, f"episode_edge={episode_edge.name}; placebo={placebo.name}"


def check_verdict() -> Tuple[bool, str]:
    verdict = _latest("decision_verdict*c13*.md")
    if verdict is None:
        return False, "missing research_state/decision_verdict_hyperliquid_native_c13_*.md"
    text = verdict.read_text()
    problems: List[str] = []
    if not re.search(r"\b25\b", text) or not re.search(r"\b9\b", text):
        problems.append("verdict must state the lead config (RSI 25 / target 9)")
    if not any(tok in text for tok in NO_GO_TOKENS) and not re.search(r"\bGO\b", text):
        problems.append("verdict must state a verdict token (GO / NO_GO / NO_DECISION_GRADE_GO / UNDERPOWERED)")
    if not any(tok in text.lower() for tok in ("bootstrap", "permutation", "placebo", "ci95", "ci 95", "confidence interval")):
        problems.append("verdict must reference dependence-aware evidence (bootstrap/permutation/placebo/CI)")
    claims_go = re.search(r"(?<!NO_)(?<!DECISION_GRADE_)\bGO\b", text) and "NO_DECISION_GRADE_GO" not in text and "NO_GO" not in text
    if claims_go and any(tok in text.lower() for tok in UNDERPOWERED_TOKENS):
        problems.append("verdict claims GO while also stating underpowered/spans-0/not-validated — contradictory")
    if problems:
        return False, f"{verdict.name}: " + "; ".join(problems)
    return True, verdict.name


def main() -> int:
    results: List[Tuple[str, bool, str]] = []

    ok, detail, prereg = check_prereg()
    _check("c13_prereg_before_compute", ok, detail)
    results.append(("c13_prereg_before_compute", ok, detail))
    prereg_ts = _parse_ts(prereg.get("generated_at_utc", "")) if prereg else None

    ok, detail = check_inference(prereg_ts)
    _check("c13_config_matched_inference", ok, detail)
    results.append(("c13_config_matched_inference", ok, detail))

    ok, detail = check_verdict()
    _check("c13_native_verdict", ok, detail)
    results.append(("c13_native_verdict", ok, detail))

    if HANDOFF.exists():
        text = HANDOFF.read_text()
        ok_handoff = "C13" in text and "verify_c13_focus_campaign.py" in text
        detail_handoff = f"{len(text)} bytes"
    else:
        ok_handoff, detail_handoff = False, "missing HANDOFF.md"
    _check("handoff_references_c13", ok_handoff, detail_handoff)
    results.append(("handoff_references_c13", ok_handoff, detail_handoff))

    ok_all = all(v[1] for v in results)
    print()
    if ok_all:
        print("C13 ACCEPTANCE: PASS — config-matched native C13 artifacts complete")
        return 0
    failed = [v[0] for v in results if not v[1]]
    print(f"C13 ACCEPTANCE: FAIL — {len(failed)} requirement(s) missing: {', '.join(failed)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())