#!/usr/bin/env python3
"""Generate canonical candle coverage/gap report for ITEM 6c (283d Hyperliquid).

Deterministic, evidence-oriented. Never fabricates data and never marks readiness
when provenance/coverage is incomplete. Used to replace stale/incorrect reports.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars, load_provenance, ProvenanceError, _parse_iso  # noqa: E402
from src.strategy.config import SPEC_MIN_DAILY_VOLUME_USD  # noqa: E402

# Default documented path searched for a verified 283d archive. Kept to the
# canonical research_state/archives location only: scanning broad system trees
# (/tmp, /home/runner/work, /opt, ...) made build_gap_report() hang the test
# suite and produced no verified archives. Extensible via --archive-searched.
archive_scan_paths: List[str] = [
    str(REPO_ROOT / "research_state" / "archives"),
]


def _volume_coverage_spec_compliant(volume_coverage: Any) -> tuple[bool, str, bool]:
    """Fail-closed spec-volume evidence check for gap-report readiness decisions.

    Campaign item 3/4: stale/sub-spec volume fields must never make the report
    optimistic. Missing evidence is non-compliant.

    Returns (ok, reason, present). `present` is True only when the caller supplied
    a volume_coverage field (even None) to be judged; when the field is absent from
    the manifest entry entirely (legacy shape), present=False and ok=True so the
    report defers to the manifest's own summary rather than inventing a block.
    """
    if volume_coverage is None:
        return False, "volume_coverage present but null (not spec-compliant evidence)", True
    if not isinstance(volume_coverage, dict):
        return False, "volume_coverage present but not an object (not spec-compliant evidence)", True
    if not volume_coverage.get("volume_filter_ok"):
        return False, "volume_filter_ok is not true", True
    floor = float(SPEC_MIN_DAILY_VOLUME_USD)
    def _num(key):
        v = volume_coverage.get(key)
        if v is None:
            return None
        try:
            return float(v)
        except Exception:
            return None
    req = _num("min_daily_volume_usd_requested")
    eff = _num("min_daily_volume_usd_effective")
    eff_or_legacy = eff if eff is not None else _num("min_daily_volume_usd")
    if eff_or_legacy is None:
        return False, "present volume_coverage missing numeric min_daily_volume_usd/effective", True
    if eff_or_legacy < floor:
        return False, f"effective min_daily_volume_usd {eff_or_legacy:g} < spec floor {floor:g}", True
    # Fail closed on provenance intent: a sub-spec request means artifact was not
    # produced under clean spec-compliant volume intent, even if floored.
    if req is not None and req < floor:
        return False, f"requested min_daily_volume_usd {req:g} < spec floor {floor:g}", True
    return True, "ok", True



def _normalize_iso(ts: Any) -> str:
    if not isinstance(ts, str):
        return ""
    try:
        dt = _parse_iso(ts)
        if dt is None:
            return ts.strip()
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return ts.strip()


def _probe_summary(probe_syms: Dict[str, Any], exp: int) -> Dict[str, Any]:
    vals = [bool(v.get("complete")) if isinstance(v, dict) else False for v in probe_syms.values()]
    mismatch = 0
    for v in probe_syms.values():
        if not isinstance(v, dict):
            continue
        pe = v.get("expected") if "expected" in v else v.get("expected_hourly_bars")
        if pe is not None and int(pe) != int(exp):
            mismatch += 1
    return {
        "symbols_probed": len(vals),
        "all_complete": all(vals) and bool(vals),
        "any_complete": any(vals),
        "target_expected_bars": int(exp),
        "expected_mismatch_symbols": int(mismatch),
    }


def _probe_gap_summary(probe_syms: Dict[str, Any], exp: int) -> Dict[str, Any]:
    """Per-symbol probe gap evidence (missing bars). Backward-compatible evidence field."""
    out: Dict[str, Any] = {}
    for sym, v in probe_syms.items():
        if not isinstance(v, dict):
            continue
        count = v.get("count") if v.get("count") is not None else v.get("observed_in_window_bars")
        try:
            count_i = int(count) if count is not None else 0
        except Exception:
            count_i = 0
        out[sym] = {
            "count": count_i,
            "expected": int(exp),
            "missing_bars": max(0, int(exp) - count_i),
            "complete": bool(v.get("complete")),
        }
        for k in ("first_t_ms", "last_t_ms", "probed_at_utc"):
            if k in v:
                out[sym][k] = v[k]
    return out


def _scan_archives(searched_paths) -> Dict[str, Any]:
    """Scan documented paths for candidate archives and verify each one.

    A candidate is any .parquet/.json/.csv/.ndjson/.jsonl file. Each is probed for
    per-symbol hourly coverage of the spec target window AND for synthetic/flat
    content. Only archives that are complete, non-synthetic, and timestamped inside
    the target window are reported as verified. Never fabricates; an archive that
    fails any check is reported as rejected with the reason.
    """
    import hashlib
    from scripts.fetch_hyperliquid_candles import detect_synthetic_candles, _read_symbol_candles_from_file
    from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars

    exp = expected_hourly_bars(TARGET_START, TARGET_END)
    start_ms = int(_parse_iso(TARGET_START).timestamp() * 1000)
    end_ms = int(_parse_iso(TARGET_END).timestamp() * 1000)
    found: List[Dict[str, Any]] = []
    seen_files = set()
    for base in searched_paths or []:
        try:
            bp = Path(base)
            if not bp.exists():
                continue
            if bp.is_file():
                files = [bp]
            else:
                try:
                    files = sorted([f for f in bp.rglob("*") if f.is_file()])
                except Exception:
                    files = []
        except Exception:
            continue
        for f in files:
            try:
                key = str(f.resolve())
            except Exception:
                key = str(f)
            if key in seen_files:
                continue
            seen_files.add(key)
            try:
                if f.suffix.lower() not in (".parquet", ".json", ".csv", ".ndjson", ".jsonl"):
                    continue
            except Exception:
                continue
            entry: Dict[str, Any] = {"path": str(f)}
            try:
                file_hash = hashlib.sha256()
                with f.open("rb") as fh:
                    for chunk in iter(lambda: fh.read(1 << 20), b""):
                        file_hash.update(chunk)
                entry["sha256"] = file_hash.hexdigest()
            except Exception as e:
                entry["error"] = f"unreadable_skipped: {type(e).__name__}: {e}"
                entry["verified"] = False
                entry["verdict"] = "unreadable_skipped"
                found.append(entry)
                continue
            try:
                symbols = {}
                all_complete = True
                any_synth = False
                probe_syms = ["BTC", "ETH"]
                for sym in probe_syms:
                    try:
                        candles, _meta = _read_symbol_candles_from_file(f, sym)
                    except Exception:
                        continue
                    if not candles:
                        continue
                    inwin = [c for c in candles
                             if (c.get("timestamp_ms") or _ts_from_ts(c)) is not None
                             and start_ms <= (c.get("timestamp_ms") or _ts_from_ts(c)) <= end_ms]
                    synth = detect_synthetic_candles(inwin)
                    complete = len(inwin) == exp and not synth.get("is_synthetic")
                    symbols[sym] = {"bars_in_window": len(inwin), "expected": exp,
                                    "complete": bool(complete), "synthetic": bool(synth.get("is_synthetic"))}
                    if synth.get("is_synthetic"):
                        any_synth = True
                    if not complete:
                        all_complete = False
                entry["symbols"] = symbols
                entry["all_complete"] = bool(all_complete and len(symbols) > 0 and not any_synth)
                entry["synthetic_detected"] = bool(any_synth)
                entry["verified"] = bool(entry["all_complete"])
                entry["verdict"] = ("verified_complete_non_synthetic" if entry["verified"]
                                    else "synthetic_or_incomplete_rejected")
            except Exception as e:
                entry["error"] = f"{type(e).__name__}: {e}"
                entry["verified"] = False
                entry["verdict"] = "probe_error_rejected"
            found.append(entry)
    verified = [e for e in found if e.get("verified")]
    return {"searched_paths": list(searched_paths or []), "candidate_archives": found,
            "verified_archives_found": [e["path"] for e in verified]}


def _ts_from_ts(c):
    ts = c.get("timestamp")
    if isinstance(ts, str):
        try:
            return int(_parse_iso(ts).timestamp() * 1000)
        except Exception:
            return None
    return None


def build_gap_report(*, manifest: Optional[Dict[str, Any]], probe_evidence: Any = None,
                     generated_at_utc: Optional[str] = None, archive_scan: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if archive_scan is None:
        archive_scan = _scan_archives(archive_scan_paths)
    elif isinstance(archive_scan, dict):
        # Honor precomputed archive_scan (tests/callers) to avoid expensive scans.
        has_precomputed = ("candidate_archives" in archive_scan) or ("verified_archives_found" in archive_scan)
        sp = archive_scan.get("searched_paths")
        if not has_precomputed and sp is not None:
            archive_scan = _scan_archives(sp)
        # else: use as-is
    exp = expected_hourly_bars(TARGET_START, TARGET_END)
    ts = generated_at_utc or datetime.now(timezone.utc).isoformat()
    spec_window = {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": exp}
    out: Dict[str, Any] = {
        "generated_at_utc": ts,
        "report_type": "candle_coverage_gap_report",
        "item": "6c_real_283d_hyperliquid_campaign",
        "target_window": dict(spec_window),
        "real_market_data": True,
        "fabricated_data": False,
        "ready_for_real_campaign": False,
        "all_complete": False,
        "blocked": True,
        "item_6c_blocked": True,
        "symbols": {},
        "probe_evidence": probe_evidence,
        "archive_scan": archive_scan or {"searched_paths": [], "verified_archives_found": []},
        "target_window_consistent_with_spec": True,
        "blocker": {
            "item_6c_blocked": True,
            "reason": "Insufficient verified 283-day hourly coverage/provenance for required universe.",
            "required_to_unblock": [
                "Verified archive or API coverage delivering 6792/6792 hourly bars per required symbol for 2025-12-20T00:00:00Z→2026-09-28T23:00:00Z",
                "Documented source/extraction, checksums, provenance.json all_complete=true ready_for_real_campaign=true",
                "Spec-relevant >=$5M 24h volume universe derived/reconciled from verified data",
            ],
        },
    }
    probe_syms = _probe_symbols(probe_evidence)
    probe_unsafe = False
    if probe_syms:
        out["probe_summary"] = _probe_summary(probe_syms, exp)
        out["probe_gap_summary"] = _probe_gap_summary(probe_syms, exp)
        probe_unsafe = (not bool(out["probe_summary"]["all_complete"])) or int(out["probe_summary"].get("expected_mismatch_symbols", 0) or 0) > 0
    else:
        out["probe_gap_summary"] = None
    if not manifest:
        out["manifest_path"] = None
        out["manifest_error"] = "manifest_missing_or_unreadable"
        if probe_unsafe:
            out["ready_for_real_campaign"] = False
            out["all_complete"] = False
            out["blocked"] = True
            out["item_6c_blocked"] = True
            out["blocker"]["item_6c_blocked"] = True
        return out
    tw = manifest.get("target_window") or {}
    tw_start = _normalize_iso(tw.get("start"))
    tw_end = _normalize_iso(tw.get("end"))
    spec_start = _normalize_iso(TARGET_START)
    spec_end = _normalize_iso(TARGET_END)
    if tw and (tw_start != spec_start or tw_end != spec_end or tw.get("expected_hourly_bars") != exp):
        out["target_window_consistent_with_spec"] = False
        out["manifest_target_window"] = {"start": tw.get("start"), "end": tw.get("end"), "expected_hourly_bars": tw.get("expected_hourly_bars")}
        out["blocker"]["item_6c_blocked"] = True
        out["blocker"]["target_window_mismatch"] = True
        out["blocker"]["reason"] = ("Manifest target_window does not match spec target window "
                                    f"{TARGET_START}→{TARGET_END} ({exp} bars); report may be stale — regenerate before use.")
        out["ready_for_real_campaign"] = False
        out["all_complete"] = False
    else:
        out["blocker"]["target_window_mismatch"] = False
    # Campaign item 4: fail-closed on contradictory manifest summary labels.
    # Recompute readiness-critical facts from validated symbol data; never trust a
    # summary that contradicts symbol synthetic/coverage facts.
    summary = manifest.get("summary") or {}
    contradiction_errors: List[str] = []
    # Compute all_complete from actual symbol facts (authoritative over summary).
    # synthetic_check missing = unknown for legacy manifests (not positive evidence
    # of synthetic); is_synthetic=true is a hard contradiction.
    syms = manifest.get("symbols") or {}
    actual_complete = []
    actual_synthetic = []
    for sym, info in syms.items():
        if not isinstance(info, dict):
            continue
        cov = info.get("coverage") or {}
        synth = info.get("synthetic_check")
        if cov.get("complete_for_target_window") is True:
            actual_complete.append(sym)
        if isinstance(synth, dict) and synth.get("is_synthetic") is True:
            actual_synthetic.append(sym)
    computed_all_complete = bool(syms) and len(actual_complete) == len(syms) and not actual_synthetic

    try:
        from src.data.provenance import validate_provenance
        v_ok, v_errs = validate_provenance(manifest, require_complete=False, require_spec_volume_floor=None)
        if not v_ok:
            # Keep only summary-contradiction errors that align with computed facts
            # (e.g. summary claims all_complete/ready while synthetic symbols exist,
            # or while computed completeness disagrees). Ignore unrelated structural/
            # unverified-entry noise for gap-report summary labeling.
            for e in v_errs:
                if "summary.ready_for_real_campaign" in e and actual_synthetic:
                    contradiction_errors.append(e)
                elif "summary.all_complete" in e and not computed_all_complete:
                    contradiction_errors.append(e)
                elif "summary.synthetic_series_detected" in e:
                    contradiction_errors.append(e)
            structural = [e for e in v_errs if e not in contradiction_errors and "summary." not in e and "contradict" not in e.lower() and "inconsistent" not in e.lower()]
            if structural and not syms:
                out["manifest_structural_errors"] = structural
    except Exception as e:
        contradiction_errors = [f"summary validation failed: {e}"]

    # Summary booleans are advisory labels only. Recompute readiness-critical facts
    # from validated symbol data; never make the report optimistic from summary, and
    # never keep it pessimistic when validated facts prove the target window is complete,
    # non-synthetic, and spec-consistent. Missing/invalid summary fields therefore do not
    # block by themselves when facts are clean.
    summary_all_complete = summary.get("all_complete")
    summary_ready = summary.get("ready_for_real_campaign")
    out["all_complete"] = computed_all_complete and out["target_window_consistent_with_spec"]
    # Ready is a fact derived from validated symbol evidence + spec-consistent target window.
    # Volume/probe/other fail-closed gates below may still block it.
    out["ready_for_real_campaign"] = computed_all_complete and out["target_window_consistent_with_spec"]
    if computed_all_complete and out["target_window_consistent_with_spec"] and not contradiction_errors and not actual_synthetic:
        out["blocker"]["item_6c_blocked"] = False
        out["blocker"]["reason"] = "Manifest indicates complete verified coverage for spec target window (validated from symbol facts)."
    stale_optimistic_summary = (
        (summary_all_complete is True and not computed_all_complete)
        or (summary_ready is True and (not computed_all_complete or actual_synthetic))
    )
    if contradiction_errors or actual_synthetic or stale_optimistic_summary:
        out["ready_for_real_campaign"] = False
        out["all_complete"] = computed_all_complete and out["target_window_consistent_with_spec"] and not contradiction_errors
        out["manifest_summary_contradiction"] = True
        out["summary_contradiction_errors"] = contradiction_errors
        out["summary_contradiction_actual_synthetic_symbols"] = actual_synthetic
        out["blocker"]["item_6c_blocked"] = True
        reason = "; ".join(contradiction_errors[:4]) if contradiction_errors else (
            f"synthetic symbols present: {actual_synthetic}" if actual_synthetic else "manifest summary contradicts validated symbol facts"
        )
        out["blocker"]["reason"] = f"Manifest summary contradicts validated symbol facts (fail-closed): {reason}"
    volume_issues: Dict[str, str] = {}
    volume_absent: List[str] = []
    for sym, info in (manifest.get("symbols") or {}).items():
        if not isinstance(info, dict):
            continue
        cov = info.get("coverage") or {}
        if "volume_coverage" not in info:
            vol_ok, vol_reason, vol_present = True, "volume_coverage absent (legacy manifest; deferred to summary)", False
        else:
            vol_ok, vol_reason, vol_present = _volume_coverage_spec_compliant(info.get("volume_coverage"))
        out["symbols"][sym] = {
            "status": info.get("status"),
            "observed_in_window_bars": cov.get("observed_in_window_bars"),
            "expected_hourly_bars": cov.get("expected_hourly_bars"),
            "complete_for_target_window": cov.get("complete_for_target_window"),
            "gap_count": cov.get("gap_count"),
            "first_timestamp": cov.get("first_timestamp"),
            "last_timestamp": cov.get("last_timestamp"),
            "first_timestamp_ms": cov.get("first_timestamp_ms"),
            "last_timestamp_ms": cov.get("last_timestamp_ms"),
            "sha256": info.get("sha256"),
            "cache_path": info.get("cache_path"),
            "volume_coverage": info.get("volume_coverage"),
            "volume_coverage_present": bool(vol_present),
            "volume_floor_compliant": bool(vol_ok),
            "volume_floor_reason": vol_reason,
        }
        if not vol_present:
            # Legacy manifest entry: no volume_coverage field at all. Defer to the
            # manifest's own summary rather than inventing a block here.
            volume_absent.append(sym)
        elif not vol_ok:
            volume_issues[sym] = vol_reason
    if (manifest.get("symbols") or {}):
        out["volume_floor_compliant"] = len(volume_issues) == 0
        out["volume_floor_issues"] = volume_issues
        out["volume_coverage_absent_symbols"] = volume_absent
    else:
        out["volume_floor_compliant"] = False
        out["volume_floor_issues"] = {"_manifest": "no symbols in manifest"}
    if volume_issues:
        out["ready_for_real_campaign"] = False
        out["all_complete"] = False
        out["blocker"]["item_6c_blocked"] = True
        out["blocker"]["volume_floor_compliant"] = False
        detail = "; ".join(f"{s}: {r}" for s, r in list(volume_issues.items())[:8]) or "missing spec-compliant volume evidence"
        out["blocker"]["reason"] = f"Manifest/provenance volume evidence is not spec-compliant (>=${float(SPEC_MIN_DAILY_VOLUME_USD):g} required, fail-closed): {detail}"
    # Probe evidence is informational but must never make the report optimistic.
    # Any incomplete/mismatched probe forces blocked (safety over optimism).
    if probe_unsafe:
        out["ready_for_real_campaign"] = False
        out["all_complete"] = False
        out["blocker"]["item_6c_blocked"] = True
        if int((out.get("probe_summary") or {}).get("expected_mismatch_symbols", 0) or 0) > 0:
            out["blocker"]["reason"] = "Probe evidence expected-bar count mismatches spec target window; cannot confirm readiness."
    if out["ready_for_real_campaign"] and out["target_window_consistent_with_spec"] and not probe_unsafe and out.get("volume_floor_compliant"):
        out["blocker"]["item_6c_blocked"] = False
        out["blocker"]["volume_floor_compliant"] = True
        out["blocker"]["reason"] = "Manifest indicates complete verified coverage with spec-compliant volume floor evidence; run gated real campaign."
    out["blocked"] = bool(out["blocker"]["item_6c_blocked"])
    out["item_6c_blocked"] = bool(out["blocker"]["item_6c_blocked"])
    return out


def _probe_symbols(probe_evidence: Any) -> Dict[str, Any]:
    probe_syms: Dict[str, Any] = {}
    if isinstance(probe_evidence, dict):
        probe_syms = probe_evidence.get("symbols") or probe_evidence.get("full") or {}
    elif isinstance(probe_evidence, list):
        for row in probe_evidence:
            if isinstance(row, dict) and row.get("symbol"):
                probe_syms[row["symbol"]] = row
    return probe_syms if isinstance(probe_syms, dict) else {}


def write_gap_report(path: Path, report: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=False) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(REPO_ROOT / "research_state/cache/hyperliquid/provenance.json"))
    ap.add_argument("--output", default=str(REPO_ROOT / "research_state/candle_coverage_gap_report.json"))
    ap.add_argument("--probe-json", default=None, help="Optional JSON string/file path with latest probe evidence")
    ap.add_argument("--archive-searched", nargs="*", default=None,
                    help="Documented paths to scan for a verified archive. Defaults to canonical set.")
    args = ap.parse_args()
    scan_paths = args.archive_searched if args.archive_searched is not None else archive_scan_paths
    manifest = None
    try:
        manifest = load_provenance(args.manifest)
    except ProvenanceError:
        manifest = None
    probe = None
    if args.probe_json:
        pj = Path(args.probe_json)
        probe = json.loads(pj.read_text() if pj.exists() else args.probe_json)
    report = build_gap_report(manifest=manifest, probe_evidence=probe,
                              archive_scan={"searched_paths": scan_paths})
    write_gap_report(Path(args.output), report)
    print(json.dumps({"wrote": str(args.output), "ready_for_real_campaign": report["ready_for_real_campaign"], "blocked": report["blocker"]["item_6c_blocked"], "verified_archives_found": (report.get("archive_scan") or {}).get("verified_archives_found")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
