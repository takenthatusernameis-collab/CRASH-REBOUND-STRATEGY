# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-12T10:03:20Z
**HEAD at audit:** `98e634b chore(kilo): checkpoint agent session` (working tree clean at audit; `git status --short` empty). **Single canonical durable handoff: ONLY this root `HANDOFF.md`.** Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT variants). `scripts/controller_progress.py`, dated/session-named tests, `__pycache__`, `.pytest_cache`, and root `_probe_*`/`_trace_*`/`_debug_*`/`leak_check.py`/`trace_leak.py` are implementation/tests/scratch, not handoffs.

## SESSION AUDIT (2026-11-12T10:03:20Z) — BOTTLENECKS CLEARED, GATE GREEN, PRIMARY GAP CONFIRMED
- **Durable handoff audit (verified):** only root `HANDOFF.md` is durable (`README.md` references it, not a handoff). No TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoff files found.
- **Lock/blocker audit (verified):** working tree clean at audit start; `git status --short` empty. No stale `*.lock` files outside `.git/`. No contradictory handoff artifacts, no process/session bottlenecks. **Bottlenecks CLEARED — nothing idle-ready.**
- **Data blocker (fail-closed, unchanged):** real 283d Hyperliquid BTC/ETH candles unavailable/unverified (`research_state/campaign_results.json` fixture/smoke-only per `research_state/campaign_artifact_provenance_erratum.md`; `research_state/universe_verified.json` excludes BTC/ETH as synthetic/manifest_error). **NEVER fabricate.** This blocks only real-data campaign runs, not engine/spec reconciliation work.
- **Scratch/state noise (non-blocking):** 105 `research_state/.test_derive_vol_*` temp dirs present (test residue) — ignore; do not treat as data/campaign artifacts and do not let them distract from material work.
- **Gap proof (2026-11-12T10:03:20Z, filesystem verified):** both-hedges terminal cells COVERED — final-exit (`tests/test_both_hedges_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_20261112.py`), STOP (`tests/test_both_hedges_rebound_short_stop_eth_hedge_cap_cut_commission_min_entry_next_bar_20261112.py`), TARGET (`tests/test_both_hedges_rebound_short_target_eth_hedge_cap_cut_commission_min_entry_next_bar_20261112.py`), TIME_EXIT (`tests/test_both_hedges_rebound_short_time_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_20261112.py`). **`find tests -name '*both*hedge*liquidation*'` → none → PRIMARY uncovered cell: BOTH-hedges + rebound-short LIQUIDATION under `cap_cut + commission_min + entry_next_bar`.**
- **Historical/stale (verify against code+tests, not authoritative):** `research_state/gap_analysis.md` (2026-10-30) and `research_state/campaign_artifact_provenance_erratum.md`. Scratch: root `_probe_*`/`_trace_*`/`_debug_*`/`leak_check.py`/`trace_leak.py`, `__pycache__`, `.pytest_cache`. Do not ship scratch.

## LAST VERIFIED GATE (REFRESHED AT CURRENT HEAD `98e634b`)
- `PYTHONPATH=. python3 -m pytest -q --tb=short` → **789 passed, 12 skipped in 54.30s** (2026-11-12T10:03:20Z, HEAD `98e634b`, working tree clean). **MANDATORY FIRST ACTION next session: re-run at current HEAD and report exact count. Do not trust this count if tree/HEAD changes. Fix before any other work if broken.**

