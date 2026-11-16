#!/usr/bin/env python3
"""Build a gate-valid C20 preregistration (prereg-before-compute).

C20 is the cross-venue spec-faithful replication + pooled synthesis campaign.

WHY C20 EXISTS (and why the prior "CLOSED / do nothing" handoff is rescinded)
---------------------------------------------------------------------------
C19 adjudicated the entry-rule fork and found ``SPEC_LITERAL_NEXT_OPEN`` is the
spec-faithful reading (spec text: "Buy at next hourly open", no same-bar rebound
confirmation). On the retained 283-day Hyperliquid-native archive that reading is
decisively negative (C18/C19: 22 trades, -47,933.58, NO_GO).

But every multi-year cross-venue campaign (C6 OKX, C8 Binance UM) was run under
the *canonical same-bar* reading (``entry_spec_literal_next_open=False``). The
spec-faithful reading has therefore never been tested out-of-sample on the two
independent multi-year venues. That is the one remaining executable,
decision-relevant question on already-verified real data:

    Does the adjudicated spec-faithful crash-rebound rule also lose (or win)
    across two independent venues and 3.4 years, or does it diverge from native?

C20 answers it with the full dependence-aware battery and a pooled cross-venue
synthesis. It does NOT acquire new data, does NOT relabel cross-venue as
Hyperliquid-native, does NOT relax the spec, and does NOT churn inference on the
exhausted C14 native data.

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

TS = "20261116T063500Z"

OKX_CACHE = "research_state/cache/okx_1h_multiyear_20230101_20260928"
OKX_UNIVERSE = "research_state/universe_okx_multiyear_verified.json"
OKX_CAMPAIGN = "research_state/campaign_results_real_okx_multiyear.json"
OKX_CENSUS = "research_state/crash_event_census_real_okx_multiyear.json"

BIN_CACHE = "research_state/cache/binance_um_1h_multiyear_20230101_20260928"
BIN_UNIVERSE = "research_state/universe_binance_um_multiyear_verified.json"
BIN_CAMPAIGN = "research_state/campaign_results_real_binance_um_multiyear.json"
BIN_CENSUS = "research_state/crash_event_census_real_binance_um_multiyear.json"

PROVENANCE_CAVEAT = (
    "Real OKX / Binance UM exchange data, non-synthetic, CROSS-VENUE vs the "
    "Hyperliquid spec; NOT Hyperliquid performance evidence and must never be "
    "relabelled as such. Multi-year window 2023-01-01T00:00:00Z.."
    "2026-09-28T23:00:00Z (32808 hourly bars/symbol). Performance evidence only "
    "when produced by the full decision-grade battery under this prereg."
)


def build(seed: int, min_draws: int, episode_draws: int, placebo_draws: int,
          generated_at: str) -> Dict[str, Any]:
    okx_campaign = f"research_state/campaign_results_real_okx_multiyear_specliteral_{TS}.json"
    bin_campaign = f"research_state/campaign_results_real_binance_um_multiyear_specliteral_{TS}.json"
    return {
        "schema_version": 1,
        "campaign": "C20",
        "generated_at_utc": generated_at,
        "label": "CROSS_VENUE_SPEC_LITERAL_REPLICATION_AND_POOLED_SYNTHESIS",
        "status": "PRE_REGISTERED_BEFORE_COMPUTE",
        "real_market_data": True,
        "is_hyperliquid_venue_data": False,
        "cross_venue": True,
        "fabricated_data": False,
        "synthetic_data": False,
        "provenance_caveat": PROVENANCE_CAVEAT,
        "objective": (
            "Run the C19-adjudicated spec-faithful entry rule (SPEC_LITERAL_NEXT_OPEN) "
            "on both independent multi-year cross-venue archives (OKX, Binance UM) with "
            "the full dependence-aware battery, then issue one cross-venue verdict plus a "
            "pooled venue-blocked synthesis. This closes the gap that all prior cross-venue "
            "evidence used the canonical same-bar reading while C19 adjudicated spec-literal "
            "as faithful."
        ),
        "binding_task": (
            "C19-T1 adjudicated SPEC_LITERAL_NEXT_OPEN as the spec-faithful reading. The "
            "native verdict under that reading is NO_GO. C20 tests whether that verdict "
            "replicates out-of-sample across two independent venues and 3.4 years, or "
            "diverges. Either outcome is decision-relevant and must be reported honestly."
        ),
        "inputs_fixed": {
            "okx": {
                "cache_dir": OKX_CACHE,
                "universe": OKX_UNIVERSE,
                "canonical_campaign_same_bar": OKX_CAMPAIGN,
                "canonical_census_same_bar": OKX_CENSUS,
                "planned_campaign_spec_literal": okx_campaign,
                "planned_census_spec_literal": f"research_state/crash_event_census_real_okx_multiyear_specliteral_{TS}.json",
                "planned_episode_edge": f"research_state/episode_edge_okx_multiyear_specliteral_{TS}.json",
                "planned_placebo": f"research_state/placebo_portfolio_okx_multiyear_specliteral_{TS}.json",
                "planned_battery": f"research_state/multiyear_robustness_battery_okx_specliteral_{TS}.json",
            },
            "binance_um": {
                "cache_dir": BIN_CACHE,
                "universe": BIN_UNIVERSE,
                "canonical_campaign_same_bar": BIN_CAMPAIGN,
                "canonical_census_same_bar": BIN_CENSUS,
                "planned_campaign_spec_literal": bin_campaign,
                "planned_census_spec_literal": f"research_state/crash_event_census_real_binance_um_multiyear_specliteral_{TS}.json",
                "planned_episode_edge": f"research_state/episode_edge_binance_um_multiyear_specliteral_{TS}.json",
                "planned_placebo": f"research_state/placebo_portfolio_binance_um_multiyear_specliteral_{TS}.json",
                "planned_battery": f"research_state/multiyear_robustness_battery_binance_um_specliteral_{TS}.json",
            },
            "priors": {
                "c19_adjudication": "research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.json",
                "c19_native_verdict": "research_state/decision_verdict_hyperliquid_native_c19_20261116T054000Z.md",
                "consolidated_final": "research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.md",
                "cross_venue_c10": "research_state/decision_verdict_consolidated_20261115T122636Z.md",
                "okx_multiyear_battery": "research_state/multiyear_robustness_battery_20261115T011700Z.json",
                "binance_multiyear_battery": "research_state/multiyear_robustness_battery_binance_um.json",
            },
            "pooled_synthesis_planned": f"research_state/c20_pooled_cross_venue_synthesis_{TS}.json",
            "verdict_planned": f"research_state/decision_verdict_cross_venue_specliteral_c20_{TS}.json",
            "consolidated_planned": f"research_state/decision_verdict_CONSOLIDATED_FINAL_{TS}.json",
        },
        "hypothesis": {
            "id": "H1_c20_spec_literal_cross_venue",
            "description": (
                "Under the C19-adjudicated spec-faithful entry rule, the crash-rebound "
                "strategy's cross-venue multi-year edge is measured on two independent "
                "venues and pooled with venue-blocked dependence-aware inference."
            ),
            "config": {
                "rsi_period": 21,
                "rsi_threshold": 20.0,
                "target_pct": 9.0,
                "rebound_short_target_pct": 9.0,
                "rebound_short_time_exit_bars": 48,
                "enable_rebound_short": True,
                "enable_eth_hedge": True,
                "min_daily_volume_usd": 5000000.0,
                "gross_cap_pct": 120.0,
                "entry_spec_literal_next_open": True,
            },
            "selection_rule": "Fixed by this prereg; no config switching after results.",
        },
        "required_artifacts": {
            "prereg": f"research_state/c20_prereg_{TS}.{{json,md}}",
            "okx_campaign": f"research_state/campaign_results_real_okx_multiyear_specliteral_{TS}.json",
            "binance_campaign": f"research_state/campaign_results_real_binance_um_multiyear_specliteral_{TS}.json",
            "okx_census": f"research_state/crash_event_census_real_okx_multiyear_specliteral_{TS}.json",
            "binance_census": f"research_state/crash_event_census_real_binance_um_multiyear_specliteral_{TS}.json",
            "okx_episode_edge": f"research_state/episode_edge_okx_multiyear_specliteral_{TS}.json",
            "binance_episode_edge": f"research_state/episode_edge_binance_um_multiyear_specliteral_{TS}.json",
            "okx_placebo": f"research_state/placebo_portfolio_okx_multiyear_specliteral_{TS}.json",
            "binance_placebo": f"research_state/placebo_portfolio_binance_um_multiyear_specliteral_{TS}.json",
            "okx_battery": f"research_state/multiyear_robustness_battery_okx_specliteral_{TS}.json",
            "binance_battery": f"research_state/multiyear_robustness_battery_binance_um_specliteral_{TS}.json",
            "pooled_synthesis": f"research_state/c20_pooled_cross_venue_synthesis_{TS}.json",
            "verdict": f"research_state/decision_verdict_cross_venue_specliteral_c20_{TS}.{{json,md}}",
            "consolidated_final": f"research_state/decision_verdict_CONSOLIDATED_FINAL_{TS}.{{json,md}}",
            "handoff": "HANDOFF.md must reference C20-T1 and verify_c20_focus_campaign.py",
        },
        "inference_plan": {
            "dependence_aware": True,
            "seed": seed,
            "min_draws": min_draws,
            "draws": episode_draws,
            "placebo_draws": placebo_draws,
            "methods": [
                "per_venue_episode_block_bootstrap_CI95_spot_hedge_rebound_total",
                "per_venue_conditional_temporal_edge_permutation_p",
                "per_venue_full_portfolio_placebo_p_ge_canonical",
                "per_venue_crash_event_census_alignment",
                "per_venue_leg_separation_spot_eth_hedge_rebound_short",
                "pooled_venue_blocked_bootstrap_over_venue_episode_totals",
                "pooled_sign_concordance_and_magnitude_ci",
            ],
            "power": (
                f"Minimum heavy-compute floor: {min_draws} permutation draws and {min_draws} "
                f"placebo subsets per venue; target {episode_draws} bootstrap/permutation draws "
                f"and {placebo_draws} placebo subsets. GO requires >=10 trades, >=5 episodes, "
                ">=5 distinct crash days, bootstrap 95% CI excluding 0, permutation p<0.05, "
                "placebo p_ge_canonical<0.05, and a positive spot leg. If unmet, verdict must be "
                "UNDERPOWERED or NO_GO with a quantified power curve."
            ),
        },
        "decision_rules": {
            "go": (
                "GO only if all hold in the pooled synthesis: episode-block bootstrap 95% CI "
                "excludes 0 with positive spot leg, permutation p < 0.05, placebo "
                "p_ge_canonical < 0.05, and effective N >= 10 trades / 5 episodes / 5 crash days."
            ),
            "no_go": [
                "pooled CI95 spans 0 for spot and total",
                "permutation p >= 0.05 or placebo p_ge_canonical >= 0.05",
                "positive total entirely hedge/rebound-masked with non-positive spot",
                "spec-literal reading is negative in both venues (corroborates C19 NO_GO)",
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
        "guardrails": [
            "No cross-venue relabeling as Hyperliquid-native evidence.",
            "No synthetic gap-fill presented as verified.",
            "No spec relaxation to manufacture a GO; SPEC_LITERAL_NEXT_OPEN is the fixed reading.",
            "No inference-only churn on exhausted C14 native data.",
            "No silent change to the canonical baseline; the spec-literal flag is opt-in and default false.",
            "C20 is executable on already-verified real archives; acquisition stays closed.",
        ],
    }


def render_md(data: Dict[str, Any]) -> str:
    p = data["power_targets"]
    i = data["inference_plan"]
    inp = data["inputs_fixed"]
    return f"""# C20 preregistration — cross-venue spec-faithful replication & pooled synthesis

