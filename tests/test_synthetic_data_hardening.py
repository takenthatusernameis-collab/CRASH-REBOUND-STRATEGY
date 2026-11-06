"""Track-4 hardening: synthetic/flat candle series must never be accepted as real evidence.

Failing-test-first targets:
- detect_synthetic_candles flags a constant flat series (all bars identical).
- detect_synthetic_candles flags a series with constant close but varied volume.
- detect_synthetic_candles passes a genuinely varied real-looking series.
- provenance gate (validate_provenance) refuses a manifest whose symbol carries
  synthetic_check.is_synthetic=true even if coverage claims completeness.
- safe complete-subset extraction drops a synthetic symbol.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.fetch_hyperliquid_candles import detect_synthetic_candles  # noqa: E402
from src.data.provenance import (  # noqa: E402
    TARGET_END,
    TARGET_START,
    complete_symbol_subset,
    expected_hourly_bars,
    validate_provenance,
)


def _flat(n=100, open_=60000.0, close=60000.0, vol=2e9):
    return [
        {"timestamp_ms": 1766188800000 + i * 3600000, "open": open_, "high": open_ * 1.02,
         "low": open_ * 0.98, "close": close, "volume": vol}
        for i in range(n)
    ]


def _constant_close_varied_volume(n=100):
    out = []
    for i in range(n):
        out.append({"timestamp_ms": 1766188800000 + i * 3600000, "open": 60000.0 + i,
                    "high": 60100.0 + i, "low": 59900.0 + i, "close": 60000.0,
                    "volume": float(1_000_000 + i)})
    return out


def _varied(n=100):
    import math
    out = []
    for i in range(n):
        px = 60000.0 + 1000.0 * math.sin(i / 7.0) + i
        out.append({"timestamp_ms": 1766188800000 + i * 3600000, "open": px,
                    "high": px + 50, "low": px - 50, "close": px + 25,
                    "volume": float(2_000_000_000 + (i % 100) * 1_000_000)})
    return out


def test_detects_flat_all_identical_series():
    res = detect_synthetic_candles(_flat(100))
    assert res["is_synthetic"] is True
    assert res["reason"] == "flat_series_all_bars_identical"
    assert res["distinct_signatures"] == 1


def test_detects_constant_close_series():
    res = detect_synthetic_candles(_constant_close_varied_volume(100))
    assert res["is_synthetic"] is True
    assert res["reason"] == "constant_close_no_price_movement"


def test_passes_genuinely_varied_series():
    res = detect_synthetic_candles(_varied(100))
    assert res["is_synthetic"] is False
    assert res["distinct_signatures"] == 100


def test_empty_series_flagged_synthetic():
    res = detect_synthetic_candles([])
    assert res["is_synthetic"] is True
    assert res["reason"] == "empty_series"


def _manifest(sym, *, synthetic=False, complete=True):
    exp = expected_hourly_bars(TARGET_START, TARGET_END)
    return {
        "fabricated_data": False,
        "real_market_data_intended": True,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": exp},
        "symbols": {
            sym: {
                "status": "ok" if (complete and not synthetic) else "error",
                "coverage": {
                    "expected_hourly_bars": exp,
                    "observed_in_window_bars": exp,
                    "gap_count": 0,
                    "complete_for_target_window": bool(complete and not synthetic),
                },
                "synthetic_check": {"is_synthetic": synthetic, "reason": "flat" if synthetic else "ok"},
            }
        },
    }


def test_gate_refuses_synthetic_symbol_even_when_coverage_claims_complete():
    m = _manifest("BTC", synthetic=True, complete=True)
    ok, errs = validate_provenance(m, require_complete=True, min_symbols=1)
    assert ok is False
    assert any("synthetic" in e for e in errs), errs


def test_gate_accepts_clean_complete_manifest():
    m = _manifest("BTC", synthetic=False, complete=True)
    ok, errs = validate_provenance(m, require_complete=True, min_symbols=1)
    assert ok is True, errs


def test_safe_subset_drops_synthetic_symbol():
    m = {
        "symbols": {
            "BTC": {"status": "ok",
                    "coverage": {"expected_hourly_bars": expected_hourly_bars(TARGET_START, TARGET_END),
                                 "observed_in_window_bars": expected_hourly_bars(TARGET_START, TARGET_END),
                                 "gap_count": 0, "complete_for_target_window": True},
                    "synthetic_check": {"is_synthetic": True, "reason": "flat"}},
            "ETH": {"status": "ok",
                    "coverage": {"expected_hourly_bars": expected_hourly_bars(TARGET_START, TARGET_END),
                                 "observed_in_window_bars": expected_hourly_bars(TARGET_START, TARGET_END),
                                 "gap_count": 0, "complete_for_target_window": True},
                    "synthetic_check": {"is_synthetic": False, "reason": "ok"}},
        }
    }
    sub = complete_symbol_subset(m)
    assert sorted(sub["symbols"].keys()) == ["ETH"]
    assert sub["summary"]["complete_symbols_subset"] == ["ETH"]