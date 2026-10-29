# Crash-Rebound Strategy (Inferred Spec)

Repository: CRASH-REBOUND-STRATEGY
Source: crash-rebound-strategy.pdf (present at repo root). PDF appears to be a rendered report (image-heavy streams); exact text not trivially extractable via simple parsers in this environment. This spec is inferred from repo name and common crash-rebound patterns, to be refined against the PDF if possible later.

## Hypothesis
Exploit sharp intraday/daily drawdowns ("crashes") with mean-reversion/rebound entries, using strict risk controls and regime filters.

## Core Rules (proposed)
- **Universe**: Liquid equities/ETFs (e.g., SPY/QQQ/IWM) or broad market; configurable.
- **Crash trigger**: e.g., % drop from prior close / intraday low relative to open/MA, or gap down + volume spike. Example: -X% in last Y bars or close < N-day low.
- **Rebound entry**: after trigger, enter on stabilization/reversal signal (e.g., hammer/doji, reclaim of VWAP/level, or RSI divergence) within entry window (e.g., same day or next open).
- **Entry timing**: limit orders near support/mean; avoid catching falling knife aggressively.
- **Exit**: take profit at first reasonable rebound level (e.g., +R, prior close/50% retrace), stop at invalidation (below crash low / ATR multiple). Time-based exit if no follow-through.
- **Risk**: position size by risk % of capital (e.g., 1% risk), max concurrent positions, max daily loss stop.
- **Filters**: avoid earnings/major news (if known), avoid low liquidity, regime filter (e.g., only in certain volatility regimes) to reduce false positives.

## Data Requirements
- OHLCV (1m/5m/daily). For backtest need timestamps, volume.
- Corporate actions optional.
- Benchmarks optional.

## Backtest Metrics
- Total return, CAGR, Sharpe, Max Drawdown, Win Rate, Profit Factor, Expectancy, Avg R, % trades with follow-through, time-in-trade.

## Implementation Plan
1. Pure signal functions (trigger + entry confirmation)
2. Position sizing + risk checks
3. Backtester with slippage/commission (configurable)
4. Deterministic fixtures for tests
5. Walk-forward/regime analysis later

## Open Questions (to resolve from PDF/logs)
- Exact trigger thresholds/percentages
- Entry confirmation criteria
- Exit targets/stops
- Universe and session constraints
- Any regime filters or blackouts
