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
from typing import Any, Dict, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars, load_provenance, ProvenanceError, _parse_iso  # noqa: E402


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


def build_gap_report(*, manifest: Optional[Dict[str, Any]], probe_evidence: Any = None,
                     generated_at_utc: Optional[str] = None, archive_scan: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
        probe_unsafe = (not bool(out["probe_summary"]["all_complete"])) or int(out["probe_summary"].get("expected_mismatch_symbols", 0) or 0) > 0
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
    summary = manifest.get("summary") or {}
    out["all_complete"] = bool(summary.get("all_complete")) and out["target_window_consistent_with_spec"]
    out["ready_for_real_campaign"] = bool(summary.get("ready_for_real_campaign")) and out["target_window_consistent_with_spec"]
    for sym, info in (manifest.get("symbols") or {}).items():
        if not isinstance(info, dict):
            continue
        cov = info.get("coverage") or {}
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
        }
    # Probe evidence is informational but must never make the report optimistic.
    # Any incomplete/mismatched probe forces blocked (safety over optimism).
    if probe_unsafe:
        out["ready_for_real_campaign"] = False
        out["all_complete"] = False
        out["blocker"]["item_6c_blocked"] = True
        if int((out.get("probe_summary") or {}).get("expected_mismatch_symbols", 0) or 0) > 0:
            out["blocker"]["reason"] = "Probe evidence expected-bar count mismatches spec target window; cannot confirm readiness."
    if out["ready_for_real_campaign"] and out["target_window_consistent_with_spec"] and not probe_unsafe:
        out["blocker"]["item_6c_blocked"] = False
        out["blocker"]["reason"] = "Manifest indicates complete verified coverage; run gated real campaign."
    out["blocked"] = bool(out["blocker"]["item_6c_blocked"])
    out["item_6c_blocked"] = bool(out["blocker"]["item_6c_blocked"])
    return out


def _probe_symbols(probe_evidence: Any) -> Dict[str, Any]:
    probe_syms: Dict[str, Any] = {}
    if isinstance(probe_evidence, dict):
        probe_syms = probe_evidence.get("symbols") or {}
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
    ap.add_argument("--archive-searched", nargs="*", default=[])
    args = ap.parse_args()
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
                              archive_scan={"searched_paths": args.archive_searched, "verified_archives_found": []})
    write_gap_report(Path(args.output), report)
    print(json.dumps({"wrote": str(args.output), "ready_for_real_campaign": report["ready_for_real_campaign"], "blocked": report["blocker"]["item_6c_blocked"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
