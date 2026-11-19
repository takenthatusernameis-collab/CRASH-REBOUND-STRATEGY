#!/usr/bin/env python3
"""Build the C26 pre-registration (PRE_REGISTERED_BEFORE_COMPUTE).

C26 is an INTRABAR PATH & PER-TRADE FUNDING FIDELITY adjudication of the frozen
crash-rebound edge, not a parameter search. C1-C24 test one execution assumption
(liquidation distance); C25 tests cost/funding fidelity. The two residual same-data
fidelity gaps C25's disclosure names are:

    (a) funding applied per trade, per symbol, per timestamp (realized 8h funding
        on every held hour of every leg) instead of the C25 venue-mean scalar;
    (b) intrabar stop/target sequencing — when a 1h bar touches both the stop and
        the target (or the liquidation distance), the within-bar sequence decides
        the exit reason, order of hedge/rebound legs, and realized PnL.

C26 asks, once, with full inference:

    Is the NO_GO robust to per-trade realized funding and conservative intrabar
    path sequencing, or does the edge flip GO under these final fidelity axes?

Only funding granularity and intrabar sequencing vary. The signal path is frozen
to the C24/C25 sentinel (rsi_period=21, rsi_threshold=20, target_pct=9,
SPEC_LITERAL_NEXT_OPEN, ETH hedge on, volume sizing on, gross_cap_pct=120).
Liquidation distance is fixed at the C24-decided primary (d15: maint=14, buffer=1
=> 15%). The cost model is frozen at the C25-decided primary. Both outcomes are
terminal.

Run (from repo root):
  PYTHONPATH=. .venv/bin/python scripts/build_c26_prereg.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / "research_state"
TS = "20261119T121500Z"
OUT_JSON = STATE / f"c26_prereg_{TS}.json"
OUT_MD = STATE / f"c26_prereg_{TS}.md"

FOLDS = [
    {"id": "2023", "start": "2023-01-01T00:00:00Z", "end": "2023-12-31T23:00:00Z"},
    {"id": "2024", "start": "2024-01-01T00:00:00Z", "end": "2024-12-31T23:00:00Z"},
    {"id": "2025", "start": "2025-01-01T00:00:00Z", "end": "2025-12-31T23:00:00Z"},
    {"id": "2026YTD", "start": "2026-01-01T00:00:00Z", "end": "2026-09-28T23:00:00Z"},
]

VENUES = ["okx", "binance_um", "mexc", "bitget"]

# Venue published taker fee (bps) per side (carried from C25 prereg, 4.5-7 bps band).
TAKER_BPS = {"okx": 5.0, "binance_um": 4.5, "mexc": 6.0, "bitget": 5.5}
REFERENCE_PX = 60000.0
BORROW_BPS = 5.0

# Liquidation distance fixed at the C24 primary arm (d15): maint=14, buffer=1 => 15%.
LIQ_MAINT = 14.0
LIQ_BUFFER = 1.0
LIQ_DISTANCE_PCT = 15.0

# Frozen signal path = C24/C25 sentinel. Any artifact whose signal_path fields differ
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

# C26 arms. Only funding granularity and intrabar sequencing vary; signal path,
# liquidation distance, and cost model are frozen at the C24/C25 sentinel.
def _taker_commission_per_share(venue: str) -> float:
    return round(REFERENCE_PX * TAKER_BPS[venue] / 10000.0, 6)

ARMS = {
    "path_base": {
        "role": "FIDELITY_ANCHOR",
        "intrabar_adverse_first": False,
        "per_trade_funding": False,
        "why": "Exact C25 primary-arm model (venue-mean scalar funding, next-open "
               "fills). MUST reproduce the C25 cost_taker_funding per-venue/per-fold "
               "PnL within +/-1.0 (PATH_ANCHOR_REPRODUCED, else PATH_ANCHOR_MISMATCH).",
    },
    "path_funding_trade": {
        "role": "DESCRIPTIVE",
        "intrabar_adverse_first": False,
        "per_trade_funding": True,
        "why": "Per-trade, per-symbol, per-timestamp realized 8h funding from the "
               "acquired venue funding caches (every held hour on every leg; longs "
               "pay when rate > 0, shorts receive). okx is UNAVAILABLE_FUNDING.",
    },
    "path_intrabar_adverse_first": {
        "role": "DESCRIPTIVE",
        "intrabar_adverse_first": True,
        "per_trade_funding": False,
        "why": "Conservative intrabar sequencing: within a 1h bar that touches both "
               "the stop and the target (or liquidation), the adverse extreme is "
               "assumed to print first (stop/liquidation before target).",
    },
    "path_intrabar_combined": {
        "role": "PRIMARY",
        "intrabar_adverse_first": True,
        "per_trade_funding": True,
        "why": "Per-trade realized funding AND conservative intrabar sequencing "
               "together — the C26 primary adjudication arm.",
    },
}

PREREG = {
    "schema_version": 1,
    "campaign": "C26",
    "binding_task": "C26-T1",
    "prereg_status": "PRE_REGISTERED_BEFORE_COMPUTE",
    "generated_at_utc": "2026-11-19T12:15:00Z",
    "title": "C26 - Intrabar Path & Per-Trade Funding Fidelity Adjudication of the frozen crash-rebound edge",
    "why_c26": (
        "C25 applies funding as one venue-mean scalar per venue and prices every fill "
        "at next-open on 1h bars. Two fidelity gaps remain, both capable of flipping "
        "sign on a 9%-target, multi-day-hold, short/hedged strategy: (a) funding "
        "applied per trade, per symbol, per timestamp instead of a venue mean; (b) "
        "intrabar stop/target sequencing. C26 adjudicates whether the NO_GO survives "
        "these final same-data fidelity axes."
    ),
    "research_question": (
        "Is the pooled spec-literal PnL sign robust to per-trade realized funding and "
        "conservative intrabar path sequencing, across four independent real venues "
        "and four folds?"
    ),
    "blocked_on": (
        "C25-T1 (round-trip cost & realized-funding fidelity). C26 build may proceed "
        "before C25 passes, but no C26 cell may run until C25 ACCEPTANCE: PASS and the "
        "C25 primary-arm per-venue/per-fold PnL is available as the path_base fidelity "
        "anchor."
    ),
    "signal_path_frozen": SIGNAL_PATH_FROZEN,
    "arms": ARMS,
    "taker_bps": TAKER_BPS,
    "reference_px": REFERENCE_PX,
    "borrow_bps": BORROW_BPS,
    "arms_rule": (
        "ONLY intrabar_adverse_first / per_trade_funding vary across arms. All other "
        "config fields (signal path + liquidation distance + cost model) are identical "
        "and drift-checked. path_base is the FIDELITY_ANCHOR; path_intrabar_combined is "
        "the PRIMARY adjudication arm. All four arms run the full 4 venues x 4 folds x "
        "20k bootstrap / 20k permutation / 2k placebo — no smoke arm, no reduced draw "
        "floors, no descriptive-only arm."
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
            "family": "primary arm path_intrabar_combined, 4 folds x 4 venues = 16 permutation tests",
        },
        "draw_floor_rule": "Draws below 20000/20000/2000/2000 => UNDERPOWERED, not evidence.",
    },
    "fidelity_anchor": {
        "arm": "path_base",
        "reference": (
            "C25 primary-arm (cost_taker_funding) per-venue/per-fold PnL from "
            "research_state/c25_decision_verdict_cost_taker_funding_20261119T045500Z.json "
            "(venue_totals). Available only after C25 ACCEPTANCE: PASS."
        ),
        "tolerance_pnl": 1.0,
        "token_ok": "PATH_ANCHOR_REPRODUCED",
        "token_bad": "PATH_ANCHOR_MISMATCH => C26_UNDERPOWERED",
        "rule": "path_base must reproduce the C25 primary-arm per-venue/per-fold PnL "
                "within +/-1.0; otherwise C26 is UNDERPOWERED and no verdict may be issued.",
    },
    "funding_acquisition": {
        "required_for": ["path_funding_trade", "path_intrabar_combined"],
        "cache_layout": "research_state/cache/<venue>_funding_<window>/funding_history.csv (+ manifest)",
        "rule": (
            "A venue without realized funding history is recorded UNAVAILABLE_FUNDING "
            "(never zero-filled) and the realistic arms are evaluated on the remaining "
            "venues; okx is UNAVAILABLE_FUNDING by API retention (33-day window)."
        ),
    },
    "decision_rules": {
        "C26_REOPENS_C1_C25": (
            "ALL of, under path_intrabar_combined (PRIMARY): (a) pooled total PnL > 0; "
            "(b) venue-blocked bootstrap CI95 lower bound > 0; (c) >= 1 BH survivor in "
            "the 16-test path_intrabar_combined family; (d) >= 3 of 4 folds positive; "
            "(e) >= 3 of 4 venues positive (available venue set; okx excluded from "
            "funding arms so binance_um, mexc, bitget must all be positive). Then the "
            "C1-C25 NO_GO is NOT robust to path/funding fidelity: record "
            "SUPERSEDED_BY_C26 and the edge is re-opened."
        ),
        "C26_NO_GO_ROBUST_TO_PATH": (
            "ANY of (a)-(e) fails under path_intrabar_combined. Then the NO_GO survives "
            "per-trade funding and intrabar path fidelity and is strengthened: record "
            "C1-C26 NO_GO ROBUST TO MARGIN, COST AND PATH; same-data fidelity work is "
            "CLOSED (only new-venue data or the CLOSED Hyperliquid-native acquisition "
            "remain)."
        ),
        "C26_UNDERPOWERED": (
            "Path anchor mismatch, prereg generated after any compute artifact, draw "
            "floors not met, missing artifacts, or signal-path/cost/intrabar drift."
        ),
        "rule": ("Both REOPENS and NO_GO_ROBUST are terminal and must be reported with the "
                 "full arm x venue x fold table, per-leg attribution and exit-reason "
                 "decomposition. Never report a bare token. C26 is not a GO search: no "
                 "configuration search, no additional thresholds, no new venues beyond the four."),
    },
    "required_artifacts": [
        f"c26_prereg_{TS}.json",
        f"c26_prereg_{TS}.md",
        f"c26_decision_verdict_path_base_{TS}.json",
        f"c26_decision_verdict_path_funding_trade_{TS}.json",
        f"c26_decision_verdict_path_intrabar_adverse_first_{TS}.json",
        f"c26_decision_verdict_path_intrabar_combined_{TS}.json",
        f"c26_decision_verdict_CONSOLIDATED_{TS}.json",
    ],
    "checkpoint_rule": (
        "A (arm, venue, fold) is DONE only when research_state/c26_ckpt_<arm>_<venue>_<fold>_"
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
        "C26 varies only funding granularity and intrabar sequencing; liquidation distance "
        "fixed at the C24 primary; cost model frozen at the C25 primary.",
        "No additional venues or folds beyond those pre-registered.",
        "Artifacts are immutable once written; do not edit completed campaign outputs.",
        "No C26 cell runs until C25 ACCEPTANCE: PASS (C26 is blocked on C25 completion).",
    ],
}


def main() -> int:
    if OUT_JSON.exists() or OUT_MD.exists():
        raise SystemExit(f"refusing to overwrite existing prereg {OUT_JSON.name}")
    OUT_JSON.write_text(json.dumps(PREREG, indent=2) + "\n")

    arms_md = "\n".join(
        f"| {a} | {v['role']} | intrabar_adverse_first={v['intrabar_adverse_first']} "
        f"per_trade_funding={v['per_trade_funding']} |"
        for a, v in ARMS.items())
    md = f"""# C26 PRE-REGISTRATION - {TS}

