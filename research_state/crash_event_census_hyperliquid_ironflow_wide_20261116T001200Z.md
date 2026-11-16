# Crash-Event Census — Real Hyperliquid-Native (Ironflow) 283-Day Run (Phase J1)

**Generated (UTC):** 2026-11-16T00:14:47.339508+00:00
**Provenance caveat:** Real Hyperliquid (Ironflow node-derived, native) exchange data, non-synthetic; node-derived (Ironflow HF, CC BY 4.0), NOT the venue's own candleSnapshot; Hyperliquid-native evidence (not cross-venue).

## Reconciliation

| Stage | Count |
|---|---|
| RSI(21) < 20 events (all 113 admitted symbols) | 661 |
| Pass volume gate (>= $5M trailing 24h) | 235 |
| Pass bounce confirmation | 71 |
| Pass regime min-price (>= $5) | 119 |
| Pass ALL signal gates (volume + bounce + price) | 9 |
| Trades actually opened by the canonical campaign | 7 |
| Trades matched to a census event | 7 |
| Signal-gate events with no capacity explanation | 0 |

## Blocking reasons (every event, exactly one)

| Blocking reason | Events |
|---|---|
| `trade_opened` | 7 |
| `volume_gate` | 426 |
| `bounce_not_confirmed` | 209 |
| `regime_min_price` | 17 |
| `one_position_per_coin` | 2 |
| **sum** | **661** |

## Per-symbol event counts

