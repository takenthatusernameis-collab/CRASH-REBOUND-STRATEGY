#!/usr/bin/env python3
from src.data.loader import make_fixture_crash_rebound
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import generate_signal, backtest_crash_rebound
from src.backtest.engine import backtest_simple


def main():
    candles = make_fixture_crash_rebound()
    config = StrategyConfig(use_rsi_trigger=False)  # use fixture's drop pattern
    sig = generate_signal(candles, config=config)
    print("Signal:", sig is not None)
    res = backtest_crash_rebound(candles, config=config)
    print(f"Exit: {res.exit_reason}, PnL: {res.pnl:.4f}, R-mult: {res.r_multiple:.4f}")
    print(f"Hedge PnL: {getattr(res, 'hedge_pnl', 0):.4f}, Total: {getattr(res, 'total_pnl', res.pnl):.4f}")
    if res.trades:
        for t in res.trades:
            print(f"  {t}")


if __name__ == '__main__':
    main()
