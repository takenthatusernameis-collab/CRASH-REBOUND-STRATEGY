#!/usr/bin/env python3
"""Phase N — exact full-portfolio robustness stress / power analysis for the OKX run.

WHY THIS EXISTS
---------------
The exact 165-subset portfolio placebo (Phase M) showed the canonical +9.16%
result is a typical 8-of-11 admission subset. It does not answer three decision
questions:

1. Is the result driven by one symbol or one trade?
2. How much data (trades / symbols) would be needed for the bootstrap CI to
   exclude zero?
3. Does the result survive an expanding-window, refit walk-forward?

The existing Phase L script computes leave-one-out by simple PnL arithmetic.
That is not the same thing: removing a symbol/trade changes portfolio admission,
gross-cap cuts and occupancy for the other candidates, so the real portfolio
engine must be re-run. This script does exactly that, using the same exact
memoized ``generate_signal`` path as Phase M.

It is a STRESS TEST, not evidence of edge. The canonical run remains
``underpowered`` unless and until Hyperliquid-native evidence meets the GO
criteria. The memo is exact only for the canonical config/data; a canonical
replay equality check is a hard failure gate, not a warning.

Outputs (new stems only; canonical artifacts are never overwritten):
* research_state/robustness_stress_okx_full.json
* research_state/robustness_stress_okx_full.md
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import random
import statistics
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.run_portfolio_placebo_okx import (  # noqa: E402
    CANONICAL_PNL,
    CANONICAL_TRADES,
    PROVENANCE_CAVEAT,
    build_memo,
    canonical_keys,
    event_keys,
    load_inputs,
    quantile,
    run_memo_portfolio,
    sha256_file,
    trade_summary,
)

SEED = 20261113
BOOTSTRAP_RESAMPLES = 20_000
TRADE_N_GRID = [8, 10, 12, 16, 20, 25, 30, 40, 50, 75, 100, 150, 200, 300, 500]
SYMBOL_N_GRID = [5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 60, 80, 100]
PREFIX_FRACTIONS = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]

# Refit only execution/portfolio knobs. Signal generation is NOT refit: the memo
# was built with the canonical spec signal config (RSI<20, 9% target, 8x safety
# stop), and re-deriving signals for other thresholds would require a new memo and
# a different data census. This is a limitation, documented in the artifact.
REFIT_GRID: List[Dict[str, Any]] = [
    {"max_positions": mp, "time_exit_max_bars": te, "rebound_short_target_pct": rs}
    for mp in (3, 5, 8)
    for te in (24, 50, 96)
    for rs in (6, 9, 12)
]


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _deep_memo(memo: Dict[Tuple[str, int], Any], keys: Sequence[Tuple[str, int]]) -> Dict[Tuple[str, int], Any]:
    wanted = set(keys)
    return {k: copy.deepcopy(memo[k]) for k in memo if k in wanted}


def _run(candles: Dict[str, List[Dict[str, Any]]], cfg: Any,
         memo: Dict[Tuple[str, int], Any], keys: Sequence[Tuple[str, int]]) -> Dict[str, Any]:
    return run_memo_portfolio(candles, cfg, _deep_memo(memo, keys))


def _cfg_with(base: Any, overrides: Dict[str, Any]) -> Any:
    cfg = copy.deepcopy(base)
    for k, v in overrides.items():
        setattr(cfg, k, v)
    return cfg


def _trade_table(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    return trade_summary(result)["trades"]


def _normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _power_curve(values: List[float], n_grid: Sequence[int], resamples: int,
                 rng: random.Random, level: float = 0.95) -> Dict[str, Any]:
    """Bootstrap CI for the mean at each sample size, plus analytic normal power.

    The bootstrap CI at size n answers "if we had n trades drawn from the observed
    distribution, where would the mean lie?" The analytic power answers "what is
    the probability that the 95% CI excludes zero?" under a normal approximation.
    Both are projections from the observed sample, not evidence of future edge.
    """
    n_obs = len(values)
    mean = statistics.fmean(values)
    sd = statistics.stdev(values) if n_obs > 1 else 0.0
    alpha = (1.0 - level) / 2.0
    rows = []
    for n in n_grid:
        draws = []
        for _ in range(resamples):
            sample = [values[rng.randrange(n_obs)] for _ in range(n)]
            draws.append(statistics.fmean(sample))
        draws.sort()
        lo = quantile(draws, alpha)
        hi = quantile(draws, 1.0 - alpha)
        se = sd / math.sqrt(n) if n > 0 else float("inf")
        z = mean / se if se > 0 else float("inf")
        # P(CI excludes zero) = P(mean_hat - 1.96*se > 0) for a two-sided 95% CI.
        analytic_power = _normal_cdf(z - 1.96) if math.isfinite(z) else 1.0
        rows.append({
            "n": int(n),
            "bootstrap_mean": round(statistics.fmean(draws), 6),
            "ci_low": round(lo, 6),
            "ci_high": round(hi, 6),
            "ci_excludes_zero": bool(lo > 0.0),
            "analytic_power_ci_excludes_zero": round(analytic_power, 6),
        })
    first_ci = next((r["n"] for r in rows if r["ci_excludes_zero"]), None)
    n80 = ((1.96 + 0.8416) * sd / mean) ** 2 if mean > 0 and sd > 0 else None
    n95 = ((1.96 + 1.6449) * sd / mean) ** 2 if mean > 0 and sd > 0 else None
    return {
        "observed_n": n_obs,
        "observed_mean": round(mean, 6),
        "observed_stdev": round(sd, 6),
        "standard_error": round(sd / math.sqrt(n_obs), 6) if n_obs else None,
        "resamples_per_n": int(resamples),
        "seed": SEED,
        "rows": rows,
        "first_bootstrap_ci_excludes_zero_at_n": first_ci,
        "analytic_n_for_80pct_power": None if n80 is None else round(n80, 2),
        "analytic_n_for_95pct_power": None if n95 is None else round(n95, 2),
        "max_n_tested": int(max(n_grid)),
    }


def _symbol_pnls(trades: List[Dict[str, Any]]) -> List[float]:
    by_symbol: Dict[str, float] = defaultdict(float)
    for t in trades:
        by_symbol[str(t["symbol"])] += float(t["total_pnl"])
    return [by_symbol[s] for s in sorted(by_symbol)]


def _concentration(trades: List[Dict[str, Any]], rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = math.fsum(float(t["total_pnl"]) for t in trades)
    gross_abs = math.fsum(abs(float(t["total_pnl"])) for t in trades) or 1.0
    by_symbol: Dict[str, Dict[str, float]] = defaultdict(lambda: {"trades": 0.0, "pnl": 0.0})
    for t in trades:
        slot = by_symbol[str(t["symbol"])]
        slot["trades"] += 1
        slot["pnl"] += float(t["total_pnl"])
    symbol_rows = []
    hhi_abs = 0.0
    for sym, agg in sorted(by_symbol.items()):
        raw_share = (agg["pnl"] / total) if total else 0.0
        abs_share = abs(agg["pnl"]) / gross_abs
        hhi_abs += abs_share * abs_share
        symbol_rows.append({
            "symbol": sym,
            "trades": int(agg["trades"]),
            "pnl": round(agg["pnl"], 6),
            "raw_pnl_share_of_total": round(raw_share, 6),
            "abs_pnl_share_of_gross": round(abs_share, 6),
        })
    symbol_rows.sort(key=lambda r: abs(r["pnl"]), reverse=True)

    # Map each canonical trade to its memo key through the census matched PnL.
    key_by_pnl: Dict[float, Tuple[str, int]] = {}
    for r in rows:
        if r.get("trade_opened_canonical") and r.get("bar_index") is not None:
            pnl = r.get("matched_trade_pnl_canonical")
            key = (str(r["symbol"]).upper(), int(r["bar_index"]))
            try:
                key_by_pnl[round(float(pnl), 6)] = key
            except (TypeError, ValueError):
                pass

    top_trade = max(trades, key=lambda t: abs(float(t["total_pnl"])))
    top_trade_key = key_by_pnl.get(round(float(top_trade["total_pnl"]), 6))
    top_symbol = symbol_rows[0]["symbol"] if symbol_rows else None

    return {
        "total_pnl": round(total, 6),
        "gross_abs_pnl": round(gross_abs, 6),
        "symbols": symbol_rows,
        "top_symbol": top_symbol,
        "top_symbol_raw_share": symbol_rows[0]["raw_pnl_share_of_total"] if symbol_rows else None,
        "top_symbol_abs_share": symbol_rows[0]["abs_pnl_share_of_gross"] if symbol_rows else None,
        "top_trade": {
            "symbol": top_trade["symbol"],
            "entry_timestamp": top_trade.get("entry_timestamp"),
            "pnl": round(float(top_trade["total_pnl"]), 6),
            "abs_share_of_gross": round(abs(float(top_trade["total_pnl"])) / gross_abs, 6),
            "memo_key": list(top_trade_key) if top_trade_key else None,
        },
        "herfindahl_hhi_abs": round(hhi_abs, 6),
        "effective_symbol_count_abs": round(1.0 / hhi_abs, 6) if hhi_abs > 0 else None,
        "simple_pnl_without_top_symbol": round(total - float(symbol_rows[0]["pnl"]), 6) if symbol_rows else None,
        "simple_pnl_without_top_trade": round(total - float(top_trade["total_pnl"]), 6),
    }


def _loo_symbol(candles: Dict[str, List[Dict[str, Any]]], cfg: Any,
                memo: Dict[Tuple[str, int], Any], rows: List[Dict[str, Any]],
                full_keys: Sequence[Tuple[str, int]]) -> Dict[str, Any]:
    out = []
    symbols = sorted({s for s, _ in full_keys})
    for sym in symbols:
        excluded_all = {k for k in full_keys if k[0] == sym}
        excluded_admitted = {k for k in canonical_keys(memo, rows) if k[0] == sym}
        allowed = [k for k in full_keys if k[0] != sym]
        res = _run(candles, cfg, memo, allowed)
        summ = trade_summary(res)
        out.append({
            "excluded_symbol": sym,
            "excluded_signal_keys": [f"{s}:{i}" for s, i in sorted(excluded_all)],
            "excluded_admitted_keys": [f"{s}:{i}" for s, i in sorted(excluded_admitted)],
            "total_pnl": round(summ["total_pnl"], 6),
            "num_trades": summ["num_trades"],
            "delta_vs_canonical": round(summ["total_pnl"] - CANONICAL_PNL, 6),
            "canonical_trades_remaining": len(
                [t for t in summ["trades"]
                 if (str(t["symbol"]).upper(), _bar_index_for(candles, t)) in set(canonical_keys(memo, rows))]
            ),
            "trades": summ["trades"],
        })
    return {
        "method": "mask every signal of the excluded symbol, re-run the exact portfolio engine",
        "runs": out,
        "all_positive": all(r["total_pnl"] > 0 for r in out),
        "min_total_pnl": min((r["total_pnl"] for r in out), default=None),
        "max_total_pnl": max((r["total_pnl"] for r in out), default=None),
    }


def _bar_index_for(candles: Dict[str, List[Dict[str, Any]]], trade: Dict[str, Any]) -> Optional[int]:
    """Best-effort index lookup used only for reporting remaining canonical trades."""
    sym = str(trade.get("symbol", "")).upper()
    cs = candles.get(sym) or []
    ts = trade.get("entry_timestamp")
    if ts is None:
        return None
    try:
        ts_int = int(ts)
    except (TypeError, ValueError):
        return None
    for i, c in enumerate(cs):
        try:
            if int(c.get("timestamp_ms") or c.get("t") or 0) == ts_int:
                return i
        except (TypeError, ValueError):
            continue
    return None


def _loto(candles: Dict[str, List[Dict[str, Any]]], cfg: Any,
          memo: Dict[Tuple[str, int], Any], rows: List[Dict[str, Any]],
          full_keys: Sequence[Tuple[str, int]]) -> Dict[str, Any]:
    canon = canonical_keys(memo, rows)
    out = []
    for key in sorted(canon):
        allowed = [k for k in full_keys if k != key]
        res = _run(candles, cfg, memo, allowed)
        summ = trade_summary(res)
        out.append({
            "excluded_key": f"{key[0]}:{key[1]}",
            "excluded_symbol": key[0],
            "total_pnl": round(summ["total_pnl"], 6),
            "num_trades": summ["num_trades"],
            "delta_vs_canonical": round(summ["total_pnl"] - CANONICAL_PNL, 6),
            "trades": summ["trades"],
        })
    return {
        "method": "mask one admitted trade's signal, re-run the exact portfolio engine",
        "runs": out,
        "all_positive": all(r["total_pnl"] > 0 for r in out),
        "min_total_pnl": min((r["total_pnl"] for r in out), default=None),
        "max_total_pnl": max((r["total_pnl"] for r in out), default=None),
    }


def _walkforward(candles: Dict[str, List[Dict[str, Any]]], cfg: Any,
                 memo: Dict[Tuple[str, int], Any], full_keys: Sequence[Tuple[str, int]]) -> Dict[str, Any]:
    n_bars = min(len(v) for v in candles.values())
    rows = []
    prev_pnl = 0.0
    prev_trades = 0
    for frac in PREFIX_FRACTIONS:
        n = int(round(frac * n_bars))
        pc = {sym: cs[:n] for sym, cs in candles.items()}
        res = _run(pc, cfg, memo, full_keys)
        pnl = float(res["total_pnl"])
        trades = int(res["num_trades"])
        rows.append({
            "fraction": frac,
            "bars": n,
            "total_pnl": round(pnl, 6),
            "num_trades": trades,
            "incremental_block_pnl": round(pnl - prev_pnl, 6),
            "incremental_block_trades": trades - prev_trades,
            "evaluable_block": (trades - prev_trades) > 0,
        })
        prev_pnl = pnl
        prev_trades = trades

    # Refit: choose execution knobs on each prefix by in-sample PnL, then measure
    # the next block with the selected knobs (no look-ahead into the next block).
    # Blocks with no new trades are not evaluable and are skipped, not scored as 0.
    refit = []
    skipped = []
    for i in range(len(PREFIX_FRACTIONS) - 1):
        cur = rows[i]
        nxt = rows[i + 1]
        frac = cur["fraction"]
        if nxt["num_trades"] <= cur["num_trades"]:
            skipped.append({
                "prefix_fraction": frac,
                "reason": "next block has no new trades; out-of-sample not evaluable",
            })
            continue

        n = cur["bars"]
        pc = {sym: cs[:n] for sym, cs in candles.items()}
        grid_rows = []
        for over in REFIT_GRID:
            gcfg = _cfg_with(cfg, over)
            res = _run(pc, gcfg, memo, full_keys)
            grid_rows.append({
                "overrides": over,
                "total_pnl": round(float(res["total_pnl"]), 6),
                "num_trades": int(res["num_trades"]),
            })
        best = max(grid_rows, key=lambda r: (r["total_pnl"], -r["num_trades"]))
        best_cfg = _cfg_with(cfg, best["overrides"])
        n_next = nxt["bars"]
        pc_next = {sym: cs[:n_next] for sym, cs in candles.items()}
        best_next = _run(pc_next, best_cfg, memo, full_keys)
        canon_next = _run(pc_next, cfg, memo, full_keys)
        refit.append({
            "prefix_fraction": frac,
            "prefix_bars": n,
            "in_sample_block_trades": cur["incremental_block_trades"],
            "best_overrides": best["overrides"],
            "in_sample_pnl": best["total_pnl"],
            "in_sample_trades": best["num_trades"],
            "out_of_sample_block_pnl": round(
                float(best_next["total_pnl"]) - best["total_pnl"], 6),
            "out_of_sample_block_trades": int(best_next["num_trades"]) - best["num_trades"],
            "canonical_out_of_sample_block_pnl": round(
                float(canon_next["total_pnl"]) - cur["total_pnl"], 6),
            "grid_best_pnl": best["total_pnl"],
            "grid_worst_pnl": min(r["total_pnl"] for r in grid_rows),
            "grid_median_pnl": round(statistics.median(r["total_pnl"] for r in grid_rows), 6),
        })

    oos_pnls = [r["out_of_sample_block_pnl"] for r in refit]
    return {
        "method": (
            "expanding-window prefixes from bar 0 (warmup preserved); canonical config "
            "and a 27-point execution-knob refit grid selected in-sample per prefix, "
            "then evaluated on the next block out-of-sample. Blocks with no new trades "
            "are skipped, not scored as zero."
        ),
        "prefix_fractions": PREFIX_FRACTIONS,
        "canonical_prefixes": rows,
        "refit": refit,
        "skipped": skipped,
        "evaluable_blocks": len(refit),
        "non_evaluable_blocks": len(skipped),
        "refit_out_of_sample_total_pnl": round(math.fsum(oos_pnls), 6),
        "refit_out_of_sample_positive_blocks": sum(1 for p in oos_pnls if p > 0),
        "refit_out_of_sample_negative_blocks": sum(1 for p in oos_pnls if p < 0),
        "canonical_incremental_total_pnl": round(
            math.fsum(r["incremental_block_pnl"] for r in rows), 6),
        "refit_grid": REFIT_GRID,
        "refit_scope": "execution/portfolio knobs only; signal generation fixed at spec config",
    }


def _render_md(r: Dict[str, Any]) -> str:
    can = r["canonical"]
    conc = r["concentration"]
    loso = r["leave_one_symbol_out"]
    loto = r["leave_one_trade_out"]
    pt = r["power"]["trade_level"]
    ps = r["power"]["symbol_level"]
    wf = r["walkforward"]
    lines = [
        "# Exact Robustness Stress / Power Analysis — Real OKX 283d",
        "",
        f"**Generated (UTC):** {r['generated_at_utc']}  ",
        f"**Seed:** {r['seed']}  ",
        f"**Provenance caveat:** {r['provenance_caveat']}",
        "",
        "This is a **stress test**, not evidence of edge. It re-runs the exact full-portfolio "
        "engine (same gates, sizing, 120% gross cap, occupancy, ETH hedge, fees, funding, "
        "liquidation) after removing a symbol or a trade, and projects how much data would be "
        "needed for the bootstrap CI to exclude zero. The verdict remains **`underpowered`**.",
        "",
        "## Canonical baseline (must reproduce exactly)",
        "",
        f"- Trades: **{can['trades']}**, total PnL: **{can['total_pnl']:.6f}**",
        f"- Full 11-signal replay: {can['full_replay']['num_trades']} trades, "
        f"PnL {can['full_replay']['total_pnl']:.6f}",
        f"- Canonical artifact sha256: `{can['sha256']}`",
        "",
        "## Leave-one-symbol-out (exact engine re-run)",
        "",
        "| Excluded | Total PnL | Δ vs canonical | Trades | All-signal keys masked |",
        "|---|---:|---:|---:|---|",
    ]
    for row in loso["runs"]:
        lines.append(
            f"| {row['excluded_symbol']} | {row['total_pnl']:.2f} | "
            f"{row['delta_vs_canonical']:+.2f} | {row['num_trades']} | "
            f"{len(row['excluded_signal_keys'])} |"
        )
    lines += [
        "",
        f"- All LOO runs positive: **{loso['all_positive']}**; "
        f"min **{loso['min_total_pnl']:.2f}**, max **{loso['max_total_pnl']:.2f}**.",
        "",
        "## Leave-one-trade-out (exact engine re-run)",
        "",
        "| Excluded signal | Total PnL | Δ vs canonical | Trades |",
        "|---|---:|---:|---:|",
    ]
    for row in loto["runs"]:
        lines.append(
            f"| {row['excluded_key']} | {row['total_pnl']:.2f} | "
            f"{row['delta_vs_canonical']:+.2f} | {row['num_trades']} |"
        )
    lines += [
        "",
        f"- All LOTO runs positive: **{loto['all_positive']}**; "
        f"min **{loto['min_total_pnl']:.2f}**, max **{loto['max_total_pnl']:.2f}**.",
        "",
        "## Concentration-adjusted inference",
        "",
        f"- Top symbol: **{conc['top_symbol']}** "
        f"({conc['top_symbol_abs_share']:.2%} of gross |PnL|); "
        f"raw share of total {conc['top_symbol_raw_share']:.2%}.",
        f"- Top trade: **{conc['top_trade']['symbol']}** @ {conc['top_trade']['entry_timestamp']} "
        f"(PnL {conc['top_trade']['pnl']:.2f}, "
        f"{conc['top_trade']['abs_share_of_gross']:.2%} of gross |PnL|).",
        f"- Absolute-PnL HHI: **{conc['herfindahl_hhi_abs']:.4f}**; "
        f"effective symbols: **{conc['effective_symbol_count_abs']:.2f}**.",
        f"- Simple PnL without top symbol: **{conc['simple_pnl_without_top_symbol']:.2f}**; "
        f"without top trade: **{conc['simple_pnl_without_top_trade']:.2f}**.",
        "",
        "## Power projection (bootstrap + analytic normal)",
        "",
        "| Level | Observed n | Mean | SD | First n with bootstrap CI > 0 | n for 80% power | n for 95% power |",
        "|---|---:|---:|---:|---:|---:|---:|",
        f"| Trade | {pt['observed_n']} | {pt['observed_mean']:.2f} | {pt['observed_stdev']:.2f} | "
        f"{pt['first_bootstrap_ci_excludes_zero_at_n']} | "
        f"{pt['analytic_n_for_80pct_power']} | {pt['analytic_n_for_95pct_power']} |",
        f"| Symbol | {ps['observed_n']} | {ps['observed_mean']:.2f} | {ps['observed_stdev']:.2f} | "
        f"{ps['first_bootstrap_ci_excludes_zero_at_n']} | "
        f"{ps['analytic_n_for_80pct_power']} | {ps['analytic_n_for_95pct_power']} |",
        "",
        "The projection assumes future trades/symbols are drawn from the observed distribution. "
        "It is a sample-size calculation, not evidence that the edge is real.",
        "",
        "## Expanding-window / refit walk-forward",
        "",
        "| Prefix | Bars | Canonical PnL | Trades | Block PnL | Block trades |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in wf["canonical_prefixes"]:
        lines.append(
            f"| {row['fraction']:.0%} | {row['bars']} | {row['total_pnl']:.2f} | "
            f"{row['num_trades']} | {row['incremental_block_pnl']:.2f} | "
            f"{row['incremental_block_trades']} |"
        )
    lines += [
        "",
        "| Prefix | Best knobs | In-sample PnL | OOS block PnL | Canonical OOS block PnL |",
        "|---|---|---:|---:|---:|",
    ]
    for row in wf["refit"]:
        lines.append(
            f"| {row['prefix_fraction']:.0%} | {row['best_overrides']} | "
            f"{row['in_sample_pnl']:.2f} | {row['out_of_sample_block_pnl']:.2f} | "
            f"{row['canonical_out_of_sample_block_pnl']:.2f} |"
        )
    if wf["skipped"]:
        lines += ["", "Skipped blocks (no new trades to evaluate):"]
        for row in wf["skipped"]:
            lines.append(f"- {row['prefix_fraction']:.0%}: {row['reason']}")
    lines += [
        "",
        f"- Refit OOS total (evaluable blocks only): **{wf['refit_out_of_sample_total_pnl']:.2f}** "
        f"({wf['refit_out_of_sample_positive_blocks']} positive / "
        f"{wf['refit_out_of_sample_negative_blocks']} negative; "
        f"{wf['evaluable_blocks']} evaluable / {wf['non_evaluable_blocks']} skipped).",
        f"- Canonical incremental total: **{wf['canonical_incremental_total_pnl']:.2f}**.",
        f"- Refit scope: {wf['refit_scope']}.",
        "",
        "## Interpretation",
        "",
        "This stress test cannot upgrade the verdict. A result that survives every "
        "leave-one-out re-run and a refit walk-forward is more credible than one that "
        "does not, but it is still an 8-trade, 5-symbol, cross-venue OKX sample. The "
        "canonical remains **`underpowered`** until Hyperliquid-native evidence meets the "
        "GO criteria in `research_state/decision_memo_okx_full.md`.",
        "",
        "## Limitations",
        "",
    ]
    for lim in r["limitations"]:
        lines.append(f"- {lim}")
    lines.append("")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="research_state/robustness_stress_okx_full")
    parser.add_argument("--resamples", type=int, default=BOOTSTRAP_RESAMPLES)
    args = parser.parse_args(argv)

    t0 = time.time()
    inp = load_inputs(REPO)
    memo, rows, memo_meta = build_memo(inp)
    full_keys = event_keys(memo, rows)
    canon = canonical_keys(memo, rows)
    candles = {s: inp["candles"][s] for s in sorted({s for s, _ in memo} | {"ETH"})
               if s in inp["candles"]}

    if memo_meta["memo_signals"] != 11:
        raise SystemExit(
            f"memo signals={memo_meta['memo_signals']}, expected 11; census/config changed")
    if not memo_meta["memo_matches_signal_gate"]:
        raise SystemExit("memo signals do not match census signal_gate_pass count")
    if len(canon) != CANONICAL_TRADES:
        raise SystemExit(f"canonical admitted keys={len(canon)}, expected {CANONICAL_TRADES}")

    full = _run(candles, inp["cfg"], memo, full_keys)
    full_summary = trade_summary(full)
    if (full_summary["num_trades"] != CANONICAL_TRADES
            or abs(full_summary["total_pnl"] - CANONICAL_PNL) > 1e-9):
        raise SystemExit(
            "canonical full-signal replay mismatch: "
            f"trades={full_summary['num_trades']} pnl={full_summary['total_pnl']!r} "
            f"expected {CANONICAL_TRADES}/{CANONICAL_PNL!r}")

    canon_run = _run(candles, inp["cfg"], memo, canon)
    canon_summary = trade_summary(canon_run)
    if (canon_summary["num_trades"] != CANONICAL_TRADES
            or abs(canon_summary["total_pnl"] - CANONICAL_PNL) > 1e-9):
        raise SystemExit(
            "canonical admitted replay mismatch: "
            f"trades={canon_summary['num_trades']} pnl={canon_summary['total_pnl']!r}")

    trades = _trade_table(canon_run)
    if len(trades) != CANONICAL_TRADES:
        raise SystemExit(f"canonical trade table has {len(trades)} trades, expected {CANONICAL_TRADES}")

    loso = _loo_symbol(candles, inp["cfg"], memo, rows, full_keys)
    loto = _loto(candles, inp["cfg"], memo, rows, full_keys)
    conc = _concentration(trades, rows)

    trade_pnls = [float(t["total_pnl"]) for t in trades]
    symbol_pnls = _symbol_pnls(trades)
    rng = random.Random(SEED)
    power = {
        "trade_level": _power_curve(trade_pnls, TRADE_N_GRID, args.resamples, rng),
        "symbol_level": _power_curve(symbol_pnls, SYMBOL_N_GRID, args.resamples, rng),
    }

    wf = _walkforward(candles, inp["cfg"], memo, full_keys)

    result = {
        "schema_version": 1,
        "generated_at_utc": iso_now(),
        "seed": SEED,
        "provenance_caveat": PROVENANCE_CAVEAT,
        "method": (
            "Exact full-portfolio robustness stress: leave-one-symbol-out and "
            "leave-one-trade-out re-run the real portfolio engine with all other "
            "signals intact; concentration-adjusted inference; bootstrap + analytic "
            "power projection; expanding-window refit walk-forward."
        ),
        "canonical": {
            "trades": CANONICAL_TRADES,
            "total_pnl": CANONICAL_PNL,
            "sha256": sha256_file(REPO / "research_state/campaign_results_real_okx_full.json"),
            "full_replay": {
                "num_trades": full_summary["num_trades"],
                "total_pnl": full_summary["total_pnl"],
            },
            "admitted_replay": {
                "num_trades": canon_summary["num_trades"],
                "total_pnl": canon_summary["total_pnl"],
            },
        },
        "memo_meta": memo_meta,
        "leave_one_symbol_out": loso,
        "leave_one_trade_out": loto,
        "concentration": conc,
        "power": power,
        "walkforward": wf,
        "verdict": "underpowered",
        "wall_seconds": round(time.time() - t0, 3),
        "limitations": [
            "8 trades across 5 symbols is a very small sample; LOO/LOTO re-runs cannot create information the sample does not contain.",
            "The bootstrap/power projection assumes future trades and symbols are drawn from the observed distribution; it is a sample-size calculation, not evidence of edge.",
            "The refit walk-forward varies execution/portfolio knobs only; signal generation is fixed at the canonical spec config (RSI<20, 9% target, 8x safety stop).",
            "Expanding-window prefixes start at bar 0 and preserve RSI warmup; trades that open in a block but do not exit by the block end are not counted.",
            "Cross-venue OKX cache; NOT Hyperliquid performance evidence.",
        ],
    }

    out_json = Path(args.out + ".json")
    out_md = Path(args.out + ".md")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, indent=2, sort_keys=False) + "\n")
    out_md.write_text(_render_md(result))

    print(f"wrote {out_json}")
    print(f"wrote {out_md}")
    print(
        f"canonical={result['canonical']['total_pnl']:.6f} "
        f"loo_all_positive={loso['all_positive']} loto_all_positive={loto['all_positive']} "
        f"trade_n_ci0={power['trade_level']['first_bootstrap_ci_excludes_zero_at_n']} "
        f"symbol_n_ci0={power['symbol_level']['first_bootstrap_ci_excludes_zero_at_n']} "
        f"refit_oos={wf['refit_out_of_sample_total_pnl']:.2f} "
        f"wall={result['wall_seconds']}s"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())