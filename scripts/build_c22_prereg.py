#!/usr/bin/env python3
"""Build the C22 prereg (MEXC out-of-sample cross-venue replication) — PRE_REGISTERED.

C22 is a NEW-DATA campaign: it re-runs the *unchanged* spec-literal crash-rebound
strategy on MEXC USDT-perp 1H data (a venue never used in C1–C21), over the same
2023-01-01..2026-09-28 multiyear window and the same pre-specified folds/strata/inference
as C21. Because the data is new (MEXC != OKX/Binance) and the spec is frozen, this is a
legitimate out-of-sample test, NOT a same-data C22+ rerun/variant and NOT p-hacking: the
config, folds, strata, inference, and decision rules are all fixed HERE, before any compute.

Outputs: research_state/c22_prereg_<TS>.json and .md
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
STATE = REPO_ROOT / "research_state"
TS = "20261118T100126Z"
SEED = 20261122

# Frozen config — must equal scripts/run_c20_cross_venue_campaign.py::spec_literal_config().
CONFIG: Dict[str, Any] = {
    "use_rsi_trigger": True,
    "rsi_period": 21,
    "rsi_threshold": 20.0,
    "target_pct": 9.0,
    "rebound_short_target_pct": 9.0,
    "rebound_short_time_exit_bars": 48,
    "enable_rebound_short": True,
    "enable_eth_hedge": True,
    "enable_volume_based_sizing": True,
    "min_daily_volume_usd": 5_000_000.0,
    "gross_cap_pct": 120.0,
    "entry_spec_literal_next_open": True,
    "seed": SEED,
}

FOLDS: List[Dict[str, str]] = [
    {"id": "2023", "start": "2023-01-01T00:00:00Z", "end": "2023-12-31T23:00:00Z"},
    {"id": "2024", "start": "2024-01-01T00:00:00Z", "end": "2024-12-31T23:00:00Z"},
    {"id": "2025", "start": "2025-01-01T00:00:00Z", "end": "2025-12-31T23:00:00Z"},
    {"id": "2026YTD", "start": "2026-01-01T00:00:00Z", "end": "2026-09-28T23:00:00Z"},
]

STRATA: List[Dict[str, Any]] = [
    {"id": "crash_severity", "bins": ["rsi_0_10", "rsi_10_15", "rsi_15_20"],
     "definition": "RSI(21) at crash signal: [0,10) / [10,15) / [15,20)"},
    {"id": "btc_trend", "bins": ["btc_down_7d", "btc_flat_7d", "btc_up_7d"],
     "definition": "BTC close vs 168h-ago close: <-5% / -5%..+5% / >+5%"},
    {"id": "funding_regime", "bins": ["funding_negative", "funding_neutral", "funding_positive"],
     "definition": "venue funding rate sign at crash day; neutral when venue has no funding history"},
]

INFERENCE: Dict[str, Any] = {
    "episode_block_bootstrap_draws": 20000,
    "permutation_draws": 20000,
    "placebo_portfolio_runs": 2000,
    "strata_permutation_draws": 2000,
    "multiplicity": {"method": "benjamini_hochberg", "alpha": 0.05,
                     "families": ["per-venue-fold", "per-stratum"]},
    "power_floor": {"min_trades": 10, "min_episodes": 5, "min_distinct_crash_days": 5,
                    "below_floor_token": "UNDERPOWERED"},
    "pooled": "venue-blocked bootstrap over fold totals + cross-venue sign concordance vs recorded OKX/Binance",
}

DECISION_RULES: Dict[str, Any] = {
    "STABLE_POSITIVE_SUBSET": (
        ">=1 pre-specified venue-fold or pooled stratum survives BH correction with bootstrap "
        "CI excluding 0 & positive spot leg, permutation p<0.05, placebo p_ge_canonical<0.05, "
        "effective N>= floor, AND same-direction effect in the other venue(s) or flagged "
        "single-venue exploratory (MEXC is the new venue; OKX/Binance are the recorded priors)."
    ),
    "NO_GO": (
        "no stratum survives BH correction; pooled CI spans 0; spot non-positive across most "
        "folds (corroborates the C1-C21 NO_GO)."
    ),
    "UNDERPOWERED": (
        "per-fold N below floor, or missing seed/SHA binding / compute predating this prereg."
    ),
    "rule": "Always report per-fold, per-venue, and pooled numbers plus the power curve — never a bare token.",
}

REQUIRED_ARTIFACTS: List[str] = [
    f"c22_prereg_{TS}.json", f"c22_prereg_{TS}.md",
    f"c22_mexc_fold_campaign_{TS}.json",
    f"c22_mexc_fold_episode_edge_{TS}.json",
    f"c22_mexc_fold_placebo_{TS}.json",
    f"c22_mexc_fold_census_{TS}.json",
    f"c22_decision_verdict_mexc_stability_{TS}.json",
    f"c22_pooled_stability_synthesis_{TS}.json",
    f"c22_decision_verdict_CONSOLIDATED_{TS}.json",
]

PROVENANCE: Dict[str, Any] = {
    "venue": "mexc",
    "venue_label": "MEXC",
    "instrument_class": "USDT perpetual futures",
    "real_market_data": True,
    "fabricated_data": False,
    "synthetic_data": False,
    "cross_venue": True,
    "is_hyperliquid_venue_data": False,
    "provenance_caveat": (
        "Real MEXC USDT-perp exchange data, non-synthetic, CROSS-VENUE vs the Hyperliquid spec; "
        "NOT Hyperliquid performance evidence and must never be relabelled as such. Multi-year "
        "window 2023-01-01T00:00:00Z..2026-09-28T23:00:00Z (32808 hourly bars/symbol)."
    ),
    "acquisition_script": "scripts/fetch_mexc_perp_archive.py",
    "acquisition_probe": f"research_state/c22_venue_acquisition_probe_{TS}.json",
    "cache_dir": "research_state/cache/mexc_1h_multiyear_20230101_20260928",
    "universe": "research_state/universe_mexc_multiyear_verified.json",
}

GUARDRAILS: List[str] = [
    "Cross-venue real MEXC data only; never relabel as Hyperliquid (is_hyperliquid_venue_data=false).",
    "Config is FROZEN to the spec-literal values above; no parameter tuning after results.",
    "Folds and strata are fixed here, before compute; no post-hoc bin/fold invention.",
    "Do NOT reduce draw counts: 20k bootstrap / 20k permutation / 2k placebo / 2k strata floors preserved.",
    "No synthetic gap-fill; symbols not listed for the full window are excluded (coverage=false), never fabricated.",
    "The C1-C21 NO_GO stands unless C22 produces a pre-registered contradiction with full evidence.",
    "MEXC is the NEW venue; a same-data C22+ rerun on OKX/Binance is forbidden. New direction beyond C22 needs new prereg + new data + explicit authorization.",
    "Report per-fold, per-venue, and pooled numbers plus the power curve — never a bare token.",
]


def build_prereg() -> Dict[str, Any]:
    # Deep-copy mutable structures so callers (tests, tooling) can never mutate the
    # module-level frozen constants through the returned dict.
    return copy.deepcopy({
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign": "C22",
        "binding_task": "C22-T1",
        "prereg_status": "PRE_REGISTERED_BEFORE_COMPUTE",
        "title": "C22 — MEXC Out-of-Sample Cross-Venue Replication (SPEC_LITERAL_NEXT_OPEN)",
        "why_c22": (
            "C1-C20 closed NO_GO on OKX + Binance UM perps; C21-T1 confirmed temporal/regime "
            "stability of that NO_GO. Before abandoning the edge, C22 asks a NEW-DATA question: "
            "does the unchanged spec-literal edge replicate on an independent venue (MEXC) never "
            "used before? This is new data + a frozen spec, not a same-data rerun and not a "
            "parameter search."
        ),
        "config": CONFIG,
        "folds": FOLDS,
        "strata": STRATA,
        "inference": INFERENCE,
        "decision_rules": DECISION_RULES,
        "required_artifacts": REQUIRED_ARTIFACTS,
        "provenance": PROVENANCE,
        "guardrails": GUARDRAILS,
    })


def render_markdown(prereg: Dict[str, Any]) -> str:
    cfg = prereg["config"]
    lines = [
        f"# C22 — MEXC Out-of-Sample Cross-Venue Replication (SPEC_LITERAL_NEXT_OPEN)",
        "",
        f"**Prereg rendered (UTC):** {prereg['generated_at_utc']} · **Status:** `{prereg['prereg_status']}` · "
        f"**Campaign:** C22 · **Binding task:** {prereg['binding_task']}",
        f"**Provenance:** {prereg['provenance']['provenance_caveat']}",
        "",
        "## Why C22 (follows the C1-C21 NO_GO)",
        "",
        prereg["why_c22"],
        "",
        "## Fixed config (no switching after results)",
        "",
        f"`rsi_period={cfg['rsi_period']}`, `rsi_threshold={cfg['rsi_threshold']}`, `target_pct={cfg['target_pct']}`, "
        f"`rebound_short_target_pct={cfg['rebound_short_target_pct']}`, "
        f"`rebound_short_time_exit_bars={cfg['rebound_short_time_exit_bars']}`, "
        f"`enable_rebound_short={cfg['enable_rebound_short']}`, `enable_eth_hedge={cfg['enable_eth_hedge']}`, "
        f"`min_daily_volume_usd={int(cfg['min_daily_volume_usd']):,}`, `gross_cap_pct={cfg['gross_cap_pct']}`, "
        f"`entry_spec_literal_next_open={cfg['entry_spec_literal_next_open']}`. Seed `{cfg['seed']}`.",
        "",
        "## Folds & strata (pre-specified)",
        "",
        "- **Folds:** " + ", ".join(f["id"] for f in prereg["folds"]) + " (2026YTD = 2026-01-01..2026-09-28). No parameter fitting.",
        "- **Strata:** " + ", ".join(s["id"] for s in prereg["strata"]) + ". Fixed here; no post-hoc invention.",
        "",
        "## Inference & power",
        "",
        f"Per venue-fold: {prereg['inference']['episode_block_bootstrap_draws']:,}-draw episode-block bootstrap CI95, "
        f"{prereg['inference']['permutation_draws']:,}-draw permutation p, "
        f"{prereg['inference']['placebo_portfolio_runs']:,}-subset portfolio placebo, stratified bootstrap with "
        f"**Benjamini-Hochberg** correction (alpha={prereg['inference']['multiplicity']['alpha']}). "
        f"Pooled venue-blocked bootstrap + cross-venue sign concordance vs the recorded OKX/Binance priors. "
        f"**Power floor:** >= {prereg['inference']['power_floor']['min_trades']} trades / "
        f">= {prereg['inference']['power_floor']['min_episodes']} episodes / "
        f">= {prereg['inference']['power_floor']['min_distinct_crash_days']} distinct crash days; "
        f"otherwise `{prereg['inference']['power_floor']['below_floor_token']}` with a power curve.",
        "",
        "## Decision rules",
        "",
        f"- **`STABLE_POSITIVE_SUBSET`**: {prereg['decision_rules']['STABLE_POSITIVE_SUBSET']}",
        f"- **`NO_GO`**: {prereg['decision_rules']['NO_GO']}",
        f"- **`UNDERPOWERED`**: {prereg['decision_rules']['UNDERPOWERED']}",
        "",
        f"Always report per-fold, per-venue, and pooled numbers plus the power curve — never a bare token.",
        "",
        "## Required artifacts (TS = " + TS + ")",
        "",
        "`" + "`; `".join(prereg["required_artifacts"]) + "`; HANDOFF references **C22-T1** and **verify_c22_focus_campaign.py**.",
        "",
        "## Guardrails",
        "",
    ]
    for g in prereg["guardrails"]:
        lines.append(f"- {g}")
    lines.append("")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Build the C22 prereg (PRE_REGISTERED_BEFORE_COMPUTE)")
    ap.add_argument("--out-json", default=str(STATE / f"c22_prereg_{TS}.json"))
    ap.add_argument("--out-md", default=str(STATE / f"c22_prereg_{TS}.md"))
    ap.add_argument("--force", action="store_true", help="Overwrite an existing prereg")
    args = ap.parse_args(argv)

    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    if not out_json.is_absolute():
        out_json = REPO_ROOT / out_json
    if not out_md.is_absolute():
        out_md = REPO_ROOT / out_md
    if out_json.exists() and not args.force:
        print(f"Prereg already exists: {out_json} (use --force to overwrite)")
        return 0

    prereg = build_prereg()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(prereg, indent=2) + "\n")
    out_md.write_text(render_markdown(prereg))
    print(f"Wrote {out_json.relative_to(REPO_ROOT)}")
    print(f"Wrote {out_md.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())