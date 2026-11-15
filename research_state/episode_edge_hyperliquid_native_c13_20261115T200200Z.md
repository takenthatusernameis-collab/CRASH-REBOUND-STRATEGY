# C6-T3 — Crash-Episode Dependence Audit & Conditional Temporal-Edge Test (Hyperliquid-native)

**Generated (UTC):** 2026-11-15T20:03:03Z
**Provenance:** Real Hyperliquid (Ironflow node-derived, native) data, non-synthetic; node-derived (Ironflow HF, CC BY 4.0), NOT the venue's own candleSnapshot; Hyperliquid-native evidence (not cross-venue).
**Verdict:** `underpowered` (Hyperliquid-native evidence)
**Config (config-matched real engine):** RSI<25, target 9%, rebound target 9%

## Inputs
- Canonical total PnL: **23244.22** (17 trades)
- Signal-gate events: **33** (RSI<25 census 202)
- Campaign: `72d98f0d1664ed4c53020ac37ec34ded2cd13257e4b3489c4eec43db56caf9a5`

## Episode clustering (98h holding-horizon link)
- Episodes: **10**, distinct crash days: **12**, symbols: **5**
- Largest episode: **9** events (27.3%)

| Episode | Window (UTC) | Events | Symbols | Distinct days |
|---|---|---|---|---|
| 0 | 2026-01-08T11:00:00Z .. 2026-01-08T12:00:00Z | 2 | ZEC | 1 |
| 1 | 2026-01-19T03:00:00Z .. 2026-01-21T01:00:00Z | 9 | ETH, SOL | 3 |
| 2 | 2026-01-25T20:00:00Z .. 2026-01-25T23:00:00Z | 5 | ETH, SOL, ZEC | 1 |
| 3 | 2026-01-31T20:00:00Z .. 2026-01-31T22:00:00Z | 8 | BTC, ETH, SOL, ZEC | 1 |
| 4 | 2026-02-05T22:00:00Z .. 2026-02-05T22:00:00Z | 1 | BTC | 1 |
| 5 | 2026-02-23T02:00:00Z .. 2026-02-23T05:00:00Z | 2 | ETH, SOL | 1 |
| 6 | 2026-03-27T14:00:00Z .. 2026-03-27T18:00:00Z | 2 | BTC | 1 |
| 7 | 2026-05-18T01:00:00Z .. 2026-05-18T01:00:00Z | 1 | ETH | 1 |
| 8 | 2026-06-02T20:00:00Z .. 2026-06-02T23:00:00Z | 2 | BTC | 1 |
| 9 | 2026-07-17T06:00:00Z .. 2026-07-17T06:00:00Z | 1 | HYPE | 1 |

## Episode-block bootstrap (resample crash episodes, not trades)
- Blocks: **10**, resamples: **20000**, seed: 20261115
- 95% CI total PnL: **[-22799.52, 79978.91]**
- Mean: **23254.48**, Median: **21441.08**, P(total PnL>0): **0.8030**
- First grid size excluding zero: **None**

## Conditional temporal-edge permutation (crash-day conditioned, real engine)
- Mode: `deterministic_seeded_draws:200_seed:20261115`
- Eligible real RSI<25 bars: **202**, draws evaluated: **200**
- Null mean: **5726.37**, median: **3322.94**
- Canonical percentile: **91.50%**, p(placebo>=canonical): **0.0850** (17/200)
- Limitation: Exact enumeration infeasible (astronomical distinct draws); used deterministic seeded subset and reported seed/count.

## Reproduction

```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_episode_edge_okx_multiyear.py --draws 200 --seed 20261115 --cache-dir research_state/cache/hyperliquid_ironflow_native_20251220_20260928 --universe research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json --census research_state/crash_event_census_hyperliquid_native_c12_rsi25_t9_20261115T180000Z.json --campaign research_state/campaign_results_real_hyperliquid_native_c12_rsi25_t9_20261115T180000Z.json --venue-label 'Hyperliquid (Ironflow node-derived, native)' --out episode_edge_hyperliquid_native_c13_20261115T200200ZZ --rsi-threshold 25
```
