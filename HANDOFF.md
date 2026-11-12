# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-12T08:02:18Z
**HEAD at audit:** `dd6785c chore(kilo): checkpoint agent session` (working tree modified: `HANDOFF.md` only, refreshed this session). Single canonical durable handoff: ONLY this root `HANDOFF.md`. Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoff variants). `scripts/controller_progress.py`, dated/session-named tests, `__pycache__`, and root `_probe_*`/`_trace_*`/`_debug_*`/`leak_check.py`/`trace_leak.py` are implementation/tests/scratch, not handoffs.

## SESSION AUDIT (2026-11-12T08:02:18Z) — BOTTLENECKS CLEARED, GATE RE-VERIFIED, NEXT CAMPAIGN REAFFIRMED
- **Durable handoff audit (verified):** only root `HANDOFF.md` is a durable handoff (`README.md` references it but is not a handoff). No TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoff files found.
- **Lock/blocker audit (verified):** no stale `*.lock` files outside `.git/`. No process/session bottlenecks found. No contradictory handoff artifacts.
- **Data blocker (fail-closed, unchanged):** real 283d Hyperliquid BTC/ETH candles unavailable/unverified (`research_state/campaign_results.json` is fixture/smoke-only per `research_state/campaign_artifact_provenance_erratum.md`). **NEVER fabricate.**
- **Gap proof (2026-11-12T08:02:18Z, filesystem verified):** both-hedges terminal cells COVERED — final-exit (`tests/test_both_hedges_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_20261112.py`), STOP (`tests/test_both_hedges_rebound_short_stop_eth_hedge_cap_cut_commission_min_entry_next_bar_20261112.py`), TARGET (`tests/test_both_hedges_rebound_short_target_eth_hedge_cap_cut_commission_min_entry_next_bar_20261112.py`), TIME_EXIT (`tests/test_both_hedges_rebound_short_time_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_20261112.py`). **No `tests/*both*hedge*liquidation*` exists → PRIMARY uncovered cell: BOTH-hedges + rebound-short LIQUIDATION under `cap_cut + commission_min + entry_next_bar`.**
- **Historical/stale (verify against code+tests):** `research_state/gap_analysis.md` (2026-10-30, trigger/sizing notes outdated vs shipped code/tests) and `research_state/campaign_artifact_provenance_erratum.md`. Scratch: root `_probe_*`/`_trace_*`/`_debug_*`/`leak_check.py`/`trace_leak.py`, `__pycache__`, `.pytest_cache`. Do not ship scratch.

## LAST VERIFIED GATE
- `PYTHONPATH=. python3 -m pytest -q --tb=short` → **789 passed, 12 skipped in 55.65s** (2026-11-12T08:02:18Z, HEAD `dd6785c`, `HANDOFF.md` dirty only). **MUST re-run first in next session**; do not treat this count as fresh if tree/HEAD changes.

## MATERIAL SHIPPED THIS SESSION (2026-11-12T08:02:18Z)
- **No engine/tests shipped.** Bottleneck/lock/handoff audit, full-gate re-verification (789 passed, 12 skipped), both-hedges liquidation gap re-proof (`find tests -name '*both*hedge*liquidation*'` → none), and root `HANDOFF.md` refreshed with a fresh timestamped, traced, heavy, non-optional next-session campaign focused on uncovered BOTH-hedges rebound-short LIQUIDATION. No stale locks or session blockers found/removed. No alternative handoff files created.

