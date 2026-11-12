# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-12T20:32:56Z
**HEAD at audit:** `8f35bd0 chore(kilo): checkpoint agent session` (working tree clean at audit start; HANDOFF refreshed to record CELL 9 provenance fail-closed hardening shipped since d0e0b9e).
**Single canonical durable handoff: ONLY this root `HANDOFF.md`.** Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT variants). `scripts/controller_progress.py`, dated/session-named tests, `__pycache__`, `.pytest_cache`, root `_probe_*`/`_trace_*`/`_debug_*`/`leak_check.py`/`trace_leak.py`, and `tmp_qfv3jj4/`/`tmpxps3dfx2/` are implementation/tests/scratch, NOT handoffs.

## SESSION AUDIT (2026-11-12T20:32:56Z) — GATE GREEN (894 passed, 12 skipped) CELL 9 PROVENANCE HARDENING SHIPPED
- **Durable handoff audit (verified):** only root `HANDOFF.md` is durable (`README.md` points here). No TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoff files outside `.git`.
- **Lock/blocker audit (verified):** no `*.lock` files outside `.git/`. No contradictory handoff artifacts. `.test_derive_vol_*` residue is 0. Bottlenecks CLEARED — nothing idle-blocked; no multi-session contention.
- **HANDOFF staleness removed:** HEAD had advanced 2 commits past the last audit (d0e0b9e → 8f35bd0) without HANDOFF update. Gate re-verified at current HEAD: 894 passed (was 885; +9 from CELL 9 provenance test file). HANDOFF now current.
- **Bottleneck removed prior session:** `research_state/gap_analysis.md` (2026-10-30) claimed ETH hedge / funding / liquidation / RSI trigger were MISSING. It is stale and contradicts the current implementation; it is banner-marked **SUPERSEDED** so future agents do not re-implement finished work. Authoritative spec = `research_state/strategy_spec.md`.
- **Stale remote branches (audit, NOT blockers):** `origin/fix/campaign-fixture-provenance-20261030` (6 commits) and `origin/fix/campaign-integrity-and-exposure-accounting-20261030` (11 commits) are ~1040 commits behind `main`, not mergeable/rebased cleanly, and are superseded by `main`. Do NOT merge/rebase them or treat their old diffs as current gaps; they are history, not pending work.
- **Real-data blocker — CONFIRMED REAL, DO NOT "UNBLOCK":** tracked `research_state/cache/hyperliquid_verified_283d_btceth/candles/{BTC,ETH}.json` are 6792-bar placeholders (`provenance.json`: per-symbol `status:"error"`, `synthetic_check.is_synthetic:true`, flat series, `ready_for_real_campaign:false`). Fabricating/promoting forbidden. **283d real-data campaign stays NOT RUN.** Blocks only real-data runs. All spec-unit and engine tests run on fixtures and remain fully executable.
- **Test-env note (verified):** install deps if missing — `python -m pip install --break-system-packages pytest numpy pandas requests` (per `.github/workflows/strategy-tests.yml`).

## LAST VERIFIED GATE (2026-11-12T20:32:56Z, HEAD 8f35bd0)
- `PYTHONPATH=. python3 -m pytest -q --tb=short` → **894 passed, 12 skipped in 34.75s** (re-verified at current HEAD). No regression.
- **MANDATORY FIRST ACTION next session:** re-run full gate at current HEAD/worktree and report exact count. Fix before any other work if broken/regressed.

## SHIPPED THIS SESSION — CELL 9 PROVENANCE FAIL-CLOSED HARDENING (OBSERVED_MIN_24H_USD_VOLUME)
- **Scope:** `src/data/provenance.py::_validate_symbol_volume_evidence` fail-closed on `observed_min_24h_usd_volume` when `require_spec_volume_floor` is set. Previously a manifest claiming `volume_filter_ok=true` + spec-compliant requested/effective floors could pass without any concrete `observed_min_24h_usd_volume` evidence. Now: observed minimum 24h USD volume must be present, numeric, and >= floor; missing/None/"n/a"/""/bool → reject; below floor → reject; at/above floor → accept. Legacy behavior (no floor arg) preserved.
- **File:** `tests/test_provenance_volume_observed_min_required_20261112.py` (8 tests): rejects absent/None/"n/a"/""/True/False/below-floor observed_min when floor required; accepts numeric >= floor; preserves legacy absent-observed behavior when no floor required.
- **CELL 9 remaining surfaces (already implemented in provenance.py, covered by existing tests — cite and move on):** summary.ready_for_real_campaign=true + synthetic contradiction; summary.ready_for_real_campaign=true + not-all-complete contradiction; summary.all_complete=true contradiction; summary.synthetic_series_detected inconsistency; temp per-symbol path rejection; manifest request_params sub-spec intent rejection; complete_symbols optimistic contradiction. Covered by `tests/test_provenance_summary_consistency_hardening_20261107.py`, `tests/test_loader_verified_rejects_temp_*`, `tests/test_real_campaign_*`.
- **CELL 9 status:** CORE HARDENING SHIPPED (observed_min fail-closed). Remaining surfaces verified covered by existing tests. CELL 9 effectively exhausted — continue to CELL 10.

