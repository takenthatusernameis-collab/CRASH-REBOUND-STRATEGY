"""Regression: a trade exiting at the final scanned bar must release occupancy
and reserved notional; final state must reconcile to zero open exposure.

HANDOFF item 2 (bars_held/exit-index alignment): occupied_until must not leak a
final-bar exit into final_open_positions / final_gross_exposure. Every admitted
trade has an exit at or before the final bar, so no position survives past the
last scanned bar.

Synthetic fixture only; non-evidence.
"""
from __future__ import annotations

import copy
from unittest.mock import patch

from scripts.run_portfolio import run_portfolio_simulation
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(i, o, h, l, cl, v=10_000_000.0):
    return {"timestamp": f"t{i:04d}", "open": o, "high": h, "low": l, "close": cl, "volume": v}


def test_final_bar_exit_releases_occupancy_and_notional():
    n = 60
    candles = [_c(i, 100.0, 101.0, 99.0, 100.0) for i in range(n)]
    # Bar n-3 crash (spike volume), bar n-2 rebound => signal at decision bar n-2.
    # entry_next_bar=False => engine enters at n-2, holds to the last bar n-1
    # (time exit) => exit_idx == n-1 == final bar -> must not leak occupancy.
    candles[n - 3] = _c(n - 3, 100.0, 101.0, 85.0, 86.0, v=50_000_000.0)
    candles[n - 2] = _c(n - 2, 86.0, 99.0, 85.0, 98.0)
    cfg = StrategyConfig(
        use_rsi_trigger=False,
        enable_rebound_short=False,
        enable_eth_hedge=False,
        min_daily_volume_usd=0.0,  # non-spec fixture escape hatch
        entry_next_bar=False,
        crash_lookback=2,
        time_exit_max_bars=1000,
        max_daily_loss_pct=5.0,
        gross_cap_pct=120.0,
        max_positions=10,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
        funding_rate_pct_per_hour=0.0,
        enable_liquidation_checks=False,
        avoid_downtrend=False,
        regime_min_price=1.0,
    )
    sig = Signal(
        symbol="X", side="long", reason="t", entry_price=100.0, stop_price=80.0,
        target_price=120.0, risk_per_share=10.0, timestamp="", size_shares=10.0,
        signal_index=n - 2,
    )

    def fake(hist, symbol=None, config=None, capital=100000.0, cache=None):
        if symbol == "X" and len(hist) - 1 == n - 2:
            s = copy.copy(sig)
            s.signal_index = len(hist) - 1
            return s
        return None

    with patch("scripts.run_portfolio.generate_signal", side_effect=fake):
        res = run_portfolio_simulation({"X": candles}, config=cfg, capital=100000.0)

    assert res["num_trades"] == 1, f"expected exactly 1 trade, got {res['trades']}"
    # Final-bar exit must release occupancy and reserved notional (no leak).
    assert res["final_open_positions"] == 0, (
        f"final-bar exit leaked occupancy: final_open_positions={res['final_open_positions']}")
    assert abs(float(res["final_gross_exposure"])) < 1e-9, (
        f"final-bar exit leaked notional: final_gross_exposure={res['final_gross_exposure']}")
    assert list(res["risk_state"].open_position_notionals) == [], (
        f"final-bar exit leaked notionals: {res['risk_state'].open_position_notionals}")
