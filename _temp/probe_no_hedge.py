"""Probe: long liquidation, cap-cut + commission_min + entry_next_bar + funding,
NO usable ETH hedge (hedge size 0). Derive deterministic expected values."""
from src.backtest.engine import backtest_simple, _slippage_commission_per_share, _apply_funding_pnl
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


class _CapCutRS:
    open_positions = 1
    gross_exposure = 80000.0
    open_position_notionals = [80000.0]

    def check_position(self, config, capital, shares, entry_price):
        from types import SimpleNamespace
        return SimpleNamespace(allowed=True, size_shares=shares)

    def apply_cap_cuts(self, capital, config, open_notional=None):
        capv = capital * config.gross_cap_pct / 100.0
        n = len(open_notional or [])
        return [capv / n] * n if n else []

    def apply_trade(self, *a, **k):
        pass


def _cfg(**ov):
    d = dict(
        enable_eth_hedge=True,
        enable_rebound_short=True,
        entry_next_bar=True,
        avoid_downtrend=False,
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=1.0,
        funding_rate_pct_per_hour=0.01,
        min_daily_volume_usd=0.0,
        time_exit_max_bars=200,
        enable_liquidation_checks=True,
        liquidation_maint_margin_pct=5.0,
        liquidation_buffer_pct=1.0,
        liquidation_penalty_pct=0.5,
        gross_cap_pct=120.0,
        hedge_vol_lookback_hours=336,
        hedge_cap_multiplier=3.0,
        rebound_short_target_pct=9.0,
        rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
    )
    d.update(ov)
    return StrategyConfig(**d)


def _sig():
    return Signal(
        symbol="T", side="long", reason="t", entry_price=100.0, stop_price=80.0,
        target_price=109.0, risk_per_share=20.0, timestamp="t5", size_shares=1000.0,
        signal_index=5,
    )


def _scenario():
    n = 40
    coin = []
    cp = 100.0
    for i in range(n):
        cm = 1.015 if i % 2 == 0 else 0.985
        co, cc = cp, cp * cm
        ch, cl = max(co, cc) * 1.002, min(co, cc) * 0.998
        coin.append(_c(f"b{i}", co, ch, cl, cc))
        cp = cc
    coin[6] = _c("e6", 100.0, 100.5, 99.5, 100.0)
    coin[8] = _c("e8", 100.0, 101.0, 93.0, 99.0)  # liquidation
    return coin


def main():
    coin = _scenario()
    res = backtest_simple(coin, _sig(), config=_cfg(), risk_state=_CapCutRS(),
                          capital=100000.0, eth_candles=None)
    print("exit_reason:", res.exit_reason)
    print("shares:", repr(res.shares))
    print("entry_price:", repr(res.entry_price))
    print("exit_price:", repr(res.exit_price))
    print("bars_held:", res.bars_held)
    print("hedge_side:", res.hedge_side, "hedge_size:", res.hedge_size)
    print("pnl:", repr(res.pnl))
    print("hedge_pnl:", res.hedge_pnl)
    print("total_pnl:", repr(res.total_pnl))
    print("max_live_coin_notional:", repr(res.max_live_coin_notional))
    print("rebound_short_pnl:", res.rebound_short_pnl)
    print("trades:", res.trades)

    # Manual replay
    cfg = _cfg()
    capv = 100000.0 * cfg.gross_cap_pct / 100.0  # 120000
    all_notionals = [80000.0, 100000.0]
    cuts = _CapCutRS().apply_cap_cuts(100000.0, cfg, all_notionals)
    print("cuts:", cuts)
    new_notional_cut = cuts[-1]  # 60000
    entry_px = 100.0
    shares = new_notional_cut / entry_px  # 600
    entry_fill = _slippage_commission_per_share(entry_px, cfg, 'buy', shares=shares)
    print("manual shares:", shares, "entry_fill:", entry_fill)
    # entry_px in engine = entry_fill (commission_min applied)
    liq_px = 93.0
    exit_fill = _slippage_commission_per_share(liq_px, cfg, 'sell', shares=shares)
    print("exit_fill:", exit_fill)
    pnl = (exit_fill - entry_fill) * shares
    penalty = cfg.liquidation_penalty_pct / 100.0 * (entry_fill * shares)
    pnl -= penalty
    hours = 3
    long_funding = _apply_funding_pnl(entry_fill * shares, hours, cfg.funding_rate_pct_per_hour, side='long')
    pnl -= long_funding
    print("manual pnl:", repr(pnl))
    print("manual max_live_coin_notional:", entry_fill * shares)


if __name__ == "__main__":
    main()