"""Failing-tests-first: TradeResult.max_live_coin_notional must equal the max live
coin-position notional across the long-entry leg and the rebound-short-entry leg
(hedges excluded from the 120% coin-positions cap context).

The engine declares max_live_coin_notional but never computes it for the rebound
short leg, so callers without leg-log parsing (portfolio reservation overlay, future
paths) would reserve only the long-entry notional while the short leg is live.
"""
from src.backtest.engine import TradeResult


def test_max_live_coin_notional_default_is_long_entry_only():
    # long entry 100 @ 100 = 10000
    t = TradeResult(
        pnl=0.0, r_multiple=0.0, exit_reason='x',
        entry_price=100.0, shares=100.0,
    )
    assert t.max_live_coin_notional == 10000.0, (
        f"long-entry default notional wrong: {t.max_live_coin_notional}"
    )


def test_max_live_coin_notional_default_includes_rebound_short_leg():
    # long entry 100 @ 100 = 10000; rebound short opens at 109 @ 100 shares = 10900.
    # The live coin-position notional (max across legs, hedges excluded) is 10900,
    # NOT the long-entry notional (10000). Without this, portfolio reservation would
    # under-reserve exposure while the rebound short is live.
    t = TradeResult(
        pnl=0.0, r_multiple=0.0, exit_reason='target_rebound_short',
        entry_price=100.0, shares=100.0,
        trades=[
            {'side': 'long', 'entry': 100.0, 'exit': 109.0, 'pnl': 900.0, 'reason': 'target'},
            {'side': 'short', 'entry': 109.0, 'exit': 100.0, 'pnl': 900.0, 'reason': 'target'},
        ],
    )
    assert t.max_live_coin_notional == 10900.0, (
        f"max_live_coin_notional ignored rebound-short leg: got {t.max_live_coin_notional}, "
        f"expected 10900.0 (max of long-entry 10000 and short-entry 10900)"
    )


def test_max_live_coin_notional_explicit_overrides_default():
    t = TradeResult(
        pnl=0.0, r_multiple=0.0, exit_reason='x',
        entry_price=100.0, shares=100.0,
        max_live_coin_notional=4242.0,
    )
    assert t.max_live_coin_notional == 4242.0


def test_max_live_coin_notional_ignores_hedge_legs():
    # Hedges are excluded from the 120% coin-positions cap context. A long hedge
    # (rebound_hedge) or short hedge (hedge) must not inflate max_live_coin_notional.
    t = TradeResult(
        pnl=0.0, r_multiple=0.0, exit_reason='target_rebound_short',
        entry_price=100.0, shares=100.0,
        trades=[
            {'side': 'long', 'entry': 100.0, 'exit': 109.0, 'pnl': 900.0, 'reason': 'target'},
            {'side': 'short', 'entry': 109.0, 'exit': 100.0, 'pnl': 900.0, 'reason': 'target'},
        ],
        hedge_side='short', hedge_size=50.0, hedge_entry=100.0, hedge_exit=100.0,
        rebound_hedge_side='long', rebound_hedge_size=50.0,
        rebound_hedge_entry=100.0, rebound_hedge_exit=100.0,
    )
    assert t.max_live_coin_notional == 10900.0, (
        f"hedge legs leaked into max_live_coin_notional: {t.max_live_coin_notional}"
    )


def test_max_live_coin_notional_no_rebound_short_uses_long_entry():
    # Non-rebound exit: only the long leg exists. max_live_coin_notional == long entry.
    t = TradeResult(
        pnl=0.0, r_multiple=0.0, exit_reason='stopped',
        entry_price=100.0, shares=100.0,
        trades=[{'side': 'long', 'entry': 100.0, 'exit': 80.0, 'pnl': -2000.0, 'reason': 'stopped'}],
    )
    assert t.max_live_coin_notional == 10000.0, (
        f"non-rebound case wrong: {t.max_live_coin_notional}"
    )