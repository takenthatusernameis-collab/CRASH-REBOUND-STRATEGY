"""B-rem8 value probe: concrete expected values for LIQ and STOP on the exact 48th held bar."""
from __future__ import annotations

from types import SimpleNamespace

from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


class _NoCutRS:
    def check_position(self, config, capital, shares, entry_price):
        return SimpleNamespace(allowed=True, size_shares=shares)

    def apply_cap_cuts(self, capital, config, open_notional=None):
        return []

    def apply_trade(self, *a, **k):
        pass


def _build(liq_enabled, high_at_55):
    n = 80
    coin = [_c(f"b{i}", 100.0, 101.0, 99.5, 100.0) for i in range(n)]
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
    coin[8] = _c("e8", 100.0, 110.0, 99.5, 109.0)
    for i in range(9, n):
        coin[i] = _c(f"s{i}", 108.0, 115.0, 100.0, 107.0)
    coin[55] = _c("b55", 108.0, high_at_55, 100.0, 107.0)

    eth = [_c(f"h{i}", 2000.0, 2020.0, 1980.0, 2000.0) for i in range(n)]
    eth[6] = _c("h6", 2000.0, 2010.0, 1990.0, 2000.0)
    eth[8] = _c("h8", 2000.0, 2030.0, 1995.0, 2025.0)
    for i in range(9, n):
        eth[i] = _c(f"eh{i}", 2030.0, 2050.0, 2020.0, 2040.0)
    eth[55] = _c("eh55", 2030.0, 2055.0, 2020.0, 2045.0)

    cfg = StrategyConfig(
        enable_eth_hedge=True, enable_rebound_short=True, entry_next_bar=True,
        avoid_downtrend=False, slippage_pct=0.0, commission_per_share=0.0,
        commission_min=1.0, funding_rate_pct_per_hour=0.01,
        min_daily_volume_usd=0.0, time_exit_max_bars=200,
        enable_liquidation_checks=liq_enabled, gross_cap_pct=120.0,
        rebound_short_target_pct=9.0, rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
    )
    sig = Signal(symbol="T", side="long", reason="t", entry_price=100.0,
                 stop_price=80.0, target_price=109.0, risk_per_share=20.0,
                 timestamp="t5", size_shares=1000.0, signal_index=5)
    return coin, eth, cfg, sig


def main():
    # LIQ case: liquidation enabled, high well above +6% threshold
    coin, eth, cfg, sig = _build(True, 120.0)
    res = backtest_simple(coin, sig, config=cfg, risk_state=_NoCutRS(),
                          capital=100000.0, eth_candles=eth)
    sl = res.trades[1]
    print("LIQ on 48th bar:")
    print(f"  exit_reason={res.exit_reason} exit_ts={res.exit_timestamp} bars_held={res.bars_held}")
    print(f"  short leg reason={sl['reason']} entry={sl['entry']!r} exit={sl['exit']!r} pnl={sl['pnl']!r}")
    print(f"  rebound_hedge_side={res.rebound_hedge_side} size={res.rebound_hedge_size!r} "
          f"entry={res.rebound_hedge_entry!r} exit={res.rebound_hedge_exit!r} pnl={res.rebound_hedge_pnl!r}")
    print(f"  max_live_coin_notional={res.max_live_coin_notional!r}")
    print(f"  total_pnl={res.total_pnl!r}")
    coin_total = sum(t["pnl"] for t in res.trades)
    print(f"  coin_total={coin_total!r} hedge_pnl={res.hedge_pnl!r}")

    # STOP case: liquidation disabled, high at +40% stop threshold
    coin, eth, cfg, sig = _build(False, 152.599)
    res = backtest_simple(coin, sig, config=cfg, risk_state=_NoCutRS(),
                          capital=100000.0, eth_candles=eth)
    sl = res.trades[1]
    print("\nSTOP on 48th bar:")
    print(f"  exit_reason={res.exit_reason} exit_ts={res.exit_timestamp} bars_held={res.bars_held}")
    print(f"  short leg reason={sl['reason']} entry={sl['entry']!r} exit={sl['exit']!r} pnl={sl['pnl']!r}")
    print(f"  rebound_hedge_side={res.rebound_hedge_side} size={res.rebound_hedge_size!r} "
          f"entry={res.rebound_hedge_entry!r} exit={res.rebound_hedge_exit!r} pnl={res.rebound_hedge_pnl!r}")
    print(f"  max_live_coin_notional={res.max_live_coin_notional!r}")
    print(f"  total_pnl={res.total_pnl!r}")
    coin_total = sum(t["pnl"] for t in res.trades)
    print(f"  coin_total={coin_total!r} hedge_pnl={res.hedge_pnl!r}")


if __name__ == "__main__":
    main()