**Status:** PRE_REGISTERED_BEFORE_COMPUTE
**Campaign:** C26-T1 - Intrabar Path & Per-Trade Funding Fidelity Adjudication
**Binding question:** {PREREG['research_question']}
**Blocked on:** C25-T1 (round-trip cost & realized-funding fidelity). No C26 cell runs
until `C25 ACCEPTANCE: PASS`.

## Why C26 exists

C1-C25 test margin (liquidation distance) and cost/funding fidelity on OKX,
Binance UM, MEXC and Bitget using the frozen spec-literal signal path. C25's
disclosure names exactly two residual fidelity gaps: (a) funding applied per trade,
per symbol, per timestamp instead of a venue-mean scalar, and (b) intrabar stop/target
sequencing on 1h bars. C26 adjudicates whether the NO_GO survives these final
same-data fidelity axes.

## Signal path (frozen = C24/C25 sentinel; drift-checked)

- rsi_period=21, rsi_threshold=20, target_pct=9, rebound_short_*,
  gross_cap=120%, volume floor $5M, sizing 1.25%, ETH hedge on,
  entry_spec_literal_next_open=True, seed=20261201.
- Liquidation distance fixed at the C24 primary arm (d15): maint=14, buffer=1 => 15%.
- Cost model frozen at the C25-decided primary.
- ONLY intrabar_adverse_first / per_trade_funding vary across arms.

