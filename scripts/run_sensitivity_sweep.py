#!/usr/bin/env python3
"""Parallel resumable parameter sweeps for the real OKX campaign.

Two grids:
- ``--grid ofat`` (default): Phase J2 one-factor-at-a-time around the spec baseline.
- ``--grid interaction``: Phase K two-factor combinations of the knobs J2 flags as
  material. Single-factor sweeps cannot see interactions, so this is the next heavy
  campaign. It reuses the J2 baseline per-run file when present.

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
- Resumable: a per-run file whose tag and knob values match the job is reused, so a
  session killed mid-sweep continues from the remaining runs instead of restarting
  the whole ~70 minute job. A lock prevents two sweeps from racing.
- Never fabricates data. Spec-locked knobs (position size pct) are reported as
  rejected with the exact error instead of being silently mutated.
"""
from __future__ import annotations

import argparse
import atexit
import json
import math
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

# Interaction grid (Phase K): two-factor combinations around the knobs that the
# one-factor sweep (Phase J2) flags as material. Single-factor sweeps cannot see
# interactions, so this is the next heavy campaign. Baseline is reused from the
# same runs-dir when present (resume contract), so only the combinations run.
INTERACTION_GRID: List[Tuple[str, Dict[str, Any], str]] = [
    ("rsi18_maxpos3", {"rsi_threshold": 18.0, "max_positions": 3},
     "RSI<18 with max 3 concurrent positions"),
    ("rsi18_maxpos8", {"rsi_threshold": 18.0, "max_positions": 8},
     "RSI<18 with max 8 concurrent positions"),
    ("rsi25_maxpos3", {"rsi_threshold": 25.0, "max_positions": 3},
     "RSI<25 with max 3 concurrent positions"),
    ("rsi25_maxpos8", {"rsi_threshold": 25.0, "max_positions": 8},
     "RSI<25 with max 8 concurrent positions"),
    ("rsi25_target6", {"rsi_threshold": 25.0, "target_pct": 6.0},
     "RSI<25 with +6% buy target"),
    ("rsi25_target12", {"rsi_threshold": 25.0, "target_pct": 12.0},
     "RSI<25 with +12% buy target"),
    ("rsi15_maxpos3", {"rsi_threshold": 15.0, "max_positions": 3},
     "RSI<15 with max 3 concurrent positions"),
    ("rsi15_maxpos8", {"rsi_threshold": 15.0, "max_positions": 8},
     "RSI<15 with max 8 concurrent positions"),
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


def _fmt(value: Any, digits: int = 4) -> str:
    """Format a possibly-missing metric without crashing the aggregate render."""
    if value is None:
        return "n/a"
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return "n/a"


def _delta(current: Any, base: Any) -> Optional[float]:
    """Return current-base, or None when either side is not a finite number."""
    if current is None or base is None:
        return None
    try:
        out = float(current) - float(base)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


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
    if report.get("resumed_runs"):
        lines.append(f"**Resumed from disk:** {report['resumed_runs']} run(s) reused  ")
    lines.append(f"**Wall clock:** {report['wall_clock_seconds']}s across {report['workers']} workers "
                 f"(sequential-equivalent {report['sequential_equivalent_seconds']}s)  ")
    lines.append(f"**Inputs:** manifest `{report['inputs']['manifest']}`  ")
    lines.append(f"Universe `{report['inputs']['universe']}` ({report['inputs']['universe_size']} symbols)  ")
    lines.append(f"Canonical campaign for reference: `{CANONICAL_CAMPAIGN}` "
                 f"(`results.num_trades={report['canonical'].get('num_trades')}`, "
                 f"`results.total_pnl={report['canonical'].get('total_pnl')}`)")
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
            f"| `{r['tag']}` | {r['label']} | {m['trade_count']} | {_fmt(m['total_return_pct'])} | "
            f"{_fmt(m['annualized_return_pct'])} | {_fmt(m['max_drawdown_pct'])} | {_fmt(m['win_rate'])} | "
            f"{_fmt(m['profit_factor'])} | "
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
        d_ret = _delta(m["total_return_pct"], base["metrics"]["total_return_pct"])
        d_ann = _delta(m["annualized_return_pct"], base["metrics"]["annualized_return_pct"])
        d_dd = _delta(m["max_drawdown_pct"], base["metrics"]["max_drawdown_pct"])
        d_tr = (m["trade_count"] or 0) - (base["metrics"]["trade_count"] or 0)
        moves = "yes" if (d_tr != 0 or (d_ret is not None and abs(d_ret) >= 0.5)) else "no (immaterial)"
        lines.append(
            f"| `{r['tag']}` | {_fmt(d_ret, 4) if d_ret is not None else 'n/a'} | "
            f"{_fmt(d_ann, 4) if d_ann is not None else 'n/a'} | "
            f"{_fmt(d_dd, 4) if d_dd is not None else 'n/a'} | {d_tr:+d} | {moves} |"
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
            lines.append(f"| `{r['tag']}` | `{json.dumps(r.get('params', {}))}` | {r.get('error')} |")
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


def _reusable_record(path: Path, job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Return a previously completed per-run record iff it matches this job exactly.

    Resume is only safe when the record's tag and knob values are identical to the
    job we are about to run; otherwise the old record is ignored and the run is
    re-executed. This is what lets a session that is killed mid-sweep continue from
    the per-run files instead of paying the full ~70 minute cost again.
    """
    if not path.exists():
        return None
    try:
        rec = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(rec, dict):
        return None
    if rec.get("tag") != job["tag"]:
        return None
    if rec.get("params") != dict(job["config_kwargs"]):
        return None
    if rec.get("status") == "ok":
        return rec if isinstance(rec.get("metrics"), dict) else None
    if rec.get("status") == "rejected":
        return rec
    return None


def _acquire_run_lock(path: Path) -> Optional[int]:
    """Take an exclusive sweep lock, or return None if a live sweep already holds it.

    Two concurrent sweeps would overwrite each other's per-run files and aggregate.
    A lock whose owning PID is gone is treated as stale and replaced.
    """
    for _ in range(2):
        try:
            fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            pid: Optional[int] = None
            try:
                pid = int(path.read_text().strip())
            except (OSError, ValueError):
                pid = None
            if pid is not None:
                try:
                    os.kill(pid, 0)
                except ProcessLookupError:
                    try:
                        path.unlink()
                    except OSError:
                        pass
                    continue
                except PermissionError:
                    print(f"BLOCKER: sweep already running (pid {pid})", file=sys.stderr)
                    return None
                print(f"BLOCKER: sweep already running (pid {pid}); use --runs-dir to isolate", file=sys.stderr)
                return None
            try:
                path.unlink()
            except OSError:
                pass
            continue
        os.write(fd, f"{os.getpid()}\n".encode())
        return fd
    return None


def build_jobs(grid_name: str, only: Optional[List[str]],
               capital: float = 100000.0) -> List[Dict[str, Any]]:
    """Build the baseline-first job list for the requested grid.

    Baseline uses pure spec defaults and is always first so deltas read against it.
    Resume reuses a matching baseline per-run file, so the interaction grid does not
    pay for the baseline twice.
    """
    grid = INTERACTION_GRID if grid_name == "interaction" else GRID
    selected = [g for g in grid if not only or g[0] in set(only)]
    if not selected:
        raise SystemExit("BLOCKER: --only matched no grid entries")
    jobs: List[Dict[str, Any]] = [{
        "tag": "baseline_spec",
        "label": "Spec baseline: RSI(21)<20, +9%/50h, short -9%/48h, 1.25% sizing, hedge 3x, 120% cap",
        "config_kwargs": {},
        "min_daily_volume_usd": 5_000_000.0,
        "capital": float(capital),
    }]
    for tag, kwargs, label in selected:
        jobs.append({
            "tag": tag,
            "label": label,
            "config_kwargs": dict(kwargs),
            "min_daily_volume_usd": 5_000_000.0,
            "capital": float(capital),
        })
    return jobs


def build_conclusions(runs: List[Dict[str, Any]], capital: float = 100000.0) -> Tuple[str, Dict[str, Any]]:
    """Rank knobs by return/trade/PnL deltas against the baseline.

    A run whose equity-curve horizon is not derivable has a null total_return_pct;
    it is still ranked by trade-count and total-PnL deltas so it cannot silently
    disappear from the analysis (and cannot crash the aggregate).
    """
    base = runs[0]["metrics"]
    base_return = base.get("total_return_pct")
    base_dd = base.get("max_drawdown_pct")
    base_trades = base.get("trade_count") or 0
    ranked = []
    for r in runs[1:]:
        m = r.get("metrics")
        if not m:
            continue
        d_ret = _delta(m.get("total_return_pct"), base_return)
        d_ann = _delta(m.get("annualized_return_pct"), base.get("annualized_return_pct"))
        d_dd = _delta(m.get("max_drawdown_pct"), base_dd)
        d_trades = (m.get("trade_count") or 0) - base_trades
        d_pnl = _delta(m.get("total_pnl"), base.get("total_pnl"))
        abs_ret = abs(d_ret) if d_ret is not None else None
        ranked.append({
            "tag": r["tag"],
            "label": r["label"],
            "delta_total_return_pp": None if d_ret is None else round(d_ret, 6),
            "delta_annualized_pp": None if d_ann is None else round(d_ann, 6),
            "delta_trades": d_trades,
            "delta_max_dd_pp": None if d_dd is None else round(d_dd, 6),
            "delta_total_pnl": None if d_pnl is None else round(d_pnl, 6),
            "abs_delta_return_pp": None if abs_ret is None else round(abs_ret, 6),
        })
    pnl_floor = 0.01 * float(capital or 0.0)
    for r in ranked:
        r["_material"] = (
            r["delta_trades"] != 0
            or (r["abs_delta_return_pp"] is not None and r["abs_delta_return_pp"] >= 0.5)
            or (r["abs_delta_return_pp"] is None and r["delta_total_pnl"] is not None
                and abs(r["delta_total_pnl"]) >= pnl_floor)
        )
    ranked.sort(key=lambda x: (
        -(x["abs_delta_return_pp"] if x["abs_delta_return_pp"] is not None
          else (abs(x["delta_total_pnl"]) / float(capital or 1.0) * 100.0
                if x["delta_total_pnl"] is not None else 0.0)),
        -abs(x["delta_trades"]),
    ))
    material = [r for r in ranked if r["_material"]]
    immaterial = [r for r in ranked if not r["_material"]]
    lines: List[str] = []
    lines.append("**Material knobs** (|Δ total return| ≥ 0.5pp, any trade-count change, or "
                 "|Δ total PnL| ≥ 1% of capital when return is not derivable), ranked:")
    lines.append("")
    if material:
        for r in material:
            ret = "n/a" if r["delta_total_return_pp"] is None else f"{r['delta_total_return_pp']:+.4f}pp"
            lines.append(
                f"- `{r['tag']}` ({r['label']}): Δ return {ret}, "
                f"Δ trades {r['delta_trades']:+d}, Δ PnL "
                f"{'n/a' if r['delta_total_pnl'] is None else format(r['delta_total_pnl'], '+.2f')}"
            )
    else:
        lines.append("- none")
    lines.append("")
    lines.append("**Immaterial knobs** (|Δ total return| < 0.5pp and identical trade count):")
    lines.append("")
    if immaterial:
        for r in immaterial:
            ret = "n/a" if r["delta_total_return_pp"] is None else f"{r['delta_total_return_pp']:+.4f}pp"
            lines.append(f"- `{r['tag']}` ({r['label']}): Δ return {ret}, Δ trades {r['delta_trades']:+d}")
    else:
        lines.append("- none")
    lines.append("")
    for r in ranked:
        r.pop("_material", None)
    summary = {
        "baseline": {
            "tag": runs[0]["tag"],
            "total_return_pct": base_return,
            "trade_count": base_trades,
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
    ap.add_argument("--grid", choices=("ofat", "interaction"), default="ofat",
                    help="ofat = one-factor Phase J2 grid; interaction = Phase K two-factor grid.")
    ap.add_argument("--only", nargs="*", default=None, help="Optional subset of grid tags to execute.")
    ap.add_argument("--no-resume", action="store_true",
                    help="Re-execute every run even if a matching per-run file already exists.")
    ap.add_argument("--allow-partial", action="store_true",
                    help="Write the aggregate even when the executed set is incomplete.")
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

    if args.smoke:
        jobs = build_jobs(args.grid, args.only, capital=args.capital)
        job = dict(jobs[0])
        job["data"] = None
        job["min_daily_volume_usd"] = 5_000_000.0
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

    try:
        jobs = build_jobs(args.grid, args.only, capital=args.capital)
    except SystemExit as exc:
        print(exc, file=sys.stderr)
        return 2

    runs_dir = REPO_ROOT / args.runs_dir
    runs_dir.mkdir(parents=True, exist_ok=True)

    lock_path = REPO_ROOT / "research_state" / ".sensitivity_sweep.lock"
    lock_fd = _acquire_run_lock(lock_path)
    if lock_fd is None:
        return 3

    def _release_lock() -> None:
        try:
            os.close(lock_fd)
        except OSError:
            pass
        try:
            lock_path.unlink()
        except OSError:
            pass

    atexit.register(_release_lock)

    records: List[Optional[Dict[str, Any]]] = [None] * len(jobs)
    todo: List[int] = list(range(len(jobs)))
    resumed = 0
    if not args.no_resume:
        todo = []
        for idx, job in enumerate(jobs):
            rec = _reusable_record(runs_dir / f"{job['tag']}.json", job)
            if rec is not None:
                records[idx] = rec
                resumed += 1
            else:
                todo.append(idx)
        if resumed:
            print(f"[sweep] resume: {resumed}/{len(jobs)} runs reused from {runs_dir}", flush=True)

    print(f"[sweep] {len(jobs)} runs, {len(todo)} to execute, workers={args.workers}", flush=True)
    wall_start = time.time()

    ctx = mp.get_context("fork")
    if todo:
        todo_jobs = [jobs[i] for i in todo]
        with ctx.Pool(processes=args.workers, initializer=_worker_init, initargs=(payload,)) as pool:
            for sub_idx, rec in enumerate(pool.imap_unordered(_worker_run, todo_jobs)):
                idx = todo[sub_idx]
                records[idx] = rec
                m = rec.get("metrics") or {}
                print(
                    f"[sweep] {rec['tag']}: status={rec['status']} "
                    f"trades={m.get('trade_count')} ret={m.get('total_return_pct')} "
                    f"dd={m.get('max_drawdown_pct')} {rec['runtime_seconds']}s",
                    flush=True,
                )
                (runs_dir / f"{rec['tag']}.json").write_text(json.dumps(rec, indent=2) + "\n")
    else:
        print("[sweep] all runs already present; rebuilding aggregate", flush=True)

    wall = round(time.time() - wall_start, 2)
    runs = [r for r in records if r is not None]
    sequential = round(sum(float(r.get("runtime_seconds") or 0.0) for r in runs), 2)

    rejected = [r for r in runs if r.get("status") != "ok"]
    executed = [r for r in runs if r.get("status") == "ok"]
    if not executed:
        print("BLOCKER: every run failed; see per-run files", file=sys.stderr)
        return 1
    if executed[0].get("tag") != "baseline_spec":
        print("BLOCKER: baseline is missing or failed; cannot build deltas", file=sys.stderr)
        return 1
    if len(executed) < len(jobs) and not args.allow_partial:
        missing = sorted({j["tag"] for j in jobs} - {r.get("tag") for r in executed})
        print(
            f"BLOCKER: {len(executed)}/{len(jobs)} runs succeeded; missing {missing}. "
            "Re-run to resume; pass --allow-partial only if an incomplete aggregate is intended.",
            file=sys.stderr,
        )
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

    conclusions_md, conclusions = build_conclusions(executed, capital=args.capital)

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
        "grid": args.grid,
        "run_type": "parameter_interaction_sweep" if args.grid == "interaction" else "parameter_sensitivity_sweep",
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
        "resumed_runs": resumed,
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