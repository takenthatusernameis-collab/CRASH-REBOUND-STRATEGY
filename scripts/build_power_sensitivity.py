#!/usr/bin/env python3
"""C3-T3 — statistical power sensitivity under achievable datasets.

WHY THIS EXISTS
---------------
C1-T2 recorded the binding power target (>=10 independent crash episodes) and a
single-point projection. That answers "how much data do we need?" but not "can
ANY achievable dataset get there?". This script quantifies P(N >= 10) under three
explicit scenarios, using the observed episode rate as a Poisson base rate:

  (a) partial window extended to the full 283-day spec window, 24 symbols
  (b) a 2-year (730d) window, 24 symbols
  (c) a multi-venue pooled window (Hyperliquid + OKX, clearly CROSS-VENUE)

Every number is derived from committed artifacts at run time:
  * episode rate      <- research_state/power_target_hyperliquid_20261114T172700Z.json
  * OKX episode count <- research_state/episode_edge_okx_full.json
  * retained window   <- research_state/hyperliquid_universe_coverage.json
No value is hand-typed except scenario definitions (window lengths, venue set).

Method notes recorded in the artifact:
  * Poisson is the arrival model for independent crash episodes; it is an
    approximation (episodes cluster on shared crash days).
  * Scenario (c) pools two venues; cross-venue dependence makes the pooled count
    an upper bound on independent information, and it is NOT Hyperliquid evidence.
"""
from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / "research_state"
POWER_TARGET = STATE / "power_target_hyperliquid_20261114T172700Z.json"
OKX_EDGE = STATE / "episode_edge_okx_full.json"
COVERAGE = STATE / "hyperliquid_universe_coverage.json"

LABEL = "NOT_EVIDENCE_POWER_SENSITIVITY"
CAVEAT = (
    "Power sensitivity projections from observed base rates. NOT performance "
    "evidence. Poisson independence is an approximation; cross-venue pooling "
    "(scenario c) is NOT Hyperliquid evidence and is an upper bound on "
    "independent information."
)


def poisson_sf(k: int, lam: float) -> float:
    """P(N >= k) for Poisson(lam), computed in log space for stability."""
    if lam <= 0:
        return 0.0 if k > 0 else 1.0
    # P(N <= k-1)
    cdf = 0.0
    for i in range(0, k):
        cdf += math.exp(-lam + i * math.log(lam) - math.lgamma(i + 1))
    return max(0.0, min(1.0, 1.0 - cdf))


