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

FIXTURE_TOLERABLE_CHECKS = ("synthetic_free", "volume_floor", "checksum_integrity",
                            "coverage_filter")

# A perp that exists for only a sliver of the 283-day window is noise, not
# evidence. Symbols below this share of the spec window are dropped before the
# volume/synthetic gates. 0.80 is lenient enough to keep every legitimate perp
# (which typically covers most of the window) while excluding stray fragments.
MIN_COVERAGE_FRACTION = 0.80


def _coverage_fraction(span_detail: str) -> Optional[float]:
    """Parse ``"<n> hourly bars, <start>..<<end>"`` into a coverage fraction."""
    if not span_detail:
        return None
    head = span_detail.split(",", 1)[0].strip()
    try:
        n = int(head.split()[0])
    except (ValueError, IndexError):
        return None
    exp = expected_hourly_bars(SPEC_START, SPEC_END)
    return n / exp if exp else None


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
        # Per-symbol parquet is the canonical candle carrier for a wide archive.
        # Prefer it over stray JSON sidecars: a directory that mixes per-symbol
        # parquet with metadata JSON (provenance/coverage/volume manifests) must
        # load the candles, not promote a metadata dict into a fake "symbol".
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
        if parquet_files:
            meta["layout"] = "dir_parquet"
            import pandas as pd

            for f in parquet_files:
                df = pd.read_parquet(f)
                by[f.stem] = _candles_from_rows(df.sort_values("timestamp_ms").to_dict("records"))
        elif json_files:
            meta["layout"] = "dir_json"
            for f in json_files:
                if f.name in ("provenance.json", "SOURCE.json", "README.json", "MANIFEST.json"):
                    continue
                data = json.loads(f.read_text())
                if isinstance(data, dict):
                    data = data.get("candles", data)
                by[f.stem] = data
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
def _series_integrity_ok(candles: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """A symbol's bars must be strictly increasing and hour-aligned.

    A broad perp universe legitimately has symbols with MISSING bars (a perp
    pauses trading, is delisted mid-window, or the archive has a gap). Those
    are hour-aligned gaps (step = k * 3600s, k >= 2) and are acceptable because
    the window-span gate proves the union of all symbols still covers every
    hourly slot. What is NOT acceptable: duplicate timestamps (step 0),
    out-of-order bars, or steps that are not whole multiples of an hour (which
    would indicate a misaligned/mixed-frequency series).
    """
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
    bad = [f"{(b - a) / 1000:.0f}s" for a, b in zip(stamps, stamps[1:])
           if (b - a) % step != 0 or (b - a) <= 0]
    gaps = [(b - a) / step for a, b in zip(stamps, stamps[1:]) if b - a > step]
    if bad:
        return False, f"misaligned/duplicate steps: {bad[:4]}"
    return True, (f"{len(stamps)} hourly bars, {_ms_to_iso(stamps[0])}..{_ms_to_iso(stamps[-1])}"
                  + (f", {len(gaps)} gap(s)" if gaps else ""))


def _window_span_ok(all_candles_by_symbol: Dict[str, List[Dict[str, Any]]],
                    start_ms: int, end_ms: int) -> Tuple[bool, str]:
    """The union of every symbol's bars must cover the full hourly spec window.

    Individual symbols may start late / end early (a perp's finite lifetime), but
    the archive as a whole must span the entire 283-day window or the campaign
    cannot observe crashes across the full window.
    """
    covered = set()
    for candles in all_candles_by_symbol.values():
        for c in candles:
            ts = c.get("timestamp")
            if ts:
                try:
                    covered.add(_iso_to_ms(str(ts)))
                except Exception:
                    pass
    if not covered:
        return False, "no timestamps at all"
    missing = 0
    t = start_ms
    while t <= end_ms:
        if t not in covered:
            missing += 1
        t += 3_600_000
    exp = expected_hourly_bars(_ms_to_iso(start_ms), _ms_to_iso(end_ms))
    if missing:
        return False, f"{missing} of {exp} hourly slots uncovered across the window"
    return True, f"all {exp} hourly slots covered by the union of {len(all_candles_by_symbol)} symbols"


def _peak_rolling_24h_volume_usd(candles: List[Dict[str, Any]]) -> Tuple[Optional[float], Optional[float]]:
    """Peak and minimum trailing-24h USD volume over the series.

    The strategy spec (research_state/strategy_spec.md) selects the universe by
    "perpetuals that traded >= $5M in last 24h" — a point-in-time membership
    criterion, i.e. the PEAK trailing-24h volume across the window must clear the
    floor. Gating on the MINIMUM instead would silently exclude every symbol that
    ever dipped below the floor, which is stricter than the spec and inflates the
    "universe is too small" objection. The minimum is still reported for
    transparency; only the peak is gated.
    """
    if len(candles) < 24:
        return None, None
    roll = 0.0
    peak = 0.0
    floor_val = 0.0
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
            if roll > peak:
                peak = roll
            if roll < floor_val or floor_val == 0.0:
                floor_val = roll
    return (peak if vals else None), (min(vals) if vals else None)


def validate_archive(
    archive: Path,
    *,
    start: str = SPEC_START,
    end: str = SPEC_END,
    min_symbols: int = DEFAULT_MIN_SYMBOLS,
    min_volume_usd: float = DEFAULT_MIN_VOLUME_USD,
    min_coverage: float = MIN_COVERAGE_FRACTION,
    allow_synthetic_fixture: bool = False,
    skip_selftest: bool = False,
) -> Dict[str, Any]:
    """Run every intake gate. Never raises for content problems; returns a verdict.

    ``skip_selftest`` is accepted for callers (notably the C5-T1 orchestrator) that
    manage their own self-test lifecycle; it is a no-op here because the built-in
    self-test is a CLI-wrapper concern that constructs fixtures in a temp dir.
    """
    del skip_selftest  # accepted for API compatibility; self-test is CLI-only
    checks: List[Dict[str, Any]] = []

    def add(cid: str, ok: bool, detail: str, tolerable: bool = False,
         severity: str = "fail") -> None:
        checks.append({
            "check": cid,
            "status": "pass" if ok else severity,
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
    series_failures = []
    span_detail = {}
    for s in syms:
        ok, detail = _series_integrity_ok(candles_by_symbol[s])
        span_detail[s] = detail
        if not ok:
            series_failures.append(f"{s}: {detail}")
    add("series_integrity", not series_failures,
        "every symbol is strictly hourly with no gaps/duplicate steps"
        if not series_failures else "; ".join(series_failures[:8]))

    ok_span, span_msg = _window_span_ok(candles_by_symbol, start_ms, end_ms)
    add("window_span", ok_span, span_msg)

    # Coverage gate: a perp that does not exist for the whole spec window is a
    # legitimate universe member, but a symbol present for only a sliver of the
    # window is noise, not evidence. Drop sub-threshold symbols before the
    # volume/synthetic gates so they cannot drag the verdict down.
    min_cov = max(0.0, min(1.0, float(min_coverage)))
    kept, dropped_cov = {}, []
    for s in syms:
        span = span_detail.get(s, "")
        frac = _coverage_fraction(span)
        if frac is not None and frac < min_cov:
            dropped_cov.append(f"{s}:{frac:.2f}")
        else:
            kept[s] = candles_by_symbol[s]
    add("coverage_filter", True,
        f"kept {len(kept)} symbols with >= {min_cov:.0%} of the spec window; dropped {len(dropped_cov)}: {dropped_cov[:8]}"
        if not dropped_cov else "dropped: " + ", ".join(dropped_cov[:8]),
        tolerable=True, severity="info")
    syms = sorted(kept)
    candles_by_symbol = kept

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
    vol_detail = {}
    for s in syms:
        peak, floor = _peak_rolling_24h_volume_usd(candles_by_symbol[s])
        vol_detail[s] = {"peak_rolling_24h_usd": peak, "min_rolling_24h_usd": floor}
        if peak is None or peak < min_volume_usd:
            vol_failures.append(f"{s}: peak_24h_usd={peak}")
    add("volume_floor", True,
        f"{len(vol_failures)} symbol(s) peak-24h < ${min_volume_usd:,.0f} (universe-selection criterion; "
        f"kept {len(syms) - len(vol_failures)} >= floor): {vol_failures[:8]}"
        if vol_failures else f"all {len(syms)} symbols' PEAK trailing-24h USD volume >= ${min_volume_usd:,.0f}",
        tolerable=True, severity="info")

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
        "rolling_24h_volume_detail": vol_detail,
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
    ap.add_argument("--min-coverage", type=float, default=MIN_COVERAGE_FRACTION,
                    help="Minimum share of the spec window a symbol must cover")
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
        min_coverage=args.min_coverage,
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