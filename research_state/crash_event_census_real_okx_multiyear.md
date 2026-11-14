# Crash-Event Census — Real OKX 283-Day Run (Phase J1)

**Generated (UTC):** 2026-11-14T23:42:25.143012+00:00
**Provenance caveat:** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence.

## Reconciliation

| Stage | Count |
|---|---|
| RSI(21) < 20 events (all 34 admitted symbols) | 1182 |
| Pass volume gate (>= $5M trailing 24h) | 782 |
| Pass bounce confirmation | 177 |
| Pass regime min-price (>= $5) | 461 |
| Pass ALL signal gates (volume + bounce + price) | 55 |
| Trades actually opened by the canonical campaign | 42 |
| Trades matched to a census event | 42 |
| Signal-gate events with no capacity explanation | 4 |

## Blocking reasons (every event, exactly one)

| Blocking reason | Events |
|---|---|
| `trade_opened` | 42 |
| `volume_gate` | 400 |
| `bounce_not_confirmed` | 658 |
| `regime_min_price` | 69 |
| `one_position_per_coin` | 9 |
| `portfolio_admission` | 4 |
| **sum** | **1182** |

## Per-symbol event counts

| Symbol | Bars | Events | Vol pass | Bounce | Signal pass | Trades |
|---|---|---|---|---|---|---|
| ETH | 32808 | 65 | 65 | 5 | 5 | 5 |
| SAND | 32808 | 63 | 21 | 12 | 0 | 0 |
| BCH | 32808 | 59 | 47 | 5 | 5 | 4 |
| TRX | 32808 | 55 | 53 | 9 | 0 | 0 |
| APT | 32808 | 54 | 48 | 7 | 5 | 3 |
| OP | 32808 | 52 | 45 | 10 | 0 | 0 |
| DOGE | 32808 | 44 | 44 | 3 | 0 | 0 |
| LTC | 32808 | 43 | 43 | 7 | 7 | 5 |
| SUSHI | 32808 | 41 | 12 | 3 | 0 | 0 |
| FIL | 32808 | 40 | 40 | 8 | 2 | 1 |
| XTZ | 32808 | 40 | 2 | 2 | 0 | 0 |
| UNI | 32808 | 39 | 34 | 4 | 3 | 3 |
| COMP | 32808 | 36 | 0 | 5 | 0 | 0 |
| ADA | 32808 | 33 | 32 | 6 | 0 | 0 |
| SOL | 32808 | 33 | 33 | 7 | 7 | 4 |
| BAT | 32808 | 32 | 0 | 6 | 0 | 0 |
| LINK | 32808 | 31 | 30 | 5 | 5 | 5 |
| MANA | 32808 | 31 | 2 | 6 | 0 | 0 |
| XRP | 32808 | 31 | 31 | 6 | 0 | 0 |
| ATOM | 32808 | 30 | 25 | 7 | 4 | 2 |
| DOT | 32808 | 30 | 22 | 9 | 1 | 1 |
| SHIB | 32808 | 30 | 27 | 4 | 0 | 0 |
| AVAX | 32808 | 29 | 27 | 4 | 4 | 4 |
| KSM | 32808 | 27 | 0 | 5 | 0 | 0 |
| GRT | 32808 | 26 | 1 | 3 | 0 | 0 |
| THETA | 32808 | 26 | 4 | 4 | 0 | 0 |
| CRV | 32808 | 25 | 21 | 4 | 0 | 0 |
| ETC | 32808 | 25 | 20 | 5 | 5 | 3 |
| AAVE | 32808 | 24 | 19 | 3 | 2 | 2 |
| ALGO | 32808 | 20 | 5 | 4 | 0 | 0 |
| SNX | 32808 | 20 | 8 | 4 | 0 | 0 |
| XLM | 32808 | 18 | 6 | 1 | 0 | 0 |
| MINA | 32808 | 16 | 2 | 4 | 0 | 0 |
| NEAR | 32808 | 14 | 13 | 0 | 0 | 0 |

## Trade-frequency gap (8 vs 85 spec)

The OKX run opened 42 trades from 55 signal-gate-passing events; 782/1182 events cleared the $5M volume gate and 177 cleared bounce confirmation. The gap to the spec's 85 trades is driven by the funnel above, not by a single bug.

Caveat: same-bar multi-candidate equal-share cuts can reduce a position below its uncut size without denying it; `admitted_under_gross_cap` records that case on matched trades.
