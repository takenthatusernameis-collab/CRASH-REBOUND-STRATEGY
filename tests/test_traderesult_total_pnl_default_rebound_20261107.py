"""Failing-tests-first: TradeResult default total_pnl must account for all legs.

Engine always passes total_pnl, but direct construction/consumer fallbacks must not
silently drop rebound short/hedge legs. Non-evidence arithmetic contract test.
"""
from src.backtest.engine import TradeResult


def test_total_pnl_default_includes_rebound_short_and_rebound_hedge():
    t = TradeResult(
        pnl=100.0,
        hedge_pnl=-10.0,
        rebound_short_pnl=50.0,
        rebound_hedge_pnl=-5.0,
        r_multiple=0.0,
        exit_reason='target_then_rebound_target',
    )
    assert t.total_pnl == 135.0, (
        f"default total_pnl dropped rebound legs: got {t.total_pnl}, expected 135.0"
    )


def test_total_pnl_explicit_overrides_default():
    t = TradeResult(pnl=100.0, hedge_pnl=-10.0, rebound_short_pnl=50.0,
                    rebound_hedge_pnl=-5.0, total_pnl=999.0, r_multiple=0.0, exit_reason='x')
    assert t.total_pnl == 999.0


def test_total_pnl_default_without_rebound_matches_existing_behavior():
    t = TradeResult(pnl=100.0, hedge_pnl=-10.0, r_multiple=0.0, exit_reason='x')
    assert t.total_pnl == 90.0
