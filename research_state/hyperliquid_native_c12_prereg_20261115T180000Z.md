# Hyperliquid-native C12 pre-registration (2026-11-15T18:00:00Z)

**Status:** PRE_REGISTERED_BEFORE_COMPUTE (design-only; written before C12 grid/inference compute).
**Label:** `HYPERLIQUID_NATIVE_C12_PREREGISTERED_DISCOVERY`
**Provenance (binding):** Real Hyperliquid-native, **node-derived (Ironflow HF, CC BY 4.0), NOT venue `candleSnapshot`** (`is_hyperliquid_venue_data=true`). 283d window 2025-12-20T00:00:00Z–2026-09-28T23:00:00Z. No synthetic/fabricated data.

## Inputs (fixed)
- Cache: `research_state/cache/hyperliquid_ironflow_native_20251220_20260928/`
- Universe: `research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json`
- Canonical anchor (20/9): `research_state/campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json` (+ C11.3 census/episode/placebo/robustness/verdict stems)

## Hypotheses (discovery framed; C11.3 signals hypothesis-generating only)
- **H1:** `rsi_threshold ∈ {20,22,25,30}` (canonical 20) — test spot/total sensitivity on native.
- **H2:** `target_pct ∈ {5.0,9.0}` (canonical 9.0) — test realized take-profit sensitivity.

## Grid (full factorial, 8 configs)
`(rsi_threshold × target_pct)` = (20,22,25,30) × (5.0,9.0). Canonical (20,9.0) reused as anchor; all others run via `scripts/run_real_campaign.py` with `--rsi-threshold/--target-pct` and NEW stems. Fixed: rsi_period 21, rebound_short_target 9%, rebound_short_time_exit 48 bars, no bounce-confirm, non-literal entry, rebound+ETH hedge on, min daily vol $5M.

## Metrics & inference (dependence-aware, honest power)
- **Primary:** spot coin PnL, ETH hedge PnL, rebound-short PnL, total PnL, trade count, episode/crash-day count, max DD, cost stress.
- **Secondary:** exit reasons, per-symbol leg decomposition, signal-gate events.
- **Inference:** episode-block bootstrap CI + conditional temporal-edge permutation where feasible + portfolio placebo (exact when small) + crash-event census alignment; fixed seed 20261115. Report effective N/episodes/clustering and label **underpowered/FRAGILE_NOT_DECISION_GRADE** where unmet (native 283d structurally small: C11.3 3 episodes/4 crash days/6 trades).

## Stop/go & claims (binding)
- Canonical RSI(21)<20 remains **NO_GO** unless re-validated under pre-registered rules.
- **No GO** from point PnL, hedge-masked totals, or in-sample sensitivity without dependence-aware inference.
- **No GO** if underpowered/non-extreme (CI spans 0, insufficient N, placebo non-extreme). Separate spot coin / ETH hedge / rebound-short alpha in verdict.
- Do not relabel cross-venue as Hyperliquid; preserve Ironflow node-derived provenance caveat.

See JSON companion for machine-readable spec.
