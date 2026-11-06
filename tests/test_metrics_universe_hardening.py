"""Heavy deterministic metrics/universe hardening tests (synthetic, non-evidence).

These tests encode expected deterministic behavior of the metrics pipeline and
universe derivation edge cases. They are regression guards only and do NOT
constitute performance evidence. Test-first: each test asserts behavior the
implementation must satisfy deterministically.
"""
from __future__ import annotations

import json
import math
from datetime import timedelta

from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars, _parse_iso
from src.metrics.campaign_metrics import (
    compute_campaign_metrics,
    compute_metrics_from_trades,
    metrics_to_csv_rows,
    metrics_to_dict,
)

EXP = expected_hourly_bars(TARGET_START, TARGET_END)


def _candle(ts_ms, close=50000.0, volume=200.0):
    return {
        "timestamp_ms": ts_ms,
        "timestamp": f"{ts_ms // 1000}Z",
        "open": close, "high": close * 1.002, "low": close * 0.998,
        "close": close, "volume": volume,
    }


def _trade(exit_ts, pnl, symbol="BTC", side="long", total_pnl=None, hedge_pnl=0.0):
    return {
        "symbol": symbol, "side": side,
        "exit_timestamp": exit_ts,
        "pnl": pnl,
        "total_pnl": total_pnl if total_pnl is not None else pnl,
        "hedge_pnl": hedge_pnl,
    }


def test_empty_trades_returns_safe_zero_metrics_no_crash():
    m = metrics_to_dict(compute_metrics_from_trades([]))
    assert m["max_drawdown"] == 0.0
    assert m["max_drawdown_timestamp"] is None
    assert m["max_drawdown_series"] == []
    assert m["win_rate"] == 0.0
    assert m["profit_factor"] == 0.0
    assert m["sharpe_ratio"] == 0.0
    assert m["sortino_ratio"] == 0.0
    assert m["calmar_ratio"] == 0.0
    assert m["monthly_breakdown"] == {}
    assert m["weekly_breakdown"] == {}
    assert m["trade_attribution"] == []
    assert m["trade_attribution_by_leg"] == []
    exp = m["exposure_metrics"]
    assert exp["total_trades"] == 0
    assert exp["total_pnl"] == 0.0
    assert exp["winning_trades"] == 0
    assert exp["losing_trades"] == 0
    assert exp["gross_profit"] == 0.0
    assert exp["gross_loss"] == 0.0


def test_empty_trades_with_equity_curve_computes_drawdown_from_curve():
    start = _parse_iso(TARGET_START)
    curve = []
    for i in range(5):
        ts = start + timedelta(hours=i)
        curve.append({
            "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "equity": 100000.0 - i * 1000.0,
        })
    m = metrics_to_dict(compute_campaign_metrics(trades=[], equity_curve=curve))
    assert m["max_drawdown"] == -4000.0
    assert m["max_drawdown_timestamp"] == curve[-1]["timestamp"]
    assert len(m["max_drawdown_series"]) == 5
    assert all("timestamp" in p and "equity" in p and "drawdown" in p for p in m["max_drawdown_series"])


def test_non_finite_pnl_sanitized_to_zero():
    m = metrics_to_dict(compute_metrics_from_trades([
        _trade("2026-01-01T00:00:00Z", float("nan")),
        _trade("2026-01-02T00:00:00Z", float("inf")),
        _trade("2026-01-03T00:00:00Z", -50.0),
        _trade("2026-01-04T00:00:00Z", "not-a-number"),
        _trade("2026-01-05T00:00:00Z", 100.0),
    ]))
    # NaN/inf/invalid -> 0; only -50 and 100 count
    exp = m["exposure_metrics"]
    assert exp["total_pnl"] == 50.0
    assert exp["winning_trades"] == 1
    assert exp["losing_trades"] == 1
    assert exp["total_trades"] == 5


def test_max_drawdown_timestamp_from_exit_timestamp():
    m = metrics_to_dict(compute_metrics_from_trades([
        _trade("2026-01-01T00:00:00Z", 100.0),
        _trade("2026-01-02T01:00:00Z", -300.0),
        _trade("2026-01-03T02:00:00Z", 10.0),
    ]))
    assert m["max_drawdown_timestamp"] == "2026-01-02T01:00:00Z"
    assert m["max_drawdown"] == -300.0
    assert [p["timestamp"] for p in m["max_drawdown_series"]] == [
        "2026-01-01T00:00:00Z", "2026-01-02T01:00:00Z", "2026-01-03T02:00:00Z",
    ]


def test_trade_timestamp_falls_back_entry_then_timestamp_key():
    m = metrics_to_dict(compute_metrics_from_trades([
        {"exit_timestamp": None, "entry_timestamp": "2026-02-01T00:00:00Z", "pnl": 10.0, "total_pnl": 10.0},
        {"exit_timestamp": None, "entry_timestamp": None, "timestamp": "2026-02-02T00:00:00Z", "pnl": -5.0, "total_pnl": -5.0},
    ]))
    assert m["max_drawdown_timestamp"] == "2026-02-02T00:00:00Z"
    assert m["max_drawdown"] == -5.0  # equity 10 then 5, dd from peak 10 -> -5


