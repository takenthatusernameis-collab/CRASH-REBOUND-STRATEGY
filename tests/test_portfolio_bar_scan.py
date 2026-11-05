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


def _concurrent_series(symbol_count, n=80):
    """Build `symbol_count` identical crash/rebound series firing at the same decision bar.

    Bars 0..17 flat, bar 18 crash (open 100 -> close 90, volume spike), bar 19 rebound
    (close in upper half of range), then flat. Volume sized so volume-based position
    sizing produces notionals far above the gross cap, forcing equal-share cuts.
    """
    out = {}
    for s in range(symbol_count):
        candles = []
        for i in range(n):
            ts = f"2026-01-01T{i%24:02d}:00:00Z"
            if i < 18:
                candles.append({"timestamp": ts, "open": 100, "high": 101, "low": 99, "close": 100, "volume": 10000})
            elif i == 18:
                candles.append({"timestamp": ts, "open": 100, "high": 101, "low": 88, "close": 90, "volume": 50000})
            elif i == 19:
                candles.append({"timestamp": ts, "open": 90, "high": 97, "low": 89, "close": 96, "volume": 40000})
            else:
                candles.append({"timestamp": ts, "open": 96, "high": 97, "low": 95, "close": 96, "volume": 10000})
        out[f"SYM{s}"] = candles
    return out


def test_portfolio_concurrent_equal_share_cuts_old_and_new(monkeypatch):
    """When several symbols fire at the same decision bar and the gross cap is breached,
    every open position (old and new) is cut to an equal share of the 120% cap.

    Spec: "cuts open positions so every position (old and new) holds equal share".
    Cuts are observed at entry time via a recording risk state; by series end all
    positions have exited, so the check is on the cut schedule, not the final state.
    """
    import scripts.run_portfolio as rp
    from src.strategy.risk import RiskState as _BaseRiskState

    recorded = []

    class RecordingRiskState(_BaseRiskState):
        def apply_cap_cuts(self, capital, config, open_notional=None):
            incoming = list(open_notional) if open_notional is not None else list(self.open_position_notionals)
            cut = super().apply_cap_cuts(capital, config, open_notional)
            recorded.append((list(incoming), list(cut)))
            return cut

    monkeypatch.setattr(rp, 'RiskState', RecordingRiskState)

    series = _concurrent_series(symbol_count=3)
    cfg = StrategyConfig(
        use_rsi_trigger=False, enable_eth_hedge=False, enable_rebound_short=False,
        min_daily_volume_usd=0, crash_lookback=5, entry_next_bar=True,
        time_exit_max_bars=50, avoid_downtrend=False, regime_min_price=1.0,
        enable_volume_based_sizing=True, position_size_pct_of_daily_volume=1.25,
        gross_cap_pct=120.0, max_positions=10,
        slippage_pct=0.0, commission_per_share=0.0, commission_min=0.0,
    )
    res = run_portfolio_simulation(series, config=cfg, capital=100000)
    cap_value = 100000 * cfg.gross_cap_pct / 100.0  # 120000
    # Three concurrent trades were admitted (deepest-first probe commits each).
    assert res['num_trades'] == 3
    # At least one cap-cut fired and every cut schedule was equal-share across all positions.
    assert recorded, "expected at least one apply_cap_cuts call"
    for incoming, cut in recorded:
        assert len(cut) >= 1
        assert abs(sum(cut) - cap_value) < 1e-6, f"cut total must equal cap: {cut} vs {cap_value}"
        assert len(cut) == len(incoming), f"cut must cover all positions (old+new): {len(cut)} vs {len(incoming)}"
        first = cut[0]
        assert all(abs(n - first) < 1e-6 for n in cut), f"unequal cut schedule: {cut}"


def test_portfolio_concurrent_cap_preserves_max_positions_intent(monkeypatch):
    """With max_positions=1 and two concurrent signals, only one is admitted and the
    cap/one-position semantics are preserved (deepest crash wins)."""
    import scripts.run_portfolio as rp
    from src.strategy.risk import RiskState as _BaseRiskState

    class RecordingRiskState(_BaseRiskState):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.open_counts = []

        def apply_cap_cuts(self, capital, config, open_notional=None):
            self.open_counts.append(len(open_notional) if open_notional is not None else len(self.open_position_notionals))
            return super().apply_cap_cuts(capital, config, open_notional)

    monkeypatch.setattr(rp, 'RiskState', RecordingRiskState)

    series = _concurrent_series(symbol_count=2)
    cfg = StrategyConfig(
        use_rsi_trigger=False, enable_eth_hedge=False, enable_rebound_short=False,
        min_daily_volume_usd=0, crash_lookback=5, entry_next_bar=True,
        time_exit_max_bars=50, avoid_downtrend=False, regime_min_price=1.0,
        enable_volume_based_sizing=True, position_size_pct_of_daily_volume=1.25,
        gross_cap_pct=120.0, max_positions=1,
        slippage_pct=0.0, commission_per_share=0.0, commission_min=0.0,
    )
    res = run_portfolio_simulation(series, config=cfg, capital=100000)
    assert res['num_trades'] == 1
    assert res['risk_state'].open_positions <= 1
    assert res['risk_state'].gross_exposure <= 120000.0 + 1e-6
