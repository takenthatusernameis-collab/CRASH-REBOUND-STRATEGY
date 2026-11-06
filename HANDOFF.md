# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-11-06T20:26:00Z

## SINGLE CANONICAL HANDOFF
Only this root `HANDOFF.md` is durable. Do **not** create/read any other handoff file. This file is the sole source of next-session direction.

## SESSION 2026-11-06T20:26:00Z — HANDOFF REFRESH (Track-4 hardening complete + full suite stable)
- **Repo-name priority:** `CRASH-REBOUND-STRATEGY` → enforce crash-rebound strategy fidelity to `crash-rebound-strategy.pdf` (spec truth: RSI(21)<20 buy at next hourly open; +9%/50h buy exit; safety stop 8x usual hourly range (avg (high-low)/prev_close over 14h) — stopped buy never opens rebound short; rebound short -9%/48h (+40% stop rare); ETH hedge every leg vol-ratio capped 3x/336h decision-time no look-ahead; >=$5M 24h vol filter everywhere; equal-share cuts old+new across 120% gross cap; one position/coin; no look-ahead; no fabricated evidence; hourly engine = execution simplification — 20s slicing / explicit spread / explicit L2 order-book impact **not** fully simulated, do not claim unmodeled microstructure fidelity).
- **Bottlenecks:** none open. Canonical gap report clean; ITEM 6c complete (verified 283d data). Track-4 tests all passing (15 passed). Synthetic/flat series now rejected by provenance gates as required.
- **Verification:** `PYTHONPATH=. python -m pytest tests/test_track4* tests/test_streaming_ingest_hardening.py tests/test_parquet_ingest_hardening.py tests/test_parquet_large_archive_hardening.py tests/test_synthetic_data_hardening.py -v` = 27 passed. Key components green; maintain >=273 baseline green (0 failures).
- **Next heavy task:** Continue Track-4 hardening as needed or focus on any new edge cases surfaced; no open blockers. Keep enforcing synthetic-data rejection and provenance gates. Update only root HANDOFF.md with concrete evidence.

## INITIAL TASK MESSAGE (TIMESTAMPED, SINGLE, NEXT AGENTIC SESSION) — EXECUTE HEAVY WORK NOW
`CRASH-REBOUND-STRATEGY | 2026-11-06T20:26:00Z | ITEM 6c COMPLETE. Track-4 (d/e/f) hardening verified green (15 track4 + streaming/parquet/synthetic). Synthetic/flat series rejected by fetch/provenance gates. MANDATORY: if new gaps appear, write failing tests first then fix; otherwise continue with spec-fidelity hardening (no-lookahead decision bar, 8x safety stop, rebound short -9%/48h/+40% stop, ETH hedge every leg vol-ratio cap 3x/336h). Run targeted/full suite keeping >=273 baseline green (0 failures). Update ONLY root HANDOFF.md with UTC timestamp, concrete evidence (tests/artifacts/commits), bottleneck status (must be none or explicitly resolved with proof), and next heavy task. DO NOT idle/re-probe unnecessarily.`

## HEAVY FOCUS CAMPAIGN (FUTURE AGENTS MUST NOT AVOID) — EXECUTE IN ORDER, NO IDLE LOOPS
1. **TRACK-4 HARDENING (primary):** Maintain streaming/large-archive/parquet-safe ingest + checksums, universe/metrics/provenance/report edge cases, and spec-fidelity gaps. Keep synthetic-data rejection enforced.
2. **VALIDATE + HANDOFF (every session):** `PYTHONPATH=. python -m pytest -q` must stay green (>=273 baseline, 0 failures). Update **only** root `HANDOFF.md` with UTC timestamp, concrete evidence, artifacts/commits, bottleneck status, and next heavy task.

## RULES (non-negotiable)
- Items 1–5, 6a/6b done — no rework. ITEM 6c complete — do not re-run as primary task; do not fabricate, do not substitute fixtures for real market evidence, no idle waiting.
- **Heavy-work guardrail:** every session ships >=1 of verified-data hardening, real metrics artifacts, or material gated-pipeline/tests/universe/spec hardening.
- PDF/spec is truth. Both legs non-negotiable. ETH hedge every leg. Funding/liquidation correct. >=$5M volume filter everywhere. Equal-share cuts across old+new. Stopped buy never opens rebound short. **20s slicing / explicit spread / explicit L2 order-book impact are not fully simulated in the hourly engine — do not claim unmodeled microstructure fidelity.**

## CRITICAL CONTEXT (SOURCE OF TRUTH)
- **Spec:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Test window 2025-12-20→2026-09-28 (283d), **6792 hourly bars/symbol**.
- **Core:** `src/strategy/*`, `src/backtest/engine.py`, `src/data/{loader,provenance,streaming_ingest}.py`, `src/metrics/campaign_metrics.py`
- **Runners/tools:** `scripts/run_campaign.py`, `scripts/fetch_hyperliquid_candles.py`, `scripts/derive_verified_universe.py`, `scripts/run_real_campaign.py`, `scripts/run_portfolio.py`, `scripts/generate_candle_coverage_gap_report.py`

## SUCCESS CRITERIA (ITEM 6c)
- [x] Verified 283-day hourly dataset ingested; provenance manifest complete for required universe.
- [x] `universe_verified.json` derived/reconciled with >=$5M 24h vol policy.
- [x] Real campaign pipeline gated; synthetic/flat data rejected.
- [x] Tests remain green (>=273 baseline, 0 failures).
- [x] `HANDOFF.md` updated with timestamped results + next concrete heavy task.
