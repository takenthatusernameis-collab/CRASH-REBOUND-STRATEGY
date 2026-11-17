#!/usr/bin/env python3
"""C21 acceptance gate — cross-venue temporal walk-forward & regime-stability.

C21 is the binding next focus campaign. C1-C20 closed with a pooled NO_GO on the
UNCONDITIONAL spec-literal next-open edge. C21 asks a pre-registered follow-up: is
that NO_GO stable across time and crash regimes, or does a pre-specified fold or
stratum survive multiplicity control with a positive spot leg and cross-venue
concordance? C21 is executable on already-verified OKX + Binance UM archives;
acquisition stays CLOSED (Hyperliquid moving tail exhausted).

This gate is fail-closed and RED until C21 is actually executed. It refuses to pass
on planning-only turns, a prereg-only turn, a single-venue half, a missing per-venue
fold battery, a missing pooled synthesis, a consolidated final that predates the
C21 prereg, or a handoff that does not point at this campaign.

Accepted C21 terminal states:
  (A) STABLE_POSITIVE_SUBSET — full C21 artifact set produced, BH-corrected stratum
      survives with cross-venue concordance, honest pooled + per-venue numbers.
  (B) NO_GO — full C21 artifact set produced and an honest pooled NO_GO issued.
  (C) UNDERPOWERED — full C21 artifact set produced with a quantified power curve.
A bare "prereg only" or "OKX folds only" is NOT an accepted C21 terminal state.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / "research_state"
HANDOFF = REPO / "HANDOFF.md"

TS = "20261117T064408Z"  # C21 prereg timestamp; fixed before any C21 compute

VALID_VERDICTS = {"STABLE_POSITIVE_SUBSET", "NO_GO", "UNDERPOWERED"}

REQUIRED_ARTIFACTS = [
    "okx_fold_campaign",
    "binance_fold_campaign",
    "okx_fold_episode_edge",
    "binance_fold_episode_edge",
    "okx_fold_placebo",
    "binance_fold_placebo",
    "okx_fold_census",
    "binance_fold_census",
    "okx_verdict",
    "binance_verdict",
    "pooled_synthesis",
    "consolidated_final",
]

ARTIFACT_STEMS: Dict[str, str] = {
    "okx_fold_campaign": f"c21_okx_fold_campaign_{TS}",
    "binance_fold_campaign": f"c21_binance_um_fold_campaign_{TS}",
    "okx_fold_episode_edge": f"c21_okx_fold_episode_edge_{TS}",
    "binance_fold_episode_edge": f"c21_binance_um_fold_episode_edge_{TS}",
    "okx_fold_placebo": f"c21_okx_fold_placebo_{TS}",
    "binance_fold_placebo": f"c21_binance_um_fold_placebo_{TS}",
    "okx_fold_census": f"c21_okx_fold_census_{TS}",
    "binance_fold_census": f"c21_binance_um_fold_census_{TS}",
    "okx_verdict": f"c21_decision_verdict_okx_stability_{TS}",
    "binance_verdict": f"c21_decision_verdict_binance_um_stability_{TS}",
    "pooled_synthesis": f"c21_pooled_stability_synthesis_{TS}",
    "consolidated_final": f"c21_decision_verdict_CONSOLIDATED_{TS}",
}

PREREG_PATH = STATE / f"c21_prereg_{TS}.json"
C20_FINAL = STATE / "decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json"


def _load(path: Path) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        return json.loads(path.read_text()), None
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def _ts_of(data: Optional[Dict[str, Any]]) -> str:
    return str((data or {}).get("generated_at_utc") or "")


def _check(label: str, ok: bool, detail: str = "") -> bool:
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f": {detail}" if detail else ""))
    return ok


def main() -> int:
    results: List[Tuple[str, bool, str]] = []

    # 1. Prereg exists, is C21, pre-registered before compute, config fixed.
    prereg: Optional[Dict[str, Any]] = None
    if not PREREG_PATH.exists():
        results.append(("c21_prereg", False, f"missing {PREREG_PATH.name}"))
    else:
        prereg, err = _load(PREREG_PATH)
        ok = (
            prereg is not None
            and prereg.get("campaign") == "C21"
            and prereg.get("status") == "PRE_REGISTERED_BEFORE_COMPUTE"
            and prereg.get("real_market_data") is True
            and prereg.get("fabricated_data") is False
            and prereg.get("synthetic_data") is False
            and prereg.get("cross_venue") is True
            and prereg.get("is_hyperliquid_venue_data") is False
            and prereg.get("hypothesis", {}).get("config", {}).get("entry_spec_literal_next_open") is True
        )
        results.append(("c21_prereg", bool(ok), PREREG_PATH.name + (f" ({err})" if err else "")))
    prereg_ts = _ts_of(prereg)

    # 2. Every required C21 artifact exists on disk (resume-safe stems).
    missing: List[str] = []
    present: List[str] = []
    artifacts: Dict[str, Optional[Dict[str, Any]]] = {}
    for key in REQUIRED_ARTIFACTS:
        p = STATE / f"{ARTIFACT_STEMS[key]}.json"
        if p.exists():
            data, _ = _load(p)
            artifacts[key] = data
            present.append(p.name)
        else:
            artifacts[key] = None
            missing.append(p.name)
    results.append((
        "c21_artifacts_present",
        len(missing) == 0,
        f"{len(present)}/{len(REQUIRED_ARTIFACTS)} present" +
        (f"; missing: {', '.join(missing)}" if missing else ""),
    ))

    # 3. Both per-venue fold campaigns computed (real, cross-venue, not Hyperliquid).
    for venue, key in (("OKX", "okx_fold_campaign"), ("Binance UM", "binance_fold_campaign")):
        c = artifacts[key]
        c_ok = (
            c is not None
            and c.get("campaign") == "C21"
            and c.get("real_market_data") is True
            and c.get("performance_evidence") is True
            and c.get("is_hyperliquid_venue_data") is False
            and c.get("cross_venue") is True
            and c.get("fabricated_data") is False
            and c.get("synthetic_data") is False
            and bool(c.get("prereg_sha256"))
            and (c.get("results") or {}).get("num_trades") is not None
        )
        detail = ARTIFACT_STEMS[key] + ".json"
        if c is not None:
            detail += f"; trades={c.get('results', {}).get('num_trades')} pnl={c.get('results', {}).get('total_pnl')}"
        results.append((f"{venue.lower().replace(' ', '_')}_fold_campaign_computed", bool(c_ok), detail))

    # 4. Both per-venue fold episode edges computed (dependence-aware, seeded).
    for venue, key in (("OKX", "okx_fold_episode_edge"), ("Binance UM", "binance_fold_episode_edge")):
        e = artifacts[key]
        e_ok = (
            e is not None
            and e.get("campaign") == "C21"
            and e.get("entry_rule") == "SPEC_LITERAL_NEXT_OPEN"
            and e.get("is_hyperliquid_venue_data") is False
            and e.get("cross_venue") is True
            and bool(e.get("seed"))
            and bool(e.get("episode_block_bootstrap"))
        )
        results.append((f"{venue.lower().replace(' ', '_')}_fold_episode_edge_computed", bool(e_ok), ARTIFACT_STEMS[key] + ".json"))

    # 5. Both per-venue fold placebos computed.
    for venue, key in (("OKX", "okx_fold_placebo"), ("Binance UM", "binance_fold_placebo")):
        pl = artifacts[key]
        pl_ok = (
            pl is not None
            and pl.get("campaign") == "C21"
            and pl.get("entry_rule") == "SPEC_LITERAL_NEXT_OPEN"
            and pl.get("is_hyperliquid_venue_data") is False
            and pl.get("cross_venue") is True
            and bool(pl.get("placebo"))
        )
        results.append((f"{venue.lower().replace(' ', '_')}_fold_placebo_computed", bool(pl_ok), ARTIFACT_STEMS[key] + ".json"))

    # 6. Both per-venue fold censuses computed.
    for venue, key in (("OKX", "okx_fold_census"), ("Binance UM", "binance_fold_census")):
        c = artifacts[key]
        c_ok = (
            c is not None
            and c.get("campaign") == "C21"
            and c.get("entry_rule") == "SPEC_LITERAL_NEXT_OPEN"
            and c.get("is_hyperliquid_venue_data") is False
            and c.get("cross_venue") is True
        )
        results.append((f"{venue.lower().replace(' ', '_')}_fold_census_computed", bool(c_ok), ARTIFACT_STEMS[key] + ".json"))

    # 7. Both per-venue verdicts computed with an explicit token.
    for venue, key in (("OKX", "okx_verdict"), ("Binance UM", "binance_verdict")):
        v = artifacts[key]
        v_ok = (
            v is not None
            and v.get("campaign") == "C21"
            and v.get("verdict") in VALID_VERDICTS
            and v.get("is_hyperliquid_venue_data") is False
            and v.get("cross_venue") is True
            and bool(v.get("prereg_sha256"))
        )
        results.append((f"{venue.lower().replace(' ', '_')}_verdict_computed", bool(v_ok),
                        ARTIFACT_STEMS[key] + ".json" + (f"; token={v.get('verdict')}" if v else "")))

    # 8. Pooled stability synthesis computed with venue-blocked bootstrap + token.
    pooled = artifacts["pooled_synthesis"]
    pooled_ok = (
        pooled is not None
        and pooled.get("campaign") == "C21"
        and pooled.get("is_hyperliquid_venue_data") is False
        and pooled.get("cross_venue") is True
        and bool(pooled.get("pooled_venue_blocked_bootstrap"))
        and (pooled.get("decision", {}).get("token") in VALID_VERDICTS)
        and bool(pooled.get("multiplicity"))
    )
    results.append(("c21_pooled_synthesis_computed", bool(pooled_ok),
                    ARTIFACT_STEMS["pooled_synthesis"] + ".json" +
                    (f"; token={pooled.get('decision', {}).get('token')}" if pooled else "")))

    # 9. Consolidated final C21: postdates prereg, supersedes C20 final, scope C21.
    cf = artifacts["consolidated_final"]
    cf_ok = False
    cf_detail = ARTIFACT_STEMS["consolidated_final"] + ".json"
    if cf is not None:
        token = cf.get("final_verdict_token") or cf.get("verdict")
        cf_ok = (
            token in VALID_VERDICTS
            and bool(prereg_ts)
            and _ts_of(cf) > prereg_ts
            and bool(cf.get("supersedes"))
            and str(cf.get("supersedes")).find("20261116T063500Z") >= 0
            and "C21" in str(cf.get("scope", ""))
        )
        cf_detail += f"; final={token}; ts={_ts_of(cf)}; supersedes={cf.get('supersedes')}; scope={cf.get('scope')}"
    results.append(("c21_consolidated_final_computed", bool(cf_ok), cf_detail))

    # 10. Handoff references C21 and this gate.
    if HANDOFF.exists() and HANDOFF.is_file() and HANDOFF.read_text():
        text = HANDOFF.read_text()
        handoff_ok = ("C21-T1" in text or "C21" in text) and "verify_c21_focus_campaign.py" in text
        results.append(("handoff_references_c21", bool(handoff_ok), f"{len(text)} bytes"))
    else:
        results.append(("handoff_references_c21", False, "missing HANDOFF.md"))

    for label, ok, detail in results:
        _check(label, ok, detail)

    ok_all = all(v[1] for v in results)
    print()
    if ok_all:
        token = (pooled or {}).get("decision", {}).get("token", "?")
        print(f"C21 ACCEPTANCE: PASS — full cross-venue temporal-stability campaign complete (pooled={token})")
        return 0
    failed = [v[0] for v in results if not v[1]]
    print(f"C21 ACCEPTANCE: FAIL — {len(failed)} requirement(s) missing: {', '.join(failed)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())