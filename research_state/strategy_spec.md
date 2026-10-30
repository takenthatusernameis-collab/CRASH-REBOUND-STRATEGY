# Strategy Spec (from crash-rebound-strategy.pdf)
Generated: 2026-10-30T01:43:44Z

## Overview
"Crash Rebound Strategy" (The Bitcoin Strategy / Premium) - buys liquid altcoins right after they crash, sells into bounce; if bounce runs too far (+9%) turns around and shorts the same coin for up to 2 days. Every trade hedged with ETH; sits in USDC between crashes.

Test window (Hyperliquid): 2025-12-20 to 2026-09-28 (283 days). Longer history since 2020 for context.

## Universe
- Hyperliquid perpetuals (altcoins) that traded >= $5M in last 24h
- ~26 coins clear this bar on Hyperliquid now; up to ~80 in 2024-2025
- One position per coin. Buys/shorts together capped at 120% of vault (coin positions cap context); hedges on top
- Between crashes hold USDC

## Crash Trigger (Buy signal)
- Signal: coin's **21-hour RSI closes below 20** (last day almost all selling)
- Buy at **next hourly open**
- When multiple fire at once, **deepest crash goes first**
- Only coins with >= $5M daily volume in last 24h considered

## Entry / Sizing
- Position size: up to **1.25% of what the coin traded over the last 24 hours** (sized to order book)
- When more crashes arrive than fit under cap, vault **cuts open positions so every position (old and new) holds equal share** of the 120% cap; positions only cut, never topped up
- Large orders in slices: never send > half resting on order book near price in one go, next slice ~20s later
- Buys and shorts together capped at **120% of vault** (one position per coin)
- Every buy opens a **short ETH position of matching risk**: coin's volatility / ETH's volatility over last 2 weeks, capped at **3x the position**
- Hedging applies to every trade

## Exits (Buy)
- Sell buy at **+9%** OR after **50 hours** at latest (whichever comes first)
- **Safety stop** (rare): buy sold if coin falls **8x its usual hourly range** below entry (hourly range = avg distance high-low/prev close over last 14 hours). Median ~15% below entry on Hyperliquid. Stops are wide; rarely fire. If stop fills, **stopped buy never opens rebound short**.
- No buy stays open > 50 hours

## Second Trade (Rebound Short)
- If buy is sold at **+9% target** (hits target fast), vault **shorts the same coin** and opens **long ETH position** against it
- Close short at **-9%** (i.e. profit target when shorting, so close if down 9% from short entry) OR after **48 hours** at latest
- **Rebound short stop**: close short if coin rises **40% above its entry** (wide, rare)
- Only coins that already bounced hard are worth shorting (shorting every buy at time exit lost money in 2020)
- Short held up to 48 hours (72 hours gave similar since 2020 but worse worst-drop; 48h chosen)

## Risk/Execution Details
- Never orders waiting on book
- ETH hedge sizing: coin's volatility / ETH's volatility over last 2 weeks, capped at 3x the position
- Gross exposure including hedges can reach high multiples in busy hours (e.g. up to ~4.8x briefly in example)
- 120% coin positions cap leaves margin free; stops not relied on for margin safety in fast crashes
- Hourly simulation with fees, spread, order-book impact, hourly funding on every leg, hourly liquidation check at worst price of each hour
- No look-ahead

## Performance (from PDF)
- Hyperliquid test (2025-12-20 to 2026-09-28, 283 days): Total +81.2% vs BTC -5.5%, altcoins -2.4%; Per year +115.2%; Worst drop -5.4%; 6 of 10 months gain
- Since 2020 (context): $10k -> $72k (~34%/year), worst -24.8%, every calendar year positive
- 85 trades in test: 73 buys (71% profitable), 12 shorts (83% profitable)
- Rebound short contributes ~27% of profit on Hyperliquid, ~40% since 2020

## Tuned vs Round Numbers (chosen settings)
- Buy target/hold: +9% / 50h (was +8% / 72h)
- Rebound short target/hold: -9% / 48h (was -10% / 72h)
- Position size: 1.25% of daily volume (was 2%)
- Result: better drawdowns, more consistent

## Costs/Fees (stated)
- Management/fees as described: 2% a year on assets and 10% of remaining profit (typical vault fee structure mentioned)
