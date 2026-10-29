# Crash-Rebound Strategy (Resolved from PDF)

Repository: CRASH-REBOUND-STRATEGY
Source: crash-rebound-strategy.pdf (extracted)

## Resolved (from PDF)
- **Universe**: Liquid coins on Hyperliquid (perps) trading >= $5M/day. When running broadly, configurable; backtest uses liquid coins meeting volume threshold.
- **Crash trigger**: Coin's 21-hour RSI closes below 20 (reading means last day was almost all selling). Signal fires when this condition met; buy at next hourly open.
- **Rebound/entry confirmation**: Enter at next hourly open after crash signal (RSI<20). No complex candle pattern required beyond the RSI condition; the strategy buys the crash.
- **Entry timing**: Buy at next hourly open. Deepest crash goes first when several fire at once.
- **Exit - Buy**: Sell at +9% target OR after 50 hours, whichever comes first.
- **Exit - Rebound short**: After buy sold at +9%, short same coin; close short at -9% or after 48 hours (whichever comes first). Short only opened when buy hit +9% target fast.
- **Stop - Buy**: Safety stop when coin falls 8 times its average hourly range (ATR(14) style) below entry. Median ~15% below entry on Hyperliquid coins (wide).
- **Stop - Short**: Closed if coin rises 40% above entry (wide).
- **Position sizing**: Up to 1.25% of coin's daily volume traded over last 24h. Buys+shorts capped at 120% of vault; when over capacity, cut open positions equally (never top up). Large orders sliced (<= half book near price).
- **Hedging**: Every buy opens short ETH position of matching risk (coin vol/ETH vol over 2 weeks, capped at 3x position). Every short gets long ETH position instead.
- **Risk/filters**: Only trade coins with >= $5M daily volume. One position per coin. Time limits enforced. Safety stops wide.
- **Fees/slippage**: Hourly simulation models exchange fees, spread, order-book impact, hourly funding on every leg, liquidation checks.

## Assumed (inferred/current implementation)
- Current implementation uses price-drop detection + rebound candle confirmation rather than RSI(21h)<20. This is a simplification to be aligned with PDF rules if needed.
- ATR-based stop (8x ATR) is specified in config; current generate_signal uses `low * 0.999` as fallback - needs to be replaced with ATR-based stop per PDF.
- Target can be +9% (config.target_pct) or derived from risk*RR; PDF states +9% target.
- Time exits: 50h for buy, 48h for rebound short (config.time_exit_max_bars currently 50).

## Implementation Plan (from PDF alignment)
1. Align trigger to RSI<20 on 21h where feasible; or keep price-based but ensure params match (+9% target, 50h).
2. Use ATR(14)*8.0 for buy stop (safety stop).
3. Enforce 120% gross cap with equal-share cuts.
4. Add rebound-short logic when buy hits +9% target.
5. Add multi-symbol fixtures and backtests.

## Backtest Metrics (from PDF)
- Hyperliquid test (2025-12-20 to 2026-09-28): +115% p.a., worst drop -5.4%, max DD small; Sharpe decent.
- Longer history since 2020 shows +34% p.a. with deeper drawdowns in some periods.
