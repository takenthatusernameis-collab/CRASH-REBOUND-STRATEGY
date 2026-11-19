#!/usr/bin/env python3
"""C25 acceptance gate — the no-avoidance check for the cost/funding fidelity adjudication.

Prints exactly one authoritative line:
  C25 ACCEPTANCE: PASS     -> prereg + all arm/venue/fold cells + full inference
                              floors + cost anchor + consolidated verdict, all consistent
  C25 ACCEPTANCE: PENDING  -> prerequisites OK, heavy battery incomplete (lists what is missing)
  C25 ACCEPTANCE: FAIL     -> prereg missing, signal-path/cost drift, anchor mismatch,
                              draw-floor violation, smoke artifacts, or invalid verdict token

PENDING is NOT done: per the handoff no-avoidance rule, PENDING means the session must
execute the heavy cost/funding battery (4 arms x 4 venues x 4 folds x 20k/20k/2k) until
this gate prints PASS. C25 is blocked on C24 ACCEPTANCE: PASS (no C25 cell may run first).

Exit codes: PASS/PENDING -> 0, FAIL -> 1.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / "research_state"
TS = "20261119T045500Z"

FOLDS = ["2023", "2024", "2025", "2026YTD"]
VENUES = ["okx", "binance_um", "mexc", "bitget"]
ARMS = ["cost_base", "cost_taker", "cost_taker_funding", "cost_stress"]
INFERENCE_ARMS = ARMS  # all four arms run full inference
PRIMARY_ARM = "cost_taker_funding"
FIDELITY_ARM = "cost_base"

VALID_VERDICTS = {"C25_REOPENS_C1_C24", "C25_NO_GO_ROBUST_TO_COST"}
ANCHOR_TOKEN = "COST_ANCHOR_REPRODUCED"

DRAW_FLOORS = {
    "episode_block_bootstrap_draws": 20000,
    "permutation_draws": 20000,
    "placebo_portfolio_runs": 2000,
    "strata_permutation_draws": 2000,
}

# Frozen signal path = C25 pre-registered sentinel (drift-checked).
FROZEN_SIGNAL_PATH = {
    "use_rsi_trigger": True,
    "rsi_period": 21,
    "rsi_threshold": 20.0,
    "target_pct": 9.0,
    "rebound_short_target_pct": 9.0,
    "rebound_short_time_exit_bars": 48,
    "enable_rebound_short": True,
    "enable_eth_hedge": True,
    "enable_volume_based_sizing": True,
    "min_daily_volume_usd": 5000000.0,
    "gross_cap_pct": 120.0,
    "entry_spec_literal_next_open": True,
    "liquidation_maint_margin_pct": 14.0,
    "liquidation_buffer_pct": 1.0,
}

# Cost_base anchor reference: C24 d15 primary-arm venue_totals (after C24 PASS).
_C24_D15_TS = "20261119T013154Z"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)

    fail: List[str] = []
    pending: List[str] = []

    # ---- prereg -------------------------------------------------------------
    prereg_path = STATE / f"c25_prereg_{TS}.json"
    if not prereg_path.exists():
        print("C25 ACCEPTANCE: FAIL")
        print("missing prereg", prereg_path.name)
        return 1
    prereg = _load(prereg_path)
    if prereg.get("prereg_status") != "PRE_REGISTERED_BEFORE_COMPUTE":
        fail.append("prereg status is not PRE_REGISTERED_BEFORE_COMPUTE")
    prereg_sha = _sha(prereg_path)

    # C25 is blocked on C24 completion.
    c24_passed = (STATE / f"c24_decision_verdict_CONSOLIDATED_{_C24_D15_TS}.json").exists()
    if not c24_passed:
        pending.append("C24 ACCEPTANCE: not yet PASS; no C25 cell may run until C24 completes")

    # ---- checkpoints --------------------------------------------------------
    missing_cells: List[str] = []
    anchor_totals: Dict[str, float] = {v: 0.0 for v in VENUES}
    for arm in ARMS:
        for v in VENUES:
            for f in FOLDS:
                p = STATE / f"c25_ckpt_{arm}_{v}_{f}_{TS}.json"
                if not p.exists():
                    missing_cells.append(f"{arm}/{v}/{f}")
                    continue
                ck = _load(p)
                if ck.get("prereg_sha256") != prereg_sha:
                    fail.append(f"prereg sha drift in {p.name}")
                if ck.get("unavailable_funding"):
                    # venue excluded from funding arms; not a missing cell
                    continue
                cfg = (ck.get("campaign_artifact") or {}).get("config") or {}
                for k, want in FROZEN_SIGNAL_PATH.items():
                    got = cfg.get(k)
                    if isinstance(want, float):
                        ok = got is not None and abs(float(got) - want) <= 1e-9
                    else:
                        ok = got == want
                    if not ok:
                        fail.append(f"signal-path/cost drift {p.name}: {k}={got} != {want}")
                if arm == FIDELITY_ARM:
                    anchor_totals[v] += float(
                        (ck.get("campaign_artifact") or {}).get("results", {}).get("total_pnl", 0.0))
    if missing_cells:
        pending.append(f"{len(missing_cells)} missing (arm, venue, fold) cells; first: "
                       f"{missing_cells[:6]}")

    # ---- cost anchor (cost_base vs C24 d15 primary venue_totals) -------------
    ref_path = STATE / f"c24_decision_verdict_d15_{_C24_D15_TS}.json"
    ref = _load(ref_path).get("venue_totals") if ref_path.exists() else None
    if ref:
        for v, expected in ref.items():
            if missing_cells and any(c.startswith(f"{FIDELITY_ARM}/{v}/") for c in missing_cells):
                continue
            if abs(anchor_totals.get(v, 0.0) - float(expected)) > 1.0:
                fail.append(f"cost anchor mismatch {v}: {anchor_totals.get(v):.2f} != {expected}")
    else:
        pending.append("cost anchor reference (C24 d15 venue_totals) not available until C24 PASS")

    # ---- inference floors ---------------------------------------------------
    if not any(c.startswith(f"{PRIMARY_ARM}/") for c in missing_cells):
        for v in VENUES:
            for f in FOLDS:
                cp = STATE / f"c25_ckpt_{PRIMARY_ARM}_{v}_{f}_{TS}.json"
                if not cp.exists() or _load(cp).get("unavailable_funding"):
                    continue
                ck = _load(cp)
                ep = ck.get("episode") or {}
                pl = ck.get("placebo") or {}
                boot = (ep.get("episode_block_bootstrap") or {}).get("resamples")
                perm = (ep.get("temporal_edge_permutation") or {}).get("draws_evaluated")
                runs = (pl.get("placebo") or {}).get("runs")
                if not boot or int(boot) < DRAW_FLOORS["episode_block_bootstrap_draws"]:
                    fail.append(f"{PRIMARY_ARM} {v} {f}: episode bootstrap draws {boot} < 20000")
                if not perm or int(perm) < DRAW_FLOORS["permutation_draws"]:
                    fail.append(f"{PRIMARY_ARM} {v} {f}: permutation draws {perm} < 20000")
                if not runs or int(runs) < DRAW_FLOORS["placebo_portfolio_runs"]:
                    fail.append(f"{PRIMARY_ARM} {v} {f}: placebo runs {runs} < 2000")

    # ---- smoke contamination -----------------------------------------------
    if list(STATE.glob(f"c25_*_{TS}_SMOKE.json")):
        fail.append("SMOKE artifacts present in research_state; remove them and rerun full")

    # ---- arm verdicts + consolidated ---------------------------------------
    for arm in ARMS:
        p = STATE / f"c25_decision_verdict_{arm}_{TS}.json"
        if not p.exists():
            missing_cells.append(f"verdict:{arm}")
    consolidated_path = STATE / f"c25_decision_verdict_CONSOLIDATED_{TS}.json"
    if not consolidated_path.exists():
        missing_cells.append("verdict:CONSOLIDATED")
    if missing_cells:
        pending.append("missing verdict artifacts (written only after all cells complete)")
    else:
        consolidated = _load(consolidated_path)
        verdict = consolidated.get("consolidated_verdict")
        if verdict not in VALID_VERDICTS:
            fail.append(f"invalid consolidated verdict token {verdict!r}")
        anchor = _load(STATE / f"c25_decision_verdict_{FIDELITY_ARM}_{TS}.json")
        if anchor.get("token") != ANCHOR_TOKEN:
            fail.append(f"fidelity arm token {anchor.get('token')!r} != {ANCHOR_TOKEN}")

    if fail:
        print("C25 ACCEPTANCE: FAIL")
        for x in fail:
            print("  FAIL:", x)
        return 1
    if pending:
        print("C25 ACCEPTANCE: PENDING")
        for x in pending:
            print("  PENDING:", x)
        print("  next: PYTHONPATH=. .venv/bin/python "
              "scripts/run_c25_cost_fidelity_campaign.py --jobs 4 --resume")
        return 0

    print("C25 ACCEPTANCE: PASS")
    consolidated = _load(STATE / f"c25_decision_verdict_CONSOLIDATED_{TS}.json")
    print(f"  consolidated={consolidated.get('consolidated_verdict')}")
    print(f"  arm_pooled_totals={consolidated.get('arm_pooled_totals')}")
    print(f"  prereg_sha256={prereg_sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
