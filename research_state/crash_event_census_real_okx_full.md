# Crash-Event Census — Real OKX 283-Day Run (Phase J1)

**Generated (UTC):** 2026-11-13T09:34:53.360163+00:00
**Provenance caveat:** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence.

## Reconciliation

| Stage | Count |
|---|---|
| RSI(21) < 20 events (all 54 admitted symbols) | 342 |
| Pass volume gate (>= $5M trailing 24h) | 187 |
| Pass bounce confirmation | 39 |
| Pass regime min-price (>= $5) | 89 |
| Pass ALL signal gates (volume + bounce + price) | 11 |
| Trades actually opened by the canonical campaign | 8 |
| Trades matched to a census event | 8 |
| Signal-gate events with no capacity explanation | 0 |

## Blocking reasons (every event, exactly one)

| Blocking reason | Events |
|---|---|
| `trade_opened` | 8 |
| `volume_gate` | 155 |
| `bounce_not_confirmed` | 159 |
| `regime_min_price` | 17 |
| `one_position_per_coin` | 3 |
| **sum** | **342** |

## Per-symbol event counts

| Symbol | Bars | Events | Vol pass | Bounce | Signal pass | Trades |
|---|---|---|---|---|---|---|
| BCH | 6792 | 29 | 19 | 3 | 3 | 2 |
| OP | 6792 | 22 | 17 | 4 | 0 | 0 |
| TRX | 6792 | 19 | 19 | 3 | 0 | 0 |
| FLOW | 6792 | 18 | 0 | 2 | 0 | 0 |
| SOL | 6792 | 16 | 16 | 5 | 5 | 3 |
| WLD | 6792 | 14 | 14 | 2 | 0 | 0 |
| COMP | 6792 | 12 | 0 | 2 | 0 | 0 |
| ETH | 6792 | 12 | 12 | 1 | 1 | 1 |
| LDO | 6792 | 12 | 0 | 0 | 0 | 0 |
| SAND | 6792 | 11 | 0 | 2 | 0 | 0 |
| STX | 6792 | 11 | 0 | 1 | 0 | 0 |
| SUI | 6792 | 11 | 11 | 2 | 0 | 0 |
| APT | 6792 | 8 | 4 | 1 | 0 | 0 |
| CHZ | 6792 | 8 | 5 | 0 | 0 | 0 |
| GALA | 6792 | 8 | 0 | 1 | 0 | 0 |
| XRP | 6792 | 8 | 8 | 1 | 0 | 0 |
| ADA | 6792 | 7 | 7 | 2 | 0 | 0 |
| DOGE | 6792 | 7 | 7 | 0 | 0 | 0 |
| FIL | 6792 | 6 | 6 | 1 | 0 | 0 |
| SEI | 6792 | 6 | 0 | 0 | 0 | 0 |
| UNI | 6792 | 6 | 5 | 0 | 0 | 0 |
| WIF | 6792 | 6 | 4 | 1 | 0 | 0 |
| XLM | 6792 | 6 | 2 | 1 | 0 | 0 |
| ALGO | 6792 | 5 | 0 | 1 | 0 | 0 |
| BONK | 6792 | 5 | 0 | 1 | 0 | 0 |
| FET | 6792 | 5 | 0 | 0 | 0 | 0 |
| PEPE | 6792 | 5 | 5 | 0 | 0 | 0 |
| SUSHI | 6792 | 5 | 0 | 0 | 0 | 0 |
| XTZ | 6792 | 5 | 0 | 0 | 0 | 0 |
| ZEC | 6792 | 5 | 5 | 0 | 0 | 0 |
| AAVE | 6792 | 4 | 3 | 0 | 0 | 0 |
| ARB | 6792 | 4 | 2 | 0 | 0 | 0 |
| INJ | 6792 | 4 | 0 | 0 | 0 | 0 |
| LINK | 6792 | 4 | 4 | 1 | 1 | 1 |
| SATS | 6792 | 4 | 0 | 0 | 0 | 0 |
| AVAX | 6792 | 3 | 3 | 1 | 1 | 1 |
| CRV | 6792 | 3 | 0 | 0 | 0 | 0 |
| DOT | 6792 | 3 | 2 | 0 | 0 | 0 |
| ORDI | 6792 | 3 | 0 | 0 | 0 | 0 |
| LTC | 6792 | 2 | 2 | 0 | 0 | 0 |
| NEAR | 6792 | 2 | 2 | 0 | 0 | 0 |
| SHIB | 6792 | 2 | 2 | 0 | 0 | 0 |
| DASH | 6792 | 1 | 0 | 0 | 0 | 0 |
| HBAR | 6792 | 1 | 0 | 0 | 0 | 0 |
| ICP | 6792 | 1 | 1 | 0 | 0 | 0 |
| JTO | 6792 | 1 | 0 | 0 | 0 | 0 |
| KSM | 6792 | 1 | 0 | 0 | 0 | 0 |
| RENDER | 6792 | 1 | 0 | 0 | 0 | 0 |
| AXS | 6792 | 0 | 0 | 0 | 0 | 0 |
| ENJ | 6792 | 0 | 0 | 0 | 0 | 0 |
| ETC | 6792 | 0 | 0 | 0 | 0 | 0 |
| JUP | 6792 | 0 | 0 | 0 | 0 | 0 |
| SNX | 6792 | 0 | 0 | 0 | 0 | 0 |
| TIA | 6792 | 0 | 0 | 0 | 0 | 0 |

## Trade-frequency gap (8 vs 85 spec)

The OKX run opened 8 trades from 11 signal-gate-passing events; 187/342 events cleared the $5M volume gate and 39 cleared bounce confirmation. The gap to the spec's 85 trades is driven by the funnel above, not by a single bug.

Caveat: same-bar multi-candidate equal-share cuts can reduce a position below its uncut size without denying it; `admitted_under_gross_cap` records that case on matched trades.
