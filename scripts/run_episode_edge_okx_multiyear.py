#!/usr/bin/env python3
"""C6-T3: crash-episode dependence audit + conditional temporal-edge permutation
for the real OKX multi-year cross-venue campaign (2023-01-01..2026-09-28).

Adapted from run_episode_edge_okx.py (Phase O) but parameterized for the
multi-year artifacts. All runs use the real portfolio engine and the real
multi-year cache. No synthetic data. CROSS-VENUE, NOT Hyperliquid evidence.
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
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from src.data.provenance import load_provenance  # noqa: E402
from src.strategy.config import StrategyConfig  # noqa: E402
from src.strategy.crash_rebound import generate_signal as real_generate_signal  # noqa: E402
import scripts.run_portfolio as portfolio_mod  # noqa: E402

SCHEMA_VERSION = 1
EPISODE_LINK_HOURS = 98.0
VENUE_LABEL = "OKX"
PROVENANCE_CAVEAT = (
    "Real OKX exchange data, non-synthetic; CROSS-VENUE vs Hyperliquid spec; "
    "NOT Hyperliquid performance evidence."
)

CACHE_DIR = REPO / "research_state/cache/okx_1h_multiyear_20230101_20260928"
UNIVERSE_PATH = REPO / "research_state/universe_okx_multiyear_verified.json"
CENSUS_PATH = REPO / "research_state/crash_event_census_real_okx_multiyear.json"
CAMPAIGN_PATH = REPO / "research_state/campaign_results_real_okx_multiyear.json"


def iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_utc(text: str) -> dt.datetime:
    if str(text).endswith("Z"):
        text = str(text)[:-1] + "+00:00"
    try:
        return dt.datetime.fromisoformat(str(text)).astimezone(dt.timezone.utc)
    except Exception:
        return dt.datetime.strptime(str(text), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_candles(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text())
    if isinstance(data, dict):
        data = data.get("candles", data)
    return data


def load_inputs() -> Dict[str, Any]:
    manifest = load_provenance(str(CACHE_DIR / "provenance.json"))
    universe = json.loads(UNIVERSE_PATH.read_text())
    symbols = [str(s).upper() for s in (universe.get("selected_symbols") or universe.get("symbols") or [])]
    census = json.loads(CENSUS_PATH.read_text())
    campaign = json.loads(CAMPAIGN_PATH.read_text())
    candles: Dict[str, List[Dict[str, Any]]] = {}
    missing: List[str] = []
    for sym in symbols:
        path = CACHE_DIR / "candles" / f"{sym}.json"
        if not path.exists():
            missing.append(sym)
            continue
        candles[sym] = load_candles(path)
    cfg = StrategyConfig(
        use_rsi_trigger=True,
        enable_rebound_short=True,
        enable_eth_hedge=True,
        enable_volume_based_sizing=True,
        min_daily_volume_usd=5_000_000.0,
    )
    return {
        "cache_dir": CACHE_DIR,
        "manifest": manifest,
        "universe": universe,
        "symbols": symbols,
        "candles": candles,
        "missing": missing,
        "census": census,
        "campaign": campaign,
        "cfg": cfg,
    }


def build_memo(inp: Dict[str, Any]) -> Tuple[Dict[Tuple[str, int], Any], List[Dict[str, Any]], Dict[str, Any]]:
    candles = inp["candles"]
    cfg = inp["cfg"]
    ts_index: Dict[str, Dict[int, int]] = {}
    for sym, cs in candles.items():
        ts_index[sym] = {
            int(c.get("timestamp_ms") or c.get("time") or c.get("timestamp")): i
            for i, c in enumerate(cs)
            if c.get("timestamp_ms") is not None or c.get("time") is not None or c.get("timestamp") is not None
        }
    memo: Dict[Tuple[str, int], Any] = {}
    rows: List[Dict[str, Any]] = []
    for e in inp["census"]["events"]:
        sym = str(e.get("symbol", "")).upper()
        ts = e.get("bar_timestamp_ms")
        if ts is None:
            continue
        cs = candles.get(sym)
        idx = ts_index.get(sym, {}).get(int(ts)) if cs else None
        if idx is None:
            rows.append({
                "symbol": sym, "bar_timestamp_ms": int(ts), "bar_timestamp_utc": e.get("bar_timestamp_utc"),
                "bar_index": None, "signal": False, "reason": "bar_not_found",
                "signal_gate_pass": bool(e.get("signal_gate_pass")), "volume_gate_pass": bool(e.get("volume_gate_pass")),
                "bounce_confirmed": bool(e.get("bounce_confirmed")), "regime_min_price_ok": bool(e.get("regime_min_price_ok")),
                "trailing_24h_volume_usd": e.get("trailing_24h_volume_usd"), "desired_notional": e.get("desired_notional"),
                "blocking_reason_canonical": e.get("blocking_reason"), "trade_opened_canonical": bool(e.get("trade_opened")),
                "matched_trade_pnl_canonical": e.get("matched_trade_pnl"),
            })
            continue
        sig = real_generate_signal(cs[: idx + 1], symbol=sym, config=cfg, capital=100000.0)
        rec = {
            "symbol": sym, "bar_index": idx, "bar_timestamp_ms": int(ts), "bar_timestamp_utc": e.get("bar_timestamp_utc"),
            "rsi": e.get("rsi"), "signal": sig is not None,
            "signal_gate_pass": bool(e.get("signal_gate_pass")), "volume_gate_pass": bool(e.get("volume_gate_pass")),
            "bounce_confirmed": bool(e.get("bounce_confirmed")), "regime_min_price_ok": bool(e.get("regime_min_price_ok")),
            "trailing_24h_volume_usd": e.get("trailing_24h_volume_usd"), "desired_notional": e.get("desired_notional"),
            "blocking_reason_canonical": e.get("blocking_reason"), "trade_opened_canonical": bool(e.get("trade_opened")),
            "matched_trade_pnl_canonical": e.get("matched_trade_pnl"),
        }
        if sig is not None:
            memo[(sym, idx)] = sig
        rows.append(rec)
    meta = {
        "census_events": len(inp["census"]["events"]),
        "rows": len(rows),
        "memo_signals": len(memo),
        "signal_gate_events": sum(1 for r in rows if r.get("signal_gate_pass")),
        "memo_matches_signal_gate": len(memo) == sum(1 for r in rows if r.get("signal_gate_pass")),
        "symbols_with_signals": sorted({s for s, _ in memo}),
        "ts_index_symbols": len(ts_index),
    }
    return memo, rows, meta


def event_keys(memo: Dict[Tuple[str, int], Any], rows: List[Dict[str, Any]]) -> List[Tuple[str, int]]:
    return sorted({
        (str(r["symbol"]).upper(), int(r["bar_index"]))
        for r in rows if r.get("signal_gate_pass") and r.get("bar_index") is not None
        and (str(r["symbol"]).upper(), int(r["bar_index"])) in memo
    })


def _bar_time(rows: List[Dict[str, Any]]) -> Dict[Tuple[str, int], str]:
    out = {}
    for r in rows:
        if r.get("bar_index") is not None and r.get("bar_timestamp_utc"):
            out[(str(r["symbol"]).upper(), int(r["bar_index"]))] = str(r["bar_timestamp_utc"])
    return out


def cluster_episodes(keys: Sequence[Tuple[str, int]], times: Dict[Tuple[str, int], str], link_hours: float):
    if not keys:
        return []
    parsed = sorted(((parse_utc(times[k]), k) for k in keys if k in times), key=lambda x: x[0])
    if not parsed:
        return []
    episodes = []
    current = [parsed[0][1]]
    anchor = parsed[0][0]
    current_end = anchor
    for moment, key in parsed[1:]:
        if (moment - anchor).total_seconds() / 3600.0 <= link_hours:
            current.append(key)
            if moment > current_end:
                current_end = moment
        else:
            episodes.append({"start": anchor.strftime("%Y-%m-%dT%H:%M:%SZ"), "end": current_end.strftime("%Y-%m-%dT%H:%M:%SZ"), "keys": list(current)})
            current = [key]
            anchor = moment
            current_end = moment
    episodes.append({"start": anchor.strftime("%Y-%m-%dT%H:%M:%SZ"), "end": current_end.strftime("%Y-%m-%dT%H:%M:%SZ"), "keys": list(current)})
    for index, ep in enumerate(episodes):
        ep["episode_id"] = index
        ep["size"] = len(ep["keys"])
        ep["events"] = len(ep["keys"])
        ep["symbols"] = sorted({k[0] for k in ep["keys"]})
        ep["distinct_days"] = len({times[k][:10] for k in ep["keys"] if k in times})
    return episodes


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
    out = []
    for t in trades:
        out.append({
            "symbol": t.get("symbol"),
            "entry_timestamp": t.get("entry_timestamp"),
            "exit_timestamp": t.get("exit_timestamp"),
            "total_pnl": float(t.get("total_pnl", 0.0) or 0.0),
            "exit_reason": t.get("exit_reason"),
            "leg": t.get("leg"),
        })
    return {"trades": out, "num_trades": int(result.get("num_trades", len(out)))}


def _q(vals, p):
    if not vals:
        return 0.0
    s = sorted(vals)
    k = (len(s) - 1) * p
    f, c = math.floor(k), math.ceil(k)
    return float(s[int(k)]) if f == c else float(s[f] * (c - k) + s[c] * (k - f))


def block_bootstrap(trade_rows, episodes, times, resamples, seed, n_grid):
    ep_bounds = [(e["episode_id"], parse_utc(e["start"]), parse_utc(e["end"])) for e in episodes]
    def assign(entry_ms):
        try:
            moment = dt.datetime.fromtimestamp(int(entry_ms) / 1000.0, dt.timezone.utc)
        except Exception:
            return ep_bounds[0][0] if ep_bounds else 0
        best, best_gap = (ep_bounds[0][0] if ep_bounds else 0), None
        for eid, start, end in ep_bounds:
            gap = 0.0 if start <= moment <= end else min(abs((moment - start).total_seconds()), abs((moment - end).total_seconds()))
            if best_gap is None or gap < best_gap:
                best, best_gap = eid, gap
        return best
    groups = {e["episode_id"]: [] for e in episodes}
    for t in trade_rows:
        groups.setdefault(assign(t.get("entry_timestamp")), []).append(float(t.get("total_pnl") or 0.0))
    ep_ids = sorted(groups)
    rng = random.Random(seed)
    totals = []
    for _ in range(resamples):
        total = 0.0
        for _ in range(len(ep_ids)):
            total += sum(groups[ep_ids[rng.randrange(len(ep_ids))]])
        totals.append(total)
    observed = sum(sum(v) for v in groups.values())
    pool = [sum(groups[e]) for e in ep_ids if groups.get(e) is not None]
    grid = []
    rng2 = random.Random(seed + 1)
    for n in n_grid:
        if n <= 0:
            continue
        draws = []
        for _ in range(4000):
            picks = [pool[rng2.randrange(len(pool))] for _ in range(min(n, max(1, len(pool)*10)))]
            # resample n episode totals with replacement from observed pool
            draws.append(sum(pool[rng2.randrange(len(pool))] for _ in range(n)))
        lo, hi = _q(draws, 0.025), _q(draws, 0.975)
        grid.append({"n_episodes": n, "ci_low": lo, "ci_high": hi, "excludes_zero": (lo > 0 or hi < 0), "mean": statistics.fmean(draws) if draws else 0.0, "within_observed": n <= len(pool)})
    first = next((row["n_episodes"] for row in grid if row["excludes_zero"]), None)
    return {
        "resamples": resamples, "seed": seed, "episode_blocks": len(ep_ids),
        "episode_trade_counts": {str(e): len(groups[e]) for e in ep_ids},
        "observed_total_pnl": observed,
        "observed_episode_totals": {str(e): sum(groups[e]) for e in ep_ids},
        "bootstrap_total_pnl": {
            "mean": statistics.fmean(totals) if totals else 0.0,
            "median": statistics.median(totals) if totals else 0.0,
            "p05": _q(totals, 0.05), "p95": _q(totals, 0.95),
            "ci_low_pnl_2p5": _q(totals, 0.025), "ci_high_pnl_97p5": _q(totals, 0.975),
            "prob_total_pnl_gt_0": (sum(1 for t in totals if t > 0) / len(totals)) if totals else 0.0,
        },
        "n_needed_for_ci_excludes_zero": {"grid": grid, "observed_episodes": len(pool), "first_size_excluding_zero": first, "extrapolation_basis": "observed episode-total PnL resampled with replacement"},
    }


def conditional_permutation_null(inp, memo, rows, keys, canonical_pnl, draws, seed):
    # Eligible crash bars: real RSI(21)<20 census bars
    eligible = sorted({(str(r["symbol"]).upper(), int(r["bar_index"])) for r in rows if r.get("bar_index") is not None and r.get("rsi") is not None and float(r.get("rsi")) < 20.0})
    by_symbol = {}
    for sym, idx in eligible:
        by_symbol.setdefault(sym, []).append((sym, idx))
    observed_syms = sorted({k[0] for k in keys})
    per_symbol_count = {s: sum(1 for k in keys if k[0] == s) for s in observed_syms}
    total_possible = 1
    try:
        for s, count in per_symbol_count.items():
            total_possible *= math.comb(len(by_symbol.get(s, [])), count)
    except Exception:
        total_possible = 10**18
    exact = total_possible <= 5000
    rng = random.Random(seed)
    subsets = []
    if exact:
        import itertools as it
        choices = [list(it.combinations(by_symbol.get(s, []), per_symbol_count[s])) for s in observed_syms]
        for combo in it.product(*choices):
            subset = []
            for part in combo:
                subset.extend(part)
            subsets.append(tuple(sorted(subset)))
    else:
        for _ in range(draws or 200):
            subset = []
            for s in observed_syms:
                pool_s = by_symbol.get(s, [])
                count = min(per_symbol_count[s], len(pool_s))
                if count <= 0:
                    continue
                subset.extend(rng.sample(pool_s, count))
            subsets.append(tuple(sorted(subset)))
    seen = set()
    results = []
    t0 = time.time()
    candles_active = {s: inp["candles"][s] for s in sorted({k[0] for k in memo} | {"ETH"}) if s in inp["candles"]}
    for subset in subsets:
        if subset in seen:
            continue
        seen.add(subset)
        active = {k: memo[k] for k in subset if k in memo}
        res = run_memo_portfolio(candles_active, inp["cfg"], active)
        results.append({"n_signals": len(active), "total_pnl": float(res.get("total_pnl", 0.0)), "num_trades": int(res.get("num_trades", 0))})
    pnls = [r["total_pnl"] for r in results]
    ge = sum(1 for p in pnls if p >= canonical_pnl)
    return {
        "method": "conditional permutation: event bars redrawn from the real RSI(21)<20 census with observed per-symbol multiplicity preserved; real portfolio engine",
        "mode": f"exact_enumeration:{len(results)}_draws" if exact else f"deterministic_seeded_draws:{len(results)}_seed:{seed}",
        "eligible_crash_bars": len(eligible),
        "observed_event_slots": len(keys),
        "observed_per_symbol": per_symbol_count,
        "distinct_possible_draws": total_possible if total_possible < 10**12 else "astronomical",
        "draws_evaluated": len(results),
        "seed": seed,
        "canonical_total_pnl": canonical_pnl,
        "null_total_pnl": {
            "mean": statistics.fmean(pnls) if pnls else 0.0,
            "median": statistics.median(pnls) if pnls else 0.0,
            "stdev": statistics.pstdev(pnls) if len(pnls) > 1 else 0.0,
            "min": min(pnls) if pnls else 0.0,
            "max": max(pnls) if pnls else 0.0,
            "p05": _q(pnls, 0.05), "p95": _q(pnls, 0.95),
            "ci_low_pnl_2p5": _q(pnls, 0.025), "ci_high_pnl_97p5": _q(pnls, 0.975),
            "prob_total_pnl_gt_0": (sum(1 for p in pnls if p > 0) / len(pnls)) if pnls else 0.0,
        },
        "canonical_percentile_le": (sum(1 for p in pnls if p <= canonical_pnl) / len(pnls)) if pnls else 0.0,
        "p_null_ge_canonical": (ge / len(pnls)) if pnls else 0.0,
        "n_null_ge_canonical": ge,
        "wall_seconds": time.time() - t0,
        "limitation": None if exact else "Exact enumeration infeasible (astronomical distinct draws); used deterministic seeded subset and reported seed/count.",
    }


def render_md(r):
    ep = r["episode_audit"]
    boot = r["episode_block_bootstrap"]
    perm = r["temporal_edge_permutation"]
    bt = boot["bootstrap_total_pnl"]
    native_label = "Hyperliquid-native" if r.get("is_hyperliquid_evidence") else "Cross-venue"
    lines = [
        f"# C6-T3 — Crash-Episode Dependence Audit & Conditional Temporal-Edge Test ({native_label})",
        "",
        f"**Generated (UTC):** {r['generated_at_utc']}",
        f"**Provenance:** {r['provenance_caveat']}",
        f"**Verdict:** `{r['verdict']}` ({'Hyperliquid-native evidence' if r.get('is_hyperliquid_evidence') else 'CROSS-VENUE; NOT Hyperliquid evidence'})",
        "",
        "## Inputs",
        f"- Canonical total PnL: **{r['inputs']['canonical_total_pnl']:.2f}** ({r['inputs']['canonical_num_trades']} trades)",
        f"- Signal-gate events: **{r['inputs']['signal_gate_events']}** (RSI<20 census {r['inputs']['census_events']})",
        f"- Campaign: `{r['inputs']['campaign_sha256']}`",
        "",
        "## Episode clustering (98h holding-horizon link)",
        f"- Episodes: **{ep['n_episodes']}**, distinct crash days: **{ep['n_distinct_crash_days']}**, symbols: **{ep['n_symbols']}**",
        f"- Largest episode: **{ep['largest_episode_events']}** events ({ep['largest_episode_share']:.1%})",
        "",
        "| Episode | Window (UTC) | Events | Symbols | Distinct days |",
        "|---|---|---|---|---|",
    ]
    for e in ep["episodes"]:
        lines.append(f"| {e['episode_id']} | {e['start']} .. {e['end']} | {e['events']} | {', '.join(e['symbols'])} | {e['distinct_days']} |")
    lines += [
        "",
        "## Episode-block bootstrap (resample crash episodes, not trades)",
        f"- Blocks: **{boot['episode_blocks']}**, resamples: **{boot['resamples']}**, seed: {boot['seed']}",
        f"- 95% CI total PnL: **[{bt['ci_low_pnl_2p5']:.2f}, {bt['ci_high_pnl_97p5']:.2f}]**",
        f"- Mean: **{bt['mean']:.2f}**, Median: **{bt['median']:.2f}**, P(total PnL>0): **{bt['prob_total_pnl_gt_0']:.4f}**",
        f"- First grid size excluding zero: **{boot['n_needed_for_ci_excludes_zero']['first_size_excluding_zero']}**",
        "",
        "## Conditional temporal-edge permutation (crash-day conditioned, real engine)",
        f"- Mode: `{perm['mode']}`",
        f"- Eligible real RSI<20 bars: **{perm['eligible_crash_bars']}**, draws evaluated: **{perm['draws_evaluated']}**",
        f"- Null mean: **{perm['null_total_pnl']['mean']:.2f}**, median: **{perm['null_total_pnl']['median']:.2f}**",
        f"- Canonical percentile: **{perm['canonical_percentile_le']:.2%}**, p(placebo>=canonical): **{perm['p_null_ge_canonical']:.4f}** ({perm['n_null_ge_canonical']}/{perm['draws_evaluated']})",
    ]
    if perm.get("limitation"):
        lines.append(f"- Limitation: {perm['limitation']}")
    lines += ["", "## Reproduction", "", "```bash", "PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_episode_edge_okx_multiyear.py --draws 200 --seed 20261114", "```", ""]
    return "\n".join(lines)


def run(draws, seed, out_stem):
    t0 = time.time()
    inp = load_inputs()
    memo, rows, meta = build_memo(inp)
    keys = event_keys(memo, rows)
    times = _bar_time(rows)
    candles_active = {s: inp["candles"][s] for s in sorted({k[0] for k in memo} | {"ETH"}) if s in inp["candles"]}
    canonical = run_memo_portfolio(candles_active, inp["cfg"], memo)
    canonical_pnl = float(canonical.get("total_pnl", 0.0))
    episodes = cluster_episodes(keys, times, EPISODE_LINK_HOURS)
    episode_sizes = [e["size"] for e in episodes]
    largest = max(episode_sizes) if episode_sizes else 0
    distinct_days = sorted({times[k][:10] for k in keys if k in times})
    ts = trade_summary(canonical)
    boot = block_bootstrap(ts["trades"], episodes, times, 20000, seed, list(range(2, 41)))
    perm = conditional_permutation_null(inp, memo, rows, keys, canonical_pnl, draws, seed)
    verdict = "underpowered"
    # keep honest: positive evidence only if CI excludes 0 and permutation significant - unlikely but don't hardcode
    bt = boot["bootstrap_total_pnl"]
    if bt["ci_low_pnl_2p5"] > 0 and perm["p_null_ge_canonical"] < 0.05:
        verdict = "hyperliquid_native_positive" if is_native else "cross_venue_positive_not_hyperliquid"
    is_native = "native" in VENUE_LABEL.lower() or "hyperliquid" in VENUE_LABEL.lower()
    result = {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": iso_now(),
        "phase": "C6-T3",
        "provenance_caveat": PROVENANCE_CAVEAT,
        "is_hyperliquid_evidence": is_native,
        "cross_venue": not is_native,
        "venue_label": VENUE_LABEL,
        "method": "Crash-episode dependence audit (98h single-linkage) + conditional temporal-edge permutation + episode-block bootstrap. Real portfolio engine, real multi-year " + VENUE_LABEL + " cache.",
        "seed": seed,
        "inputs": {
            "census_events": meta["census_events"],
            "signal_gate_events": meta["signal_gate_events"],
            "memo_signals": meta["memo_signals"],
            "memo_matches_signal_gate": meta["memo_matches_signal_gate"],
            "canonical_total_pnl": canonical_pnl,
            "canonical_num_trades": int(canonical.get("num_trades", 0)),
            "campaign_sha256": sha256_file(CAMPAIGN_PATH),
            "census_sha256": sha256_file(CENSUS_PATH),
            "cache_dir": str(CACHE_DIR),
        },
        "episode_audit": {
            "link_hours": EPISODE_LINK_HOURS,
            "n_events": len(keys),
            "n_episodes": len(episodes),
            "n_symbols": len({k[0] for k in keys}),
            "n_distinct_crash_days": len(distinct_days),
            "distinct_crash_days": distinct_days,
            "largest_episode_events": largest,
            "largest_episode_share": (largest / len(keys)) if keys else 0.0,
            "mean_episode_size": statistics.fmean(episode_sizes) if episode_sizes else 0.0,
            "episodes": episodes,
            "effective_independent_sample": {"trades": int(canonical.get("num_trades", 0)), "symbols": len({k[0] for k in keys}), "episodes": len(episodes), "distinct_crash_days": len(distinct_days)},
        },
        "episode_block_bootstrap": boot,
        "temporal_edge_permutation": perm,
        "canonical_replay": trade_summary(canonical),
        "verdict": verdict,
        "wall_seconds": time.time() - t0,
        "limitations": [
            "CROSS-VENUE " + VENUE_LABEL + " multi-year cache; NOT Hyperliquid performance evidence.",
            "Permutation preserves observed per-symbol multiplicity and conditions on real RSI<20 crash bars; it tests timing, not detector existence.",
            "Episode clustering uses 98h holding horizon; different link changes counts but not dependence fact.",
            "Power extrapolation is based on observed episode distribution only.",
        ],
    }
    out_base = REPO / "research_state" / out_stem
    out_base.with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n")
    out_base.with_suffix(".md").write_text(render_md(result))
    print(f"episode_edge_multiyear: events={len(keys)} episodes={len(episodes)} days={len(distinct_days)} trades={canonical.get('num_trades')} pnl={canonical_pnl:.2f} perm_p={perm['p_null_ge_canonical']:.4f} boot_CI=[{bt['ci_low_pnl_2p5']:.2f},{bt['ci_high_pnl_97p5']:.2f}] wall={time.time()-t0:.1f}s verdict={verdict}")
    return result


def main(argv=None):
    global CACHE_DIR, UNIVERSE_PATH, CENSUS_PATH, CAMPAIGN_PATH, PROVENANCE_CAVEAT, VENUE_LABEL
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20261114)
    ap.add_argument("--out", default="episode_edge_okx_multiyear")
    ap.add_argument("--cache-dir", default=str(CACHE_DIR), help="Verified cache dir (default: canonical OKX multi-year)")
    ap.add_argument("--universe", default=str(UNIVERSE_PATH), help="Universe JSON (default: canonical OKX multi-year)")
    ap.add_argument("--census", default=str(CENSUS_PATH), help="Crash-event census JSON (default: canonical OKX multi-year)")
    ap.add_argument("--campaign", default=str(CAMPAIGN_PATH), help="Campaign results JSON (default: canonical OKX multi-year)")
    ap.add_argument("--venue-label", default="OKX", help="Venue label used in provenance strings (e.g. 'Binance UM')")
    args = ap.parse_args(argv)
    CACHE_DIR = Path(args.cache_dir)
    UNIVERSE_PATH = Path(args.universe)
    CENSUS_PATH = Path(args.census)
    CAMPAIGN_PATH = Path(args.campaign)
    VENUE_LABEL = str(args.venue_label)
    is_native = "native" in VENUE_LABEL.lower() or "hyperliquid" in VENUE_LABEL.lower()
    if is_native:
        PROVENANCE_CAVEAT = (
            f"Real {VENUE_LABEL} data, non-synthetic; node-derived (Ironflow HF, CC BY 4.0), "
            "NOT the venue's own candleSnapshot; Hyperliquid-native evidence (not cross-venue)."
        )
    else:
        PROVENANCE_CAVEAT = (
            f"Real {VENUE_LABEL} exchange data, non-synthetic; CROSS-VENUE vs Hyperliquid spec; "
            "NOT Hyperliquid performance evidence."
        )
    run(args.draws, args.seed, args.out)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
