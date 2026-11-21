#!/usr/bin/env python3
"""Build the C31 pre-registration (PRE_REGISTERED_BEFORE_COMPUTE).

C31 is the NEXT FOCUS CAMPAIGN in the `C24 -> C25 -> C26 -> C27 -> C28 -> C29 ->
C30 -> C31+` heavy queue. Per the HANDOFF no-avoidance rule, once C30
ACCEPTANCE: PASS lands, the same session MUST open C31 with a fresh sha-pinned
prereg anchored on the completed C24..C30 primary-arm evidence — and then
durably launch it. C31 is never optional, never "no authorized work", never a
same-data rerun, never a frozen-signal parameter search, never a reduced-draw
run.

Direction c31-a = strict_temporal_oos_holdout: strict temporal out-of-sample
holdout on the newest never-scored real data window (2026-09-29 -> 2026-11-21,
beyond the archived 2023-2026YTD multiyear window). No C1-C30 cell has ever
scored this window. The pooled sign on data no prior cell has touched decides
whether the crash-rebound edge generalizes forward in time. A fresh archive
manifest (`research_state/cache/<venue>_1h_multiyear_20260929_20261121`) must be
acquired before any C31 inference cell runs; until then the campaign is gated on
acquisition, not on inference.

Run (from repo root):
  PYTHONPATH=. .venv/bin/python scripts/build_c31_prereg.py --direction c31-a
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / "research_state"
TS = "20261121T052233Z"

FOLDS = [
    {"id": "2023", "start": "2023-01-01T00:00:00Z", "end": "2023-12-31T23:00:00Z"},
    {"id": "2024", "start": "2024-01-01T00:00:00Z", "end": "2024-12-31T23:00:00Z"},
    {"id": "2025", "start": "2025-01-01T00:00:00Z", "end": "2025-12-31T23:00:00Z"},
    {"id": "2026YTD", "start": "2026-01-01T00:00:00Z", "end": "2026-09-28T23:00:00Z"},
]

HOLDOUT_FOLD = {
    "id": "2026_H2_never_scored",
    "start": "2026-09-29T00:00:00Z",
    "end": "2026-11-21T00:00:00Z",
    "note": "newest never-scored window beyond the archived multiyear window "
    "(2023-2026YTD ends 2026-09-28); requires a fresh archive manifest "
    "<venue>_1h_multiyear_20260929_20261121 before inference",
}

VENUES = ["okx", "binance_um", "mexc", "bitget"]

LIQ_MAINT = 14.0
LIQ_BUFFER = 1.0
LIQ_DISTANCE_PCT = 15.0

SIGNAL_PATH_FROZEN = {
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
    "min_daily_volume_usd": 5_000_000.0,
    "gross_cap_pct": 120.0,
    "entry_spec_literal_next_open": True,
    "seed": 20261201,
    "time_exit_max_bars": 50,
    "liquidation_maint_margin_pct": LIQ_MAINT,
    "liquidation_buffer_pct": LIQ_BUFFER,
    "liquidation_distance_pct": LIQ_DISTANCE_PCT,
    "drift_rule": "Any artifact whose signal_path/cost/execution fields differ "
    "from this prereg are INVALID.",
}

TAKER_BPS = {"okx": 5.0, "binance_um": 4.5, "mexc": 6.0, "bitget": 5.5}
REFERENCE_PX = 60000.0
BORROW_BPS = 5.0

DIRECTIONS: Dict[str, Dict[str, Any]] = {
    "c31-a": {
        "name": "strict_temporal_oos_holdout",
        "title": "C31-A Strict Temporal Out-of-Sample Holdout on the Newest Never-Scored Window",
        "why": "C1-C30 adjudicate margin/liquidation, cost/funding, intrabar-path, "
        "portfolio-level allocation, execution-realism stress and a strict temporal "
        "holdout on the archived multiyear window. C31-A opens the forward-time "
        "holdout frontier: the pooled sign on the newest never-scored real data "
        "window (2026-09-29 -> 2026-11-21), which no C1-C30 cell has ever scored. "
        "This is the best-powered candidate by realized evidence and the honest "
        "test of whether the edge survives out of sample in forward time. No "
        "holdout on data newer than C29's archived window has yet been scored; "
        "C31-A closes that gap so the heavy-work queue never dries out and no "
        "session may claim 'no authorized work'. C31 may NOT launch until C30 "
        "ACCEPTANCE: PASS; C30 on C29; C29 on C28; C28 on C27; C27 on C26; C26 on "
        "C25; C25 IN FLIGHT.",
        "axis": "strict_temporal_oos_holdout",
        "arms": {
            "holdout_base": {
                "role": "FIDELITY_ANCHOR",
                "why": "C30 primary-arm model re-run on the archived multiyear "
                "folds; must reproduce the C30 primary-arm per-venue/per-fold PnL "
                "within +/-1.0 (HOLDOUT_ANCHOR_REPRODUCED). Baseline for the "
                "holdout direction.",
            },
            "holdout_primary": {
                "role": "PRIMARY",
                "why": "Strict temporal OOS holdout on never-scored real data "
                "(the newest window 2026-09-29 -> 2026-11-21 no C1-C30 cell has "
                "scored). Pooled sign and CI95 on the holdout window decide whether "
                "the edge generalizes forward in time. Requires a fresh archive "
                "manifest per venue before any cell infers.",
                "holdout_window": HOLDOUT_FOLD,
            },
        },
    },
}

INFERENCE = {
    "episode_block_bootstrap_draws": 20000,
    "permutation_draws": 20000,
    "placebo_portfolio_runs": 2000,
    "strata_permutation_draws": 2000,
    "pooled": "venue-blocked bootstrap over the venue-fold cell totals (20000 draws)",
    "multiplicity": {
        "method": "benjamini_hochberg",
        "alpha": 0.05,
        "family": "primary arm, 4 folds x 4 venues = 16 permutation tests",
    },
    "draw_floor_rule": "Draws below 20000/20000/2000/2000 => UNDERPOWERED, not evidence.",
    "power_floor": ">= 10 trades / >= 5 episodes / >= 5 distinct crash days per fold; "
    "otherwise UNDERPOWERED with a power curve.",
}

FUNDING_ACQUISITION = {
    "rule": (
        "A venue without realized funding history is recorded UNAVAILABLE_FUNDING "
        "(never zero-filled) and the realistic arms are evaluated on the remaining "
        "venues; okx is UNAVAILABLE_FUNDING by API retention (33-day window)."
    ),
    "cache_layout": "research_state/cache/<venue>_funding_<window>/funding_history.csv (+ manifest)",
}

ANCHOR_RULE = {
    "rule": (
        "Anchor verification against the prior primary arm is mandatory BEFORE any "
        "C31 inference cell runs. The fidelity-anchor arm of the selected direction "
        "must reproduce the C30 primary-arm per-venue/per-fold PnL within +/-1.0 "
        "(HOLDOUT_ANCHOR_REPRODUCED). Anchor mismatch => C31_UNDERPOWERED; no "
        "verdict may be issued until the anchor reproduces."
    ),
    "tolerance_pnl": 1.0,
}

GUARDRAILS = [
    "No cross-venue relabeling as Hyperliquid-native (is_hyperliquid_venue_data=false).",
    "No synthetic gap-fill; no spec relaxation of RSI/target/hold/sizing/volume/gross cap.",
    "Signal path frozen to the C24/C25/C26/C30 sentinel; liquidation distance fixed "
    "at the C24 primary d15; cost model frozen at C25 primary; funding model honest "
    "(okx = UNAVAILABLE_FUNDING, never zero-filled or proxied).",
    "No additional venues, folds, or directions beyond those pre-registered for the "
    "selected C31 direction.",
    "Artifacts are immutable once written; do not edit completed campaign outputs.",
    "No C31 cell runs until C30 ACCEPTANCE: PASS (sequential adjudication chain).",
    "Draw floors (20k/20k/2k/2k) are not reducible. No reduced-draw runs.",
    "No same-data rerun of a closed campaign; C31-A needs a fresh prereg + anchor "
    "verification; the holdout axis varies only the data window (newest never-scored), "
    "never the signal path or draw counts.",
    "The holdout_primary arm requires a fresh archive manifest "
    "research_state/cache/<venue>_1h_multiyear_20260929_20261121 per venue; absent "
    "manifest => cell recorded holdout_manifest_missing, no synthetic data.",
]

DECISION_RULES_COMMON = {
    "C31_REOPENS_C1_C30": (
        "ALL of, under the PRIMARY arm of the selected direction: (a) pooled total "
        "PnL > 0; (b) venue-blocked bootstrap CI95 lower bound > 0; (c) >= 1 BH "
        "survivor in the 16-test primary-arm family; (d) >= 3 of 4 folds positive; "
        "(e) >= 3 of 4 venues positive (available venue set). Then the C1-C30 NO_GO "
        "is NOT robust to the C31 forward-time holdout axis: record "
        "SUPERSEDED_BY_C31 and the edge is re-opened."
    ),
    "C31_NO_GO_ROBUST_TO_HOLDOUT": (
        "ANY of (a)-(e) fails under the PRIMARY arm. Then the NO_GO survives the "
        "C31 forward-time holdout axis and is strengthened: record C1-C31 NO_GO "
        "ROBUST TO MARGIN, COST, PATH, ALLOCATION, HOLDOUT AND EXECUTION REALISM."
    ),
    "C31_UNDERPOWERED": (
        "Anchor mismatch, prereg generated after any compute artifact, draw floors "
        "not met, missing artifacts, signal-path/cost/execution drift, acquisition "
        "gate not passed, or holdout manifest missing.",
    ),
}

REQUIRED_ARTIFACTS_TMPL = [
    f"c31_prereg_{{TS}}.json",
    f"c31_prereg_{{TS}}.md",
    f"c31_decision_verdict_{{fidelity_arm}}_{{TS}}.json",
    f"c31_decision_verdict_{{primary_arm}}_{{TS}}.json",
    f"c31_decision_verdict_CONSOLIDATED_{{TS}}.json",
]

PROVENANCE = {
    "real_market_data": True,
    "fabricated_data": False,
    "synthetic_data": False,
    "cross_venue": True,
    "is_hyperliquid_venue_data": False,
    "caveat": ("Real exchange USDT-perp data, non-synthetic, CROSS-VENUE vs the "
               "Hyperliquid spec; NEVER Hyperliquid performance evidence and never "
               "relabelled as such."),
}


def _direction_prereg(direction_key: str) -> Dict[str, Any]:
    d = DIRECTIONS[direction_key]
    fidelity_arm = next(a for a, v in d["arms"].items() if v["role"] == "FIDELITY_ANCHOR")
    primary_arm = next(a for a, v in d["arms"].items() if v["role"] == "PRIMARY")
    prereg = {
        "schema_version": 1,
        "campaign": "C31",
        "binding_task": f"C31-{direction_key[-1].upper()}-T1",
        "direction": direction_key,
        "direction_name": d["name"],
        "prereg_status": "PRE_REGISTERED_BEFORE_COMPUTE",
        "generated_at_utc": "2026-11-21T05:22:33Z",
        "title": d["title"],
        "why_c31": (
            "C24 established margin/liquidation fidelity (PASS, consolidated "
            "C24_REOPENS_C1_C23). C25/C26 adjudicate cost/funding and "
            "intrabar-path fidelity; C27 is next-venue replication; C28 is "
            "portfolio-level capital allocation; C29-A is the strict temporal "
            "out-of-sample holdout on the archived multiyear window; C30-A is the "
            "execution-realism stress. C31-A is the mandatory same-session successor "
            "on C30 ACCEPTANCE: PASS: it opens the forward-time holdout frontier "
            "(newest never-scored window 2026-09-29 -> 2026-11-21) so the heavy-work "
            "queue does not terminate at C30 and no session may claim 'no authorized "
            "work'. C31 may NOT launch until C30 ACCEPTANCE: PASS; C30 on C29; "
            "C29 on C28; C28 on C27; C27 on C26; C26 on C25; C25 IN FLIGHT."
        ),
        "research_question": (
            f"Does the pooled spec-literal crash-rebound edge remain positive under "
            f"the {d['name']} fidelity axis, across four real venues, when scored "
            f"on the strict temporal holdout window {HOLDOUT_FOLD['start']} -> "
            f"{HOLDOUT_FOLD['end']} (newest never-scored real data) with the signal "
            f"path, cost and funding frozen at C25/C26 primary and draw floors intact?"
        ),
        "blocked_on": (
            "C30-T1 (execution-realism stress), which is blocked on C29, which is "
            "blocked on C28, which is blocked on C27, which is blocked on C26, "
            "which is blocked on C25. C31 build (this prereg) may proceed before "
            "C25/C26/C27/C28/C29/C30 pass, but no C31 cell may run until C30 "
            "ACCEPTANCE: PASS and the C30 primary-arm evidence is available as "
            "anchor reference, and until the per-venue archive manifest for the "
            "holdout window 2026-09-29 -> 2026-11-21 is acquired."
        ),
        "signal_path_frozen": SIGNAL_PATH_FROZEN,
        "arms": d["arms"],
        "taker_bps": TAKER_BPS,
        "reference_px": REFERENCE_PX,
        "borrow_bps": BORROW_BPS,
        "liquidation": {
            "maint_margin_pct": LIQ_MAINT,
            "buffer_pct": LIQ_BUFFER,
            "distance_pct": LIQ_DISTANCE_PCT,
            "rule": "Liquidation distance fixed at the C24 primary arm (d15: "
            "maint=14, buffer=1 => 15%); not a C31 variable.",
        },
        "arms_rule": (
            "ONLY the C31 direction axis varies across arms. All other config fields "
            "(signal path + liquidation distance + cost model + funding model) are "
            "identical and drift-checked. The FIDELITY_ANCHOR arm reproduces the "
            "prior primary-arm baseline within +/-1.0; the PRIMARY arm is the "
            "adjudication arm. All arms run the full 4 venues x 4 folds x "
            "20k bootstrap / 20k permutation / 2k placebo — no smoke arm, no reduced "
            "draw floors, no descriptive-only arm. The holdout_primary arm additionally "
            "requires the per-venue archive manifest for the newest never-scored "
            "window."
        ),
        "venues": VENUES,
        "folds": FOLDS,
        "holdout_fold": HOLDOUT_FOLD,
        "inference": INFERENCE,
        "funding_acquisition": FUNDING_ACQUISITION,
        "anchor_rule": {**ANCHOR_RULE, "token_ok": "HOLDOUT_ANCHOR_REPRODUCED",
                        "token_bad": "Anchor mismatch => C31_UNDERPOWERED",
                        "fidelity_arm": fidelity_arm},
        "decision_rules": DECISION_RULES_COMMON,
        "required_artifacts": [a.format(TS=TS, fidelity_arm=fidelity_arm,
                                        primary_arm=primary_arm)
                               for a in REQUIRED_ARTIFACTS_TMPL],
        "checkpoint_rule": (
            "A (direction, arm, venue, fold) is DONE only when "
            "research_state/c31_ckpt_<direction>_<arm>_<venue>_<fold>_<TS>.json "
            "exists. Resume with --resume; never relaunch completed folds. A "
            "holdout_primary cell whose venue archive manifest for the holdout "
            "window is absent is recorded holdout_manifest_missing (no inference)."
        ),
        "provenance": PROVENANCE,
        "guardrails": GUARDRAILS,
    }
    return prereg


def _md(direction_key: str, prereg: Dict[str, Any]) -> str:
    d = DIRECTIONS[direction_key]
    arms_md = "\n".join(
        f"| {a} | {v['role']} | {d['axis']} varies |"
        for a, v in d["arms"].items())
    return f"""# C31 PRE-REGISTRATION - {TS} \u2014 direction {direction_key} ({d['name']})

