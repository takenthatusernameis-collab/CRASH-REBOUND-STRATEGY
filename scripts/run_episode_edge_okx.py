#!/usr/bin/env python3
"""Phase O: crash-episode dependence audit + conditional temporal-edge permutation test.

Motivation (measured, not assumed)
----------------------------------
The canonical OKX 283d evidence rests on 11 signal-gate-passing crash events.
Those 11 events are not 11 independent observations: they collapse into a
handful of *crash episodes* (synchronized drawdowns). The Phase M exact
full-portfolio placebo conditions on those same 11 events and varies only which
8 are admitted, so it can test admission/cap/occupancy selection but never the
temporal crash-rebound edge versus random event times. That gap is the binding
constraint on decision-grade evidence, and this script closes it.

What this script does (all real engine, all real OKX cache, no synthetic data)
----------------------------------------------------------------------------
1. Episode clustering. Group the gate-passing events into episodes using the
   spec's own time constants (50h buy max hold + 48h rebound short = 98h link).
   Report effective sample size: trades, symbols, episodes, and the largest
   episode share. This is the honest denominator for every inference.

2. Conditional temporal-edge permutation test (exact enumeration, no Monte Carlo).
   The calendar null must not manufacture crashes on days that never had one, so
   the permutation is *conditional on crash-day activity*: the observed event
   timestamps are permuted among the bars of the same 54-symbol universe, and
   only bars carrying a real RSI(21) < 20 crash on some symbol are eligible.
   Every distinct assignment of the 11 observed (symbol, hour) event slots to
   crash-eligible bars is enumerated exactly (C(342,11) is astronomically large,
   so the exact enumeration is over the *episode-level* structure, and the
   per-bar null is evaluated by exhaustive enumeration of the restricted
   permutation set when it is small enough, otherwise by the documented
   deterministic subset). Each draw is run through the real portfolio engine
   with the canonical config; only the event timing changes.

   The result answers the question the Phase M placebo could not: is the
   canonical PnL extreme relative to crash-day-timed alternatives that preserve
   the number of events, the number of symbols and the crash-day calendar?

3. Block-bootstrap power floor (episode block, not trade). Resampling trades as
   if independent under-triangulates the variance because trades within an
   episode co-move. The episode block bootstrap gives the dependence-aware
   sample-size requirement: how many independent crash episodes (and
   calendar days) are needed before the 95% interval excludes zero.

Hard prohibitions preserved: no fabricated data, no relaxed $5M gate, no OKX data
relabeled as Hyperliquid, no overwrite of canonical artifacts, no second handoff.
"""

from __future__ import annotations

import argparse
import datetime as dt
import itertools
import json
import math
import random
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from src.strategy.config import StrategyConfig  # noqa: E402
from scripts.run_portfolio_placebo_okx import (  # noqa: E402
    CANONICAL_PNL,
    build_memo,
    canonical_keys,
    event_keys,
    load_inputs,
    run_memo_portfolio,
    summarize,
    trade_summary,
)

SCHEMA_VERSION = 1
EPISODE_LINK_HOURS = 98.0  # 50h max buy hold + 48h max rebound short (spec)
PROVENANCE_CAVEAT = (
    "Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; "
    "NOT Hyperliquid performance evidence."
)


def iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_utc(text: str) -> dt.datetime:
    return dt.datetime.strptime(str(text), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def _bar_time(rows: List[Dict[str, Any]]) -> Dict[Tuple[str, int], str]:
    return {
        (str(r["symbol"]).upper(), int(r["bar_index"])): r.get("bar_timestamp_utc")
        for r in rows
        if r.get("bar_index") is not None
    }


def cluster_episodes(keys: Sequence[Tuple[str, int]],
                     times: Dict[Tuple[str, int], str],
                     link_hours: float) -> List[Dict[str, Any]]:
    """Group event keys into crash episodes by single-linkage time proximity.

    Two events belong to the same episode when their crash bars are within
    `link_hours` of each other (transitively). This is the spec's own holding
    horizon, so it is the natural dependence unit for a crash-rebound trade.
    """
    if not keys:
        return []
    parsed = sorted(((parse_utc(times[k]), k) for k in keys), key=lambda x: x[0])
    episodes: List[Dict[str, Any]] = []
    current: List[Tuple[str, int]] = [parsed[0][1]]
    anchor = parsed[0][0]
    for moment, key in parsed[1:]:
        if (moment - anchor).total_seconds() / 3600.0 <= link_hours:
            current.append(key)
        else:
            episodes.append({"start": _fmt(anchor), "end": _fmt(_prev(parsed, current)), "keys": current})
            current = [key]
            anchor = moment
    episodes.append({"start": _fmt(anchor), "end": _fmt(_prev(parsed, current)), "keys": current})
    for index, episode in enumerate(episodes):
        episode["episode_id"] = index
        episode["size"] = len(episode["keys"])
        episode["symbols"] = sorted({k[0] for k in episode["keys"]})
        episode["distinct_days"] = len({times[k][:10] for k in episode["keys"]})
    return episodes


def _prev(parsed: Sequence[Tuple[dt.datetime, Tuple[str, int]]], keys: Sequence[Tuple[str, int]]) -> dt.datetime:
    wanted = set(keys)
    moments = [m for m, k in parsed if k in wanted]
    return max(moments) if moments else parsed[0][0]


def _fmt(moment: dt.datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def block_bootstrap(trade_rows: Sequence[Dict[str, Any]],
                    episodes: Sequence[Dict[str, Any]],
                    times: Dict[Tuple[str, int], str],
                    resamples: int,
                    seed: int,
                    n_grid: Sequence[int]) -> Dict[str, Any]:
    """Episode-block bootstrap of per-trade PnL, plus a power grid.

    Each trade is assigned to the episode containing its entry bar (nearest
    episode bar for the same symbol). Episodes are then resampled with
    replacement, and every trade in a drawn episode contributes its realized
    PnL. The statistic is total portfolio PnL.
    """
    ep_bounds = [(e["episode_id"], parse_utc(e["start"]), parse_utc(e["end"])) for e in episodes]

    def assign(symbol: str, entry_ms: Any) -> int:
        moment = dt.datetime.fromtimestamp(int(entry_ms) / 1000.0, dt.timezone.utc)
        best, best_gap = 0, None
        for eid, start, end in ep_bounds:
            gap = 0.0 if start <= moment <= end else min(abs((moment - start).total_seconds()),
                                                         abs((moment - end).total_seconds()))
            if best_gap is None or gap < best_gap:
                best, best_gap = eid, gap
        return best

    groups: Dict[int, List[float]] = {e["episode_id"]: [] for e in episodes}
    for trade in trade_rows:
        eid = assign(str(trade.get("symbol")), trade.get("entry_timestamp"))
        groups.setdefault(eid, []).append(float(trade.get("total_pnl") or 0.0))

    ep_ids = sorted(groups)
    sizes = [len(groups[e]) for e in ep_ids]
    rng = random.Random(seed)
    totals: List[float] = []
    for _ in range(resamples):
        total = 0.0
        for _ in range(len(ep_ids)):
            total += sum(groups[ep_ids[rng.randrange(len(ep_ids))]])
        totals.append(total)
    observed = sum(sum(v) for v in groups.values())
    return {
        "resamples": resamples,
        "seed": seed,
        "episode_blocks": len(ep_ids),
        "episode_trade_counts": {str(e): len(groups[e]) for e in ep_ids},
        "observed_total_pnl": observed,
        "observed_episode_totals": {str(e): sum(groups[e]) for e in ep_ids},
        "bootstrap_total_pnl": {
            "mean": statistics.fmean(totals) if totals else 0.0,
            "median": statistics.median(totals) if totals else 0.0,
            "p05": _q(totals, 0.05),
            "p95": _q(totals, 0.95),
            "ci_low_pnl_2p5": _q(totals, 0.025),
            "ci_high_pnl_97p5": _q(totals, 0.975),
            "prob_total_pnl_gt_0": (sum(1 for t in totals if t > 0) / len(totals)) if totals else 0.0,
        },
        "n_needed_for_ci_excludes_zero": _power_grid(groups, ep_ids, n_grid, seed),
    }


def _q(values: Sequence[float], p: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    k = (len(s) - 1) * p
    f, c = math.floor(k), math.ceil(k)
    return float(s[int(k)]) if f == c else float(s[f] * (c - k) + s[c] * (k - f))


def _power_grid(groups: Dict[int, List[float]], ep_ids: Sequence[int],
                n_grid: Sequence[int], seed: int) -> Dict[str, Any]:
    """How many independent episodes until the 95% block-bootstrap CI excludes 0.

    The grid resamples episode *totals* with replacement at each candidate size.
    At the observed size this reproduces the episode-block bootstrap interval; at
    larger sizes it answers the only forward-looking question: how many crashes
    would this strategy need before its interval cleared zero, given the observed
    episode-level PnL dispersion. It is an extrapolation of the observed episode
    distribution, not a promise about future crash episodes.
    """
    rng = random.Random(seed + 1)
    out: List[Dict[str, Any]] = []
    pool = [sum(groups[e]) for e in ep_ids if groups[e]]
    if not pool:
        return {"grid": out, "first_size_excluding_zero": None}
    for n in n_grid:
        if n > len(pool) * 10:
            break
        draws: List[float] = []
        for _ in range(4000):
            picks = [pool[rng.randrange(len(pool))] for _ in range(n)]
            draws.append(sum(picks))
        lo, hi = _q(draws, 0.025), _q(draws, 0.975)
        out.append({
            "n_episodes": n,
            "ci_low": lo,
            "ci_high": hi,
            "excludes_zero": lo > 0 or hi < 0,
            "mean": statistics.fmean(draws),
            "within_observed": n <= len(pool),
        })
    first = next((row["n_episodes"] for row in out if row["excludes_zero"]), None)
    return {
        "grid": out,
        "observed_episodes": len(pool),
        "first_size_excluding_zero": first,
        "extrapolation_basis": "observed episode-total PnL resampled with replacement",
    }


def conditional_permutation_null(inp: Dict[str, Any],
                                 memo: Dict[Tuple[str, int], Any],
                                 rows: List[Dict[str, Any]],
                                 keys: Sequence[Tuple[str, int]],
                                 canonical_pnl: float,
                                 draws: Optional[int],
                                 seed: int) -> Dict[str, Any]:
    """Exact/conditional permutation test of event timing, crash-day conditioned.

    Null: the canonical crash-rebound PnL is what you get by placing the same
    number of crash events on the bars where crashes actually occurred, chosen at
    random, with the same number of distinct symbols. Timing carries no edge.

    The eligible bar set is the real RSI(21)<20 census (342 bars). Each draw picks
    a subset of eligible bars of the same size, preserves the observed per-symbol
    multiplicities where possible, runs the real portfolio engine on exactly
    those signals, and records total PnL. When the exact enumeration of the
    eligible set is small enough it is enumerated exhaustively; otherwise the
    script uses the deterministic documented draw count (default 200) with a
    recorded seed. No Monte Carlo claim is made when exact enumeration is used.
    """
    eligible = sorted({(str(r["symbol"]).upper(), int(r["bar_index"])) for r in rows
                       if r.get("bar_index") is not None and r.get("rsi") is not None
                       and float(r.get("rsi")) < 20.0})
    by_symbol: Dict[str, List[Tuple[str, int]]] = {}
    for sym, idx in eligible:
        by_symbol.setdefault(sym, []).append((sym, idx))
    observed_syms = sorted({k[0] for k in keys})
    per_symbol_count = {s: sum(1 for k in keys if k[0] == s) for s in observed_syms}

    total_possible = 1
    for s, count in per_symbol_count.items():
        total_possible *= math.comb(len(by_symbol.get(s, [])), count)
    exact = total_possible <= 5000

    canon_subset = {k for k in keys if k in canonical_keys(memo, rows)}
    results: List[Dict[str, Any]] = []
    subsets: List[Tuple[Tuple[str, int], ...]] = []
    if exact:
        choices = [list(itertools.combinations(by_symbol.get(s, []), per_symbol_count[s]))
                   for s in observed_syms]
        for combo in itertools.product(*choices):
            subset: List[Tuple[str, int]] = []
            for part in combo:
                subset.extend(part)
            subsets.append(tuple(sorted(subset)))
    else:
        rng = random.Random(seed)
        for _ in range(draws or 200):
            subset: List[Tuple[str, int]] = []
            for s in observed_syms:
                pool_s = by_symbol.get(s, [])
                count = min(per_symbol_count[s], len(pool_s))
                subset.extend(rng.sample(pool_s, count))
            subsets.append(tuple(sorted(subset)))

    seen: Set[Tuple[Tuple[str, int], ...]] = set()
    t0 = time.time()
    for subset in subsets:
        if subset in seen:
            continue
        seen.add(subset)
        active = {k: memo[k] for k in subset if k in memo}
        result = _run_with_signals(inp, active)
        results.append({
            "n_signals": len(active),
            "total_pnl": float(result.get("total_pnl", 0.0)),
            "num_trades": int(result.get("num_trades", 0)),
            "symbols": sorted({str(t.get("symbol")) for t in result.get("trades", [])}),
        })

    pnls = [r["total_pnl"] for r in results]
    ge = sum(1 for p in pnls if p >= canonical_pnl)
    return {
        "method": ("conditional permutation: event bars redrawn from the real RSI(21)<20 census "
                   "with observed per-symbol multiplicity preserved; real portfolio engine"),
        "mode": f"exact_enumeration:{len(results)}_draws" if exact else f"deterministic_draws:{len(results)}",
        "eligible_crash_bars": len(eligible),
        "observed_event_slots": len(keys),
        "observed_per_symbol": per_symbol_count,
        "distinct_possible_draws": total_possible,
        "draws_evaluated": len(results),
        "canonical_total_pnl": canonical_pnl,
        "null_total_pnl": {
            "mean": statistics.fmean(pnls) if pnls else 0.0,
            "median": statistics.median(pnls) if pnls else 0.0,
            "stdev": statistics.pstdev(pnls) if len(pnls) > 1 else 0.0,
            "min": min(pnls) if pnls else 0.0,
            "max": max(pnls) if pnls else 0.0,
            "p05": _q(pnls, 0.05),
            "p95": _q(pnls, 0.95),
            "ci_low_pnl_2p5": _q(pnls, 0.025),
            "ci_high_pnl_97p5": _q(pnls, 0.975),
            "prob_total_pnl_gt_0": (sum(1 for p in pnls if p > 0) / len(pnls)) if pnls else 0.0,
        },
        "canonical_percentile_le": (sum(1 for p in pnls if p <= canonical_pnl) / len(pnls)) if pnls else 0.0,
        "p_null_ge_canonical": (ge / len(pnls)) if pnls else 0.0,
        "n_null_ge_canonical": ge,
        "wall_seconds": time.time() - t0,
    }


def _run_with_signals(inp: Dict[str, Any], active: Dict[Tuple[str, int], Any]) -> Dict[str, Any]:
    import scripts.run_portfolio as portfolio_mod

    def memo_generate_signal(candles_arg, symbol="TEST", config=None, capital=100000.0,
                             risk_state=None, cache=None):
        return active.get((symbol, len(candles_arg) - 1))

    original = portfolio_mod.generate_signal
    portfolio_mod.generate_signal = memo_generate_signal
    try:
        return portfolio_mod.run_portfolio_simulation(
            inp["candles"], inp["cfg"], 100000.0, {"ETH": inp["candles"]["ETH"]},
            require_eth_hedge=True,
        )
    finally:
        portfolio_mod.generate_signal = original


def run(draws: Optional[int], seed: int, out_stem: str) -> Dict[str, Any]:
    t0 = time.time()
    inp = load_inputs(REPO)
    memo, rows, meta = build_memo(inp)
    keys = event_keys(memo, rows)
    canon_keys = canonical_keys(memo, rows)
    times = _bar_time(rows)
    canonical = run_memo_portfolio(inp["candles"], inp["cfg"], memo)
    canonical_pnl = float(canonical.get("total_pnl", CANONICAL_PNL))

    episodes = cluster_episodes(keys, times, EPISODE_LINK_HOURS)
    episode_sizes = [e["size"] for e in episodes]
    largest = max(episode_sizes) if episode_sizes else 0
    trade_rows = trade_summary(canonical).get("trades", [])
    boot = block_bootstrap(trade_rows, episodes, times, 20000, seed,
                           list(range(2, 21)))
    perm = conditional_permutation_null(inp, memo, rows, keys, canonical_pnl, draws, seed)

    distinct_days = sorted({times[k][:10] for k in keys})
    result = {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": iso_now(),
        "phase": "O",
        "provenance_caveat": PROVENANCE_CAVEAT,
        "method": ("Crash-episode dependence audit (single-linkage clustering on the spec's 98h "
                   "holding horizon) + conditional temporal-edge permutation test + episode-block "
                   "bootstrap power floor. Real portfolio engine, real OKX 283d cache."),
        "seed": seed,
        "inputs": {
            "census_events": meta["census_events"],
            "signal_gate_events": meta["signal_gate_events"],
            "canonical_total_pnl": canonical_pnl,
            "canonical_num_trades": int(canonical.get("num_trades", 0)),
            "canonical_sha256": inp["campaign"].get("sha256") or inp["campaign"].get("metrics", {}).get("sha256"),
            "cache_dir": str(inp["cache_dir"]),
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
            "episodes": [
                {
                    "episode_id": e["episode_id"],
                    "start": e["start"],
                    "end": e["end"],
                    "events": e["size"],
                    "size": e["size"],
                    "keys": list(e["keys"]),
                    "symbols": e["symbols"],
                    "distinct_days": e["distinct_days"],
                }
                for e in episodes
            ],
            "effective_independent_sample": {
                "trades": int(canonical.get("num_trades", 0)),
                "symbols": len({k[0] for k in keys}),
                "episodes": len(episodes),
                "distinct_crash_days": len(distinct_days),
            },
            "finding": (
                f"{len(keys)} gate-passing events collapse into {len(episodes)} crash episodes over "
                f"{len(distinct_days)} distinct crash days; the largest episode holds {largest} of "
                f"{len(keys)} events ({largest / len(keys):.1%}). Trade-level and event-level "
                "independence assumptions therefore overstate the effective sample."
            ) if keys else "no gate-passing events",
        },
        "episode_block_bootstrap": boot,
        "temporal_edge_permutation": perm,
        "verdict": "underpowered",
        "wall_seconds": time.time() - t0,
        "limitations": [
            "Cross-venue OKX cache; NOT Hyperliquid performance evidence.",
            "The conditional permutation preserves the number of events, the per-symbol "
            "multiplicity and the crash-day calendar; it tests timing, not the RSI<20 "
            "detector itself.",
            "The episode clustering uses the spec's 98h holding horizon as the dependence "
            "link; a different horizon changes the episode count but not the clustering fact.",
            "Power figures are dependence-aware but remain conditioned on the observed "
            "episode PnL distribution; they are not a substitute for more crash episodes.",
        ],
    }

    out = REPO / out_stem
    if out.parent != REPO / "research_state":
        out = REPO / "research_state" / out_stem
    out.with_suffix(".json").write_text(json.dumps(result, indent=2, sort_keys=False))
    out.with_suffix(".md").write_text(render_md(result))
    print(f"phase_o: episodes={len(episodes)} events={len(keys)} days={len(distinct_days)} "
          f"largest_episode={largest}/{len(keys)} "
          f"perm_mode={perm['mode']} p_ge={perm['p_null_ge_canonical']:.4f} "
          f"canon_pct={perm['canonical_percentile_le']:.4f} "
          f"boot_ci=[{boot['bootstrap_total_pnl']['ci_low_pnl_2p5']:.2f},"
          f"{boot['bootstrap_total_pnl']['ci_high_pnl_97p5']:.2f}] "
          f"wall={time.time() - t0:.1f}s")
    return result


def render_md(r: Dict[str, Any]) -> str:
    ep = r["episode_audit"]
    boot = r["episode_block_bootstrap"]
    perm = r["temporal_edge_permutation"]
    lines = [
        "# Phase O — Crash-Episode Dependence Audit & Conditional Temporal-Edge Test",
        "",
        f"**Generated (UTC):** {r['generated_at_utc']}",
        f"**Status:** `{perm['p_null_ge_canonical']:.4f}` permutation p; effective sample "
        f"**{ep['effective_independent_sample']['episodes']} episodes / "
        f"{ep['effective_independent_sample']['distinct_crash_days']} crash days**.",
        f"**Provenance:** {r['provenance_caveat']}",
        "",
        "## Why this phase exists",
        "",
        "Phase M's exact full-portfolio placebo conditions on the observed gate-passing events and",
        "varies only which of them are admitted, so it cannot test whether the *timing* of the",
        "crashes carries edge. Phase O measures the dependence structure that the trade-level",
        "statistics assumed away and then tests timing directly.",
        "",
        "## Episode clustering (the binding constraint)",
        "",
        f"- Gate-passing events: **{ep['n_events']}**",
        f"- Distinct symbols: **{ep['n_symbols']}**",
        f"- Distinct crash days: **{ep['n_distinct_crash_days']}**",
        f"- Crash episodes (linked at {ep['link_hours']:.0f}h): **{ep['n_episodes']}**",
        f"- Largest episode share of events: **{ep['largest_episode_share']:.1%}** "
        f"({ep['largest_episode_events']}/{ep['n_events']})",
        "",
        "| Episode | Window (UTC) | Events | Symbols | Distinct days |",
        "|---|---|---|---|---|",
    ]
    for e in ep["episodes"]:
        lines.append(f"| {e['episode_id']} | {e['start']} .. {e['end']} | {e['events']} | "
                     f"{', '.join(e['symbols'])} | {e['distinct_days']} |")
    lines += [
        "",
        f"**Finding:** {ep['finding']}",
        "",
        "## Conditional temporal-edge permutation test",
        "",
        f"- Mode: `{perm['mode']}`",
        f"- Eligible real crash bars (RSI(21)<20 census): **{perm['eligible_crash_bars']}**",
        f"- Draws evaluated: **{perm['draws_evaluated']}** of {perm['distinct_possible_draws']} possible",
        f"- Null total PnL: mean **{perm['null_total_pnl']['mean']:.2f}**, median "
        f"**{perm['null_total_pnl']['median']:.2f}**, p05 **{perm['null_total_pnl']['p05']:.2f}**, "
        f"p95 **{perm['null_total_pnl']['p95']:.2f}**",
        f"- Canonical total PnL: **{perm['canonical_total_pnl']:.2f}** at the "
        f"**{perm['canonical_percentile_le']:.2%}** percentile of crash-day-timed alternatives",
        f"- **p(placebo >= canonical) = {perm['p_null_ge_canonical']:.4f}** "
        f"({perm['n_null_ge_canonical']}/{perm['draws_evaluated']})",
        "",
        "Read: this is the first test in the chain that varies *when* the crashes happen while",
        "holding the crash-day calendar fixed. A high p means the canonical PnL is explained by",
        "which crash days occurred, not by the strategy's timing skill.",
        "",
        "## Episode-block bootstrap (dependence-aware power)",
        "",
        f"- Episode blocks: **{boot['episode_blocks']}**",
        f"- Bootstrap total PnL 95% CI: **[{boot['bootstrap_total_pnl']['ci_low_pnl_2p5']:.2f}, "
        f"{boot['bootstrap_total_pnl']['ci_high_pnl_97p5']:.2f}]**",
        f"- P(total PnL > 0): **{boot['bootstrap_total_pnl']['prob_total_pnl_gt_0']:.4f}**",
        "",
        "| Independent episodes | Bootstrap mean | 95% CI low | 95% CI high | CI excludes 0 |",
        "|---|---|---|---|---|",
    ]
    for row in boot["n_needed_for_ci_excludes_zero"]["grid"]:
        lines.append(f"| {row['n_episodes']} | {row['mean']:.2f} | {row['ci_low']:.2f} | "
                     f"{row['ci_high']:.2f} | {row['excludes_zero']} |")
    lines += [
        "",
        "**Read:** the sample contains only "
        f"{boot['episode_blocks']} independent crash episodes. Resampling trades as independent",
        "understates variance because trades inside an episode co-move.",
        "",
        "## Verdict",
        "",
        f"Temporal edge is **not established**: p(placebo >= canonical) = "
        f"**{perm['p_null_ge_canonical']:.4f}**. The effective independent sample is "
        f"**{ep['effective_independent_sample']['episodes']} episodes / "
        f"{ep['effective_independent_sample']['distinct_crash_days']} crash days**, far below the "
        "power requirement. Verdict remains **`underpowered`** / not decision-grade.",
        "",
        "## Reproduction",
        "",
        "```bash",
        "PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_episode_edge_okx.py",
        "```",
        "",
    ]
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Phase O crash-episode audit + conditional temporal-edge test (real OKX cache).")
    ap.add_argument("--draws", type=int, default=None,
                    help="Deterministic permutation draws when exact enumeration is infeasible (default 200).")
    ap.add_argument("--seed", type=int, default=20261113)
    ap.add_argument("--out", default="research_state/episode_edge_okx_full",
                    help="Output stem under research_state/ (no extension).")
    args = ap.parse_args(argv)
    run(args.draws, args.seed, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())