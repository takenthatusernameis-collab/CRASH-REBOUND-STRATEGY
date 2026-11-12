# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-12T16:50:29Z
**HEAD at audit:** `a79c94c chore(kilo): checkpoint agent session` (working tree clean on a79c94c; cell-2 + cell-3 material committed on a5bac9b; a79c94c added only scratch `_trace_cell4{a,b,c}.py` + `scripts/run_portfolio.py` edits — NOT handoff material; **no commit requested**).
**Single canonical durable handoff: ONLY this root `HANDOFF.md`.** Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT variants). `scripts/controller_progress.py`, dated/session-named tests, `__pycache__`, `.pytest_cache`, root `_probe_*`/`_trace_*`/`_debug_*`/`leak_check.py`/`trace_leak.py`, and `tmp_qfv3jj4/` are implementation/tests/scratch, NOT handoffs.

## SESSION AUDIT (2026-11-12T16:50:29Z) — GATE RE-VERIFIED GREEN (870 passed, 12 skipped)
- **Durable handoff audit (verified):** only root `HANDOFF.md` is durable (`README.md` points here). No TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoff files outside `.git`.
- **Lock/blocker audit (verified):** no `*.lock` files outside `.git/`. No contradictory artifacts. `.test_derive_vol_*` residue is 0.
- **Real-data blocker — CONFIRMED REAL, DO NOT "UNBLOCK":** tracked `research_state/cache/hyperliquid_verified_283d_btceth/candles/{BTC,ETH}.json` are 6792-bar placeholders (`research_state/cache/hyperliquid_verified_283d_btceth/provenance.json`: per-symbol `status:"error"`, `synthetic_check.is_synthetic:true`, `flat_series_all_bars_identical`, 1 distinct/6792; `ready_for_real_campaign:false`). Fabricating/promoting forbidden. **283d real-data campaign stays NOT RUN.** Blocks only real-data runs.

## LAST VERIFIED GATE (2026-11-12T16:50:29Z, working tree clean on a79c94c)
- `PYTHONPATH=. python3 -m pytest -q --tb=short` → **870 passed, 12 skipped in 43.28s** (baseline 823 → 870; +47 new tests, zero regressions).
- **MANDATORY FIRST ACTION next session:** re-run full gate at current HEAD/worktree and report exact count. Fix before any other work if broken/regressed.

## MATERIAL SHIPPED THIS SESSION (TRACED, committed on a5bac9b)
- **Cell 2 (FEE CONFIG SURFACE TESTS — DONE):** `tests/test_vault_fees_config_surface_20261112.py` (38 tests). Locks CLI flags `--aum-rate-annual`/`--profit-share-rate`/`--fee-hours-per-step` parse (default None) in both runners; `fee_config_from_args` absent→{} / partial→only-provided / explicit-zero-kept; `validate_fee_config` rejects negative/NaN/inf/non-numeric with `VaultFeeConfigError`; partial invalid set rejects whole; runner `main()` returns 2 before I/O on invalid knob; traced accrual value locks (0.02/0.10/1.0). Mutation-verified non-vacuous (removing negative guard → 8 fails).
- **Cell 3 (FEE × EQUITY-CURVE ELAPSED-HOURS — IMPLEMENTED + TESTED):** proved a real AUM under-charge defect: `run_portfolio_simulation` emits `equity_curve` as ONE point per trade exit (irregular multi-hour/day gaps); `_equity_series_for_fees` fed those to `accrue_vault_fees` with FLAT `hours_per_step=1.0`, so a 48h gap was charged 1h (traced **18.09x undercharge**). Fix (opt-in, default unchanged): new `elapsed_hours_from_timestamps()` in `src/metrics/vault_fees.py` (first step=default_hours, step i = Δhours between timestamps, fail-safe on missing/invalid/out-of-order, negative→0); `_attach_vault_fee_metrics` honors `fee_use_timestamp_hours=True`; CLI `--fee-hours-from-timestamps` (default off) in both runners. Tests: `tests/test_vault_fees_elapsed_hours_20261112.py` (9 tests).
- **Cell 3b (REAL-RUNNER KNOB DROPPED — FIXED):** `run_real_campaign.py` hardcoded `fee_hours_per_step=1.0` and **dropped `fee_kwargs`**, so `--aum-rate-annual`/`--profit-share-rate`/`--fee-hours-per-step` were validated but never applied in the real runner. Now passes `**fee_kwargs` + `fee_use_timestamp_hours`. Locked by `test_real_runner_applies_explicit_fee_knobs_to_metrics`.
- **Vault fee core (NEW, locked):** `src/metrics/vault_fees.py` pure 2%/yr AUM + 10% profit-above-HWM; opt-in reconciliation in `compute_campaign_metrics` with gross/net/fee components. Default metric outputs unchanged.

