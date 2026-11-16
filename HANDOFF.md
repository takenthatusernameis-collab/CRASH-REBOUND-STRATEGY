# HANDOFF — CRASH-REBOUND-STRATEGY
**Generated (UTC):** 2026-11-16T03:44:39Z
**Repo:** `CRASH-REBOUND-STRATEGY` (crash-rebound strategy research/backtesting, Hyperliquid-native evidence chain)
**Single durable handoff for next agentic session — read before doing anything else.**

## Current state (do not relitigate)
- **Implementation/spec:** complete and spec-compliant (`src/strategy`, `src/backtest/engine.py`, `src/data`, `research_state/strategy_spec.md`, `crash-rebound-strategy.pdf`). Session gates passing in recorded campaigns.
- **Evidence:** C1–C13 consolidated FINAL `NO_GO`; C11.3/C12/C13 underpowered/fragile; **C14 UNDERPOWERED** on widest verified native Ironflow archive (283d window 2025-12-20..2026-09-28, 197 perps / 113 @ $5M): 3 effective episodes, 4 crash days, 7 trades, bootstrap 95% CI [−1,144, +17,547] spans zero (first CI exclusion at n=4, archive max 4), permutation p=0.03595, placebo p=0.4444. **C15 BLOCKED_EVIDENCED_DATA_REQUIRED**. **C16 re-probe (2026-11-16T03:44:39Z) BLOCKED_EVIDENCED_DATA_REQUIRED** — no verified Hyperliquid-native multiyear/episode-extending archive acquirable from probed public sources.
- **Hard blocker:** no verified **Hyperliquid-native** hourly OHLCV archive extends to **≥2023-01-01** or yields **≥1 additional independent crash episode** beyond C14 (target n≥4) under unchanged spec. Re-probed with command-level evidence:
  - Hyperliquid public `candleSnapshot` (live): moving tail only, `full_window_served=false`, earliest ~`2026-04-21T16:00:00Z`, 3848/6792 bars, verdict `FULL_283D_BLOCKED_BY_API_RETENTION` (`research_state/hyperliquid_retention_probe_c16_20261116T034225Z.json`).
  - HuggingFace `ironflow/hyperliquid-candles-1h` (HF API metadata): lastModified 2026-11-13T07:20:50Z, coverage 2025-05-25..2026-10-31 (`data/2025-05..2026-10.parquet`), no pre-2025 history; widest native ingest already present `research_state/archives/hyperliquid_ironflow_wide_20261115T214900Z` (207 files, C14 scope 197/113 @ $5M). No other HF ironflow candles dataset.
  - Repo/env: no credentials/storage hooks or additional native multiyear source found; `datasets/huggingface_hub` libs absent. Cross-venue data is **not acceptable** (C10 NO_GO when non-native).

## Initial task for this session (non-optional)
**Mission: secure a validated Hyperliquid-native extension that enables decision-grade C16, or produce/maintain definitive exhaustion proof if still unavailable.** Do not run C16+ inference on exhausted C14 data and do not relax spec defaults to manufacture episodes.

### Required work plan (execute, don't summarize)
1. **Baseline & constraints (first actions):**
   - Read this handoff, `research_state/c16_acquisition_attempt_20261116T034439Z.{md,json}`, `research_state/c15_*`, `research_state/crash_event_census_hyperliquid_ironflow_wide_20261116T001200Z.json`, `research_state/episode_edge_hyperliquid_ironflow_wide_20261116T001200Z.json`.
   - Fixed: native Hyperliquid perps only, hourly gap-free bars, per-symbol SHA256 + non-synthetic/provenance attestation, `spec_compliant_volume_threshold=true` ($5M rolling-24h), unchanged RSI/sizing/exits/hedge, `is_hyperliquid_venue_data=true` only for native artifacts.
2. **Acquisition/re-probe (do real work, not desk research):**
   - Check for *new* sources not exhausted by C16: re-probe Hyperliquid public/API & official historical datasets/docs, search public repos/datasets for **Hyperliquid-native perps 1h** candles with pre-2025 coverage or additional independent crash episodes, and inspect any newly added `research_state/archives/`, scripts, or env hooks/credentials.
   - Run concrete commands, capture timestamps/ranges/row counts/coverage, and record evidence in a new dated artifact `research_state/c17_acquisition_attempt_<UTCSTAMP>.{md,json}` (or next appropriate id) with pass/fail against acceptance criteria.
3. **Unblock continuation on validated intake:**
   - If a candidate native archive is obtained, stage under `research_state/archives/<source>/...`, produce SOURCE/manifest/provenance, and validate with `scripts/validate_hyperliquid_archive_intake.py` and relevant derivation/verification scripts before claiming success.
   - Only on validated intake that adds ≥1 independent crash episode or extends to ≥2023-01-01: pre-register and execute decision-grade C16 (next campaign) under spec defaults, emit full metrics/verdict artifacts, and update this handoff with outcome and next focus.
4. **If still unavailable:** update artifacts/handoff with definitive, evidence-backed exhaustion (every path tried, why insufficient, exact minimum external deliverable) so next session can act immediately on any newly available source.
5. **Guardrails (never violate):** no cross-venue relabeling, no synthetic gap-filling presented as verified, no spec relaxation, no inference-only churn on exhausted C14 data. HIP-3/spot scope, if considered, must be explicitly labeled and kept separate from native-perps evidence.

## Key files
- Handoff/state: `HANDOFF.md`, `README.md`, `research_state/strategy_spec.md`
- Latest acquisition evidence: `research_state/c16_acquisition_attempt_20261116T034439Z.{md,json}`, `research_state/hyperliquid_retention_probe_c16_20261116T034225Z.json`, prior `research_state/c15_*`
- C14 evidence: `research_state/c14_*`, `research_state/crash_event_census_hyperliquid_ironflow_wide_20261116T001200Z.json`, `research_state/episode_edge_hyperliquid_ironflow_wide_20261116T001200Z.json`
- Intake/validation: `scripts/validate_hyperliquid_archive_intake.py`, `scripts/probe_hyperliquid_blocker.py`, `scripts/derive_verified_universe.py`, `research_state/archive_intake_validation_*`
- Data/code: `src/data/*`, `src/strategy/config.py`, `scripts/*`; widest native archive: `research_state/archives/hyperliquid_ironflow_wide_20261115T214900Z`

## Session-end requirement
Update this file with UTC timestamp, actions taken, artifacts produced, and the single clearest next task. Leave the repo in a state where progress can continue without rediscovery.