**Status:** PRE_REGISTERED_BEFORE_COMPUTE
**Campaign:** C31 \u2014 {d['title']}
**Binding question:** {prereg['research_question']}
**Blocked on:** C30 ACCEPTANCE: PASS (C30 -> C29 -> C28 -> C27 -> C26 -> C25 chain;
C25 IN FLIGHT). No C31 cell runs until `C30 ACCEPTANCE: PASS`, the C30 primary-arm
anchor exists, and the per-venue archive manifest for the holdout window
2026-09-29 -> 2026-11-21 is acquired.

## Why C31 exists

{prereg['why_c31']}

The C24->C25->C26->C27->C28->C29->C30 chain adjudicates margin, cost/funding,
intrabar-path, portfolio-level allocation and execution-realism stress on four
venues over the archived multiyear window (2023-2026YTD, ending 2026-09-28).
C31 opens the forward-time holdout frontier ({d['name']}) on the newest
never-scored window so the heavy-work queue does not terminate at C30 and no
future session may declare "no authorized work."

## Signal path (frozen = C24/C25/C26/C30 sentinel; drift-checked)

- rsi_period=21, rsi_threshold=20, target_pct=9, rebound_short_*,
  gross_cap=120%, volume floor $5M, sizing 1.25%, ETH hedge on,
  entry_spec_literal_next_open=True, seed=20261201.