def main() -> int:
    for p in (POWER_TARGET, OKX_EDGE, COVERAGE):
        if not p.exists():
            print(f"MISSING required input: {p}", file=sys.stderr)
            return 2

    pt = json.loads(POWER_TARGET.read_text())
    okx = json.loads(OKX_EDGE.read_text())
    cov = json.loads(COVERAGE.read_text())

    base = pt["observed_base_rates"]
    rate_per_day = float(base["traded_episodes_per_calendar_day"])
    symbols = int(base["symbols"])
    retained_days = float(base["retained_window_days"])
    crash_days_per_day = float(base["crash_days_per_calendar_day"])

    okx_episodes = int(((okx.get("episode_audit") or {}).get("n_episodes"))
                       or ((okx.get("effective_independent_sample") or {}).get("episodes"))
                       or 0)

    target = int(pt["binding_target"]["min_independent_crash_episodes"])

    scenarios: List[Dict[str, Any]] = []

    def add(key: str, days: float, rate: float, note: str, cross_venue: bool = False,
            symbols_override: int | None = None) -> None:
        lam = rate * days
        scenarios.append({
            "scenario": key,
            "window_days": days,
            "symbols": symbols_override or symbols,
            "rate_traded_episodes_per_day": rate,
            "expected_episodes_lambda": lam,
            "prob_at_least_target": poisson_sf(target, lam),
            "prob_at_least_target_pct": 100.0 * poisson_sf(target, lam),
            "cross_venue": cross_venue,
            "note": note,
        })

    add("a_partial_extended_to_283d_spec_window",
        283.0, rate_per_day,
        "Observed retained-window episode rate extended to the full 283-day spec "
        "window at the same 24 symbols; no new symbols, no new venues.")
    add("b_two_year_window_24_symbols",
        730.0, rate_per_day,
        "Same rate/universe held for 2 years of calendar time (beyond the API "
        "retention horizon, so operator archive required).")
    add("c_multi_venue_pooled_hl_plus_okx",
        283.0, rate_per_day + (okx_episodes / 283.0 if okx_episodes else 0.0),
        "Hyperliquid observed rate plus OKX observed episode rate pooled over the "
        "same 283-day window. CROSS-VENUE: not Hyperliquid evidence; pooling "
        "assumes independence across venues, which shared market crashes violate, "
        "so this is an upper bound on independent information.",
        cross_venue=True)

    # Sensitivity of the headline scenario to the rate estimate: crash-day rate
    # is far better determined (4 events) than the traded-episode rate (2 events).
    rate_low = rate_per_day * 0.5
    rate_high = rate_per_day * 1.5
    rate_sensitivity = {
        "basis": "traded-episode rate is estimated from 2 events; +/-50% band shown",
        "rate_per_day_low": rate_low,
        "rate_per_day_high": rate_high,
        "prob_at_least_target_283d_low": poisson_sf(target, rate_low * 283.0),
        "prob_at_least_target_283d_high": poisson_sf(target, rate_high * 283.0),
        "prob_at_least_target_730d_low": poisson_sf(target, rate_low * 730.0),
        "prob_at_least_target_730d_high": poisson_sf(target, rate_high * 730.0),
    }

    best = max(s["prob_at_least_target"] for s in scenarios)
    ts_compact = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    ts_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    artifact = {
        "schema_version": 1,
        "generated_at_utc": ts_iso,
        "run_type": "power_sensitivity",
        "label": LABEL,
        "performance_evidence": False,
        "provenance_caveat": CAVEAT,
        "inputs": {
            "power_target": str(POWER_TARGET.relative_to(REPO)),
            "power_target_sha256": __import__("hashlib").sha256(POWER_TARGET.read_bytes()).hexdigest(),
            "okx_episode_edge": str(OKX_EDGE.relative_to(REPO)),
            "coverage": str(COVERAGE.relative_to(REPO)),
        },
        "observed": {
            "traded_episodes_per_calendar_day": rate_per_day,
            "crash_days_per_calendar_day": crash_days_per_day,
            "symbols": symbols,
            "retained_window_days": retained_days,
            "okx_independent_episodes": okx_episodes,
        },
        "target_min_independent_episodes": target,
        "scenarios": scenarios,
        "rate_sensitivity": rate_sensitivity,
        "best_case_prob_at_least_target": best,
        "verdict": (
            "POWER_FLOOR_UNREACHABLE_ON_ACHIEVABLE_DATA"
            if best < 0.5
            else "POWER_FLOOR_REACHABLE_UNDER_AT_LEAST_ONE_SCENARIO"
        ),
        "interpretation": (
            "Even the most favourable achievable scenario stays well below even "
            "odds of reaching the >=10 independent-episode floor. The 283-day "
            "spec window at the observed rate cannot reach the floor; only a "
            "multi-year archive or a materially higher episode rate can, and the "
            "pooled cross-venue scenario is an upper bound, not evidence."
            if best < 0.5 else
            "At least one scenario reaches >=50% probability of the episode floor."
        ),
        "no_new_data_fabricated": True,
    }

    out_json = STATE / f"power_sensitivity_{ts_compact}.json"
    out_json.write_text(json.dumps(artifact, indent=2) + "\n")

    lines = [
        f"# Power Sensitivity — {ts_iso}",
        "",
        f"**Label:** `{LABEL}` — projections from observed base rates, NOT performance evidence.",
        "",
        f"Target: **>= {target} independent crash episodes**. "
        f"Observed traded-episode rate: **{rate_per_day:.6f}/calendar day** "
        f"({symbols} symbols, {retained_days:.3f} retained days).",
        "",
        "| Scenario | Days | λ (expected episodes) | P(N ≥ target) | Cross-venue |",
        "|---|---|---|---|---|",
    ]
    for s in scenarios:
        lines.append(
            f"| `{s['scenario']}` | {s['window_days']:.0f} | {s['expected_episodes_lambda']:.3f} "
            f"| **{s['prob_at_least_target']*100:.2f}%** | {s['cross_venue']} |"
        )
    lines += [
        "",
        "## Rate sensitivity (±50% on the traded-episode rate)",
        "",
        f"- 283d: {rate_sensitivity['prob_at_least_target_283d_low']*100:.2f}% "
        f"(low) .. {rate_sensitivity['prob_at_least_target_283d_high']*100:.2f}% (high)",
        f"- 730d: {rate_sensitivity['prob_at_least_target_730d_low']*100:.2f}% "
        f"(low) .. {rate_sensitivity['prob_at_least_target_730d_high']*100:.2f}% (high)",
        "",
        "## Interpretation",
        "",
        artifact["interpretation"],
        "",
        "## Caveats",
        "",
        "- Poisson independence is an approximation: crash episodes cluster on shared crash days.",
        "- The traded-episode rate rests on 2 observed episodes; the ±50% band is a diagnostic, not a CI.",
        "- Scenario (c) pools venues and is NOT Hyperliquid evidence.",
        "- No data was fabricated; every input is a committed artifact.",
        "",
        f"**Verdict:** `{artifact['verdict']}`",
    ]
    out_md = STATE / f"power_sensitivity_{ts_compact}.md"
    out_md.write_text("\n".join(lines) + "\n")

    print(f"wrote {out_json}")
    print(f"wrote {out_md}")
    print(f"best_case={best:.4f} verdict={artifact['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())