"""Failing-tests-first: engine fill accounting must honor commission_min (per-share min).

Config/risk model commission_min and risk.apply_slippage_commission applies
max(commission_per_share, commission_min/shares). Engine's _slippage_commission_per_share
previously ignored commission_min (pass), causing fee under-accounting on small-share fills.
"""
from __future__ import annotations

import pytest

from src.backtest.engine import backtest_simple, _slippage_commission_per_share
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.strategy.risk import apply_slippage_commission


def _cfg(**kw):
    base = dict(
        slippage_pct=0.0,
        commission_per_share=0.001,
        commission_min=1.0,
        funding_rate_pct_per_hour=0.0,
        min_daily_volume_usd=0.0,
        enable_eth_hedge=False,
        enable_rebound_short=False,
        entry_next_bar=False,
        use_spec_safety_stop=False,
        time_exit_max_bars=50,
    )
    base.update(kw)
    return StrategyConfig(**base)


def test_engine_slippage_commission_helper_honors_commission_min():
    cfg = _cfg()
    px = _slippage_commission_per_share(100.0, cfg, 'buy', shares=1.0)
    expected = apply_slippage_commission(100.0, 1.0, cfg, 'buy')
    assert px == pytest.approx(expected)
    assert px == pytest.approx(101.0)
    pxs = _slippage_commission_per_share(100.0, cfg, 'sell', shares=1.0)
    expected_s = apply_slippage_commission(100.0, 1.0, cfg, 'sell')
    assert pxs == pytest.approx(expected_s)
    assert pxs == pytest.approx(99.0)


def test_engine_slippage_commission_helper_zero_shares_falls_back():
    cfg = _cfg(commission_min=1.0, commission_per_share=0.001, slippage_pct=0.0)
    px = _slippage_commission_per_share(100.0, cfg, 'buy')
    assert px == pytest.approx(100.001)


def test_engine_backtest_target_exit_respects_commission_min():
    cfg = _cfg()
    candles = [
        {'timestamp': 't0', 'open': 100, 'high': 100, 'low': 99, 'close': 100, 'volume': 1000},
        {'timestamp': 't1', 'open': 100, 'high': 100, 'low': 99, 'close': 100, 'volume': 1000},
        {'timestamp': 't2', 'open': 105, 'high': 115, 'low': 104, 'close': 110, 'volume': 1000},
    ]
    target_px = 100.0 * 1.09
    sig = Signal(
        symbol='TEST',
        side='long',
        reason='test',
        entry_price=100.0,
        stop_price=80.0,
        target_price=target_px,
        size_shares=1.0,
        risk_per_share=20.0,
        timestamp='t1',
        signal_index=1,
    )
    res = backtest_simple(candles, sig, config=cfg)
    assert res is not None
    assert res.shares == 1.0
    exp_entry = apply_slippage_commission(100.0, 1.0, cfg, 'buy')
    exp_exit = apply_slippage_commission(target_px, 1.0, cfg, 'sell')
    assert res.entry_price == pytest.approx(exp_entry)
    assert res.exit_price == pytest.approx(exp_exit)
