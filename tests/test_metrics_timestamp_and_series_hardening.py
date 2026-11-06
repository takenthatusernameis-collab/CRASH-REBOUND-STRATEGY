import math
from src.metrics.campaign_metrics import compute_campaign_metrics, metrics_to_dict, metrics_to_csv_rows


def test_max_dd_uses_exit_timestamp_preference():
    trades = [
        {'symbol': 'BTC', 'side': 'long', 'pnl': 10.0, 'entry_timestamp': '2026-01-01T00:00:00Z', 'exit_timestamp': '2026-01-01T01:00:00Z', 'timestamp': '2026-01-01T00:30:00Z'},
        {'symbol': 'BTC', 'side': 'long', 'pnl': -15.0, 'entry_timestamp': '2026-01-01T02:00:00Z', 'exit_timestamp': '2026-01-01T03:00:00Z', 'timestamp': '2026-01-01T02:30:00Z'},
        {'symbol': 'BTC', 'side': 'long', 'pnl': 5.0, 'entry_timestamp': '2026-01-01T04:00:00Z', 'exit_timestamp': '2026-01-01T05:00:00Z'},
    ]
    m = compute_campaign_metrics(trades=trades)
    assert m['max_drawdown'] == -15.0
    assert m['max_drawdown_timestamp'] == '2026-01-01T03:00:00Z'
    assert len(m['max_drawdown_series']) == 3
    assert m['max_drawdown_series'][1]['timestamp'] == '2026-01-01T03:00:00Z'
    assert m['max_drawdown_series'][1]['drawdown'] == -15.0


def test_monthly_weekly_breakdown_use_exit_or_fallback_timestamp():
    trades = [
        {'pnl': 7.0, 'exit_timestamp': '2026-01-31T23:00:00Z'},
        {'pnl': -2.0, 'entry_timestamp': '2026-02-01T00:00:00Z'},
        {'pnl': 3.0, 'timestamp': '2026-02-02T00:00:00Z'},
    ]
    m = compute_campaign_metrics(trades=trades)
    assert m['monthly_breakdown']['2026-01'] == 7.0
    assert m['monthly_breakdown']['2026-02'] == 1.0
    assert sum(m['monthly_breakdown'].values()) == 8.0


def test_equity_curve_metrics_sanitize_nonfinite_and_track_max_dd():
    curve = [
        {'timestamp': '2026-01-01T00:00:00Z', 'equity': 100.0},
        {'timestamp': '2026-01-01T01:00:00Z', 'equity': float('nan')},
        {'timestamp': '2026-01-01T02:00:00Z', 'equity': 90.0},
        {'timestamp': '2026-01-01T03:00:00Z', 'equity': float('inf')},
    ]
    m = compute_campaign_metrics(trades=[], equity_curve=curve)
    assert len(m['max_drawdown_series']) == 4
    assert m['max_drawdown_series'][1]['equity'] == 0.0
    assert math.isfinite(m['max_drawdown'])
    d = metrics_to_dict(m)
    for pt in d['max_drawdown_series']:
        assert math.isfinite(float(pt['equity']))
        assert math.isfinite(float(pt['drawdown']))


def test_metrics_to_csv_rows_stable_and_finite():
    m = compute_campaign_metrics(trades=[{'pnl': 1.0, 'exit_timestamp': '2026-01-01T00:00:00Z'}])
    m['weird'] = float('nan')
    rows = metrics_to_csv_rows(m)
    keys = [r['metric'] for r in rows]
    assert keys == sorted(keys)
    vals = {r['metric']: r['value'] for r in rows}
    assert vals['weird'] == 0.0
    assert 'max_drawdown_series_points' in vals
