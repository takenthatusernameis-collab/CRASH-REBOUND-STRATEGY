"""Verification/provenance helpers for real (non-fixture) candle datasets.

Real campaign runs MUST refuse to execute unless provenance indicates verified,
complete coverage for the target window from a documented source. This module
provides machine-checkable validation and gap reporting.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


TARGET_START = "2025-12-20T00:00:00Z"
TARGET_END = "2026-09-28T23:00:00Z"


class ProvenanceError(ValueError):
    pass


def _parse_iso(s: str) -> datetime:
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def expected_hourly_bars(start_iso: str = TARGET_START, end_iso: str = TARGET_END) -> int:
    s = int(_parse_iso(start_iso).timestamp() * 1000)
    e = int(_parse_iso(end_iso).timestamp() * 1000)
    return max(0, int((e - s) / 3_600_000) + 1)


def load_provenance(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise ProvenanceError(f"Provenance manifest missing: {p}")
    try:
        return json.loads(p.read_text())
    except Exception as e:
        raise ProvenanceError(f"Invalid provenance manifest JSON: {e}") from e


def validate_provenance(manifest: Dict[str, Any], *, require_complete: bool = True,
                        require_real_market_data: bool = True,
                        min_symbols: int = 1,
                        start: str = TARGET_START, end: str = TARGET_END) -> Tuple[bool, List[str]]:
    errs: List[str] = []
    if not isinstance(manifest, dict):
        return False, ["manifest must be an object"]
    if manifest.get("fabricated_data") is True:
        errs.append("fabricated_data=true is prohibited for real runs")
    if require_real_market_data and not manifest.get("real_market_data_intended", True):
        errs.append("manifest not marked as intended real market data")
    tw = manifest.get("target_window") or {}
    if tw.get("start") and _parse_iso(tw["start"]) != _parse_iso(start):
        errs.append(f"target_window.start mismatch: {tw.get('start')} != {start}")
    if tw.get("end") and _parse_iso(tw["end"]) != _parse_iso(end):
        errs.append(f"target_window.end mismatch: {tw.get('end')} != {end}")
    exp = expected_hourly_bars(start, end)
    if tw.get("expected_hourly_bars") not in (None, exp):
        errs.append(f"expected_hourly_bars mismatch: {tw.get('expected_hourly_bars')} != {exp}")
    symbols = manifest.get("symbols") or {}
    if not isinstance(symbols, dict) or len(symbols) < min_symbols:
        errs.append(f"insufficient symbols in manifest (need >= {min_symbols})")
    complete = []
    for sym, info in (symbols.items() if isinstance(symbols, dict) else []):
        if not isinstance(info, dict):
            errs.append(f"{sym}: invalid symbol entry")
            continue
        cov = info.get("coverage") or {}
        if info.get("status") == "ok" and cov.get("complete_for_target_window") is True:
            # verify coverage fields
            if cov.get("expected_hourly_bars") != exp:
                errs.append(f"{sym}: expected_hourly_bars {cov.get('expected_hourly_bars')} != {exp}")
                continue
            if cov.get("observed_in_window_bars") != exp:
                errs.append(f"{sym}: observed_in_window_bars != expected")
                continue
            if (cov.get("gap_count") or 0) != 0:
                errs.append(f"{sym}: gap_count != 0")
                continue
            complete.append(sym)
        elif require_complete:
            errs.append(f"{sym}: incomplete or error (status={info.get('status')}, observed={cov.get('observed_in_window_bars')}/{cov.get('expected_hourly_bars')})")
    if require_complete and len(complete) != len(symbols):
        errs.append(f"not all symbols complete: {len(complete)}/{len(symbols)}")
    if len(complete) < min_symbols:
        errs.append(f"complete symbols {len(complete)} < {min_symbols}")
    return (len(errs) == 0), errs


def require_verified_provenance(manifest_path: str | Path, **kwargs) -> Dict[str, Any]:
    manifest = load_provenance(manifest_path)
    ok, errs = validate_provenance(manifest, **kwargs)
    if not ok:
        raise ProvenanceError("Real campaign blocked by provenance/coverage validation:\n- " + "\n- ".join(errs))
    return manifest
