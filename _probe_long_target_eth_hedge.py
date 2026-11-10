"""Probe: long TARGET exit with ETH hedge + cap-cut + commission_min + entry_next_bar + funding."""
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


class _CapCutRS:
    open_positions = 1
    gross_exposure = 80000.0
    open_position_notionals = [80000.0]

    def check_position(self, config, capital, shares, entry_price):
        from types import SimpleNamespace
        return SimpleNamespace(allowed=True, size_shares=shares)

    def apply_cap_cuts(self, capital, config, open_notional=None):
        capv = capital * config.gross_cap_pct / 100.0
        n = len(open_notional or [])
        return [capv / n] * n if n else []

    def apply_trade(self, *a, **k):
        pass


def _cfg(**ov):
    d = dict(
        enable_eth_hedge=True,
        enable_rebound_short=False,
        entry_next_bar=True,
        avoid_downtrend=False,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=1.0,
        funding_rate_pct_per_hour=0.01,
        min_daily_volume_usd=0.0,
        time_exit_max_bars=200,
        enable_liquidation_checks=True,
        liquidation_maint_margin_pct=5.0,
        liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5,
        gross_cap_pct=120.0,
        hedge_vol_lookback_hours=336,
    )
    d.update(ov)
    return StrategyConfig(**d)


def _sig():
    return Signal(
        symbol="T",
        side="long",
        reason="t",
        entry_price=100.0,
        stop_price=80.0,
        target_price=100.5,  # hit at bar 8 (high 101.0 >= 100.501)
        risk_per_share=20.0,
        timestamp="t5",
        size_shares=1000.0,
        signal_index=5,
    )


def _scenario():
    n = 40
    coin = []
    eth = []
    cp = 100.0
    ep = 2000.0
    for i in range(n):
        cm = 1.015 if i % 2 == 0 else 0.985
        em = 1.008 if i % 2 == 0 else 0.992
        co, cc = cp, cp * cm
        ch, cl = max(co, cc) * 1.002, min(co, cc) * 0.998
        eo, ec = ep, ep * em
        eh, el = max(eo, ec) * 1.001, min(eo, ec) * 0.999
        coin.append(_c(f"b{i}", co, ch, cl, cc))
        eth.append(_c(f"h{i}", eo, eh, el, ec))
        cp = cc
        ep = ec
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
    eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
    coin[7] = _c("e7", 100.0, 101.0, 99.0, 100.2)
    eth[7] = _c("h7", 2010.0, 2020.0, 2000.0, 2015.0)
    coin[8] = _c("e8", 100.0, 101.0, 99.0, 100.5)  # target hit (high 101 >= 100.501)
    eth[8] = _c("h8", 2030.0, 2040.0, 2020.0, 2035.0)  # hedge exit
    return coin, eth


if __name__ == "__main__":
    coin, eth = _scenario()
    rs = _CapCutRS()
    res = backtest_simple(coin, _sig(), config=_cfg(), risk_state=rs, capital=100000.0, eth_candles=eth)
    print("exit_reason:", res.exit_reason)
    print("bars_held:", res.bars_held)
    print("shares:", repr(res.shares))
    print("entry_price:", repr(res.entry_price))
    print("exit_price:", repr(res.exit_price))
    print("pnl:", repr(res.pnl))
    print("hedge_side:", res.hedge_side)
    print("hedge_size:", repr(res.hedge_size))
    print("hedge_entry:", repr(res.hedge_entry))
    print("hedge_exit:", repr(res.hedge_exit))
    print("hedge_pnl:", repr(res.hedge_pnl))
    print("total_pnl:", repr(res.total_pnl))
    print("max_live_coin_notional:", repr(res.max_live_coin_notional))
    print("trades:", res.trades)
    print("rebound_short_pnl:", res.rebound_short_pnl)
    print("exit_timestamp:", res.exit_timestamp)

    # funding reconciliation
    on = res
    off = backtest_simple(coin, _sig(), config=_cfg(funding_rate_pct_per_hour=0.0), risk_state=_CapCutRS(), capital=100000.0, eth_candles=eth)
    hours = on.bars_held
    rate = 0.01
    coin_cost = (on.entry_price * on.shares) * hours * (rate / 100.0)
    hedge_funding = (on.hedge_entry * on.hedge_size) * hours * (rate / 100.0)
    print("coin_cost:", coin_cost, "hedge_funding:", hedge_funding)
    print("funding net actual:", on.total_pnl - off.total_pnl, "expected:", -coin_cost + hedge_funding)
    print("off total_pnl:", off.total_pnl)