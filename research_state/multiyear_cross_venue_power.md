# Multi-Year Cross-Venue Power Reassessment (C6-T2)

**Generated (UTC):** 2026-11-14T23:42:25Z
**Verdict:** `CROSS_VENUE_POWERED_OBSERVED`
**Venue basis:** OKX public REST v5 history-candles. **NOT Hyperliquid evidence.**

## Observed

| Slice | Events | Episodes | Distinct crash days | Largest episode share |
|---|---:|---:|---:|---:|
| All RSI<20 | 1182 | 69 | 96 | 0.133 |
| Volume-gate pass | 782 | 57 | 79 | 0.128 |
| Signal-gate pass | 55 | 19 | 23 | 0.164 |

## Power-floor checks

- Signal-gate episodes >= 10: **True** (19)
- Signal-gate distinct crash days >= 10: **True** (23)
- Observed days >= 1013.2: **False** (None)
- Largest episode share < 0.5: **True** (0.164)

This artifact removes the *sample-size* bottleneck for the cross-venue track. It does not promote OKX to Hyperliquid evidence and does not by itself establish profitability; the campaign PnL, episode-block bootstrap, crash-day permutation and portfolio placebo must still be run on this multi-year cache.
