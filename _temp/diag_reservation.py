"""Diagnostic: trace engine probe_state.open_position_notionals and max_live_coin_notional
for a rebound-short trade under cap pressure, to find a concrete reservation defect."""
import copy
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.backtest.engine import backtest_simple
from src.strategy.risk import RiskState


def _c(ts, o, c, h=None, l=None, v=1_500_000.0):
    h = max(o, c) * 1.002 if h is None else h
    l = min(o, c) * 0.998 if l is None else l
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def cfg(**kw):
    base = dict(
        use_rsi_trigger=False, enable_rebound_short=True, enable_eth_hedge=False,
        entry_next_bar=True, min_daily_volume_usd=1_000_000, slippage_pct=0.0,
        commission_per_share=0.0, commission_min=0.0, funding_rate_pct_per_hour=0.0,
        avoid_downtrend=False, gross_cap_pct=120.0, max_positions=10,
        rebound_short_time_exit_bars=48, rebound_short_stop_pct=40.0,
        rebound_short_target_pct=9.0, time_exit_max_bars=200, max_daily_loss_pct=100.0,
    )
    base.update(kw)
    return StrategyConfig(**base)


def make_y_candles():
    """Y: crash bar 25, target hit bar 26 (rebound short opens), holds to bar 74 time exit."""
    cs = []
    for i in range(100):
        ts = f"2026-01-{1 + i // 24:02d}T{i % 24:02d}:00:00Z"
        if i == 25:
            cs.append(_c(ts, 100.0, 90.0, 100.0, 88.0))
        elif i == 26:
            cs.append(_c(ts, 100.0, 110.0, 111.0, 99.0))
        elif 27 <= i <= 74:
            cs.append(_c(ts, 108.0, 108.0, 108.5, 107.5))
        else:
            cs.append(_c(ts, 100.0, 100.0, 101.0, 99.0))
    return cs


def main():
    cfg_comm = cfg(commission_min=1.0)  # commission_min > 0
    candles_y = make_y_candles()
    sig_y = Signal(symbol="Y", side="long", reason="t", entry_price=100.0, stop_price=80.0,
                   target_price=109.0, risk_per_share=20.0, size_shares=50.0,
                   signal_index=25, timestamp="")

    # Simulate: X already open at 8000, Y admits under cap pressure.
    capital = 10000.0
    risk_state = RiskState(date="")
    # Pretend X is open with 8000 notional
    risk_state.open_position_notionals = [8000.0]
    risk_state.gross_exposure = 8000.0
    risk_state.open_positions = 1

    res = backtest_simple(candles_y, sig_y, config=cfg_comm, capital=capital,
                          risk_state=risk_state, eth_candles=None)
    print("=== commission_min=1.0, X open 8000, Y admits ===")
    print("exit_reason:", res.exit_reason)
    print("shares:", res.shares)
    print("entry_price (long fill, comm-adjusted):", res.entry_price)
    print("max_live_coin_notional:", res.max_live_coin_notional)
    print("probe_state.open_position_notionals AFTER run:", risk_state.open_position_notionals)
    print("probe_state.gross_exposure:", risk_state.gross_exposure)
    print("probe_state.open_positions:", risk_state.open_positions)
    print("trades:", res.trades)

    # Now check: what does the portfolio reservation see?
    executed_notional = float(getattr(res, 'max_live_coin_notional', 0.0) or 0.0)
    post_notionals = list(risk_state.open_position_notionals)
    existing_syms = ["X"]  # X was the only existing
    print("\n--- portfolio reconciliation ---")
    print("executed_notional (max_live):", executed_notional)
    print("post_notionals:", post_notionals)
    print("len(post)=%d, len(existing)+1=%d" % (len(post_notionals), len(existing_syms) + 1))
    if post_notionals and len(post_notionals) >= len(existing_syms) + 1:
        print("BRANCH >= existing+1: would set Y =", executed_notional, "X =", post_notionals[0])
    elif post_notionals and len(post_notionals) == len(existing_syms):
        print("BRANCH == existing: would set X = min(cur, post[0]), Y = min(executed, cap)")
    else:
        print("BRANCH else: fallback Y = min(executed, cap)")

    # Key question: does max_live_coin_notional (short entry) exceed the engine's
    # cut notional for Y? If so, portfolio reserves more than engine cut.
    print("\n--- mismatch check ---")
    print("long entry notional (engine cut basis):", res.entry_price * res.shares)
    print("max_live (short entry notional):", res.max_live_coin_notional)


if __name__ == "__main__":
    main()