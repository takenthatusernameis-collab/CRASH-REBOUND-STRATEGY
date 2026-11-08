# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-08T05:17:30Z
**Single canonical handoff:** ONLY this root `HANDOFF.md` is durable. Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/session variants). `__pycache__`/compiled artifacts are not evidence.

## BOTTLENECK CHECK
- **Status:** No bottlenecks removed/needed. No conflicting handoff/TODO/NEXT/PROGRESS files exist (scan confirmed: only root HANDOFF.md). CI: `.github/workflows/strategy-tests.yml` runs `python -m pytest tests/ -q` (Python 3.12, `PYTHONPATH=.`).
- **Baseline (re-verified this session):** entry gate `522 passed, 11 skipped` (~26.70s); final gate `525 passed, 11 skipped` (~26.98s) after shipping (`cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no`, 2026-11-08T05:17Z).

## REPO-NAME PRIORITY / SPEC CONTRACT (MANDATORY)
**CRASH-REBOUND-STRATEGY** → fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. **Hourly engine only.** Never claim 20s slicing / explicit spread / L2 order-book impact.

Non-negotiable: hourly funding on **every leg** (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on all exits including edge/missing-data/missing-ETH/fallback paths; hourly liquidation at worst price with correct sequencing vs stop/target/time and correct notional/timing/penalty; **stopped buy never opens rebound short**; 8x safety stop (`use_spec_safety_stop` ratio semantics); rebound short `-9%/48h/+40%`; ETH hedge every leg, vol-ratio over 336h capped 3x; `RSI(21)<20` next-hour open, deepest-first; `>= $5M` 24h volume in **all spec-compliant gating paths** (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only, never top-ups); one position/coin; strict no-look-ahead.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (TIMESTAMPED, MANDATORY)
```text
CRASH-REBOUND-STRATEGY | 2026-11-08T05:17:30Z | INITIAL TASK (HEAVY, NON-OPTIONAL)

Repo priority: CRASH-REBOUND-STRATEGY → fidelity to crash-rebound-strategy.pdf / research_state/strategy_spec.md. Hourly engine only. Never claim 20s slicing / explicit spread / L2 order-book impact.

Verified baseline: 525 passed, 11 skipped (PYTHONPATH=. python3 -m pytest tests/ -q --tb=no, ~27.0s, 2026-11-08T05:17Z). No bottlenecks. Sole durable handoff: root HANDOFF.md only.

You MUST ship >=1 MATERIAL item this session. Passive re-verification, handoff-only edits, or claiming "blocked" without a concrete missing input is NOT allowed. Use failing-tests-first for every change.

MANDATORY EXECUTION ORDER:
1) Gate: `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no` (expect 525+ passed, 11 skipped).
2) Item 3 residual (OPEN, NEXT HEAVY) — continue fail-closed audit of raw-ingress/verified-evidence surfaces:
   a) `scripts/fetch_hyperliquid_candles._read_symbol_candles_from_file` (JSON/other branch, ~387) still reads via `load_hyperliquid_candles(str(p), symbol=symbol, require_verified=..., provenance_info=...)` then has a raw JSON-parse fallback on loader failure (~401+). That fallback (and any path where callers pass require_verified=False/provenance_info=None, e.g. gap-report scan uses it without verified context) can read data without the same verified-evidence contract. Audit: for verified-evidence decisions, require present+clean `synthetic_check`, runtime re-detection, sha256 when manifest provides it; fail-closed (ProvenanceError or explicit non-evidence verdict) rather than silent acceptance. 2026-11-08T05:17Z closed the gap-report JSON declared-`synthetic_check` case; remaining raw/fallback paths still need evidence-backed hardening.
   b) `scripts/generate_candle_coverage_gap_report._scan_archives` now rejects JSON payloads with declared `synthetic_check.is_synthetic` (2026-11-08T05:17Z) and uses runtime detection, but it reads via `_read_symbol_candles_from_file` without `require_verified`/provenance_info — so non-JSON formats and raw fallback paths are not uniformly manifest-guarded. Ensure scan verdicts cannot become "verified_complete_non_synthetic" without fail-closed synthetic/provenance checks appropriate to the evidence being scanned (document intent: scan is probing untrusted files; it must never upgrade unverified files to trusted coverage truth).
   c) Re-audit repo-wide raw `load_hyperliquid_candles(` / `stream_normalize(` / `load_multi_coin_data(` usages outside manifest-guarded loaders (fixture/test/non-evidence uses are fine). Require `require_verified`/provenance_info or explicit non-evidence/fixture justification.
   d) `run_portfolio.py` fixture/dir loads (no manifest) — confirm no verified-evidence path depends on it without provenance.
   Broaden universe only with archived verified data + full provenance. Canonical placeholder `research_state/cache/hyperliquid_verified_283d_btceth/provenance.json` remains fail-closed by design.
3) If (2) yields no real defect after an evidence-backed audit, ship another material item (spec-fidelity hardening+tests, or gated-pipeline/API-guardrail hardening) with failing-tests-first evidence.
4) Final gate: `PYTHONPATH=. python3 -m pytest tests/ -q --tb=no`.
5) Update ONLY root `HANDOFF.md`: UTC timestamp, exact commands/results, files changed, shipped material item(s) + evidence, remaining risks, next heavy task message. No other handoff files.
```

## HEAVY FOCUS CAMPAIGN (EXECUTE IN ORDER)
1. **Gate first:** `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no`.
2. **Item 3 residual — NEXT HEAVY:** verified-data/provenance/raw-ingress hardening (failing-tests-first). Close remaining fail-open gaps where a trusted path could accept unverified data (present+clean `synthetic_check`, runtime re-detection on raw ingress, sha256 verification when available, validated-fact authority over labels).
3. **Item 2 watch (cleared):** portfolio occupancy/multi-leg lifecycle/final-bar release/no-lookahead/cap/daily-loss covered. Fix regressions only with failing tests.
4. **Item 4 watch (cleared):** production consumers recompute from validated facts; missing `synthetic_check` unverified/fail-closed. Fix regressions only with failing tests.
5. **Optional only after 2–4:** refactor only when it reduces spec-fidelity risk and is test-covered.
6. **Material shipped item definition:** spec-fidelity hardening+tests, or verified-data/provenance hardening, or material gated-pipeline/API-guardrail hardening — with concrete failing-tests-first evidence.
7. **Final gate + handoff required.**

## SHIPPED (CONDENSED)
- **2026-11-08T05:17:30Z (this session):** Item 3 residual material hardening — gap-report archive scan fail-closed on declared synthetic evidence. `scripts/generate_candle_coverage_gap_report._scan_archives` now rejects JSON payloads carrying `synthetic_check.is_synthetic=true` (or present-but-malformed `synthetic_check`) before probing, marking `declared_synthetic_rejected` / `verified=false`; prevents a declared-synthetic cache file from being reported as `verified_complete_non_synthetic` coverage truth. Failing-tests-first: `tests/test_gap_report_archive_scan_verified_hardening_20261108.py` (3 tests) — declared-synthetic case failed pre-fix (`verified_archives_found` non-empty), passed post-fix; runtime-flat rejection and varied non-synthetic controls pass. Entry gate `522/11`; final gate **`525 passed, 11 skipped`**.
- **2026-11-08T04:27Z:** Item 3 residual — raw-ingress fail-closed APIs + consumer wiring (`load_hyperliquid_candles`/`load_multi_coin_data` `require_verified`, `stream_normalize_verified`, guarded campaign/universe cache reads). 522/11.
- **2026-11-08T03:21:21Z:** Item 3 residual — structural-validation fail-closed at cache emission (`fetch_hyperliquid_candles`/`merge_verified_archives`). 507/11.
- **2026-11-08T03:10:50Z:** `merge_verified_archives` emits normalized payload `sha256` with `synthetic_check`/`archive_sha256`. 504/11.
- **2026-11-08T02:35:37Z:** `run_real_campaign.load_verified_cache` fail-closed on missing/unverified `synthetic_check` + runtime re-detect. 503/11.
- **2026-11-08T02:21:02Z:** `derive_verified_universe.py` fail-closed on missing manifest `synthetic_check`. 496/11.
- **723144c / 2026-11-08T01:26Z:** `provenance.verify_candles_not_synthetic` accepts present-clean `synthetic_check` with `require_synthetic_check=True`. 494/11.
- **2026-11-08T01:14:16Z:** final-bar exit releases occupancy/notional. 487/11.
- **2026-11-08T00:29:47Z:** Item 4 residual cleared (validated-fact authority). 486/11.

## REMAINING RISKS / NEXT HEAVY FOCUS
- **Item 3 residual (OPEN, NEXT HEAVY):** continue fail-closed audit of remaining manifest-backed/verified-data surfaces. `scripts/generate_candle_coverage_gap_report._scan_archives` now rejects JSON declared `synthetic_check` (2026-11-08T05:17Z) but reads via `_read_symbol_candles_from_file` without `require_verified`/provenance_info and relies on runtime detection; non-JSON and fetch-script JSON/raw-fallback paths still read without uniform verified-evidence contracts (`fetch_hyperliquid_candles._read_symbol_candles_from_file` JSON branch ~387 loader call + raw fallback). For verified-evidence decisions require present+clean `synthetic_check`, runtime re-detection, sha256 when available, validated-fact authority over labels; fail-closed. Re-audit repo-wide raw `load_hyperliquid_candles`/`stream_normalize`/`load_multi_coin_data` usages outside manifest-guarded loaders (fixture/test/non-evidence fine).
- **Item 4 (watch):** label-trust/validated-fact regressions.
- **Item 2 (watch):** occupancy/lifecycle/no-lookahead/cap regressions.
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
