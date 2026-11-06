"""Verification/provenance helpers for real (non-fixture) candle datasets.

Real campaign runs MUST refuse to execute unless provenance indicates verified,
complete coverage for the target window from a documented source. This module
provides machine-checkable validation and gap reporting.
"""
from __future__ import annotations

import hashlib
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
            # verify coverage fields for any symbol claiming completeness
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


def _complete_symbol_subset_safe(manifest: Dict[str, Any], *, start: str = TARGET_START, end: str = TARGET_END) -> Dict[str, Any]:
    """Return a manifest view containing only symbols verified complete for the target window.

    Conservative/safe: only includes symbols with status==ok and coverage fields proving
    completeness against expected bars for the window. Malformed entries excluded.
    """
    if not isinstance(manifest, dict):
        return {"symbols": {}, "summary": {"complete_symbols_subset": [], "complete_symbols_subset_count": 0}}
    syms = manifest.get("symbols") or {}
    exp = expected_hourly_bars(start, end)
    complete: Dict[str, Any] = {}
    for k, v in (syms.items() if isinstance(syms, dict) else []):
        if not isinstance(v, dict):
            continue
        cov = v.get("coverage") or {}
        if (
            v.get("status") == "ok"
            and cov.get("complete_for_target_window") is True
            and cov.get("expected_hourly_bars") == exp
            and cov.get("observed_in_window_bars") == exp
            and (cov.get("gap_count") or 0) == 0
        ):
            complete[k] = v
    out = dict(manifest)
    out["symbols"] = complete
    out["summary"] = dict(manifest.get("summary") or {})
    out["summary"]["complete_symbols_subset"] = sorted(complete.keys())
    out["summary"]["complete_symbols_subset_count"] = len(complete)
    return out


def complete_symbol_subset(manifest: Dict[str, Any], *, start: str = TARGET_START, end: str = TARGET_END) -> Dict[str, Any]:
    """Public alias for safe complete-subset extraction (testable, deterministic)."""
    return _complete_symbol_subset_safe(manifest, start=start, end=end)


def sha256_file(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_cache_sha256(path: str | Path, expected: Optional[str], symbol: str) -> None:
    """If manifest provides expected sha256, verify cached file bytes match.

    Backward compatible: no expected value -> no-op. Mismatch raises ProvenanceError
    with concrete evidence (never silent)."""
    if expected is None:
        return
    exp = str(expected).strip()
    if not exp:
        return
    actual = sha256_file(path)
    if actual != exp:
        raise ProvenanceError(
            f"Cache checksum mismatch for {symbol}: file={path} "
            f"expected_sha256={exp} actual_sha256={actual}. "
            "Refusing to use tampered/corrupted cache; re-fetch or restore verified archive."
        )


def require_verified_provenance(manifest_path: str | Path, **kwargs) -> Dict[str, Any]:
    manifest = load_provenance(manifest_path)
    ok, errs = validate_provenance(manifest, **kwargs)
    if not ok:
        raise ProvenanceError("Real campaign blocked by provenance/coverage validation:\n- " + "\n- ".join(errs))
    return manifest
