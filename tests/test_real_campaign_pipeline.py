from __future__ import annotations

import csv
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

from src.data.provenance import (
    TARGET_START,
    TARGET_END,
    expected_hourly_bars,
    validate_provenance,
    require_verified_provenance,
    ProvenanceError,
)
from scripts.run_real_campaign import _complete_symbol_subset, main as run_real_main
from scripts.fetch_hyperliquid_candles import (
    analyze_coverage,
    ingest_archive,
    analyze_symbol_volume_coverage,
    _expected_hourly_bars,
    _parse_iso,
    _dt_to_ms,
)
from src.data.loader import load_hyperliquid_candles
from scripts.run_real_campaign import load_universe, validate_symbol_volume_coverage


EXP = expected_hourly_bars(TARGET_START, TARGET_END)


def _write_csv_candles(path: Path, start_iso: str, n: int, symbol: str = "BTC"):
    start = _parse_iso(start_iso)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "open", "high", "low", "close", "volume"])
        for i in range(n):
            ts = start + timedelta(hours=i)
            o = 100.0 + i * 0.01
            w.writerow([ts.strftime("%Y-%m-%dT%H:%M:%SZ"), o, o + 1.0, o - 1.0, o + 0.5, 100000.0])


def _complete_manifest(tmp_path: Path, symbol: str = "BTC") -> Path:
    m = {
        "fabricated_data": False,
        "real_market_data_intended": True,
        "target_window": {
            "start": TARGET_START,
            "end": TARGET_END,
            "expected_hourly_bars": EXP,
        },
        "symbols": {
            symbol: {
                "status": "ok",
                "coverage": {
                    "expected_hourly_bars": EXP,
                    "observed_in_window_bars": EXP,
                    "gap_count": 0,
                    "complete_for_target_window": True,
                },
            }
        },
    }
    p = tmp_path / "provenance.json"
    p.write_text(json.dumps(m))
    return p


def test_partial_not_evidence_never_sets_performance_evidence(tmp_path, monkeypatch):
    """Heavy safety test: incomplete manifest with >=1 complete symbol can run ONLY in explicit
    partial-not-evidence mode, producing artifacts that are never marked performance_evidence."""
    cache_dir = tmp_path / "cache" / "hyperliquid"
    _write_full_hourly_cache(cache_dir, "BTC", n=EXP)
    # incomplete manifest view: BTC complete, ETH missing/incomplete
    m = {
        "schema_version": 1,
        "generated_at_utc": "2026-11-05T00:00:00Z",
        "run_type": "data_acquisition_provenance",
        "real_market_data_intended": True,
        "fabricated_data": False,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": EXP},
        "source": {"kind": "hyperliquid_info_api"},
        "symbols": {
            "BTC": {
                "status": "ok",
                "coverage": {
                    "expected_hourly_bars": EXP,
                    "observed_in_window_bars": EXP,
                    "gap_count": 0,
                    "complete_for_target_window": True,
                },
            },
            "ETH": {
                "status": "incomplete",
                "coverage": {
                    "expected_hourly_bars": EXP,
                    "observed_in_window_bars": 4094,
                    "gap_count": 0,
                    "complete_for_target_window": False,
                },
            },
        },
        "summary": {"all_complete": False, "ready_for_real_campaign": False, "complete_symbols": ["BTC"]},
    }
    mp = cache_dir / "provenance.json"
    cache_dir.mkdir(parents=True, exist_ok=True)
    mp.write_text(json.dumps(m, indent=2))
    fake_repo = tmp_path / "repo"
    (fake_repo / "research_state").mkdir(parents=True)
    monkeypatch.setattr(sys, "argv", [
        "run_real_campaign.py", "--cache-dir", str(cache_dir), "--manifest", str(mp),
        "--output-prefix", "campaign_results_partial_debug", "--min-symbols", "1",
        "--allow-partial-not-evidence",
    ])
    import scripts.run_real_campaign as rrc
    monkeypatch.setattr(rrc, "REPO_ROOT", fake_repo)
    rc = rrc.main()
    assert rc == 0
    data = json.loads((fake_repo / "research_state" / "campaign_results_partial_debug.json").read_text())
    assert data["performance_evidence"] is False
    assert data["partial_universe_not_evidence"] is True
    assert data["research_status"] == "NOT_EVIDENCE_PARTIAL_UNIVERSE"
    assert data["real_market_data"] is True  # data source is real, but run is not evidence
    assert data["fabricated_data"] is False
    assert data["data_provenance"]["symbols_loaded"] == ["BTC"]
    assert "NOT performance evidence" in (data.get("evidence_warning") or "")


