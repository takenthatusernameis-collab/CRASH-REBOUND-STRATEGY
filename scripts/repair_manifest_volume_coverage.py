#!/usr/bin/env python3
"""Repair a provenance manifest's `volume_coverage` from verified local caches.

The OKX full-universe manifest (`research_state/cache/okx_1h_full_20251220_20260928/provenance.json`)
was emitted before Phase E added `observed_max_24h_usd_volume` and
`universe_membership_ok` to `analyze_symbol_volume_coverage`. Without those fields the
spec-reconciled admission path fails-closed on the legacy all-bars
`volume_filter_ok is not true` message, blocking the full-universe real campaign even
though the underlying verified caches are valid.

This script does NOT re-fetch data and does NOT fabricate anything. It re-reads each
verified cache file (enforcing sha256 + synthetic_check via the guarded loader path),
recomputes `volume_coverage` with `analyze_symbol_volume_coverage`, and rewrites the
manifest in place. All other fields (sha256, status, coverage, synthetic_check,
cache_path, request_params, summary) are preserved.

Usage:
    python scripts/repair_manifest_volume_coverage.py \
        --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json \
        [--dry-run] [--require-verified]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.fetch_hyperliquid_candles import analyze_symbol_volume_coverage  # noqa: E402
from src.data.provenance import (  # noqa: E402
    ProvenanceError,
    load_provenance,
    verify_cache_sha256,
)
from src.data.loader import load_hyperliquid_candles  # noqa: E402


def _read_verified_candles(sym: str, info: Dict[str, Any], cache_dir: Path):
    p = cache_dir / "candles" / f"{sym}.json"
    if not p.exists():
        mp = info.get("cache_path")
        if mp:
            p = REPO_ROOT / mp
    if not p.exists():
        raise ProvenanceError(f"{sym}: cache file missing: {p}")
    verify_cache_sha256(p, info.get("sha256"), sym)
    return load_hyperliquid_candles(str(p), symbol=sym, require_verified=True, provenance_info=info)


def repair_manifest(manifest_path: str, *, dry_run: bool = False, require_verified: bool = True) -> Dict[str, Any]:
    manifest = load_provenance(manifest_path)
    cache_dir = Path(manifest_path).resolve().parent
    tw = manifest.get("target_window") or {}
    start_ms = None
    end_ms = None
    if tw.get("start"):
        start_ms = int(datetime.fromisoformat(tw["start"].replace("Z", "+00:00")).timestamp() * 1000)
    if tw.get("end"):
        end_ms = int(datetime.fromisoformat(tw["end"].replace("Z", "+00:00")).timestamp() * 1000)

    symbols = manifest.get("symbols") or {}
    if not isinstance(symbols, dict):
        raise ProvenanceError("manifest symbols must be an object")

    repaired: Dict[str, Any] = {}
    errors: List[str] = []
    for sym, info in symbols.items():
        if not isinstance(info, dict):
            errors.append(f"{sym}: not an object")
            continue
        if info.get("status") != "ok":
            repaired[sym] = dict(info)
            continue
        try:
            candles = _read_verified_candles(sym, info, cache_dir)
        except ProvenanceError as e:
            errors.append(f"{sym}: {e}")
            continue
        volcov = analyze_symbol_volume_coverage(candles, 5_000_000.0)
        # Preserve any caller-supplied requested/effective intent fields verbatim.
        for k in ("min_daily_volume_usd_requested", "min_daily_volume_usd_effective"):
            if k in info.get("volume_coverage", {}):
                volcov[k] = info["volume_coverage"][k]
        new_info = dict(info)
        new_info["volume_coverage"] = volcov
        repaired[sym] = new_info

    if errors and require_verified:
        raise ProvenanceError("Manifest repair blocked by unverified caches:\n- " + "\n- ".join(errors))

    out = dict(manifest)
    out["symbols"] = repaired
    # Idempotent: reuse an existing repair stamp when present so repeated dry runs
    # produce byte-identical manifests (the repaired fields are deterministic).
    prev = manifest.get("repaired_volume_coverage") if isinstance(manifest.get("repaired_volume_coverage"), dict) else None
    stamp = (prev or {}).get("generated_at_utc") or __import__("datetime").datetime.now(timezone.utc).isoformat()
    out["repaired_volume_coverage"] = {
        "generated_at_utc": stamp,
        "method": "recomputed from verified local caches via analyze_symbol_volume_coverage; "
                  "observed_max_24h_usd_volume / universe_membership_ok added; all other fields preserved",
        "errors": errors,
    }
    if not dry_run:
        Path(manifest_path).write_text(json.dumps(out, indent=2) + "\n")
    return {"manifest": out, "repaired": True, "errors": errors, "dry_run": dry_run}


def main():
    ap = argparse.ArgumentParser(description="Repair manifest volume_coverage from verified caches")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--require-verified", action="store_true", default=True)
    args = ap.parse_args()
    res = repair_manifest(args.manifest, dry_run=args.dry_run, require_verified=args.require_verified)
    print(f"Repaired {len(res['manifest'].get('symbols', {}))} symbols")
    if res["errors"]:
        print("Errors:", "\n".join(res["errors"]), file=sys.stderr)
    return 0 if not res["errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())