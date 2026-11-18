#!/usr/bin/env python3
"""C22 data acquisition — MEXC USDT-perpetual 1h OHLCV into a verifiable cache.

WHY THIS EXISTS
---------------
C1–C21 closed `NO_GO` on the spec-literal crash-rebound edge across OKX + Binance UM
perps. The prior handoff claimed acquisition was CLOSED/exhausted and that "no
new-venue network is available". Runtime probing (scripts/probe_c22_venue_acquisition.py)
showed that claim is OUTDATED for MEXC: the public MEXC contract REST API is reachable
from the runner, serves real USDT-perp 1h OHLCV, and honours arbitrary ``start``/``end``
windows back to 2023. That makes a NEW-DATA, out-of-sample C22 replication feasible —
this script is the acquisition primitive for it.

This is REAL market data from a REAL exchange. It is NOT Hyperliquid data and must never
be relabelled as Hyperliquid performance evidence (``is_hyperliquid_venue_data=false``).

MEXC CONTRACT REST (public, no auth)
------------------------------------
    GET https://contract.mexc.com/api/v1/contract/kline/<SYMBOL>
        ?interval=Min60&start=<unix_sec>&end=<unix_sec>
    -> {"success":true,"data":{"time":[...],"open":[...],"high":[...],"low":[...],
                                "close":[...],"vol":[...],"amount":[...]}}

The endpoint caps a single response at ~2000 bars and, when the window holds more than
that, returns the MOST-RECENT bars in the window. We therefore page FORWARD in
``--window-hours`` (default 1500h < 2000) slices so every hour is covered exactly once.

VOLUME UNIT NORMALIZATION (critical for spec fidelity)
------------------------------------------------------
MEXC ``vol`` is in *contracts* (contract size != 1 base coin for most symbols) and
``amount`` is the per-bar quote (USDT) volume. The strategy/engine treats ``volume`` as
BASE-COIN volume and derives quote volume as ``sum(volume * close)`` (see
``src/strategy/crash_rebound.py::_daily_volume_usd``). To stay consistent with the OKX
cache convention we store ``volume = amount / close`` so that ``close * volume == amount``
(true quote USD) for every bar. ``quote_volume_usd`` and ``raw_contracts`` are kept for
transparency; the loader/engine only read ``volume``.

OUTPUT (cache layout consumed by ``c20.load_venue`` / ``derive_verified_universe.py``)
--------------------------------------------------------------------------------------
    <out>/candles/<SYM>.json   normalized candles (timestamp ms, OHLC, volume, timestamp_ms)
    <out>/provenance.json      manifest mirroring the OKX cache schema (per-symbol sha256,
                               coverage via analyze_coverage, synthetic_check is_synthetic=false)
    <out>/SOURCE.json          same manifest (archive-convention alias)

Coverage is reported HONESTLY: a symbol not listed for the whole window (e.g. listed in
2024) yields ``complete_for_target_window=false`` and is excluded from the verified
universe by ``derive_verified_universe.py`` — never fabricated or gap-filled.
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
    _ms_to_iso,
    _parse_iso,
    analyze_coverage,
)
from src.data.provenance import expected_hourly_bars  # noqa: E402

MEXC_KLINE_URL = "https://contract.mexc.com/api/v1/contract/kline/{symbol}"
MEXC_TICKER_URL = "https://contract.mexc.com/api/v1/contract/ticker"
QUOTE = "USDT"
SOURCE_LABEL = "mexc_public_contract_fapi_kline_min60"


def mexc_instrument(symbol: str, quote: str = QUOTE) -> str:
    return f"{symbol.upper()}_{quote.upper()}"


def _ohlc_ok(o: float, h: float, l: float, c: float) -> bool:
    return (h >= max(o, c) and l <= min(o, c) and h >= l and min(o, h, l, c) > 0)


def normalize_mexc_row(time_s: int, o: float, h: float, l: float, c: float,
                       vol: float, amount: float) -> Optional[Dict[str, Any]]:
    """Normalize one MEXC kline row to the repo candle schema.

    ``volume`` is stored as base-coin-equivalent (``amount / close``) so that
    ``close * volume == amount`` (true quote USD), matching the OKX convention.
    Falls back to raw contract count only if quote amount is unavailable.
    """
    if not _ohlc_ok(o, h, l, c):
        return None
    if amount is not None and amount > 0 and c > 0:
        volume = amount / c
    else:
        volume = vol
    ts_ms = int(time_s) * 1000
    return {
        "timestamp": ts_ms,
        "open": float(o),
        "high": float(h),
        "low": float(l),
        "close": float(c),
        "volume": float(volume),
        "timestamp_ms": ts_ms,
        "quote_volume_usd": float(amount) if amount is not None else None,
        "raw_contracts": float(vol) if vol is not None else None,
    }


def mexc_kline_page(symbol: str, start_s: int, end_s: int, session, timeout: int,
                    retries: int = 4) -> List[Dict[str, Any]]:
    """One MEXC kline page for [start_s, end_s] (unix seconds, inclusive)."""
    url = MEXC_KLINE_URL.format(symbol=mexc_instrument(symbol))
    params = {"interval": "Min60", "start": str(int(start_s)), "end": str(int(end_s))}
    last_err: Optional[Exception] = None
    for attempt in range(retries):
        try:
            resp = session.get(url, params=params, timeout=timeout)
            if resp.status_code != 200:
                raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:160]}")
            body = resp.json()
            if not body.get("success"):
                raise RuntimeError(f"MEXC code={body.get('code')} msg={body.get('message')}")
            data = body.get("data") or {}
            times = data.get("time") or []
            return [
                {
                    "time": int(times[i]),
                    "open": data["open"][i],
                    "high": data["high"][i],
                    "low": data["low"][i],
                    "close": data["close"][i],
                    "vol": data.get("vol", [None] * len(times))[i],
                    "amount": (data.get("amount") or [None] * len(times))[i],
                }
                for i in range(len(times))
            ]
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            time.sleep(1.0 * (attempt + 1))
    raise RuntimeError(f"MEXC page fetch failed for {symbol} [{start_s},{end_s}]: {last_err}")


def mexc_fetch_range(symbol: str, start_ms: int, end_ms: int, session, timeout: int,
                     window_hours: int = 1500, sleep_s: float = 0.15,
                     retries: int = 4) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Page forward in <=1900h windows so every hourly bar in [start_ms,end_ms] is covered.

    Returns (ordered_candles, meta). Missing/empty windows are recorded, never fabricated.
    """
    window = min(int(window_hours), 1900)
    step_ms = window * 3_600_000
    candles: Dict[int, Dict[str, Any]] = {}
    cursor_ms = start_ms
    pages = 0
    empty_windows = 0
    while cursor_ms <= end_ms and pages < 10_000:
        window_end_ms = min(cursor_ms + step_ms - 3_600_000, end_ms)
        rows = mexc_kline_page(symbol, cursor_ms // 1000, window_end_ms // 1000,
                               session, timeout, retries=retries)
        pages += 1
        kept = 0
        for r in rows:
            try:
                ts_ms = int(r["time"]) * 1000
            except (TypeError, ValueError):
                continue
            if ts_ms < start_ms or ts_ms > end_ms or ts_ms in candles:
                continue
            vol = r.get("vol")
            amount = r.get("amount")
            try:
                o, h, l, c = float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])
            except (TypeError, ValueError):
                continue
            candle = normalize_mexc_row(
                r["time"], o, h, l, c,
                float(vol) if vol is not None else 0.0,
                float(amount) if amount is not None else 0.0,
            )
            if candle is None:
                continue
            candles[ts_ms] = candle
            kept += 1
        if kept == 0:
            empty_windows += 1
        if sleep_s:
            time.sleep(sleep_s)
        cursor_ms = window_end_ms + 3_600_000
    ordered = [candles[k] for k in sorted(candles)]
    meta = {
        "venue": "mexc",
        "instrument": mexc_instrument(symbol),
        "endpoint": f"GET {MEXC_KLINE_URL.format(symbol='<SYMBOL>')} (interval=Min60, start/end unix sec)",
        "bar": "1H",
        "pages_fetched": pages,
        "empty_windows": empty_windows,
        "window_hours": window,
        "rows_deduped": len(ordered),
        "pagination": "forward <=1900h windows; MEXC caps ~2000 bars/call (most-recent)",
        "volume_normalization": "volume = amount/close (base-coin equiv; close*volume == quote USD)",
    }
    return ordered, meta


