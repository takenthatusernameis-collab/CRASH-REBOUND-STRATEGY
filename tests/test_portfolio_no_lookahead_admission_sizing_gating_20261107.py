"""Failing-tests-first regressions (2026-11-07T10:54:27Z): extend no-lookahead proof
and $5M gating guard for portfolio admission/sizing/hedge/gating.

Covers residual future-bar influence in scripts/run_portfolio.py:
- hist[:i+1] slicing feeds generate_signal (gating/admission decision)
- probe/exit path runs full series for execution realism, but admission at bar i
  (blocked vs admitted) must not depend on bars after entry_next_bar (i+1)
- entry_next_bar entry price is the next bar open (i+1), not future bars
- hedge sizing history must not use future bars (engine contract, exercised via portfolio)
- $5M gating: no spec-compliant path bypasses enforce_spec_volume_floor()/floored semantics
  (sub-threshold config values must not admit under-$5M history)

Synthetic fixtures only (non-evidence). BTC/ETH 283d 0-trade remains sole verified truth.
"""
from __future__ import annotations

import copy

from src.strategy.config import StrategyConfig, enforce_spec_volume_floor, SPEC_MIN_DAILY_VOLUME_USD
from src.strategy.crash_rebound import generate_signal, filter_universe
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


def _crash_rebound_series(n: int = 120, crash_at: int = 30, base_vol: float = 1_500_000.0):
    """Deterministic drop-trigger crash+rebound with volume sufficient only when sized."""
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


def _admissions(res):
    # Admission identity at decision level: which symbols were admitted (not blocked/no_signal).
    return [(t.get("symbol"), t.get("entry_timestamp")) for t in res.get("trades", [])]


def test_portfolio_admission_at_decision_bar_ignores_bars_after_entry_next_bar():
    """A1: hist[:i+1] drives gating; entry is at i+1 (entry_next_bar). Mutating bars
    strictly after i+1 must not change admission (blocked vs admitted) at decision bar i.
    Exit/PnL may differ (trade lifecycle uses future bars), but the decision to admit must
    not be influenced by bars after the entry bar."""
    base_candles = _crash_rebound_series(n=120, crash_at=30, base_vol=1_500_000.0)
    cfg = _cfg(min_daily_volume_usd=1_000_000.0)  # fixture threshold via floor? 1M -> floored to 5M
    # Use explicit fixture escape hatch? No — 1M is sub-threshold and must floor to 5M; but
    # series base_vol 1.5M * 24h window won't reach 5M. Use volume that reaches 5M at decision.
    candles = _crash_rebound_series(n=120, crash_at=30, base_vol=300_000.0)
    cfg = _cfg(min_daily_volume_usd=5_000_000.0)
    eth = {"ETH": _eth_series(120)}
    base = run_portfolio_simulation({"X": copy.deepcopy(candles)}, config=cfg, capital=100000.0, eth_candles=eth)
    mutated = copy.deepcopy(candles)
    # Crash around 30, decision likely 30/31; entry_next_bar => entry at 31/32. Mutate from 33 onward.
    for j in range(33, len(mutated)):
        mutated[j]["open"] = 9999.0
        mutated[j]["close"] = 9999.0
        mutated[j]["high"] = 10000.0
        mutated[j]["low"] = 9998.0
        mutated[j]["volume"] = 999_999_999.0
    fut = run_portfolio_simulation({"X": mutated}, config=cfg, capital=100000.0, eth_candles=eth)
    assert _admissions(base) == _admissions(fut), (
        f"admission/entry identity changed by bars after entry_next_bar: base={_admissions(base)} fut={_admissions(fut)}\n"
        f"base_trades={base['trades']}\nfut_trades={fut['trades']}")


def test_portfolio_entry_price_uses_next_bar_open_not_future_mutation():
    """A2: With entry_next_bar=True, executed entry must use next bar open. Mutating
    bars after that next bar must not change the entry price/timestamp of the admitted trade."""
    candles = _crash_rebound_series(n=120, crash_at=30, base_vol=300_000.0)
    cfg = _cfg(min_daily_volume_usd=5_000_000.0, entry_next_bar=True)
    eth = {"ETH": _eth_series(120)}
    base = run_portfolio_simulation({"X": copy.deepcopy(candles)}, config=cfg, capital=100000.0, eth_candles=eth)
    if base["num_trades"] == 0:
        # ensure we have a trade to assert on; if not, this fixture/setup needs adjustment
        # but don't fabricate — assert the precondition explicitly
        raise AssertionError(f"fixture precondition failed: expected >=1 trade, got {base['trades']}")
    base_entry = [(t["symbol"], t["entry_timestamp"]) for t in base["trades"]]
    mutated = copy.deepcopy(candles)
    for j in range(40, len(mutated)):
        mutated[j]["open"] = 7777.0
        mutated[j]["close"] = 7777.0
        mutated[j]["high"] = 7778.0
        mutated[j]["low"] = 7776.0
        mutated[j]["volume"] = 888_888_888.0
    fut = run_portfolio_simulation({"X": mutated}, config=cfg, capital=100000.0, eth_candles=eth)
    fut_entry = [(t["symbol"], t["entry_timestamp"]) for t in fut["trades"]]
    assert base_entry == fut_entry, f"entry identity changed by far-future mutation: {base_entry} vs {fut_entry}"


