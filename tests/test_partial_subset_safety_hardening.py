"""Track-4 hardening (test-first): partial-not-evidence subset extraction must be safe.

Deterministic, synthetic non-evidence. An incomplete manifest may contain symbols that
claim completeness with inconsistent coverage fields; partial mode must include ONLY
symbols with fully verified-consistent completeness (expected==observed, gap_count==0).
It must never load/emit results for inconsistently-claimed symbols, and must never set
performance_evidence=true.
"""
from __future__ import annotations

import json
import sys
from datetime import timedelta
from pathlib import Path

from scripts.fetch_hyperliquid_candles import _parse_iso
from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars


EXP = expected_hourly_bars(TARGET_START, TARGET_END)


def _write_full_hourly_cache(cache_dir: Path, symbol: str, n: int) -> None:
    candles_dir = cache_dir / "candles"
    candles_dir.mkdir(parents=True, exist_ok=True)
    start = _parse_iso(TARGET_START)
    rows = []
    for i in range(n):
        ts = start + timedelta(hours=i)
        o = 100.0 + i * 0.001
        rows.append(
            {
                "t": int(ts.timestamp() * 1000),
                "o": o,
                "h": o + 1.0,
                "l": max(0.01, o - 1.0),
                "c": o + 0.2,
                "v": 1_000_000.0,
            }
        )
    (candles_dir / f"{symbol}.json").write_text(json.dumps(rows))


def test_partial_mode_excludes_inconsistent_complete_claim(tmp_path, monkeypatch):
    cache_dir = tmp_path / "cache" / "hyperliquid"
    _write_full_hourly_cache(cache_dir, "BTC", EXP)
    _write_full_hourly_cache(cache_dir, "ETH", EXP)  # cache exists, but manifest claim inconsistent
    m = {
        "schema_version": 1,
        "generated_at_utc": "2026-11-06T00:00:00Z",
        "run_type": "data_acquisition_provenance",
        "real_market_data_intended": True,
        "fabricated_data": False,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": EXP},
        "source": {"kind": "archive"},
        "symbols": {
            "BTC": {
                "status": "ok",
                "synthetic_check": {"is_synthetic": False, "reason": "varied_series_ok"},
                "cache_path": f"cache/candles/BTC.json",
                "coverage": {
                    "expected_hourly_bars": EXP,
                    "observed_in_window_bars": EXP,
                    "gap_count": 0,
                    "complete_for_target_window": True,
                },
                "volume_coverage": {"volume_filter_ok": True, "observed_min_24h_usd_volume": 9e9},
            },
            "ETH": {
                "status": "ok",
                "synthetic_check": {"is_synthetic": False, "reason": "varied_series_ok"},
                "cache_path": f"cache/candles/ETH.json",
                "coverage": {
                    "expected_hourly_bars": EXP,
                    "observed_in_window_bars": EXP - 10,  # inconsistent with complete claim
                    "gap_count": 0,
                    "complete_for_target_window": True,
                },
                "volume_coverage": {"volume_filter_ok": True, "observed_min_24h_usd_volume": 9e9},
            },
        },
        "summary": {"all_complete": False, "ready_for_real_campaign": False, "complete_symbols": ["BTC"]},
    }
    mp = cache_dir / "provenance.json"
    mp.write_text(json.dumps(m, indent=2))
    fake_repo = tmp_path / "repo"
    (fake_repo / "research_state").mkdir(parents=True)
    monkeypatch.setattr(sys, "argv", [
        "run_real_campaign.py", "--cache-dir", str(cache_dir), "--manifest", str(mp),
        "--output-prefix", "campaign_results_partial_safe", "--min-symbols", "1",
        "--allow-partial-not-evidence",
    ])
    import scripts.run_real_campaign as rrc

    monkeypatch.setattr(rrc, "REPO_ROOT", fake_repo)
    rc = rrc.main()
    assert rc == 0
    payload = json.loads((fake_repo / "research_state" / "campaign_results_partial_safe.json").read_text())
    assert payload["performance_evidence"] is False
    assert payload["partial_universe_not_evidence"] is True
    assert payload["data_provenance"]["symbols_loaded"] == ["BTC"]
    # subset evidence should not include inconsistently-claimed ETH
    assert "ETH" not in (payload["data_provenance"].get("coverage_summary") or {})
