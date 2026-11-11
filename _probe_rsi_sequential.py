"""Probe (2026-11-11): #3 sequential path - existing open position from prior bar +
new same-bar RSI candidates exceeding 120% cap (non-batch path)."""
from __future__ import annotations
from scripts.run_portfolio import run_portfolio_simulation
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import _rsi


def _bar(i, o, c, v):
    hi = max(o, c) * 1.01
    lo = min(o, c) * 0.99
    return {"timestamp": f"2026-01-01T{i:02d}:00:00Z", "open": o, "high": hi,
            "low": lo, "close": c, "volume": v}


def _make_rsi_series(step, volume, n=60):
    candles = []
    p = 100.0
    for i in range(n):
        c = p * step
        candles.append(_bar(i, p, c, volume))
        p = c
    candles.append(_bar(n, p, p * 1.05, volume))  # rebound confirmation at decision bar
    return candles


def _cfg(**kw):
    d = dict(
        use_rsi_trigger=True, rsi_period=21, rsi_threshold=20.0,
        avoid_downtrend=True, regime_min_price=0.0, min_daily_volume_usd=0.0,
        enable_eth_hedge=False, enable_rebound_short=True,
        enable_volume_based_sizing=True, gross_cap_pct=120.0, max_positions=4,
        slippage_pct=0.0, commission_per_share=0.0, commission_min=0.0,
        entry_next_bar=False, target_pct=200.0, rebound_short_target_pct=9.0,
        rebound_short_stop_pct=40.0, rebound_short_time_exit_bars=5,
        time_exit_max_bars=5,
    )
    d.update(kw)
    return StrategyConfig(**d)


# Build a series where X fires early (bar 50) and holds, then A,B,C,D fire at bar 60.
# X needs RSI<20 at bar 50 with rebound confirmation. Make X a sustained downtrend
# ending at bar 50 with a rebound bar, then flat-ish continuation to bar 60.
def _make_x_series():
    """X: downtrend to bar 50 (RSI<20, rebound confirm), then flat to 60."""
    candles = []
    p = 100.0
    # bars 0..49: downtrend step 0.97
    for i in range(50):
        c = p * 0.97
        candles.append(_bar(i, p, c, 5_000_000))
        p = c
    # bar 50: rebound confirmation (decision bar for X)
    candles.append(_bar(50, p, p * 1.05, 5_000_000))
    p = p * 1.05
    # bars 51..60: flat-ish so no new X trigger, but A,B,C,D can fire at 60
    for i in range(51, 61):
        c = p * 1.001
        candles.append(_bar(i, p, c, 5_000_000))
        p = c
    return candles


X = _make_x_series()
A = _make_rsi_series(0.97, 5_000_000)
B = _make_rsi_series(0.98, 8_000_000)
C = _make_rsi_series(0.985, 6_000_000)
D = _make_rsi_series(0.99, 7_000_000)
print("X RSI at bar 50:", _rsi(X[:51], 21))
print("A,B,C,D RSI:", [_rsi(x, 21) for x in (A, B, C, D)])

# All series must align: X has 61 bars (0..60), A has 61 bars (0..60).
# X fires at bar 50, holds time_exit_max_bars=5 -> exits at bar 55.
# A,B,C,D fire at bar 60 (their last bar). At bar 60, X already exited (occupied_until[X]=55 < 60).
# So no existing position at bar 60. Need X to still be open at bar 60.
# Increase X's time_exit_max_bars so it holds past bar 60.
cfg = _cfg(time_exit_max_bars=15, max_positions=4)
res = run_portfolio_simulation({"X": X, "A": A, "B": B, "C": C, "D": D}, config=cfg, capital=100000.0)
print("\nSequential probe: X fires bar 50, A-D fire bar 60, X holds 15 bars")
print("  num_trades:", res["num_trades"])
for t in res["trades"]:
    notional = float(t["shares"]) * float(t["entry_price"])
    print(f"  {t['symbol']}: exit={t['exit_reason']} entry_ts={t['entry_timestamp']} "
          f"notional={notional:.4f}")
print("  final_open:", res["final_open_positions"], "final_gross:", res["final_gross_exposure"])