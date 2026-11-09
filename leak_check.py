"""Verify suspected gross-exposure leak: batch-cut pre-adjusts shares based on
long-entry notional, but rebound-short max_live (higher due to +9% target) leaks
beyond the 120% cap under heterogeneous entry prices."""
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


def _cfg(comm_min=0.0):
    return StrategyConfig(
        use_rsi_trigger=False, enable_rebound_short=True, enable_eth_hedge=False,
        entry_next_bar=True, min_daily_volume_usd=1_000_000, slippage_pct=0.0,
        commission_per_share=0.0, commission_min=comm_min,
        funding_rate_pct_per_hour=0.0, avoid_downtrend=False,
        gross_cap_pct=120.0, max_positions=10,
        rebound_short_time_exit_bars=48, rebound_short_stop_pct=40.0,
        rebound_short_target_pct=9.0, time_exit_max_bars=200, max_daily_loss_pct=100.0,
    )


def _mk(sym, idx=25):
    return Signal(symbol=sym, side="long", reason="t", entry_price=100.0,
                  stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                  size_shares=100.0, signal_index=idx, timestamp="")


def run_case(name, prices, comm_min, hits, hold_bars=48):
    cfg = _cfg(comm_min)
    cands = {}
    sigs = {}
    syms = "XYZ"
    for sym, px, hit in zip(syms, prices, hits):
        cands[sym] = _make(25, px, hit, hold_bars)
        sigs[sym] = _mk(sym)

    def fake(hist, symbol=None, config=None, capital=10000.0, cache=None):
        idx = len(hist) - 1
        if idx == 25 and symbol in sigs:
            s = copy.copy(sigs[symbol]); s.signal_index = idx; return s
        return None

    with patch("scripts.run_portfolio.generate_signal", side_effect=fake):
        res = run_portfolio_simulation(cands, config=cfg, capital=10000.0)

    by = {t["symbol"]: t for t in res["trades"]}
    cap = 12000.0
    print(f"\n=== {name} (prices={prices} comm={comm_min} hits={hits}) ===")
    for sym, px in zip(syms, prices):
        t = by.get(sym)
        if t:
            print(f"  {sym}: px={px} shares={t['shares']:.4f} exit={t['exit_reason']} total_pnl={t['total_pnl']:.4f}")
        else:
            print(f"  {sym}: NOT ADMITTED")
    print(f"  final_gross={res['final_gross_exposure']} open={res['final_open_positions']}")
    return res, by


# Case: heterogeneous prices, all hit target, no commission
# X px=100, Y px=120, Z px=100. All 100 shares.
# total_desired = 10000 + 12000 + 10000 = 32000 > 12000. Batch-cut: equal_share=4000.
# X: 40 shares, Y: 33.33 shares, Z: 40 shares.
# Y hits target: short_entry = 120*1.09 = 130.8. max_live = 130.8 * 33.33 = 4360.
# Gross = 4000 + 4360 + 4000 = 12360 > 12000. LEAK!
run_case("LEAK-CHECK hetero all-hit comm0", [100, 120, 100], 0.0, [True, True, True])

# Same but with commission_min=100
run_case("LEAK-CHECK hetero all-hit comm100", [100, 120, 100], 100.0, [True, True, True])

# 4 candidates
run_case("LEAK-CHECK 4 hetero all-hit comm0", [100, 120, 100, 110], 0.0, [True, True, True, True])