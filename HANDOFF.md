# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-12T02:57:25Z
**HEAD:** `4542606 chore(kilo): checkpoint agent session` (working tree clean at audit)
Single canonical durable handoff: ONLY this root `HANDOFF.md`. Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoff variants). `scripts/controller_progress.py`, `tests/test_controller_progress_accounting.py`, timed/session-named tests, `__pycache__`, and `_probe_*`/`_trace_*`/`_debug_*` artifacts are implementation/tests/scratch, not handoffs.

## SESSION AUDIT (2026-11-12T02:57:25Z) — BOTTLENECKS AUDITED/CLEARED, HANDOFF REFRESHED, HEAVY CAMPAIGN CONTINUES
- **Durable handoff audit (verified):** only root `HANDOFF.md` is a durable handoff. No TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT/*handoff* durable docs found. `scripts/controller_progress.py`, dated/session tests, probes/traces/debugs, `__pycache__` are implementation/tests/scratch, not handoffs.
- **Lock/blocker audit (verified):** no stale `*.lock` files outside `.git/`. No process/session bottlenecks found; nothing to remove. Working tree clean (`git status --short` empty).
- **Scratch/non-blockers:** root `_probe_*`/`_trace_*`/`_debug_*`, `__pycache__`, `research_state/.test_derive_vol_*`. Do not re-ship scratch traces.
- **Historical docs (stale/verify against code+tests):** `research_state/gap_analysis.md` (2026-10-30, lists RSI/hedge/sizing/universe as missing but later tests/impl cover major parts) and `research_state/campaign_artifact_provenance_erratum.md`.
- **Environment:** `pytest 9.2.0` installed (per prior session audit). **Real 283d Hyperliquid BTC/ETH candles unavailable/unverified (fail-closed) — NEVER fabricate.**
- **Coverage evidence spot-check (2026-11-12T02:57:25Z):** both-leg primary target (final-exit loop-else, long-leg short ETH hedge + rebound-leg long ETH hedge established and funded simultaneously, cap_cut+commission_min+entry_next_bar) COVERED by `tests/test_both_hedges_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_20261112.py` (present in tree). Prior coverage: rebound-only aligned/missing-final-ETH final-exit, long-only final-exit, 48th-bar liq/stop/target, stop-at-48h cap_cut/missing-ETH, rebound-short funding/liq/final-exit/missing-ETH fallback families, gated pipeline/provenance fail-closed suites.

## LAST VERIFIED GATE (CARRY-FORWARD; RE-RUN FIRST IN NEXT SESSION)
- `PYTHONPATH=. python3 -m pytest -q --tb=short` → **778 passed, 12 skipped in 34.67s** (2026-11-12T02:55:xxZ, HEAD 4542606; clean tree at that time). **MUST re-run first in next session**; do not treat this count as fresh if tree/HEAD changes.

## MATERIAL SHIPPED / LOCKED EVIDENCE (CARRY-FORWARD)
- **2026-11-12T02:55:00Z (PRIMARY CELL SHIPPED):** `tests/test_both_hedges_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_20261112.py` — final-exit loop-else with BOTH long-leg short ETH hedge AND rebound-leg long ETH hedge established and funded simultaneously under cap_cut+commission_min+entry_next_bar; per-leg PnL/funding reconciliation, `total_pnl`, `max_live_coin_notional`, `DailyRiskState` release/settlement parity, funding on/off delta.
- **2026-11-11T23:53:36Z:** `tests/test_rebound_short_stop_48th_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py` — 48th held bar STOP precedence over 48h time-exit, cap_cut-implied 600 shares, commission_min, entry_next_bar, aligned/absent ETH at exit, per-leg fills/PnL/funding, hedge sizing/entry/exit/fallback, `total_pnl`, `max_live_coin_notional`, `risk_state` settlement/release, funding on/off deltas.
- **2026-11-11T23:44:38Z:** `tests/test_rebound_short_target_48th_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py` — 48th-bar TARGET precedence.
- **2026-11-11T23:44:56Z:** `tests/test_rebound_short_liquidation_48th_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py` — 48th-bar LIQUIDATION precedence.
- **2026-11-11T13:17:59Z (#4):** `tests/test_rebound_short_stop_target_missing_eth_exit_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py`
- **2026-11-11T12:17:54Z:** `tests/test_long_time_exit_missing_eth_exit_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py`
- **2026-11-11T09:16:00Z (#3 COMPLETE):** batch/sequential cuts, heterogeneous commission_min, deterministic tie-break, no top-up, settlement reconciliation, no-look-ahead.
- **2026-11-11T05:29:28Z (#2/#1):** rebound-short liquidation ETH bar entirely absent at exit index locked; 1.25% 24h-volume sizing bypass fixed/locked.
- **Anchors:** 48th-bar liq/stop/target boundaries, stop-at-48h cap_cut/missing-ETH, rebound-short funding/liq/final-exit/missing-ETH fallback families, gated pipeline/provenance fail-closed suites.

## IMPLEMENTATION STATUS (EVIDENCE-BACKED)
- Core/spec-compliant paths: RSI(21)<20 crash trigger, $5M 24h volume enforcement, 1.25% 24h-volume sizing when enabled, ETH hedge sizing 336h vol-ratio capped 3x with no-look-ahead (`eth_candles[:idx+1]`), rebound short after +9% target (stop +40%, target -9%, 48h), 8x spec safety stop, 120% gross-cap equal-share cuts (cuts only), portfolio bar-by-bar no-look-ahead admission with deepest-first ordering.
- Runners/gating: `scripts/run_portfolio.py` per-bar gating/deepest-first/reservation/cap-cut. `run_real_campaign.py` fail-closed provenance/verified gates. Engine fail-closed when `require_eth_hedge=True` and no usable hedge.
- Engine rebound-short sequencing (`src/backtest/engine.py`): liquidation > stop > target > time-exit; `hours_held_short = sidx - short_start_idx + 1`; time-exit fires when `>= short_bars_max` (default 48). Liquidation `~507`, stop `~543`, target `~576`, time-exit `~605`.
- Final-exit loop-else: if `final_coin_idx >= len(eth_candles)` → hedge exit raw falls back to `hedge_info['entry']` independently per hedge.
- Known interpretation (not defect without proof): `max_live_coin_notional` may exceed entry-notional cap at pressure/rebound points while reservations record entry-notional cap — do NOT "fix" without concrete failing defect preserving anchors.

## REMAINING RISKS / HEAVY FOCUS CAMPAIGN (MANDATORY — NO ESCAPE, NO IDLE, NO RE-VERIFICATION-ONLY)
- **BLOCKED (fail-closed):** real 283d Hyperliquid candles unavailable/unverified. Never fabricate.
- **NEXT CAMPAIGN CELLS ACTIVE (ship in priority order with evidence — EACH SESSION MUST SHIP ≥1 MATERIAL ITEM):**
  1. **PRIMARY — Next uncovered cross-leg terminal path with BOTH long-leg ETH hedge AND rebound-short ETH hedge established simultaneously** under `cap_cut + commission_min + entry_next_bar` (e.g. stop/target/time_exit/liquidation × aligned or missing/absent ETH at exit for either/both hedges). Both-hedges final-exit is COVERED; probe/ship the next uncovered both-hedges cell with traced per-leg PnL/funding, `total_pnl`, `max_live_coin_notional`, `DailyRiskState` settlement/release parity, funding on/off deltas.
  2. **If a probed both-hedges cell is covered, move to any other uncovered `stop`/`target`/`time_exit`/`liquidation`/`final_exit` × (cap_cut/commission_min/entry_next_bar/missing-or-absent-ETH-exit) cross-leg settlement cell** proven by gap evidence.
  3. **Gated-pipeline/provenance fail-closed hardening** with concrete expected values if all engine reconciliation cells probed are covered.
- **No-idle rule — ENFORCED:** if probed cell is already locked, document why with file/test evidence and probe next until you ship ≥1 MATERIAL guardrail (failing-tests-first regression lock with concrete traced values, or proven defect fix + proof). **Passive re-verification is NOT work. Editing HANDOFF.md without shipping a test+fix is NOT work.**

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

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (2026-11-12T02:57:25Z, MANDATORY, HEAVY, NON-OPTIONAL, NO ESCAPE)
```text
CRASH-REBOUND-STRATEGY | 2026-11-12T02:57:25Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

Repo identity/priority (MUST DRIVE ALL WORK): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly bar-by-bar backtest engine only. NEVER claim 20s slicing, spread/L2/order-book impact.

CAMPAIGN STATUS: #1–#4 COMPLETE. 48th-bar TARGET, LIQUIDATION, and STOP under cap_cut+commission_min+entry_next_bar (aligned + ETH entirely absent at exit, full traced settlement/funding/risk_state) are VERIFIED COVERED. PRIMARY both-hedges final-exit cell COVERED by `tests/test_both_hedges_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_20261112.py`. Do NOT re-litigate #1–#4 or covered cells without concrete failing evidence. NEXT CAMPAIGN CELLS ACTIVE.

BOTTLENECKS (audit 2026-11-12T02:57:25Z, HEAD 4542606): CLEARED. Only root `HANDOFF.md` durable. No stale `*.lock` outside `.git/`. pytest 9.2.0 installed (prior audit). Working tree clean. `research_state/gap_analysis.md` (2026-10-30) and `research_state/campaign_artifact_provenance_erratum.md` historical/partially stale — verify against code+tests. Real 283d Hyperliquid BTC/ETH data UNAVAILABLE/UNVERIFIED (fail-closed) — NEVER fabricate. If any blocker appears, REMOVE/FIX it FIRST with failing-tests-first evidence.

BLOCKING GATE (MUST RUN FIRST — NO EXCEPTIONS): `PYTHONPATH=. python3 -m pytest -q --tb=short`. Last verified 2026-11-12T02:55:xxZ → 778 passed, 12 skipped in 34.67s (HEAD 4542606). Re-run NOW; if broken/regressed, fix before ANYTHING else. Report exact count.

LOCKED (keep ALL anchors green — ZERO REGRESSION TOLERANCE): all existing anchors including 48th-bar liq/stop/target locks, boundaries `tests/test_rebound_short_liq_stop_on_48th_bar_boundary_20261108.py` and `tests/test_rebound_short_target_wins_on_48th_bar_boundary_20261108.py`, stop-at-48h cap_cut/missing-ETH, both-hedges final-exit lock `tests/test_both_hedges_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_20261112.py`, and all #1–#4 locks. Known interpretation: `max_live_coin_notional` may exceed entry-notional cap at pressure/rebound points while reservations record entry-notional cap — do NOT "fix" without concrete failing defect preserving all anchors.

NEXT CAMPAIGN PRIMARY TARGET (MANDATORY, START HERE, FAILING-TESTS-FIRST — NO ALTERNATIVES):
Ship ≥1 MATERIAL cross-leg reconciliation/settlement guardrail lock (or proven defect fix) for an UNCOVERED terminal path with BOTH long-leg and rebound-leg ETH hedges established simultaneously under `cap_cut + commission_min + entry_next_bar`, with concrete traced expected values. Hourly bar-by-bar only. Both-hedges final-exit is covered; probe the next uncovered both-hedges cell, e.g. `stop`, `target`, `time_exit`, or `liquidation` × (aligned ETH exits, or missing/absent ETH bar at exit for either/both hedges) with per-leg reconciliation and `DailyRiskState` close/settlement parity. If you find a probed cell already locked, document why with file/test evidence and probe the next uncovered cross-leg cell until you ship ≥1 MATERIAL guardrail.

Execution (NON-OPTIONAL — DEVIATION = SESSION FAILURE):
  1) GAP PROOF (do FIRST — output to console): confirm the chosen target cell is uncovered — search `tests/` for relevant `test*both*hedge*` and the specific terminal path/combination you intend to lock. Cite exact file/test evidence. If uncovered, this is the target; if covered, document exact evidence and move to next uncovered cross-leg cell.
  2) TRACE FIRST (red phase — hand-trace BEFORE asserting): deterministic hand-traced fixture from engine math. Cover coin long leg (entry, funding per held hour, exit fill/pnl) + long-leg ETH hedge (size from `eth_candles[:start_idx+1]` vol-ratio cap 3x, aligned entry, funding per held hour, exit fill/pnl, fallback to hedge entry if ETH bar missing at exit index) + rebound short leg opened after +9% target (entry, funding per held hour, exit fill/pnl) + rebound-leg ETH hedge (size from `eth_candles[:rebound_idx+1]`, aligned entry, funding, exit/fallback). Reconcile per-leg PnL, all funding legs, `total_pnl`, `max_live_coin_notional`, timestamps/bars_held, `DailyRiskState` settlement/release/close accounting parity, and funding on/off deltas. Strict no-look-ahead. Use `src/backtest/engine.py` sequencing: rebound-short checks liquidation > stop > target > time-exit; `hours_held_short = sidx - short_start_idx + 1`; time-exit fires when `>= short_bars_max` (default 48). Final-exit loop-else: if final_coin_idx >= len(eth_candles) → hedge exit raw falls back to `hedge_info['entry']` for each hedge independently.
  3) SHIP: add dated failing-tests-first regression test `tests/test_*202611*.py` (red→green). Fix engine ONLY if a concrete defect is proven by trace/spec; preserve all anchors.
  4) VERIFY: run targeted new test(s) and full gate `PYTHONPATH=. python3 -m pytest -q --tb=short` (report exact count). Keep all anchors green.

AFTER shipping first cell: continue probing/shipping remaining uncovered cross-leg reconciliation/settlement cells (stop/target/time_exit/liquidation/final_exit × cap_cut/commission_min/entry_next_bar/missing-or-absent-ETH-exit, including both-hedges cases) until exhausted; if exhausted with evidence, ship another MATERIAL guardrail (gated-pipeline/provenance or uncovered spec path) — NO IDLE, NO passive re-verification-only, NO handoff-only edit without material progress.

FINAL STEPS (MANDATORY):
  - Report exact commands/results and files changed.
  - Update ONLY root `HANDOFF.md`: new UTC timestamp, bottleneck audit, shipped material item(s)+concrete evidence, gate count, remaining risks, and a new timestamped heavy initial task for the next session.

SPEC NON-NEGOTIABLES: hourly funding on every leg/exit; hourly liquidation worst price correct sequencing/notional/timing/penalty; stopped buy never opens rebound short; 8x safety stop; rebound `-9%/48h/+40%` anchored to executed short entry; ETH hedge every leg (336h vol ratio cap 3x), hedge sizing uses `eth_candles[:idx+1]`, entry aligned (no look-ahead); RSI(21)<20 next open deepest-first in spec path; `$5M` 24h volume in all spec-compliant gating paths; 1.25% 24h-volume sizing in spec-compliant path; equal-share cuts old+new across 120% gross cap (cuts only, never top-up); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification and on missing/insufficient required ETH hedge in spec-compliant paths.
```

---

**END OF HANDOFF — THIS IS THE ONLY DURABLE CONTEXT. NEXT SESSION MUST EXECUTE THE INITIAL TASK ABOVE OR FAIL.**
