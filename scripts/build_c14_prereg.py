#!/usr/bin/env python3
"""Build a gate-valid C14 preregistration (prereg-before-compute).

C14 is the broad-universe native power escalation: validate/falsify the
crash-rebound edge on the widest available verified Hyperliquid-native Ironflow
archive with dependence-aware inference. The spec-literal canonical config is
pre-registered (RSI 21 < 20, target 9%, rebound short on, ETH hedge on, $5M
volume gate) to avoid post-hoc config selection. A new config requires a new
prereg and new stems.

Writes prereg JSON + markdown and refuses to overwrite unless --force.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any, Dict

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

TS = "20261116T001200Z"
ARCHIVE = "research_state/archives/hyperliquid_ironflow_wide_20261115T214900Z"
CACHE_DIR = "research_state/cache/hyperliquid_ironflow_wide_20261115T234000Z"
UNIVERSE = "research_state/universe_hyperliquid_ironflow_wide_20261115T225100Z.json"
CENSUS = f"research_state/crash_event_census_hyperliquid_ironflow_wide_{TS}.json"
CAMPAIGN = f"research_state/campaign_results_real_hyperliquid_ironflow_wide_{TS}.json"
INTAKE = "research_state/archive_intake_validation_20261116T001129Z.json"
PROVENANCE_CAVEAT = (
    "Real Hyperliquid-native, node-derived (Ironflow HF, CC BY 4.0), NOT venue "
    "candleSnapshot. Real fetched/archived candles, non-synthetic. 283d window "
    "2025-12-20T00:00:00Z–2026-09-28T23:00:00Z. Performance evidence only when "
    "produced by the full decision-grade battery under this prereg."
)


def build(seed: int, min_draws: int, episode_draws: int, placebo_draws: int, generated_at: str) -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "campaign": "C14",
        "generated_at_utc": generated_at,
        "label": "HYPERLIQUID_NATIVE_C14_BROAD_UNIVERSE_POWER_ESCALATION",
        "status": "PRE_REGISTERED_BEFORE_COMPUTE",
        "real_market_data": True,
        "is_hyperliquid_venue_data": True,
        "fabricated_data": False,
        "synthetic_data": False,
        "provenance_caveat": PROVENANCE_CAVEAT,
        "inputs": {
            "archive_dir": ARCHIVE,
            "intake_validation": INTAKE,
            "cache_dir": CACHE_DIR,
            "universe_file": UNIVERSE,
            "census_planned": CENSUS,
            "campaign_planned": CAMPAIGN,
            "priors": {
                "consolidated_final": "research_state/decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z.md",
                "cross_venue_c10": "research_state/decision_verdict_consolidated_20261115T122636Z.md",
                "native_c11_3": "research_state/decision_verdict_hyperliquid_native_20261115T155318Z.md",
                "native_c12": "research_state/decision_verdict_hyperliquid_native_c12_20261115T181500Z.md",
                "native_c13": "research_state/decision_verdict_hyperliquid_native_c13_20261115T203734Z.md",
                "power_target": "research_state/power_target_hyperliquid_20261114T172700Z.md",
            },
        },
        "hypothesis": {
            "id": "H1_c14_broad_universe_canonical",
            "description": (
                "Broad-universe Hyperliquid-native (Ironflow) power escalation of the spec "
                "crash-rebound strategy to raise effective independent crash episodes toward "
                "the decision floor, evaluated with dependence-aware inference."
            ),
            "config": {
                "rsi_threshold": 20.0,
                "rsi_period": 21,
                "target_pct": 9.0,
                "rebound_short_target_pct": 9.0,
                "rebound_short_time_exit_bars": 48,
                "enable_rebound_short": True,
                "enable_eth_hedge": True,
                "min_daily_volume_usd": 5000000.0,
                "entry_spec_literal_next_open": False,
            },
            "selection_rule": "Fixed by this prereg; no config switching after results.",
        },
        "inference_plan": {
            "dependence_aware": True,
            "seed": seed,
            "min_draws": min_draws,
            "draws": episode_draws,
            "placebo_draws": placebo_draws,
            "methods": [
                "episode_block_bootstrap_CI95_spot_hedge_rebound_total",
                "conditional_temporal_edge_permutation_p",
                "portfolio_placebo_admission_selection_p_ge_canonical",
                "crash_event_census_alignment",
                "leg_separation_spot_eth_hedge_rebound_short",
            ],
            "power": (
                f"Minimum floor: {min_draws} permutation draws and {min_draws} placebo subsets. "
                "GO requires >=10 trades, >=5 episodes, >=5 distinct crash days, bootstrap 95% CI "
                "excluding 0, permutation p<0.05, placebo p_ge_canonical<0.05, and spot leg > 0. "
                "If unmet, verdict must be UNDERPOWERED or NO_GO with a quantified power curve."
            ),
        },
        "decision_rules": {
            "go": (
                "GO only if all hold: episode-block bootstrap 95% CI excludes 0 (spot or total with "
                "positive spot), permutation p < 0.05, placebo p_ge_canonical < 0.05, and effective "
                "N >= 10 trades / 5 episodes / 5 crash days."
            ),
            "no_go": [
                "CI95 spans 0 for spot and total",
                "permutation p >= 0.05 or placebo p_ge_canonical >= 0.05",
                "positive total entirely hedge/rebound-masked with non-positive spot",
                "census/funnel shows no reproducible edge on widened universe",
            ],
            "underpowered": [
                "Effective sample below floor; label UNDERPOWERED/FRAGILE_NOT_DECISION_GRADE",
                "Missing seed/SHA binding or compute predating this prereg",
            ],
            "power_curve_required_if_not_go": True,
        },
        "power_targets": {
            "min_episode_block_bootstrap_draws": min_draws,
            "min_permutation_draws": episode_draws,
            "min_placebo_subsets": placebo_draws,
            "min_effective_trades_for_go": 10,
            "min_effective_episodes_for_go": 5,
            "min_distinct_crash_days_for_go": 5,
            "alpha": 0.05,
        },
    }


def render_md(data: Dict[str, Any]) -> str:
    p = data["power_targets"]; i = data["inference_plan"]
    return f"""# C14 preregistration — Hyperliquid-native broad-universe power escalation