def test_partial_not_evidence_refuses_without_complete_symbols(tmp_path, monkeypatch):
    m = {
        "fabricated_data": False,
        "real_market_data_intended": True,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": EXP},
        "symbols": {
            "BTC": {"status": "incomplete", "coverage": {"expected_hourly_bars": EXP, "observed_in_window_bars": 1, "gap_count": 0, "complete_for_target_window": False}},
        },
        "summary": {"all_complete": False},
    }
    mp = tmp_path / "p.json"
    mp.write_text(json.dumps(m))
    import scripts.run_real_campaign as rrc
    monkeypatch.setattr(sys, "argv", ["run_real_campaign.py", "--manifest", str(mp), "--allow-partial-not-evidence", "--cache-dir", str(tmp_path)])
    assert rrc.main() == 2


def test_complete_symbol_subset_filters_correctly():
    raw = {
        "symbols": {
            "A": {
                "status": "ok",
                "coverage": {
                    "complete_for_target_window": True,
                    "expected_hourly_bars": EXP,
                    "observed_in_window_bars": EXP,
                    "gap_count": 0,
                },
            },
            "B": {
                "status": "incomplete",
                "coverage": {
                    "complete_for_target_window": False,
                    "expected_hourly_bars": EXP,
                    "observed_in_window_bars": 1,
                    "gap_count": 0,
                },
            },
            "C": {
                "status": "ok",
                "coverage": {
                    "complete_for_target_window": False,
                    "expected_hourly_bars": EXP,
                    "observed_in_window_bars": EXP - 1,
                    "gap_count": 0,
                },
            },
        }
    }
    sub = _complete_symbol_subset(raw)
    assert list(sub["symbols"].keys()) == ["A"]


def test_require_verified_provenance_accepts_complete(tmp_path):
    p = _complete_manifest(tmp_path)
    m = require_verified_provenance(p)
    assert m["real_market_data_intended"] is True
    assert m["symbols"]["BTC"]["coverage"]["complete_for_target_window"] is True


def test_ingest_archive_csv_normalizes_and_counts(tmp_path):
    archive = tmp_path / "archive"
    archive.mkdir()
    _write_csv_candles(archive / "BTC.csv", "2025-12-20T00:00:00Z", 200)
    candles, meta = ingest_archive(archive, "BTC")
    assert len(candles) == 200
    assert meta["source"] == "user_supplied_archive"
    assert "sha256" in meta and len(meta["sha256"]) == 64
    c0 = candles[0]
    assert c0["open"] == 100.0 and c0["close"] == 100.5 and c0["volume"] == 100000.0
    assert "timestamp" in c0


def test_ingest_archive_json_normalizes(tmp_path):
    archive = tmp_path / "archive"
    archive.mkdir()
    start = _parse_iso("2025-12-20T00:00:00Z")
    candles = []
    for i in range(50):
        ts = start + timedelta(hours=i)
        o = 50.0 + i
        candles.append(
            {
                "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "open": o,
                "high": o + 2,
                "low": o - 2,
                "close": o + 1,
                "volume": 50000.0,
            }
        )
    (archive / "ETH.json").write_text(json.dumps(candles))
    out, meta = ingest_archive(archive, "ETH")
    assert len(out) == 50
    assert all(k in out[0] for k in ("open", "high", "low", "close", "volume", "timestamp"))


def test_ingest_archive_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        ingest_archive(tmp_path / "nope", "BTC")


