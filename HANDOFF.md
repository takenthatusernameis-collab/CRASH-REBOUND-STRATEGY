# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-11-07T17:22:58Z
## SINGLE CANONICAL HANDOFF
Only this root `HANDOFF.md` is durable. Do **not** create/read any other handoff file. Do **not** create TODO/NEXT/PROGRESS/session handoff variants.

## SESSION 2026-11-07T17:22:58Z — MATERIAL ITEM 3/4 SHIPPED: fetch_hyperliquid_candles PROVENANCE VOLUME-FLOOR ENFORCED + AUDIT FIELDS
- **Repo-name priority (mandatory):** `CRASH-REBOUND-STRATEGY` → fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly engine only. **Never claim** 20s slicing / explicit spread / L2 order-book impact.
- **Non-negotiable spec contracts:** hourly funding on **every leg** (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on all exits including edge/missing-data/missing-ETH/fallback paths and missing/incomplete bars as applicable; hourly liquidation at worst price with correct sequencing vs stop/target/time, correct notional/timing/penalty; **stopped buy never opens rebound short**; 8x safety stop (`use_spec_safety_stop` ratio semantics); rebound short `-9%/48h/+40%`; ETH hedge every leg, vol-ratio over 336h capped 3x; `RSI(21)<20` next-hour open, deepest-first; `>= $5M` 24h volume in **all spec-compliant gating paths** (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only, never top-ups); one position/coin; strict no-look-ahead.
- **Bottlenecks:** none blocking. Sole durable handoff is this root `HANDOFF.md`. `pytest` not installed in this environment (CI installs it per `.github/workflows/strategy-tests.yml`); used `python3 -m unittest` for failing-tests-first + targeted regression on affected unittest-style suites.
- **Shipped (material, failing-tests-first):** `scripts/fetch_hyperliquid_candles.py` CLI now enforces spec-compliant provenance/volume-coverage floor for `--min-daily-volume-usd` (sub-$5M or 0/invalid → effective `$5M`, warning emitted). Manifest `request_params` now records `min_daily_volume_usd_requested`, `min_daily_volume_usd_effective`, `spec_floor_enforced`, `spec_compliant_volume_floor_usd` and keeps backward-compat `min_daily_volume_usd` as effective. Prevents sub-$5M/0 provenance acquisition from being mislabeled as valid spec volume evidence. `analyze_symbol_volume_coverage` already floored values (unchanged behavior). New regression: `tests/test_fetch_hyperliquid_volume_floor_20261107.py` (3 tests) — 2 CLI assertions failed pre-fix (missing requested/effective fields; 0 not floored), all passed after.
- **Commands/results (2026-11-07T17:22Z UTC):**
  - `python3 -m unittest tests.test_fetch_hyperliquid_volume_floor_20261107 -v` → **3 OK** (post-fix; 2 failed pre-fix).
  - `python3 -m unittest tests.test_archive_universe_hardening tests.test_cache_sha256_verification tests.test_candle_coverage_gap_report tests.test_e2e_archive_to_manifest_universe_and_gate tests.test_ndjson_ingest_hardening tests.test_parquet_ingest_hardening tests.test_parquet_large_archive_hardening` → **28 OK, 8 skipped**.
  - `python3 -m unittest` discovery over 56 non-pytest-style test modules (16 pytest-style skipped in this env) → **69 OK, 11 skipped, RC 0**.
  - `python3 -m pytest tests/ -q --tb=no` → **not runnable here** (`pytest` missing). CI workflow installs `pytest numpy pandas requests`; prior verified baseline 414 passed / 11 skipped (2026-11-07T16:44Z).
- **Files changed:** `scripts/fetch_hyperliquid_candles.py`, `tests/test_fetch_hyperliquid_volume_floor_20261107.py` (new), `HANDOFF.md`.

## INITIAL TASK MESSAGE (TIMESTAMPED, SINGLE, NEXT AGENTIC SESSION) — MANDATORY HEAVY EXECUTION
`CRASH-REBOUND-STRATEGY | 2026-11-07T17:22:58Z | REPO-NAME PRIORITY (MANDATORY): CRASH-REBOUND-STRATEGY → fidelity to crash-rebound-strategy.pdf / research_state/strategy_spec.md. HOURLY ENGINE ONLY — never claim 20s slicing / explicit spread / L2 order-book impact. LAST VERIFIED PYTEST BASELINE 414 PASSED / 11 SKIPPED (2026-11-07T16:44Z); this env lacks pytest — CI installs it; local non-pytest unittest discovery over 56 modules passed 69 OK/11 skipped after 2026-11-07 changes. NO BOTTLENECKS BLOCKING. SOLE DURABLE HANDOFF = ROOT HANDOFF.md (no other handoff files; __pycache__ is not evidence). YOU MAY NOT SKIP HEAVY WORK, CLAIM BLOCKED WITHOUT A REAL MISSING INPUT, OR STOP AFTER PASSIVE RE-VERIFICATION. FAILING-TESTS-FIRST. SHIP >=1 MATERIAL HARDENED ITEM WITH EVIDENCE (spec-fidelity hardening, verified-data/provenance hardening, or gated-pipeline/API-guardrail hardening) BEFORE ENDING SESSION. FINAL GATE: python -m pytest tests/ -q --tb=no must stay green where pytest is available (CI). UPDATE ONLY THIS HANDOFF.md.`

## HEAVY FOCUS CAMPAIGN — EXECUTE IN ORDER (NON-OPTIONAL)
Every session must complete steps 1 and 8, and ship at least one material item from steps 2–5. Re-running tests / updating handoff alone is **not** a shipped item.

1. **Gate (required):** `python -m pytest tests/ -q --tb=no` where available (or run targeted unittest suites + state env limitation honestly). Investigate real failures before new work.
2. **Campaign item 3 — $5M gating/provenance-derivation integrity** (all spec-compliant surfaces + CLI/derivation): `detect_crash`, `detect_crash_rsi`, `passes_universe_filter`, `filter_universe`, `generate_signal`, `load_multi_coin_data`, `analyze_symbol_volume_coverage`, `scripts/derive_verified_universe.py` (floor-enforced 2026-11-07), `scripts/run_real_campaign.py` volume guards, `scripts/fetch_hyperliquid_candles.py` CLI/manifest (floor-enforced + requested/effective audit 2026-11-07). Remaining watch: any other `--min-daily-volume-usd`/`--min-24h-volume-usd`/universe-selection CLI or artifact consumer that could label sub-$5M as spec-compliant evidence; run_campaign/run_backtest/finalize scripts reviewed as low-risk/hardcoded or non-gated — failing-tests-first if a real bypass is found.
3. **Campaign item 4 — verified-data/provenance hardening** (fail-closed checksums/manifests): `verify_cache_sha256`, `validate_provenance`, `require_verified_provenance`, `detect_synthetic_candles`, `derive_verified_universe.py --verify-cache-sha256`, `run_real_campaign.py` sha rejection, fetch provenance manifests. Broaden universe only with archived verified data + full provenance. Confirm current verified canonical artifacts remain fail-closed/trusted.
4. **Campaign item 2 residual watch** (closed base): multi-leg `occupied_until`/reservation invariants; timestamp/day normalization when `risk_state.date` is empty in summary states; no-lookahead/admission/cap/timestamp/daily-loss regression surfaces across gated wrappers/runners/portfolio. Failing-tests-first for any real defect.
5. **Optional only after 2–4:** Refactor only when it reduces spec-fidelity risk and is covered by tests. No speculative architecture work.
6. **Definition of material shipped item:** spec-fidelity hardening + tests, OR verified-data/provenance hardening, OR material gated-pipeline/API-guardrail hardening. Concrete failing-tests-first evidence required.
7. **Final gate (required):** `python -m pytest tests/ -q --tb=no` where available.
8. **Handoff (required):** Update **ONLY** this root `HANDOFF.md` with UTC timestamp, exact commands/results, files changed, shipped material item(s), remaining risks, and next heavy task message. No other handoff files.

## SHIPPED / DONE (CONDENSED)
- **2026-11-07T17:22:58Z (this):** Material campaign item 3/4 — `scripts/fetch_hyperliquid_candles.py` provenance/volume-coverage CLI floors `--min-daily-volume-usd` (sub-$5M/0/invalid → $5M effective) and records requested/effective/spec_floor_enforced in manifest `request_params`; backward-compat `min_daily_volume_usd` kept as effective. Failing-tests-first: `tests/test_fetch_hyperliquid_volume_floor_20261107.py` (3 tests) — 2 CLI assertions red pre-fix, all green after. Affected provenance/ingest/archive unittest suites green (28 OK/8 skipped) + non-pytest unittest discovery 69 OK/11 skipped in this env.
- **2026-11-07T16:44:00Z:** Campaign item 3/4 — `scripts/derive_verified_universe.py` enforces `enforce_spec_volume_floor` on `--min-24h-volume-usd`; emits `requested_min_24h_volume_usd` + `spec_compliant_volume_threshold`. Failing-tests-first regression added. Suite green **414 passed, 11 skipped** (pytest).
- **2026-11-07T16:36:17Z:** Handoff consolidated — single durable root `HANDOFF.md`; baseline re-verified green **411 passed, 11 skipped**.
- **2026-11-07T15:50:00Z:** Campaign item 2 residual — `TradeResult.max_live_coin_notional` authoritative across long-entry + rebound-short-entry legs (hedges excluded); portfolio leg-log parsing removed. Failing-tests-first. Suite green **411 passed, 11 skipped**.
- **Earlier:** portfolio live rebound-short notional reservation; rebound grand-total consumer audit; default `total_pnl` includes rebound short/hedge legs; portfolio daily-loss/exposure no-lookahead reconciliation; rebound-short attribution + risk_state registration; timestamp-normalized daily accounting; rebound-short hedge funding/attribution/atomic risk/trade-log contracts.

## REMAINING RISKS / NEXT HEAVY FOCUS
- **Item 3/4 watch (next heavy):** Audit remaining artifact consumers/manifests for sub-$5M mislabeling (e.g., gap reports, derived manifests, any reader that trusts stale `volume_filter_ok` or `min_daily_volume_usd` without effective/floor fields). Consider adding schema/version compatibility checks where manifests are consumed for spec-evidence decisions. `run_campaign.py` / `run_backtest.py` / finalize/monitor scripts reviewed as lower risk — failing-tests-first if evidence of bypass appears.
- **Item 4:** fail-closed verified-data/provenance hardening (checksums/manifests, consumer-side enforcement). Universe expansion only with archived verified data + full provenance.
- **Item 2 watch:** multi-leg `occupied_until`/reservation invariants; timestamp/day normalization when `risk_state.date` empty; no-lookahead/admission/cap/daily-loss regressions.

## CRITICAL CONTEXT
- **Spec:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Test window 2025-12-20→2026-09-28 (283d), 6792 hourly bars/symbol.
- **Core:** `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/{loader,provenance,streaming_ingest}.py`, `src/metrics/campaign_metrics.py`
- **Runners:** `scripts/run_portfolio.py`, `scripts/run_real_campaign.py` (verified gate), `scripts/run_campaign.py` (fixture smoke), `scripts/derive_verified_universe.py` (floor-enforced 2026-11-07), `scripts/fetch_hyperliquid_candles.py` (floor-enforced + audit fields 2026-11-07)
- **Verified artifacts (canonical):** `research_state/cache/hyperliquid_verified_283d_btceth/`, `research_state/universe_verified.json`, `research_state/real_campaign_verified_btceth_283d*.json`, `research_state/candle_coverage_gap_report_verified_btceth_283d.json`

## SUCCESS CRITERIA
- [x] Bottlenecks cleared & re-verified.
- [x] Prior pytest baseline green (414 passed, 11 skipped, 2026-11-07T16:44Z). This env lacks pytest; affected unittest suites + non-pytest discovery green after 2026-11-07 change.
- [x] 283d BTC/ETH verified/provenanced; real campaign truthful (0 trades).
- [x] RiskState timestamp-normalized daily accounting preserves live cap-cut/notional state.
- [x] TradeResult rebound-short attribution + risk_state rebound-short notional registration.
- [x] Portfolio realized daily-loss/exposure reconciliation is no-look-ahead.
- [x] TradeResult default `total_pnl` includes rebound short/hedge legs.
- [x] Rebound grand-total consumer audit shipped.
- [x] Portfolio live rebound-short notional reservation hardened.
- [x] Campaign item 2 residual shipped — `max_live_coin_notional` authoritative across long-entry + rebound-short-entry legs.
- [x] Campaign item 3/4 shipped — `derive_verified_universe.py` sub-$5M threshold floor-enforced + truthful labeling.
- [x] Campaign item 3/4 shipped — `fetch_hyperliquid_candles.py` provenance CLI/manifest sub-$5M/0 floor-enforced + requested/effective audit fields.
- [ ] **NEXT SESSION (mandatory):** Ship >=1 material campaign item 3/4 hardened fix with failing-tests-first evidence (e.g., manifest/consumer schema or stale-field trust hardening), pytest green where available, update ONLY this `HANDOFF.md`.

## RULES (NON-NEGOTIABLE)
- **Heavy-work guardrail:** Each session ships >=1 material item: spec-fidelity hardening + tests, or verified-data/provenance hardening, or material gated-pipeline/API-guardrail hardening. Concrete evidence required.
- **Spec is truth:** PDF/spec authoritative. Both legs non-negotiable. ETH hedge every leg. Funding/liquidation correct on every leg. $5M gating everywhere spec-compliant. Equal-share cuts across old+new. Stopped buy never opens rebound short.
- **Gating boundaries:** `backtest_simple` is low-level executor (signal assumed), not volume-gated. Spec-compliant gating lives in `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners.
- **Fail-closed:** Missing provenance/verification for real path → reject. Never fabricate numbers/artifacts.
