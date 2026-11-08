"""Item 3 residual (2026-11-08, failing-tests-first): gap report archive scan must
not treat unverified/synthetic cache files as verified coverage truth.

_scan_archives probes candidate files via fetch_hyperliquid_candles._read_symbol_candles_from_file
and its own runtime synthetic detection. It must reject: (1) runtime-flat/synthetic series,
(2) JSON payloads carrying declared synthetic_check.is_synthetic=true (if readable as candles),
and (3) files whose content cannot be verified as clean non-synthetic complete coverage.

Synthetic non-evidence fixtures only.
"""
from __future__ import annotations

import json
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars, _parse_iso


def _bars(exp=None, *, flat=False, declared_synthetic=None):
    exp = expected_hourly_bars(TARGET_START, TARGET_END) if exp is None else exp
    start = _parse_iso(TARGET_START)
    rows = []
    for i in range(exp):
        ts = start + timedelta(hours=i)
        if flat:
            o = h = l = c = 100.0
            v = 1000.0
        else:
            # deterministic varied, non-flat, realistic-ish
            c = 100.0 + 0.15 * ((i % 97) - 48) / 48.0 + 0.0005 * (i % 13)
            o = c - 0.01
            h = c + 0.05
            l = c - 0.06
            v = 1_000_000.0 + 500.0 * (i % 100)
        rows.append({
            "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "open": o, "high": h, "low": l, "close": c, "volume": v,
        })
    if declared_synthetic is not None:
        return {"candles": rows, "synthetic_check": declared_synthetic}
    return rows


def test_scan_rejects_runtime_flat_synthetic_archive():
    from scripts.generate_candle_coverage_gap_report import _scan_archives
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "BTC.json"
        p.write_text(json.dumps(_bars(flat=True)))
        out = _scan_archives([td])
        assert out["verified_archives_found"] == [], out
        assert len(out["candidate_archives"]) == 1, out
        c = out["candidate_archives"][0]
        assert c.get("verified") is False, c
        # must not silently accept synthetic-as-coverage
        assert c.get("synthetic_detected") is True or c.get("verdict") not in (None, "verified_complete_non_synthetic"), c


def test_scan_rejects_payload_with_declared_synthetic_check():
    from scripts.generate_candle_coverage_gap_report import _scan_archives
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "BTC.json"
        p.write_text(json.dumps(_bars(flat=False, declared_synthetic={"is_synthetic": True, "reason": "test"})))
        out = _scan_archives([td])
        assert out["verified_archives_found"] == [], out
        c = out["candidate_archives"][0]
        assert c.get("verified") is False, c


def test_scan_complete_varied_not_marked_synthetic():
    """Control: complete varied series in spec window should not be flagged synthetic by runtime detector."""
    from scripts.generate_candle_coverage_gap_report import _scan_archives
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "BTC.json"
        p.write_text(json.dumps(_bars(flat=False)))
        out = _scan_archives([td])
        assert len(out["candidate_archives"]) == 1, out
        c = out["candidate_archives"][0]
        assert c.get("synthetic_detected") is False, c
        # may still be non-verified for other reasons, but must not be rejected as synthetic
