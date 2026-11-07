#!/usr/bin/env python3
"""Run a REAL 283-day crash-rebound campaign ONLY against verified market data.

Hard gates:
- requires a verified provenance manifest (coverage + documented source)
- refuses fixture/synthetic data and incomplete coverage
- never fabricates data
- writes real artifacts clearly marked real_market_data=true with provenance ref

If verified data is unavailable, this script exits non-zero with concrete blockers.
"""
from __future__ import annotations

import argparse
import csv
import json
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.provenance import (  # noqa: E402
    require_verified_provenance,
    ProvenanceError,
    TARGET_START,
    TARGET_END,
    verify_cache_sha256,
    complete_symbol_subset,
    verify_candles_not_synthetic,
)
from src.data.loader import load_hyperliquid_candles  # noqa: E402
from src.strategy.config import StrategyConfig  # noqa: E402
from scripts.run_portfolio import run_portfolio_simulation  # noqa: E402
from src.metrics import compute_campaign_metrics, metrics_to_dict, metrics_to_csv_rows  # noqa: E402


def load_universe(universe_file: Optional[Path], manifest: dict) -> List[str]:
    if universe_file and universe_file.exists():
        u = json.loads(universe_file.read_text())
        syms = u.get("symbols") if isinstance(u, dict) else u
        return [str(s).upper() for s in syms]
    return [str(s).upper() for s in (manifest.get("symbols") or {}).keys()]


def validate_symbol_volume_coverage(manifest: dict, symbols: List[str],
                                    min_daily_volume_usd: float) -> List[str]:
    """Require every universe symbol to pass the >= min_daily_volume_usd 24h volume filter per verified coverage.

    Enforces both the manifest's volume_filter_ok flag AND the requested numeric
    threshold against observed_min_24h_usd_volume (never trust a stale/lying flag).
    Returns list of symbols that pass; raises ProvenanceError with concrete blockers.
    """
    errs: List[str] = []
    passing: List[str] = []
    symbols_map = manifest.get("symbols") or {}
    threshold = float(min_daily_volume_usd) if min_daily_volume_usd is not None else 0.0
    for sym in symbols:
        info = symbols_map.get(sym)
        if not isinstance(info, dict):
            errs.append(f"{sym}: missing from provenance manifest")
            continue
        cov = info.get("coverage") or {}
        if info.get("status") != "ok" or cov.get("complete_for_target_window") is not True:
            errs.append(
                f"{sym}: incomplete coverage (status={info.get('status')}, "
                f"observed={cov.get('observed_in_window_bars')}/{cov.get('expected_hourly_bars')})"
            )
            continue
        volcov = info.get("volume_coverage") or {}
        obs_min = volcov.get("observed_min_24h_usd_volume")
        if not volcov.get("volume_filter_ok"):
            errs.append(
                f"{sym}: volume filter not met (min_24h_usd={obs_min}, "
                f"mean={volcov.get('observed_mean_24h_usd_volume')}, bars={volcov.get('bars_passing')}/{volcov.get('bars_checked')})"
            )
            continue
        # Never trust flag alone: enforce requested threshold against observed minimum.
        if threshold > 0:
            if obs_min is None:
                errs.append(
                    f"{sym}: volume threshold {threshold:g} required but observed_min_24h_usd_volume missing "
                    f"(volume_filter_ok={volcov.get('volume_filter_ok')})"
                )
                continue
            try:
                obs_min_f = float(obs_min)
            except (TypeError, ValueError):
                errs.append(f"{sym}: observed_min_24h_usd_volume not numeric: {obs_min!r}")
                continue
            if obs_min_f < threshold:
                errs.append(
                    f"{sym}: observed_min_24h_usd_volume {obs_min_f:g} < required threshold {threshold:g} "
                    f"(volume_filter_ok={volcov.get('volume_filter_ok')})"
                )
                continue
        passing.append(sym)
    if errs:
        raise ProvenanceError("Real campaign blocked by per-symbol coverage/volume validation:\n- " + "\n- ".join(errs))
    return passing