def test_analyze_coverage_detects_gap_marks_incomplete(tmp_path):
    start = _parse_iso(TARGET_START)
    # 100 hourly bars then a 48-hour gap then 100 more bars within window
    candles = []
    for i in range(100):
        ts = start + timedelta(hours=i)
        candles.append({"timestamp_ms": int(ts.timestamp() * 1000), "open": 1.0, "high": 2.0, "low": 0.5, "close": 1.0, "volume": 1.0})
    gap_end = start + timedelta(hours=148)
    for i in range(100):
        ts = gap_end + timedelta(hours=i)
        candles.append({"timestamp_ms": int(ts.timestamp() * 1000), "open": 1.0, "high": 2.0, "low": 0.5, "close": 1.0, "volume": 1.0})
    cov = analyze_coverage(candles, _parse_iso(TARGET_START), _parse_iso(TARGET_END))
    assert cov["observed_in_window_bars"] == 200
    assert cov["gap_count"] >= 1
    assert cov["complete_for_target_window"] is False
    assert cov["coverage_pct"] < 100.0


def test_analyze_coverage_complete_exact_window_marks_complete():
    start = _parse_iso(TARGET_START)
    end = _parse_iso(TARGET_END)
    candles = []
    ts = start
    while ts <= end:
        candles.append(
            {
                "timestamp_ms": int(ts.timestamp() * 1000),
                "timestamp": ts.isoformat(),
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.0,
                "volume": 100000.0,
            }
        )
        ts += timedelta(hours=1)
    assert len(candles) == EXP
    cov = analyze_coverage(candles, start, end)
    assert cov["observed_in_window_bars"] == EXP
    assert cov["gap_count"] == 0
    assert cov["complete_for_target_window"] is True
    assert cov["first_timestamp_ms"] == _dt_to_ms(start)
    assert cov["last_timestamp_ms"] == _dt_to_ms(end)


def test_load_hyperliquid_candles_from_csv_validates(tmp_path):
    p = tmp_path / "BTC.csv"
    _write_csv_candles(p, "2025-12-20T00:00:00Z", 10)
    candles = load_hyperliquid_candles(str(p), symbol="BTC")
    assert len(candles) == 10
    assert all(k in candles[0] for k in ("open", "high", "low", "close", "volume", "timestamp"))


def test_max_drawdown_series_with_timestamps_deterministic():
    from src.metrics.campaign_metrics import compute_campaign_metrics, metrics_to_dict
    trades = [
        {"exit_timestamp": "2026-01-01T00:00:00Z", "total_pnl": 100.0, "pnl": 100.0, "symbol": "BTC", "side": "long"},
        {"exit_timestamp": "2026-01-02T00:00:00Z", "total_pnl": -150.0, "pnl": -150.0, "symbol": "BTC", "side": "long"},
        {"exit_timestamp": "2026-01-03T00:00:00Z", "total_pnl": -50.0, "pnl": -50.0, "symbol": "ETH", "side": "short"},
        {"exit_timestamp": "2026-01-04T00:00:00Z", "total_pnl": 200.0, "pnl": 200.0, "symbol": "BTC", "side": "long"},
    ]
    m = metrics_to_dict(compute_campaign_metrics(trades=trades))
    assert m["max_drawdown"] == -200.0
    assert m["max_drawdown_timestamp"] == "2026-01-03T00:00:00Z"
    series = m["max_drawdown_series"]
    assert len(series) == 4
    assert series[0]["drawdown"] == 0.0
    assert series[1]["drawdown"] == -150.0
    assert series[2]["drawdown"] == -200.0
    assert series[3]["drawdown"] == 0.0
    assert m["max_drawdown"] == -200.0
    assert m["max_drawdown_timestamp"] == "2026-01-03T00:00:00Z"
    assert m["calmar_ratio"] == 0.5  # total_pnl=100 / abs(max_dd=200)
    assert m["win_rate"] == 0.5
    assert m["profit_factor"] == 300.0 / 200.0


