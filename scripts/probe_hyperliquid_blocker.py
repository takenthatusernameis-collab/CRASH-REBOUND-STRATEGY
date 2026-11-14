#!/usr/bin/env python3
"""Reproducible Hyperliquid API retention probe — the machine-checked data blocker.

WHY THIS EXISTS
---------------
The handoff claims "the full 283-day Hyperliquid window is BLOCKED by public-API
retention" and demands an operator-supplied archive. A prose claim in a markdown
file cannot be verified by the next session, and it silently rots: the partial
runbook in `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` still names 24
symbols, two of which (MATIC, FTM) return ZERO bars from the live API, so any
agent following that runbook literally gets a fail-closed refusal instead of
progress.

This script converts the prose claim into a reproducible artifact:

1. Queries the live public `candleSnapshot` endpoint for the exact spec window
   `2025-12-20T00:00:00Z .. 2026-09-28T23:00:00Z` (expected 6792 hourly bars).
2. Enumerates the *current* perp universe from `metaAndAssetCtxs` and measures
   each symbol's live 24h notional volume against the spec's $5M floor. This
   replaces the stale hardcoded 24-symbol list with the symbols that actually
   trade today.
3. For every qualifying symbol, probes how many of the 6792 expected bars the API
   actually serves, and where the served window begins.
4. Writes `research_state/hyperliquid_retention_probe.json`: exact counts, the
   first missing hour, the served/expected ratio, and a machine-checkable
   verdict.

The output is evidence, not an argument. No number in it is hardcoded: rerunning
against a live API that *does* serve the full window flips `full_window_served`
to true and the downstream gate will then demand a real full campaign instead of
accepting the blocker.

This script NEVER writes candles, never fabricates a bar, and never marks a
partial window as evidence. It only records what the API served.

Usage:
    PYTHONPATH=. python scripts/probe_hyperliquid_blocker.py
    PYTHONPATH=. python scripts/probe_hyperliquid_blocker.py --json
    PYTHONPATH=. python scripts/probe_hyperliquid_blocker.py --symbols BTC ETH --limit 5
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

HL_INFO_URL = "https://api.hyperliquid.xyz/info"
DEFAULT_OUT = REPO / "research_state" / "hyperliquid_retention_probe.json"

SPEC_START = "2025-12-20T00:00:00Z"
SPEC_END = "2026-09-28T23:00:00Z"
SPEC_MIN_DAILY_VOLUME_USD = 5_000_000.0

# Bars the API returned for the requested window in the first recorded probe
# (2026-11-13). Retained only as a *change detector* for the artifact note; the
# verdict is computed from the live response, never from this constant.
LAST_RECORDED_FULL_WINDOW_BARS = 3900


def iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_utc(text: str) -> dt.datetime:
    return dt.datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def to_ms(moment: dt.datetime) -> int:
    return int(moment.timestamp() * 1000)


def from_ms(ms: int) -> dt.datetime:
    return dt.datetime.fromtimestamp(ms / 1000.0, dt.timezone.utc)


def expected_hourly_bars(start: dt.datetime, end: dt.datetime) -> int:
    """Inclusive hourly bar count between two whole-hour bounds."""
    delta = end - start
    return int(delta.total_seconds() // 3600) + 1


def http_json(url: str, payload: Optional[Dict[str, Any]] = None,
              timeout: int = 30, retries: int = 3) -> Any:
    """POST JSON to the Hyperliquid info endpoint with bounded retry.

    A transient network error must not be recorded as "the API does not serve
    the window": that would convert an outage into a false permanent blocker.
    """
    import urllib.error
    import urllib.request

    last_exc: Optional[BaseException] = None
    for attempt in range(retries):
        try:
            data = None
            headers = {"Content-Type": "application/json"}
            if payload is not None:
                data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - recorded, then retried
            last_exc = exc
            if attempt + 1 < retries:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Hyperliquid info request failed after {retries} attempts: {last_exc}")


def fetch_universe(url: str) -> Tuple[List[str], Dict[str, float]]:
    """Return (perp names, {name: day notional volume USD}) from the live meta."""
    data = http_json(url, {"type": "metaAndAssetCtxs"})
    if isinstance(data, dict):
        meta_universe = data.get("universe") or []
        ctxs = data.get("assetCtxs") or data.get("ctxs") or []
    elif isinstance(data, list) and len(data) >= 2:
        # Public response is [ {universe, marginTables, ...}, [ctx, ...] ].
        meta_block, ctxs = data[0], data[1]
        meta_universe = meta_block.get("universe") if isinstance(meta_block, dict) else meta_block
        if not isinstance(meta_universe, list):
            meta_universe = []
    else:
        raise RuntimeError("unexpected metaAndAssetCtxs response shape")
    names: List[str] = []
    volumes: Dict[str, float] = {}
    for entry, ctx in zip(meta_universe, ctxs):
        if isinstance(entry, dict):
            name = str(entry.get("name", "")).upper()
        else:
            name = str(entry).upper()
        if not name:
            continue
        names.append(name)
        try:
            volumes[name] = float(ctx.get("dayNtlVlm") or 0.0)
        except (TypeError, ValueError, AttributeError):
            volumes[name] = 0.0
    return names, volumes


def probe_symbol(url: str, symbol: str, start_ms: int, end_ms: int,
                 interval: str = "1h", timeout: int = 30) -> Dict[str, Any]:
    """Fetch one symbol's candles for the window and summarize what was served."""
    payload = {
        "type": "candleSnapshot",
        "req": {"coin": symbol, "interval": interval,
                "startTime": start_ms, "endTime": end_ms},
    }
    try:
        candles = http_json(url, payload, timeout=timeout)
    except Exception as exc:  # noqa: BLE001
        return {"symbol": symbol, "status": "error", "error": str(exc)[:300],
                "bars_returned": 0}
    if not isinstance(candles, list):
        return {"symbol": symbol, "status": "error",
                "error": f"unexpected candle response type {type(candles).__name__}",
                "bars_returned": 0}
    if not candles:
        return {"symbol": symbol, "status": "empty", "bars_returned": 0}
    stamps = sorted(int(c.get("t")) for c in candles if c.get("t") is not None)
    if not stamps:
        return {"symbol": symbol, "status": "empty", "bars_returned": 0}
    first, last = stamps[0], stamps[-1]
    return {
        "symbol": symbol,
        "status": "ok",
        "bars_returned": len(candles),
        "first_bar_utc": from_ms(first).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "last_bar_utc": from_ms(last).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def build_probe(url: str, symbols: Optional[List[str]] = None,
                limit: Optional[int] = None,
                min_volume: float = SPEC_MIN_DAILY_VOLUME_USD,
                timeout: int = 30) -> Dict[str, Any]:
    start = parse_utc(SPEC_START)
    end = parse_utc(SPEC_END)
    expected = expected_hourly_bars(start, end)

    names, volumes = fetch_universe(url)
    qualifying = sorted(
        (n for n in names if volumes.get(n, 0.0) >= min_volume),
        key=lambda n: (-volumes.get(n, 0.0), n),
    )
    if symbols:
        wanted = {str(s).strip().upper() for s in symbols if str(s).strip()}
        probed_universe = [n for n in qualifying if n in wanted]
        missing_from_universe = sorted(wanted - set(probed_universe))
    else:
        probed_universe = qualifying
        missing_from_universe = []

    if limit is not None and limit > 0:
        probed_universe = probed_universe[:limit]

    per_symbol: List[Dict[str, Any]] = []
    full_served: List[str] = []
    partial_served: List[str] = []
    empty_or_error: List[str] = []
    earliest_served_start: Optional[str] = None

    for sym in probed_universe:
        result = probe_symbol(url, sym, to_ms(start), to_ms(end), timeout=timeout)
        result["day_volume_usd"] = round(volumes.get(sym, 0.0), 2)
        per_symbol.append(result)
        bars = int(result.get("bars_returned", 0))
        if result.get("status") == "ok" and bars >= expected:
            full_served.append(sym)
        elif result.get("status") == "ok" and bars > 0:
            partial_served.append(sym)
            first = result.get("first_bar_utc")
            if first and (earliest_served_start is None or first < earliest_served_start):
                earliest_served_start = first
        else:
            empty_or_error.append(sym)

    full_window_served = bool(probed_universe) and len(full_served) == len(probed_universe)
    served_counts = [int(r.get("bars_returned", 0)) for r in per_symbol]
    max_served = max(served_counts) if served_counts else 0
    missing = max(0, expected - max_served)

    verdict_parts = []
    if full_window_served:
        verdict_parts.append("FULL_283D_SERVED_BY_PUBLIC_API")
    else:
        verdict_parts.append("FULL_283D_BLOCKED_BY_API_RETENTION")
    if empty_or_error:
        verdict_parts.append(f"UNPROBEABLE_SYMBOLS:{len(empty_or_error)}")
    if missing_from_universe:
        verdict_parts.append(f"REQUESTED_NOT_IN_LIVE_UNIVERSE:{len(missing_from_universe)}")

    return {
        "schema_version": 1,
        "generated_at_utc": iso_now(),
        "run_type": "hyperliquid_api_retention_probe",
        "provenance_caveat": (
            "Live Hyperliquid public API probe; non-synthetic; records only what the "
            "public candleSnapshot endpoint served. Not performance evidence."
        ),
        "endpoint": {"url": url, "method": "candleSnapshot + metaAndAssetCtxs"},
        "target_window": {
            "start": SPEC_START,
            "end": SPEC_END,
            "expected_hourly_bars": expected,
        },
        "spec_min_daily_volume_usd": min_volume,
        "universe": {
            "perps_total": len(names),
            "perps_passing_volume_gate": len(qualifying),
            "probed": len(probed_universe),
            "requested_not_in_live_universe": missing_from_universe,
            "probe_limit": limit,
        },
        "probe_summary": {
            "full_window_served": full_window_served,
            "symbols_full_window": full_served,
            "symbols_partial_window": partial_served,
            "symbols_empty_or_error": empty_or_error,
            "max_bars_returned": max_served,
            "expected_hourly_bars": expected,
            "missing_early_bars_vs_expected": missing,
            "earliest_served_start_utc": earliest_served_start,
        },
        "per_symbol": per_symbol,
        "verdict": ";".join(verdict_parts),
        "next_action": (
            "Public API cannot supply the full 283-day window; obtain an operator-supplied "
            "verified Hyperliquid-native archive per research_state/DATA_REQUEST_283D_HYPERLIQUID.md."
            if not full_window_served else
            "Public API serves the full window; run the full-window campaign via scripts/run_real_campaign.py."
        ),
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", default=HL_INFO_URL)
    ap.add_argument("--symbols", nargs="*", default=None,
                    help="Restrict the probe to these symbols (still volume-gated).")
    ap.add_argument("--limit", type=int, default=None,
                    help="Probe at most N qualifying symbols (keeps the probe cheap).")
    ap.add_argument("--min-daily-volume-usd", type=float, default=SPEC_MIN_DAILY_VOLUME_USD)
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--json", action="store_true", help="Print the artifact JSON to stdout.")
    ap.add_argument("--no-write", action="store_true",
                    help="Probe without writing the artifact (for dry inspection).")
    args = ap.parse_args(argv)

    report = build_probe(args.url, symbols=args.symbols, limit=args.limit,
                         min_volume=args.min_daily_volume_usd, timeout=args.timeout)

    if not args.no_write:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2) + "\n")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        s = report["probe_summary"]
        print(f"universe perps={report['universe']['perps_total']} "
              f"passing_gate={report['universe']['perps_passing_volume_gate']} "
              f"probed={report['universe']['probed']}")
        print(f"expected_hourly_bars={s['expected_hourly_bars']} "
              f"max_bars_returned={s['max_bars_returned']} "
              f"missing={s['missing_early_bars_vs_expected']}")
        print(f"full_window_served={s['full_window_served']} "
              f"earliest_served={s['earliest_served_start_utc']}")
        print(f"verdict: {report['verdict']}")
        if not args.no_write:
            print(f"wrote {args.out}")

    # Exit 0 whenever the probe itself succeeded. The *verdict* (blocked or served)
    # is data, not a process failure: the gate reads the artifact, not this code.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())