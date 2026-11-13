"""Verify stop repro: stop_px=95, liquidation checks disabled, bar[8] low=93.0."""
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.strategy.risk import RiskState

ENTRY_PX = 100.0
SHARES = 1.0
RATE = 0.01
SIGNAL_IDX = 5


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _coin_base(n):
    return [_c(f"2025-01-01T{i % 24:02d}:00:00", 100 + (i % 5) * 0.2, 101.8, 98.2, 100 + (i % 5) * 0.2) for i in range(n)]


def _eth_var(n):
    return [_c(f"2025-01-01T{i % 24:02d}:00:00", 2000 + i % 7 * 3, 2008 + i % 7 * 3, 1992 + i % 7 * 3, 2000 + i % 7 * 3) for i in range(n)]


def _sig_stop():
    return Signal(symbol="T", side="long", reason="t", entry_price=ENTRY_PX, stop_price=95.0,
                  target_price=150.0, risk_per_share=1.0, timestamp="2025-01-01T05:00:00",
                  size_shares=SHARES, signal_index=SIGNAL_IDX)


def _cfg_stop(**kw):
    d = dict(
        enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=False,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=0.0, funding_rate_pct_per_hour=RATE, min_daily_volume_usd=0.0,
        time_exit_max_bars=200, enable_liquidation_checks=False,
        liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5,
    )
    d.update(kw)
    return StrategyConfig(**d)


def run_stop():
    candles = _coin_base(40)
    candles[8] = _c(f"2025-01-01T08:00:00", 96.0, 96.5, 93.0, 93.5)
    eth = _eth_var(40)
    rs = RiskState(); rs.date = "2025-01-01T05:00:00"
    res = backtest_simple(candles, _sig_stop(), config=_cfg_stop(funding_rate_pct_per_hour=RATE), risk_state=rs, eth_candles=eth)
    print(f"stop       exit={res.exit_reason} coin={res.pnl:.4f} hedge={res.hedge_pnl:.4f} total_pnl={res.total_pnl:.4f} realized_pnl={rs.realized_pnl:.4f} match={rs.realized_pnl == res.total_pnl}")
    return rs.realized_pnl == res.total_pnl


def run_stop_f0():
    candles = _coin_base(40)
    candles[8] = _c(f"2025-01-01T08:00:00", 96.0, 96.5, 93.0, 93.5)
    eth = _eth_var(40)
    rs = RiskState(); rs.date = "2025-01-01T05:00:00"
    res = backtest_simple(candles, _sig_stop(), config=_cfg_stop(funding_rate_pct_per_hour=0.0), risk_state=rs, eth_candles=eth)
    print(f"stop(f=0)  exit={res.exit_reason} coin={res.pnl:.4f} hedge={res.hedge_pnl:.4f} total_pnl={res.total_pnl:.4f} realized_pnl={rs.realized_pnl:.4f} match={rs.realized_pnl == res.total_pnl}")
    return rs.realized_pnl == res.total_pnl


if __name__ == "__main__":
    ok = run_stop() and run_stop_f0()
    print("STOP_REPRO_OK" if ok else "STOP_REPRO_FAIL")