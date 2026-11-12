"""Scratch probe: trace risk_state apply_trade calls for both-hedges stop."""
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.strategy.risk import DailyRiskState


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _ts(i):
    return f"2025-01-01T{i:02d}:00:00"


def _cfg(rate=0.01):
    return StrategyConfig(
        enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=1.0, funding_rate_pct_per_hour=rate,
        min_daily_volume_usd=0.0, time_exit_max_bars=1000,
        enable_liquidation_checks=False, gross_cap_pct=120.0,
        rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
    )


def _sig(shares=10.0):
    return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                  stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                  timestamp="t5", size_shares=shares, signal_index=5)


def _coin():
    n = 80
    coin = []
    for i in range(6):
        cl = 100.5 if i % 2 == 0 else 99.5
        coin.append(_c(_ts(i), 100.0, 101.0, 99.0, cl))
    coin.append(_c(_ts(6), 100.0, 100.5, 99.5, 100.0))
    coin.append(_c(_ts(7), 108.0, 109.0, 107.0, 107.0))
    coin.append(_c(_ts(8), 108.0, 110.0, 107.0, 109.0))
    for i in range(9, n):
        coin.append(_c(_ts(i), 108.0, 115.0, 100.0, 107.0))
    coin[55] = _c(_ts(55), 108.0, 152.598, 100.5, 107.0)
    return coin


def _eth_aligned():
    n = 80
    return [_c(_ts(i), 2000.0 + i * 5, 2020.0 + i * 5, 1980.0 + i * 5, 2005.0 + i * 5)
            for i in range(n)]


class TraceRS(DailyRiskState):
    def apply_trade(self, date, pnl, opened, closed, notional=0.0):
        print(f"  apply_trade date={date} pnl={pnl!r} opened={opened} closed={closed} notional={notional!r}")
        super().apply_trade(date, pnl, opened, closed, notional)


rs = TraceRS()
res = backtest_simple(_coin(), _sig(10.0), config=_cfg(0.01),
                      risk_state=rs, capital=100000.0, eth_candles=_eth_aligned())
print("RESULT:", res.total_pnl, "rs.realized=", rs.realized_pnl)
print("rs.open_positions=", rs.open_positions, "gross=", rs.gross_exposure, "notionals=", rs.open_position_notionals)