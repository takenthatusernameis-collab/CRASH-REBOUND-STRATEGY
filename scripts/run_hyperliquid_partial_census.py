#!/usr/bin/env python3
"""Cross-sectional RSI(21)<20 crash census for the partial Hyperliquid API window.

The partial window is NOT the 283-day spec window and is NOT performance evidence.
It exists to quantify how many crash events and confirmed rebound signals the
maximum public-API window contains, so future sessions cannot claim "data was
unavailable" without a reproducible count.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from src.strategy.config import StrategyConfig  # noqa: E402
from src.strategy.crash_rebound import detect_crash_rsi, generate_signal  # noqa: E402

DEFAULT_CACHE = REPO / "research_state/cache/hyperliquid_partial_20260419_20260928"
DEFAULT_OUT = REPO / "research_state/hyperliquid_partial_crash_census_20260419_20260928.json"
DEFAULT_SYMBOLS = ["ADA", "ALGO", "ARB", "ATOM", "AVAX", "BTC", "ETH", "LTC", "NEAR", "OP", "SOL", "TIA"]
CAVEAT = (
    "Real Hyperliquid public API candles, non-synthetic; PARTIAL window "
    "2026-04-19T12:00Z..2026-09-28T23:00Z; NOT the 283-day spec window and "
    "NOT performance evidence."
)


def load_candles(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text())
    if isinstance(data, dict):
        data = data.get("candles", data)
    return data


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache-dir", default=str(DEFAULT_CACHE))
    ap.add_argument("--output", default=str(DEFAULT_OUT))
    ap.add_argument("--symbols", nargs="*", default=DEFAULT_SYMBOLS)
    args = ap.parse_args(argv)

    cache = Path(args.cache_dir) / "candles"
    cfg = StrategyConfig(
        use_rsi_trigger=True,
        enable_rebound_short=True,
        enable_eth_hedge=True,
        enable_volume_based_sizing=True,
        min_daily_volume_usd=5_000_000.0,
    )
    out: Dict[str, Any] = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_type": "hyperliquid_partial_crash_census",
        "provenance_caveat": CAVEAT,
        "target_window": {
            "start": "2026-04-19T12:00:00+00:00",
            "end": "2026-09-28T23:00:00+00:00",
            "expected_hourly_bars": 3900,
        },
        "config": {
            "rsi_period": cfg.rsi_period,
            "rsi_threshold": cfg.rsi_threshold,
            "min_daily_volume_usd": cfg.min_daily_volume_usd,
        },
        "symbols": {},
    }
    for sym in args.symbols:
        path = cache / f"{sym}.json"
        if not path.exists():
            out["symbols"][sym] = {"error": f"missing cache: {path}"}
            continue
        candles = load_candles(path)
        memo: Dict[Any, Any] = {}
        crashes = []
        signals = []
        for i in range(len(candles)):
            prefix = candles[: i + 1]
            if detect_crash_rsi(
                prefix,
                rsi_period=cfg.rsi_period,
                rsi_threshold=cfg.rsi_threshold,
                min_daily_volume_usd=cfg.min_daily_volume_usd,
                cache=memo,
            ):
                crashes.append(prefix[-1].get("timestamp"))
            sig = generate_signal(prefix, symbol=sym, config=cfg, cache=memo)
            if sig is not None:
                signals.append({"timestamp": sig.timestamp, "side": sig.side, "entry_price": sig.entry_price})
        out["symbols"][sym] = {
            "bars": len(candles),
            "rsi_crash_events": len(crashes),
            "confirmed_signals": len(signals),
            "crash_timestamps": crashes,
            "signal_timestamps": [s["timestamp"] for s in signals],
        }
    out["totals"] = {
        "symbols": len(args.symbols),
        "bars": sum(v.get("bars", 0) for v in out["symbols"].values()),
        "rsi_crash_events": sum(v.get("rsi_crash_events", 0) for v in out["symbols"].values()),
        "confirmed_signals": sum(v.get("confirmed_signals", 0) for v in out["symbols"].values()),
    }
    Path(args.output).write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out["totals"], indent=2))
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())