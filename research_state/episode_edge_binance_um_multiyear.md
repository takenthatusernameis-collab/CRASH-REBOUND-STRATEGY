# C6-T3 — Crash-Episode Dependence Audit & Conditional Temporal-Edge Test (OKX Multi-Year, Cross-Venue)

**Generated (UTC):** 2026-11-15T06:05:21Z
**Provenance:** Real Binance UM exchange data, non-synthetic; CROSS-VENUE vs Hyperliquid spec; NOT Hyperliquid performance evidence.
**Verdict:** `underpowered` (CROSS-VENUE; NOT Hyperliquid evidence)

## Inputs
- Canonical total PnL: **21994.06** (42 trades)
- Signal-gate events: **64** (RSI<20 census 1204)
- Campaign: `4e65dfbff1abb6ac1e0f49d69dc6b668654ae73acd856b70cff8140b17cef38e`

## Episode clustering (98h holding-horizon link)
- Episodes: **19**, distinct crash days: **23**, symbols: **15**
- Largest episode: **14** events (21.9%)

| Episode | Window (UTC) | Events | Symbols | Distinct days |
|---|---|---|---|---|
| 0 | 2023-03-10T11:00:00Z .. 2023-03-10T11:00:00Z | 1 | LTC | 1 |
| 1 | 2023-06-05T17:00:00Z .. 2023-06-05T18:00:00Z | 2 | ETC | 1 |
| 2 | 2023-06-10T07:00:00Z .. 2023-06-10T13:00:00Z | 14 | AAVE, APT, ATOM, AVAX, COMP, ETC, KSM, LINK, LTC, SOL | 1 |
| 3 | 2023-08-15T21:00:00Z .. 2023-08-17T22:00:00Z | 4 | APT, BCH, ETH | 3 |
| 4 | 2023-09-10T05:00:00Z .. 2023-09-10T05:00:00Z | 1 | SOL | 1 |
| 5 | 2024-01-03T14:00:00Z .. 2024-01-03T14:00:00Z | 1 | LTC | 1 |
| 6 | 2024-04-12T19:00:00Z .. 2024-04-12T20:00:00Z | 6 | ATOM, AVAX, ETC, FIL, LINK | 1 |
| 7 | 2024-07-05T03:00:00Z .. 2024-07-05T07:00:00Z | 10 | APT, ATOM, BCH, DOT, ETC, KSM, LTC, UNI | 1 |
| 8 | 2024-08-05T02:00:00Z .. 2024-08-05T02:00:00Z | 2 | ETH, UNI | 1 |
| 9 | 2024-08-28T01:00:00Z .. 2024-08-28T02:00:00Z | 2 | ETH, UNI | 1 |
| 10 | 2025-01-27T07:00:00Z .. 2025-01-27T07:00:00Z | 1 | UNI | 1 |
| 11 | 2025-02-03T03:00:00Z .. 2025-02-03T03:00:00Z | 1 | ETH | 1 |
| 12 | 2025-04-06T23:00:00Z .. 2025-04-06T23:00:00Z | 1 | LTC | 1 |
| 13 | 2025-10-10T22:00:00Z .. 2025-10-11T00:00:00Z | 6 | AAVE, AVAX, COMP, KSM, SOL | 2 |
| 14 | 2026-01-19T02:00:00Z .. 2026-01-20T19:00:00Z | 4 | ETH, SOL | 2 |
| 15 | 2026-01-25T20:00:00Z .. 2026-01-25T20:00:00Z | 1 | SOL | 1 |
| 16 | 2026-01-31T18:00:00Z .. 2026-01-31T21:00:00Z | 5 | BCH, COMP, SOL | 1 |
| 17 | 2026-05-18T08:00:00Z .. 2026-05-18T08:00:00Z | 1 | BCH | 1 |
| 18 | 2026-05-23T00:00:00Z .. 2026-05-23T00:00:00Z | 1 | COMP | 1 |

## Episode-block bootstrap (resample crash episodes, not trades)
- Blocks: **19**, resamples: **20000**, seed: 20261114
- 95% CI total PnL: **[-57363.40, 122139.16]**
- Mean: **21569.27**, Median: **17956.20**, P(total PnL>0): **0.6542**
- First grid size excluding zero: **None**

## Conditional temporal-edge permutation (crash-day conditioned, real engine)
- Mode: `deterministic_seeded_draws:200_seed:20261114`
- Eligible real RSI<20 bars: **1204**, draws evaluated: **200**
- Null mean: **9840.36**, median: **8540.28**
- Canonical percentile: **81.50%**, p(placebo>=canonical): **0.1850** (37/200)
- Limitation: Exact enumeration infeasible (astronomical distinct draws); used deterministic seeded subset and reported seed/count.

## Reproduction

```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_episode_edge_okx_multiyear.py --draws 200 --seed 20261114
```
