# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-12T01:12:02Z
**HEAD:** `7aaa0fd chore(kilo): checkpoint agent session`
Single canonical durable handoff: ONLY this root `HANDOFF.md`. Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoff variants). `scripts/controller_progress.py`, `tests/test_controller_progress_accounting.py`, timed/session-named tests, `__pycache__`, and `_probe_*`/`_trace_*`/`_debug_*` artifacts are implementation/tests/scratch, not handoffs.

## SESSION AUDIT (2026-11-12T01:12:02Z) — BOTTLENECKS AUDITED/CLEARED, HEAVY CAMPAIGN CONFIRMED
- **Durable handoff audit:** only root `HANDOFF.md` is a durable handoff (verified). No TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT durable handoff docs found (`scripts/controller_progress.py`, dated/session tests, probes/traces/debugs, `__pycache__` are implementation/tests/scratch, not handoffs).
- **Lock/blocker audit:** no stale `*.lock` files outside `.git/` (verified). Working tree clean before this HANDOFF refresh. No process/session bottlenecks found; nothing to remove.
- **Scratch/non-blockers:** root `_probe_*`/`_trace_*`/`_debug_*`, `__pycache__`, `research_state/.test_derive_vol_*`. Do not re-ship scratch traces.
- **Historical docs:** `research_state/gap_analysis.md` (2026-10-30) and `research_state/campaign_artifact_provenance_erratum.md` are historical/partially stale — verify against code+tests.
- **Environment:** `pytest 9.2.0` installed. **Real 283d Hyperliquid BTC/ETH candles unavailable/unverified (fail-closed) — NEVER fabricate.**
- **Coverage evidence (reconfirmed):** 48th-bar TARGET, LIQUIDATION, and STOP under cap_cut+commission_min+entry_next_bar (aligned + ETH entirely absent at exit, full traced settlement/funding/risk_state) are all locked and passing.

## LAST VERIFIED GATE (CARRY-FORWARD; NOT RE-RUN THIS SESSION)
- `PYTHONPATH=. python3 -m pytest -q --tb=short` → **776 passed, 12 skipped in 35.09s** (2026-11-12T01:08:40Z, HEAD 7aaa0fd). **MUST re-run first in next session**; do not treat this count as fresh if tree changes.

