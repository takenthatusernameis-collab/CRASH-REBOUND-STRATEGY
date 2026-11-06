"""Track-4 hardening: universe derivation volume-key consistency + metrics sanitization.

Deterministic, synthetic, non-evidence. Failing-test-first targets:
- derive_verified_universe.max_rolling_24h_quote_volume must return a consistent
  key shape for empty and non-empty inputs (no key-shape drift).
- campaign_metrics must sanitize NaN/Inf in nested outputs and remain robust to
  malformed trade/equity records.
"""
from __future__ import annotations

import math

from scripts.derive_verified_universe import max_rolling_24h_quote_volume
from src.metrics.campaign_metrics import compute_campaign_metrics, metrics_to_dict


def test_rolling_24h_volume_empty_key_shape_consistent():
    out = max_rolling_24h_quote_volume([])
    assert out["bars"] == 0
    # canonical key must exist even when empty (no key-shape drift)
    assert "max_rolling_24h_quote_volume_usd_proxy" in out
    assert out["max_rolling_24h_quote_volume_usd_proxy"] == 0.0
    assert out["passes_5m_any_24h_window"] is False
    # optional legacy alias accepted but canonical must be present
    assert "first_ts_ms" in out and out["first_ts_ms"] is None
    assert "last_ts_ms" in out and out["last_ts_ms"] is None


def test_rolling_24h_volume_filters_window_and_counts():
    candles = [
        {"timestamp_ms": 0, "close": 10, "volume": 10},           # qv 100
        {"timestamp_ms": 3600000, "close": 10, "volume": 20},    # qv 200
        {"timestamp_ms": 25 * 3600000, "close": 10, "volume": 5},# outside 24h of last
    ]
    out = max_rolling_24h_quote_volume(candles, start_ms=0, end_ms=25 * 3600000)
    assert out["bars"] == 3
    # rolling 24h window max should include first two together but third alone after cutoff
    assert out["max_rolling_24h_quote_volume_usd_proxy"] >= 300.0 - 1e-9
    assert out["passes_5m_any_24h_window"] is False


def test_metrics_sanitizes_nan_inf_nested():
    trades = [
        {"total_pnl": float("nan"), "symbol": "X", "exit_timestamp": "2025-01-01T00:00:00Z"},
        {"total_pnl": float("inf"), "symbol": "X", "exit_timestamp": "2025-01-02T00:00:00Z"},
        {"total_pnl": -5.0, "symbol": "Y", "exit_timestamp": "2025-01-03T00:00:00Z"},
    ]
    m = compute_campaign_metrics(trades=trades)
    d = metrics_to_dict(m)

    def walk(v):
        if isinstance(v, float):
            assert math.isfinite(v), f"non-finite leaked: {v}"
        elif isinstance(v, dict):
            for vv in v.values():
                walk(vv)
        elif isinstance(v, list):
            for vv in v:
                walk(vv)
    walk(d)
    assert d["exposure_metrics"]["losing_trades"] == 1


def test_metrics_equity_curve_nonfinite_sanitized():
    m = compute_campaign_metrics(equity_curve=[
        {"equity": 100.0, "timestamp": "t1"},
        {"equity": float("nan"), "timestamp": "t2"},
        {"equity": float("-inf"), "timestamp": "t3"},
        {"equity": "bad", "timestamp": "t4"},
    ])
    d = metrics_to_dict(m)
    # series equities must be finite (bad/nan/inf treated via _finite -> 0.0)
    for pt in d.get("max_drawdown_series", []):
        assert math.isfinite(float(pt["equity"]))
        assert math.isfinite(float(pt["drawdown"]))
