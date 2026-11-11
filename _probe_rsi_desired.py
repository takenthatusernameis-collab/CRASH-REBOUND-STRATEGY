"""Probe (2026-11-11): trace desired notionals for the 4-candidate RSI fixtures
to hand-trace expected equal-share values under max_positions < candidates.
"""
from __future__ import annotations

from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import generate_signal, _rsi


def _bar(i, o, c, v):
    hi = max(o, c) * 1.01
    lo = min(o, c) * 0.99
    return {
        "timestamp": f"2026-01-01T{i:02d}:00:00Z",
        "open": o, "high": hi, "low": lo, "close": c, "volume": v,
    }


def _make_rsi_series(step: float, volume: float, n: int = 60):
    candles = []
    p = 100.0
    for i in range(n):
        c = p * step
        candles.append(_bar(i, p, c, volume))
        p = c
    candles.append(_bar(n, p, p * 1.05, volume))
    return candles


def _cfg():
    return StrategyConfig(
        use_rsi_trigger=True, rsi_period=21, rsi_threshold=20.0,
        avoid_downtrend=True, regime_min_price=0.0, min_daily_volume_usd=0.0,
        enable_eth_hedge=False, enable_rebound_short=True,
        enable_volume_based_sizing=True, gross_cap_pct=120.0,
        max_positions=4, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=0.0, entry_next_bar=False, target_pct=200.0,
        rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=5, time_exit_max_bars=5,
    )


def main():
    specs = [("A", 0.97, 5_000_000), ("B", 0.98, 8_000_000),
             ("C", 0.985, 6_000_000), ("D", 0.99, 7_000_000)]
    cfg = _cfg()
    for name, step, vol in specs:
        series = _make_rsi_series(step, vol)
        rsi = _rsi(series, 21)
        sig = generate_signal(series, symbol=name, config=cfg, capital=100000.0)
        if sig is None:
            print(name, "NO SIGNAL", "rsi=", rsi)
            continue
        desired = sig.entry_price * float(sig.size_shares)
        print(f"{name}: rsi={rsi:.4f} entry_px={sig.entry_price:.6f} shares={sig.size_shares:.4f} desired_notional={desired:.2f}")


if __name__ == "__main__":
    main()