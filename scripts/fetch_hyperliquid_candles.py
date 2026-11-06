#!/usr/bin/env python3
"""Fetch/ingest Hyperliquid hourly candles with verifiable provenance.

This script NEVER fabricates data. It acquires candles from a documented source
(Hyperliquid public `info` API candleSnapshot) or ingests a user-supplied,
verifiable archive, writes per-symbol cache files, and emits a machine-readable
provenance manifest. Downstream real-campaign runs MUST refuse incomplete
coverage/provenance.

Target research window (spec): 2025-12-20 00:00:00Z -> 2026-09-28 23:00:00Z
inclusive hourly bars (283 days). Expected bars are computed from the exact
start/end bounds.
"""
from __future__ import annotations

import argparse
import hashlib
import gzip
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    import pandas as _pd  # type: ignore
except Exception:
    _pd = None

try:
    import pyarrow  # type: ignore  # noqa: F401
    import pyarrow.parquet as _pq  # type: ignore
except Exception:
    _pq = None

try:
    import requests
except Exception:  # pragma: no cover
    requests = None  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.loader import load_hyperliquid_candles, validate_candles  # noqa: E402

HL_INFO_URL = "https://api.hyperliquid.xyz/info"
TARGET_START = "2025-12-20T00:00:00Z"
TARGET_END = "2026-09-28T23:00:00Z"


