# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-11-07T13:50:27Z
## SINGLE CANONICAL HANDOFF
Only this root `HANDOFF.md` is durable. Do **not** create/read any other handoff file.

## SESSION 2026-11-07T14:43:40Z — PORTFOLIO LIVE REBOUND-SHORT NOTIONAL RESERVATION HARDENED; SUITE GREEN 406/11; HANDOFF REFRESHED
- **Repo-name priority:** `CRASH-REBOUND-STRATEGY` → fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly engine only; **do not claim** 20s slicing / explicit spread / L2 order-book impact.
- **Non-negotiable spec contracts (unchanged):** hourly funding on **every leg** (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on all exits including edge/missing-data/missing-ETH/fallback paths and missing/incomplete bars as applicable; hourly liquidation at worst price with correct sequencing vs stop/target/time, correct notional/timing/penalty; **stopped buy never opens rebound short**; 8x safety stop (`use_spec_safety_stop` ratio semantics); rebound short `-9%/48h/+40%`; ETH hedge every leg, vol-ratio over 336h capped 3x; `RSI(21)<20` next-hour open, deepest-first; `>= $5M` 24h volume in **all spec-compliant gating paths** (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only, never top-ups); one position/coin; strict no-look-ahead.
- **Bottlenecks:** none blocking. Sole durable handoff remains this root `HANDOFF.md`. `research_state/candle_coverage_gap_report.json` may be dirtied by local tooling; reverted to HEAD (no material change). `__pycache__` artifacts from imports are not evidence.

- **Baseline (verified this session, start):** `python -m pytest tests/ -q --tb=no` → **404 passed, 11 skipped in 42.22s**.

- **Material defect exposed (failing-tests-first, campaign item 2 residual — live notional/cap):** `scripts/run_portfolio.py` reserved each admitted trade as `res.shares * res.entry_price` (long-entry notional) for the full `occupied_until`/overlay lifetime. For `target_rebound_short` multi-leg trades, the rebound short opens at `trades_log` short-entry price (≈ target exit, e.g. 109) while `res.entry_price` remains the original long entry (e.g. 100) and `res.shares` is reused. Result: portfolio under-reserved live short-leg exposure (10900 vs 10000 in probe) and allowed a future-bar admission that should have triggered the 120% gross-cap/equal-share path. `TradeResult`/engine do not expose a short-entry notional field; short leg entry is present in `res.trades` (leg log).

- **Shipped (failing-tests-first, minimal fix):** `scripts/run_portfolio.py` reservation/cap path
  - After computing `executed_notional = shares * entry_price`, for multi-leg results scan `res.trades` for `side=='short'` and promote `executed_notional` to `max(executed_notional, short_leg_entry * res.shares)`. This makes overlay/cap/equal-share admission see live rebound-short notional while the short holds. No behavior change for non-rebound trades (no short leg in `res.trades`).
  - Same-bar probe admission remains real-engine/reservation-overlay based (no future-exit look-ahead into same-bar sibling decisions), per existing semantics.

- **Regressions added (failing-tests-first):** `tests/test_portfolio_rebound_short_live_notional_reservation_20261107.py` (2 tests, synthetic/non-evidence):
  1. `test_rebound_short_live_notional_triggers_cap_cut_future_admission` — **FAILED before fix** (`Y.shares=15.0`, wrong long-entry reservation `10000+1500<=12000` => no cut; live short notional `10900+1500>12000` must trigger cut path). **Passes after fix** (`Y.shares=60.0` under equal-share schedule; assertion: shares != uncut 15).
  2. `test_final_state_reconciles_after_rebound_short_live_notional_trade` — passes; final occupancy/gross/notionals reconcile to zero.

- **Verification evidence (2026-11-07T14:43:40Z UTC):**
  - Pre-fix red: `python -m pytest tests/test_portfolio_rebound_short_live_notional_reservation_20261107.py -q --tb=short` → `1 failed, 1 passed` (asserted 15.0 uncut).
  - Targeted regression: `python -m pytest tests/test_portfolio_cap_liquidation_rebound_interaction_20261107.py tests/test_portfolio_no_lookahead_admission_sizing_gating_20261107.py tests/test_portfolio_filter_universe_no_lookahead_20261107.py tests/test_portfolio_gating_no_lookahead_20261107.py tests/test_rebound_short_attribution_and_risk_state_20261107.py -q --tb=short` → **26 passed**.
  - Full suite: `python -m pytest tests/ -q --tb=no` → **406 passed, 11 skipped in 41.81s**.

- **Files changed this session (material):** `scripts/run_portfolio.py`, `tests/test_portfolio_rebound_short_live_notional_reservation_20261107.py`, `HANDOFF.md`. Reverted non-material: `research_state/candle_coverage_gap_report.json`.

- **Remaining risks / next heavy focus:**
  - Campaign item 2 residual: no-lookahead/admission/cap/timestamp/daily-loss regression watch across `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners/portfolio. Reservation now uses max(long-entry, rebound-short-leg-entry) notional from `res.trades`; consider exposing explicit live/max leg notional on `TradeResult` if future paths need it without leg-log parsing. Rebound hedge notional/edge cases and `occupied_until` occupancy semantics for multi-leg bars still warrant targeted audit. Timestamp/day normalization (`risk_state.date` may be empty in some summary states) remains.
  - Campaign item 3: $5M gating integrity regression watch across all spec-compliant surfaces (`backtest_simple` low-level/non-gated by design; `run_backtest.py`/fixture smoke runners not spec-gated evidence).
  - Campaign item 4: verified-data/provenance hardening (fail-closed checksums/manifests); broaden universe only with archived verified data + full provenance. BTC/ETH 283d 0-trade remains sole verified truth.

## PRIOR SESSIONS (CONDENSED)
- **2026-11-07T13:50:27Z:** grand-total consumer audit shipped (`campaign_metrics:_trade_pnl` + runner fallback); rebound legs never dropped. 404 passed, 11 skipped.
- **2026-11-07T13:47:34Z:** baseline re-verified green; rebound `total_pnl` default fix shipped (TradeResult). 400 passed, 11 skipped.
- **2026-11-07T13:41:05Z:** portfolio daily-loss/exposure no-lookahead reconciliation; realized exits applied only at/through exit bar (3 tests). 397 passed, 11 skipped.
- **2026-11-07T12:37:09Z:** rebound-short attribution fields + risk_state rebound-short notional registration (7 tests). 394 passed, 11 skipped.
- **2026-11-07T12:27:42Z:** cleared bottlenecks; fixed RiskState timestamp-normalized daily accounting preserving live cap-cut/notional state (3 tests). 387 passed, 11 skipped.

## INITIAL TASK MESSAGE (TIMESTAMPED, SINGLE, NEXT AGENTIC SESSION) — EXECUTE HEAVY WORK NOW
`CRASH-REBOUND-STRATEGY | 2026-11-07T14:43:40Z | MANDATORY: CAMPAIGN ITEM 2/3 RESIDUAL (NO-LOOKAHEAD/ADMISSION/CAP/TIMESTAMP + $5M GATING INTEGRITY). Baseline 406 passed/11 skipped green; portfolio live rebound-short notional reservation hardened (cap/admission sees short-leg notional, not long entry). No bottlenecks; sole durable handoff is this root HANDOFF.md. FAILING-TESTS-FIRST. SHIP >=1 MATERIAL HARDENED ITEM.`

**Required execution order:**
1. `python -m pytest tests/ -q --tb=no` (must stay green baseline: 406 passed, 11 skipped expected absent environment drift).
2. **Campaign item 2 residual (priority):** no-lookahead/admission/cap/timestamp/daily-loss regression watch across `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners/portfolio. Audit rebound hedge live-notional/edge cases, multi-leg `occupied_until`/reservation invariants, and timestamp/day normalization (`risk_state.date` may be empty in some summary states). Consider explicit live/max leg notional on `TradeResult` if needed. Failing-tests-first for real defects.
3. **Campaign item 3 if (2) clean:** $5M gating integrity regression watch on all spec-compliant surfaces; do not conflate `backtest_simple`/`run_backtest.py`/fixture smoke low-level/non-gated paths with spec-compliant gating.
4. **Campaign item 4 if (2)/(3) clean:** verified-data/provenance hardening (fail-closed checksums/manifests); broaden universe only with archived verified data + full provenance.
5. `python -m pytest tests/ -q --tb=no` — full suite green.
6. **Update ONLY this root `HANDOFF.md`** with UTC timestamp, exact commands/results, files changed, shipped material item(s), remaining risks, and next heavy task. No other handoff files.

## HEAVY FOCUS CAMPAIGN (MUST EXECUTE IN ORDER; FUTURE AGENTS MAY NOT AVOID)
1. **[DONE 2026-11-07T12:37:09Z]** Rebound-short hedge funding/attribution + atomic risk/trade-log contracts; same-bar boundary lock.
2. **[DONE 2026-11-07T13:50:27Z]** Rebound grand-total consumer audit hardened (`campaign_metrics:_trade_pnl` + `run_portfolio.py:228`); rebound short/hedge legs never silently dropped in attribution/aggregation.
3. **[IN PROGRESS / RESIDUAL, 2026-11-07T14:43:40Z hardening]** No-lookahead & portfolio-cap/timestamp/daily-loss regression watch (admission/sizing/gating/history/cap cuts equal-share old+new, no top-ups; realized exits reconciled only at/through exit bar). Portfolio now reserves max(long-entry, rebound-short-leg-entry) live notional from `res.trades` for overlay/cap. Remaining: rebound hedge live-notional/edge cases, explicit TradeResult live/max leg notional if needed, timestamp/day normalization, multi-leg occupancy invariants.
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
- [x] Rebound grand-total consumer audit shipped (`campaign_metrics:_trade_pnl` + `run_portfolio.py` grand-total fallback).
- [x] **THIS SESSION (2026-11-07T14:43:40Z):** Portfolio live rebound-short notional reservation hardened (`scripts/run_portfolio.py`: max long-entry/short-leg-entry notional for overlay/cap); failing-tests-first (`tests/test_portfolio_rebound_short_live_notional_reservation_20261107.py`, 2 tests, 1 red before fix); targeted 26 passed; full suite **406 passed, 11 skipped**; only `HANDOFF.md` updated (+ reverted non-material `research_state/candle_coverage_gap_report.json`).
- [ ] **NEXT SESSION:** Ship >=1 material campaign item 2/3 hardened fix with failing-tests-first evidence, full suite green, update ONLY this `HANDOFF.md`.
