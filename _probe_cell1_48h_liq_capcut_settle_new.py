"""Trace probe (2026-11-11): rebound-short LIQUIDATION on exact 48th held bar
UNDER cap_cut regime + commission_min + entry_next_bar, with DailyRiskState
settlement (NOT _NoCutRS), aligned ETH present at exit bar.

short_start_idx = 8. 48th held bar: sidx - 8 + 1 == 48 => sidx = 55.
"""
from __future__ import annotations

from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.strategy.risk import DailyRiskState


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _candles():
    n = 80
    coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)    # entry_next_bar long fill
    coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)    # long target -> rebound short opens
    for i in range(9, n):
        coin[i] = _c(f"s{i}", 108.0, 115.0, 100.0, 107.0)
    # 48th held bar (sidx=55): high=120.0 triggers liq (threshold ~115.54), low=100.5 > target (99.19)
    coin[55] = _c("b55", 108.0, 120.0, 100.5, 107.0)
    return coin


def _eth():
    n = 80
    eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
    eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
    eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)    # rebound hedge entry idx 8
    for i in range(9, n):
        eth[i] = _c(f"eh{i}", 2030.0, 2050.0, 2020.0, 2040.0)
    eth[55] = _c("eh55", 2030.0, 2055.0, 2020.0, 2045.0)  # hedge exit on 48th bar
    return eth


def _cfg():
    return StrategyConfig(
        enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=1.0, funding_rate_pct_per_hour=0.01,
        min_daily_volume_usd=0.0, time_exit_max_bars=200,
        enable_liquidation_checks=True, liquidation_maint_margin_pct=5.0,
        liquidation_buffer_pct=1.0, liquidation_penalty_pct=0.5, gross_cap_pct=120.0,
        rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
    )


def _sig():
    return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                  stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                  timestamp="t5", size_shares=1000.0, signal_index=5)


def main():
    coin = _candles()
    eth = _eth()
    cfg = _cfg()
    sig = _sig()
    rs = DailyRiskState()
    res = backtest_simple(coin, sig, config=cfg, risk_state=rs,
                          capital=100000.0, eth_candles=eth)
    print("exit_reason:", res.exit_reason)
    print("exit_timestamp:", res.exit_timestamp)
    print("bars_held:", res.bars_held)
    print("trades:", res.trades)
    print("rebound_hedge_side:", res.rebound_hedge_side)
    print("rebound_hedge_size:", repr(res.rebound_hedge_size))
    print("rebound_hedge_entry:", repr(res.rebound_hedge_entry))
    print("rebound_hedge_exit:", repr(res.rebound_hedge_exit))
    print("rebound_hedge_pnl:", repr(res.rebound_hedge_pnl))
    print("hedge_pnl:", repr(res.hedge_pnl))
    print("max_live_coin_notional:", repr(res.max_live_coin_notional))
    print("total_pnl:", repr(res.total_pnl))
    print("risk_state.realized_pnl:", repr(rs.realized_pnl))
    print("risk_state.open_positions:", rs.open_positions)
    print("risk_state.gross_exposure:", rs.gross_exposure)
    print("risk_state.open_position_notionals:", rs.open_position_notionals)
    print("--- long-leg hedge (hedge_*) ---")
    print("hedge_side:", res.hedge_side)
    print("hedge_size:", repr(res.hedge_size))
    print("hedge_entry:", repr(res.hedge_entry))
    print("hedge_exit:", repr(res.hedge_exit))
    print("hedge_pnl:", repr(res.hedge_pnl))
    print("rebound_short_pnl:", repr(res.rebound_short_pnl))
    print("pnl (long coin net):", repr(res.pnl))
    # funding-off baseline
    rs2 = DailyRiskState()
    cfg_off = _cfg()
    cfg_off.funding_rate_pct_per_hour = 0.0
    res2 = backtest_simple(coin, sig, config=cfg_off, risk_state=rs2,
                           capital=100000.0, eth_candles=eth)
    print("--- funding off ---")
    print("total_pnl_off:", repr(res2.total_pnl))
    print("rebound_hedge_pnl_off:", repr(res2.rebound_hedge_pnl))
    print("risk_state.realized_pnl_off:", repr(rs2.realized_pnl))


if __name__ == "__main__":
    main()