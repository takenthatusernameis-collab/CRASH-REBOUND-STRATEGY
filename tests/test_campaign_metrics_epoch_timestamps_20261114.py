from datetime import datetime, timezone

from src.metrics.campaign_metrics import _parse_dt, compute_campaign_metrics


def test_parse_dt_handles_epoch_millis_and_seconds():
    ms = _parse_dt("1672531200000")
    assert ms == datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc)
    sec = _parse_dt("1672531200")
    assert sec == datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc)


def test_equity_horizon_uses_epoch_millis_not_garbled_iso_date():
    curve = [
        {"timestamp": "1672531200000", "equity": 100_000.0},
        {"timestamp": "1704067200000", "equity": 110_000.0},
    ]
    m = compute_campaign_metrics(trades=[], equity_curve=curve, initial_capital=100_000.0)
    assert abs(m["equity_horizon_years"] - 1.0) < 1e-9
    assert abs(m["equity_total_return_pct"] - 10.0) < 1e-9