# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-11-07T16:36:17Z
## SINGLE CANONICAL HANDOFF
Only this root `HANDOFF.md` is durable. Do **not** create/read any other handoff file. Do **not** create TODO/NEXT/PROGRESS/session handoff variants.

## SESSION 2026-11-07T16:36:17Z — BASELINE VERIFIED GREEN (411/11); WORKING TREE CLEAN; NO BOTTLENECKS
- **Repo-name priority (mandatory):** `CRASH-REBOUND-STRATEGY` → fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly engine only. **Never claim** 20s slicing / explicit spread / L2 order-book impact.
- **Non-negotiable spec contracts:** hourly funding on **every leg** (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on all exits including edge/missing-data/missing-ETH/fallback paths and missing/incomplete bars as applicable; hourly liquidation at worst price with correct sequencing vs stop/target/time, correct notional/timing/penalty; **stopped buy never opens rebound short**; 8x safety stop (`use_spec_safety_stop` ratio semantics); rebound short `-9%/48h/+40%`; ETH hedge every leg, vol-ratio over 336h capped 3x; `RSI(21)<20` next-hour open, deepest-first; `>= $5M` 24h volume in **all spec-compliant gating paths** (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only, never top-ups); one position/coin; strict no-look-ahead.
- **Bottlenecks:** none blocking. Working tree clean (`git status --short` empty). Sole durable handoff is this root `HANDOFF.md`. `__pycache__` artifacts are not evidence.
- **Baseline (verified this session):** `python -m pytest tests/ -q --tb=no` → **411 passed, 11 skipped in 42.34s** (2026-11-07T16:36Z). Suite green.

## INITIAL TASK MESSAGE (TIMESTAMPED, SINGLE, NEXT AGENTIC SESSION) — MANDATORY HEAVY EXECUTION
`CRASH-REBOUND-STRATEGY | 2026-11-07T16:36:17Z | MANDATORY: FIDELITY TO crash-rebound-strategy.pdf / research_state/strategy_spec.md (hourly only; no 20s slicing / explicit spread / L2 impact claims). BASELINE GREEN 411 PASSED / 11 SKIPPED. WORKING TREE CLEAN. NO BOTTLENECKS. SOLE DURABLE HANDOFF = ROOT HANDOFF.md. YOU MAY NOT SKIP HEAVY WORK, CLAIM BLOCKED WITHOUT A REAL MISSING INPUT, OR STOP AFTER PASSIVE RE-VERIFICATION. FAILING-TESTS-FIRST. SHIP >=1 MATERIAL HARDENED ITEM WITH EVIDENCE BEFORE ENDING SESSION.`

## HEAVY FOCUS CAMPAIGN — EXECUTE IN ORDER (NON-OPTIONAL)
Every session must complete steps 1 and 8, and ship at least one material item from steps 2–5.

1. **Gate (required):** `python -m pytest tests/ -q --tb=no` — must remain green (expected 411 passed, 11 skipped absent environment drift). Investigate real failures before new work.
2. **Campaign item 3 — $5M gating integrity regression watch** (all spec-compliant surfaces): `detect_crash`, `detect_crash_rsi`, `passes_universe_filter`, `filter_universe`, `generate_signal`, `load_multi_coin_data`, `analyze_symbol_volume_coverage`. `backtest_simple` is low-level/non-gated by design; `run_backtest.py`/fixture smoke runners are not spec-gated evidence. Never conflate low-level/non-gated paths with spec-compliant gating. Failing-tests-first for any real bypass surface; add targeted regressions that harden a real uncovered contract boundary.
3. **Campaign item 4 — verified-data/provenance hardening** (fail-closed checksums/manifests): `verify_cache_sha256`, `validate_provenance`, `require_verified_provenance`, `detect_synthetic_candles`, `derive_verified_universe.py --verify-cache-sha256`, `run_real_campaign.py` sha rejection. Broaden universe only with archived verified data + full provenance. BTC/ETH 283d 0-trade remains sole verified truth.
4. **Campaign item 2 residual watch** (already closed): multi-leg `occupied_until`/reservation invariants; timestamp/day normalization when `risk_state.date` is empty in summary states; no-lookahead/admission/cap/timestamp/daily-loss regression surfaces across gated wrappers/runners/portfolio. Failing-tests-first for any real defect.
5. **Optional only after 2–4:** Refactor only when it reduces spec-fidelity risk and is covered by tests. No speculative architecture work.
6. **Definition of material shipped item:** spec-fidelity hardening + tests, OR verified-data/provenance hardening, OR material gated-pipeline/API-guardrail hardening. Re-running tests alone is **not** a shipped item. Updating handoff alone is **not** a shipped item.
7. **Final gate (required):** `python -m pytest tests/ -q --tb=no` — full suite green.
8. **Handoff (required):** Update **ONLY** this root `HANDOFF.md` with UTC timestamp, exact commands/results, files changed, shipped material item(s), remaining risks, and next heavy task message. No other handoff files.

## SHIPPED / DONE (CONDENSED)
- **2026-11-07T16:36:17Z (this):** Handoff consolidated — single durable root `HANDOFF.md`; duplicated CRITICAL CONTEXT / SUCCESS CRITERIA / campaign listings removed; baseline re-verified green **411 passed, 11 skipped**; working tree clean; no bottlenecks. Next session initial task message set.
- **2026-11-07T15:50:00Z:** Campaign item 2 residual shipped — `TradeResult.max_live_coin_notional` authoritative = max live coin-position notional across long-entry leg and rebound-short-entry leg (hedges excluded); `run_portfolio.py` reads `res.max_live_coin_notional` directly, leg-log parsing removed. Failing-tests-first `tests/test_traderesult_max_live_coin_notional_rebound_20261107.py` (5 tests, 2 red pre-fix). Fixed in `src/backtest/engine.py` + `scripts/run_portfolio.py`. Suite green **411 passed, 11 skipped**.
- **2026-11-07T15:31:18Z:** Fixed real defect: `scripts/run_portfolio.py` `executed_notional` always evaluates rebound-short leg notional from `res.trades` so live rebound short counts toward gross cap/occupancy and triggers equal-share cap cuts. Failing-tests-first regression. Suite green 406/11.
- **Earlier campaign items 1–2 base:** rebound-short hedge funding/attribution/atomic risk/trade-log contracts; rebound grand-total consumer audit; TradeResult default `total_pnl` includes rebound short/hedge legs; portfolio daily-loss/exposure no-lookahead reconciliation; rebound-short attribution fields + risk_state rebound-short notional registration; RiskState timestamp-normalized daily accounting preserves live cap-cut/notional state.

## REMAINING RISKS / NEXT HEAVY FOCUS
- **Item 3:** $5M gating integrity regression watch across all spec-compliant surfaces (no sub-$5M non-zero bypass; 0 is non-spec escape hatch only).
- **Item 4:** fail-closed verified-data/provenance hardening (checksums/manifests); universe expansion only with archived verified data + full provenance.
- **Item 2 watch:** multi-leg `occupied_until`/reservation invariants; timestamp/day normalization when `risk_state.date` empty; no-lookahead/admission/cap/daily-loss regressions.

## CRITICAL CONTEXT
- **Spec:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Test window 2025-12-20→2026-09-28 (283d), 6792 hourly bars/symbol.
- **Core:** `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/{loader,provenance,streaming_ingest}.py`, `src/metrics/campaign_metrics.py`
- **Runners:** `scripts/run_portfolio.py`, `scripts/run_real_campaign.py` (verified gate), `scripts/run_campaign.py` (fixture smoke)
- **Verified artifacts (canonical):** `research_state/cache/hyperliquid_verified_283d_btceth/`, `research_state/universe_verified.json`, `research_state/real_campaign_verified_btceth_283d*.json`, `research_state/candle_coverage_gap_report_verified_btceth_283d.json`

## SUCCESS CRITERIA
- [x] Bottlenecks cleared & re-verified.
- [x] Baseline green (411 passed, 11 skipped).
- [x] 283d BTC/ETH verified/provenanced; real campaign truthful (0 trades).
- [x] RiskState timestamp-normalized daily accounting preserves live cap-cut/notional state.
- [x] TradeResult rebound-short attribution + risk_state rebound-short notional registration.
- [x] Portfolio realized daily-loss/exposure reconciliation is no-look-ahead.
- [x] TradeResult default `total_pnl` includes rebound short/hedge legs.
- [x] Rebound grand-total consumer audit shipped.
- [x] Portfolio live rebound-short notional reservation hardened.
- [x] Campaign item 2 residual shipped — `max_live_coin_notional` authoritative across long-entry + rebound-short-entry legs (hedges excluded); leg-log parsing removed.
- [ ] **NEXT SESSION (mandatory):** Ship >=1 material campaign item 3/4 hardened fix with failing-tests-first evidence, full suite green, update ONLY this `HANDOFF.md`.

## RULES (NON-NEGOTIABLE)
- **Heavy-work guardrail:** Each session ships >=1 material item: spec-fidelity hardening + tests, or verified-data/provenance hardening, or material gated-pipeline/API-guardrail hardening. Concrete evidence required.
- **Spec is truth:** PDF/spec authoritative. Both legs non-negotiable. ETH hedge every leg. Funding/liquidation correct on every leg. $5M gating everywhere spec-compliant. Equal-share cuts across old+new. Stopped buy never opens rebound short.
- **Gating boundaries:** `backtest_simple` is low-level executor (signal assumed), not volume-gated. Spec-compliant gating lives in `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners.
- **Fail-closed:** Missing provenance/verification for real path → reject. Never fabricate numbers/artifacts.
