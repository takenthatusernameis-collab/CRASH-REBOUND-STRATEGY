#!/usr/bin/env python3
"""Exploratory spec-literal next-open adjudication on the retained Hyperliquid chain.

WHY THIS EXISTS
---------------
`research_state/strategy_spec.md` defines the crash trigger as "21-hour RSI closes
below 20" and the entry as "Buy at next hourly open". The canonical implementation
additionally requires a same-bar `confirm_rebound` candle before `generate_signal`
returns a signal. On the retained aligned Hyperliquid chain that extra gate blocks
every volume-passing crash hour, producing a structural 0-trade funnel. The
canonical path is correct-by-default and is NOT changed here.

This harness runs the REAL portfolio engine with the opt-in
`entry_spec_literal_next_open=True` flag, which bypasses ONLY the same-bar
rebound confirmation. Fees, funding, slippage, the trailing-24h >= $5M volume
floor, regime/price floor, 1.25%-of-volume sizing, the 120% gross cap, one
position per coin, ETH hedge and liquidation checks are unchanged.

OUTPUT IS EXPLORATORY: `NOT_EVIDENCE_EXPLORATORY_FANOUT`,
`performance_evidence=false`. The retained window is a PARTIAL window with only a
handful of independent crash episodes; this is never Hyperliquid performance
evidence and never a validation or capital-allocation result.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.build_crash_event_census import _rsi_series  # noqa: E402
from scripts.run_portfolio import run_portfolio_simulation  # noqa: E402
from src.data.loader import load_hyperliquid_candles  # noqa: E402
from src.metrics import (  # noqa: E402
    compute_campaign_metrics,
    metrics_to_csv_rows,
    metrics_to_dict,
)
from src.strategy.config import StrategyConfig  # noqa: E402
from src.strategy.crash_rebound import (  # noqa: E402
    _close,
    _volume,
    confirm_rebound,
    generate_signal,
)

LABEL = "NOT_EVIDENCE_EXPLORATORY_FANOUT"
CAVEAT = (
    "Exploratory spec-literal next-open adjudication on the retained PARTIAL aligned "
    "Hyperliquid chain; real fetched candles, non-synthetic; NOT the 283-day spec "
    "window and NOT performance evidence. Never use for validation or capital "
    "allocation. Canonical baseline is unchanged."
)


def load_candles(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text())
    if isinstance(data, dict):
        data = data.get("candles", data)
    return data


def rolling_volume_24h(candles: List[Dict[str, Any]]) -> List[Optional[float]]:
    prefix = [0.0]
    for c in candles:
        v = _volume(c)
        close = _close(c)
        if v is not None and close is not None and close > 0:
            prefix.append(prefix[-1] + float(v) * float(close))
        else:
            prefix.append(prefix[-1])
    out: List[Optional[float]] = []
    for i in range(len(candles)):
        start = max(0, i + 1 - 24)
        out.append(prefix[i + 1] - prefix[start])
    return out


def build_funnel(candles_by_symbol: Dict[str, List[Dict[str, Any]]],
                 cfg: StrategyConfig) -> Dict[str, Any]:
    """Count the funnel on real bars. Signal counts use the real generator."""
    totals = {
        "symbols": len(candles_by_symbol),
        "bars_total": sum(len(c) for c in candles_by_symbol.values()),
        "rsi_crash_hours_no_volume_gate": 0,
        "rsi_crash_hours_passing_trailing_24h_5m_volume": 0,
        "same_bar_rebound_confirm_implementation": 0,
        "next_bar_rebound_confirm_implementation": 0,
        "generate_signal_canonical_same_bar_confirm": 0,
        "generate_signal_spec_literal_next_open": 0,
    }
    per_symbol: Dict[str, Dict[str, int]] = {}
    for symbol, candles in sorted(candles_by_symbol.items()):
        closes = []
        for c in candles:
            close = _close(c)
            if close is None:
                raise ValueError(f"{symbol}: bar without close; refusing to misalign RSI")
            closes.append(float(close))
        rsis = _rsi_series(closes, cfg.rsi_period)
        vols = rolling_volume_24h(candles)
        memo: Dict[Any, Any] = {}
        counts = {k: 0 for k in totals if k not in ("symbols", "bars_total")}
        for i in range(len(candles)):
            rsi = rsis[i]
            if rsi is None or rsi >= cfg.rsi_threshold:
                continue
            counts["rsi_crash_hours_no_volume_gate"] += 1
            vol = vols[i]
            if vol is None or vol < cfg.min_daily_volume_usd:
                continue
            counts["rsi_crash_hours_passing_trailing_24h_5m_volume"] += 1
            prefix = candles[: i + 1]
            if confirm_rebound(prefix, lookback=cfg.rebound_lookback,
                               min_body_ratio=cfg.rebound_min_body_ratio):
                counts["same_bar_rebound_confirm_implementation"] += 1
            if i + 1 < len(candles) and confirm_rebound(
                candles[: i + 2], lookback=cfg.rebound_lookback,
                min_body_ratio=cfg.rebound_min_body_ratio,
            ):
                counts["next_bar_rebound_confirm_implementation"] += 1
            canonical_cfg = StrategyConfig(**{**cfg.__dict__, "entry_spec_literal_next_open": False})
            if generate_signal(prefix, symbol=symbol, config=canonical_cfg, cache=memo) is not None:
                counts["generate_signal_canonical_same_bar_confirm"] += 1
            if generate_signal(prefix, symbol=symbol, config=cfg, cache=memo) is not None:
                counts["generate_signal_spec_literal_next_open"] += 1
        per_symbol[symbol] = counts
        for k, v in counts.items():
            totals[k] += v
    return {"totals": totals, "per_symbol": per_symbol}


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache-dir", required=True, help="Aligned complete cache dir containing candles/")
    ap.add_argument("--manifest", default=None, help="Provenance manifest (default: <cache-dir>/provenance.json)")
    ap.add_argument("--capital", type=float, default=100000.0)
    ap.add_argument("--min-daily-volume-usd", type=float, default=5_000_000.0)
    ap.add_argument("--output-prefix", default=None,
                    help="Default: campaign_results_real_hyperliquid_exploratory_next_open_<TS>")
    ap.add_argument("--out-dir", default="research_state",
                    help="Artifact directory; use a temp dir for dry runs so the canonical latest pointer is never overwritten")
    ap.add_argument("--skip-funnel", action="store_true", help="Skip the (slow) funnel recount")
    args = ap.parse_args(argv)

    cache = Path(args.cache_dir)
    if not cache.is_absolute():
        cache = (REPO_ROOT / cache).resolve()
    candles_dir = cache / "candles"
    if not candles_dir.exists():
        print(f"BLOCKER: candles dir missing: {candles_dir}", file=sys.stderr)
        return 2
    manifest_path = Path(args.manifest) if args.manifest else cache / "provenance.json"
    if not manifest_path.exists():
        print(f"BLOCKER: manifest missing: {manifest_path}", file=sys.stderr)
        return 2
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("fabricated_data") is True:
        print("BLOCKER: fabricated_data=true is prohibited.", file=sys.stderr)
        return 2

    symbols = sorted(p.stem for p in candles_dir.glob("*.json"))
    if not symbols:
        print("BLOCKER: no symbol candle files.", file=sys.stderr)
        return 2

    data: Dict[str, List[Dict[str, Any]]] = {}
    for sym in symbols:
        info = (manifest.get("symbols") or {}).get(sym) or {}
        expected_sha = info.get("sha256")
        path = candles_dir / f"{sym}.json"
        if expected_sha:
            got = hashlib.sha256(path.read_bytes()).hexdigest()
            if got != expected_sha:
                print(f"BLOCKER: sha256 mismatch for {sym}: {got} != {expected_sha}", file=sys.stderr)
                return 2
        data[sym] = load_hyperliquid_candles(str(path), symbol=sym)

    eth = data.get("ETH")
    if eth is None:
        print("BLOCKER: retained chain has no ETH candles; ETH hedge cannot be verified.", file=sys.stderr)
        return 2

    cfg = StrategyConfig(
        use_rsi_trigger=True,
        enable_rebound_short=True,
        enable_eth_hedge=True,
        enable_volume_based_sizing=True,
        min_daily_volume_usd=float(args.min_daily_volume_usd),
        entry_spec_literal_next_open=True,
    )

    funnel = None if args.skip_funnel else build_funnel(data, cfg)

    results = run_portfolio_simulation(
        data, config=cfg, capital=args.capital,
        eth_candles={"ETH": eth}, require_eth_hedge=True,
    )
    metrics = metrics_to_dict(compute_campaign_metrics(
        trades=results.get("trades", []),
        equity_curve=results.get("equity_curve"),
        initial_capital=args.capital,
    ))

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (REPO_ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = args.output_prefix or f"campaign_results_real_hyperliquid_exploratory_next_open_{ts}"

    num_trades = int(results.get("num_trades") or 0)
    total_pnl = float(results.get("total_pnl") or 0.0)
    export = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "run_type": "real_market_campaign_exploratory_spec_literal_next_open",
        "label": LABEL,
        "research_status": LABEL,
        "real_market_data": True,
        "performance_evidence": False,
        "fabricated_data": False,
        "partial_universe_not_evidence": True,
        "canonical_baseline_changed": False,
        "provenance_caveat": CAVEAT,
        "config": {
            "use_rsi_trigger": cfg.use_rsi_trigger,
            "rsi_period": cfg.rsi_period,
            "rsi_threshold": cfg.rsi_threshold,
            "entry_next_bar": cfg.entry_next_bar,
            "entry_spec_literal_next_open": cfg.entry_spec_literal_next_open,
            "enable_rebound_short": cfg.enable_rebound_short,
            "enable_eth_hedge": cfg.enable_eth_hedge,
            "enable_volume_based_sizing": cfg.enable_volume_based_sizing,
            "position_size_pct_of_daily_volume": cfg.position_size_pct_of_daily_volume,
            "min_daily_volume_usd": cfg.min_daily_volume_usd,
            "gross_cap_pct": cfg.gross_cap_pct,
            "slippage_pct": cfg.slippage_pct,
            "funding_rate_pct_per_hour": cfg.funding_rate_pct_per_hour,
            "enable_liquidation_checks": cfg.enable_liquidation_checks,
        },
        "data_provenance": {
            "manifest_path": str(manifest_path.relative_to(REPO_ROOT))
            if str(manifest_path).startswith(str(REPO_ROOT)) else str(manifest_path),
            "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            "source": manifest.get("source"),
            "target_window": manifest.get("target_window"),
            "symbols_loaded": sorted(data.keys()),
        },
        "funnel": funnel,
        "results": {
            "num_trades": num_trades,
            "total_pnl": total_pnl,
            "final_open_positions": results.get("final_open_positions"),
            "final_gross_exposure": results.get("final_gross_exposure"),
            "trades": results.get("trades"),
            "equity_curve_points": len(results.get("equity_curve") or []),
        },
        "metrics": metrics,
    }
    (out_dir / f"{prefix}.json").write_text(json.dumps(export, indent=2, default=str) + "\n")
    (out_dir / f"{prefix}_metrics.json").write_text(json.dumps(metrics, indent=2, default=str) + "\n")
    # Durable "latest" pointer consumed by the session gate. This is the same
    # payload, not a second campaign: it is overwritten by each exploratory run.
    (out_dir / "hyperliquid_exploratory_next_open_latest.json").write_text(
        json.dumps(export, indent=2, default=str) + "\n")
    with (out_dir / f"{prefix}_metrics.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["metric", "value"])
        w.writeheader()
        for row in metrics_to_csv_rows(metrics):
            w.writerow(row)

    funnel_path = None
    if funnel is not None:
        funnel_path = out_dir / f"hyperliquid_signal_funnel_exploratory_next_open_{ts}.json"
        funnel_md = out_dir / f"hyperliquid_signal_funnel_exploratory_next_open_{ts}.md"
        payload = {
            "schema_version": 1,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "run_type": "hyperliquid_signal_funnel_exploratory_next_open_real_engine",
            "label": LABEL,
            "real_market_data": True,
            "performance_evidence": False,
            "canonical_baseline_changed": False,
            "cache_dir": str(cache.relative_to(REPO_ROOT)) if str(cache).startswith(str(REPO_ROOT)) else str(cache),
            "provenance_caveat": CAVEAT,
            "counts": funnel["totals"],
            "per_symbol": funnel["per_symbol"],
            "campaign_artifact": str((out_dir / f"{prefix}.json").relative_to(REPO_ROOT)),
            "campaign_num_trades": num_trades,
            "campaign_total_pnl": total_pnl,
        }
        funnel_path.write_text(json.dumps(payload, indent=2) + "\n")
        t = funnel["totals"]
        funnel_md.write_text(
            "# Hyperliquid signal funnel — spec-literal next-open (EXPLORATORY, NOT EVIDENCE)\n\n"
            f"Generated (UTC): {payload['generated_at_utc']}\n\n"
            f"Label: `{LABEL}` — performance_evidence=false. {CAVEAT}\n\n"
            "| Stage | Count |\n|---|---|\n"
            f"| Symbols | {t['symbols']} |\n"
            f"| Bars | {t['bars_total']} |\n"
            f"| RSI(21)<20 hours | {t['rsi_crash_hours_no_volume_gate']} |\n"
            f"| …passing trailing-24h >= $5M volume | {t['rsi_crash_hours_passing_trailing_24h_5m_volume']} |\n"
            f"| …same-bar rebound confirm (canonical gate) | {t['same_bar_rebound_confirm_implementation']} |\n"
            f"| …next-bar rebound confirm | {t['next_bar_rebound_confirm_implementation']} |\n"
            f"| generate_signal canonical (same-bar confirm) | {t['generate_signal_canonical_same_bar_confirm']} |\n"
            f"| generate_signal spec-literal next-open | {t['generate_signal_spec_literal_next_open']} |\n"
            f"| Real-engine trades (spec-literal path) | {num_trades} |\n"
            f"| Real-engine total PnL | {total_pnl} |\n\n"
            "The structural 0-trade canonical result is explained by the same-bar "
            "confirmation gate, which the spec does not require.\n"
        )

    print(f"EXPLORATORY {LABEL}: {num_trades} trades, total_pnl={total_pnl}, symbols={len(data)}")
    print(f"Wrote {out_dir / f'{prefix}.json'}")
    if funnel_path is not None:
        print(f"Wrote {funnel_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())