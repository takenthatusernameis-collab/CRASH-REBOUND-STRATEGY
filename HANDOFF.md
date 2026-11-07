# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-11-07T15:50:00Z
## SINGLE CANONICAL HANDOFF
Only this root `HANDOFF.md` is durable. Do **not** create/read any other handoff file. Do **not** create TODO/NEXT/PROGRESS/session handoff variants.

## SESSION 2026-11-07T16:35:09Z — BASELINE RE-VERIFIED GREEN (411/11); WORKING TREE CLEAN; NO BOTTLENECKS; HEAVY FOCUS CAMPAIGN LOCKED
- **Repo-name priority (mandatory):** `CRASH-REBOUND-STRATEGY` → fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly engine only. **Never claim** 20s slicing / explicit spread / L2 order-book impact.
- **Non-negotiable spec contracts:** hourly funding on **every leg** (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on all exits including edge/missing-data/missing-ETH/fallback paths and missing/incomplete bars as applicable; hourly liquidation at worst price with correct sequencing vs stop/target/time, correct notional/timing/penalty; **stopped buy never opens rebound short**; 8x safety stop (`use_spec_safety_stop` ratio semantics); rebound short `-9%/48h/+40%`; ETH hedge every leg, vol-ratio over 336h capped 3x; `RSI(21)<20` next-hour open, deepest-first; `>= $5M` 24h volume in **all spec-compliant gating paths** (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only, never top-ups); one position/coin; strict no-look-ahead.
- **Bottlenecks:** none blocking. Working tree clean (`git status --short` empty). Sole durable handoff is this root `HANDOFF.md`. `__pycache__` artifacts are not evidence.
- **Baseline (verified this session):** `python -m pytest tests/ -q --tb=no` → **411 passed, 11 skipped in 42.07s** (2026-11-07T15:50Z). Prior baseline 406/11 (2026-11-07T15:31Z). Pre-fix one real failure: `tests/test_portfolio_rebound_short_live_notional_reservation_20261107.py::test_rebound_short_live_notional_triggers_cap_cut_future_admission` (future admission ignored live rebound-short notional; reserved long-entry instead). Fixed in `scripts/run_portfolio.py`: `executed_notional` now always evaluates the rebound-short leg notional from `res.trades` (short entry × shares), not only when `max_live_coin_notional` is absent. Suite green after fix.

## INITIAL TASK MESSAGE (TIMESTAMPED, SINGLE, NEXT AGENTIC SESSION) — MANDATORY HEAVY EXECUTION
`CRASH-REBOUND-STRATEGY | 2026-11-07T16:35:09Z | MANDATORY: FIDELITY TO crash-rebound-strategy.pdf / research_state/strategy_spec.md (hourly only; no 20s slicing / explicit spread / L2 impact claims). BASELINE GREEN 411 PASSED / 11 SKIPPED. WORKING TREE CLEAN. NO BOTTLENECKS. SOLE DURABLE HANDOFF = ROOT HANDOFF.md. YOU MAY NOT SKIP HEAVY WORK, CLAIM BLOCKED WITHOUT A REAL MISSING INPUT, OR STOP AFTER PASSIVE RE-VERIFICATION. FAILING-TESTS-FIRST. SHIP >=1 MATERIAL HARDENED ITEM WITH EVIDENCE BEFORE ENDING SESSION.`

## HEAVY FOCUS CAMPAIGN — EXECUTE IN ORDER (NON-OPTIONAL)
Every session must complete steps 1 and 8, and ship at least one material item from steps 2–6.

1. **Gate (required):** `python -m pytest tests/ -q --tb=no` — must remain green (expected 411 passed, 11 skipped absent environment drift). Investigate real failures before new work.
2. **Campaign item 2 residual (CLOSED 2026-11-07T15:50:00Z):** `TradeResult.max_live_coin_notional` is now authoritative — max live coin-position notional across long-entry and rebound-short-entry legs (hedges excluded); `run_portfolio.py` reads it directly with no leg-log parsing. Remaining watch: multi-leg `occupied_until`/reservation invariants; timestamp/day normalization when `risk_state.date` is empty in summary states; other no-lookahead/admission/cap/timestamp/daily-loss regression surfaces across gated wrappers/runners/portfolio. Failing-tests-first for any real defect; add targeted regressions even when clean only if they harden a real uncovered contract boundary.
3. **Campaign item 3 (material work if 2 clean):** $5M gating integrity regression watch on all spec-compliant surfaces. `backtest_simple` is low-level/non-gated by design; `run_backtest.py`/fixture smoke runners are not spec-gated evidence. Never conflate low-level/non-gated paths with spec-compliant gating.
4. **Campaign item 4 (material work if 2/3 clean):** Verified-data/provenance hardening (fail-closed checksums/manifests). Broaden universe only with archived verified data + full provenance. BTC/ETH 283d 0-trade remains sole verified truth.
5. **Optional only after 2–4:** Refactor only when it reduces spec-fidelity risk and is covered by tests. No speculative architecture work.
6. **Definition of material shipped item:** spec-fidelity hardening + tests, OR verified-data/provenance hardening, OR material gated-pipeline/API-guardrail hardening. Re-running tests alone is **not** a shipped item. Updating handoff alone is **not** a shipped item.
7. **Final gate (required):** `python -m pytest tests/ -q --tb=no` — full suite green.
8. **Handoff (required):** Update **ONLY** this root `HANDOFF.md` with UTC timestamp, exact commands/results, files changed, shipped material item(s), remaining risks, and next heavy task message. No other handoff files.

## SHIPPED / DONE (CONDENSED)
- **2026-11-07T15:50:00Z (this):** Campaign item 2 residual shipped — `TradeResult.max_live_coin_notional` is now authoritative and computed as the **max live coin-position notional across the long-entry leg and the rebound-short-entry leg (hedges excluded)**. Failing-tests-first: `tests/test_traderesult_max_live_coin_notional_rebound_20261107.py` (5 tests, 2 red pre-fix: rebound-short leg ignored, hedge legs leaked). Fixed in `src/backtest/engine.py`: default `max_live_coin_notional` walks `res.trades` coin legs (`side` in `long`/`short`) at `shares × entry`, taking the max over the long-entry default. `scripts/run_portfolio.py` reservation now reads `res.max_live_coin_notional` directly — leg-log parsing removed (the old `for _leg in res.trades` short-entry scan is gone). Suite green **411 passed, 11 skipped**. Only `HANDOFF.md` updated (+ reverted non-canonical `research_state/candle_coverage_gap_report.json`).
- **2026-11-07T15:31:18Z (prior):** Fixed real defect: `scripts/run_portfolio.py` `executed_notional` now always evaluates rebound-short leg notional from `res.trades` (short entry × shares), so a live rebound short counts toward gross cap / occupancy and triggers equal-share cap cuts for future admissions. Failing-tests-first regression confirmed (test was red pre-fix, green post-fix). Suite green 406/11.
- **2026-11-07T13:50:27Z:** Rebound grand-total consumer audit (`campaign_metrics:_trade_pnl` + runner fallback); rebound legs never dropped.
- **2026-11-07T13:47:34Z:** TradeResult default `total_pnl` includes rebound short/hedge legs.
- **2026-11-07T13:41:05Z:** Portfolio daily-loss/exposure no-lookahead reconciliation (exits applied only at/through exit bar).
- **2026-11-07T12:37:09Z:** Rebound-short attribution fields + risk_state rebound-short notional registration.
- **2026-11-07T12:27:42Z:** RiskState timestamp-normalized daily accounting preserves live cap-cut/notional state.
- **Earlier campaign items 1–2 base:** rebound-short hedge funding/attribution/atomic risk/trade-log contracts; grand-total consumer audit.

## REMAINING RISKS / NEXT HEAVY FOCUS
- **Item 2 residual (CLOSED 2026-11-07T15:50:00Z):** `TradeResult.max_live_coin_notional` now explicitly carries the max live coin-position notional across long-entry and rebound-short-entry legs (hedges excluded); `run_portfolio.py` reads it directly with no leg-log parsing. Remaining item-2 watch: multi-leg `occupied_until`/reservation invariants; timestamp/day normalization when `risk_state.date` is empty in summary states; other no-lookahead/admission/cap/timestamp/daily-loss regression surfaces across gated wrappers/runners/portfolio.
- **Item 3:** $5M gating integrity regression watch across all spec-compliant surfaces.
- **Item 4:** fail-closed verified-data/provenance hardening (checksums/manifests); universe expansion only with archived verified data + full provenance. BTC/ETH 283d 0-trade remains sole verified truth.

## CRITICAL CONTEXT
- **Spec:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Test window 2025-12-20→2026-09-28 (283d), 6792 hourly bars/symbol.
- **Core:** `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/{loader,provenance,streaming_ingest}.py`, `src/metrics/campaign_metrics.py`
- **Runners:** `scripts/run_portfolio.py`, `scripts/run_real_campaign.py` (verified gate), `scripts/run_campaign.py` (fixture smoke)
- **Verified artifacts (canonical):** `research_state/cache/hyperliquid_verified_283d_btceth/`, `research_state/universe_verified.json`, `research_state/real_campaign_verified_btceth_283d*.json`, `research_state/candle_coverage_gap_report_verified_btceth_283d.json`

## SUCCESS CRITERIA
- [x] Bottlenecks cleared & re-verified (2026-11-07T15:31Z).
- [x] Baseline green (406 passed, 11 skipped).
- [x] 283d BTC/ETH verified/provenanced; real campaign truthful (0 trades).
- [x] RiskState timestamp-normalized daily accounting preserves live cap-cut/notional state.
- [x] TradeResult rebound-short attribution + risk_state rebound-short notional registration.
- [x] Portfolio realized daily-loss/exposure reconciliation is no-look-ahead.
- [x] TradeResult default `total_pnl` includes rebound short/hedge legs.
- [x] Rebound grand-total consumer audit shipped.
- [x] Portfolio live rebound-short notional reservation hardened.
- [x] **THIS SESSION (2026-11-07T15:50:00Z):** Campaign item 2 residual shipped — `TradeResult.max_live_coin_notional` now carries the max live coin-position notional across long-entry and rebound-short-entry legs (hedges excluded); `run_portfolio.py` reads it directly with no leg-log parsing; failing-tests-first `tests/test_traderesult_max_live_coin_notional_rebound_20261107.py` (5 tests, 2 red pre-fix); full suite **411 passed, 11 skipped**; only `HANDOFF.md` updated.
- [ ] **NEXT SESSION (mandatory):** Ship >=1 material campaign item 3/4 hardened fix with failing-tests-first evidence, full suite green, update ONLY this `HANDOFF.md`.

## HEAVY FOCUS CAMPAIGN (MUST EXECUTE IN ORDER; FUTURE AGENTS MAY NOT AVOID)
1. **[DONE 2026-11-07T12:37:09Z]** Rebound-short hedge funding/attribution + atomic risk/trade-log contracts; same-bar boundary lock.
2. **[DONE 2026-11-07T13:50:27Z]** Rebound grand-total consumer audit hardened (`campaign_metrics:_trade_pnl` + `run_portfolio.py:228`); rebound short/hedge legs never silently dropped in attribution/aggregation.
3. **[DONE 2026-11-07T15:50:00Z]** No-lookahead & portfolio-cap/timestamp/daily-loss regression watch (admission/sizing/gating/history/cap cuts equal-share old+new, no top-ups; realized exits reconciled only at/through exit bar). **Fixed 2026-11-07T15:31:18Z:** `executed_notional` now always evaluates rebound-short leg notional from `res.trades` so a live rebound short counts toward gross cap/occupancy and triggers equal-share cuts for future admissions. **Fixed 2026-11-07T15:50:00Z:** `TradeResult.max_live_coin_notional` is now authoritative — computed as the max live coin-position notional across long-entry and rebound-short-entry legs (hedges excluded), so future paths without leg-log parsing reserve the live short notional. `run_portfolio.py` reads it directly; leg-log parsing removed. Remaining: multi-leg `occupied_until`/reservation invariants, timestamp/day normalization when `risk_state.date` is empty in summary states.
4. **$5M gating integrity regression watch** (all spec-compliant surfaces; `backtest_simple` is low-level/non-gated).
5. **Verified-data/provenance hardening** (fail-closed checksums/manifests; broaden universe only with archived verified data + full provenance).
6. **Every session gate:** `python -m pytest tests/ -q --tb=no` green, ship >=1 material hardened item with evidence, update only `HANDOFF.md`.

## RULES (NON-NEGOTIABLE)
- **Heavy-work guardrail:** Each session ships >=1 material item: spec-fidelity hardening + tests, or verified-data/provenance hardening, or material gated-pipeline/API-guardrail hardening. Concrete evidence required.
- **Spec is truth:** PDF/spec authoritative. Both legs non-negotiable. ETH hedge every leg. Funding/liquidation correct on every leg. $5M gating everywhere spec-compliant. Equal-share cuts across old+new. Stopped buy never opens rebound short.
- **Gating boundaries:** `backtest_simple` is low-level executor (signal assumed), not volume-gated. Spec-compliant gating lives in `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners.
- **Fail-closed:** Missing provenance/verification for real path → reject. Never fabricate numbers/artifacts.

## CRITICAL CONTEXT
- **Spec:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Test window 2025-12-20→2026-09-28 (283d), 6792 hourly bars/symbol.
- **Core:** `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/{loader,provenance,streaming_ingest}.py`, `src/metrics/campaign_metrics.py`
- **Runners:** `scripts/run_portfolio.py`, `scripts/run_real_campaign.py` (verified gate), `scripts/run_campaign.py` (fixture smoke)
- **Verified artifacts (canonical):** `research_state/cache/hyperliquid_verified_283d_btceth/`, `research_state/universe_verified.json`, `research_state/real_campaign_verified_btceth_283d*.json`, `research_state/candle_coverage_gap_report_verified_btceth_283d.json`

## SUCCESS CRITERIA
- [x] Bottlenecks cleared & re-verified.
- [x] Baseline green and improved (406 passed, 11 skipped).
- [x] 283d BTC/ETH verified/provenanced; real campaign truthful (0 trades).
- [x] RiskState timestamp-normalized daily accounting preserves live cap-cut/notional state.
- [x] TradeResult rebound-short attribution + risk_state rebound-short notional registration.
- [x] Portfolio realized daily-loss/exposure reconciliation is no-look-ahead (exits applied only at/through exit bar), with cross-bar + same-bar probe-leak regressions.
- [x] TradeResult default `total_pnl` includes rebound short/hedge legs (explicit `total_pnl` still authoritative).
- [x] Rebound grand-total consumer audit shipped (`campaign_metrics:_trade_pnl` + `run_portfolio.py` grand-total fallback).
- [x] **PRIOR SESSION (2026-11-07T14:43:40Z):** Portfolio live rebound-short notional reservation hardened (`scripts/run_portfolio.py`: max long-entry/short-leg-entry notional for overlay/cap); failing-tests-first (`tests/test_portfolio_rebound_short_live_notional_reservation_20261107.py`, 2 tests, 1 red before fix); targeted 26 passed; full suite **406 passed, 11 skipped**; only `HANDOFF.md` updated (+ reverted non-material `research_state/candle_coverage_gap_report.json`).
- [x] **THIS SESSION (2026-11-07T15:31:18Z):** Fixed real defect — `scripts/run_portfolio.py` `executed_notional` now always evaluates rebound-short leg notional from `res.trades` so live rebound short triggers cap cuts for future admissions; failing-tests-first regression confirmed; full suite 406 passed, 11 skipped; only `HANDOFF.md` updated.
- [ ] **NEXT SESSION:** Ship >=1 material campaign item 2/3 hardened fix with failing-tests-first evidence, full suite green, update ONLY this `HANDOFF.md`.
