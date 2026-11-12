"""2026-11-12 CELL 13: portfolio-level bounce-gated rebound-short admission under the 120% cap.

Spec (crash-rebound-strategy.pdf): "Only coins that already bounced hard are worth shorting".
CELL 12 wired the opt-in engine gate `rebound_short_require_bounce_confirm` (default False) at
src/backtest/engine.py:472-479: when True, the rebound short may only open when the target bar
itself confirms (confirm_rebound over candles[:idx+1], no look-ahead); otherwise the long closes
at target with exit_reason='target' and no short leg.

Gap proof (2026-11-12): grep across tests/ and scripts/run_portfolio.py shows the bounce gate is
covered ONLY at engine level (`tests/test_rebound_short_requires_bounce_confirmation_20261112.py`,
backtest_simple directly). No portfolio/runner test asserts what happens to the admitted coin book
when the gate suppresses the rebound short:
  - does max_live_coin_notional (run_portfolio.py:341-345; engine.py:33-37) stay at the long-entry
    notional instead of the rebound-inflated short-entry notional?
  - is there portfolio-level parity (same crash book, gate on vs off → coin notionals identical
    except the suppressed short's notional difference)?
  - does gate-on cut the long (it must not)?

run_portfolio.py records `executed_notional = max_live_coin_notional` for the reservation overlay
but never exposed it in the trade record, so the portfolio-layer reservation basis was
unobservable. This test adds it additively (scripts/run_portfolio.py trade dict key
`max_live_coin_notional`) and asserts it.

Scenario (capital=100000, 120% cap=120000, single symbol T, no hedges, no slippage/commission/
funding, liquidation off):
  - bar 5 = crash/decision signal, bar 6 = entry fill @100 (1000 shares, entry notional 100000),
    bar 7 = long +9% target (high 110 >= 109).
  - bar 7 NON-CONFIRMING: open 109.5, close 109 (close <= open) -> confirm_rebound False.
  - bar 7 CONFIRMING: open 108, close 109.5, high 110, low 108 -> body 1.5/2 = 0.75 >= 0.5 -> True.
  - bars 8-11 flat @108.5; an opened short exits at series end @108.5 (+500).

Traced values:
  - long-only: exit_reason='target', max_live_coin_notional=100000 (long entry only), total_pnl=9000.
  - short opens: exit_reason='target_rebound_short', max_live_coin_notional=109000 (rebound-inflated),
    total_pnl=9500, short entry notional 109000.
  - gate-on must NOT cut the long: shares == 1000 (full admission, entry notional 100000 <= cap).

Mutation-verified non-vacuous: stubbing confirm_rebound->False with gate ON + confirming bar flips
the confirming case back to long-only (max_live 100000), proving the gate is consulted at the
portfolio layer, not dead code.
"""

from __future__ import annotations

import copy
from unittest.mock import patch

from scripts.run_portfolio import run_portfolio_simulation
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal

CAPITAL = 100000.0
CAP_VALUE = CAPITAL * 120.0 / 100.0  # 120000.0
SHARES = 1000.0
ENTRY_PX = 100.0
TARGET_PX = 109.0
SHORT_ENTRY_PX = 109.0
SHORT_EXIT_PX = 108.5
LONG_ENTRY_NOTIONAL = ENTRY_PX * SHARES  # 100000.0
SHORT_NOTIONAL = SHORT_ENTRY_PX * SHARES  # 109000.0
LONG_PNL = (TARGET_PX - ENTRY_PX) * SHARES  # 9000.0
SHORT_PNL = (SHORT_ENTRY_PX - SHORT_EXIT_PX) * SHARES  # 500.0
TOTAL_LONG_ONLY = LONG_PNL  # 9000.0
TOTAL_WITH_SHORT = LONG_PNL + SHORT_PNL  # 9500.0


def _c(i, o, h, l, cl, v=10_000_000.0):
    return {"timestamp": f"2025-12-20T{i:02d}:00:00Z", "open": o, "high": h, "low": l, "close": cl, "volume": v}