def test_numeric_ts_ms_vs_seconds_boundary():
    # numeric `timestamp` key: ms (>1e10) and seconds (<1e10) both normalized to ISO
    m = metrics_to_dict(compute_metrics_from_trades([
        {"timestamp": 1766188800000, "pnl": 10.0, "total_pnl": 10.0},
        {"timestamp": 1766188800, "pnl": -5.0, "total_pnl": -5.0},
    ]))
    # 1766188800000 ms = 2025-12-20T00:00:00Z ; 1766188800 s = same instant
    assert m["max_drawdown_series"][0]["timestamp"] == "2025-12-20T00:00:00Z"
    assert m["max_drawdown_series"][1]["timestamp"] == "2025-12-20T00:00:00Z"


def test_monthly_weekly_aggregation_deterministic_and_order_independent():
    trades = [
        _trade("2026-01-15T10:00:00Z", 100.0),
        _trade("2026-01-20T12:00:00Z", -40.0),
        _trade("2026-02-03T08:00:00Z", 200.0),
    ]
    m1 = compute_metrics_from_trades(list(trades))
    m2 = compute_metrics_from_trades(list(reversed(trades)))
    assert m1["monthly_breakdown"] == m2["monthly_breakdown"]
    assert m1["weekly_breakdown"] == m2["weekly_breakdown"]
    assert m1["monthly_breakdown"]["2026-01"] == 60.0
    assert m1["monthly_breakdown"]["2026-02"] == 200.0


def test_profit_factor_edge_cases():
    # All wins -> gross_loss 0 -> profit_factor 1.0 if profit > 0 else 0
    m = metrics_to_dict(compute_metrics_from_trades([
        _trade("2026-01-01T00:00:00Z", 10.0), _trade("2026-01-02T00:00:00Z", 20.0),
    ]))
    assert m["profit_factor"] == 1.0
    # All losses -> gross_profit 0 -> profit_factor 0
    m = metrics_to_dict(compute_metrics_from_trades([
        _trade("2026-01-01T00:00:00Z", -10.0), _trade("2026-01-02T00:00:00Z", -20.0),
    ]))
    assert m["profit_factor"] == 0.0


def test_csv_rows_covers_scalar_metrics_and_series_points_hint():
    m = metrics_to_dict(compute_metrics_from_trades([
        _trade("2026-01-01T00:00:00Z", 50.0),
        _trade("2026-01-02T00:00:00Z", -20.0),
    ]))
    rows = metrics_to_csv_rows(m)
    keys = {r["metric"] for r in rows}
    assert "max_drawdown_series_points" in keys
    assert "max_drawdown" in keys
    assert "win_rate" in keys
    assert "sharpe_ratio" in keys
    # series points equals series length
    sp = [r for r in rows if r["metric"] == "max_drawdown_series_points"][0]["value"]
    assert sp == len(m["max_drawdown_series"])
    # all values finite/sanitized
    for r in rows:
        if isinstance(r["value"], float):
            assert math.isfinite(r["value"])


def test_trade_attribution_includes_coin_and_hedge_pnl():
    m = metrics_to_dict(compute_metrics_from_trades([
        _trade("2026-01-01T00:00:00Z", 100.0, symbol="BTC", side="long", total_pnl=100.0, hedge_pnl=5.0),
        _trade("2026-01-02T00:00:00Z", -30.0, symbol="ETH", side="short", total_pnl=-30.0, hedge_pnl=-2.0),
    ]))
    by_sym = {a["symbol"]: a for a in m["trade_attribution"]}
    assert by_sym["BTC"]["pnl"] == 100.0
    assert by_sym["BTC"]["coin_pnl"] == 100.0
    assert by_sym["BTC"]["hedge_pnl"] == 5.0
    assert by_sym["ETH"]["pnl"] == -30.0
    assert by_sym["ETH"]["hedge_pnl"] == -2.0
    by_leg = {a["leg"]: a for a in m["trade_attribution_by_leg"]}
    assert by_leg["long"]["pnl"] == 100.0
    assert by_leg["short"]["pnl"] == -30.0


def test_expected_hourly_bars_matches_spec_window():
    assert EXP == 6792
    assert expected_hourly_bars(TARGET_START, TARGET_END) == 6792


def test_target_window_iso_parses_utc():
    s = _parse_iso(TARGET_START)
    e = _parse_iso(TARGET_END)
    assert s.tzinfo is not None and e.tzinfo is not None
    delta_h = int((e.timestamp() - s.timestamp()) // 3600)
    assert delta_h + 1 == 6792
    # JSON-serializable manifest round-trip
    manifest = {
        "schema_version": 1,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": EXP},
        "fabricated_data": False,
        "all_complete": False,
        "ready_for_real_campaign": False,
    }
    assert json.loads(json.dumps(manifest)) == manifest