- Liquidation distance fixed at the C24 primary arm (d15): maint=14, buffer=1 => 15%.
- Cost model frozen at C25 primary; funding model honest (okx = UNAVAILABLE_FUNDING).
- ONLY the {d['name']} axis varies across arms: the holdout_primary arm scores the
  newest never-scored window (2026-09-29 -> 2026-11-21) instead of the archived folds.

## Direction: {d['title']}

{d['why']}

| arm | role | axis |
|---|---|---|
{arms_md}

- Fidelity-anchor arm must reproduce the C30 primary-arm per-venue/per-fold PnL
  within +/-1.0 (HOLDOUT_ANCHOR_REPRODUCED, else `C31_UNDERPOWERED`).
- Primary arm is the adjudication arm for the selected direction.

## Inference (floors, not reducible; all arms)

- Episode-block bootstrap: 20,000 draws
- Conditional temporal-edge permutation: 20,000 draws
- Full-portfolio placebo: 2,000 runs
- Strata permutation: 2,000 draws
- BH (alpha 0.05) family: primary arm, 4 folds x 4 venues = 16 tests
- Pooled: venue-blocked bootstrap over venue-fold cells, 20,000 draws
- Power floor: >= 10 trades / >= 5 episodes / >= 5 distinct crash days per fold

