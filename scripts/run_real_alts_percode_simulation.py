#!/usr/bin/env python3
"""Run a REAL-data crash-rebound portfolio simulation across the full OKX altcoin
universe (62 symbols) with the spec point-in-time volume filter applied per
decision bar (via StrategyConfig.min_daily_volume_usd + generate_signal gating).

HONESTY / PROVENANCE
--------------------
This is REAL, non-synthetic exchange data (OKX 1H, full 2025-12-20..2026-09-28
window, verified provenance manifest) run through the REAL strategy engine with
the spec point-in-time (>= $5M trailing-24h USD volume at decision time) filter.

It is NOT labelled `performance_evidence=true` because the campaign runner's
manifest-level volume gate (`volume_filter_ok` = EVERY hourly bar's trailing-24h
volume >= $5M across the WHOLE 283-day window) is NOT satisfied by the alts
(even liquid alts dip below $5M in some hour; only BTC/ETH clear that strict
whole-window-min bar). The simulation's own per-bar point-in-time filter is the
spec's actual universe rule; this script reports that behavior transparently and
does NOT relabel it as spec-provenance evidence.

Outputs: research_state/campaign_results_real_okx_alts_percode.json
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.provenance import load_provenance, verify_cache_sha256, verify_candles_not_synthetic
from src.data.loader import load_hyperliquid_candles
from src.strategy.config import StrategyConfig
from scripts.run_portfolio import run_portfolio_simulation
from src.metrics import compute_campaign_metrics, metrics_to_dict, metrics_to_csv_rows

ALTS_MANIFEST = REPO_ROOT / "research_state/cache/okx_1h_full_20251220_20260928/provenance.json"
ALTS_CACHE = REPO_ROOT / "research_state/cache/okx_1h_full_20251220_20260928"
ETH_MANIFEST = REPO_ROOT / "research_state/cache/okx_smoke/provenance.json"
ETH_CACHE = REPO_ROOT / "research_state/cache/okx_smoke"
OUT = REPO_ROOT / "research_state/campaign_results_real_okx_alts_percode.json"


def load_cache(cache_dir: Path, manifest: dict) -> dict:
    candles_dir = cache_dir / "candles"
    out = {}
    for sym, info in (manifest.get("symbols") or {}).items():
        if info.get("status") != "ok":
            continue
        p = candles_dir / f"{sym}.json"
        if not p.exists():
            mp = info.get("cache_path")
            if mp:
                p = REPO_ROOT / mp
        if not p.exists():
            raise SystemExit(f"Missing cache file for {sym}: {p}")
        verify_cache_sha256(p, info.get("sha256"), sym)
        candles = load_hyperliquid_candles(str(p), symbol=sym, require_verified=True, provenance_info=info)
        verify_candles_not_synthetic(candles, require_synthetic_check=True,
                                     synthetic_check=info.get("synthetic_check"), raise_on_synthetic=True)
        out[sym] = candles
    return out


def main() -> int:
    alts_manifest = load_provenance(str(ALTS_MANIFEST))
    eth_manifest = load_provenance(str(ETH_MANIFEST))

    alts = load_cache(ALTS_CACHE, alts_manifest)
    eth = load_cache(ETH_CACHE, eth_manifest)
    eth_candles = eth.get("ETH")
    if not eth_candles:
        raise SystemExit("ETH candles missing for hedge")

    config = StrategyConfig(
        use_rsi_trigger=True,
        rsi_period=21,
        rsi_threshold=20.0,
        enable_rebound_short=True,
        enable_eth_hedge=True,
        enable_volume_based_sizing=True,
        position_size_pct_of_daily_volume=1.25,
        min_daily_volume_usd=5_000_000.0,
        gross_cap_pct=120.0,
    )
    capital = 100000.0
    results = run_portfolio_simulation(
        alts, config=config, capital=capital,
        eth_candles={"ETH": eth_candles},
        require_eth_hedge=True,
    )
    metrics = metrics_to_dict(compute_campaign_metrics(
        trades=results.get("trades", []),
        equity_curve=results.get("equity_curve"),
        initial_capital=capital,
    ))
    # Checkpoint raw results (incl. non-serializable internals) so compute is never lost.
    import pickle
    ckpt = REPO_ROOT / "research_state" / "cache" / "alts_percode_results.pkl"
    ckpt.parent.mkdir(parents=True, exist_ok=True)
    with ckpt.open("wb") as f:
        pickle.dump({"results": results, "metrics": metrics, "symbols": sorted(alts.keys())}, f)
    print(f"checkpoint: {ckpt.relative_to(REPO_ROOT)}", flush=True)
    ts = datetime.now(timezone.utc).isoformat()
    manifest_sha = hashlib.sha256(ALTS_MANIFEST.read_bytes()).hexdigest()
    # Strip non-JSON-serializable internals (RiskState object, RSI cache) for export.
    results_public = {k: v for k, v in results.items() if k not in ("risk_state", "rsi_cache")}
    export = {
        "timestamp": ts,
        "run_type": "real_market_campaign_alts_percode_simulation",
        "research_status": "REAL_DATA_PERCODE_SIMULATION",
        "real_market_data": True,
        "performance_evidence": False,
        "fabricated_data": False,
        "provenance_note": (
            "REAL, non-synthetic OKX 1H data (full 2025-12-20..2026-09-28 window, 62 alts + ETH), "
            "run through the REAL strategy engine with the spec point-in-time (>= $5M trailing-24h USD "
            "volume at decision time) filter. NOT performance_evidence: the manifest-level strict "
            "volume gate (every hourly bar's trailing-24h >= $5M across the whole window) is not met "
            "by alts (only BTC/ETH clear it). This reports real strategy behavior on real alt data, "
            "not spec-provenance evidence."
        ),
        "data_provenance": {
            "manifest_path": str(ALTS_MANIFEST.relative_to(REPO_ROOT)),
            "manifest_sha256": manifest_sha,
            "alt_symbols": sorted(alts.keys()),
            "eth_source": str(ETH_MANIFEST.relative_to(REPO_ROOT)),
            "target_window": {"start": "2025-12-20T00:00:00Z", "end": "2026-09-28T23:00:00Z"},
        },
        "execution_realism": {
            "model": "hourly_bar_simplified",
            "order_slicing_simulated": False,
            "order_book_impact_model": "slippage_proxy",
            "slippage_pct": 0.0005,
            "funding_rate_pct_per_hour": 0.01,
            "enable_liquidation_checks": True,
            "limitations": [
                "20s order slicing and L2 order-book impact not reproduced (hourly-bar proxy).",
                "Cross-venue (OKX) prices are proxies for Hyperliquid-denominated spec; document basis.",
            ],
        },
        "config": {
            "use_rsi_trigger": True, "rsi_period": 21, "rsi_threshold": 20.0,
            "enable_rebound_short": True, "enable_eth_hedge": True,
            "enable_volume_based_sizing": True, "position_size_pct_of_daily_volume": 1.25,
            "min_daily_volume_usd": 5_000_000.0, "gross_cap_pct": 120.0,
            "execution_model": "hourly_bar_simplified",
        },
        "results": results_public,
        "metrics": metrics,
    }
    OUT.write_text(json.dumps(export, indent=2) + "\n")
    # CSV metrics (flat rows; full series in JSON)
    csv_path = OUT.with_name(OUT.stem + "_metrics.csv")
    import csv
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["metric", "value"])
        w.writeheader()
        for row in metrics_to_csv_rows(metrics):
            w.writerow(row)
    print(json.dumps({
        "out": str(OUT.relative_to(REPO_ROOT)),
        "symbols": len(alts),
        "num_trades": results.get("num_trades"),
        "total_pnl": results.get("total_pnl"),
        "sharpe": metrics.get("sharpe_ratio"),
        "sortino": metrics.get("sortino_ratio"),
        "max_drawdown": metrics.get("max_drawdown"),
        "win_rate": metrics.get("win_rate"),
        "profit_factor": metrics.get("profit_factor"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())