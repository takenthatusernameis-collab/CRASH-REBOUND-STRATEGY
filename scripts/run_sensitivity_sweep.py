#!/usr/bin/env python3
"""Parallel one-factor-at-a-time sensitivity sweep for the real OKX campaign (Phase J2).

Why this exists: a single canonical campaign run over the verified 54-symbol OKX
cache takes ~10 minutes of pure bar-by-bar simulation. A 16-run sweep is therefore a
~2.7 hour serial job, which is why earlier sessions kept deferring Phase J2. This
runner removes that bottleneck by fanning the runs out across worker processes
(the bar loop is CPU-bound and per-run independent), so the full sweep completes in
the time of a few sequential runs.

Contract:
- Inputs are ONLY the committed on-disk manifest + cache + universe (never re-acquired).
- Every run goes through the same provenance/volume gates as scripts/run_real_campaign.py.
- Canonical artifacts are NEVER written or overwritten. Each run writes
  research_state/sweep_runs/<tag>.json; the aggregate is
  research_state/sensitivity_sweep_real_okx_full.json + .md.
- Never fabricates data. Spec-locked knobs (position size pct) are reported as
  rejected with the exact error instead of being silently mutated.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

PROVENANCE_CAVEAT = (
    "Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; "
    "NOT Hyperliquid performance evidence."
)

DEFAULT_MANIFEST = "research_state/cache/okx_1h_full_20251220_20260928/provenance.json"
DEFAULT_CACHE = "research_state/cache/okx_1h_full_20251220_20260928"
DEFAULT_UNIVERSE = "research_state/universe_okx_full_verified.json"
CANONICAL_CAMPAIGN = "research_state/campaign_results_real_okx_full.json"

# One-factor-at-a-time grid around the spec baseline. Each entry is
# (tag, config_kwargs, human_label). Baseline is added automatically and must be
# the first entry in the aggregate so deltas read against it.
GRID: List[Tuple[str, Dict[str, Any], str]] = [
    ("rsi_threshold_15", {"rsi_threshold": 15.0}, "RSI(21) crash trigger < 15 (spec 20)"),
    ("rsi_threshold_18", {"rsi_threshold": 18.0}, "RSI(21) crash trigger < 18 (spec 20)"),
    ("rsi_threshold_25", {"rsi_threshold": 25.0}, "RSI(21) crash trigger < 25 (spec 20)"),
    ("buy_target_6pct", {"target_pct": 6.0}, "Buy target +6% (spec +9%)"),
    ("buy_target_12pct", {"target_pct": 12.0}, "Buy target +12% (spec +9%)"),
    ("buy_hold_24h", {"time_exit_max_bars": 24}, "Buy max hold 24h (spec 50h)"),
    ("buy_hold_72h", {"time_exit_max_bars": 72}, "Buy max hold 72h (spec 50h)"),
    ("short_target_6pct", {"rebound_short_target_pct": 6.0}, "Rebound-short target -6% (spec -9%)"),
    ("short_target_12pct", {"rebound_short_target_pct": 12.0}, "Rebound-short target -12% (spec -9%)"),
    ("short_hold_24h", {"rebound_short_time_exit_bars": 24}, "Rebound-short max hold 24h (spec 48h)"),
    ("short_hold_72h", {"rebound_short_time_exit_bars": 72}, "Rebound-short max hold 72h (spec 48h)"),
    ("eth_hedge_cap_1x", {"hedge_cap_multiplier": 1.0}, "ETH hedge cap 1x position (spec 3x)"),
    ("eth_hedge_cap_2x", {"hedge_cap_multiplier": 2.0}, "ETH hedge cap 2x position (spec 3x)"),
    ("no_rebound_short", {"enable_rebound_short": False}, "Rebound short disabled (spec enabled)"),
    ("max_positions_3", {"max_positions": 3}, "Max concurrent positions 3 (spec 5)"),
    ("max_positions_8", {"max_positions": 8}, "Max concurrent positions 8 (spec 5)"),
]

# Knobs the spec pins, so they cannot be swept as free parameters. Recorded as
# rejected with the raised error rather than silently mutated.
SPEC_LOCKED: List[Tuple[str, Dict[str, Any], str]] = [
    ("position_size_0p5pct", {"position_size_pct_of_daily_volume": 0.5},
     "Position size 0.5% of 24h volume (spec 1.25%)"),
    ("position_size_2p0pct", {"position_size_pct_of_daily_volume": 2.0},
     "Position size 2.0% of 24h volume (spec 1.25%)"),
]


def _iso(ms: Optional[int]) -> Optional[str]:
    if ms is None:
        return None
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_inputs(manifest_path: Path, cache_dir: Path, universe_file: Path, capital: float):
    """Run the exact same gate chain as run_real_campaign, then load verified candles once."""
    from src.data.provenance import require_verified_provenance, load_provenance
    from scripts.run_real_campaign import (
        load_universe,
        load_verified_cache,
        validate_symbol_volume_coverage,
        _validated_complete_symbols,
    )
    from src.strategy.config import SPEC_MIN_DAILY_VOLUME_USD

    # Universe scoping MUST precede provenance validation (same ordering as
    # run_real_campaign): a manifest may legitimately hold symbols that do not meet
    # the >= $5M floor in this market, and those out-of-universe symbols must not be
    # able to fail the whole run.
    raw = load_provenance(manifest_path)
    universe = load_universe(universe_file, raw)
    if not universe:
        raise SystemExit("BLOCKER: universe file empty or unreadable")

    manifest = require_verified_provenance(
        manifest_path,
        require_complete=True,
        min_symbols=1,
        require_spec_volume_floor=SPEC_MIN_DAILY_VOLUME_USD,
        symbols=universe,
    )
    filtered = {k: v for k, v in (manifest.get("symbols") or {}).items() if str(k).upper() in set(universe)}
    if not filtered:
        raise SystemExit("BLOCKER: no manifest symbols match universe file")
    manifest = dict(manifest)
    manifest["symbols"] = filtered
    passing = validate_symbol_volume_coverage(
        manifest, universe, SPEC_MIN_DAILY_VOLUME_USD
    )
    data = load_verified_cache(cache_dir, manifest)
    data = {s: d for s, d in data.items() if s in set(passing)}
    if not data:
        raise SystemExit("BLOCKER: no verified symbol data passed coverage + volume validation")
    return manifest, data, universe, _validated_complete_symbols(manifest)


def _run_one(job: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a single campaign configuration. Runs in a worker process."""
    tag = job["tag"]
    label = job["label"]
    kwargs = dict(job["config_kwargs"])
    started = time.time()
    record: Dict[str, Any] = {
        "tag": tag,
        "label": label,
        "params": dict(kwargs),
        "status": "ok",
    }
    try:
        from src.strategy.config import StrategyConfig
        from scripts.run_portfolio import run_portfolio_simulation
        from src.metrics import compute_campaign_metrics

        config = StrategyConfig(
            use_rsi_trigger=True,
            enable_rebound_short=True,
            enable_eth_hedge=True,
            enable_volume_based_sizing=True,
            min_daily_volume_usd=job["min_daily_volume_usd"],
            **kwargs,
        )
        eth = job["data"].get("ETH")
        results = run_portfolio_simulation(
            job["data"],
            config=config,
            capital=job["capital"],
            eth_candles={"ETH": eth} if eth else None,
            require_eth_hedge=bool(getattr(config, "enable_eth_hedge", True)),
        )
        metrics = compute_campaign_metrics(
            trades=results.get("trades", []),
            equity_curve=results.get("equity_curve"),
            initial_capital=job["capital"],
            apply_vault_fees=True,
        )
        trades = results.get("trades") or []
        by_leg: Dict[str, Dict[str, Any]] = {}
        for t in trades:
            leg = str(t.get("leg") or "buy")
            slot = by_leg.setdefault(leg, {"trades": 0, "pnl": 0.0, "wins": 0})
            slot["trades"] += 1
            slot["pnl"] += float(t.get("total_pnl") or 0.0)
            if float(t.get("total_pnl") or 0.0) > 0:
                slot["wins"] += 1
        exit_reasons: Dict[str, int] = {}
        for t in trades:
            r = str(t.get("exit_reason") or "unknown")
            exit_reasons[r] = exit_reasons.get(r, 0) + 1
        record["metrics"] = {
            "total_return_pct": metrics.get("equity_total_return_pct"),
            "annualized_return_pct": metrics.get("equity_annualized_return_pct"),
            "horizon_years": metrics.get("equity_horizon_years"),
            "max_drawdown_pct": metrics.get("equity_max_drawdown_pct"),
            "sharpe": metrics.get("sharpe_ratio"),
            "sortino": metrics.get("sortino_ratio"),
            "calmar": metrics.get("calmar_ratio"),
            "win_rate": metrics.get("win_rate"),
            "profit_factor": metrics.get("profit_factor"),
            "trade_count": int(metrics.get("exposure_metrics", {}).get("total_trades", len(trades)) or 0),
            "total_pnl": results.get("total_pnl"),
            "net_total_pnl": metrics.get("net_total_pnl"),
            "equity_final": metrics.get("equity_final"),
            "positive_months": metrics.get("positive_months"),
            "negative_months": metrics.get("negative_months"),
            "total_months": metrics.get("total_months"),
            "by_leg": by_leg,
            "exit_reasons": exit_reasons,
            "traded_symbols": sorted({str(t.get("symbol")) for t in trades}),
            "max_live_coin_notional_max": max(
                [float(t.get("max_live_coin_notional") or 0.0) for t in trades] or [0.0]
            ),
            "gross_cap_usd": job["capital"] * float(config.gross_cap_pct) / 100.0,
        }
    except Exception as exc:  # spec-lock rejection or any other fail-closed error
        record["status"] = "rejected"
        record["error_type"] = type(exc).__name__
        record["error"] = str(exc)
        record["metrics"] = None
    record["runtime_seconds"] = round(time.time() - started, 2)
    return record


