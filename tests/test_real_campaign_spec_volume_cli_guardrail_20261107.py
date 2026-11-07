"""HANDOFF 2026-11-07T03:54Z priority (1): $5M/no-lookahead gating audit.

Failing-tests-first: spec-compliant full-evidence `run_real_campaign` path must
not accept a sub-$5M daily-volume threshold (would bypass >=$5M spec filter at
the verified-manifest validation boundary). Partial-not-evidence debug mode is
excluded from spec-evidence claims and is not required to satisfy spec volume.

Synthetic fixtures only (non-evidence).
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import scripts.run_real_campaign as rrc
from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars
from scripts.fetch_hyperliquid_candles import _parse_iso, _dt_to_ms

EXP = expected_hourly_bars(TARGET_START, TARGET_END)


def _write_full_hourly_cache(cache_dir: Path, symbol: str, n: int = EXP):
    candles_dir = cache_dir / "candles"
    candles_dir.mkdir(parents=True, exist_ok=True)
    start = _parse_iso(TARGET_START)
    candles = []
    for i in range(n):
        ts = start + dt.timedelta(hours=i)
        # Varied per-bar signatures: the runtime synthetic/flat guard re-detects
        # constant OHLCV at load time, so fixtures must carry distinct signatures.
        o = 50000.0 + (i % 7) * 0.25
        candles.append({
            "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "timestamp_ms": _dt_to_ms(ts),
            "open": o, "high": o + 100.0 + (i % 5), "low": o - 100.0 - (i % 3),
            "close": o + 50.0 + (i % 11), "volume": 200.0 + (i % 13),
        })
    (candles_dir / f"{symbol}.json").write_text(json.dumps(candles))


def _complete_verified_manifest(cache_dir: Path, symbols):
    m = {
        "schema_version": 1,
        "generated_at_utc": "2026-11-05T00:00:00Z",
        "run_type": "data_acquisition_provenance",
        "real_market_data_intended": True,
        "fabricated_data": False,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": EXP},
        "source": {"kind": "archive", "input_archive": "/verified/archive", "hl_url": None},
        "symbols": {},
        "summary": {},
    }
    for sym in symbols:
        m["symbols"][sym] = {
            "status": "ok",
            "source": "user_supplied_archive",
            "cache_path": f"research_state/cache/hyperliquid/candles/{sym}.json",
            "synthetic_check": {"is_synthetic": False, "reason": "varied_series_ok"},
            "coverage": {
                "expected_hourly_bars": EXP,
                "observed_in_window_bars": EXP,
                "coverage_pct": 100.0,
                "first_timestamp_ms": _dt_to_ms(_parse_iso(TARGET_START)),
                "last_timestamp_ms": _dt_to_ms(_parse_iso(TARGET_END)),
                "gap_count": 0,
                "gaps": [],
                "complete_for_target_window": True,
                "start": TARGET_START,
                "end": TARGET_END,
            },
            "volume_coverage": {
                "min_daily_volume_usd": 5_000_000.0,
                "observed_min_24h_usd_volume": 240000000.0,
                "observed_mean_24h_usd_volume": 240000000.0,
                "bars_checked": EXP,
                "bars_passing": EXP,
                "volume_filter_ok": True,
            },
        }
    m["summary"] = {"symbols_requested": len(symbols), "symbols_complete": len(symbols),
                    "symbols_incomplete_or_error": 0, "all_complete": True,
                    "ready_for_real_campaign": True, "complete_symbols": list(symbols)}
    mp = cache_dir / "provenance.json"
    cache_dir.mkdir(parents=True, exist_ok=True)
    mp.write_text(json.dumps(m, indent=2))
    return mp


def test_full_evidence_rejects_sub_5m_min_daily_volume_usd(tmp_path, monkeypatch, capsys):
    cache_dir = tmp_path / "cache" / "hyperliquid"
    _write_full_hourly_cache(cache_dir, "BTC", n=EXP)
    mp = _complete_verified_manifest(cache_dir, ["BTC"])
    fake_repo = tmp_path / "repo"
    (fake_repo / "research_state").mkdir(parents=True)
    monkeypatch.setattr(rrc, "REPO_ROOT", fake_repo)
    monkeypatch.setattr(sys, "argv", [
        "run_real_campaign.py", "--cache-dir", str(cache_dir), "--manifest", str(mp),
        "--min-daily-volume-usd", "1000000",
    ])
    rc = rrc.main()
    assert rc == 2
    err = capsys.readouterr().err.lower()
    assert "5" in err and ("volume" in err or "spec" in err or "million" in err or "000" in err)


def test_full_evidence_accepts_explicit_5m_threshold(tmp_path, monkeypatch):
    cache_dir = tmp_path / "cache" / "hyperliquid"
    _write_full_hourly_cache(cache_dir, "BTC", n=EXP)
    mp = _complete_verified_manifest(cache_dir, ["BTC"])
    fake_repo = tmp_path / "repo"
    (fake_repo / "research_state").mkdir(parents=True)
    monkeypatch.setattr(rrc, "REPO_ROOT", fake_repo)
    monkeypatch.setattr(sys, "argv", [
        "run_real_campaign.py", "--cache-dir", str(cache_dir), "--manifest", str(mp),
        "--min-daily-volume-usd", "5000000",
    ])
    rc = rrc.main()
    assert rc == 0