## CELL 8 STATUS (EXHAUSTED WITH EVIDENCE — DO NOT RE-LITIGATE)
- All three candidates proven covered by implementation + existing tests:
  - **(a) exactly $5,000,000 24h rolling volume is INCLUSIVE (`>=`):** `passes_universe_filter` at `src/strategy/crash_rebound.py:324` uses `daily_vol_usd < min_daily_volume_usd` (so `>=` passes); `enforce_spec_volume_floor` at `src/strategy/config.py:16-29` returns `v if v >= SPEC_MIN_DAILY_VOLUME_USD else SPEC_MIN_DAILY_VOLUME_USD`. Covered by `tests/test_volume_gating_boundary_audit_20261107.py`, `tests/test_volume_gating_integrity_20261107.py`, `tests/test_volume_gating_remaining_surfaces_20261107.py`, `tests/test_derive_verified_universe_volume_floor_20261107.py`, `tests/test_fetch_hyperliquid_volume_floor_20261107.py`, `tests/test_real_campaign_volume_threshold_20261107.py`.
  - **(b) missing/non-finite volume field is fail-closed EXCLUDED, never treated as pass:** `passes_universe_filter` line 324 `if daily_vol_usd is None or daily_vol_usd < min_daily_volume_usd: return False`; `_daily_volume_usd` at `src/strategy/crash_rebound.py:141` returns `None` when no usable bars (skips invalid volume bars). Covered by `tests/test_loader_verified_*_20261109.py`, `tests/test_volume_gating_*_20261107.py`.
  - **(c) one-position-per-coin: an open buy must not admit a second same-coin position (buy→rebound-short path):** covered by `tests/test_portfolio_bar_scan.py:30` (`test_portfolio_one_position_per_coin_no_overlap`) and `tests/test_engine_cap_cut_no_top_up_cross_bar_20261110.py`.
- CELL 8 exhausted-with-evidence; continue top-down to CELL 9.

## CELL 5 — EXHAUSTED WITH EVIDENCE (all 3 candidates already covered; DO NOT RE-LITIGATE)
- **(a) Hedge-leg funding on loop-else FINAL EXIT:** covered by `tests/test_rebound_short_funding_all_paths.py` (parametrized `final_exit` asserts coin+hedge funding delta), `tests/test_rebound_final_exit_hedge_funding_missing_eth.py`, `tests/test_hedge_funding_fallback_on_missing_eth_exit.py`.
- **(b) Rebound-short LIQUIDATION at the 48h boundary:** covered by `tests/test_rebound_short_liquidation_48th_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py` (exact 48th held bar: full 48h funding + liquidation penalty + cap_cut + missing-ETH fallback).
- **(c) Equal-share cap cuts with same-bar rebound-short admission + mid-flight long:** covered by `tests/test_portfolio_same_bar_rebound_short_admission_reservation_20261109.py` and `tests/test_portfolio_cap_cut_existing_preserved_when_rebound_probe_completes_20261109.py`.

