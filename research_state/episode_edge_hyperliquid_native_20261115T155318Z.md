# C6-T3 — Crash-Episode Dependence Audit & Conditional Temporal-Edge Test (Hyperliquid-native)

**Generated (UTC):** 2026-11-15T15:53:54Z
**Provenance:** Real Hyperliquid (Ironflow node-derived, native) data, non-synthetic; node-derived (Ironflow HF, CC BY 4.0), NOT the venue's own candleSnapshot; Hyperliquid-native evidence (not cross-venue).
**Verdict:** `underpowered` (Hyperliquid-native evidence)

## Inputs
- Canonical total PnL: **4292.50** (6 trades)
- Signal-gate events: **7** (RSI<20 census 43)
- Campaign: `f90d18eed27263b1edf918346865b6fb1f4be849e5a8ba39750d1971c7470665`

## Episode clustering (98h holding-horizon link)
- Episodes: **3**, distinct crash days: **4**, symbols: **3**
- Largest episode: **3** events (42.9%)

| Episode | Window (UTC) | Events | Symbols | Distinct days |
|---|---|---|---|---|
| 0 | 2026-01-19T03:00:00Z .. 2026-01-20T19:00:00Z | 3 | ETH, SOL | 2 |
| 1 | 2026-01-25T20:00:00Z .. 2026-01-25T20:00:00Z | 1 | SOL | 1 |
| 2 | 2026-01-31T20:00:00Z .. 2026-01-31T20:00:00Z | 3 | BTC, ETH, SOL | 1 |

## Episode-block bootstrap (resample crash episodes, not trades)
- Blocks: **3**, resamples: **20000**, seed: 20261115
- 95% CI total PnL: **[-1143.66, 10339.42]**
- Mean: **4276.82**, Median: **4292.50**, P(total PnL>0): **0.9624**
- First grid size excluding zero: **4**

## Conditional temporal-edge permutation (crash-day conditioned, real engine)
- Mode: `deterministic_seeded_draws:200_seed:20261115`
- Eligible real RSI<20 bars: **43**, draws evaluated: **200**
- Null mean: **1882.19**, median: **1838.72**
- Canonical percentile: **92.00%**, p(placebo>=canonical): **0.0800** (16/200)
- Limitation: Exact enumeration infeasible (astronomical distinct draws); used deterministic seeded subset and reported seed/count.

## Reproduction

```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_episode_edge_okx_multiyear.py --draws 200 --seed 20261115 --cache-dir research_state/cache/hyperliquid_ironflow_native_20251220_20260928 --universe research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json --census research_state/crash_event_census_hyperliquid_ironflow_native_20261115T155226Z.json --campaign research_state/campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json --venue-label 'Hyperliquid (Ironflow node-derived, native)' --out episode_edge_hyperliquid_native_20261115T155318Z
```
