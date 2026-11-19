#!/usr/bin/env python3
"""C25 stage-0 probe — realized funding acquisition feasibility.

C25's cost_taker_funding (PRIMARY) and cost_stress arms require realized per-venue
8h funding history. This probe checks what funding data is already cached under
research_state/cache/<venue>_funding_<window>/ and reports which venues are
funding-available vs UNAVAILABLE_FUNDING (never zero-filled). It emits no verdict
and no inference; it exists solely to justify the funding acquisition step before
any C25 funding-arm cell runs.

Run (from repo root):
  PYTHONPATH=. .venv/bin/python scripts/probe_c25_funding_acquisition.py
"""
from __future__ import annotations

import datetime as dt
import glob
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

STATE = REPO / "research_state"
VENUES = ["okx", "binance_um", "mexc", "bitget"]


def iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _venue_funding(venue: str) -> Dict[str, Any]:
    matches = glob.glob(str(STATE / "cache" / f"{venue}_funding_*"))
    result: Dict[str, Any] = {"venue": venue, "cache_dirs": [],
                              "funding_available": False, "rate_pct_per_hour": None,
                              "manifests": []}
    for cache_dir in sorted(matches):
        cdir = Path(cache_dir)
        result["cache_dirs"].append(str(cdir.relative_to(REPO)))
        mpath = cdir / "funding_manifest.json"
        if mpath.exists():
            try:
                man = json.loads(mpath.read_text())
                result["manifests"].append({
                    "path": str(mpath.relative_to(REPO)),
                    "generated_at_utc": man.get("generated_at_utc"),
                    "rate_pct_per_hour": man.get("funding_rate_pct_per_hour"),
                    "symbols": man.get("symbols"),
                    "window": man.get("window"),
                })
                if man.get("funding_rate_pct_per_hour") is not None:
                    result["funding_available"] = True
                    result["rate_pct_per_hour"] = man["funding_rate_pct_per_hour"]
            except Exception as exc:  # noqa: BLE001
                result["manifests"].append({"path": str(mpath.relative_to(REPO)),
                                            "error": str(exc)})
    return result


def main() -> int:
    report = {
        "schema_version": 1,
        "generated_at_utc": iso_now(),
        "probe": "c25_funding_acquisition",
        "venues": [_venue_funding(v) for v in VENUES],
        "summary": {
            "funding_available": [v for v in VENUES
                                  if _venue_funding(v)["funding_available"]],
            "unavailable_funding": [v for v in VENUES
                                    if not _venue_funding(v)["funding_available"]],
        },
    }
    out = STATE / f"c25_funding_acquisition_probe_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["summary"], indent=2))
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
