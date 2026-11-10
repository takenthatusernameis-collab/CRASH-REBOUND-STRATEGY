"""Trace in-loop 48h TIME_EXIT with NO aligned ETH bar at exit index (fallback path)."""
from __future__ import annotations
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.strategy.risk import DailyRiskState


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _cfg(fr=0.01):
    return StrategyConfig(
        enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=1.0, funding_rate_pct_per_hour=fr,
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


def _candles():
    n = 120
    coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
    coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)
    for i in range(9, n):
        coin[i] = _c(f"s{i}", 108.0, 115.0, 100.0, 107.0)
    # ETH: aligned at entry idx8, but SHORTER series so sidx(56) >= len(eth)
    eth = [_c(f"e{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
    eth[6] = _c("e6", 2000.0, 2010.0, 1990.0, 2000.0)
    eth[8] = _c("e8", 2000.0, 2030.0, 1995.0, 2025.0)
    for i in range(9, n):
        eth[i] = _c(f"eh{i}", 2030.0, 2050.0, 2020.0, 2040.0)
    # Truncate ETH to 55 bars: in-loop 48h exit at sidx=55 is MISSING -> fallback to hedge entry
    eth = eth[:55]
    return coin, eth


def main():
    coin, eth = _candles()
    print("len(coin)=", len(coin), "len(eth)=", len(eth))
    sig = _sig(600.0)

    rs_on = DailyRiskState()
    res_on = backtest_simple(coin, sig, config=_cfg(0.01), risk_state=rs_on, capital=100000.0, eth_candles=eth)
    rs_off = DailyRiskState()
    res_off = backtest_simple(coin, sig, config=_cfg(0.0), risk_state=rs_off, capital=100000.0, eth_candles=eth)

    print("exit_reason:", res_on.exit_reason)
    print("exit_timestamp:", res_on.exit_timestamp)
    print("bars_held:", res_on.bars_held)
    print("trades:", [(t["side"], t["reason"], t["entry"], t["exit"], t["pnl"]) for t in res_on.trades])
    print("rebound_hedge_side:", res_on.rebound_hedge_side)
    print("rebound_hedge_size:", res_on.rebound_hedge_size)
    print("rebound_hedge_entry:", res_on.rebound_hedge_entry)
    print("rebound_hedge_exit:", res_on.rebound_hedge_exit)
    print("rebound_hedge_pnl:", res_on.rebound_hedge_pnl)
    print("hedge_pnl:", res_on.hedge_pnl)
    print("max_live_coin_notional:", res_on.max_live_coin_notional)
    print("total_pnl(on):", res_on.total_pnl)
    print("total_pnl(off):", res_off.total_pnl)
    print("total_pnl delta:", res_on.total_pnl - res_off.total_pnl)
    print("--- risk_state ON ---")
    print("realized_pnl:", rs_on.realized_pnl)
    print("open_positions:", rs_on.open_positions)
    print("gross_exposure:", rs_on.gross_exposure)
    print("open_position_notionals:", rs_on.open_position_notionals)
    print("--- risk_state OFF ---")
    print("realized_pnl:", rs_off.realized_pnl)
    print("open_positions:", rs_off.open_positions)
    print("gross_exposure:", rs_off.gross_exposure)
    print("open_position_notionals:", rs_off.open_position_notionals)
    print("realized delta:", rs_on.realized_pnl - rs_off.realized_pnl)


if __name__ == "__main__":
    main()