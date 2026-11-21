#!/usr/bin/env python3
"""Build the C30 pre-registration (PRE_REGISTERED_BEFORE_COMPUTE).

C30 is the NEXT FOCUS CAMPAIGN in the `C24 -> C25 -> C26 -> C27 -> C28 -> C30+` heavy
queue. Per the HANDOFF no-avoidance rule, once C28 ACCEPTANCE: PASS lands, the
same session MUST open C30 with a fresh sha-pinned prereg anchored on the
completed C24/C25/C26/C27/C28 primary-arm evidence — and then durably launch it.
C30 is never optional, never "no authorized work", never a same-data rerun, never a
frozen-signal parameter search, never a reduced-draw run.

Direction c30-a = strict_temporal_oos_holdout: strict temporal out-of-sample holdout
on the newest never-scored real data window. The pooled sign on data that no C1-C28
cell has ever scored decides whether the edge generalizes forward in time.

Run (from repo root):
  PYTHONPATH=. .venv/bin/python scripts/build_c30_prereg.py --direction c30-a
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
TS = "20261121T051754Z"

FOLDS = [
    {"id": "2023", "start": "2023-01-01T00:00:00Z", "end": "2023-12-31T23:00:00Z"},
    {"id": "2024", "start": "2024-01-01T00:00:00Z", "end": "2024-12-31T23:00:00Z"},
    {"id": "2025", "start": "2025-01-01T00:00:00Z", "end": "2025-12-31T23:00:00Z"},
    {"id": "2026YTD", "start": "2026-01-01T00:00:00Z", "end": "2026-09-28T23:00:00Z"},
]

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
    "c30-a": {
        "name": "execution_realism_stress",
        "title": "C30-A Execution-Realism Stress (Slippage & Taker-Fee Fidelity)",
        "why": "C1-C29 adjudicate margin/liquidation, cost/funding, intrabar-path, "
        "portfolio-level allocation and a strict temporal holdout. C30-A asks whether "
        "the edge survives a harsher execution-realism axis: 3x empirical slippage "
        "(15 bps/side vs the 5 bps base) plus full venue taker commission, with the "
        "signal path, funding and liquidation frozen at C25/C26 primary. This is the "
        "honest upper bound on execution friction the hourly engine can model "
        "(order slicing / L2 impact remain documented non-simulated limitations).",
        "axis": "execution_realism",
        "arms": {
            "exec_base": {
                "role": "FIDELITY_ANCHOR",
                "why": "Baseline execution config (5 bps slippage, $0.001/share, "
                "flat 0.01%/h funding); must reproduce the C29 primary-arm per-venue "
                "baseline within +/-1.0 (EXEC_ANCHOR_REPRODUCED).",
            },
            "exec_stress": {
                "role": "PRIMARY",
                "why": "3x empirical slippage (15 bps/side) + full venue taker "
                "commission. Pooled sign and CI95 under stress decide whether the "
                "edge is robust to realistic execution friction.",
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
        "C30 inference cell runs. The fidelity-anchor arm of the selected direction "
        "must reproduce the C29 primary-arm per-venue/per-fold PnL within +/-1.0 "
        "(EXEC_ANCHOR_REPRODUCED). Anchor mismatch => C30_UNDERPOWERED; no verdict "
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
    "selected C30 direction.",
    "Artifacts are immutable once written; do not edit completed campaign outputs.",
    "No C30 cell runs until C29 ACCEPTANCE: PASS (sequential adjudication chain).",
    "Draw floors (20k/20k/2k/2k) are not reducible. No reduced-draw runs.",
    "No same-data rerun of a closed campaign; C30-A needs a fresh prereg + anchor "
    "verification; execution-realism stress varies only slippage and taker "
    "commission, never the signal path or draw counts.",
]

DECISION_RULES_COMMON = {
    "C30_REOPENS_C1_C29": (
        "ALL of, under the PRIMARY arm of the selected direction: (a) pooled total "
        "PnL > 0; (b) venue-blocked bootstrap CI95 lower bound > 0; (c) >= 1 BH "
        "survivor in the 16-test primary-arm family; (d) >= 3 of 4 folds positive; "
        "(e) >= 3 of 4 venues positive (available venue set). Then the C1-C29 NO_GO "
        "is NOT robust to the C30 execution-realism axis: record SUPERSEDED_BY_C30 "
        "and the edge is re-opened."
    ),
    "C30_NO_GO_ROBUST_TO_EXECUTION": (
        "ANY of (a)-(e) fails under the PRIMARY arm. Then the NO_GO survives the "
        "C30 execution-realism axis and is strengthened: record C1-C30 NO_GO ROBUST "
        "TO MARGIN, COST, PATH, ALLOCATION, HOLDOUT AND EXECUTION REALISM."
    ),
    "C30_UNDERPOWERED": (
        "Anchor mismatch, prereg generated after any compute artifact, draw floors "
        "not met, missing artifacts, signal-path/cost/execution drift, or acquisition "
        "gate not passed.",
    ),
}

REQUIRED_ARTIFACTS_TMPL = [
    f"c30_prereg_{{TS}}.json",
    f"c30_prereg_{{TS}}.md",
    f"c30_decision_verdict_{{fidelity_arm}}_{{TS}}.json",
    f"c30_decision_verdict_{{primary_arm}}_{{TS}}.json",
    f"c30_decision_verdict_CONSOLIDATED_{{TS}}.json",
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
        "campaign": "C30",
        "binding_task": f"C30-{direction_key[-1].upper()}-T1",
        "direction": direction_key,
        "direction_name": d["name"],
        "prereg_status": "PRE_REGISTERED_BEFORE_COMPUTE",
        "generated_at_utc": "2026-11-21T05:17:54Z",
        "title": d["title"],
        "why_c30": (
            "C24 established margin/liquidation fidelity (PASS, consolidated "
            "C24_REOPENS_C1_C23). C25/C26 adjudicate cost/funding and "
            "intrabar-path fidelity; C27 is next-venue replication; C28 is "
            "portfolio-level capital allocation; C29-A is the strict temporal "
            "out-of-sample holdout. C30-A is the mandatory same-session successor "
            "on C29 ACCEPTANCE: PASS: it opens the execution-realism stress frontier "
            "(3x empirical slippage + full venue taker commission) so the heavy-work "
            "queue does not terminate at C29 and no session may claim 'no authorized "
            "work'. C30 may NOT launch until C29 ACCEPTANCE: PASS; C29 on C28; C28 on "
            "C27; C27 on C26; C26 on C25; C25 IN FLIGHT."
        ),
        "research_question": (
            f"Does the pooled spec-literal crash-rebound edge remain positive under "
            f"the {d['name']} fidelity axis, across four real venues, when scored "
            f"with 3x empirical slippage and full venue taker commission while the "
            f"signal path, funding and liquidation stay frozen at C25/C26 primary?"
        ),
        "blocked_on": (
            "C29-T1 (strict temporal out-of-sample holdout), which is blocked on "
            "C28, which is blocked on C27, which is blocked on C26, which is "
            "blocked on C25. C30 build (this prereg) may proceed before C25/C26/"
            "C27/C28/C29 pass, but no C30 cell may run until C29 ACCEPTANCE: PASS and "
            "the C29 primary-arm evidence is available as anchor reference."
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
            "maint=14, buffer=1 => 15%); not a C30 variable.",
        },
        "arms_rule": (
            "ONLY the C30 direction axis varies across arms. All other config fields "
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
        "anchor_rule": {**ANCHOR_RULE, "token_ok": "EXEC_ANCHOR_REPRODUCED",
                        "token_bad": "Anchor mismatch => C30_UNDERPOWERED",
                        "fidelity_arm": fidelity_arm},
        "decision_rules": DECISION_RULES_COMMON,
        "required_artifacts": [a.format(TS=TS, fidelity_arm=fidelity_arm,
                                        primary_arm=primary_arm)
                               for a in REQUIRED_ARTIFACTS_TMPL],
        "checkpoint_rule": (
            "A (direction, arm, venue, fold) is DONE only when "
            "research_state/c30_ckpt_<direction>_<arm>_<venue>_<fold>_<TS>.json "
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
    return f"""# C30 PRE-REGISTRATION - {TS} \u2014 direction {direction_key} ({d['name']})