## PRIMARY PROVABLE GAP — NEXT CAMPAIGN
Cell 2 tests + Cell 3 elapsed-hours fix are shipped. Cell 3 equity-curve path is now correct for opt-in timestamp accrual. Next: Cell 4 — probe other provably uncovered spec-accounting gaps via file-search proof, or gated-pipeline/provenance fail-closed hardening with concrete expected values. Tests-first.

## NEXT FOCUS CAMPAIGN (FINITE, ORDERED, HEAVY — SHIP ≥1 MATERIAL ITEM/SESSION)
Repo name priority: **CRASH-REBOUND-STRATEGY** → crash→rebound fidelity to spec with auditable accounting. Execute top-down. For each cell: **prove gap** (cite search/consumer), **trace expected values**, write dated failing test, make it green.

1. **CELL 4 — OTHER PROVABLY UNCOVERED SPEC-ACCOUNTING GAPS:** probe via file-search proof (`grep` consumers/tests) for spec-accounting areas still lacking tests. Candidates to PROVE first (do not assume): (a) funding accrual on every leg/exit path incl. hedge legs at 48h boundary — is there a test asserting hedge-leg funding at the time-exit bar? (b) 8x spec safety stop interaction with rebound short on the SAME bar; (c) equal-share cap cuts across 120% gross cap when a NEW entry would top-up (must be cuts-only); (d) liquidation penalty sequencing vs funding on the same bar. Cite file evidence for each; only write tests for gaps proven absent. Otherwise ship gated-pipeline/provenance fail-closed hardening with concrete expected values.
2. **CELL 5 — ONLY IF 4 EXHAUSTED WITH EVIDENCE:** continue probing uncovered spec-accounting/guardrail gaps via file-search proof; otherwise hardening with traced values. Tests-first.

**No-idle rule:** passive re-verification or handoff-only edit without a material test/fix is NOT work. If a probed cell is already covered, cite file evidence and move to next.

## IMPLEMENTATION STATUS (EVIDENCE-BACKED)
- **Core/spec-compliant:** RSI(21)<20 crash trigger, $5M 24h volume enforcement, 1.25% 24h-volume sizing, ETH hedge vol-ratio (336h) capped 3x with no-look-ahead, rebound short after +9% target (stop +40%, target -9%, 48h), 8x spec safety stop, 120% gross-cap equal-share cuts, portfolio bar-by-bar deepest-first admission, hourly funding + liquidation at worst price.
- **Vault fees (NEW):** pure 2%/yr AUM accrual + 10% profit-above-HWM in `src/metrics/vault_fees.py`; opt-in reconciliation in `compute_campaign_metrics`; traced tests locked. Default outputs unchanged.
- **Fee config surface (DONE):** CLI flags + fail-closed `validate_fee_config`/`fee_config_from_args`/`VaultFeeConfigError`; traced tests `tests/test_vault_fees_config_surface_20261112.py`.
- **Fee × equity-curve elapsed hours (DONE, opt-in):** `elapsed_hours_from_timestamps` + `fee_use_timestamp_hours` + `--fee-hours-from-timestamps`; real runner now applies explicit knobs.
- **Runners/gating:** `scripts/run_portfolio.py`, `run_real_campaign.py` (fail-closed provenance/verified gates), engine fail-closed when `require_eth_hedge=True` and no usable hedge.

