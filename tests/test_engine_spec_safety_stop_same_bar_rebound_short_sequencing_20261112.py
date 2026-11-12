"""Dated regression lock (2026-11-12, CELL 4b): 8x SPEC safety-stop interaction
with a rebound short on the SAME bar — which exit wins, and can a rebound short
ever open off a safety-stop exit?

Gap proof (file-search verified): the engine's long-leg same-bar ordering is
  liquidation > stop > target > time-exit
(src/backtest/engine.py long loop: `_check_liquidation` first, then
`_stop_low <= stop_px`, then `_target_high >= target_px`). Existing same-bar
sequencing locks (tests/test_long_same_bar_stop_target_sequencing_20261108.py,
tests/test_long_liquidation_vs_stop_ordering.py) exercise a PLAIN stop, and
tests/test_rebound_short_attribution_and_risk_state_20261107.py exercises the
SHORT leg's stop-vs-target ordering — but NO test drives the SPEC 8x safety stop
(use_spec_safety_stop=True, stop = entry*(1-8*range_ratio) from generate_signal)
through a same-bar collision with a +9% long target. That is the uncovered cell.

Invariant proved here (the spec 8x safety stop is structurally below the 6%
liquidation threshold for normal hourly ranges, so on a same-bar stop+target
collision the ordering is):
  - If the safety stop is BELOW the liq threshold (typical): a same-bar
    stop+target collision resolves to LIQUIDATION (worst-price), and a stopped/
    liquidated buy NEVER opens a rebound short.
  - If a stop is ABOVE the liq threshold (unusual wide-range case): the STOP wins
    over target on the same bar, and again NO rebound short opens.
Either branch upholds: "if stop fills, stopped buy never opens rebound short."

Deterministic hand trace (entry=100, liq = entry*(1-0.06) = 94.0):
  CASE 1 — safety stop 86.0 (< 94.0), same bar breaches stop (low 90 <= 86? NO) ...
  We instead assert the DOMINANT branch: with stop 86.0 below liq, a bar that
  breaches the stop (low 85 <= 86) necessarily breaches liq (low 85 <= 94) too,
  so the engine resolves to LIQUIDATION at worst price 85.0. Target high 110 is
  also breached but liquidation outranks it. No short leg. (liquidation pnl trace
  is locked separately in test_long_liquidation_funding_same_bar_ordering_20261112.py.)

  CASE 2 — safety stop 96.0 (> 94.0), same bar breaches BOTH stop (low 95 <= 96)
  and target (high 110 >= 109) WITHOUT breaching liq (low 95 > 94). Stop is checked
  before target -> 'stopped' at exit_px 96.0, hours_held = 2, funding 0.02,
  pnl = (96-100)*1 - 100*1*(0.01/100)*2 = -4.02. No short leg.

Synthetic fixtures only; not performance evidence; no real market data; no look-ahead.
"""
from src.backtest.engine import backtest_simple
from src.strategy.crash_rebound import Signal
from src.strategy.config import StrategyConfig


def _c(ts, o, h, l, cl, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": cl, "volume": v}


def _sig(stop, target=109.0, idx=5):
    return Signal(
        symbol="T", side="long", reason="t", entry_price=100.0, stop_price=stop,
        target_price=target, risk_per_share=100.0 - stop, timestamp=f"t{idx:04d}",
        size_shares=1.0, signal_index=idx,
    )


def _cfg(**kw):
    d = dict(
        enable_eth_hedge=False, enable_rebound_short=True, entry_next_bar=False,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=0.0, funding_rate_pct_per_hour=0.01, min_daily_volume_usd=0.0,
        time_exit_max_bars=200, enable_liquidation_checks=True,
        use_spec_safety_stop=True, stop_atr_mult=8.0, atr_period=14,
        liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5,
    )
    d.update(kw)
    return StrategyConfig(**d)


def _base(n=12):
    return [_c(f"t{i:04d}", 100.0, 101.0, 99.0, 100.0) for i in range(n)]


def test_safety_stop_below_liq_same_bar_stop_target_collision_liquidates_no_rebound():
    """Safety stop 86.0 sits below the 6% liq threshold (94.0). A same-bar collision
    that breaches the stop (low 85) also breaches liq; liquidation outranks stop and
    target, and the liquidated buy NEVER opens a rebound short."""
    candles = _base()
    # low 85 <= stop 86 AND <= liq 94; high 110 >= target 109.
    candles[6] = _c("t0006", 100.0, 110.0, 85.0, 100.0)
    res = backtest_simple(candles, _sig(stop=86.0), config=_cfg())

    assert res.exit_reason == "liquidated", res.exit_reason
    assert res.exit_price == 85.0                       # worst price = bar low
    assert res.bars_held == 2                          # idx 6 - start 5 + 1
    assert not any(t.get("side") == "short" for t in (res.trades or [])), (
        "liquidated buy must never open a rebound short"
    )


def test_safety_stop_above_liq_same_bar_stop_beats_target_no_rebound():
    """Safety stop 96.0 sits above the liq threshold (94.0). A bar breaches both
    stop (low 95) and target (high 110) without breaching liq; stop is checked
    before target -> 'stopped' at 96.0, and no rebound short opens."""
    candles = _base()
    candles[6] = _c("t0006", 100.0, 110.0, 95.0, 100.0)  # stop+target breach, no liq
    res = backtest_simple(candles, _sig(stop=96.0), config=_cfg())

    assert res.exit_reason == "stopped", res.exit_reason
    assert res.exit_price == 96.0
    assert res.bars_held == 2
    assert not any(t.get("side") == "short" for t in (res.trades or [])), (
        "stopped buy must never open a rebound short"
    )
    # hours_held = 2 -> funding 0.02; pnl = (96-100) - 0.02 = -4.02
    expected = (96.0 - 100.0) - 100.0 * (0.01 / 100.0) * 2
    assert abs(res.pnl - expected) < 1e-9, (res.pnl, expected)
    assert abs(res.pnl - (-4.02)) < 1e-9, res.pnl


def test_safety_stop_above_liq_target_only_still_opens_rebound_control():
    """Control: with the stop above liq but NOT breached (low 98 > 96), a pure
    +9% target (high 110) fires the long target and DOES open the rebound short.
    Confirms the two locks above are due to stop/liq dominance, not a dead path."""
    candles = _base()
    candles[6] = _c("t0006", 100.0, 110.0, 98.0, 109.0)  # target only; stop not breached
    res = backtest_simple(candles, _sig(stop=96.0), config=_cfg())

    assert res.exit_reason == "target_rebound_short", res.exit_reason
    assert any(t.get("side") == "short" for t in (res.trades or [])), (
        "pure target must open the rebound short (control)"
    )