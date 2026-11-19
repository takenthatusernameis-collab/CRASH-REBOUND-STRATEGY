#!/usr/bin/env python3
"""Build the C24 pre-registration (PRE_REGISTERED_BEFORE_COMPUTE).

C24 is a REPLICATION-VALIDITY adjudication, not a parameter search.  Stage-0
(scripts/probe_c24_liquidation_fidelity.py) reproduced the recorded C20/C22/C23 PnL
exactly with the frozen execution model and showed PnL flips sign between a 10% and a
15% liquidation distance.  Because the frozen model force-exits at 6% -- stricter than
the spec's own wide safety stop (~15% median) -- C24 asks the single question that can
invalidate or confirm the C1-C23 NO_GO:

    Is the NO_GO robust to a spec-plausible liquidation distance, or is it an artifact
    of the 6% margin model?

Only the liquidation-distance execution parameter varies.  The signal path is frozen.
Both outcomes are terminal.

Run (from repo root):
  PYTHONPATH=. .venv/bin/python scripts/build_c24_prereg.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / "research_state"
TS = "20261119T013154Z"
OUT_JSON = STATE / f"c24_prereg_{TS}.json"
OUT_MD = STATE / f"c24_prereg_{TS}.md"

FOLDS = [
    {"id": "2023", "start": "2023-01-01T00:00:00Z", "end": "2023-12-31T23:00:00Z"},
    {"id": "2024", "start": "2024-01-01T00:00:00Z", "end": "2024-12-31T23:00:00Z"},
    {"id": "2025", "start": "2025-01-01T00:00:00Z", "end": "2025-12-31T23:00:00Z"},
    {"id": "2026YTD", "start": "2026-01-01T00:00:00Z", "end": "2026-09-28T23:00:00Z"},
]

ARMS = {
    "base_6": {"maint": 5.0, "buffer": 1.0, "disable": False, "role": "FIDELITY_ANCHOR",
               "liquidation_distance_pct": 6.0},
    "d10": {"maint": 9.0, "buffer": 1.0, "disable": False, "role": "SECONDARY_DESCRIPTIVE",
            "liquidation_distance_pct": 10.0},
    "d15": {"maint": 14.0, "buffer": 1.0, "disable": False, "role": "PRIMARY",
            "liquidation_distance_pct": 15.0},
    "d30": {"maint": 29.0, "buffer": 1.0, "disable": False, "role": "SECONDARY_DESCRIPTIVE",
            "liquidation_distance_pct": 30.0},
    "noliq": {"maint": 5.0, "buffer": 1.0, "disable": True, "role": "UPPER_BOUND_DESCRIPTIVE",
              "liquidation_distance_pct": None},
}

PREREG = {
    "schema_version": 1,
    "campaign": "C24",
    "binding_task": "C24-T1",
    "prereg_status": "PRE_REGISTERED_BEFORE_COMPUTE",
    "generated_at_utc": "2026-11-19T01:31:54Z",
    "title": "C24 - Margin / Liquidation Fidelity Adjudication of the frozen crash-rebound edge",
    "why_c24": (
        "C1-C23 closed NO_GO on OKX, Binance UM, MEXC and Bitget using an execution model "
        "that force-liquidates at a -(5+1)=6% adverse move (src/backtest/engine.py"
        "::_check_liquidation). The published spec's own risk exit is a WIDE safety stop at "
        "8x the usual hourly range (median ~15% below entry on Hyperliquid) and states the "
        "120% coin cap 'leaves margin free'. A 6% forced exit pre-empts the strategy's own "
        "stop and is not specified in the PDF. The C1-C23 NO_GO may therefore describe the "
        "margin model rather than the strategy. C24 adjudicates exactly this, once, with "
        "full inference, before the NO_GO is treated as final."
    ),
    "research_question": (
        "Is the pooled spec-literal PnL sign robust to the liquidation distance used by the "
        "execution model, across four independent real venues and four folds?"
    ),
    "stage0_probe": {
        "artifact": f"research_state/c24_liquidation_fidelity_probe_{TS}.json",
        "script": "scripts/probe_c24_liquidation_fidelity.py",
        "fidelity_anchor_reproduced": True,
        "evidence_class": "DESCRIPTIVE_NO_INFERENCE",
        "pooled_all_venue_sum_by_arm": {
            "base_6": -232760.21, "d10": -61002.11, "d15": 144651.69,
            "d30": 417169.70, "noliq": 539745.51,
        },
        "note": ("Descriptive only: no bootstrap, permutation, placebo or BH. It may NOT "
                 "emit a GO token. It exists solely to justify running the C24 inference arm."),
    },
    "signal_path_frozen": {
        "use_rsi_trigger": True,
        "rsi_period": 21,
        "rsi_threshold": 20.0,
        "target_pct": 9.0,
        "time_exit_max_bars": 50,
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
        "drift_rule": "Any artifact whose signal_path fields differ from this block is INVALID.",
    },
    "arms": ARMS,
    "arms_rule": (
        "ONLY liquidation_maint_margin_pct / liquidation_buffer_pct / enable_liquidation_checks "
        "vary across arms. All other config fields are identical and drift-checked. d15 is "
        "PRIMARY because 15% equals the spec's stated median safety-stop distance, so a "
        "spec-faithful liquidation model cannot fire before the strategy's own stop.")
    ,
    "venues": ["okx", "binance_um", "mexc", "bitget"],
    "folds": FOLDS,
    "inference_scope": {
        "base_6": {"mode": "anchor", "full_inference": False,
                   "why": ("Frozen config; its 20k/20k/2k inference is already recorded in C20 "
                           "(OKX, Binance UM), C22 (MEXC) and C23 (Bitget). C24 only re-checks "
                           "that its campaign PnL reproduces the recorded totals exactly.")},
        "d15": {"mode": "inference", "full_inference": True,
                "why": "PRIMARY adjudication arm; full pre-registered battery required."},
        "d10": {"mode": "campaign_only", "full_inference": False,
                "why": "Descriptive threshold-curve point; no inference, no verdict power."},
        "d30": {"mode": "campaign_only", "full_inference": False,
                "why": "Descriptive threshold-curve point; no inference, no verdict power."},
        "noliq": {"mode": "campaign_only", "full_inference": False,
                  "why": "Upper bound on margin-model sensitivity; not a fidelity claim."},
    },
    "inference": {
        "episode_block_bootstrap_draws": 20000,
        "permutation_draws": 20000,
        "placebo_portfolio_runs": 2000,
        "strata_permutation_draws": 2000,
        "pooled": "venue-blocked bootstrap over the 16 (venue, fold) cell totals (20000 draws)",
        "multiplicity": {
            "method": "benjamini_hochberg",
            "alpha": 0.05,
            "family": "primary arm d15, 4 folds x 4 venues = 16 permutation tests",
        },
        "draw_floor_rule": "Draws below 20000/20000/2000/2000 => UNDERPOWERED, not evidence.",
    },
    "fidelity_anchor": {
        "arm": "base_6",
        "recorded_pooled_pnl": {
            "okx": -54799.23, "binance_um": -70071.41,
            "mexc": -49760.24, "bitget": -58129.33,
        },
        "tolerance_pnl": 1.0,
        "rule": "base_6 must reproduce the recorded C20/C22/C23 pooled PnL within 1.0; "
                "otherwise C24 is INVALID and no verdict may be issued.",
    },
    "decision_rules": {
        "C24_REOPENS_C1_C23": (
            "ALL of: (a) d15 pooled total PnL > 0; (b) venue-blocked bootstrap CI95 lower "
            "bound > 0; (c) >= 1 BH survivor in the 16-test d15 family; (d) >= 3 of 4 folds "
            "positive; (e) >= 3 of 4 venues positive. Then the C1-C23 NO_GO is NOT robust to "
            "a spec-plausible liquidation distance: record SUPERSEDED_BY_C24 and authorize "
            "C24-T2 (portfolio-margin fidelity arm + full re-adjudication)."
        ),
        "C24_NO_GO_ROBUST_TO_MARGIN": (
            "ANY of (a)-(e) fails. Then the NO_GO survives a spec-plausible liquidation "
            "distance and is strengthened: record C1-C24 NO_GO ROBUST and CLOSE the program."
        ),
        "C24_UNDERPOWERED": (
            "Fidelity anchor mismatch, prereg generated after any compute artifact, draw "
            "floors not met, missing artifacts, or signal-path drift."
        ),
        "rule": ("Both REOPENS and NO_GO_ROBUST are terminal and must be reported with the "
                 "full arm x venue x fold table, per-leg attribution and exit-reason "
                 "decomposition. Never report a bare token. C24 is not a GO search: no "
                 "configuration search, no additional thresholds, no new venues beyond the four."),
    },
    "required_artifacts": [
        f"c24_prereg_{TS}.json",
        f"c24_prereg_{TS}.md",
        f"c24_liquidation_fidelity_probe_{TS}.json",
        f"c24_decision_verdict_base_6_{TS}.json",
        f"c24_decision_verdict_d15_{TS}.json",
        f"c24_decision_verdict_d10_{TS}.json",
        f"c24_decision_verdict_d30_{TS}.json",
        f"c24_decision_verdict_noliq_{TS}.json",
        f"c24_decision_verdict_CONSOLIDATED_{TS}.json",
    ],
    "checkpoint_rule": (
        "A (arm, venue, fold) is DONE only when research_state/c24_ckpt_<arm>_<venue>_<fold>_"
        f"{TS}.json exists. Resume with --resume; never relaunch completed folds."),
    "provenance": {
        "real_market_data": True,
        "fabricated_data": False,
        "synthetic_data": False,
        "cross_venue": True,
        "is_hyperliquid_venue_data": False,
        "caveat": ("Real exchange USDT-perp data, non-synthetic, CROSS-VENUE vs the "
                   "Hyperliquid spec; NEVER Hyperliquid performance evidence and never "
                   "relabelled as such."),
    },
    "guardrails": [
        "No cross-venue relabeling as Hyperliquid-native.",
        "No synthetic gap-fill; no spec relaxation of RSI/target/hold/sizing/volume/gross cap.",
        "The liquidation-distance change INCREASES fidelity (the frozen 6% is stricter than "
        "the spec's own ~15% median stop); it must never be described as a tuned edge.",
        "No additional liquidation thresholds, venues or folds beyond those pre-registered.",
        "Artifacts are immutable once written; do not edit completed campaign outputs.",
    ],
}


def main() -> int:
    if OUT_JSON.exists() or OUT_MD.exists():
        raise SystemExit(f"refusing to overwrite existing prereg {OUT_JSON.name}")
    OUT_JSON.write_text(json.dumps(PREREG, indent=2) + "\n")

    arms_md = "\n".join(
        f"| {a} | {v['role']} | {v['liquidation_distance_pct']} | "
        f"maint={v['maint']} buffer={v['buffer']} disable={v['disable']} |"
        for a, v in ARMS.items())
    md = f"""# C24 PRE-REGISTRATION - {TS}