# Pre-signal history bars 0-4 (no crash), crash/decision bar 5, entry fill bar 6 @100,
# target bar 7 (variant), flat post-target bars 8-11 @108.5 (short exits at series end).
def _candles(bar7):
    return [
        _c(0, 100.0, 101.0, 99.0, 100.0),
        _c(1, 100.0, 101.0, 99.0, 100.0),
        _c(2, 100.0, 101.0, 99.0, 100.0),
        _c(3, 100.0, 101.0, 99.0, 100.0),
        _c(4, 100.0, 101.0, 99.0, 100.0),
        _c(5, 100.0, 100.0, 90.0, 90.0),   # crash/decision bar (signal fires here)
        _c(6, 100.0, 101.0, 99.0, 100.0),  # entry fill @100
        bar7,                                # target bar (high 110 >= 109)
        _c(8, 108.5, 109.0, 108.0, 108.5),
        _c(9, 108.5, 109.0, 108.0, 108.5),
        _c(10, 108.5, 109.0, 108.0, 108.5),
        _c(11, 108.5, 109.0, 108.0, 108.5),
    ]


_NONCONFIRMING = _c(7, 109.5, 110.0, 108.5, 109.0)  # close <= open -> does not confirm
_CONFIRMING = _c(7, 108.0, 110.0, 108.0, 109.5)      # close>open, body 1.5/2=0.75>=0.5 -> confirms

CANDLES_NONCONFIRM = _candles(_NONCONFIRMING)
CANDLES_CONFIRM = _candles(_CONFIRMING)


def _cfg(confirm: bool) -> StrategyConfig:
    return StrategyConfig(
        use_rsi_trigger=False,
        enable_rebound_short=True,
        enable_eth_hedge=False,
        enable_liquidation_checks=False,
        entry_next_bar=True,
        min_daily_volume_usd=0.0,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
        funding_rate_pct_per_hour=0.0,
        avoid_downtrend=False,
        regime_min_price=0.0,
        gross_cap_pct=120.0,
        max_positions=10,
        time_exit_max_bars=48,
        stop_atr_mult=8.0,
        use_spec_safety_stop=True,
        atr_period=14,
        rebound_short_target_pct=9.0,
        rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
        rebound_lookback=3,
        rebound_min_body_ratio=0.5,
        rebound_short_require_bounce_confirm=confirm,
        target_pct=9.0,
    )


_SIG = Signal(
    symbol="T",
    side="long",
    reason="crash_then_rebound",
    entry_price=ENTRY_PX,
    stop_price=50.0,
    target_price=TARGET_PX,
    risk_per_share=20.0,
    size_shares=SHARES,
    signal_index=5,
    timestamp="2025-12-20T05:00:00Z",
)


def _fake(hist, symbol=None, config=None, capital=CAPITAL, cache=None):
    idx = len(hist) - 1
    if symbol == "T" and idx == 5:
        s = copy.copy(_SIG)
        s.signal_index = idx
        return s
    return None


def _run(candles, confirm: bool):
    with patch("scripts.run_portfolio.generate_signal", side_effect=_fake):
        return run_portfolio_simulation(
            {"T": candles},
            config=_cfg(confirm),
            capital=CAPITAL,
        )


