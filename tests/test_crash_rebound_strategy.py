from src.strategy.crash_rebound import detect_crash, confirm_rebound, generate_signal
from src.strategy.config import StrategyConfig, DEFAULT_CONFIG
from src.strategy.risk import DailyRiskState, size_by_risk, check_daily_loss_halt
from src.data.loader import make_fixture_crash_rebound
from src.backtest.engine import backtest_simple


def make_candles(rows):
    return rows


def test_detect_crash_custom_threshold():
    # A -1.5% drop should NOT trigger at -2.0% default, but should at -1.0%
    candles = [
        {"open": 100.0, "high": 100.0, "low": 99.0, "close": 99.0, "volume": 1000},
        {"open": 100.0, "high": 100.0, "low": 98.4, "close": 98.5, "volume": 2000},
    ]
    assert detect_crash(candles, pct_drop=-2.0) is False
    assert detect_crash(candles, pct_drop=-1.0) is True


def test_volume_confirmation_filters_low_volume_crash():
    candles = [
        {"open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0, "volume": 1000},
        {"open": 100.0, "high": 100.0, "low": 97.0, "close": 97.5, "volume": 1000},  # crash, low vol
    ]
    # Default volume_spike_mult=1.5: 1000 < 1000*1.5 → not confirmed
    assert detect_crash(candles) is False
    # With mult=0.5: 1000 >= 1000*0.5 → confirmed
    assert detect_crash(candles, volume_spike_mult=0.5) is True


def test_regime_filter_blocks_downtrend():
    config = StrategyConfig(avoid_downtrend=True, ma_fast_period=3, regime_min_price=1.0)
    # Persistent downtrend: every close below the fast MA
    candles = [
        {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0, "volume": 5000},
        {"open": 100.0, "high": 100.0, "low": 98.0, "close": 98.0, "volume": 5000},
        {"open": 98.0, "high": 99.0, "low": 96.0, "close": 97.0, "volume": 5000},
        {"open": 98.0, "high": 99.0, "low": 95.0, "close": 96.0, "volume": 5000},  # crash + rebound-like
        {"open": 96.0, "high": 99.0, "low": 95.5, "close": 97.0, "volume": 5000},
    ]
    # Regime filter should block because close (97) < MA of last 3 (97.67)
    sig = generate_signal(candles, config=config)
    assert sig is None


def test_position_size_by_risk():
    shares = size_by_risk(entry_price=100.0, stop_price=99.0, capital=100000.0, risk_pct=1.0)
    assert abs(shares - (1000.0 / 1.0)) < 1e-6
    # Zero/negative risk per share → 0 shares
    assert size_by_risk(entry_price=100.0, stop_price=100.0, capital=100000.0, risk_pct=1.0) == 0.0
    assert size_by_risk(entry_price=100.0, stop_price=101.0, capital=100000.0, risk_pct=1.0) == 0.0


def test_risk_state_daily_loss_limit_halt():
    state = DailyRiskState(date="2025-01-01", realized_pnl=-350.0, open_positions=0)
    config = StrategyConfig(max_daily_loss_pct=3.0)
    assert check_daily_loss_halt(state, config, capital=10000.0) is True  # -3.5% >= -3%
    assert check_daily_loss_halt(state, config, capital=20000.0) is False  # -1.75% < 3%


def test_risk_state_max_positions_blocked():
    state = DailyRiskState(date="2025-01-01", realized_pnl=0.0, open_positions=5)
    config = StrategyConfig(max_positions=5)
    check = state.check_position(config, capital=100000.0, size_shares=100.0)
    assert check.allowed is False
    assert check.reason == "max_positions_reached"
    assert check.size_shares == 0.0


def test_no_signal_when_no_crash():
    candles = [
        {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5, "volume": 1000},
        {"open": 100.5, "high": 101.5, "low": 100.0, "close": 101.0, "volume": 1000},
    ]
    assert detect_crash(candles) is False
    assert generate_signal(candles) is None


def test_no_signal_when_crash_but_no_rebound():
    # Crash candle followed by bearish candle (close < open)
    candles = [
        {"open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0, "volume": 1000},
        {"open": 100.0, "high": 100.1, "low": 97.0, "close": 97.5, "volume": 5000},  # crash
        {"open": 97.6, "high": 98.0, "low": 96.0, "close": 96.5, "volume": 3000},  # no rebound
    ]
    assert detect_crash(candles) is True
    assert confirm_rebound(candles) is False
    assert generate_signal(candles) is None


def test_backtest_time_exit_signal_on_last_bar():
    # Look-ahead guard: signal on last bar must not stop out on the prior crash candle.
    candles = make_fixture_crash_rebound()
    sig = generate_signal(candles)
    assert sig is not None
    res = backtest_simple(candles, sig)
    assert res.exit_reason in ('target', 'stopped', 'time_exit')
    assert isinstance(res.pnl, float)
    assert isinstance(res.r_multiple, float)
    # With signal on last bar and no future data, exit must be time_exit (no look-ahead).
    assert res.exit_reason == 'time_exit'


def test_backtest_applies_slippage_commission():
    config = StrategyConfig(slippage_pct=0.001, commission_per_share=0.01)
    candles = make_fixture_crash_rebound()
    sig = generate_signal(candles, config=config)
    assert sig is not None
    res_default = backtest_simple(candles, sig, config=DEFAULT_CONFIG)
    res_costly = backtest_simple(candles, sig, config=config)
    # Costly config should not produce higher pnl than default on same time-exit path.
    assert res_costly.pnl <= res_default.pnl + 1e-9


def test_generate_signal_uses_config_defaults():
    candles = make_fixture_crash_rebound()
    sig = generate_signal(candles)
    assert sig is not None
    assert sig.config_used is not None
    assert sig.config_used["crash_pct_drop"] == DEFAULT_CONFIG.crash_pct_drop
    assert sig.size_shares > 0
