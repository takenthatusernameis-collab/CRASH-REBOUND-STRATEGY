# C6-T3 — Crash-Episode Dependence Audit & Conditional Temporal-Edge Test (Hyperliquid-native)

**Generated (UTC):** 2026-11-16T00:52:56Z
**Provenance:** Real Hyperliquid data, non-synthetic; node-derived (Ironflow HF, CC BY 4.0), NOT the venue's own candleSnapshot; Hyperliquid-native evidence (not cross-venue).
**Verdict:** `underpowered` (Hyperliquid-native evidence)
**Config (config-matched real engine):** RSI<20, target 9%, rebound target 9%

## Inputs
- Canonical total PnL: **8914.33** (7 trades)
- Signal-gate events: **9** (RSI<20 census 661)
- Campaign: `7d32720119597124f152b437012e8cdb88636bf0dedd72f25d4a69806676cdd1`

## Episode clustering (98h holding-horizon link)
- Episodes: **3**, distinct crash days: **4**, symbols: **4**
- Largest episode: **5** events (55.6%)

| Episode | Window (UTC) | Events | Symbols | Distinct days |
|---|---|---|---|---|
| 0 | 2026-01-19T03:00:00Z .. 2026-01-20T19:00:00Z | 3 | ETH, SOL | 2 |
| 1 | 2026-01-25T20:00:00Z .. 2026-01-25T20:00:00Z | 1 | SOL | 1 |
| 2 | 2026-01-31T18:00:00Z .. 2026-01-31T21:00:00Z | 5 | BCH, BTC, ETH, SOL | 1 |

## Episode-block bootstrap (resample crash episodes, not trades)
- Blocks: **3**, resamples: **20000**, seed: 20261116
- 95% CI total PnL: **[-1143.66, 17547.24]**
- Mean: **8903.68**, Median: **8914.33**, P(total PnL>0): **0.9638**
- First grid size excluding zero: **4**

## Conditional temporal-edge permutation (crash-day conditioned, real engine)
- Mode: `deterministic_seeded_draws:20000_seed:20261116`
- Eligible real RSI<20 bars: **661**, draws evaluated: **20000**
- Null mean: **2560.72**, median: **2475.77**
- Canonical percentile: **96.41%**, p(placebo>=canonical): **0.0360** (719/20000)
- Limitation: Exact enumeration infeasible (astronomical distinct draws); used deterministic seeded subset and reported seed/count.

## Reproduction

```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_episode_edge_okx_multiyear.py --draws 20000 --seed 20261116 --cache-dir research_state/cache/hyperliquid_ironflow_wide_20261115T234000Z --universe research_state/universe_hyperliquid_ironflow_wide_20261115T225100Z.json --census research_state/crash_event_census_hyperliquid_ironflow_wide_20261115T234000Z.json --campaign research_state/campaign_results_real_okx_multiyear.json --venue-label 'Hyperliquid' --out episode_edge_hyperliquid_ironflow_wide_20261115T234000Z
```
