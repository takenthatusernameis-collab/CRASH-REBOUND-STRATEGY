# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-11T13:25:12Z
**Single canonical durable handoff:** ONLY this root `HANDOFF.md`. Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoff variants). `scripts/controller_progress.py`, `tests/test_controller_progress_accounting.py`, timed/session-named tests, `__pycache__`, and `_probe_*` artifacts are implementation/tests/scratch, not handoffs.

## SESSION AUDIT (2026-11-11T13:25:12Z) — #4 COMPLETE (ALL COMBOS LOCKED; NEXT CAMPAIGN DEFINED)
- **Repo identity/priorities:** `CRASH-REBOUND-STRATEGY` — crash→rebound execution fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md` (hourly bar-by-bar backtest). Never claim 20s slicing, spread/L2/order-book impact.
- **Bottlenecks checked/cleared:** only root `HANDOFF.md` exists as durable handoff (no duplicate TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoff docs). No `*.lock` outside `.git/`. `_probe_*`/cache artifacts and `research_state/.test_derive_vol_*` are scratch/gitignored — not blockers. `research_state/gap_analysis.md` and `research_state/campaign_artifact_provenance_erratum.md` are historical/partially stale — verify against code+tests before acting. Real 283d Hyperliquid BTC/ETH candles remain unavailable/unverified (fail-closed by design, environment blocker — never fabricate). **No process/session blockers preventing heavy implementation work.**
- **Campaign status:** #1 COMPLETE. #2 COMPLETE. #3 COMPLETE. **#4 COMPLETE (PRIMARY + ALL SUB-ITEMS LOCKED).** This session confirms #4 fully locked with concrete evidence: rebound-short 48h TIME_EXIT missing-ETH fallback + explicit per-leg funding-off reconciliation + risk_state settlement (`tests/test_rebound_short_48h_time_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_missing_eth_bar_fallback_raw_risk_settlement_20261111.py`, 2 passed); funding accrual sign correctness on every rebound-short exit path (stop/target/liquidation/time_exit/final_exit, `tests/test_rebound_short_funding_all_paths.py`); liquidation worst-price sequencing/notional/timing/penalty under cap_cut+commission_min+entry_next_bar with ETH entirely absent at exit index + funding delta (`tests/test_rebound_short_liquidation_eth_absent_at_exit_index_cap_cut_commission_min_entry_next_bar_funding_20261111.py`, 2 passed); rebound-short final-exit missing-ETH fallback reconciliation with risk_state settlement and funding parity (`tests/test_rebound_short_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_missing_final_eth_20261110.py`). **No uncovered #4 combo remains.**
- **Gate evidence (re-verified this session 2026-11-11T13:25:12Z):**
  - `PYTHONPATH=. python3 -m pytest -q --tb=short tests/test_rebound_short_stop_target_missing_eth_exit_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py` → **2 passed in 0.03s**
  - `PYTHONPATH=. python3 -m pytest -q --tb=short tests/test_rebound_short_48h_time_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_missing_eth_bar_fallback_raw_risk_settlement_20261111.py` → **2 passed in 0.03s**
  - `PYTHONPATH=. python3 -m pytest -q --tb=short` → **767 passed, 12 skipped in 29.10s**
  **Next session MUST re-run full gate as blocking first action and fix FIRST if broken/regressed. Do not treat this count as fresh without re-run.**

## MATERIAL SHIPPED THIS SESSION (2026-11-11T13:17:59Z)
- **Added `tests/test_rebound_short_stop_target_missing_eth_exit_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py` (2 tests, failing-tests-first traced lock):**
  - Rebound-short STOP with long ETH hedge, entry_next_bar, `shares=600` (cap-cut context), `commission_min=1.0`, `slippage=0`, missing/unusable ETH candle at exit idx 11 (fallback `rebound_hedge_exit=2000.0` from `rebound_hedge_entry=2000.010193821759`, `rebound_hedge_size=98.098635`), long leg `target` pnl `5381.089699999996`, short leg `stopped` entry `108.99848333333333` exit `152.59954333333332` pnl `-26134.476363999995`, rebound hedge pnl `-79.47930799999152`, `total_pnl=-20832.86597199999`, `max_live_coin_notional=65399.09`, bars 6, timestamps `e6`→`e11`.
  - Rebound-short TARGET with same sizing/hedge setup, missing/unusable ETH candle at exit idx 10, short leg `target` entry `108.99848333333333` exit `99.1902865` pnl `5904.5378269999965`, rebound hedge pnl `-59.85948099999151`, `total_pnl=11225.768046000001`, `max_live_coin_notional=65399.09`, bars 5, timestamps `e6`→`e10`.
  - **Funding reconciliation (both cases, vs funding-off):** explicit per-leg `delta = -(long_coin_cost + short_coin_cost + hedge_long_cost)` via `_apply_funding_pnl` (STOP: long 3h, short 4h, hedge 4h; TARGET: long 3h, short 3h, hedge 3h), including per-leg pnl deltas and hedge exit fallback parity with funding off (no fabricated market exit).
  - **Settlement/risk_state:** rebound-leg settlement realized at close (`realized_pnl = rebound_short_pnl + rebound_hedge_pnl`), position released, gross/notionals cleared. No liquidation, no look-ahead, stopped-buy-never-opens invariant preserved by scenario design.

## MATERIAL SHIPPED (CARRY-FORWARD EVIDENCE)
- **2026-11-11T12:17:54Z (#4 progressed):** `tests/test_long_time_exit_missing_eth_exit_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py` (2 tests) — long TIME_EXIT missing ETH at exit idx, fallback hedge-exit accounting, cap_cut/commission_min/entry_next_bar/funding reconciliation and risk_state settlement traced.
- **2026-11-11T09:16:00Z (#3 COMPLETE):** 6 test files / 14 tests covering uncovered #3 edge cases (batch/sequential cuts, heterogeneous commission_min, deterministic tie-break, no top-up, settlement reconciliation, no-look-ahead).
- **2026-11-11T05:29:28Z (#2 COMPLETE, #1 COMPLETE):** rebound-short liquidation ETH bar ENTIRELY ABSENT at exit index locked; 1.25% 24h-volume sizing bypass fixed/locked.
- **#4 locks through 2026-11-11:** long/rebound-short exit/missing-ETH/hedge/funding/liquidation/settlement combo locks in dated `tests/test_*202611*.py`.

## IMPLEMENTATION STATUS (EVIDENCE-BACKED, KEY SURFACES)
`research_state/gap_analysis.md` is historical/partially stale; verify against code+tests before acting.
- **Core/spec-compliant paths:** RSI(21)<20 crash trigger, $5M 24h volume enforcement in trigger/universe/gated paths, 1.25% 24h-volume sizing when enabled, ETH hedge sizing 336h vol-ratio capped 3x with no-look-ahead (`eth_candles[:idx+1]`), rebound short after +9% target (stop +40%, target -9%, 48h), 8x spec safety stop, 120% gross-cap equal-share cuts (cuts only), portfolio bar-by-bar no-look-ahead admission with deepest-first ordering.
- **Runners/gating:** `scripts/run_portfolio.py` per-bar gating, deepest-first sort, reservation/cap-cut overlay, batch-cut pre-cutting for rebound-short multi-candidate same-bar admissions when no existing positions and total desired>cap. `run_real_campaign.py` sets RSI+ETH hedge+volume sizing+verified gates, fail-closed provenance.
- **Fail-closed:** engine raises when `require_eth_hedge=True` and no usable hedge; provenance/verified-cache guards fail closed for real paths.

## REMAINING RISKS / HEAVY FOCUS CAMPAIGN (EVIDENCE-BACKED, MANDATORY)
- **BLOCKED by environment (fail-closed):** real 283d Hyperliquid candles unavailable/unverified here. Never fabricate.
- **#1 COMPLETE. #2 COMPLETE. #3 COMPLETE. #4 COMPLETE (all locked, evidence above).**
- **NEXT CAMPAIGN (ACTIVE, PRIMARY, MANDATORY, heavy, failing-tests-first): material guardrail hardening with failing-tests-first proof — cross-leg reconciliation/settlement lock for every terminal path (stop/target/time_exit/liquidation/final_exit) on both legs (coin long/short + ETH hedge), with concrete traced expected values (fills per leg, PnL per leg, timestamps, hedge notional/side, funding, liquidation penalty where relevant, settlement reconciliation, no look-ahead), OR gated-pipeline/provenance guardrail hardening with concrete expected values.**
  - **NEXT uncovered/high-value cell (do now):** pick any terminal path × leg combo without an explicit cross-leg reconciliation/settlement lock (e.g. long-leg liquidation-vs-stop same-bar settlement with cap_cut+commission_min+entry_next_bar funding reconciliation, or rebound-short target+stop same-bar sequencing settlement on both legs, or time_exit final-exit both-leg reconciliation), prove the gap with evidence, ship a failing-tests-first regression lock (or defect fix + proof) with concrete traced values from engine math.
  - After that: continue through every remaining terminal path × leg until all are locked, then ship another MATERIAL guardrail (failing-tests-first regression lock with concrete expected values for an uncovered spec path). **Do not idle.**
- **No-idle rule:** if no concrete failing case after evidence-backed attempts, ship another MATERIAL guardrail (failing-tests-first regression lock with concrete expected values for an uncovered spec path). Do not end idle.

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

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (2026-11-11T13:25:12Z, MANDATORY, HEAVY, NON-OPTIONAL)
```text
CRASH-REBOUND-STRATEGY | 2026-11-11T13:25:12Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