**Status:** PRE_REGISTERED_BEFORE_COMPUTE
**Campaign:** C30 \u2014 {d['title']}
**Binding question:** {prereg['research_question']}
**Blocked on:** C29 ACCEPTANCE: PASS (C29 -> C28 -> C27 -> C26 -> C25 chain). No C30
cell runs until `C29 ACCEPTANCE: PASS`.

## Why C30 exists

{prereg['why_c30']}

The C24->C25->C26->C27->C28->C29 chain adjudicates margin, cost/funding, intrabar-path,
portfolio-level allocation and the strict temporal holdout on four venues. C30 opens the
execution-realism stress frontier ({d['name']}) so the heavy-work queue does not terminate
at C29 and no future session may declare "no authorized work."

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
  within +/-1.0 (anchor token, else `C30_UNDERPOWERED`).
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

## Anchor verification (mandatory before any C30 cell)

{ANCHOR_RULE['rule']} Tolerance +/-1.0 PnL. Token: EXEC_ANCHOR_REPRODUCED.

## Decision rules

- **C30_REOPENS_C1_C29**: under the PRIMARY arm: pooled total > 0 AND CI95 lower >
  0 AND >= 1 BH survivor AND >= 3/4 folds positive AND >= 3/4 venues positive.
  Then record `SUPERSEDED_BY_C30`.
