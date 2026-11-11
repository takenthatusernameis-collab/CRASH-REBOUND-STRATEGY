"""PROBE (2026-11-11): cell #1 — rebound-short LIQUIDATION on exact 48th held bar
UNDER cap_cut regime (DailyRiskState, gross_cap 120%) + commission_min + entry_next_bar.
Captures engine-traced values to encode as a failing-tests-first regression lock.
"""
from __future__ import annotations

from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.strategy.risk import DailyRiskState


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def base_setup():
    n = 80
    coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)      # long entry_next_bar fill
    coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)      # long target -> rebound short opens
    for i in range(9, n):
        coin[i] = _c(f"s{i}", 108.0, 115.0, 100.0, 107.0)
    return coin


def eth_base():
    n = 80
    eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
    eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
    eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)  # rebound hedge entry idx 8
    for i in range(9, n):
        eth[i] = _c(f"eh{i}", 2030.0, 2050.0, 2020.0, 2040.0)
    return eth


def cfg_liq():
    return StrategyConfig(
        enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=1.0, funding_rate_pct_per_hour=0.01,
        min_daily_volume_usd=0.0, time_exit_max_bars=200,
        enable_liquidation_checks=True, liquidation_maint_margin_pct=5.0,
        liquidation_buffer_pct=1.0, liquidation_penalty_pct=0.5, gross_cap_pct=120.0,
        rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
    )


def sig(shares=1000.0):
    return Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                  stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                  timestamp="t5", size_shares=shares, signal_index=5)


def show(res, rs, label):
    print(f"=== {label} ===")
    print("exit_reason:", res.exit_reason)
    print("exit_timestamp:", res.exit_timestamp)
    print("bars_held:", res.bars_held)
    for i, t in enumerate(res.trades):
        print(f"  trade[{i}]: {t}")
    print("rebound_hedge_side:", res.rebound_hedge_side)
    print("rebound_hedge_size:", repr(res.rebound_hedge_size))
    print("rebound_hedge_entry:", repr(res.rebound_hedge_entry))
    print("rebound_hedge_exit:", repr(res.rebound_hedge_exit))
    print("rebound_hedge_pnl:", repr(res.rebound_hedge_pnl))
    print("hedge_pnl:", repr(res.hedge_pnl))
    print("max_live_coin_notional:", repr(res.max_live_coin_notional))
    print("total_pnl:", repr(res.total_pnl))
    coin_total = sum(t["pnl"] for t in res.trades)
    print("coin_total:", repr(coin_total))
    print("risk_state.realized_pnl:", repr(rs.realized_pnl))
    print("risk_state.open_positions:", rs.open_positions)
    print("risk_state.gross_exposure:", repr(rs.gross_exposure))
    print("risk_state.open_position_notionals:", rs.open_position_notionals)
    print()


def run_aligned():
    coin = base_setup()
    coin[55] = _c("b55", 108.0, 120.0, 100.5, 107.0)  # 48th held bar liq
    eth = eth_base()
    eth[55] = _c("eh55", 2030.0, 2055.0, 2020.0, 2045.0)
    rs = DailyRiskState()
    res = backtest_simple(coin, sig(), config=cfg_liq(), risk_state=rs,
                          capital=100000.0, eth_candles=eth)
    show(res, rs, "ALIGNED ETH, 48th-bar liquidation, cap_cut regime")


def run_missing_eth():
    """ETH entirely absent at exit index (shorter series)."""
    coin = base_setup()
    coin[55] = _c("b55", 108.0, 120.0, 100.5, 107.0)
    # ETH length 55 (indices 0..54) -> exit index 55 entirely absent
    eth = eth_base()[:55]
    rs = DailyRiskState()
    res = backtest_simple(coin, sig(), config=cfg_liq(), risk_state=rs,
                          capital=100000.0, eth_candles=eth)
    show(res, rs, "MISSING ETH (absent at exit idx 55), 48th-bar liquidation, cap_cut")


def run_funding_delta():
    """Funding-on vs funding-off delta for both variants."""
    for label, mk in (("ALIGNED", lambda: (base_setup(), eth_base(), 55,
                                           lambda c, e: c.__setitem__(55, _c("b55", 108.0, 120.0, 100.5, 107.0)) or e.__setitem__(55, _c("eh55", 2030.0, 2055.0, 2020.0, 2045.0)))),
                      ("MISSING", lambda: (base_setup()[:56] if False else base_setup(), eth_base()[:55], 55,
                                           lambda c, e: c.__setitem__(55, _c("b55", 108.0, 120.0, 100.5, 107.0)))):
        pass
    # aligned
    coin = base_setup(); coin[55] = _c("b55", 108.0, 120.0, 100.5, 107.0)
    eth = eth_base(); eth[55] = _c("eh55", 2030.0, 2055.0, 2020.0, 2045.0)
    for fr in (0.0, 0.01):
        rs = DailyRiskState()
        res = backtest_simple(coin, sig(), config=cfg_liq() if fr else cfg_liq(), risk_state=rs,
                              capital=100000.0, eth_candles=eth)
        # patch funding
        cfg = StrategyConfig(
            enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
            avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
            commission_min=1.0, funding_rate_pct_per_hour=fr,
            min_daily_volume_usd=0.0, time_exit_max_bars=200,
            enable_liquidation_checks=True, liquidation_maint_margin_pct=5.0,
            liquidation_buffer_pct=1.0, liquidation_penalty_pct=0.5, gross_cap_pct=120.0,
            rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
            rebound_short_time_exit_bars=48,
        )
        rs = DailyRiskState()
        res = backtest_simple(coin, sig(), config=cfg, risk_state=rs, capital=100000.0, eth_candles=eth)
        print(f"ALIGNED funding={fr}: total_pnl={res.total_pnl!r} realized={rs.realized_pnl!r} hedge_pnl={res.rebound_hedge_pnl!r}")
    # missing eth
    coin = base_setup(); coin[55] = _c("b55", 108.0, 120.0, 100.5, 107.0)
    eth = eth_base()[:55]
    for fr in (0.0, 0.01):
        cfg = StrategyConfig(
            enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
            avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
            commission_min=1.0, funding_rate_pct_per_hour=fr,
            min_daily_volume_usd=0.0, time_exit_max_bars=200,
            enable_liquidation_checks=True, liquidation_maint_margin_pct=5.0,
            liquidation_buffer_pct=1.0, liquidation_penalty_pct=0.5, gross_cap_pct=120.0,
            rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
            rebound_short_time_exit_bars=48,
        )
        rs = DailyRiskState()
        res = backtest_simple(coin, sig(), config=cfg, risk_state=rs, capital=100000.0, eth_candles=eth)
        print(f"MISSING funding={fr}: total_pnl={res.total_pnl!r} realized={rs.realized_pnl!r} hedge_pnl={res.rebound_hedge_pnl!r}")


if __name__ == "__main__":
    run_aligned()
    run_missing_eth()
    run_funding_delta()