#!/usr/bin/env python3
"""Build the C25 pre-registration (PRE_REGISTERED_BEFORE_COMPUTE).

C25 is a COST / REALIZED-FUNDING FIDELITY adjudication, not a parameter search.
C1-C24 (once C24 passes) test one execution assumption (liquidation distance) on
four real cross-venue caches. The remaining un-adjudicated fidelity gap is COST:
the engine's slippage_pct=0.0005 (5 bps/side), commission_per_share=0.001 charged
per share (~0.0017 bps on BTC at $60k, effectively free), commission_min=1.0, and
funding_rate_pct_per_hour=0.01 (flat 0.24%/day) are materially more permissive than
real venue taker fees (~4.5-7 bps/side => 9-14 bps round trip) and realized 8h
funding. Because the strategy exits at a 9% target with multi-day holds and a
short/hedge leg, cost mis-specification is the largest remaining candidate
explanation for the four-venue NO_GO.

C25 asks, once, with full inference:

    Is the NO_GO robust to a realistic round-trip cost + realized funding model,
    or does the edge flip GO under realistic costs?

Only cost/funding parameters vary. The signal path is frozen to the C24 sentinel
(rsi_period=21, rsi_threshold=20, target_pct=9, SPEC_LITERAL_NEXT_OPEN, ETH hedge
on, volume sizing on, gross_cap_pct=120). Liquidation distance is fixed at the
C24-decided primary (pre-registered here as the d15 arm: maint=14, buffer=1 => 15%;
confirmed against the C24 consolidated verdict before any C25 compute). Both
outcomes are terminal.

Run (from repo root):
  PYTHONPATH=. .venv/bin/python scripts/build_c25_prereg.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / "research_state"
TS = "20261119T045500Z"
OUT_JSON = STATE / f"c25_prereg_{TS}.json"
OUT_MD = STATE / f"c25_prereg_{TS}.md"

FOLDS = [
    {"id": "2023", "start": "2023-01-01T00:00:00Z", "end": "2023-12-31T23:00:00Z"},
    {"id": "2024", "start": "2024-01-01T00:00:00Z", "end": "2024-12-31T23:00:00Z"},
    {"id": "2025", "start": "2025-01-01T00:00:00Z", "end": "2025-12-31T23:00:00Z"},
    {"id": "2026YTD", "start": "2026-01-01T00:00:00Z", "end": "2026-09-28T23:00:00Z"},
]

VENUES = ["okx", "binance_um", "mexc", "bitget"]

# Venue published taker fee (bps) per side, within the 4.5-7 bps band cited in
# HANDOFF.md. To be validated against published fee schedules during funding
# acquisition; recorded here as pre-registered constants so the gate can enforce
# PRE_REGISTERED_BEFORE_COMPUTE.
TAKER_BPS = {"okx": 5.0, "binance_um": 4.5, "mexc": 6.0, "bitget": 5.5}
REFERENCE_PX = 60000.0  # BTC reference price for bps-of-notional -> per-share conversion
BORROW_BPS = 5.0  # cost_stress borrow/financing surcharge (bps)

# Liquidation distance fixed at the C24 primary arm (d15): maint=14, buffer=1 => 15%.
# Confirmed against C24's consolidated verdict before C25 compute begins.
LIQ_MAINT = 14.0
LIQ_BUFFER = 1.0
LIQ_DISTANCE_PCT = 15.0

# Frozen signal path = C24 sentinel. Any artifact whose signal_path fields differ
# from this block is INVALID (drift rule).
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
    "drift_rule": "Any artifact whose signal_path/cost fields differ from this prereg are INVALID.",
}

# Cost/funding arms (only slippage/commission/funding vary; signal path frozen;
# liquidation distance fixed at 15%). All four arms run the full battery.
def _taker_commission_per_share(venue: str) -> float:
    return round(REFERENCE_PX * TAKER_BPS[venue] / 10000.0, 6)

ARMS = {
    "cost_base": {
        "role": "FIDELITY_ANCHOR",
        "slippage_pct": 0.0005,
        "commission_per_share": 0.001,
        "commission_min": 1.0,
        "funding_rate_pct_per_hour": 0.01,
        "why": "Exact current engine model; MUST reproduce the C24 d15 primary-arm "
               "per-venue/per-fold PnL within +/-1.0 (COST_ANCHOR_REPRODUCED).",
    },
    "cost_taker": {
        "role": "DESCRIPTIVE",
        "slippage_pct": 0.0005,
        "commission_per_share": None,  # set per venue: reference_px * taker_bps/10000
        "commission_min": 1.0,
        "funding_rate_pct_per_hour": 0.01,
        "why": "Per-venue published taker fee (bps) per side + 5 bps slippage + $1 min "
               "commission; long and short/hedge legs both charged.",
    },
    "cost_taker_funding": {
        "role": "PRIMARY",
        "slippage_pct": 0.0005,
        "commission_per_share": None,  # set per venue
        "commission_min": 1.0,
        "funding_rate_pct_per_hour": None,  # realized 8h funding per venue (UNAVAILABLE_FUNDING if missing)
        "why": "cost_taker + realized 8h funding series on every leg (longs pay when "
               "rate > 0, shorts receive), from acquired venue funding history.",
    },
    "cost_stress": {
        "role": "DESCRIPTIVE",
        "slippage_pct": 0.0010,
        "commission_per_share": None,  # set per venue
        "commission_min": 1.0,
        "funding_rate_pct_per_hour": None,  # realized 8h funding
        "why": "cost_taker_funding + 2x slippage + 5 bps borrow/financing.",
    },
}

PREREG = {
    "schema_version": 1,
    "campaign": "C25",
    "binding_task": "C25-T1",
    "prereg_status": "PRE_REGISTERED_BEFORE_COMPUTE",
    "generated_at_utc": "2026-11-19T04:55:00Z",
    "title": "C25 - Round-Trip Cost & Realized-Funding Fidelity Adjudication of the frozen crash-rebound edge",
    "why_c25": (
        "C1-C24 test one published execution assumption (liquidation distance) on OKX, "
        "Binance UM, MEXC and Bitget. The remaining un-adjudicated fidelity gap is cost: "
        "the engine's slippage_pct=0.0005 (5 bps/side), commission_per_share=0.001 per "
        "share (~0.0017 bps on BTC at $60k, effectively free), commission_min=1.0, and "
        "funding_rate_pct_per_hour=0.01 (flat 0.24%/day) are materially more permissive "
        "than real venue taker fees (~4.5-7 bps/side => 9-14 bps round trip) and realized "
        "8h funding. Because the strategy exits at a 9% target with multi-day holds and a "
        "short/hedge leg, cost mis-specification is the largest remaining candidate "
        "explanation for the four-venue NO_GO. C25 adjudicates whether NO_GO survives a "
        "realistic cost model."
    ),
    "research_question": (
        "Is the pooled spec-literal PnL sign robust to realistic round-trip costs and "
        "realized 8h funding, across four independent real venues and four folds?"
    ),
    "blocked_on": (
        "C24-T1 (margin/liquidation fidelity). C25 build may proceed before C24 passes, "
        "but no C25 cell may run until C24 ACCEPTANCE: PASS and the C24 d15 primary-arm "
        "per-venue/per-fold PnL is available as the cost_base fidelity anchor."
    ),
    "signal_path_frozen": SIGNAL_PATH_FROZEN,
    "arms": ARMS,
    "taker_bps": TAKER_BPS,
    "reference_px": REFERENCE_PX,
    "borrow_bps": BORROW_BPS,
    "arms_rule": (
        "ONLY slippage_pct / commission_per_share / commission_min / funding_rate_pct_per_hour "
        "vary across arms. All other config fields (signal path + liquidation distance) are "
        "identical and drift-checked. cost_base is the FIDELITY_ANCHOR; cost_taker_funding is "
        "the PRIMARY adjudication arm. All four arms run the full 4 venues x 4 folds x "
        "20k bootstrap / 20k permutation / 2k placebo — no smoke arm, no reduced draw "
        "floors, no descriptive-only arm, because the question is a cost-driven sign flip."
    ),
    "venues": VENUES,
    "folds": FOLDS,
    "inference": {
        "episode_block_bootstrap_draws": 20000,
        "permutation_draws": 20000,
        "placebo_portfolio_runs": 2000,
        "strata_permutation_draws": 2000,
        "pooled": "venue-blocked bootstrap over the 16 (venue, fold) cell totals (20000 draws)",
        "multiplicity": {
            "method": "benjamini_hochberg",
            "alpha": 0.05,
            "family": "primary arm cost_taker_funding, 4 folds x 4 venues = 16 permutation tests",
        },
        "draw_floor_rule": "Draws below 20000/20000/2000/2000 => UNDERPOWERED, not evidence.",
    },
    "fidelity_anchor": {
        "arm": "cost_base",
        "reference": (
            "C24 d15 primary-arm per-venue/per-fold PnL from "
            "research_state/c24_decision_verdict_d15_20261119T013154Z.json "
            "(venue_totals) and c24_ckpt_d15_<venue>_<fold>_20261119T013154Z.json. "
            "Available only after C24 ACCEPTANCE: PASS."
        ),
        "tolerance_pnl": 1.0,
        "token_ok": "COST_ANCHOR_REPRODUCED",
        "token_bad": "COST_ANCHOR_MISMATCH => C25_UNDERPOWERED",
        "rule": "cost_base must reproduce the C24 d15 primary-arm per-venue/per-fold PnL "
                "within +/-1.0; otherwise C25 is UNDERPOWERED and no verdict may be issued.",
    },
    "funding_acquisition": {
        "required_for": ["cost_taker_funding", "cost_stress"],
        "cache_layout": "research_state/cache/<venue>_funding_<window>/ with a manifest sha256 and universe file",
        "rule": (
            "A venue without realized funding history is recorded UNAVAILABLE_FUNDING "
            "(never zero-filled) and the realistic arm is evaluated on the remaining "
            "venues; the decision rule then requires >=3 positive folds and >=3 positive "
            "venues out of the available set."
        ),
    },
    "decision_rules": {
        "C25_REOPENS_C1_C24": (
            "ALL of, under cost_taker_funding (NOT cost_stress): (a) pooled total PnL > 0; "
            "(b) venue-blocked bootstrap CI95 lower bound > 0; (c) >= 1 BH survivor in the "
            "16-test cost_taker_funding family; (d) >= 3 of 4 folds positive; (e) >= 3 of 4 "
            "venues positive. Then the C1-C24 NO_GO is NOT robust to a realistic cost model: "
            "record SUPERSEDED_BY_C25 and the edge is re-opened."
        ),
        "C25_NO_GO_ROBUST_TO_COST": (
            "ANY of (a)-(e) fails under cost_taker_funding. Then the NO_GO survives a "
            "realistic cost model and is strengthened: record C1-C25 NO_GO ROBUST TO MARGIN "
            "AND COST; same-data fidelity work is CLOSED (only new-venue data or the CLOSED "
            "Hyperliquid-native acquisition remain)."
        ),
        "C25_UNDERPOWERED": (
            "Cost anchor mismatch, prereg generated after any compute artifact, draw floors "
            "not met, missing artifacts, or signal-path/cost drift."
        ),
        "rule": ("Both REOPENS and NO_GO_ROBUST are terminal and must be reported with the "
                 "full arm x venue x fold table, per-leg attribution and exit-reason "
                 "decomposition. Never report a bare token. C25 is not a GO search: no "
                 "configuration search, no additional thresholds, no new venues beyond the four."),
    },
    "required_artifacts": [
        f"c25_prereg_{TS}.json",
        f"c25_prereg_{TS}.md",
        f"c25_decision_verdict_cost_base_{TS}.json",
        f"c25_decision_verdict_cost_taker_{TS}.json",
        f"c25_decision_verdict_cost_taker_funding_{TS}.json",
        f"c25_decision_verdict_cost_stress_{TS}.json",
        f"c25_decision_verdict_CONSOLIDATED_{TS}.json",
    ],
    "checkpoint_rule": (
        "A (arm, venue, fold) is DONE only when research_state/c25_ckpt_<arm>_<venue>_<fold>_"
        f"{TS}.json exists. Resume with --resume; never relaunch completed folds."
    ),
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
        "C25 varies only cost/funding; liquidation distance fixed at the C24 primary.",
        "No additional cost thresholds, venues or folds beyond those pre-registered.",
        "Artifacts are immutable once written; do not edit completed campaign outputs.",
        "No C25 cell runs until C24 ACCEPTANCE: PASS (C25 is blocked on C24 completion).",
    ],
}


def main() -> int:
    if OUT_JSON.exists() or OUT_MD.exists():
        raise SystemExit(f"refusing to overwrite existing prereg {OUT_JSON.name}")
    OUT_JSON.write_text(json.dumps(PREREG, indent=2) + "\n")

    arms_md = "\n".join(
        f"| {a} | {v['role']} | slippage={v['slippage_pct']} "
        f"comm={v['commission_per_share']} min={v['commission_min']} "
        f"funding={v['funding_rate_pct_per_hour']} |"
        for a, v in ARMS.items())
    md = f"""# C25 PRE-REGISTRATION - {TS}

