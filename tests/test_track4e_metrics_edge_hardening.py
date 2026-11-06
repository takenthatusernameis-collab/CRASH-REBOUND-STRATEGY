"""Track-4e hardening: metrics max-DD timestamp alignment + equity-curve edge cases.

Deterministic, synthetic, non-evidence. Failing-test-first targets.
"""
from __future__ import annotations

import math

from src.metrics.campaign_metrics import compute_campaign_metrics, metrics_to_dict


def test_max_drawdown_timestamp_aligns_with_worst_point_from_trades():
    # cumulative pnl: 10 -> 5 (dd -5, worst) -> 6
    trades = [
        {"total_pnl": 10.0, "exit_timestamp": "2026-01-01T00:00:00Z", "symbol": "A"},
        {"total_pnl": -5.0, "exit_timestamp": "2026-01-02T00:00:00Z", "symbol": "A"},
        {"total_pnl": 1.0, "exit_timestamp": "2026-01-03T00:00:00Z", "symbol": "A"},
    ]
    m = compute_campaign_metrics(trades=trades)
    assert math.isclose(m["max_drawdown"], -5.0, rel_tol=0, abs_tol=1e-12)
    assert m["max_drawdown_timestamp"] == "2026-01-02T00:00:00Z"
    series = m["max_drawdown_series"]
    assert isinstance(series, list) and len(series) == 3
    worst = min(series, key=lambda p: p["drawdown"])
    assert worst["timestamp"] == "2026-01-02T00:00:00Z"


def test_equity_curve_drawdown_timestamp_and_length():
    curve = [
        {"equity": 100.0, "timestamp": "2026-01-01T00:00:00Z"},
        {"equity": 120.0, "timestamp": "2026-01-02T00:00:00Z"},
        {"equity": 90.0, "timestamp": "2026-01-03T00:00:00Z"},
        {"equity": 95.0, "timestamp": "2026-01-04T00:00:00Z"},
    ]
    m = compute_campaign_metrics(trades=[], equity_curve=curve)
    # peak 120 -> 90 => -30
    assert math.isclose(m["max_drawdown"], -30.0, rel_tol=0, abs_tol=1e-12)
    assert m["max_drawdown_timestamp"] == "2026-01-03T00:00:00Z"
    assert len(m["max_drawdown_series"]) == 4
    d = metrics_to_dict(m)
    # sanitized
    for pt in d["max_drawdown_series"]:
        assert math.isfinite(pt["equity"])
        assert math.isfinite(pt["drawdown"])


def test_metrics_accepts_numeric_epoch_timestamps_deterministically():
    trades = [
        {"total_pnl": 1.0, "exit_timestamp": 1766188800000, "symbol": "A"},  # ms epoch
    ]
    m = compute_campaign_metrics(trades=trades)
    assert isinstance(m["max_drawdown_series"][0]["timestamp"], str)
    assert m["max_drawdown_series"][0]["timestamp"].startswith("2025-12-20")
