# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-11T16:34:00Z
**Single canonical durable handoff:** ONLY this root `HANDOFF.md`. Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoff variants). `scripts/controller_progress.py`, `tests/test_controller_progress_accounting.py`, timed/session-named tests, `__pycache__`, and `_probe_*` artifacts are implementation/tests/scratch, not handoffs.

## SESSION AUDIT (2026-11-11T16:34:00Z) — BOTTLENECKS CLEARED/RECORDED, HEAVY NEXT CAMPAIGN LOCKED
- **Repo identity/priorities (drives all work):** `CRASH-REBOUND-STRATEGY` → crash→rebound execution fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md` (hourly bar-by-bar backtest). Never claim 20s slicing, spread/L2/order-book impact.
- **Durable handoff audit:** **only root `HANDOFF.md` present** (no duplicate TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoff variants). No stale `*.lock` outside `.git/`.
- **Scratch/non-blockers (leave as-is unless relevant):** `_probe_*` scripts at root, `__pycache__`, `research_state/.test_derive_vol_*` are scratch/test artifacts, not handoffs/blockers.
- **Historical/partially stale docs — verify against code+tests before acting:** `research_state/gap_analysis.md` (states RSI trigger missing / ETH hedge missing / 58 tests — contradicted by current codebase/tests), `research_state/campaign_artifact_provenance_erratum.md` (historical note). Do not trust stale claims.
- **Environment blockers (fail-closed, not removable here):** real 283d Hyperliquid BTC/ETH candles unavailable/unverified — never fabricate. `pytest` is **not installed** in this environment (`python3 -m pytest` / `pip show pytest` unavailable; `/usr/share/miniconda/bin/python -m pytest` also unavailable), so the full gate could **not** be freshly re-run this audit; treat last recorded gate as unverified until reproduced in a pytest-capable env. **Next session must install/use an env with pytest and run the blocking gate first.**
- **Campaign status:** **#1 COMPLETE. #2 COMPLETE. #3 COMPLETE. #4 COMPLETE (all known missing-ETH/funding/liquidation/final-exit combos locked per prior evidence).** No uncovered #4 combo re-opened without concrete failing evidence. Work MUST move to the NEXT CAMPAIGN (cross-leg reconciliation/settlement guardrails, failing-tests-first).

## LAST RECORDED GATE (UNVERIFIED THIS SESSION — ENV MISSING PYTEST)
- Recorded 2026-11-11T15:03:07Z: `PYTHONPATH=. python3 -m pytest -q --tb=short` → **767 passed, 12 skipped in 28.69s**.
- **2026-11-11T16:34:00Z:** could not re-run (pytest unavailable). **Blocking first action next session:** run full gate in pytest-capable env and fix FIRST if broken/regressed.

## MATERIAL SHIPPED (CARRY-FORWARD EVIDENCE)
- **2026-11-11T13:17:59Z (#4 completed):** `tests/test_rebound_short_stop_target_missing_eth_exit_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py` (2 passed) — rebound-short STOP/TARGET with missing ETH at exit idx, cap_cut/commission_min/entry_next_bar, per-leg funding reconciliation vs funding-off, fallback hedge-exit parity, rebound-leg settlement/risk_state release, `max_live_coin_notional` traced.
- **2026-11-11T12:17:54Z:** `tests/test_long_time_exit_missing_eth_exit_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py` (2 tests) — long TIME_EXIT missing ETH fallback + funding/settlement reconciliation.
- **2026-11-11T09:16:00Z (#3 COMPLETE):** 6 test files / 14 tests — batch/sequential cuts, heterogeneous commission_min, deterministic tie-break, no top-up, settlement reconciliation, no-look-ahead.
- **2026-11-11T05:29:28Z (#2/#1 COMPLETE):** rebound-short liquidation ETH bar entirely absent at exit index locked; 1.25% 24h-volume sizing bypass fixed/locked.
- **#4 anchor locks (examples):** `tests/test_rebound_short_48h_time_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_missing_eth_bar_fallback_raw_risk_settlement_20261111.py`, `tests/test_rebound_short_funding_all_paths.py`, `tests/test_rebound_short_liquidation_eth_absent_at_exit_index_cap_cut_commission_min_entry_next_bar_funding_20261111.py`, `tests/test_rebound_short_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_missing_final_eth_20261110.py`.

## IMPLEMENTATION STATUS (EVIDENCE-BACKED, KEY SURFACES — verify stale docs against these)
- **Core/spec-compliant paths:** RSI(21)<20 crash trigger, $5M 24h volume enforcement, 1.25% 24h-volume sizing when enabled, ETH hedge sizing 336h vol-ratio capped 3x with no-look-ahead (`eth_candles[:idx+1]`), rebound short after +9% target (stop +40%, target -9%, 48h), 8x spec safety stop, 120% gross-cap equal-share cuts (cuts only), portfolio bar-by-bar no-look-ahead admission with deepest-first ordering.
- **Runners/gating:** `scripts/run_portfolio.py` per-bar gating, deepest-first sort, reservation/cap-cut overlay/batch pre-cut. `run_real_campaign.py` fail-closed provenance/verified gates. Engine fail-closed when `require_eth_hedge=True` and no usable hedge.
- **Known interpretation (not a defect without concrete failing proof):** `max_live_coin_notional` can exceed entry-notional cap at pressure points/across rebound leg while reservations record entry-notional cap — do NOT "fix" without concrete failing defect preserving all anchors.
- **Engine rebound-short sequencing (evidence `src/backtest/engine.py`):** on each rebound-short bar checks liquidation > stop > target > time-exit; `hours_held_short = sidx - short_start_idx + 1`; time-exit fires when `>= short_bars_max` (default 48). This is the implementation truth to trace against spec.

## REMAINING RISKS / HEAVY FOCUS CAMPAIGN (MANDATORY)
- **BLOCKED by environment (fail-closed):** real 283d Hyperliquid candles unavailable/unverified. Never fabricate.
- **#1–#4 COMPLETE. NEXT CAMPAIGN ACTIVE (PRIMARY, MANDATORY, heavy, failing-tests-first):** cross-leg reconciliation/settlement guardrail hardening for terminal paths (`stop`/`target`/`time_exit`/`liquidation`/`final_exit`) on all live legs (coin long/short + ETH/rebound hedge) with concrete traced expected values — fills per leg, PnL per leg, timestamps, hedge notional/side/entry/exit, hourly funding per held hour per leg, liquidation penalty/worst-price where relevant, `total_pnl`, `max_live_coin_notional`, `risk_state` settlement/release, and strict no-look-ahead. OR gated-pipeline/provenance fail-closed guardrail hardening with concrete expected values.
- **Candidate first cells to PROBE WITH EVIDENCE (pick first proven-uncovered, ship lock):**
  1. **Rebound-short liquidation on exact 48th held bar UNDER cap_cut (not `_NoCutRS`) + commission_min + entry_next_bar** with aligned AND missing ETH — full cross-leg settlement/funding reconciliation and precedence over 48h time-exit. **PRIMARY START.** Coverage gap (evidence): `tests/test_rebound_short_liq_stop_on_48th_bar_boundary_20261108.py` covers liq/stop-beats-time-exit on 48th bar with aligned ETH, `commission_min=1.0`, `entry_next_bar=True` but uses `_NoCutRS` (no cap_cut, no missing ETH); `tests/test_rebound_short_time_exit_48h_funding_spec_20261108.py` covers time-exit funding with `enable_eth_hedge=False`/no liq checks. No existing test combines 48th-bar liquidation breach + cap_cut + commission_min + entry_next_bar + (aligned and missing ETH) + full traced per-leg reconciliation.
  2. **Rebound-short stop on exact 48th held bar UNDER cap_cut + commission_min + entry_next_bar** (aligned/missing ETH) — traced settlement/funding per leg, precedence over time-exit.
  3. **Rebound-short liquidation-at-48h-boundary with ETH entirely absent/unusable** under cap_cut path — fail-closed/fallback semantics proven by trace and locked.
  4. **Final-exit path (end-of-data) with both long+rebound-short+both hedges funded** under `cap_cut + commission_min + entry_next_bar` — explicit per-leg reconciliation and `risk_state` close accounting parity.
- **No-idle rule:** if a probed cell is already locked, document why with file/test evidence and probe next candidate until you ship >=1 MATERIAL guardrail (failing-tests-first regression lock with concrete traced values, or proven defect fix + proof).

## CRITICAL CONTEXT
- **Spec truth:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Test window 2025-12-20→2026-09-28 (283d), 6792 hourly bars/symbol.
- **Core:** `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/{loader,provenance,streaming_ingest}.py`, `src/metrics/campaign_metrics.py`
- **Runners/guards:** `scripts/run_portfolio.py`, `scripts/run_real_campaign.py`, `scripts/run_campaign.py`, `scripts/derive_verified_universe.py`, `scripts/fetch_hyperliquid_candles.py`, `scripts/generate_candle_coverage_gap_report.py`

## RULES (NON-NEGOTIABLE)
- **Heavy-work guardrail:** each session ships >=1 material item with concrete evidence.
- **Spec is truth:** both legs, ETH hedge every leg, funding/liquidation correct on every leg/exit path, $5M gating in all spec-compliant paths, 1.25% 24h-volume sizing in spec-compliant paths, equal-share cuts old+new, stopped buy never opens rebound short.
- **Gating boundaries:** `backtest_simple` is low-level executor (signal assumed). Spec-compliant gating in `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners.
- **Fail-closed:** missing provenance/verification for real path → reject. Never fabricate numbers/artifacts.
- **Single handoff:** only root `HANDOFF.md`.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (2026-11-11T16:34:00Z, MANDATORY, HEAVY, NON-OPTIONAL)
```text
CRASH-REBOUND-STRATEGY | 2026-11-11T16:34:00Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

Repo identity/priority (MUST DRIVE ALL WORK): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly bar-by-bar backtest engine only. NEVER claim 20s slicing, spread/L2/order-book impact.

CAMPAIGN STATUS (2026-11-11T16:34:00Z): #1 COMPLETE. #2 COMPLETE. #3 COMPLETE. #4 COMPLETE (all known missing-ETH/funding/liquidation/final-exit combos locked per recorded evidence). Do NOT re-litigate #1-#4 without concrete failing evidence. NEXT CAMPAIGN is ACTIVE and MANDATORY.

BOTTLENECKS (audit 2026-11-11T16:34:00Z): CLEARED/RECORDED. Only root `HANDOFF.md` is durable (no duplicate TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoffs). No stale `*.lock` outside `.git/`. `_probe_*`/`__pycache__`/`research_state/.test_derive_vol_*` are scratch/test artifacts, not blockers. `research_state/gap_analysis.md` and `research_state/campaign_artifact_provenance_erratum.md` are historical/partially stale — verify against code+tests before use. Real 283d Hyperliquid BTC/ETH data UNAVAILABLE/UNVERIFIED (fail-closed) — NEVER fabricate. `pytest` is not installed in this environment (gate not freshly runnable here) — this is the immediate environment bottleneck: obtain/use a pytest-capable env and run the blocking gate FIRST. If you encounter any other blocker (duplicate handoff, stale lock, broken gate, contradictory artifact), REMOVE/FIX it FIRST with failing-tests-first evidence before other work.

BLOCKING GATE (MUST RUN FIRST): `PYTHONPATH=. python3 -m pytest -q --tb=short` in a pytest-capable environment. Last recorded 2026-11-11T15:03:07Z → **767 passed, 12 skipped in 28.69s** (NOT freshly verified this audit). If broken/regressed, fix before anything else. Do not treat prior counts as fresh.

LOCKED (keep ALL anchors green): all existing engine/runner/regression anchors including #4 locks: `tests/test_rebound_short_48h_time_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_missing_eth_bar_fallback_raw_risk_settlement_20261111.py`, `tests/test_rebound_short_funding_all_paths.py`, `tests/test_rebound_short_liquidation_eth_absent_at_exit_index_cap_cut_commission_min_entry_next_bar_funding_20261111.py`, `tests/test_rebound_short_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_missing_final_eth_20261110.py`, `tests/test_rebound_short_stop_target_missing_eth_exit_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py`, `tests/test_long_time_exit_missing_eth_exit_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py`, and all #3/#2/#1 locks. Known interpretation: `max_live_coin_notional` may exceed entry-notional cap at pressure/rebound points while reservations record entry-notional cap — do NOT "fix" without concrete failing defect preserving all anchors.

NEXT CAMPAIGN PRIMARY TARGET (MANDATORY, START HERE, failing-tests-first):
Ship >=1 MATERIAL cross-leg reconciliation/settlement guardrail lock (or proven defect fix) for an UNCOVERED terminal path on all live legs with concrete traced expected values. Hourly bar-by-bar only.

Execution (non-optional):
  1) GAP PROOF: probe candidate uncovered cells and pick the first proven-uncovered. START WITH cell #1: rebound-short LIQUIDATION on exact 48th held bar (precedence over 48h time-exit) UNDER cap_cut (NOT `_NoCutRS`) + commission_min + entry_next_bar, for aligned ETH and missing/unusable ETH — full cross-leg settlement/funding reconciliation. Coverage gap (evidence): `tests/test_rebound_short_liq_stop_on_48th_bar_boundary_20261108.py` covers liq/stop-beats-time-exit on 48th bar with aligned ETH, commission_min=1.0, entry_next_bar=True but `_NoCutRS` (no cap_cut, no missing ETH); `tests/test_rebound_short_time_exit_48h_funding_spec_20261108.py` covers time-exit funding with enable_eth_hedge=False/no liq checks. NO existing test combines 48th-bar liquidation breach + cap_cut + commission_min + entry_next_bar + (aligned and missing ETH) + full traced per-leg reconciliation. Cite existing tests/files proving/disproving coverage; do not guess.
  2) TRACE FIRST (red phase): build deterministic hand-traced fixture from engine math BEFORE asserting — coin long/short entry+exit fills, pnl per leg, hedge side/size/entry/exit, hedge pnl, hourly funding per held hour on EVERY live leg (long coin, short coin, long/short ETH hedges), liquidation penalty/worst-price/timing where relevant, `total_pnl`, `max_live_coin_notional`, timestamps/bars_held, `risk_state` settlement+release, no look-ahead.
  3) SHIP: add dated failing-tests-first regression test `tests/test_*202611*.py` (red→green). Fix engine ONLY if a concrete defect is proven by the trace/spec; preserve all anchors.
  4) VERIFY: run targeted new test(s) and full gate `PYTHONPATH=. python3 -m pytest -q --tb=short` (report exact count). Keep all anchors green (expect >=767 passed, 12 skipped unless legitimately changed by material work).

AFTER shipping first cell: continue probing/shipping remaining uncovered cross-leg reconciliation/settlement cells until exhausted; if exhausted with evidence, ship another MATERIAL guardrail (gated-pipeline/provenance or uncovered spec path) — NO IDLE, NO passive re-verification-only, NO handoff-only edit without material progress.

FINAL STEPS:
  - Report exact commands/results and files changed.
  - Update ONLY root `HANDOFF.md`: new UTC timestamp, bottleneck audit, shipped material item(s)+concrete evidence, gate count, remaining risks, and a new timestamped heavy initial task for the next session.

SPEC NON-NEGOTIABLES (never regress): hourly funding on every leg/exit; hourly liquidation worst price correct sequencing/notional/timing/penalty; stopped buy never opens rebound short; 8x safety stop; rebound `-9%/48h/+40%` anchored to executed short entry; ETH hedge every leg (336h vol ratio cap 3x), hedge sizing uses `eth_candles[:idx+1]`, entry aligned (no look-ahead); RSI(21)<20 next open deepest-first in spec path; `$5M` 24h volume in all spec-compliant gating paths; 1.25% 24h-volume sizing in spec-compliant path; equal-share cuts old+new across 120% gross cap (cuts only, never top-up); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification and on missing/insufficient required ETH hedge in spec-compliant paths.
```
