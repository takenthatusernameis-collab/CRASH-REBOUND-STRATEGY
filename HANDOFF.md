# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-12T20:12:28Z
**HEAD at audit:** `0e825c1 chore(kilo): checkpoint agent session` (working tree modified: uncommitted CELL 7 fixes in `src/metrics/campaign_metrics.py` + `tests/test_campaign_metrics_equity_performance_20261112.py` — gate was RED at this HEAD, fixed this session; **no commit requested**).
**Single canonical durable handoff: ONLY this root `HANDOFF.md`.** Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT variants). `scripts/controller_progress.py`, dated/session-named tests, `__pycache__`, `.pytest_cache`, root `_probe_*`/`_trace_*`/`_debug_*`/`leak_check.py`/`trace_leak.py`, and `tmp_qfv3jj4/` are implementation/tests/scratch, NOT handoffs.

## SESSION AUDIT (2026-11-12T20:12:28Z) — GATE GREEN (885 passed, 12 skipped) AFTER FIXING CELL 7 REGRESSION
- **Durable handoff audit (verified):** only root `HANDOFF.md` is durable (`README.md` points here). No TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoff files outside `.git`.
- **Lock/blocker audit (verified):** no `*.lock` files outside `.git/`. No contradictory handoff artifacts. `.test_derive_vol_*` residue is 0. Bottlenecks CLEARED — nothing idle-blocked; no multi-session contention.
- **Bottleneck removed this session:** `research_state/gap_analysis.md` (2026-10-30) claimed ETH hedge / funding / liquidation / RSI trigger were MISSING. It is stale and contradicts the current implementation; it is now banner-marked **SUPERSEDED** at the top so future agents do not re-implement finished work. Authoritative spec = `research_state/strategy_spec.md`.
- **Stale remote branches (audit, NOT blockers):** `origin/fix/campaign-fixture-provenance-20261030` (6 commits) and `origin/fix/campaign-integrity-and-exposure-accounting-20261030` (11 commits) are ~1040 commits behind `main`, not mergeable/rebased cleanly, and are superseded by `main`. Do NOT merge/rebase them or treat their old diffs as current gaps; they are history, not pending work.
- **Real-data blocker — CONFIRMED REAL, DO NOT "UNBLOCK":** tracked `research_state/cache/hyperliquid_verified_283d_btceth/candles/{BTC,ETH}.json` are 6792-bar placeholders (`provenance.json`: per-symbol `status:"error"`, `synthetic_check.is_synthetic:true`, flat series, `ready_for_real_campaign:false`). Fabricating/promoting forbidden. **283d real-data campaign stays NOT RUN.** Blocks only real-data runs. All spec-unit and engine tests run on fixtures and remain fully executable.
- **Test-env note (verified):** system `python3` had NO pytest; installed `pytest numpy pandas requests` per `.github/workflows/strategy-tests.yml` (`python -m pip install --break-system-packages`). Gate command below is canonical.

## LAST VERIFIED GATE (2026-11-12T20:12:28Z, HEAD 0e825c1 + uncommitted CELL 7 fixes)
- `PYTHONPATH=. python3 -m pytest -q --tb=short` → **885 passed, 12 skipped in 34.96s** (baseline 883 → 885; +6 CELL 7 equity tests green after fixes).
- **GATE REGRESSION FIXED THIS SESSION:** CELL 7 equity-performance reporting was committed in intermediate checkpoints (fb89b2d→0e825c1) but left the gate RED: (1) `test_equity_sharpe_sortino_traced_from_explicit_curve` asserted sortino `1/30` vs traced `1/3` (test arithmetic bug; implementation matches the per-trade convention `mean/down_std` at `src/metrics/campaign_metrics.py:118-121`); (2) `_attach_equity_performance` annualization `(final_eq / start_f) ** (1.0 / years)` raised `OverflowError` on sub-day horizons (e.g. 1h span → exponent 8760) — guarded with `math.pow` + `OverflowError` skip so total return is still emitted but non-finite annualized values never are. Fixes are uncommitted in `src/metrics/campaign_metrics.py` and `tests/test_campaign_metrics_equity_performance_20261112.py`.
- **MANDATORY FIRST ACTION next session:** re-run full gate at current HEAD/worktree and report exact count. Fix before any other work if broken/regressed.