## Arms (only funding granularity and intrabar sequencing vary)

| arm | role | intrabar_adverse_first | per_trade_funding |
|---|---|---|---|
{arms_md}

- `path_base`: FIDELITY_ANCHOR. C25 primary-arm model (venue-mean scalar funding);
  MUST reproduce the C25 cost_taker_funding per-venue/per-fold PnL within +/-1.0
  (`PATH_ANCHOR_REPRODUCED`, else `PATH_ANCHOR_MISMATCH` => `C26_UNDERPOWERED`).
- `path_funding_trade`: per-trade/per-symbol/per-timestamp realized 8h funding from
  the acquired caches; every held hour on every leg.
- `path_intrabar_adverse_first`: conservative intrabar sequencing (adverse extreme
  before favourable within a bar).
- `path_intrabar_combined`: PRIMARY. Per-trade funding AND conservative intrabar
  sequencing together.

## Inference (floors, not reducible; all four arms)

- Episode-block bootstrap: 20,000 draws
- Conditional temporal-edge permutation: 20,000 draws
- Full-portfolio placebo: 2,000 runs
- Strata permutation: 2,000 draws
- BH (alpha 0.05) family: primary arm `path_intrabar_combined`, 4 folds x 4 venues = 16 tests
- Pooled: venue-blocked bootstrap over 16 (venue, fold) cells, 20,000 draws

