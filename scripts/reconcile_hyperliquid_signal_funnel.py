#!/usr/bin/env python3
"""Reconcile the Hyperliquid partial-window signal funnel: crash -> confirmation -> trade.

WHY THIS EXISTS
---------------
The partial Hyperliquid window produces ``rsi_crash_events > 0`` but
``confirmed_signals == 0``. Without a funnel breakdown that is indistinguishable
from a silent scanner bug, and every later session re-litigates it. This script
quantifies each stage on a real aligned complete cache slice:

  RSI(21) < 20 hours
    -> hours that also pass the trailing-24h >= $5M volume floor
    -> hours whose SAME bar has a bullish rebound confirmation candle
       (``confirm_rebound``; the implementation requires this before entry)
    -> hours whose NEXT bar has a rebound confirmation candle
    -> hours for which the full spec signal generator returns a signal

The output is descriptive only. It is PARTIAL window, NOT the 283-day spec
window and NOT performance evidence. It never fabricates bars and never changes
the canonical baseline.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.build_crash_event_census import _rsi_series  # noqa: E402
from src.strategy.config import StrategyConfig  # noqa: E402
from src.strategy.crash_rebound import (  # noqa: E402
    _close,
    _volume,
    confirm_rebound,
    generate_signal,
)

CAVEAT = (
    "Real Hyperliquid public-API candles, non-synthetic; PARTIAL aligned window; "
    "NOT the 283-day spec window and NOT performance evidence."
)


def load_candles(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text())
    if isinstance(data, dict):
        data = data.get("candles", data)
    return data


def rolling_volume_24h(candles: List[Dict[str, Any]]) -> List[Optional[float]]:
    """Trailing-24h quote volume, matching ``_daily_volume_usd`` (volume * close)."""
    prefix = [0.0]
    valid = [0]
    for c in candles:
        v = _volume(c)
        close = _close(c)
        if v is not None and close is not None and close > 0:
            prefix.append(prefix[-1] + v * close)
            valid.append(valid[-1] + 1)
        else:
            prefix.append(prefix[-1])
            valid.append(valid[-1])
    out: List[Optional[float]] = []
    for i in range(len(candles)):
        start = max(0, i + 1 - 24)
        if valid[i + 1] - valid[start] == 0:
            out.append(None)
        else:
            out.append(prefix[i + 1] - prefix[start])
    return out


def reconcile_symbol(
    candles: List[Dict[str, Any]], cfg: StrategyConfig
) -> Tuple[Dict[str, Any], Dict[str, int]]:
    closes = []
    for c in candles:
        close = _close(c)
        if close is None:
            raise ValueError("aligned candle cache contains a bar without a close; refusing to misalign RSI")
        closes.append(float(close))
    rsis = _rsi_series(closes, cfg.rsi_period)
    vols = rolling_volume_24h(candles)
    memo: Dict[Any, Any] = {}

    crash_hours = 0
    pass_volume = 0
    same_bar_confirm = 0
    next_bar_confirm = 0
    generated = 0
    samples: List[Dict[str, Any]] = []

    for i in range(len(candles)):
        rsi = rsis[i]
        if rsi is None or rsi >= cfg.rsi_threshold:
            continue
        crash_hours += 1
        vol = vols[i]
        vol_ok = vol is not None and vol >= cfg.min_daily_volume_usd
        if not vol_ok:
            continue
        pass_volume += 1
        prefix = candles[: i + 1]
        same = confirm_rebound(prefix)
        nxt = i + 1 < len(candles) and confirm_rebound(candles[: i + 2])
        if same:
            same_bar_confirm += 1
        if nxt:
            next_bar_confirm += 1
        sig = generate_signal(prefix, symbol="", config=cfg, cache=memo)
        if sig is not None:
            generated += 1
        if len(samples) < 50:
            samples.append(
                {
                    "timestamp": candles[i].get("timestamp"),
                    "rsi": round(rsi, 4),
                    "volume_24h_usd": round(float(vol), 2),
                    "same_bar_rebound_confirm": bool(same),
                    "next_bar_rebound_confirm": bool(nxt),
                    "generate_signal": bool(sig is not None),
                }
            )

    return (
        {
            "rsi_crash_hours": crash_hours,
            "rsi_crash_hours_pass_volume": pass_volume,
            "same_bar_rebound_confirm": same_bar_confirm,
            "next_bar_rebound_confirm": next_bar_confirm,
            "generate_signal_confirmed": generated,
            "crash_samples": samples,
        },
        {
            "rsi_crash_hours": crash_hours,
            "rsi_crash_hours_pass_volume": pass_volume,
            "same_bar_rebound_confirm": same_bar_confirm,
            "next_bar_rebound_confirm": next_bar_confirm,
            "generate_signal_confirmed": generated,
        },
    )


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache-dir", required=True, help="Aligned complete cache dir containing candles/")
    ap.add_argument("--symbols", nargs="*", default=None, help="Symbols (default: every candle file present)")
    ap.add_argument("--output", default=None, help="JSON output path")
    ap.add_argument("--md-output", default=None, help="Optional markdown output path")
    args = ap.parse_args(argv)

    cache = Path(args.cache_dir)
    if not cache.is_absolute():
        cache = (REPO / cache).resolve()
    candles_dir = cache / "candles"
    if not candles_dir.exists():
        print(f"ERROR: candles dir missing: {candles_dir}", file=sys.stderr)
        return 2

    if args.symbols:
        symbols = list(args.symbols)
    else:
        symbols = sorted(p.stem for p in candles_dir.glob("*.json"))
    if not symbols:
        print("ERROR: no symbols to reconcile", file=sys.stderr)
        return 2

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
        "run_type": "hyperliquid_signal_funnel_reconciliation",
        "provenance_caveat": CAVEAT,
        "cache_dir": str(cache),
        "config": {
            "rsi_period": cfg.rsi_period,
            "rsi_threshold": cfg.rsi_threshold,
            "min_daily_volume_usd": cfg.min_daily_volume_usd,
            "entry_note": "Implementation requires a same-bar rebound confirmation candle (confirm_rebound) before generate_signal returns a signal.",
        },
        "symbols": {},
        "interpretation": {
            "rsi_crash_hours_pass_volume": (
                "Upper bound on spec-literal entries: every volume-passing RSI crash hour "
                "could enter at the next hourly open under the PDF spec. Portfolio one-position "
                "and cap rules can only reduce this number."
            ),
            "same_bar_rebound_confirm": (
                "Implementation gate: confirm_rebound requires a bullish candle on the SAME bar "
                "as the RSI crash before generate_signal returns a signal."
            ),
            "next_bar_rebound_confirm": (
                "Informational: a rebound confirmation candle on the following bar, which the "
                "spec-literal next-open entry does not require."
            ),
        },
    }
    totals = {
        "symbols": 0,
        "bars": 0,
        "rsi_crash_hours": 0,
        "rsi_crash_hours_pass_volume": 0,
        "same_bar_rebound_confirm": 0,
        "next_bar_rebound_confirm": 0,
        "generate_signal_confirmed": 0,
    }
    for sym in symbols:
        path = candles_dir / f"{sym}.json"
        if not path.exists():
            out["symbols"][sym] = {"error": f"missing cache: {path}"}
            continue
        candles = load_candles(path)
        detail, summary = reconcile_symbol(candles, cfg)
        detail["bars"] = len(candles)
        out["symbols"][sym] = detail
        totals["symbols"] += 1
        totals["bars"] += len(candles)
        for k in (
            "rsi_crash_hours",
            "rsi_crash_hours_pass_volume",
            "same_bar_rebound_confirm",
            "next_bar_rebound_confirm",
            "generate_signal_confirmed",
        ):
            totals[k] += summary[k]
    out["totals"] = totals

    out_path = Path(args.output) if args.output else REPO / "research_state" / (
        f"hyperliquid_signal_funnel_{cache.name}.json"
    )
    out_path.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(totals, indent=2))
    print(f"Wrote {out_path}")

    if args.md_output:
        lines = [
            "# Hyperliquid partial signal funnel",
            "",
            f"Generated: {out['generated_at_utc']}",
            "",
            f"Cache: `{cache}`",
            "",
            "| Stage | Count |",
            "|---|---|",
            f"| RSI({cfg.rsi_period}) < {cfg.rsi_threshold:g} hours | {totals['rsi_crash_hours']} |",
            f"| ... passing trailing-24h >= ${cfg.min_daily_volume_usd:,.0f} (upper bound on spec-literal entries) | {totals['rsi_crash_hours_pass_volume']} |",
            f"| ... same-bar rebound confirmation | {totals['same_bar_rebound_confirm']} |",
            f"| ... next-bar rebound confirmation | {totals['next_bar_rebound_confirm']} |",
            f"| ... generate_signal confirmed | {totals['generate_signal_confirmed']} |",
            "",
            CAVEAT,
        ]
        md_path = Path(args.md_output)
        md_path.write_text("\n".join(lines) + "\n")
        print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())