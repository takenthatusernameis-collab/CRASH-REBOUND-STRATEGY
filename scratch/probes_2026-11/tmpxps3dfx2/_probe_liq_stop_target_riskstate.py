"""PROBE (2026-11-11T02:10:00Z) — RiskState settlement under uncovered cell."""
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.strategy.risk import RiskState


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
        rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
    )
    d.update(ov)
    return StrategyConfig(**d)


def _sig():
    return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                  stop_price=95.0, target_price=109.0, risk_per_share=20.0,
                  timestamp="t5", size_shares=1000.0, signal_index=5)


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
        cp, ec_p = cc, ec
        ep = ec_p
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
    eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
    coin[8] = _c("e8", 100.0, 109.5, 93.0, 99.0)
    eth[8] = _c("h8", 2050.0, 2100.0, 2000.0, 2070.0)
    return coin, eth


if __name__ == "__main__":
    coin, eth = _scenario()
    rs = RiskState()
    rs.date = "2025-01-01T05:00:00"
    res = backtest_simple(coin, _sig(), config=_cfg(), risk_state=rs,
                          capital=100000.0, eth_candles=eth)
    print("exit_reason:", res.exit_reason)
    print("rs.open_positions:", rs.open_positions)
    print("rs.gross_exposure:", rs.gross_exposure)
    print("rs.open_position_notionals:", rs.open_position_notionals)
    print("rs.realized_pnl:", repr(rs.realized_pnl))
    print("res.total_pnl:", repr(res.total_pnl))
    print("res.max_live_coin_notional:", repr(res.max_live_coin_notional))
    print("rs.gross_exposure == 0:", rs.gross_exposure == 0.0)
    print("rs.open_positions == 0:", rs.open_positions == 0)
    print("rs.realized_pnl == res.total_pnl:", rs.realized_pnl == res.total_pnl)