**Status:** PRE_REGISTERED_BEFORE_COMPUTE
**Campaign:** C25-T1 - Round-Trip Cost & Realized-Funding Fidelity Adjudication
**Binding question:** {PREREG['research_question']}
**Blocked on:** C24-T1 (margin/liquidation fidelity). No C25 cell runs until
`C24 ACCEPTANCE: PASS`.

## Why C25 exists

C1-C24 test one published execution assumption (liquidation distance) on OKX,
Binance UM, MEXC and Bitget. The remaining un-adjudicated fidelity gap is **cost**:
the engine's `slippage_pct=0.0005` (5 bps/side), `commission_per_share=0.001` charged
per share (~0.0017 bps on BTC at $60k, effectively free), `commission_min=1.0`, and
`funding_rate_pct_per_hour=0.01` (flat 0.24%/day) are materially more permissive than
real venue taker fees (~4.5-7 bps/side => 9-14 bps round trip) and realized 8h funding.
Because the strategy exits at a 9% target with multi-day holds and a short/hedge leg,
cost mis-specification is the largest remaining candidate explanation for the
four-venue `NO_GO`.

## Signal path (frozen = C24 sentinel; drift-checked)

- rsi_period=21, rsi_threshold=20, target_pct=9, rebound_short_*,
  gross_cap=120%, volume floor $5M, sizing 1.25%, ETH hedge on,
  entry_spec_literal_next_open=True, seed=20261201.
