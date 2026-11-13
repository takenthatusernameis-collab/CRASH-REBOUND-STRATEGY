"""TRACE PROBE 2 (throwaway): same cell with REAL DailyRiskState seeded with
existing 80k notional, to capture exact settlement/release numbers."""
from __future__ import annotations
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.strategy.risk import DailyRiskState
from _trace_liq48_capcut import build, _RS


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


if __name__ == "__main__":
    coin, eth, cfg, sig = build()
    # Real risk state seeded with existing 80k position (cap-cut context)
    rs = DailyRiskState(date="2025-01-01", open_positions=1, gross_exposure=80000.0,
                        open_position_notionals=[80000.0])
    res = backtest_simple(coin, sig, config=cfg, risk_state=rs,
                          capital=100000.0, eth_candles=eth)
    print("exit_reason=", res.exit_reason, "exit_ts=", res.exit_timestamp, "bars_held=", res.bars_held)
    for t in res.trades:
        print("  trade", t)
    print("shares=", res.shares, "entry_price=", res.entry_price)
    print("rebound_hedge_size=", res.rebound_hedge_size, "entry=", res.rebound_hedge_entry,
          "exit=", res.rebound_hedge_exit, "pnl=", res.rebound_hedge_pnl)
    print("max_live_coin_notional=", res.max_live_coin_notional)
    print("total_pnl=", res.total_pnl)
    print("rs.realized_pnl=", rs.realized_pnl)
    print("rs.open_positions=", rs.open_positions)
    print("rs.gross_exposure=", rs.gross_exposure)
    print("rs.open_position_notionals=", rs.open_position_notionals)

    # funding-off control
    coin2, eth2, cfg2, sig2 = build()
    cfg2.funding_rate_pct_per_hour = 0.0
    rs2 = DailyRiskState(date="2025-01-01", open_positions=1, gross_exposure=80000.0,
                         open_position_notionals=[80000.0])
    res2 = backtest_simple(coin2, sig2, config=cfg2, risk_state=rs2,
                           capital=100000.0, eth_candles=eth2)
    print("\nFUNDING-OFF:")
    print("total_pnl=", res2.total_pnl)
    print("short pnl=", res2.trades[1]["pnl"], "rh pnl=", res2.rebound_hedge_pnl)
    print("rs2.realized_pnl=", rs2.realized_pnl)
    print("rs2.open_position_notionals=", rs2.open_position_notionals)
    print("funding delta total=", res.total_pnl - res2.total_pnl)
    print("funding delta realized=", rs.realized_pnl - rs2.realized_pnl)