## PRIOR SHIPPED (TRACED, committed on fb89b2d or earlier — DO NOT RE-LITIGATE)
- CELL 6 annual/positive-month reporting `src/metrics/campaign_metrics.py`, `tests/test_campaign_metrics_annual_positive_months_20261112.py` (3, mutation-verified).
- CELL 7 equity reporting continuation `src/metrics/campaign_metrics.py`, `tests/test_campaign_metrics_equity_performance_20261112.py` (6, mutation-verified 2026-11-12: annual_return_pct/alias, sortino downside-std, annualized -1).
- Cell 4d long-liq vs funding same-bar ordering `tests/test_long_liquidation_funding_same_bar_ordering_20261112.py` (3, mutation-verified).
- Cell 4b spec safety-stop × rebound-short same-bar sequencing `tests/test_engine_spec_safety_stop_same_bar_rebound_short_sequencing_20261112.py` (3).
- Cell 2 fee config surface `tests/test_vault_fees_config_surface_20261112.py` (38).
- Cell 3 fee elapsed-hours `src/metrics/vault_fees.py::elapsed_hours_from_timestamps` + `tests/test_vault_fees_elapsed_hours_20261112.py` (9).
- Vault fee core `src/metrics/vault_fees.py` + opt-in reconciliation; cell 1 fee export wiring; both-hedges FINAL EXIT/STOP/TARGET/TIME_EXIT/LIQUIDATION family; portfolio both-hedged rebound loop-else final exit; stopped-buy-never-opens-rebound E2E.

## NEXT FOCUS CAMPAIGN (FINITE, ORDERED, HEAVY — SHIP ≥1 MATERIAL ITEM/SESSION)
Repo name priority: **CRASH-REBOUND-STRATEGY** → crash→rebound fidelity to spec with auditable accounting. Execute top-down. For each cell: **prove gap** (cite `grep -rn` of tests/ and consumers), **trace expected values**, write dated failing test, make it green, mutation-verify non-vacuous, run full gate. If a candidate is already covered, cite the file and move on.

1. **CELL 9 — PROVENANCE FAIL-CLOSED HARDENING (OBSERVED_MIN SHIPPED, remaining surfaces covered — cite and move on).**
2. **CELL 10 — END-TO-END RUNNER GATING INTEGRATION (NEXT, MANDATORY):** prove concrete gap in real-campaign runner end-to-end fail-closed enforcement. Probe candidates with `grep -rn` across `scripts/run_real_campaign.py`, `scripts/derive_verified_universe.py`, `scripts/fetch_hyperliquid_candles.py`, `src/data/{loader,provenance,streaming_ingest}.py`: does `run_real_campaign.py` actually call `require_verified_provenance(..., require_spec_volume_floor=SPEC_MIN_DAILY_VOLUME_USD)` and reject on any provenance failure before executing? Does `derive_verified_universe.py` enforce the $5M floor and reject sub-spec universes? Does the engine fail-closed when `require_eth_hedge=True` and no usable hedge exists on any leg? Many provenance gate surfaces are implemented in `src/data/provenance.py` — **prove the runner/consumer integration gap before adding tests**. If exhausted, cite evidence and move to next materially real spec-fidelity cell.
3. **CELL 11 — ONLY IF 10 EXHAUSTED WITH EVIDENCE:** next proven reporting/gating spec edge with concrete traced values (no speculative refactors).

**No-idle rule:** passive re-verification or handoff-only edit without a material test/fix is NOT work. If a probed cell is already covered, cite file evidence and move to next.

## IMPLEMENTATION STATUS (EVIDENCE-BACKED)
- **Core/spec-compliant:** RSI(21)<20 crash trigger, $5M 24h volume enforcement, 1.25% 24h-volume sizing, ETH hedge vol-ratio (336h) capped 3x with no-look-ahead, rebound short after +9% target (stop +40%, target -9%, 48h), 8x spec safety stop, 120% gross-cap equal-share cuts, portfolio bar-by-bar deepest-first admission, hourly funding + liquidation at worst price (long uses low, short uses high).
- **Reporting:** Sharpe/Sortino/Calmar/win-rate/profit-factor/monthly/weekly breakdown/per-leg attribution/exposure; per-year + months-gain counts (CELL 6); equity `equity_*` Sharpe/Sortino/Calmar/annual-return (CELL 7, mutation-verified).
- **Provenance/gating:** fail-closed `observed_min_24h_usd_volume` evidence when spec floor required (CELL 9, just shipped); summary contradiction rejection; temp path rejection; synthetic_check missing rejection; request_params intent validation (all in `src/data/provenance.py`).
- **Vault fees:** pure 2%/yr AUM (capped to equity) + 10% profit-above-HWM in `src/metrics/vault_fees.py`; opt-in reconciliation in `compute_campaign_metrics`. Default outputs unchanged.
- **Runners/gating:** `scripts/run_portfolio.py`, `run_real_campaign.py` (fail-closed provenance/verified gates), engine fail-closed when `require_eth_hedge=True` and no usable hedge.

