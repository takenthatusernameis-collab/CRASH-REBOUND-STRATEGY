#!/usr/bin/env python3
"""Build the C28 pre-registration (PRE_REGISTERED_BEFORE_COMPUTE).

C28 is the NEXT FOCUS CAMPAIGN in the `C24 -> C25 -> C26 -> C27 -> C28+` heavy
queue. Per the HANDOFF no-avoidance rule, once C27 ACCEPTANCE: PASS lands, the
same session MUST open C28 with a fresh sha-pinned prereg anchored on the
completed C24/C25/C26 primary-arm evidence — and then durably launch it. C28 is
never optional, never "no authorized work", never a same-data rerun, never a
frozen-signal parameter search, never a reduced-draw run.

Three candidate heavy directions are pre-registered here; exactly ONE direction
is selected per C28 build (--direction). Each direction adds a NEW fidelity axis
on top of the frozen C24/C25/C26 primary arm:

  C28-A portfolio_level_allocation   : cross-venue capital allocation under a
      fixed budget + venue-correlation fidelity. Does the pooled GO survive
      capital constraints and cross-venue return correlation? (allocation
      varies; signal, cost, funding frozen at C25/C26 primary)
  C28-B temporal_oos_holdout         : strict temporal OOS holdout on the
      newest never-scored window. Pooled sign on data that no C1-C27 cell has
      ever seen. (new fold/window varies; everything else frozen)
  C28-C execution_realism_stress     : execution-realism stress (latency,
      partial fills, empirical slippage distribution). Execution parameters
      vary; signal/funding frozen at C25/C26 primary.

Common invariants across all directions:
  - real market data only, cross_venue=true, is_hyperliquid_venue_data=false
  - signal path frozen to C24/C25/C26 sentinel (drift-checked)
  - liquidation distance fixed at C24 primary d15 (maint=14, buffer=1 => 15%)
  - draw floors 20k bootstrap / 20k permutation / 2k placebo / 2k strata
  - anchor verification against the prior primary arm BEFORE inference
  - BH correction per venue-fold family; terminal tokens only
  - no same-data rerun, no parameter search, no reduced draws

Run (from repo root):
  PYTHONPATH=. .venv/bin/python scripts/build_c28_prereg.py --direction c28-a
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
TS = "20261121T013400Z"

FOLDS = [
    {"id": "2023", "start": "2023-01-01T00:00:00Z", "end": "2023-12-31T23:00:00Z"},
    {"id": "2024", "start": "2024-01-01T00:00:00Z", "end": "2024-12-31T23:00:00Z"},
    {"id": "2025", "start": "2025-01-01T00:00:00Z", "end": "2025-12-31T23:00:00Z"},
    {"id": "2026YTD", "start": "2026-01-01T00:00:00Z", "end": "2026-09-28T23:00:00Z"},
]

VENUES = ["okx", "binance_um", "mexc", "bitget"]

# C24 primary arm (d15) liquidation distance: maint=14, buffer=1 => 15%.
LIQ_MAINT = 14.0
LIQ_BUFFER = 1.0
LIQ_DISTANCE_PCT = 15.0

# Frozen signal path = C24/C25/C26 sentinel. Any artifact whose signal_path/cost
# fields differ from this block is INVALID (drift rule).
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
    "min_daily_volume_usd": 5000000.0,
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

# Venue published taker fee (bps) per side (carried from C25 prereg, 4.5-7 bps band).
TAKER_BPS = {"okx": 5.0, "binance_um": 4.5, "mexc": 6.0, "bitget": 5.5}
REFERENCE_PX = 60000.0
BORROW_BPS = 5.0

# Per-direction config treatments (ONLY the named axis varies per direction;
# signal path, liquidation distance, cost model frozen at C25/C26 primary).
DIRECTIONS: Dict[str, Dict[str, Any]] = {
    "c28-a": {
        "name": "portfolio_level_allocation",
        "title": "C28-A Portfolio-Level Cross-Venue Capital Allocation & Correlation Fidelity",
        "why": "C25/C26 adjudicate cost/funding and intrabar-path fidelity per venue "
        "on 4 venues x 4 folds. C28-A asks the portfolio-level successor question: "
        "does the pooled GO survive cross-venue capital constraints and venue return "
        "correlation when all viable venues share a fixed gross budget? Allocation "
        "weights vary; signal, cost, funding, liquidation frozen at C25/C26 primary.",
        "axis": "capital_allocation",
        "arms": {
            "alloc_base": {
                "role": "FIDELITY_ANCHOR",
                "why": "Equal-ish per-venue allocation reproducing the C25/C26 "
                "primary-arm per-venue/per-fold PnL within +/-1.0 "
                "(ALLOC_ANCHOR_REPRODUCED). Baseline for the fixed-budget pool.",
            },
            "alloc_correlation": {
                "role": "PRIMARY",
                "why": "Cross-venue capital allocation under a fixed gross budget "
                "(gross_cap_pct applied to the pooled portfolio, per-venue caps, "
                "correlation-aware sizing). Tests whether pooled sign survives capital "
                "constraints + venue correlation.",
            },
        },
    },
    "c28-b": {
        "name": "temporal_oos_holdout",
        "title": "C28-B Strict Temporal Out-of-Sample Holdout on the Newest Never-Scored Window",
        "why": "C1-C27 score folds through 2026YTD (ends 2026-09-28). C28-B asks "
        "whether the edge holds on a strict temporal holdout window that no C1-C27 "
        "cell has ever scored (post-2026-09-28 real data acquired fresh). New data "
        "manifest + fresh fold; signal/cost/funding frozen at C25/C26 primary.",
        "axis": "temporal_holdout",
        "arms": {
            "holdout_base": {
                "role": "FIDELITY_ANCHOR",
                "why": "C25/C26 primary-arm model re-run on the holdout window; "
                "must reproduce the established per-venue baseline within +/-1.0 "
                "(HOLDOUT_ANCHOR_REPRODUCED).",
            },
            "holdout_oos": {
                "role": "PRIMARY",
                "why": "Strict temporal OOS holdout on never-scored real data. "
                "Pooled sign and CI95 on the holdout window decide whether the edge "
                "generalizes forward in time.",
            },
        },
    },
    "c28-c": {
        "name": "execution_realism_stress",
        "title": "C28-C Execution-Realism Stress (Latency, Partial Fills, Empirical Slippage Distribution)",
        "why": "C25/C26 assume next-open fills at flat slippage. C28-C asks whether "
        "the edge survives execution realism: empirical slippage distribution, "
        "latency-driven fill degradation, partial fills. Execution parameters vary; "
        "signal/funding frozen at C25/C26 primary.",
        "axis": "execution_realism",
        "arms": {
            "exec_base": {
                "role": "FIDELITY_ANCHOR",
                "why": "Flat slippage 5 bps/side, next-open fills (C25 primary cost "
                "model). MUST reproduce the C25/C26 primary-arm per-venue/per-fold "
                "PnL within +/-1.0 (EXEC_ANCHOR_REPRODUCED).",
            },
            "exec_stress": {
                "role": "PRIMARY",
                "why": "Empirical slippage distribution + latency + partial-fill "
                "stress applied to fills on the same real data. Tests edge survival "
                "under execution realism.",
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
        "C28 inference cell runs. The fidelity-anchor arm of the selected direction "
        "must reproduce the C25/C26 primary-arm per-venue/per-fold PnL (or the "
        "corresponding C28-A/C28-B/C28-C baseline) within +/-1.0 "
        "(<AXIS>_ANCHOR_REPRODUCED). Anchor mismatch => C28_UNDERPOWERED; no verdict "
        "may be issued until the anchor reproduces."
    ),
    "tolerance_pnl": 1.0,
}

GUARDRAILS = [
    "No cross-venue relabeling as Hyperliquid-native (is_hyperliquid_venue_data=false).",
    "No synthetic gap-fill; no spec relaxation of RSI/target/hold/sizing/volume/gross cap.",
    "Signal path frozen to the C24/C25/C26 sentinel; liquidation distance fixed at "
    "the C24 primary d15; cost model frozen at C25 primary; funding model honest "
    "(okx = UNAVAILABLE_FUNDING, never zero-filled or proxied).",
    "No additional venues, folds, or directions beyond those pre-registered for the "
    "selected C28 direction.",
    "Artifacts are immutable once written; do not edit completed campaign outputs.",
    "No C28 cell runs until C27 ACCEPTANCE: PASS (sequential adjudication chain).",
    "Draw floors (20k/20k/2k/2k) are not reducible. No reduced-draw runs.",
    "No same-data rerun of a closed campaign; each C28 direction needs a new data "
    "manifest (holdout window or execution cache) + fresh prereg + anchor verification.",
]

DECISION_RULES_COMMON = {
    "C28_REOPENS_C1_C27": (
        "ALL of, under the PRIMARY arm of the selected direction: (a) pooled total "
        "PnL > 0; (b) venue-blocked bootstrap CI95 lower bound > 0; (c) >= 1 BH "
        "survivor in the 16-test primary-arm family; (d) >= 3 of 4 folds positive; "
        "(e) >= 3 of 4 venues positive (available venue set). Then the C1-C27 NO_GO "
        "is NOT robust to the C28 fidelity axis: record SUPERSEDED_BY_C28 and the "
        "edge is re-opened."
    ),
    "C28_NO_GO_ROBUST_TO_AXIS": (
        "ANY of (a)-(e) fails under the PRIMARY arm. Then the NO_GO survives the "
        "C28 fidelity axis and is strengthened: record C1-C28 NO_GO ROBUST TO "
        "MARGIN, COST, PATH AND <AXIS>."
    ),
    "C28_UNDERPOWERED": (
        "Anchor mismatch, prereg generated after any compute artifact, draw floors "
        "not met, missing artifacts, signal-path/cost/execution drift, or acquisition "
        "gate not passed.",
    ),
}

REQUIRED_ARTIFACTS_TMPL = [
    f"c28_prereg_{{TS}}.json",
    f"c28_prereg_{{TS}}.md",
    f"c28_decision_verdict_{{fidelity_arm}}_{{TS}}.json",
    f"c28_decision_verdict_{{primary_arm}}_{{TS}}.json",
    f"c28_decision_verdict_CONSOLIDATED_{{TS}}.json",
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
    anchor_token = {
        "c28-a": "ALLOC_ANCHOR_REPRODUCED",
        "c28-b": "HOLDOUT_ANCHOR_REPRODUCED",
        "c28-c": "EXEC_ANCHOR_REPRODUCED",
    }[direction_key]
    prereg = {
        "schema_version": 1,
        "campaign": "C28",
        "binding_task": f"C28-{direction_key[-1].upper()}-T1",
        "direction": direction_key,
        "direction_name": d["name"],
        "prereg_status": "PRE_REGISTERED_BEFORE_COMPUTE",
        "generated_at_utc": "2026-11-21T01:34:00Z",
        "title": d["title"],
        "why_c28": (
            "C24 established margin/liquidation fidelity (PASS, consolidated "
            "C24_REOPENS_C1_C23). C25/C26 adjudicate cost/funding and "
            "intrabar-path fidelity on the same four venues. C27 is the next-venue "
            "replication. C28 is the mandatory same-session successor on C27 PASS: "
            "it opens the portfolio/allocation/holdout/execution-realism fidelity "
            "frontier so the heavy-work queue never dries out and no session may "
            "claim 'no authorized work'. C28 may NOT launch until C27 ACCEPTANCE: "
            "PASS; C27 may NOT launch until C26 ACCEPTANCE: PASS; C26 may NOT "
            "launch until C25 ACCEPTANCE: PASS; C25 is IN FLIGHT."
        ),
        "research_question": (
            f"Does the pooled spec-literal crash-rebound edge remain positive under "
            f"the {d['name']} fidelity axis, across four real venues and four folds, "
            f"with the signal path frozen and draw floors intact?"
        ),
        "blocked_on": (
            "C27-T1 (next independent USDT-perp venue replication), which is itself "
            "blocked on C26, which is blocked on C25. C28 build (this prereg) may "
            "proceed before C25/C26/C27 pass, but no C28 cell may run until C27 "
            "ACCEPTANCE: PASS and the prior primary-arm evidence is available as "
            "anchor reference."
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
            "maint=14, buffer=1 => 15%); not a C28 variable.",
        },
        "arms_rule": (
            "ONLY the C28 direction axis varies across arms. All other config fields "
            "(signal path + liquidation distance + cost model + funding model) are "
            "identical and drift-checked. The FIDELITY_ANCHOR arm reproduces the "
            "prior primary-arm baseline within +/-1.0; the PRIMARY arm is the "
            "adjudication arm. All arms run the full 4 venues x 4 folds x "
            "20k bootstrap / 20k permutation / 2k placebo — no smoke arm, no reduced "
            "draw floors, no descriptive-only arm."
        ),
        "venues": VENUES,
        "folds": FOLDS,
        "inference": INFERENCE,
        "funding_acquisition": FUNDING_ACQUISITION,
        "anchor_rule": {**ANCHOR_RULE, "token_ok": anchor_token,
                        "token_bad": f"Anchor mismatch => C28_UNDERPOWERED",
                        "fidelity_arm": fidelity_arm},
        "decision_rules": DECISION_RULES_COMMON,
        "required_artifacts": [a.format(TS=TS, fidelity_arm=fidelity_arm,
                                        primary_arm=primary_arm)
                               for a in REQUIRED_ARTIFACTS_TMPL],
        "checkpoint_rule": (
            "A (direction, arm, venue, fold) is DONE only when "
            "research_state/c28_ckpt_<direction>_<arm>_<venue>_<fold>_<TS>.json "
            "exists. Resume with --resume; never relaunch completed folds."
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
    inf = prereg["inference"]
    anchor_token = {
        "c28-a": "ALLOC_ANCHOR_REPRODUCED",
        "c28-b": "HOLDOUT_ANCHOR_REPRODUCED",
        "c28-c": "EXEC_ANCHOR_REPRODUCED",
    }[direction_key]
    return f"""# C28 PRE-REGISTRATION - {TS} — direction {direction_key} ({d['name']})