## MATERIAL LOCKED EVIDENCE (CARRY-FORWARD — DO NOT RE-LITIGATE)
- **2026-11-12 vault fees accounting/reconciliation** — `tests/test_vault_fees_20261112.py`, `tests/test_vault_fees_metrics_integration_20261112.py`, `src/metrics/vault_fees.py`.
- **2026-11-12 vault fee export wiring (cell 1)** — `scripts/run_campaign.py` (`--apply-vault-fees`/`--capital`), `scripts/run_real_campaign.py`, `tests/test_vault_fees_export_wiring_20261112.py`.
- **2026-11-12 vault fee config surface (cell 2 tests)** — `tests/test_vault_fees_config_surface_20261112.py` (38 tests).
- **2026-11-12 vault fee elapsed-hours (cell 3)** — `src/metrics/vault_fees.py::elapsed_hours_from_timestamps`, `src/metrics/campaign_metrics.py::_attach_vault_fee_metrics` (`fee_use_timestamp_hours`), `tests/test_vault_fees_elapsed_hours_20261112.py`.
- **2026-11-12 both-hedges family** (`cap_cut+commission_min+entry_next_bar`): FINAL EXIT/STOP/TARGET/TIME_EXIT/LIQUIDATION — `tests/test_both_hedges_*_20261112.py`.
- **2026-11-12 portfolio runner both-hedged rebound loop-else final exit** — `tests/test_portfolio_both_hedges_rebound_loop_exit_cap_cut_max_live_20261112.py`.
- **Stopped-buy-never-opens-rebound (portfolio E2E, real engine)** — `tests/test_portfolio_stopped_buy_real_engine_e2e.py`.
- **Locked semantics:** `max_live_coin_notional` may exceed entry-notional cap at pressure/rebound while reservations record entry-notional cap. Overall `exit_reason` may stay `target_rebound_short` while short-leg trade reason differs (assert per-leg). Loop-else final exit applies `short_pnl` only to risk_state; portfolio runner reconciles `total_pnl` into master risk_state.

## CRITICAL CONTEXT
- Spec truth: `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Test window 2025-12-20→2026-09-28 (283d), 6792 hourly bars/symbol.
- Core: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/{loader,provenance,streaming_ingest}.py`, `src/metrics/{campaign_metrics,vault_fees}.py`.
- Runners/guards: `scripts/run_portfolio.py`, `run_real_campaign.py`, `run_campaign.py`, `derive_verified_universe.py`, `fetch_hyperliquid_candles.py`, `generate_candle_coverage_gap_report.py`.

## RULES (NON-NEGOTIABLE — VIOLATION = SESSION FAILURE)
- Each session ships ≥1 material item with concrete evidence (dated test + gate count + traced values).
- Spec is truth: both legs, ETH hedge every leg, funding/liquidation on every leg/exit path, $5M gating, 1.25% sizing in spec paths, equal-share cuts old+new, stopped buy never opens rebound short.
- `backtest_simple` is low-level executor (signal assumed). Spec-compliant gating lives in `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners.
- Fail-closed: missing provenance/verification on real path → reject. Never fabricate data or results.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (2026-11-12T16:50:29Z, MANDATORY, HEAVY, NON-OPTIONAL)
```text
CRASH-REBOUND-STRATEGY | 2026-11-12T16:50:29Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

Repo identity/priority (DRIVES ALL WORK): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to crash-rebound-strategy.pdf / research_state/strategy_spec.md. Hourly bar-by-bar backtest engine only. NEVER claim 20s slicing, spread/L2/order-book impact. Mission: RSI(21)<20 crash trigger → rebound short (+9% target, +40% stop, -9% target, 48h) with ETH hedge every leg, equal-share cap cuts, no look-ahead, fail-closed gates.

