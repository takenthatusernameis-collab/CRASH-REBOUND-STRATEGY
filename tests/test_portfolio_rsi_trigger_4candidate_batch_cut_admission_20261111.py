"""Regression lock (2026-11-11): RSI-trigger deepest-first admission + equal-share
batch cut for 4 same-decision-bar candidates in the portfolio/gated path.

Covers uncovered #3 edge case: 3+ RSI-trigger candidates on the same decision bar
with enable_rebound_short batch-cut path active (multiple candidates, no existing
positions) and total desired notional above 120% gross cap. Spec: admit deepest
RSI crashes first and apply equal-share cuts (old+new context: all concurrent
admissions) across the 120% cap. Deterministic synthetic fixtures only.
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
        max_positions=4,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
        entry_next_bar=False,
        target_pct=200.0,  # keep long leg from target-hitting on synthetic bar
        rebound_short_target_pct=9.0,
        rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=5,
        time_exit_max_bars=5,
    )
    d.update(kw)
    return StrategyConfig(**d)


def test_portfolio_rsi_trigger_4_candidates_batch_equal_share_cut_and_order():
    """4 symbols fire same decision bar; desired notionals (1.25% 24h vol sizing)
    exceed 120% gross cap, so batch-cut path applies equal-share cuts. All 4
    admitted in deepest-first RSI order, each reserved/executed at cap/4.

    Traced (capital=100000, gross_cap_pct=120): cap=120000, equal_share=30000.
    Volumes/steps produce RSI ordering A<B<C<D (all <20) and heterogeneous
    desired notionals (1.25%*24h vol) well above equal share. Entry at decision
    bar close (entry_next_bar=False), target_pct high so exit is time_exit.
    """
    A = _make_rsi_series(0.97, 5_000_000)   # deepest RSI
    B = _make_rsi_series(0.98, 8_000_000)
    C = _make_rsi_series(0.985, 6_000_000)
    D = _make_rsi_series(0.99, 7_000_000)   # mildest RSI (still <20)
    rsis = [_rsi(x, 21) for x in (A, B, C, D)]
    assert all(r is not None and r < 20.0 for r in rsis), rsis
    assert rsis == sorted(rsis), rsis  # A deepest -> D mildest

    cfg = _cfg()
    res = run_portfolio_simulation({"A": A, "B": B, "C": C, "D": D}, config=cfg, capital=100000.0)

    assert res["num_trades"] == 4
    symbols = [t["symbol"] for t in res["trades"]]
    assert symbols == ["A", "B", "C", "D"], (symbols, rsis)

    cap = 100000.0 * 120.0 / 100.0
    equal_share = cap / 4.0  # 30000.0
    decision_ts = A[-1]["timestamp"]
    for t, series in zip(res["trades"], (A, B, C, D)):
        assert t["entry_timestamp"] == decision_ts
        assert abs(float(t["entry_price"]) - float(series[-1]["close"])) < 1e-12
        notional = float(t["shares"]) * float(t["entry_price"])
        assert abs(notional - equal_share) < 1e-6, (t["symbol"], notional, equal_share)
        assert t["exit_reason"] == "time_exit"
    assert res["final_open_positions"] == 0
    assert abs(float(res["final_gross_exposure"])) < 1e-12


def test_portfolio_rsi_trigger_4_candidates_batch_equal_share_cut_entry_next_bar():
    """Same 4-candidate RSI deepest-first batch-equal-share admission holds with
    entry_next_bar=True: decision on history-only bar, fills at next bar open,
    no look-ahead. One extra post-decision bar appended for execution."""
    A = _make_rsi_series(0.97, 5_000_000)
    B = _make_rsi_series(0.98, 8_000_000)
    C = _make_rsi_series(0.985, 6_000_000)
    D = _make_rsi_series(0.99, 7_000_000)
    rsis = [_rsi(x, 21) for x in (A, B, C, D)]
    assert rsis == sorted(rsis) and all(r < 20.0 for r in rsis)

    for series in (A, B, C, D):
        last = series[-1]["close"]
        # execution bar after decision; keep flat so no unintended target/stop
        series.append(_bar(len(series), last * 1.01, last * 1.005, series[-1]["volume"]))

    cfg = _cfg(entry_next_bar=True)
    res = run_portfolio_simulation({"A": A, "B": B, "C": C, "D": D}, config=cfg, capital=100000.0)

    assert res["num_trades"] == 4
    assert [t["symbol"] for t in res["trades"]] == ["A", "B", "C", "D"]
    cap = 100000.0 * 120.0 / 100.0
    equal_share = cap / 4.0
    exec_ts = A[61]["timestamp"]  # decision=60, fill next bar
    for t, series in zip(res["trades"], (A, B, C, D)):
        assert t["entry_timestamp"] == exec_ts
        assert abs(float(t["entry_price"]) - float(series[61]["open"])) < 1e-12
        notional = float(t["shares"]) * float(t["entry_price"])
        assert abs(notional - equal_share) < 1e-6, (t["symbol"], notional, equal_share)
        assert t["exit_reason"] == "time_exit"
    assert res["final_open_positions"] == 0
    assert abs(float(res["final_gross_exposure"])) < 1e-12