**Generated (UTC):** {data['generated_at_utc']}
**Status:** {data['status']} — fixed BEFORE any C20 compute.
**Provenance:** {data['provenance_caveat']}

## Objective
Run the C19-adjudicated spec-faithful entry rule (`SPEC_LITERAL_NEXT_OPEN`) on both
independent multi-year cross-venue archives (OKX, Binance UM) with the full
dependence-aware battery, then issue one cross-venue verdict plus a pooled
venue-blocked synthesis.

## Why this is the binding task
C19 adjudicated `SPEC_LITERAL_NEXT_OPEN` as the spec-faithful reading and the native
verdict under it is `NO_GO`. Every multi-year cross-venue campaign to date used the
canonical same-bar reading, so the spec-faithful reading has never been tested
out-of-sample across venues. C20 closes that gap on already-verified real data.

## Inputs (fixed)
- OKX: cache `{inp['okx']['cache_dir']}`, universe `{inp['okx']['universe']}`, canonical same-bar campaign `{inp['okx']['canonical_campaign_same_bar']}`
- Binance UM: cache `{inp['binance_um']['cache_dir']}`, universe `{inp['binance_um']['universe']}`, canonical same-bar campaign `{inp['binance_um']['canonical_campaign_same_bar']}`
- Priors: C19 adjudication `{inp['priors']['c19_adjudication']}`, C19 native verdict `{inp['priors']['c19_native_verdict']}`