NO EXPLICIT NEW DIRECTION → YOU OWN THE FINITE CAMPAIGN (MANDATORY): Continue NEXT FOCUS CAMPAIGN in HANDOFF.md (top-down). Shipped prior sessions (committed): cell-2 config-surface tests (tests/test_vault_fees_config_surface_20261112.py, 38) and cell-3 elapsed-hours fee reconciliation (src/metrics/vault_fees.py::elapsed_hours_from_timestamps, campaign_metrics.py fee_use_timestamp_hours, --fee-hours-from-timestamps in both runners, tests/test_vault_fees_elapsed_hours_20261112.py, 9; plus real-runner knob-drop fix). Full gate last verified 870 passed, 12 skipped in 43.28s (working tree clean on a79c94c). Execute CELL 4 now:

  CELL 4 — OTHER PROVABLY UNCOVERED SPEC-ACCOUNTING GAPS: For EACH candidate below, FIRST prove presence/absence via file search (cite grep -rn of tests/ and consumers/), then trace exact expected values, write a dated failing test, make green:
    (a) Hedge-leg FUNDING accrual at the time-exit bar (48h boundary) — COVERED, do not re-test: tests/test_rebound_short_48h_time_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_risk_settlement_20261110.py asserts funding delta on every leg with real DailyRiskState under cap-cut shares + ETH exit. Cite it and move on.
    (b) 8x spec safety stop interaction with rebound short on the SAME bar (sequencing: which wins) — test_engine_spec_safety_stop_hedge_ratio_locks_20261108.py exists but SAME-BAR stop-vs-rebound-short sequencing is UNPROVEN. grep engine.py stop/liquidation/target/time-exit ordering + rebound short path; if no same-bar test exists, add a dated failing test with traced values.
    (c) Equal-share cap cuts across 120% gross cap for a NEW entry that would TOP-UP (must be cuts-only, never top-up) — COVERED, do not re-test: tests/test_engine_cap_cut_no_top_up_cross_bar_20261110.py::test_engine_cap_cut_no_top_up_new_position (Z gets 10 shares / 1000 notional requested, no top-up). Cite it and move on.
    (d) Liquidation penalty vs funding on the same bar ordering — test_long_liquidation_precedes_stop_and_target_same_bar_cap_cut_commission_min_entry_next_bar_eth_hedge_20261111.py covers liq vs stop/target same bar; liq vs FUNDING same-bar ordering is UNPROVEN. If absent, add a dated failing test with traced values.
  If a candidate is already covered, cite the file evidence and move on; do NOT re-litigate anchored behavior. If all are covered, ship gated-pipeline/provenance fail-closed hardening with concrete expected values (tests-first).

Do NOT stop after one cell. Do NOT end with passive re-verification or handoff-only edit. Each session ships ≥1 material item with dated test + gate count + traced values.

BOTTLENECKS (audit 2026-11-12T16:50:29Z): CLEARED. Single durable handoff = root HANDOFF.md only. No *.lock outside .git/. No contradictory handoff files. `.test_derive_vol_*` residue is 0. No commit requested. All gaps are explicit campaign cells with proof-of-absence requirements. Nothing is idle-blocked; the only hard blocker is real data, which is NOT a bottleneck to fix.

DATA BLOCKER — CONFIRMED REAL, DO NOT TRY TO UNBLOCK: tracked 6792-bar BTC/ETH under research_state/cache/hyperliquid_verified_283d_btceth/ are PLACEHOLDER (provenance per-symbol status=error, synthetic_check.is_synthetic=true, flat_series_all_bars_identical, 1 distinct/6792, ready_for_real_campaign=false). NOT a false bottleneck. 283d campaign stays NOT RUN. Blocks ONLY real-data runs. All spec-unit and engine tests run on fixtures and remain fully executable.

BLOCKING GATE (RUN FIRST): `PYTHONPATH=. python3 -m pytest -q --tb=short`
  - Last verified (2026-11-12T16:50:29Z, working tree clean on a79c94c): 870 passed, 12 skipped in 43.28s.
  - Re-run NOW at current HEAD/worktree; report exact count. If broken/regressed, fix before ANYTHING else.

