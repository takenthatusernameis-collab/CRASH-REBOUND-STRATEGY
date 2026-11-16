# HANDOFF — CRASH-REBOUND-STRATEGY
**Generated (UTC):** 2026-11-16T04:38:40Z
**Repo:** `CRASH-REBOUND-STRATEGY` (crash-rebound strategy research/backtesting, Hyperliquid-native evidence chain)
**Single durable handoff for next agentic session — read before doing anything else.**

## Current state (do not relitigate)
- **Implementation/spec:** complete and spec-compliant (`src/strategy`, `src/backtest/engine.py`, `src/data`, `research_state/strategy_spec.md`, `crash-rebound-strategy.pdf`). Session gates passing in recorded campaigns.
- **Evidence:** C1–C13 consolidated FINAL `NO_GO`; C11.3/C12/C13 underpowered/fragile; **C14 UNDERPOWERED** on widest verified native Ironflow archive (283d window 2025-12-20..2026-09-28, 197 perps / 113 @ $5M): 3 effective episodes, 4 crash days, 7 trades, bootstrap 95% CI [−1,144, +17,547] spans zero (first CI exclusion at n=4, archive max 4), permutation p=0.03595, placebo p=0.4444. **C15–C17 BLOCKED_EVIDENCED_DATA_REQUIRED**.
- **Hard blocker:** no verified **Hyperliquid-native** hourly OHLCV archive extends to **≥2023-01-01** or yields **≥1 additional independent crash episode** beyond C14 (target n≥4) under unchanged spec. **C17 re-probe (2026-11-16T04:38:40Z) — no change since C16:**
  - Hyperliquid public `candleSnapshot` (live): moving tail only, `full_window_served=false`, earliest ~`2026-04-21T17:00:00Z`, max 3847/6792 bars, verdict `FULL_283D_BLOCKED_BY_API_RETENTION` (`research_state/hyperliquid_retention_probe_c17_20261116T043840Z.json`).
  - HuggingFace `ironflow/hyperliquid-candles-1h` (HF API): lastModified 2026-11-13T07:20:50Z, sha 5177a7f7, coverage `data/2025-05.parquet`..`data/2026-10.parquet` only (no earlier/later additions); only HF match for "hyperliquid candles 1h". Widest native ingest already present `research_state/archives/hyperliquid_ironflow_wide_20261115T214900Z` (207 files; C14 scope 197/113 @ $5M).
  - Repo/env: git clean, no new native archives, no HF/HYPER/IRON/archive credentials or storage hooks; `datasets/huggingface_hub` absent. Cross-venue archives (OKX/Binance) **not acceptable** as Hyperliquid-native evidence (C10 NO_GO when non-native).

## Initial task for this session (non-optional)
**Mission: obtain and validate a Hyperliquid-native archive that extends to ≥2023-01-01 or adds ≥1 independent crash episode beyond C14 (n≥4), then pre-register/execute decision-grade next campaign under spec defaults. If no new source is available, perform a real, evidence-backed re-probe and record definitive exhaustion — do not churn inference on C14.**

### Required work plan (execute, don't summarize)
1. **Baseline & constraints (first actions):**
   - Read this handoff, `research_state/c17_acquisition_attempt_20261116T043840Z.{md,json}`, `research_state/hyperliquid_retention_probe_c17_20261116T043840Z.json`, `research_state/c16_acquisition_attempt_20261116T034439Z.{md,json}`, `research_state/crash_event_census_hyperliquid_ironflow_wide_20261116T001200Z.json`, `research_state/episode_edge_hyperliquid_ironflow_wide_20261116T001200Z.json`.
   - Fixed: native Hyperliquid perps only, hourly gap-free bars, per-symbol SHA256 + non-synthetic/provenance attestation, `spec_compliant_volume_threshold=true` ($5M rolling-24h), unchanged RSI/sizing/exits/hedge, `is_hyperliquid_venue_data=true` only for native artifacts.
2. **Check for newly available sources (do real work):**
   - Inspect for new operator-supplied/native archives under `research_state/archives/` or elsewhere in-repo; inspect env/credentials/storage hooks that may unlock historical data.
   - Re-probe live Hyperliquid public/API & HF/other public sources for **Hyperliquid-native perps 1h** candles with pre-2025 coverage or episode-extending history. Run concrete commands, capture timestamps/ranges/counts/coverage.
   - Record all attempts and evidence in a new dated artifact `research_state/c18_acquisition_attempt_<UTCSTAMP>.{md,json}` with pass/fail against acceptance criteria.
3. **If a candidate native archive is found/obtained — unblock continuation:**
   - Stage under `research_state/archives/<source>/...` with SOURCE/provenance, per-file SHA256, coverage/non-synthetic attestations.
   - Validate via `scripts/validate_hyperliquid_archive_intake.py` and relevant derivation/verification scripts (`scripts/derive_verified_universe.py` etc.) before any evidence claim.
   - Only on validated intake that extends to ≥2023-01-01 or adds ≥1 independent crash episode (n≥4 feasible under unchanged spec): pre-register and execute decision-grade next campaign, emit full metrics/verdict artifacts, and update this handoff with outcome and next focus.
4. **If still unavailable:** update artifacts/handoff with definitive, evidence-backed exhaustion (every path tried, why insufficient, exact minimum external deliverable) so next session acts immediately on any newly available source.
5. **Guardrails (never violate):** no cross-venue relabeling, no synthetic gap-filling presented as verified, no spec relaxation, no inference-only churn on exhausted C14 data. HIP-3/spot, if considered, must be explicitly labeled and kept separate from native-perps evidence.

## Key files
- Handoff/state: `HANDOFF.md`, `README.md`, `research_state/strategy_spec.md`
- Latest acquisition evidence: `research_state/c17_acquisition_attempt_20261116T043840Z.{md,json}`, `research_state/hyperliquid_retention_probe_c17_20261116T043840Z.json`, prior `research_state/c16_*`, `research_state/c15_*`
- C14 evidence (exhausted): `research_state/c14_*`, `research_state/crash_event_census_hyperliquid_ironflow_wide_20261116T001200Z.json`, `research_state/episode_edge_hyperliquid_ironflow_wide_20261116T001200Z.json`
- Intake/validation: `scripts/validate_hyperliquid_archive_intake.py`, `scripts/probe_hyperliquid_blocker.py`, `scripts/derive_verified_universe.py`, `research_state/archive_intake_validation_*`
- Data/code: `src/data/*`, `src/strategy/config.py`, `scripts/*`; widest native archive: `research_state/archives/hyperliquid_ironflow_wide_20261115T214900Z`

## Session-end requirement
Update this file with UTC timestamp, actions taken, artifacts produced, and the single clearest next task. Leave the repo in a state where progress can continue without rediscovery.
