# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-12T11:45:00Z
**HEAD at audit start:** `87eda38 chore(kilo): checkpoint agent session` (working tree clean; new material test added this session). **Single canonical durable handoff: ONLY this root `HANDOFF.md`.** Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT variants). `scripts/controller_progress.py`, dated/session-named tests, `__pycache__`, `.pytest_cache`, and root `_probe_*`/`_trace_*`/`_debug_*`/`leak_check.py`/`trace_leak.py` are implementation/tests/scratch, not handoffs.

## SESSION AUDIT (2026-11-12T11:45:00Z) — BOTTLENECKS CLEARED, GATE GREEN, MATERIAL SHIPPED
- **Durable handoff audit (verified):** only root `HANDOFF.md` is durable (`README.md` references it, not a handoff). No TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoff files found.
- **Lock/blocker audit (verified):** no stale `*.lock` files outside `.git/`. No contradictory handoff artifacts, no process/session bottlenecks. **Bottlenecks CLEARED — nothing idle-ready.** Working tree clean at HEAD `87eda38`.
- **Data blocker (fail-closed, unchanged):** real 283d Hyperliquid BTC/ETH candles unavailable/unverified (`research_state/campaign_results.json` fixture/smoke-only per `research_state/campaign_artifact_provenance_erratum.md`; `research_state/universe_verified.json` excludes BTC/ETH as synthetic/manifest_error). **NEVER fabricate.** This blocks only real-data campaign runs, not engine/spec reconciliation work.
- **Scratch/state noise (non-blocking):** `research_state/.test_derive_vol_*` temp dirs present (test residue) — ignore. Root scratch/probe scripts untracked/existing as before — do not treat as durable artifacts or ship as product code.

## LAST VERIFIED GATE (REFRESHED AT HEAD `87eda38` + WORKING TREE)
- `PYTHONPATH=. python3 -m pytest -q --tb=short` → **798 passed, 12 skipped in 42.42s** (2026-11-12T11:45:00Z; was 795 passed, 12 skipped at 2026-11-12T10:21:36Z, +3 new tests). **MANDATORY FIRST ACTION next session: re-run at current HEAD and report exact count. Do not trust this count if tree/HEAD changes. Fix before any other work if broken.**

## MATERIAL SHIPPED THIS SESSION (2026-11-12T11:45:00Z)
- **Runner/portfolio regression lock (material, no engine change required):** added `tests/test_portfolio_both_hedges_rebound_loop_exit_cap_cut_max_live_20261112.py` (3 tests, traced, deterministic) locking **portfolio/runner-level both-hedged rebound loop-else FINAL EXIT under same-bar batch cap-cut pressure**, the HANDOFF cell-(b) cross-leg reconciliation cell that was NOT covered by low-level `backtest_simple` both-hedges tests nor by portfolio rebound tests (which use rebound TARGET exits and assert only clean final-state zeroing).
  - **Cell:** capital=10000, 120% cap=12000; symbols A and B fire same decision bar (bar 20, entry bar 21 @100), size_shares=100 → desired 10000 each, total 20000 > cap → **batch equal-share cut to 6000 entry notional = 60 shares each (cuts only, no top-up)**; concurrent entry-notional gross = 12000 = cap, never exceeded. Both hit +9% target at bar 22 → rebound short opens @109 → **max_live_coin_notional = 6540 (rebound-inflated vs 6000 entry notional)**, the value the runner records as `executed_notional` for the reservation overlay. ETH hedge on every leg (coin/ETH mirror ×20 → hedge ratio exactly 1.0 → hedge value = position value). Rebound shorts hold to series end (bar 59) → **loop-else FINAL EXIT (short-leg reason time_exit, overall target_rebound_short)**; ETH spans final bar → both hedge exits aligned (no fallback).
  - **Concrete traced assertions (mirror real engine functions):** per-trade shares=60, entry_price=100, entry notional=6000=cap/2; exit_reason=`target_rebound_short`, bars_held=39, entry_timestamp=`t0021`, exit_timestamp=`t0059`, exit_price=108; long-leg ETH hedge `hedge_side=short`, `hedge_size=3.0`, aligned entry/exit (2000→2180); `res.pnl` = long-leg settlement only (538.8 + −538.8 = 0.0); `res.hedge_pnl` = long+rebound hedge (−538.8 + 498.348 = −40.452); `res.total_pnl` = 583.2 (all four legs: long coin 538.8 + long hedge −538.8 + short coin 84.852 + rebound hedge 498.348). Engine-level companion asserts `TradeResult.max_live_coin_notional == 6540` (rebound-inflated reservation basis), short-leg trade reason `time_exit`, both hedge exits aligned.
  - **Portfolio settlement/release parity:** `risk_state.realized_pnl == 2 × 583.2 = 1166.4` (sum of per-trade total_pnl); `res.total_pnl == 1166.4`; final `open_positions=0`, `gross_exposure=0`, `open_position_notionals=[]` (no occupancy/exposure/notional leak).