**Status:** PRE_REGISTERED_BEFORE_COMPUTE
**Campaign:** C24-T1 - Margin / Liquidation Fidelity Adjudication
**Binding question:** {PREREG['research_question']}

## Why C24 exists

C1-C23 closed `NO_GO` on OKX, Binance UM, MEXC and Bitget with an execution model that
force-closes any position on a **-(5+1) = 6%** adverse move
(`src/backtest/engine.py::_check_liquidation`). The published spec's own risk exit is a
**wide** safety stop at 8x the usual hourly range (median ~15% below entry on
Hyperliquid) and states the 120% coin cap "leaves margin free". A 6% forced exit fires
**before** the strategy's own stop and appears nowhere in the PDF.

Stage-0 probe (`scripts/probe_c24_liquidation_fidelity.py`) reproduced the recorded
C20/C22/C23 pooled PnL exactly with the 6% arm and found a sign flip between the 10%
and 15% arms. That is descriptive only (no inference) and cannot emit a verdict; C24 is
the pre-registered inference campaign that decides whether the NO_GO is real.

## Arms (only the liquidation distance varies; signal path frozen)

| arm | role | distance % | params |
|---|---|---|---|
{arms_md}

## Inference (floors, not reducible)

- Episode-block bootstrap: 20,000 draws
- Conditional temporal-edge permutation: 20,000 draws
- Full-portfolio placebo: 2,000 runs
- Strata permutation: 2,000 draws
- BH (alpha 0.05) family: primary arm `d15`, 4 folds x 4 venues = 16 tests
- Pooled: venue-blocked bootstrap over 16 (venue, fold) cells, 20,000 draws

