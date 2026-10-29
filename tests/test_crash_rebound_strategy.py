from src.strategy.crash_rebound import detect_crash, confirm_rebound, generate_signal
from src.data.loader import make_fixture_crash_rebound
from src.backtest.engine import backtest_simple


def test_detect_crash_on_fixture():
    candles = make_fixture_crash_rebound()
    assert detect_crash(candles) is True


def test_confirm_rebound_on_fixture():
    candles = make_fixture_crash_rebound()
    assert confirm_rebound(candles) is True


def test_generate_signal_on_fixture():
    candles = make_fixture_crash_rebound()
    sig = generate_signal(candles, symbol='SPY')
    assert sig is not None
    assert sig.side == 'long'
    assert sig.entry_price > sig.stop_price
    assert sig.target_price > sig.entry_price


def test_backtest_hits_target_or_exits():
    candles = make_fixture_crash_rebound()
    sig = generate_signal(candles)
    res = backtest_simple(candles, sig)
    assert res.exit_reason in ('target', 'stopped', 'time_exit')
    assert isinstance(res.pnl, float)
    assert isinstance(res.r_multiple, float)
