"""Probe: derive engine-traced values for rebound-short STOP/TARGET exit with ETH
hedge bar missing at the exit index (uncovered #4 cell). Synthetic fixture only.
"""
from __future__ import annotations

from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.strategy.risk import DailyRiskState


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _cfg(rate=0.01):
    return StrategyConfig(
        enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=1.0, funding_rate_pct_per_hour=rate,
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


def _base_coin():
    n = 120
    coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)    # entry_next_bar long fill
    coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)    # long target -> rebound short opens
    return coin


def _base_eth():
    # ETH len 9 (indices 0..8): hedge sizing/entry aligned at idx 8 present;
    # rebound exit idx 9 is OUT OF RANGE -> fallback-to-entry RAW path.
    eth = [_c(f"e{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(9)]
    eth[6] = _c("e6", 2000.0, 2010.0, 1990.0, 2000.0)
    eth[8] = _c("e8", 2000.0, 2030.0, 1995.0, 2025.0)  # rebound hedge entry aligned idx 8
    return eth


def _run(coin, eth, rate=0.01):
    rs = DailyRiskState()
    res = backtest_simple(coin, _sig(600.0), config=_cfg(rate),
                          risk_state=rs, capital=100000.0, eth_candles=eth)
    rs2 = DailyRiskState()
    res2 = backtest_simple(coin, _sig(600.0), config=_cfg(0.0),
                           risk_state=rs2, capital=100000.0, eth_candles=eth)
    return res, rs, res2, rs2


def dump(tag, res, rs, res2, rs2):
    print(f"=== {tag} ===")
    print("exit_reason:", res.exit_reason)
    print("exit_timestamp:", res.exit_timestamp)
    print("bars_held:", res.bars_held)
    print("trades:", res.trades)
    print("rebound_short_pnl:", repr(res.rebound_short_pnl))
    print("rebound_hedge_side:", res.rebound_hedge_side)
    print("rebound_hedge_size:", repr(res.rebound_hedge_size))
    print("rebound_hedge_entry:", repr(res.rebound_hedge_entry))
    print("rebound_hedge_exit:", repr(res.rebound_hedge_exit))
    print("rebound_hedge_pnl:", repr(res.rebound_hedge_pnl))
    print("hedge_pnl:", repr(res.hedge_pnl))
    print("max_live_coin_notional:", repr(res.max_live_coin_notional))
    print("total_pnl:", repr(res.total_pnl))
    print("rs.realized_pnl:", repr(rs.realized_pnl))
    print("rs.open_positions:", rs.open_positions)
    print("rs.gross_exposure:", rs.gross_exposure)
    print("rs.open_position_notionals:", rs.open_position_notionals)
    print("off.total_pnl:", repr(res2.total_pnl))
    print("off.rs.realized_pnl:", repr(rs2.realized_pnl))
    print("delta total:", repr(res.total_pnl - res2.total_pnl))
    print("delta rs:", repr(rs.realized_pnl - rs2.realized_pnl))
    print()


def main():
    # STOP: coin[9] high 153 >= short_stop 152.598 -> rebound short STOPPED.
    coin_s = _base_coin()
    coin_s[9] = _c("s9", 108.0, 153.0, 100.0, 107.0)
    res, rs, res2, rs2 = _run(coin_s, _base_eth())
    dump("STOP (ETH OOR at exit idx 9)", res, rs, res2, rs2)

    # TARGET: coin[9] low 99.0 <= short_target 99.189 -> rebound short target hit.
    coin_t = _base_coin()
    coin_t[9] = _c("s9", 108.0, 115.0, 99.0, 107.0)
    res, rs, res2, rs2 = _run(coin_t, _base_eth())
    dump("TARGET (ETH OOR at exit idx 9)", res, rs, res2, rs2)


if __name__ == "__main__":
    main()