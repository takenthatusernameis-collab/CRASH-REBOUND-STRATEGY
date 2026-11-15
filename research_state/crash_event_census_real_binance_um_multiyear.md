# Crash-Event Census — Real OKX 283-Day Run (Phase J1)

**Generated (UTC):** 2026-11-15T02:27:55.613965+00:00
**Provenance caveat:** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence.

## Reconciliation

| Stage | Count |
|---|---|
| RSI(21) < 20 events (all 33 admitted symbols) | 1204 |
| Pass volume gate (>= $5M trailing 24h) | 1198 |
| Pass bounce confirmation | 167 |
| Pass regime min-price (>= $5) | 485 |
| Pass ALL signal gates (volume + bounce + price) | 64 |
| Trades actually opened by the canonical campaign | 42 |
| Trades matched to a census event | 42 |
| Signal-gate events with no capacity explanation | 11 |

## Blocking reasons (every event, exactly one)

| Blocking reason | Events |
|---|---|
| `trade_opened` | 42 |
| `volume_gate` | 6 |
| `bounce_not_confirmed` | 1031 |
| `regime_min_price` | 103 |
| `one_position_per_coin` | 11 |
| `portfolio_admission` | 11 |
| **sum** | **1204** |

## Per-symbol event counts

| Symbol | Bars | Events | Vol pass | Bounce | Signal pass | Trades |
|---|---|---|---|---|---|---|
| ETH | 32808 | 67 | 67 | 5 | 5 | 5 |
| BCH | 32808 | 62 | 62 | 5 | 5 | 3 |
| SAND | 32808 | 61 | 61 | 11 | 0 | 0 |
| APT | 32808 | 54 | 54 | 6 | 5 | 2 |
| OP | 32808 | 54 | 54 | 11 | 0 | 0 |
| TRX | 32808 | 54 | 54 | 6 | 0 | 0 |
| SUSHI | 32808 | 47 | 45 | 3 | 0 | 0 |
| DOGE | 32808 | 45 | 45 | 5 | 0 | 0 |
| COMP | 32808 | 43 | 43 | 8 | 8 | 3 |
| LTC | 32808 | 43 | 43 | 7 | 7 | 4 |
| UNI | 32808 | 42 | 42 | 5 | 4 | 4 |
| XTZ | 32808 | 41 | 41 | 5 | 0 | 0 |
| FIL | 32808 | 40 | 40 | 8 | 2 | 1 |
| ADA | 32808 | 36 | 36 | 8 | 0 | 0 |
| MANA | 32808 | 36 | 36 | 7 | 0 | 0 |
| XRP | 32808 | 34 | 34 | 5 | 0 | 0 |
| BAT | 32808 | 33 | 30 | 5 | 0 | 0 |
| SOL | 32808 | 32 | 32 | 8 | 8 | 6 |
| ATOM | 32808 | 31 | 31 | 7 | 4 | 2 |
| AVAX | 32808 | 30 | 30 | 3 | 3 | 2 |
| DOT | 32808 | 29 | 29 | 7 | 1 | 1 |
| GRT | 32808 | 29 | 29 | 2 | 0 | 0 |
| KSM | 32808 | 29 | 28 | 3 | 3 | 2 |
| LINK | 32808 | 29 | 29 | 2 | 2 | 2 |
| AAVE | 32808 | 28 | 28 | 2 | 2 | 2 |
| ETC | 32808 | 28 | 28 | 5 | 5 | 3 |
| SHIB | 32808 | 28 | 28 | 3 | 0 | 0 |
| CRV | 32808 | 25 | 25 | 5 | 0 | 0 |
| THETA | 32808 | 23 | 23 | 2 | 0 | 0 |
| SNX | 32808 | 22 | 22 | 2 | 0 | 0 |
| ALGO | 32808 | 18 | 18 | 3 | 0 | 0 |
| NEAR | 32808 | 16 | 16 | 1 | 0 | 0 |
| XLM | 32808 | 15 | 15 | 2 | 0 | 0 |

## Trade-frequency gap (8 vs 85 spec)

The OKX run opened 42 trades from 64 signal-gate-passing events; 1198/1204 events cleared the $5M volume gate and 167 cleared bounce confirmation. The gap to the spec's 85 trades is driven by the funnel above, not by a single bug.

Caveat: same-bar multi-candidate equal-share cuts can reduce a position below its uncut size without denying it; `admitted_under_gross_cap` records that case on matched trades.
