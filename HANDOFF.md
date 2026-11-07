# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-11-07T13:43:10Z
## SINGLE CANONICAL HANDOFF
Only this root `HANDOFF.md` is durable. Do **not** create/read any other handoff file.

## SESSION 2026-11-07T13:43:10Z — TRADERESULT TOTAL_PNL REBOUND-LEG DEFAULT CONTRACT HARDENED (MATERIAL, EVIDENCED)
- **Repo-name priority:** `CRASH-REBOUND-STRATEGY` → fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly engine only; **do not claim** 20s slicing / explicit spread / L2 order-book impact.
- **Non-negotiable spec contracts (unchanged):** hourly funding on **every leg** (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on all exits including edge/missing-data/missing-ETH/fallback paths and missing/incomplete bars as applicable; hourly liquidation at worst price with correct sequencing vs stop/target/time, correct notional/timing/penalty; **stopped buy never opens rebound short**; 8x safety stop (`use_spec_safety_stop` ratio semantics); rebound short `-9%/48h/+40%`; ETH hedge every leg, vol-ratio over 336h capped 3x; `RSI(21)<20` next-hour open, deepest-first; `>= $5M` 24h volume in **all spec-compliant gating paths** (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only, never top-ups); one position/coin; strict no-look-ahead.
- **Bottlenecks:** none blocking. Sole durable handoff remains this root `HANDOFF.md`. `scripts/__pycache__/run_portfolio.cpython-312.pyc` may appear in worktree from imports; not evidence.

- **Baseline (verified 2026-11-07T13:42:30Z UTC context):** `python -m pytest tests/ -q --tb=no` → **397 passed, 11 skipped in 42.11s**.

- **Material defect exposed (failing-tests-first):** `src/backtest/engine.py` `TradeResult.__init__` defaulted `total_pnl = pnl + hedge_pnl` when `total_pnl` was omitted. Engine construction paths always pass explicit `total_pnl`, but direct construction/consumer fallback semantics silently dropped `rebound_short_pnl` and `rebound_hedge_pnl` (grand-total accounting risk for rebound trades; inconsistent with campaign item 1 rebound-short hedge funding/attribution work).

- **Shipped (failing-tests-first, minimal fix):** `src/backtest/engine.py`
  - `TradeResult` default now: `total_pnl = pnl + hedge_pnl + rebound_short_pnl + rebound_hedge_pnl` when `total_pnl` is omitted.
  - Explicit `total_pnl` still overrides (engine/runtime authoritative path preserved).

- **Regressions added (failing-tests-first):** `tests/test_traderesult_total_pnl_default_rebound_20261107.py` (3 tests, arithmetic/non-evidence):
  1. `test_total_pnl_default_includes_rebound_short_and_rebound_hedge` — **FAILED before fix** (`got 90.0, expected 135.0`); passes after.
  2. `test_total_pnl_explicit_overrides_default` — passes.
  3. `test_total_pnl_default_without_rebound_matches_existing_behavior` — passes.

- **Verification evidence (2026-11-07T13:43:10Z UTC):**
  - `python -m pytest tests/test_traderesult_total_pnl_default_rebound_20261107.py -q --tb=short` (pre-fix red): `1 failed, 2 passed in 0.03s` (`default total_pnl dropped rebound legs: got 90.0, expected 135.0`).
  - `python -m pytest tests/test_traderesult_total_pnl_default_rebound_20261107.py tests/test_portfolio_daily_loss_cross_bar_reconciliation_20261107.py tests/test_portfolio_gating_no_lookahead_20261107.py tests/test_portfolio_no_lookahead_admission_sizing_gating_20261107.py -q --tb=no` → **18 passed**.
  - `python -m pytest tests/ -q --tb=no` → **400 passed, 11 skipped in 41.92s**.

- **Files changed this session:** `src/backtest/engine.py`, `tests/test_traderesult_total_pnl_default_rebound_20261107.py`, `HANDOFF.md`.

- **Remaining risks / next heavy focus:**
  - Audit consumers that may still compute grand totals ad hoc from `pnl + hedge_pnl` (instead of `total_pnl`) for rebound trades; add failing-tests-first coverage where behavior is reachable.
  - Portfolio reconciles realized PnL/halt from `total_pnl` at exit-bar time only (no look-ahead) — verify `total_pnl` semantics against any wrapper that reports/aggregates rebound/multi-leg trades outside engine.
  - `risk_state.date` may be empty in some summary states; consider deterministic final-day normalization if downstream requires it.
  - Campaign item 2 residual: continue no-lookahead/admission/cap/timestamp audit for wrapper/runner paths bypassing `run_portfolio_simulation` semantics; add failing-tests-first coverage for portfolio-level live rebound-short notional invariants.
  - Campaign item 3: $5M gating integrity regression watch across all spec-compliant surfaces (`backtest_simple` remains low-level/non-gated by design).
  - Campaign item 4: verified-data/provenance hardening (fail-closed checksums/manifests); broaden universe only with archived verified data + full provenance. BTC/ETH 283d 0-trade remains sole verified truth.

## PRIOR SESSIONS (CONDENSED)
- **2026-11-07T13:41:05Z:** portfolio daily-loss/exposure no-lookahead reconciliation; realized exits applied only at/through exit bar (3 tests). 397 passed, 11 skipped.
- **2026-11-07T12:37:09Z:** rebound-short attribution fields + risk_state rebound-short notional registration (7 tests). 394 passed, 11 skipped.
- **2026-11-07T12:27:42Z:** cleared bottlenecks; fixed RiskState timestamp-normalized daily accounting preserving live cap-cut/notional state (3 tests). 387 passed, 11 skipped.

## INITIAL TASK MESSAGE (TIMESTAMPED, SINGLE, NEXT AGENTIC SESSION) — EXECUTE HEAVY WORK NOW
`CRASH-REBOUND-STRATEGY | 2026-11-07T13:43:10Z | MANDATORY: REBOUND TOTAL_PNL CONSUMER AUDIT + NO-LOOKAHEAD/PORTFOLIO RESIDUAL. Baseline 400 passed/11 skipped green. FAILING-TESTS-FIRST.`

**Required execution order (ship >=1 material hardened item this session):**
1. `python -m pytest tests/ -q --tb=no` (must stay green baseline: 400 passed, 11 skipped expected absent environment drift).
2. **Audit `pnl + hedge_pnl` grand-total consumers for rebound trades:** find reachable code/tests/runners that compute totals without `total_pnl`/rebound legs. Write FAILING tests first for any real defect, minimal fix only.
3. **Campaign item 2 residual in parallel priority:** no-lookahead/admission/cap/timestamp/daily-loss regression watch across `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners/portfolio. Confirm live rebound-short notional invariants and timestamp/day normalization. Failing-tests-first for real defects.
4. **Campaign item 3 if (2)/(3) clean:** $5M gating integrity regression watch on all spec-compliant surfaces; do not conflate `backtest_simple` low-level executor behavior.
5. `python -m pytest tests/ -q --tb=no` — full suite green.
6. **Update ONLY this root `HANDOFF.md`** with UTC timestamp, exact commands/results, files changed, shipped material item(s), remaining risks, and next heavy task. No other handoff files.

## HEAVY FOCUS CAMPAIGN (MUST EXECUTE IN ORDER; FUTURE AGENTS MAY NOT AVOID)
1. **[DONE 2026-11-07T12:37:09Z]** Rebound-short hedge funding/attribution + atomic risk/trade-log contracts; same-bar boundary lock.
2. **[IN PROGRESS / RESIDUAL]** No-lookahead & portfolio-cap/timestamp/daily-loss regression watch (admission/sizing/gating/history/cap cuts equal-share old+new, no top-ups; realized exits reconciled only at/through exit bar; live rebound-short notional invariants; rebound grand-total consumer audit).
3. **$5M gating integrity regression watch** (all spec-compliant surfaces; `backtest_simple` is low-level/non-gated).
4. **Verified-data/provenance hardening** (fail-closed checksums/manifests; broaden universe only with archived verified data + full provenance).
5. **Every session gate:** `python -m pytest tests/ -q --tb=no` green, ship >=1 material hardened item with evidence, update only `HANDOFF.md`.

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
- [x] Baseline green and improved (400 passed, 11 skipped).
- [x] 283d BTC/ETH verified/provenanced; real campaign truthful (0 trades).
- [x] RiskState timestamp-normalized daily accounting preserves live cap-cut/notional state.
- [x] TradeResult rebound-short attribution + risk_state rebound-short notional registration.
- [x] Portfolio realized daily-loss/exposure reconciliation is no-look-ahead (exits applied only at/through exit bar), with cross-bar + same-bar probe-leak regressions.
- [x] TradeResult default `total_pnl` includes rebound short/hedge legs (explicit `total_pnl` still authoritative).
- [ ] **NEXT SESSION (NOW):** Ship >=1 material rebound grand-total consumer audit / campaign item 2/3 hardened fix with failing-tests-first evidence, full suite green, update ONLY this `HANDOFF.md`.
