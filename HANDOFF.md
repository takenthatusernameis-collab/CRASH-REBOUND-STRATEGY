# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-11-07T13:41:05Z
## SINGLE CANONICAL HANDOFF
Only this root `HANDOFF.md` is durable. Do **not** create/read any other handoff file.

## SESSION 2026-11-07T13:41:05Z — PORTFOLIO DAILY-LOSS/EXPOSURE NO-LOOKAHEAD RECONCILIATION (MATERIAL, EVIDENCED)
- **Repo-name priority:** `CRASH-REBOUND-STRATEGY` → fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly engine only; **do not claim** 20s slicing / explicit spread / L2 order-book impact.
- **Non-negotiable spec contracts (unchanged):** hourly funding on **every leg** (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on all exits including edge/missing-data/missing-ETH/fallback paths and missing/incomplete bars as applicable; hourly liquidation at worst price with correct sequencing vs stop/target/time, correct notional/timing/penalty; **stopped buy never opens rebound short**; 8x safety stop (`use_spec_safety_stop` ratio semantics); rebound short `-9%/48h/+40%`; ETH hedge every leg, vol-ratio over 336h capped 3x; `RSI(21)<20` next-hour open, deepest-first; `>= $5M` 24h volume in **all spec-compliant gating paths** (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only, never top-ups); one position/coin; strict no-look-ahead.
- **Bottlenecks:** none blocking. Sole durable handoff remains this root `HANDOFF.md`. Accidental `research_state/candle_coverage_gap_report.json` drift was reverted (not part of this hardening). `scripts/__pycache__/run_portfolio.cpython-312.pyc` may appear in worktree from test imports; do not treat as evidence.

- **Baseline (verified 2026-11-07T13:41:05Z UTC):** `python -m pytest tests/ -q --tb=no` → **394 passed, 11 skipped in 41.59s**.

- **Material defect exposed (failing-tests-first):** `scripts/run_portfolio.py` probed admitted trades with `backtest_simple` over the full series for execution realism but never reconciled master `risk_state.realized_pnl`/`daily_loss_limit_hit` from realized exits. Consequences: (1) a loss realized at exit bar N did **not** block a future same-day admission at bar M>N under `max_daily_loss_pct`; (2) master exposure/daily state could drift from the reservation overlay across bars. Same-bar probe future exits were already prevented from leaking into sibling probes via probe copies, but cross-bar master reconciliation was missing.

- **Shipped (failing-tests-first, minimal fix):** `scripts/run_portfolio.py`
  - Added `pending_realized_exits: [(exit_idx, exit_timestamp, trade_pnl)]` for admitted trades; records `total_pnl` (coin + hedge legs, per engine contract) at admission.
  - Added `_reconcile_realized_through(bar_idx, max_len)` — applies only exits with `exit_idx <= bar_idx` (no look-ahead), normalizes day via `str(ts)[:10]`, resets daily counters on true day change, accumulates `realized_pnl`, and sets `daily_loss_limit_hit` when `daily_loss_pct(capital) >= max_daily_loss_pct`.
  - Added `_sync_master_overlay(bar_date)` — syncs master `open_position_notionals/gross_exposure/open_positions` from reservation overlay (`open_notionals`) and normalizes day without wiping live exposure.
  - Scan loop now reconciles realized exits through decision bar `i`, syncs overlay/date, frees occupancy before candidate admission; final reconciliation runs through `max_len-1`.
  - Probe base still uses master realized PnL/halt reconciled through bar `i` only; probe runs full series for execution realism but does not mutate master. Same-bar reservation overlay/cap/max_positions behavior preserved.

- **Regressions added (failing-tests-first):** `tests/test_portfolio_daily_loss_cross_bar_reconciliation_20261107.py` (3 tests, synthetic non-evidence):
  1. `test_realized_daily_loss_blocks_future_same_day_admission_after_exit_bar` — A exits stopped (loss > daily limit) at bar 6; B signal at bar 12 same day must be blocked. **Failed before fix** (`B admitted after realized daily loss halt`); passes after.
  2. `test_same_bar_probe_future_loss_does_not_block_sibling_via_master_state` — both fire same bar; A loses later, B profits; B must not be blocked by A probe future loss leaking into master (reservation/cap separate). Passes.
  3. `test_daily_loss_resets_on_new_day_with_timestamp_normalization` — day 1 loss halts day 1 accounting; day 2 admission allowed after timestamp-normalized day reset. Passes.

- **Verification evidence (2026-11-07T13:41:05Z UTC):**
  - `python -m pytest tests/test_portfolio_daily_loss_cross_bar_reconciliation_20261107.py -q --tb=short` → **3 passed**.
  - `python -m pytest tests/test_portfolio_gating_no_lookahead_20261107.py tests/test_portfolio_no_lookahead_admission_sizing_gating_20261107.py tests/test_portfolio_filter_universe_no_lookahead_20261107.py tests/test_portfolio_cap_liquidation_rebound_interaction_20261107.py -q --tb=no` → **19 passed**.
  - `python -m pytest tests/ -q --tb=no` → **397 passed, 11 skipped in 42.15s**.

- **Files changed this session:** `scripts/run_portfolio.py`, `tests/test_portfolio_daily_loss_cross_bar_reconciliation_20261107.py`, `HANDOFF.md` (reverted unrelated `research_state/candle_coverage_gap_report.json`).

- **Remaining risks / next heavy focus:**
  - Portfolio now reconciles realized PnL/halt from `total_pnl` at exit-bar time; verify any edge where `total_pnl` vs `pnl` semantics differ for rebound/multi-leg accounting consumers (engine contract: `total_pnl` is grand total).
  - `TradeResult.__init__` default `total_pnl = self.pnl + self.hedge_pnl` remains arithmetically inconsistent when rebound short present (engine always passes `total_pnl`); consumers must use `total_pnl` for grand total.
  - `risk_state.date` may be empty in some summary states; consider deterministic final-day normalization if downstream requires it.
  - Campaign item 2 residual: continue no-lookahead/admission/cap/timestamp audit for any wrapper/runner paths that bypass `run_portfolio_simulation` semantics; add failing-tests-first coverage for portfolio-level live rebound-short notional invariants.
  - Campaign item 3: $5M gating integrity regression watch across all spec-compliant surfaces (`backtest_simple` remains low-level/non-gated by design).
  - Campaign item 4: verified-data/provenance hardening (fail-closed checksums/manifests); broaden universe only with archived verified data + full provenance. BTC/ETH 283d 0-trade remains sole verified truth.

## PRIOR SESSIONS (CONDENSED)
- **2026-11-07T12:37:09Z:** rebound-short attribution fields + risk_state rebound-short notional registration (7 tests). 394 passed, 11 skipped.
- **2026-11-07T12:27:42Z:** cleared bottlenecks; fixed RiskState timestamp-normalized daily accounting preserving live cap-cut/notional state (3 tests). 387 passed, 11 skipped.

## INITIAL TASK MESSAGE (TIMESTAMPED, SINGLE, NEXT AGENTIC SESSION) — EXECUTE HEAVY WORK NOW
`CRASH-REBOUND-STRATEGY | 2026-11-07T13:41:05Z | MANDATORY: NO-LOOKAHEAD/PORTFOLIO RESIDUAL + $5M GATING/PROVENANCE WATCH. Baseline 397 passed/11 skipped green. FAILING-TESTS-FIRST.`

**Required execution order (ship >=1 material hardened item this session):**
1. `python -m pytest tests/ -q --tb=no` (must stay green baseline: 397 passed, 11 skipped expected absent environment drift).
2. **Campaign item 2 residual — No-lookahead & portfolio-cap/timestamp regression watch:** audit admission/sizing/gating/history/cap cuts (equal-share old+new, no top-ups), daily-loss/halt, and timestamp/day normalization across `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners/portfolio. Confirm live rebound-short notional + `total_pnl`/consumer reconciliation has regression coverage. Write FAILING tests first for any real defect, minimal fix only.
3. **Campaign item 3 in parallel priority if (2) is clean:** $5M gating integrity regression watch on all spec-compliant surfaces; do not conflate `backtest_simple` low-level executor behavior.
4. `python -m pytest tests/ -q --tb=no` — full suite green.
5. **Update ONLY this root `HANDOFF.md`** with UTC timestamp, exact commands/results, files changed, shipped material item(s), remaining risks, and next heavy task. No other handoff files.

## HEAVY FOCUS CAMPAIGN (MUST EXECUTE IN ORDER; FUTURE AGENTS MAY NOT AVOID)
1. **[DONE 2026-11-07T12:37:09Z]** Rebound-short hedge funding/attribution + atomic risk/trade-log contracts; same-bar boundary lock.
2. **[IN PROGRESS / RESIDUAL]** No-lookahead & portfolio-cap/timestamp/daily-loss regression watch (admission/sizing/gating/history/cap cuts equal-share old+new, no top-ups; realized exits reconciled only at/through exit bar; live rebound-short notional invariants).
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
- [x] Baseline green and improved (397 passed, 11 skipped).
- [x] 283d BTC/ETH verified/provenanced; real campaign truthful (0 trades).
- [x] RiskState timestamp-normalized daily accounting preserves live cap-cut/notional state.
- [x] TradeResult rebound-short attribution + risk_state rebound-short notional registration.
- [x] Portfolio realized daily-loss/exposure reconciliation is no-look-ahead (exits applied only at/through exit bar), with cross-bar + same-bar probe-leak regressions.
- [ ] **NEXT SESSION (NOW):** Ship >=1 material campaign item 2/3 hardened fix with failing-tests-first evidence, full suite green, update ONLY this `HANDOFF.md`.
