#!/usr/bin/env python3
"""C23 data acquisition — Bitget USDT-M perpetual 1h OHLCV into a verifiable cache.

WHY THIS EXISTS
---------------
C22 closed `NO_GO` on MEXC (new venue, frozen spec-literal edge). C23 tests the SAME
unchanged spec on a second never-used USDT-perp venue. Runtime probing
(``scripts/probe_c23_venue_acquisition.py``) shows the public Bitget USDT-M REST API is
reachable, serves real 1H OHLCV back to 2023-01-01, and lists the entire spec altcoin
universe. This script is the acquisition primitive for C23.

This is REAL exchange data. It is NOT Hyperliquid data and must never be relabelled as
Hyperliquid performance evidence (``is_hyperliquid_venue_data=false``).

BITGET USDT-M REST (public, no auth)
------------------------------------
    GET https://api.bitget.com/api/v2/mix/market/history-candles
        ?symbol=SOLUSDT&productType=usdt-futures&granularity=1H
        &startTime=<ms>&endTime=<ms>&limit=200
    -> {"code":"00000","data":[["<ts_ms>","open","high","low","close","baseVol","quoteVol"], ...]}

PAGINATION (empirically verified 2026-11-18)
--------------------------------------------
* A single response is capped at 200 bars.
* For a requested span wider than the cap the endpoint returns the LAST 200 bars of the
  span (NOT the first) — forward paging would silently skip hours.
* Bars are ``[startTime, endTime)``: an N-hour span returns N-1 bars.
=> This fetcher pages BACKWARD from ``--end`` in <=199h windows (endTime = cursor, then
   cursor = earliest timestamp received). Every hour in the window is covered exactly
   once; dedupe by timestamp; missing hours are recorded honestly, never fabricated.

VOLUME UNIT NORMALIZATION (spec fidelity)
-----------------------------------------
Bitget ``quoteVol`` is per-bar quote (USDT) volume and ``baseVol`` is base-coin volume.
The engine treats ``volume`` as BASE-COIN volume and derives quote volume as
``sum(volume * close)``. We store ``volume = quoteVol / close`` so ``close * volume``
== true quote USD, matching the OKX/MEXC cache convention. ``quote_volume_usd`` and
``raw_base_volume`` are kept for transparency.

OUTPUT (cache layout consumed by ``c20.load_venue`` / ``derive_verified_universe.py``)
--------------------------------------------------------------------------------------
    <out>/candles/<SYM>.json   normalized candles (timestamp ms, OHLC, volume, timestamp_ms)
    <out>/provenance.json      manifest mirroring the OKX cache schema (per-symbol sha256,
                               coverage via analyze_coverage, synthetic_check is_synthetic=false)
    <out>/SOURCE.json          same manifest (archive-convention alias)

Symbols without full-window coverage yield ``complete_for_target_window=false`` and are
excluded from the verified universe by ``derive_verified_universe.py`` — never gap-filled.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests
except Exception:  # pragma: no cover
    requests = None  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.acquire_exchange_archive import (  # noqa: E402
    DEFAULT_USER_AGENT,
    _dt_to_ms,
    _parse_iso,
    analyze_coverage,
)
from src.data.provenance import expected_hourly_bars  # noqa: E402

BITGET_HISTORY_URL = "https://api.bitget.com/api/v2/mix/market/history-candles"
PRODUCT_TYPE = "usdt-futures"
GRANULARITY = "1H"
SOURCE_LABEL = "bitget_public_mix_market_history_candles_1h"
MAX_SPAN_HOURS = 199  # 200-bar cap -> <=199h windows on an hourly grid


def bitget_symbol(base: str) -> str:
    return f"{base.upper()}USDT"


def _ohlc_ok(o: float, h: float, l: float, c: float) -> bool:
    return (h >= max(o, c) and l <= min(o, c) and h >= l and min(o, h, l, c) > 0)


def normalize_bitget_row(ts_ms: int, o: float, h: float, l: float, c: float,
                         base_vol: float, quote_vol: float) -> Optional[Dict[str, Any]]:
    if not _ohlc_ok(o, h, l, c):
        return None
    if quote_vol is not None and quote_vol > 0 and c > 0:
        volume = quote_vol / c
    else:
        volume = base_vol
    return {
        "timestamp": int(ts_ms),
        "open": float(o),
        "high": float(h),
        "low": float(l),
        "close": float(c),
        "volume": float(volume),
        "timestamp_ms": int(ts_ms),
        "quote_volume_usd": float(quote_vol) if quote_vol is not None else None,
        "raw_base_volume": float(base_vol) if base_vol is not None else None,
    }


def bitget_page(base: str, start_ms: int, end_ms: int, session, timeout: int,
                retries: int = 5) -> List[Dict[str, Any]]:
    """One Bitget page for [start_ms, end_ms); returns raw rows sorted ascending."""
    params = {
        "symbol": bitget_symbol(base),
        "productType": PRODUCT_TYPE,
        "granularity": GRANULARITY,
        "startTime": str(int(start_ms)),
        "endTime": str(int(end_ms)),
        "limit": "200",
    }
    last_err: Optional[Exception] = None
    for attempt in range(retries):
        try:
            resp = session.get(BITGET_HISTORY_URL, params=params, timeout=timeout)
            if resp.status_code == 429:
                raise RuntimeError("HTTP 429 rate limited")
            if resp.status_code != 200:
                raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:160]}")
            body = resp.json()
            if str(body.get("code")) != "00000":
                raise RuntimeError(f"Bitget code={body.get('code')} msg={body.get('msg')}")
            out: List[Dict[str, Any]] = []
            for row in (body.get("data") or []):
                try:
                    out.append({
                        "time_ms": int(row[0]),
                        "open": row[1], "high": row[2], "low": row[3], "close": row[4],
                        "base_vol": row[5] if len(row) > 5 else None,
                        "quote_vol": row[6] if len(row) > 6 else None,
                    })
                except (IndexError, TypeError, ValueError):
                    continue
            return out
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            time.sleep(min(1.0 * (attempt + 1), 8.0))
    raise RuntimeError(f"Bitget page fetch failed for {base} [{start_ms},{end_ms}]: {last_err}")


def bitget_fetch_range(base: str, start_ms: int, end_ms: int, session, timeout: int,
                       sleep_s: float = 0.1, retries: int = 5) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Page BACKWARD from end_ms so no hour is skipped (endpoint returns the LAST 200 bars)."""
    candles: Dict[int, Dict[str, Any]] = {}
    cursor_end = int(end_ms) + 3_600_000  # make the final bar (end_ms) inclusive
    pages = 0
    empty_windows = 0
    span_ms = MAX_SPAN_HOURS * 3_600_000
    while cursor_end > int(start_ms) and pages < 20_000:
        window_start = max(int(start_ms), cursor_end - span_ms)
        rows = bitget_page(base, window_start, cursor_end, session, timeout, retries=retries)
        pages += 1
        kept = 0
        earliest = None
        for r in rows:
            ts_ms = int(r["time_ms"])
            earliest = ts_ms if earliest is None else min(earliest, ts_ms)
            if ts_ms < start_ms or ts_ms > end_ms or ts_ms in candles:
                continue
            try:
                o, h, l, c = float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])
                bv = float(r["base_vol"]) if r["base_vol"] is not None else 0.0
                qv = float(r["quote_vol"]) if r["quote_vol"] is not None else 0.0
            except (TypeError, ValueError):
                continue
            candle = normalize_bitget_row(ts_ms, o, h, l, c, bv, qv)
            if candle is None:
                continue
            candles[ts_ms] = candle
            kept += 1
        if kept == 0:
            empty_windows += 1
        if sleep_s:
            time.sleep(sleep_s)
        if earliest is None:
            break
        cursor_end = earliest
    ordered = [candles[k] for k in sorted(candles)]
    meta = {
        "venue": "bitget",
        "instrument": bitget_symbol(base),
        "endpoint": f"GET {BITGET_HISTORY_URL} (productType={PRODUCT_TYPE}, granularity=1H)",
        "bar": "1H",
        "pages_fetched": pages,
        "empty_windows": empty_windows,
        "window_hours": MAX_SPAN_HOURS,
        "rows_deduped": len(ordered),
        "pagination": "backward <=199h windows (endpoint returns LAST 200 bars of a span)",
        "volume_normalization": "volume = quoteVol/close (base-coin equiv; close*volume == quote USD)",
    }
    return ordered, meta


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="Acquire Bitget USDT-M perp 1h OHLCV into a verifiable cache (C23 new-venue data).")
    ap.add_argument("--symbols", nargs="+", required=True, help="Base symbols, e.g. SOL ADA DOGE")
    ap.add_argument("--start", default="2023-01-01T00:00:00Z")
    ap.add_argument("--end", default="2026-09-28T23:00:00Z")
    ap.add_argument("--out", required=True,
                    help="Cache dir to write candles/<SYM>.json + provenance.json into")
    ap.add_argument("--sleep", type=float, default=0.1, help="Seconds between API pages")
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--retries", type=int, default=5)
    ap.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    ap.add_argument("--force", action="store_true", help="Exit 0 even when coverage is incomplete")
    return ap


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if requests is None:
        print("BLOCKER: requests is required (pip install requests)", file=sys.stderr)
        return 2
    start, end = _parse_iso(args.start), _parse_iso(args.end)
    start_ms, end_ms = _dt_to_ms(start), _dt_to_ms(end)
    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = REPO_ROOT / out_dir
    candles_dir = out_dir / "candles"
    candles_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": args.user_agent, "Accept": "application/json"})

    symbol_report: Dict[str, Any] = {}
    all_complete = True
    for symbol in args.symbols:
        sym = symbol.upper()
        started = time.time()
        try:
            candles, meta = bitget_fetch_range(
                sym, start_ms, end_ms, session, args.timeout,
                sleep_s=args.sleep, retries=args.retries,
            )
        except Exception as exc:  # noqa: BLE001
            symbol_report[sym] = {"symbol": sym, "status": "error",
                                  "error": f"{type(exc).__name__}: {exc}"}
            all_complete = False
            print(f"{sym}: ERROR {type(exc).__name__}: {exc}", flush=True)
            continue
        cov = analyze_coverage(candles, start, end) if candles else {
            "observed_in_window_bars": 0, "expected_hourly_bars": None,
            "complete_for_target_window": False, "gap_count": None,
            "first_timestamp": None, "last_timestamp": None,
            "first_timestamp_ms": None, "last_timestamp_ms": None,
        }
        payload = json.dumps(candles, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        sha = hashlib.sha256(payload).hexdigest()
        path = candles_dir / f"{sym}.json"
        path.write_bytes(payload)
        status = "ok" if cov["complete_for_target_window"] else "incomplete"
        if status != "ok":
            all_complete = False
        symbol_report[sym] = {
            "symbol": sym, "status": status, "venue": "bitget",
            "instrument": meta["instrument"], "endpoint": meta["endpoint"],
            "bar": meta["bar"], "pages_fetched": meta["pages_fetched"],
            "rows_written": len(candles), "sha256": sha,
            "cache_path": str(path.relative_to(REPO_ROOT)) if str(path).startswith(str(REPO_ROOT)) else str(path),
            "source": SOURCE_LABEL,
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            "retrieval_seconds": round(time.time() - started, 2),
            "coverage": cov,
            "synthetic_check": {"is_synthetic": False, "reason": "bitget_public_exchange_download"},
        }
        print(f"{sym}: {status} {cov['observed_in_window_bars']}/{cov['expected_hourly_bars']} "
              f"gaps={cov['gap_count']} first={cov['first_timestamp']} last={cov['last_timestamp']}",
              flush=True)

    manifest = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_type": "data_acquisition_provenance",
        "real_market_data_intended": True,
        "fabricated_data": False,
        "real_market_data": True,
        "performance_evidence": False,
        "is_hyperliquid_venue_data": False,
        "source": {
            "kind": "external_exchange",
            "venue": "bitget",
            "endpoint": BITGET_HISTORY_URL,
            "source_label": SOURCE_LABEL,
        },
        "request_params": {
            "granularity": "1h",
            "start_ms": start_ms,
            "end_ms": end_ms,
            "symbols": [s.upper() for s in args.symbols],
            "window_hours": MAX_SPAN_HOURS,
            "min_daily_volume_usd_requested": 5_000_000.0,
        },
        "venue_note": (
            "REAL Bitget USDT-M perpetual OHLCV, non-synthetic, cross-venue vs the Hyperliquid "
            "spec. NOT Hyperliquid candles and must never be relabelled as Hyperliquid "
            "performance evidence (is_hyperliquid_venue_data=false)."
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
    (out_dir / "provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (out_dir / "SOURCE.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote {len(symbol_report)} symbol files + provenance.json -> {out_dir}")
    if not all_complete and not args.force:
        print("INCOMPLETE: some symbols lack full-window coverage; see provenance.json "
              "(use --force to exit 0)", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
