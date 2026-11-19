#!/usr/bin/env python3
"""Acquire realized per-venue funding-rate history for C25 (new data input).

C25's PRIMARY arm (`cost_taker_funding`) and `cost_stress` require realized
funding history; the engine's flat ``funding_rate_pct_per_hour=0.01`` proxy is the
cost-fidelity gap C25 adjudicates. This script acquires real funding history for
the C22/C23/C24 universes and writes the cache layout the C25 runner reads:

    research_state/cache/<venue>_funding_<window>/funding_history.csv
    research_state/cache/<venue>_funding_<window>/funding_manifest.json

The manifest carries the scalar ``funding_rate_pct_per_hour`` (mean realized 8h
rate across the venue universe, expressed in percent per hour) used by
``scripts/run_c25_cost_fidelity_campaign.py::_funding_rate_pct_per_hour``.

Venues without a reachable funding source are reported UNAVAILABLE_FUNDING and
never zero-filled; the C25 decision rule then applies to the available venues.

Sources (real market data, no synthesis):
  - binance_um : https://data.binance.vision/data/futures/um/monthly/fundingRate/
  - mexc       : https://contract.mexc.com/api/v1/contract/funding_rate/history
  - bitget     : https://api.bitget.com/api/v2/mix/market/history-fund-rate
  - okx        : https://www.okx.com/api/v5/public/funding-rate-history (403 here)

Run (from repo root):
  PYTHONPATH=. .venv/bin/python scripts/fetch_funding_history.py \
      --venues binance_um mexc bitget --workers 8
"""
from __future__ import annotations

import argparse
import concurrent.futures as futures
import csv
import datetime as dt
import hashlib
import io
import json
import sys
import time
import urllib.request
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

STATE = REPO / "research_state"
WINDOW_START = "2023-01-01"
WINDOW_END = "2026-09-28"
WINDOW_TAG = f"{WINDOW_START.replace('-', '')}_{WINDOW_END.replace('-', '')}"
WINDOW_END_MS = int(dt.datetime(2026, 9, 29, tzinfo=dt.timezone.utc).timestamp() * 1000)
WINDOW_START_MS = int(dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)

UNIVERSE = {
    "binance_um": STATE / "universe_binance_um_multiyear_verified.json",
    "mexc": STATE / "universe_mexc_multiyear_verified.json",
    "bitget": STATE / "universe_bitget_multiyear_verified.json",
    "okx": STATE / "universe_okx_multiyear_verified.json",
}
CONTRACT_FMT = {
    "binance_um": "{s}USDT",
    "mexc": "{s}_USDT",
    "bitget": "{s}USDT",
    "okx": "{s}-USDT-SWAP",
}
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) crash-rebound-research/1.0"


def iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _get(url: str, timeout: int = 30, retries: int = 5) -> bytes:
    last: Optional[Exception] = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(1.5 * (attempt + 1))
    assert last is not None
    raise last


def _get_json(url: str, timeout: int = 30, retries: int = 5) -> Dict[str, Any]:
    return json.loads(_get(url, timeout=timeout, retries=retries))


def load_symbols(venue: str) -> List[str]:
    p = UNIVERSE[venue]
    if not p.exists():
        return []
    d = json.loads(p.read_text())
    syms = d.get("selected_symbols") or d.get("symbols") or []
    return sorted({str(s).upper() for s in syms})


