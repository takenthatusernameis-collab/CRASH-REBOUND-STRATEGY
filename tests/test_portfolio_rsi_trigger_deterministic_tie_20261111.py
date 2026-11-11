"""Regression lock (2026-11-11): RSI-trigger deterministic tie handling
when multiple candidates have identical RSI values.

Covers uncovered #3 edge case: 2+ candidates with exactly equal RSI on the
same decision bar. Spec: deterministic tie-breaking (e.g., by symbol name)
so admission order is reproducible. Deterministic synthetic fixtures only.
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


def _make_identical_rsi_series(volume: float, n: int = 60):
    """Create series with identical price action -> identical RSI."""
    candles = []
    p = 100.0
    for i in range(n):
        c = p * 0.98  # Same step for all
        candles.append(_bar(i, p, c, volume))
        p = c
    candles.append(_bar(n, p, p * 1.05, volume))
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
        max_positions=4,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
        entry_next_bar=False,
        target_pct=200.0,
        rebound_short_target_pct=9.0,
        rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=5,
        time_exit_max_bars=5,
    )
    d.update(kw)
    return StrategyConfig(**d)


def test_portfolio_rsi_trigger_deterministic_tie_same_rsi():
    """3 candidates with IDENTICAL price series -> IDENTICAL RSI.
    Same volume -> same desired notional. Cap=120000, equal_share=30000.
    Tie-break must be deterministic (symbol name sort)."""
    A = _make_identical_rsi_series(5_000_000)
    B = _make_identical_rsi_series(5_000_000)
    C = _make_identical_rsi_series(5_000_000)
    rsis = [_rsi(x, 21) for x in (A, B, C)]
    assert all(r is not None and r < 20.0 for r in rsis), rsis
    assert rsis[0] == rsis[1] == rsis[2], rsis  # identical

    cfg = _cfg()
    res = run_portfolio_simulation({"A": A, "B": B, "C": C}, config=cfg, capital=100000.0)

    assert res["num_trades"] == 3
    symbols = [t["symbol"] for t in res["trades"]]
    # Deterministic tie-break: symbol name alphabetical
    assert symbols == ["A", "B", "C"], (symbols, rsis)

    cap = 100000.0 * 120.0 / 100.0
    equal_share = cap / 3.0  # 40000
    decision_ts = A[-1]["timestamp"]
    for t, series in zip(res["trades"], (A, B, C)):
        assert t["entry_timestamp"] == decision_ts
        assert abs(float(t["entry_price"]) - float(series[-1]["close"])) < 1e-12
        notional = float(t["shares"]) * float(t["entry_price"])
        assert abs(notional - equal_share) < 1e-6, (t["symbol"], notional, equal_share)
        assert t["exit_reason"] == "time_exit"
    assert res["final_open_positions"] == 0
    assert abs(float(res["final_gross_exposure"])) < 1e-12


def test_portfolio_rsi_trigger_deterministic_tie_maxpos2():
    """Same identical RSI, but max_positions=2. Only 2 admitted (A, B by alpha)."""
    A = _make_identical_rsi_series(5_000_000)
    B = _make_identical_rsi_series(5_000_000)
    C = _make_identical_rsi_series(5_000_000)
    rsis = [_rsi(x, 21) for x in (A, B, C)]
    assert rsis[0] == rsis[1] == rsis[2]

    cfg = _cfg(max_positions=2)
    res = run_portfolio_simulation({"A": A, "B": B, "C": C}, config=cfg, capital=100000.0)

    assert res["num_trades"] == 2
    symbols = [t["symbol"] for t in res["trades"]]
    # Truncate to max_positions=2 with alphabetical tie-break
    assert symbols == ["A", "B"], symbols

    cap = 100000.0 * 120.0 / 100.0
    equal_share = cap / 2.0  # 60000
    decision_ts = A[-1]["timestamp"]
    for t, series in zip(res["trades"], (A, B)):
        assert t["entry_timestamp"] == decision_ts
        notional = float(t["shares"]) * float(t["entry_price"])
        assert abs(notional - equal_share) < 1e-6, (t["symbol"], notional, equal_share)
    assert res["final_open_positions"] == 0
    assert abs(float(res["final_gross_exposure"])) < 1e-12


def test_portfolio_rsi_trigger_deterministic_tie_entry_next_bar():
    """Identical RSI tie-break holds with entry_next_bar=True."""
    A = _make_identical_rsi_series(5_000_000)
    B = _make_identical_rsi_series(5_000_000)
    C = _make_identical_rsi_series(5_000_000)
    for series in (A, B, C):
        last = series[-1]["close"]
        series.append(_bar(len(series), last * 1.01, last * 1.005, series[-1]["volume"]))
    rsis = [_rsi(x, 21) for x in (A, B, C)]
    assert rsis[0] == rsis[1] == rsis[2]

    cfg = _cfg(entry_next_bar=True)
    res = run_portfolio_simulation({"A": A, "B": B, "C": C}, config=cfg, capital=100000.0)

    assert res["num_trades"] == 3
    assert [t["symbol"] for t in res["trades"]] == ["A", "B", "C"]
    cap = 100000.0 * 120.0 / 100.0
    equal_share = cap / 3.0
    exec_ts = A[61]["timestamp"]
    for t, series in zip(res["trades"], (A, B, C)):
        assert t["entry_timestamp"] == exec_ts
        assert abs(float(t["entry_price"]) - float(series[61]["open"])) < 1e-12
        notional = float(t["shares"]) * float(t["entry_price"])
        assert abs(notional - equal_share) < 1e-6
    assert res["final_open_positions"] == 0
    assert abs(float(res["final_gross_exposure"])) < 1e-12