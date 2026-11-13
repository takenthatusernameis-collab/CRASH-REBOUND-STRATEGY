"""Precise trace for long TIME_EXIT missing-ETH fallback test."""
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


coin, eth = _scenario()
cfg = _cfg()
sig = _sig()
start_idx = sig.signal_index + 1
coin_notional_raw = 100.0 * 1000.0
hedge_value = compute_eth_hedge_size(coin[:start_idx+1], eth[:start_idx+1], 100001.0, cfg)
print("hedge_value:", repr(hedge_value))
hedge_shares = hedge_value / 2000.0
print("hedge_shares:", repr(hedge_shares))
hedge_comm_ps = max(0.0, 1.0 / hedge_shares)
print("hedge_comm_ps:", repr(hedge_comm_ps))
hedge_entry_px = 2000.0 - 2000.0*0.0 - hedge_comm_ps
print("hedge_entry_px:", repr(hedge_entry_px))
# raw fallback: eth_exit = hedge_entry_px (executed), buy-side close
hedge_exit_px = hedge_entry_px + hedge_entry_px*0.0 + hedge_comm_ps
print("hedge_exit_px:", repr(hedge_exit_px))
hedge_gross = (hedge_entry_px - hedge_exit_px) * hedge_shares
print("hedge_gross:", repr(hedge_gross))
hedge_notional = hedge_entry_px * hedge_shares
print("hedge_notional:", repr(hedge_notional))
hedge_funding = _apply_funding_pnl(hedge_notional, 3, 0.01, "short")
print("hedge_funding:", repr(hedge_funding))
hedge_pnl = hedge_gross - hedge_funding
print("hedge_pnl:", repr(hedge_pnl))
coin_gross = (100.499 - 100.001) * 1000.0
coin_funding = _apply_funding_pnl(100001.0, 3, 0.01, "long")
print("coin_gross:", repr(coin_gross), "coin_funding:", repr(coin_funding))
coin_pnl = coin_gross - coin_funding
print("coin_pnl:", repr(coin_pnl))
print("total_pnl:", repr(coin_pnl + hedge_pnl))
print("max_live:", repr(100001.0))
rs = DailyRiskState()
res = backtest_simple(coin, sig, config=cfg, risk_state=rs, capital=100000.0, eth_candles=eth)
print("engine hedge_pnl:", repr(res.hedge_pnl))
print("engine total_pnl:", repr(res.total_pnl))
print("engine pnl:", repr(res.pnl))
print("engine hedge_exit:", repr(res.hedge_exit))
print("engine hedge_entry:", repr(res.hedge_entry))
print("engine hedge_size:", repr(res.hedge_size))
print("engine realized:", repr(rs.realized_pnl))