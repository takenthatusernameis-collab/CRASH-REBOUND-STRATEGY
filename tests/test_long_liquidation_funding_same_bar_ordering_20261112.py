"""Dated regression lock (2026-11-12, CELL 4d): LONG liquidation vs FUNDING
same-bar ordering with concrete traced values.

Gap proof (file-search verified): the long-leg liquidation path in
src/backtest/engine.py (~lines 316-352) computes
`hours_held_liq = idx - start_idx + 1` and subtracts
`_apply_funding_pnl(entry_px*shares, hours_held_liq, rate, side='long')` in the
SAME liquidation branch that applies the liquidation penalty. Existing liq tests
assert the penalty (e.g. tests/test_long_liquidation_vs_stop_ordering.py) but do
NOT assert the funding delta on the liquidation branch, nor the deterministic
boundary that funding is 0 on the entry bar (idx == start_idx) and accrues
per-held-hour thereafter. This lock proves the ordering: on the liquidation bar
funding is charged for every held hour INCLUDING the liquidation hour, at the
worst (liq) price notional basis (entry_px*shares), with no double-count.

Deterministic hand trace (engine config: maint 5% + buffer 1% = 6% => long liq
threshold = entry*(1-0.06)):
  ENTRY_PX = 100.0, SHARES = 1.0, RATE = 0.01 %/h, penalty = 0.5% of notional.
  Liq threshold = 100.0 * (1 - 0.06) = 94.0.  (engine _check_liquidation)

  CASE A — liquidation at the ENTRY bar (idx == start_idx => hours_held == 1):
    entry bar low = 90.0 (<= 94.0).  liq_px = 90.0 (worst price = bar low).
    exit_px = 90.0 (slippage/commission/min = 0).
    long_funding = 100.0 * (0.01/100) * 1 = 0.01  -> pnl -= 0.01.
    penalty = 0.5/100 * (100.0*1.0) = 0.5.
    pnl = (90.0 - 100.0)*1.0 - 0.5 - 0.01 = -10.51.
    exit_reason = 'liquidated', exit_price = 90.0, bars_held = 1.

  CASE B — liquidation LATER (idx = start_idx + 1 => hours_held == 2):
    entry bar low = 95.0 (above 94.0 => no liq).  next bar low = 90.0 (<=94).
    hours_held_liq = idx - start_idx + 1 = 2.
    long_funding = 100.0 * 0.0001 * 2 = 0.02.
    penalty = 0.5.  pnl = (90-100)*1 - 0.5 - 0.02 = -10.52.
    Difference vs CASE A is EXACTLY one extra hour of funding = 0.01.

Synthetic fixtures only; not performance evidence; no real market data; no look-ahead.
"""
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal

ENTRY_PX = 100.0
SHARES = 1.0
RATE = 0.01          # 0.01% per hour funding
PENALTY_PCT = 0.5    # liquidation penalty % of notional
SIGNAL_IDX = 5


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _sig():
    return Signal(
        symbol="TEST", side="long", reason="t",
        entry_price=ENTRY_PX, stop_price=ENTRY_PX * 0.90,   # 90.0: BELOW liq threshold 94.0 so liquidation wins over stop
        target_price=ENTRY_PX * 1.09,                       # 109.0
        risk_per_share=1.0, timestamp="2025-01-01T05:00:00", size_shares=SHARES,
        signal_index=SIGNAL_IDX,
    )


def _cfg(**kw):
    d = dict(
        enable_eth_hedge=False, enable_rebound_short=False, entry_next_bar=False,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=0.0, funding_rate_pct_per_hour=RATE, min_daily_volume_usd=0.0,
        time_exit_max_bars=200, enable_liquidation_checks=True,
        liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=PENALTY_PCT,
    )
    d.update(kw)
    return StrategyConfig(**d)