Repo identity/priority (MUST DRIVE ALL WORK): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly bar-by-bar backtest engine only. NEVER claim 20s slicing, spread/L2/order-book impact.

CAMPAIGN STATUS (2026-11-11T13:25:12Z): #1 COMPLETE. #2 COMPLETE. #3 COMPLETE. #4 COMPLETE — all missing-ETH/funding/liquidation/final-exit combos locked with concrete evidence:
  - tests/test_rebound_short_48h_time_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_missing_eth_bar_fallback_raw_risk_settlement_20261111.py (2 passed) — rebound-short 48h TIME_EXIT missing-ETH fallback + funding-off delta + risk_state settlement.
  - tests/test_rebound_short_funding_all_paths.py — funding sign correctness on target/stop/liquidation/time_exit/final_exit (both legs).
  - tests/test_rebound_short_liquidation_eth_absent_at_exit_index_cap_cut_commission_min_entry_next_bar_funding_20261111.py (2 passed) — liquidation worst-price/notional/timing/penalty under cap_cut+commission_min+entry_next_bar, ETH entirely absent at exit, funding delta.
  - tests/test_rebound_short_final_exit_eth_hedge_cap_cut_commission_min_entry_next_bar_missing_final_eth_20261110.py — final-exit missing-ETH fallback + risk_state settlement + funding parity.
