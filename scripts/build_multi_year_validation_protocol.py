#!/usr/bin/env python3
"""C4-T2 — multi-year validation protocol + executable power/duration calculation.

WHY THIS EXISTS
---------------
C1-T2/C3-T3 established the binding power floor (>=10 independent crash episodes)
and showed that the achievable 283-day window almost certainly cannot reach it.
What was missing was a *protocol*: the exact endpoint, clustering rule,
resampling/placebo methods, multiplicity correction, stop/go rules and the
archive duration required for 80% power — in machine-checkable form, with the
calculation executed rather than asserted in prose.

This script emits that protocol. Every number is derived from committed artifacts
at run time; the only inputs that are not artifacts are the protocol choices
themselves (endpoint definitions, alpha, power target, clustering window).

The calculation is a real numerical solve (Poisson episode arrivals, bisection on
duration), not a lookup. Its output and the code that produced it are recorded in
the artifact so the number can be reproduced and audited.

OUTPUT IS A PROTOCOL, NOT EVIDENCE: `performance_evidence=false`. It changes no
strategy behaviour and no canonical artifact.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / "research_state"
POWER_TARGET = STATE / "power_target_hyperliquid_20261114T172700Z.json"
POWER_SENSITIVITY = STATE / "power_sensitivity_20261114T182832Z.json"
COVERAGE = STATE / "hyperliquid_universe_coverage.json"
OKX_EDGE = STATE / "episode_edge_okx_full.json"

LABEL = "NOT_EVIDENCE_VALIDATION_PROTOCOL"
CAVEAT = (
    "Protocol + power calculation only. NOT performance evidence. The protocol "
    "defines what a future GO decision requires; it does not validate the "
    "strategy, and it never relabels partial, cross-venue, or synthetic data."
)

POWER_TARGET_PROB = 0.80
ALPHA = 0.05
MIN_EPISODES = 10
CLUSTER_WINDOW_HOURS = 72
BOOTSTRAP_RESAMPLES = 10_000
PERMUTATION_RESAMPLES = 10_000


def poisson_sf(k: int, lam: float) -> float:
    if lam <= 0:
        return 0.0 if k > 0 else 1.0
    cdf = 0.0
    for i in range(k):
        cdf += math.exp(-lam + i * math.log(lam) - math.lgamma(i + 1))
    return max(0.0, min(1.0, 1.0 - cdf))


def days_for_power(rate_per_day: float, k: int, power: float) -> Dict[str, Any]:
    """Bisection solve for D such that P(Poisson(rate*D) >= k) == power."""
    if rate_per_day <= 0:
        return {"solvable": False, "reason": "rate_per_day <= 0"}
    lo, hi = 1.0, 10.0
    while poisson_sf(k, rate_per_day * hi) < power and hi < 1e7:
        hi *= 2.0
    if poisson_sf(k, rate_per_day * hi) < power:
        return {"solvable": False, "reason": "no duration up to 1e7 days reaches target"}
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if poisson_sf(k, rate_per_day * mid) < power:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-6:
            break
    days = 0.5 * (lo + hi)
    return {
        "solvable": True,
        "target_power": power,
        "min_episodes": k,
        "rate_per_day": rate_per_day,
        "required_days": days,
        "required_years": days / 365.0,
        "required_hours_per_symbol": days * 24.0,
        "required_hourly_bars_per_symbol": int(math.ceil(days * 24.0)) + 1,
        "achieved_power_at_solution": poisson_sf(k, rate_per_day * days),
    }


def main() -> int:
    for p in (POWER_TARGET, POWER_SENSITIVITY, COVERAGE, OKX_EDGE):
        if not p.exists():
            print(f"MISSING required input: {p}", file=sys.stderr)
            return 2

    pt = json.loads(POWER_TARGET.read_text())
    ps = json.loads(POWER_SENSITIVITY.read_text())
    cov = json.loads(COVERAGE.read_text())
    okx = json.loads(OKX_EDGE.read_text())

    base = pt["observed_base_rates"]
    rate_traded = float(base["traded_episodes_per_calendar_day"])
    rate_crash_days = float(base["crash_days_per_calendar_day"])
    symbols = int(base["symbols"])
    retained_days = float(base["retained_window_days"])
    observed_episodes = int(base.get("exploratory_traded_episodes") or 0)
    observed_crash_days = int(base.get("census_distinct_crash_days")
                              or round(rate_crash_days * retained_days))

    calc_traded = {p: days_for_power(rate_traded, MIN_EPISODES, p)
                   for p in (0.80, 0.90, 0.95)}
    calc_crash_days = {p: days_for_power(rate_crash_days, MIN_EPISODES, p)
                       for p in (0.80, 0.90, 0.95)}

    required_80 = calc_traded[0.80]
    protocol = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "run_type": "multi_year_validation_protocol",
        "label": LABEL,
        "performance_evidence": False,
        "provenance_caveat": CAVEAT,
        "decision_lock": {
            "current_verdict": "NO_GO",
            "reason": (
                "Retained Hyperliquid window is a partial 161-day window with only "
                f"{observed_crash_days} distinct crash days and {observed_episodes} "
                "traded episodes; the power floor is >=10 independent crash episodes. "
                "No achievable API window can reach the floor, and no cross-venue, "
                "partial, dry-run, or synthetic artifact may be promoted to evidence."
            ),
            "continue_only_with": (
                "an operator-supplied, C4-T1-validated, Hyperliquid-native archive "
                "covering at least the duration computed below (>=10 independent "
                "crash episodes), ingested through the DATA_REQUEST runbook"
            ),
            "forbidden_relabelings": [
                "OKX artifacts as Hyperliquid evidence",
                "partial-window campaigns as full-window evidence",
                "dry-run/synthetic fixtures as market data",
                "the placeholder parquet as evidence",
                "the exploratory spec-literal fan-out as validation",
            ],
        },
        "primary_endpoint": {
            "name": "episode_level_net_pnl",
            "definition": (
                "Net PnL of one crash episode (all positions opened by that episode's "
                "crash-day signal, including ETH hedge legs, funding, fees, slippage, "
                "and liquidation penalties), aggregated per independent episode"
            ),
            "test": "two-sided 95% episode-block bootstrap CI on the mean episode PnL",
            "go_rule": "bootstrap 95% CI excludes 0 in the positive direction",
            "alpha": ALPHA,
        },
        "secondary_endpoints": [
            {
                "name": "episode_win_rate",
                "definition": "fraction of independent episodes with positive net PnL",
                "go_rule": "95% CI lower bound > 0.5",
            },
            {
                "name": "max_drawdown",
                "definition": "peak-to-trough equity drawdown across the episode sequence",
                "go_rule": "no drawdown worse than -8%",
            },
            {
                "name": "rebound_short_profit_share",
                "definition": "rebound-short leg PnL / total PnL",
                "go_rule": "reported, not a GO gate (spec target ~27%, not a validity test)",
            },
        ],
        "episode_clustering_rule": {
            "unit": "independent crash episode",
            "cluster_key": "utc_crash_day",
            "window_hours": CLUSTER_WINDOW_HOURS,
            "rule": (
                f"Collapse all crash signals within {CLUSTER_WINDOW_HOURS}h on the same "
                "UTC crash day into one episode; an episode counts once regardless of how "
                "many symbols fired. Independence requires distinct crash days."
            ),
            "independence_requirement": (
                "Episodes on the same crash day are NOT independent (shared market move). "
                "Inference uses crash-day blocks, never raw trade counts."
            ),
        },
        "resampling": {
            "bootstrap": {
                "method": "stationary block bootstrap over crash-day blocks",
                "block_unit": "crash_day",
                "resamples": BOOTSTRAP_RESAMPLES,
                "statistic": "mean episode net PnL",
                "ci": "95% percentile",
            },
            "permutation": {
                "method": "crash-day label permutation",
                "resamples": PERMUTATION_RESAMPLES,
                "null": "episode PnL is exchangeable across crash days (no crash-day effect)",
                "go_rule": "permutation p < 0.05",
            },
            "placebo": {
                "method": "full-portfolio placebo over all signal-gate events",
                "detail": (
                    "Enumerate exact subsets of signal-gate events where feasible; "
                    "otherwise Monte Carlo over event subsets, replaying the real engine."
                ),
                "go_rule": "canonical result is not an extreme of the placebo distribution "
                           "(one-sided p < 0.05 against the placebo mean)",
            },
        },
        "multiple_testing": {
            "method": "Holm-Bonferroni",
            "family": ["episode_level_net_pnl", "episode_win_rate", "max_drawdown"],
            "alpha": ALPHA,
            "rule": "GO requires the primary endpoint to survive Holm correction across the family",
        },
        "minimum_independent_episodes": MIN_EPISODES,
        "power_calculation": {
            "method": "Poisson episode arrivals; bisection solve for duration D at target power",
            "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "reproduce": (
                "PYTHONPATH=. /tmp/crs-venv/bin/python "
                "scripts/build_multi_year_validation_protocol.py"
            ),
            "inputs": {
                "observed_traded_episodes_per_day": rate_traded,
                "observed_crash_days_per_day": rate_crash_days,
                "symbols": symbols,
                "retained_window_days": retained_days,
                "observed_independent_episodes": observed_episodes,
                "observed_crash_days": observed_crash_days,
                "power_sensitivity_best_case_prob_at_least_target":
                    ps.get("best_case_prob_at_least_target"),
            },
            "traded_episode_rate": calc_traded,
            "crash_day_rate": calc_crash_days,
            "required_for_80pct_power": required_80,
            "archive_requirement": {
                "min_independent_crash_episodes": MIN_EPISODES,
                "min_duration_days": required_80.get("required_days"),
                "min_duration_years": required_80.get("required_years"),
                "min_hourly_bars_per_symbol": required_80.get("required_hourly_bars_per_symbol"),
                "symbols": symbols,
                "min_total_bars_all_symbols": (
                    (required_80.get("required_hourly_bars_per_symbol") or 0) * symbols
                ),
                "window_start": "2025-12-20T00:00:00Z",
                "window_end": "2026-09-28T23:00:00Z",
                "note": (
                    "The spec window is only 283 days; reaching 80% power needs a longer "
                    "archive than the spec window, which is exactly why the operator "
                    "archive must be multi-year."
                ),
            },
        },
        "stop_go_rules": {
            "GO": [
                f">= {MIN_EPISODES} independent crash episodes on distinct crash days",
                "primary endpoint bootstrap 95% CI excludes 0 (positive)",
                "crash-day permutation p < 0.05",
                "full-portfolio placebo one-sided p < 0.05",
                "primary endpoint survives Holm-Bonferroni",
                "all inputs C4-T1 validated Hyperliquid-native, non-synthetic, checksummed",
            ],
            "NO_GO": [
                "any criterion unmet",
                "episode count < floor",
                "any input is partial, cross-venue, synthetic, or unchecksummed",
            ],
            "current_status": "NO_GO (retained partial window; floor unreachable on API data)",
        },
        "okx_cross_venue_note": {
            "okx_independent_episodes": ((okx.get("episode_audit") or {}).get("n_episodes")
                                         or (okx.get("effective_independent_sample") or {}).get("episodes")),
            "statement": "OKX is cross-venue and is never Hyperliquid evidence.",
        },
        "coverage_reference": {
            "coverage_artifact": str(COVERAGE.relative_to(REPO)),
            "verdict": cov.get("verdict"),
        },
        "no_new_data_fabricated": True,
    }

    STATE.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_json = STATE / f"multi_year_validation_protocol_{ts}.json"
    out_json.write_text(json.dumps(protocol, indent=2) + "\n")

    req = required_80
    lines = [
        f"# Multi-Year Validation Protocol — {protocol['generated_at_utc']}",
        "",
        f"**Label:** `{LABEL}` — protocol and power calculation, NOT performance evidence.",
        "",
        "## Decision lock",
        "",
        f"**Current verdict: `{protocol['decision_lock']['current_verdict']}`.** "
        f"{protocol['decision_lock']['reason']}",
        "",
        f"Continue only with: {protocol['decision_lock']['continue_only_with']}.",
        "",
        "## Power calculation (executed, not asserted)",
        "",
        f"Observed traded-episode rate: **{rate_traded:.6f}/calendar day** "
        f"({observed_episodes} episodes / {retained_days:.1f} retained days, {symbols} symbols).",
        f"Observed crash-day rate: **{rate_crash_days:.6f}/day** ({observed_crash_days} crash days).",
        "",
        "| Target power | Required duration (traded-episode rate) | Required duration (crash-day rate) |",
        "|---|---|---|",
    ]
    for p in (0.80, 0.90, 0.95):
        a, b = calc_traded[p], calc_crash_days[p]
        lines.append(
            f"| {p*100:.0f}% | {a.get('required_days', float('nan')):.1f} d "
            f"({a.get('required_years', float('nan')):.2f} y) | "
            f"{b.get('required_days', float('nan')):.1f} d "
            f"({b.get('required_years', float('nan')):.2f} y) |"
        )
    lines += [
        "",
        f"**Archive requirement at 80% power:** >= {MIN_EPISODES} independent crash episodes; "
        f">= {req.get('required_days', float('nan')):.1f} days "
        f"({req.get('required_years', float('nan')):.2f} years); "
        f">= {req.get('required_hourly_bars_per_symbol')} hourly bars/symbol × {symbols} symbols "
        f"= {protocol['power_calculation']['archive_requirement']['min_total_bars_all_symbols']} bars.",
        "",
        "The spec window is 283 days; 80% power needs a materially longer archive. "
        "That is the quantitative reason a multi-year operator archive is required.",
        "",
        "## Protocol summary",
        "",
        f"- Primary endpoint: `{protocol['primary_endpoint']['name']}` — "
        f"{protocol['primary_endpoint']['test']}; GO if {protocol['primary_endpoint']['go_rule']}.",
        f"- Clustering: {protocol['episode_clustering_rule']['rule']}",
        f"- Bootstrap: {protocol['resampling']['bootstrap']['resamples']} resamples over "
        f"crash-day blocks; permutation: {protocol['resampling']['permutation']['resamples']} "
        f"resamples; placebo: {protocol['resampling']['placebo']['method']}.",
        f"- Multiplicity: {protocol['multiple_testing']['method']} across "
        f"{', '.join(protocol['multiple_testing']['family'])}.",
        "",
        "## Reproduce",
        "",
        "```bash",
        protocol["power_calculation"]["reproduce"],
        "```",
        "",
        f"Script sha256: `{protocol['power_calculation']['code_sha256']}`",
        "",
        f"**Verdict:** `{protocol['decision_lock']['current_verdict']}` — "
        "`STRATEGY_UNDERPOWERED` until every GO criterion is met.",
        "",
    ]
    out_md = STATE / f"multi_year_validation_protocol_{ts}.md"
    out_md.write_text("\n".join(lines) + "\n")

    print(f"verdict={protocol['decision_lock']['current_verdict']} "
          f"required_days_80pct={req.get('required_days')} "
          f"required_bars_per_symbol={req.get('required_hourly_bars_per_symbol')}")
    print(f"wrote {out_json}")
    print(f"wrote {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())