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
from src.data.provenance import (  # noqa: E402
    ProvenanceError,
    TARGET_END,
    TARGET_START,
    detect_synthetic_candles,
    expected_hourly_bars,
    load_provenance,
    verify_cache_sha256,
)


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

    from src.strategy.config import enforce_spec_volume_floor, SPEC_MIN_DAILY_VOLUME_USD
    requested_min = float(args.min_24h_volume_usd)
    effective_min = enforce_spec_volume_floor(requested_min)
    if requested_min != effective_min:
        print(
            f"WARNING: spec-compliant derivation enforces >= ${SPEC_MIN_DAILY_VOLUME_USD:g} 24h volume; "
            f"requested {requested_min:g} raised to {effective_min:g}.",
            file=sys.stderr,
        )
    args.min_24h_volume_usd = effective_min
    spec_compliant_volume_threshold = effective_min >= SPEC_MIN_DAILY_VOLUME_USD or effective_min == 0.0 and False
    # 0 is explicit non-spec escape hatch only; never label as spec-compliant selection.
    spec_compliant_volume_threshold = effective_min >= SPEC_MIN_DAILY_VOLUME_USD

    manifest = load_provenance(args.manifest)
    if args.require_complete_manifest:
        from src.data.provenance import validate_provenance
        ok, errs = validate_provenance(
            manifest,
            require_complete=True,
            min_symbols=args.min_symbols,
            require_spec_volume_floor=SPEC_MIN_DAILY_VOLUME_USD,
        )
        if not ok:
            raise SystemExit("Manifest not complete/verified:\n- " + "\n- ".join(errs))

    tw = manifest.get("target_window") or {}
    start_ms = int(_parse_iso(tw["start"]).timestamp() * 1000) if tw.get("start") else None
    end_ms = int(_parse_iso(tw["end"]).timestamp() * 1000) if tw.get("end") else None
    cache_dir = Path(args.cache_dir)
    candles_dir = cache_dir / "candles"

    report = {}
    selected = []
    runtime_synth_by_sym: Dict[str, Dict[str, Any]] = {}
    for sym, info in (manifest.get("symbols") or {}).items():
        p = candles_dir / f"{sym}.json"
        mp = info.get("cache_path")
        if mp and not p.exists():
            p = REPO_ROOT / mp
        if not p.exists():
            report[sym] = {"error": f"missing cache: {p}", "selected": False, "excluded_reason": "missing_cache"}
            continue
        if args.verify_cache_sha256:
            verify_cache_sha256(p, info.get("sha256"), sym)
        candles = load_hyperliquid_candles(str(p), symbol=sym)
        vol = max_rolling_24h_quote_volume(candles, start_ms=start_ms, end_ms=end_ms)
        manifest_status = info.get("status")
        manifest_complete = bool((info.get("coverage") or {}).get("complete_for_target_window"))
        synth_manifest = info.get("synthetic_check") if isinstance(info.get("synthetic_check"), dict) else None
        runtime_synth = detect_synthetic_candles(candles)
        runtime_synth_by_sym[sym] = runtime_synth
        excluded_reason = None
        if manifest_status != "ok":
            excluded_reason = f"manifest_status:{manifest_status}"
        elif not manifest_complete:
            excluded_reason = "manifest_incomplete_coverage"
        elif not isinstance(info.get("synthetic_check"), dict):
            excluded_reason = "manifest_synthetic_check_missing_unverified"
        elif synth_manifest is not None and synth_manifest.get("is_synthetic"):
            excluded_reason = f"manifest_synthetic:{synth_manifest.get('reason') or 'unknown'}"
        elif runtime_synth.get("is_synthetic"):
            excluded_reason = f"runtime_synthetic:{runtime_synth.get('reason') or 'unknown'}"
        elif int(vol.get("bars") or 0) <= 0:
            excluded_reason = "no_in_window_bars"
        passes_volume = float(vol.get("max_rolling_24h_quote_volume_usd_proxy") or 0.0) >= args.min_24h_volume_usd
        selected_ok = passes_volume and excluded_reason is None
        rec = {
            **vol,
            "selected": selected_ok,
            "volume_passes_threshold": passes_volume,
            "manifest_status": manifest_status,
            "manifest_complete": manifest_complete,
            "cache_sha256_from_manifest": info.get("sha256"),
            "synthetic_check": synth_manifest,
            "runtime_synthetic_check": runtime_synth,
        }
        if excluded_reason:
            rec["excluded_reason"] = excluded_reason
        report[sym] = rec
        if selected_ok:
            selected.append(sym)

    # Campaign item 4 residual: summary-consumer hardening. Manifest summary labels
    # (all_complete / ready_for_real_campaign) are evidence only; authoritative
    # completeness is recomputed from validated symbol facts and is fail-closed when
    # the summary contradicts those facts. Never trust a summary boolean over symbol
    # coverage/synthetic/status facts.
    summary = manifest.get("summary") or {}
    symbols = manifest.get("symbols") or {}
    tw_start = tw.get("start")
    tw_end = tw.get("end")
    exp = (
        expected_hourly_bars(tw_start, tw_end)
        if (tw_start and tw_end)
        else expected_hourly_bars(TARGET_START, TARGET_END)
    )
    actual_complete: List[str] = []
    for sym, info in (symbols.items() if isinstance(symbols, dict) else []):
        if not isinstance(info, dict):
            continue
        cov = info.get("coverage") or {}
        synth = info.get("synthetic_check")
        rt = runtime_synth_by_sym.get(sym)
        if info.get("status") != "ok":
            continue
        if cov.get("complete_for_target_window") is not True:
            continue
        if cov.get("expected_hourly_bars") != exp:
            continue
        if cov.get("observed_in_window_bars") != exp:
            continue
        if (cov.get("gap_count") or 0) != 0:
            continue
        if synth is None:
            continue
        if isinstance(synth, dict) and synth.get("is_synthetic"):
            continue
        if rt and rt.get("is_synthetic"):
            continue
        actual_complete.append(sym)
    computed_all_complete = bool(symbols) and len(actual_complete) == len(symbols)

    summary_all_complete = bool(summary.get("all_complete"))
    summary_ready = bool(summary.get("ready_for_real_campaign"))
    # Campaign item 4 residual (summary-consumer hardening): manifest summary labels
    # are advisory only. Optimistic contradictions remain fail-closed (never emit
    # real_market_data/selection when summary claims complete but validated facts do
    # not prove it). Stale-pessimistic labels must NOT block when validated symbol
    # facts prove completeness and non-synthetic evidence for all symbols; do not
    # emit real_market_data/selection without validated complete non-synthetic
    # evidence. Archived-verified evidence only; never fabricate.
    summary_contradiction = (summary_all_complete and not computed_all_complete)
    selected_rows = [r for r in report.values() if isinstance(r, dict) and r.get("selected")]
    all_selected_verified_non_synthetic = bool(selected_rows) and all(
        r.get("manifest_status") == "ok"
        and r.get("manifest_complete") is True
        and not bool((r.get("synthetic_check") or {}).get("is_synthetic"))
        and not bool((r.get("runtime_synthetic_check") or {}).get("is_synthetic"))
        and not r.get("excluded_reason")
        for r in selected_rows
    )
    real_market_data = (
        computed_all_complete
        and all_selected_verified_non_synthetic
        and not summary_contradiction
    )
    if selected and not real_market_data:
        raise SystemExit(
            "Refusing to emit selected verified-universe symbols without complete verified non-synthetic source evidence. "
            "Use --require-complete-manifest for real-campaign derivation and ensure manifest/symbol status, coverage, and synthetic checks are truthful."
        )
    out = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_type": "verified_universe_derivation",
        "real_market_data": real_market_data,
        "performance_evidence": False,
        "fabricated_data": False,
        "source_manifest": str(Path(args.manifest).resolve()),
        "target_window": tw,
        "requested_min_24h_volume_usd": requested_min,
        "min_24h_volume_usd": args.min_24h_volume_usd,
        "spec_compliant_volume_threshold": spec_compliant_volume_threshold,
        "volume_method": "max rolling 24h sum(close*volume) over verified local hourly OHLCV in target window; proxy for exchange 24h quote volume",
        "symbols": sorted(report.keys()),
        "selected_symbols": sorted(selected) if real_market_data else [],
        "selected_count": len(selected) if real_market_data else 0,
        "report": report,
        "notes": [
            "Derived from local verified caches only; not a live exchange universe snapshot.",
            "For real campaign claims, use with a complete verified provenance manifest and truthful real_market_data flags.",
            "min_24h_volume_usd is the effective threshold after spec-floor enforcement; requested_min_24h_volume_usd records the caller input. sub-$5M non-zero inputs are raised to $5M for spec-compliant derivation.",
            "Symbols with manifest status!=ok, incomplete coverage, manifest synthetic_check, runtime synthetic detection, or missing in-window evidence are excluded fail-closed and never labeled real_market_data.",
        ],
    }
    Path(args.output).write_text(json.dumps(out, indent=2) + "\n")
    print(f"Wrote {args.output} with {len(selected)} selected symbols")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