## MATERIAL SHIPPED THIS SESSION (2026-11-12T08:55:11Z)
- **No engine/tests shipped.** Durable-handoff refresh only: re-audited single root `HANDOFF.md` (no alternates), clean tree at HEAD `98e634b`, no stale locks outside `.git/`, data/provenance blocker still fail-closed, primary uncovered cell re-confirmed (`find tests -name '*both*hedge*liquidation*'` → none). Gate refreshed at current HEAD: **789 passed, 12 skipped in 54.30s** (green). Rewrote mandatory initial task into a heavier, explicit execution contract (gate-first, gap-proof, trace-first red→green, concrete assertions, final reporting/handoff update). Gate count now fresh at HEAD `98e634b`.

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

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (2026-11-12T10:03:20Z, MANDATORY, HEAVY, NON-OPTIONAL)
```text
CRASH-REBOUND-STRATEGY | 2026-11-12T10:03:20Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

Repo identity/priority (MUST DRIVE ALL WORK): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly bar-by-bar backtest engine only. NEVER claim 20s slicing, spread/L2/order-book impact.

BOTTLENECKS (audit 2026-11-12T10:03:20Z, HEAD `98e634b`, clean tree): CLEARED. Single durable handoff is root `HANDOFF.md` only. No stale `*.lock` outside `.git/`. No contradictory handoff files. `research_state/gap_analysis.md` and `research_state/campaign_artifact_provenance_erratum.md` are historical — verify against code+tests. Real 283d Hyperliquid BTC/ETH data UNAVAILABLE/UNVERIFIED (fail-closed) — NEVER fabricate (blocks real-data runs only, not engine/spec reconciliation). 105 `research_state/.test_derive_vol_*` temp dirs are test residue/noise — ignore. If any blocker appears, REMOVE/FIX it FIRST with failing-tests-first evidence.

GAP PROOF (2026-11-12T10:03:20Z): `find tests -name '*both*hedge*liquidation*'` → none. PRIMARY uncovered cell confirmed.

COVERED (DO NOT RE-LITIGATE WITHOUT CONCRETE FAILING EVIDENCE): #1–#4 complete; both-hedges final-exit/STOP/TARGET/TIME_EXIT under `cap_cut + commission_min + entry_next_bar`; 48th-bar liq/stop/target and boundaries locked.

BLOCKING GATE (MUST RUN FIRST): `PYTHONPATH=. python3 -m pytest -q --tb=short`.
  - Last verified (fresh at HEAD `98e634b`, 2026-11-12T10:03:20Z): **789 passed, 12 skipped in 54.30s**.
  - Re-run NOW at current HEAD; report exact count. If broken/regressed, fix before ANYTHING else.

LOCKED SEMANTICS (ZERO REGRESSION / ASSERT PER TRACED ENGINE BEHAVIOR):
  - `max_live_coin_notional` may exceed entry-notional cap at pressure/rebound points while reservations record entry-notional cap — do NOT "fix" without concrete failing defect preserving anchors.
  - Overall `exit_reason` may remain `target_rebound_short` while short-leg trade reason is `time_exit`/`liquidated` in traces — assert per-leg trade reasons and traced result fields.
  - Sequencing: liquidation > stop > target > time-exit. `hours_held_short = sidx - short_start_idx + 1`; time-exit fires when `>= short_bars_max` (default 48).
  - Hedge exit fallback when aligned ETH bar unavailable: engine uses hedge entry and re-applies exit slippage/commission. Hedge sizing from `eth_candles[:idx+1]`, vol-ratio cap 3x, no look-ahead.

PRIMARY TARGET (MANDATORY, START HERE, FAILING-TESTS-FIRST):
Ship ≥1 MATERIAL cross-leg reconciliation/settlement guardrail lock (or proven defect fix) for UNCOVERED: BOTH long-leg ETH hedge AND rebound-short ETH hedge established simultaneously under `cap_cut + commission_min + entry_next_bar`, with rebound short exiting via **LIQUIDATION** (worst hourly price, +40% stop not hit first).
  - Variants to cover as feasible in this/next cells: aligned ETH exits; missing/absent ETH bar at exit for either/both hedges. Hourly bar-by-bar only.

EXECUTION (NON-OPTIONAL):
  1) GAP PROOF: search `tests/` for `*both*hedge*liquidation*` and target path; cite evidence. If already covered, move to next uncovered cross-leg `stop`/`target`/`time_exit`/`liquidation`/`final_exit` × (`cap_cut`/`commission_min`/`entry_next_bar`/missing-or-absent-ETH-exit) cell and repeat until you ship material work.
  2) TRACE FIRST (red phase): build deterministic hand-traced fixture from engine/spec math — coin long leg + long-leg ETH hedge (`eth_candles[:start_idx+1]` vol-ratio cap 3x) + rebound short after +9% target + rebound-short ETH hedge (`eth_candles[:rebound_idx+1]`). Compute expected funding, liquidation exit/fallback fills, per-leg PnL, `total_pnl`, `max_live_coin_notional`, `DailyRiskState` settlement/release/close parity, and strict no-look-ahead. On rebound-short liquidation engine sets `short_pnl` (includes liq penalty + funding), closes rebound hedge (settles funding), applies `risk_state.apply_trade(short_pnl + rebound_hedge_pnl, closed=True, notional=short_entry_px*shares)`, appends trade reason `liquidated`; result `exit_reason`/`exit_timestamp` may reflect long-leg target context — assert per traced engine semantics.
  3) SHIP: add dated failing-tests-first regression test `tests/test_*202611*.py` (red→green). Lock per-leg PnL/funding reconciliation, `total_pnl`, `max_live_coin_notional`, `DailyRiskState` settlement/release/close parity, funding on/off deltas, liquidation notional/timing/penalty correctness. Fix engine ONLY if concrete defect proven by trace/spec; preserve all anchors.
  4) VERIFY: run targeted test(s) and full gate `PYTHONPATH=. python3 -m pytest -q --tb=short` (exact count). Keep all anchors green.

NO-IDLE / CONTINUATION: after first cell, continue shipping remaining uncovered cross-leg reconciliation/settlement cells (stop/target/time_exit/liquidation/final_exit × cap_cut/commission_min/entry_next_bar/missing-or-absent-ETH-exit, including both-hedges) until exhausted with evidence; if exhausted, ship another MATERIAL guardrail (gated-pipeline/provenance fail-closed or uncovered spec path). Passive re-verification or handoff-only edit without material test/fix is NOT work. Each session must ship ≥1 material item.

FINAL STEPS (MANDATORY):
  - Report exact commands/results and files changed.
  - Update ONLY root `HANDOFF.md`: new UTC timestamp, bottleneck audit, shipped material item(s)+concrete traced evidence, full-gate count, remaining risks, and a new timestamped heavy initial task for the next session.

SPEC NON-NEGOTIABLES: hourly funding on every leg/exit; hourly liquidation worst price, correct sequencing/notional/timing/penalty; stopped buy never opens rebound short; 8x safety stop; rebound `-9%/48h/+40%` anchored to executed short entry; ETH hedge every leg (336h vol ratio cap 3x), hedge sizing `eth_candles[:idx+1]`, entry aligned; RSI(21)<20 next open deepest-first in spec path; `$5M` 24h volume in all spec-compliant gating; 1.25% 24h-volume sizing in spec-compliant path; equal-share cuts old+new across 120% gross cap (cuts only, never top-up); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification and on missing/insufficient required ETH hedge in spec-compliant paths.
```

---

**END OF HANDOFF — THIS IS THE ONLY DURABLE CONTEXT. NEXT SESSION MUST EXECUTE THE INITIAL TASK ABOVE OR FAIL. (2026-11-12T10:03:20Z)**