def load_verified_cache(cache_dir: Path, manifest: dict) -> dict:
    candles_dir = cache_dir / "candles"
    out = {}
    for sym, info in (manifest.get("symbols") or {}).items():
        if info.get("status") != "ok":
            continue
        p = candles_dir / f"{sym}.json"
        if not p.exists():
            # try manifest path
            mp = info.get("cache_path")
            if mp:
                p = REPO_ROOT / mp
        if not p.exists():
            raise ProvenanceError(f"Missing verified cache file for {sym}: {p}")
        verify_cache_sha256(p, info.get("sha256"), sym)
        candles = load_hyperliquid_candles(str(p), symbol=sym)
        # Runtime re-detection: never trust the manifest's synthetic_check flag.
        # A flat / constant-close series is a placeholder dataset, not market
        # evidence, and must fail closed even if provenance claims status=ok.
        try:
            verify_candles_not_synthetic(candles, raise_on_synthetic=True)
        except ProvenanceError as e:
            raise ProvenanceError(
                f"{sym}: cached candle series rejected as synthetic ({p}): {e}"
            ) from e
        out[sym] = candles
    if not out:
        raise ProvenanceError("No complete verified symbol caches loaded")
    return out


def _normalize_output_prefix(output_prefix: str) -> str:
    """Normalize --output-prefix to a safe basename stem under research_state/.

    Prevents accidental nested paths like research_state/research_state/* when
    callers pass a prefix that already includes research_state/. Rejects
    path traversal / absolute prefixes.
    """
    raw = str(output_prefix or "").replace("\\", "/").strip()
    while raw.startswith("./"):
        raw = raw[2:]
    # Strip repeated leading research_state/ segments.
    while raw == "research_state" or raw.startswith("research_state/"):
        raw = raw[len("research_state"):] if raw == "research_state" else raw[len("research_state/"):]
        raw = raw.lstrip("/")
    raw = raw.strip("/")
    if not raw:
        raise ProvenanceError("output-prefix resolves to an empty filename stem")
    p = Path(raw)
    if p.is_absolute() or ".." in p.parts or len(p.parts) != 1:
        raise ProvenanceError(
            f"Unsafe output-prefix {output_prefix!r}: must resolve to a single filename stem under research_state/"
        )
    return p.name


def _execution_realism_metadata(config):
    """Explicit spec-vs-implementation execution realism markers (no microstructure claims)."""
    return {
        "execution_model": getattr(config, "execution_model", "hourly_bar_simplified"),
        "order_slicing_simulated": bool(getattr(config, "order_slicing_simulated", False)),
        "order_book_impact_model": getattr(config, "order_book_impact_model", "slippage_proxy"),
        "spread_bps_assumed": getattr(config, "spread_bps_assumed", 0.0),
        "slippage_pct": getattr(config, "slippage_pct", None),
        "funding_rate_pct_per_hour": getattr(config, "funding_rate_pct_per_hour", None),
        "enable_liquidation_checks": bool(getattr(config, "enable_liquidation_checks", False)),
        "liquidation_maint_margin_pct": getattr(config, "liquidation_maint_margin_pct", None),
        "limitation_note": (
            "Hourly bar simulation only. Per spec the strategy uses 20s order slicing and "
            "order-book-aware impact; this implementation does NOT simulate sub-hourly 20s "
            "slicing, explicit spread, or live L2 order-book impact. Fees/funding/hourly "
            "worst-price liquidation checks and slippage proxy may be modeled, but results "
            "must not be interpreted as evidence that 20s slicing/market impact were reproduced."
        ),
    }


