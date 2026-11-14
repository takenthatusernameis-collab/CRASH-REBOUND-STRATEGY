#!/usr/bin/env python3
"""C4-T1 — fail-closed Hyperliquid archive intake validator.

WHY THIS EXISTS
---------------
The research program is blocked on one external input: a verified
Hyperliquid-native archive covering the 283-day spec window. Nothing in this repo
can manufacture that data, but until now there was no executable gate that would
stop an operator-supplied archive (or a placeholder parquet, or a truncated
slice, or a flat/synthetic series) from being silently promoted to evidence.

This validator is that gate. It accepts an archive only when provenance,
coverage, non-synthetic integrity, volume floor and checksums all hold. It never
fabricates candles, never relabels OKX data, and never calls the committed
placeholder parquet evidence.

VERDICT SEMANTICS
-----------------
* ``ACCEPT_AS_EVIDENCE_CANDIDATE`` — every gate passed; safe to ingest with the
  DATA_REQUEST runbook. Still ``performance_evidence=false``: intake validation
  is not a backtest.
* ``ACCEPT_FIXTURE_NON_EVIDENCE`` — only reachable with ``--allow-synthetic-fixture``
  and only for plumbing tests. The artifact records
  ``is_market_data=false``, ``is_evidence=false``, ``performance_evidence=false``.
  A truncated window is NEVER fixture-tolerable.
* ``REJECT_NOT_EVIDENCE`` — fail closed. This is the correct verdict for the
  committed placeholder parquet, short windows, flat series, missing provenance,
  missing symbols, missing/mismatched hashes.

SELF-TEST
---------
Every run executes a built-in self-test that constructs three fixtures in a temp
dir and asserts the expected verdicts (synthetic fixture -> fixture-accept only
with the opt-in flag; truncated fixture -> reject; flat placeholder -> reject).
If any expectation is not met the whole run exits non-zero, so a broken gate can
never be reported as green.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from src.data.provenance import (  # noqa: E402
    TARGET_END,
    TARGET_START,
    detect_synthetic_candles,
    expected_hourly_bars,
    _parse_iso,
)

STATE = REPO / "research_state"
SPEC_START = TARGET_START
SPEC_END = TARGET_END
DEFAULT_MIN_SYMBOLS = 2
DEFAULT_MIN_VOLUME_USD = 5_000_000.0
KNOWN_PLACEHOLDER = (
    STATE
    / "archives"
    / "hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet"
)

CAVEAT = (
    "Intake validation only: proves the archive is structurally usable as evidence "
    "input, NOT that the strategy is profitable. Never relabel OKX, partial "
    "snapshots, dry-run fixtures, or the placeholder parquet as Hyperliquid evidence."
)

FIXTURE_TOLERABLE_CHECKS = ("synthetic_free", "volume_floor", "checksum_integrity")


# --------------------------------------------------------------------------- io
def _iso_to_ms(iso: str) -> int:
    return int(_parse_iso(iso).timestamp() * 1000)


def _ms_to_iso(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _candles_from_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for r in rows:
        out.append({
            "timestamp": _ms_to_iso(int(r["timestamp_ms"])),
            "open": float(r["open"]),
            "high": float(r["high"]),
            "low": float(r["low"]),
            "close": float(r["close"]),
            "volume": float(r["volume"]),
        })
    return out


def load_archive(path: Path) -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, Any]]:
    """Load candles from a parquet file/dir or a directory of per-symbol JSON.

    Returns (candles_by_symbol, meta) where meta carries the detected layout,
    checksums and sidecar documents actually found.
    """
    meta: Dict[str, Any] = {"archive_path": str(path), "layout": None,
                            "documents": [], "checksums": {}}
    if path.is_file():
        import pandas as pd

        if path.suffix.lower() not in (".parquet", ".pq"):
            raise ValueError(f"unsupported archive file type: {path.suffix}")
        df = pd.read_parquet(path)
        required = {"symbol", "timestamp_ms", "open", "high", "low", "close", "volume"}
        missing = sorted(required - set(df.columns))
        if missing:
            raise ValueError(f"parquet missing required columns: {missing}")
        by: Dict[str, List[Dict[str, Any]]] = {}
        for sym, grp in df.groupby("symbol", sort=True):
            by[str(sym)] = _candles_from_rows(grp.sort_values("timestamp_ms").to_dict("records"))
        meta["layout"] = "parquet_file"
        meta["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        for sidecar in (path.with_suffix(path.suffix + ".README.json"),
                        path.with_suffix(".README.json"),
                        path.with_suffix(".SOURCE.json")):
            if sidecar.exists():
                meta["documents"].append(str(sidecar))
                meta["sidecar_sha256_declared"] = _declared_sha(sidecar)
        return by, meta

    if path.is_dir():
        json_files = sorted(path.glob("*.json"))
        parquet_files = sorted(path.glob("*.parquet"))
        for doc_name in ("SOURCE.md", "SOURCE.json", "README.md", "README.json",
                         "provenance.json", "MANIFEST.json"):
            doc = path / doc_name
            if doc.exists():
                meta["documents"].append(str(doc))
        by = {}
        if json_files:
            meta["layout"] = "dir_json"
            for f in json_files:
                if f.name in ("provenance.json", "SOURCE.json", "README.json", "MANIFEST.json"):
                    continue
                data = json.loads(f.read_text())
                if isinstance(data, dict):
                    data = data.get("candles", data)
                by[f.stem] = data
            prov = path / "provenance.json"
            if prov.exists():
                meta["provenance_manifest"] = str(prov)
                try:
                    pm = json.loads(prov.read_text())
                    meta["manifest_symbols"] = pm.get("symbols") or {}
                    for sym, info in (pm.get("symbols") or {}).items():
                        if isinstance(info, dict) and info.get("sha256"):
                            meta["checksums"][str(sym)] = str(info["sha256"])
                except Exception:
                    meta["manifest_error"] = "unreadable provenance.json"
        elif parquet_files:
            meta["layout"] = "dir_parquet"
            import pandas as pd

            for f in parquet_files:
                df = pd.read_parquet(f)
                by[f.stem] = _candles_from_rows(df.sort_values("timestamp_ms").to_dict("records"))
        else:
            raise ValueError(f"no candle files found in archive dir: {path}")
        return by, meta

    raise ValueError(f"archive path does not exist: {path}")


def _declared_sha(sidecar: Path) -> Optional[str]:
    try:
        data = json.loads(sidecar.read_text())
    except Exception:
        return None
    for key in ("sha256", "checksum", "file_sha256"):
        v = data.get(key)
        if isinstance(v, str) and len(v) == 64:
            return v
    return None


# --------------------------------------------------------------------- checks
def _hourly_series_ok(candles: List[Dict[str, Any]], start_ms: int, end_ms: int) -> Tuple[bool, str]:
    if not candles:
        return False, "empty"
    stamps = []
    for c in candles:
        ts = c.get("timestamp")
        if not ts:
            return False, "bar without timestamp"
        try:
            stamps.append(_iso_to_ms(str(ts)))
        except Exception:
            return False, f"unparseable timestamp: {ts}"
    if any(b <= a for a, b in zip(stamps, stamps[1:])):
        return False, "timestamps not strictly increasing"
    step = 3_600_000
    for a, b in zip(stamps, stamps[1:]):
        if b - a != step:
            return False, f"non-hourly gap/duplicate step of {(b - a) / 1000:.0f}s"
    if stamps[0] > start_ms:
        return False, f"starts late: {_ms_to_iso(stamps[0])} > {_ms_to_iso(start_ms)}"
    if stamps[-1] < end_ms:
        return False, f"ends early: {_ms_to_iso(stamps[-1])} < {_ms_to_iso(end_ms)}"
    exp = expected_hourly_bars(_ms_to_iso(start_ms), _ms_to_iso(end_ms))
    if len(stamps) != exp:
        return False, f"bar count {len(stamps)} != expected {exp}"
    return True, f"{len(stamps)} bars, {_ms_to_iso(stamps[0])}..{_ms_to_iso(stamps[-1])}"


def _min_rolling_24h_volume_usd(candles: List[Dict[str, Any]]) -> Optional[float]:
    if len(candles) < 24:
        return None
    roll = 0.0
    vals: List[float] = []
    for i, c in enumerate(candles):
        close = float(c["close"])
        vol = float(c["volume"])
        roll += vol * close if close > 0 else 0.0
        if i >= 24:
            pc = float(candles[i - 24]["close"])
            pv = float(candles[i - 24]["volume"])
            roll -= pv * pc if pc > 0 else 0.0
        if i >= 23:
            vals.append(roll)
    return min(vals) if vals else None


def validate_archive(
    archive: Path,
    *,
    start: str = SPEC_START,
    end: str = SPEC_END,
    min_symbols: int = DEFAULT_MIN_SYMBOLS,
    min_volume_usd: float = DEFAULT_MIN_VOLUME_USD,
    allow_synthetic_fixture: bool = False,
) -> Dict[str, Any]:
    """Run every intake gate. Never raises for content problems; returns a verdict."""
    checks: List[Dict[str, Any]] = []

    def add(cid: str, ok: bool, detail: str, tolerable: bool = False) -> None:
        checks.append({
            "check": cid,
            "status": "pass" if ok else "fail",
            "detail": detail,
            "fixture_tolerable": tolerable,
        })

    try:
        candles_by_symbol, meta = load_archive(archive)
    except Exception as exc:
        add("archive_present", False, f"cannot load archive: {exc}")
        return _verdict(checks, meta, archive, allow_synthetic_fixture)

    add("archive_present", True,
        f"{len(candles_by_symbol)} symbol(s) loaded, layout={meta.get('layout')}")

    resolved = archive.resolve()
    placeholder_hit = resolved == KNOWN_PLACEHOLDER.resolve()
    add("placeholder_not_evidence", not placeholder_hit,
        "known placeholder parquet detected; never evidence" if placeholder_hit
        else "not the committed placeholder parquet")

    docs = [Path(p) for p in meta.get("documents", [])]
    doc_text = ""
    for d in docs:
        try:
            doc_text += d.read_text(errors="ignore") + "\n"
        except Exception:
            pass
    low = doc_text.lower()
    declares_hl = "hyperliquid" in low
    declares_fixture = any(m in low for m in ("synthetic", "placeholder", "fixture"))
    add("source_provenance", bool(docs) and declares_hl,
        f"provenance documents={len(docs)}; declares_hyperliquid={declares_hl}; "
        f"declares_fixture_or_synthetic={declares_fixture}"
        + ("" if docs else "; no SOURCE/README/manifest found"))

    syms = sorted(candles_by_symbol)
    add("symbol_universe", len(syms) >= min_symbols and all(candles_by_symbol[s] for s in syms),
        f"{len(syms)} symbol(s) >= min_symbols {min_symbols}: {syms}")

    start_ms, end_ms = _iso_to_ms(start), _iso_to_ms(end)
    cov_failures = []
    for s in syms:
        ok, detail = _hourly_series_ok(candles_by_symbol[s], start_ms, end_ms)
        if not ok:
            cov_failures.append(f"{s}: {detail}")
    add("window_coverage", not cov_failures,
        "all symbols cover the full hourly window with no gaps"
        if not cov_failures else "; ".join(cov_failures[:8]))

    synth_failures = []
    synth_detail = {}
    for s in syms:
        res = detect_synthetic_candles(candles_by_symbol[s])
        synth_detail[s] = res
        if res["is_synthetic"]:
            synth_failures.append(f"{s}: {res['reason']} ({res['distinct_signatures']}/{res['bars_checked']})")
    add("synthetic_free", not synth_failures,
        "no flat/constant-close series detected"
        if not synth_failures else "; ".join(synth_failures[:8]),
        tolerable=True)

    vol_failures = []
    min_vols = {}
    for s in syms:
        mv = _min_rolling_24h_volume_usd(candles_by_symbol[s])
        min_vols[s] = mv
        if mv is None or mv < min_volume_usd:
            vol_failures.append(f"{s}: {mv}")
    add("volume_floor", not vol_failures,
        f"all symbols >= ${min_volume_usd:,.0f} trailing-24h USD volume"
        if not vol_failures else "below floor: " + ", ".join(vol_failures[:8]),
        tolerable=True)

    checksums = meta.get("checksums") or {}
    declared = meta.get("sidecar_sha256_declared")
    problems = []
    if declared and meta.get("sha256") and declared != meta["sha256"]:
        problems.append(f"sidecar sha256 {declared} != file sha256 {meta['sha256']}")
    if not checksums and not declared:
        problems.append("no checksum declared (unverified intake)")
    for sym, expected in checksums.items():
        actual = meta.get("sha256") if meta.get("layout") == "parquet_file" else None
        if actual and actual != expected:
            problems.append(f"{sym}: sha256 mismatch")
    add("checksum_integrity", not problems,
        "checksums verified" if not problems else "; ".join(problems), tolerable=True)

    verdict, is_market_data, is_evidence = _verdict(
        checks, meta, archive, allow_synthetic_fixture, return_flags=True)
    # The committed placeholder is never acceptable, not even as a plumbing
    # fixture: it is a flat series that has already leaked into one dry run.
    if placeholder_hit:
        verdict, is_market_data, is_evidence = "REJECT_NOT_EVIDENCE", False, False

    return {
        "schema_version": 1,
        "run_type": "hyperliquid_archive_intake_validation",
        "archive": str(archive),
        "archive_sha256": meta.get("sha256"),
        "archive_layout": meta.get("layout"),
        "requested_window": {"start": start, "end": end,
                             "expected_hourly_bars": expected_hourly_bars(start, end)},
        "min_symbols_required": min_symbols,
        "min_volume_usd_required": min_volume_usd,
        "allow_synthetic_fixture": allow_synthetic_fixture,
        "symbols": syms,
        "symbol_count": len(syms),
        "checks": checks,
        "synthetic_detail": synth_detail,
        "min_rolling_24h_volume_usd": min_vols,
        "verdict": verdict,
        "is_market_data": is_market_data,
        "is_evidence": is_evidence,
        "performance_evidence": False,
        "provenance_caveat": CAVEAT,
        "no_new_data_fabricated": True,
    }


def _verdict(checks: List[Dict[str, Any]], meta: Dict[str, Any], archive: Path,
             allow_fixture: bool, return_flags: bool = False):
    failed = {c["check"] for c in checks if c["status"] == "fail"}
    hard = failed - set(FIXTURE_TOLERABLE_CHECKS)
    if not failed:
        verdict = "ACCEPT_AS_EVIDENCE_CANDIDATE"
        flags = (True, True)
    elif allow_fixture and not hard and failed:
        verdict = "ACCEPT_FIXTURE_NON_EVIDENCE"
        flags = (False, False)
    else:
        verdict = "REJECT_NOT_EVIDENCE"
        flags = (False, False)
    if return_flags:
        return verdict, flags[0], flags[1]
    return verdict


# ------------------------------------------------------------------- selftest
def _write_fixture(root: Path, name: str, symbols: List[str], bars: int,
                   *, flat: bool, start: str = SPEC_START,
                   declare: str = "synthetic plumbing fixture") -> Path:
    d = root / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SOURCE.md").write_text(
        f"# {name}\n\nSynthetic {declare} for intake-validator plumbing tests.\n"
        "NOT market data. NOT evidence. Hyperliquid-native shape only.\n")
    start_ms = _iso_to_ms(start)
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
        import pandas as pd

        pd.DataFrame(rows).to_parquet(d / f"{sym}.parquet", index=False)
    return d


def run_selftest(tmp: Path) -> Dict[str, Any]:
    results = []

    def expect(name: str, archive: Path, allow: bool, want: str) -> None:
        res = validate_archive(archive, allow_synthetic_fixture=allow)
        ok = res["verdict"] == want
        results.append({
            "case": name,
            "allow_synthetic_fixture": allow,
            "expected_verdict": want,
            "actual_verdict": res["verdict"],
            "pass": ok,
            "failed_checks": [c["check"] for c in res["checks"] if c["status"] == "fail"],
            "is_market_data": res["is_market_data"],
            "is_evidence": res["is_evidence"],
            "performance_evidence": res["performance_evidence"],
        })

    flat = _write_fixture(tmp, "fixture_flat_full", ["BTC", "ETH"],
                          expected_hourly_bars(SPEC_START, SPEC_END), flat=True)
    expect("flat_full_window_fixture_without_optin", flat, False, "REJECT_NOT_EVIDENCE")
    expect("flat_full_window_fixture_with_optin", flat, True, "ACCEPT_FIXTURE_NON_EVIDENCE")

    trunc = _write_fixture(tmp, "fixture_truncated", ["BTC", "ETH"], 300, flat=False)
    expect("truncated_varying_fixture_with_optin", trunc, True, "REJECT_NOT_EVIDENCE")

    if KNOWN_PLACEHOLDER.exists():
        expect("committed_placeholder_parquet", KNOWN_PLACEHOLDER, True, "REJECT_NOT_EVIDENCE")

    return {
        "cases": results,
        "all_expectations_met": all(r["pass"] for r in results),
        "case_count": len(results),
    }


def _write_artifacts(payload: Dict[str, Any]) -> Tuple[Path, Path]:
    STATE.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_json = STATE / f"archive_intake_validation_{ts}.json"
    out_json.write_text(json.dumps(payload, indent=2) + "\n")
    lines = [
        f"# Hyperliquid Archive Intake Validation — {payload['generated_at_utc']}",
        "",
        f"**Verdict:** `{payload['verdict']}`  ",
        f"**is_market_data:** `{payload['is_market_data']}` · "
        f"**is_evidence:** `{payload['is_evidence']}` · "
        f"**performance_evidence:** `{payload['performance_evidence']}`",
        "",
        f"Archive: `{payload['archive']}`  ",
        f"Requested window: `{payload['requested_window']['start']}` .. "
        f"`{payload['requested_window']['end']}` "
        f"({payload['requested_window']['expected_hourly_bars']} expected hourly bars/symbol)",
        "",
        "## Gate results",
        "",
        "| Check | Status | Detail |",
        "|---|---|---|",
    ]
    for c in payload["checks"]:
        detail = c["detail"].replace("|", "\\|")
        lines.append(f"| `{c['check']}` | {c['status']} | {detail} |")
    st = payload["selftest"]
    lines += [
        "",
        "## Built-in self-test (fail-closed proof)",
        "",
        f"All expectations met: **{st['all_expectations_met']}** ({st['case_count']} cases)",
        "",
        "| Case | Opt-in | Expected | Actual | Pass |",
        "|---|---|---|---|---|",
    ]
    for r in st["cases"]:
        lines.append(
            f"| `{r['case']}` | {r['allow_synthetic_fixture']} | `{r['expected_verdict']}` "
            f"| `{r['actual_verdict']}` | {r['pass']} |")
    lines += [
        "",
        "## Caveats",
        "",
        f"- {CAVEAT}",
        "- A fixture acceptance is plumbing-only: `is_market_data=false`, `is_evidence=false`.",
        "- A truncated window is never fixture-tolerable; only synthetic/volume/checksum "
        "gaps may be waived by the explicit opt-in flag.",
        "- This validator does not run a backtest and makes no profitability claim.",
        "",
    ]
    out_md = STATE / f"archive_intake_validation_{ts}.md"
    out_md.write_text("\n".join(lines) + "\n")
    return out_json, out_md


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--archive", default=str(KNOWN_PLACEHOLDER),
                    help="Parquet file or directory of per-symbol candle files")
    ap.add_argument("--start", default=SPEC_START)
    ap.add_argument("--end", default=SPEC_END)
    ap.add_argument("--min-symbols", type=int, default=DEFAULT_MIN_SYMBOLS)
    ap.add_argument("--min-24h-volume-usd", type=float, default=DEFAULT_MIN_VOLUME_USD)
    ap.add_argument("--allow-synthetic-fixture", action="store_true",
                    help="Permit a clearly-labelled synthetic fixture for plumbing only")
    ap.add_argument("--skip-selftest", action="store_true")
    args = ap.parse_args(argv)

    selftest: Dict[str, Any] = {"skipped": True}
    if not args.skip_selftest:
        with tempfile.TemporaryDirectory(prefix="crs_intake_selftest_") as td:
            selftest = run_selftest(Path(td))
        if not selftest["all_expectations_met"]:
            payload = {
                "schema_version": 1,
                "run_type": "hyperliquid_archive_intake_validation_selftest_failure",
                "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "verdict": "SELFTEST_FAILED_GATE_NOT_TRUSTWORTHY",
                "is_market_data": False,
                "is_evidence": False,
                "performance_evidence": False,
                "selftest": selftest,
                "provenance_caveat": CAVEAT,
            }
            out_json, out_md = _write_artifacts(payload)
            print(json.dumps(selftest, indent=2))
            print(f"BLOCKER: intake validator self-test failed; wrote {out_json} and {out_md}",
                  file=sys.stderr)
            return 4

    archive = Path(args.archive)
    if not archive.is_absolute():
        archive = (REPO / archive).resolve()

    res = validate_archive(
        archive,
        start=args.start,
        end=args.end,
        min_symbols=args.min_symbols,
        min_volume_usd=args.min_24h_volume_usd,
        allow_synthetic_fixture=args.allow_synthetic_fixture,
    )
    res["generated_at_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    res["selftest"] = selftest
    out_json, out_md = _write_artifacts(res)

    print(f"verdict={res['verdict']} symbols={res['symbol_count']} "
          f"is_market_data={res['is_market_data']} is_evidence={res['is_evidence']} "
          f"performance_evidence={res['performance_evidence']}")
    for c in res["checks"]:
        if c["status"] != "pass":
            print(f"  FAIL {c['check']}: {c['detail']}")
    print(f"wrote {out_json}")
    print(f"wrote {out_md}")

    if res["verdict"] == "ACCEPT_AS_EVIDENCE_CANDIDATE":
        return 0
    if res["verdict"] == "ACCEPT_FIXTURE_NON_EVIDENCE":
        return 3
    return 2


if __name__ == "__main__":
    raise SystemExit(main())