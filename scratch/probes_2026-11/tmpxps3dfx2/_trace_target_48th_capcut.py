"""Trace script: compute exact expected values for the PRIMARY TARGET CELL
(rebound-short TARGET on exact 48th held bar, cap_cut-implied shares,
commission_min, entry_next_bar, aligned ETH and ETH-absent-at-exit).

This is a scratch trace (not a test, not a handoff). Run with:
    PYTHONPATH=. python3 _trace_target_48th_capcut.py
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
        enable_liquidation_checks=True,
        liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5, gross_cap_pct=120.0,
        rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
    )


def _coin():
    n = 80
    coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)      # long entry_next_bar fill
    coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)      # long target -> rebound short opens idx8
    for i in range(9, n):
        coin[i] = _c(f"s{i}", 108.0, 115.0, 100.0, 107.0)
    # 48th held bar: sidx - 8 + 1 == 48 => sidx=55. low hits -9% target.
    coin[55] = _c("b55", 108.0, 115.0, 99.0, 107.0)
    return coin


def _eth_aligned():
    n = 80
    eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
    eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
    eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)  # rebound hedge entry idx8
    for i in range(9, n):
        eth[i] = _c(f"eh{i}", 2030.0, 2050.0, 2020.0, 2040.0)
    eth[55] = _c("eh55", 2030.0, 2055.0, 2020.0, 2045.0)  # hedge exit on 48th bar
    return eth


def _eth_absent_at_exit():
    eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(10)]
    eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
    eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)
    return eth


def _sig(shares=600.0):
    return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                  stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                  timestamp="t5", size_shares=shares, signal_index=5)


def run(label, eth, funding):
    coin = _coin()
    rs = DailyRiskState()
    res = backtest_simple(coin, _sig(600.0), config=_cfg(funding),
                          risk_state=rs, capital=100000.0, eth_candles=eth)
    print(f"\n=== {label} (funding={funding}) ===")
    print(f"exit_reason={res.exit_reason} exit_ts={res.exit_timestamp} bars_held={res.bars_held}")
    print(f"reasons={[t['reason'] for t in res.trades]}")
    for t in res.trades:
        print(f"  {t['side']:5s} entry={t['entry']!r} exit={t['exit']!r} pnl={t['pnl']!r}")
    print(f"long leg pnl (trades[0])={res.trades[0]['pnl']!r}")
    print(f"short leg pnl (trades[1])={res.trades[1]['pnl']!r}")
    print(f"rebound_hedge_side={res.rebound_hedge_side}")
    print(f"rebound_hedge_size={res.rebound_hedge_size!r}")
    print(f"rebound_hedge_entry={res.rebound_hedge_entry!r}")
    print(f"rebound_hedge_exit={res.rebound_hedge_exit!r}")
    print(f"rebound_hedge_pnl={res.rebound_hedge_pnl!r}")
    print(f"hedge_pnl={res.hedge_pnl!r}")
    print(f"max_live_coin_notional={res.max_live_coin_notional!r}")
    coin_total = sum(t["pnl"] for t in res.trades)
    print(f"coin_total={coin_total!r}")
    print(f"total_pnl={res.total_pnl!r}")
    print(f"total_pnl == coin_total + hedge_pnl: {res.total_pnl == coin_total + res.hedge_pnl}")
    print(f"risk_state: realized={rs.realized_pnl!r} open={rs.open_positions} gross={rs.gross_exposure!r} notionals={rs.open_position_notionals}")
    return res, rs


if __name__ == "__main__":
    run("aligned ETH", _eth_aligned(), 0.01)
    run("aligned ETH funding=0", _eth_aligned(), 0.0)
    run("ETH absent at exit", _eth_absent_at_exit(), 0.01)
    run("ETH absent at exit funding=0", _eth_absent_at_exit(), 0.0)