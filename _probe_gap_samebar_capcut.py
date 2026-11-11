"""Scratch probe: understand hedge_pnl_total vs rebound_hedge_pnl in rebound-short
same-bar stop-vs-target sequencing under cap_cut shares (600) + commission_min +
entry_next_bar + ETH hedge + funding. Not a handoff."""
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
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)     # long entry_next_bar
    coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)     # long target -> rebound short opens
    coin[9] = _c("b9", 110.0, 115.0, 109.0, 110.0)    # short holds
    coin[10] = _c("e10", 108.0, 160.0, 98.0, 120.0)   # short stop AND target breach -> stop wins
    eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
    eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
    eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)
    eth[10] = {"timestamp": "h10"}                      # missing close/open at exit idx
    return coin, eth


if __name__ == "__main__":
    coin, eth = _scenario()
    on = backtest_simple(coin, _sig(), config=_cfg(RATE), capital=100000.0, eth_candles=eth)
    off = backtest_simple(coin, _sig(), config=_cfg(0.0), capital=100000.0, eth_candles=eth)
    print("ON exit_reason:", on.exit_reason)
    print("ON exit_timestamp:", on.exit_timestamp, "bars_held:", on.bars_held)
    print("ON trades:", on.trades)
    print("ON entry_price:", repr(on.entry_price))
    print("ON exit_price:", repr(on.exit_price))
    print("ON shares:", repr(on.shares))
    print("ON max_live_coin_notional:", repr(on.max_live_coin_notional))
    print("ON hedge_side:", on.hedge_side, "hedge_size:", repr(on.hedge_size))
    print("ON hedge_entry:", repr(on.hedge_entry), "hedge_exit:", repr(on.hedge_exit))
    print("ON hedge_pnl:", repr(on.hedge_pnl))
    print("ON rebound_hedge_side:", on.rebound_hedge_side, "size:", repr(on.rebound_hedge_size))
    print("ON rebound_hedge_entry:", repr(on.rebound_hedge_entry), "exit:", repr(on.rebound_hedge_exit))
    print("ON rebound_hedge_pnl:", repr(on.rebound_hedge_pnl))
    print("ON rebound_short_pnl:", repr(on.rebound_short_pnl))
    print("ON pnl:", repr(on.pnl), "total_pnl:", repr(on.total_pnl))
    print("OFF total_pnl:", repr(off.total_pnl))
    print("delta:", repr(on.total_pnl - off.total_pnl))
    # expected funding delta: long 3h + short 3h + hedge 3h
    long_leg, short_leg = on.trades
    long_cost = _apply_funding_pnl(long_leg["entry"] * SHARES, 3, RATE, side="long")
    short_cost = _apply_funding_pnl(short_leg["entry"] * SHARES, 3, RATE, side="short")
    hedge_cost = _apply_funding_pnl(on.rebound_hedge_entry * on.rebound_hedge_size, 3, RATE, side="long")
    print("expected delta:", repr(-long_cost - short_cost - hedge_cost))
    print("long_cost:", repr(long_cost), "short_cost:", repr(short_cost), "hedge_cost:", repr(hedge_cost))