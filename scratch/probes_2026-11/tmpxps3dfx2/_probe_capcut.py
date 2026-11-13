"""Probe: cap-cut variant of long TIME_EXIT missing-ETH fallback."""
from src.backtest.engine import backtest_simple, _apply_funding_pnl
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal, compute_eth_hedge_size
from src.strategy.risk import DailyRiskState


def _c(ts, o, h, l, cl, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": cl, "volume": v}


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
    return coin, eth[:8]


def _cfg(rate=0.01, comm_min=1.0):
    return StrategyConfig(
        enable_eth_hedge=True, enable_rebound_short=False, entry_next_bar=True,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=comm_min, funding_rate_pct_per_hour=rate,
        min_daily_volume_usd=0.0, time_exit_max_bars=3,
        enable_liquidation_checks=True, liquidation_maint_margin_pct=5.0,
        liquidation_buffer_pct=1.0, liquidation_penalty_pct=0.5,
        gross_cap_pct=120.0, hedge_vol_lookback_hours=336,
    )


def _sig(shares=1000.0):
    return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                  stop_price=80.0, target_price=200.0, risk_per_share=20.0,
                  timestamp="t5", size_shares=shares, signal_index=5)


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


coin, eth = _scenario()
cfg = _cfg()
sig = _sig()
rs = _CapCutRS()
res = backtest_simple(coin, sig, config=cfg, risk_state=rs, capital=100000.0, eth_candles=eth)
print("cap-cut shares:", repr(res.shares))
print("entry_price:", repr(res.entry_price))
print("exit_price:", repr(res.exit_price))
print("hedge_size:", repr(res.hedge_size))
print("hedge_entry:", repr(res.hedge_entry))
print("hedge_exit:", repr(res.hedge_exit))
print("pnl:", repr(res.pnl))
print("hedge_pnl:", repr(res.hedge_pnl))
print("total_pnl:", repr(res.total_pnl))
print("max_live:", repr(res.max_live_coin_notional))
print("trades:", res.trades)