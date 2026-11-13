"""Detailed component trace for both-hedges fixture."""
from src.backtest.engine import _apply_funding_pnl

SHARES = 10.0
SLIP = 0.001
COMM_MIN = 0.5
RATE = 0.01

# Long leg
entry_px = 96.17603
target_px = 104.8318727
long_exit = 104.6770408273
long_gross = (long_exit - entry_px) * SHARES
long_notional = entry_px * SHARES
long_funding = _apply_funding_pnl(long_notional, 2, RATE, 'long')
long_pnl = long_gross - long_funding
print("LONG gross:", long_gross, "funding:", long_funding, "pnl:", long_pnl)

# Long-leg hedge
hedge_shares = 0.4842571760509429
hedge_entry = 1996.9674907781905
hedge_exit = 2103.1325092218094
hedge_gross = (hedge_entry - hedge_exit) * hedge_shares
hedge_notional = hedge_entry * hedge_shares
hedge_funding = _apply_funding_pnl(hedge_notional, 2, RATE, 'short')
hedge_pnl = hedge_gross - hedge_funding
print("HEDGE gross:", hedge_gross, "notional:", hedge_notional, "funding:", hedge_funding, "pnl:", hedge_pnl)

# Rebound short
short_entry = 104.52236378647271
short_exit = 108.158
short_gross = (short_entry - short_exit) * SHARES
short_notional = short_entry * SHARES
short_funding = _apply_funding_pnl(short_notional, 5, RATE, 'short')
short_pnl = short_gross - short_funding
print("SHORT gross:", short_gross, "funding:", short_funding, "pnl:", short_pnl)

# Rebound hedge
reb_shares = 0.5703795415377099
reb_entry = 2102.976609281343
reb_exit = 2107.013390718657
reb_gross = (reb_exit - reb_entry) * reb_shares
reb_notional = reb_entry * reb_shares
reb_funding = _apply_funding_pnl(reb_notional, 5, RATE, 'long')
reb_pnl = reb_gross - reb_funding
print("REB_HEDGE gross:", reb_gross, "notional:", reb_notional, "funding:", reb_funding, "pnl:", reb_pnl)

print("total_pnl:", long_pnl + hedge_pnl + short_pnl + reb_pnl)
print("hedge_pnl field (long+reb):", hedge_pnl + reb_pnl)
print("risk_state realized (long+hedge+short):", long_pnl + hedge_pnl + short_pnl)
print("delta funding on vs off:", (long_funding + hedge_funding + short_funding + reb_funding))