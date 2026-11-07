# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-11-07T16:51:08Z
## SINGLE CANONICAL HANDOFF
Only this root `HANDOFF.md` is durable. Do **not** create/read any other handoff file. Do **not** create TODO/NEXT/PROGRESS/session handoff variants.

## SESSION 2026-11-07T16:51:08Z — BASELINE RE-VERIFIED GREEN 414/11; NO BOTTLENECKS; SOLE DURABLE HANDOFF = ROOT HANDOFF.md
- **Repo-name priority (mandatory):** `CRASH-REBOUND-STRATEGY` → fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly engine only. **Never claim** 20s slicing / explicit spread / L2 order-book impact.
- **Non-negotiable spec contracts:** hourly funding on **every leg** (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on all exits including edge/missing-data/missing-ETH/fallback paths and missing/incomplete bars as applicable; hourly liquidation at worst price with correct sequencing vs stop/target/time, correct notional/timing/penalty; **stopped buy never opens rebound short**; 8x safety stop (`use_spec_safety_stop` ratio semantics); rebound short `-9%/48h/+40%`; ETH hedge every leg, vol-ratio over 336h capped 3x; `RSI(21)<20` next-hour open, deepest-first; `>= $5M` 24h volume in **all spec-compliant gating paths** (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only, never top-ups); one position/coin; strict no-look-ahead.
- **Bottlenecks:** none blocking. No alternate handoff files found. Sole durable handoff is this root `HANDOFF.md`. `__pycache__` artifacts are not evidence. Unrelated `research_state/candle_coverage_gap_report.json` modification was restored (not part of this shipped item).
- **Baseline (verified 2026-11-07T16:44Z):** `python -m pytest tests/ -q --tb=no` → **414 passed, 11 skipped in 42.11s**. Suite green.

## INITIAL TASK MESSAGE (TIMESTAMPED, SINGLE, NEXT AGENTIC SESSION) — MANDATORY HEAVY EXECUTION
`CRASH-REBOUND-STRATEGY | 2026-11-07T16:51:08Z | REPO-NAME PRIORITY (MANDATORY): CRASH-REBOUND-STRATEGY → fidelity to crash-rebound-strategy.pdf / research_state/strategy_spec.md. HOURLY ENGINE ONLY — never claim 20s slicing / explicit spread / L2 order-book impact. BASELINE GREEN 414 PASSED / 11 SKIPPED (re-verified 2026-11-07T16:51Z). NO BOTTLENECKS BLOCKING. SOLE DURABLE HANDOFF = ROOT HANDOFF.md (no other handoff files; __pycache__ is not evidence). YOU MAY NOT SKIP HEAVY WORK, CLAIM BLOCKED WITHOUT A REAL MISSING INPUT, OR STOP AFTER PASSIVE RE-VERIFICATION. FAILING-TESTS-FIRST. SHIP >=1 MATERIAL HARDENED ITEM WITH EVIDENCE (spec-fidelity hardening, verified-data/provenance hardening, or gated-pipeline/API-guardrail hardening) BEFORE ENDING SESSION. FINAL GATE: python -m pytest tests/ -q --tb=no must stay green. UPDATE ONLY THIS HANDOFF.md.`

## HEAVY FOCUS CAMPAIGN — EXECUTE IN ORDER (NON-OPTIONAL)
Every session must complete steps 1 and 8, and ship at least one material item from steps 2–5. Re-running tests / updating handoff alone is **not** a shipped item.

1. **Gate (required):** `python -m pytest tests/ -q --tb=no` — must remain green (expected 414 passed, 11 skipped absent environment drift). Investigate real failures before new work.
2. **Campaign item 3 — $5M gating/provenance-derivation integrity** (all spec-compliant surfaces + CLI/derivation): `detect_crash`, `detect_crash_rsi`, `passes_universe_filter`, `filter_universe`, `generate_signal`, `load_multi_coin_data`, `analyze_symbol_volume_coverage`, `scripts/derive_verified_universe.py` (floor-enforced 2026-11-07), `scripts/run_real_campaign.py` volume guards. `backtest_simple` is low-level/non-gated by design; fixture smoke runners are not spec-gated evidence. Failing-tests-first for any real bypass/labeling surface.
3. **Campaign item 4 — verified-data/provenance hardening** (fail-closed checksums/manifests): `verify_cache_sha256`, `validate_provenance`, `require_verified_provenance`, `detect_synthetic_candles`, `derive_verified_universe.py --verify-cache-sha256`, `run_real_campaign.py` sha rejection. Broaden universe only with archived verified data + full provenance. BTC/ETH 283d 0-trade remains sole verified truth.
4. **Campaign item 2 residual watch** (closed base): multi-leg `occupied_until`/reservation invariants; timestamp/day normalization when `risk_state.date` is empty in summary states; no-lookahead/admission/cap/timestamp/daily-loss regression surfaces across gated wrappers/runners/portfolio. Failing-tests-first for any real defect.
5. **Optional only after 2–4:** Refactor only when it reduces spec-fidelity risk and is covered by tests. No speculative architecture work.
6. **Definition of material shipped item:** spec-fidelity hardening + tests, OR verified-data/provenance hardening, OR material gated-pipeline/API-guardrail hardening. Concrete failing-tests-first evidence required.
7. **Final gate (required):** `python -m pytest tests/ -q --tb=no` — full suite green.
8. **Handoff (required):** Update **ONLY** this root `HANDOFF.md` with UTC timestamp, exact commands/results, files changed, shipped material item(s), remaining risks, and next heavy task message. No other handoff files.

## SHIPPED / DONE (CONDENSED)
- **2026-11-07T16:44:00Z (this):** Material campaign item 3/4 — `scripts/derive_verified_universe.py` now enforces `enforce_spec_volume_floor` on `--min-24h-volume-usd` (sub-$5M non-zero raised to $5M with warning) and emits `requested_min_24h_volume_usd` + `spec_compliant_volume_threshold`; prevents silent sub-$5M “verified” universe selection/labeling. Failing-tests-first: `tests/test_derive_verified_universe_volume_floor_20261107.py` (3 tests) failed pre-fix (`1000000 < 5000000`), passed after. Existing volume guardrails still green (23 passed). Final gate: **414 passed, 11 skipped**.
- **2026-11-07T16:36:17Z:** Handoff consolidated — single durable root `HANDOFF.md`; duplicated CRITICAL CONTEXT / SUCCESS CRITERIA / campaign listings removed; baseline re-verified green **411 passed, 11 skipped**; working tree clean; no bottlenecks.
- **2026-11-07T15:50:00Z:** Campaign item 2 residual shipped — `TradeResult.max_live_coin_notional` authoritative = max live coin-position notional across long-entry leg and rebound-short-entry leg (hedges excluded); `run_portfolio.py` reads `res.max_live_coin_notional` directly, leg-log parsing removed. Failing-tests-first `tests/test_traderesult_max_live_coin_notional_rebound_20261107.py` (5 tests, 2 red pre-fix). Fixed in `src/backtest/engine.py` + `scripts/run_portfolio.py`. Suite green **411 passed, 11 skipped**.
- **2026-11-07T15:31:18Z:** Fixed real defect: `scripts/run_portfolio.py` `executed_notional` always evaluates rebound-short leg notional from `res.trades` so live rebound short counts toward gross cap/occupancy and triggers equal-share cap cuts. Failing-tests-first regression. Suite green 406/11.
- **Earlier campaign items 1–2 base:** rebound-short hedge funding/attribution/atomic risk/trade-log contracts; rebound grand-total consumer audit; TradeResult default `total_pnl` includes rebound short/hedge legs; portfolio daily-loss/exposure no-lookahead reconciliation; rebound-short attribution fields + risk_state rebound-short notional registration; RiskState timestamp-normalized daily accounting preserves live cap-cut/notional state.

## REMAINING RISKS / NEXT HEAVY FOCUS
- **Item 3/4 watch (next):** Audit other CLI/derivation/provenance surfaces for sub-$5M acceptance or mislabeled spec compliance (e.g. any `--min-daily-volume-usd`/`--min-24h-volume-usd`/universe selection paths in scripts/tests not yet covered); ensure fail-closed where 0/low thresholds could be presented as spec-evidence. `fetch_hyperliquid_candles.py` analysis helpers partially floor-enforced — verify all spec-facing outputs/CLI args.
- **Item 4:** fail-closed verified-data/provenance hardening (checksums/manifests); universe expansion only with archived verified data + full provenance. Verified provenance artifacts show `status: "error"` in cache manifest snippets historically — confirm current verified canonical artifacts remain fail-closed and trusted.
- **Item 2 watch:** multi-leg `occupied_until`/reservation invariants; timestamp/day normalization when `risk_state.date` empty; no-lookahead/admission/cap/daily-loss regressions.

## CRITICAL CONTEXT
- **Spec:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Test window 2025-12-20→2026-09-28 (283d), 6792 hourly bars/symbol.
- **Core:** `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/{loader,provenance,streaming_ingest}.py`, `src/metrics/campaign_metrics.py`
- **Runners:** `scripts/run_portfolio.py`, `scripts/run_real_campaign.py` (verified gate), `scripts/run_campaign.py` (fixture smoke), `scripts/derive_verified_universe.py` (floor-enforced 2026-11-07)
- **Verified artifacts (canonical):** `research_state/cache/hyperliquid_verified_283d_btceth/`, `research_state/universe_verified.json`, `research_state/real_campaign_verified_btceth_283d*.json`, `research_state/candle_coverage_gap_report_verified_btceth_283d.json`

## SUCCESS CRITERIA
- [x] Bottlenecks cleared & re-verified.
- [x] Baseline green (414 passed, 11 skipped).
- [x] 283d BTC/ETH verified/provenanced; real campaign truthful (0 trades).
- [x] RiskState timestamp-normalized daily accounting preserves live cap-cut/notional state.
- [x] TradeResult rebound-short attribution + risk_state rebound-short notional registration.
- [x] Portfolio realized daily-loss/exposure reconciliation is no-look-ahead.
- [x] TradeResult default `total_pnl` includes rebound short/hedge legs.
- [x] Rebound grand-total consumer audit shipped.
- [x] Portfolio live rebound-short notional reservation hardened.
- [x] Campaign item 2 residual shipped — `max_live_coin_notional` authoritative across long-entry + rebound-short-entry legs (hedges excluded); leg-log parsing removed.
- [x] Campaign item 3/4 shipped — `derive_verified_universe.py` sub-$5M threshold floor-enforced + truthful labeling; failing-tests-first regression added.
- [ ] **NEXT SESSION (mandatory):** Ship >=1 material campaign item 3/4 hardened fix with failing-tests-first evidence, full suite green, update ONLY this `HANDOFF.md`.

## RULES (NON-NEGOTIABLE)
- **Heavy-work guardrail:** Each session ships >=1 material item: spec-fidelity hardening + tests, or verified-data/provenance hardening, or material gated-pipeline/API-guardrail hardening. Concrete evidence required.
- **Spec is truth:** PDF/spec authoritative. Both legs non-negotiable. ETH hedge every leg. Funding/liquidation correct on every leg. $5M gating everywhere spec-compliant. Equal-share cuts across old+new. Stopped buy never opens rebound short.
- **Gating boundaries:** `backtest_simple` is low-level executor (signal assumed), not volume-gated. Spec-compliant gating lives in `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners.
- **Fail-closed:** Missing provenance/verification for real path → reject. Never fabricate numbers/artifacts.
