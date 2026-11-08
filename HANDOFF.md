# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-08T04:27:08Z
**Single canonical handoff:** ONLY this root `HANDOFF.md` is durable. Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/session variants). `__pycache__`/compiled artifacts are not evidence.

## BOTTLENECK CHECK
- **Status:** No bottlenecks removed/needed. No conflicting handoff/TODO/NEXT/PROGRESS files. CI: `.github/workflows/strategy-tests.yml` runs `python -m pytest tests/ -q` (Python 3.12, `PYTHONPATH=.`).
- **Baseline (verified this session):** `522 passed, 11 skipped` (`cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no`, ~41.2s, 2026-11-08T04:27Z).

## REPO-NAME PRIORITY / SPEC CONTRACT (MANDATORY)
**CRASH-REBOUND-STRATEGY** → fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. **Hourly engine only.** Never claim 20s slicing / explicit spread / L2 order-book impact.

Non-negotiable: hourly funding on **every leg** (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on all exits including edge/missing-data/missing-ETH/fallback paths; hourly liquidation at worst price with correct sequencing vs stop/target/time and correct notional/timing/penalty; **stopped buy never opens rebound short**; 8x safety stop (`use_spec_safety_stop` ratio semantics); rebound short `-9%/48h/+40%`; ETH hedge every leg, vol-ratio over 336h capped 3x; `RSI(21)<20` next-hour open, deepest-first; `>= $5M` 24h volume in **all spec-compliant gating paths** (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only, never top-ups); one position/coin; strict no-look-ahead.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (TIMESTAMPED, MANDATORY)
```text
CRASH-REBOUND-STRATEGY | 2026-11-08T04:27:08Z | INITIAL TASK (HEAVY, NON-OPTIONAL)

Repo priority: CRASH-REBOUND-STRATEGY → fidelity to crash-rebound-strategy.pdf / research_state/strategy_spec.md. Hourly engine only. Never claim 20s slicing / explicit spread / L2 order-book impact.

Verified baseline: 522 passed, 11 skipped (PYTHONPATH=. python3 -m pytest tests/ -q --tb=no, ~41.2s, 2026-11-08T04:27Z). No bottlenecks. Sole durable handoff: root HANDOFF.md only.

You MUST ship >=1 MATERIAL item this session. Passive re-verification, handoff-only edits, or claiming "blocked" without a concrete missing input is NOT allowed. Use failing-tests-first for every change.

MANDATORY EXECUTION ORDER:
1) Gate: `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no` (expect 522+ passed, 11 skipped).
2) Item 3 residual (OPEN, NEXT HEAVY) — continue verified-data/provenance/raw-ingress fail-closed audit. 2026-11-08T04:27Z shipped guarded raw-ingress APIs + key consumer wiring (loader/streaming_ingest/run_real_campaign/derive_verified_universe); remaining surfaces must not accept unverified data (present+clean `synthetic_check`, runtime re-detection, sha256 when manifest provides it, validated-fact authority over labels):
   a) `scripts/generate_candle_coverage_gap_report.py` loads via `fetch_hyperliquid_candles._read_symbol_candles_from_file` (uses loader raw path) for probe/scan decisions; audit that manifest-described/verified-evidence reads are fail-closed (sha/synthetic/runtime) and that gap-report never treats unverified cache as coverage truth. Add failing tests.
   b) `scripts/fetch_hyperliquid_candles.py` archive/ingest/raw read helpers and any merge/read paths that still bypass guarded verification for manifest-backed cache decisions; confirm synthetic_check+sha+runtime re-detection are fail-closed everywhere a trusted label is emitted. Add failing tests.
   c) Any `complete_symbol_subset` callers / raw cache readers outside manifest-guarded loaders (audit repo-wide `load_hyperliquid_candles(` / `stream_normalize(` / `load_multi_coin_data(` usages; require_verified/provenance_info or explicit non-evidence/fixture justification). Prefer narrow, behavior-preserving guards; keep fixtures/synthetic smoke paths working unless they claim real evidence.
   d) `run_portfolio.py` uses `load_multi_coin_data` for fixture/dir loads (no manifest) — confirm no verified-evidence path depends on it without provenance; document/guard if a real-data mode appears.
   Broaden universe only with archived verified data + full provenance. Canonical placeholder `research_state/cache/hyperliquid_verified_283d_btceth/provenance.json` (synthetic, status=error, ready_for_real_campaign=false) remains fail-closed by design.
3) If (2) yields no real defect after an evidence-backed audit, ship another material item (spec-fidelity hardening+tests, or gated-pipeline/API-guardrail hardening) with failing-tests-first evidence. Document audit evidence.
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
- **2026-11-08T04:27Z (this session):** Item 3 residual material hardening — raw-ingress fail-closed APIs + consumer wiring. `src/data/loader.py`: `load_hyperliquid_candles(..., require_verified, provenance_info)` and `load_multi_coin_data(..., require_verified, manifest)` fail-closed for file-backed verified reads (present dict `synthetic_check`, runtime re-detection, sha256 when provided; missing/non-dict/declared-synthetic/runtime-synthetic => `ProvenanceError`; in-memory rejected in verified mode). `src/data/streaming_ingest.py`: added `stream_normalize_verified` (sha256/synthetic_check/runtime re-detection); low-level `stream_normalize` unchanged for raw parsing. `scripts/run_real_campaign.py` `load_verified_cache`: guarded loader read (defense-in-depth, covers archive-reload/manifest path). `scripts/derive_verified_universe.py`: guarded per-symbol cache reads; sha mismatch hard-fails when `--verify-cache-sha256` (explicit tamper check), synthetic/unverified evidence excluded with specific fail-closed reason codes; preserved existing backward-compat CLI contract. Failing-tests-first: `tests/test_loader_raw_ingress_hardening_20261108.py` (6), `tests/test_streaming_ingest_provenance_hardening_20261108.py` (4), `tests/test_load_multi_coin_data_verified_20261108.py` (2), `tests/test_run_real_campaign_load_verified_cache_guarded_20261108.py` (2). Also fixed test contract: `tests/test_derive_verified_universe_sha256_mismatch_20261108.py` accepts `SystemExit` as hard-fail (script-level). Full suite: **522 passed, 11 skipped**.
- **2026-11-08T03:21:21Z:** Item 3 residual — structural-validation fail-closed at cache emission (`fetch_hyperliquid_candles`/`merge_verified_archives`). 507/11.
- **2026-11-08T03:10:50Z:** `merge_verified_archives` emits normalized payload `sha256` with `synthetic_check`/`archive_sha256`. 504/11.
- **2026-11-08T02:35:37Z:** `run_real_campaign.load_verified_cache` fail-closed on missing/unverified `synthetic_check` + runtime re-detect. 503/11.
- **2026-11-08T02:21:02Z:** `derive_verified_universe.py` fail-closed on missing manifest `synthetic_check`. 496/11.
- **723144c / 2026-11-08T01:26Z:** `provenance.verify_candles_not_synthetic` accepts present-clean `synthetic_check` with `require_synthetic_check=True`. 494/11.
- **2026-11-08T01:14:16Z:** final-bar exit releases occupancy/notional. 487/11.
- **2026-11-08T00:29:47Z:** Item 4 residual cleared (validated-fact authority). 486/11.

## REMAINING RISKS / NEXT HEAVY FOCUS
- **Item 3 residual (OPEN, NEXT HEAVY):** continue fail-closed audit of remaining manifest-backed/verified-data surfaces. Key unverified surfaces after 2026-11-08T04:27Z: `scripts/generate_candle_coverage_gap_report.py` probe/scan/archive decisions loading via `fetch_hyperliquid_candles._read_symbol_candles_from_file` (loader raw path) — ensure verified-evidence decisions cannot accept unverified cache; `scripts/fetch_hyperliquid_candles.py` archive read/merge helper paths that emit trusted labels; repo-wide raw `load_hyperliquid_candles`/`stream_normalize`/`load_multi_coin_data` usages that handle verified evidence without `require_verified`/provenance context (fixture/non-evidence uses are fine). Always require present+clean `synthetic_check`, runtime re-detection, sha256 when available, validated-fact authority over labels.
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
