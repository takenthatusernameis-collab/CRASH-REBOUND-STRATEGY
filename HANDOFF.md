# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-11-06T22:34:48Z
## SINGLE CANONICAL HANDOFF
Only this root `HANDOFF.md` is durable. Do **not** create/read any other handoff file. This file is the sole source of next-session direction.

## SESSION 2026-11-06T22:34:48Z — HEAVY SPEC-FIDELITY CAMPAIGN (priority: enforce every invariant, block regressions)

- **Repo-name priority:** `CRASH-REBOUND-STRATEGY` → enforce crash-rebound fidelity to `crash-rebound-strategy.pdf`. Canonical rules: RSI(21)<20 buy at next hourly open (deepest-first when multiple), +9%/50h buy exit OR 8x usual hourly range (avg (high-low)/prev_close over 14h) safety stop → **stopped buy never opens rebound short**, one position/coin, >=$5M 24h vol filter everywhere, equal-share cuts old+new across 120% gross cap (cuts only), 1.25% of 24h vol sizing with 20s slicing logic awareness, ETH hedge every leg vol-ratio `coin_vol/ETH_vol` over 336h capped 3x, rebound short +long ETH when +9% hit → close at -9%/48h or +40% stop, hourly funding on every leg, hourly liquidation check at worst price, no look-ahead. **Hourly engine = execution simplification — 20s slicing / explicit spread / explicit L2 order-book impact NOT fully simulated; do NOT claim unmodeled microstructure fidelity.**
- **Bottlenecks:** none open. Track-4 (d/e/f) hardening verified green. Synthetic/flat series rejected by provenance gates. Maintain regression guard.
- **Verification:** `PYTHONPATH=. python -m pytest tests/test_track4* tests/test_streaming_ingest_hardening.py tests/test_parquet_ingest_hardening.py tests/test_parquet_large_archive_hardening.py tests/test_synthetic_data_hardening.py -v` = 27 passed; Track-4 suite 15 passed. Run full suite each session keeping >=273 baseline, 0 failures.
- **Immediate heavy task:** Build a hard enforcement pass. Add/strengthen failing tests first for any suspected spec gap (especially: stopped buy blocks rebound short creation unconditionally, 8x safety stop uses avg((H-L)/prev_close) over 14h with correct formula, rebound short target/stop/time match -9%/48h/+40%, vol-ratio cap 3x/336h applied to every leg hedge, >=$5M vol filter enforced in all gating paths, equal-share cut behavior under cap pressure, one-position-per-coin, funding/liquidation per leg, no look-ahead). Fix to pass. Leave concrete artifacts/evidence in HANDOFF. Do not re-run ITEM 6c as the only task — push spec-fidelity hardening.
## INITIAL TASK MESSAGE (TIMESTAMPED, SINGLE, NEXT AGENTIC SESSION) — EXECUTE HEAVY WORK NOW
`CRASH-REBOUND-STRATEGY | 2026-11-06T22:34:48Z | SPEC-FIDELITY ENFORCEMENT CAMPAIGN. Hard-block gaps: stopped-buy must never open rebound short (enforce + test). Verify 8x safety stop formula (avg((H-L)/prev_close) over 14h), rebound short -9%/48h +40% stop + long-ETH hedge, hedge vol-ratio coin/ETH over 336h capped 3x every leg, >=$5M 24h vol filter in all gating, equal-share cuts old+new across 120% cap (cuts only), one-position-per-coin, hourly funding+liquidation per leg, no look-ahead. Write failing tests first if uncertain; fix minimally to match spec. Do not claim 20s/L2/spread fully modeled. Run targeted+full suite keeping >=273 baseline green (0 failures). Update ONLY root HANDOFF.md with UTC timestamp, concrete evidence (tests/artifacts/commits), bottleneck status (none or resolved with proof), and next heavy task. Do heavy work, no idle loops.`
## HEAVY FOCUS CAMPAIGN (FUTURE AGENTS MUST NOT AVOID) — EXECUTE IN ORDER, NO IDLE LOOPS
1. **SPEC FIDELITY ENFORCEMENT (primary):** Harden invariants - stopped buy blocks rebound short unconditionally; 8x safety stop uses avg((H-L)/prev_close) over 14h; rebound short -9%/48h +40% stop with long-ETH hedge every leg; hedge vol-ratio coin/ETH over 336h capped 3x; >=$5M 24h vol filter in all gating; equal-share cuts old+new across 120% cap; one-position-per-coin; hourly funding on every leg; hourly liquidation check at worst price; strict no-look-ahead. Write failing tests first when uncertain.
2. **DATA/INGEST HARDENING:** Keep synthetic/flat rejection, provenance checksums/manifests, streaming/parquet large-archive safety.
3. **VALIDATE + HANDOFF (every session):** `PYTHONPATH=. python -m pytest -q` must stay green (>=273 baseline, 0 failures). Update **only** root `HANDOFF.md` with UTC timestamp, concrete evidence (tests/artifacts/commits), bottleneck status (must be none or explicitly resolved with proof), and next heavy task. Ship >=1 material hardened item.
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