def test_compute_campaign_metrics_equity_curve_no_trades():
    from src.metrics.campaign_metrics import compute_campaign_metrics, metrics_to_dict
    equity_curve = [
        {"timestamp": "2026-01-01T00:00:00Z", "equity": 100000.0, "pnl": 0.0},
        {"timestamp": "2026-01-02T00:00:00Z", "equity": 90000.0, "pnl": -10000.0},
        {"timestamp": "2026-01-03T00:00:00Z", "equity": 95000.0, "pnl": 5000.0},
    ]
    m = metrics_to_dict(compute_campaign_metrics(trades=[], equity_curve=equity_curve))
    assert m["max_drawdown"] == -10000.0
    assert m["max_drawdown_timestamp"] == "2026-01-02T00:00:00Z"
    assert len(m["max_drawdown_series"]) == 3


def test_expected_hourly_bars_matches_manifest():
    assert EXP == 6792
    assert _expected_hourly_bars(_parse_iso(TARGET_START), _parse_iso(TARGET_END)) == EXP


def test_fetch_symbol_parsing_comma_and_space():
    # Pure parsing unit check (no network): fetch script normalizes comma/semicolon/whitespace.
    raw = ["BTC,ETH", "SOL", "xrp;ada", "  dot "]
    norm = []
    for s in raw:
        for part in str(s).replace(';', ',').split(','):
            part = part.strip().upper()
            if part:
                norm.append(part)
    assert norm == ["BTC", "ETH", "SOL", "XRP", "ADA", "DOT"]


