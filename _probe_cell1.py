"""Trace candidate cell #1: rebound-short liquidation on the 48th held bar,
with post-cap-cut shares (600), commission_min, entry_next_bar, real
DailyRiskState settlement, aligned AND missing ETH.

Precedence under test: liquidation beats 48h time_exit on the same bar.
"""
from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.strategy.risk import DailyRiskState


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def base_coin(n=80):
    coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)      # entry_next_bar long fill
    coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)      # long target -> rebound short opens
    for i in range(9, n):
        coin[i] = _c(f"s{i}", 108.0, 115.0, 100.0, 107.0)
    return coin


def base_eth(n=80):
    eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
    eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
    eth[8] = _c("eh8", 2000.0, 2030.0, 1995.0, 2025.0)  # rebound hedge entry aligned idx 8
    for i in range(9, n):
        eth[i] = _c(f"eh{i}", 2030.0, 2050.0, 2020.0, 2040.0)
    return eth


def cfg(funding=0.01, liq=True):
    return StrategyConfig(
        enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=1.0, funding_rate_pct_per_hour=funding,
        min_daily_volume_usd=0.0, time_exit_max_bars=200,
        enable_liquidation_checks=liq,
        liquidation_maint_margin_pct=5.0, liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5, gross_cap_pct=120.0,
        rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
    )


def sig(shares=600.0):
    return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                  stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                  timestamp="t5", size_shares=shares, signal_index=5)


def run(label, coin, eth, funding=0.01, liq=True):
    rs = DailyRiskState()
    res = backtest_simple(coin, sig(), config=cfg(funding, liq),
                          risk_state=rs, capital=100000.0, eth_candles=eth)
    print(f"--- {label} ---")
    print("exit_reason:", res.exit_reason)
    print("exit_timestamp:", res.exit_timestamp, "bars_held:", res.bars_held)
    for t in res.trades:
        print("  trade:", t)
    print("hedge_side:", res.hedge_side, "size:", res.rebound_hedge_size)
    print("hedge_entry:", res.rebound_hedge_entry, "hedge_exit:", res.rebound_hedge_exit)
    print("hedge_pnl:", res.hedge_pnl, "rebound_hedge_pnl:", res.rebound_hedge_pnl)
    print("max_live_coin_notional:", res.max_live_coin_notional)
    print("total_pnl:", res.total_pnl)
    print("risk_state realized:", rs.realized_pnl, "open:", rs.open_positions,
          "gross:", rs.gross_exposure, "notionals:", rs.open_position_notionals)
    print()


if __name__ == "__main__":
    # ALIGNED ETH: liquidation on 48th bar (sidx=55), high=120 triggers liq
    coin = base_coin()
    coin[55] = _c("b55", 108.0, 120.0, 100.5, 107.0)
    eth = base_eth()
    eth[55] = _c("eh55", 2030.0, 2055.0, 2020.0, 2045.0)
    run("ALIGNED-ETH liq-on-48th", coin, eth)

    # MISSING ETH at exit index (len 55 -> sidx 55 OOR -> raw fallback)
    coin = base_coin()
    coin[55] = _c("b55", 108.0, 120.0, 100.5, 107.0)
    eth = base_eth(n=55)
    run("MISSING-ETH liq-on-48th (raw fallback)", coin, eth)

    # STOP on 48th bar variant (high=152.599 triggers stop)
    coin = base_coin()
    coin[55] = _c("b55", 108.0, 152.599, 100.5, 107.0)
    eth = base_eth()
    eth[55] = _c("eh55", 2030.0, 2055.0, 2020.0, 2045.0)
    run("ALIGNED-ETH stop-on-48th", coin, eth, liq=False)