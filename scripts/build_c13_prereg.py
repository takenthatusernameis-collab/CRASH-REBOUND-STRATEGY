#!/usr/bin/env python3
"""Build a gate-valid C13 preregistration (prereg-before-compute).

C13 is the pre-registered decision-grade validation of the C12 lead
(`rsi_threshold 25, target_pct 9`) on Hyperliquid-native evidence. This script
writes the prereg JSON + markdown with the analysis plan fixed BEFORE any C13
compute, then validates it with `scripts/verify_c13_focus_campaign.check_prereg`.

It refuses to overwrite an existing prereg unless --force is given, so a session
cannot silently rewrite the plan after seeing results.

Usage:
    PYTHONPATH=. python scripts/build_c13_prereg.py

Outputs (new stems only):
    research_state/hyperliquid_native_c13_prereg_<UTC>.json
    research_state/hyperliquid_native_c13_prereg_<UTC>.md
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

from scripts.verify_c13_focus_campaign import MIN_DRAWS, check_prereg  # noqa: E402

PROVENANCE_CAVEAT = (
    "Real Hyperliquid-native, node-derived (Ironflow HF, CC BY 4.0), NOT venue "
    "candleSnapshot. Real fetched/archived candles, non-synthetic. 283d window "
    "2025-12-20T00:00:00Z–2026-09-28T23:00:00Z."
)

CACHE_DIR = "research_state/cache/hyperliquid_ironflow_native_20251220_20260928"
UNIVERSE = "research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json"
LEAD_CENSUS = "research_state/crash_event_census_hyperliquid_native_c12_rsi25_t9_20261115T180000Z.json"
LEAD_CAMPAIGN = "research_state/campaign_results_real_hyperliquid_native_c12_rsi25_t9_20261115T180000Z.json"


def build_prereg(seed: int, min_draws: int, episode_draws: int,
                 placebo_draws: int, generated_at: str) -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "campaign": "C13",
        "generated_at_utc": generated_at,
        "label": "HYPERLIQUID_NATIVE_C13_PREREGISTERED_DECISION_GRADE_VALIDATION",
        "status": "PRE_REGISTERED_BEFORE_COMPUTE",
        "real_market_data": True,
        "is_hyperliquid_venue_data": True,
        "fabricated_data": False,
        "synthetic_data": False,
        "provenance_caveat": PROVENANCE_CAVEAT,
        "inputs": {
            "cache_dir": CACHE_DIR,
            "universe_file": UNIVERSE,
            "lead_census": LEAD_CENSUS,
            "lead_campaign": LEAD_CAMPAIGN,
            "canonical_anchor_campaign": "research_state/campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json",
            "canonical_anchor_census": "research_state/crash_event_census_hyperliquid_ironflow_native_20261115T155226Z.json",
            "canonical_anchor_episode_edge": "research_state/episode_edge_hyperliquid_native_20261115T155318Z.json",
            "canonical_anchor_placebo": "research_state/placebo_portfolio_hyperliquid_native_20261115T155625Z.json",
            "canonical_anchor_verdict": "research_state/decision_verdict_hyperliquid_native_20261115T155318Z.md",
        },
        "hypotheses": [
            {
                "id": "H1_c12_lead_rsi25_target9",
                "description": (
                    "Validate or falsify the C12 in-sample lead (RSI(21) crash threshold 25, "
                    "long target 9%) on Hyperliquid-native evidence with dependence-aware inference."
                ),
                "rsi_threshold": 25.0,
                "target_pct": 9.0,
                "origin_note": (
                    "C12 discovery only (c12_25_9: 17 trades / 10 episodes / 11 crash days, "
                    "total +23,244.22; episode-block bootstrap CI95 spans 0). Hypothesis-generating, "
                    "NOT a validated GO."
                ),
            }
        ],
        "grid": {
            "design": "single_preregistered_lead_config",
            "rsi_threshold": 25.0,
            "target_pct": 9.0,
            "canonical_anchor": {"rsi_threshold": 20.0, "target_pct": 9.0, "reuse_existing_anchor_stem": True},
            "fixed_unless_overridden": {
                "rsi_period": 21,
                "rebound_short_target_pct": 9.0,
                "rebound_short_time_exit_bars": 48,
                "rebound_short_require_bounce_confirm": False,
                "entry_spec_literal_next_open": False,
                "enable_rebound_short": True,
                "enable_eth_hedge": True,
                "min_daily_volume_usd": 5000000.0,
            },
        },
        "primary_metrics": [
            "spot_coin_pnl_total",
            "eth_hedge_pnl_total",
            "rebound_short_pnl_total",
            "total_pnl",
            "trade_count",
            "episode_count",
            "crash_days_count",
            "max_drawdown_or_observed",
            "cost_stress_sensitivity_if_available",
        ],
        "secondary_metrics": [
            "exit_reasons_distribution",
            "per_symbol_leg_decomposition",
            "win_loss_profile",
            "signal_gate_event_count",
        ],
        "inference_plan": {
            "dependence_aware": True,
            "seed": seed,
            "min_draws": min_draws,
            "draws": episode_draws,
            "placebo_draws": placebo_draws,
            "methods": [
                "episode_block_bootstrap_CI_for_spot_hedge_rebound_total (episode-level dependence unit)",
                "conditional_temporal_edge_permutation_p (real-engine, config-matched)",
                "portfolio_placebo_admission_selection_p_ge_canonical (real-engine, config-matched)",
                "crash_event_census_alignment (events, signal-gate, trades, episodes/clustering)",
            ],
            "power": (
                f"Minimum heavy-compute floor: {min_draws} permutation draws and {min_draws} placebo "
                "subsets. Minimum effective sample for any GO claim: 10 trades, 5 episodes, "
                "5 distinct crash days. The C12 lead has 17 trades / 10 episodes / 11 crash days "
                "on a 283d native window, which is structurally underpowered."
            ),
            "honest_power_handling": (
                "Report effective N, episodes, crash days, CI95, permutation p and placebo p for every "
                "claim. Label underpowered when criteria are unmet. Never claim GO from point PnL, "
                "hedge-masked totals, in-sample discovery, or a CI that spans 0."
            ),
            "lead_config_selection_rule": (
                "The lead is fixed by this prereg (rsi 25 / target 9). Do not switch configs after "
                "seeing C13 results; a new config requires a new prereg and a new stem."
            ),
        },
        "decision_rules": {
            "go": (
                "GO only if the pre-registered dependence-aware criteria all hold: episode-block "
                "bootstrap CI95 for spot or total excludes 0 with effective N >= 10 trades / "
                "5 episodes / 5 crash days, AND config-matched permutation p < 0.05, AND "
                "config-matched placebo p_ge_canonical < 0.05, AND the result is not hedge-masked "
                "(spot leg reported separately)."
            ),
            "no_go": [
                "CI95 spans 0 for spot and total",
                "permutation p >= 0.05 or placebo p_ge_canonical >= 0.05",
                "positive total is entirely hedge/rebound-masked with negative spot",
                "effective sample below the pre-registered floor",
            ],
            "insufficient": [
                "Effective sample below floor: label UNDERPOWERED / FRAGILE_NOT_DECISION_GRADE",
                "Artifacts missing seed/SHA binding or generated before this prereg",
            ],
            "stop_go": (
                "Canonical RSI(21)<20 stays NO_GO unless re-validated under a new prereg. "
                "A C13 NO_GO/UNDERPOWERED result preserves canonical NO_GO."
            ),
        },
        "power_targets": {
            "min_episode_block_bootstrap_draws": min_draws,
            "min_permutation_draws": episode_draws,
            "min_placebo_subsets": placebo_draws,
            "min_effective_trades_for_go": 10,
            "min_effective_episodes_for_go": 5,
            "min_distinct_crash_days_for_go": 5,
            "alpha": 0.05,
            "ci": "95% episode-block bootstrap",
        },
        "runner": {
            "episode_edge": "scripts/run_episode_edge_okx_multiyear.py",
            "placebo": "scripts/run_portfolio_placebo_okx.py",
            "notes": (
                "Both runners must be invoked with --rsi-threshold 25 --target-pct 9 and the C12 lead "
                "census/campaign paths. Each writes a config block with config_matched=true and records "
                "seed + campaign/census SHA256. Do not overwrite canonical artifacts."
            ),
        },
    }


def render_md(data: Dict[str, Any], seed: int, min_draws: int,
              episode_draws: int, placebo_draws: int) -> str:
    plan = data["inference_plan"]
    return f"""# C13 preregistration — Hyperliquid-native decision-grade validation