- Liquidation distance fixed at the C24 primary arm (d15): maint=14, buffer=1 => 15%.
- ONLY slippage/commission/funding vary across arms.

## Arms (only cost/funding vary; signal path frozen)

| arm | role | slippage | commission/share | commission_min | funding rate/hr |
|---|---|---|---|---|---|
{arms_md}

- `cost_base`: FIDELITY_ANCHOR. Exact current model; MUST reproduce the C24 d15
  primary-arm per-venue/per-fold PnL within +/-1.0 (`COST_ANCHOR_REPRODUCED`,
  else `COST_ANCHOR_MISMATCH` => `C25_UNDERPOWERED`).
- `cost_taker`: per-venue published taker fee ({TAKER_BPS} bps) per side + 5 bps
  slippage + $1 min commission; both legs charged.
- `cost_taker_funding`: PRIMARY. `cost_taker` + realized 8h funding on every leg.
- `cost_stress`: `cost_taker_funding` + 2x slippage + 5 bps borrow/financing.

## Inference (floors, not reducible; all four arms)

- Episode-block bootstrap: 20,000 draws
- Conditional temporal-edge permutation: 20,000 draws
- Full-portfolio placebo: 2,000 runs
- Strata permutation: 2,000 draws
- BH (alpha 0.05) family: primary arm `cost_taker_funding`, 4 folds x 4 venues = 16 tests
- Pooled: venue-blocked bootstrap over 16 (venue, fold) cells, 20,000 draws