No uncovered #4 combo remains. Do NOT re-litigate #4.

BOTTLENECKS CLEARED (2026-11-11T13:25:12Z): only root `HANDOFF.md` is durable. No duplicate durable handoff docs. No stale `*.lock` outside `.git/`. `_probe_*` and scratch/cache dirs are not blockers. Historical docs (`research_state/gap_analysis.md`, `campaign_artifact_provenance_erratum.md`) must be verified against code+tests before use. Real 283d Hyperliquid BTC/ETH data UNAVAILABLE/UNVERIFIED (fail-closed) — NEVER fabricate. If you see any blocker (duplicate handoff, stale lock, broken gate, contradictory artifact), REMOVE/FIX it FIRST with failing-tests-first evidence before other work.

BLOCKING GATE (re-verified 2026-11-11T13:25:12Z): `PYTHONPATH=. python3 -m pytest -q --tb=short` → **767 passed, 12 skipped in 29.10s**. Run this as your FIRST action; if broken/regressed, fix before anything else. Do not treat prior counts as fresh.

LOCKED (keep ALL anchors green): all previously locked anchors plus every #4 test above. Known interpretation: `max_live_coin_notional` can exceed entry-notional cap at pressure points/across rebound leg while reservations record entry-notional cap — do NOT "fix" without concrete failing defect preserving all anchors.