def _complete_symbol_subset(manifest: dict, *, start: str = TARGET_START, end: str = TARGET_END) -> dict:
    """Return a manifest view containing only symbols verified complete for the target window.

    Safety-critical for partial-not-evidence mode: delegates to provenance.complete_symbol_subset,
    which requires consistent coverage fields (expected==observed, gap_count==0). Never trust a
    bare complete_for_target_window flag. Honors the (possibly overridden) target window so
    partial-mode test windows with different expected bar counts are handled correctly.
    """
    return complete_symbol_subset(manifest, start=start, end=end)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache-dir", default=str(REPO_ROOT / "research_state" / "cache" / "hyperliquid"))
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--capital", type=float, default=100000.0)
    ap.add_argument("--output-prefix", default="campaign_results_real")
    ap.add_argument("--min-symbols", type=int, default=1)
    ap.add_argument("--universe-file", default=None, help="Optional JSON file with verified symbol universe (list or {symbols:[...]}).")
    ap.add_argument("--min-daily-volume-usd", type=float, default=5_000_000.0, help="Minimum 24h USD volume per symbol (>= $5M spec filter)")
    ap.add_argument(
        "--allow-partial-not-evidence",
        action="store_true",
        help=(
            "Run on a verified COMPLETE SUBSET of symbols from an incomplete manifest. "
            "Outputs are explicitly marked NOT_EVIDENCE_PARTIAL_UNIVERSE and NEVER set "
            "performance_evidence=true. Use for pipeline/debug hardening only; NOT spec evidence."
        ),
    )
    ap.add_argument("--window-start", default=None, help="PARTIAL-NOT-EVIDENCE ONLY: override target window start for synthetic pipeline tests; ignored for real evidence runs.")
    ap.add_argument("--window-end", default=None, help="PARTIAL-NOT-EVIDENCE ONLY: override target window end for synthetic pipeline tests; ignored for real evidence runs.")
    args = ap.parse_args()
    cache_dir = Path(args.cache_dir)
    manifest_path = Path(args.manifest) if args.manifest else cache_dir / "provenance.json"
    partial_mode = bool(args.allow_partial_not_evidence)
    spec_min_daily_volume_usd = 5_000_000.0
    if not partial_mode and float(args.min_daily_volume_usd) < spec_min_daily_volume_usd:
        print(
            f"BLOCKER: spec-compliant full-evidence runs require --min-daily-volume-usd >= {spec_min_daily_volume_usd:g} "
            f"(requested {args.min_daily_volume_usd!r}).",
            file=sys.stderr,
        )
        return 2

    target_start = TARGET_START
    target_end = TARGET_END
    if partial_mode and args.window_start and args.window_end:
        target_start = args.window_start
        target_end = args.window_end

    try:
        manifest = require_verified_provenance(
            manifest_path,
            require_complete=not partial_mode,
            min_symbols=args.min_symbols,
            start=target_start,
            end=target_end,
        )
    except ProvenanceError as e:
        if partial_mode:
            # In partial mode, accept a non-fabricated manifest and run only on complete symbols.
            raw = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
            if raw.get("fabricated_data") is True:
                print("BLOCKER: fabricated_data=true is prohibited.", file=sys.stderr)
                return 2
            tw = raw.get("target_window") or {}
            if tw.get("start") and tw.get("end"):
                from src.data.provenance import _parse_iso
                if _parse_iso(tw["start"]) != _parse_iso(target_start) or _parse_iso(tw["end"]) != _parse_iso(target_end):
                    print(f"BLOCKER: target_window mismatch for partial run: {tw} vs expected {target_start}->{target_end}", file=sys.stderr)
                    return 2
            manifest = _complete_symbol_subset(raw, start=target_start, end=target_end)
            if len(manifest.get("symbols") or {}) < args.min_symbols:
                print(str(e), file=sys.stderr)
                print(f"\nBLOCKER: no complete verified symbols available for partial-not-evidence run (need >= {args.min_symbols}).", file=sys.stderr)
                print("Provide verified archive coverage; do NOT fabricate data.", file=sys.stderr)
                return 2
        else:
            print(str(e), file=sys.stderr)
            print(f"\nBLOCKER: Verified 283-day Hyperliquid dataset unavailable for {TARGET_START}→{TARGET_END}.", file=sys.stderr)
            print("Do NOT fabricate data. Provide a verified archive via scripts/fetch_hyperliquid_candles.py --source archive --input-archive <path>.", file=sys.stderr)
            print("For non-evidence pipeline debugging on a verified subset, use --allow-partial-not-evidence with >=1 complete symbol.", file=sys.stderr)
            return 2
    # Optional verified universe filter
    universe_symbols: Optional[List[str]] = None
    if args.universe_file:
        universe_symbols = load_universe(Path(args.universe_file), manifest)
        if not universe_symbols:
            print("BLOCKER: universe file empty or not found.", file=sys.stderr)
            return 2
        # restrict manifest symbols to universe intersection
        syms = manifest.get("symbols") or {}
        filtered = {k: v for k, v in syms.items() if k.upper() in set(universe_symbols)}
        if not filtered:
            print("BLOCKER: no manifest symbols match universe file.", file=sys.stderr)
            return 2
        manifest = dict(manifest)
        manifest["symbols"] = filtered
        manifest["universe_filter"] = {"source": str(Path(args.universe_file)), "symbols": universe_symbols}

    # Per-symbol verified volume-coverage gating (>= $5M 24h USD volume per spec).
    # Applies to the full-evidence path only; partial-not-evidence runs skip strict gating.
    validation_symbols: List[str] = []
    if args.universe_file:
        validation_symbols = universe_symbols
    else:
        validation_symbols = [str(s).upper() for s in (manifest.get("symbols") or {}).keys()]
    if not partial_mode and validation_symbols:
        try:
            passing_symbols = validate_symbol_volume_coverage(manifest, validation_symbols, max(spec_min_daily_volume_usd, float(args.min_daily_volume_usd)))
        except ProvenanceError as e:
            print(str(e), file=sys.stderr)
            print(f"\nBLOCKER: Per-symbol coverage/volume validation failed for {TARGET_START}→{TARGET_END}.", file=sys.stderr)
            print("Provide a verified archive covering all universe symbols with >= $5M 24h volume via scripts/fetch_hyperliquid_candles.py --source archive --input-archive <path>.", file=sys.stderr)
            return 2
    else:
        passing_symbols = validation_symbols

    data = load_verified_cache(cache_dir, manifest)
    # Restrict to symbols that passed coverage + volume validation (full-evidence path).
    if not partial_mode and passing_symbols:
        data = {s: d for s, d in data.items() if s in set(passing_symbols)}
    if not data:
        print("BLOCKER: No verified symbol data passed coverage + volume validation.", file=sys.stderr)
        return 2
    eth = data.get("ETH")
    config = StrategyConfig(
        use_rsi_trigger=True,
        enable_rebound_short=True,
        enable_eth_hedge=True,
        enable_volume_based_sizing=True,
        min_daily_volume_usd=max(spec_min_daily_volume_usd, float(args.min_daily_volume_usd)) if not partial_mode else float(args.min_daily_volume_usd),
    )
    results = run_portfolio_simulation(data, config=config, capital=args.capital,
                                       eth_candles={"ETH": eth} if eth else None)
    metrics = metrics_to_dict(compute_campaign_metrics(trades=results.get("trades", []), equity_curve=results.get("equity_curve")))
    out_dir = REPO_ROOT / "research_state"
    out_dir.mkdir(parents=True, exist_ok=True)
    output_prefix = _normalize_output_prefix(args.output_prefix)
    ts = datetime.now(timezone.utc).isoformat()
    manifest_sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest() if manifest_path.exists() else None
    research_status = "NOT_EVIDENCE_PARTIAL_UNIVERSE" if partial_mode else "REAL_MARKET_RUN"
    run_type = "real_market_campaign_partial_not_evidence" if partial_mode else "real_market_campaign"
    export = {
        "timestamp": ts,
        "run_type": run_type,
        "research_status": research_status,
        "real_market_data": True,
        "performance_evidence": False if partial_mode else True,
        "fabricated_data": False,
        "partial_universe_not_evidence": bool(partial_mode),
        "evidence_warning": (
            "PARTIAL VERIFIED-SUBSET RUN: NOT performance evidence and NOT a spec 283-day campaign result. "
            "Only complete-coverage symbols from the manifest were loaded; universe/coverage is incomplete. "
            "Do not compare to spec targets or cite as campaign performance."
        ) if partial_mode else None,
        "data_provenance": {
            "manifest_path": str(manifest_path.relative_to(REPO_ROOT)) if str(manifest_path).startswith(str(REPO_ROOT)) else str(manifest_path),
            "manifest_sha256": manifest_sha,
            "source": manifest.get("source"),
            "target_window": manifest.get("target_window"),
            "symbols_complete": manifest.get("summary", {}).get("complete_symbols"),
            "symbols_loaded": sorted(data.keys()),
            "coverage_summary": {s: v.get("coverage") for s, v in (manifest.get("symbols") or {}).items() if v.get("status") == "ok"},
            "universe_filter": manifest.get("universe_filter"),
            "universe_filter_policy": {
                "min_daily_volume_usd": config.min_daily_volume_usd,
                "applied_in": ["src.strategy.crash_rebound.filter_universe", "src.data.loader.load_multi_coin_data", "scripts.run_portfolio.run_portfolio_simulation"], "spec_min_daily_volume_usd": 5_000_000.0 if not partial_mode else None,
                "note": "Real-universe membership must be justified by verified per-symbol data/provenance for the target window.",
            },
            "partial_mode": partial_mode,
        },
        "execution_realism": _execution_realism_metadata(config),
        "config": {
            "use_rsi_trigger": config.use_rsi_trigger,
            "rsi_period": config.rsi_period,
            "rsi_threshold": config.rsi_threshold,
            "enable_rebound_short": config.enable_rebound_short,
            "enable_eth_hedge": config.enable_eth_hedge,
            "enable_volume_based_sizing": config.enable_volume_based_sizing,
            "position_size_pct_of_daily_volume": config.position_size_pct_of_daily_volume,
            "min_daily_volume_usd": config.min_daily_volume_usd,
            "gross_cap_pct": config.gross_cap_pct,
            "execution_model": getattr(config, "execution_model", "hourly_bar_simplified"),
            "order_slicing_simulated": bool(getattr(config, "order_slicing_simulated", False)),
            "order_book_impact_model": getattr(config, "order_book_impact_model", "slippage_proxy"),
            "spread_bps_assumed": getattr(config, "spread_bps_assumed", 0.0),
            "slippage_pct": getattr(config, "slippage_pct", None),
            "funding_rate_pct_per_hour": getattr(config, "funding_rate_pct_per_hour", None),
            "enable_liquidation_checks": bool(getattr(config, "enable_liquidation_checks", False)),
        },
        "results": {
            "total_pnl": results.get("total_pnl"),
            "num_trades": results.get("num_trades"),
            "final_open_positions": results.get("final_open_positions"),
            "final_gross_exposure": results.get("final_gross_exposure"),
            "trades": results.get("trades"),
            "equity_curve_points": len(results.get("equity_curve") or []),
        },
        "metrics": metrics,
    }
    (out_dir / f"{output_prefix}.json").write_text(json.dumps(export, indent=2, default=str) + "\n")
    (out_dir / f"{output_prefix}_metrics.json").write_text(json.dumps(metrics, indent=2, default=str) + "\n")
    with (out_dir / f"{output_prefix}_metrics.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["metric", "value"])
        w.writeheader()
        for row in metrics_to_csv_rows(metrics):
            w.writerow(row)
    if partial_mode:
        print(f"PARTIAL NOT-EVIDENCE run complete (performance_evidence=false): {export['results']['num_trades']} trades, total_pnl={export['results']['total_pnl']}, symbols={sorted(data.keys())}")
    else:
        print(f"REAL run complete: {export['results']['num_trades']} trades, total_pnl={export['results']['total_pnl']}")
    print(f"Wrote {out_dir / f'{output_prefix}.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