- **Targeted:** `PYTHONPATH=. python3 -m pytest -q --tb=short tests/test_portfolio_both_hedges_rebound_loop_exit_cap_cut_max_live_20261112.py` → **3 passed**. **Full:** `PYTHONPATH=. python3 -m pytest -q --tb=short` → **798 passed, 12 skipped in 42.42s**.

## MATERIAL SHIPPED / LOCKED EVIDENCE (CARRY-FORWARD)
- **2026-11-12 (both-hedges, cap_cut+commission_min+entry_next_bar):** final-exit aligned `tests/test_both_hedges_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_20261112.py`; **final-exit missing-ETH-at-final-bar rebound fallback `tests/test_both_hedges_final_exit_missing_eth_exit_bar_cap_cut_commission_min_entry_next_bar_20261112.py`**; STOP `tests/test_both_hedges_rebound_short_stop_eth_hedge_cap_cut_commission_min_entry_next_bar_20261112.py`; TARGET `tests/test_both_hedges_rebound_short_target_eth_hedge_cap_cut_commission_min_entry_next_bar_20261112.py`; TIME_EXIT `tests/test_both_hedges_rebound_short_time_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_20261112.py`; LIQUIDATION `tests/test_both_hedges_rebound_short_liquidation_eth_hedge_cap_cut_commission_min_entry_next_bar_20261112.py`.
- **2026-11-12T11:45:00Z (runner cell-b):** **portfolio runner both-hedged rebound loop-else final exit under batch cap-cut `tests/test_portfolio_both_hedges_rebound_loop_exit_cap_cut_max_live_20261112.py`** (3 tests) — traced per-leg PnL/funding, max_live_coin_notional reservation basis, risk_state settlement parity, equal-share entry-notional cut, final-state release.
- **2026-11-11:** 48th-bar liq/stop/target precedence & boundaries (`test_rebound_short_liquidation_48th_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py`, `test_rebound_short_stop_48th_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py`, `test_rebound_short_target_48th_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py`); stop-target missing-ETH exit bar and long time-exit missing-ETH exit bar locks; RSI-trigger batch/sequential cuts, heterogeneous commission_min, deterministic tie-break, no top-up, settlement reconciliation, no-look-ahead (#3). Rebound-short liquidation ETH bar entirely absent at exit index locked; 1.25% 24h-volume sizing bypass fixed/locked (#1/#2).
- **Anchors:** gated pipeline/provenance fail-closed suites, funding/liq/final-exit/missing-ETH fallback families, equal-share cuts old+new, stopped buy never opens rebound short.

## IMPLEMENTATION STATUS (EVIDENCE-BACKED)
- **Core/spec-compliant:** RSI(21)<20 crash trigger, $5M 24h volume enforcement, 1.25% 24h-volume sizing when enabled, ETH hedge sizing 336h vol-ratio capped 3x with no-look-ahead (`eth_candles[:idx+1]`), rebound short after +9% target (stop +40%, target -9%, 48h), 8x spec safety stop, 120% gross-cap equal-share cuts (cuts only), portfolio bar-by-bar no-look-ahead admission with deepest-first ordering.
- **Runners/gating:** `scripts/run_portfolio.py` per-bar gating/deepest-first/reservation/cap-cut. `run_real_campaign.py` fail-closed provenance/verified gates. Engine fail-closed when `require_eth_hedge=True` and no usable hedge.
- **Engine sequencing (`src/backtest/engine.py`):** liquidation > stop > target > time-exit; `hours_held_short = sidx - short_start_idx + 1`; time-exit fires when `>= short_bars_max` (default 48). Hedge exit fallback: if aligned ETH bar unavailable at exit index, engine uses `hedge_info['entry']` and re-applies exit slippage/commission to that adjusted fill. Overall result `exit_reason` may remain `target_rebound_short` when long leg targeted before short time-exit; short-leg closure reason is on `trades` (traced). Loop-else final exit applies `short_pnl` only to `risk_state.apply_trade` (rebound-leg ETH hedge PnL excluded from that risk-state call — locked engine behavior; portfolio runner reconciles `total_pnl` including rebound hedge into master risk_state).
- **Known interpretation (not defect without proof):** `max_live_coin_notional` may exceed entry-notional cap at pressure/rebound points while reservations record entry-notional cap — do NOT "fix" without concrete failing defect preserving anchors. (Now locked at portfolio runner level by the 2026-11-12T11:45:00Z cell: runner cuts at entry-notional level equal share; engine max_live reflects rebound-inflated short entry.)

## REMAINING RISKS / HEAVY FOCUS CAMPAIGN (MANDATORY — NO ESCAPE, NO IDLE)
- **BLOCKED (fail-closed):** real 283d Hyperliquid candles unavailable/unverified. Never fabricate.
- **NEXT CAMPAIGN CELLS (ship in priority order with evidence — EACH SESSION MUST SHIP ≥1 MATERIAL ITEM):**
  1. **PRIMARY — prove next uncovered cell:** search `tests/` and cite concrete gap evidence before building. Both-hedges engine terminal family and the portfolio runner both-hedged rebound loop-exit cell are now locked under `cap_cut+commission_min+entry_next_bar`. Probe next uncovered material cell: (a) any remaining asymmetric missing-ETH exit granularity in both-hedges contexts with provable distinct path (prove by engine path/fixture; do not duplicate), (b) portfolio/runner-level traced cross-bar reconciliation not yet pinned (e.g. stopped-buy-never-opens-rebound under cap pressure, asymmetric same-bar mix where one leg liquidates while sibling rebounds to loop-else final exit, or max_live reservation propagation into a third later-bar admission), or (c) other spec-critical cross-leg reconciliation cell (funding/liq/penalty/notional/commission_min/cap_cut/entry_next_bar) with missing coverage proven by file search. Do not re-ship already-covered cells.
  2. **If engine/portfolio reconciliation cells exhausted with evidence,** ship MATERIAL gated-pipeline/provenance fail-closed hardening with concrete expected values (runner/reservation/max_live/reporting/manifest/CLI/provenance edge cases) — still failing-tests-first with traced expectations.
- **No-idle rule:** if probed cell is already locked, document file/test evidence and probe next until you ship ≥1 MATERIAL guardrail (failing-tests-first regression lock with concrete traced values, or proven defect fix + proof). **Passive re-verification or handoff-only edit without a material test/fix is NOT work.**

## CRITICAL CONTEXT
- Spec truth: `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Test window 2025-12-20→2026-09-28 (283d), 6792 hourly bars/symbol.
- Core: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/{loader,provenance,streaming_ingest}.py`, `src/metrics/campaign_metrics.py`
- Runners/guards: `scripts/run_portfolio.py`, `scripts/run_real_campaign.py`, `scripts/run_campaign.py`, `scripts/derive_verified_universe.py`, `scripts/fetch_hyperliquid_candles.py`, `scripts/generate_candle_coverage_gap_report.py`

## RULES (NON-NEGOTIABLE — VIOLATION = SESSION FAILURE)
- Each session ships ≥1 material item with concrete evidence (dated test file + gate count + traced values).
- Spec is truth: both legs, ETH hedge every leg, funding/liquidation correct on every leg/exit path, $5M gating, 1.25% 24h-volume sizing in spec-compliant paths, equal-share cuts old+new, stopped buy never opens rebound short.
- `backtest_simple` is low-level executor (signal assumed). Spec-compliant gating in `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners.
- Fail-closed: missing provenance/verification for real path → reject. Never fabricate.
- Single handoff: only root `HANDOFF.md`.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (2026-11-12T11:45:00Z, MANDATORY, HEAVY, NON-OPTIONAL)
```text
CRASH-REBOUND-STRATEGY | 2026-11-12T11:45:00Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

Repo identity/priority (MUST DRIVE ALL WORK): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly bar-by-bar backtest engine only. NEVER claim 20s slicing, spread/L2/order-book impact.

BOTTLENECKS (audit 2026-11-12T11:45:00Z, HEAD `87eda38` + clean working tree): CLEARED. Single durable handoff is root `HANDOFF.md` only. No stale `*.lock` outside `.git/`. No contradictory handoff files. `research_state/gap_analysis.md` and `research_state/campaign_artifact_provenance_erratum.md` are historical — verify against code+tests. Real 283d Hyperliquid BTC/ETH data UNAVAILABLE/UNVERIFIED (fail-closed) — NEVER fabricate (blocks real-data runs only, not engine/spec reconciliation). `research_state/.test_derive_vol_*` temp dirs are test residue/noise — ignore. If any blocker appears, REMOVE/FIX it FIRST with failing-tests-first evidence.

COVERED (DO NOT RE-LITIGATE WITHOUT CONCRETE FAILING EVIDENCE): #1–#4 complete; both-hedges FINAL EXIT (aligned + missing-ETH-at-final-bar rebound fallback), STOP, TARGET, TIME_EXIT, LIQUIDATION under `cap_cut + commission_min + entry_next_bar` (including aligned/missing-rebound-ETH/missing-both-ETH variants); portfolio runner both-hedged rebound loop-else final exit under batch cap-cut with traced per-leg PnL/funding, max_live_coin_notional reservation basis (6540 rebound-inflated vs 6000 entry notional), equal-share entry-notional cut (6000 each = cap/2), risk_state settlement parity (1166.4), final-state release — `tests/test_portfolio_both_hedges_rebound_loop_exit_cap_cut_max_live_20261112.py`.

GAP PROOF (MANDATORY FIRST STEP): run `find tests -maxdepth 1 -name '*both_hedges*' -o -name '*cap_cut*commission_min*entry_next_bar*' | sort` and targeted searches; cite concrete file absence/presence and distinct engine/runner path evidence to identify the NEXT uncovered material cell. Do not assume; prove. Cells now locked are off-limits without failing evidence.

BLOCKING GATE (MUST RUN FIRST): `PYTHONPATH=. python3 -m pytest -q --tb=short`.
  - Last verified (2026-11-12T11:45:00Z): **798 passed, 12 skipped in 42.42s**.
  - Re-run NOW at current HEAD; report exact count. If broken/regressed, fix before ANYTHING else.

LOCKED SEMANTICS (ZERO REGRESSION / ASSERT PER TRACED ENGINE BEHAVIOR):
  - `max_live_coin_notional` may exceed entry-notional cap at pressure/rebound points while reservations record entry-notional cap — do NOT "fix" without concrete failing defect preserving anchors.
  - Overall `exit_reason` may remain `target_rebound_short` while short-leg trade reason is `time_exit`/`liquidated`/`stopped`/`target` in traces — assert per-leg trade reasons and traced result fields.
  - Sequencing: liquidation > stop > target > time-exit. `hours_held_short = sidx - short_start_idx + 1`; time-exit fires when `>= short_bars_max` (default 48).
  - Hedge exit fallback when aligned ETH bar unavailable: engine uses hedge entry and re-applies exit slippage/commission. Hedge sizing from `eth_candles[:idx+1]`, vol-ratio cap 3x, no look-ahead.
  - Loop-else final exit: engine applies `short_pnl` only to risk_state (rebound-hedge PnL excluded from that risk-state call); portfolio runner reconciles `total_pnl` (all legs) into master risk_state.

PRIMARY TARGET (MANDATORY, START HERE, FAILING-TESTS-FIRST):
Prove and ship ≥1 MATERIAL next uncovered cross-leg reconciliation/settlement guardrail lock (or proven defect fix). Priority: (a) portfolio/runner-level traced cell exercising BOTH hedges across rebound/cap_cut/reservation/settlement/max_live_coin_notional with concrete multi-leg expected values not yet pinned (e.g. stopped-buy-never-opens-rebound under cap pressure, asymmetric same-bar liquidation+rebound-to-loop-else, or max_live reservation propagation into a later-bar third admission), or (b) any proven-uncovered engine reconciliation cell (funding/liq/penalty/notional/commission_min/cap_cut/entry_next_bar/missing-or-aligned ETH exit) with distinct path evidence. If engine/portfolio reconciliation cells are exhausted with evidence, ship MATERIAL gated-pipeline/provenance fail-closed hardening with concrete expected values. Hourly bar-by-bar only.

EXECUTION (NON-OPTIONAL):
  1) GAP PROOF: search `tests/` and relevant code paths for the target cell; cite evidence. If already covered, move to next uncovered cell and repeat until you ship material work.
  2) TRACE FIRST (red phase): build deterministic hand-traced fixture from engine/spec math covering all involved legs/hedges, funding, exit/fallback fills, per-leg PnL, `total_pnl`, `max_live_coin_notional`, `DailyRiskState`/`RiskState` settlement/release/close parity, and strict no-look-ahead. Assert per traced engine semantics.
  3) SHIP: add dated failing-tests-first regression test `tests/test_*202611*.py` (red→green). Fix engine ONLY if concrete defect proven by trace/spec; preserve all anchors.
  4) VERIFY: run targeted test(s) and full gate `PYTHONPATH=. python3 -m pytest -q --tb=short` (exact count). Keep all anchors green.

