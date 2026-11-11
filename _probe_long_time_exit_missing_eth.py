"""Probe: long TIME_EXIT with ETH hedge missing at exit index (fallback raw)."""
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


def _cfg(funding_rate_pct_per_hour=0.01):
    return StrategyConfig(
        enable_eth_hedge=True, enable_rebound_short=False, entry_next_bar=True,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=1.0, funding_rate_pct_per_hour=funding_rate_pct_per_hour,
        min_daily_volume_usd=0.0, time_exit_max_bars=3,
        enable_liquidation_checks=True, liquidation_maint_margin_pct=5.0,
        liquidation_buffer_pct=1.0, liquidation_penalty_pct=0.5,
        gross_cap_pct=120.0, hedge_vol_lookback_hours=336,
    )


def _sig():
    return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                  stop_price=80.0, target_price=200.0, risk_per_share=20.0,
                  timestamp="t5", size_shares=1000.0, signal_index=5)


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
    coin[8] = _c("e8", 100.0, 101.0, 99.0, 100.5)
    # eth[8] INTENTIONALLY MISSING -> truncate to 8 bars (0..7)
    return coin, eth[:8]


if __name__ == "__main__":
    coin, eth = _scenario()
    print("len(coin)=", len(coin), "len(eth)=", len(eth))
    rs = _CapCutRS()
    res = backtest_simple(coin, _sig(), config=_cfg(), risk_state=rs,
                          capital=100000.0, eth_candles=eth)
    print("exit_reason:", res.exit_reason)
    print("bars_held:", res.bars_held)
    print("entry_price:", repr(res.entry_price))
    print("exit_price:", repr(res.exit_price))
    print("shares:", repr(res.shares))
    print("hedge_side:", res.hedge_side)
    print("hedge_size:", repr(res.hedge_size))
    print("hedge_entry:", repr(res.hedge_entry))
    print("hedge_exit:", repr(res.hedge_exit))
    print("pnl:", repr(res.pnl))
    print("hedge_pnl:", repr(res.hedge_pnl))
    print("total_pnl:", repr(res.total_pnl))
    print("max_live_coin_notional:", repr(res.max_live_coin_notional))
    print("trades:", res.trades)
    print("entry_timestamp:", res.entry_timestamp)
    print("exit_timestamp:", res.exit_timestamp)

    # funding-off baseline
    rs2 = _CapCutRS()
    res_off = backtest_simple(coin, _sig(), config=_cfg(0.0), risk_state=rs2,
                              capital=100000.0, eth_candles=eth)
    print("--- off ---")
    print("total_pnl off:", repr(res_off.total_pnl))
    print("delta:", repr(res.total_pnl - res_off.total_pnl))