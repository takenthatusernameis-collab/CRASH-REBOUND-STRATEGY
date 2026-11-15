#!/usr/bin/env python3
"""C10.2 — Conditioned full-portfolio placebo for Binance UM multi-year campaign.

Thin venue-parameterized runner mirroring run_portfolio_placebo_okx_multiyear.py.
Deterministic seeded random admission subsets run through the real portfolio engine;
preserves gates, sizing, cap, occupancy, hedge, fees, funding and liquidation.
CROSS-VENUE, NOT Hyperliquid evidence. No synthetic data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import multiprocessing as mp
import os
import random
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from src.data.provenance import load_provenance  # noqa: E402
from src.strategy.config import StrategyConfig  # noqa: E402
from src.strategy.crash_rebound import generate_signal as real_generate_signal  # noqa: E402
import scripts.run_portfolio as portfolio_mod  # noqa: E402

PROVENANCE_CAVEAT = (
    "Real Binance UM exchange data, non-synthetic; CROSS-VENUE vs Hyperliquid spec; "
    "NOT Hyperliquid performance evidence."
)


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
        if ts is None:
            continue
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


_WORKER_STATE = {}


def _init_placebo_worker(candles_active, memo, cfg):
    _WORKER_STATE["candles"] = candles_active
    _WORKER_STATE["memo"] = memo
    _WORKER_STATE["cfg"] = cfg


def _run_placebo_draw(sub):
    memo = _WORKER_STATE["memo"]
    res = run_memo_portfolio(
        _WORKER_STATE["candles"], _WORKER_STATE["cfg"], {k: memo[k] for k in sub if k in memo}
    )
    return {"num_trades": int(res.get("num_trades", 0)), "total_pnl": float(res.get("total_pnl", 0.0))}


def render_md(result, venue_label):
    pl = result["placebo"]; can = result["canonical"]; s = pl["summary"]
    lines = [
        f"# C10.2 — Full-Portfolio Placebo ({venue_label} Multi-Year, Cross-Venue)",
        "", f"**Generated (UTC):** {result['generated_at_utc']}", f"**Provenance:** {result['provenance_caveat']}",
        f"**Mode:** `{result['mode']}` (exact enumeration infeasible; deterministic seeded subset)", f"**Verdict:** `{result['verdict']}`",
        f"**is_hyperliquid_venue_data:** false",
        "", "## Canonical", f"- Trades: **{can['trades']}**, total PnL: **{can['total_pnl']:.6f}**", f"- Replay: {can['replay']['num_trades']} trades, {can['replay']['total_pnl']:.6f}",
        "", "## Placebo", f"- Pool signal-gate events: **{result['pool']['signal_gate_events']}**, choose_k (canonical admitted): **{result['pool']['choose_k']}**",
        f"- Runs: **{pl['runs']}**, seed: {result['seed']}",
        f"- Mean: **{s['mean']:.2f}**, median: **{s['median']:.2f}**, p05: **{s['p05']:.2f}**, p95: **{s['p95']:.2f}**",
        f"- Canonical percentile: **{pl['canonical_percentile_le']:.4f}**, p(placebo>=canonical): **{pl['p_ge_canonical']:.4f}**",
        f"- P(placebo>0): **{pl['prob_total_pnl_positive']:.4f}**",
        "", "## Limitation", "- Exact enumeration infeasible; deterministic seeded random subsets used (documented seed and count).",
        "- Tests admission/cap/occupancy selection within the observed gate-passing pool, not temporal crash timing.",
        f"- CROSS-VENUE {venue_label}; NOT Hyperliquid performance evidence.",
        "", "## Reproduction", "```bash", result.get("repro_cmd", ""), "```", ""
    ]
    return "\n".join(lines)


def run(cache_dir, universe_path, census_path, campaign_path, venue_label, draws, seed, out_stem, jobs=1):
    t0 = time.time()
    manifest = load_provenance(str(cache_dir / "provenance.json"))
    universe = json.loads(universe_path.read_text())
    symbols = [str(s).upper() for s in (universe.get("selected_symbols") or universe.get("symbols") or [])]
    census = json.loads(census_path.read_text())
    campaign = json.loads(campaign_path.read_text())
    candles = {}
    missing = []
    for sym in symbols:
        path = cache_dir / "candles" / f"{sym}.json"
        if not path.exists():
            missing.append(sym); continue
        candles[sym] = load_candles(path)
    cfg = StrategyConfig(use_rsi_trigger=True, enable_rebound_short=True, enable_eth_hedge=True,
                         enable_volume_based_sizing=True, min_daily_volume_usd=5_000_000.0)
    inp = {"cache_dir": cache_dir, "manifest": manifest, "universe": universe, "symbols": symbols,
           "candles": candles, "missing": missing, "census": census, "campaign": campaign, "cfg": cfg}

    memo, rows, meta = build_memo(inp)
    keys = sorted({(str(r["symbol"]).upper(), int(r["bar_index"])) for r in rows if r.get("signal_gate_pass") and r.get("bar_index") is not None and (str(r["symbol"]).upper(), int(r["bar_index"])) in memo})
    if meta["memo_signals"] != meta["signal_gate_events"] or not meta["memo_matches_signal_gate"]:
        raise SystemExit(f"memo mismatch: signals={meta['memo_signals']} gate={meta['signal_gate_events']}")
    candles_active = {s: inp["candles"][s] for s in sorted({k[0] for k in memo} | {"ETH"}) if s in inp["candles"]}
    canon_run = run_memo_portfolio(candles_active, inp["cfg"], memo)
    canon_summary = trade_summary(canon_run)

    admitted = sorted({(str(r["symbol"]).upper(), int(r["bar_index"])) for r in rows if r.get("trade_opened_canonical") and r.get("bar_index") is not None and (str(r["symbol"]).upper(), int(r["bar_index"])) in memo})
    choose_k = len(admitted) if admitted else canon_summary["num_trades"]
    choose_k = min(choose_k, len(keys))
    if admitted and len(admitted) == choose_k:
        replay = run_memo_portfolio(candles_active, inp["cfg"], {k: memo[k] for k in admitted if k in memo})
        replay_summary = trade_summary(replay)
    else:
        replay_summary = canon_summary

    rng = random.Random(seed)
    subsets = [tuple(sorted(rng.sample(keys, choose_k))) for _ in range(draws)]
    if jobs > 1 and "fork" in mp.get_all_start_methods():
        ctx = mp.get_context("fork")
        with ctx.Pool(
            processes=jobs,
            initializer=_init_placebo_worker,
            initargs=(candles_active, memo, inp["cfg"]),
        ) as pool:
            results = pool.map(_run_placebo_draw, subsets, chunksize=1)
    else:
        results = []
        for sub in subsets:
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
    repro = (
        f"PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_binance_um_multiyear.py "
        f"--draws {draws} --seed {seed} --out {out_stem}"
    )
    result = {
        "schema_version": 1, "generated_at_utc": iso_now(), "phase": "C10.2",
        "provenance_caveat": PROVENANCE_CAVEAT, "is_hyperliquid_evidence": False, "is_hyperliquid_venue_data": False, "cross_venue": True,
        "venue_label": venue_label,
        "method": "Deterministic seeded full-portfolio placebo: random gate-passing event subsets of fixed size run through real portfolio engine; preserves gates/sizing/cap/occupancy/hedge/fees/funding/liquidation.",
        "mode": f"deterministic_seeded_draws:{len(results)}_choose_{choose_k}_of_{len(keys)}",
        "seed": seed,
        "execution": {"jobs": jobs, "parallel_start_method": "fork" if jobs > 1 and "fork" in mp.get_all_start_methods() else "serial"},
        "inputs": {
            "cache_dir": str(cache_dir.relative_to(REPO)) if cache_dir.is_relative_to(REPO) else str(cache_dir),
            "universe": str(universe_path.relative_to(REPO)) if universe_path.is_relative_to(REPO) else str(universe_path),
            "campaign": str(campaign_path.relative_to(REPO)) if campaign_path.is_relative_to(REPO) else str(campaign_path),
            "census": str(census_path.relative_to(REPO)) if census_path.is_relative_to(REPO) else str(census_path),
            "campaign_sha256": sha256_file(campaign_path), "census_sha256": sha256_file(census_path),
            "missing_symbols": missing,
        },
        "canonical": {"trades": canon_summary["num_trades"], "total_pnl": canon_summary["total_pnl"], "replay": replay_summary, "admitted_keys_count": len(admitted)},
        "pool": {"signal_gate_events": len(keys), "choose_k": choose_k, "exact_combinations_infeasible": True},
        "placebo": pl,
        "verdict": verdict,
        "wall_seconds": time.time() - t0,
        "repro_cmd": repro,
        "limitations": [
            "Exact enumeration infeasible; used deterministic seeded subset (seed/count documented).",
            "Tests admission/cap/occupancy selection on observed pool, not temporal crash timing.",
            f"CROSS-VENUE {venue_label}; NOT Hyperliquid performance evidence.",
        ],
    }
    out_base = REPO / "research_state" / out_stem
    out_base.with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n")
    out_base.with_suffix(".md").write_text(render_md(result, venue_label))
    print(f"placebo_{venue_label}: pool={len(keys)} choose={choose_k} runs={draws} canon_pnl={canon_summary['total_pnl']:.2f} p_ge={pl['p_ge_canonical']:.4f} pct={pl['canonical_percentile_le']:.4f} wall={time.time()-t0:.1f}s -> {out_base.name}")
    return result


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache-dir", default="research_state/cache/binance_um_1h_multiyear_20230101_20260928")
    ap.add_argument("--universe", default="research_state/universe_binance_um_multiyear_verified.json")
    ap.add_argument("--census", default="research_state/crash_event_census_real_binance_um_multiyear.json")
    ap.add_argument("--campaign", default="research_state/campaign_results_real_binance_um_multiyear.json")
    ap.add_argument("--venue-label", default="Binance UM")
    ap.add_argument("--draws", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20261114)
    ap.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
    ap.add_argument("--out", default="placebo_portfolio_binance_um_multiyear")
    args = ap.parse_args(argv)
    run(REPO / args.cache_dir, REPO / args.universe, REPO / args.census, REPO / args.campaign,
        args.venue_label, args.draws, args.seed, args.out, args.jobs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