## MATERIAL SHIPPED / LOCKED EVIDENCE (CARRY-FORWARD)
- **2026-11-11T23:53:36Z:** `tests/test_rebound_short_stop_48th_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py` — 48th held bar STOP precedence over 48h time-exit, cap_cut-implied 600 shares, commission_min, entry_next_bar, aligned/absent ETH at exit, per-leg fills/PnL/funding, hedge sizing/entry/exit/fallback, `total_pnl`, `max_live_coin_notional`, `risk_state` settlement/release, funding on/off deltas.
- **2026-11-11T23:44:38Z:** `tests/test_rebound_short_target_48th_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py` — 48th-bar TARGET precedence.
- **2026-11-11T20:44:56Z:** `tests/test_rebound_short_liquidation_48th_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py` — 48th-bar LIQUIDATION precedence.
- **2026-11-11T13:17:59Z (#4):** `tests/test_rebound_short_stop_target_missing_eth_exit_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py`
- **2026-11-11T12:17:54Z:** `tests/test_long_time_exit_missing_eth_exit_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py`
- **2026-11-11T09:16:00Z (#3 COMPLETE):** batch/sequential cuts, heterogeneous commission_min, deterministic tie-break, no top-up, settlement reconciliation, no-look-ahead.
- **2026-11-11T05:29:28Z (#2/#1):** rebound-short liquidation ETH bar entirely absent at exit index locked; 1.25% 24h-volume sizing bypass fixed/locked.
- **Anchors:** 48th-bar liq/stop/target boundaries, stop-at-48h cap_cut/missing-ETH, rebound-short funding/liq/final-exit/missing-ETH fallback families, gated pipeline/provenance fail-closed suites.

## IMPLEMENTATION STATUS (EVIDENCE-BACKED)
- Core/spec-compliant paths: RSI(21)<20 crash trigger, $5M 24h volume enforcement, 1.25% 24h-volume sizing when enabled, ETH hedge sizing 336h vol-ratio capped 3x with no-look-ahead (`eth_candles[:idx+1]`), rebound short after +9% target (stop +40%, target -9%, 48h), 8x spec safety stop, 120% gross-cap equal-share cuts (cuts only), portfolio bar-by-bar no-look-ahead admission with deepest-first ordering.
- Runners/gating: `scripts/run_portfolio.py` per-bar gating/deepest-first/reservation/cap-cut. `run_real_campaign.py` fail-closed provenance/verified gates. Engine fail-closed when `require_eth_hedge=True` and no usable hedge.
- Engine rebound-short sequencing (`src/backtest/engine.py`): liquidation > stop > target > time-exit; `hours_held_short = sidx - short_start_idx + 1`; time-exit fires when `>= short_bars_max` (default 48). Liquidation `~507`, stop `~543`, target `~576`, time-exit `~605`.
- Known interpretation (not defect without proof): `max_live_coin_notional` may exceed entry-notional cap at pressure/rebound points while reservations record entry-notional cap — do NOT "fix" without concrete failing defect preserving anchors.

## REMAINING RISKS / HEAVY FOCUS CAMPAIGN (MANDATORY)
- **BLOCKED (fail-closed):** real 283d Hyperliquid candles unavailable/unverified. Never fabricate.
- **NEXT CAMPAIGN CELLS ACTIVE (ship in priority order with evidence):**
  1. **Final-exit path (end-of-data) with long+rebound-short+both hedges funded** under `cap_cut + commission_min + entry_next_bar` — explicit per-leg reconciliation and `DailyRiskState` close accounting parity with funding on/off deltas. Gap: existing tests cover final-exit with aligned/missing ETH for rebound short alone (`tests/test_rebound_short_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_20261110.py`, `tests/test_rebound_short_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_missing_final_eth_20261110.py`) and long leg alone (`tests/test_long_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_20261110.py`), but **NO test covers both long-leg ETH hedge AND rebound-short ETH hedge simultaneously established and funded through final-exit loop-else**. Cite existing tests/files proving/disproving coverage before coding.
  2. **Any other uncovered `stop`/`target`/`time_exit`/`liquidation`/`final_exit` × (cap_cut/commission_min/entry_next_bar/missing-or-absent-ETH-exit) cross-leg settlement cell** proven by gap evidence (including cases where both long-leg and rebound-leg hedges are established simultaneously).
  3. **Gated-pipeline/provenance fail-closed hardening** with concrete expected values if all engine reconciliation cells probed are covered.
- **No-idle rule:** if probed cell is already locked, document why with file/test evidence and probe next until you ship >=1 MATERIAL guardrail (failing-tests-first regression lock with concrete traced values, or proven defect fix + proof).

## CRITICAL CONTEXT
- Spec truth: `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Test window 2025-12-20→2026-09-28 (283d), 6792 hourly bars/symbol.
- Core: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/{loader,provenance,streaming_ingest}.py`, `src/metrics/campaign_metrics.py`
- Runners/guards: `scripts/run_portfolio.py`, `scripts/run_real_campaign.py`, `scripts/run_campaign.py`, `scripts/derive_verified_universe.py`, `scripts/fetch_hyperliquid_candles.py`, `scripts/generate_candle_coverage_gap_report.py`

## RULES (NON-NEGOTIABLE)
- Each session ships >=1 material item with concrete evidence.
- Spec is truth: both legs, ETH hedge every leg, funding/liquidation correct on every leg/exit path, $5M gating, 1.25% 24h-volume sizing in spec-compliant paths, equal-share cuts old+new, stopped buy never opens rebound short.
- `backtest_simple` is low-level executor (signal assumed). Spec-compliant gating in `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners.
- Fail-closed: missing provenance/verification for real path → reject. Never fabricate.
- Single handoff: only root `HANDOFF.md`.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (2026-11-12T01:12:02Z, MANDATORY, HEAVY, NON-OPTIONAL)
```text
CRASH-REBOUND-STRATEGY | 2026-11-12T01:12:02Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

Repo identity/priority (MUST DRIVE ALL WORK): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly bar-by-bar backtest engine only. NEVER claim 20s slicing, spread/L2/order-book impact.

CAMPAIGN STATUS: #1–#4 COMPLETE. 48th-bar TARGET, LIQUIDATION, and STOP under cap_cut+commission_min+entry_next_bar (aligned + ETH entirely absent at exit, full traced settlement/funding/risk_state) are VERIFIED COVERED by passing `tests/test_rebound_short_target_48th_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py`, `tests/test_rebound_short_liquidation_48th_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py`, and `tests/test_rebound_short_stop_48th_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py`. Do NOT re-litigate #1–#4 or covered cells without concrete failing evidence. NEXT CAMPAIGN CELLS ACTIVE.

BOTTLENECKS (audit 2026-11-12T01:12:02Z, HEAD 7aaa0fd): CLEARED. Only root `HANDOFF.md` durable. No stale `*.lock` outside `.git/`. Working tree clean (pre-handoff). pytest 9.2.0 installed. `research_state/gap_analysis.md` (2026-10-30) and `research_state/campaign_artifact_provenance_erratum.md` historical/partially stale — verify against code+tests. Real 283d Hyperliquid BTC/ETH data UNAVAILABLE/UNVERIFIED (fail-closed) — NEVER fabricate. If any blocker appears, REMOVE/FIX it FIRST with failing-tests-first evidence.

BLOCKING GATE (MUST RUN FIRST): `PYTHONPATH=. python3 -m pytest -q --tb=short`. Last verified 2026-11-12T01:08:40Z → 776 passed, 12 skipped in 35.09s (not re-run this session). Re-run now; if broken/regressed, fix before anything else.

LOCKED (keep ALL anchors green): all existing anchors including the three 48th-bar locks above, boundaries `tests/test_rebound_short_liq_stop_on_48th_bar_boundary_20261108.py` and `tests/test_rebound_short_target_wins_on_48th_bar_boundary_20261108.py`, stop-at-48h cap_cut/missing-ETH, and all #1–#4 locks. Known interpretation: `max_live_coin_notional` may exceed entry-notional cap at pressure/rebound points while reservations record entry-notional cap — do NOT "fix" without concrete failing defect preserving all anchors.

NEXT CAMPAIGN PRIMARY TARGET (MANDATORY, START HERE, failing-tests-first):
Ship >=1 MATERIAL cross-leg reconciliation/settlement guardrail lock (or proven defect fix) for an UNCOVERED terminal path on all live legs with concrete traced expected values. Hourly bar-by-bar only.

Execution (non-optional):
  1) GAP PROOF: probe candidates and pick first proven-uncovered. START WITH: final-exit (loop-else/end-of-data) path with long+rebound-short+both hedges funded under `cap_cut + commission_min + entry_next_bar` — require explicit per-leg reconciliation AND `DailyRiskState` close accounting parity with funding on/off deltas. Cite files/tests proving/disproving coverage (e.g. `tests/test_rebound_short_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_20261110.py` covers rebound-only aligned ETH; `tests/test_rebound_short_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_missing_final_eth_20261110.py` covers rebound-only missing-final-ETH; `tests/test_long_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_20261110.py` covers long-only missing-final-ETH — NONE cover BOTH long-leg hedge + rebound-leg hedge together through final-exit). If uncovered, treat as primary target; if already fully covered, document with evidence and move to next uncovered cross-leg cell.
  2) TRACE FIRST (red phase): deterministic hand-traced fixture from engine math BEFORE asserting — coin long/short entry+exit fills, pnl per leg, both hedge sides/sizes/entry/exit if present, hedge pnl per leg, hourly funding per held hour on EVERY live leg, liquidation penalty/worst-price/timing where relevant, `total_pnl`, `max_live_coin_notional`, timestamps/bars_held, `risk_state` settlement+release (and any in-loop vs final settlement semantics), strict no-look-ahead. Use `src/backtest/engine.py` sequencing: rebound-short checks liquidation > stop > target > time-exit; `hours_held_short = sidx - short_start_idx + 1`; time-exit fires when `>= short_bars_max` (default 48). Long-leg hedge sized on `eth_candles[:start_idx+1]` aligned to `start_idx`; rebound-leg hedge sized on `eth_candles[:rebound_idx+1]` aligned to `rebound_idx` (no look-ahead). Final-exit loop-else: if final_coin_idx >= len(eth_candles) → hedge exit raw falls back to hedge_info['entry'] for both hedges independently.
  3) SHIP: add dated failing-tests-first regression test `tests/test_*202611*.py` (red→green). Fix engine ONLY if a concrete defect is proven by trace/spec; preserve all anchors.
  4) VERIFY: run targeted new test(s) and full gate `PYTHONPATH=. python3 -m pytest -q --tb=short` (report exact count). Keep all anchors green.

