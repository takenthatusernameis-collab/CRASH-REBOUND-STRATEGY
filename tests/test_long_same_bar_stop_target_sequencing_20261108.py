"""Regression lock (2026-11-08, 2b extension): long-leg same-bar stop-vs-target
sequencing when both levels are breached in the same hourly bar and liquidation
is not triggered.

Hourly OHLC bars cannot determine intra-bar path; the spec mandates hourly
liquidation checks at worst price but does not spell out stop-vs-target order
when both breach on the same bar without liquidation. The engine uses a
deterministic, conservative ordering: liquidation checked first, then stop
(low <= stop_px), then target (high >= target_px). This lock documents that
choice for the long coin leg (short leg has analogous locks in
test_rebound_short_attribution_and_risk_state_20261107.py).

Synthetic fixtures only; not performance evidence; no look-ahead.
"""
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal

ENTRY_PX = 100.0
SHARES = 1.0
SIGNAL_IDX = 5
STOP_PX = 90.0
TARGET_PX = 110.0


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _coin(n):
    return [_c(f"2025-01-01T{i % 24:02d}:00:00", 100.2, 101.5, 99.0, 100.2) for i in range(n)]


def _eth(n):
    return [_c(f"2025-01-01T{i % 24:02d}:00:00", 2000.0, 2005.0, 1995.0, 2000.0 + (i % 3)) for i in range(n)]


def _sig():
    return Signal(symbol="T", side="long", reason="t", entry_price=ENTRY_PX, stop_price=STOP_PX,
                  target_price=TARGET_PX, risk_per_share=ENTRY_PX - STOP_PX, timestamp="2025-01-01T05:00:00",
                  size_shares=SHARES, signal_index=SIGNAL_IDX)


def _cfg(**kw):
    d = dict(
        enable_eth_hedge=False, enable_rebound_short=False, entry_next_bar=False,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=0.0, funding_rate_pct_per_hour=0.0, min_daily_volume_usd=0.0,
        time_exit_max_bars=200, enable_liquidation_checks=False,
        liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5,
    )
    d.update(kw)
    return StrategyConfig(**d)


def test_long_same_bar_stop_and_target_both_breached_stop_first_no_liquidation():
    """Bar breaches both stop (low 89 <= 90) and target (high 111 >= 110), liquidation
    disabled. Engine checks stop before target -> deterministic conservative 'stopped'."""
    candles = _coin(30)
    candles[8] = _c("2025-01-01T08:00:00", 100.0, 111.0, 89.0, 100.0)
    res = backtest_simple(candles, _sig(), config=_cfg())
    assert res.exit_reason == "stopped"
    assert res.exit_price == STOP_PX
    assert res.bars_held == 8 - SIGNAL_IDX + 1


def test_long_same_bar_target_only_when_stop_not_breached():
    """Sanity: target breached, stop not breached -> target fires."""
    candles = _coin(30)
    candles[8] = _c("2025-01-01T08:00:00", 100.0, 111.0, 91.0, 109.0)
    res = backtest_simple(candles, _sig(), config=_cfg(enable_rebound_short=False))
    assert res.exit_reason == "target"
    assert res.exit_price == TARGET_PX


def test_long_same_bar_stop_only_when_target_not_breached():
    """Sanity: stop breached, target not breached -> stopped."""
    candles = _coin(30)
    candles[8] = _c("2025-01-01T08:00:00", 100.0, 109.0, 89.0, 91.0)
    res = backtest_simple(candles, _sig(), config=_cfg())
    assert res.exit_reason == "stopped"
    assert res.exit_price == STOP_PX


def test_long_same_bar_liquidation_precedes_stop_and_target_when_all_breach():
    """If liquidation, stop, and target thresholds are all breached on the same bar,
    liquidation (worst-price, spec-explicit) must win over stop/target ordering."""
    candles = _coin(30)
    # liq threshold = 100*(1 - 0.06) = 94.0. Low 93 breaches liq, stop (90) not needed,
    # but set stop above liq threshold? No - stop is 90 here, liq is 94; low 93 breaches liq
    # but not stop (93 > 90). To make all three "relevant": use stop=95, target=110, liq=94.
    candles[8] = _c("2025-01-01T08:00:00", 100.0, 111.0, 93.0, 93.5)
    sig = Signal(symbol="T", side="long", reason="t", entry_price=ENTRY_PX, stop_price=95.0,
                 target_price=TARGET_PX, risk_per_share=5.0, timestamp="2025-01-01T05:00:00",
                 size_shares=SHARES, signal_index=SIGNAL_IDX)
    res = backtest_simple(candles, sig, config=_cfg(enable_liquidation_checks=True))
    assert res.exit_reason == "liquidated"
    assert res.exit_price == 93.0
