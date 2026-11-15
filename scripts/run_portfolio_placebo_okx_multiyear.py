#!/usr/bin/env python3
"""C6-T3: conditioned full-portfolio placebo for the OKX multi-year campaign.

Exact enumeration of C(55,42) is infeasible. This script uses a deterministic,
seeded, documented set of random admission subsets of the gate-passing event pool,
run through the real portfolio engine with all other signals masked. It preserves
gates, sizing, cap, occupancy, hedge, fees, funding and liquidation.
CROSS-VENUE, NOT Hyperliquid evidence. No synthetic data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from src.data.provenance import load_provenance  # noqa: E402
from src.strategy.config import StrategyConfig  # noqa: E402
from src.strategy.crash_rebound import generate_signal as real_generate_signal  # noqa: E402
import scripts.run_portfolio as portfolio_mod  # noqa: E402

PROVENANCE_CAVEAT = (
    "Real OKX exchange data, non-synthetic; CROSS-VENUE vs Hyperliquid spec; "
    "NOT Hyperliquid performance evidence."
)

CACHE_DIR = REPO / "research_state/cache/okx_1h_multiyear_20230101_20260928"
UNIVERSE_PATH = REPO / "research_state/universe_okx_multiyear_verified.json"
CENSUS_PATH = REPO / "research_state/crash_event_census_real_okx_multiyear.json"
CAMPAIGN_PATH = REPO / "research_state/campaign_results_real_okx_multiyear.json"


def iso_now():
    import datetime as dt
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_candles(path):
    data = json.loads(path.read_text())
    if isinstance(data, dict):
        data = data.get("candles", data)
    return data


def quantile(sorted_vals, p):
    if not sorted_vals:
        return float("nan")
    k = (len(sorted_vals) - 1) * p
    f = math.floor(k); c = math.ceil(k)
    if f == c:
        return float(sorted_vals[int(k)])
    return float(sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f))


def summarize(vals):
    s = sorted(float(v) for v in vals)
    return {
        "n": len(s), "mean": statistics.fmean(s), "median": statistics.median(s),
        "stdev": statistics.pstdev(s) if len(s) > 1 else 0.0,
        "min": s[0], "max": s[-1],
        "p05": quantile(s, 0.05), "p25": quantile(s, 0.25), "p75": quantile(s, 0.75), "p95": quantile(s, 0.95),
    }


def load_inputs():
    manifest = load_provenance(str(CACHE_DIR / "provenance.json"))
    universe = json.loads(UNIVERSE_PATH.read_text())
    symbols = [str(s).upper() for s in (universe.get("selected_symbols") or universe.get("symbols") or [])]
    census = json.loads(CENSUS_PATH.read_text())
    campaign = json.loads(CAMPAIGN_PATH.read_text())
    candles = {}
    missing = []
    for sym in symbols:
        path = CACHE_DIR / "candles" / f"{sym}.json"
        if not path.exists():
            missing.append(sym); continue
        candles[sym] = load_candles(path)
    cfg = StrategyConfig(use_rsi_trigger=True, enable_rebound_short=True, enable_eth_hedge=True,
                         enable_volume_based_sizing=True, min_daily_volume_usd=5_000_000.0)
    return {"cache_dir": CACHE_DIR, "manifest": manifest, "universe": universe, "symbols": symbols,
            "candles": candles, "missing": missing, "census": census, "campaign": campaign, "cfg": cfg}


def build_memo(inp):
    candles = inp["candles"]; cfg = inp["cfg"]
    ts_index = {}
    for sym, cs in candles.items():
        ts_index[sym] = {int(c.get("timestamp") or c.get("timestamp_ms") or c.get("time")): i for i, c in enumerate(cs)
                         if c.get("timestamp") is not None or c.get("timestamp_ms") is not None or c.get("time") is not None}
    memo = {}; rows = []
    for e in inp["census"]["events"]:
        sym = str(e.get("symbol", "")).upper()
        ts = e.get("bar_timestamp_ms")
        if ts is None: continue
        cs = candles.get(sym)
        idx = ts_index.get(sym, {}).get(int(ts)) if cs else None
        if idx is None:
            rows.append({"symbol": sym, "bar_index": None, "bar_timestamp_ms": int(ts), "bar_timestamp_utc": e.get("bar_timestamp_utc"),
                         "signal": False, "signal_gate_pass": bool(e.get("signal_gate_pass")), "trade_opened_canonical": bool(e.get("trade_opened"))})
            continue
        sig = real_generate_signal(cs[: idx + 1], symbol=sym, config=cfg, capital=100000.0)
        rec = {"symbol": sym, "bar_index": idx, "bar_timestamp_ms": int(ts), "bar_timestamp_utc": e.get("bar_timestamp_utc"),
               "signal": sig is not None, "signal_gate_pass": bool(e.get("signal_gate_pass")), "trade_opened_canonical": bool(e.get("trade_opened"))}
        if sig is not None:
            memo[(sym, idx)] = sig
        rows.append(rec)
    meta = {"census_events": len(inp["census"]["events"]), "rows": len(rows), "memo_signals": len(memo),
            "signal_gate_events": sum(1 for r in rows if r.get("signal_gate_pass")),
            "memo_matches_signal_gate": len(memo) == sum(1 for r in rows if r.get("signal_gate_pass"))}
    return memo, rows, meta


def run_memo_portfolio(candles, cfg, memo):
    active = {k: v for k, v in memo.items()}
    def memo_generate_signal(candles_arg, symbol="TEST", config=None, capital=100000.0, risk_state=None, cache=None):
        return active.get((symbol, len(candles_arg) - 1))
    original = portfolio_mod.generate_signal
    portfolio_mod.generate_signal = memo_generate_signal
    try:
        return portfolio_mod.run_portfolio_simulation(candles, cfg, 100000.0, {"ETH": candles["ETH"]}, require_eth_hedge=True)
    finally:
        portfolio_mod.generate_signal = original


def trade_summary(result):
    trades = result.get("trades", []) or []
    return {"num_trades": int(result.get("num_trades", len(trades))), "total_pnl": float(result.get("total_pnl", 0.0)),
            "symbols": sorted({str(t.get("symbol")) for t in trades})}


def render_md(result):
    pl = result["placebo"]; can = result["canonical"]; s = pl["summary"]
    lines = [
        "# C6-T3 — Full-Portfolio Placebo (OKX Multi-Year, Cross-Venue)",
        "", f"**Generated (UTC):** {result['generated_at_utc']}", f"**Provenance:** {result['provenance_caveat']}",
        f"**Mode:** `{result['mode']}` (exact enumeration infeasible; deterministic seeded subset)", f"**Verdict:** `{result['verdict']}`",
        "", "## Canonical", f"- Trades: **{can['trades']}**, total PnL: **{can['total_pnl']:.6f}**", f"- Replay: {can['replay']['num_trades']} trades, {can['replay']['total_pnl']:.6f}",
        "", "## Placebo", f"- Pool signal-gate events: **{result['pool']['signal_gate_events']}**, choose_k (canonical admitted): **{result['pool']['choose_k']}**",
        f"- Runs: **{pl['runs']}**, seed: {result['seed']}",
        f"- Mean: **{s['mean']:.2f}**, median: **{s['median']:.2f}**, p05: **{s['p05']:.2f}**, p95: **{s['p95']:.2f}**",
        f"- Canonical percentile: **{pl['canonical_percentile_le']:.2%}**, p(placebo>=canonical): **{pl['p_ge_canonical']:.4f}**",
        f"- P(placebo>0): **{pl['prob_total_pnl_positive']:.4f}**",
        "", "## Limitation", "- C(55,42) is infeasible to enumerate exactly; deterministic seeded random subsets used (documented seed and count).",
        "- Tests admission/cap/occupancy selection within the observed gate-passing pool, not temporal crash timing.",
        "- CROSS-VENUE OKX; NOT Hyperliquid performance evidence.",
        "", "## Reproduction", "```bash", f"PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_okx_multiyear.py --draws {pl['runs']} --seed {result['seed']}", "```", ""
    ]
    return "\n".join(lines)


def run(draws, seed, out_stem):
    t0 = time.time()
    inp = load_inputs()
    memo, rows, meta = build_memo(inp)
    keys = sorted({(str(r["symbol"]).upper(), int(r["bar_index"])) for r in rows if r.get("signal_gate_pass") and r.get("bar_index") is not None and (str(r["symbol"]).upper(), int(r["bar_index"])) in memo})
    if meta["memo_signals"] != meta["signal_gate_events"] or not meta["memo_matches_signal_gate"]:
        raise SystemExit(f"memo mismatch: signals={meta['memo_signals']} gate={meta['signal_gate_events']}")
    candles_active = {s: inp["candles"][s] for s in sorted({k[0] for k in memo} | {"ETH"}) if s in inp["candles"]}
    canon_run = run_memo_portfolio(candles_active, inp["cfg"], memo)
    canon_summary = trade_summary(canon_run)
    k = canon_summary["num_trades"]
    if k < 1 or k >= len(keys):
        # fallback: use events that actually opened in canonical mapping
        # but easier: choose_k = number of trades canonical produced? subset of signals admitted; trades < events due to occupancy/cap
        # better placebo: vary which k events are allowed where k is canonical admitted count (trades_opened) if known
        pass
    # determine canonical admitted (trade_opened) signal keys
    admitted = sorted({(str(r["symbol"]).upper(), int(r["bar_index"])) for r in rows if r.get("trade_opened_canonical") and r.get("bar_index") is not None and (str(r["symbol"]).upper(), int(r["bar_index"])) in memo})
    if not admitted:
        # fallback: infer by running with all and see - but easier use trade_opened count
        admitted = [k for k in keys if any(str(r.get("symbol")).upper()==k[0] and int(r.get("bar_index") or -1)==k[1] and r.get("trade_opened_canonical") for r in rows)]
    choose_k = len(admitted) if admitted else k
    choose_k = min(choose_k, len(keys))
    # replay canonical subset if admitted known
    if admitted and len(admitted) == choose_k:
        replay = run_memo_portfolio(candles_active, inp["cfg"], {k: memo[k] for k in admitted if k in memo})
        replay_summary = trade_summary(replay)
    else:
        replay_summary = canon_summary
    rng = random.Random(seed)
    results = []
    for _ in range(draws):
        sub = tuple(sorted(rng.sample(keys, choose_k)))
        res = run_memo_portfolio(candles_active, inp["cfg"], {k: memo[k] for k in sub if k in memo})
        results.append({"num_trades": int(res.get("num_trades", 0)), "total_pnl": float(res.get("total_pnl", 0.0))})
    pnls = [r["total_pnl"] for r in results]
    ge = sum(1 for x in pnls if x >= canon_summary["total_pnl"])
    le = sum(1 for x in pnls if x <= canon_summary["total_pnl"])
    pl = {
        "runs": len(results), "summary": summarize(pnls),
        "p_ge_canonical": ge / len(results) if results else None,
        "canonical_percentile_le": le / len(results) if results else None,
        "prob_total_pnl_positive": sum(1 for x in pnls if x > 0) / len(results) if results else None,
        "ci_low_pnl_2p5": quantile(sorted(pnls), 0.025), "ci_high_pnl_97p5": quantile(sorted(pnls), 0.975),
    }
    verdict = "underpowered"
    if pl["summary"]["p05"] > 0 and pl["p_ge_canonical"] < 0.05:
        verdict = "cross_venue_positive_not_hyperliquid"
    result = {
        "schema_version": 1, "generated_at_utc": iso_now(), "phase": "C6-T3",
        "provenance_caveat": PROVENANCE_CAVEAT, "is_hyperliquid_evidence": False, "cross_venue": True,
        "method": "Deterministic seeded full-portfolio placebo: random gate-passing event subsets of fixed size run through real portfolio engine; preserves gates/sizing/cap/occupancy/hedge/fees.",
        "mode": f"deterministic_seeded_draws:{len(results)}_choose_{choose_k}_of_{len(keys)}",
        "seed": seed,
        "inputs": {"campaign_sha256": sha256_file(CAMPAIGN_PATH), "census_sha256": sha256_file(CENSUS_PATH)},
        "canonical": {"trades": canon_summary["num_trades"], "total_pnl": canon_summary["total_pnl"], "replay": replay_summary, "admitted_keys_count": len(admitted)},
        "pool": {"signal_gate_events": len(keys), "choose_k": choose_k, "exact_combinations_infeasible": True},
        "placebo": pl,
        "verdict": verdict,
        "wall_seconds": time.time() - t0,
        "limitations": [
            "C(55,42)-class exact enumeration infeasible; used deterministic seeded subset (seed/count documented).",
            "Tests admission/cap/occupancy selection on observed pool, not temporal crash timing.",
            "CROSS-VENUE OKX; NOT Hyperliquid performance evidence.",
        ],
    }
    out_base = REPO / "research_state" / out_stem
    out_base.with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n")
    out_base.with_suffix(".md").write_text(render_md(result))
    print(f"placebo_multiyear: pool={len(keys)} choose={choose_k} runs={draws} canon_pnl={canon_summary['total_pnl']:.2f} p_ge={pl['p_ge_canonical']:.4f} pct={pl['canonical_percentile_le']:.4f} wall={time.time()-t0:.1f}s")
    return result


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20261114)
    ap.add_argument("--out", default="placebo_portfolio_okx_multiyear")
    args = ap.parse_args(argv)
    run(args.draws, args.seed, args.out)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
