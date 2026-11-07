"""Failing-test-first hardening: a verified-cache file whose candle series is flat /
constant / synthetic must NEVER be accepted by the real-campaign loader, even when
the provenance manifest claims status=ok and complete coverage.

Root cause found 2026-11-07: `research_state/cache/hyperliquid_verified_283d_btceth/`
carries a manifest with `synthetic_check: null` for BTC/ETH, yet the cached candle
files contain a single identical (open,high,low,close,volume) signature across all
6792 bars. The loader trusted the manifest flag and loaded flat data as if it were
real market evidence, producing a "REAL_MARKET_RUN" artifact with 0 trades that
looked like a truthful 283-day result rather than a placeholder dataset.

Targets:
- `verify_candles_not_synthetic` redetects flat/constant-close series at runtime.
- `load_verified_cache` in scripts/run_real_campaign.py re-detects and fails closed.
- A manifest missing `synthetic_check` is treated as unverified (never trusted).
- The shipped verified cache is honestly annotated with `synthetic_check`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.provenance import (  # noqa: E402
    ProvenanceError,
    load_provenance,
    verify_candles_not_synthetic,
)
from scripts.fetch_hyperliquid_candles import detect_synthetic_candles  # noqa: E402


def _flat(n=100, open_=60000.0, close=60000.0, vol=2e9):
    return [
        {"timestamp": "2025-12-20T%02d:00:00+00:00" % (i % 24),
         "open": open_, "high": open_ * 1.02, "low": open_ * 0.98,
         "close": close, "volume": vol}
        for i in range(n)
    ]


def _varied(n=100):
    import math
    out = []
    for i in range(n):
        px = 60000.0 + 1000.0 * math.sin(i / 7.0) + i
        out.append({"timestamp": "2025-12-20T%02d:00:00+00:00" % (i % 24),
                    "open": px, "high": px + 50, "low": px - 50,
                    "close": px + 25, "volume": float(2_000_000_000 + (i % 100) * 1_000_000)})
    return out


def test_verify_candles_not_synthetic_flags_flat_series():
    res = verify_candles_not_synthetic(_flat(100))
    assert res["is_synthetic"] is True
    assert res["reason"] == "flat_series_all_bars_identical"


def test_verify_candles_not_synthetic_flags_constant_close():
    out = [
        {"timestamp": "t%d" % i, "open": 60000.0 + i, "high": 60100.0 + i,
         "low": 59900.0 + i, "close": 60000.0, "volume": float(1_000_000 + i)}
        for i in range(100)
    ]
    res = verify_candles_not_synthetic(out)
    assert res["is_synthetic"] is True
    assert res["reason"] == "constant_close_no_price_movement"


def test_verify_candles_not_synthetic_passes_varied_series():
    res = verify_candles_not_synthetic(_varied(100))
    assert res["is_synthetic"] is False


def test_verify_candles_not_synthetic_raises_on_flat():
    with pytest.raises(ProvenanceError):
        verify_candles_not_synthetic(_flat(100), raise_on_synthetic=True)


def test_verify_candles_not_synthetic_missing_synthetic_check_is_untrusted():
    """A manifest entry without synthetic_check must not be treated as verified."""
    with pytest.raises(ProvenanceError):
        verify_candles_not_synthetic(_flat(100), require_synthetic_check=True)


def test_real_campaign_loader_rejects_flat_verified_cache():
    """scripts/run_real_campaign.load_verified_cache must fail closed on flat data."""
    from scripts.run_real_campaign import load_verified_cache  # noqa: E402

    manifest = load_provenance(
        str(REPO_ROOT / "research_state" / "cache" / "hyperliquid_verified_283d_btceth" / "provenance.json")
    )
    cache_dir = REPO_ROOT / "research_state" / "cache" / "hyperliquid_verified_283d_btceth"
    with pytest.raises(ProvenanceError):
        load_verified_cache(cache_dir, manifest)


def test_real_campaign_cli_rejects_flat_cache_full_evidence():
    """Full-evidence path must not silently ship a flat-cache artifact."""
    import subprocess

    proc = subprocess.run(
        [sys.executable, "scripts/run_real_campaign.py",
         "--cache-dir", "research_state/cache/hyperliquid_verified_283d_btceth",
         "--min-daily-volume-usd", "5000000"],
        cwd=str(REPO_ROOT), capture_output=True, text=True,
    )
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "synth" in (proc.stdout + proc.stderr).lower(), proc.stdout + proc.stderr


def test_shipped_verified_cache_manifest_is_honestly_annotated():
    """The shipped manifest must carry a synthetic_check that is not silently ok."""
    p = REPO_ROOT / "research_state" / "cache" / "hyperliquid_verified_283d_btceth" / "provenance.json"
    m = json.loads(p.read_text())
    for sym in ("BTC", "ETH"):
        entry = m["symbols"][sym]
        assert entry.get("synthetic_check") is not None, f"{sym} synthetic_check missing"
        assert entry["synthetic_check"].get("is_synthetic") is True, (
            f"{sym} must be flagged synthetic, got {entry['synthetic_check']}"
        )
        assert entry.get("status") != "ok", f"{sym} must not be status=ok while synthetic"