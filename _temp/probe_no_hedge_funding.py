"""Probe: funding reconciliation for no-hedge liquidation."""
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
        enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=1.0, funding_rate_pct_per_hour=0.01,
        min_daily_volume_usd=0.0, time_exit_max_bars=200,
        enable_liquidation_checks=True, liquidation_maint_margin_pct=5.0,
        liquidation_buffer_pct=1.0, liquidation_penalty_pct=0.5,
        gross_cap_pct=120.0, hedge_vol_lookback_hours=336,
        hedge_cap_multiplier=3.0, rebound_short_target_pct=9.0,
        rebound_short_stop_pct=40.0, rebound_short_time_exit_bars=48,
    )
    d.update(ov)
    return StrategyConfig(**d)


def _sig():
    return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                  stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                  timestamp="t5", size_shares=1000.0, signal_index=5)


def _scenario():
    n = 40
    coin = []
    cp = 100.0
    for i in range(n):
        cm = 1.015 if i % 2 == 0 else 0.985
        co, cc = cp, cp * cm
        ch, cl = max(co, cc) * 1.002, min(co, cc) * 0.998
        coin.append(_c(f"b{i}", co, ch, cl, cc))
        cp = cc
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
    coin[8] = _c("e8", 100.0, 101.0, 93.0, 99.0)
    return coin


coin = _scenario()
on = backtest_simple(coin, _sig(), config=_cfg(funding_rate_pct_per_hour=0.01),
                     risk_state=_CapCutRS(), capital=100000.0, eth_candles=None)
off = backtest_simple(coin, _sig(), config=_cfg(funding_rate_pct_per_hour=0.0),
                      risk_state=_CapCutRS(), capital=100000.0, eth_candles=None)
print("on.total_pnl:", repr(on.total_pnl))
print("off.total_pnl:", repr(off.total_pnl))
hours = on.bars_held
rate = 0.01
coin_cost = (on.entry_price * on.shares) * hours * (rate / 100.0)
expected_net = -coin_cost
actual_net = on.total_pnl - off.total_pnl
print("expected_net:", repr(expected_net))
print("actual_net:", repr(actual_net))
print("match:", abs(actual_net - expected_net) < 1e-6)