def test_portfolio_hedge_sizing_history_not_influenced_by_future_eth_coin_bars():
    """A3: Hedge sizing uses history available at entry decision (engine contract). Mutating
    coin/ETH bars after entry must not change admission or entry identity in portfolio."""
    candles = _crash_rebound_series(n=140, crash_at=30, base_vol=300_000.0)
    eth = _eth_series(140, v=6_000_000.0)
    cfg = _cfg(min_daily_volume_usd=5_000_000.0, enable_eth_hedge=True)
    base = run_portfolio_simulation({"X": copy.deepcopy(candles)}, config=cfg, capital=100000.0,
                                    eth_candles={"ETH": copy.deepcopy(eth)})
    mutated_c = copy.deepcopy(candles)
    mutated_e = copy.deepcopy(eth)
    for j in range(40, len(mutated_c)):
        mutated_c[j]["volume"] = 999_999_999.0
        mutated_c[j]["close"] *= 5.0
        mutated_c[j]["open"] *= 5.0
        mutated_c[j]["high"] *= 5.0
        mutated_c[j]["low"] *= 5.0
    for j in range(40, len(mutated_e)):
        mutated_e[j]["volume"] = 999_999_999.0
        mutated_e[j]["close"] *= 0.2
        mutated_e[j]["open"] *= 0.2
        mutated_e[j]["high"] *= 0.2
        mutated_e[j]["low"] *= 0.2
    fut = run_portfolio_simulation({"X": mutated_c}, config=cfg, capital=100000.0,
                                    eth_candles={"ETH": mutated_e})
    assert _admissions(base) == _admissions(fut), (
        f"admission changed by future coin/ETH bars under hedge sizing: base={_admissions(base)} fut={_admissions(fut)}")


def test_spec_volume_floor_enforced_for_subthreshold_values():
    """B1: $5M gating guard — sub-threshold non-zero values floor to spec minimum; 0 preserved."""
    assert enforce_spec_volume_floor(0) == 0.0
    assert enforce_spec_volume_floor(0.0) == 0.0
    assert enforce_spec_volume_floor(1) == SPEC_MIN_DAILY_VOLUME_USD
    assert enforce_spec_volume_floor(4_999_999.99) == SPEC_MIN_DAILY_VOLUME_USD
    assert enforce_spec_volume_floor(5_000_000.0) == SPEC_MIN_DAILY_VOLUME_USD
    assert enforce_spec_volume_floor(6_000_000.0) == 6_000_000.0
    assert enforce_spec_volume_floor(-1) == 0.0  # non-positive treated as escape hatch by implementation


def test_generate_signal_floors_subthreshold_config_volume():
    """B2: generate_signal must not admit under-$5M history when config carries sub-threshold value."""
    candles = _crash_rebound_series(n=60, crash_at=30, base_vol=100.0)  # ~2400 USD/24h
    hist = candles[:32]
    # sub-threshold config — generate_signal must floor to $5M and reject
    cfg = _cfg(min_daily_volume_usd=1_000.0)
    sig = generate_signal(hist, symbol="X", config=cfg, capital=100000.0)
    assert sig is None, f"sub-threshold config bypassed $5M floor in generate_signal: {sig}"


def test_filter_universe_floors_subthreshold_volume():
    """B3: filter_universe must not admit under-$5M history when given sub-threshold min volume."""
    candles = _crash_rebound_series(n=60, crash_at=30, base_vol=100.0)
    out = filter_universe({"X": candles}, min_daily_volume_usd=1_000.0)
    assert "X" not in out, f"sub-threshold min_daily_volume bypassed $5M floor in filter_universe: {out.keys()}"


def test_portfolio_does_not_admit_under_5m_history_with_subthreshold_config():
    """B4: Portfolio path uses generate_signal (floored) — sub-threshold config must not create
    a bypass for spec-compliant admission decisions."""
    candles = _crash_rebound_series(n=120, crash_at=30, base_vol=100.0)  # under $5M
    cfg = _cfg(min_daily_volume_usd=1_000.0)  # bypass attempt — must floor
    res = run_portfolio_simulation({"X": candles}, config=cfg, capital=100000.0,
                                   eth_candles={"ETH": _eth_series(120)})
    assert res["num_trades"] == 0, (
        f"portfolio admitted under-$5M history via sub-threshold config bypass: {res['trades']}")