## MATERIAL LOCKED EVIDENCE (CARRY-FORWARD — DO NOT RE-LITIGATE)
- **2026-11-12 CELL 9 provenance observed_min fail-closed hardening** — `src/data/provenance.py::_validate_symbol_volume_evidence`, `tests/test_provenance_volume_observed_min_required_20261112.py` (8 tests): missing/None/"n/a"/""/True/False/below-floor observed_min rejected when floor required; numeric >= floor accepted; legacy preserved without floor.
- **2026-11-12 CELL 7 equity reporting mutation-verified** — `src/metrics/campaign_metrics.py`, `tests/test_campaign_metrics_equity_performance_20261112.py` (6): annual_return_pct/alias mutation broke 2 tests; sortino downside-std mutation broke 1; annualized-return `-1` omission broke 1 (121.0% vs 21.0%).
- **2026-11-12 CELL 6 annual/positive-month reporting** — `src/metrics/campaign_metrics.py`, `tests/test_campaign_metrics_annual_positive_months_20261112.py` (3, mutation-verified).
- **2026-11-12 liquidation funding same-bar ordering (cell 4d)** — `tests/test_long_liquidation_funding_same_bar_ordering_20261112.py` (3).
- **2026-11-12 spec safety stop × rebound-short same-bar sequencing (cell 4b)** — `tests/test_engine_spec_safety_stop_same_bar_rebound_short_sequencing_20261112.py` (3).
- **2026-11-12 vault fees accounting/reconciliation/config/elapsed-hours** — `tests/test_vault_fees_*_20261112.py`, `src/metrics/vault_fees.py`.
- **2026-11-12 both-hedges family** — `tests/test_both_hedges_*_20261112.py`.
- **2026-11-12 portfolio runner both-hedged rebound loop-else final exit** — `tests/test_portfolio_both_hedges_rebound_loop_exit_cap_cut_max_live_20261112.py`.
- **Stopped-buy-never-opens-rebound (portfolio E2E)** — `tests/test_portfolio_stopped_buy_real_engine_e2e.py`.
- **Locked semantics:** `max_live_coin_notional` may exceed entry-notional cap at pressure/rebound while reservations record entry-notional cap. Overall `exit_reason` may stay `target_rebound_short` while short-leg trade reason differs (assert per-leg). Loop-else final exit applies `short_pnl` only to risk_state; portfolio runner reconciles `total_pnl` into master risk_state.

## CRITICAL CONTEXT
- Spec truth: `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Test window 2025-12-20→2026-09-28 (283d), 6792 hourly bars/symbol. `research_state/gap_analysis.md` is SUPERSEDED (historical only).
- Core: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/{loader,provenance,streaming_ingest}.py`, `src/metrics/{campaign_metrics,vault_fees}.py`.
- Runners/guards: `scripts/run_portfolio.py`, `run_real_campaign.py`, `run_campaign.py`, `derive_verified_universe.py`, `fetch_hyperliquid_candles.py`, `generate_candle_coverage_gap_report.py`.

## RULES (NON-NEGOTIABLE — VIOLATION = SESSION FAILURE)
- Each session ships ≥1 material item with concrete evidence (dated test + gate count + traced values).
- Spec is truth: both legs, ETH hedge every leg, funding/liquidation on every leg/exit path, $5M gating, 1.25% sizing in spec paths, equal-share cuts old+new, stopped buy never opens rebound short.
- `backtest_simple` is low-level executor (signal assumed). Spec-compliant gating lives in `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners.
- Fail-closed: missing provenance/verification on real path → reject. Never fabricate data or results.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (2026-11-12T20:32:56Z, MANDATORY, HEAVY, NON-OPTIONAL)
```text
CRASH-REBOUND-STRATEGY | 2026-11-12T20:32:56Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

Repo identity/priority (DRIVES ALL WORK): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to crash-rebound-strategy.pdf / research_state/strategy_spec.md. Hourly bar-by-bar backtest engine only. NEVER claim 20s slicing, spread/L2/order-book impact. Mission: RSI(21)<20 crash trigger → rebound short (+9% target, +40% stop, -9% target, 48h) with ETH hedge every leg, equal-share cap cuts, no look-ahead, fail-closed gates.

GATE (RUN FIRST, NON-NEGOTIABLE): `PYTHONPATH=. python3 -m pytest -q --tb=short`
  - Last verified (2026-11-12T20:32:56Z, HEAD 8f35bd0): **894 passed, 12 skipped in ~35s**, GREEN.
  - Re-run NOW at current HEAD/worktree; report exact count. If broken/regressed, fix before ANYTHING else.
  - Test env: install deps first if missing — `python -m pip install --break-system-packages pytest numpy pandas requests` (per .github/workflows/strategy-tests.yml).