| Symbol | Bars | Events | Vol pass | Bounce | Signal pass | Trades |
|---|---|---|---|---|---|---|
| BCH | 6792 | 29 | 9 | 3 | 2 | 1 |
| OP | 6792 | 24 | 14 | 5 | 0 | 0 |
| PAXG | 6792 | 23 | 9 | 3 | 0 | 0 |
| TRX | 6792 | 19 | 9 | 2 | 0 | 0 |
| CAKE | 6792 | 18 | 0 | 2 | 0 | 0 |
| TRUMP | 6792 | 18 | 18 | 3 | 0 | 0 |
| MNT | 6792 | 17 | 0 | 2 | 0 | 0 |
| SOL | 6792 | 16 | 16 | 4 | 4 | 3 |
| BERA | 6792 | 14 | 0 | 2 | 0 | 0 |
| LDO | 6792 | 13 | 1 | 0 | 0 | 0 |
| STX | 6792 | 13 | 0 | 3 | 0 | 0 |
| SUI | 6792 | 13 | 13 | 2 | 0 | 0 |
| XPL | 6792 | 13 | 12 | 2 | 0 | 0 |
| ETH | 6792 | 12 | 12 | 2 | 2 | 2 |
| KAITO | 6792 | 12 | 10 | 1 | 0 | 0 |
| WLD | 6792 | 12 | 10 | 1 | 0 | 0 |
| EIGEN | 6792 | 11 | 0 | 3 | 0 | 0 |
| SAND | 6792 | 11 | 0 | 1 | 0 | 0 |
| WLFI | 6792 | 11 | 6 | 1 | 0 | 0 |
| BTC | 6792 | 10 | 10 | 1 | 1 | 1 |
| ETHFI | 6792 | 10 | 0 | 0 | 0 | 0 |
| YGG | 6792 | 10 | 0 | 1 | 0 | 0 |
| DOGE | 6792 | 9 | 9 | 1 | 0 | 0 |
| MON | 6792 | 9 | 9 | 1 | 0 | 0 |
| BANANA | 6792 | 8 | 0 | 0 | 0 | 0 |
| CC | 6792 | 8 | 0 | 0 | 0 | 0 |
| LAYER | 6792 | 8 | 0 | 1 | 0 | 0 |
| PENDLE | 6792 | 8 | 0 | 2 | 0 | 0 |
| RUNE | 6792 | 8 | 2 | 0 | 0 | 0 |
| XRP | 6792 | 8 | 8 | 1 | 0 | 0 |
| APT | 6792 | 7 | 1 | 1 | 0 | 0 |
| VVV | 6792 | 7 | 0 | 1 | 0 | 0 |
| ADA | 6792 | 6 | 6 | 2 | 0 | 0 |
| APE | 6792 | 6 | 0 | 1 | 0 | 0 |
| BIO | 6792 | 6 | 0 | 1 | 0 | 0 |
| BNB | 6792 | 6 | 5 | 0 | 0 | 0 |
| ME | 6792 | 6 | 0 | 1 | 0 | 0 |
| MET | 6792 | 6 | 0 | 1 | 0 | 0 |
| PENGU | 6792 | 6 | 3 | 1 | 0 | 0 |
| XLM | 6792 | 6 | 0 | 1 | 0 | 0 |
| ZK | 6792 | 6 | 0 | 0 | 0 | 0 |
| ZORA | 6792 | 6 | 0 | 0 | 0 | 0 |
| AAVE | 6792 | 5 | 4 | 0 | 0 | 0 |
| AR | 6792 | 5 | 0 | 0 | 0 | 0 |
| BLUR | 6792 | 5 | 0 | 1 | 0 | 0 |
| CFX | 6792 | 5 | 0 | 2 | 0 | 0 |
| FET | 6792 | 5 | 0 | 0 | 0 | 0 |
| FIL | 6792 | 5 | 0 | 1 | 0 | 0 |
| KBONK | 6792 | 5 | 1 | 1 | 0 | 0 |
| ORDI | 6792 | 5 | 0 | 0 | 0 | 0 |
| PNUT | 6792 | 5 | 0 | 1 | 0 | 0 |
| RESOLV | 6792 | 5 | 0 | 0 | 0 | 0 |
| SOPH | 6792 | 5 | 0 | 0 | 0 | 0 |
| SUPER | 6792 | 5 | 0 | 1 | 0 | 0 |
| UNI | 6792 | 5 | 1 | 0 | 0 | 0 |
| WIF | 6792 | 5 | 0 | 1 | 0 | 0 |
| ZEC | 6792 | 5 | 5 | 0 | 0 | 0 |
| ZRO | 6792 | 5 | 5 | 0 | 0 | 0 |
| 0G | 6792 | 4 | 0 | 0 | 0 | 0 |
| GRASS | 6792 | 4 | 3 | 0 | 0 | 0 |
| INJ | 6792 | 4 | 0 | 0 | 0 | 0 |
| KPEPE | 6792 | 4 | 4 | 0 | 0 | 0 |
| ONDO | 6792 | 4 | 0 | 0 | 0 | 0 |
| POPCAT | 6792 | 4 | 0 | 0 | 0 | 0 |
| SEI | 6792 | 4 | 0 | 0 | 0 | 0 |
| STRK | 6792 | 4 | 0 | 1 | 0 | 0 |
| ALGO | 6792 | 3 | 0 | 0 | 0 | 0 |
| ANIME | 6792 | 3 | 0 | 0 | 0 | 0 |
| ARB | 6792 | 3 | 0 | 0 | 0 | 0 |
| ASTER | 6792 | 3 | 1 | 0 | 0 | 0 |
| AVAX | 6792 | 3 | 2 | 0 | 0 | 0 |
| BABY | 6792 | 3 | 0 | 1 | 0 | 0 |
| CRV | 6792 | 3 | 3 | 0 | 0 | 0 |
| DOT | 6792 | 3 | 0 | 0 | 0 | 0 |
| ENA | 6792 | 3 | 3 | 0 | 0 | 0 |
| FARTCOIN | 6792 | 3 | 3 | 0 | 0 | 0 |
| GMT | 6792 | 3 | 0 | 0 | 0 | 0 |
| LINK | 6792 | 3 | 3 | 0 | 0 | 0 |
| MOODENG | 6792 | 3 | 0 | 0 | 0 | 0 |
| MORPHO | 6792 | 3 | 0 | 0 | 0 | 0 |
| PEOPLE | 6792 | 3 | 0 | 0 | 0 | 0 |
| POL | 6792 | 3 | 0 | 0 | 0 | 0 |
| PYTH | 6792 | 3 | 0 | 0 | 0 | 0 |
| STABLE | 6792 | 3 | 0 | 0 | 0 | 0 |
| VIRTUAL | 6792 | 3 | 2 | 0 | 0 | 0 |
| ETC | 6792 | 2 | 0 | 0 | 0 | 0 |
| HYPER | 6792 | 2 | 0 | 0 | 0 | 0 |
| ICP | 6792 | 2 | 0 | 0 | 0 | 0 |
| IO | 6792 | 2 | 0 | 1 | 0 | 0 |
| JUP | 6792 | 2 | 0 | 0 | 0 | 0 |
| KSHIB | 6792 | 2 | 0 | 0 | 0 | 0 |
| LTC | 6792 | 2 | 2 | 0 | 0 | 0 |
| ACE | 6792 | 1 | 0 | 0 | 0 | 0 |
| AERO | 6792 | 1 | 0 | 0 | 0 | 0 |
| HBAR | 6792 | 1 | 0 | 0 | 0 | 0 |
| JTO | 6792 | 1 | 0 | 0 | 0 | 0 |
| MELANIA | 6792 | 1 | 0 | 0 | 0 | 0 |
| NEAR | 6792 | 1 | 1 | 0 | 0 | 0 |
| PROVE | 6792 | 1 | 0 | 0 | 0 | 0 |
| RENDER | 6792 | 1 | 0 | 0 | 0 | 0 |
| SKY | 6792 | 1 | 0 | 0 | 0 | 0 |
| AIXBT | 6792 | 0 | 0 | 0 | 0 | 0 |
| AVNT | 6792 | 0 | 0 | 0 | 0 | 0 |
| HYPE | 6792 | 0 | 0 | 0 | 0 | 0 |
| INIT | 6792 | 0 | 0 | 0 | 0 | 0 |
| MANTA | 6792 | 0 | 0 | 0 | 0 | 0 |
| NIL | 6792 | 0 | 0 | 0 | 0 | 0 |
| PUMP | 6792 | 0 | 0 | 0 | 0 | 0 |
| REZ | 6792 | 0 | 0 | 0 | 0 | 0 |
| SPX | 6792 | 0 | 0 | 0 | 0 | 0 |
| TAO | 6792 | 0 | 0 | 0 | 0 | 0 |
| TIA | 6792 | 0 | 0 | 0 | 0 | 0 |
| ZEN | 6792 | 0 | 0 | 0 | 0 | 0 |

## Trade-frequency gap (vs 85 spec)

The Hyperliquid-Native (Ironflow) run opened 7 trades from 9 signal-gate-passing events; 235/661 events cleared the $5M volume gate and 71 cleared bounce confirmation. The gap to the spec's 85 trades is driven by the funnel above, not by a single bug.

Caveat: same-bar multi-candidate equal-share cuts can reduce a position below its uncut size without denying it; `admitted_under_gross_cap` records that case on matched trades.