## Funding acquisition

{FUNDING_ACQUISITION['rule']}
Cache layout: {FUNDING_ACQUISITION['cache_layout']}

## Anchor verification (mandatory before any C31 cell)

{ANCHOR_RULE['rule']} Tolerance +/-1.0 PnL. Token: HOLDOUT_ANCHOR_REPRODUCED.
Anchor reference: C30 primary-arm venue_totals from
research_state/c30_decision_verdict_CONSOLIDATED_20261121T051754Z.json.

## Decision rules

- **C31_REOPENS_C1_C30**: under the PRIMARY arm: pooled total > 0 AND CI95 lower >
  0 AND >= 1 BH survivor AND >= 3/4 folds positive AND >= 3/4 venues positive.
  Then record `SUPERSEDED_BY_C31`.
- **C31_NO_GO_ROBUST_TO_HOLDOUT**: any condition fails. Record C1-C31 `NO_GO` robust
  to margin, cost, path, allocation, holdout and execution realism.
- **C31_UNDERPOWERED**: anchor mismatch, draw-floor violation, drift, missing
  artifacts, acquisition gate not passed, holdout manifest missing.

Both terminal outcomes require the full arm x venue x fold table, per-leg
attribution and exit-reason decomposition. No bare token. C31 is an adjudication,
not a search.

