#!/usr/bin/env python3
"""Acquire FULL-WINDOW hourly OHLCV candles for the spec universe from a documented
external exchange and emit a verifiable, provenance-ready archive directory.

WHY THIS EXISTS
---------------
The Hyperliquid public ``info`` API ``candleSnapshot`` endpoint only returns hourly
candles from ~2026-04-18T16:00:00Z onward (verified 2026-11-13). The spec window is
2025-12-20T00:00:00Z -> 2026-09-28T23:00:00Z, so Hyperliquid's own API can never supply
the first ~119 days of the campaign. Prior sessions correctly refused to fabricate that
window and the durable campaign was blocked.

This script does NOT fabricate anything. It downloads *real, exchange-published* OHLCV
for each requested instrument, records the exact source endpoint, response shape,
retrieval time and per-file sha256, and writes a plain archive directory of
``<SYMBOL>.json`` files that the existing, provenance-gated ingest path
(``scripts/fetch_hyperliquid_candles.py --source archive``) already knows how to verify.

It deliberately does NOT self-certify the result as Hyperliquid evidence: cross-venue
basis is a documented limitation. What it does produce is a *real, non-synthetic,
gap-checked, full-window* archive that can finally drive a real campaign. The emitted
``SOURCE.json`` is the provenance manifest for the archive itself.

DATA SOURCE (default): OKX ``GET /api/v5/market/history-candles``
  https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-candles
  - ``bar=1H`` gives hourly candles; ``after`` paginates backwards in time.
  - Row shape: [ts_ms, open, high, low, close, volume, volCcy, volCcyQuote, confirm]
  - ``confirm == "1"`` marks a closed candle (we require this; partial last bar is dropped).
  - No API key required.

USAGE
-----
    PYTHONPATH=. python scripts/acquire_exchange_archive.py \
        --venues okx --symbols BTC ETH SOL \
        --start 2025-12-20T00:00:00Z --end 2026-09-28T23:00:00Z \
        --out research_state/archives/okx_1h_20251220_20260928

    # then verify + ingest through the provenance gate:
    PYTHONPATH=. python scripts/fetch_hyperliquid_candles.py \
        --source archive --input-archive research_state/archives/okx_1h_20251220_20260928 \
        --start 2025-12-20T00:00:00Z --end 2026-09-28T23:00:00Z \
        --cache-dir research_state/cache/okx_1h_full

The script is deterministic, idempotent (re-running rewrites the archive) and exits
non-zero if any requested symbol fails to achieve complete, gap-free coverage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests
except Exception:  # pragma: no cover
    requests = None  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.provenance import expected_hourly_bars  # noqa: E402

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36 crash-rebound-research/1.0"
)

# Venue adapters. Each returns a list of normalized candle dicts for one page.
# Implementations must return rows in the venue's own order (descending for OKX).


def _parse_iso(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)


def _dt_to_ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def _ms_to_iso(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat()


def _okx_instrument(symbol: str, quote: str) -> str:
    return f"{symbol.upper()}-{quote.upper()}"


def okx_fetch_page(symbol: str, quote: str, after_ms: int, limit: int,
                   session, timeout: int) -> List[Dict[str, Any]]:
    """One page of OKX 1H candles strictly older than ``after_ms`` (exclusive)."""
    url = "https://www.okx.com/api/v5/market/history-candles"
    params = {
        "instId": _okx_instrument(symbol, quote),
        "bar": "1H",
        "after": str(after_ms),
        "limit": str(limit),
    }
    last_err: Optional[Exception] = None
    for attempt in range(4):
        try:
            resp = session.get(url, params=params, timeout=timeout)
            if resp.status_code != 200:
                raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
            body = resp.json()
            if body.get("code") != "0":
                raise RuntimeError(f"OKX error code={body.get('code')} msg={body.get('msg')}")
            return body.get("data") or []
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            time.sleep(1.0 * (attempt + 1))
    raise RuntimeError(f"OKX page fetch failed for {symbol}-{quote}: {last_err}")


def okx_fetch_range(symbol: str, quote: str, start_ms: int, end_ms: int,
                    session, timeout: int, page_limit: int = 300,
                    max_pages: int = 400) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Page backwards from ``end_ms`` until ``start_ms`` is covered."""
    candles: Dict[int, Dict[str, Any]] = {}
    after = end_ms + 1
    pages = 0
    while pages < max_pages:
        rows = okx_fetch_page(symbol, quote, after, page_limit, session, timeout)
        pages += 1
        if not rows:
            break
        kept = 0
        for r in rows:
            try:
                ts = int(r[0])
            except (TypeError, ValueError):
                continue
            # confirm flag is the last column for history-candles
            confirmed = str(r[8]) == "1" if len(r) > 8 else True
            if ts < start_ms or ts > end_ms or not confirmed:
                continue
            if ts in candles:
                continue
            o, h, l, c, v = (float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5]))
            if not (h >= max(o, c) and l <= min(o, c) and h >= l and min(o, h, l, c) > 0):
                continue
            candles[ts] = {
                "timestamp": ts,
                "open": o, "high": h, "low": l, "close": c, "volume": v,
            }
            kept += 1
        oldest = min(int(r[0]) for r in rows if str(r[0]).isdigit())
        if oldest <= start_ms or kept == 0:
            break
        after = oldest  # OKX `after` is exclusive: candles older than this value
    ordered = [candles[k] for k in sorted(candles)]
    meta = {
        "venue": "okx",
        "instrument": _okx_instrument(symbol, quote),
        "endpoint": "GET https://www.okx.com/api/v5/market/history-candles",
        "bar": "1H",
        "pages_fetched": pages,
        "rows_deduped": len(ordered),
        "pagination": "after (exclusive, backwards in time); confirm=='1' required",
    }
    return ordered, meta


