"""CELL 4(b) probe: 8x spec safety stop vs rebound short on the SAME bar.

Question: with enable_rebound_short=True and use_spec_safety_stop=True, when one
hourly bar breaches BOTH the 8x safety stop (low) and the +9% target (high), does
the engine exit 'stopped' (no rebound short) or 'target_rebound_short'?

Engine ordering (src/backtest/engine.py long-leg loop): liquidation -> stop
(low <= stop_px) -> target (high >= target_px). Stop is checked before target, so
a same-bar breach of both must exit 'stopped' and must NOT open a rebound short.

This probe traces exact values for the dated regression test.
"""
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(ts, o, h, l, cl, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": cl, "volume": v}


def _coin(n, base=100.0):
    return [_c(f"2025-01-01T{i % 24:02d}:00:00", base, base * 1.002, base * 0.998, base)
            for i in range(n)]


def _eth(n, base=2000.0):
    return [_c(f"2025-01-01T{i % 24:02d}:00:00", base, base * 1.001, base * 0.999, base)
            for i in range(n)]


def _cfg(**kw):
    d = dict(
        enable_eth_hedge=False,
        enable_rebound_short=True,
        entry_next_bar=False,
        avoid_downtrend=False,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
        funding_rate_pct_per_hour=0.0,
        min_daily_volume_usd=0.0,
        time_exit_max_bars=200,
        enable_liquidation_checks=False,
        use_spec_safety_stop=True,
        stop_atr_mult=8.0,
        atr_period=14,
    )
    d.update(kw)
    return StrategyConfig(**d)


ENTRY = 100.0
SHARES = 1.0
SIGNAL_IDX = 5
# 8x spec safety stop with avg hourly range ratio 0.02 -> 100*(1-8*0.02)=84.0
STOP = 84.0
TARGET = 109.0


def _sig():
    return Signal(symbol="T", side="long", reason="t", entry_price=ENTRY, stop_price=STOP,
                  target_price=TARGET, risk_per_share=ENTRY - STOP, timestamp="2025-01-01T05:00:00",
                  size_shares=SHARES, signal_index=SIGNAL_IDX)


def main():
    candles = _coin(40)
    # Bar 8: low 83 (<= stop 84) AND high 110 (>= target 109). Both breached.
    candles[8] = _c("2025-01-01T08:00:00", 100.0, 110.0, 83.0, 100.0)
    res = backtest_simple(candles, _sig(), config=_cfg())

    print("exit_reason:", res.exit_reason)
    print("exit_price:", res.exit_price)
    print("entry_price:", res.entry_price)
    print("shares:", res.shares)
    print("bars_held:", res.bars_held)
    print("pnl:", res.pnl)
    print("total_pnl:", res.total_pnl)
    print("rebound_short_pnl:", res.rebound_short_pnl)
    print("rebound_hedge_pnl:", res.rebound_hedge_pnl)
    print("trades:", res.trades)
    print("short legs:", [t for t in (res.trades or []) if t.get("side") == "short"])

    # Sanity: without target breach, stop alone -> stopped, no rebound
    candles2 = _coin(40)
    candles2[8] = _c("2025-01-01T08:00:00", 100.0, 105.0, 83.0, 100.0)
    r2 = backtest_simple(candles2, _sig(), config=_cfg())
    print("\nstop-only -> exit_reason:", r2.exit_reason, "short legs:", [t for t in (r2.trades or []) if t.get("side") == "short"])

    # Sanity: target breach, no stop -> target + rebound short
    candles3 = _coin(40)
    candles3[8] = _c("2025-01-01T08:00:00", 100.0, 110.0, 90.0, 109.0)
    r3 = backtest_simple(candles3, _sig(), config=_cfg())
    print("target-only -> exit_reason:", r3.exit_reason, "short legs:", [t for t in (r3.trades or []) if t.get("side") == "short"])


if __name__ == "__main__":
    main()