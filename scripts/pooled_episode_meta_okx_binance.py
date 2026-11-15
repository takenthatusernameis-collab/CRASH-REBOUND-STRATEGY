#!/usr/bin/env python3
"""C10.3 — Pooled dependence-aware episode meta-analysis (OKX + Binance UM).

Combines per-episode observed totals from the two independent multi-year venue
C6-T3 runs via episode-block bootstrap and a permutation null over the pooled
independent episode set. NO pooling of same-venue duplicates. CROSS-VENUE,
NOT Hyperliquid evidence. No synthetic data. No scipy dependency.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import random
import statistics
from pathlib import Path
from typing import Any, Dict, List

REPO = Path(__file__).resolve().parents[1]
OKX_EDGE = REPO / "research_state/episode_edge_okx_multiyear.json"
BIN_EDGE = REPO / "research_state/episode_edge_binance_um_multiyear.json"

PROVENANCE_CAVEAT = (
    "Real OKX/Binance UM exchange data, non-synthetic; CROSS-VENUE vs Hyperliquid spec; "
    "NOT Hyperliquid performance evidence. Pooling is across independent venues only."
)


def iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def quantile(sorted_vals: List[float], p: float) -> float:
    if not sorted_vals:
        return float("nan")
    k = (len(sorted_vals) - 1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return float(sorted_vals[int(k)])
    return float(sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f))


def load_episode_totals(path: Path, venue: str) -> List[Dict[str, Any]]:
    d = json.loads(path.read_text())
    b = d.get("episode_block_bootstrap", {})
    totals = b.get("observed_episode_totals", {})
    counts = b.get("episode_trade_counts", {})
    episodes_meta = d.get("episode_audit", {}).get("episodes", [])
    meta_by_id = {str(ep.get("episode_id")): ep for ep in episodes_meta}
    out = []
    for ep_id, total in totals.items():
        meta = meta_by_id.get(str(ep_id), {})
        out.append({
            "venue": venue,
            "episode_id": str(ep_id),
            "episode_key": f"{venue}:{ep_id}",
            "observed_total_pnl": float(total),
            "trade_count": int(counts.get(str(ep_id), meta.get("size", 0))),
            "start": meta.get("start"),
            "end": meta.get("end"),
            "symbols": meta.get("symbols", []),
        })
    # stable order
    out.sort(key=lambda x: (x["venue"], int(x["episode_id"]) if x["episode_id"].isdigit() else x["episode_id"]))
    return out


def bootstrap_pooled(episodes: List[Dict[str, Any]], seed: int, n: int) -> Dict[str, Any]:
    vals = [e["observed_total_pnl"] for e in episodes]
    m = len(vals)
    rng = random.Random(seed)
    obs_total = float(sum(vals))
    totals = []
    for _ in range(n):
        s = 0.0
        for _ in range(m):
            s += vals[rng.randrange(m)]
        totals.append(s)
    ts = sorted(totals)
    mean = statistics.fmean(totals)
    median = statistics.median(totals)
    ci = [quantile(ts, 0.025), quantile(ts, 0.975)]
    p_gt_0 = sum(1 for x in totals if x > 0) / n
    # rough n_needed: scale episodes (blocks) so that mean/sd * sqrt(n/n0)*z >= mean? approximate via normal on bootstrap sd
    sd = statistics.pstdev(totals) if len(totals) > 1 else 0.0
    n_needed = None
    if mean > 0 and sd > 0:
        # want lower 2.5% bound of mean*n_scale/sqrt-scale approx: mean - 1.96*sd/sqrt(k) > 0 => k > (1.96*sd/mean)^2 with k=n/n0
        k = (1.96 * sd / mean) ** 2
        n_needed = math.ceil(m * k)
    return {
        "resamples": n,
        "seed": seed,
        "episode_blocks": m,
        "observed_total_pnl": obs_total,
        "observed_mean_episode_pnl": statistics.fmean(vals),
        "observed_median_episode_pnl": statistics.median(vals),
        "bootstrap_total_pnl": {
            "mean": mean,
            "median": median,
            "stdev": sd,
            "p05": quantile(ts, 0.05),
            "p95": quantile(ts, 0.95),
            "ci_low_pnl_2p5": ci[0],
            "ci_high_pnl_97p5": ci[1],
            "prob_total_pnl_gt_0": p_gt_0,
        },
        "ci_excludes_zero": not (ci[0] <= 0.0 <= ci[1]),
        "approx_episode_blocks_needed_for_ci_excludes_zero": n_needed,
    }


def permutation_null(episodes: List[Dict[str, Any]], seed: int, n: int) -> Dict[str, Any]:
    """Sign-flip permutation null on episode totals: under H0 (no edge direction),
    each episode total is equally likely +/-|x| in sign contribution relative to 0?
    More directly: randomly flip sign of episode totals (centered null on direction)
    OR shuffle sign labels. A standard placebo is sign-flip permutation: total' = sum(s_i * x_i), s_i in {+1,-1}.
    Also report p_null_ge_canonical for the observed (positive) total.
    """
    vals = [e["observed_total_pnl"] for e in episodes]
    obs = float(sum(vals))
    rng = random.Random(seed)
    m = len(vals)
    totals = []
    ge = 0
    le_abs = 0
    for _ in range(n):
        s = 0.0
        for v in vals:
            s += v if rng.getrandbits(1) else -v
        totals.append(s)
        if s >= obs:
            ge += 1
        if abs(s) >= abs(obs):
            le_abs += 1
    ts = sorted(totals)
    return {
        "method": "episode_sign_flip_permutation",
        "draws": n,
        "seed": seed,
        "episode_blocks": m,
        "observed_total_pnl": obs,
        "null_mean": statistics.fmean(totals),
        "null_stdev": statistics.pstdev(totals) if len(totals) > 1 else 0.0,
        "null_p05": quantile(ts, 0.05),
        "null_p95": quantile(ts, 0.95),
        "p_null_ge_canonical_one_sided": ge / n,
        "p_null_abs_ge_abs_canonical_two_sided": le_abs / n,
        "canonical_percentile_le": sum(1 for x in totals if x <= obs) / n,
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--okx", default=str(OKX_EDGE))
    ap.add_argument("--binance", default=str(BIN_EDGE))
    ap.add_argument("--seed", type=int, default=20261115)
    ap.add_argument("--boot", type=int, default=20000)
    ap.add_argument("--perm", type=int, default=20000)
    ap.add_argument("--out-stem", default=None)
    args = ap.parse_args(argv)

    okx_path = Path(args.okx)
    bin_path = Path(args.binance)
    okx_eps = load_episode_totals(okx_path, "okx")
    bin_eps = load_episode_totals(bin_path, "binance_um")
    pooled = okx_eps + bin_eps

    boot = bootstrap_pooled(pooled, args.seed, args.boot)
    perm = permutation_null(pooled, args.seed + 1, args.perm)

    by_venue = {}
    for venue, eps in [("okx", okx_eps), ("binance_um", bin_eps)]:
        vals = [e["observed_total_pnl"] for e in eps]
        by_venue[venue] = {
            "episodes": len(eps),
            "total_pnl": float(sum(vals)),
            "mean_episode_pnl": statistics.fmean(vals) if vals else None,
            "median_episode_pnl": statistics.median(vals) if vals else None,
            "positive_episodes": sum(1 for v in vals if v > 0),
            "negative_episodes": sum(1 for v in vals if v < 0),
        }

    ci = boot["bootstrap_total_pnl"]
    verdict = "underpowered"
    if ci["ci_low_pnl_2p5"] > 0 and ci["prob_total_pnl_gt_0"] >= 0.95 and perm["p_null_ge_canonical_one_sided"] < 0.05:
        verdict = "pooled_positive_not_hyperliquid"
    elif ci["ci_high_pnl_97p5"] < 0:
        verdict = "pooled_negative_not_hyperliquid"

    result = {
        "schema_version": 1,
        "generated_at_utc": iso_now(),
        "phase": "C10.3",
        "script": "scripts/pooled_episode_meta_okx_binance.py",
        "provenance_caveat": PROVENANCE_CAVEAT,
        "is_hyperliquid_venue_data": False,
        "cross_venue": True,
        "independence_assumption": (
            "OKX and Binance UM are independent venues with distinct matching engines, "
            "liquidity, and microstructure; their per-episode PnL paths are treated as "
            "independent draws. Pooling combines episode blocks across these independent "
            "venues only — NO same-venue duplicates pooled. Crash episodes may be "
            "temporally aligned across venues (common market shocks) while per-trade "
            "execution/PnL remains venue-specific; this is stated, not hidden."
        ),
        "inputs": {
            "okx_episode_edge": str(okx_path.relative_to(REPO)) if okx_path.is_relative_to(REPO) else str(okx_path),
            "binance_episode_edge": str(bin_path.relative_to(REPO)) if bin_path.is_relative_to(REPO) else str(bin_path),
            "okx_sha256": sha256_file(okx_path),
            "binance_sha256": sha256_file(bin_path),
        },
        "by_venue": by_venue,
        "pooled_episode_count": len(pooled),
        "pooled_episodes": pooled,
        "episode_block_bootstrap": boot,
        "permutation_null": perm,
        "verdict": verdict,
        "verdict_detail": (
            f"pooled_episodes={len(pooled)}, observed_total={boot['observed_total_pnl']:.4f}, "
            f"bootstrap_95CI=[{ci['ci_low_pnl_2p5']:.4f},{ci['ci_high_pnl_97p5']:.4f}], "
            f"P(total>0)={ci['prob_total_pnl_gt_0']:.5f}, "
            f"perm_p_null_ge_canonical={perm['p_null_ge_canonical_one_sided']:.5f}, "
            f"perm_p_two_sided_abs={perm['p_null_abs_ge_abs_canonical_two_sided']:.5f}"
        ),
        "limitations": [
            "Pooling is across independent venues (OKX, Binance UM) only; no same-venue duplicates. Cross-venue episodes may be temporally correlated via common market shocks though PnL paths differ.",
            "Episode totals are taken from prior C6-T3 dependence-aware artifacts (98h linkage) as the unit of inference; no re-simulation performed.",
            "Sign-flip permutation tests directional edge of episode totals, not the full temporal-admission null; interpret alongside per-venue temporal permutation p-values.",
            "CROSS-VENUE, is_hyperliquid_venue_data=false; NOT Hyperliquid performance evidence.",
        ],
    }

    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stem = args.out_stem or f"pooled_episode_meta_okx_binance_{ts}"
    out_base = REPO / "research_state" / stem
    out_base.with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n")

    md = [
        f"# C10.3 — Pooled Episode Meta-Analysis OKX+Binance ({ts})",
        "",
        f"**Generated (UTC):** {result['generated_at_utc']}",
        f"**Verdict:** `{verdict}`",
        f"**Provenance:** {PROVENANCE_CAVEAT}",
        f"**is_hyperliquid_venue_data:** false",
        "",
        "## Independence assumption",
        result["independence_assumption"],
        "",
        "## By venue",
    ]
    for v, info in by_venue.items():
        md.append(f"- **{v}**: episodes={info['episodes']}, total_pnl={info['total_pnl']:.4f}, mean_ep={info['mean_episode_pnl']:.4f}, +ep={info['positive_episodes']}, -ep={info['negative_episodes']}")
    md += [
        "",
        "## Pooled dependence-aware inference",
        f"- Pooled episodes (blocks): **{len(pooled)}** (OKX {len(okx_eps)} + Binance {len(bin_eps)})",
        f"- Observed pooled total: **{boot['observed_total_pnl']:.4f}**",
        f"- Episode-block bootstrap (seed={args.seed}, n={args.boot}): mean={ci['mean']:.4f}, median={ci['median']:.4f}, 95% CI=[{ci['ci_low_pnl_2p5']:.4f}, {ci['ci_high_pnl_97p5']:.4f}], P(total>0)={ci['prob_total_pnl_gt_0']:.5f}",
        f"- CI excludes zero: **{boot['ci_excludes_zero']}**; approx episodes needed for CI>0: {boot.get('approx_episode_blocks_needed_for_ci_excludes_zero')}",
        f"- Permutation null sign-flip (seed={args.seed+1}, n={args.perm}): p_null_ge_canonical(one-sided)={perm['p_null_ge_canonical_one_sided']:.5f}, p_abs(two-sided)={perm['p_null_abs_ge_abs_canonical_two_sided']:.5f}, null_mean={perm['null_mean']:.4f}",
        "",
        "## Verdict",
        f"- `{verdict}` — {result['verdict_detail']}",
        "",
        "## Limitations",
        *[f"- {x}" for x in result["limitations"]],
        "",
        "## Reproduction",
        "```bash",
        f"PYTHONPATH=. /tmp/crs-venv/bin/python scripts/pooled_episode_meta_okx_binance.py --seed {args.seed} --boot {args.boot} --perm {args.perm}",
        "```",
        "",
    ]
    out_base.with_suffix(".md").write_text("\n".join(md))
    print(f"C10.3 verdict={verdict} pooled={len(pooled)} total={boot['observed_total_pnl']:.2f} ci=[{ci['ci_low_pnl_2p5']:.2f},{ci['ci_high_pnl_97p5']:.2f}] p_gt0={ci['prob_total_pnl_gt_0']:.4f} perm_p={perm['p_null_ge_canonical_one_sided']:.4f} out={out_base.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