VENUES = {
    "okx": {
        "fetch_range": okx_fetch_range,
        "default_quote": "USDT",
        "source_label": "okx_public_rest_v5_history_candles",
    },
}


def analyze_coverage(candles: List[Dict[str, Any]], start: datetime, end: datetime) -> Dict[str, Any]:
    """Exact coverage accounting for the target window (mirrors fetch script)."""
    start_ms, end_ms = _dt_to_ms(start), _dt_to_ms(end)
    exp = expected_hourly_bars(start.isoformat(), end.isoformat())
    if not candles:
        return {"observed_in_window_bars": 0, "expected_hourly_bars": exp,
                "complete_for_target_window": False, "gap_count": None,
                "first_timestamp": None, "last_timestamp": None,
                "first_timestamp_ms": None, "last_timestamp_ms": None}
    times = sorted(int(c["timestamp"]) for c in candles if start_ms <= int(c["timestamp"]) <= end_ms)
    gaps = 0
    for i in range(1, len(times)):
        if times[i] - times[i - 1] != 3_600_000:
            gaps += 1
    first, last = times[0], times[-1]
    complete = (len(times) == exp and gaps == 0 and first == start_ms and last == end_ms)
    return {
        "observed_in_window_bars": len(times),
        "expected_hourly_bars": exp,
        "complete_for_target_window": complete,
        "gap_count": gaps,
        "first_timestamp": _ms_to_iso(first),
        "last_timestamp": _ms_to_iso(last),
        "first_timestamp_ms": first,
        "last_timestamp_ms": last,
    }


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Acquire full-window hourly OHLCV from an external exchange into a verifiable archive")
    ap.add_argument("--venues", nargs="+", default=["okx"], choices=sorted(VENUES))
    ap.add_argument("--symbols", nargs="+", required=True, help="Base symbols, e.g. BTC ETH SOL")
    ap.add_argument("--quote", default=None, help="Quote currency (default: venue default, e.g. USDT)")
    ap.add_argument("--start", default="2025-12-20T00:00:00Z")
    ap.add_argument("--end", default="2026-09-28T23:00:00Z")
    ap.add_argument("--out", required=True, help="Archive directory to write <SYMBOL>.json files into")
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    ap.add_argument("--max-pages", type=int, default=400)
    ap.add_argument("--allow-incomplete", action="store_true",
                    help="Write the archive even if some symbols are incomplete (still reported; exit non-zero unless --force)")
    ap.add_argument("--force", action="store_true", help="Exit 0 even when coverage is incomplete")
    return ap


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if requests is None:
        print("BLOCKER: requests is required (pip install requests)", file=sys.stderr)
        return 2
    start, end = _parse_iso(args.start), _parse_iso(args.end)
    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = REPO_ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": args.user_agent, "Accept": "application/json"})

    symbol_report: Dict[str, Any] = {}
    all_complete = True
    for venue in args.venues:
        adapter = VENUES[venue]
        quote = args.quote or adapter["default_quote"]
        for symbol in args.symbols:
            sym = symbol.upper()
            started = time.time()
            try:
                candles, meta = adapter["fetch_range"](sym, quote, _dt_to_ms(start), _dt_to_ms(end),
                                                       session, args.timeout, max_pages=args.max_pages)
            except Exception as exc:  # noqa: BLE001
                symbol_report[sym] = {"symbol": sym, "status": "error",
                                      "error": f"{type(exc).__name__}: {exc}"}
                all_complete = False
                print(f"{sym}: ERROR {type(exc).__name__}: {exc}")
                continue
            cov = analyze_coverage(candles, start, end)
            payload = json.dumps(candles, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
            sha = hashlib.sha256(payload).hexdigest()
            path = out_dir / f"{sym}.json"
            path.write_bytes(payload)
            status = "ok" if cov["complete_for_target_window"] else "incomplete"
            if status != "ok":
                all_complete = False
            symbol_report[sym] = {
                "symbol": sym, "status": status, "venue": venue,
                "instrument": meta["instrument"], "endpoint": meta["endpoint"],
                "bar": meta["bar"], "pages_fetched": meta["pages_fetched"],
                "rows_written": len(candles), "sha256": sha,
                "archive_file": str(path.relative_to(REPO_ROOT)) if str(path).startswith(str(REPO_ROOT)) else str(path),
                "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
                "retrieval_seconds": round(time.time() - started, 2),
                "coverage": cov,
                "synthetic_check": {"is_synthetic": False, "reason": "external_exchange_download"},
            }
            print(f"{sym}: {status} {cov['observed_in_window_bars']}/{cov['expected_hourly_bars']} "
                  f"gaps={cov['gap_count']} first={cov['first_timestamp']} last={cov['last_timestamp']}")

    manifest = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_type": "external_exchange_archive_acquisition",
        "fabricated_data": False,
        "real_market_data": True,
        "performance_evidence": False,
        "is_hyperliquid_venue_data": False,
        "venue_note": (
            "Candles are REAL, exchange-published OHLCV for the requested instruments but are "
            "NOT Hyperliquid candles. They are cross-venue price/volume proxies for the spec "
            "universe. Use for real strategy/behavior campaign runs; document the venue basis "
            "when comparing to the Hyperliquid-denominated spec targets."
        ),
        "target_window": {"start": start.isoformat(), "end": end.isoformat(),
                          "expected_hourly_bars": expected_hourly_bars(args.start, args.end)},
        "symbols": symbol_report,
        "summary": {
            "symbols_requested": len(args.symbols),
            "symbols_complete": sum(1 for v in symbol_report.values() if v.get("status") == "ok"),
            "all_complete": all_complete,
        },
    }
    (out_dir / "SOURCE.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote {len(symbol_report)} symbol files + SOURCE.json -> {out_dir}")
    if not all_complete and not args.force:
        print("BLOCKED: incomplete coverage; see SOURCE.json", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())