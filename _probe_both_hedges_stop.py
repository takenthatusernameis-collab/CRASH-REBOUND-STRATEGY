"""Scratch probe (2026-11-12): BOTH-hedges + rebound short exits via STOP under
cap_cut + commission_min + entry_next_bar. Computes exact engine values for the
regression test (red->green). NOT a handoff.
"""
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
        min_daily_volume_usd=0.0, time_exit_max_bars=1000,
        enable_liquidation_checks=False, gross_cap_pct=120.0,
        rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
    )


def _sig(shares=10.0):
    return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                  stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                  timestamp="t5", size_shares=shares, signal_index=5)


def _ts(i):
    return f"2025-01-01T{i:02d}:00:00"


def _coin():
    n = 80
    # bars 0..5: varying closes for nonzero realized vol (long-hedge sizing window COIN[:7])
    coin = []
    for i in range(6):
        cl = 100.5 if i % 2 == 0 else 99.5
        coin.append(_c(_ts(i), 100.0, 101.0, 99.0, cl))
    # bar 6: long entry (entry_next_bar from signal_index=5)
    coin.append(_c(_ts(6), 100.0, 100.5, 99.5, 100.0))
    # bar 7: no target yet (high 109 < target_px ~109.109)
    coin.append(_c(_ts(7), 108.0, 109.0, 107.0, 107.0))
    # bar 8: long +9% target hit -> rebound short opens here (short_start_idx=8)
    coin.append(_c(_ts(8), 108.0, 110.0, 107.0, 109.0))
    for i in range(9, n):
        coin.append(_c(_ts(i), 108.0, 115.0, 100.0, 107.0))
    # 48th held bar (55-8+1=48): +40% stop fires, -9% target NOT hit (low 100.5 > 99.107)
    coin[55] = _c(_ts(55), 108.0, 152.598, 100.5, 107.0)
    return coin


def _eth_aligned():
    n = 80
    return [_c(_ts(i), 2000.0 + i * 5, 2020.0 + i * 5, 1980.0 + i * 5, 2005.0 + i * 5)
            for i in range(n)]


def _eth_absent_at_exit():
    return [_c(_ts(i), 2000.0 + i * 5, 2020.0 + i * 5, 1980.0 + i * 5, 2005.0 + i * 5)
            for i in range(10)]


def probe(label, coin, eth, rate):
    rs = DailyRiskState()
    res = backtest_simple(coin, _sig(10.0), config=_cfg(rate),
                          risk_state=rs, capital=100000.0, eth_candles=eth)
    print(f"=== {label} (rate={rate}) ===")
    print(f"exit_reason={res.exit_reason} exit_ts={res.exit_timestamp} bars_held={res.bars_held}")
    print(f"entry_px={res.entry_price!r} exit_px={res.exit_price!r} shares={res.shares!r}")
    print(f"max_live_coin_notional={res.max_live_coin_notional!r}")
    print(f"hedge_side={res.hedge_side} hedge_size={res.hedge_size!r} "
          f"hedge_entry={res.hedge_entry!r} hedge_exit={res.hedge_exit!r}")
    print(f"rebound_hedge_side={res.rebound_hedge_side} rebound_hedge_size={res.rebound_hedge_size!r} "
          f"rebound_hedge_entry={res.rebound_hedge_entry!r} rebound_hedge_exit={res.rebound_hedge_exit!r}")
    print(f"pnl={res.pnl!r} hedge_pnl={res.hedge_pnl!r} rebound_short_pnl={res.rebound_short_pnl!r} "
          f"rebound_hedge_pnl={res.rebound_hedge_pnl!r} total_pnl={res.total_pnl!r}")
    print(f"trades={[(t['side'], t['reason'], t['entry'], t['exit'], t['pnl']) for t in res.trades]}")
    print(f"risk_state: realized={rs.realized_pnl!r} open={rs.open_positions} "
          f"gross={rs.gross_exposure!r} notionals={rs.open_position_notionals}")
    print()


for label, eth in [("aligned", _eth_aligned()), ("absent", _eth_absent_at_exit())]:
    probe(label, _coin(), eth, 0.01)
    probe(label, _coin(), eth, 0.0)