def _months() -> List[str]:
    out = []
    y, m = 2023, 1
    while (y, m) <= (2026, 9):
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def _binance_symbol_rows(symbol: str, workers: int) -> List[Tuple[int, float]]:
    contract = CONTRACT_FMT["binance_um"].format(s=symbol)

    def one(month: str) -> List[Tuple[int, float]]:
        url = ("https://data.binance.vision/data/futures/um/monthly/fundingRate/"
               f"{contract}/{contract}-fundingRate-{month}.zip")
        try:
            raw = _get(url, timeout=30, retries=2)
        except Exception:
            return []
        try:
            with zipfile.ZipFile(io.BytesIO(raw)) as z:
                name = z.namelist()[0]
                text = z.read(name).decode("utf-8", "replace")
        except Exception:
            return []
        rows: List[Tuple[int, float]] = []
        for rec in csv.DictReader(io.StringIO(text)):
            try:
                ts = int(float(rec["calc_time"]))
                rate = float(rec["last_funding_rate"])
            except (KeyError, TypeError, ValueError):
                continue
            if WINDOW_START_MS <= ts < WINDOW_END_MS:
                rows.append((ts, rate))
        return rows

    months = _months()
    with futures.ThreadPoolExecutor(max_workers=workers) as ex:
        chunks = list(ex.map(one, months))
    return [r for chunk in chunks for r in chunk]


def _mexc_symbol_rows(symbol: str, workers: int) -> List[Tuple[int, float]]:
    contract = CONTRACT_FMT["mexc"].format(s=symbol)
    base = ("https://contract.mexc.com/api/v1/contract/funding_rate/history"
            f"?symbol={contract}&page_num={{page}}&page_size=100")
    rows: List[Tuple[int, float]] = []
    page = 1
    total_pages = 1
    while page <= total_pages:
        try:
            d = _get_json(base.format(page=page), timeout=25, retries=2)
        except Exception:
            break
        data = d.get("data") or {}
        total_pages = int(data.get("totalPage") or 1)
        recs = data.get("resultList") or []
        if not recs:
            break
        for rec in recs:
            try:
                ts = int(rec["settleTime"])
                rate = float(rec["fundingRate"])
            except (KeyError, TypeError, ValueError):
                continue
            if WINDOW_START_MS <= ts < WINDOW_END_MS:
                rows.append((ts, rate))
        page += 1
        if page > 500:
            break
    return rows


def _bitget_symbol_rows(symbol: str, workers: int) -> List[Tuple[int, float]]:
    contract = CONTRACT_FMT["bitget"].format(s=symbol)
    base = ("https://api.bitget.com/api/v2/mix/market/history-fund-rate"
            f"?symbol={contract}&productType=usdt-futures&pageSize=100&pageNo={{page}}")
    rows: List[Tuple[int, float]] = []
    page = 1
    while page <= 500:
        try:
            d = _get_json(base.format(page=page), timeout=25, retries=2)
        except Exception:
            break
        recs = d.get("data") or []
        if not isinstance(recs, list) or not recs:
            break
        oldest = None
        for rec in recs:
            try:
                ts = int(rec["fundingTime"])
                rate = float(rec["fundingRate"])
            except (KeyError, TypeError, ValueError):
                continue
            oldest = ts if oldest is None else min(oldest, ts)
            if WINDOW_START_MS <= ts < WINDOW_END_MS:
                rows.append((ts, rate))
        if oldest is not None and oldest < WINDOW_START_MS:
            break
        page += 1
    return rows


FETCHERS = {
    "binance_um": _binance_symbol_rows,
    "mexc": _mexc_symbol_rows,
    "bitget": _bitget_symbol_rows,
}


