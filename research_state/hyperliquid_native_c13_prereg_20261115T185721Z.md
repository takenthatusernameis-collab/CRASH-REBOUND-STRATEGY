# C13 preregistration — Hyperliquid-native decision-grade validation

**Generated (UTC):** 2026-11-15T18:57:21Z
**Status:** PRE_REGISTERED_BEFORE_COMPUTE — fixed BEFORE any C13 compute.
**Provenance:** Real Hyperliquid-native, node-derived (Ironflow HF, CC BY 4.0), NOT venue candleSnapshot. Real fetched/archived candles, non-synthetic. 283d window 2025-12-20T00:00:00Z–2026-09-28T23:00:00Z.

## Lead hypothesis (fixed)

- `rsi_threshold`: **25**
- `target_pct`: **9**
- Origin: C12 discovery only (`c12_25_9`: 17 trades / 10 episodes / 11 crash days, total +23,244.22; episode-block bootstrap CI95 spans 0). Not a validated GO.
- The config is fixed by this prereg. A different config requires a new prereg and a new artifact stem.

## Inputs

- cache: `research_state/cache/hyperliquid_ironflow_native_20251220_20260928`
- universe: `research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json`
- lead census: `research_state/crash_event_census_hyperliquid_native_c12_rsi25_t9_20261115T180000Z.json`
- lead campaign: `research_state/campaign_results_real_hyperliquid_native_c12_rsi25_t9_20261115T180000Z.json`

## Dependence-aware inference (required for any claim)

- Episode-block bootstrap CI95 for spot / ETH hedge / rebound short / total.
- Config-matched conditional temporal-edge permutation.
- Config-matched portfolio placebo (admission/cap/occupancy selection).
- Census alignment: events, signal-gate passes, trades, episodes, crash days.

## Pre-registered floors and power

- Seed: **20261115**
- Minimum heavy-compute floor: **100** permutation draws and **100** placebo subsets.
- Planned compute: **200** permutation draws, **200** placebo subsets.
- Minimum effective sample for GO: **10 trades / 5 episodes / 5 distinct crash days**.
- The 283d native window is structurally underpowered; report effective N and label underpowered honestly.

## Decision rules

- **GO** only if all hold: GO only if the pre-registered dependence-aware criteria all hold: episode-block bootstrap CI95 for spot or total excludes 0 with effective N >= 10 trades / 5 episodes / 5 crash days, AND config-matched permutation p < 0.05, AND config-matched placebo p_ge_canonical < 0.05, AND the result is not hedge-masked (spot leg reported separately).
- **NO_GO** if any: CI95 spans 0 for spot and total; permutation p >= 0.05 or placebo p_ge_canonical >= 0.05; positive total is entirely hedge/rebound-masked with negative spot; effective sample below the pre-registered floor
- **UNDERPOWERED / FRAGILE** if: Effective sample below floor: label UNDERPOWERED / FRAGILE_NOT_DECISION_GRADE; Artifacts missing seed/SHA binding or generated before this prereg
- Canonical RSI(21)<20 remains **NO_GO** unless re-validated under a new prereg.

## Commands (run after this file exists)

```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_episode_edge_okx_multiyear.py \
  --draws 200 --seed 20261115 --rsi-threshold 25 --target-pct 9 \
  --cache-dir research_state/cache/hyperliquid_ironflow_native_20251220_20260928 \
  --universe research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json \
  --census research_state/crash_event_census_hyperliquid_native_c12_rsi25_t9_20261115T180000Z.json \
  --campaign research_state/campaign_results_real_hyperliquid_native_c12_rsi25_t9_20261115T180000Z.json \
  --venue-label 'Hyperliquid (Ironflow node-derived, native)' \
  --out episode_edge_hyperliquid_native_c13_<TS>Z

PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_okx.py \
  --draws 200 --seed 20261115 --rsi-threshold 25 --target-pct 9 \
  --cache-dir research_state/cache/hyperliquid_ironflow_native_20251220_20260928 \
  --universe research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json \
  --census research_state/crash_event_census_hyperliquid_native_c12_rsi25_t9_20261115T180000Z.json \
  --campaign research_state/campaign_results_real_hyperliquid_native_c12_rsi25_t9_20261115T180000Z.json \
  --venue-label 'Hyperliquid (Ironflow node-derived, native)' \
  --out placebo_portfolio_hyperliquid_native_c13_<TS>Z
```

Then write `research_state/decision_verdict_hyperliquid_native_c13_<TS>Z.md` and run:

```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c13_focus_campaign.py
```

Do not edit this prereg after compute. If the plan must change, create a new prereg stem and document why.