def test_portfolio_bounce_gate_on_nonconfirming_suppresses_short_long_entry_notional_reserved():
    """Gate ON + non-confirming target bar: rebound short suppressed -> long-only target exit.

    max_live_coin_notional stays at the long-entry notional (100000), NOT the rebound-inflated
    short-entry notional (109000). The long is admitted full (shares == 1000, not cut) because
    100000 <= 120000 cap.
    """
    res = _run(CANDLES_NONCONFIRM, confirm=True)
    by = {t["symbol"]: t for t in res["trades"]}
    assert "T" in by, f"T did not trade: {res['trades']}"
    t = by["T"]
    assert t["exit_reason"] == "target", t
    assert [t for t in res["trades"]][0]["entry_price"] == ENTRY_PX
    assert abs(float(t["shares"]) - SHARES) < 1e-9, (  # long NOT cut
        f"gate-on cut the long: {t['shares']} trades={res['trades']}")
    assert abs(float(t["entry_price"]) - ENTRY_PX) < 1e-9, t
    assert abs(float(t["max_live_coin_notional"]) - LONG_ENTRY_NOTIONAL) < 1e-6, (
        f"max_live_coin_notional not long-entry-only: {t['max_live_coin_notional']} "
        f"(expected {LONG_ENTRY_NOTIONAL}, rebound-inflated would be {SHORT_NOTIONAL})")
    assert abs(float(t["total_pnl"]) - TOTAL_LONG_ONLY) < 1e-9, t
    # Portfolio-level parity: entry notional identical to gate-off case; max_live differs only by
    # the suppressed short's notional (109000 - 100000 = 9000).
    assert abs(float(t["shares"]) * float(t["entry_price"]) - LONG_ENTRY_NOTIONAL) < 1e-6


def test_portfolio_bounce_gate_off_same_bar_short_opens_rebound_inflated_max_live():
    """Gate OFF + same non-confirming target bar: short opens -> target_rebound_short, max_live
    rebound-inflated at 109000 (long 100000 vs short 109000). Same crash book as gate-on case."""
    res = _run(CANDLES_NONCONFIRM, confirm=False)
    by = {t["symbol"]: t for t in res["trades"]}
    assert "T" in by, f"T did not trade: {res['trades']}"
    t = by["T"]
    assert t["exit_reason"] == "target_rebound_short", t
    assert abs(float(t["shares"]) - SHARES) < 1e-9, t
    assert abs(float(t["entry_price"]) - ENTRY_PX) < 1e-9, t
    assert abs(float(t["max_live_coin_notional"]) - SHORT_NOTIONAL) < 1e-6, (
        f"max_live_coin_notional not rebound-inflated: {t['max_live_coin_notional']} "
        f"(expected {SHORT_NOTIONAL})")
    assert abs(float(t["total_pnl"]) - TOTAL_WITH_SHORT) < 1e-9, t
    # Parity vs gate-on: entry notional identical (100000); max_live higher by exactly the
    # suppressed short's notional difference (9000).
    assert abs(float(t["shares"]) * float(t["entry_price"]) - LONG_ENTRY_NOTIONAL) < 1e-6


def test_portfolio_bounce_gate_on_confirming_bar_short_opens():
    """Gate ON + confirming target bar: gate passes, short opens (mirrors gate-off behavior)."""
    res = _run(CANDLES_CONFIRM, confirm=True)
    by = {t["symbol"]: t for t in res["trades"]}
    assert "T" in by, f"T did not trade: {res['trades']}"
    t = by["T"]
    assert t["exit_reason"] == "target_rebound_short", t
    assert abs(float(t["max_live_coin_notional"]) - SHORT_NOTIONAL) < 1e-6, t
    assert abs(float(t["total_pnl"]) - TOTAL_WITH_SHORT) < 1e-9, t


def test_portfolio_bounce_gate_consulted_mutation_confirm_false():
    """Mutation check: stub confirm_rebound->False with gate ON + confirming bar. The confirming
    case must collapse to long-only (max_live 100000), proving the gate is actually consulted
    at the portfolio layer and not dead code."""
    with patch("src.backtest.engine.confirm_rebound", return_value=False):
        res = _run(CANDLES_CONFIRM, confirm=True)
    by = {t["symbol"]: t for t in res["trades"]}
    assert "T" in by, f"T did not trade: {res['trades']}"
    t = by["T"]
    assert t["exit_reason"] == "target", t
    assert abs(float(t["max_live_coin_notional"]) - LONG_ENTRY_NOTIONAL) < 1e-6, (
        f"gate not load-bearing: max_live {t['max_live_coin_notional']} (expected long-only "
        f"{LONG_ENTRY_NOTIONAL})")
    assert abs(float(t["total_pnl"]) - TOTAL_LONG_ONLY) < 1e-9, t


if __name__ == "__main__":
    import unittest
    unittest.main()
