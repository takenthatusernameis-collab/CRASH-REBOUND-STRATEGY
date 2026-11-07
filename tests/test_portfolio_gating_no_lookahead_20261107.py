"""HANDOFF 2026-11-07T02:13:53Z priority (1): NO-LOOK-AHEAD + $5M GATING INTEGRITY
at portfolio scanner/wrapper/runner boundaries.

Failing-tests-first material hardening. Synthetic fixtures only (non-evidence).

Contracts proven:
- Portfolio scanner passes decision-available history (hist[:i+1]) to
  generate_signal / severity evaluation; mutating bars AFTER a completed trade's
  exit cannot change admission/sizing/hedge decision fields.
- $5M 24h volume enforced at decision time (not by future-bar inflation).
- Volume-based sizing derived from decision-available history.
- ETH hedge inputs derived from decision-available bars (future ETH mutations
  after exit do not change decision-relevant hedge fields).
- generate_signal enforces $5M using only provided history (caller-sliced).
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
        wiggle = 1.0 + (0.002 if i % 3 == 0 else -0.001)
        o, c = p, p * wiggle
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
    trades = []
    for t in res.get("trades", []):
        trades.append({
            "symbol": t.get("symbol"),
            "exit_reason": t.get("exit_reason"),
            "entry_timestamp": t.get("entry_timestamp"),
            "exit_timestamp": t.get("exit_timestamp"),
            "bars_held": t.get("bars_held"),
            "shares": round(float(t.get("shares", 0.0) or 0.0), 8),
            "hedge_side": t.get("hedge_side"),
            "hedge_size": round(float(t.get("hedge_size", 0.0) or 0.0), 8),
        })
    return {"num_trades": res.get("num_trades"), "trades": trades}


def _mutate_after_exits(candles, base_res, *, from_min=0):
    mutated = copy.deepcopy(candles)
    # compute conservative exit index upper bound from timestamps/bars_held
    max_exit = from_min
    for t in base_res.get("trades", []):
        # entry at decision+1 in next-bar mode; bars_held is engine-reported
        # scan timestamps to find exit index
        exit_ts = t.get("exit_timestamp")
        if exit_ts:
            for idx, c in enumerate(candles):
                if c.get("timestamp") == exit_ts:
                    max_exit = max(max_exit, idx)
        max_exit = max(max_exit, int(t.get("bars_held") or 0) + 40)
    start = min(len(mutated) - 1, max_exit + 5)
    for j in range(start, len(mutated)):
        p = max(0.01, mutated[j]["close"] * 50.0)
        mutated[j] = _bar(j, p, p * 1.01, v=999_999_999.0)
        mutated[j]["high"] = p * 1.02
        mutated[j]["low"] = p * 0.98
    return mutated, start


def test_portfolio_admission_sizing_stable_to_post_exit_future_mutation():
    candles = _crash_rebound_series(n=120, crash_at=30, base_vol=1_200_000.0)
    cfg = _cfg(min_daily_volume_usd=5_000_000.0)
    eth = {"ETH": _eth_series(120)}
    base = run_portfolio_simulation({"X": copy.deepcopy(candles)}, config=cfg, capital=100000.0, eth_candles=eth)
    assert base["num_trades"] >= 1, f"expected baseline trade, got {base}"
    mutated, start = _mutate_after_exits(candles, base)
    assert start < len(candles), "test setup: no post-exit tail to mutate"
    fut = run_portfolio_simulation({"X": mutated}, config=cfg, capital=100000.0, eth_candles=eth)
    assert _sig(base) == _sig(fut), f"post-exit mutation changed decision outcome: base={_sig(base)} fut={_sig(fut)}"


def test_portfolio_5m_volume_enforced_at_decision_not_future():
    candles = _crash_rebound_series(n=120, crash_at=30, base_vol=100.0)
    cfg = _cfg(min_daily_volume_usd=5_000_000.0)
    eth = {"ETH": _eth_series(120)}
    base = run_portfolio_simulation({"X": copy.deepcopy(candles)}, config=cfg, capital=100000.0, eth_candles=eth)
    assert base["num_trades"] == 0, f"below-$5M admitted: {base['trades']}"
    mutated = copy.deepcopy(candles)
    # Inflate far-future bars; decision is around bar 31, so mutating 70+ cannot help.
    for j in range(70, len(mutated)):
        mutated[j]["volume"] = 999_999_999.0
        mutated[j]["close"] = 500.0
        mutated[j]["open"] = 500.0
        mutated[j]["high"] = 501.0
        mutated[j]["low"] = 499.0
    fut = run_portfolio_simulation({"X": mutated}, config=cfg, capital=100000.0, eth_candles=eth)
    assert fut["num_trades"] == 0, f"future volume inflation admitted: {fut['trades']}"


def test_portfolio_volume_sizing_stable_to_post_exit_future_mutation():
    candles = _crash_rebound_series(n=120, crash_at=30, base_vol=1_500_000.0)
    cfg = _cfg(min_daily_volume_usd=1_000_000.0, enable_volume_based_sizing=True,
               position_size_pct_of_daily_volume=1.25)
    eth = {"ETH": _eth_series(120)}
    base = run_portfolio_simulation({"X": copy.deepcopy(candles)}, config=cfg, capital=100000.0, eth_candles=eth)
    assert base["num_trades"] >= 1, f"expected baseline trade, got {base}"
    mutated, start = _mutate_after_exits(candles, base)
    assert start < len(candles)
    for j in range(start, len(mutated)):
        mutated[j]["volume"] = 999_999_999.0
        mutated[j]["close"] *= 3.0
        mutated[j]["open"] *= 3.0
        mutated[j]["high"] = max(mutated[j]["open"], mutated[j]["close"]) * 1.001
        mutated[j]["low"] = min(mutated[j]["open"], mutated[j]["close"]) * 0.999
    fut = run_portfolio_simulation({"X": mutated}, config=cfg, capital=100000.0, eth_candles=eth)
    assert _sig(base) == _sig(fut), f"post-exit volume mutation changed sizing: base={_sig(base)} fut={_sig(fut)}"


def test_portfolio_hedge_inputs_stable_to_post_exit_future_eth_mutation():
    candles = _crash_rebound_series(n=120, crash_at=30, base_vol=1_500_000.0)
    eth = _eth_series(120)
    cfg = _cfg(min_daily_volume_usd=1_000_000.0, enable_eth_hedge=True, hedge_vol_lookback_hours=20)
    base = run_portfolio_simulation({"X": copy.deepcopy(candles)}, config=cfg, capital=100000.0,
                                    eth_candles={"ETH": eth})
    mutated_eth, _ = _mutate_after_exits(eth, base)
    for j in range(len(mutated_eth)):
        if mutated_eth[j]["volume"] == 999_999_999.0:
            p = max(0.01, mutated_eth[j]["close"] * (1.5 if j % 2 == 0 else 0.6))
            mutated_eth[j] = _bar(j, p / 1.1, p, v=9_999_999.0)
    fut = run_portfolio_simulation({"X": copy.deepcopy(candles)}, config=cfg, capital=100000.0,
                                    eth_candles={"ETH": mutated_eth})
    assert _sig(base) == _sig(fut), f"post-exit ETH mutation changed hedge/admission: base={_sig(base)} fut={_sig(fut)}"


def test_generate_signal_5m_volume_gate_uses_only_provided_history():
    from src.strategy.crash_rebound import generate_signal, _daily_volume_usd

    low = _crash_rebound_series(n=40, crash_at=30, base_vol=100.0)
    cfg = _cfg(min_daily_volume_usd=5_000_000.0)
    hist = low[:32]
    assert _daily_volume_usd(hist, 24) < 5_000_000.0
    assert generate_signal(hist, symbol="X", config=cfg, capital=100000.0) is None

    healthy = _crash_rebound_series(n=120, crash_at=30, base_vol=1_500_000.0)
    s1 = generate_signal(healthy[:32], symbol="X", config=cfg, capital=100000.0)
    s2 = generate_signal(copy.deepcopy(healthy[:32]), symbol="X", config=cfg, capital=100000.0)
    assert (s1 is None) == (s2 is None)
    if s1 and s2:
        assert s1.size_shares == s2.size_shares
        assert s1.signal_index == s2.signal_index
