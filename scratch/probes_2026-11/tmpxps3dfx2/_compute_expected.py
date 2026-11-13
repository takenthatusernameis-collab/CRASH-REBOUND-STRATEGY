"""Compute exact expected values for the long-stop hedge regression lock."""
import sys
sys.path.insert(0, '.')
from src.backtest.engine import backtest_simple, _slippage_commission_per_share
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal, compute_eth_hedge_size
from src.backtest.engine import _apply_funding_pnl

from _probe_long_stop_eth_hedge import _cfg, _sig, _scenario, _CapCutRS


def _c(ts, o, h, l, c, v=10_000_000.0):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


coin, eth = _scenario()
cfg = _cfg()
sig = _sig()
CAPITAL = 100000.0

entry = sig.entry_price  # 100.0
shares_req = sig.size_shares  # 1000
entry_px = _slippage_commission_per_share(entry, cfg, 'buy', shares=shares_req)
ratio = entry_px / entry
stop_px = sig.stop_price * ratio  # 80.0 * ratio
target_px = sig.target_price * ratio

# cap-cut
notional_pre = entry_px * shares_req
cap_value = CAPITAL * cfg.gross_cap_pct / 100.0
all_notionals = [80000.0, notional_pre]
equal_share = cap_value / len(all_notionals)
new_notional_cut = min(equal_share, notional_pre)
shares = new_notional_cut / entry_px
live_notional = entry_px * shares

# hedge sizing (no look-ahead: coin[:7], eth[:7])
hedge_value = compute_eth_hedge_size(coin[:7], eth[:7], live_notional, cfg)
eth_entry_price = eth[6].get('open')  # 2000.0
hedge_shares = hedge_value / float(eth_entry_price)
hedge_entry_px = _slippage_commission_per_share(float(eth_entry_price), cfg, 'sell', shares=hedge_shares)

# exit at bar 8 (idx 8): stop fires, low=80.0 <= stop_px
exit_px = _slippage_commission_per_share(stop_px, cfg, 'sell', shares=shares)
coin_gross_pnl = (exit_px - entry_px) * shares
long_funding = _apply_funding_pnl(live_notional, 3, cfg.funding_rate_pct_per_hour, side='long')
coin_pnl = coin_gross_pnl - long_funding

# hedge exit at bar 8: eth[8].close = 2070.0
eth_exit_price = eth[8].get('close')  # 2070.0
hedge_exit_px = _slippage_commission_per_share(float(eth_exit_price), cfg, 'buy', shares=hedge_shares)
gross_hedge_pnl = (hedge_entry_px - hedge_exit_px) * hedge_shares
hedge_notional = hedge_entry_px * hedge_shares
hedge_funding_cost = _apply_funding_pnl(hedge_notional, 3, cfg.funding_rate_pct_per_hour, side='short')
hedge_pnl = gross_hedge_pnl - hedge_funding_cost

total_pnl = coin_pnl + hedge_pnl

print("=== EXPECTED VALUES ===")
print(f"entry_px = {entry_px!r}")
print(f"ratio = {ratio!r}")
print(f"stop_px = {stop_px!r}")
print(f"target_px = {target_px!r}")
print(f"notional_pre = {notional_pre!r}")
print(f"cap_value = {cap_value!r}")
print(f"equal_share = {equal_share!r}")
print(f"new_notional_cut = {new_notional_cut!r}")
print(f"shares = {shares!r}")
print(f"live_notional = {live_notional!r}")
print(f"hedge_value = {hedge_value!r}")
print(f"hedge_shares = {hedge_shares!r}")
print(f"hedge_entry_px = {hedge_entry_px!r}")
print(f"exit_px = {exit_px!r}")
print(f"coin_gross_pnl = {coin_gross_pnl!r}")
print(f"long_funding = {long_funding!r}")
print(f"coin_pnl = {coin_pnl!r}")
print(f"hedge_exit_px = {hedge_exit_px!r}")
print(f"gross_hedge_pnl = {gross_hedge_pnl!r}")
print(f"hedge_notional = {hedge_notional!r}")
print(f"hedge_funding_cost = {hedge_funding_cost!r}")
print(f"hedge_pnl = {hedge_pnl!r}")
print(f"total_pnl = {total_pnl!r}")
print(f"funding_delta = {total_pnl - backtest_simple(coin, _sig(), config=_cfg(funding_rate_pct_per_hour=0.0), risk_state=_CapCutRS(), capital=CAPITAL, eth_candles=eth).total_pnl!r}")

res = backtest_simple(coin, _sig(), config=_cfg(), risk_state=_CapCutRS(), capital=CAPITAL, eth_candles=eth)
print("=== ENGINE ===")
print(f"exit_reason = {res.exit_reason!r}")
print(f"shares = {res.shares!r}")
print(f"entry_price = {res.entry_price!r}")
print(f"exit_price = {res.exit_price!r}")
print(f"bars_held = {res.bars_held!r}")
print(f"hedge_side = {res.hedge_side!r}")
print(f"hedge_size = {res.hedge_size!r}")
print(f"hedge_entry = {res.hedge_entry!r}")
print(f"hedge_exit = {res.hedge_exit!r}")
print(f"pnl = {res.pnl!r}")
print(f"hedge_pnl = {res.hedge_pnl!r}")
print(f"total_pnl = {res.total_pnl!r}")
print(f"max_live_coin_notional = {res.max_live_coin_notional!r}")
print(f"rebound_short_pnl = {res.rebound_short_pnl!r}")
print(f"rebound_hedge_pnl = {res.rebound_hedge_pnl!r}")
print(f"trades = {res.trades!r}")