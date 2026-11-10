"""Instrumented trace: derive exact engine internals for the long-leg STOP path
with ETH hedge + commission_min + entry_next_bar + cap-cut equal-share.
Prints every intermediate so expected values can be hand-traced.
"""
import sys
sys.path.insert(0, '.')
from src.backtest.engine import backtest_simple, _slippage_commission_per_share
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.strategy.risk import usual_hourly_range_ratio

# Reuse the probe's exact fixtures
from _probe_long_stop_eth_hedge import _cfg, _sig, _scenario, _CapCutRS


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


coin, eth = _scenario()
cfg = _cfg()
sig = _sig()

# Replicate engine entry math
entry = sig.entry_price  # 100.0
shares0 = sig.size_shares  # 1000
entry_px = _slippage_commission_per_share(entry, cfg, 'buy', shares=shares0)
print("entry_px (slip+comm):", repr(entry_px))
print("comm per share:", max(cfg.commission_per_share, cfg.commission_min / shares0))

start_idx = sig.signal_index + 1  # 6
ratio = entry_px / entry
print("ratio:", repr(ratio))
rr = usual_hourly_range_ratio(coin[:start_idx + 1], period=cfg.atr_period)
print("range_ratio:", repr(rr))
stop_px = entry * (1.0 - cfg.stop_atr_mult * rr) if rr else None
print("stop (signal-bar):", repr(stop_px))
print("stop_px (re-anchored):", repr(stop_px * ratio))
target_px = sig.target_price * ratio
print("target_px:", repr(target_px))
risk = entry_px - stop_px * ratio
print("risk:", repr(risk))

# Cap-cut math
notional_pre = entry_px * shares0
print("notional_pre:", repr(notional_pre))
cap_value = 100000.0 * cfg.gross_cap_pct / 100.0
all_notionals = [80000.0, notional_pre]
print("cap_value:", repr(cap_value), "all_notionals:", all_notionals)
equal_share = cap_value / len(all_notionals)
print("equal_share:", repr(equal_share))
new_notional_cut = min(equal_share, notional_pre)
print("new_notional_cut:", repr(new_notional_cut))
shares = new_notional_cut / entry_px
print("shares:", repr(shares))
print("entry_px*shares (live notional):", repr(entry_px * shares))

# Exit at bar 8 (idx 8): low=80.0
exit_bar = coin[8]
print("bar8 low:", exit_bar['low'], "stop_px:", repr(stop_px * ratio), "fired:", exit_bar['low'] <= stop_px * ratio)
exit_px = _slippage_commission_per_share(stop_px * ratio, cfg, 'sell', shares=shares)
print("exit_px:", repr(exit_px))
pnl = (exit_px - entry_px) * shares
print("pnl (gross):", repr(pnl))
long_funding = abs(entry_px * shares) * 3 * (cfg.funding_rate_pct_per_hour / 100.0)
print("long_funding (3h):", repr(long_funding))
print("pnl net:", repr(pnl - long_funding))

res = backtest_simple(coin, _sig(), config=_cfg(), risk_state=_CapCutRS(),
                      capital=100000.0, eth_candles=eth)
print("---ENGINE---")
print("exit_reason:", res.exit_reason)
print("shares:", repr(res.shares))
print("entry_price:", repr(res.entry_price))
print("exit_price:", repr(res.exit_price))
print("pnl:", repr(res.pnl))
print("hedge_side:", res.hedge_side)
print("hedge_size:", repr(res.hedge_size))
print("hedge_entry:", repr(res.hedge_entry))
print("hedge_exit:", repr(res.hedge_exit))
print("hedge_pnl:", repr(res.hedge_pnl))
print("total_pnl:", repr(res.total_pnl))
print("max_live_coin_notional:", repr(res.max_live_coin_notional))
print("bars_held:", res.bars_held)
hedge_notional = res.hedge_entry * res.hedge_size
print("hedge_notional:", repr(hedge_notional))
hedge_funding = -hedge_notional * 3 * (cfg.funding_rate_pct_per_hour / 100.0)  # short receives
print("hedge_funding (3h, short):", repr(hedge_funding))
print("funding delta (coin+hedge):", repr((-long_funding) + hedge_funding))
off = backtest_simple(coin, _sig(), config=_cfg(funding_rate_pct_per_hour=0.0),
                      risk_state=_CapCutRS(), capital=100000.0, eth_candles=eth)
print("off total_pnl:", repr(off.total_pnl))
print("funding delta actual:", repr(res.total_pnl - off.total_pnl))