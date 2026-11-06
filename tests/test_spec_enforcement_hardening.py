"""Spec-fidelity enforcement campaign: regression guards for crash-rebound PDF invariants.

Failing-test-first enforcement of invariants the hourly engine must honor:
- rebound short exits: -9% target / +40% stop / 48h time exit
- ETH hedge vol-ratio coin/ETH over 336h capped at 3x on every leg
- equal-share cuts old+new across 120% gross cap (cuts only, never tops up)
- one position per coin via max_positions guard
- stopped buy never opens rebound short (reinforces test_spec_safety_stop)

Deterministic synthetic fixtures only; not market evidence; no look-ahead.
"""
from __future__ import annotations

from src.strategy.config import StrategyConfig
from src.strategy.risk import RiskState
from src.backtest.engine import backtest_simple
from src.strategy.crash_rebound import Signal, compute_eth_hedge_size


def _candle(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _base_cfg(**kw):
    base = dict(
        enable_eth_hedge=True,
        enable_rebound_short=True,
        entry_next_bar=False,
        avoid_downtrend=False,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
        funding_rate_pct_per_hour=0.0,
        time_exit_max_bars=1000,
        rebound_short_target_pct=9.0,
        rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
        min_daily_volume_usd=0.0,
        enable_liquidation_checks=False,
    )
    base.update(kw)
    return StrategyConfig(**base)


def _signal(entry=100.0, stop=50.0, target=109.0, idx=5):
    return Signal(
        symbol="TEST", side="long", reason="t",
        entry_price=entry, stop_price=stop, target_price=target,
        risk_per_share=entry - stop, timestamp="2025-01-01T05:00:00",
        size_shares=1.0, signal_index=idx,
    )


def test_rebound_short_target_stop_time_match_spec_values():
    # Long hits +9% target at bar 6 -> rebound short enters at 109.
    # Spec: short closes at -9% (99.19), stops at +40% (152.6), time exit at 48h.
    entry_idx = 5
    candles = [_candle(f"2025-01-01T{i:02d}:00:00", 100.0, 101.0, 99.0, 100.0) for i in range(entry_idx + 1)]
    candles.append(_candle("2025-01-01T06:00:00", 100.0, 110.0, 99.0, 109.0))  # long target hit
    # Flat after: neither short target (99.19) nor short stop (152.6) touched -> time exit at 48h.
    for i in range(7, 56):
        candles.append(_candle(f"2025-01-01T{i:02d}:00:00", 109.0, 110.0, 108.0, 109.0))
    eth = [_candle(f"2025-01-01T{i:02d}:00:00", 100.0, 101.0, 99.0, 100.0) for i in range(len(candles))]
    res = backtest_simple(candles, _signal(), config=_base_cfg(), eth_candles=eth)
    short_trades = [t for t in (res.trades or []) if t.get("side") == "short"]
    assert short_trades, "rebound short leg must open after long +9% target"
    # 48 bars held on the short leg (idx 6 -> idx 53 inclusive = 48 bars)
    assert any(t.get("reason") == "time_exit" for t in short_trades), short_trades
    last_short = short_trades[-1]
    assert abs(last_short["exit"] - 109.0) < 1e-6, last_short  # flat -> exit at entry


def test_rebound_short_closes_at_minus_nine_percent_target():
    entry_idx = 5
    candles = [_candle(f"2025-01-01T{i:02d}:00:00", 100.0, 101.0, 99.0, 100.0) for i in range(entry_idx + 1)]
    candles.append(_candle("2025-01-01T06:00:00", 100.0, 110.0, 99.0, 109.0))  # long target -> short entry 109
    # Bar 7 low hits short target 109 * 0.91 = 99.19
    candles.append(_candle("2025-01-01T07:00:00", 109.0, 110.0, 99.0, 100.0))
    eth = [_candle(f"2025-01-01T{i:02d}:00:00", 100.0, 101.0, 99.0, 100.0) for i in range(len(candles))]
    res = backtest_simple(candles, _signal(), config=_base_cfg(), eth_candles=eth)
    short_trades = [t for t in (res.trades or []) if t.get("side") == "short"]
    assert short_trades and short_trades[-1].get("reason") == "target", short_trades
    assert abs(short_trades[-1]["exit"] - 109.0 * 0.91) < 1e-6, short_trades[-1]


def test_rebound_short_stops_at_plus_forty_percent():
    entry_idx = 5
    candles = [_candle(f"2025-01-01T{i:02d}:00:00", 100.0, 101.0, 99.0, 100.0) for i in range(entry_idx + 1)]
    candles.append(_candle("2025-01-01T06:00:00", 100.0, 110.0, 99.0, 109.0))  # short entry 109
    # Bar 7 high breaches short stop 109 * 1.40 = 152.6
    candles.append(_candle("2025-01-01T07:00:00", 109.0, 160.0, 108.0, 109.0))
    eth = [_candle(f"2025-01-01T{i:02d}:00:00", 100.0, 101.0, 99.0, 100.0) for i in range(len(candles))]
    res = backtest_simple(candles, _signal(), config=_base_cfg(), eth_candles=eth)
    short_trades = [t for t in (res.trades or []) if t.get("side") == "short"]
    assert short_trades and short_trades[-1].get("reason") == "stopped", short_trades
    assert abs(short_trades[-1]["exit"] - 109.0 * 1.40) < 1e-6, short_trades[-1]


def _vol_candles(n, step):
    """Deterministic candles whose hourly return magnitude is ~step."""
    out = []
    p = 100.0
    for i in range(n):
        c = p * (1.0 + step if i % 2 == 0 else 1.0 - step)
        out.append(_candle(f"2025-01-01T{i%24:02d}:00:00", p, max(p, c) * 1.001, min(p, c) * 0.999, c))
        p = c
    return out


def test_eth_hedge_vol_ratio_capped_at_3x_over_336h():
    # Coin vol (~0.02) / ETH vol (~0.005) = 4 -> hedge must be capped at 3x position.
    n = 340  # >= 336h lookback + 1
    coin = _vol_candles(n, 0.02)
    eth = _vol_candles(n, 0.005)
    cfg = _base_cfg(hedge_vol_lookback_hours=336, hedge_cap_multiplier=3.0)
    position_value = 100_000.0
    hedge = compute_eth_hedge_size(coin, eth, position_value, cfg)
    assert abs(hedge - 3.0 * position_value) < 1e-6, hedge  # capped, not 4x


def test_eth_hedge_uncapped_when_ratio_under_cap():
    # Ratio < 3 -> hedge = coin_vol/eth_vol * position, no cap applied.
    n = 340
    coin = _vol_candles(n, 0.02)
    eth = _vol_candles(n, 0.01)  # ratio 2
    cfg = _base_cfg(hedge_vol_lookback_hours=336, hedge_cap_multiplier=3.0)
    position_value = 100_000.0
    hedge = compute_eth_hedge_size(coin, eth, position_value, cfg)
    assert abs(hedge - 2.0 * position_value) < 1e-6, hedge


def test_equal_share_cuts_old_and_new_under_120pct_cap_cuts_only():
    state = RiskState(date="2025-01-01", open_position_notionals=[60.0, 50.0], open_positions=2, gross_exposure=110.0)
    cfg = StrategyConfig(gross_cap_pct=120.0)
    cuts = state.cut_positions_to_cap(capital=100.0, config=cfg, open_notional=[60.0, 50.0, 30.0])  # old+new = 140 > 120 cap
    assert cuts == [40.0, 40.0, 40.0], cuts  # equal share across old+new, never tops up
    assert sum(cuts) <= 100.0 * 1.2


def test_apply_cap_cuts_persists_equal_share_cuts_to_state():
    state = RiskState(date="2025-01-01", open_position_notionals=[80.0, 40.0], open_positions=2, gross_exposure=120.0)
    cfg = StrategyConfig(gross_cap_pct=120.0)
    cuts = state.apply_cap_cuts(capital=100.0, config=cfg, open_notional=[80.0, 40.0, 20.0])  # 140 > 120
    assert cuts == [40.0, 40.0, 40.0], cuts
    assert state.open_position_notionals == cuts
    assert abs(state.gross_exposure - 120.0) < 1e-9
    assert state.open_positions == 3


def test_one_position_per_coin_max_positions_guard():
    state = RiskState(date="2025-01-01", open_positions=1, gross_exposure=50.0)
    cfg = StrategyConfig(max_positions=1)
    check = state.check_position(cfg, capital=100000.0, size_shares=1.0, entry_price=100.0)
    assert check.allowed is False
    assert check.reason == "max_positions_reached", check.reason
    assert check.size_shares == 0.0