## Config (fixed, spec-faithful)
- RSI(21) < 20, target 9%, rebound short 9%/48h, ETH hedge on, $5M volume gate,
  `entry_spec_literal_next_open=true`. No config switching post-results.

## Dependence-aware inference (required)
- Per-venue episode-block bootstrap 95% CI (spot/hedge/rebound/total)
- Per-venue conditional temporal-edge permutation
- Per-venue full-portfolio placebo (admission/selection)
- Per-venue census alignment + leg separation
- Pooled venue-blocked bootstrap + sign-concordance/magnitude CI

## Floors / power (pre-registered)
- Seed **{i['seed']}**; min draws **{p['min_episode_block_bootstrap_draws']}**; target **{p['min_permutation_draws']}** bootstrap/permutation and **{p['min_placebo_subsets']}** placebo per venue.
- GO needs >= {p['min_effective_trades_for_go']} trades / {p['min_effective_episodes_for_go']} episodes / {p['min_distinct_crash_days_for_go']} crash days, CI95 excludes 0, permutation p<0.05, placebo p_ge_canonical<0.05, spot leg > 0.
- If not GO: verdict **UNDERPOWERED** or **NO_GO** with a quantified **power curve**.

## Priors (must be referenced by verdict)
- {inp['priors']['c19_adjudication']}
- {inp['priors']['c19_native_verdict']}
- {inp['priors']['consolidated_final']}
- {inp['priors']['cross_venue_c10']}
- {inp['priors']['okx_multiyear_battery']}
- {inp['priors']['binance_multiyear_battery']}
"""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int, default=20261120)
    ap.add_argument('--min-draws', type=int, default=100)
    ap.add_argument('--episode-draws', type=int, default=20000)
    ap.add_argument('--placebo-draws', type=int, default=2000)
    ap.add_argument('--force', action='store_true')
    args = ap.parse_args(argv)
    stem = f"c20_prereg_{TS}"
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