## MATERIAL SHIPPED / LOCKED EVIDENCE (CARRY-FORWARD)
- **2026-11-12 (both-hedges terminals, cap_cut+commission_min+entry_next_bar):** final-exit `tests/test_both_hedges_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_20261112.py`; STOP `tests/test_both_hedges_rebound_short_stop_eth_hedge_cap_cut_commission_min_entry_next_bar_20261112.py`; TARGET `tests/test_both_hedges_rebound_short_target_eth_hedge_cap_cut_commission_min_entry_next_bar_20261112.py`; TIME_EXIT `tests/test_both_hedges_rebound_short_time_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_20261112.py`.
- **2026-11-11:** 48th-bar liq/stop/target precedence & boundaries (`test_rebound_short_liquidation_48th_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py`, `test_rebound_short_stop_48th_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py`, `test_rebound_short_target_48th_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py`); stop-target missing-ETH exit bar and long time-exit missing-ETH exit bar locks; RSI-trigger batch/sequential cuts, heterogeneous commission_min, deterministic tie-break, no top-up, settlement reconciliation, no-look-ahead (#3). Rebound-short liquidation ETH bar entirely absent at exit index locked; 1.25% 24h-volume sizing bypass fixed/locked (#1/#2).
- **Anchors:** gated pipeline/provenance fail-closed suites, funding/liq/final-exit/missing-ETH fallback families, equal-share cuts old+new, stopped buy never opens rebound short.

## IMPLEMENTATION STATUS (EVIDENCE-BACKED)
- **Core/spec-compliant:** RSI(21)<20 crash trigger, $5M 24h volume enforcement, 1.25% 24h-volume sizing when enabled, ETH hedge sizing 336h vol-ratio capped 3x with no-look-ahead (`eth_candles[:idx+1]`), rebound short after +9% target (stop +40%, target -9%, 48h), 8x spec safety stop, 120% gross-cap equal-share cuts (cuts only), portfolio bar-by-bar no-look-ahead admission with deepest-first ordering.
- **Runners/gating:** `scripts/run_portfolio.py` per-bar gating/deepest-first/reservation/cap-cut. `run_real_campaign.py` fail-closed provenance/verified gates. Engine fail-closed when `require_eth_hedge=True` and no usable hedge.
- **Engine sequencing (`src/backtest/engine.py`):** liquidation > stop > target > time-exit; `hours_held_short = sidx - short_start_idx + 1`; time-exit fires when `>= short_bars_max` (default 48). Hedge exit fallback: if aligned ETH bar unavailable at exit index, engine uses `hedge_info['entry']` and re-applies exit slippage/commission to that adjusted fill. Overall result `exit_reason` may remain `target_rebound_short` when long leg targeted before short time-exit; short-leg closure reason is on `trades` (traced).
- **Known interpretation (not defect without proof):** `max_live_coin_notional` may exceed entry-notional cap at pressure/rebound points while reservations record entry-notional cap — do NOT "fix" without concrete failing defect preserving anchors.

## REMAINING RISKS / HEAVY FOCUS CAMPAIGN (MANDATORY — NO ESCAPE, NO IDLE)
- **BLOCKED (fail-closed):** real 283d Hyperliquid candles unavailable/unverified. Never fabricate.
- **NEXT CAMPAIGN CELLS (ship in priority order with evidence — EACH SESSION MUST SHIP ≥1 MATERIAL ITEM):**
  1. **PRIMARY — uncovered:** BOTH long-leg ETH hedge AND rebound-short ETH hedge established simultaneously under `cap_cut + commission_min + entry_next_bar`, rebound short exiting via **LIQUIDATION** (worst hourly price, +40% stop not hit first) × (aligned ETH exits; missing/absent ETH bar at exit for either/both hedges as feasible). No `tests/*both*hedge*liquidation*` exists. Lock per-leg PnL/funding reconciliation, `total_pnl`, `max_live_coin_notional`, `DailyRiskState` settlement/release parity, funding on/off deltas, liquidation notional/timing/penalty correctness.
  2. **If covered by proof,** move to next uncovered cross-leg `stop`/`target`/`time_exit`/`liquidation`/`final_exit` × (`cap_cut`/`commission_min`/`entry_next_bar`/missing-or-absent-ETH-exit) settlement cell with gap evidence.
  3. **If engine reconciliation cells exhausted with evidence,** ship MATERIAL gated-pipeline/provenance fail-closed hardening with concrete expected values.
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

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (2026-11-12T08:02:18Z, MANDATORY, HEAVY, NON-OPTIONAL)
```text
CRASH-REBOUND-STRATEGY | 2026-11-12T08:02:18Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

Repo identity/priority (MUST DRIVE ALL WORK): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly bar-by-bar backtest engine only. NEVER claim 20s slicing, spread/L2/order-book impact.

CAMPAIGN STATUS: #1–#4 COMPLETE. BOTH-hedges cells COVERED (verified 2026-11-12): final-exit, STOP, TARGET, TIME_EXIT under `cap_cut + commission_min + entry_next_bar` (see HANDOFF locked evidence). 48th-bar liq/stop/target and boundaries locked. Do NOT re-litigate covered cells without concrete failing evidence.

BOTTLENECKS (audit 2026-11-12T08:02:18Z, HEAD dd6785c): CLEARED. Only root `HANDOFF.md` durable. No stale `*.lock` outside `.git/`. No contradictory handoff files. `research_state/gap_analysis.md` and `research_state/campaign_artifact_provenance_erratum.md` historical — verify against code+tests. Real 283d Hyperliquid BTC/ETH data UNAVAILABLE/UNVERIFIED (fail-closed) — NEVER fabricate. If any blocker appears, REMOVE/FIX it FIRST with failing-tests-first evidence.

GAP PROOF (2026-11-12T08:02:18Z): `find tests -name '*both*hedge*liquidation*'` → none. Primary target UNCOVERED.

BLOCKING GATE (MUST RUN FIRST): `PYTHONPATH=. python3 -m pytest -q --tb=short`. Last verified 2026-11-12T08:02:18Z → 789 passed, 12 skipped in 55.65s (HEAD dd6785c, HANDOFF.md dirty only). Re-run NOW; if broken/regressed, fix before ANYTHING else. Report exact count.

LOCKED (ZERO REGRESSION): all existing anchors including 48th-bar liq/stop/target/boundaries, both-hedges final-exit/stop/target/time-exit, and all #1–#4 locks. `max_live_coin_notional` may exceed entry-notional cap at pressure/rebound points while reservations record entry-notional cap — do NOT "fix" without concrete failing defect preserving anchors. Engine `exit_reason` can be `target_rebound_short` while short-leg trade reason is `time_exit` (traced) — assert per traced semantics.

NEXT CAMPAIGN PRIMARY TARGET (MANDATORY, START HERE, FAILING-TESTS-FIRST):
Ship ≥1 MATERIAL cross-leg reconciliation/settlement guardrail lock (or proven defect fix) for UNCOVERED: BOTH long-leg and rebound-leg ETH hedges established simultaneously under `cap_cut + commission_min + entry_next_bar`, with rebound short exiting via **LIQUIDATION** (worst hourly price, +40% stop not hit first) × (aligned ETH exits and missing/absent ETH bar at exit for either/both hedges as feasible). Hourly bar-by-bar only.

Execution (NON-OPTIONAL):
  1) GAP PROOF: search `tests/` for `*both*hedge*liquidation*` and the target terminal path. Cite evidence. If covered, move to next uncovered cross-leg cell and repeat.
  2) TRACE FIRST (red phase): deterministic hand-traced fixture from engine math — coin long leg + long-leg ETH hedge (sized from `eth_candles[:start_idx+1]` vol-ratio cap 3x) + rebound short after +9% target + rebound-leg ETH hedge (sized from `eth_candles[:rebound_idx+1]`). Cover funding, exit/fallback, per-leg PnL, `total_pnl`, `max_live_coin_notional`, `DailyRiskState` parity, strict no-look-ahead. Sequencing: liquidation > stop > target > time-exit; `hours_held_short = sidx - short_start_idx + 1`. Hedge exit fallback when aligned ETH bar unavailable: engine uses hedge entry and re-applies exit slippage/commission. On rebound-short liquidation engine sets `short_pnl` (includes liq penalty + funding), closes rebound hedge (settles funding), does `risk_state.apply_trade(short_pnl + rebound_hedge_pnl, closed=True, notional=short_entry_px*shares)` and appends trade reason `liquidated`; `exit_reason`/`exit_timestamp` reflect long-leg target context in combined result — assert per traced engine semantics.
  3) SHIP: add dated failing-tests-first regression test `tests/test_*202611*.py` (red→green). Lock per-leg PnL/funding reconciliation, `total_pnl`, `max_live_coin_notional`, `DailyRiskState` settlement/release/close parity, funding on/off deltas, liquidation notional/timing/penalty correctness. Fix engine ONLY if concrete defect proven by trace/spec; preserve all anchors.
  4) VERIFY: run targeted test(s) and full gate `PYTHONPATH=. python3 -m pytest -q --tb=short` (exact count). Keep all anchors green.

AFTER first cell: continue shipping remaining uncovered cross-leg reconciliation/settlement cells (stop/target/time_exit/liquidation/final_exit × cap_cut/commission_min/entry_next_bar/missing-or-absent-ETH-exit, including both-hedges) until exhausted; if exhausted with evidence, ship another MATERIAL guardrail (gated-pipeline/provenance or uncovered spec path). NO IDLE, NO passive re-verification-only, NO handoff-only edit without material progress.

FINAL STEPS (MANDATORY):
  - Report exact commands/results and files changed.
  - Update ONLY root `HANDOFF.md`: new UTC timestamp, bottleneck audit, shipped material item(s)+concrete evidence, gate count, remaining risks, and a new timestamped heavy initial task for the next session.

SPEC NON-NEGOTIABLES: hourly funding on every leg/exit; hourly liquidation worst price correct sequencing/notional/timing/penalty; stopped buy never opens rebound short; 8x safety stop; rebound `-9%/48h/+40%` anchored to executed short entry; ETH hedge every leg (336h vol ratio cap 3x), hedge sizing `eth_candles[:idx+1]`, entry aligned; RSI(21)<20 next open deepest-first in spec path; `$5M` 24h volume in all spec-compliant gating; 1.25% 24h-volume sizing in spec-compliant path; equal-share cuts old+new across 120% gross cap (cuts only, never top-up); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification and on missing/insufficient required ETH hedge in spec-compliant paths.
```

---

**END OF HANDOFF — THIS IS THE ONLY DURABLE CONTEXT. NEXT SESSION MUST EXECUTE THE INITIAL TASK ABOVE OR FAIL. (2026-11-12T08:02:18Z)**
