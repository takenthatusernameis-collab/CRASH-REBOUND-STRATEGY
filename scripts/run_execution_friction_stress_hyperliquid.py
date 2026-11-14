#!/usr/bin/env python3
"""C4-T3 — execution-friction stress on the retained exploratory Hyperliquid path.

WHY THIS EXISTS
---------------
The spec-literal exploratory run (`entry_spec_literal_next_open=True`) is the only
path that produced trades on the retained chain, and it produced two. Before any
future agent treats that path as a fragility signal, the fee/slippage/funding/
liquidation/hedge assumptions that produced those two trades must be stress-tested
on the SAME chain. This script does that with the real portfolio engine.

It is NOT a re-run of the exploratory campaign and it is NOT evidence. It changes
no config default, no canonical artifact, and no `hyperliquid_exploratory_next_open_latest.json`
pointer. The retained baseline run is recomputed here only as the comparison
anchor inside this artifact.

LABEL: `NOT_EVIDENCE_EXECUTION_FRICTION`, `performance_evidence=false`,
`canonical_baseline_changed=false`.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.run_portfolio import run_portfolio_simulation  # noqa: E402
from src.data.loader import load_hyperliquid_candles  # noqa: E402
from src.metrics import compute_campaign_metrics, metrics_to_csv_rows, metrics_to_dict  # noqa: E402
from src.strategy.config import StrategyConfig  # noqa: E402

STATE = REPO / "research_state"
DEFAULT_CACHE = STATE / (
    "cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z"
)
LABEL = "NOT_EVIDENCE_EXECUTION_FRICTION"
CAVEAT = (
    "Execution-friction stress on the retained PARTIAL aligned Hyperliquid chain "
    "using the opt-in exploratory spec-literal next-open path. Real fetched candles, "
    "non-synthetic, but NOT the 283-day spec window and NOT performance evidence. "
    "Fragility check only: never promote to evidence, never change the canonical "
    "default, never use for validation or capital allocation."
)

BASE_CONFIG = {
    "slippage_pct": 0.0005,
    "commission_min": 1.0,
    "funding_rate_pct_per_hour": 0.01,
    "liquidation_maint_margin_pct": 5.0,
    "liquidation_buffer_pct": 1.0,
    "liquidation_penalty_pct": 0.5,
    "enable_eth_hedge": True,
}

VARIANTS: Dict[str, Dict[str, Any]] = {
    "baseline": {},
    "slippage_2x": {"slippage_pct": 0.0010},
    "slippage_4x": {"slippage_pct": 0.0020},
    "slippage_10x": {"slippage_pct": 0.0050},
    "fee_min_10x": {"commission_min": 10.0},
    "funding_3x": {"funding_rate_pct_per_hour": 0.03},
    "liquidation_stress": {
        "liquidation_maint_margin_pct": 10.0,
        "liquidation_buffer_pct": 0.5,
        "liquidation_penalty_pct": 1.5,
    },
    "no_eth_hedge": {"enable_eth_hedge": False},
    "combined_stress": {
        "slippage_pct": 0.0020,
        "commission_min": 10.0,
        "funding_rate_pct_per_hour": 0.03,
        "liquidation_maint_margin_pct": 10.0,
        "liquidation_buffer_pct": 0.5,
        "liquidation_penalty_pct": 1.5,
    },
}


def load_chain(cache: Path) -> Dict[str, List[Dict[str, Any]]]:
    candles_dir = cache / "candles"
    if not candles_dir.exists():
        raise SystemExit(f"BLOCKER: candles dir missing: {candles_dir}")
    manifest_path = cache / "provenance.json"
    if not manifest_path.exists():
        raise SystemExit(f"BLOCKER: manifest missing: {manifest_path}")
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("fabricated_data") is True:
        raise SystemExit("BLOCKER: fabricated_data=true is prohibited.")
    symbols = sorted(p.stem for p in candles_dir.glob("*.json"))
    if not symbols:
        raise SystemExit("BLOCKER: no symbol candle files.")
    data: Dict[str, List[Dict[str, Any]]] = {}
    for sym in symbols:
        info = (manifest.get("symbols") or {}).get(sym) or {}
        path = candles_dir / f"{sym}.json"
        expected = info.get("sha256")
        if expected:
            got = hashlib.sha256(path.read_bytes()).hexdigest()
            if got != expected:
                raise SystemExit(f"BLOCKER: sha256 mismatch for {sym}")
        data[sym] = load_hyperliquid_candles(str(path), symbol=sym)
    if "ETH" not in data:
        raise SystemExit("BLOCKER: retained chain has no ETH candles.")
    return data


def run_variant(data: Dict[str, List[Dict[str, Any]]], overrides: Dict[str, Any],
                capital: float, min_volume: float) -> Dict[str, Any]:
    params = {**BASE_CONFIG, **overrides}
    cfg = StrategyConfig(
        use_rsi_trigger=True,
        enable_rebound_short=True,
        enable_volume_based_sizing=True,
        min_daily_volume_usd=min_volume,
        entry_spec_literal_next_open=True,
        **params,
    )
    results = run_portfolio_simulation(
        data, config=cfg, capital=capital,
        eth_candles={"ETH": data["ETH"]},
        require_eth_hedge=bool(params["enable_eth_hedge"]),
    )
    metrics = metrics_to_dict(compute_campaign_metrics(
        trades=results.get("trades", []),
        equity_curve=results.get("equity_curve"),
        initial_capital=capital,
    ))
    return {
        "config": params,
        "num_trades": int(results.get("num_trades") or 0),
        "total_pnl": float(results.get("total_pnl") or 0.0),
        "final_open_positions": results.get("final_open_positions"),
        "metrics": metrics,
        "trades": results.get("trades", []),
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache-dir", default=str(DEFAULT_CACHE))
    ap.add_argument("--capital", type=float, default=100_000.0)
    ap.add_argument("--min-daily-volume-usd", type=float, default=5_000_000.0)
    ap.add_argument("--variants", default="all",
                    help="comma-separated variant names, or 'all'")
    args = ap.parse_args(argv)

    cache = Path(args.cache_dir)
    if not cache.is_absolute():
        cache = (REPO / cache).resolve()
    data = load_chain(cache)

    names = list(VARIANTS) if args.variants == "all" else [
        v.strip() for v in args.variants.split(",") if v.strip()]
    unknown = [n for n in names if n not in VARIANTS]
    if unknown:
        print(f"BLOCKER: unknown variants: {unknown}", file=sys.stderr)
        return 2

    runs: List[Dict[str, Any]] = []
    for name in names:
        res = run_variant(data, VARIANTS[name], args.capital, args.min_daily_volume_usd)
        res["variant"] = name
        res["overrides"] = VARIANTS[name]
        runs.append(res)
        print(f"{name}: trades={res['num_trades']} pnl={res['total_pnl']:.4f}")

    by_name = {r["variant"]: r for r in runs}
    baseline = by_name.get("baseline")
    if baseline is None and names:
        baseline = run_variant(data, {}, args.capital, args.min_daily_volume_usd)
        baseline["variant"] = "baseline"
        baseline["overrides"] = {}
        runs.insert(0, baseline)
        by_name["baseline"] = baseline
        print(f"baseline: trades={baseline['num_trades']} pnl={baseline['total_pnl']:.4f}")

    pnls = [r["total_pnl"] for r in runs]
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    payload = {
        "schema_version": 1,
        "generated_at_utc": iso,
        "run_type": "execution_friction_stress_hyperliquid",
        "label": LABEL,
        "real_market_data": True,
        "performance_evidence": False,
        "canonical_baseline_changed": False,
        "provenance_caveat": CAVEAT,
        "cache_dir": str(cache.relative_to(REPO)) if str(cache).startswith(str(REPO)) else str(cache),
        "entry_rule": "spec-literal next hourly open after RSI(21)<20; opt-in flag only",
        "capital": args.capital,
        "min_daily_volume_usd": args.min_daily_volume_usd,
        "baseline_config": BASE_CONFIG,
        "variants": [
            {
                "variant": r["variant"],
                "overrides": r["overrides"],
                "config": r["config"],
                "num_trades": r["num_trades"],
                "total_pnl": r["total_pnl"],
                "delta_pnl_vs_baseline": (
                    r["total_pnl"] - baseline["total_pnl"] if baseline else None
                ),
                "max_drawdown": r["metrics"].get("max_drawdown"),
                "win_rate": r["metrics"].get("win_rate"),
                "sharpe_ratio": r["metrics"].get("sharpe_ratio"),
                "trades": r["trades"],
            }
            for r in runs
        ],
        "summary": {
            "variant_count": len(runs),
            "baseline_trades": baseline["num_trades"] if baseline else None,
            "baseline_total_pnl": baseline["total_pnl"] if baseline else None,
            "all_variants_negative_total_pnl": all(p < 0 for p in pnls),
            "min_total_pnl": min(pnls),
            "max_total_pnl": max(pnls),
            "pnl_range": [min(pnls), max(pnls)],
            "trade_count_range": [min(r["num_trades"] for r in runs),
                                  max(r["num_trades"] for r in runs)],
        },
        "interpretation": (
            "Execution friction is a fragility check on a 2-trade exploratory path, "
            "not an estimate of live performance. The retained window has 4 crash "
            "days; no friction grid can make it evidence."
        ),
        "no_new_data_fabricated": True,
    }

    STATE.mkdir(parents=True, exist_ok=True)
    out_json = STATE / f"execution_friction_stress_hyperliquid_{ts}.json"
    out_json.write_text(json.dumps(payload, indent=2, default=str) + "\n")
    out_csv = STATE / f"execution_friction_stress_hyperliquid_{ts}.csv"
    with out_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["variant", "num_trades", "total_pnl", "delta_pnl_vs_baseline",
                    "max_drawdown", "win_rate", "sharpe_ratio"])
        for item in payload["variants"]:
            w.writerow([item["variant"], item["num_trades"], item["total_pnl"],
                        item["delta_pnl_vs_baseline"], item["max_drawdown"],
                        item["win_rate"], item["sharpe_ratio"]])

    lines = [
        f"# Execution-Friction Stress (Hyperliquid, retained chain) — {iso}",
        "",
        f"**Label:** `{LABEL}` — `performance_evidence=false`, "
        "`canonical_baseline_changed=false`.",
        "",
        f"Chain: `{payload['cache_dir']}` · capital ${args.capital:,.0f} · "
        f"trailing-24h floor ${args.min_daily_volume_usd:,.0f}",
        "",
        "| Variant | Trades | Total PnL | Δ vs baseline | Max DD | Win rate |",
        "|---|---|---|---|---|---|",
    ]
    for item in payload["variants"]:
        dd = item["max_drawdown"]
        wr = item["win_rate"]
        lines.append(
            f"| `{item['variant']}` | {item['num_trades']} | {item['total_pnl']:.4f} | "
            f"{item['delta_pnl_vs_baseline']:.4f} | "
            f"{dd:.4f} | {wr:.4f} |"
        )
    lines += [
        "",
        f"**Range:** total PnL {min(pnls):.4f} .. {max(pnls):.4f}; "
        f"all variants negative: {payload['summary']['all_variants_negative_total_pnl']}.",
        "",
        "## Caveats",
        "",
        f"- {CAVEAT}",
        "- Hourly bar simulation only: 20s order slicing and L2 book impact are NOT modeled.",
        "- The no-ETH-hedge variant is a structural fragility probe, not a spec configuration.",
        "",
    ]
    out_md = STATE / f"execution_friction_stress_hyperliquid_{ts}.md"
    out_md.write_text("\n".join(lines) + "\n")

    print(f"summary={json.dumps(payload['summary'])}")
    print(f"wrote {out_json}")
    print(f"wrote {out_csv}")
    print(f"wrote {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())