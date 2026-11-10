"""Temporary probe: long-leg TIME-EXIT (time_exit_max_bars hit) with short ETH hedge.
Compute exact engine values to hand-trace a regression lock."""
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _cfg(**ov):
    d = dict(
        enable_eth_hedge=True,
        enable_rebound_short=True,
        entry_next_bar=False,
        avoid_downtrend=False,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
        funding_rate_pct_per_hour=0.01,
        min_daily_volume_usd=0.0,
        time_exit_max_bars=10,
        enable_liquidation_checks=True,
        liquidation_maint_margin_pct=5.0,
        liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5,
        gross_cap_pct=120.0,
        hedge_vol_lookback_hours=336,
        rebound_short_target_pct=9.0,
        rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
    )
    d.update(ov)
    return StrategyConfig(**d)


def _sig():
    return Signal(
        symbol="T", side="long", reason="t",
        entry_price=100.0, stop_price=80.0, target_price=109.0,
        risk_per_share=20.0, timestamp="t5", size_shares=1000.0, signal_index=5,
    )


def _scenario():
    n = 40
    coin, eth = [], []
    cp, ep = 100.0, 2000.0
    for i in range(n):
        cm = 1.015 if i % 2 == 0 else 0.985
        em = 1.008 if i % 2 == 0 else 0.992
        co, cc = cp, cp * cm
        ch, cl = max(co, cc) * 1.002, min(co, cc) * 0.998
        eo, ec = ep, ep * em
        eh, el = max(eo, ec) * 1.001, min(eo, ec) * 0.999
        coin.append(_c(f"b{i}", co, ch, cl, cc))
        eth.append(_c(f"h{i}", eo, eh, el, ec))
        cp, ep = cc, ec
    return coin, eth


def main():
    coin, eth = _scenario()
    res = backtest_simple(coin, _sig(), config=_cfg(), capital=100000.0, eth_candles=eth)
    print("exit_reason:", res.exit_reason)
    print("shares:", res.shares)
    print("entry_price:", res.entry_price)
    print("exit_price:", res.exit_price)
    print("bars_held:", res.bars_held)
    print("hedge_side:", res.hedge_side)
    print("hedge_size:", res.hedge_size)
    print("hedge_entry:", res.hedge_entry)
    print("hedge_exit:", res.hedge_exit)
    print("pnl:", res.pnl)
    print("hedge_pnl:", res.hedge_pnl)
    print("total_pnl:", res.total_pnl)
    print("max_live_coin_notional:", res.max_live_coin_notional)
    print("trades:", res.trades)

    on = backtest_simple(coin, _sig(), config=_cfg(funding_rate_pct_per_hour=0.01), capital=100000.0, eth_candles=eth)
    off = backtest_simple(coin, _sig(), config=_cfg(funding_rate_pct_per_hour=0.0), capital=100000.0, eth_candles=eth)
    print("\nFunding delta (on-off):", on.total_pnl - off.total_pnl)
    hours = on.bars_held
    rate = 0.01
    coin_cost = (on.entry_price * on.shares) * hours * (rate / 100.0)
    hedge_benefit = (on.hedge_entry * on.hedge_size) * hours * (rate / 100.0)
    print("hours:", hours, "expected coin_cost:", coin_cost, "hedge_benefit:", hedge_benefit, "net:", -coin_cost + hedge_benefit)
    print("reconcile:", abs((on.total_pnl - off.total_pnl) - (-coin_cost + hedge_benefit)) < 1e-6)


if __name__ == "__main__":
    main()