NO EXPLICIT NEW DIRECTION → YOU OWN THE FINITE CAMPAIGN (MANDATORY): Continue NEXT FOCUS CAMPAIGN in HANDOFF.md (top-down). CELL 5/6/7/8 are EXHAUSTED WITH EVIDENCE (do NOT re-litigate). CELL 9 provenance observed_min fail-closed hardening SHIPPED this session (8 tests in `tests/test_provenance_volume_observed_min_required_20261112.py`); remaining CELL 9 surfaces covered by existing tests — cite and move on.

  CELL 10 — END-TO-END RUNNER GATING INTEGRATION (NEXT, MANDATORY): prove concrete gap in real-campaign runner end-to-end fail-closed enforcement. Probe candidates with `grep -rn` across `scripts/run_real_campaign.py`, `scripts/derive_verified_universe.py`, `scripts/fetch_hyperliquid_candles.py`, `src/data/{loader,provenance,streaming_ingest}.py`: does `run_real_campaign.py` actually call `require_verified_provenance(..., require_spec_volume_floor=SPEC_MIN_DAILY_VOLUME_USD)` and reject on any provenance failure before executing? Does `derive_verified_universe.py` enforce the $5M floor and reject sub-spec universes? Does the engine fail-closed when `require_eth_hedge=True` and no usable hedge exists on any leg? Provenance gate surfaces are implemented in `src/data/provenance.py` — **prove the runner/consumer integration gap (`grep -rn` tests/ + consumers) before adding tests**. If exhausted, cite file evidence and move to next materially real spec-fidelity cell.
  CELL 11 — ONLY IF 10 EXHAUSTED WITH EVIDENCE: next proven reporting/gating spec edge with concrete traced values (no speculative refactors).

For each candidate: (1) GAP PROOF — cite concrete absence/need (`grep -rn` tests/ + consumer paths). (2) TRACE FIRST — deterministic hand-traced fixtures with exact expected fail-closed/values. (3) SHIP — dated failing-tests-first (red→green), preserve all anchors, mutation-verify non-vacuous. (4) VERIFY — targeted + full gate `PYTHONPATH=. python3 -m pytest -q --tb=short` (exact count). (5) CONTINUE down campaign until exhausted with evidence.

Do NOT stop after one cell. Do NOT end with passive re-verification or handoff-only edit. Each session ships ≥1 material item with dated test + gate count + traced values.

BOTTLENECKS (audit 2026-11-12T20:32:56Z): CLEARED. Single durable handoff = root HANDOFF.md only. No `*.lock` outside `.git/`. No contradictory handoff artifacts. `.test_derive_vol_*` residue is 0. Gate GREEN (894/12); nothing idle-blocked; no multi-session contention. HANDOFF staleness fixed (HEAD advanced past last audit without update — now current). Stale `research_state/gap_analysis.md` marked SUPERSEDED. Stale remote branches origin/fix/campaign-* are ~1040 commits behind main and NOT blockers — do not merge/rebase. Nothing is idle-blocked; the only hard blocker is real data, which is NOT a bottleneck to fix.

DATA BLOCKER — CONFIRMED REAL, DO NOT TRY TO UNBLOCK: tracked 6792-bar BTC/ETH under `research_state/cache/hyperliquid_verified_283d_btceth/` are PLACEHOLDER (provenance per-symbol `status:"error"`, `synthetic_check.is_synthetic:true`, flat series, `ready_for_real_campaign:false`). NOT a false bottleneck. 283d campaign stays NOT RUN. Blocks ONLY real-data runs. All spec-unit and engine tests run on fixtures and remain fully executable.

