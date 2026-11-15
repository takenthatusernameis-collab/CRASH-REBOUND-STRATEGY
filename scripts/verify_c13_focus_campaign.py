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

MIN_DRAWS = 100
MIN_EFFECTIVE_TRADES = 10
MIN_EPISODES = 5
LEAD_CAMPAIGN = STATE / "campaign_results_real_hyperliquid_native_c12_rsi25_t9_20261115T180000Z.json"
LEAD_CENSUS = STATE / "crash_event_census_hyperliquid_native_c12_rsi25_t9_20261115T180000Z.json"


def _sha256(path: Path) -> Optional[str]:
    try:
        import hashlib
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _as_int(value: Any) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _prereg_seed(prereg: Optional[Dict[str, Any]]) -> Optional[int]:
    if not prereg:
        return None
    plan = prereg.get("inference_plan") or {}
    return _as_int(plan.get("seed", prereg.get("seed")))


def _prereg_min_draws(prereg: Optional[Dict[str, Any]]) -> Optional[int]:
    if not prereg:
        return None
    plan = prereg.get("inference_plan") or {}
    return _as_int(plan.get("min_draws", prereg.get("min_draws")))


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
    plan = data.get("inference_plan") or {}
    if _prereg_seed(data) is None:
        problems.append("prereg must pre-register inference_plan.seed")
    min_draws = _prereg_min_draws(data)
    if min_draws is None or min_draws < MIN_DRAWS:
        problems.append(f"prereg must state inference_plan.min_draws >= {MIN_DRAWS} (heavy-compute floor)")
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
    if "node-derived" not in caveat or "candlesnapshot" not in caveat:
        return False
    venue = str(data.get("venue_label", "")).lower()
    if data.get("is_hyperliquid_evidence") is not True and "hyperliquid" not in venue:
        return False
    if data.get("fabricated_data") is True or data.get("synthetic_data") is True:
        return False
    return True


def check_inference(prereg: Optional[Dict[str, Any]],
                    prereg_ts: Optional[dt.datetime]) -> Tuple[bool, str, Dict[str, Path]]:
    """Require BOTH config-matched inference artifacts at decision-grade compute.

    Artifacts are bound to the prereg by seed and to the C12 lead by the
    campaign/census SHA256 recorded by the runners. Among eligible artifacts the
    one with the most compute is selected, then it must clear the heavy-compute
    floors; a stale thin artifact can neither shadow nor substitute for real work.
    """
    problems: List[str] = []
    prereg_seed = _prereg_seed(prereg)
    expected_campaign = _sha256(LEAD_CAMPAIGN)
    expected_census = _sha256(LEAD_CENSUS)
    episode_candidates: List[Tuple[int, Path, Dict[str, Any]]] = []
    placebo_candidates: List[Tuple[int, Path, Dict[str, Any]]] = []

    for path in sorted(STATE.glob("*.json")):
        data = _load_json(path)
        if not isinstance(data, dict) or not _is_config_matched_inference(data):
            continue
        gen = _parse_ts(data.get("generated_at_utc", ""))
        if prereg_ts is not None and (gen is None or gen < prereg_ts):
            continue
        if prereg_seed is not None and _as_int(data.get("seed")) != prereg_seed:
            continue
        inputs = data.get("inputs") or {}
        if expected_campaign and str(inputs.get("campaign_sha256") or "") != expected_campaign:
            continue
        if expected_census and str(inputs.get("census_sha256") or "") != expected_census:
            continue
        if "temporal_edge_permutation" in data:
            compute = _as_int((data.get("temporal_edge_permutation") or {}).get("draws_evaluated")) or 0
            episode_candidates.append((compute, path, data))
        if isinstance(data.get("placebo"), dict) and (data.get("canonical") or {}).get("trades"):
            compute = _as_int((data.get("placebo") or {}).get("runs")) or 0
            placebo_candidates.append((compute, path, data))

    artifacts: Dict[str, Path] = {}
    if not episode_candidates:
        problems.append(
            "no config-matched episode-edge artifact (rsi25/t9, seed/sha-bound, generated after prereg)"
        )
    else:
        compute, path, data = max(episode_candidates, key=lambda item: item[0])
        artifacts["episode_edge"] = path
        if compute < MIN_DRAWS:
            problems.append(
                f"episode-edge {path.name} evaluated only {compute} permutation draws; need >= {MIN_DRAWS}"
            )
        eff = (data.get("episode_audit") or {}).get("effective_independent_sample") or {}
        trades = _as_int(eff.get("trades")) or 0
        episodes = _as_int(eff.get("episodes")) or 0
        if trades < MIN_EFFECTIVE_TRADES:
            problems.append(
                f"episode-edge {path.name} effective trades={trades}; need >= {MIN_EFFECTIVE_TRADES}"
            )
        if episodes < MIN_EPISODES:
            problems.append(
                f"episode-edge {path.name} episodes={episodes}; need >= {MIN_EPISODES}"
            )

    if not placebo_candidates:
        problems.append(
            "no config-matched portfolio-placebo artifact (rsi25/t9, seed/sha-bound, generated after prereg)"
        )
    else:
        compute, path, _data = max(placebo_candidates, key=lambda item: item[0])
        artifacts["placebo"] = path
        if compute < MIN_DRAWS:
            problems.append(
                f"placebo {path.name} evaluated only {compute} subsets; need >= {MIN_DRAWS}"
            )

    if problems:
        return False, "; ".join(problems), artifacts
    ep = artifacts["episode_edge"]
    pl = artifacts["placebo"]
    ep_draws = _as_int(((_load_json(ep) or {}).get("temporal_edge_permutation") or {}).get("draws_evaluated")) or 0
    pl_runs = _as_int(((_load_json(pl) or {}).get("placebo") or {}).get("runs")) or 0
    return True, f"episode_edge={ep.name} (draws={ep_draws}); placebo={pl.name} (runs={pl_runs})", artifacts


def check_verdict(prereg: Optional[Dict[str, Any]],
                  artifacts: Dict[str, Path]) -> Tuple[bool, str]:
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
    if not re.search(r"(trades|episodes)", text, re.I):
        problems.append("verdict must state the effective sample (trades/episodes)")
    prereg_path = _latest("hyperliquid_native_c13_prereg_*.json")
    prereg_name = prereg_path.name if prereg_path is not None else ""
    if prereg_name and prereg_name not in text and "c13_prereg" not in text:
        problems.append("verdict must reference the C13 prereg artifact (traceability)")
    for key, label in (("episode_edge", "episode-edge"), ("placebo", "placebo")):
        path = artifacts.get(key)
        if path is not None and path.name not in text:
            problems.append(f"verdict must reference the {label} artifact {path.name}")
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

    ok, detail, artifacts = check_inference(prereg, prereg_ts)
    _check("c13_config_matched_inference", ok, detail)
    results.append(("c13_config_matched_inference", ok, detail))

    ok, detail = check_verdict(prereg, artifacts)
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