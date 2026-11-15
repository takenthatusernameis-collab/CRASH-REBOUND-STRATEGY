# Crash-Event Census — Real Hyperliquid-Native (Ironflow) 283-Day Run (Phase J1)

**Generated (UTC):** 2026-11-15T15:52:26.731441+00:00
**Provenance caveat:** Real Hyperliquid (Ironflow node-derived, native) exchange data, non-synthetic; node-derived (Ironflow HF, CC BY 4.0), NOT the venue's own candleSnapshot; Hyperliquid-native evidence (not cross-venue).

## Reconciliation

| Stage | Count |
|---|---|
| RSI(21) < 20 events (all 5 admitted symbols) | 43 |
| Pass volume gate (>= $5M trailing 24h) | 43 |
| Pass bounce confirmation | 7 |
| Pass regime min-price (>= $5) | 43 |
| Pass ALL signal gates (volume + bounce + price) | 7 |
| Trades actually opened by the canonical campaign | 6 |
| Trades matched to a census event | 6 |
| Signal-gate events with no capacity explanation | 0 |

## Blocking reasons (every event, exactly one)

| Blocking reason | Events |
|---|---|
| `trade_opened` | 6 |
| `bounce_not_confirmed` | 36 |
| `one_position_per_coin` | 1 |
| **sum** | **43** |

## Per-symbol event counts

| Symbol | Bars | Events | Vol pass | Bounce | Signal pass | Trades |
|---|---|---|---|---|---|---|
| SOL | 6792 | 16 | 16 | 4 | 4 | 3 |
| ETH | 6792 | 12 | 12 | 2 | 2 | 2 |
| BTC | 6792 | 10 | 10 | 1 | 1 | 1 |
| ZEC | 6792 | 5 | 5 | 0 | 0 | 0 |
| HYPE | 6792 | 0 | 0 | 0 | 0 | 0 |

## Trade-frequency gap (vs 85 spec)

The Hyperliquid-Native (Ironflow) run opened 6 trades from 7 signal-gate-passing events; 43/43 events cleared the $5M volume gate and 7 cleared bounce confirmation. The gap to the spec's 85 trades is driven by the funnel above, not by a single bug.

Caveat: same-bar multi-candidate equal-share cuts can reduce a position below its uncut size without denying it; `admitted_under_gross_cap` records that case on matched trades.
