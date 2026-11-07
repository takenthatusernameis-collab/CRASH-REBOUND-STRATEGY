"""Deterministic spec-fidelity regressions (2026-11-07):

1. Spec invariant (strategy_spec.md:31): "If stop fills, stopped buy never opens
   rebound short." With rebound_short enabled, a long stopped on its safety stop
   must never open a rebound short - even when the target is also breached on the
   same bar (liquidation checked first, then stop, then target).
2. Rebound-short coin-leg funding applied on the stop path, isolated from the ETH
   hedge (enable_eth_hedge=False, eth_candles=None): the short side receives the
   hourly funding benefit.

Spec: "hourly funding on every leg"; hourly liquidation at worst price; no look-ahead.
Synthetic fixtures only; not performance evidence; no real market data; no look-ahead.
"""
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal

ENTRY_PX = 100.0
SHORT_ENTRY_PX = 109.0  # long +9% target -> rebound short entry
SHARES = 1.0
RATE = 0.01  # 0.01% per hour
SIGNAL_IDX = 5
# Liquidation threshold: maint 5% + buffer 1% => 6% against long => 94.0.


def _candle(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _signal():
    return Signal(
        symbol="TEST", side="long", reason="t",
        entry_price=ENTRY_PX, stop_price=ENTRY_PX * 0.95,  # 95.0
        target_price=ENTRY_PX * 1.09,  # 109.0
        risk_per_share=1.0, timestamp="2025-01-01T05:00:00", size_shares=SHARES,
        signal_index=SIGNAL_IDX,
    )


def _base(**kw):
    d = dict(
        enable_eth_hedge=False, enable_rebound_short=True, entry_next_bar=False,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=0.0, funding_rate_pct_per_hour=RATE, min_daily_volume_usd=0.0,
        time_exit_max_bars=1000, rebound_short_target_pct=9.0,
        rebound_short_stop_pct=40.0, rebound_short_time_exit_bars=100,
        enable_liquidation_checks=True,
        liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0,
    )
    d.update(kw)
    return StrategyConfig(**d)


def _run(candles, cfg, eth=None):
    return backtest_simple(candles, _signal(), config=cfg, eth_candles=eth)


def test_stopped_buy_never_opens_rebound_short_same_bar_target_breached():
    """Bar 6 breaches both stop (low 94.8 <= 95) and target (high 110 >= 109)
    but stays above the liquidation threshold (low 94.8 > 94). Stop is checked
    before target, so the buy stops and NO rebound short is opened."""
    candles = [_candle(f"2025-01-01T{i:02d}:00:00", 100.0, 101.0, 99.0, 100.0) for i in range(6)]
    candles.append(_candle("2025-01-01T06:00:00", 100.0, 110.0, 94.8, 100.0))
    res = _run(candles, _base(enable_rebound_short=True))
    assert res.exit_reason == "stopped", res.exit_reason
    assert not any(t.get("side") == "short" for t in (res.trades or [])), (
        "stopped buy must not open a rebound short"
    )


def test_rebound_short_stop_coin_funding_benefit_isolated_from_hedge():
    """Long target hit at bar 6 (rebound short enters at 109), short stop hit
    at bar 7 (high 160 >= 152.6). Liquidation checks disabled so the short stop
    path (wide 40% stop) is reachable - otherwise the +6% liquidation threshold
    fires first. No ETH hedge. Short receives funding benefit; long coin pays.
    Net delta = short_benefit + long_cost."""
    candles = [_candle(f"2025-01-01T{i:02d}:00:00", 100.0, 101.0, 99.0, 100.0) for i in range(6)]
    candles.append(_candle("2025-01-01T06:00:00", 100.0, 110.0, 99.0, 109.0))  # long target
    candles.append(_candle("2025-01-01T07:00:00", 109.0, 160.0, 108.0, 109.0))  # short stop
    on = _run(candles, _base(funding_rate_pct_per_hour=RATE,
                             enable_liquidation_checks=False), eth=None)
    off = _run(candles, _base(funding_rate_pct_per_hour=0.0,
                              enable_liquidation_checks=False), eth=None)
    short_trades = [t for t in (on.trades or []) if t.get("side") == "short"]
    assert short_trades and short_trades[0]["reason"] == "stopped"
    # long held bar 5->6 (2h) pays; short held bar 6->7 (2h) receives benefit.
    long_cost = -ENTRY_PX * SHARES * 2 * (RATE / 100.0)
    short_benefit = SHORT_ENTRY_PX * SHARES * 2 * (RATE / 100.0)
    expected = long_cost + short_benefit
    delta = (on.total_pnl or 0.0) - (off.total_pnl or 0.0)
    assert abs(delta - expected) < 1e-9, (delta, expected)