- **C30_NO_GO_ROBUST_TO_EXECUTION**: any condition fails. Record C1-C30 `NO_GO` robust
  to margin, cost, path, allocation, holdout and execution realism.
- **C30_UNDERPOWERED**: anchor mismatch, draw-floor violation, drift, missing
  artifacts, acquisition gate not passed.

Both terminal outcomes require the full arm x venue x fold table, per-leg
attribution and exit-reason decomposition. No bare token. C30 is an adjudication,
not a search.

## Execution-realism scope

The hourly engine consumes `slippage_pct` per side (src/backtest/engine.py) and
per-share/min commission; C30-A varies these (5 bps -> 15 bps slippage, flat ->
venue taker commission). Order slicing, L2 book impact and sub-hourly latency remain
explicit non-simulated limitations of the hourly engine and are NOT claimed as
reproduced.

## Run order

```
PYTHONPATH=. .venv/bin/python scripts/build_c30_prereg.py --direction {direction_key}  # done (this file)
# after C29 ACCEPTANCE: PASS:
PYTHONPATH=. .venv/bin/python scripts/run_c30_campaign.py --direction {direction_key} --jobs 4 --resume
PYTHONPATH=. .venv/bin/python scripts/verify_c30_focus_campaign.py --direction {direction_key}   # -> C30 ACCEPTANCE: PASS
bash scripts/status_c30.sh --direction {direction_key}
```

## Provenance

Real exchange USDT-perp data, non-synthetic, `cross_venue=true`,
`is_hyperliquid_venue_data=false`. Never Hyperliquid performance evidence, never
relabelled as such.
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the C30 pre-registration")
    ap.add_argument("--direction", required=True, choices=sorted(DIRECTIONS),
                    help="C30 direction to pre-register (c30-a)")
    args = ap.parse_args()

    direction_key = args.direction
    prereg = _direction_prereg(direction_key)

    out_json = STATE / f"c30_prereg_{TS}.json"
    out_md = STATE / f"c30_prereg_{TS}.md"
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
