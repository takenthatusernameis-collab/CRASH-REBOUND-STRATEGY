#!/usr/bin/env python3
"""C14-T3 bootstrap: build the in-scope symbol list for universe derivation.

The Ironflow wide archive legitimately contains short-lived perps (a coin that
lists or is delisted mid-window) alongside the durable universe. The manifest's
completeness gate is correct for a *scoped* campaign but must not be applied to
the raw archive: requiring every one of 195 symbols to be complete would reject
a dataset that has nothing wrong with its 146 durable symbols.

This script reads the C14 provenance manifest and emits the subset of symbols
that are simultaneously:
  * status == "ok"
  * coverage complete for the target window (observed == expected, gap_count == 0)
  * not synthetic (manifest synthetic_check clean)

The output is consumed by `derive_verified_universe.py --universe-file` so the
completeness gate scopes to exactly the durable universe. Volume membership is
still recomputed by the derivation (peak rolling-24h >= $5M), so this scope is
coverage-only and never relaxes the spec volume floor.

Usage:
  PYTHONPATH=. python scripts/build_c14_universe_scope.py \
      --manifest research_state/cache/hyperliquid_ironflow_wide_<TS>/provenance.json \
      --output research_state/universe_scope_hyperliquid_ironflow_wide_<TS>.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from src.data.provenance import load_provenance  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--min-symbols", type=int, default=24)
    args = ap.parse_args(argv)

    m = load_provenance(args.manifest)
    tw = m.get("target_window") or {}
    from src.data.provenance import expected_hourly_bars  # noqa: E402
    exp = expected_hourly_bars(tw.get("start"), tw.get("end"))

    scope = []
    skipped = []
    for sym, info in (m.get("symbols") or {}).items():
        if not isinstance(info, dict):
            skipped.append((sym, "invalid entry"))
            continue
        cov = info.get("coverage") or {}
        synth = info.get("synthetic_check")
        if info.get("status") != "ok":
            skipped.append((sym, f"status={info.get('status')}"))
            continue
        if cov.get("complete_for_target_window") is not True:
            skipped.append((sym, "incomplete coverage"))
            continue
        if cov.get("expected_hourly_bars") != exp:
            skipped.append((sym, "coverage window mismatch"))
            continue
        if (cov.get("gap_count") or 0) != 0:
            skipped.append((sym, f"gap_count={cov.get('gap_count')}"))
            continue
        if not isinstance(synth, dict) or synth.get("is_synthetic"):
            skipped.append((sym, "synthetic"))
            continue
        scope.append(sym)

    scope = sorted(scope)
    out = {
        "schema_version": 1,
        "generated_at_utc": m.get("generated_at_utc"),
        "run_type": "c14_universe_scope",
        "source_manifest": str(Path(args.manifest).resolve()),
        "target_window": tw,
        "scope_method": (
            "coverage-complete, non-synthetic, status==ok symbols from the C14 "
            "manifest. Volume membership is NOT decided here; "
            "derive_verified_universe.py recomputes peak rolling-24h >= $5M."
        ),
        "symbols": scope,
        "scope_count": len(scope),
        "skipped": {s: r for s, r in skipped},
    }
    Path(args.output).write_text(json.dumps(out, indent=2) + "\n")
    print(f"scope: {len(scope)} symbols; skipped {len(skipped)}")
    if len(scope) < args.min_symbols:
        print(f"ERROR: scope {len(scope)} < min_symbols {args.min_symbols}", file=sys.stderr)
        return 2
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())