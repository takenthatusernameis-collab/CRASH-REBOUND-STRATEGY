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


def _as_volume_number(value: Any) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        try:
            n = float(value)
        except Exception:
            return None
        return n if n == n and n not in (float("inf"), float("-inf")) else None
    try:
        n = float(str(value).strip())
    except Exception:
        return None
    return n if n == n and n not in (float("inf"), float("-inf")) else None


def _validate_symbol_volume_evidence(sym: str, info: Dict[str, Any], floor: float,
                                     errs: List[str]) -> None:
    """Fail-closed spec volume evidence check for provenance consumers.

    Legacy-compatible: manifests lacking requested/effective intent fields are
    accepted when volume_filter_ok is true, min_daily_volume_usd >= floor, and
    observed_min_24h_usd_volume (when present and numeric) >= floor. Manifests
    carrying intent fields must not declare sub-spec requested/effective values.
    """
    volcov = info.get("volume_coverage")
    if not isinstance(volcov, dict):
        errs.append(f"{sym}: missing volume_coverage; cannot prove >= ${floor:g} 24h volume evidence")
        return
    if not volcov.get("volume_filter_ok"):
        errs.append(f"{sym}: volume_filter_ok is not true; spec-compliant volume evidence required")
    req = _as_volume_number(volcov.get("min_daily_volume_usd_requested"))
    eff = _as_volume_number(volcov.get("min_daily_volume_usd_effective"))
    legacy = _as_volume_number(volcov.get("min_daily_volume_usd"))
    eff_or_legacy = eff if eff is not None else legacy
    if eff_or_legacy is None:
        errs.append(f"{sym}: volume_coverage missing numeric min_daily_volume_usd/effective")
    elif eff_or_legacy < floor:
        errs.append(f"{sym}: effective min_daily_volume_usd {eff_or_legacy:g} < required spec floor {floor:g}")
    if req is not None and req < floor:
        errs.append(f"{sym}: requested min_daily_volume_usd {req:g} < required spec floor {floor:g}")
    # Manifest-level intent audit (optional; checked at symbol level context by callers
    # too, but provenance may see request_params via manifest root in future; no-op here).
    observed = _as_volume_number(volcov.get("observed_min_24h_usd_volume"))
    if observed is not None and observed < floor:
        errs.append(f"{sym}: observed_min_24h_usd_volume {observed:g} < required spec floor {floor:g}")


