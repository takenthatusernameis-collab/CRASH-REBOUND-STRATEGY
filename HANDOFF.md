# HANDOFF — CRASH-REBOUND-STRATEGY
**Generated (UTC):** 2026-11-16T03:30:35Z
**Repo:** `CRASH-REBOUND-STRATEGY` (crash-rebound strategy research/backtesting, Hyperliquid-native evidence chain)
**Single durable handoff for next agentic session — read before doing anything else.**

## Current state (do not relitigate)
- **Implementation/spec:** complete and spec-compliant (`src/strategy`, `src/backtest/engine.py`, `src/data`, `research_state/strategy_spec.md`, `crash-rebound-strategy.pdf`). Session gates passing in recorded campaigns.
- **Evidence:** C1–C13 consolidated FINAL `NO_GO`; C11.3/C12/C13 underpowered/fragile; **C14 UNDERPOWERED** on widest verified native Ironflow archive (283d window 2025-12-20..2026-09-28, 197 perps / 113 @ $5M): 3 effective episodes, 4 crash days, 7 trades, bootstrap 95% CI [−1,144, +17,547] spans zero (first CI exclusion at n=4, archive max 4), permutation p=0.03595, placebo p=0.4444. **C15 BLOCKED_EVIDENCED_DATA_REQUIRED** — no verified Hyperliquid-native multiyear/episode-extending archive acquirable from probed public sources.
- **Hard blocker:** no verified **Hyperliquid-native** hourly OHLCV archive extends to **≥2023-01-01** or yields **≥1 additional independent crash episode** beyond C14 (target n≥4) under unchanged spec. Probes: Ironflow HF `ironflow/hyperliquid-candles-1h` is 2025-05-25T14:00Z..2026-10-31T23:00Z (same source, fully ingested); Hyperliquid `candleSnapshot` is moving tail only (earliest ~2026-04-21). Cross-venue data is **not acceptable** (C10 NO_GO when non-native).

## Initial task for this session (non-optional)
**Mission: execute a heavy, evidenced Hyperliquid-native data-acquisition campaign until a decision-grade extension is secured or every viable native path is exhausted with command-level proof.** Do not run C16+ inference on the existing archive and do not relax spec defaults to manufacture episodes.

### Required work plan (execute, don't summarize)
1. **Baseline & constraints (first actions):**
   - Read `research_state/c15_data_request_stem_20261116T024001Z.md`, `research_state/c15_acquisition_attempt_20261116T024001Z.md`, `research_state/c15_decision_verdict_hyperliquid_native_c15_20261116T024001Z.{md,json}`, `research_state/crash_event_census_hyperliquid_ironflow_wide_20261116T001200Z.json`, `research_state/episode_edge_hyperliquid_ironflow_wide_20261116T001200Z.json`.
   - Treat as fixed: native Hyperliquid perps only, hourly gap-free bars, per-symbol SHA256 + non-synthetic/provenance attestation, `spec_compliant_volume_threshold=true` ($5M rolling-24h), unchanged RSI/sizing/exits/hedge, `is_hyperliquid_venue_data=true` only for native artifacts.
2. **Source discovery & acquisition attempts (do real work, not desk research):**
   - Re-probe and document **current** availability of: Hyperliquid public/API historical endpoints, Hyperliquid official historical datasets/docs, HuggingFace/other public repos for *Hyperliquid-native perps* 1h candles, any repo-vendored acquisition scripts or credentials/hooks (`scripts/`, `research_state/`, env) that could yield verified native history.
   - For each candidate path run concrete commands (API probes, dataset inspections, downloads where feasible), capture timestamps/ranges/row counts/coverage limits, and record exact evidence in a new dated artifact `research_state/c16_acquisition_attempt_<UTCSTAMP>.{md,json}` (or equivalent) with pass/fail against acceptance criteria.
   - If a candidate archive is obtained, stage it under `research_state/archives/<source>/...` (or appropriate path), produce SOURCE/manifest/provenance, and validate with `scripts/validate_hyperliquid_archive_intake.py` and relevant derivation/verification scripts before claiming success.
3. **Unblock continuation:**
   - On validated intake that adds ≥1 independent crash episode or extends to ≥2023-01-01: pre-register and execute the next decision-grade campaign (C16) under spec defaults, emit full metrics/verdict artifacts, and update this handoff with outcome and next focus.
   - If no viable native source is found: produce a definitive, evidence-backed exhaustion report (every path tried, why insufficient, exact minimum external deliverable still required) and update this handoff so the next session can act immediately on any newly available source.
4. **Guardrails (never violate):**
   - No cross-venue relabeling, no synthetic gap-filling presented as verified, no spec relaxation, no inference-only churn on exhausted C14 data.
   - Prefer extending native history over inventing proxies; if HIP-3/spot scope is considered it must be explicitly labeled and kept separate from native-perps evidence.

## Key files
- Handoff/state: `HANDOFF.md`, `README.md`, `research_state/strategy_spec.md`
- C14/C15 evidence: `research_state/c14_*`, `research_state/c15_*`, `research_state/crash_event_census_hyperliquid_ironflow_wide_20261116T001200Z.json`, `research_state/episode_edge_hyperliquid_ironflow_wide_20261116T001200Z.json`
- Intake/validation: `scripts/validate_hyperliquid_archive_intake.py`, `research_state/archive_intake_validation_*`
- Data/code: `src/data/*`, `src/strategy/config.py`, `scripts/*`

## Session-end requirement
Update this file with UTC timestamp, actions taken, artifacts produced, and the single clearest next task. Leave the repo in a state where progress can continue without rediscovery.