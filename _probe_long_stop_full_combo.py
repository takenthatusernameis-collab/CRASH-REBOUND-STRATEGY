"""Probe (2026-11-10T11:50Z): long-leg STOPPED with ETH hedge + commission_min +
entry_next_bar + equal-share cap-cut + hourly funding. NOT covered by existing
locks (liquidated + no-hedge liquidated are covered; stopped/time_exit with the
full combo are not). Prints exact engine outputs to hand-trace into a regression
lock. Synthetic fixtures only; non-evidence; hourly only; no look-ahead.
"""
from __future__ import annotations

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
        enable_rebound_short=True,
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
        rebound_short_target_pct=9.0,
        rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
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
        target_price=109.0,
        risk_per_share=20.0,
        timestamp="t5",
        size_shares=1000.0,
        signal_index=5,
    )


def _scenario():
    """Coin/ETH histories with nonzero realized-vol ratio => ETH hedge opens.
    entry_next_bar long fill at bar 6 (open 100). Long SAFETY STOP fires at bar 7:
    stop_px = 80 * (100.001/100) = 80.0008; bar 7 low 79.0 breaches. ETH hedge
    (short) opened at aligned entry bar idx 6, closed same stop bar. No rebound
    short opened (stopped buy never opens rebound short per spec)."""
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
    coin[7] = _c("e7", 100.0, 101.0, 79.0, 99.0)    # long safety stop breach
    eth[7] = _c("h7", 2050.0, 2100.0, 2000.0, 2070.0)  # hedge exit on stop bar
    return coin, eth


if __name__ == "__main__":
    coin, eth = _scenario()
    res = backtest_simple(coin, _sig(), config=_cfg(), risk_state=_CapCutRS(),
                          capital=100000.0, eth_candles=eth)
    print("exit_reason:", res.exit_reason)
    print("shares:", repr(res.shares))
    print("entry_price:", repr(res.entry_price))
    print("exit_price:", repr(res.exit_price))
    print("bars_held:", res.bars_held)
    print("hedge_side:", res.hedge_side)
    print("hedge_size:", repr(res.hedge_size))
    print("hedge_entry:", repr(res.hedge_entry))
    print("hedge_exit:", repr(res.hedge_exit))
    print("pnl:", repr(res.pnl))
    print("hedge_pnl:", repr(res.hedge_pnl))
    print("total_pnl:", repr(res.total_pnl))
    print("max_live_coin_notional:", repr(res.max_live_coin_notional))
    print("rebound_short_pnl:", repr(res.rebound_short_pnl))
    print("rebound_hedge_pnl:", repr(res.rebound_hedge_pnl))
    print("trades:", res.trades)