def acquire(venue: str, workers: int, limit_symbols: Optional[int]) -> Dict[str, Any]:
    if venue not in FETCHERS:
        return {"venue": venue, "status": "UNAVAILABLE_FUNDING",
                "note": f"no reachable funding source for {venue}",
                "funding_rate_pct_per_hour": None}
    symbols = load_symbols(venue)
    if limit_symbols:
        symbols = symbols[:limit_symbols]
    if not symbols:
        return {"venue": venue, "status": "UNAVAILABLE_FUNDING",
                "note": "universe missing", "funding_rate_pct_per_hour": None}

    def one(sym: str) -> Tuple[str, List[Tuple[int, float]]]:
        try:
            return sym, FETCHERS[venue](sym, max(1, workers // 4))
        except Exception as exc:  # noqa: BLE001
            print(f"[warn] {venue} {sym}: {type(exc).__name__}: {exc}", flush=True)
            return sym, []

    with futures.ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(one, symbols))

    per_symbol: Dict[str, Dict[str, Any]] = {}
    all_rows: List[Tuple[str, int, float]] = []
    for sym, rows in results:
        if not rows:
            continue
        per_symbol[sym] = {
            "rows": len(rows),
            "mean_funding_rate": sum(r for _, r in rows) / len(rows),
            "first_ms": min(ts for ts, _ in rows),
            "last_ms": max(ts for ts, _ in rows),
        }
        all_rows.extend((sym, ts, rate) for ts, rate in rows)

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if not all_rows:
        return {"venue": venue, "status": "UNAVAILABLE_FUNDING",
                "note": "no funding records acquired", "generated_at_utc": iso_now(),
                "attempted_symbols": symbols, "funding_rate_pct_per_hour": None}

    cache_dir = STATE / "cache" / f"{venue}_funding_{WINDOW_TAG}"
    cache_dir.mkdir(parents=True, exist_ok=True)
    csv_path = cache_dir / "funding_history.csv"
    with csv_path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["symbol", "funding_time_ms", "funding_rate"])
        for sym, ts, rate in sorted(all_rows, key=lambda r: (r[0], r[1])):
            w.writerow([sym, ts, repr(rate)])

    # Equal-weight mean of per-symbol means (avoids high-frequency symbols
    # dominating the venue-level scalar), then 8h rate -> percent per hour.
    sym_means = [v["mean_funding_rate"] for v in per_symbol.values()]
    mean_rate = sum(sym_means) / len(sym_means)
    pct_per_hour = mean_rate * 100.0 / 8.0

    manifest = {
        "schema_version": 1,
        "generated_at_utc": iso_now(),
        "acquisition_stamp": stamp,
        "venue": venue,
        "window": {"start": WINDOW_START, "end": WINDOW_END,
                   "start_ms": WINDOW_START_MS, "end_ms": WINDOW_END_MS},
        "source": {
            "binance_um": "GET https://data.binance.vision/data/futures/um/monthly/fundingRate/<CONTRACT>/<CONTRACT>-fundingRate-<YYYY-MM>.zip",
            "mexc": "GET https://contract.mexc.com/api/v1/contract/funding_rate/history",
            "bitget": "GET https://api.bitget.com/api/v2/mix/market/history-fund-rate",
        }[venue],
        "symbols_requested": len(symbols),
        "symbols_acquired": sorted(per_symbol),
        "symbols_missing": sorted(set(symbols) - set(per_symbol)),
        "rows_total": len(all_rows),
        "funding_interval_hours": 8,
        "mean_funding_rate_per_8h": mean_rate,
        "funding_rate_pct_per_hour": pct_per_hour,
        "aggregation": "equal-weight mean of per-symbol mean realized 8h rate / 8 / 100",
        "per_symbol": per_symbol,
        "real_market_data": True,
        "performance_evidence": False,
        "fabricated_data": False,
        "funding_history_csv": str(csv_path.relative_to(REPO)),
        "funding_history_sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
    }
    (cache_dir / "funding_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"[done] {venue}: symbols={len(per_symbol)} rows={len(all_rows)} "
          f"pct_per_hour={pct_per_hour:.6f} -> {cache_dir.relative_to(REPO)}", flush=True)
    return {"venue": venue, "status": "FUNDING_ACQUIRED",
            "funding_rate_pct_per_hour": pct_per_hour,
            "rows_total": len(all_rows), "symbols_acquired": len(per_symbol),
            "cache_dir": str(cache_dir.relative_to(REPO))}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--venues", nargs="+", default=["binance_um", "mexc", "bitget"])
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit-symbols", type=int, default=None)
    args = ap.parse_args()

    summary = [acquire(v, args.workers, args.limit_symbols) for v in args.venues]
    out = STATE / f"c25_funding_acquisition_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    out.write_text(json.dumps({
        "schema_version": 1, "generated_at_utc": iso_now(),
        "probe": "c25_funding_acquisition", "window": {"start": WINDOW_START, "end": WINDOW_END},
        "venues": summary,
    }, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
