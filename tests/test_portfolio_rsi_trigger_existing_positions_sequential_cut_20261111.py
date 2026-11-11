"""Regression lock (2026-11-11): RSI-trigger admission with existing open
positions from prior bars (sequential/non-batch path under cap-cut).

Covers uncovered #3 edge case: existing open positions (from earlier decision
bars, also RSI-triggered) + new RSI candidates on same decision bar.
Spec: sequential admission with cap cuts (old+new), NO batch equal-share
(batch_cut_case requires zero existing positions). Equal-share cuts only
apply old+new when there are no existing positions. Deterministic synthetic
fixtures only.
"""
from __future__ import annotations

from scripts.run_portfolio import run_portfolio_simulation
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import _rsi


def _bar(i, o, c, v):
    hi = max(o, c) * 1.01
    lo = min(o, c) * 0.99
    return {
        "timestamp": f"2026-01-01T{i:02d}:00:00Z",
        "open": o,
        "high": hi,
        "low": lo,
        "close": c,
        "volume": v,
    }


def _make_early_rsi_series(step: float, volume: float, n: int = 60, crash_start: int = 20):
    """RSI series that fires EARLY (at crash_start + 21 bars) and holds long.
    Sustained downtrend drives RSI below 20 early; then flat/up so position holds."""
    candles = []
    p = 100.0
    for i in range(n + 1):  # +1 for decision bar
        if i < crash_start:
            # Pre-crash: gentle uptrend
            c = p * 1.001
        elif i < crash_start + 25:
            # Crash period: sustained sell-off
            c = p * step
        else:
            # Post-crash: flat/up so RSI recovers but position holds via time_exit
            c = p * 1.0005
        candles.append(_bar(i, p, c, volume))
        p = c
    return candles


def _make_late_rsi_series(step: float, volume: float, n: int = 60):
    """RSI series that fires LATE (at bar n) - standard."""
    candles = []
    p = 100.0
    for i in range(n):
        c = p * step
        candles.append(_bar(i, p, c, volume))
        p = c
    candles.append(_bar(n, p, p * 1.05, volume))  # rebound confirmation
    return candles


def _cfg(**kw):
    d = dict(
        use_rsi_trigger=True,
        rsi_period=21,
        rsi_threshold=20.0,
        avoid_downtrend=True,
        regime_min_price=0.0,
        min_daily_volume_usd=0.0,
        enable_eth_hedge=False,
        enable_rebound_short=True,
        enable_volume_based_sizing=True,
        gross_cap_pct=120.0,
        max_positions=3,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
        entry_next_bar=False,
        target_pct=200.0,
        rebound_short_target_pct=9.0,
        rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=30,
        time_exit_max_bars=30,
    )
    d.update(kw)
    return StrategyConfig(**d)


def test_portfolio_rsi_trigger_existing_positions_sequential_cap_cut():
    """EXISTING RSI position from earlier bar (fires ~bar 40) + 2 new RSI
    candidates firing at bar 60. Existing holds through bar 60 (time_exit 20).
    Should use sequential path (batch_cut_case=False due to existing pos).
    Total desired > cap, so sequential cap cuts apply old+new (cuts only).
    """
    # EXISTING: fires early (around bar 40), holds through bar 60
    existing = _make_early_rsi_series(0.97, 10_000_000, n=65, crash_start=15)
    existing_rsi = _rsi(existing[:45], 21)
    assert existing_rsi is not None and existing_rsi < 20.0, existing_rsi

    # Two NEW RSI-trigger candidates firing at decision bar 60
    A = _make_late_rsi_series(0.97, 5_000_000)   # deepest RSI
    B = _make_late_rsi_series(0.98, 8_000_000)   # middle RSI
    rsis = [_rsi(x, 21) for x in (A, B)]
    assert all(r is not None and r < 20.0 for r in rsis), rsis
    assert rsis == sorted(rsis), rsis  # A deepest -> B

    cfg = _cfg()
    res = run_portfolio_simulation(
        {"EXISTING": existing, "A": A, "B": B}, config=cfg, capital=100000.0
    )

    # All 3 should trade: existing + 2 new
    assert res["num_trades"] == 3, (res["num_trades"], [t["symbol"] for t in res["trades"]])
    symbols = [t["symbol"] for t in res["trades"]]
    # Existing should be first (traded earlier)
    assert symbols[0] == "EXISTING", symbols

    # The two RSI candidates should be admitted in RSI order
    rsi_symbols = [s for s in symbols if s in ("A", "B")]
    assert rsi_symbols == ["A", "B"], (rsi_symbols, rsis)

    # Final positions reconciled
    assert res["final_open_positions"] == 0
    assert abs(float(res["final_gross_exposure"])) < 1e-12


def test_portfolio_rsi_trigger_existing_positions_sequential_cap_cut_entry_next_bar():
    """Same as above but entry_next_bar=True: existing fills at next bar open
    after its decision; new RSI candidates fire at their decision bar (60),
    execute at next bar open (61). No look-ahead."""
    existing = _make_early_rsi_series(0.97, 10_000_000, n=66, crash_start=15)
    existing_rsi = _rsi(existing[:45], 21)
    assert existing_rsi is not None and existing_rsi < 20.0
    # Add execution bar for existing's entry_next_bar
    last = existing[-1]["close"]
    existing.append(_bar(len(existing), last * 1.01, last * 1.005, existing[-1]["volume"]))

    A = _make_late_rsi_series(0.97, 5_000_000)
    B = _make_late_rsi_series(0.98, 8_000_000)
    for series in (A, B):
        last = series[-1]["close"]
        series.append(_bar(len(series), last * 1.01, last * 1.005, series[-1]["volume"]))
    rsis = [_rsi(x, 21) for x in (A, B)]
    assert rsis == sorted(rsis) and all(r < 20.0 for r in rsis)

    cfg = _cfg(entry_next_bar=True)
    res = run_portfolio_simulation(
        {"EXISTING": existing, "A": A, "B": B}, config=cfg, capital=100000.0
    )

    assert res["num_trades"] == 3, (res["num_trades"], [t["symbol"] for t in res["trades"]])
    symbols = [t["symbol"] for t in res["trades"]]
    assert symbols[0] == "EXISTING"
    rsi_symbols = [s for s in symbols if s in ("A", "B")]
    assert rsi_symbols == ["A", "B"], rsi_symbols
    assert res["final_open_positions"] == 0
    assert abs(float(res["final_gross_exposure"])) < 1e-12