## Funding acquisition (required for path_funding_trade / path_intrabar_combined)

Per-venue realized funding-rate history is cached in
`research_state/cache/<venue>_funding_<window>/funding_history.csv` with a manifest.
okx is `UNAVAILABLE_FUNDING` by API retention (33-day window) and is excluded from
funding arms; the decision rule then requires >=3 positive folds and >=3 positive
venues out of the available set (binance_um, mexc, bitget all positive).

## Decision rules

- **C26_REOPENS_C1_C25**: under `path_intrabar_combined` (not stress): pooled total > 0
  AND pooled CI95 lower > 0 AND >=1 BH survivor AND >=3/4 folds positive AND
  >=3/4 venues positive. Then C1-C25 `NO_GO` is not robust to path/funding fidelity ->
  record `SUPERSEDED_BY_C26`.
- **C26_NO_GO_ROBUST_TO_PATH**: any condition fails. The `NO_GO` survives per-trade
  funding and intrabar path fidelity; program closes as C1-C26 `NO_GO` ROBUST TO
  MARGIN, COST AND PATH.
- **C26_UNDERPOWERED**: anchor mismatch, draw-floor violation, drift, missing artifacts.

Both terminal outcomes require the full arm x venue x fold table, per-leg attribution
and exit-reason decomposition. No bare token. No extra configurations, thresholds or
venues - C26 is an adjudication, not a search.

## Run order

```
PYTHONPATH=. .venv/bin/python scripts/build_c26_prereg.py        # done (this file)
# after C25 ACCEPTANCE: PASS:
PYTHONPATH=. .venv/bin/python scripts/run_c26_path_fidelity_campaign.py --jobs 4 --resume
PYTHONPATH=. .venv/bin/python scripts/verify_c26_focus_campaign.py   # -> C26 ACCEPTANCE: PASS
bash scripts/status_c26.sh
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