## Fidelity anchor

`base_6` MUST reproduce the recorded pooled PnL within 1.0:
okx -54,799.23 | binance_um -70,071.41 | mexc -49,760.24 | bitget -58,129.33.
Otherwise C24 is INVALID and no verdict may be issued.

## Decision rules

- **C24_REOPENS_C1_C23**: d15 pooled > 0 AND pooled CI95 lower > 0 AND >=1 BH survivor
  AND >=3/4 folds positive AND >=3/4 venues positive. Then C1-C23 `NO_GO` is not robust
  to a spec-plausible liquidation distance -> record `SUPERSEDED_BY_C24` and authorize
  C24-T2 (portfolio-margin arm + full re-adjudication).
- **C24_NO_GO_ROBUST_TO_MARGIN**: any condition fails. The `NO_GO` survives and the
  program closes as C1-C24 `NO_GO` ROBUST.
- **C24_UNDERPOWERED**: anchor mismatch, draw-floor violation, drift, missing artifacts.

Both terminal outcomes require the full arm x venue x fold table, per-leg attribution
and exit-reason decomposition. No bare token. No extra configurations, thresholds or
venues - C24 is an adjudication, not a search.

## Run order

```
PYTHONPATH=. .venv/bin/python scripts/build_c24_prereg.py            # done (this file)
PYTHONPATH=. .venv/bin/python scripts/run_c24_margin_fidelity_campaign.py --jobs 4 --resume
PYTHONPATH=. .venv/bin/python scripts/verify_c24_focus_campaign.py   # -> C24 ACCEPTANCE: PASS
bash scripts/status_c24.sh
```

## Provenance

Real exchange USDT-perp data, non-synthetic, `cross_venue=true`,
`is_hyperliquid_venue_data=false`. Never Hyperliquid performance evidence, never
relabelled as such.
"""
    OUT_MD.write_text(md)
    print("wrote", OUT_JSON)
    print("wrote", OUT_MD)
    print("sha256", hashlib.sha256(OUT_JSON.read_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