LOCKED SEMANTICS (assert per traced engine behavior — zero regression):
  - `max_live_coin_notional` may exceed entry-notional cap at pressure/rebound while reservations record entry-notional cap — do NOT 'fix' without a concrete failing defect preserving anchors.
  - Overall `exit_reason` may remain `target_rebound_short` while short-leg trade reason differs — assert per-leg trade reasons.
  - Sequencing: liquidation > stop > target > time-exit. `hours_held_short = sidx - short_start_idx + 1`; time-exit at >= `short_bars_max` (default 48).
  - Long-leg liq funding: `hours_held_liq = idx - start_idx + 1`, subtracted in the SAME branch as the penalty (cell 4d lock). Spec 8x safety stop sits below the 6% liq threshold → same-bar stop+target collision resolves to liquidation and never opens a rebound short (cell 4b lock).
  - Hedge exit fallback when aligned ETH bar unavailable: engine uses hedge entry and re-applies exit slippage/commission. Hedge sizing from `eth_candles[:idx+1]`, vol-ratio cap 3x, no look-ahead.
  - Loop-else final exit: engine applies `short_pnl` only to risk_state; portfolio runner reconciles `total_pnl` (all legs) into master risk_state.
  - Vault fees (locked): AUM = equity * rate * hours/8760 per step (capped to equity); profit share = 10% * max(0, equity_after_aum - HWM), HWM on post-fee net peaks; opt-in metrics reconciliation must not alter default trade aggregates.
  - Reporting (CELL 6+7 lock): `annual_breakdown`/`annual_trade_counts`/`positive_months`/`negative_months`/`flat_months`/`total_months` and equity `equity_*` fields are ADDITIVE; existing `win_rate`/`monthly`/`weekly`/exposure aggregates and anchored per-trade `sharpe_ratio`/`sortino_ratio`/`calmar_ratio` must be unchanged.
  - `backtest_simple` is low-level executor (signal assumed). Spec-compliant gating lives in `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners. Fail-closed: missing provenance/verification on real path → reject. Never fabricate data or results.

COVERED — DO NOT RE-LITIGATE WITHOUT CONCRETE FAILING EVIDENCE: cell 1 fee export wiring; vault fee core + opt-in reconciliation; cell 2 fee config surface (38); cell 3 fee elapsed-hours; cell 4b spec safety-stop × rebound-short same-bar sequencing (3); cell 4d liquidation-vs-funding same-bar ordering (3); CELL 5 (a)(b)(c) all covered (files in HANDOFF); CELL 6 annual/positive-month reporting (3, mutation-verified); CELL 7 equity reporting continuation (6 tests, mutation-verified 2026-11-12: annual_return_pct/alias, sortino downside-std, annualized -1); CELL 8 volume-gating spec edges (exhausted with evidence); CELL 9 provenance observed_min fail-closed hardening shipped (8 tests); remaining CELL 9 surfaces covered by existing tests; both-hedges FINAL EXIT/STOP/TARGET/TIME_EXIT/LIQUIDATION; portfolio both-hedged rebound loop-else final exit; stopped-buy-never-opens-rebound E2E; fee HWM dip/recover no-double-charge and AUM-capped-to-equity; one-position-per-coin (multiple portfolio tests); `.test_derive_vol_*` fixture cleanup.

EXECUTION (NON-NEGOTIABLE):
  1) GAP PROOF: cite concrete absence/need (grep/read consumer paths).
  2) TRACE FIRST (red): deterministic hand-traced fixtures with exact expected values.
  3) SHIP: dated failing-tests-first tests (red→green). Preserve all anchors. Mutation-verify non-vacuous.
  4) VERIFY: targeted + full gate `PYTHONPATH=. python3 -m pytest -q --tb=short` (exact count).
  5) CONTINUE down campaign until exhausted with evidence.

NO-IDLE / CONTINUATION: passive re-verification or handoff-only edit without material test/fix is NOT work. Each session ships ≥1 material item.

FINAL STEPS (MANDATORY):
  - Report exact commands/results and files changed.
  - Update ONLY root HANDOFF.md: new UTC timestamp, bottleneck audit, shipped material item(s)+concrete traced evidence, full-gate count, remaining risks, and a new timestamped heavy initial task for the next session.

SPEC NON-NEGOTIABLES: hourly funding on every leg/exit; hourly liquidation at worst price, correct sequencing/notional/timing/penalty; stopped buy never opens rebound short; 8x safety stop; rebound -9%/48h/+40% anchored to executed short entry; ETH hedge every leg (336h vol ratio cap 3x), hedge sizing `eth_candles[:idx+1]`, entry aligned; RSI(21)<20 next open deepest-first; $5M 24h volume in all spec gating; 1.25% 24h-volume sizing in spec path; equal-share cuts old+new across 120% gross cap (cuts only, never top-up); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification and on missing/insufficient required ETH hedge.

---

**END OF HANDOFF — THIS IS THE ONLY DURABLE CONTEXT. NEXT SESSION MUST EXECUTE THE INITIAL TASK ABOVE OR FAIL. (2026-11-12T20:32:56Z)**