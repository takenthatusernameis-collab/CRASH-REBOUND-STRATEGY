"""Item 3 residual (failing-tests-first): gap report archive scan must never
upgrade an unverified probed file to trusted coverage truth.

_scan_archives probes untrusted files without manifest provenance. Runtime
detection + complete coverage is NOT verified evidence: a scanned file must
remain verified=False and must never earn verdict verified_complete_non_synthetic
without fail-closed verified provenance (present clean synthetic_check, sha256
when available, validated-fact authority). Declared-synthetic / runtime-synthetic
/ unreadable / probe-error paths are rejected; clean complete files are reported
as probed-but-unverified, never as coverage truth.
"""
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars, _parse_iso


def _bars(exp=None, *, flat=False):
    exp = expected_hourly_bars(TARGET_START, TARGET_END) if exp is None else exp
    start = _parse_iso(TARGET_START)
    rows = []
    for i in range(exp):
        ts = start + timedelta(hours=i)
        if flat:
            o = h = l = c = 100.0
            v = 1000.0
        else:
            c = 100.0 + 0.15 * ((i % 97) - 48) / 48.0 + 0.0005 * (i % 13)
            o = c - 0.01
            h = c + 0.05
            l = c - 0.06
            v = 1_000_000.0 + 500.0 * (i % 100)
        rows.append({
            "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "open": o, "high": h, "low": l, "close": c, "volume": v,
        })
    return rows


def test_scan_never_upgrades_complete_probed_file_to_verified_truth():
    from scripts.generate_candle_coverage_gap_report import _scan_archives
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "BTC.json"
        p.write_text(json.dumps(_bars(flat=False)))
        out = _scan_archives([td])
        assert out["verified_archives_found"] == [], out
        assert len(out["candidate_archives"]) == 1, out
        c = out["candidate_archives"][0]
        # probed but NOT verified: runtime detection alone is not evidence
        assert c.get("verified") is False, c
        assert c.get("verdict") != "verified_complete_non_synthetic", c
        # and it must not be rejected as synthetic either (clean varied series)
        assert c.get("synthetic_detected") is False, c


def test_scan_rejects_flat_probed_file_without_upgrading():
    from scripts.generate_candle_coverage_gap_report import _scan_archives
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "ETH.json"
        p.write_text(json.dumps(_bars(flat=True)))
        out = _scan_archives([td])
        assert out["verified_archives_found"] == [], out
        c = out["candidate_archives"][0]
        assert c.get("verified") is False, c
        assert c.get("synthetic_detected") is True or c.get("verdict") == "synthetic_or_incomplete_rejected", c
