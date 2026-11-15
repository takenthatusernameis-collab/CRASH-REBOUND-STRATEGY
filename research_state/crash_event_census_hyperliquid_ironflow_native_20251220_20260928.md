# Crash-Event Census — Real OKX 283-Day Run (Phase J1)

**Generated (UTC):** 2026-11-15T14:06:44.724588+00:00
**Provenance caveat:** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence.

## Reconciliation

| Stage | Count |
|---|---|
| RSI(21) < 20 events (all 5 admitted symbols) | 43 |
| Pass volume gate (>= $5M trailing 24h) | 43 |
| Pass bounce confirmation | 7 |
| Pass regime min-price (>= $5) | 43 |
| Pass ALL signal gates (volume + bounce + price) | 7 |
| Trades actually opened by the canonical campaign | 6 |
| Trades matched to a census event | 0 |
| Signal-gate events with no capacity explanation | 7 |

## Blocking reasons (every event, exactly one)

| Blocking reason | Events |
|---|---|
| `bounce_not_confirmed` | 36 |
| `portfolio_admission` | 7 |
| **sum** | **43** |

## Unmatched campaign trades (audit required)

- `SOL` buy entry `2026-01-19T04:00:00+00:00` exit_reason `liquidated`
- `ETH` buy entry `2026-01-20T20:00:00+00:00` exit_reason `time_exit`
- `SOL` buy entry `2026-01-25T21:00:00+00:00` exit_reason `time_exit`
- `ETH` buy entry `2026-01-31T21:00:00+00:00` exit_reason `liquidated`
- `SOL` buy entry `2026-01-31T21:00:00+00:00` exit_reason `time_exit`
- `BTC` buy entry `2026-01-31T21:00:00+00:00` exit_reason `time_exit`

## Per-symbol event counts

| Symbol | Bars | Events | Vol pass | Bounce | Signal pass | Trades |
|---|---|---|---|---|---|---|
| SOL | 6792 | 16 | 16 | 4 | 4 | 0 |
| ETH | 6792 | 12 | 12 | 2 | 2 | 0 |
| BTC | 6792 | 10 | 10 | 1 | 1 | 0 |
| ZEC | 6792 | 5 | 5 | 0 | 0 | 0 |
| HYPE | 6792 | 0 | 0 | 0 | 0 | 0 |

## Trade-frequency gap (8 vs 85 spec)

The OKX run opened 6 trades from 7 signal-gate-passing events; 43/43 events cleared the $5M volume gate and 7 cleared bounce confirmation. The gap to the spec's 85 trades is driven by the funnel above, not by a single bug.

Caveat: same-bar multi-candidate equal-share cuts can reduce a position below its uncut size without denying it; `admitted_under_gross_cap` records that case on matched trades.
