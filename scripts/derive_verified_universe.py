#!/usr/bin/env python3
"""Derive a verifiable universe file from already-ingested, verified candle caches.

This does NOT fabricate data and does NOT contact exchanges. It computes 24h
quote-volume proxies from verified local OHLCV (close*volume summed over rolling
24h windows within the target window) and emits a universe JSON suitable for
`--universe-file` with scripts/fetch_hyperliquid_candles.py and
scripts/run_real_campaign.py.

Output is evidence only about the provided verified local data; it must be used
with a verified provenance manifest for any real campaign claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.loader import load_hyperliquid_candles  # noqa: E402
from src.data.provenance import load_provenance, ProvenanceError, verify_cache_sha256  # noqa: E402


def _parse_iso(s: str) -> datetime:
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _ts_ms(c: Dict[str, Any]):
    ts = c.get("timestamp_ms")
    if ts is not None:
        try:
            return int(ts)
        except Exception:
            return None
    t = c.get("timestamp") or c.get("time") or c.get("t")
    if isinstance(t, (int, float)):
        t = int(t)
        return t if t > 10**12 else t * 1000
    if isinstance(t, str):
        try:
            return int(_parse_iso(t).timestamp() * 1000)
        except Exception:
            return None
    return None


def max_rolling_24h_quote_volume(candles: List[Dict[str, Any]], start_ms: int = None, end_ms: int = None) -> Dict[str, Any]:
    rows = []
    for c in candles:
        ts = _ts_ms(c)
        if ts is None:
            continue
        if start_ms is not None and ts < start_ms:
            continue
        if end_ms is not None and ts > end_ms:
            continue
        try:
            qv = float(c.get("close", 0.0)) * float(c.get("volume", 0.0))
        except Exception:
            qv = 0.0
        rows.append((ts, qv))
    rows.sort(key=lambda x: x[0])
    if not rows:
        return {
            "bars": 0,
            "max_rolling_24h_quote_volume_usd_proxy": 0.0,
            "max_24h_quote_volume": 0.0,  # legacy alias
            "passes_5m_any_24h_window": False,
            "first_ts_ms": None,
            "last_ts_ms": None,
        }
    # rolling 24 bars/hours window by count is sufficient for hourly bars; also safe by timestamp span.
    best = 0.0
    from collections import deque
    dq = deque()
    ssum = 0.0
    for ts, qv in rows:
        dq.append((ts, qv))
        ssum += qv
        cutoff = ts - 24 * 3600 * 1000
        while dq and dq[0][0] <= cutoff:
            _, old = dq.popleft()
            ssum -= old
        if ssum > best:
            best = ssum
    return {
        "bars": len(rows),
        "max_rolling_24h_quote_volume_usd_proxy": round(best, 6),
        "max_24h_quote_volume": round(best, 6),  # legacy alias
        "passes_5m_any_24h_window": best >= 5_000_000.0,
        "first_ts_ms": rows[0][0],
        "last_ts_ms": rows[-1][0],
    }


def main():
    ap = argparse.ArgumentParser(description="Derive verified-universe JSON from verified local candle caches")
    ap.add_argument("--manifest", required=True, help="Verified provenance manifest path")
    ap.add_argument("--cache-dir", default=str(REPO_ROOT / "research_state" / "cache" / "hyperliquid"))
    ap.add_argument("--min-24h-volume-usd", type=float, default=5_000_000.0)
    ap.add_argument("--output", default=str(REPO_ROOT / "research_state" / "universe_verified.json"))
    ap.add_argument("--require-complete-manifest", action="store_true", help="Fail unless manifest is fully complete/verified for real run")
    ap.add_argument("--min-symbols", type=int, default=1)
    ap.add_argument("--verify-cache-sha256", action="store_true",
                    help="Verify each cache file's sha256 against manifest before use; refuses tampered/corrupted caches. Backward compatible no-op when manifest sha256 absent.")
    args = ap.parse_args()

    manifest = load_provenance(args.manifest)
    if args.require_complete_manifest:
        from src.data.provenance import validate_provenance
        ok, errs = validate_provenance(manifest, require_complete=True, min_symbols=args.min_symbols)
        if not ok:
            raise SystemExit("Manifest not complete/verified:\n- " + "\n- ".join(errs))

    tw = manifest.get("target_window") or {}
    start_ms = int(_parse_iso(tw["start"]).timestamp() * 1000) if tw.get("start") else None
    end_ms = int(_parse_iso(tw["end"]).timestamp() * 1000) if tw.get("end") else None
    cache_dir = Path(args.cache_dir)
    candles_dir = cache_dir / "candles"

    report = {}
    selected = []
    for sym, info in (manifest.get("symbols") or {}).items():
        p = candles_dir / f"{sym}.json"
        mp = info.get("cache_path")
        if mp and not p.exists():
            p = REPO_ROOT / mp
        if not p.exists():
            report[sym] = {"error": f"missing cache: {p}", "selected": False}
            continue
        if args.verify_cache_sha256:
            verify_cache_sha256(p, info.get("sha256"), sym)
        candles = load_hyperliquid_candles(str(p), symbol=sym)
        vol = max_rolling_24h_quote_volume(candles, start_ms=start_ms, end_ms=end_ms)
        passes = float(vol.get("max_rolling_24h_quote_volume_usd_proxy") or 0.0) >= args.min_24h_volume_usd
        rec = {
            **vol,
            "selected": passes,
            "manifest_status": info.get("status"),
            "manifest_complete": bool((info.get("coverage") or {}).get("complete_for_target_window")),
            "cache_sha256_from_manifest": info.get("sha256"),
        }
        report[sym] = rec
        if passes:
            selected.append(sym)

    out = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_type": "verified_universe_derivation",
        "real_market_data": bool(manifest.get("summary", {}).get("all_complete")),
        "performance_evidence": False,
        "fabricated_data": False,
        "source_manifest": str(Path(args.manifest).resolve()),
        "target_window": tw,
        "min_24h_volume_usd": args.min_24h_volume_usd,
        "volume_method": "max rolling 24h sum(close*volume) over verified local hourly OHLCV in target window; proxy for exchange 24h quote volume",
        "symbols": sorted(report.keys()),
        "selected_symbols": sorted(selected),
        "selected_count": len(selected),
        "report": report,
        "notes": [
            "Derived from local verified caches only; not a live exchange universe snapshot.",
            "For real campaign claims, use with a complete verified provenance manifest and truthful real_market_data flags.",
        ],
    }
    Path(args.output).write_text(json.dumps(out, indent=2) + "\n")
    print(f"Wrote {args.output} with {len(selected)} selected symbols")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
