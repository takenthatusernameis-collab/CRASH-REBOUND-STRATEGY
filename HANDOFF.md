# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-08T06:00:50Z
**Single canonical handoff:** ONLY this root `HANDOFF.md` is durable. Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/session variants). `__pycache__`/compiled artifacts are not evidence.

## BOTTLENECK CHECK
- **Status:** No bottlenecks. Only root HANDOFF.md exists (scan confirmed). CI: `.github/workflows/strategy-tests.yml` runs `python -m pytest tests/ -q` (Python 3.12, `PYTHONPATH=.`).
- **Baseline (this session):** gate `527 passed, 11 skipped` (~27.11s) after shipping raw-ingress/verified-evidence hardening (`cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no`, 2026-11-08T06:00:50Z). Entry gate was `525 passed, 11 skipped`; +2 from prior failing-tests-first hardening tests. Item 3 residual complete.

## REPO-NAME PRIORITY / SPEC CONTRACT (MANDATORY)
**CRASH-REBOUND-STRATEGY** → fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. **Hourly engine only.** Never claim 20s slicing / explicit spread / L2 order-book impact.

Non-negotiable: hourly funding on **every leg** (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on all exits including edge/missing-data/missing-ETH/fallback paths; hourly liquidation at worst price with correct sequencing vs stop/target/time and correct notional/timing/penalty; **stopped buy never opens rebound short**; 8x safety stop (`use_spec_safety_stop` ratio semantics); rebound short `-9%/48h/+40%`; ETH hedge every leg, vol-ratio over 336h capped 3x; `RSI(21)<20` next-hour open, deepest-first; `>= $5M` 24h volume in **all spec-compliant gating paths** (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only, never top-ups); one position/coin; strict no-look-ahead.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (TIMESTAMPED, MANDATORY)
```text
CRASH-REBOUND-STRATEGY | 2026-11-08T06:00:50Z | INITIAL TASK (HEAVY, NON-OPTIONAL)

Repo priority: CRASH-REBOUND-STRATEGY → fidelity to crash-rebound-strategy.pdf / research_state/strategy_spec.md. Hourly engine only. Never claim 20s slicing / explicit spread / L2 order-book impact.

Verified baseline: 527 passed, 11 skipped (PYTHONPATH=. python3 -m pytest tests/ -q --tb=no, ~27.11s, 2026-11-08T06:00:50Z). No bottlenecks. Sole durable handoff: root HANDOFF.md only. Item 3 residual (raw-ingress/verified-evidence hardening) SHIPPED.

You MUST ship >=1 MATERIAL item this session. Passive re-verification, handoff-only edits, or claiming "blocked" without a concrete missing input is NOT allowed. Use failing-tests-first for every change.

MANDATORY EXECUTION ORDER:
1) Gate: `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no` (expect 527+ passed, 11 skipped).
2) NEXT HEAVY — spec-fidelity hardening of the backtest engine (crash-rebound-strategy.pdf / research_state/strategy_spec.md), failing-tests-first, one material item minimum:
   a) Hourly funding on EVERY leg (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on ALL exits incl. edge/missing-data/missing-ETH/fallback paths.
   b) Hourly liquidation at worst price: correct sequencing vs stop/target/time; correct notional/timing/penalty.
   c) 8x safety stop (`use_spec_safety_stop` ratio semantics); stopped buy never opens rebound short.
   d) Rebound short `-9%` target / `48h` max hold / `+40%` stop; ETH hedge every leg; vol-ratio over 336h capped 3x.
   e) `RSI(21)<20` next-hour open, deepest-first crash first; `>= $5M` 24h volume in all spec-compliant gating paths (`enforce_spec_volume_floor`).
   f) Equal-share cuts old+new across 120% gross cap (cuts only, never top-ups); one position/coin; strict no-look-ahead.
   Core files: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`. Gating boundaries: `backtest_simple` is low-level executor (signal assumed); spec-compliant gating in `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners.
   Anchor every change with a failing spec-fidelity test first; prove the fix with the test passing.
3) If (2) yields no real defect after an evidence-backed audit, ship another material item (gated-pipeline/API-guardrail hardening) with failing-tests-first evidence.
4) Final gate: `PYTHONPATH=. python3 -m pytest tests/ -q --tb=no`.
5) Update ONLY root `HANDOFF.md`: UTC timestamp, exact commands/results, files changed, shipped material item(s) + evidence, remaining risks, next heavy task message. No other handoff files.
```

## HEAVY FOCUS CAMPAIGN (EXECUTE IN ORDER)
1. **Gate first:** `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no`.
2. **ACTIVE — spec-fidelity engine hardening** (failing-tests-first, one material item minimum): hourly funding/liquidation/stops/rebound/hedge/volume-gating/cap/no-look-ahead per `crash-rebound-strategy.pdf`/`strategy_spec.md` (see INITIAL TASK MESSAGE step 2).
3. **Item 3 residual (SHIPPED 2026-11-08T06:00:26Z):** verified-data/provenance/raw-ingress hardening complete — `_read_symbol_candles_from_file` raw-ingress fallback fail-closed (require_verified rejects missing provenance before any read); `_scan_archives` never upgrades probed files to `verified_complete_non_synthetic` coverage truth; repo-wide raw usage re-audit done (all verified-path consumers guarded; fixtures/tests/non-evidence fine); `run_portfolio.py` confirmed fixture-only, no verified-evidence dependency. Fix regressions only with failing tests.
4. **Item 4 watch (cleared):** production consumers recompute from validated facts; missing `synthetic_check` unverified/fail-closed. Fix regressions only with failing tests.
5. **Optional only after 2–3:** refactor only when it reduces spec-fidelity risk and is test-covered.
6. **Material shipped item definition:** spec-fidelity hardening+tests, or verified-data/provenance hardening, or material gated-pipeline/API-guardrail hardening — with concrete failing-tests-first evidence.
7. **Final gate + handoff required.**

## SHIPPED (CONDENSED)
- **2026-11-08T06:00:26Z (prior session):** Item 3 residual complete — raw-ingress/verified-evidence hardening.
  - `scripts/fetch_hyperliquid_candles._read_symbol_candles_from_file`: `require_verified=True` now rejects missing/non-dict `provenance_info` before any read (ProvenanceError); the raw JSON/other fallback can no longer bypass the verified-evidence contract (present+clean `synthetic_check`, runtime re-detection, sha256 when manifest provides it, fail-closed).
  - `scripts/generate_candle_coverage_gap_report._scan_archives`: scanned (untrusted) files never marked `verified=True` / `verified_complete_non_synthetic`; stay `verified=False` (verdict `runtime_probed_unverified` when clean/complete, `synthetic_or_incomplete_rejected` otherwise) and never enter `verified_archives_found` — scan never upgrades unverified files to trusted coverage truth.
  - New failing-tests-first evidence: `tests/test_gap_report_archive_scan_never_upgrades_unverified_20261108.py` (2 tests — complete probed file not upgraded to verified truth; flat probed file rejected without upgrading).
  - Gate: entry `525/11` → final **`527 passed, 11 skipped`**.
- **2026-11-08T05:17:30Z:** Item 3 residual — gap-report archive scan fail-closed on declared synthetic evidence. `tests/test_gap_report_archive_scan_verified_hardening_20261108.py` (3 tests). Final gate `525 passed, 11 skipped`.
- **2026-11-08T04:27Z:** Item 3 residual — raw-ingress fail-closed APIs + consumer wiring. 522/11.
- **2026-11-08T03:21:21Z:** Item 3 residual — structural-validation fail-closed at cache emission. 507/11.
- **2026-11-08T03:10:50Z:** `merge_verified_archives` emits normalized payload `sha256` with `synthetic_check`/`archive_sha256`. 504/11.
- **2026-11-08T02:35:37Z:** `run_real_campaign.load_verified_cache` fail-closed on missing/unverified `synthetic_check` + runtime re-detect. 503/11.
- **2026-11-08T02:21:02Z:** `derive_verified_universe.py` fail-closed on missing manifest `synthetic_check`. 496/11.
- **723144c / 2026-11-08T01:26Z:** `provenance.verify_candles_not_synthetic` accepts present-clean `synthetic_check` with `require_synthetic_check=True`. 494/11.
- **2026-11-08T01:14:16Z:** final-bar exit releases occupancy/notional. 487/11.
- **2026-11-08T00:29:47Z:** Item 4 residual cleared (validated-fact authority). 486/11.

## REMAINING RISKS / NEXT HEAVY FOCUS
- **Next heavy (active campaign):** spec-fidelity engine hardening per `crash-rebound-strategy.pdf`/`strategy_spec.md` — hourly funding on every leg/all exit paths, hourly liquidation at worst price, 8x safety stop (stopped buy never opens rebound short), rebound short `-9%/48h/+40%`, ETH hedge every leg vol-ratio capped 3x, `RSI(21)<20` next-hour open deepest-first, `>= $5M` gating everywhere, equal-share cuts across 120% cap, one position/coin, strict no-look-ahead. Failing-tests-first.
- **Item 2/4 (watch):** occupancy/lifecycle/no-lookahead/cap and validated-fact regressions — fix regressions only with failing tests.
- **Environment constraint:** real 283d Hyperliquid candles unavailable here; expand universe only with archived verified data + full provenance. Canonical BTC/ETH placeholder remains fail-closed by design.

## CRITICAL CONTEXT
- **Spec:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Test window 2025-12-20→2026-09-28 (283d), 6792 hourly bars/symbol.
- **Core:** `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/{loader,provenance,streaming_ingest}.py`, `src/metrics/campaign_metrics.py`
- **Runners:** `scripts/run_portfolio.py`, `scripts/run_real_campaign.py` (verified gate), `scripts/run_campaign.py` (fixture smoke), `scripts/derive_verified_universe.py`, `scripts/fetch_hyperliquid_candles.py`, `scripts/generate_candle_coverage_gap_report.py`
- **Canonical artifacts:** `research_state/cache/hyperliquid_verified_283d_btceth/` (placeholder fail-closed), `research_state/universe_verified.json`, `research_state/real_campaign_verified_btceth_283d*.json`, `research_state/candle_coverage_gap_report_verified_btceth_283d.json`

## RULES (NON-NEGOTIABLE)
- **Heavy-work guardrail:** each session ships >=1 material item with concrete evidence.
- **Spec is truth:** both legs, ETH hedge every leg, funding/liquidation correct on every leg/exit path, $5M gating in all spec-compliant paths, equal-share cuts across old+new, stopped buy never opens rebound short.
- **Gating boundaries:** `backtest_simple` is low-level executor (signal assumed). Spec-compliant gating in `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners.
- **Fail-closed:** missing provenance/verification for real path → reject. Never fabricate numbers/artifacts.
