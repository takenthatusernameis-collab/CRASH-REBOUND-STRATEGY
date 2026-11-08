"""Debug: trace pending_realized_exits and risk_state during 2g experiment."""
from __future__ import annotations
import copy
from unittest.mock import patch
import scripts.run_portfolio as rp
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.strategy.risk import RiskState


def _c(i, o, h, l, cl, v=10_000_000.0):
    return {"timestamp": f"t{i:03d}", "open": o, "high": h, "low": l, "close": cl, "volume": v}


def _base(n=60):
    return [_c(i, 100.0, 101.0, 99.0, 100.0) for i in range(n)]


orig_reconcile = rp.run_portfolio_simulation.__wrapped__ if hasattr(rp.run_portfolio_simulation, "__wrapped__") else None

import functools

def main():
    n = 60
    a = _base(n); b = _base(n); c = _base(n)
    a[6] = _c(6, 100.0, 100.5, 99.0, 99.5)
    a[10] = _c(10, 100.0, 112.0, 99.0, 109.0)
    a[14] = _c(14, 115.0, 118.0, 114.0, 117.0)
    b[12] = _c(12, 96.0, 97.0, 93.0, 93.5)
    c[11] = _c(11, 100.0, 100.5, 99.0, 99.5)
    c[15] = _c(15, 100.0, 112.0, 99.0, 109.0)

    cfg = StrategyConfig(
        use_rsi_trigger=False, min_daily_volume_usd=0.0, enable_eth_hedge=False,
        enable_rebound_short=True, enable_liquidation_checks=True, entry_next_bar=True,
        enable_volume_based_sizing=False, gross_cap_pct=120.0, max_positions=2,
        avoid_downtrend=False, regime_min_price=1.0, crash_lookback=5,
        slippage_pct=0.01, commission_per_share=0.0, commission_min=0.0,
        funding_rate_pct_per_hour=0.0, liquidation_maint_margin_pct=5.0,
        liquidation_buffer_pct=1.0, liquidation_penalty_pct=0.5,
        rebound_short_time_exit_bars=48, max_daily_loss_pct=3.0,
    )
    sigs = {
        "A": Signal(symbol="A", side="long", reason="a", entry_price=100.0, stop_price=80.0,
                    target_price=109.0, risk_per_share=20.0, timestamp="t0005", size_shares=700.0, signal_index=5),
        "B": Signal(symbol="B", side="long", reason="b", entry_price=100.0, stop_price=80.0,
                    target_price=109.0, risk_per_share=20.0, timestamp="t0005", size_shares=700.0, signal_index=5),
        "C": Signal(symbol="C", side="long", reason="c", entry_price=100.0, stop_price=80.0,
                    target_price=109.0, risk_per_share=20.0, timestamp="t0010", size_shares=700.0, signal_index=10),
    }

    def fake_gen(hist, symbol=None, config=None, capital=100000.0, cache=None):
        if symbol in sigs and len(hist) - 1 == sigs[symbol].signal_index:
            s = copy.copy(sigs[symbol]); s.signal_index = len(hist) - 1; return s
        return None

    # Monkeypatch the reconcile to trace
    import types
    src = open(rp.__file__).read()
    # Instead, just wrap run_portfolio_simulation internals by re-implementing trace via patching _reconcile is hard (closure).
    # Simpler: patch RiskState.apply_trade to trace
    orig_apply = RiskState.apply_trade
    calls = []
    def traced_apply(self, date, pnl, opened, closed, notional=0.0):
        calls.append((date, pnl, opened, closed, notional, self.realized_pnl))
        return orig_apply(self, date, pnl, opened, closed, notional)
    RiskState.apply_trade = traced_apply

    with patch("scripts.run_portfolio.generate_signal", side_effect=fake_gen):
        res = rp.run_portfolio_simulation({"A": a, "B": b, "C": c}, config=cfg, capital=100000.0)
    RiskState.apply_trade = orig_apply
    print("apply_trade calls:")
    for c_ in calls:
        print("  ", c_)
    print("final realized_pnl:", res["risk_state"].realized_pnl)
    print("final open_position_notionals:", res["risk_state"].open_position_notionals)


if __name__ == "__main__":
    main()