**Generated (UTC):** {data['generated_at_utc']}
**Status:** {data['status']} — fixed BEFORE any C13 compute.
**Provenance:** {data['provenance_caveat']}

## Lead hypothesis (fixed)

- `rsi_threshold`: **25**
- `target_pct`: **9**
- Origin: C12 discovery only (`c12_25_9`: 17 trades / 10 episodes / 11 crash days, total +23,244.22; episode-block bootstrap CI95 spans 0). Not a validated GO.
- The config is fixed by this prereg. A different config requires a new prereg and a new artifact stem.

## Inputs

- cache: `{data['inputs']['cache_dir']}`
- universe: `{data['inputs']['universe_file']}`
- lead census: `{data['inputs']['lead_census']}`
- lead campaign: `{data['inputs']['lead_campaign']}`

## Dependence-aware inference (required for any claim)

- Episode-block bootstrap CI95 for spot / ETH hedge / rebound short / total.
- Config-matched conditional temporal-edge permutation.
- Config-matched portfolio placebo (admission/cap/occupancy selection).
- Census alignment: events, signal-gate passes, trades, episodes, crash days.

## Pre-registered floors and power

- Seed: **{seed}**
- Minimum heavy-compute floor: **{min_draws}** permutation draws and **{min_draws}** placebo subsets.
- Planned compute: **{episode_draws}** permutation draws, **{placebo_draws}** placebo subsets.
- Minimum effective sample for GO: **10 trades / 5 episodes / 5 distinct crash days**.
- The 283d native window is structurally underpowered; report effective N and label underpowered honestly.

