from __future__ import annotations

import json
import sys
from datetime import timedelta
from pathlib import Path

from scripts.fetch_hyperliquid_candles import ingest_archive, analyze_coverage, _parse_iso
from scripts.derive_verified_universe import max_rolling_24h_quote_volume
from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars

EXP = expected_hourly_bars(TARGET_START, TARGET_END)


def _rows(n=48, start="2025-12-20T00:00:00Z", sym_price=100.0, vol=1_000_000.0):
    s = _parse_iso(start)
    return [
        {
            "timestamp": (s + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "open": sym_price,
            "high": sym_price * 1.01,
            "low": sym_price * 0.99,
            "close": sym_price,
            "volume": vol,
        }
        for i in range(n)
    ]


def test_ingest_multi_symbol_json_container(tmp_path):
    p = tmp_path / "multi.json"
    p.write_text(json.dumps({"BTC": _rows(sym_price=100), "ETH": _rows(sym_price=50)}))
    candles, meta = ingest_archive(p, "BTC")
    assert len(candles) == 48
    assert meta["source"] == "user_supplied_archive"
    # format may vary by loader path; key outcome is correct symbol extraction + provenance fields
    assert "sha256" in meta and len(meta["sha256"]) == 64


def test_ingest_multi_symbol_csv_with_symbol_column(tmp_path):
    import csv
    p = tmp_path / "multi.csv"
    with p.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["symbol", "timestamp", "open", "high", "low", "close", "volume"])
        w.writeheader()
        for r in _rows(sym_price=100):
            w.writerow({"symbol": "BTC", **r})
        for r in _rows(sym_price=50):
            w.writerow({"symbol": "ETH", **r})
    candles, meta = ingest_archive(p, "ETH")
    assert len(candles) == 48
    assert all(abs(c["close"] - 50.0) < 1e-9 for c in candles[:2])
    assert meta.get("multi_symbol_container") is True or meta.get("format") == "csv"


def test_derive_verified_universe_max_rolling_24h_volume():
    # 24 hourly bars at close=100, volume=100000 => 10,000,000 per bar quote, 240,000,000 window
    candles = _rows(n=24, sym_price=100.0, vol=100000.0)
    rep = max_rolling_24h_quote_volume(candles)
    assert rep["passes_5m_any_24h_window"] is True
    assert rep["max_rolling_24h_quote_volume_usd_proxy"] >= 240_000_000.0 - 1e-3


def test_derive_verified_universe_below_threshold():
    candles = _rows(n=24, sym_price=1.0, vol=1000.0)
    rep = max_rolling_24h_quote_volume(candles)
    assert rep["passes_5m_any_24h_window"] is False


def test_run_real_campaign_universe_file_blocks_when_no_match(tmp_path, monkeypatch):
    # complete manifest for BTC only
    manifest = {
        "fabricated_data": False,
        "real_market_data_intended": True,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": EXP},
        "summary": {"all_complete": True, "complete_symbols": ["BTC"]},
        "symbols": {
            "BTC": {
                "status": "ok",
                "coverage": {"expected_hourly_bars": EXP, "observed_in_window_bars": EXP, "gap_count": 0, "complete_for_target_window": True},
            }
        },
    }
    mp = tmp_path / "prov.json"
    mp.write_text(json.dumps(manifest))
    uf = tmp_path / "u.json"
    uf.write_text(json.dumps({"symbols": ["ZZZNOTREAL"]}))

    import scripts.run_real_campaign as rrc
    monkeypatch.setattr(sys, "argv", ["run_real_campaign.py", "--manifest", str(mp), "--universe-file", str(uf), "--cache-dir", str(tmp_path / "cache")])
    rc = rrc.main()
    assert rc == 2