def _worker_init(payload: Dict[str, Any]) -> None:
    """Load inputs once per worker process (fork-inherited cache is not relied on)."""
    manifest, data, universe, complete = _load_inputs(
        Path(payload["manifest"]), Path(payload["cache_dir"]),
        Path(payload["universe"]), float(payload["capital"]),
    )
    _worker_init.state = {  # type: ignore[attr-defined]
        "data": data,
        "universe": universe,
        "complete": complete,
        "manifest": manifest,
        "capital": float(payload["capital"]),
    }


def _worker_run(job: Dict[str, Any]) -> Dict[str, Any]:
    job = dict(job)
    job["data"] = _worker_init.state["data"]  # type: ignore[attr-defined]
    job.setdefault("capital", _worker_init.state.get("capital", 100000.0))  # type: ignore[attr-defined]
    return _run_one(job)


def render_markdown(report: Dict[str, Any]) -> str:
    runs = report["runs"]
    base = runs[0]
    lines: List[str] = []
    lines.append("# Parameter Sensitivity Sweep — Real OKX 283-Day Campaign (Phase J2)")
    lines.append("")
    lines.append(f"**Generated (UTC):** {report['generated_at_utc']}  ")
    lines.append(f"**Provenance caveat:** {report['provenance_caveat']}")
    lines.append("")
    lines.append("One-factor-at-a-time around the spec baseline. Every run re-executes the full "
                 "bar-by-bar portfolio simulation from the committed on-disk manifest/cache/universe. "
                 "No canonical artifact was overwritten; per-run outputs live in `research_state/sweep_runs/`.")
    lines.append("")
    lines.append(f"**Runs executed:** {len(runs)} (baseline + {len(runs) - 1} variants)  ")
    lines.append(f"**Wall clock:** {report['wall_clock_seconds']}s across {report['workers']} workers "
                 f"(sequential-equivalent {report['sequential_equivalent_seconds']}s)  ")
    lines.append(f"**Inputs:** manifest `{report['inputs']['manifest']}`  ")
    lines.append(f"Universe `{report['inputs']['universe']}` ({report['inputs']['universe_size']} symbols)  ")
    lines.append(f"Canonical campaign for reference: `{CANONICAL_CAMPAIGN}` "
                 f"(`results.num_trades={report['canonical']['num_trades']}`, "
                 f"`results.total_pnl={report['canonical']['total_pnl']}`)")
    lines.append("")
    lines.append("## Baseline vs variants")
    lines.append("")
    lines.append("| Run | Change | Trades | Total return % | Annualized % | Worst DD % | Win rate | PF | Buy PnL | Short PnL | Runtime s |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in runs:
        m = r.get("metrics")
        if not m:
            lines.append(f"| `{r['tag']}` | {r['label']} | REJECTED: {r.get('error_type')} | - | - | - | - | - | - | - | {r.get('runtime_seconds')} |")
            continue
        by_leg = m.get("by_leg") or {}
        buy = by_leg.get("buy", {}).get("pnl")
        short = by_leg.get("short", {}).get("pnl")
        lines.append(
            f"| `{r['tag']}` | {r['label']} | {m['trade_count']} | {m['total_return_pct']:.4f} | "
            f"{m['annualized_return_pct']:.4f} | {m['max_drawdown_pct']:.4f} | {m['win_rate']:.4f} | "
            f"{m['profit_factor']:.4f} | "
            f"{'n/a' if buy is None else f'{buy:,.2f}'} | "
            f"{'n/a' if short is None else f'{short:,.2f}'} | {r['runtime_seconds']} |"
        )
    lines.append("")
    lines.append("## Deltas vs baseline (total return percentage points, trade count)")
    lines.append("")
    lines.append("| Run | Δ total return (pp) | Δ annualized (pp) | Δ worst DD (pp) | Δ trades | Moves result? |")
    lines.append("|---|---|---|---|---|---|")
    for r in runs[1:]:
        m = r.get("metrics")
        if not m:
            lines.append(f"| `{r['tag']}` | rejected ({r.get('error_type')}) | - | - | - | n/a |")
            continue
        d_ret = m["total_return_pct"] - base["metrics"]["total_return_pct"]
        d_ann = m["annualized_return_pct"] - base["metrics"]["annualized_return_pct"]
        d_dd = m["max_drawdown_pct"] - base["metrics"]["max_drawdown_pct"]
        d_tr = m["trade_count"] - base["metrics"]["trade_count"]
        moves = "yes" if abs(d_ret) >= 0.5 or d_tr != 0 else "no (immaterial)"
        lines.append(
            f"| `{r['tag']}` | {d_ret:+.4f} | {d_ann:+.4f} | {d_dd:+.4f} | {d_tr:+d} | {moves} |"
        )
    lines.append("")
    if report.get("rejected_runs"):
        lines.append("## Spec-locked knobs (not swept — rejected by design)")
        lines.append("")
        lines.append("`StrategyConfig` refuses to treat these as free parameters when volume-based sizing is "
                     "enabled, so a mutated value is a spec bypass attempt. They are recorded, not run:")
        lines.append("")
        lines.append("| Knob | Value | Error |")
        lines.append("|---|---|---|")
        for r in report["rejected_runs"]:
            lines.append(f"| `{r['tag']}` | `{json.dumps(r['params'])}` | {r.get('error')} |")
        lines.append("")
    lines.append("## Which knobs move results, which do not")
    lines.append("")
    lines.append(report["conclusions_md"])
    lines.append("")
    lines.append("## Caveats")
    lines.append("")
    for c in report["caveats"]:
        lines.append(f"- {c}")
    lines.append("")
    return "\n".join(lines)


def build_conclusions(runs: List[Dict[str, Any]]) -> Tuple[str, Dict[str, Any]]:
    """Rank knobs by |Δ total return| and |Δ trades| against the baseline."""
    base = runs[0]["metrics"]
    ranked = []
    for r in runs[1:]:
        m = r.get("metrics")
        if not m:
            continue
        ranked.append({
            "tag": r["tag"],
            "label": r["label"],
            "delta_total_return_pp": round(m["total_return_pct"] - base["total_return_pct"], 6),
            "delta_trades": m["trade_count"] - base["trade_count"],
            "delta_max_dd_pp": round(m["max_drawdown_pct"] - base["max_drawdown_pct"], 6),
            "abs_delta_return_pp": round(abs(m["total_return_pct"] - base["total_return_pct"]), 6),
        })
    ranked.sort(key=lambda x: (-x["abs_delta_return_pp"], -abs(x["delta_trades"])))
    material = [r for r in ranked if r["abs_delta_return_pp"] >= 0.5 or r["delta_trades"] != 0]
    immaterial = [r for r in ranked if r not in material]
    lines: List[str] = []
    lines.append("**Material knobs** (|Δ total return| ≥ 0.5pp or any trade-count change), ranked:")
    lines.append("")
    if material:
        for r in material:
            lines.append(
                f"- `{r['tag']}` ({r['label']}): Δ return {r['delta_total_return_pp']:+.4f}pp, "
                f"Δ trades {r['delta_trades']:+d}, Δ worst DD {r['delta_max_dd_pp']:+.4f}pp"
            )
    else:
        lines.append("- none")
    lines.append("")
    lines.append("**Immaterial knobs** (|Δ total return| < 0.5pp and identical trade count):")
    lines.append("")
    if immaterial:
        for r in immaterial:
            lines.append(f"- `{r['tag']}` ({r['label']}): Δ return {r['delta_total_return_pp']:+.4f}pp, Δ trades {r['delta_trades']:+d}")
    else:
        lines.append("- none")
    lines.append("")
    summary = {
        "baseline": {
            "tag": runs[0]["tag"],
            "total_return_pct": base["total_return_pct"],
            "trade_count": base["trade_count"],
        },
        "material_knobs": material,
        "immaterial_knobs": immaterial,
        "ranked": ranked,
    }
    return "\n".join(lines), summary


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", default=DEFAULT_MANIFEST)
    ap.add_argument("--cache-dir", default=DEFAULT_CACHE)
    ap.add_argument("--universe-file", default=DEFAULT_UNIVERSE)
    ap.add_argument("--capital", type=float, default=100000.0)
    ap.add_argument("--workers", type=int, default=max(1, min(4, os.cpu_count() or 1)))
    ap.add_argument("--runs-dir", default="research_state/sweep_runs")
    ap.add_argument("--output-prefix", default="sensitivity_sweep_real_okx_full")
    ap.add_argument("--only", nargs="*", default=None, help="Optional subset of grid tags to execute.")
    ap.add_argument("--smoke", action="store_true",
                    help="Fast plumbing check: 1 baseline run, write to a temp prefix, no aggregate.")
    args = ap.parse_args(argv)

    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = REPO_ROOT / manifest_path
    cache_dir = Path(args.cache_dir)
    if not cache_dir.is_absolute():
        cache_dir = REPO_ROOT / cache_dir
    universe_file = Path(args.universe_file)
    if not universe_file.is_absolute():
        universe_file = REPO_ROOT / universe_file

    prefix = Path(args.output_prefix)
    if prefix.is_absolute() or ".." in prefix.parts or len(prefix.parts) != 1:
        print(f"BLOCKER: unsafe output prefix {args.output_prefix!r}", file=sys.stderr)
        return 2

    grid = [g for g in GRID if not args.only or g[0] in set(args.only)]
    if not grid:
        print("BLOCKER: --only matched no grid entries", file=sys.stderr)
        return 2

    if args.smoke:
        job = {
            "tag": grid[0][0], "label": grid[0][2], "config_kwargs": dict(grid[0][1]),
            "data": None, "capital": args.capital,
            "min_daily_volume_usd": 5_000_000.0,
        }
        _, data, _, _ = _load_inputs(manifest_path, cache_dir, universe_file, args.capital)
        job["data"] = data
        rec = _run_one(job)
        print(json.dumps(rec, indent=2)[:2000])
        return 0 if rec.get("status") == "ok" else 1

    payload = {
        "manifest": str(manifest_path),
        "cache_dir": str(cache_dir),
        "universe": str(universe_file),
        "capital": args.capital,
    }

    # Baseline first, then the grid. Baseline uses pure spec defaults.
    jobs: List[Dict[str, Any]] = [{
        "tag": "baseline_spec",
        "label": "Spec baseline: RSI(21)<20, +9%/50h, short -9%/48h, 1.25% sizing, hedge 3x, 120% cap",
        "config_kwargs": {},
        "min_daily_volume_usd": 5_000_000.0,
        "capital": args.capital,
    }]
    for tag, kwargs, label in grid:
        jobs.append({
            "tag": tag, "label": label, "config_kwargs": dict(kwargs),
            "min_daily_volume_usd": 5_000_000.0,
            "capital": args.capital,
        })

    runs_dir = REPO_ROOT / args.runs_dir
    runs_dir.mkdir(parents=True, exist_ok=True)

    print(f"[sweep] {len(jobs)} runs, workers={args.workers}", flush=True)
    wall_start = time.time()
    records: List[Optional[Dict[str, Any]]] = [None] * len(jobs)

    ctx = mp.get_context("fork")
    with ctx.Pool(processes=args.workers, initializer=_worker_init, initargs=(payload,)) as pool:
        for idx, rec in enumerate(pool.imap_unordered(_worker_run, jobs)):
            records[idx] = rec
            m = rec.get("metrics") or {}
            print(
                f"[sweep] {rec['tag']}: status={rec['status']} "
                f"trades={m.get('trade_count')} ret={m.get('total_return_pct')} "
                f"dd={m.get('max_drawdown_pct')} {rec['runtime_seconds']}s",
                flush=True,
            )
            (runs_dir / f"{rec['tag']}.json").write_text(json.dumps(rec, indent=2) + "\n")

    wall = round(time.time() - wall_start, 2)
    runs = [r for r in records if r is not None]
    sequential = round(sum(float(r.get("runtime_seconds") or 0.0) for r in runs), 2)

    rejected = [r for r in runs if r.get("status") != "ok"]
    executed = [r for r in runs if r.get("status") == "ok"]
    if not executed:
        print("BLOCKER: every run failed; see per-run files", file=sys.stderr)
        return 1

    # Spec-locked probe: attempt them so the rejection is observed, not assumed.
    rejected_runs: List[Dict[str, Any]] = list(rejected)
    try:
        from src.strategy.config import StrategyConfig, enforce_spec_position_size_pct
        for tag, kwargs, label in SPEC_LOCKED:
            err = None
            try:
                StrategyConfig(enable_volume_based_sizing=True, **kwargs)
            except Exception as exc:
                err = f"{type(exc).__name__}: {exc}"
            rejected_runs.append({
                "tag": tag, "label": label, "params": dict(kwargs),
                "status": "rejected", "error": err or "no error raised (unexpected)",
            })
    except Exception:
        traceback.print_exc()

    conclusions_md, conclusions = build_conclusions(executed)

    canonical = {}
    canon_path = REPO_ROOT / CANONICAL_CAMPAIGN
    if canon_path.exists():
        c = json.loads(canon_path.read_text())
        canonical = {
            "num_trades": (c.get("results") or {}).get("num_trades"),
            "total_pnl": (c.get("results") or {}).get("total_pnl"),
            "metrics_total_return_pct": (c.get("metrics") or {}).get("equity_total_return_pct"),
            "sha256_note": "canonical artifact is read-only input to this sweep",
        }

    report = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_type": "parameter_sensitivity_sweep",
        "provenance_caveat": PROVENANCE_CAVEAT,
        "inputs": {
            "manifest": str(manifest_path.relative_to(REPO_ROOT)) if str(manifest_path).startswith(str(REPO_ROOT)) else str(manifest_path),
            "cache_dir": str(cache_dir),
            "universe": str(universe_file),
            "universe_size": len(json.loads(universe_file.read_text()).get("selected_symbols") or []),
            "canonical_campaign": CANONICAL_CAMPAIGN,
            "capital": args.capital,
        },
        "workers": args.workers,
        "wall_clock_seconds": wall,
        "sequential_equivalent_seconds": sequential,
        "speedup": round(sequential / wall, 2) if wall > 0 else None,
        "canonical": canonical,
        "runs": executed,
        "rejected_runs": rejected_runs,
        "conclusions": conclusions,
        "caveats": [
            "Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence.",
            "Single-factor variation only: no interaction effects are measured; a knob that is immaterial alone may matter conditional on another.",
            "Horizon is the realized-trade horizon, not the full 283-day window (no trades in the final ~4 months).",
            "Per-run full result JSON is retained under research_state/sweep_runs/ for audit.",
        ],
    }
    report["conclusions_md"] = conclusions_md

    out_json = REPO_ROOT / "research_state" / f"{prefix.name}.json"
    out_md = REPO_ROOT / "research_state" / f"{prefix.name}.md"
    out_json.write_text(json.dumps(report, indent=2) + "\n")
    out_md.write_text(render_markdown(report))

    print(f"[sweep] wall={wall}s sequential_equiv={sequential}s speedup={report['speedup']}x")
    print(f"[sweep] wrote {out_json}")
    print(f"[sweep] wrote {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())