## Decision rules

- **GO** only if all hold: {data['decision_rules']['go']}
- **NO_GO** if any: {'; '.join(data['decision_rules']['no_go'])}
- **UNDERPOWERED / FRAGILE** if: {'; '.join(data['decision_rules']['insufficient'])}
- Canonical RSI(21)<20 remains **NO_GO** unless re-validated under a new prereg.

## Commands (run after this file exists)

```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_episode_edge_okx_multiyear.py \\
  --draws {episode_draws} --seed {seed} --rsi-threshold 25 --target-pct 9 \\
  --cache-dir {data['inputs']['cache_dir']} \\
  --universe {data['inputs']['universe_file']} \\
  --census {data['inputs']['lead_census']} \\
  --campaign {data['inputs']['lead_campaign']} \\
  --venue-label 'Hyperliquid (Ironflow node-derived, native)' \\
  --out episode_edge_hyperliquid_native_c13_<TS>Z

PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_okx.py \\
  --draws {placebo_draws} --seed {seed} --rsi-threshold 25 --target-pct 9 \\
  --cache-dir {data['inputs']['cache_dir']} \\
  --universe {data['inputs']['universe_file']} \\
  --census {data['inputs']['lead_census']} \\
  --campaign {data['inputs']['lead_campaign']} \\
  --venue-label 'Hyperliquid (Ironflow node-derived, native)' \\
  --out placebo_portfolio_hyperliquid_native_c13_<TS>Z
```

Then write `research_state/decision_verdict_hyperliquid_native_c13_<TS>Z.md` and run:

```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c13_focus_campaign.py
```

Do not edit this prereg after compute. If the plan must change, create a new prereg stem and document why.
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=20261115)
    ap.add_argument("--min-draws", type=int, default=MIN_DRAWS,
                    help=f"heavy-compute floor written into the prereg (default {MIN_DRAWS})")
    ap.add_argument("--episode-draws", type=int, default=200,
                    help="planned permutation draws (default 200)")
    ap.add_argument("--placebo-draws", type=int, default=200,
                    help="planned placebo subsets (default 200)")
    ap.add_argument("--out", default=None,
                    help="output stem (default research_state/hyperliquid_native_c13_prereg_<UTC>)")
    ap.add_argument("--force", action="store_true", help="overwrite an existing prereg")
    args = ap.parse_args(argv)

    if args.min_draws < MIN_DRAWS:
        ap.error(f"--min-draws must be >= {MIN_DRAWS}")

    now = dt.datetime.now(dt.timezone.utc)
    generated_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    stem = args.out or f"research_state/hyperliquid_native_c13_prereg_{now.strftime('%Y%m%dT%H%M%SZ')}"
    stem_path = Path(stem)
    if not stem_path.is_absolute():
        stem_path = REPO / stem_path
    json_path = stem_path.with_suffix(".json")
    md_path = stem_path.with_suffix(".md")

    if (json_path.exists() or md_path.exists()) and not args.force:
        print(f"refusing to overwrite existing prereg: {json_path} (use --force to replace)")
        return 2

    data = build_prereg(args.seed, args.min_draws, args.episode_draws,
                        args.placebo_draws, generated_at)
    json_path.write_text(json.dumps(data, indent=2) + "\n")
    md_path.write_text(render_md(data, args.seed, args.min_draws,
                                 args.episode_draws, args.placebo_draws))

    ok, detail, _ = check_prereg()
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    print(f"prereg validation: {'PASS' if ok else 'FAIL'} — {detail}")
    if not ok:
        return 1

    print()
    print("C13 is now pre-registered. Run the two commands in the markdown, then write the verdict.")
    print("The C13 gate is RED until prereg + config-matched episode-edge + config-matched placebo + verdict exist.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())