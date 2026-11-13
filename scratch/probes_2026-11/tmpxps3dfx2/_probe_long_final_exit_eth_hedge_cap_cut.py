"""Probe for the uncovered long-final-exit ETH-hedge cell (2026-11-10T18:0xZ).

Deterministic scenario: long-leg final-exit (end of coin series, no liq/stop/
target/time-exit) with ETH hedge, equal-share cap-cut, commission_min,
entry_next_bar, nonzero hourly funding. Hand-traced expected values below.
"""
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


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
        time_exit_max_bars=1000,
        enable_liquidation_checks=False,
        gross_cap_pct=120.0,
        hedge_vol_lookback_hours=336,
    )
    d.update(ov)
    return StrategyConfig(**d)


def _sig():
    return Signal(
        symbol="T", side="long", reason="t", entry_price=100.0,
        stop_price=80.0, target_price=200.0, risk_per_share=20.0,
        timestamp="t5", size_shares=1000.0, signal_index=5,
    )


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
    # entry_next_bar fill at bar 6 (open 100). No liq/stop/target/time-exit ->
    # final-exit at last bar (idx 39).
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
    eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
    coin[39] = _c("e39", 100.0, 105.0, 95.0, 103.0)
    eth[39] = _c("h39", 2000.0, 2060.0, 1940.0, 2025.0)
    return coin, eth


def main():
    coin, eth = _scenario()
    res = backtest_simple(coin, _sig(), config=_cfg(), risk_state=_CapCutRS(),
                          capital=100000.0, eth_candles=eth)
    print("exit_reason:", res.exit_reason)
    print("bars_held:", res.bars_held)
    print("shares:", repr(res.shares))
    print("entry_price:", repr(res.entry_price))
    print("exit_price:", repr(res.exit_price))
    print("hedge_side:", res.hedge_side, "size:", repr(res.hedge_size))
    print("hedge_entry:", repr(res.hedge_entry), "hedge_exit:", repr(res.hedge_exit))
    print("pnl:", repr(res.pnl))
    print("hedge_pnl:", repr(res.hedge_pnl))
    print("total_pnl:", repr(res.total_pnl))
    print("max_live_coin_notional:", repr(res.max_live_coin_notional))
    print("trades:", res.trades)
    # funding-on vs funding-off reconciliation
    on = backtest_simple(coin, _sig(), config=_cfg(funding_rate_pct_per_hour=0.01),
                         risk_state=_CapCutRS(), capital=100000.0, eth_candles=eth)
    off = backtest_simple(coin, _sig(), config=_cfg(funding_rate_pct_per_hour=0.0),
                          risk_state=_CapCutRS(), capital=100000.0, eth_candles=eth)
    print("funding delta total_pnl:", repr(on.total_pnl - off.total_pnl))
    print("funding delta pnl:", repr(on.pnl - off.pnl))
    print("funding delta hedge_pnl:", repr(on.hedge_pnl - off.hedge_pnl))


if __name__ == "__main__":
    main()