**Status:** PRE_REGISTERED_BEFORE_COMPUTE
**Campaign:** C28 — {d['title']}
**Binding question:** {prereg['research_question']}
**Blocked on:** C27 ACCEPTANCE: PASS (C27 -> C26 -> C25 chain). No C28 cell runs
until `C27 ACCEPTANCE: PASS`.

## Why C28 exists

{prereg['why_c28']}

The C24->C25->C26->C27 chain adjudicates margin, cost/funding and intrabar-path
fidelity on four venues. C28 opens the next fidelity frontier
({d['name']}) so the heavy-work queue does not terminate at C27 and no future
session may declare "no authorized work." Exactly one direction is selected per
build ({direction_key}); axes are never mixed within a single prereg.

## Signal path (frozen = C24/C25/C26 sentinel; drift-checked)

- rsi_period=21, rsi_threshold=20, target_pct=9, rebound_short_*,
  gross_cap=120%, volume floor $5M, sizing 1.25%, ETH hedge on,
  entry_spec_literal_next_open=True, seed=20261201.
- Liquidation distance fixed at the C24 primary arm (d15): maint=14, buffer=1 => 15%.
- Cost model frozen at C25 primary; funding model honest (okx = UNAVAILABLE_FUNDING).
- ONLY the {d['name']} axis varies across arms.