NO-IDLE / CONTINUATION: after first cell, continue shipping remaining uncovered cells until exhausted with evidence; then ship other MATERIAL guardrails. Passive re-verification or handoff-only edit without material test/fix is NOT work. Each session must ship ≥1 material item.

FINAL STEPS (MANDATORY):
  - Report exact commands/results and files changed.
  - Update ONLY root `HANDOFF.md`: new UTC timestamp, bottleneck audit, shipped material item(s)+concrete traced evidence, full-gate count, remaining risks, and a new timestamped heavy initial task for the next session.

SPEC NON-NEGOTIABLES: hourly funding on every leg/exit; hourly liquidation worst price, correct sequencing/notional/timing/penalty; stopped buy never opens rebound short; 8x safety stop; rebound `-9%/48h/+40%` anchored to executed short entry; ETH hedge every leg (336h vol ratio cap 3x), hedge sizing `eth_candles[:idx+1]`, entry aligned; RSI(21)<20 next open deepest-first in spec path; `$5M` 24h volume in all spec-compliant gating; 1.25% 24h-volume sizing in spec-compliant path; equal-share cuts old+new across 120% gross cap (cuts only, never top-up); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification and on missing/insufficient required ETH hedge in spec-compliant paths.
```

---

**END OF HANDOFF — THIS IS THE ONLY DURABLE CONTEXT. NEXT SESSION MUST EXECUTE THE INITIAL TASK ABOVE OR FAIL. (2026-11-12T11:45:00Z)**
