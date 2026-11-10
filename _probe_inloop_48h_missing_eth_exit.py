"""Probe: rebound-short in-loop 48h TIME_EXIT with NO aligned ETH bar at exit index.

ETH series truncated to bars 0..8 (len 9); coin series 120 bars. Rebound hedge
established at idx 8 (aligned), but in-loop 48h break fires at sidx=55 where
`sidx >= len(eth_candles)` -> rebound hedge exit raw falls back to
rebound_hedge_info['entry'], then sell-side slippage/commission_min closes the
long ETH hedge. Hourly funding still applies on every leg.

Derives exact engine-traced expected values for the regression lock.
"""
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.strategy.risk import DailyRiskState


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def _cfg(rate=0.01):
    return StrategyConfig(
        enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=1.0, funding_rate_pct_per_hour=rate,
        min_daily_volume_usd=0.0, time_exit_max_bars=200,
        enable_liquidation_checks=False,
        liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5, gross_cap_pct=120.0,
        rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
    )


def _sig(shares=600.0):
    return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                  stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                  timestamp="t5", size_shares=shares, signal_index=5)


def _candles():
    n = 120
    coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)          # entry_next_bar long fill
    coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)          # long target -> rebound short opens
    for i in range(9, n):
        coin[i] = _c(f"s{i}", 108.0, 115.0, 100.0, 107.0)
    eth = [_c(f"e{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
    eth[6] = _c("e6", 2000.0, 2010.0, 1990.0, 2000.0)
    eth[8] = _c("e8", 2000.0, 2030.0, 1995.0, 2025.0)      # rebound hedge entry aligned idx 8
    for i in range(9, n):
        eth[i] = _c(f"eh{i}", 2030.0, 2050.0, 2020.0, 2040.0)
    eth[56] = _c("eh56", 2030.0, 2055.0, 2020.0, 2045.0)  # (unused: ETH truncated)
    eth_short = eth[:9]  # bars 0..8 only -> sidx=55 >= 9 -> fallback
    return coin, eth_short


def main():
    coin, eth = _candles()
    sig = _sig(600.0)

    rs_on = DailyRiskState()
    res_on = backtest_simple(coin, sig, config=_cfg(0.01), risk_state=rs_on, capital=100000.0, eth_candles=eth)
    rs_off = DailyRiskState()
    res_off = backtest_simple(coin, sig, config=_cfg(0.0), risk_state=rs_off, capital=100000.0, eth_candles=eth)

    print("== result (funding ON) ==")
    for k in ("exit_reason", "exit_timestamp", "bars_held", "entry_price", "exit_price",
              "shares", "max_live_coin_notional", "pnl", "hedge_pnl", "rebound_short_pnl",
              "rebound_hedge_pnl", "total_pnl", "rebound_hedge_side", "rebound_hedge_size",
              "rebound_hedge_entry", "rebound_hedge_exit"):
        print(f"  {k} = {getattr(res_on, k)!r}")
    print("  trades:")
    for t in res_on.trades:
        print(f"    {t}")
    print("== risk_state (funding ON) ==")
    print(f"  realized_pnl = {rs_on.realized_pnl!r}")
    print(f"  open_positions = {rs_on.open_positions!r}")
    print(f"  gross_exposure = {rs_on.gross_exposure!r}")
    print(f"  open_position_notionals = {rs_on.open_position_notionals!r}")
    print("== funding parity ==")
    print(f"  total_pnl on  = {res_on.total_pnl!r}")
    print(f"  total_pnl off = {res_off.total_pnl!r}")
    print(f"  total_pnl delta = {res_on.total_pnl - res_off.total_pnl!r}")
    print(f"  realized_pnl on  = {rs_on.realized_pnl!r}")
    print(f"  realized_pnl off = {rs_off.realized_pnl!r}")
    print(f"  realized delta = {rs_on.realized_pnl - rs_off.realized_pnl!r}")
    print(f"  len(eth) = {len(eth)}")


if __name__ == "__main__":
    main()