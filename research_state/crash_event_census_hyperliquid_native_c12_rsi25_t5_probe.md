# Crash-Event Census — Real Hyperliquid-Native (Ironflow) 283-Day Run (Phase J1)

**Generated (UTC):** 2026-11-15T17:54:28.422028+00:00
**Provenance caveat:** Real Hyperliquid (Ironflow node-derived, native) exchange data, non-synthetic; node-derived (Ironflow HF, CC BY 4.0), NOT the venue's own candleSnapshot; Hyperliquid-native evidence (not cross-venue).

## Reconciliation

| Stage | Count |
|---|---|
| RSI(21) < 20 events (all 5 admitted symbols) | 202 |
| Pass volume gate (>= $5M trailing 24h) | 202 |
| Pass bounce confirmation | 33 |
| Pass regime min-price (>= $5) | 202 |
| Pass ALL signal gates (volume + bounce + price) | 33 |
| Trades actually opened by the canonical campaign | 17 |
| Trades matched to a census event | 17 |
| Signal-gate events with no capacity explanation | 0 |

## Blocking reasons (every event, exactly one)

| Blocking reason | Events |
|---|---|
| `trade_opened` | 17 |
| `bounce_not_confirmed` | 169 |
| `one_position_per_coin` | 16 |
| **sum** | **202** |

## Per-symbol event counts

| Symbol | Bars | Events | Vol pass | Bounce | Signal pass | Trades |
|---|---|---|---|---|---|---|
| SOL | 6792 | 60 | 60 | 11 | 11 | 4 |
| BTC | 6792 | 54 | 54 | 7 | 7 | 4 |
| ETH | 6792 | 48 | 48 | 10 | 10 | 5 |
| ZEC | 6792 | 28 | 28 | 4 | 4 | 3 |
| HYPE | 6792 | 12 | 12 | 1 | 1 | 1 |

## Trade-frequency gap (vs 85 spec)

The Hyperliquid-Native (Ironflow) run opened 17 trades from 33 signal-gate-passing events; 202/202 events cleared the $5M volume gate and 33 cleared bounce confirmation. The gap to the spec's 85 trades is driven by the funnel above, not by a single bug.

Caveat: same-bar multi-candidate equal-share cuts can reduce a position below its uncut size without denying it; `admitted_under_gross_cap` records that case on matched trades.