def validate_provenance(manifest: Dict[str, Any], *, require_complete: bool = True,
                        require_real_market_data: bool = True,
                        min_symbols: int = 1,
                        require_spec_volume_floor: Optional[float] = None,
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
    synthetic_detected_actual: List[str] = []
    for sym, info in (symbols.items() if isinstance(symbols, dict) else []):
        if not isinstance(info, dict):
            errs.append(f"{sym}: invalid symbol entry")
            continue
        cov = info.get("coverage") or {}
        synth = info.get("synthetic_check")
        # Fail-closed: a provenance entry that never computed synthetic_check is
        # unverified. A missing field must not be treated as "clean" — real
        # acquisition always populates it (fetch_hyperliquid_candles does).
        if synth is None:
            errs.append(f"{sym}: synthetic_check missing; provenance entry is unverified")
            continue
        if isinstance(synth, dict) and synth.get("is_synthetic"):
            synthetic_detected_actual.append(sym)
            errs.append(f"{sym}: synthetic/flat data series detected ({synth.get('reason')}); not real market evidence")
            continue
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
            # Campaign item 3/4: consumer-boundary volume evidence check. Only
            # when a caller requires a spec-compliant floor (real campaign path).
            # Does not invalidate completeness claim for non-volume callers.
            floor = _as_volume_number(require_spec_volume_floor)
            if floor is not None and floor > 0:
                _validate_symbol_volume_evidence(sym, info, floor, errs)
            complete.append(sym)
        elif require_complete:
            errs.append(f"{sym}: incomplete or error (status={info.get('status')}, observed={cov.get('observed_in_window_bars')}/{cov.get('expected_hourly_bars')})")
    if require_complete and len(complete) != len(symbols):
        errs.append(f"not all symbols complete: {len(complete)}/{len(symbols)}")
    # Campaign item 4: fail-closed summary consistency. Manifest summary fields
    # are evidence labels; when present they must not contradict symbol facts.
    # Optimistic contradictions (summary claims ready/complete but validated facts
    # do not prove it) fail-closed. Stale-pessimistic labels must NOT block when
    # validated facts prove completeness/non-synthetic evidence; consumers recompute
    # from validated symbol facts. Legacy manifests lacking summary/fields remain
    # compatible.
    summary = manifest.get("summary")
    if isinstance(summary, dict):
        if summary.get("ready_for_real_campaign") is True and synthetic_detected_actual:
            errs.append(
                "summary.ready_for_real_campaign=true contradicts synthetic symbol(s): "
                + ",".join(sorted(synthetic_detected_actual))
            )
        if summary.get("ready_for_real_campaign") is True and len(complete) != len(symbols):
            errs.append(
                "summary.ready_for_real_campaign=true optimistic contradiction: validated symbol facts do not prove complete non-synthetic readiness "
                f"(complete={len(complete)}/{len(symbols)} symbols={sorted(symbols.keys())})"
            )
        if summary.get("all_complete") is True and len(complete) != len(symbols):
            errs.append(
                f"summary.all_complete=true contradicts symbol completeness: {len(complete)}/{len(symbols)} complete"
            )
        ssd = summary.get("synthetic_series_detected")
        if isinstance(ssd, list):
            listed = [str(x) for x in ssd]
            actual = sorted(set(synthetic_detected_actual))
            if sorted(set(listed)) != actual:
                errs.append(
                    "summary.synthetic_series_detected inconsistent with symbol synthetic_check facts "
                    f"(listed={sorted(set(listed))} actual={actual})"
                )
            non_synthetic_listed = [s for s in listed if s in symbols and not (isinstance((symbols[s] or {}).get("synthetic_check"), dict) and (symbols[s] or {}).get("synthetic_check", {}).get("is_synthetic"))]
            if non_synthetic_listed:
                errs.append(
                    "summary.synthetic_series_detected lists non-synthetic symbol(s): "
                    + ",".join(sorted(set(non_synthetic_listed)))
                )
    # Also enforce manifest-level request_params intent when present (fail-closed
    # on stale audit fields). Legacy manifests without request_params unaffected.
    floor = _as_volume_number(require_spec_volume_floor)
    if floor is not None and floor > 0 and isinstance(manifest, dict):
        rp = manifest.get("request_params")
        if isinstance(rp, dict):
            g_req = _as_volume_number(rp.get("min_daily_volume_usd_requested"))
            g_eff = _as_volume_number(rp.get("min_daily_volume_usd_effective"))
            if g_req is not None and g_req < floor:
                errs.append(f"manifest request_params.min_daily_volume_usd_requested {g_req:g} < required spec floor {floor:g}")
            if g_eff is not None and g_eff < floor:
                errs.append(f"manifest request_params.min_daily_volume_usd_effective {g_eff:g} < required spec floor {floor:g}")
    # Campaign item 4 residual: summary.complete_symbols / summary.symbols_complete
    # are advisory evidence labels. Fail-closed on OPTIMISTIC contradictions only
    # (summary claims completeness that validated symbol facts do not prove). Do NOT
    # block on stale-pessimistic labels when validated facts prove completeness:
    # consumers must recompute from validated symbol coverage/synthetic/status facts
    # and never trust stale labels over facts, but stale pessimism is not fabricated
    # evidence. Legacy manifests lacking these fields remain compatible.
    if isinstance(summary, dict):
        actual_complete = sorted(set(complete))
        actual_complete_set = set(complete)
        scs = summary.get("complete_symbols")
        if isinstance(scs, list):
            listed_complete = [str(x) for x in scs]
            invalid_listed = [s for s in listed_complete if s not in symbols]
            if invalid_listed:
                errs.append(
                    "summary.complete_symbols lists unknown symbol(s): "
                    + ",".join(sorted(set(invalid_listed)))
                )
            noncomplete_listed = [s for s in listed_complete if s in symbols and s not in actual_complete_set]
            if noncomplete_listed:
                errs.append(
                    "summary.complete_symbols lists incomplete/invalid symbol(s): "
                    + ",".join(sorted(set(noncomplete_listed)))
                )
            # Fail-closed only when summary claims symbols complete that facts do not
            # validate (unknown/noncomplete). Omitting actually-complete symbols is
            # stale-pessimistic and must not block validated-fact completeness.
            optimistic_listed = sorted(set(invalid_listed) | set(noncomplete_listed))
            if optimistic_listed:
                errs.append(
                    "summary.complete_symbols optimistic contradiction: claims complete without validated symbol facts "
                    f"(claimed={sorted(set(listed_complete))} unproven={optimistic_listed} actual_validated={actual_complete})"
                )
        scn = summary.get("symbols_complete")
        if scn is not None:
            try:
                scn_i = int(scn)
            except (TypeError, ValueError):
                errs.append(f"summary.symbols_complete not an integer: {scn!r}")
            else:
                # Fail-closed on optimistic overcount; stale-pessimistic undercount
                # must not block when validated facts prove completeness.
                if scn_i > len(complete):
                    errs.append(
                        f"summary.symbols_complete={scn_i} optimistic contradiction: exceeds validated complete symbol count {len(complete)}"
                    )
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
        synth = v.get("synthetic_check")
        if synth is None:
            continue
        if isinstance(synth, dict) and synth.get("is_synthetic"):
            continue
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


def _candle_signature(c: Dict[str, Any]) -> Any:
    return (c.get("open"), c.get("high"), c.get("low"), c.get("close"), c.get("volume"))


def detect_synthetic_candles(candles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Reject flat / constant-close / synthetic-looking candle series at runtime.

    A real hourly OHLCV series over hundreds of days varies. A series where every
    bar shares the identical (open, high, low, close, volume) signature, or where
    the close is constant while everything else moves, is a placeholder / fabricated
    dataset, not market evidence.

    Returns a dict describing the finding; `is_synthetic` True means the series must
    never be treated as real market data. This is a runtime re-check: it does not
    trust a manifest's synthetic_check flag, it inspects the actual candles.
    """
    n = len(candles)
    if n == 0:
        return {"is_synthetic": True, "reason": "empty_series",
                "distinct_signatures": 0, "bars_checked": 0,
                "distinct_signature_ratio": 0.0}
    signatures = [_candle_signature(c) for c in candles]
    distinct = len(set(signatures))
    closes = [c.get("close") for c in candles]
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


def verify_candles_not_synthetic(
    candles: List[Dict[str, Any]],
    *,
    require_synthetic_check: bool = False,
    raise_on_synthetic: bool = False,
    synthetic_check: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Runtime re-detection of synthetic/flat candle series.

    Never trusts a manifest's synthetic_check flag blindly: the actual candles
    are re-inspected. When `require_synthetic_check` is True the provenance entry
    must carry an explicit synthetic_check dict:

    * missing / non-dict -> unverified, fail-closed (raises ProvenanceError);
    * dict with is_synthetic True -> synthetic evidence, fail-closed (raises
      ProvenanceError when raise_on_synthetic is True, otherwise reported);
    * dict with is_synthetic False/absent -> accepted as verified at the
      provenance layer, then still re-checked against the actual candles.

    Raises ProvenanceError when the series is synthetic (provenance-declared or
    runtime-detected) and `raise_on_synthetic` is True.
    """
    if require_synthetic_check:
        if not isinstance(synthetic_check, dict):
            # A missing field means the provenance was never computed -> not verified.
            raise ProvenanceError(
                "synthetic_check missing from provenance entry; cannot treat as verified real data"
            )
        if synthetic_check.get("is_synthetic"):
            if raise_on_synthetic:
                raise ProvenanceError(
                    f"provenance-declared synthetic candle series detected "
                    f"({synthetic_check.get('reason') or 'unknown'}); "
                    "refusing to treat as real market evidence"
                )
            return {
                "is_synthetic": True,
                "reason": synthetic_check.get("reason") or "provenance_declared_synthetic",
                "distinct_signatures": synthetic_check.get("distinct_signatures"),
                "bars_checked": synthetic_check.get("bars_checked"),
                "distinct_signature_ratio": synthetic_check.get("distinct_signature_ratio"),
                "source": "provenance_manifest",
            }
    res = detect_synthetic_candles(candles)
    if res["is_synthetic"] and raise_on_synthetic:
        raise ProvenanceError(
            f"synthetic/flat candle series detected ({res['reason']}: "
            f"{res['distinct_signatures']}/{res['bars_checked']} distinct signatures); "
            "refusing to treat as real market evidence"
        )
    return res


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