def _dt_to_ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def _parse_iso(s: str) -> datetime:
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _expected_hourly_bars(start: datetime, end: datetime) -> int:
    # Inclusive hourly bars when start/end are aligned to hour boundaries.
    delta_h = int((_dt_to_ms(end) - _dt_to_ms(start)) / 3_600_000)
    return max(0, delta_h + 1)


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _sha256_obj(obj: Any) -> str:
    return _sha256_bytes(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def _normalize_hl_candle(c: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # Hyperliquid candleSnapshot commonly returns {t,T,s,i,o,c,h,l,v,n,...}
    if not isinstance(c, dict):
        return None
    out: Dict[str, Any] = {}
    # timestamp
    for k in ("t", "time", "timestamp", "T", "startTime"):
        if k in c and c[k] is not None:
            v = c[k]
            try:
                iv = int(v)
                # ms -> ISO for readability; keep ms too
                if iv > 10**12:
                    out["timestamp_ms"] = iv
                    out["timestamp"] = datetime.fromtimestamp(iv / 1000, tz=timezone.utc).isoformat()
                else:
                    out["timestamp_ms"] = iv * 1000
                    out["timestamp"] = datetime.fromtimestamp(iv, tz=timezone.utc).isoformat()
            except Exception:
                out["timestamp"] = str(v)
            break
    # OHLCV
    keymap = {
        "o": "open", "open": "open",
        "h": "high", "high": "high",
        "l": "low", "low": "low",
        "c": "close", "close": "close",
        "v": "volume", "volume": "volume", "vol": "volume",
    }
    for k, v in c.items():
        nk = keymap.get(str(k).lower()) or keymap.get(str(k))
        if nk and v is not None:
            try:
                out[nk] = float(v)
            except Exception:
                pass
    if all(k in out for k in ("open", "high", "low", "close", "volume")):
        return out
    return None


def _post_hl(payload, url: str, timeout: int, max_retries: int):
    last_err = None
    for attempt in range(max_retries):
        try:
            resp = requests.post(url, json=payload, timeout=timeout)
            if resp.status_code >= 500 or resp.status_code == 429:
                time.sleep(min(30, 2 ** attempt))
                continue
            resp.raise_for_status()
            return resp.json(), None
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(min(30, 2 ** attempt))
    return None, last_err


def _extract_raw(raw, coin):
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        for k in ("candles", "data", "result", coin, coin.upper()):
            if k in raw and isinstance(raw[k], list):
                return raw[k]
        for v in raw.values():
            if isinstance(v, list):
                return v
    return []


def fetch_hl_candles(coin: str, start_ms: int, end_ms: int, interval: str = "1h",
                     url: str = HL_INFO_URL, timeout: int = 30,
                     max_retries: int = 4, chunk_hours: int = 1500) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Fetch candles, chunking large windows to mitigate API range limits.

    Note: Hyperliquid's public candle history availability is limited by the
    venue; if the API does not serve the requested historical window, this
    returns whatever is available and the coverage analysis/manifest will mark
    the dataset incomplete. It never fabricates missing bars.
    """
    if requests is None:
        raise RuntimeError("requests is required for Hyperliquid API fetching; install requests or use --input-archive")
    step = max(1, int(chunk_hours)) * 3_600_000
    cur = int(start_ms)
    all_norm = []
    requests_meta = []
    last_err = None
    while cur <= end_ms:
        chunk_end = min(end_ms, cur + step - 3_600_000)
        payload = {"type": "candleSnapshot", "req": {"coin": coin.upper(), "interval": interval, "startTime": cur, "endTime": chunk_end}}
        raw, err = _post_hl(payload, url, timeout, max_retries)
        requests_meta.append({"startTime": cur, "endTime": chunk_end, "ok": raw is not None, "error": err})
        if raw is not None:
            candles_raw = _extract_raw(raw, coin)
            for c in candles_raw:
                nc = _normalize_hl_candle(c)
                if nc is not None:
                    all_norm.append(nc)
        else:
            last_err = err
        cur = chunk_end + 3_600_000
        time.sleep(0.05)
    # dedupe/sort
    by_ts = {}
    for c in all_norm:
        ts = c.get("timestamp_ms")
        if ts is not None:
            by_ts[ts] = c
    norm = [by_ts[k] for k in sorted(by_ts.keys())]
    meta = {
        "source": "hyperliquid_info_api",
        "url": url,
        "request_count": len(requests_meta),
        "requests": requests_meta[:20],
        "requests_truncated": max(0, len(requests_meta) - 20),
        "last_error": last_err,
        "normalized_count": len(norm),
        "note": "Public API may not serve full historical window; coverage/provenance gates real runs.",
    }
    return norm, meta


def _normalize_loaded_candle(c: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Normalize loader-style candle dicts to a stable shape with timestamp_ms."""
    if not isinstance(c, dict):
        return None
    out = dict(c)
    ts = out.get("timestamp_ms")
    if ts is None:
        t = out.get("timestamp") or out.get("time") or out.get("t")
        if isinstance(t, (int, float)):
            it = int(t)
            ts = it if it > 10**12 else it * 1000
        elif isinstance(t, str):
            try:
                ts = _dt_to_ms(_parse_iso(t))
            except Exception:
                ts = None
    if ts is not None:
        out["timestamp_ms"] = int(ts)
        if "timestamp" not in out:
            out["timestamp"] = datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc).isoformat()
    need = ("open", "high", "low", "close", "volume")
    if not all(k in out for k in need):
        # try HL-style keys
        nc = _normalize_hl_candle(out)
        if nc:
            out.update(nc)
    if all(k in out for k in need):
        try:
            for k in need:
                out[k] = float(out[k])
            return out
        except Exception:
            return None
    return None


def _read_symbol_candles_from_parquet(p: Path, symbol: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Read per-symbol candles from a Parquet file (single- or multi-symbol container).

    Streaming-safe: reads only the columns needed and filters by symbol in a
    single pass via row-group filtering, so large archives do not need to be
    loaded fully into memory. Falls back gracefully when pyarrow is unavailable.
    """
    if _pq is None:
        raise RuntimeError("pyarrow not installed; cannot read parquet archive")
    import pyarrow.parquet as pq

    pf = pq.ParquetFile(str(p))
    # Column projection: only read what the normalizer needs (+ optional symbol col).
    schema_names = set(pf.schema_arrow.names)
    want = {"open", "high", "low", "close", "volume", "timestamp", "timestamp_ms", "time", "t"}
    cols = [c for c in want if c in schema_names]
    if "symbol" in schema_names or "coin" in schema_names:
        cols += [c for c in ("symbol", "coin") if c in schema_names]
    if not cols:
        cols = None  # read all

    candles: List[Dict[str, Any]] = []
    sym_col = None
    sym_values = set()
    had_rows = False
    for batch in pf.iter_batches(columns=cols, batch_size=65536):
        rows = batch.to_pylist()
        for r in rows:
            had_rows = True
            if sym_col is None:
                for k in ("symbol", "coin"):
                    if k in r:
                        sym_col = k
                        break
            if sym_col is not None:
                rv = str(r.get(sym_col) or "").strip().upper()
                if rv:
                    sym_values.add(rv)
                    if rv != symbol.upper():
                        continue
            nc = _normalize_loaded_candle(r)
            if nc:
                candles.append(nc)
    if had_rows and sym_col is not None and not candles:
        raise ValueError(f"Parquet contains symbol-tagged rows but none for {symbol}: {p}")
    multi = sym_col is not None and len(sym_values) > 1
    meta = {"format": "parquet", "multi_symbol_container": multi,
            "symbol_column": sym_col, "distinct_symbols_seen": len(sym_values),
            "row_groups": pf.metadata.num_row_groups,
            "rows_scanned": len(candles) if multi else None}
    return candles, meta


def _read_symbol_candles_from_file(p: Path, symbol: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Read per-symbol candles from JSON/NDJSON/JSONL/CSV/Parquet, including multi-symbol containers."""
    suffix = p.suffix.lower()
    if suffix == ".parquet":
        return _read_symbol_candles_from_parquet(p, symbol)
    if suffix == ".csv":
        import csv
        rows = []
        sym_rows = []
        with p.open("r", newline="") as f:
            reader = csv.DictReader(f)
            has_symbol = "symbol" in {str(k).lower() for k in (reader.fieldnames or [])}
            for row in reader:
                rows.append(row)
                if has_symbol:
                    rv = None
                    for k, v in row.items():
                        if str(k).lower() == "symbol":
                            rv = str(v).strip().upper()
                            break
                    if rv == symbol.upper():
                        sym_rows.append(row)
        use = sym_rows if sym_rows else rows
        if has_symbol and not sym_rows:
            raise ValueError(f"CSV contains symbol column but no rows for {symbol}: {p}")
        candles = []
        for row in use:
            # synthesize dict matching loader expectations
            mapped = {}
            for k, v in row.items():
                kl = str(k).lower()
                if kl in ("timestamp", "time", "date", "t"):
                    mapped["timestamp"] = v
                elif kl in ("open", "o"):
                    mapped["open"] = v
                elif kl in ("high", "h"):
                    mapped["high"] = v
                elif kl in ("low", "l"):
                    mapped["low"] = v
                elif kl in ("close", "c"):
                    mapped["close"] = v
                elif kl in ("volume", "v", "vol"):
                    mapped["volume"] = v
            nc = _normalize_loaded_candle(mapped)
            if nc:
                candles.append(nc)
        meta = {"format": "csv", "multi_symbol_container": bool(sym_rows), "rows_total": len(rows)}
        return candles, meta
    if suffix in (".ndjson", ".jsonl"):
        rows_total = 0
        sym_rows = 0
        candles = []
        with p.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rows_total += 1
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if not isinstance(obj, dict):
                    continue
                rv = None
                for k, v in obj.items():
                    if str(k).lower() in ("symbol", "coin", "s"):
                        rv = str(v).strip().upper()
                        break
                if rv is not None:
                    if rv != symbol.upper():
                        continue
                    sym_rows += 1
                nc = _normalize_loaded_candle(obj)
                if nc:
                    candles.append(nc)
        if rows_total > 0 and sym_rows == 0 and not candles:
            raise ValueError(f"NDJSON contains symbol-tagged rows but none for {symbol}: {p}")
        meta = {"format": "ndjson", "multi_symbol_container": sym_rows > 0, "rows_total": rows_total}
        return candles, meta
    # JSON / other: try loader first (handles dict-of-symbols and lists)
    try:
        raw = load_hyperliquid_candles(str(p), symbol=symbol)
        candles = []
        for c in raw:
            nc = _normalize_loaded_candle(c)
            if nc:
                candles.append(nc)
        meta = {"format": suffix.lstrip(".") or "json", "loaded_via": "data_loader"}
        return candles, meta
    except Exception as e:
        # fallback: raw JSON parse for odd shapes
        obj = json.loads(p.read_text())
        seq = None
        if isinstance(obj, dict):
            for k in (symbol, symbol.upper(), symbol.lower()):
                if k in obj and isinstance(obj[k], list):
                    seq = obj[k]
                    break
            if seq is None and isinstance(obj.get("candles"), list):
                seq = obj["candles"]
            if seq is None and isinstance(obj.get("data"), list):
                seq = obj["data"]
        elif isinstance(obj, list):
            seq = obj
        if seq is None:
            raise
        candles = []
        for c in seq:
            nc = _normalize_loaded_candle(c if isinstance(c, dict) else {})
            if nc:
                candles.append(nc)
        meta = {"format": suffix.lstrip(".") or "json", "loaded_via": "raw_parse_fallback", "loader_error": f"{type(e).__name__}: {e}"}
        return candles, meta


def discover_archive_sources(archive_path: Path, symbols: List[str]) -> Dict[str, Any]:
    """Discover ingest sources for symbols in a directory or single file.

    Supports per-symbol files (`<SYMBOL>.json|csv`), and multi-symbol container
    files where a single JSON/CSV holds multiple symbols (loader/normalizer
    extracts the requested symbol).
    """
    p = archive_path
    report = {"archive_path": str(p.resolve()), "is_dir": p.is_dir(), "symbols": {}, "container_files": []}
    if p.is_file():
        # single container may serve many symbols
        report["container_files"].append(str(p.resolve()))
        for sym in symbols:
            report["symbols"][sym] = {"source_path": str(p.resolve()), "kind": "multi_symbol_container_candidate"}
        return report
    if not p.is_dir():
        raise FileNotFoundError(str(p))
    # gather files
    files = [x for x in p.iterdir() if x.is_file()]
    by_stem = {}
    for f in files:
        by_stem.setdefault(f.stem.upper(), []).append(f)
        by_stem.setdefault(f.name.upper(), []).append(f)
    for sym in symbols:
        candidates = [p / f"{sym}.json", p / f"{sym.upper()}.json", p / f"{sym.lower()}.json",
                      p / f"{sym}.csv", p / f"{sym.upper()}.csv", p / f"{sym}.ndjson", p / f"{sym}.jsonl",
                      p / f"{sym}.parquet", p / f"{sym.upper()}.parquet", p / f"{sym}_candles.json",
                      p / f"{sym.upper()}_candles.json", p / f"{sym}_candles.parquet"]
        chosen = next((c for c in candidates if c.exists()), None)
        if chosen is None and sym.upper() in by_stem:
            # prefer exact-ish matches
            prefs = by_stem[sym.upper()]
            chosen = sorted(prefs, key=lambda x: (x.suffix != ".json", x.name))[0]
        if chosen is not None:
            report["symbols"][sym] = {"source_path": str(chosen.resolve()), "kind": "per_symbol_file"}
        else:
            # fallback: any json/csv/ndjson/parquet container
            containers = [f for f in files if f.suffix.lower() in (".json", ".csv", ".ndjson", ".jsonl", ".parquet")]
            report["symbols"][sym] = {"source_path": None, "kind": "missing", "container_candidates": [str(c) for c in containers[:50]]}
    report["container_files"] = [str(f.resolve()) for f in files if f.suffix.lower() in (".json", ".csv", ".ndjson", ".jsonl", ".parquet")]
    return report


def ingest_archive(archive_path: Path, symbol: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    # Accept: dir/<SYMBOL>.json|csv|ndjson|jsonl, file per symbol, or multi-coin container.
    p = archive_path
    container_meta: Dict[str, Any] = {}
    if p.is_dir():
        candidates = [p / f"{symbol}.json", p / f"{symbol.upper()}.json", p / f"{symbol.lower()}.json",
                      p / f"{symbol}.csv", p / f"{symbol.upper()}.csv", p / f"{symbol}.ndjson", p / f"{symbol}.jsonl",
                      p / f"{symbol}.parquet", p / f"{symbol.upper()}.parquet", p / f"{symbol}_candles.json",
                      p / f"{symbol}_candles.parquet"]
        for c in candidates:
            if c.exists():
                p = c
                break
        else:
            # try multi-symbol containers in directory (deterministic order)
            containers = sorted([f for f in p.iterdir() if f.is_file() and f.suffix.lower() in (".json", ".csv", ".ndjson", ".jsonl", ".parquet")])
            found = None
            for c in containers:
                try:
                    probe, pm = _read_symbol_candles_from_file(c, symbol)
                    if probe:
                        found = (c, probe, pm)
                        break
                except Exception:
                    continue
            if found is None:
                raise FileNotFoundError(f"No archive file/rows for {symbol} in {archive_path}")
            p, candles, container_meta = found
            file_sha = _sha256_bytes(p.read_bytes()) if p.exists() else None
            meta = {"source": "user_supplied_archive", "archive_path": str(p.resolve()), "normalized_count": len(candles),
                    "sha256": file_sha, "archive_kind": "multi_symbol_container", **container_meta}
            return candles, meta
    if not p.exists():
        raise FileNotFoundError(str(p))
    candles, container_meta = _read_symbol_candles_from_file(p, symbol)
    file_sha = _sha256_bytes(p.read_bytes())
    meta = {"source": "user_supplied_archive", "archive_path": str(p.resolve()), "normalized_count": len(candles),
            "sha256": file_sha, **container_meta}
    return candles, meta


def merge_verified_archives(archive_paths: List[Path], symbols: List[str], start: datetime, end: datetime,
                            min_daily_volume_usd: float) -> Dict[str, Any]:
    """Merge multiple verified archives into a single symbol-union manifest.

    Track-4 hardening (multi-source / multi-archive): several independently
    verified archives may each cover a disjoint subset of the >= $5M universe.
    This ingests every archive, unions symbols, and records per-source
    provenance (archive path + sha256) for every symbol so downstream gates
    can verify each symbol against its own source. Never fabricates: a symbol
    is only "ok" if its coverage is complete for the target window.
    """
    if not archive_paths:
        raise ValueError("merge_verified_archives requires at least one archive path")
    seen: Dict[str, Dict[str, Any]] = {}
    conflicts: List[Dict[str, str]] = []
    for archive_path in archive_paths:
        ap = Path(archive_path)
        if not ap.exists():
            raise FileNotFoundError(f"archive not found: {ap}")
        for sym in symbols:
            try:
                candles, meta = ingest_archive(ap, sym)
            except FileNotFoundError:
                continue
            cov = analyze_coverage(candles, start, end)
            volcov = analyze_symbol_volume_coverage(candles, min_daily_volume_usd)
            entry = {
                "symbol": sym,
                "status": "ok" if cov.get("complete_for_target_window") else "incomplete",
                "source": meta.get("source", "user_supplied_archive"),
                "archive_path": str(ap.resolve()),
                "archive_sha256": meta.get("sha256"),
                "normalized_count": meta.get("normalized_count"),
                "format": meta.get("format"),
                "multi_symbol_container": meta.get("multi_symbol_container"),
                "symbol_column": meta.get("symbol_column"),
                "distinct_symbols_seen": meta.get("distinct_symbols_seen"),
                "coverage": cov,
                "volume_coverage": volcov,
            }
            prev = seen.get(sym)
            if prev is None:
                seen[sym] = entry
            else:
                # Same symbol from multiple archives: require identical coverage
                # evidence (same bar count + same endpoints); otherwise flag conflict.
                pc, nc = prev.get("coverage"), cov
                same = (pc.get("observed_in_window_bars") == nc.get("observed_in_window_bars")
                        and pc.get("first_timestamp_ms") == nc.get("first_timestamp_ms")
                        and pc.get("last_timestamp_ms") == nc.get("last_timestamp_ms"))
                if same:
                    entry["merged_from"] = [prev.get("archive_path"), str(ap.resolve())]
                    seen[sym] = entry
                else:
                    conflicts.append({"symbol": sym, "archive_a": prev.get("archive_path"),
                                      "archive_b": str(ap.resolve()),
                                      "bars_a": pc.get("observed_in_window_bars"),
                                      "bars_b": nc.get("observed_in_window_bars")})
    return {"symbols": seen, "conflicts": conflicts}


def analyze_coverage(candles: List[Dict[str, Any]], start: datetime, end: datetime) -> Dict[str, Any]:
    expected = _expected_hourly_bars(start, end)
    start_ms = _dt_to_ms(start)
    end_ms = _dt_to_ms(end)
    in_window = []
    gaps = []
    prev = None
    for c in candles:
        ts = c.get("timestamp_ms")
        if ts is None:
            tss = c.get("timestamp")
            if isinstance(tss, str):
                try:
                    ts = _dt_to_ms(_parse_iso(tss))
                except Exception:
                    ts = None
        if ts is None:
            continue
        if start_ms <= ts <= end_ms:
            in_window.append({"ts": ts, "c": c})
    in_window.sort(key=lambda x: x["ts"])
    seen = [x["ts"] for x in in_window]
    if seen:
        prev = seen[0]
        for ts in seen[1:]:
            diff = (ts - prev) / 3_600_000
            if diff > 1.01:
                gaps.append({"from_ms": prev, "to_ms": ts, "missing_hours_approx": max(0, round(diff - 1))})
            prev = ts
    first_ts = seen[0] if seen else None
    last_ts = seen[-1] if seen else None
    coverage_pct = (len(in_window) / expected * 100.0) if expected else 0.0
    complete = (expected > 0 and len(in_window) == expected and not gaps
                and first_ts == start_ms and last_ts == end_ms)
    return {
        "expected_hourly_bars": expected,
        "observed_in_window_bars": len(in_window),
        "coverage_pct": round(coverage_pct, 6),
        "first_timestamp_ms": first_ts,
        "last_timestamp_ms": last_ts,
        "first_timestamp": datetime.fromtimestamp(first_ts/1000, tz=timezone.utc).isoformat() if first_ts else None,
        "last_timestamp": datetime.fromtimestamp(last_ts/1000, tz=timezone.utc).isoformat() if last_ts else None,
        "gap_count": len(gaps),
        "gaps": gaps[:200],  # bounded
        "gaps_truncated": max(0, len(gaps) - 200),
        "complete_for_target_window": complete,
        "start": start.isoformat(),
        "end": end.isoformat(),
    }


def _candle_close(c: Dict[str, Any]) -> Optional[float]:
    v = c.get("close")
    try:
        return float(v) if v is not None else None
    except Exception:
        return None


def _candle_volume(c: Dict[str, Any]) -> Optional[float]:
    v = c.get("volume")
    try:
        return float(v) if v is not None else None
    except Exception:
        return None


def analyze_symbol_volume_coverage(candles: List[Dict[str, Any]], min_daily_volume_usd: float) -> Dict[str, Any]:
    """Rolling 24h USD volume coverage vs min_daily_volume_usd.

    USD volume per bar = volume * close (Hyperliquid perp base volume * quote price).
    For each bar, sum volume*close over the trailing 24 hourly bars including current;
    a symbol passes the universe filter when every bar's 24h USD volume >= threshold.
    Returns pass/fail plus min/mean observed 24h USD volume for provenance.
    """
    n = len(candles)
    usd_vols: List[float] = []
    for i in range(n):
        close = _candle_close(candles[i])
        vol = _candle_volume(candles[i])
        window_start = max(0, i - 23)
        total = 0.0
        has = False
        for j in range(window_start, i + 1):
            vj = _candle_volume(candles[j])
            cj = _candle_close(candles[j])
            if vj is not None and cj is not None and cj > 0:
                total += vj * cj
                has = True
        if has:
            usd_vols.append(total)
    if not usd_vols:
        return {
            "min_daily_volume_usd": min_daily_volume_usd,
            "observed_min_24h_usd_volume": None,
            "observed_mean_24h_usd_volume": None,
            "bars_checked": 0,
            "bars_passing": 0,
            "volume_filter_ok": False,
        }
    passing = sum(1 for v in usd_vols if v >= min_daily_volume_usd)
    return {
        "min_daily_volume_usd": min_daily_volume_usd,
        "observed_min_24h_usd_volume": round(min(usd_vols), 6),
        "observed_mean_24h_usd_volume": round(sum(usd_vols) / len(usd_vols), 6),
        "bars_checked": len(usd_vols),
        "bars_passing": passing,
        "volume_filter_ok": passing == len(usd_vols),
    }


def detect_synthetic_candles(candles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Reject flat/synthetic-looking series.

    A real hourly OHLCV series over 283 days varies. A series where every bar
    shares the identical (open, high, low, close, volume) signature is a
    placeholder/fabricated dataset, not market evidence. Returns a dict describing
    the finding; `is_synthetic` True means the series must never be treated as
    real market data.
    """
    n = len(candles)
    if n == 0:
        return {"is_synthetic": True, "reason": "empty_series", "distinct_signatures": 0, "bars_checked": 0}
    def sig(c: Dict[str, Any]) -> Any:
        return (c.get("open"), c.get("high"), c.get("low"), c.get("close"), c.get("volume"))
    signatures = [sig(c) for c in candles]
    distinct = len(set(signatures))
    # Also flag series where close is constant (no price movement at all).
    closes = [_candle_close(c) for c in candles]
    close_vals = [c for c in closes if c is not None]
    constant_close = bool(close_vals) and len(set(close_vals)) == 1
    flat = distinct == 1
    is_synthetic = flat or constant_close
    return {
        "is_synthetic": is_synthetic,
        "reason": ("flat_series_all_bars_identical" if flat else
                   "constant_close_no_price_movement" if constant_close else "varied_series_ok"),
        "distinct_signatures": distinct,
        "bars_checked": n,
        "distinct_signature_ratio": round(distinct / n, 6) if n else 0.0,
    }


def main():
    ap = argparse.ArgumentParser(description="Fetch/ingest verifiable Hyperliquid hourly candles + provenance")
    ap.add_argument("--symbols", nargs="*", default=None, help="Symbols to fetch (default: built-in universe or all from archive)")
    ap.add_argument("--start", default=TARGET_START)
    ap.add_argument("--end", default=TARGET_END)
    ap.add_argument("--interval", default="1h")
    ap.add_argument("--cache-dir", default=str(REPO_ROOT / "research_state" / "cache" / "hyperliquid"))
    ap.add_argument("--source", choices=["hyperliquid_api", "archive"], default="hyperliquid_api")
    ap.add_argument("--input-archive", default=None, help="Path to user-supplied verified archive dir/file")
    ap.add_argument("--input-archives", nargs="+", default=None, help="Multiple verified archive paths to merge into one symbol-union manifest (Track-4 multi-source).")
    ap.add_argument("--hl-url", default=HL_INFO_URL)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--allow-partial", action="store_true", help="Write manifest even if incomplete (still marked incomplete; real run must refuse)")
    ap.add_argument("--universe-file", default=None, help="Optional JSON file with symbol list")
    ap.add_argument("--min-daily-volume-usd", type=float, default=5_000_000.0, help="Minimum 24h USD volume per symbol (>= $5M spec filter)")
    args = ap.parse_args()

    start = _parse_iso(args.start)
    end = _parse_iso(args.end)
    start_ms, end_ms = _dt_to_ms(start), _dt_to_ms(end)
    cache_dir = Path(args.cache_dir)
    candles_dir = cache_dir / "candles"
    candles_dir.mkdir(parents=True, exist_ok=True)

    symbols = args.symbols
    if not symbols and args.universe_file and Path(args.universe_file).exists():
        u = json.loads(Path(args.universe_file).read_text())
        symbols = u.get("symbols") if isinstance(u, dict) else u
    if not symbols and args.source == "archive" and args.input_archive:
        # Auto-discover symbols from archive directory contents (per-symbol files).
        apth = Path(args.input_archive)
        if apth.is_dir():
            discovered = []
            for f in sorted(apth.iterdir()):
                if f.is_file() and f.suffix.lower() in (".json", ".csv", ".ndjson", ".jsonl"):
                    stem = f.stem.upper().replace("_CANDLES", "")
                    if stem and stem.isalnum() and 2 <= len(stem) <= 15:
                        discovered.append(stem)
            symbols = sorted(set(discovered))
    if not symbols:
        # Conservative default: caller should supply verified universe.
        symbols = ["BTC", "ETH", "SOL", "XRP", "DOGE", "AVAX", "LINK", "SUI", "ADA", "ARB", "OP", "NEAR", "APT", "TIA", "INJ", "LTC", "BCH", "DOT", "ATOM", "UNI", "AAVE", "MATIC", "SEI", "FTM", "ALGO", "ICP"]
    # Accept comma-separated symbols in any position for CLI robustness.
    norm = []
    for s in symbols:
        for part in str(s).replace(';', ',').split(','):
            part = part.strip().upper()
            if part:
                norm.append(part)
    symbols = norm

    manifest = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_type": "data_acquisition_provenance",
        "real_market_data_intended": args.source == "hyperliquid_api" or args.source == "archive",
        "fabricated_data": False,
        "target_window": {"start": start.isoformat(), "end": end.isoformat(), "expected_hourly_bars": _expected_hourly_bars(start, end)},
        "source": {"kind": args.source, "hl_url": args.hl_url if args.source == "hyperliquid_api" else None,
                   "input_archive": str(Path(args.input_archive).resolve()) if args.input_archive else None,
                   "input_archives": [str(Path(p).resolve()) for p in (args.input_archives or [])]},
        "request_params": {"interval": args.interval, "start_ms": start_ms, "end_ms": end_ms, "symbols": symbols},
        "symbols": {},
        "summary": {},
    }

    # Multi-archive / multi-source merge path (Track-4): union symbols across several
    # independently verified archives, each with its own sha256 provenance.
    if args.source == "archive" and args.input_archives:
        merged = merge_verified_archives([Path(p) for p in args.input_archives], symbols, start, end, args.min_daily_volume_usd)
        manifest["merge_conflicts"] = merged.get("conflicts")
        for sym, entry in merged.get("symbols", {}).items():
            candles = None
            try:
                candles, _meta = ingest_archive(Path(entry["archive_path"]), sym)
            except Exception:
                candles = None
            if candles is None:
                entry["status"] = "error"
                entry["error"] = "Failed to re-read candles for cache write"
            else:
                payload = json.dumps(candles, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
                entry["sha256"] = _sha256_bytes(payload)
                out_path = candles_dir / f"{sym}.json"
                entry["cache_path"] = str(out_path.relative_to(REPO_ROOT)) if str(out_path).startswith(str(REPO_ROOT)) else str(out_path)
                if not args.dry_run:
                    out_path.write_bytes(payload)
            manifest["symbols"][sym] = entry
            print(f"{sym}: {entry['status']} {entry.get('coverage',{}).get('observed_in_window_bars','?')}/{entry.get('coverage',{}).get('expected_hourly_bars','?')}")
else:
        for sym in symbols:
            entry = {"symbol": sym, "status": "pending"}
            try:
                if args.source == "archive":
                    if not args.input_archive:
                        raise ValueError("--input-archive required for --source archive")
                    candles, meta = ingest_archive(Path(args.input_archive), sym)
                else:
                    candles, meta = fetch_hl_candles(sym, start_ms, end_ms, interval=args.interval, url=args.hl_url, timeout=args.timeout)
                # Validate structure (best-effort; allow archive to carry timestamps)
                try:
                    validate_candles(candles, check_gaps=False)
                except Exception as ve:
                    entry["validation_warning"] = str(ve)
                cov = analyze_coverage(candles, start, end)
                volcov = analyze_symbol_volume_coverage(candles, args.min_daily_volume_usd)
                synth = detect_synthetic_candles(candles)
                payload = json.dumps(candles, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
                entry.update(meta)
                entry["coverage"] = cov
                entry["volume_coverage"] = volcov
                entry["synthetic_check"] = synth
                entry["sha256"] = _sha256_bytes(payload)
                # A flat/constant series is not real market evidence; never mark it ok/complete.
                if synth.get("is_synthetic"):
                    entry["status"] = "error"
                    entry["error"] = f"{synth.get('reason')}: {synth.get('distinct_signatures')}/{synth.get('bars_checked')} distinct signatures"
                else:
                    entry["status"] = "ok" if cov.get("complete_for_target_window") else "incomplete"
                out_path = candles_dir / f"{sym}.json"
                entry["cache_path"] = str(out_path.relative_to(REPO_ROOT)) if str(out_path).startswith(str(REPO_ROOT)) else str(out_path)
                if not args.dry_run:
                    out_path.write_bytes(payload)
            except Exception as e:
                entry["status"] = "error"
                entry["error"] = f"{type(e).__name__}: {e}"
            manifest["symbols"][sym] = entry
            print(f"{sym}: {entry['status']} {entry.get('coverage',{}).get('observed_in_window_bars','?')}/{entry.get('coverage',{}).get('expected_hourly_bars','?')}")

    ok_all = all(v.get("status") == "ok" for v in manifest["symbols"].values()) and len(manifest["symbols"]) > 0
    complete_syms = [s for s, v in manifest["symbols"].items() if v.get("status") == "ok" and v.get("coverage", {}).get("complete_for_target_window")]
    manifest["summary"] = {
        "symbols_requested": len(symbols),
        "symbols_complete": len(complete_syms),
        "symbols_incomplete_or_error": len(symbols) - len(complete_syms),
        "all_complete": ok_all and len(complete_syms) == len(symbols),
        "ready_for_real_campaign": ok_all and len(complete_syms) > 0 and len(complete_syms) == len(symbols),
        "complete_symbols": complete_syms,
    }
    manifest_path = cache_dir / "provenance.json"
    if not args.dry_run:
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        # Canonical gap report (blocker/provenance fields preserved; never clobbered to a simplified form).
        from scripts.generate_candle_coverage_gap_report import build_gap_report  # noqa: E402
        probe_full = {}
        for sym, info in manifest.get("symbols", {}).items():
            cov = info.get("coverage") or {}
            probe_full[sym] = {
                "coin": sym,
                "count": cov.get("observed_in_window_bars"),
                "first_t": cov.get("first_timestamp_ms"),
                "last_t": cov.get("last_timestamp_ms"),
                "complete": bool(cov.get("complete_for_target_window")),
            }
        probe_evidence = {
            "ts": manifest.get("generated_at_utc"),
            "window": manifest.get("target_window"),
            "full": probe_full,
            "source": manifest.get("source"),
        }
        archive_scan = {
            "searched_paths": [str(Path(args.input_archive).resolve())] if args.input_archive else [],
            "verified_archives_found": [],
        }
        canonical_report = build_gap_report(
            manifest=manifest,
            probe_evidence=probe_evidence,
            generated_at_utc=manifest.get("generated_at_utc"),
            archive_scan=archive_scan,
        )
        (REPO_ROOT / "research_state" / "candle_coverage_gap_report.json").write_text(
            json.dumps(canonical_report, indent=2) + "\n"
        )
        print(f"Wrote manifest: {manifest_path}")
    else:
        print("Dry run; manifest not written.")

    if not manifest["summary"]["all_complete"] and not args.allow_partial:
        print("BLOCKED: incomplete coverage/provenance for target window. Real campaign must not run.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