## Direction: {d['title']}

{d['why']}

| arm | role | axis |
|---|---|---|
{arms_md}

- Fidelity-anchor arm must reproduce the prior primary-arm per-venue/per-fold PnL
  within +/-1.0 (anchor token, else `C28_UNDERPOWERED`).
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

## Anchor verification (mandatory before any C28 cell)

{ANCHOR_RULE['rule']} Tolerance +/-1.0 PnL. Token: {anchor_token}.

## Decision rules

- **C28_REOPENS_C1_C27**: under the PRIMARY arm: pooled total > 0 AND CI95 lower >
  0 AND >= 1 BH survivor AND >= 3/4 folds positive AND >= 3/4 venues positive.
  Then record `SUPERSEDED_BY_C28`.
- **C28_NO_GO_ROBUST_TO_AXIS**: any condition fails. Record C1-C28 `NO_GO` robust
  to margin, cost, path and <axis>.
- **C28_UNDERPOWERED**: anchor mismatch, draw-floor violation, drift, missing
  artifacts, acquisition gate not passed.

Both terminal outcomes require the full arm x venue x fold table, per-leg
attribution and exit-reason decomposition. No bare token. C28 is an adjudication,
not a search.

## Run order

```
PYTHONPATH=. .venv/bin/python scripts/build_c28_prereg.py --direction {direction_key}  # done (this file)
# after C27 ACCEPTANCE: PASS:
PYTHONPATH=. .venv/bin/python scripts/run_c28_campaign.py --direction {direction_key} --jobs 4 --resume
PYTHONPATH=. .venv/bin/python scripts/verify_c28_focus_campaign.py --direction {direction_key}   # -> C28 ACCEPTANCE: PASS
bash scripts/status_c28.sh --direction {direction_key}
```

## Provenance

Real exchange USDT-perp data, non-synthetic, `cross_venue=true`,
`is_hyperliquid_venue_data=false`. Never Hyperliquid performance evidence, never
relabelled as such.
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the C28 pre-registration")
    ap.add_argument("--direction", required=True, choices=sorted(DIRECTIONS),
                    help="C28 direction to pre-register (c28-a / c28-b / c28-c)")
    args = ap.parse_args()

    direction_key = args.direction
    prereg = _direction_prereg(direction_key)

    out_json = STATE / f"c28_prereg_{TS}.json"
    out_md = STATE / f"c28_prereg_{TS}.md"
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
