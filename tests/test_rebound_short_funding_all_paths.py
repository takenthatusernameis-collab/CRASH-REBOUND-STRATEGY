"""Deterministic regressions: rebound-short coin-leg + ETH-hedge funding on every exit path.

Spec (crash-rebound-strategy.pdf): "hourly funding on every leg". The rebound short
coin leg and its ETH hedge must both receive hourly funding on liquidation / stop /
target / time-exit / final-exit. Synthetic fixtures only; not performance evidence;
no real market data; no look-ahead.
"""
import pytest
from src.strategy.config import StrategyConfig
from src.backtest.engine import backtest_simple
from src.strategy.crash_rebound import Signal, compute_eth_hedge_size

ENTRY_PX = 100.0
SHORT_ENTRY_PX = 109.0  # long +9% target -> rebound short entry
SHARES = 1.0
RATE = 0.01  # 0.01% per hour
SIGNAL_IDX = 5
LONG_TARGET_BAR = 6
LONG_HOURS = LONG_TARGET_BAR - SIGNAL_IDX + 1  # 2


def _candle(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _stable_coin_candles(n):
    out = []
    for i in range(n):
        c = 100.0 + (0.5 if i % 2 == 0 else -0.5)
        out.append(_candle(f"2025-01-01T{i:02d}:00:00", c, c + 1.0, c - 1.0, c))
    return out


def _eth_candles(n):
    out = []
    for i in range(n):
        c = 100.0 + (0.2 if i % 3 == 0 else -0.15)
        out.append(_candle(f"2025-01-01T{i:02d}:00:00", c, c + 1.0, c - 1.0, c))
    return out


def _base_cfg(**kw):
    base = dict(
        enable_eth_hedge=True,
        enable_rebound_short=True,
        entry_next_bar=False,
        avoid_downtrend=False,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
        funding_rate_pct_per_hour=RATE,
        time_exit_max_bars=1000,
        rebound_short_target_pct=9.0,
        rebound_short_stop_pct=40.0,
        min_daily_volume_usd=0.0,
    )
    base.update(kw)
    return StrategyConfig(**base)


def _signal():
    return Signal(
        symbol="TEST", side="long", reason="t",
        entry_price=ENTRY_PX, stop_price=ENTRY_PX * 0.5, target_price=ENTRY_PX * 1.09,
        risk_per_share=1.0, timestamp="2025-01-01T05:00:00", size_shares=SHARES,
        signal_index=SIGNAL_IDX,
    )


def _run(candles, eth_candles, cfg):
    return backtest_simple(candles, _signal(), config=cfg, eth_candles=eth_candles)


def _expected_delta(candles, eth_candles, short_hours):
    """Net funding effect on total_pnl (funded - unfunded) using engine conventions.

    long coin   (long side  -> cost, subtracts)
    long hedge  (ETH short  -> benefit, adds)
    short coin  (short side -> benefit, adds)
    rebound hedge (ETH long -> cost, subtracts)
    """
    rate = RATE / 100.0
    long_coin_notional = ENTRY_PX * SHARES
    short_coin_notional = SHORT_ENTRY_PX * SHARES
    cfg = _base_cfg()
    long_hedge_val = compute_eth_hedge_size(candles[:6], eth_candles[:6], long_coin_notional, cfg)
    rebound_hedge_val = compute_eth_hedge_size(candles[:7], eth_candles[:7], short_coin_notional, cfg)
    return rate * (
        -long_coin_notional * LONG_HOURS
        + long_hedge_val * LONG_HOURS
        + short_coin_notional * short_hours
        - rebound_hedge_val * short_hours
    )


def _candles_for_path(exit_kind):
    candles = _stable_coin_candles(SIGNAL_IDX + 1)  # indices 0..5, close 100 at idx 5
    # bar 6: long hits +9% target -> rebound short enters at 109
    candles.append(_candle("2025-01-01T06:00:00", 100.0, 110.0, 99.0, 109.0))
    if exit_kind == "target":
        # bar 7: low hits short target 109*0.91 = 99.19
        candles.append(_candle("2025-01-01T07:00:00", 109.0, 110.0, 99.0, 100.0))
    elif exit_kind == "stop":
        # bar 7: high hits short stop 109*1.40 = 152.6
        candles.append(_candle("2025-01-01T07:00:00", 109.0, 160.0, 108.0, 109.0))
    elif exit_kind == "liquidation":
        # bar 7: high breaches short liq threshold 109*1.06 = 115.54
        candles.append(_candle("2025-01-01T07:00:00", 109.0, 120.0, 108.0, 109.0))
    elif exit_kind == "time_exit":
        for i in range(7, 12):
            candles.append(_candle(f"2025-01-01T{i:02d}:00:00", 109.0, 110.0, 108.0, 109.0))
    elif exit_kind == "final_exit":
        for i in range(7, 11):
            candles.append(_candle(f"2025-01-01T{i:02d}:00:00", 109.0, 110.0, 108.0, 109.0))
    else:
        raise ValueError(exit_kind)
    return candles


PATH_SHORT_HOURS = {"target": 2, "stop": 2, "liquidation": 2, "time_exit": 5, "final_exit": 5}


@pytest.mark.parametrize("exit_kind", ["target", "stop", "liquidation", "time_exit", "final_exit"])
def test_rebound_short_funding_applied_on_all_exit_paths(exit_kind):
    liq = exit_kind == "liquidation"
    # Spec-consistent: N-bar max hold = N funding hours (inclusive, same as long leg).
    reb_time = 5 if exit_kind == "time_exit" else 100
    cfg_on = _base_cfg(enable_liquidation_checks=liq,
                       rebound_short_time_exit_bars=reb_time)
    cfg_off = _base_cfg(funding_rate_pct_per_hour=0.0,
                        enable_liquidation_checks=liq,
                        rebound_short_time_exit_bars=reb_time)
    candles = _candles_for_path(exit_kind)
    eth = _eth_candles(len(candles))
    short_hours = PATH_SHORT_HOURS[exit_kind]
    expected = _expected_delta(candles, eth, short_hours)

    res_on = _run(candles, eth, cfg_on)
    res_off = _run(candles, eth, cfg_off)

    assert any(t.get("side") == "short" for t in (res_on.trades or [])), (
        f"rebound short did not trigger for {exit_kind}"
    )
    delta = (res_on.total_pnl or 0.0) - (res_off.total_pnl or 0.0)
    assert abs(delta - expected) < 1e-6, (
        f"{exit_kind}: funding delta {delta} != expected {expected}; "
        "coin+hedge funding may be missing on an exit path"
    )


def test_rebound_short_funding_scales_with_rate():
    """Funding delta scales linearly with funding_rate_pct_per_hour (target path)."""
    candles = _candles_for_path("target")
    eth = _eth_candles(len(candles))

    def run(rate):
        cfg = _base_cfg(funding_rate_pct_per_hour=rate)
        return _run(candles, eth, cfg).total_pnl or 0.0

    d1 = run(0.01) - run(0.0)
    d2 = run(0.02) - run(0.0)
    assert abs(d2 - 2 * d1) < 1e-6, "funding delta should scale linearly with rate"
    assert d1 != 0.0, "funding must have a nonzero effect"