def _empty_coverage() -> Dict[str, Any]:
    return {
        "observed_in_window_bars": 0, "expected_hourly_bars": None,
        "complete_for_target_window": False, "gap_count": None,
        "first_timestamp": None, "last_timestamp": None,
        "first_timestamp_ms": None, "last_timestamp_ms": None,
    }


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="Acquire MEXC USDT-perp 1h OHLCV into a verifiable cache (C22 new-venue data).")
    ap.add_argument("--symbols", nargs="+", required=True, help="Base symbols, e.g. SOL ADA DOGE")
    ap.add_argument("--start", default="2023-01-01T00:00:00Z")
    ap.add_argument("--end", default="2026-09-28T23:00:00Z")
    ap.add_argument("--out", required=True,
                    help="Cache dir to write candles/<SYM>.json + provenance.json into")
    ap.add_argument("--window-hours", type=int, default=1500)
    ap.add_argument("--sleep", type=float, default=0.15, help="Seconds between API pages")
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--retries", type=int, default=4)
    ap.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    ap.add_argument("--allow-incomplete", action="store_true",
                    help="Write cache even if some symbols are incomplete (still reported)")
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
            candles, meta = mexc_fetch_range(
                sym, start_ms, end_ms, session, args.timeout,
                window_hours=args.window_hours, sleep_s=args.sleep, retries=args.retries,
            )
        except Exception as exc:  # noqa: BLE001
            symbol_report[sym] = {"symbol": sym, "status": "error",
                                  "error": f"{type(exc).__name__}: {exc}"}
            all_complete = False
            print(f"{sym}: ERROR {type(exc).__name__}: {exc}")
            continue
        cov = analyze_coverage(candles, start, end) if candles else _empty_coverage()
        payload = json.dumps(candles, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        sha = hashlib.sha256(payload).hexdigest()
        path = candles_dir / f"{sym}.json"
        path.write_bytes(payload)
        status = "ok" if cov["complete_for_target_window"] else "incomplete"
        if status != "ok":
            all_complete = False
        symbol_report[sym] = {
            "symbol": sym, "status": status, "venue": "mexc",
            "instrument": meta["instrument"], "endpoint": meta["endpoint"],
            "bar": meta["bar"], "pages_fetched": meta["pages_fetched"],
            "rows_written": len(candles), "sha256": sha,
            "cache_path": str(path.relative_to(REPO_ROOT)) if str(path).startswith(str(REPO_ROOT)) else str(path),
            "source": SOURCE_LABEL,
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            "retrieval_seconds": round(time.time() - started, 2),
            "coverage": cov,
            "synthetic_check": {"is_synthetic": False, "reason": "mexc_public_exchange_download"},
        }
        print(f"{sym}: {status} {cov['observed_in_window_bars']}/{cov['expected_hourly_bars']} "
              f"gaps={cov['gap_count']} first={cov['first_timestamp']} last={cov['last_timestamp']}")

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
            "venue": "mexc",
            "endpoint": MEXC_KLINE_URL.format(symbol="<SYMBOL>"),
            "source_label": SOURCE_LABEL,
        },
        "request_params": {
            "interval": "1h",
            "start_ms": start_ms,
            "end_ms": end_ms,
            "symbols": [s.upper() for s in args.symbols],
            "window_hours": min(args.window_hours, 1900),
            "min_daily_volume_usd_requested": 5_000_000.0,
        },
        "venue_note": (
            "REAL MEXC USDT-perpetual OHLCV, non-synthetic, cross-venue vs the Hyperliquid "
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