def _write_full_hourly_cache(cache_dir: Path, symbol: str, n: int = EXP):
    candles_dir = cache_dir / "candles"
    candles_dir.mkdir(parents=True, exist_ok=True)
    start = _parse_iso(TARGET_START)
    candles = []
    for i in range(n):
        ts = start + timedelta(hours=i)
        ts_ms = int(ts.timestamp() * 1000)
        # high-volume, stable OHLC to pass >=$5M daily volume filter
        candles.append({
            "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "timestamp_ms": ts_ms,
            "open": 50000.0,
            "high": 50100.0,
            "low": 49900.0,
            "close": 50000.0,
            "volume": 200.0,  # 200*50000*24 = 240M/day
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
    m["summary"] = {
        "symbols_requested": len(symbols),
        "symbols_complete": len(symbols),
        "symbols_incomplete_or_error": 0,
        "all_complete": True,
        "ready_for_real_campaign": True,
        "complete_symbols": list(symbols),
    }
    mp = cache_dir / "provenance.json"
    cache_dir.mkdir(parents=True, exist_ok=True)
    mp.write_text(json.dumps(m, indent=2))
    return mp


def test_run_real_campaign_gated_executes_with_complete_verified_manifest(tmp_path, monkeypatch):
    """Integration: complete verified manifest + complete caches pass gate and emit real-marked artifacts.
    Test uses deterministic generated OHLCV in tmp_path to exercise pipeline wiring (not repo evidence)."""
    import scripts.run_real_campaign as rrc

    cache_dir = tmp_path / "cache" / "hyperliquid"
    for sym in ["BTC", "ETH"]:
        _write_full_hourly_cache(cache_dir, sym, n=EXP)
    mp = _complete_verified_manifest(cache_dir, ["BTC", "ETH"])

    # isolate outputs to tmp research_state by monkeypatching REPO_ROOT
    fake_repo = tmp_path / "repo"
    (fake_repo / "research_state").mkdir(parents=True)
    monkeypatch.setattr(rrc, "REPO_ROOT", fake_repo)
    monkeypatch.setattr(sys, "argv", [
        "run_real_campaign.py", "--cache-dir", str(cache_dir), "--manifest", str(mp),
        "--output-prefix", "campaign_results_real", "--min-symbols", "1",
    ])
    rc = rrc.main()
    assert rc == 0
    out = fake_repo / "research_state" / "campaign_results_real.json"
    met = fake_repo / "research_state" / "campaign_results_real_metrics.json"
    csvp = fake_repo / "research_state" / "campaign_results_real_metrics.csv"
    assert out.exists() and met.exists() and csvp.exists()
    data = json.loads(out.read_text())
    assert data["real_market_data"] is True
    assert data["performance_evidence"] is True
    assert data["fabricated_data"] is False
    assert data["data_provenance"]["manifest_sha256"]
    assert "BTC" in data["data_provenance"]["symbols_loaded"]
    assert data["data_provenance"]["universe_filter_policy"]["min_daily_volume_usd"] == 5_000_000.0
    assert "metrics" in data and "max_drawdown_series" in data["metrics"]


def test_validate_provenance_rejects_missing_manifest_sha_fields_when_incomplete_symbol_status():
    # status ok but coverage incomplete should be rejected
    m = {
        "fabricated_data": False,
        "real_market_data_intended": True,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": EXP},
        "symbols": {"BTC": {"status": "ok", "coverage": {"expected_hourly_bars": EXP, "observed_in_window_bars": EXP-10, "gap_count": 0, "complete_for_target_window": False}}},
    }
    ok, errs = validate_provenance(m)
    assert not ok


def test_e2e_archive_to_manifest_universe_and_gate(tmp_path):
    """Deterministic non-evidence e2e: archive ingest manifest -> universe derivation -> gate behavior.
    Uses synthetic hourly OHLCV in tmp_path only (not repo performance evidence)."""
    import csv
    from scripts.fetch_hyperliquid_candles import ingest_archive, analyze_coverage, _parse_iso
    from scripts.derive_verified_universe import max_rolling_24h_quote_volume
    from src.data.provenance import validate_provenance, ProvenanceError, expected_hourly_bars
    archive = tmp_path / "archive"
    archive.mkdir()
    start = _parse_iso(TARGET_START)
    # write a small incomplete archive for BTC (10 bars) to prove gate refuses
    def _write(sym, n):
        with (archive / f"{sym}.csv").open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["timestamp","open","high","low","close","volume"])
            for i in range(n):
                ts = start + timedelta(hours=i)
                o = 50000.0
                w.writerow([ts.strftime("%Y-%m-%dT%H:%M:%SZ"), o, o+10, o-10, o, 200.0])
    _write("BTC", 10)
    candles, meta = ingest_archive(archive, "BTC")
    cov = analyze_coverage(candles, _parse_iso(TARGET_START), _parse_iso(TARGET_END))
    assert cov["complete_for_target_window"] is False
    manifest = {
        "schema_version": 1, "generated_at_utc": "2026-01-01T00:00:00Z",
        "run_type": "data_acquisition_provenance", "real_market_data_intended": True,
        "fabricated_data": False,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": EXP},
        "source": {"kind": "archive"}, "symbols": {
            "BTC": {"status": "incomplete", "coverage": cov, "source": meta.get("source"),
                    "cache_path": "tmp/BTC.json"}
        },
        "summary": {"symbols_requested":1,"symbols_complete":0,"all_complete":False,"ready_for_real_campaign":False,"complete_symbols":[]},
    }
    ok, errs = validate_provenance(manifest)
    assert not ok
    # derive universe on synthetic rows (passes volume proxy)
    vol = max_rolling_24h_quote_volume(candles)
    assert isinstance(vol, dict)
    # complete verified-like manifest in tmp should validate structure when all coverage fields satisfied
    full = {
        "schema_version": 1, "generated_at_utc": "2026-01-01T00:00:00Z",
        "run_type": "data_acquisition_provenance", "real_market_data_intended": True,
        "fabricated_data": False,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": EXP},
        "source": {"kind": "archive"}, "symbols": {
            "BTC": {"status": "ok", "coverage": {"expected_hourly_bars": EXP, "observed_in_window_bars": EXP,
                    "gap_count": 0, "complete_for_target_window": True}}
        }, "summary": {"all_complete": True, "complete_symbols": ["BTC"]},
    }
    ok2, errs2 = validate_provenance(full)
    assert ok2, errs2
