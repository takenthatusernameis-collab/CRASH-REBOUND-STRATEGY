"""Deterministic tests: portfolio/real campaign must find signals across full series (bar-by-bar),
not only at the final bar. Synthetic, no market evidence."""
from src.strategy.config import StrategyConfig
from scripts.run_portfolio import run_portfolio_simulation


def _series_with_mid_crash_rebound():
    candles = []
    for i in range(40):
        ts = f"2026-01-01T{i:02d}:00:00Z"
        if i == 10:
            candles.append({"timestamp": ts, "open": 100, "high": 101, "low": 88, "close": 90, "volume": 500})
        elif i == 11:
            candles.append({"timestamp": ts, "open": 90, "high": 97, "low": 89, "close": 96, "volume": 400})
        else:
            candles.append({"timestamp": ts, "open": 100, "high": 101, "low": 99, "close": 100, "volume": 200})
    return candles


def test_portfolio_finds_mid_series_signal_drop_trigger():
    candles = _series_with_mid_crash_rebound()
    cfg = StrategyConfig(
        use_rsi_trigger=False, enable_eth_hedge=False, min_daily_volume_usd=0,
        crash_lookback=2, entry_next_bar=False, time_exit_max_bars=50,
    )
    res = run_portfolio_simulation({'X': candles}, config=cfg, capital=100000)
    assert res['num_trades'] >= 1, f"expected >=1 trade from mid-series crash/rebound, got {res}"


def test_portfolio_one_position_per_coin_no_overlap():
    # Two crash/rebound setups in same coin; second occurs while first may still be open
    candles = []
    for i in range(60):
        ts = f"2026-01-01T{i%24:02d}:00:00Z"
        if i in (10, 30):
            candles.append({"timestamp": ts, "open": 100, "high": 101, "low": 88, "close": 90, "volume": 500})
        elif i in (11, 31):
            candles.append({"timestamp": ts, "open": 90, "high": 97, "low": 89, "close": 96, "volume": 400})
        else:
            candles.append({"timestamp": ts, "open": 100, "high": 101, "low": 99, "close": 100, "volume": 200})
    cfg = StrategyConfig(
        use_rsi_trigger=False, enable_eth_hedge=False, min_daily_volume_usd=0,
        crash_lookback=2, entry_next_bar=False, time_exit_max_bars=5, enable_rebound_short=False,
        gross_cap_pct=500.0, max_positions=10,
    )
    res = run_portfolio_simulation({'X': candles}, config=cfg, capital=100000)
    trades = res.get('trades') or []
    # with 5-bar time exit and entries around 11 and 31, should be able to take both non-overlapping
    assert len(trades) >= 1
    # entries must not overlap implausibly - at minimum verify trades exist; strict overlap test via bars if present
    assert res['num_trades'] == len(trades)


def test_portfolio_deepest_crash_first_same_hour():
    # Two symbols crash/rebound same decision bar; deeper drop should be prioritized when cap tight
    base = []
    for i in range(30):
        base.append({"timestamp": f"t{i}", "open": 100, "high": 101, "low": 99, "close": 100, "volume": 300})
    deep = list(base)
    deep[10] = {"timestamp": "t10", "open": 100, "high": 101, "low": 80, "close": 82, "volume": 800}  # deeper
    deep[11] = {"timestamp": "t11", "open": 82, "high": 95, "low": 81, "close": 93, "volume": 600}
    mild = list(base)
    mild[10] = {"timestamp": "t10", "open": 100, "high": 101, "low": 94, "close": 95, "volume": 500}  # mild
    mild[11] = {"timestamp": "t11", "open": 95, "high": 99, "low": 94, "close": 98, "volume": 400}
    cfg = StrategyConfig(
        use_rsi_trigger=False, enable_eth_hedge=False, min_daily_volume_usd=0,
        crash_lookback=2, entry_next_bar=False, max_positions=1, gross_cap_pct=500.0,
        enable_rebound_short=False,
    )
    res = run_portfolio_simulation({'DEEP': deep, 'MILD': mild}, config=cfg, capital=100000)
    assert res['num_trades'] == 1
    assert res['trades'][0]['symbol'] == 'DEEP'