## SHIPPED THIS SESSION — CELL 6 (REPORTING FIDELITY, additive, mutation-verified)
- **File:** `src/metrics/campaign_metrics.py` (+27 lines) and `tests/test_campaign_metrics_annual_positive_months_20261112.py` (3 tests).
- **Gap proof (file-search verified):** `compute_metrics_from_trades` emitted `monthly_breakdown`/`weekly_breakdown` (currency PnL) but had NO per-year bucket and NO positive/negative/flat month counts. `research_state/strategy_spec.md` Performance cites **"Per year +115.2%"** and **"6 of 10 months gain"**, so machine-checkable per-year PnL and months-gain counts are required. `grep -rn "annual_breakdown\|positive_months\|negative_months" tests/ src/` returned nothing before this change.
- **Added (purely additive — existing aggregates untouched):** `annual_breakdown` (YYYY→PnL), `annual_trade_counts` (YYYY→count), `positive_months`, `negative_months`, `flat_months`, `total_months`. New `_year_key()` helper.
- **Traced values:** trades +100 (2025-12-31), −40 (2026-01-15), +10 (2026-01-20), +25 (2026-02-10), 0 (2026-03-05) → `annual_breakdown={"2025":100.0,"2026":-5.0}`, `annual_trade_counts={"2025":1,"2026":4}`, monthly `{2025-12:100, 2026-01:-30, 2026-02:25, 2026-03:0}`, `positive_months=2, negative_months=1, flat_months=1, total_months=4`. Invariants asserted: annual sums = total PnL (95.0); month counts partition; annual trade counts sum = trade count.
- **Mutation-verified non-vacuous:** setting `annual[_year_key(ts)] += 0.0` failed 2 of 3 tests (restored clean; `git diff` shows only the feature).