AFTER shipping first cell: continue probing/shipping remaining uncovered cross-leg reconciliation/settlement cells (stop/target/time_exit/liquidation/final_exit × cap_cut/commission_min/entry_next_bar/missing-or-absent-ETH-exit, including both-hedges cases) until exhausted; if exhausted with evidence, ship another MATERIAL guardrail (gated-pipeline/provenance or uncovered spec path) — NO IDLE, NO passive re-verification-only, NO handoff-only edit without material progress.

FINAL STEPS:
  - Report exact commands/results and files changed.
  - Update ONLY root `HANDOFF.md`: new UTC timestamp, bottleneck audit, shipped material item(s)+concrete evidence, gate count, remaining risks, and a new timestamped heavy initial task for the next session.

SPEC NON-NEGOTIABLES: hourly funding on every leg/exit; hourly liquidation worst price correct sequencing/notional/timing/penalty; stopped buy never opens rebound short; 8x safety stop; rebound `-9%/48h/+40%` anchored to executed short entry; ETH hedge every leg (336h vol ratio cap 3x), hedge sizing uses `eth_candles[:idx+1]`, entry aligned (no look-ahead); RSI(21)<20 next open deepest-first in spec path; `$5M` 24h volume in all spec-compliant gating paths; 1.25% 24h-volume sizing in spec-compliant path; equal-share cuts old+new across 120% gross cap (cuts only, never top-up); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification and on missing/insufficient required ETH hedge in spec-compliant paths.
```