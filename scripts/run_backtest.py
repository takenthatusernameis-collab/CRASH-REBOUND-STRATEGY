#!/usr/bin/env python3
"""Low-level demo script (NOT volume-gated/spec-compliant production gating).

Uses fixture data and direct engine/wrapper calls for local inspection. Production
spec-compliant gating must flow through generate_signal/filter_universe and gated
runners (e.g. run_portfolio/run_real_campaign validators).
"""
from src.data.loader import make_fixture_crash_rebound
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import generate_signal, backtest_crash_rebound
from src.backtest.engine import backtest_simple


def main():
    candles = make_fixture_crash_rebound()
    config = StrategyConfig(use_rsi_trigger=False)  # use fixture's drop pattern
    sig = generate_signal(candles, config=config)
    print("Signal:", sig is not None)
    # Low-level demo (NOT spec-compliant production gating): opt out of the fail-closed
    # ETH-hedge contract so fixture series without aligned ETH candles can be inspected.
    res = backtest_crash_rebound(candles, config=config, require_eth_hedge=False)
    print("=" * 60)
    print("DETAILED BACKTEST REPORT")
    print("=" * 60)
    print(f"Exit reason: {res.exit_reason}")
    print(f"Entry: {res.entry_price:.6f}, Exit: {res.exit_price:.6f}")
    print(f"Shares: {res.shares:.6f}, Bars held: {res.bars_held}")
    print(f"Coin PnL: {res.pnl:.4f}, R-mult: {res.r_multiple:.4f}")
    print(f"Hedge side: {res.hedge_side}, Hedge size: {res.hedge_size:.6f}")
    print(f"Hedge entry: {res.hedge_entry:.6f}, Hedge exit: {res.hedge_exit:.6f}")
    print(f"Hedge PnL: {getattr(res, 'hedge_pnl', 0):.4f}")
    print(f"Total PnL: {getattr(res, 'total_pnl', res.pnl):.4f}")
    if res.trades:
        print("\n" + "-" * 60)
        print(f"TRADE BREAKDOWN ({len(res.trades)} legs)")
        print("-" * 60)
        for i, t in enumerate(res.trades):
            side = t.get('side', '?')
            entry = t.get('entry', 0)
            exit = t.get('exit', 0)
            pnl_t = t.get('pnl', 0)
            reason = t.get('reason', '')
            print(f"  [{i+1}] {side:5s} | Entry: {entry:.6f} | Exit: {exit:.6f} | PnL: {pnl_t:+.4f} | {reason}")
    print("=" * 60)


if __name__ == '__main__':
    main()
