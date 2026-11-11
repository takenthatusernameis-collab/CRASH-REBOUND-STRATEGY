"""Probe (2026-11-11): long TIME_EXIT with ETH hedge present at entry but ETH bar
missing at exit index -> engine fallback to hedge_info['entry'] for hedge
exit-price accounting, under cap_cut + commission_min + entry_next_bar + funding.
Print exact engine outputs so the regression lock can hardcode traced values.
"""
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
        time_exit_max_bars=3,
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
        symbol="T", side="long", reason="t",
        entry_price=100.0, stop_price=80.0, target_price=200.0,
        risk_per_share=20.0, timestamp="t5", size_shares=1000.0, signal_index=5,
    )


def _scenario(eth_exit_mode):
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
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
    eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
    coin[7] = _c("e7", 100.0, 101.0, 99.0, 100.2)
    eth[7] = _c("h7", 2010.0, 2020.0, 2000.0, 2015.0)
    coin[8] = _c("e8", 100.0, 101.0, 99.0, 100.5)
    if eth_exit_mode == "missing_fields":
        eth[8] = {"timestamp": "h8"}  # present but no close/open
    elif eth_exit_mode == "truncated":
        eth = eth[:8]  # idx 8 out of range
    else:
        eth[8] = _c("h8", 2030.0, 2040.0, 2020.0, 2035.0)
    return coin, eth


for mode in ["present", "missing_fields", "truncated"]:
    coin, eth = _scenario(mode)
    on = backtest_simple(coin, _sig(), config=_cfg(funding_rate_pct_per_hour=0.01),
                         risk_state=_CapCutRS(), capital=100000.0, eth_candles=eth)
    off = backtest_simple(coin, _sig(), config=_cfg(funding_rate_pct_per_hour=0.0),
                          risk_state=_CapCutRS(), capital=100000.0, eth_candles=eth)
    print(f"=== mode={mode} ===")
    print(f"  exit_reason={on.exit_reason} bars_held={on.bars_held}")
    print(f"  shares={on.shares!r}")
    print(f"  entry_price={on.entry_price!r} exit_price={on.exit_price!r}")
    print(f"  hedge_side={on.hedge_side} hedge_size={on.hedge_size!r}")
    print(f"  hedge_entry={on.hedge_entry!r} hedge_exit={on.hedge_exit!r}")
    print(f"  pnl={on.pnl!r} hedge_pnl={on.hedge_pnl!r} total_pnl={on.total_pnl!r}")
    print(f"  max_live_coin_notional={on.max_live_coin_notional!r}")
    print(f"  trades={on.trades}")
    delta = on.total_pnl - off.total_pnl
    print(f"  funding delta={delta!r}  off.total_pnl={off.total_pnl!r}")
    print()