"""Scratch: precise traced values for same-bar stop-vs-target sequencing lock."""
from src.backtest.engine import backtest_simple, _apply_funding_pnl
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal, compute_eth_hedge_size

RATE = 0.01
SHARES = 600.0


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _cfg(rate=RATE):
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


def _sig(shares=SHARES):
    return Signal(symbol="T", side="long", reason="t",
                  entry_price=100.0, stop_price=80.0, target_price=109.0,
                  risk_per_share=20.0, timestamp="t5",
                  size_shares=shares, signal_index=5)


def _scenario():
    n = 30
    coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
    coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)
    coin[9] = _c("b9", 110.0, 115.0, 109.0, 110.0)
    coin[10] = _c("e10", 108.0, 160.0, 98.0, 120.0)
    eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
    eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
    eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)
    eth[10] = {"timestamp": "h10"}
    return coin, eth


if __name__ == "__main__":
    coin, eth = _scenario()
    on = backtest_simple(coin, _sig(), config=_cfg(RATE), capital=100000.0, eth_candles=eth)
    off = backtest_simple(coin, _sig(), config=_cfg(0.0), capital=100000.0, eth_candles=eth)
    long_leg, short_leg = on.trades
    long_cost = _apply_funding_pnl(long_leg["entry"] * SHARES, 3, RATE, side="long")
    short_cost = _apply_funding_pnl(short_leg["entry"] * SHARES, 3, RATE, side="short")
    hedge_cost = _apply_funding_pnl(on.rebound_hedge_entry * on.rebound_hedge_size, 3, RATE, side="long")
    print("long_leg entry:", repr(long_leg["entry"]))
    print("long_leg exit:", repr(long_leg["exit"]))
    print("long_leg pnl:", repr(long_leg["pnl"]))
    print("short_leg entry:", repr(short_leg["entry"]))
    print("short_leg exit:", repr(short_leg["exit"]))
    print("short_leg pnl:", repr(short_leg["pnl"]))
    print("rebound_hedge_size:", repr(on.rebound_hedge_size))
    print("rebound_hedge_entry:", repr(on.rebound_hedge_entry))
    print("rebound_hedge_exit:", repr(on.rebound_hedge_exit))
    print("rebound_hedge_pnl:", repr(on.rebound_hedge_pnl))
    print("hedge_pnl:", repr(on.hedge_pnl))
    print("rebound_short_pnl:", repr(on.rebound_short_pnl))
    print("pnl:", repr(on.pnl))
    print("total_pnl:", repr(on.total_pnl))
    print("max_live_coin_notional:", repr(on.max_live_coin_notional))
    print("bars_held:", on.bars_held, "exit_timestamp:", on.exit_timestamp)
    print("off short_leg pnl:", repr(off.trades[1]["pnl"]))
    print("off rebound_hedge_pnl:", repr(off.rebound_hedge_pnl))
    print("off total_pnl:", repr(off.total_pnl))
    print("long_cost:", repr(long_cost))
    print("short_cost:", repr(short_cost))
    print("hedge_cost:", repr(hedge_cost))
    print("expected delta:", repr(-long_cost - short_cost - hedge_cost))
    print("actual delta:", repr(on.total_pnl - off.total_pnl))
    # risk_state
    from src.strategy.risk import DailyRiskState
    rs = DailyRiskState()
    r = backtest_simple(coin, _sig(), config=_cfg(RATE), capital=100000.0, eth_candles=eth, risk_state=rs)
    print("rs open_positions:", rs.open_positions, "gross_exposure:", repr(rs.gross_exposure))
    print("rs open_position_notionals:", rs.open_position_notionals)
    print("rs realized_pnl:", repr(rs.realized_pnl))
    print("rs realized vs short+hedge:", repr(short_leg["pnl"] + on.rebound_hedge_pnl))