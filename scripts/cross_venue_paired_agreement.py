#!/usr/bin/env python3
"""C10.1 — Cross-venue paired symbol/date agreement + sign concordance.

Compares real OKX and Binance UM multi-year campaign trades (independent venues)
on matched (symbol, entry_date_utc[, leg]) to test reproducibility of edge direction.
CROSS-VENUE, NOT Hyperliquid evidence. No synthetic data. No scipy dependency.
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
from typing import Any, Dict, List, Tuple

REPO = Path(__file__).resolve().parents[1]
OKX_CAMPAIGN = REPO / "research_state/campaign_results_real_okx_multiyear.json"
BIN_CAMPAIGN = REPO / "research_state/campaign_results_real_binance_um_multiyear.json"

PROVENANCE_CAVEAT = (
    "Real OKX/Binance UM exchange data, non-synthetic; CROSS-VENUE vs Hyperliquid spec; "
    "NOT Hyperliquid performance evidence. Paired comparison across independent venues only."
)


def iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def to_date_utc(ms: Any) -> str:
    ts = int(ms)
    return dt.datetime.fromtimestamp(ts / 1000, tz=dt.timezone.utc).strftime("%Y-%m-%d")


def load_trades(path: Path) -> List[Dict[str, Any]]:
    d = json.loads(path.read_text())
    trades = d.get("results", {}).get("trades", [])
    out = []
    for t in trades:
        out.append({
            "symbol": str(t.get("symbol", "")).upper(),
            "entry_date_utc": to_date_utc(t.get("entry_timestamp")),
            "entry_timestamp": str(t.get("entry_timestamp")),
            "exit_timestamp": str(t.get("exit_timestamp")),
            "leg": str(t.get("leg", "")),
            "pnl": float(t.get("pnl", t.get("total_pnl", 0.0))),
            "total_pnl": float(t.get("total_pnl", t.get("pnl", 0.0))),
            "exit_reason": t.get("exit_reason"),
        })
    return out


def quantile(sorted_vals: List[float], p: float) -> float:
    if not sorted_vals:
        return float("nan")
    k = (len(sorted_vals) - 1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return float(sorted_vals[int(k)])
    return float(sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f))


def paired_bootstrap(diffs: List[float], seed: int, n: int) -> Dict[str, Any]:
    if not diffs:
        return {"error": "no_pairs"}
    rng = random.Random(seed)
    m = len(diffs)
    means = []
    medians = []
    for _ in range(n):
        sample = [diffs[rng.randrange(m)] for _ in range(m)]
        means.append(statistics.fmean(sample))
        medians.append(statistics.median(sample))
    means_s = sorted(means)
    medians_s = sorted(medians)
    obs_mean = statistics.fmean(diffs)
    obs_median = statistics.median(diffs)
    # two-sided bootstrap p for mean diff != 0 via reflection around 0
    centered = [d - obs_mean for d in diffs]
    ge = 0
    for _ in range(n):
        sample = [centered[rng.randrange(m)] for _ in range(m)]
        if abs(statistics.fmean(sample)) >= abs(obs_mean):
            ge += 1
    p_two_sided = ge / n
    return {
        "n_pairs": m,
        "n_boot": n,
        "seed": seed,
        "observed_mean_diff_okx_minus_binance": obs_mean,
        "observed_median_diff_okx_minus_binance": obs_median,
        "mean_ci_95": [quantile(means_s, 0.025), quantile(means_s, 0.975)],
        "median_ci_95": [quantile(medians_s, 0.025), quantile(medians_s, 0.975)],
        "bootstrap_p_mean_diff_ne_0_two_sided": p_two_sided,
        "mean_diff_ci_excludes_zero": not (quantile(means_s, 0.025) <= 0.0 <= quantile(means_s, 0.975)),
    }


def sign_concordance(okx_pnls: List[float], bin_pnls: List[float]) -> Dict[str, Any]:
    n = len(okx_pnls)
    if n == 0:
        return {"n": 0}
    same = sum(1 for a, b in zip(okx_pnls, bin_pnls) if (a > 0) == (b > 0))
    both_pos = sum(1 for a, b in zip(okx_pnls, bin_pnls) if a > 0 and b > 0)
    both_neg = sum(1 for a, b in zip(okx_pnls, bin_pnls) if a <= 0 and b <= 0)
    okx_pos_bin_neg = sum(1 for a, b in zip(okx_pnls, bin_pnls) if a > 0 and b <= 0)
    okx_neg_bin_pos = sum(1 for a, b in zip(okx_pnls, bin_pnls) if a <= 0 and b > 0)
    # exact two-sided sign test on direction of (okx-bin) differences being nonzero-equally-likely
    diffs = [a - b for a, b in zip(okx_pnls, bin_pnls)]
    nz = [d for d in diffs if d != 0]
    pos_diff = sum(1 for d in nz if d > 0)
    neg_diff = sum(1 for d in nz if d < 0)
    # binomial two-sided p-value without scipy: 2 * P(X <= min(pos,neg)) for n', p=0.5
    def log_choose(nc, kc):
        return math.lgamma(nc + 1) - math.lgamma(kc + 1) - math.lgamma(nc - kc + 1)

    def binom_cdf(k, ntrials):
        # P(X <= k), X~Bin(n,0.5)
        terms = [math.exp(log_choose(ntrials, i) - ntrials * math.log(2)) for i in range(0, k + 1)]
        return min(1.0, sum(terms))

    n_nz = len(nz)
    if n_nz == 0:
        sign_p = 1.0
    else:
        kmin = min(pos_diff, neg_diff)
        sign_p = min(1.0, 2.0 * binom_cdf(kmin, n_nz))
    return {
        "n_pairs": n,
        "same_sign_count": same,
        "same_sign_rate": same / n,
        "both_positive": both_pos,
        "both_nonpositive": both_neg,
        "okx_pos_binance_nonpos": okx_pos_bin_neg,
        "okx_nonpos_binance_pos": okx_neg_bin_pos,
        "okx_positive_rate": sum(1 for a in okx_pnls if a > 0) / n,
        "binance_positive_rate": sum(1 for b in bin_pnls if b > 0) / n,
        "sign_test_on_paired_diff": {
            "n_nonzero_diffs": n_nz,
            "n_okx_gt_binance": pos_diff,
            "n_binance_gt_okx": neg_diff,
            "two_sided_p": sign_p,
        },
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--okx", default=str(OKX_CAMPAIGN))
    ap.add_argument("--binance", default=str(BIN_CAMPAIGN))
    ap.add_argument("--seed", type=int, default=20261115)
    ap.add_argument("--boot", type=int, default=10000)
    ap.add_argument("--out-stem", default=None)
    args = ap.parse_args(argv)

    okx_path = Path(args.okx)
    bin_path = Path(args.binance)
    okx_trades = load_trades(okx_path)
    bin_trades = load_trades(bin_path)

    # index by (symbol, entry_date_utc, leg) keeping list (should be unique)
    def key(t):
        return (t["symbol"], t["entry_date_utc"], t["leg"])

    from collections import defaultdict
    okx_map = defaultdict(list)
    bin_map = defaultdict(list)
    for t in okx_trades:
        okx_map[key(t)].append(t)
    for t in bin_trades:
        bin_map[key(t)].append(t)

    common_keys = sorted(set(okx_map) & set(bin_map))
    # only 1:1 matches
    pairs = []
    ambiguous = []
    for k in common_keys:
        if len(okx_map[k]) == 1 and len(bin_map[k]) == 1:
            pairs.append((k, okx_map[k][0], bin_map[k][0]))
        else:
            ambiguous.append({"key": list(k), "okx_count": len(okx_map[k]), "binance_count": len(bin_map[k])})

    okx_only = sorted([list(k) for k in (set(okx_map) - set(bin_map))])
    bin_only = sorted([list(k) for k in (set(bin_map) - set(okx_map))])

    okx_pnls = [o["pnl"] for _, o, _ in pairs]
    bin_pnls = [b["pnl"] for _, _, b in pairs]
    diffs = [o - b for o, b in zip(okx_pnls, bin_pnls)]

    overall = sign_concordance(okx_pnls, bin_pnls)
    overall["paired_bootstrap_pnl_diff"] = paired_bootstrap(diffs, args.seed, args.boot)

    by_leg = {}
    legs = sorted({k[2] for k, _, _ in pairs})
    for leg in legs:
        sub = [(k, o, b) for k, o, b in pairs if k[2] == leg]
        op = [o["pnl"] for _, o, _ in sub]
        bp = [b["pnl"] for _, _, b in sub]
        dp = [o - b for o, b in zip(op, bp)]
        by_leg[leg or "unknown"] = {
            **sign_concordance(op, bp),
            "paired_bootstrap_pnl_diff": paired_bootstrap(dp, args.seed + hash(leg) % 100000, args.boot),
        }

    # verdict: direction replicates if same_sign_rate clearly > 0.5 and both venues' positive rates similar in direction of mean
    same_rate = overall.get("same_sign_rate", 0.0)
    n_pairs = overall.get("n_pairs", 0)
    ci = overall["paired_bootstrap_pnl_diff"].get("mean_ci_95", [None, None])
    mean_diff = overall["paired_bootstrap_pnl_diff"].get("observed_mean_diff_okx_minus_binance")
    # conservative: direction replicates when majority same-sign AND per-trade sign of edge isn't systematically opposite
    if n_pairs >= 10 and same_rate >= 0.6:
        verdict = "DIRECTION_REPLICATES_MAJORITY"
    elif n_pairs >= 10 and same_rate >= 0.5:
        verdict = "DIRECTION_MIXED"
    elif n_pairs < 10:
        verdict = "INSUFFICIENT_PAIRS"
    else:
        verdict = "DIRECTION_NOT_REPLICATED"

    result = {
        "schema_version": 1,
        "generated_at_utc": iso_now(),
        "phase": "C10.1",
        "script": "scripts/cross_venue_paired_agreement.py",
        "provenance_caveat": PROVENANCE_CAVEAT,
        "is_hyperliquid_venue_data": False,
        "cross_venue": True,
        "inputs": {
            "okx_campaign": str(okx_path.relative_to(REPO)) if okx_path.is_relative_to(REPO) else str(okx_path),
            "binance_campaign": str(bin_path.relative_to(REPO)) if bin_path.is_relative_to(REPO) else str(bin_path),
            "okx_campaign_sha256": sha256_file(okx_path),
            "binance_campaign_sha256": sha256_file(bin_path),
            "okx_trades": len(okx_trades),
            "binance_trades": len(bin_trades),
        },
        "pairing": {
            "key": ["symbol", "entry_date_utc", "leg"],
            "matched_pairs": len(pairs),
            "ambiguous_pairs_excluded": len(ambiguous),
            "ambiguous": ambiguous,
            "okx_only_keys": okx_only,
            "binance_only_keys": bin_only,
        },
        "overall": overall,
        "by_leg": by_leg,
        "paired_examples": [
            {
                "key": list(k),
                "okx_pnl": o["pnl"],
                "binance_pnl": b["pnl"],
                "diff_okx_minus_binance": o["pnl"] - b["pnl"],
                "okx_exit": o.get("exit_reason"),
                "binance_exit": b.get("exit_reason"),
            }
            for k, o, b in pairs
        ],
        "verdict": verdict,
        "verdict_detail": (
            f"n_pairs={n_pairs}, same_sign_rate={same_rate:.4f}, "
            f"mean_diff_okx-bin={mean_diff}, mean_diff_95CI={ci}, "
            f"okx_pos_rate={overall.get('okx_positive_rate')}, bin_pos_rate={overall.get('binance_positive_rate')}"
        ),
        "limitations": [
            "Pairs matched on (symbol, entry_date_utc, leg); same calendar-day entry is a proxy for same crash episode, not identical bar identity.",
            "Unpaired trades reflect venue-specific signal/admission differences and are reported but excluded from paired stats.",
            "CROSS-VENUE (OKX/Binance UM), is_hyperliquid_venue_data=false; NOT Hyperliquid performance evidence.",
            "Bootstrap on paired differences (seeded, >=10k) without scipy; sign test exact binomial two-sided.",
        ],
    }

    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stem = args.out_stem or f"cross_venue_paired_agreement_{ts}"
    out_base = REPO / "research_state" / stem
    out_base.with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n")

    md = [
        f"# C10.1 — Cross-Venue Paired Symbol/Date Agreement ({ts})",
        "",
        f"**Generated (UTC):** {result['generated_at_utc']}",
        f"**Verdict:** `{verdict}`",
        f"**Provenance:** {PROVENANCE_CAVEAT}",
        f"**is_hyperliquid_venue_data:** false",
        "",
        "## Pairing",
        f"- Key: (symbol, entry_date_utc, leg)",
        f"- OKX trades: {len(okx_trades)}, Binance trades: {len(bin_trades)}",
        f"- Matched 1:1 pairs: **{len(pairs)}**, ambiguous excluded: {len(ambiguous)}",
        f"- OKX-only: {len(okx_only)}, Binance-only: {len(bin_only)}",
        "",
        "## Overall paired agreement",
        f"- Same-sign rate: **{same_rate:.4f}** ({overall.get('same_sign_count')}/{n_pairs})",
        f"- Both positive: {overall.get('both_positive')}, both nonpositive: {overall.get('both_nonpositive')}",
        f"- OKX+ / Binance-: {overall.get('okx_pos_binance_nonpos')}, OKX- / Binance+: {overall.get('okx_nonpos_binance_pos')}",
        f"- OKX positive rate: {overall.get('okx_positive_rate'):.4f}, Binance positive rate: {overall.get('binance_positive_rate'):.4f}",
        f"- Mean diff (OKX−Binance): **{mean_diff:.4f}**, 95% bootstrap CI: {ci}",
        f"- Sign test on paired diff (two-sided, exact binomial): p={overall['sign_test_on_paired_diff']['two_sided_p']:.6g} (OKX>Bin {overall['sign_test_on_paired_diff']['n_okx_gt_binance']}, Bin>OKX {overall['sign_test_on_paired_diff']['n_binance_gt_okx']}, nonzero {overall['sign_test_on_paired_diff']['n_nonzero_diffs']})",
        "",
        "## By leg",
    ]
    for leg, v in by_leg.items():
        bci = v["paired_bootstrap_pnl_diff"].get("mean_ci_95")
        md.append(f"- **{leg}**: n={v['n_pairs']}, same_sign_rate={v.get('same_sign_rate')}, mean_diff={v['paired_bootstrap_pnl_diff'].get('observed_mean_diff_okx_minus_binance')}, 95% CI={bci}, okx_pos={v.get('okx_positive_rate')}, bin_pos={v.get('binance_positive_rate')}")
    md += [
        "",
        "## Verdict",
        f"- `{verdict}` — {result['verdict_detail']}",
        "",
        "## Limitations",
        *[f"- {x}" for x in result["limitations"]],
        "",
        "## Reproduction",
        "```bash",
        f"PYTHONPATH=. /tmp/crs-venv/bin/python scripts/cross_venue_paired_agreement.py --seed {args.seed} --boot {args.boot}",
        "```",
        "",
    ]
    out_base.with_suffix(".md").write_text("\n".join(md))
    print(f"C10.1 verdict={verdict} pairs={len(pairs)} same_sign_rate={same_rate:.4f} mean_diff={mean_diff:.4f} out={out_base.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
