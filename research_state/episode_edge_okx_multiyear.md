# C6-T3 — Crash-Episode Dependence Audit & Conditional Temporal-Edge Test (OKX Multi-Year, Cross-Venue)

**Generated (UTC):** 2026-11-15T00:35:31Z
**Provenance:** Real OKX exchange data, non-synthetic; CROSS-VENUE vs Hyperliquid spec; NOT Hyperliquid performance evidence.
**Verdict:** `underpowered` (CROSS-VENUE; NOT Hyperliquid evidence)

## Inputs
- Canonical total PnL: **18220.86** (42 trades)
- Signal-gate events: **55** (RSI<20 census 1182)
- Campaign: `7d32720119597124f152b437012e8cdb88636bf0dedd72f25d4a69806676cdd1`

## Episode clustering (98h holding-horizon link)
- Episodes: **19**, distinct crash days: **23**, symbols: **13**
- Largest episode: **9** events (16.4%)

| Episode | Window (UTC) | Events | Symbols | Distinct days |
|---|---|---|---|---|
| 0 | 2023-03-10T11:00:00Z .. 2023-03-10T11:00:00Z | 1 | LTC | 1 |
| 1 | 2023-06-05T17:00:00Z .. 2023-06-05T18:00:00Z | 2 | ETC | 1 |
| 2 | 2023-06-10T07:00:00Z .. 2023-06-10T10:00:00Z | 8 | APT, ATOM, AVAX, ETC, LINK, LTC, SOL | 1 |
| 3 | 2023-08-15T21:00:00Z .. 2023-08-17T22:00:00Z | 4 | APT, BCH, ETH | 3 |
| 4 | 2023-09-10T05:00:00Z .. 2023-09-10T05:00:00Z | 1 | SOL | 1 |
| 5 | 2024-01-03T14:00:00Z .. 2024-01-03T14:00:00Z | 1 | LTC | 1 |
| 6 | 2024-04-12T19:00:00Z .. 2024-04-12T20:00:00Z | 6 | ATOM, AVAX, ETC, FIL, LINK | 1 |
| 7 | 2024-07-05T03:00:00Z .. 2024-07-05T07:00:00Z | 9 | APT, ATOM, BCH, DOT, ETC, LTC, UNI | 1 |
| 8 | 2024-08-05T02:00:00Z .. 2024-08-05T02:00:00Z | 2 | ETH, UNI | 1 |
| 9 | 2024-08-28T01:00:00Z .. 2024-08-28T01:00:00Z | 1 | ETH | 1 |
| 10 | 2025-01-27T07:00:00Z .. 2025-01-27T07:00:00Z | 1 | UNI | 1 |
| 11 | 2025-02-03T03:00:00Z .. 2025-02-03T03:00:00Z | 2 | APT, ETH | 1 |
| 12 | 2025-04-06T23:00:00Z .. 2025-04-06T23:00:00Z | 1 | LTC | 1 |
| 13 | 2025-09-22T08:00:00Z .. 2025-09-22T08:00:00Z | 2 | AAVE, LINK | 1 |
| 14 | 2025-10-10T22:00:00Z .. 2025-10-11T00:00:00Z | 3 | AAVE, AVAX, LINK | 2 |
| 15 | 2026-01-19T02:00:00Z .. 2026-01-20T19:00:00Z | 4 | ETH, SOL | 2 |
| 16 | 2026-01-25T20:00:00Z .. 2026-01-25T20:00:00Z | 2 | LINK, SOL | 1 |
| 17 | 2026-01-31T18:00:00Z .. 2026-01-31T21:00:00Z | 4 | AVAX, BCH, SOL | 1 |
| 18 | 2026-05-18T08:00:00Z .. 2026-05-18T08:00:00Z | 1 | BCH | 1 |

## Episode-block bootstrap (resample crash episodes, not trades)
- Blocks: **19**, resamples: **20000**, seed: 20261114
- 95% CI total PnL: **[-50660.49, 99295.03]**
- Mean: **18156.53**, Median: **15844.59**, P(total PnL>0): **0.6649**
- First grid size excluding zero: **None**

## Conditional temporal-edge permutation (crash-day conditioned, real engine)
- Mode: `deterministic_seeded_draws:20_seed:20261114`
- Eligible real RSI<20 bars: **1182**, draws evaluated: **20**
- Null mean: **6324.41**, median: **6871.12**
- Canonical percentile: **90.00%**, p(placebo>=canonical): **0.1000** (2/20)
- Limitation: Exact enumeration infeasible (astronomical distinct draws); used deterministic seeded subset and reported seed/count.

## Reproduction

```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_episode_edge_okx_multiyear.py --draws 200 --seed 20261114
```
