#!/usr/bin/env python3
"""C19 acceptance gate — Hyperliquid-native spec adjudication & final synthesis.

C19 is the post-acquisition focus campaign. Native-market acquisition is
exhausted (C15/C16/C17/C18 all BLOCKED_EVIDENCED_DATA_REQUIRED), so the binding
remaining work is executable and local: adjudicate the same-bar vs spec-literal
next-open rebound-confirmation fork, reconcile the contradictory native runs
(C14 canonical +8,914.33 / 7 trades vs C18 spec-literal -47,933.58 / 22 trades),
and issue a single decision-grade final verdict.

This gate is fail-closed. It refuses to pass on planning-only turns, a
narrative-only adjudication, a verdict that does not reconcile C14/C18, a
consolidated final that predates the C19 prereg, or a handoff that does not
point at this campaign. It is intentionally separate from session_gate.py: the
21-check evidence-chain gate stays green on the retained canonical state, while
this gate measures the new C19 work.

Accepted terminal states:
  (A) GO          — adjudication + native verdict GO + new consolidated final
  (B) UNDERPOWERED / NO_GO — adjudication + native verdict + new consolidated final
A bare "blocked" or "no new data" is NOT an accepted C19 terminal state: C19 is
local analysis, not acquisition.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / "research_state"
HANDOFF = REPO / "HANDOFF.md"

PREREG_GLOB = "c19_prereg_*.json"
ADJ_GLOB = "spec_rebound_confirmation_adjudication_*.json"
NATIVE_VERDICT_GLOB = "decision_verdict_hyperliquid_native_c19_*.json"
CONSOLIDATED_GLOB = "decision_verdict_CONSOLIDATED_FINAL_*.json"

ADJ_LABEL = "NOT_EVIDENCE_SPEC_INTERPRETATION_ADJUDICATION"
VALID_DECISIONS = {"SPEC_LITERAL_NEXT_OPEN", "CANONICAL_SAME_BAR_RETAINED"}
VALID_VERDICTS = {"GO", "UNDERPOWERED", "NO_GO"}

PREREG_TS = "20261116T053500Z"


def _latest(pattern: str) -> Optional[Path]:
    matches = sorted(STATE.glob(pattern))
    return matches[-1] if matches else None


def _load(path: Path) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        return json.loads(path.read_text()), None
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def _check(label: str, ok: bool, detail: str = "") -> bool:
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f": {detail}" if detail else ""))
    return ok


def _ts_of(data: Dict[str, Any]) -> str:
    return str(data.get("generated_at_utc") or "")


def main() -> int:
    results: List[Tuple[str, bool, str]] = []

    # 1. Prereg exists, is C19, pre-registered, and predates all compute.
    prereg_p = _latest(PREREG_GLOB)
    prereg = None
    if prereg_p is None:
        results.append(("c19_prereg", False, f"missing {PREREG_GLOB}"))
    else:
        prereg, err = _load(prereg_p)
        ok = (
            prereg is not None
            and prereg.get("campaign") == "C19"
            and prereg.get("status") == "PRE_REGISTERED_BEFORE_COMPUTE"
            and prereg.get("adjudication_question", {}).get("decision_rule_pre_registered")
            and prereg.get("decision_floors", {}).get("go_requires")
        )
        results.append((
            "c19_prereg",
            bool(ok),
            f"{prereg_p.name}" + (f" ({err})" if err else ""),
        ))
    prereg_ts = _ts_of(prereg) if prereg else ""

    # 2. Adjudication artifact: real audit, explicit decision, reconciles C14/C18.
    adj_p = _latest(ADJ_GLOB)
    adj = None
    if adj_p is None:
        results.append(("c19_adjudication", False, f"missing {ADJ_GLOB}"))
    else:
        adj, err = _load(adj_p)
        ok = False
        detail = f"{adj_p.name}"
        if err:
            detail += f" ({err})"
        elif isinstance(adj, dict):
            decision = adj.get("decision")
            sources = adj.get("spec_sources") or []
            code_changes = adj.get("code_changes_made")
            ok = (
                adj.get("campaign") == "C19"
                and adj.get("label") == ADJ_LABEL
                and adj.get("performance_evidence") is False
                and isinstance(code_changes, bool)
                and (code_changes is False or bool(adj.get("code_change_description")))
                and decision in VALID_DECISIONS
                and isinstance(sources, list)
                and len(sources) > 0
                and adj.get("reconciles_c14_c18") is True
                and bool(adj.get("c14_stem"))
                and bool(adj.get("c18_stem"))
                and bool(prereg_ts)
                and _ts_of(adj) >= prereg_ts
            )
            detail += f"; decision={decision}; code_changes={code_changes}; sources={len(sources)}"
        results.append(("c19_adjudication", ok, detail))

    # 3. Native C19 verdict: token + reconciliation + dependence-aware inference.
    nv_p = _latest(NATIVE_VERDICT_GLOB)
    if nv_p is None:
        results.append(("c19_native_verdict", False, f"missing {NATIVE_VERDICT_GLOB}"))
    else:
        nv, err = _load(nv_p)
        ok = False
        detail = f"{nv_p.name}"
        if err:
            detail += f" ({err})"
        elif isinstance(nv, dict):
            token = nv.get("verdict")
            refs = nv.get("references") or {}
            ref_text = json.dumps(refs) + " " + json.dumps(nv.get("reconciliation") or {})
            inf = nv.get("inference") or {}
            has_inf = all(
                k in json.dumps(inf).lower()
                for k in ("bootstrap", "permutation", "placebo")
            )
            ok = (
                nv.get("campaign") == "C19"
                and token in VALID_VERDICTS
                and nv.get("is_hyperliquid_evidence") is True
                and nv.get("cross_venue") is False
                and "20261116T001200Z" in ref_text
                and "20261116T045000Z" in ref_text
                and has_inf
                and (token != "GO" or "underpowered" not in json.dumps(nv).lower())
                and bool(adj is not None and _ts_of(nv) >= _ts_of(adj))
            )
            detail += f"; verdict={token}; refs_c14_c18={'20261116T001200Z' in ref_text and '20261116T045000Z' in ref_text}; inference={has_inf}"
        results.append(("c19_native_verdict", ok, detail))

    # 4. New consolidated final: must postdate the C19 prereg and reference C19.
    cf_p = _latest(CONSOLIDATED_GLOB)
    if cf_p is None:
        results.append(("c19_consolidated_final", False, f"missing {CONSOLIDATED_GLOB}"))
    else:
        cf, err = _load(cf_p)
        ok = False
        detail = f"{cf_p.name}"
        if err:
            detail += f" ({err})"
        elif isinstance(cf, dict):
            token = cf.get("final_verdict") or cf.get("verdict")
            refs = json.dumps(cf.get("references") or {})
            ok = (
                token in VALID_VERDICTS
                and bool(prereg_ts)
                and _ts_of(cf) > prereg_ts
                and ("C19" in refs or "C19" in json.dumps(cf))
                and bool(cf.get("supersedes"))
            )
            detail += f"; final={token}; ts={_ts_of(cf)}; supersedes={cf.get('supersedes')}"
        results.append(("c19_consolidated_final", ok, detail))

    # 5. Handoff points at C19 and this gate.
    if HANDOFF.exists():
        text = HANDOFF.read_text()
        ok = "C19-T1" in text and "verify_c19_focus_campaign.py" in text
        results.append(("handoff_references_c19", ok, f"{len(text)} bytes"))
    else:
        results.append(("handoff_references_c19", False, "missing HANDOFF.md"))

    ok_all = all(v[1] for v in results)
    print()
    if ok_all:
        print("C19 ACCEPTANCE: PASS — spec adjudication + native verdict + consolidated final complete")
        return 0
    failed = [v[0] for v in results if not v[1]]
    print(f"C19 ACCEPTANCE: FAIL — {len(failed)} requirement(s) missing: {', '.join(failed)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())