## CELL 7 STATUS (SHIPPED, MUTATION VERIFY PENDING — CLOSEOUT IS THE NEXT SESSION'S FIRST ITEM)
- CELL 7 — equity-based reporting continuation is implemented and green: `annual_return_pct` (per-year return % on starting equity), `equity_sharpe_ratio`/`equity_sortino_ratio` (population std, non-annualized, per-trade convention), `equity_max_drawdown_pct`, `equity_total_return_pct`, plus `equity_annualized_return_pct`/`equity_horizon_years`/`equity_annualized_calmar_ratio` only when an explicit curve horizon is derivable (never guessed; skipped if annualization overflows). All additive — anchored per-trade `sharpe_ratio`/`sortino_ratio`/`calmar_ratio` untouched; zero regressions (gate 885/12).
- Tests: `tests/test_campaign_metrics_equity_performance_20261112.py` (6 tests, all green after this session's fixes).
- **Still open:** mutation-verify the 6 CELL 7 tests are non-vacuous (per CELL 6 precedent: perturb each new field/assertion, confirm the dated test breaks, restore clean). Mark CELL 7 exhausted-with-evidence, then continue top-down to CELL 8.

## CELL 5 — EXHAUSTED WITH EVIDENCE (all 3 candidates already covered; DO NOT RE-LITIGATE)
- **(a) Hedge-leg funding on loop-else FINAL EXIT:** covered by `tests/test_rebound_short_funding_all_paths.py` (parametrized `final_exit` asserts coin+hedge funding delta), `tests/test_rebound_final_exit_hedge_funding_missing_eth.py`, `tests/test_hedge_funding_fallback_on_missing_eth_exit.py`.
- **(b) Rebound-short LIQUIDATION at the 48h boundary:** covered by `tests/test_rebound_short_liquidation_48th_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py` (exact 48th held bar: full 48h funding + liquidation penalty + cap_cut + missing-ETH fallback).
- **(c) Equal-share cap cuts with same-bar rebound-short admission + mid-flight long:** covered by `tests/test_portfolio_same_bar_rebound_short_admission_reservation_20261109.py` and `tests/test_portfolio_cap_cut_existing_preserved_when_rebound_probe_completes_20261109.py`.

## PRIOR SHIPPED (TRACED, committed on fb89b2d or earlier — DO NOT RE-LITIGATE)
- Cell 4d long-liq vs funding same-bar ordering `tests/test_long_liquidation_funding_same_bar_ordering_20261112.py` (3, mutation-verified).
- Cell 4b spec safety-stop × rebound-short same-bar sequencing `tests/test_engine_spec_safety_stop_same_bar_rebound_short_sequencing_20261112.py` (3).
- Cell 2 fee config surface `tests/test_vault_fees_config_surface_20261112.py` (38).
- Cell 3 fee elapsed-hours `src/metrics/vault_fees.py::elapsed_hours_from_timestamps` + `tests/test_vault_fees_elapsed_hours_20261112.py` (9).
- Vault fee core `src/metrics/vault_fees.py` + opt-in reconciliation; cell 1 fee export wiring; both-hedges FINAL EXIT/STOP/TARGET/TIME_EXIT/LIQUIDATION family; portfolio both-hedged rebound loop-else final exit; stopped-buy-never-opens-rebound E2E.

## NEXT FOCUS CAMPAIGN (FINITE, ORDERED, HEAVY — SHIP ≥1 MATERIAL ITEM/SESSION)
Repo name priority: **CRASH-REBOUND-STRATEGY** → crash→rebound fidelity to spec with auditable accounting. Execute top-down. For each cell: **prove gap** (cite `grep -rn` of tests/ and consumers), **trace expected values**, write dated failing test, make it green, mutation-verify non-vacuous, run full gate. If a candidate is already covered, cite the file and move on.

1. **CELL 7 — REPORTING FIDELITY CONTINUATION (equity-based; verified OPEN):** `compute_metrics_from_trades`/`compute_campaign_metrics` have NO equity-curve-based Sharpe/Sortino and NO annual return % (`grep -rn "equity_sharpe\|annual_return\|annualized\|return_pct" src/ tests/` → empty). Spec PDF reports Sharpe/Calmar on the equity path and "Per year +115.2%". Add **additive** fields (never change anchored per-trade `sharpe_ratio`/`sortino_ratio`/`calmar_ratio`):
   (a) `annual_return_pct` / per-year return % when a starting equity is known (`initial_capital`/`capital` kwarg or first `equity_curve` point) — trace e.g. 2025 PnL 100 on 1000 start = 10%.
   (b) `equity_sharpe_ratio` / `equity_sortino_ratio` computed from `equity_curve` per-period returns (annualization optional, document convention).
   (c) Optional annualized Calmar when horizon is derivable from the equity curve.
   Trace exact values, dated failing test, green, mutation-verify.
2. **CELL 8 — UNIVERSE/VOLUME GATING SPEC EDGES:** candidates (prove presence/absence first): (a) exactly $5,000,000 24h rolling volume is INCLUSIVE (`>=`); (b) missing/non-finite volume field is fail-closed EXCLUDED, never treated as pass; (c) one-position-per-coin: an open buy must not admit a second same-coin position (buy→rebound-short path) — cite existing `test_portfolio_bar_scan.py`/`test_engine_cap_cut_no_top_up_cross_bar_20261110.py` first. If already covered, cite and move on.
3. **CELL 9 — ONLY IF 7–8 EXHAUSTED WITH EVIDENCE:** gated-pipeline/provenance fail-closed hardening with concrete expected values (manifest summary contradiction `ready_for_real_campaign=true` + synthetic; verified-cache temp-path rejection) — many are covered by `test_provenance_summary_consistency_hardening_20261107.py` / `test_loader_verified_rejects_temp_*`; prove absence before adding.

**No-idle rule:** passive re-verification or handoff-only edit without a material test/fix is NOT work. If a probed cell is already covered, cite file evidence and move to next.

## IMPLEMENTATION STATUS (EVIDENCE-BACKED)
- **Core/spec-compliant:** RSI(21)<20 crash trigger, $5M 24h volume enforcement, 1.25% 24h-volume sizing, ETH hedge vol-ratio (336h) capped 3x with no-look-ahead, rebound short after +9% target (stop +40%, target -9%, 48h), 8x spec safety stop, 120% gross-cap equal-share cuts, portfolio bar-by-bar deepest-first admission, hourly funding + liquidation at worst price (long uses low, short uses high).
- **Reporting:** Sharpe/Sortino/Calmar/win-rate/profit-factor/monthly/weekly breakdown/per-leg attribution/exposure; **NEW** per-year + months-gain counts (CELL 6).
- **Vault fees:** pure 2%/yr AUM (capped to equity) + 10% profit-above-HWM in `src/metrics/vault_fees.py`; opt-in reconciliation in `compute_campaign_metrics`. Default outputs unchanged.
- **Runners/gating:** `scripts/run_portfolio.py`, `run_real_campaign.py` (fail-closed provenance/verified gates), engine fail-closed when `require_eth_hedge=True` and no usable hedge.

## MATERIAL LOCKED EVIDENCE (CARRY-FORWARD — DO NOT RE-LITIGATE)
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

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (2026-11-12T20:12:28Z, MANDATORY, HEAVY, NON-OPTIONAL)
```text
CRASH-REBOUND-STRATEGY | 2026-11-12T20:12:28Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

Repo identity/priority (DRIVES ALL WORK): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to crash-rebound-strategy.pdf / research_state/strategy_spec.md. Hourly bar-by-bar backtest engine only. NEVER claim 20s slicing, spread/L2/order-book impact. Mission: RSI(21)<20 crash trigger → rebound short (+9% target, +40% stop, -9% target, 48h) with ETH hedge every leg, equal-share cap cuts, no look-ahead, fail-closed gates.

GATE (RUN FIRST, NON-NEGOTIABLE): `PYTHONPATH=. python3 -m pytest -q --tb=short`
  - Last verified (2026-11-12T20:12:28Z, HEAD 0e825c1 + uncommitted CELL 7 fixes): **885 passed, 12 skipped in 34.96s**, GREEN after fixing a committed-but-broken CELL 7 (sortino trace `1/30→1/3`; annualization OverflowError on sub-day horizons).
  - Re-run NOW at current HEAD/worktree; report exact count. If broken/regressed, fix before ANYTHING else.
  - Test env: install deps first if missing — `python -m pip install --break-system-packages pytest numpy pandas requests` (per .github/workflows/strategy-tests.yml).

NO EXPLICIT NEW DIRECTION → YOU OWN THE FINITE CAMPAIGN (MANDATORY): Continue NEXT FOCUS CAMPAIGN in HANDOFF.md (top-down). Prior sessions exhausted CELL 5 (all 3 candidates covered) and shipped CELL 6 (annual/positive-month reporting, mutation-verified). CELL 7 (equity reporting continuation) is implemented and GREEN but NOT yet mutation-verified — close it first:

  CELL 7 CLOSEOUT (MANDATORY FIRST ITEM): mutation-verify `tests/test_campaign_metrics_equity_performance_20261112.py` (6 tests) non-vacuous — for each traced field/assertion, perturb the implementation (e.g. flip equity sortino to sample std, remove the annualization OverflowError guard, change annual_return_pct base) and confirm the dated failing test breaks; restore clean; `git diff` shows only the feature. Then cite evidence: CELL 7 exhausted-with-evidence.

  CELL 8 — UNIVERSE/VOLUME GATING SPEC EDGES (VERIFIED OPEN): prove presence/absence first (cite `grep -rn` of tests/ and consumers before writing anything):
    (a) exactly $5,000,000 24h rolling volume is INCLUSIVE (`>=`) — check `test_volume_gating_*_20261107.py`, `scripts/derive_verified_universe.py`, `scripts/fetch_hyperliquid_candles.py`.
    (b) missing/non-finite volume field is fail-closed EXCLUDED, never treated as pass — check loader/provenance consumers (`src/data/loader.py`, `src/data/provenance.py`); `test_loader_verified_*_20261109.py`, `test_real_campaign_volume_threshold_20261107.py`.
    (c) one-position-per-coin: an open buy must not admit a second same-coin position (buy→rebound-short path) — cite `test_portfolio_bar_scan.py`, `test_engine_cap_cut_no_top_up_cross_bar_20261110.py` first.
  For each candidate: prove gap (cite grep/read evidence), trace exact expected values on hand-built fixtures, write a dated failing test, make it green, mutation-verify non-vacuous, run full gate. If already covered, cite the covering file and move to the next candidate. Do NOT re-implement covered behavior.

  CELL 9 — ONLY IF 7–8 EXHAUSTED WITH EVIDENCE: gated-pipeline/provenance fail-closed hardening (manifest summary contradiction `ready_for_real_campaign=true` + synthetic; verified-cache temp-path rejection) — many are covered by `test_provenance_summary_consistency_hardening_20261107.py` / `test_loader_verified_rejects_temp_*`; prove absence before adding.

Do NOT stop after one cell. Do NOT end with passive re-verification or handoff-only edit. Each session ships ≥1 material item with dated test + gate count + traced values.

BOTTLENECKS (audit 2026-11-12T20:12:28Z): CLEARED. Single durable handoff = root HANDOFF.md only. No `*.lock` outside `.git/`. No contradictory handoff artifacts. `.test_derive_vol_*` residue is 0. Gate regression (committed CELL 7) FIXED this session — nothing idle-blocked; no multi-session contention. Stale `research_state/gap_analysis.md` marked SUPERSEDED. Stale remote branches origin/fix/campaign-* are ~1040 commits behind main and NOT blockers — do not merge/rebase. Nothing is idle-blocked; the only hard blocker is real data, which is NOT a bottleneck to fix.

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

COVERED — DO NOT RE-LITIGATE WITHOUT CONCRETE FAILING EVIDENCE: cell 1 fee export wiring; vault fee core + opt-in reconciliation; cell 2 fee config surface (38); cell 3 fee elapsed-hours; cell 4b spec safety-stop × rebound-short same-bar sequencing (3); cell 4d liquidation-vs-funding same-bar ordering (3); CELL 5 (a)(b)(c) all covered (files in HANDOFF); CELL 6 annual/positive-month reporting (3, mutation-verified); CELL 7 equity reporting continuation (6 tests green, mutation verify PENDING — closeout is mandatory first item); both-hedges FINAL EXIT/STOP/TARGET/TIME_EXIT/LIQUIDATION; portfolio both-hedged rebound loop-else final exit; stopped-buy-never-opens-rebound E2E; fee HWM dip/recover no-double-charge and AUM-capped-to-equity; one-position-per-coin (multiple portfolio tests); `.test_derive_vol_*` fixture cleanup.

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
```

---

**END OF HANDOFF — THIS IS THE ONLY DURABLE CONTEXT. NEXT SESSION MUST EXECUTE THE INITIAL TASK ABOVE OR FAIL. (2026-11-12T20:12:28Z)**