#1 COMPLETE. #2 COMPLETE. #3 COMPLETE. #4 COMPLETE. NEXT CAMPAIGN ACTIVE — MATERIAL WORK REQUIRED THIS SESSION.

NEXT CAMPAIGN PRIMARY TARGET (MANDATORY, START HERE, failing-tests-first):
Material guardrail hardening with failing-tests-first proof — cross-leg reconciliation/settlement lock for every terminal path (stop/target/time_exit/liquidation/final_exit) on both legs (coin long/short + ETH hedge), OR gated-pipeline/provenance guardrail hardening with concrete expected values.

Execution requirements (non-optional):
  1) Identify the exact gap with evidence: enumerate terminal paths × legs and find any combo without an explicit cross-leg reconciliation/settlement lock with concrete traced values. Candidate first cell: long-leg liquidation-vs-stop same-bar sequencing settlement under cap_cut+commission_min+entry_next_bar with explicit per-leg funding reconciliation vs funding-off; or rebound-short target+stop same-bar sequencing settlement on both legs; or time_exit/final_exit both-leg reconciliation. Prove the gap, or state precisely why each candidate is already locked.
  2) Build deterministic, hand-traced fixture for the first uncovered cell: trace concrete expected values from engine math before asserting — coin short/long entry/exit fills, coin pnl per leg, hedge entry/size/exit fill, hedge pnl, hourly funding per held hour on every leg (long coin, short coin, long/short ETH hedge), liquidation penalty/worst-price where relevant, total/max_live/settlement, timestamps, no look-ahead.
  3) Ship failing-tests-first regression lock (dated test file, `tests/test_*202611*.py` style) — red/green; fix engine only if a concrete defect is proven.
  4) Keep ALL existing anchors green (full gate >=767 passed, 12 skipped).

AFTER first cell is locked with concrete evidence:
  - Continue through every remaining terminal path × leg until all cross-leg reconciliation/settlement locks are in place.
  - Then ship another MATERIAL guardrail (failing-tests-first regression lock with concrete expected values for an uncovered spec path).
**If the next campaign becomes fully proven locked with concrete evidence, ship another MATERIAL guardrail — no idle.**

HEAVY-WORK GUARANTEE (ENFORCED): ship >=1 MATERIAL item with concrete evidence this session. Material = spec-fidelity defect fix + failing-tests-first proof, OR failing-tests-first regression lock for an uncovered spec path with concrete traced values, OR material gated-pipeline/provenance guardrail hardening with proof. NO passive re-verification-only work, NO handoff-only edits without material progress, NO speculative refactors, NO idle.

FINAL STEPS:
  - `PYTHONPATH=. python3 -m pytest -q --tb=short` (report exact count; expect >=767 passed, 12 skipped unless legitimately changed by material work).
  - Update ONLY root `HANDOFF.md`: new UTC timestamp, exact commands/results, files changed, shipped material item(s)+concrete evidence, remaining risks, and a new timestamped heavy initial task for the next session. No other handoff files.

SPEC NON-NEGOTIABLES (never regress): hourly funding on every leg/exit; hourly liquidation worst price correct sequencing/notional/timing/penalty; stopped buy never opens rebound short; 8x safety stop; rebound `-9%/48h/+40%` anchored to executed short entry; ETH hedge every leg (336h vol ratio cap 3x), hedge sizing uses `eth_candles[:idx+1]`, entry aligned (no look-ahead); RSI(21)<20 next open deepest-first in spec path; `$5M` 24h volume in all spec-compliant gating paths; 1.25% 24h-volume sizing in spec-compliant path; equal-share cuts old+new across 120% gross cap (cuts only, never top-up); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification and on missing/insufficient required ETH hedge in spec-compliant paths.
```