def test_liquidation_funding_same_bar_ordering_entry_bar_charges_one_hour():
    """Liq on the ENTRY bar (idx == start_idx): exactly ONE hour of funding is
    charged alongside the penalty, at the worst (liq) price. Deterministic."""
    candles = [_c(f"2025-01-01T{i % 24:02d}:00:00", 100.2, 101.5, 99.0, 100.2) for i in range(30)]
    candles[SIGNAL_IDX] = _c("2025-01-01T05:00:00", 100.0, 101.0, 90.0, 95.0)  # low 90 <= 94.0
    res = backtest_simple(candles, _sig(), config=_cfg())

    assert res.exit_reason == "liquidated"
    assert res.exit_price == 90.0                 # worst price = bar low
    assert res.bars_held == 1                      # idx == start_idx -> 1 bar

    # pnl = (90-100)*1 - penalty(0.5) - funding(0.01) = -10.51
    expected = (90.0 - 100.0) * SHARES
    expected -= PENALTY_PCT / 100.0 * (ENTRY_PX * SHARES)
    expected -= ENTRY_PX * SHARES * (RATE / 100.0) * 1
    assert abs(res.pnl - expected) < 1e-9, (res.pnl, expected)
    assert abs(res.pnl - (-10.51)) < 1e-9, res.pnl


def test_liquidation_funding_accrues_per_held_hour_not_entry_bar_only():
    """Liq LATER (idx = start_idx+1 => hours_held=2) charges EXACTLY one more hour
    of funding than the entry-bar liquidation: delta == 0.01, proving per-hour
    accrual and the same-bar (penalty+funding) ordering is not entry-bar-only."""
    candles = [_c(f"2025-01-01T{i % 24:02d}:00:00", 100.2, 101.5, 99.0, 100.2) for i in range(30)]
    candles[SIGNAL_IDX] = _c("2025-01-01T05:00:00", 100.0, 101.0, 95.0, 100.0)   # low 95 > 94.0: no liq
    candles[SIGNAL_IDX + 1] = _c("2025-01-01T06:00:00", 100.0, 101.0, 90.0, 95.0)  # low 90 <= 94.0: liq
    res = backtest_simple(candles, _sig(), config=_cfg())

    assert res.exit_reason == "liquidated"
    assert res.exit_price == 90.0
    assert res.bars_held == 2                      # idx == start_idx+1

    expected = (90.0 - 100.0) * SHARES
    expected -= PENALTY_PCT / 100.0 * (ENTRY_PX * SHARES)
    expected -= ENTRY_PX * SHARES * (RATE / 100.0) * 2
    assert abs(res.pnl - expected) < 1e-9, (res.pnl, expected)
    assert abs(res.pnl - (-10.52)) < 1e-9, res.pnl


def test_liquidation_vs_funding_delta_is_exactly_one_hour():
    """Cross-case invariant: funding on the liquidation branch is linear in
    hours_held, so a liq one bar later must differ by exactly one hour of funding
    (0.01) and nothing else (same worst price, same penalty)."""
    base = [_c(f"2025-01-01T{i % 24:02d}:00:00", 100.2, 101.5, 99.0, 100.2) for i in range(30)]

    a = list(base)
    a[SIGNAL_IDX] = _c("2025-01-01T05:00:00", 100.0, 101.0, 90.0, 95.0)
    res_a = backtest_simple(a, _sig(), config=_cfg())

    b = list(base)
    b[SIGNAL_IDX] = _c("2025-01-01T05:00:00", 100.0, 101.0, 95.0, 100.0)
    b[SIGNAL_IDX + 1] = _c("2025-01-01T06:00:00", 100.0, 101.0, 90.0, 95.0)
    res_b = backtest_simple(b, _sig(), config=_cfg())

    one_hour = ENTRY_PX * SHARES * (RATE / 100.0)
    assert abs((res_a.pnl - res_b.pnl) - one_hour) < 1e-9, (res_a.pnl, res_b.pnl, one_hour)