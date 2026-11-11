"""Regression lock (2026-11-11): RSI-trigger deepest-first admission with
max_positions < candidates batch-cut truncation + equal-share cuts.

Covers uncovered #3 edge case: 3 RSI-trigger candidates on the same decision
bar with enable_rebound_short batch-cut path active (multiple candidates, no
existing positions), max_positions=2 < 3 candidates. Spec: truncate to
max_positions (deepest RSI first), then apply equal-share cuts across the
120% gross cap for the admitted subset only. Deterministic synthetic fixtures
only.
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


def _make_rsi_series(step: float, volume: float, n: int = 60):
    candles = []
    p = 100.0
    for i in range(n):
        c = p * step
        candles.append(_bar(i, p, c, volume))
        p = c
    # rebound confirmation on decision bar (history-only)
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
        max_positions=2,
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


def test_portfolio_rsi_trigger_3_candidates_maxpos2_batch_truncate_equal_share():
    """3 symbols fire same decision bar; max_positions=2 truncates to deepest 2,
    then equal-share cuts apply (total desired > 120% cap). Each admitted gets cap/2.

    Traced (capital=100000, gross_cap_pct=120): cap=120000, equal_share=60000.
    Volumes/steps produce RSI ordering A<B<C (all <20), so A and B admitted.
    Desired notionals (1.25%*24h vol) well above equal share, triggering cut.
    Entry at decision bar close (entry_next_bar=False), time_exit.
    """
    A = _make_rsi_series(0.97, 5_000_000)   # deepest RSI
    B = _make_rsi_series(0.98, 8_000_000)   # middle RSI
    C = _make_rsi_series(0.985, 6_000_000)  # mildest RSI (still <20)
    rsis = [_rsi(x, 21) for x in (A, B, C)]
    assert all(r is not None and r < 20.0 for r in rsis), rsis
    assert rsis == sorted(rsis), rsis  # A deepest -> B -> C mildest

    cfg = _cfg()
    res = run_portfolio_simulation({"A": A, "B": B, "C": C}, config=cfg, capital=100000.0)

    assert res["num_trades"] == 2
    symbols = [t["symbol"] for t in res["trades"]]
    assert symbols == ["A", "B"], (symbols, rsis)

    cap = 100000.0 * 120.0 / 100.0
    equal_share = cap / 2.0  # 60000.0
    decision_ts = A[-1]["timestamp"]
    for t, series in zip(res["trades"], (A, B)):
        assert t["entry_timestamp"] == decision_ts
        assert abs(float(t["entry_price"]) - float(series[-1]["close"])) < 1e-12
        notional = float(t["shares"]) * float(t["entry_price"])
        assert abs(notional - equal_share) < 1e-6, (t["symbol"], notional, equal_share)
        assert t["exit_reason"] == "time_exit"
    assert res["final_open_positions"] == 0
    assert abs(float(res["final_gross_exposure"])) < 1e-12


def test_portfolio_rsi_trigger_3_candidates_maxpos2_batch_truncate_entry_next_bar():
    """Same 3-candidate RSI maxpos=2 batch-truncate holds with entry_next_bar=True:
    decision on history-only bar, fills at next bar open, no look-ahead."""
    A = _make_rsi_series(0.97, 5_000_000)
    B = _make_rsi_series(0.98, 8_000_000)
    C = _make_rsi_series(0.985, 6_000_000)
    rsis = [_rsi(x, 21) for x in (A, B, C)]
    assert rsis == sorted(rsis) and all(r < 20.0 for r in rsis)

    for series in (A, B, C):
        last = series[-1]["close"]
        series.append(_bar(len(series), last * 1.01, last * 1.005, series[-1]["volume"]))

    cfg = _cfg(entry_next_bar=True)
    res = run_portfolio_simulation({"A": A, "B": B, "C": C}, config=cfg, capital=100000.0)

    assert res["num_trades"] == 2
    assert [t["symbol"] for t in res["trades"]] == ["A", "B"]
    cap = 100000.0 * 120.0 / 100.0
    equal_share = cap / 2.0
    exec_ts = A[61]["timestamp"]  # decision=60, fill next bar
    for t, series in zip(res["trades"], (A, B)):
        assert t["entry_timestamp"] == exec_ts
        assert abs(float(t["entry_price"]) - float(series[61]["open"])) < 1e-12
        notional = float(t["shares"]) * float(t["entry_price"])
        assert abs(notional - equal_share) < 1e-6, (t["symbol"], notional, equal_share)
        assert t["exit_reason"] == "time_exit"
    assert res["final_open_positions"] == 0
    assert abs(float(res["final_gross_exposure"])) < 1e-12