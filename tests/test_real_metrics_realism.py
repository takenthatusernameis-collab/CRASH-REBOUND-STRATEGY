"""Heavy deterministic tests for real-metrics realism (non-evidence, synthetic).

These tests exercise the portfolio->metrics pipeline with timestamps preserved and
prove DD series / timestamps are computed from real equity/trade paths. They do
NOT constitute performance evidence.
"""
import csv
from datetime import timedelta
from pathlib import Path

from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars, _parse_iso
from src.metrics.campaign_metrics import compute_campaign_metrics, metrics_to_dict, metrics_to_csv_rows
from scripts.run_real_campaign import load_verified_cache  # noqa: F401 (import sanity)
from scripts.run_portfolio import run_portfolio_simulation
from src.strategy.config import StrategyConfig


EXP = expected_hourly_bars(TARGET_START, TARGET_END)


def _stable_candles(n=EXP, base=50000.0):
    start = _parse_iso(TARGET_START)
    out = []
    for i in range(n):
        ts = start + timedelta(hours=i)
        o = base
        out.append({
            "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "timestamp_ms": int(ts.timestamp() * 1000),
            "open": o, "high": o * 1.002, "low": o * 0.998, "close": o, "volume": 200.0,
        })
    return out


def test_portfolio_simulation_produces_timestamped_equity_curve_and_metrics():
    # Use no-trade-ish stable candles; pipeline must still produce coherent artifacts.
    candles_by_symbol = {"BTC": _stable_candles(200), "ETH": _stable_candles(200)}
    config = StrategyConfig(use_rsi_trigger=False, enable_eth_hedge=False)
    res = run_portfolio_simulation(candles_by_symbol, config=config, capital=100000.0,
                                   eth_candles={"ETH": candles_by_symbol["ETH"]})
    trades = res.get("trades") or []
    metrics = metrics_to_dict(compute_campaign_metrics(trades=trades, equity_curve=res.get("equity_curve")))
    assert "max_drawdown_series" in metrics
    assert "max_drawdown" in metrics
    assert "exposure_metrics" in metrics
    # equity curve timestamps must be strings
    for pt in res.get("equity_curve") or []:
        assert "timestamp" in pt and "equity" in pt


def test_metrics_dd_series_carries_exit_timestamps_from_trades():
    trades = [
        {"exit_timestamp": "2026-01-01T00:00:00Z", "total_pnl": 50.0, "pnl": 50.0, "symbol": "BTC", "side": "long"},
        {"exit_timestamp": "2026-01-02T01:00:00Z", "total_pnl": -80.0, "pnl": -80.0, "symbol": "ETH", "side": "short"},
        {"exit_timestamp": "2026-01-03T02:00:00Z", "total_pnl": 10.0, "pnl": 10.0, "symbol": "BTC", "side": "long"},
    ]
    m = metrics_to_dict(compute_campaign_metrics(trades=trades))
    assert m["max_drawdown_timestamp"] == "2026-01-02T01:00:00Z"
    assert [p["timestamp"] for p in m["max_drawdown_series"]] == [
        "2026-01-01T00:00:00Z", "2026-01-02T01:00:00Z", "2026-01-03T02:00:00Z",
    ]


def test_metrics_to_csv_rows_includes_dd_series_hint(tmp_path):
    trades = [{"exit_timestamp": "2026-01-01T00:00:00Z", "total_pnl": -10.0, "pnl": -10.0, "symbol": "BTC", "side": "long"}]
    m = metrics_to_dict(compute_campaign_metrics(trades=trades))
    rows = metrics_to_csv_rows(m)
    p = tmp_path / "m.csv"
    with p.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["metric", "value"])
        w.writeheader()
        for row in rows:
            w.writerow(row)
    text = p.read_text()
    assert "max_drawdown_timestamp" in text
    assert "max_drawdown_series_points" in text or "max_drawdown_series" in text
    assert "2026-01-01T00:00:00Z" in text
