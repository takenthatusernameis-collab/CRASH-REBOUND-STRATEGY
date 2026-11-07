# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-11-07T13:50:27Z
## SINGLE CANONICAL HANDOFF
Only this root `HANDOFF.md` is durable. Do **not** create/read any other handoff file.

## SESSION 2026-11-07T13:50:27Z — GRAND-TOTAL CONSUMER AUDIT SHIPPED; SUITE GREEN 404/11; HANDOFF REFRESHED
- **Repo-name priority:** `CRASH-REBOUND-STRATEGY` → fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly engine only; **do not claim** 20s slicing / explicit spread / L2 order-book impact.
- **Non-negotiable spec contracts (unchanged):** hourly funding on **every leg** (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on all exits including edge/missing-data/missing-ETH/fallback paths and missing/incomplete bars as applicable; hourly liquidation at worst price with correct sequencing vs stop/target/time, correct notional/timing/penalty; **stopped buy never opens rebound short**; 8x safety stop (`use_spec_safety_stop` ratio semantics); rebound short `-9%/48h/+40%`; ETH hedge every leg, vol-ratio over 336h capped 3x; `RSI(21)<20` next-hour open, deepest-first; `>= $5M` 24h volume in **all spec-compliant gating paths** (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only, never top-ups); one position/coin; strict no-look-ahead.
- **Bottlenecks:** none blocking. Sole durable handoff remains this root `HANDOFF.md`. `scripts/__pycache__/run_portfolio.cpython-312.pyc` may appear in worktree from imports; not evidence.

- **Baseline (verified this session):** `python -m pytest tests/ -q --tb=no` → **404 passed, 11 skipped in 41.81s** (was 400 passed; +4 new grand-total rebound-leg tests).

- **Material defect exposed (failing-tests-first):** consumers computing a trade grand total from bare `pnl` instead of `total_pnl` silently dropped `rebound_short_pnl` / `rebound_hedge_pnl` (and `hedge_pnl`) legs, corrupting attribution/aggregation for rebound trades. Prime surface: `src/metrics/campaign_metrics.py:_trade_pnl` fallback `t.get("pnl", 0.0)`. Runner surface: `scripts/run_portfolio.py:228` `getattr(res, "total_pnl", res.pnl)` bare-`pnl` fallback.

- **Shipped (failing-tests-first, minimal fix):** `src/metrics/campaign_metrics.py`
  - `_trade_pnl` default now: grand total `pnl + hedge_pnl + rebound_short_pnl + rebound_hedge_pnl` when `total_pnl` key absent/`None` (mirrors `TradeResult.__init__`); explicit `total_pnl` still authoritative.
  - `scripts/run_portfolio.py:228`: `getattr(res, "total_pnl", res.pnl)` bare-`pnl` fallback hardened to leg-sum grand total when `total_pnl` is absent; no behavior change via `backtest_simple` (always sets `total_pnl`).

- **Regressions added (failing-tests-first):** `tests/test_campaign_metrics_grand_total_rebound_legs_20261107.py` (4 tests, arithmetic/non-evidence):
  1. `test_trade_pnl_without_total_pnl_includes_all_legs` — **FAILED before fix** (got 100.0, expected 135.0); passes after.
  2. `test_trade_pnl_total_pnl_authoritative_overrides_leg_sum` — passes.
  3. `test_trade_pnl_without_rebound_legs_matches_existing_behavior` — passes.
  4. `test_trade_pnl_leg_summary_uses_grand_total_not_bare_pnl` — FAILED before fix (got 100.0, expected 135.0); passes after.

- **Verification evidence (2026-11-07T13:50:27Z UTC):**
  - `python -m pytest tests/test_campaign_metrics_grand_total_rebound_legs_20261107.py -q --tb=short` (pre-fix red): `3 failed, 1 passed`.
  - `python -m pytest tests/ -q --tb=no` → **404 passed, 11 skipped in 41.81s**.

- **Files changed this session:** `src/metrics/campaign_metrics.py`, `scripts/run_portfolio.py`, `tests/test_campaign_metrics_grand_total_rebound_legs_20261107.py`, `HANDOFF.md`.

- **Remaining risks / next heavy focus:**
  - Campaign item 2 residual: no-lookahead/admission/cap/timestamp/daily-loss regression watch across `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners/portfolio; confirm live rebound-short notional invariants and timestamp/day normalization. Failing-tests-first for real defects.
  - Campaign item 3: $5M gating integrity regression watch across all spec-compliant surfaces (`backtest_simple` remains low-level/non-gated by design).
  - Campaign item 4: verified-data/provenance hardening (fail-closed checksums/manifests); broaden universe only with archived verified data + full provenance. BTC/ETH 283d 0-trade remains sole verified truth.
  - `risk_state.date` may be empty in some summary states; consider deterministic final-day normalization if downstream requires it.

## PRIOR SESSIONS (CONDENSED)
- **2026-11-07T13:47:34Z:** baseline re-verified green; rebound `total_pnl` default fix shipped (TradeResult). 400 passed, 11 skipped.
- **2026-11-07T13:41:05Z:** portfolio daily-loss/exposure no-lookahead reconciliation; realized exits applied only at/through exit bar (3 tests). 397 passed, 11 skipped.
- **2026-11-07T12:37:09Z:** rebound-short attribution fields + risk_state rebound-short notional registration (7 tests). 394 passed, 11 skipped.
- **2026-11-07T12:27:42Z:** cleared bottlenecks; fixed RiskState timestamp-normalized daily accounting preserving live cap-cut/notional state (3 tests). 387 passed, 11 skipped.

## INITIAL TASK MESSAGE (TIMESTAMPED, SINGLE, NEXT AGENTIC SESSION) — EXECUTE HEAVY WORK NOW
`CRASH-REBOUND-STRATEGY | 2026-11-07T13:50:27Z | MANDATORY: CAMPAIGN ITEM 2/3 RESIDUAL (NO-LOOKAHEAD/ADMISSION/CAP/TIMESTAMP + $5M GATING INTEGRITY). Baseline 404 passed/11 skipped green; grand-total consumer audit shipped (rebound legs never dropped). No bottlenecks; sole durable handoff is this root HANDOFF.md. FAILING-TESTS-FIRST. SHIP >=1 MATERIAL HARDENED ITEM.`

**Required execution order:**
1. `python -m pytest tests/ -q --tb=no` (must stay green baseline: 404 passed, 11 skipped expected absent environment drift).
2. **Campaign item 2 residual (parallel priority):** no-lookahead/admission/cap/timestamp/daily-loss regression watch across `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners/portfolio. Confirm live rebound-short notional invariants and timestamp/day normalization. Failing-tests-first for real defects.
3. **Campaign item 3 if (2) clean:** $5M gating integrity regression watch on all spec-compliant surfaces; do not conflate `backtest_simple` low-level executor behavior.
4. **Campaign item 4 if (2)/(3) clean:** verified-data/provenance hardening (fail-closed checksums/manifests); broaden universe only with archived verified data + full provenance.
5. `python -m pytest tests/ -q --tb=no` — full suite green.
6. **Update ONLY this root `HANDOFF.md`** with UTC timestamp, exact commands/results, files changed, shipped material item(s), remaining risks, and next heavy task. No other handoff files.

## HEAVY FOCUS CAMPAIGN (MUST EXECUTE IN ORDER; FUTURE AGENTS MAY NOT AVOID)
1. **[DONE 2026-11-07T12:37:09Z]** Rebound-short hedge funding/attribution + atomic risk/trade-log contracts; same-bar boundary lock.
2. **[DONE 2026-11-07T13:50:27Z]** Rebound grand-total consumer audit hardened (`campaign_metrics:_trade_pnl` + `run_portfolio.py:228`); rebound short/hedge legs never silently dropped in attribution/aggregation.
3. **[IN PROGRESS / RESIDUAL]** No-lookahead & portfolio-cap/timestamp/daily-loss regression watch (admission/sizing/gating/history/cap cuts equal-share old+new, no top-ups; realized exits reconciled only at/through exit bar; live rebound-short notional invariants).
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
- [x] Baseline green and improved (404 passed, 11 skipped).
- [x] 283d BTC/ETH verified/provenanced; real campaign truthful (0 trades).
- [x] RiskState timestamp-normalized daily accounting preserves live cap-cut/notional state.
- [x] TradeResult rebound-short attribution + risk_state rebound-short notional registration.
- [x] Portfolio realized daily-loss/exposure reconciliation is no-look-ahead (exits applied only at/through exit bar), with cross-bar + same-bar probe-leak regressions.
- [x] TradeResult default `total_pnl` includes rebound short/hedge legs (explicit `total_pnl` still authoritative).
- [x] **THIS SESSION:** Rebound grand-total consumer audit shipped (`campaign_metrics:_trade_pnl` + `run_portfolio.py:228`); failing-tests-first evidence; full suite green; only `HANDOFF.md` updated.
- [ ] **NEXT SESSION:** Ship >=1 material campaign item 2/3 hardened fix with failing-tests-first evidence, full suite green, update ONLY this `HANDOFF.md`.