**Generated (UTC):** {data['generated_at_utc']}
**Status:** {data['status']} — fixed BEFORE any C14 compute.
**Provenance:** {data['provenance_caveat']}

## Objective
Raise effective independent crash-episode N by using the widest verified Hyperliquid-native Ironflow archive, then run the full dependence-aware validation battery and issue a GO/UNDERPOWERED/NO_GO verdict with a power curve if not GO.

## Inputs (fixed)
- Archive: `{data['inputs']['archive_dir']}` (intake: `{data['inputs']['intake_validation']}`)
- Cache: `{data['inputs']['cache_dir']}`
- Universe: `{data['inputs']['universe_file']}`
- Planned census: `{data['inputs']['census_planned']}`
- Planned campaign: `{data['inputs']['campaign_planned']}`

## Config (fixed, spec-canonical)
- RSI(21) < 20, target 9%, rebound short 9%/48h, ETH hedge on, min_daily_volume_usd $5M, no config switching post-results.

## Dependence-aware inference (required)
- Episode-block bootstrap 95% CI (spot/hedge/rebound/total)
- Conditional temporal-edge permutation
- Portfolio placebo (admission/selection)
- Census alignment + leg separation

## Floors / power (pre-registered)
- Seed **{i['seed']}**; min draws **{data['power_targets']['min_permutation_draws']}** permutation, **{data['power_targets']['min_placebo_subsets']}** placebo (heavy-compute floor **{i['min_draws']}**).
- GO needs >= {p['min_effective_trades_for_go']} trades / {p['min_effective_episodes_for_go']} episodes / {p['min_distinct_crash_days_for_go']} crash days, CI95 excludes 0, permutation p<0.05, placebo p_ge_canonical<0.05, spot leg > 0.
- If not GO: verdict **UNDERPOWERED** or **NO_GO** with a quantified **power curve** (episodes required at observed variance; max episodes achievable from C14 archive).

## Priors (must be referenced by verdict)
- {data['inputs']['priors']['native_c11_3']}
- {data['inputs']['priors']['native_c12']}
- {data['inputs']['priors']['native_c13']}
- {data['inputs']['priors']['cross_venue_c10']}
- {data['inputs']['priors']['consolidated_final']}
"""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int, default=20261116)
    ap.add_argument('--min-draws', type=int, default=100)
    ap.add_argument('--episode-draws', type=int, default=20000)
    ap.add_argument('--placebo-draws', type=int, default=2000)
    ap.add_argument('--force', action='store_true')
    args = ap.parse_args(argv)
    stem = f"hyperliquid_native_c14_prereg_{TS}"
    jpath = REPO / 'research_state' / f'{stem}.json'
    mpath = REPO / 'research_state' / f'{stem}.md'
    if jpath.exists() and not args.force:
        print(f'EXISTS (use --force to overwrite): {jpath}', file=sys.stderr)
        return 2
    generated_at = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    data = build(args.seed, args.min_draws, args.episode_draws, args.placebo_draws, generated_at)
    jpath.write_text(json.dumps(data, indent=2) + '\n')
    mpath.write_text(render_md(data))
    print(f'WROTE {jpath}')
    print(f'WROTE {mpath}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
