#!/usr/bin/env python3
"""C20 acceptance gate — cross-venue spec-faithful replication & pooled synthesis.

C20 is the binding next focus campaign. C19 adjudicated SPEC_LITERAL_NEXT_OPEN as
the spec-faithful entry rule and the Hyperliquid-native verdict under it is NO_GO.
Every multi-year cross-venue campaign to date used the canonical same-bar reading,
so the spec-faithful rule has never been tested out-of-sample on two independent
real venues. C20 closes that gap on already-verified OKX + Binance UM archives;
acquisition stays closed (full 283-day Hyperliquid window remains blocked by API
retention).

This gate is fail-closed. It refuses to pass on planning-only turns, missing
venue artifacts, a missing per-venue inference battery, a missing pooled
synthesis, a consolidated final that predates the C20 prereg, or a handoff that
does not point at this campaign.

Accepted terminal states:
  (A) GO          — both venue campaigns + batteries + pooled synthesis +
                    new consolidated final, all green
  (B) UNDERPOWERED / NO_GO — full C20 artifact set produced and an honest
                    consolidated final issued
A bare "prereg only" or "OKX done" is NOT an accepted C20 terminal state: C20
requires both venues end-to-end.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / "research_state"
HANDOFF = REPO / "HANDOFF.md"

TS = "20261116T063500Z"  # C20 prereg timestamp; fixed before any C20 compute

REQUIRED_ARTIFACTS = [
    "c20_prereg",
    "okx_campaign",
    "binance_campaign",
    "okx_census",
    "binance_census",
    "okx_episode_edge",
    "binance_episode_edge",
    "okx_placebo",
    "binance_placebo",
    "okx_battery",
    "binance_battery",
    "okx_verdict",
    "binance_verdict",
    "pooled_synthesis",
    "consolidated_final",
]

ARTIFACT_STEMS: Dict[str, str] = {
    "c20_prereg": f"c20_prereg_{TS}",
    "okx_campaign": f"campaign_results_real_okx_multiyear_specliteral_{TS}",
    "binance_campaign": f"campaign_results_real_binance_um_multiyear_specliteral_{TS}",
    "okx_census": f"crash_event_census_real_okx_multiyear_specliteral_{TS}",
    "binance_census": f"crash_event_census_real_binance_um_multiyear_specliteral_{TS}",
    "okx_episode_edge": f"episode_edge_okx_multiyear_specliteral_{TS}",
    "binance_episode_edge": f"episode_edge_binance_um_multiyear_specliteral_{TS}",
    "okx_placebo": f"placebo_portfolio_okx_multiyear_specliteral_{TS}",
    "binance_placebo": f"placebo_portfolio_binance_um_multiyear_specliteral_{TS}",
    "okx_battery": f"multiyear_robustness_battery_okx_specliteral_{TS}",
    "binance_battery": f"multiyear_robustness_battery_binance_um_specliteral_{TS}",
    "okx_verdict": f"decision_verdict_cross_venue_okx_specliteral_c20_{TS}",
    "binance_verdict": f"decision_verdict_cross_venue_binance_um_specliteral_c20_{TS}",
    "pooled_synthesis": f"c20_pooled_cross_venue_synthesis_{TS}",
    "consolidated_final": f"decision_verdict_CONSOLIDATED_FINAL_{TS}",
}

VALID_VERDICTS = {"GO", "UNDERPOWERED", "NO_GO"}


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

    # 1. Prereg exists, is C20, pre-registered before compute, config fixed.
    prereg_p = STATE / f"c20_prereg_{TS}.json"
    prereg = None
    if not prereg_p.exists():
        results.append(("c20_prereg", False, f"missing c20_prereg_{TS}.json"))
    else:
        prereg, err = _load(prereg_p)
        ok = (
            prereg is not None
            and prereg.get("campaign") == "C20"
            and prereg.get("status") == "PRE_REGISTERED_BEFORE_COMPUTE"
            and prereg.get("real_market_data") is True
            and prereg.get("fabricated_data") is False
            and prereg.get("synthetic_data") is False
            and prereg.get("cross_venue") is True
            and prereg.get("is_hyperliquid_venue_data") is False
            and prereg.get("hypothesis", {}).get("config", {}).get("entry_spec_literal_next_open") is True
        )
        results.append(("c20_prereg", bool(ok), f"{prereg_p.name}" + (f" ({err})" if err else "")))
    prereg_ts = _ts_of(prereg) if prereg else ""

    # 2. Every required C20 artifact exists on disk (resume-safe stems).
    missing: List[str] = []
    present: List[str] = []
    artifacts: Dict[str, Optional[Dict[str, Any]]] = {}
    for key in REQUIRED_ARTIFACTS:
        p = STATE / f"{ARTIFACT_STEMS[key]}.json"
        if p.exists():
            data, err = _load(p)
            artifacts[key] = data
            present.append(p.name)
        else:
            artifacts[key] = None
            missing.append(p.name)
    results.append(
        ("c20_artifacts_present",
         len(missing) == 0,
         f"{len(present)}/{len(REQUIRED_ARTIFACTS)} present" +
         (f"; missing: {', '.join(missing)}" if missing else ""),
    ))

    # 3. OKX campaign already computed: real market, cross-venue, not Hyperliquid.
    okx_camp = artifacts["okx_campaign"]
    okx_ok = (
        okx_camp is not None
        and okx_camp.get("campaign") == "C20"
        and okx_camp.get("real_market_data") is True
        and okx_camp.get("performance_evidence") is True
        and okx_camp.get("is_hyperliquid_venue_data") is False
        and okx_camp.get("cross_venue") is True
        and okx_camp.get("fabricated_data") is False
        and okx_camp.get("synthetic_data") is False
        and bool(okx_camp.get("prereg_sha256"))
    )
    results.append(
        ("okx_campaign_computed", bool(okx_ok),
         f"{ARTIFACT_STEMS['okx_campaign']}.json" +
         (f"; trades={okx_camp.get('results',{}).get('num_trades')} pnl={okx_camp.get('results',{}).get('total_pnl')}" if okx_camp else "")),
    )

    # 4. Binance UM campaign computed (the missing half of C20).
    bn_camp = artifacts["binance_campaign"]
    bn_ok = (
        bn_camp is not None
        and bn_camp.get("campaign") == "C20"
        and bn_camp.get("real_market_data") is True
        and bn_camp.get("is_hyperliquid_venue_data") is False
        and bn_camp.get("cross_venue") is True
        and bool(bn_camp.get("prereg_sha256"))
    )
    results.append(
        ("binance_um_campaign_computed", bool(bn_ok),
         f"{ARTIFACT_STEMS['binance_campaign']}.json" +
         (f"; trades={bn_camp.get('results',{}).get('num_trades')} pnl={bn_camp.get('results',{}).get('total_pnl')}" if bn_camp else "")),
    )

    # 5. Both censuses computed under spec-literal gate.
    for venue, key in (("OKX", "okx_census"), ("Binance UM", "binance_census")):
        c = artifacts[key]
        c_ok = (
            c is not None
            and c.get("campaign") == "C20"
            and c.get("entry_rule") == "SPEC_LITERAL_NEXT_OPEN"
            and c.get("is_hyperliquid_venue_data") is False
            and c.get("cross_venue") is True
        )
        results.append((f"{venue.lower().replace(' ', '_')}_census_computed", bool(c_ok), f"{ARTIFACT_STEMS[key]}.json"))

    # 6. Both episode edges (dependence-aware inference) computed.
    for venue, key in (("OKX", "okx_episode_edge"), ("Binance UM", "binance_episode_edge")):
        e = artifacts[key]
        e_ok = (
            e is not None
            and e.get("campaign") == "C20"
            and e.get("phase") == "C20"
            and e.get("entry_rule") == "SPEC_LITERAL_NEXT_OPEN"
            and e.get("is_hyperliquid_venue_data") is False
            and e.get("cross_venue") is True
            and bool(e.get("seed"))
            and bool(e.get("episode_block_bootstrap"))
        )
        results.append((f"{venue.lower().replace(' ', '_')}_episode_edge_computed", bool(e_ok), f"{ARTIFACT_STEMS[key]}.json"))

    # 7. Both placebos computed.
    for venue, key in (("OKX", "okx_placebo"), ("Binance UM", "binance_placebo")):
        pl = artifacts[key]
        pl_ok = (
            pl is not None
            and pl.get("campaign") == "C20"
            and pl.get("entry_rule") == "SPEC_LITERAL_NEXT_OPEN"
            and pl.get("is_hyperliquid_venue_data") is False
            and pl.get("cross_venue") is True
            and bool(pl.get("placebo"))
        )
        results.append((f"{venue.lower().replace(' ', '_')}_placebo_computed", bool(pl_ok), f"{ARTIFACT_STEMS[key]}.json"))

    # 8. Both robustness batteries computed.
    for venue, key in (("OKX", "okx_battery"), ("Binance UM", "binance_battery")):
        bt = artifacts[key]
        bt_ok = (
            bt is not None
            and bt.get("campaign") == "C20"
            and bt.get("is_hyperliquid_venue_data") is False
            and bt.get("cross_venue") is True
            and bool(bt.get("A"))
        )
        results.append((f"{venue.lower().replace(' ', '_')}_battery_computed", bool(bt_ok), f"{ARTIFACT_STEMS[key]}.json"))

    # 9. Both per-venue verdicts computed with an explicit token.
    for venue, key in (("OKX", "okx_verdict"), ("Binance UM", "binance_verdict")):
        v = artifacts[key]
        v_ok = (
            v is not None
            and v.get("campaign") == "C20"
            and v.get("verdict") in VALID_VERDICTS
            and v.get("is_hyperliquid_venue_data") is False
            and v.get("cross_venue") is True
            and bool(v.get("prereg_sha256"))
        )
        results.append((f"{venue.lower().replace(' ', '_')}_verdict_computed", bool(v_ok),
                        f"{ARTIFACT_STEMS[key]}.json; token={v.get('verdict')}" if v else ""))

    # 10. Pooled venue-blocked synthesis computed.
    pooled = artifacts["pooled_synthesis"]
    pooled_ok = (
        pooled is not None
        and pooled.get("campaign") == "C20"
        and pooled.get("is_hyperliquid_venue_data") is False
        and pooled.get("cross_venue") is True
        and bool(pooled.get("pooled_venue_blocked_bootstrap"))
        and bool(pooled.get("decision", {}).get("token"))
    )
    results.append(("c20_pooled_synthesis_computed", bool(pooled_ok),
                    f"{ARTIFACT_STEMS['pooled_synthesis']}.json; token={pooled.get('decision',{}).get('token')}" if pooled else ""))

    # 11. Consolidated final C1-C20: postdates prereg, references C19 + C20 pooled, supersedes C19 final.
    cf = artifacts["consolidated_final"]
    cf_ok = False
    cf_detail = f"{ARTIFACT_STEMS['consolidated_final']}.json"
    if cf is not None:
        token = cf.get("final_verdict_token") or cf.get("verdict")
        refs = json.dumps(cf.get("priors_referenced") or {}) + " " + json.dumps(cf)
        cf_ok = (
            token in VALID_VERDICTS
            and bool(prereg_ts)
            and _ts_of(cf) > prereg_ts
            and ("C19" in refs or "c19" in refs.lower())
            and ("c20" in refs.lower() or "C20" in refs)
            and bool(cf.get("supersedes"))
            and cf.get("scope") == "C1-C20 final consolidation"
        )
        cf_detail += f"; final={token}; ts={_ts_of(cf)}; supersedes={cf.get('supersedes')}"
    results.append(("c20_consolidated_final_computed", bool(cf_ok), cf_detail))

    # 12. Handoff references C20 and this gate.
    if HANDOFF.exists() and HANDOFF.is_file() and HANDOFF.read_text():
        text = HANDOFF.read_text()
        handoff_ok = ("C20-T1" in text or "C20" in text) and "verify_c20_focus_campaign.py" in text
        results.append(("handoff_references_c20", bool(handoff_ok), f"{len(text)} bytes"))
    else:
        results.append(("handoff_references_c20", False, "missing HANDOFF.md"))

    ok_all = all(v[1] for v in results)
    print()
    if ok_all:
        token = (pooled or {}).get("decision", {}).get("token", "?")
        print(f"C20 ACCEPTANCE: PASS — full cross-venue spec-literal campaign complete "
              f"(pooled={token})")
        return 0
    failed = [v[0] for v in results if not v[1]]
    print(f"C20 ACCEPTANCE: FAIL — {len(failed)} requirement(s) missing: {', '.join(failed)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