GAP PROOF (MANDATORY): before each change, prove the specific uncovered integration/guardrail (grep/read consumer paths) and cite evidence. Do not "improve" anchored behavior without a concrete failing defect.

LOCKED SEMANTICS (assert per traced engine behavior — zero regression):
  - max_live_coin_notional may exceed entry-notional cap at pressure/rebound while reservations record entry-notional cap — do NOT 'fix' without a concrete failing defect preserving anchors.
  - Overall exit_reason may remain target_rebound_short while short-leg trade reason differs — assert per-leg trade reasons.
  - Sequencing: liquidation > stop > target > time-exit. hours_held_short = sidx - short_start_idx + 1; time-exit at >= short_bars_max (default 48).
  - Hedge exit fallback when aligned ETH bar unavailable: engine uses hedge entry and re-applies exit slippage/commission. Hedge sizing from eth_candles[:idx+1], vol-ratio cap 3x, no look-ahead.
  - Loop-else final exit: engine applies short_pnl only to risk_state; portfolio runner reconciles total_pnl (all legs) into master risk_state.
  - Vault fees (locked): AUM = equity * rate * hours/8760 per step; profit share = 10% * max(0, equity_after_aum - HWM), HWM on post-fee net peaks; opt-in metrics reconciliation must not alter default trade aggregates. Fee hours: flat fee_hours_per_step (default 1.0) unless fee_use_timestamp_hours=True (elapsed hours between equity-curve timestamps).

COVERED — DO NOT RE-LITIGATE WITHOUT CONCRETE FAILING EVIDENCE: cell 1 fee export wiring; vault fee core + opt-in metrics reconciliation; cell 2 fee config surface (38 tests); cell 3 fee elapsed-hours reconciliation + real-runner knob-drop fix; both-hedges FINAL EXIT/STOP/TARGET/TIME_EXIT/LIQUIDATION under cap_cut+commission_min+entry_next_bar; portfolio both-hedged rebound loop-else final exit; stopped-buy-never-opens-rebound E2E; (a) time-exit hedge funding; (c) no-top-up cap cuts; .test_derive_vol_* fixture cleanup.

EXECUTION (NON-NEGOTIABLE):
  1) GAP PROOF: cite concrete absence/need.
  2) TRACE FIRST (red): deterministic hand-traced fixtures with exact expected values.
  3) SHIP: dated failing-tests-first tests (red→green). Preserve all anchors.
  4) VERIFY: targeted + full gate `PYTHONPATH=. python3 -m pytest -q --tb=short` (exact count).
  5) CONTINUE down campaign until exhausted with evidence.

NO-IDLE / CONTINUATION: passive re-verification or handoff-only edit without material test/fix is NOT work. Each session ships ≥1 material item.

FINAL STEPS (MANDATORY):
  - Report exact commands/results and files changed.
  - Update ONLY root HANDOFF.md: new UTC timestamp, bottleneck audit, shipped material item(s)+concrete traced evidence, full-gate count, remaining risks, and a new timestamped heavy initial task for the next session.

SPEC NON-NEGOTIABLES: hourly funding on every leg/exit; hourly liquidation at worst price, correct sequencing/notional/timing/penalty; stopped buy never opens rebound short; 8x safety stop; rebound -9%/48h/+40% anchored to executed short entry; ETH hedge every leg (336h vol ratio cap 3x), hedge sizing eth_candles[:idx+1], entry aligned; RSI(21)<20 next open deepest-first; $5M 24h volume in all spec gating; 1.25% 24h-volume sizing in spec path; equal-share cuts old+new across 120% gross cap (cuts only, never top-up); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification and on missing/insufficient required ETH hedge.
```

---

**END OF HANDOFF — THIS IS THE ONLY DURABLE CONTEXT. NEXT SESSION MUST EXECUTE THE INITIAL TASK ABOVE OR FAIL. (2026-11-12T16:50:29Z)**