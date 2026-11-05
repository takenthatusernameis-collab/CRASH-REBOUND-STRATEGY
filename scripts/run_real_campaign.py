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

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.provenance import require_verified_provenance, ProvenanceError, TARGET_START, TARGET_END  # noqa: E402
from src.data.loader import load_hyperliquid_candles  # noqa: E402
from src.strategy.config import StrategyConfig  # noqa: E402
from scripts.run_portfolio import run_portfolio_simulation  # noqa: E402
from src.metrics import compute_campaign_metrics, metrics_to_dict, metrics_to_csv_rows  # noqa: E402


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
        out[sym] = load_hyperliquid_candles(str(p), symbol=sym)
    if not out:
        raise ProvenanceError("No complete verified symbol caches loaded")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache-dir", default=str(REPO_ROOT / "research_state" / "cache" / "hyperliquid"))
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--capital", type=float, default=100000.0)
    ap.add_argument("--output-prefix", default="campaign_results_real")
    ap.add_argument("--min-symbols", type=int, default=1)
    ap.add_argument("--universe-file", default=None, help="Optional JSON file with verified symbol universe (list or {symbols:[...]}).")
    args = ap.parse_args()
    cache_dir = Path(args.cache_dir)
    manifest_path = Path(args.manifest) if args.manifest else cache_dir / "provenance.json"

    try:
        manifest = require_verified_provenance(manifest_path, require_complete=True, min_symbols=args.min_symbols)
    except ProvenanceError as e:
        print(str(e), file=sys.stderr)
        print(f"\nBLOCKER: Verified 283-day Hyperliquid dataset unavailable for {TARGET_START}→{TARGET_END}.", file=sys.stderr)
        print("Do NOT fabricate data. Provide a verified archive via scripts/fetch_hyperliquid_candles.py --source archive --input-archive <path>.", file=sys.stderr)
        return 2
    # Optional verified universe filter
    universe_symbols = None
    if args.universe_file:
        up = Path(args.universe_file)
        if not up.exists():
            print(f"BLOCKER: universe file not found: {up}", file=sys.stderr)
            return 2
        raw = json.loads(up.read_text())
        if isinstance(raw, dict):
            universe_symbols = raw.get("symbols") or raw.get("universe") or []
        else:
            universe_symbols = raw
        universe_symbols = [str(s).upper() for s in universe_symbols]
        # restrict manifest symbols to universe intersection
        syms = manifest.get("symbols") or {}
        filtered = {k: v for k, v in syms.items() if k.upper() in universe_symbols}
        if not filtered:
            print("BLOCKER: no manifest symbols match universe file.", file=sys.stderr)
            return 2
        manifest = dict(manifest)
        manifest["symbols"] = filtered
        manifest["universe_filter"] = {"source": str(up), "symbols": universe_symbols}

    data = load_verified_cache(cache_dir, manifest)
    eth = data.get("ETH")
    config = StrategyConfig(
        use_rsi_trigger=True,
        enable_rebound_short=True,
        enable_eth_hedge=True,
        enable_volume_based_sizing=True,
        min_daily_volume_usd=5_000_000.0,
    )
    results = run_portfolio_simulation(data, config=config, capital=args.capital,
                                       eth_candles={"ETH": eth} if eth else None)
    metrics = metrics_to_dict(compute_campaign_metrics(trades=results.get("trades", []), equity_curve=results.get("equity_curve")))
    out_dir = REPO_ROOT / "research_state"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()
    manifest_sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest() if manifest_path.exists() else None
    export = {
        "timestamp": ts,
        "run_type": "real_market_campaign",
        "research_status": "REAL_MARKET_RUN",
        "real_market_data": True,
        "performance_evidence": True,
        "fabricated_data": False,
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
                "applied_in": ["src.strategy.crash_rebound.filter_universe", "scripts.run_portfolio.run_portfolio_simulation"],
                "note": "Real-universe membership must be justified by verified per-symbol data/provenance for the target window.",
            },
        },
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
    (out_dir / f"{args.output_prefix}.json").write_text(json.dumps(export, indent=2, default=str) + "\n")
    # Also write canonical metrics files for real run (separate naming to avoid overwriting fixture smoke by accident?)
    # The handoff asks for campaign_metrics.json/.csv marked real; keep fixture separate via explicit name.
    (out_dir / f"{args.output_prefix}_metrics.json").write_text(json.dumps(metrics, indent=2, default=str) + "\n")
    with (out_dir / f"{args.output_prefix}_metrics.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["metric", "value"])
        w.writeheader()
        for row in metrics_to_csv_rows(metrics):
            w.writerow(row)
    print(f"REAL run complete: {export['results']['num_trades']} trades, total_pnl={export['results']['total_pnl']}")
    print(f"Wrote {out_dir / f'{args.output_prefix}.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
