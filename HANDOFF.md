# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-12T02:08:30Z
**HEAD:** `b13e4ae chore(kilo): checkpoint agent session` (working tree clean at audit; no new commit shipped this session)
Single canonical durable handoff: ONLY this root `HANDOFF.md`. Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoff variants). `scripts/controller_progress.py`, `tests/test_controller_progress_accounting.py`, timed/session-named tests, `__pycache__`, and `_probe_*`/`_trace_*`/`_debug_*` artifacts are implementation/tests/scratch, not handoffs.

## SESSION AUDIT (2026-11-12T02:06:46Z) — BOTTLENECKS AUDITED/CLEARED, HEAVY CAMPAIGN CONFIRMED
- **Durable handoff audit (verified):** only root `HANDOFF.md` is a durable handoff. No TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT/*handoff* durable docs found. `scripts/controller_progress.py`, dated/session tests, probes/traces/debugs, `__pycache__` are implementation/tests/scratch, not handoffs.
- **Lock/blocker audit (verified):** no stale `*.lock` files outside `.git/`. No process/session bottlenecks found; nothing to remove. Working tree clean.
- **Scratch/non-blockers:** root `_probe_*`/`_trace_*`/`_debug_*`, `__pycache__`, `research_state/.test_derive_vol_*`. Do not re-ship scratch traces.
- **Historical docs (stale/verify against code+tests):** `research_state/gap_analysis.md` (2026-10-30, lists RSI/hedge/sizing/universe as missing but later tests/impl cover major parts) and `research_state/campaign_artifact_provenance_erratum.md`.
- **Environment:** `pytest 9.2.0` installed. **Real 283d Hyperliquid BTC/ETH candles unavailable/unverified (fail-closed) — NEVER fabricate.**
- **Coverage evidence spot-check (2026-11-12T02:08:30Z):** final-exit tests exist for rebound-only aligned ETH (`tests/test_rebound_short_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_20261110.py`), rebound-only missing-final-ETH (`tests/test_rebound_short_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_missing_final_eth_20261110.py`), and long-only (`tests/test_long_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_20261110.py`); **no `tests/test*both*hedge*` present** — confirms primary target (both long-leg + rebound-leg hedges funded through final-exit loop-else, cap_cut+commission_min+entry_next_bar) remains uncovered and highest-priority.

## LAST VERIFIED GATE (CARRY-FORWARD; NOT RE-RUN THIS SESSION)
- `PYTHONPATH=. python3 -m pytest -q --tb=short` → **776 passed, 12 skipped in 34.62s** (2026-11-12T02:08:xxZ, HEAD b13e4ae; tree clean, checkpoint only, no source/test edits this session). **MUST re-run first in next session**; do not treat this count as fresh if tree/HEAD changes.

## MATERIAL SHIPPED / LOCKED EVIDENCE (CARRY-FORWARD)
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
  1. **PRIMARY — Final-exit path (end-of-data, loop-else) with BOTH long-leg ETH hedge AND rebound-short ETH hedge established and funded simultaneously** under `cap_cut + commission_min + entry_next_bar` — explicit per-leg reconciliation and `DailyRiskState` close accounting parity with funding on/off deltas (UNCOVERED; no both-hedges test exists).
  2. **Any other uncovered `stop`/`target`/`time_exit`/`liquidation`/`final_exit` × (cap_cut/commission_min/entry_next_bar/missing-or-absent-ETH-exit) cross-leg settlement cell** proven by gap evidence (including cases where both long-leg and rebound-leg hedges are established simultaneously).
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

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (2026-11-12T02:08:30Z, MANDATORY, HEAVY, NON-OPTIONAL, NO ESCAPE)
```text
CRASH-REBOUND-STRATEGY | 2026-11-12T02:08:30Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

Repo identity/priority (MUST DRIVE ALL WORK): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly bar-by-bar backtest engine only. NEVER claim 20s slicing, spread/L2/order-book impact.

CAMPAIGN STATUS: #1–#4 COMPLETE. 48th-bar TARGET, LIQUIDATION, and STOP under cap_cut+commission_min+entry_next_bar (aligned + ETH entirely absent at exit, full traced settlement/funding/risk_state) are VERIFIED COVERED by passing `tests/test_rebound_short_target_48th_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py`, `tests/test_rebound_short_liquidation_48th_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py`, and `tests/test_rebound_short_stop_48th_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py`. Do NOT re-litigate #1–#4 or covered cells without concrete failing evidence. NEXT CAMPAIGN CELLS ACTIVE.

BOTTLENECKS (audit 2026-11-12T02:08:30Z, HEAD b13e4ae): CLEARED. Only root `HANDOFF.md` durable. No stale `*.lock` outside `.git/`. pytest 9.2.0 installed. Working tree clean. `research_state/gap_analysis.md` (2026-10-30) and `research_state/campaign_artifact_provenance_erratum.md` historical/partially stale — verify against code+tests. Real 283d Hyperliquid BTC/ETH data UNAVAILABLE/UNVERIFIED (fail-closed) — NEVER fabricate. If any blocker appears, REMOVE/FIX it FIRST with failing-tests-first evidence.

BLOCKING GATE (MUST RUN FIRST — NO EXCEPTIONS): `PYTHONPATH=. python3 -m pytest -q --tb=short`. Last verified 2026-11-12T02:08:xxZ → 776 passed, 12 skipped in 34.62s (HEAD b13e4ae). Re-run NOW; if broken/regressed, fix before ANYTHING else. Report exact count.

LOCKED (keep ALL anchors green — ZERO REGRESSION TOLERANCE): all existing anchors including the three 48th-bar locks above, boundaries `tests/test_rebound_short_liq_stop_on_48th_bar_boundary_20261108.py` and `tests/test_rebound_short_target_wins_on_48th_bar_boundary_20261108.py`, stop-at-48h cap_cut/missing-ETH, and all #1–#4 locks. Known interpretation: `max_live_coin_notional` may exceed entry-notional cap at pressure/rebound points while reservations record entry-notional cap — do NOT "fix" without concrete failing defect preserving all anchors.

NEXT CAMPAIGN PRIMARY TARGET (MANDATORY, START HERE, FAILING-TESTS-FIRST — NO ALTERNATIVES):
Ship ≥1 MATERIAL cross-leg reconciliation/settlement guardrail lock (or proven defect fix) for an UNCOVERED terminal path on ALL live legs with concrete traced expected values. Hourly bar-by-bar only.

Execution (NON-OPTIONAL — DEVIATION = SESSION FAILURE):
  1) GAP PROOF (do FIRST — output to console): confirm primary target uncovered — final-exit (loop-else/end-of-data) with BOTH long-leg ETH hedge AND rebound-short ETH hedge established and funded simultaneously under `cap_cut + commission_min + entry_next_bar`. Existing coverage to cite: `tests/test_rebound_short_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_20261110.py` (rebound-only aligned), `tests/test_rebound_short_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_missing_final_eth_20261110.py` (rebound-only missing-final-ETH), `tests/test_long_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_20261110.py` (long-only) — NONE cover both hedges together (no `tests/test*both*hedge*` found). If truly uncovered, this is the target; if you find full coverage elsewhere, document exact file/test evidence and move to next uncovered cross-leg cell.
  2) TRACE FIRST (red phase — hand-trace BEFORE asserting): deterministic hand-traced fixture from engine math. Cover coin long leg (entry, funding per held hour, final-exit fill/pnl) + long-leg ETH hedge (size from `eth_candles[:start_idx+1]` vol-ratio cap 3x, aligned entry, funding per held hour, final-exit fill/pnl, fallback to hedge entry if final ETH bar missing) + rebound short leg opened after +9% target (entry, funding per held hour, final-exit fill/pnl) + rebound-leg ETH hedge (size from `eth_candles[:rebound_idx+1]`, aligned entry, funding, final-exit/fallback). Reconcile per-leg PnL, all funding legs, `total_pnl`, `max_live_coin_notional`, timestamps/bars_held, `DailyRiskState` settlement/release/close accounting parity, and funding on/off deltas. Strict no-look-ahead. Use `src/backtest/engine.py` sequencing: rebound-short checks liquidation > stop > target > time-exit; `hours_held_short = sidx - short_start_idx + 1`; time-exit fires when `>= short_bars_max` (default 48). Final-exit loop-else: if final_coin_idx >= len(eth_candles) → hedge exit raw falls back to `hedge_info['entry']` for each hedge independently.
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