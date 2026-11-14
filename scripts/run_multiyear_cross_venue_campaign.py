#!/usr/bin/env python3
"""C6-T1 — multi-year cross-venue campaign (real OKX hourly OHLCV).

WHY THIS EXISTS
---------------
The Hyperliquid public API only retains ~3.9k hourly bars (283-day spec window),
and the operator archive is not present in this environment.  That blocks the
*Hyperliquid-native* verdict, but it does NOT block a *cross-venue* test of the
strategy's temporal edge: OKX serves real, gap-free hourly OHLCV back to 2023
(and earlier).  This runner executes the same real portfolio engine on an
explicitly-labelled, non-Hyperliquid multi-year archive so the power bottleneck
can be attacked with real data instead of handoff churn.

HARD LABELS
-----------
- real_market_data = true
- fabricated_data = false
- is_hyperliquid_venue_data = false
- cross_venue = true
- research_status = CROSS_VENUE_MULTIYEAR_NOT_HYPERLIQUID
- performance_evidence = true (real-market PnL, but NEVER Hyperliquid evidence)

This script never writes to the canonical Hyperliquid latest pointer, never
overwrites an existing artifact stem, and never claims Hyperliquid performance.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.provenance import (  # noqa: E402
    ProvenanceError,
    complete_symbol_subset,
    expected_hourly_bars,
    load_provenance,
    require_verified_provenance,
)
from src.strategy.config import StrategyConfig  # noqa: E402
from src.metrics import (  # noqa: E402
    compute_campaign_metrics,
    metrics_to_csv_rows,
    metrics_to_dict,
)
from scripts.run_portfolio import run_portfolio_simulation  # noqa: E402
from scripts.run_real_campaign import (  # noqa: E402
    _execution_realism_metadata,
    load_verified_cache,
    validate_symbol_volume_coverage,
)

DEFAULT_START = "2023-01-01T00:00:00Z"
DEFAULT_END = "2026-09-28T23:00:00Z"
SPEC_MIN_DAILY_VOLUME_USD = 5_000_000.0


def _normalize_output_prefix(output_prefix: str) -> str:
    raw = str(output_prefix or "").replace("\\", "/").strip()
    while raw.startswith("./"):
        raw = raw[2:]
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


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="Run a REAL multi-year CROSS-VENUE campaign (not Hyperliquid evidence)."
    )
    ap.add_argument("--cache-dir", required=True)
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--universe-file", default=None)
    ap.add_argument("--start", default=DEFAULT_START)
    ap.add_argument("--end", default=DEFAULT_END)
    ap.add_argument("--capital", type=float, default=100_000.0)
    ap.add_argument("--output-prefix", default="campaign_results_real_okx_multiyear")
    ap.add_argument("--min-symbols", type=int, default=1)
    ap.add_argument("--min-daily-volume-usd", type=float, default=SPEC_MIN_DAILY_VOLUME_USD)
    ap.add_argument("--apply-vault-fees", action="store_true", default=False)
    ap.add_argument("--aum-rate-annual", type=float, default=None)
    ap.add_argument("--profit-share-rate", type=float, default=None)
    ap.add_argument("--fee-hours-per-step", type=float, default=None)
    ap.add_argument("--fee-hours-from-timestamps", action="store_true", default=False)
    return ap


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    from src.metrics.vault_fees import fee_config_from_args, VaultFeeConfigError
    try:
        fee_kwargs = fee_config_from_args(args)
    except VaultFeeConfigError as exc:
        print(f"BLOCKER: invalid vault fee config: {exc}", file=sys.stderr)
        return 2

    cache_dir = Path(args.cache_dir)
    manifest_path = Path(args.manifest) if args.manifest else cache_dir / "provenance.json"
    if not manifest_path.exists():
        print(f"BLOCKER: manifest not found: {manifest_path}", file=sys.stderr)
        return 2
    if float(args.min_daily_volume_usd) < SPEC_MIN_DAILY_VOLUME_USD:
        print(
            f"BLOCKER: spec-compliant runs require --min-daily-volume-usd >= {SPEC_MIN_DAILY_VOLUME_USD:g}",
            file=sys.stderr,
        )
        return 2

    start, end = args.start, args.end
    expected = expected_hourly_bars(start, end)

    universe_symbols: Optional[List[str]] = None
    raw_manifest = load_provenance(manifest_path)
    if args.universe_file:
        u = json.loads(Path(args.universe_file).read_text())
        if isinstance(u, dict):
            for key in ("selected_symbols", "symbols"):
                val = u.get(key)
                if isinstance(val, list) and val:
                    universe_symbols = [str(s).upper() for s in val]
                    break
        elif isinstance(u, list):
            universe_symbols = [str(s).upper() for s in u]
        if not universe_symbols:
            print("BLOCKER: universe file empty or invalid.", file=sys.stderr)
            return 2

    try:
        manifest = require_verified_provenance(
            manifest_path,
            require_complete=True,
            min_symbols=args.min_symbols,
            require_spec_volume_floor=SPEC_MIN_DAILY_VOLUME_USD,
            start=start,
            end=end,
            symbols=universe_symbols,
        )
    except ProvenanceError as exc:
        print(str(exc), file=sys.stderr)
        print(
            f"\nBLOCKER: verified multi-year cross-venue dataset unavailable for {start}→{end} "
            f"(expected {expected} hourly bars/symbol).",
            file=sys.stderr,
        )
        return 2

    if universe_symbols:
        syms = manifest.get("symbols") or {}
        filtered = {k: v for k, v in syms.items() if str(k).upper() in set(universe_symbols)}
        if not filtered:
            print("BLOCKER: no manifest symbols match universe file.", file=sys.stderr)
            return 2
        manifest = dict(manifest)
        manifest["symbols"] = filtered
        manifest["universe_filter"] = {
            "source": str(Path(args.universe_file)),
            "symbols": universe_symbols,
        }

    validation_symbols = universe_symbols or [str(s).upper() for s in (manifest.get("symbols") or {}).keys()]
    try:
        passing_symbols = validate_symbol_volume_coverage(
            manifest, validation_symbols, SPEC_MIN_DAILY_VOLUME_USD
        )
    except ProvenanceError as exc:
        print(str(exc), file=sys.stderr)
        print(
            f"\nBLOCKER: per-symbol coverage/volume validation failed for {start}→{end}.",
            file=sys.stderr,
        )
        return 2

    data = load_verified_cache(cache_dir, manifest)
    data = {s: d for s, d in data.items() if s in set(passing_symbols)}
    if not data:
        print("BLOCKER: no verified symbol data passed coverage + volume validation.", file=sys.stderr)
        return 2

    eth = data.get("ETH")
    config = StrategyConfig(
        use_rsi_trigger=True,
        enable_rebound_short=True,
        enable_eth_hedge=True,
        enable_volume_based_sizing=True,
        min_daily_volume_usd=SPEC_MIN_DAILY_VOLUME_USD,
    )
    results = run_portfolio_simulation(
        data,
        config=config,
        capital=args.capital,
        eth_candles={"ETH": eth} if eth else None,
        require_eth_hedge=bool(getattr(config, "enable_eth_hedge", True)),
    )
    metrics = metrics_to_dict(
        compute_campaign_metrics(
            trades=results.get("trades", []),
            equity_curve=results.get("equity_curve"),
            initial_capital=args.capital,
            apply_vault_fees=args.apply_vault_fees,
            fee_use_timestamp_hours=args.fee_hours_from_timestamps,
            **fee_kwargs,
        )
    )

    out_dir = REPO_ROOT / "research_state"
    output_prefix = _normalize_output_prefix(args.output_prefix)
    out_json = out_dir / f"{output_prefix}.json"
    if out_json.exists():
        print(f"BLOCKER: refusing to overwrite existing artifact {out_json}", file=sys.stderr)
        return 2

    manifest_sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    ts = datetime.now(timezone.utc).isoformat()
    export = {
        "timestamp": ts,
        "run_type": "cross_venue_multiyear_campaign",
        "research_status": "CROSS_VENUE_MULTIYEAR_NOT_HYPERLIQUID",
        "real_market_data": True,
        "performance_evidence": True,
        "fabricated_data": False,
        "cross_venue": True,
        "is_hyperliquid_venue_data": False,
        "partial_universe_not_evidence": False,
        "evidence_warning": (
            "REAL OKX exchange data, non-synthetic, but CROSS-VENUE. This is NOT Hyperliquid "
            "performance evidence and must never be relabelled as such. It is a multi-year "
            "cross-venue test of the strategy's temporal edge/power, with venue basis stated."
        ),
        "data_provenance": {
            "manifest_path": str(manifest_path.relative_to(REPO_ROOT))
            if str(manifest_path).startswith(str(REPO_ROOT))
            else str(manifest_path),
            "manifest_sha256": manifest_sha,
            "source": manifest.get("source"),
            "target_window": manifest.get("target_window"),
            "expected_hourly_bars": expected,
            "symbols_complete": sorted((complete_symbol_subset(manifest, start=start, end=end).get("symbols") or {}).keys()),
            "symbols_loaded": sorted(data.keys()),
            "universe_filter": manifest.get("universe_filter"),
            "venue_basis": "okx_public_rest_v5_history_candles",
            "is_hyperliquid_venue_data": False,
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
        },
        "results": {
            "total_pnl": results.get("total_pnl"),
            "num_trades": results.get("num_trades"),
            "final_open_positions": results.get("final_open_positions"),
            "final_gross_exposure": results.get("final_gross_exposure"),
            "trades": results.get("trades"),
            "equity_curve": results.get("equity_curve"),
            "equity_curve_points": len(results.get("equity_curve") or []),
        },
        "metrics": metrics,
    }
    out_json.write_text(json.dumps(export, indent=2, default=str) + "\n")
    (out_dir / f"{output_prefix}_metrics.json").write_text(
        json.dumps(metrics, indent=2, default=str) + "\n"
    )
    with (out_dir / f"{output_prefix}_metrics.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["metric", "value"])
        writer.writeheader()
        for row in metrics_to_csv_rows(metrics):
            writer.writerow(row)

    print(
        f"CROSS-VENUE MULTI-YEAR run complete (NOT Hyperliquid evidence): "
        f"{export['results']['num_trades']} trades, total_pnl={export['results']['total_pnl']}, "
        f"symbols={len(data)}"
    )
    print(f"Wrote {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())