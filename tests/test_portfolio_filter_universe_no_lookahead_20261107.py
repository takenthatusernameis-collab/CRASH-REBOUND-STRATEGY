"""HANDOFF 2026-11-07 priority (1): NO-LOOKAHEAD/$5M GATING at portfolio wrapper.

Failing-tests-first: run_portfolio must not use full-series/future bars when
applying universe/volume gating. generate_signal gates per decision (volume,
regime, trigger) on decision-available history; portfolio prefilter must not
block symbols that are eligible at decision time just because end-of-series
state becomes ineligible, and must not admit based on future bars.

Synthetic fixtures only (non-evidence).
"""
from __future__ import annotations

import copy

from src.strategy.config import StrategyConfig
from scripts.run_portfolio import run_portfolio_simulation


def _ts(i: int) -> str:
    return f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z"


def _bar(i: int, o: float, c: float, v: float = 1_000_000.0) -> dict:
    hi = max(o, c) * 1.001
    lo = min(o, c) * 0.999
    return {"timestamp": _ts(i), "open": o, "high": hi, "low": lo, "close": c, "volume": v}


def _eth_series(n: int, v: float = 5_000_000.0):
    p = 2000.0
    out = []
    for i in range(n):
        o, c = p, p * (1.002 if i % 3 == 0 else 0.999)
        out.append(_bar(i, o, c, v=v))
        p = c
    return out


def _crash_rebound_series(n: int = 120, crash_at: int = 30, base_vol: float = 1_200_000.0):
    candles = []
    p = 100.0
    for i in range(n):
        if i < crash_at - 4:
            o, c, v = p, p * 1.002, base_vol
        elif i in (crash_at - 3, crash_at - 2):
            o, c, v = p, p * 0.998, base_vol
        elif i == crash_at - 1:
            o, c, v = p, p * 0.965, base_vol
        elif i == crash_at:
            o, c, v = p, p * 0.88, base_vol * 3.0
        elif i == crash_at + 1:
            o, c, v = p, p * 1.08, base_vol
        elif i == crash_at + 2:
            o, c, v = p, p * 1.01, base_vol
        else:
            o, c, v = p, p * 1.0002, base_vol
        candles.append(_bar(i, o, c, v))
        p = c
    return candles


def _cfg(**kw):
    defaults = dict(
        use_rsi_trigger=False,
        enable_rebound_short=False,
        enable_eth_hedge=False,
        enable_volume_based_sizing=False,
        min_daily_volume_usd=5_000_000.0,
        entry_next_bar=True,
        use_spec_safety_stop=True,
        enable_liquidation_checks=False,
        avoid_downtrend=False,
        time_exit_max_bars=72,
    )
    defaults.update(kw)
    return StrategyConfig(**defaults)


def _sig(res):
    return [(t.get("symbol"), t.get("exit_reason"), t.get("entry_timestamp"))
            for t in res.get("trades", [])]


def test_portfolio_full_series_prefilter_must_not_block_decision_time_eligible_symbol():
    """Regression: full-series filter_universe prefilter can block a symbol whose
    decision-time 24h volume/regime is eligible but end-of-series is not. That
    leaks future state into admission and creates false negatives."""
    candles = []
    p = 100.0
    for i in range(120):
        if i < 26:
            o, c, v = p, p * 1.002, 1_500_000.0
        elif i in (26, 27):
            o, c, v = p, p * 0.998, 1_500_000.0
        elif i == 28:
            o, c, v = p, p * 0.965, 1_500_000.0
        elif i == 29:
            o, c, v = p, p * 0.88, 1_500_000.0 * 3.0
        elif i == 30:
            o, c, v = p, p * 1.08, 1_500_000.0
        elif i == 31:
            o, c, v = p, p * 1.01, 1_500_000.0
        elif i < 80:
            o, c, v = p, p * 1.0002, 1_500_000.0
        else:
            # End-of-series becomes ineligible (below $5M) — must not block earlier decision.
            o, c, v = p * 0.7, p * 0.7, 100.0
        candles.append(_bar(i, o, c, v))
        p = c
    cfg = _cfg(min_daily_volume_usd=5_000_000.0, avoid_downtrend=False)
    res = run_portfolio_simulation({"X": candles}, config=cfg, capital=100000.0,
                                    eth_candles={"ETH": _eth_series(120)})
    assert res["num_trades"] >= 1, (
        "portfolio blocked a decision-time eligible symbol due to future end-of-series state: "
        f"{res['trades']}")


def test_portfolio_does_not_admit_symbol_due_to_future_volume_inflating_full_series_prefilter():
    """Future volume inflation must not admit via any wrapper boundary."""
    candles = _crash_rebound_series(n=120, crash_at=30, base_vol=100.0)
    cfg = _cfg(min_daily_volume_usd=5_000_000.0)
    eth = {"ETH": _eth_series(120)}
    base = run_portfolio_simulation({"X": copy.deepcopy(candles)}, config=cfg, capital=100000.0, eth_candles=eth)
    assert base["num_trades"] == 0
    mutated = copy.deepcopy(candles)
    for j in range(70, len(mutated)):
        mutated[j]["volume"] = 999_999_999.0
        mutated[j]["close"] = 500.0
        mutated[j]["open"] = 500.0
        mutated[j]["high"] = 501.0
        mutated[j]["low"] = 499.0
    fut = run_portfolio_simulation({"X": mutated}, config=cfg, capital=100000.0, eth_candles=eth)
    assert fut["num_trades"] == 0, f"future volume inflation admitted via wrapper boundary: {fut['trades']}"


def test_portfolio_prefilter_uses_decision_available_regime_not_future_tail_only():
    candles = _crash_rebound_series(n=120, crash_at=30, base_vol=1_500_000.0)
    cfg = _cfg(min_daily_volume_usd=1_000_000.0, avoid_downtrend=True, ma_fast_period=20)
    eth = {"ETH": _eth_series(120)}
    base = run_portfolio_simulation({"X": copy.deepcopy(candles)}, config=cfg, capital=100000.0, eth_candles=eth)
    mutated = copy.deepcopy(candles)
    for j in range(80, len(mutated)):
        mutated[j]["close"] = 10_000.0
        mutated[j]["open"] = 10_000.0
        mutated[j]["high"] = 10_001.0
        mutated[j]["low"] = 9_999.0
        mutated[j]["volume"] = 5_000_000.0
    fut = run_portfolio_simulation({"X": mutated}, config=cfg, capital=100000.0, eth_candles=eth)
    assert _sig(base) == _sig(fut), f"future regime tail changed outcome: base={_sig(base)} fut={_sig(fut)}"
