"""Regression lock (2026-11-10): MISSING-CANDLE-FIELD STOP COMPARISON.

Spec-fidelity defect: `src/backtest/engine.py` long-leg stop check reads
`low = c.get('low')` and skips the stop when `low is None`, even when the bar's
`close` is decisively below the stop price. The spec says the safety stop fires
when the coin falls 8x its usual hourly range below entry; a bar whose low
field is absent but whose close is far below stop is still a stop bar — the
engine must not silently skip it and run to time exit.

This is the missing-candle-field stop comparison in the spec-compliant flow.
Synthetic fixtures (non-evidence). Hourly only.
"""

from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.backtest.engine import backtest_simple


def _cfg(**overrides):
    defaults = dict(
        entry_next_bar=False,
        use_spec_safety_stop=False,
        enable_rebound_short=False,
        enable_eth_hedge=False,
        funding_rate_pct_per_hour=0.0,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
        time_exit_max_bars=200,
    )
    defaults.update(overrides)
    return StrategyConfig(**defaults)


def _signal(entry=100.0, stop=90.0, target=109.0, shares=10.0):
    return Signal(symbol='TEST', side='long', reason='crash_then_rebound',
                  entry_price=entry, stop_price=stop, target_price=target,
                  risk_per_share=entry - stop, timestamp='t0', size_shares=shares,
                  signal_index=0)


def test_stop_fires_when_low_field_missing_but_close_below_stop():
    """Bar with low=None but close=89 < stop=90 must still trigger 'stopped'.

    Before fix the engine skipped the stop (low is None) and ran to time exit.
    """
    candles = [
        {'timestamp': 't0', 'open': 100.0, 'high': 101.0, 'low': 99.0, 'close': 100.0, 'volume': 1e6},
        {'timestamp': 't1', 'open': 100.0, 'high': 101.0, 'low': None, 'close': 89.0, 'volume': 1e6},
        {'timestamp': 't2', 'open': 100.0, 'high': 101.0, 'low': 99.0, 'close': 100.0, 'volume': 1e6},
    ]
    res = backtest_simple(candles, _signal(), config=_cfg())
    assert res.exit_reason == 'stopped', (
        f"expected 'stopped' (close 89 < stop 90 despite low=None), got {res.exit_reason}"
    )
    assert res.bars_held == 2, res.bars_held


def test_stop_fires_when_high_field_missing_on_rebound_short_stop():
    """Rebound short stop (up 40%) must fire when high=None but close is above stop.

    Long hits +9% target at bar 1 -> rebound short enters ~109. Bar 2 has
    high=None but close=160 > short_stop=152.6 -> must stop the short.
    """
    candles = [
        {'timestamp': 't0', 'open': 100.0, 'high': 100.0, 'low': 100.0, 'close': 100.0, 'volume': 1e6},
        {'timestamp': 't1', 'open': 108.0, 'high': 110.0, 'low': 107.0, 'close': 109.0, 'volume': 1e6},
        {'timestamp': 't2', 'open': 109.0, 'high': None, 'low': 108.0, 'close': 160.0, 'volume': 1e6},
        {'timestamp': 't3', 'open': 109.0, 'high': 112.0, 'low': 106.0, 'close': 109.0, 'volume': 1e6},
    ]
    cfg = _cfg(enable_rebound_short=True, rebound_short_stop_pct=40.0,
               rebound_short_target_pct=9.0, rebound_short_time_exit_bars=48)
    res = backtest_simple(candles, _signal(), config=cfg)
    short_leg = next((t for t in (res.trades or []) if t.get('side') == 'short'), None)
    assert short_leg is not None, f"expected rebound short leg, trades={res.trades}"
    assert short_leg['reason'] == 'stopped', (
        f"expected rebound short 'stopped' (close 160 > stop 152.6 despite high=None), "
        f"got {short_leg['reason']}"
    )


def test_stop_skipped_when_close_above_stop_and_low_missing():
    """Sanity: a bar with low=None but close ABOVE stop must NOT stop the trade."""
    candles = [
        {'timestamp': 't0', 'open': 100.0, 'high': 101.0, 'low': 99.0, 'close': 100.0, 'volume': 1e6},
        {'timestamp': 't1', 'open': 100.0, 'high': 101.0, 'low': None, 'close': 95.0, 'volume': 1e6},
        {'timestamp': 't2', 'open': 100.0, 'high': 101.0, 'low': 99.0, 'close': 100.0, 'volume': 1e6},
    ]
    res = backtest_simple(candles, _signal(stop=90.0), config=_cfg())
    assert res.exit_reason != 'stopped', (
        f"close 95 > stop 90 should not stop, got {res.exit_reason}"
    )