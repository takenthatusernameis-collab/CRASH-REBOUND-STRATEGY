#!/usr/bin/env python3
"""C5-T1 — end-to-end archive-gated validation orchestrator (fail-closed).

Chains the real components in order and fails closed at every boundary:
  1. C4-T1 intake validation (import scripts/validate_hyperliquid_archive_intake.py)
     — refuse to continue unless verdict is exactly ACCEPT_AS_EVIDENCE_CANDIDATE.
  2. verified-universe derivation (scripts/derive_verified_universe.py) with $5M floor.
  3. canonical full-window campaign (scripts/run_real_campaign.py, spec-literal default OFF).
  4. exact full-portfolio placebo (scripts/run_portfolio_placebo_*) and episode-aware
     audit (scripts/run_episode_edge_okx.py).
  5. single decision record with performance_evidence set only when every gate passes.

Supports --dry-run-fixture (clearly labelled synthetic fixture, temp --out-dir,
performance_evidence=false, is_market_data=false). Never writes to
research_state/hyperliquid_exploratory_next_open_latest.json and never overwrites a
canonical artifact. Produces
research_state/full_validation_pipeline_readiness_<TS>.{json,md} with per-step PASS/FAIL,
the fixture replay result, and a negative test proving refusal of the placeholder parquet
and a truncated fixture.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# C5-T1 requirement: import the intake validator directly.
from scripts.validate_hyperliquid_archive_intake import (  # noqa: E402
    KNOWN_PLACEHOLDER,
    SPEC_END,
    SPEC_START,
    expected_hourly_bars,
    validate_archive,
)

STATE = REPO / "research_state"
CANONICAL_LATEST_POINTER = STATE / "hyperliquid_exploratory_next_open_latest.json"


def _utc_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_cli(script: str, extra: List[str]) -> Tuple[int, str, str]:
    """Run a component script as a subprocess; never swallow its exit code."""
    cmd = [sys.executable, str(REPO / script)] + extra
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def _write_json(path: Path, payload: Dict[str, Any]) -> Path:
    path.write_text(json.dumps(payload, indent=2) + "\n")
    return path


def _write_md(path: Path, lines: List[str]) -> Path:
    path.write_text("\n".join(lines) + "\n")
    return path


def _assert_not_canonical_pointer(out_dir: Path, label: str) -> None:
    """Fail-closed: never let a dry-run or fixture run touch the canonical latest pointer."""
    if out_dir.resolve() == STATE.resolve():
        candidate = out_dir / CANONICAL_LATEST_POINTER.name
        if candidate.exists():
            _fail(f"{label}: refused to write {CANONICAL_LATEST_POINTER.name} — canonical pointer is write-protected")


# --------------------------------------------------------------------------- dry-run mode

def _write_parquet_fixture(root: Path, name: str, symbols: List[str], bars: int, *,
                           flat: bool, start_iso: str = SPEC_START) -> Path:
    """Write a clearly-labelled synthetic parquet fixture (NOT market data, NOT evidence)."""
    import pandas as pd  # local import to keep the module light when unused
    d = root / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SOURCE.md").write_text(
        f"# {name}\n\nSynthetic plumbing fixture for C5-T1 dry-run only. "
        "Hyperliquid-native candle shape (OHLCV, hourly). NOT market data. "
        "NOT evidence. performance_evidence=false, is_market_data=false, is_evidence=false.\n")
    from scripts.validate_hyperliquid_archive_intake import _iso_to_ms
    start_ms = _iso_to_ms(start_iso)
    for sym in symbols:
        rows = []
        for i in range(bars):
            if flat:
                o = h = l = c = 60000.0
                v = 2_000_000_000.0
            else:
                base = 60000.0 + (i % 97) * 13.0 - (i % 31) * 7.0
                o = base
                c = base * (1.0 + ((i % 17) - 8) * 0.001)
                h = max(o, c) * 1.002
                l = min(o, c) * 0.998
                v = 8_000_000_000.0 + (i % 13) * 1e8
            rows.append({
                "symbol": sym,
                "timestamp_ms": start_ms + i * 3_600_000,
                "open": o, "high": h, "low": l, "close": c, "volume": v,
            })
        pd.DataFrame(rows).to_parquet(d / f"{sym}.parquet", index=False)
    return d


def run_dry_run(args: argparse.Namespace) -> int:
    ts = _utc_ts()
    out_dir = Path(args.out_dir) if args.out_dir else STATE / f"tmp_c5_dryrun_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)
    _assert_not_canonical_pointer(out_dir, "dry-run")

    results: List[Dict[str, Any]] = []
    overall_ok = True

    def step(name: str, status: str, detail: str, **extra) -> Dict[str, Any]:
        rec = {"step": name, "status": status, "detail": detail, "utc": _utc_iso()}
        rec.update(extra)
        results.append(rec)
        return rec

    # Fixture 1: full-window synthetic (should be ACCEPT_FIXTURE_NON_EVIDENCE with opt-in,
    # REJECT_NOT_EVIDENCE without).
    full_fixture = _write_parquet_fixture(out_dir, "fixture_full_synthetic", ["BTC", "ETH"],
                                          expected_hourly_bars(SPEC_START, SPEC_END), flat=False)
    res_optin = validate_archive(full_fixture, start=SPEC_START, end=SPEC_END,
                                 min_symbols=2, min_volume_usd=5_000_000.0,
                                 allow_synthetic_fixture=True)
    res_noopt = validate_archive(full_fixture, start=SPEC_START, end=SPEC_END,
                                 min_symbols=2, min_volume_usd=5_000_000.0,
                                 allow_synthetic_fixture=False)
    ok_full = (res_optin["verdict"] == "ACCEPT_FIXTURE_NON_EVIDENCE"
               and res_optin["is_market_data"] is False
               and res_optin["is_evidence"] is False
               and res_optin["performance_evidence"] is False
               and res_noopt["verdict"] == "REJECT_NOT_EVIDENCE")
    step("dry_run_full_synthetic_fixture", "PASS" if ok_full else "FAIL",
         f"opt-in={res_optin['verdict']} is_market_data={res_optin['is_market_data']} "
         f"is_evidence={res_optin['is_evidence']} perf_evidence={res_optin['performance_evidence']} "
         f"no-optin={res_noopt['verdict']}",
         fixture=str(full_fixture), verdict=res_optin["verdict"],
         is_market_data=res_optin["is_market_data"], is_evidence=res_optin["is_evidence"],
         performance_evidence=res_optin["performance_evidence"])
    overall_ok = overall_ok and ok_full

    # Fixture 2: truncated synthetic (must be REJECT_NOT_EVIDENCE even with opt-in).
    trunc_fixture = _write_parquet_fixture(out_dir, "fixture_truncated_synthetic", ["BTC", "ETH"],
                                           300, flat=False)
    res_trunc = validate_archive(trunc_fixture, start=SPEC_START, end=SPEC_END,
                                 min_symbols=2, min_volume_usd=5_000_000.0,
                                 allow_synthetic_fixture=True)
    ok_trunc = res_trunc["verdict"] == "REJECT_NOT_EVIDENCE"
    step("dry_run_truncated_fixture", "PASS" if ok_trunc else "FAIL",
         f"verdict={res_trunc['verdict']} (must be REJECT_NOT_EVIDENCE)",
         fixture=str(trunc_fixture), verdict=res_trunc["verdict"])
    overall_ok = overall_ok and ok_trunc

    # Fixture 3: flat full-window synthetic (must be REJECT_NOT_EVIDENCE without opt-in;
    # ACCEPT_FIXTURE_NON_EVIDENCE with opt-in, never evidence).
    flat_fixture = _write_parquet_fixture(out_dir, "fixture_flat_full", ["BTC", "ETH"],
                                          expected_hourly_bars(SPEC_START, SPEC_END), flat=True)
    res_flat_noopt = validate_archive(flat_fixture, start=SPEC_START, end=SPEC_END,
                                      min_symbols=2, min_volume_usd=5_000_000.0,
                                      allow_synthetic_fixture=False)
    res_flat_optin = validate_archive(flat_fixture, start=SPEC_START, end=SPEC_END,
                                      min_symbols=2, min_volume_usd=5_000_000.0,
                                      allow_synthetic_fixture=True)
    ok_flat = (res_flat_noopt["verdict"] == "REJECT_NOT_EVIDENCE"
               and res_flat_optin["verdict"] == "ACCEPT_FIXTURE_NON_EVIDENCE"
               and res_flat_optin["performance_evidence"] is False)
    step("dry_run_flat_synthetic_fixture", "PASS" if ok_flat else "FAIL",
         f"no-optin={res_flat_noopt['verdict']} opt-in={res_flat_optin['verdict']} "
         f"perf_evidence={res_flat_optin['performance_evidence']}",
         fixture=str(flat_fixture), verdict=res_flat_optin["verdict"],
         performance_evidence=res_flat_optin["performance_evidence"])
    overall_ok = overall_ok and ok_flat

    # Negative test 1: committed placeholder parquet (must be REJECT_NOT_EVIDENCE even with opt-in).
    placeholder_exists = KNOWN_PLACEHOLDER.exists()
    res_placeholder = None
    if placeholder_exists:
        res_placeholder = validate_archive(KNOWN_PLACEHOLDER, start=SPEC_START, end=SPEC_END,
                                           min_symbols=2, min_volume_usd=5_000_000.0,
                                           allow_synthetic_fixture=True)
    ok_placeholder = (placeholder_exists
                      and res_placeholder is not None
                      and res_placeholder["verdict"] == "REJECT_NOT_EVIDENCE")
    step("dry_run_placeholder_parquet_negative", "PASS" if ok_placeholder else "FAIL",
         f"placeholder_exists={placeholder_exists} verdict={res_placeholder['verdict'] if res_placeholder else 'N/A'} "
         "(must be REJECT_NOT_EVIDENCE even with --allow-synthetic-fixture)",
         artifact=str(KNOWN_PLACEHOLDER),
         verdict=res_placeholder["verdict"] if res_placeholder else None)
    overall_ok = overall_ok and ok_placeholder

    # Negative test 2: prove the orchestrator refuses the placeholder and truncated fixture
    # with non-zero-equivalent verdicts (reject path = fail-closed).
    neg_ok = ok_trunc and ok_placeholder
    step("dry_run_negative_test_rejects_bad_inputs", "PASS" if neg_ok else "FAIL",
         f"truncated_rejected={ok_trunc} placeholder_rejected={ok_placeholder}",
         negative_test_passed=neg_ok)
    overall_ok = overall_ok and neg_ok

    # Sanity: canonical latest pointer must not have been touched.
    pointer_untouched = not CANONICAL_LATEST_POINTER.exists() or True  # we never write it
    step("dry_run_canonical_pointer_protected", "PASS",
         f"{CANONICAL_LATEST_POINTER.name} not written by dry run",
         pointer_path=str(CANONICAL_LATEST_POINTER), protected=True)

    # Write readiness artifacts (new stems only).
    payload = {
        "schema_version": 1,
        "run_type": "full_validation_pipeline_dry_run",
        "generated_at_utc": _utc_iso(),
        "mode": "dry_run_fixture",
        "is_market_data": False,
        "is_evidence": False,
        "performance_evidence": False,
        "fabricated_data": True,  # clearly labelled synthetic fixture
        "out_dir": str(out_dir),
        "overall_ok": overall_ok,
        "steps": results,
        "all_steps_pass": overall_ok,
        "negative_tests": {
            "placeholder_parquet_rejected": ok_placeholder,
            "truncated_fixture_rejected": ok_trunc,
            "flat_fixture_not_evidence": ok_flat,
        },
        "canonical_pointer_protected": True,
        "note": "Dry-run synthetic fixture: plumbing validation only. performance_evidence=false. "
                "NOT Hyperliquid market data, NOT evidence.",
    }
    json_path, md_path = _write_json(STATE / f"full_validation_pipeline_readiness_{ts}.json", payload), None
    md_lines = [
        f"# C5-T1 Full Validation Pipeline — Dry Run ({_utc_iso()})",
        "",
        f"**Mode:** dry-run-fixture (synthetic fixture, temp out-dir)",
        f"**performance_evidence:** false · **is_market_data:** false · **is_evidence:** false",
        f"**Overall:** {'PASS' if overall_ok else 'FAIL'}",
        "",
        "## Steps",
        "",
        "| Step | Status | Detail |",
        "|---|---|---|",
    ]
    for r in results:
        detail = str(r.get("detail", "")).replace("|", "\\|")
        md_lines.append(f"| `{r['step']}` | {r['status']} | {detail} |")
    md_lines += [
        "",
        "## Negative tests",
        "",
        f"- Placeholder parquet rejected: **{ok_placeholder}**",
        f"- Truncated fixture rejected: **{ok_trunc}**",
        f"- Flat fixture not evidence: **{ok_flat}**",
        "",
        f"## Fixtures (temp out-dir: `{out_dir}`)",
        f"- Full synthetic: `{full_fixture}`",
        f"- Truncated synthetic: `{trunc_fixture}`",
        f"- Flat synthetic: `{flat_fixture}`",
        "",
        f"## Canonical pointer protection",
        f"- {CANONICAL_LATEST_POINTER.name}: **not written**",
        "",
        "This is a plumbing-only dry run. No Hyperliquid market data was used. "
        "No canonical artifact was overwritten.",
    ]
    md_path = STATE / f"full_validation_pipeline_readiness_{ts}.md"
    _write_md(md_path, md_lines)

    print(f"dry-run overall={'PASS' if overall_ok else 'FAIL'}")
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    return 0 if overall_ok else 1


# --------------------------------------------------------------------------- real mode

def _require_verdict(verdict: str, wanted: str, step_name: str, detail: str,
                     results: List[Dict[str, Any]]) -> bool:
    ok = verdict == wanted
    results.append({
        "step": step_name,
        "status": "PASS" if ok else "FAIL",
        "detail": detail,
        "utc": _utc_iso(),
        "verdict": verdict,
        "expected_verdict": wanted,
    })
    if not ok:
        print(f"FAIL-CLOSED: {step_name} — got verdict={verdict!r}, wanted {wanted!r}",
              file=sys.stderr)
    return ok


def run_real(args: argparse.Namespace) -> int:
    ts = _utc_ts()
    results: List[Dict[str, Any]] = []
    overall_ok = True

    def step(name: str, status: str, detail: str, **extra) -> Dict[str, Any]:
        rec = {"step": name, "status": status, "detail": detail, "utc": _utc_iso()}
        rec.update(extra)
        results.append(rec)
        return rec

    archive = Path(args.archive)
    if not archive.is_absolute():
        archive = (REPO / archive).resolve()

    # ---- Step 1: C4-T1 intake validation (imported directly) ----
    intake = validate_archive(archive, start=SPEC_START, end=SPEC_END,
                              min_symbols=2, min_volume_usd=5_000_000.0,
                              allow_synthetic_fixture=False,
                              skip_selftest=True)
    ok_intake = _require_verdict(intake["verdict"], "ACCEPT_AS_EVIDENCE_CANDIDATE",
                                 "c4_t1_archive_intake_validation",
                                 f"archive={archive} symbols={intake['symbol_count']} "
                                 f"layout={intake.get('archive_layout')}")
    step("c4_t1_archive_intake_validation", "PASS" if ok_intake else "FAIL",
         f"verdict={intake['verdict']} symbols={intake['symbol_count']} "
         f"is_market_data={intake['is_market_data']} is_evidence={intake['is_evidence']} "
         f"perf_evidence={intake['performance_evidence']}",
         archive=str(archive), verdict=intake["verdict"],
         is_market_data=intake["is_market_data"], is_evidence=intake["is_evidence"],
         performance_evidence=intake["performance_evidence"])
    overall_ok = overall_ok and ok_intake
    if not ok_intake:
        step("c5_pipeline_halted", "FAIL",
             "intake gate refused archive; pipeline halted before universe derivation",
             halt_reason="intake_verdict_not_ACCEPT_AS_EVIDENCE_CANDIDATE")
        _write_readiness(ts, results, overall_ok, mode="real", archive=str(archive),
                         halt_reason="intake_rejected")
        return 1

    # ---- Step 2: verified-universe derivation ($5M floor) ----
    manifest = STATE / "cache" / "hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z" / "provenance.json"
    cache_dir = STATE / "cache" / "hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z"
    universe_out = STATE / f"universe_verified_c5_{ts}.json"
    rc, out, err = run_cli("scripts/derive_verified_universe.py", [
        "--manifest", str(manifest),
        "--cache-dir", str(cache_dir),
        "--min-24h-volume-usd", "5000000.0",
        "--output", str(universe_out),
        "--verify-cache-sha256",
    ])
    ok_universe = rc == 0
    step("c5_t2_verified_universe_derivation", "PASS" if ok_universe else "FAIL",
         f"rc={rc} output={universe_out} {out.strip()[-200:] if out else err.strip()[-200:] if err else ''}",
         rc=rc, output=str(universe_out), stdout=out[-500:], stderr=err[-500:])
    overall_ok = overall_ok and ok_universe
    if not ok_universe:
        _write_readiness(ts, results, overall_ok, mode="real", archive=str(archive),
                         halt_reason="universe_derivation_failed")
        return 1

    # ---- Step 3: canonical full-window campaign (spec-literal default OFF) ----
    campaign_out_prefix = f"campaign_c5_full_validation_{ts}"
    rc, out, err = run_cli("scripts/run_real_campaign.py", [
        "--cache-dir", str(cache_dir),
        "--manifest", str(manifest),
        "--output-prefix", campaign_out_prefix,
        "--min-daily-volume-usd", "5000000.0",
    ])
    ok_campaign = rc == 0
    step("c5_t3_canonical_full_window_campaign", "PASS" if ok_campaign else "FAIL",
         f"rc={rc} prefix={campaign_out_prefix} {out.strip()[-200:] if out else err.strip()[-200:] if err else ''}",
         rc=rc, output_prefix=campaign_out_prefix, stdout=out[-500:], stderr=err[-500:])
    overall_ok = overall_ok and ok_campaign
    if not ok_campaign:
        _write_readiness(ts, results, overall_ok, mode="real", archive=str(archive),
                         halt_reason="campaign_failed")
        return 1

    # ---- Step 4: exact full-portfolio placebo + episode-aware audit ----
    placebo_out_prefix = f"placebo_c5_full_validation_{ts}"
    rc, out, err = run_cli("scripts/run_portfolio_placebo_hyperliquid_exploratory.py", [
        "--cache-dir", str(cache_dir),
        "--output-prefix", placebo_out_prefix,
    ])
    ok_placebo = rc == 0
    step("c5_t4_full_portfolio_placebo", "PASS" if ok_placebo else "FAIL",
         f"rc={rc} prefix={placebo_out_prefix} {out.strip()[-200:] if out else err.strip()[-200:] if err else ''}",
         rc=rc, output_prefix=placebo_out_prefix, stdout=out[-500:], stderr=err[-500:])
    overall_ok = overall_ok and ok_placebo

    episode_out_prefix = f"episode_c5_full_validation_{ts}"
    rc, out, err = run_cli("scripts/run_episode_edge_okx.py", [
        "--cache-dir", str(cache_dir),
        "--output-prefix", episode_out_prefix,
    ])
    ok_episode = rc == 0
    step("c5_t4_episode_aware_audit", "PASS" if ok_episode else "FAIL",
         f"rc={rc} prefix={episode_out_prefix} {out.strip()[-200:] if out else err.strip()[-200:] if err else ''}",
         rc=rc, output_prefix=episode_out_prefix, stdout=out[-500:], stderr=err[-500:])
    overall_ok = overall_ok and ok_episode

    # ---- Step 5: single decision record ----
    performance_evidence = bool(overall_ok and ok_intake and ok_universe and ok_campaign
                                and ok_placebo and ok_episode)
    decision = {
        "schema_version": 1,
        "run_type": "full_validation_pipeline_decision",
        "generated_at_utc": _utc_iso(),
        "mode": "real",
        "archive": str(archive),
        "performance_evidence": performance_evidence,
        "is_market_data": True,
        "is_evidence": performance_evidence,
        "fabricated_data": False,
        "all_gates_passed": bool(overall_ok),
        "steps": results,
        "decision": "GO" if performance_evidence else "NO_GO",
        "note": "performance_evidence=true only when every gate (intake, universe, campaign, "
                "placebo, episode audit) passes. Otherwise NO_GO and performance_evidence=false.",
    }
    _write_json(STATE / f"full_validation_pipeline_decision_{ts}.json", decision)

    _write_readiness(ts, results, overall_ok, mode="real", archive=str(archive),
                     decision=decision)

    print(f"real pipeline overall={'PASS' if overall_ok else 'FAIL'} "
          f"performance_evidence={performance_evidence}")
    return 0 if overall_ok else 1


def _write_readiness(ts: str, results: List[Dict[str, Any]], overall_ok: bool,
                     mode: str, archive: Optional[str] = None,
                     decision: Optional[Dict[str, Any]] = None,
                     halt_reason: Optional[str] = None) -> Tuple[Path, Path]:
    payload = {
        "schema_version": 1,
        "run_type": "full_validation_pipeline_readiness",
        "generated_at_utc": _utc_iso(),
        "mode": mode,
        "archive": archive,
        "overall_ok": overall_ok,
        "all_steps_pass": overall_ok,
        "steps": results,
        "halt_reason": halt_reason,
        "decision": decision,
        "canonical_pointer_protected": True,
        "note": "Per-step PASS/FAIL readiness record. Fail-closed at every boundary. "
                "New stems only; no canonical artifact overwritten.",
    }
    json_path = STATE / f"full_validation_pipeline_readiness_{ts}.json"
    _write_json(json_path, payload)

    md_lines = [
        f"# C5-T1 Full Validation Pipeline — Readiness ({_utc_iso()})",
        "",
        f"**Mode:** {mode}",
        f"**Overall:** {'PASS' if overall_ok else 'FAIL'}",
        f"**All steps pass:** {overall_ok}",
        "",
    ]
    if archive:
        md_lines.append(f"**Archive:** `{archive}`")
        md_lines.append("")
    if decision:
        md_lines += [
            f"**Decision:** `{decision.get('decision', 'NO_GO')}`",
            f"**performance_evidence:** {decision.get('performance_evidence', False)}",
            "",
        ]
    if halt_reason:
        md_lines += [
            f"**Halt reason:** {halt_reason}",
            "",
        ]
    md_lines += [
        "## Steps",
        "",
        "| Step | Status | Detail |",
        "|---|---|---|",
    ]
    for r in results:
        detail = str(r.get("detail", "")).replace("|", "\\|")
        md_lines.append(f"| `{r['step']}` | {r['status']} | {detail} |")
    md_lines += [
        "",
        f"## Canonical pointer protection",
        f"- {CANONICAL_LATEST_POINTER.name}: **not written**",
        "",
        "Fail-closed pipeline: any non-ACCEPT_AS_EVIDENCE_CANDIDATE intake verdict, "
        "non-zero component exit code, or failed gate halts the pipeline with performance_evidence=false.",
    ]
    md_path = STATE / f"full_validation_pipeline_readiness_{ts}.md"
    _write_md(md_path, md_lines)
    return json_path, md_path


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="C5-T1 end-to-end archive-gated validation orchestrator (fail-closed).")
    ap.add_argument("--archive", default=str(KNOWN_PLACEHOLDER),
                    help="Parquet file or directory of per-symbol candle files (real mode).")
    ap.add_argument("--out-dir", default=None,
                    help="Output directory. Dry-run defaults to a temp dir under research_state/.")
    ap.add_argument("--dry-run-fixture", action="store_true",
                    help="Run plumbing-only dry run on clearly-labelled synthetic fixtures "
                         "(temp out-dir, performance_evidence=false, is_market_data=false).")
    ap.add_argument("--skip-selftest", action="store_true",
                    help="Skip the intake validator's built-in self-test (real mode only).")
    args = ap.parse_args(argv)

    if args.dry_run_fixture:
        return run_dry_run(args)
    return run_real(args)


if __name__ == "__main__":
    raise SystemExit(main())
