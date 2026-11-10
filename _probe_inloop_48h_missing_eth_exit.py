"""Probe: rebound-short in-loop 48h TIME_EXIT with NO aligned ETH bar at the 48h
exit index (truncated ETH series: sidx >= len(eth_candles) at exit) x cap-cut
shares x commission_min x entry_next_bar x nonzero funding, with DailyRiskState.

Mirrors tests/test_rebound_short_48h_time_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_risk_settlement_20261110.py
but truncates the ETH series so the in-loop 48h break falls back to the hedge
entry raw for the rebound hedge exit (instead of an aligned ETH bar).
"""
from __future__ import annotations

from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.strategy.risk import DailyRiskState


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _cfg(funding_rate_pct_per_hour=0.01):
    return StrategyConfig(
        enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=1.0, funding_rate_pct_per_hour=funding_rate_pct_per_hour,
        min_daily_volume_usd=0.0, time_exit_max_bars=200,
        enable_liquidation_checks=False,
        liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5, gross_cap_pct=120.0,
        rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
    )


def _sig(shares=600.0):
    return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                  stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                  timestamp="t5", size_shares=shares, signal_index=5)


def _candles(eth_len=10):
    n = 120
    coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)      # entry_next_bar long fill
    coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)      # long target -> rebound short opens
    for i in range(9, n):
        coin[i] = _c(f"s{i}", 108.0, 115.0, 100.0, 107.0)
    # ETH truncated to eth_len bars (0..eth_len-1). Bars 0..8 identical to the
    # aligned lock so hedge sizing/entry are unchanged; bar 56 (48h exit) is
    # absent -> sidx=56 >= len(eth_candles) -> fallback to hedge entry raw.
    eth = [_c(f"e{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(eth_len)]
    if eth_len > 6:
        eth[6] = _c("e6", 2000.0, 2010.0, 1990.0, 2000.0)
    if eth_len > 8:
        eth[8] = _c("e8", 2000.0, 2030.0, 1995.0, 2025.0)  # rebound hedge entry aligned idx 8
    for i in range(9, eth_len):
        eth[i] = _c(f"eh{i}", 2030.0, 2050.0, 2020.0, 2040.0)
    return coin, eth


def main():
    coin, eth = _candles(eth_len=10)
    sig = _sig(600.0)

    rs_on = DailyRiskState()
    res_on = backtest_simple(coin, sig, config=_cfg(0.01), risk_state=rs_on,
                             capital=100000.0, eth_candles=eth)
    rs_off = DailyRiskState()
    res_off = backtest_simple(coin, sig, config=_cfg(0.0), risk_state=rs_off,
                              capital=100000.0, eth_candles=eth)

    print("=== exit_reason / bars ===")
    print("exit_reason:", res_on.exit_reason)
    print("exit_timestamp:", res_on.exit_timestamp)
    print("bars_held:", res_on.bars_held)
    print("trades reasons:", [t["reason"] for t in res_on.trades])
    print("len(trades):", len(res_on.trades))

    long_leg, short_leg = res_on.trades
    print("=== long leg ===")
    print("entry:", repr(long_leg["entry"]))
    print("exit:", repr(long_leg["exit"]))
    print("pnl:", repr(long_leg["pnl"]))
    print("=== short leg ===")
    print("entry:", repr(short_leg["entry"]))
    print("exit:", repr(short_leg["exit"]))
    print("pnl:", repr(short_leg["pnl"]))
    print("=== hedge ===")
    print("rebound_hedge_side:", res_on.rebound_hedge_side)
    print("rebound_hedge_size:", repr(res_on.rebound_hedge_size))
    print("rebound_hedge_entry:", repr(res_on.rebound_hedge_entry))
    print("rebound_hedge_exit:", repr(res_on.rebound_hedge_exit))
    print("rebound_hedge_pnl:", repr(res_on.rebound_hedge_pnl))
    print("hedge_pnl:", repr(res_on.hedge_pnl))
    print("=== aggregates ===")
    print("pnl field:", repr(res_on.pnl))
    print("total_pnl on:", repr(res_on.total_pnl))
    print("total_pnl off:", repr(res_off.total_pnl))
    print("max_live_coin_notional:", repr(res_on.max_live_coin_notional))
    print("=== risk state (funding on) ===")
    print("realized_pnl on:", repr(rs_on.realized_pnl))
    print("open_positions:", rs_on.open_positions)
    print("gross_exposure:", repr(rs_on.gross_exposure))
    print("open_position_notionals:", rs_on.open_position_notionals)
    print("=== risk state (funding off) ===")
    print("realized_pnl off:", repr(rs_off.realized_pnl))
    print("open_positions:", rs_off.open_positions)
    print("gross_exposure:", repr(rs_off.gross_exposure))
    print("=== deltas ===")
    print("total_pnl delta:", repr(res_on.total_pnl - res_off.total_pnl))
    print("realized_pnl delta:", repr(rs_on.realized_pnl - rs_off.realized_pnl))

    # Sanity: hedge exit must fall back to entry (not an aligned bar).
    print("=== fallback check ===")
    print("hedge exit == entry?", res_on.rebound_hedge_exit == res_on.rebound_hedge_entry)
    print("len(eth):", len(eth), "sidx at 48h exit:", 8 + 48)


if __name__ == "__main__":
    main()