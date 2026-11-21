#!/usr/bin/env python3
"""C29 acceptance gate — the no-avoidance check for the next focus campaign.

Prints exactly one authoritative line:
  C29 ACCEPTANCE: PASS     -> prereg + all direction/arm/venue/fold cells +
                               full inference floors + fidelity anchor +
                               consolidated verdict, all consistent
  C29 ACCEPTANCE: PENDING  -> prerequisites OK, heavy battery incomplete (lists what is missing)
  C29 ACCEPTANCE: FAIL     -> prereg missing/drift, signal-path/execution drift,
                               anchor mismatch, draw-floor violation, smoke artifacts,
                               or invalid verdict token

PENDING is NOT done: per the handoff no-avoidance rule, PENDING means the session
must execute the heavy C29 battery until this gate prints PASS. C29 is blocked on
C28 ACCEPTANCE: PASS; C28 on C27; C27 on C26; C26 on C25; C25 IN FLIGHT.

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
TS = "20261121T031907Z"

FOLDS = ["2023", "2024", "2025", "2026YTD"]
VENUES = ["okx", "binance_um", "mexc", "bitget"]
DIRECTIONS = ["c29-a"]
VALID_VERDICTS = {"C29_REOPENS_C1_C28", "C29_NO_GO_ROBUST_TO_HOLDOUT"}
DRAW_FLOORS = {
    "episode_block_bootstrap_draws": 20000,
    "permutation_draws": 20000,
    "placebo_portfolio_runs": 2000,
    "strata_permutation_draws": 2000,
}

# Frozen signal path = C24/C25/C26 sentinel (drift-checked).
FROZEN_SIGNAL_PATH = {
    "use_rsi_trigger": True,
    "rsi_period": 21,
    "rsi_threshold": 20.0,
    "target_pct": 9.0,
    "rebound_short_target_pct": 9.0,
    "rebound_short_time_exit_bars": 48,
    "rebound_short_stop_pct": 40.0,
    "enable_rebound_short": True,
    "enable_eth_hedge": True,
    "enable_volume_based_sizing": True,
    "position_size_pct_of_daily_volume": 1.25,
    "min_daily_volume_usd": 5000000.0,
    "gross_cap_pct": 120.0,
    "entry_spec_literal_next_open": True,
    "seed": 20261201,
    "time_exit_max_bars": 50,
    "liquidation_maint_margin_pct": 14.0,
    "liquidation_buffer_pct": 1.0,
    "liquidation_distance_pct": 15.0,
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="C29 acceptance gate")
    ap.add_argument("--direction", required=True, choices=DIRECTIONS,
                    help="C29 direction to verify (c29-a)")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)

    direction = args.direction
    fail: List[str] = []
    pending: List[str] = []

    # ---- prereg --------------------------------------------------------------
    prereg_path = STATE / f"c29_prereg_{TS}.json"
    if not prereg_path.exists():
        print("C29 ACCEPTANCE: FAIL")
        print("missing prereg", prereg_path.name)
        return 1
    prereg = _load(prereg_path)
    if prereg.get("prereg_status") != "PRE_REGISTERED_BEFORE_COMPUTE":
        fail.append("prereg status is not PRE_REGISTERED_BEFORE_COMPUTE")
    if prereg.get("direction") != direction:
        fail.append(f"prereg direction {prereg.get('direction')} != requested {direction}")
    prereg_sha = _sha(prereg_path)

    arms_cfg = prereg.get("arms", {})
    if not arms_cfg:
        fail.append(f"no arms registered for direction {direction} in prereg")
    arms = list(arms_cfg.keys())
    fidelity_arm = next((a for a, c in arms_cfg.items() if c.get("role") == "FIDELITY_ANCHOR"), None)
    primary_arm = next((a for a, c in arms_cfg.items() if c.get("role") == "PRIMARY"), None)

    # C29 is blocked on C28 completion (anchor reference must exist).
    c28_passed = (STATE / f"c28_decision_verdict_CONSOLIDATED_20261121T013400Z.json").exists()
    if not c28_passed:
        pending.append("C28 ACCEPTANCE: not yet PASS; no C29 cell may run until C28 completes "
                       "(C28 -> C27 -> C26 -> C25 chain; C25 IN FLIGHT)")

    # ---- checkpoints ---------------------------------------------------------
    missing_cells: List[str] = []
    anchor_totals: Dict[str, float] = {v: 0.0 for v in VENUES}
    anchor_ok = False
    anchor_ref: Dict[str, float] = {}
    ref_path = STATE / "c28_decision_verdict_CONSOLIDATED_20261121T013400Z.json"
    if ref_path.exists():
        try:
            anchor_ref = _load(ref_path).get("venue_totals") or {}
        except Exception:  # noqa: BLE001
            anchor_ref = {}
    if not anchor_ref:
        pending.append("anchor reference (C28 primary-arm venue_totals) not available until C28 PASS")

    for arm in arms:
        for v in VENUES:
            for f in FOLDS:
                p = STATE / f"c29_ckpt_{direction}_{arm}_{v}_{f}_{TS}.json"
                if not p.exists():
                    missing_cells.append(f"{direction}/{arm}/{v}/{f}")
                    continue
                ck = _load(p)
                if ck.get("prereg_sha256") != prereg_sha:
                    fail.append(f"prereg sha drift in {p.name}")
                if ck.get("unavailable_funding"):
                    continue
                cfg = (ck.get("campaign_artifact") or {}).get("config") or {}
                for k, want in FROZEN_SIGNAL_PATH.items():
                    got = cfg.get(k)
                    if isinstance(want, float):
                        ok = got is not None and abs(float(got) - want) <= 1e-9
                    else:
                        ok = got == want
                    if not ok:
                        fail.append(f"signal-path drift {p.name}: {k}={got} != {want}")
                if arm == fidelity_arm:
                    anchor_totals[v] += float(
                        (ck.get("campaign_artifact") or {}).get("results", {}).get("total_pnl", 0.0))
    if missing_cells:
        pending.append(f"{len(missing_cells)} missing (direction, arm, venue, fold) cells; first: "
                       f"{missing_cells[:6]}")

    # ---- fidelity anchor (fidelity arm reproduces C28 primary within +/-1.0) --
    if anchor_ref and fidelity_arm:
        anchor_ok = all(abs(anchor_totals.get(v, 0.0) - float(anchor_ref.get(v, 0.0))) <= 1.0
                        for v in VENUES)
        if not anchor_ok:
            fail.append(f"fidelity anchor mismatch for {fidelity_arm}: "
                        f"{ {v: round(anchor_totals.get(v, 0.0), 2) for v in VENUES} } "
                        f"vs { {v: round(float(anchor_ref.get(v, 0.0)), 2) for v in VENUES} }")
    elif fidelity_arm:
        pending.append("fidelity anchor cannot be checked until C28 primary-arm venue_totals exist")

    # ---- inference floors ----------------------------------------------------
    if primary_arm and not any(c.startswith(f"{direction}/{primary_arm}/") for c in missing_cells):
        for v in VENUES:
            for f in FOLDS:
                cp = STATE / f"c29_ckpt_{direction}_{primary_arm}_{v}_{f}_{TS}.json"
                if not cp.exists() or _load(cp).get("unavailable_funding"):
                    continue
                ck = _load(cp)
                ep = ck.get("episode") or {}
                pl = ck.get("placebo") or {}
                boot = (ep.get("episode_block_bootstrap") or {}).get("resamples")
                perm = (ep.get("temporal_edge_permutation") or {}).get("draws_evaluated")
                runs = (pl.get("placebo") or {}).get("runs")
                if not boot or int(boot) < DRAW_FLOORS["episode_block_bootstrap_draws"]:
                    fail.append(f"{primary_arm} {v} {f}: episode bootstrap draws {boot} < 20000")
                if not perm or int(perm) < DRAW_FLOORS["permutation_draws"]:
                    fail.append(f"{primary_arm} {v} {f}: permutation draws {perm} < 20000")
                if not runs or int(runs) < DRAW_FLOORS["placebo_portfolio_runs"]:
                    fail.append(f"{primary_arm} {v} {f}: placebo runs {runs} < 2000")

    # ---- smoke contamination -------------------------------------------------
    if list(STATE.glob(f"c29_*_{TS}_SMOKE.json")):
        fail.append("SMOKE artifacts present in research_state; remove them and rerun full")

    # ---- arm verdicts + consolidated -----------------------------------------
    for arm in arms:
        p = STATE / f"c29_decision_verdict_{arm}_{TS}.json"
        if not p.exists():
            missing_cells.append(f"verdict:{arm}")
    consolidated_path = STATE / f"c29_decision_verdict_CONSOLIDATED_{TS}.json"
    if not consolidated_path.exists():
        missing_cells.append("verdict:CONSOLIDATED")
    if missing_cells:
        pending.append("missing verdict artifacts (written only after all cells complete)")
    else:
        consolidated = _load(consolidated_path)
        verdict = consolidated.get("consolidated_verdict")
        if verdict not in VALID_VERDICTS:
            fail.append(f"invalid consolidated verdict token {verdict!r}")
        anchor = _load(STATE / f"c29_decision_verdict_{fidelity_arm}_{TS}.json")
        token_ok = prereg.get("anchor_rule", {}).get("token_ok", "HOLDOUT_ANCHOR_REPRODUCED")
        if anchor.get("token") != token_ok:
            fail.append(f"fidelity arm token {anchor.get('token')!r} != {token_ok}")

    if fail:
        print("C29 ACCEPTANCE: FAIL")
        for x in fail:
            print("  FAIL:", x)
        return 1
    if pending:
        print("C29 ACCEPTANCE: PENDING")
        for x in pending:
            print("  PENDING:", x)
        print("  next: PYTHONPATH=. .venv/bin/python "
              f"scripts/run_c29_campaign.py --direction {direction} --jobs 4 --resume")
        return 0

    print("C29 ACCEPTANCE: PASS")
    consolidated = _load(STATE / f"c29_decision_verdict_CONSOLIDATED_{TS}.json")
    print(f"  consolidated={consolidated.get('consolidated_verdict')}")
    print(f"  arm_pooled_totals={consolidated.get('arm_pooled_totals')}")
    print(f"  prereg_sha256={prereg_sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
