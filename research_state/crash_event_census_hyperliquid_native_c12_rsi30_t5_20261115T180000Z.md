# Crash-Event Census — Real Hyperliquid-Native (Ironflow) 283-Day Run (Phase J1)

**Generated (UTC):** 2026-11-15T18:03:46.910671+00:00
**Provenance caveat:** Real Hyperliquid (Ironflow node-derived, native) exchange data, non-synthetic; node-derived (Ironflow HF, CC BY 4.0), NOT the venue's own candleSnapshot; Hyperliquid-native evidence (not cross-venue).

## Reconciliation

| Stage | Count |
|---|---|
| RSI(21) < 20 events (all 5 admitted symbols) | 671 |
| Pass volume gate (>= $5M trailing 24h) | 671 |
| Pass bounce confirmation | 148 |
| Pass regime min-price (>= $5) | 671 |
| Pass ALL signal gates (volume + bounce + price) | 148 |
| Trades actually opened by the canonical campaign | 58 |
| Trades matched to a census event | 58 |
| Signal-gate events with no capacity explanation | 10 |

## Blocking reasons (every event, exactly one)

| Blocking reason | Events |
|---|---|
| `trade_opened` | 58 |
| `bounce_not_confirmed` | 523 |
| `one_position_per_coin` | 80 |
| `portfolio_admission` | 10 |
| **sum** | **671** |

## Per-symbol event counts

| Symbol | Bars | Events | Vol pass | Bounce | Signal pass | Trades |
|---|---|---|---|---|---|---|
| ETH | 6792 | 179 | 179 | 48 | 48 | 16 |
| BTC | 6792 | 158 | 158 | 35 | 35 | 13 |
| SOL | 6792 | 147 | 147 | 33 | 33 | 12 |
| ZEC | 6792 | 116 | 116 | 19 | 19 | 12 |
| HYPE | 6792 | 71 | 71 | 13 | 13 | 5 |

## Trade-frequency gap (vs 85 spec)

The Hyperliquid-Native (Ironflow) run opened 58 trades from 148 signal-gate-passing events; 671/671 events cleared the $5M volume gate and 148 cleared bounce confirmation. The gap to the spec's 85 trades is driven by the funnel above, not by a single bug.

Caveat: same-bar multi-candidate equal-share cuts can reduce a position below its uncut size without denying it; `admitted_under_gross_cap` records that case on matched trades.
