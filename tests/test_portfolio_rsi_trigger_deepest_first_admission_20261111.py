"""Regression lock (2026-11-11): RSI-trigger deepest-first admission/ordering in
the portfolio/gated path.

Spec (crash-rebound-strategy.pdf / strategy_spec): the RSI(21)<20 crash is the
primary trigger and, when multiple symbols fire at the same decision bar, the
deepest crash is admitted first. In the RSI-trigger path severity is the RSI
value itself (lower RSI = deeper crash). This lock proves portfolio admission
orders RSI-triggered same-bar candidates by RSI severity (deepest/lowest RSI
first) with no look-ahead and correct next-bar-open execution.

Deterministic synthetic fixtures only; not market evidence.
"""
from __future__ import annotations

from scripts.run_portfolio import run_portfolio_simulation
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import _rsi


def _bar(i, o, c, v=10_000_000.0):
    hi = max(o, c) * 1.001
    lo = min(o, c) * 0.999
    return {
        "timestamp": f"2026-01-01T{i:02d}:00:00Z",
        "open": o,
        "high": hi,
        "low": lo,
        "close": c,
        "volume": v,
    }


def _make_rsi_series(step: float, n: int = 60):
    """Sustained downtrend (step < 1) drives RSI(21) below 20; final bar is a
    bullish rebound confirmation so detect_crash_rsi + confirm_rebound both pass
    on the decision bar (last bar). History-only, no look-ahead."""
    candles = []
    p = 100.0
    for i in range(n):
        c = p * step
        candles.append(_bar(i, p, c))
        p = c
    candles.append(_bar(n, p, p * 1.05))  # rebound confirmation at decision bar
    return candles


def _cfg(**kw):
    d = dict(
        use_rsi_trigger=True,
        rsi_period=21,
        rsi_threshold=20.0,
        avoid_downtrend=True,  # must NOT nullify RSI trigger (RSI is downtrend signal)
        regime_min_price=0.0,
        min_daily_volume_usd=0.0,
        enable_eth_hedge=False,
        enable_rebound_short=False,
        enable_volume_based_sizing=False,
        gross_cap_pct=500.0,
        max_positions=1,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
    )
    d.update(kw)
    return StrategyConfig(**d)


def test_portfolio_rsi_trigger_deepest_crash_first_same_decision_bar_max_positions():
    """Two RSI-triggered symbols fire on the same decision bar; max_positions=1
    admits only the deeper crash (lower RSI). Severity is (RSI, 0.0) so lower
    RSI sorts first.
    """
    deep = _make_rsi_series(0.97)  # deeper sustained sell-off
    mild = _make_rsi_series(0.99)  # milder sell-off, still RSI<20
    deep_rsi = _rsi(deep, 21)
    mild_rsi = _rsi(mild, 21)
    assert deep_rsi is not None and mild_rsi is not None
    assert deep_rsi < 20.0 and mild_rsi < 20.0
    assert deep_rsi < mild_rsi, (deep_rsi, mild_rsi)  # traced: ~4.468 < ~17.329

    cfg = _cfg(entry_next_bar=False)
    res = run_portfolio_simulation({"DEEP": deep, "MILD": mild}, config=cfg, capital=100000.0)

    assert res["num_trades"] == 1
    t = res["trades"][0]
    assert t["symbol"] == "DEEP", (t["symbol"], deep_rsi, mild_rsi)
    # Decision bar is the last bar of the constructed series (index 60).
    assert t["entry_timestamp"] == deep[-1]["timestamp"]
    assert abs(float(t["entry_price"]) - float(deep[-1]["close"])) < 1e-12
    assert res["final_open_positions"] == 0
    assert abs(float(res["final_gross_exposure"])) < 1e-12


def test_portfolio_rsi_trigger_deepest_crash_first_entry_next_bar_open():
    """Same RSI-severity ordering holds with entry_next_bar=True: admission is
    decided on the decision bar (history-only RSI) and execution fills at the
    next bar open with no look-ahead leakage."""
    deep = _make_rsi_series(0.97)
    mild = _make_rsi_series(0.99)
    deep_rsi = _rsi(deep, 21)
    mild_rsi = _rsi(mild, 21)
    assert deep_rsi < mild_rsi < 20.0

    # Append one extra bar so entry_next_bar can execute after the decision bar.
    for series in (deep, mild):
        last = series[-1]["close"]
        series.append(_bar(len(series), last * 1.01, last * 1.005))

    cfg = _cfg(entry_next_bar=True, time_exit_max_bars=10)
    res = run_portfolio_simulation({"DEEP": deep, "MILD": mild}, config=cfg, capital=100000.0)

    assert res["num_trades"] == 1
    t = res["trades"][0]
    assert t["symbol"] == "DEEP", (t["symbol"], deep_rsi, mild_rsi)
    # Entry executes at next bar open after decision bar (index 60 -> fills at 61).
    assert t["entry_timestamp"] == deep[61]["timestamp"]
    assert abs(float(t["entry_price"]) - float(deep[61]["open"])) < 1e-12
    assert res["final_open_positions"] == 0
    assert abs(float(res["final_gross_exposure"])) < 1e-12
