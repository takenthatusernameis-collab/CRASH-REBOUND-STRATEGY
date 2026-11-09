"""Instrumented trace of run_portfolio same-bar loop to find the leak."""
import copy
from unittest.mock import patch
from scripts.run_portfolio import run_portfolio_simulation
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(ts, o, c, h=None, l=None, v=1_500_000.0):
    h = max(o, c) * 1.002 if h is None else h
    l = min(o, c) * 0.998 if l is None else l
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _make(signal_bar, entry_open, hit_target, hold_bars=48):
    candles = []
    for i in range(100):
        ts = f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z"
        if i == signal_bar:
            candles.append(_c(ts, 100.0, 90.0, 100.0, 88.0))
        elif i == signal_bar + 1:
            if hit_target:
                candles.append(_c(ts, entry_open, entry_open * 1.10, entry_open * 1.11, entry_open * 0.99))
            else:
                candles.append(_c(ts, entry_open, entry_open * 1.01, entry_open * 1.02, entry_open * 0.99))
        elif signal_bar + 2 <= i <= signal_bar + 1 + hold_bars:
            candles.append(_c(ts, entry_open * 1.08, entry_open * 1.08, entry_open * 1.085, entry_open * 1.075))
        else:
            candles.append(_c(ts, 100.0, 100.0, 101.0, 99.0))
    return candles


cfg = StrategyConfig(
    use_rsi_trigger=False, enable_rebound_short=True, enable_eth_hedge=False,
    entry_next_bar=True, min_daily_volume_usd=1_000_000, slippage_pct=0.0,
    commission_per_share=0.0, commission_min=0.0,
    funding_rate_pct_per_hour=0.0, avoid_downtrend=False,
    gross_cap_pct=120.0, max_positions=10,
    rebound_short_time_exit_bars=48, rebound_short_stop_pct=40.0,
    rebound_short_target_pct=9.0, time_exit_max_bars=200, max_daily_loss_pct=100.0,
)

cx = _make(25, 100.0, True)
cy = _make(25, 120.0, True)
cz = _make(25, 100.0, True)

def _mk(sym, idx=25):
    return Signal(symbol=sym, side="long", reason="t", entry_price=100.0,
                  stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                  size_shares=100.0, signal_index=idx, timestamp="")

def fake(hist, symbol=None, config=None, capital=10000.0, cache=None):
    idx = len(hist) - 1
    if idx == 25 and symbol in ("X", "Y", "Z"):
        return _mk(symbol)
    return None

# Monkey-patch backtest_simple to print max_live
import scripts.run_portfolio as rp
orig_backtest = rp.backtest_simple

def traced_backtest(candles, sig, config=None, capital=100000.0, risk_state=None, eth_candles=None):
    res = orig_backtest(candles, sig, config=config, capital=capital, risk_state=risk_state, eth_candles=eth_candles)
    print(f"  backtest {sig.symbol}: exit={res.exit_reason} shares={res.shares} max_live={res.max_live_coin_notional} post_notionals={risk_state.open_position_notionals if risk_state else None}")
    return res

rp.backtest_simple = traced_backtest

with patch("scripts.run_portfolio.generate_signal", side_effect=fake):
    res = run_portfolio_simulation({"X": cx, "Y": cy, "Z": cz}, config=cfg, capital=10000.0)

print("\nFINAL:")
print("  trades:", [(t['symbol'], t['shares'], t['exit_reason']) for t in res['trades']])
print("  final_gross:", res['final_gross_exposure'], "open:", res['final_open_positions'])