## Holdout-window acquisition gate

The holdout_primary arm scores data from 2026-09-29 -> 2026-11-21, which is beyond
the archived multiyear window. Before any holdout_primary cell infers, the archive
manifest `research_state/cache/<venue>_1h_multiyear_20260929_20261121` must exist
for each venue (funding cache `<venue>_funding_20260929_20261121` where available).
Until a manifest is acquired the cell is recorded `holdout_manifest_missing`; no
synthetic data, no same-data rerun, no reduced window.

## Run order

```
PYTHONPATH=. .venv/bin/python scripts/build_c31_prereg.py --direction {direction_key}  # done (this file)
# after C30 ACCEPTANCE: PASS and holdout-window manifests acquired:
PYTHONPATH=. .venv/bin/python scripts/run_c31_campaign.py --direction {direction_key} --jobs 4 --resume
PYTHONPATH=. .venv/bin/python scripts/verify_c31_focus_campaign.py --direction {direction_key}   # -> C31 ACCEPTANCE: PASS
bash scripts/status_c31.sh --direction {direction_key}
```

## Provenance

Real exchange USDT-perp data, non-synthetic, `cross_venue=true`,
`is_hyperliquid_venue_data=false`. Never Hyperliquid performance evidence, never
relabelled as such.
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the C31 pre-registration")
    ap.add_argument("--direction", required=True, choices=sorted(DIRECTIONS),
                    help="C31 direction to pre-register (c31-a)")
    args = ap.parse_args()

    direction_key = args.direction
    prereg = _direction_prereg(direction_key)

    out_json = STATE / f"c31_prereg_{TS}.json"
    out_md = STATE / f"c31_prereg_{TS}.md"
    if out_json.exists() or out_md.exists():
        raise SystemExit(f"refusing to overwrite existing prereg {out_json.name}")

    out_json.write_text(json.dumps(prereg, indent=2) + "\n")
    out_md.write_text(_md(direction_key, prereg))
    sha = hashlib.sha256(out_json.read_bytes()).hexdigest()
    print("wrote", out_json)
    print("wrote", out_md)
    print("sha256", sha)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
