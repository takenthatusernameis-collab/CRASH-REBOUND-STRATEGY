#!/usr/bin/env python3
"""C11.2 — Hyperliquid-native power & decision pre-registration (default path while native archive is blocked).

Builds the anti-avoidance artifact that pre-specifies the eventual Hyperliquid-native
campaign so it cannot be faked or avoided. Produces
research_state/hyperliquid_native_power_prereg_<TS>Z.{json,md}.

Inputs (real, non-synthetic, cross-venue only):
  - Retained Hyperliquid partial chain crash census: observed RSI(21)<20 crash-event
    rate over the Apr-19..Sep-28 2026 partial window (24 symbols, 3900 bars each).
  - Cross-venue effect-size priors from OKX + Binance multi-year episode-block
    bootstrap distributions (is_hyperliquid_venue_data=false throughout).

Method:
  - Episode-block bootstrap power grid across candidate episode counts N.
  - For each N, resample N episode totals with replacement from the pooled
    cross-venue episode-total pool; compute the two-sided 95% CI of the total PnL.
  - Power(N) = fraction of 4000 simulations where CI excludes zero.
  - N80 = smallest N with power >= 80% at alpha=0.05.
  - MDE = smallest mean episode PnL detectable with 80% power at N80.

Output contract (binding):
  - is_hyperliquid_venue_data = false
  - performance_evidence = false
  - This is a DESIGN / POWER artifact only. NOT a verdict. NOT evidence.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import random
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

SCHEMA_VERSION = 1
ALPHA = 0.05
POWER_TARGET = 0.80
POWER_SIMULATIONS = 4000
N_GRID_MIN = 20
N_GRID_MAX = 400
N_GRID_STEP = 10
SEED = 20261115

HL_CENSUS = REPO / "research_state" / "hyperliquid_partial_crash_census_20260419_20260928.json"
OKX_EPISODE_EDGE = REPO / "research_state" / "episode_edge_okx_multiyear.json"
BINANCE_EPISODE_EDGE = REPO / "research_state" / "episode_edge_binance_um_multiyear.json"

SPEC_START = "2025-12-20T00:00:00Z"
SPEC_END = "2026-09-28T23:00:00Z"


def iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_utc(text: str) -> dt.datetime:
    text = str(text)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    return dt.datetime.fromisoformat(text).astimezone(dt.timezone.utc)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _q(vals: List[float], p: float) -> float:
    if not vals:
        return 0.0
    s = sorted(vals)
    k = (len(s) - 1) * p
    f, c = math.floor(k), math.ceil(k)
    return float(s[int(k)]) if f == c else float(s[f] * (c - k) + s[c] * (k - f))


def load_hl_partial_census() -> Dict[str, Any]:
    data = json.loads(HL_CENSUS.read_text())
    totals = data.get("totals", {})
    window = data.get("target_window", {})
    start = parse_utc(window.get("start", SPEC_START))
    end = parse_utc(window.get("end", SPEC_END))
    days = (end - start).total_seconds() / 86400.0
    rsi_events = int(totals.get("rsi_crash_events", 0))
    confirmed_signals = int(totals.get("confirmed_signals", 0))
    symbols = int(totals.get("symbols", 0))
    bars = int(totals.get("bars", 0))
    return {
        "source": str(HL_CENSUS.relative_to(REPO)),
        "sha256": sha256_file(HL_CENSUS),
        "window_start": window.get("start"),
        "window_end": window.get("end"),
        "expected_hourly_bars": window.get("expected_hourly_bars"),
        "days_observed": days,
        "symbols": symbols,
        "bars": bars,
        "rsi_crash_events": rsi_events,
        "confirmed_signals": confirmed_signals,
        "crash_events_per_day": rsi_events / days if days > 0 else 0.0,
        "signals_per_day": confirmed_signals / days if days > 0 else 0.0,
    }


def load_cross_venue_episode_totals() -> Tuple[List[float], Dict[str, Any]]:
    """Pool OKX + Binance observed episode-total PnLs as the effect-size prior."""
    episode_totals: List[float] = []
    venues: Dict[str, Any] = {}

    for label, path in (("OKX", OKX_EPISODE_EDGE), ("Binance", BINANCE_EPISODE_EDGE)):
        data = json.loads(path.read_text())
        boot = data.get("episode_block_bootstrap", {})
        observed = boot.get("observed_episode_totals", {})
        venue_totals = [float(v) for v in observed.values()]
        episode_totals.extend(venue_totals)
        audit = data.get("episode_audit", {})
        venues[label] = {
            "source": str(path.relative_to(REPO)),
            "sha256": sha256_file(path),
            "generated_at_utc": data.get("generated_at_utc"),
            "n_episodes": audit.get("n_episodes"),
            "n_distinct_crash_days": audit.get("n_distinct_crash_days"),
            "canonical_total_pnl": data.get("inputs", {}).get("canonical_total_pnl"),
            "canonical_num_trades": data.get("inputs", {}).get("canonical_num_trades"),
            "verdict": data.get("verdict"),
            "episode_totals": venue_totals,
        }

    return episode_totals, venues


def bootstrap_power_grid(episode_totals: List[float], n_grid: List[int], simulations: int, seed: int) -> Dict[str, Any]:
    """For each N in n_grid, estimate power = P(95% CI excludes zero | N episodes)."""
    rng = random.Random(seed)
    pool = episode_totals
    if not pool:
        return {"grid": [], "n80": None, "power_at_max_n": 0.0, "mde": None}

    grid_results: List[Dict[str, Any]] = []
    n80 = None
    power_at_max_n = 0.0

    for n in n_grid:
        if n <= 0 or n > len(pool) * 50:
            continue
        excludes_zero_count = 0
        ci_lows: List[float] = []
        ci_highs: List[float] = []
        means: List[float] = []
        for _ in range(simulations):
            sample = [pool[rng.randrange(len(pool))] for _ in range(n)]
            mean = statistics.fmean(sample)
            # two-sided 95% CI via percentile bootstrap over the sample's resampling distribution
            # approximate: standard error = sd / sqrt(n); CI = mean ± 1.96 * se
            if len(sample) > 1:
                sd = statistics.pstdev(sample)
            else:
                sd = 0.0
            se = sd / math.sqrt(n) if n > 0 else 0.0
            z = 1.959963984540054  # two-sided 95%
            ci_low = mean - z * se
            ci_high = mean + z * se
            ci_lows.append(ci_low)
            ci_highs.append(ci_high)
            means.append(mean)
            if ci_low > 0 or ci_high < 0:
                excludes_zero_count += 1
        power = excludes_zero_count / simulations
        if power_at_max_n == 0.0 or n == n_grid[-1]:
            power_at_max_n = power
        if n80 is None and power >= POWER_TARGET:
            n80 = n
        grid_results.append({
            "n_episodes": n,
            "simulations": simulations,
            "power": power,
            "ci_excludes_zero_count": excludes_zero_count,
            "mean_ci_low": statistics.fmean(ci_lows) if ci_lows else 0.0,
            "mean_ci_high": statistics.fmean(ci_highs) if ci_highs else 0.0,
            "mean_total_pnl": statistics.fmean(means) if means else 0.0,
            "reaches_80pct_power": power >= POWER_TARGET,
        })

    return {
        "grid": grid_results,
        "n80": n80,
        "power_at_max_n": power_at_max_n,
        "n_grid_tested": len(grid_results),
    }


def compute_mde(episode_totals: List[float], n80: int, simulations: int, seed: int) -> Dict[str, Any]:
    """Minimum detectable effect: smallest mean episode PnL detectable with 80% power at n80."""
    if n80 is None or not episode_totals:
        return {"mde_mean_episode_pnl": None, "n80": None, "method": "N80 not found; MDE not computable"}

    rng = random.Random(seed + 1)
    pool = episode_totals
    observed_mean = statistics.fmean(pool)

    # Binary search over effect-size multipliers
    lo, hi = 0.0, 5.0
    best_mde = None
    for _ in range(24):
        mid = (lo + hi) / 2.0
        scaled = [v * mid for v in pool]
        excludes = 0
        for _ in range(simulations // 4):  # fewer sims for speed in search
            sample = [scaled[rng.randrange(len(scaled))] for _ in range(n80)]
            mean = statistics.fmean(sample)
            sd = statistics.pstdev(sample) if len(sample) > 1 else 0.0
            se = sd / math.sqrt(n80) if n80 > 0 else 0.0
            z = 1.959963984540054
            ci_low = mean - z * se
            ci_high = mean + z * se
            if ci_low > 0 or ci_high < 0:
                excludes += 1
        power = excludes / (simulations // 4)
        if power >= POWER_TARGET:
            best_mde = mid * observed_mean
            hi = mid
        else:
            lo = mid

    return {
        "mde_mean_episode_pnl": best_mde,
        "mde_multiplier_of_observed_mean": (best_mde / observed_mean) if (best_mde is not None and observed_mean != 0) else None,
        "observed_mean_episode_pnl": observed_mean,
        "n80": n80,
        "method": "binary search over effect-size multiplier; power estimated via episode-block bootstrap CI exclusion",
    }


def pre_register_decision_rule(n80: int | None, mde: float | None, hl_rate: Dict[str, Any]) -> Dict[str, Any]:
    """Pre-register the GO/NO-GO decision rule for the eventual Hyperliquid-native run."""
    # Expected episodes over the 283-day spec window at the observed HL partial rate
    spec_days = (parse_utc(SPEC_END) - parse_utc(SPEC_START)).total_seconds() / 86400.0
    expected_episodes = hl_rate["crash_events_per_day"] * spec_days

    return {
        "alpha": ALPHA,
        "power_target": POWER_TARGET,
        "n80_required_episodes": n80,
        "expected_hl_episodes_over_283d": expected_episodes,
        "episodes_gap": (n80 - expected_episodes) if (n80 is not None) else None,
        "mde_mean_episode_pnl": mde,
        "decision_rule": {
            "go_requires": [
                "is_hyperliquid_venue_data == true",
                "performance_evidence == true",
                "native archive covers full 283-day spec window (2025-12-20 .. 2026-09-28)",
                "C6-T3 episode-edge test: bootstrap 95% CI of total PnL excludes zero at alpha=0.05",
                "episode count >= N80 (>= 80% power)",
                "conditional permutation p(null >= canonical) < 0.05",
                "placebo portfolio: canonical PnL exceeds placebo distribution at alpha=0.05",
                "volume_filter_ok gate holds (trailing-24h >= $5M)",
            ],
            "no_go_if": [
                "any GO requirement fails",
                "native archive not obtained (REJECT_NOT_EVIDENCE persists)",
                "N < N80 (underpowered)",
                "CI includes zero",
                "permutation p >= 0.05",
            ],
            "flips_to_go_only_if": "Hyperliquid-native evidence clears every pre-registered requirement above",
        },
        "caveat": "This pre-registration is a design artifact. It does not constitute evidence, performance, or a verdict.",
    }


def render_md(payload: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# C11.2 — Hyperliquid-Native Power & Decision Pre-Registration")
    lines.append("")
    lines.append(f"**Generated (UTC):** {payload['generated_at_utc']}")
    lines.append(f"**Schema version:** {payload['schema_version']}")
    lines.append(f"**Verdict:** `{payload['verdict']}`")
    lines.append(f"**is_hyperliquid_venue_data:** {payload['is_hyperliquid_venue_data']}")
    lines.append(f"**performance_evidence:** {payload['performance_evidence']}")
    lines.append("")
    lines.append("## Status")
    lines.append("- This is a **design / power pre-registration artifact only**.")
    lines.append("- It is **NOT** Hyperliquid performance evidence.")
    lines.append("- It is **NOT** a GO/NO-GO verdict.")
    lines.append("- It pre-specifies the eventual Hyperliquid-native campaign so it cannot be faked or avoided.")
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append("### Hyperliquid partial chain (observed crash-episode rate)")
    hl = payload["inputs"]["hyperliquid_partial_chain"]
    lines.append(f"- Source: `{hl['source']}` (sha256: {hl['sha256'][:16]}...)")
    lines.append(f"- Window: {hl['window_start']} .. {hl['window_end']}")
    lines.append(f"- Days observed: {hl['days_observed']:.1f}")
    lines.append(f"- Symbols: {hl['symbols']}, bars: {hl['bars']}")
    lines.append(f"- RSI(21)<20 crash events: {hl['rsi_crash_events']}")
    lines.append(f"- Confirmed signals: {hl['confirmed_signals']}")
    lines.append(f"- Crash events per day: {hl['crash_events_per_day']:.4f}")
    lines.append(f"- Expected episodes over 283-day spec window: {payload['decision_rule']['expected_hl_episodes_over_283d']:.1f}")
    lines.append("")
    lines.append("### Cross-venue effect-size priors (OKX + Binance)")
    for label, v in payload["inputs"]["cross_venue_priors"].items():
        lines.append(f"- {label}: {v['n_episodes']} episodes, {v['n_distinct_crash_days']} distinct crash days, "
                     f"canonical PnL {v['canonical_total_pnl']:.2f}, verdict `{v['verdict']}`")
        lines.append(f"  Source: `{v['source']}` (sha256: {v['sha256'][:16]}...)")
    lines.append("")
    lines.append("## Power grid results")
    pg = payload["power_grid"]
    lines.append(f"- Alpha: {ALPHA}, power target: {POWER_TARGET:.0%}")
    lines.append(f"- N grid tested: {pg['n_grid_tested']} values ({N_GRID_MIN}..{N_GRID_MAX}, step {N_GRID_STEP})")
    lines.append(f"- Simulations per N: {POWER_SIMULATIONS}")
    lines.append(f"- **N80 (episodes for >=80% power): {pg['n80']}**")
    lines.append(f"- Power at max N tested: {pg['power_at_max_n']:.4f}")
    lines.append("")
    lines.append("| N episodes | Power | CI excludes zero | Mean CI low | Mean CI high | Mean total PnL |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for row in pg["grid"]:
        lines.append(f"| {row['n_episodes']} | {row['power']:.4f} | {row['ci_excludes_zero_count']}/{row['simulations']} | "
                     f"{row['mean_ci_low']:.2f} | {row['mean_ci_high']:.2f} | {row['mean_total_pnl']:.2f} |")
    lines.append("")
    lines.append("## Minimum detectable effect (MDE)")
    mde = payload["mde"]
    lines.append("- N80: " + (str(mde['n80']) if mde.get('n80') is not None else "NOT FOUND in grid"))
    lines.append(f"- Observed mean episode PnL (cross-venue prior): {mde.get('observed_mean_episode_pnl', 'N/A')}")
    lines.append(f"- **MDE mean episode PnL: {mde.get('mde_mean_episode_pnl', 'N/A')}**")
    lines.append(f"- MDE as multiplier of observed mean: {mde.get('mde_multiplier_of_observed_mean', 'N/A')}")
    lines.append("")
    lines.append("## Pre-registered GO/NO-GO decision rule")
    dr = payload["decision_rule"]
    lines.append(f"- Alpha: {dr['alpha']}, power target: {dr['power_target']:.0%}")
    lines.append(f"- N80 required: {dr['n80_required_episodes']} episodes")
    lines.append(f"- Expected HL episodes over 283d: {dr['expected_hl_episodes_over_283d']:.1f}")
    lines.append(f"- Episode gap (N80 - expected): {dr['episodes_gap']}")
    lines.append("")
    lines.append("### GO requires (all):")
    for r in dr["decision_rule"]["go_requires"]:
        lines.append(f"  - {r}")
    lines.append("")
    lines.append("### NO-GO if (any):")
    for r in dr["decision_rule"]["no_go_if"]:
        lines.append(f"  - {r}")
    lines.append("")
    lines.append("### Flip to GO only if:")
    lines.append(f"  {dr['decision_rule']['flips_to_go_only_if']}")
    lines.append("")
    lines.append("## Caveat")
    lines.append("- " + dr["caveat"])
    lines.append("")
    lines.append("## Reproduction")
    lines.append("")
    lines.append("```bash")
    lines.append("PYTHONPATH=. /tmp/crs-venv/bin/python scripts/build_hyperliquid_native_power_prereg.py")
    lines.append("```")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="C11.2 Hyperliquid-native power & decision pre-registration")
    ap.add_argument("--out", default="research_state/hyperliquid_native_power_prereg", help="Output stem (no extension)")
    ap.add_argument("--seed", type=int, default=SEED, help="Random seed")
    args = ap.parse_args(argv)

    ts = iso_now()
    out_stem = args.out
    hl_rate = load_hl_partial_census()
    episode_totals, venues = load_cross_venue_episode_totals()

    # --- Power grid ---
    n_grid = list(range(N_GRID_MIN, N_GRID_MAX + 1, N_GRID_STEP))
    power = bootstrap_power_grid(episode_totals, n_grid, POWER_SIMULATIONS, args.seed)
    n80 = power["n80"]

    # --- MDE ---
    mde = compute_mde(episode_totals, n80, POWER_SIMULATIONS, args.seed)
    mde_value = mde.get("mde_mean_episode_pnl")

    # --- Decision rule ---
    decision = pre_register_decision_rule(n80, mde_value, hl_rate)

    # --- Assemble payload ---
    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": ts,
        "run_type": "hyperliquid_native_power_preregistration",
        "phase": "C11.2",
        "verdict": "PRE_REGISTRATION_DESIGN_ARTIFACT_NOT_VERDICT",
        "is_hyperliquid_venue_data": False,
        "cross_venue": True,
        "performance_evidence": False,
        "fabricated_data": False,
        "synthetic_data": False,
        "provenance_caveat": (
            "Cross-venue effect-size priors from OKX + Binance multi-year caches "
            "(is_hyperliquid_venue_data=false). Hyperliquid partial-chain crash rate "
            "from retained public-API partial window (not the 283-day spec window). "
            "This is a design/power pre-registration artifact, NOT performance evidence, "
            "NOT a verdict."
        ),
        "seed": args.seed,
        "method": {
            "episode_block_bootstrap_power_grid": True,
            "alpha": ALPHA,
            "power_target": POWER_TARGET,
            "simulations_per_n": POWER_SIMULATIONS,
            "n_grid_min": N_GRID_MIN,
            "n_grid_max": N_GRID_MAX,
            "n_grid_step": N_GRID_STEP,
            "ci_method": "normal_approximation_mean_pm_1_96_se",
            "mde_method": "binary_search_effect_size_multiplier",
        },
        "inputs": {
            "hyperliquid_partial_chain": hl_rate,
            "cross_venue_priors": venues,
            "pooled_episode_totals_count": len(episode_totals),
        },
        "power_grid": power,
        "mde": mde,
        "decision_rule": decision,
        "contract": {
            "is_design_artifact": True,
            "is_performance_evidence": False,
            "is_verdict": False,
            "blocks_fake_native_claims": True,
            "must_be_run_before_c11_3": True,
        },
    }

    clean_ts = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_json = REPO / f"{out_stem}_{clean_ts}.json"
    out_md = REPO / f"{out_stem}_{clean_ts}.md"

    out_json.write_text(json.dumps(payload, indent=2) + "\n")
    out_md.write_text(render_md(payload))

    print(f"hyperliquid_native_power_prereg: N80={n80} power_at_max={power['power_at_max_n']:.4f} "
          f"mde={mde_value} episodes_pool={len(episode_totals)}")
    print(f"wrote {out_json.relative_to(REPO)} and {out_md.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
