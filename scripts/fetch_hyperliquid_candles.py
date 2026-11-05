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
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

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


def ingest_archive(archive_path: Path, symbol: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    # Accept: dir/<SYMBOL>.json|csv, file per symbol, or multi-coin json.
    p = archive_path
    if p.is_dir():
        candidates = [p / f"{symbol}.json", p / f"{symbol.upper()}.json", p / f"{symbol.lower()}.json",
                      p / f"{symbol}.csv", p / f"{symbol.upper()}.csv"]
        for c in candidates:
            if c.exists():
                p = c
                break
        else:
            raise FileNotFoundError(f"No archive file for {symbol} in {archive_path}")
    if not p.exists():
        raise FileNotFoundError(str(p))
    candles = load_hyperliquid_candles(str(p), symbol=symbol)
    meta = {"source": "user_supplied_archive", "archive_path": str(p.resolve()), "normalized_count": len(candles),
            "sha256": _sha256_bytes(p.read_bytes())}
    return candles, meta


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


def main():
    ap = argparse.ArgumentParser(description="Fetch/ingest verifiable Hyperliquid hourly candles + provenance")
    ap.add_argument("--symbols", nargs="*", default=None, help="Symbols to fetch (default: built-in universe or all from archive)")
    ap.add_argument("--start", default=TARGET_START)
    ap.add_argument("--end", default=TARGET_END)
    ap.add_argument("--interval", default="1h")
    ap.add_argument("--cache-dir", default=str(REPO_ROOT / "research_state" / "cache" / "hyperliquid"))
    ap.add_argument("--source", choices=["hyperliquid_api", "archive"], default="hyperliquid_api")
    ap.add_argument("--input-archive", default=None, help="Path to user-supplied verified archive dir/file")
    ap.add_argument("--hl-url", default=HL_INFO_URL)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--allow-partial", action="store_true", help="Write manifest even if incomplete (still marked incomplete; real run must refuse)")
    ap.add_argument("--universe-file", default=None, help="Optional JSON file with symbol list")
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
    if not symbols:
        # Conservative default: top liquid perps likely relevant; caller should supply verified universe.
        symbols = ["BTC", "ETH", "SOL", "XRP", "DOGE", "AVAX", "LINK", "SUI", "ADA", "ARB", "OP", "NEAR", "APT", "TIA", "INJ", "LTC", "BCH", "DOT", "ATOM", "UNI", "AAVE", "MATIC", "SEI", "FTM", "ALGO", "ICP"]
    symbols = [str(s).upper() for s in symbols]

    manifest = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_type": "data_acquisition_provenance",
        "real_market_data_intended": args.source == "hyperliquid_api" or args.source == "archive",
        "fabricated_data": False,
        "target_window": {"start": start.isoformat(), "end": end.isoformat(), "expected_hourly_bars": _expected_hourly_bars(start, end)},
        "source": {"kind": args.source, "hl_url": args.hl_url if args.source == "hyperliquid_api" else None,
                   "input_archive": str(Path(args.input_archive).resolve()) if args.input_archive else None},
        "request_params": {"interval": args.interval, "start_ms": start_ms, "end_ms": end_ms, "symbols": symbols},
        "symbols": {},
        "summary": {},
    }

    ok_all = True
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
            payload = json.dumps(candles, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
            entry.update(meta)
            entry["coverage"] = cov
            entry["sha256"] = _sha256_bytes(payload)
            entry["status"] = "ok" if cov.get("complete_for_target_window") else "incomplete"
            if entry["status"] != "ok":
                ok_all = False
            out_path = candles_dir / f"{sym}.json"
            entry["cache_path"] = str(out_path.relative_to(REPO_ROOT)) if str(out_path).startswith(str(REPO_ROOT)) else str(out_path)
            if not args.dry_run:
                out_path.write_bytes(payload)
        except Exception as e:
            ok_all = False
            entry["status"] = "error"
            entry["error"] = f"{type(e).__name__}: {e}"
        manifest["symbols"][sym] = entry
        print(f"{sym}: {entry['status']} {entry.get('coverage',{}).get('observed_in_window_bars','?')}/{entry.get('coverage',{}).get('expected_hourly_bars','?')}")

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
        # Gap report
        gap_report = {s: v.get("coverage", {}) for s, v in manifest["symbols"].items() if not v.get("coverage", {}).get("complete_for_target_window")}
        (REPO_ROOT / "research_state" / "candle_coverage_gap_report.json").write_text(json.dumps({"generated_at_utc": manifest["generated_at_utc"], "target_window": manifest["target_window"], "gaps": gap_report}, indent=2) + "\n")
        print(f"Wrote manifest: {manifest_path}")
    else:
        print("Dry run; manifest not written.")

    if not manifest["summary"]["all_complete"] and not args.allow_partial:
        print("BLOCKED: incomplete coverage/provenance for target window. Real campaign must not run.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