## Funding acquisition (required for cost_taker_funding / cost_stress)

Acquire per-venue realized funding-rate history into
`research_state/cache/<venue>_funding_<window>/` with a manifest sha256 and universe
file. A venue without funding history is recorded `UNAVAILABLE_FUNDING` (never
zero-filled) and the realistic arm is evaluated on the remaining venues; the decision
rule then requires >=3 positive folds and >=3 positive venues out of the available set.

## Decision rules

- **C25_REOPENS_C1_C24**: under `cost_taker_funding` (not stress): pooled total > 0
  AND pooled CI95 lower > 0 AND >=1 BH survivor AND >=3/4 folds positive AND
  >=3/4 venues positive. Then C1-C24 `NO_GO` is not robust to realistic cost ->
  record `SUPERSEDED_BY_C25`.
- **C25_NO_GO_ROBUST_TO_COST**: any condition fails. The `NO_GO` survives realistic
  cost and the program closes as C1-C25 `NO_GO` ROBUST TO MARGIN AND COST.
- **C25_UNDERPOWERED**: anchor mismatch, draw-floor violation, drift, missing artifacts.

Both terminal outcomes require the full arm x venue x fold table, per-leg attribution
and exit-reason decomposition. No bare token. No extra configurations, thresholds or
venues - C25 is an adjudication, not a search.

## Run order

```
PYTHONPATH=. .venv/bin/python scripts/build_c25_prereg.py        # done (this file)
# funding acquisition: scripts/probe_c25_funding_acquisition.py  (before cost_taker_funding cells)
PYTHONPATH=. .venv/bin/python scripts/run_c25_cost_fidelity_campaign.py --jobs 4 --resume
PYTHONPATH=. .venv/bin/python scripts/verify_c25_focus_campaign.py   # -> C25 ACCEPTANCE: PASS
bash scripts/status_c25.sh
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
