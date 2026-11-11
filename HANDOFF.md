# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-11T13:17:59Z
**Single canonical durable handoff:** ONLY this root `HANDOFF.md`. Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoff variants). `scripts/controller_progress.py`, `tests/test_controller_progress_accounting.py`, timed/session-named tests, `__pycache__`, and `_probe_*` artifacts are implementation/tests/scratch, not handoffs.

## SESSION AUDIT (2026-11-11T13:17:59Z) — MATERIAL #4 PROGRESS SHIPPED (REBOUND-SHORT STOP/TARGET MISSING-ETH EXIT RECONCILIATION LOCKED)
- **Repo identity/priorities:** `CRASH-REBOUND-STRATEGY` — crash→rebound execution fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md` (hourly bar-by-bar backtest). Never claim 20s slicing, spread/L2/order-book impact.
- **Bottlenecks checked/cleared:** only root `HANDOFF.md` exists as durable handoff (no duplicate TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoff docs). No `*.lock` outside `.git/`. `_probe_*`/cache artifacts and `research_state/.test_derive_vol_*` are scratch/gitignored — not blockers. `research_state/gap_analysis.md` and `research_state/campaign_artifact_provenance_erratum.md` are historical/partially stale — verify against code+tests before acting. Real 283d Hyperliquid BTC/ETH candles remain unavailable/unverified (fail-closed by design, environment blocker — never fabricate). **No process/session blockers preventing heavy implementation work.**
- **Campaign status:** #1 COMPLETE. #2 COMPLETE. #3 COMPLETE. **#4 ACTIVE (PRIMARY).** This session shipped a material traced regression lock for rebound-short STOP and TARGET exits with missing ETH bar at exit index, cap-cut-implied shares, commission_min, entry_next_bar, and hourly funding reconciliation on both legs. Remaining #4 coverage still requires evidence-backed locks for other uncovered missing-ETH/funding/liquidation/final-exit combos.
- **Gate evidence (re-verified this session 2026-11-11T13:17:59Z):**
  - `PYTHONPATH=. python3 -m pytest -q --tb=short tests/test_rebound_short_stop_target_missing_eth_exit_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py` → **2 passed in 0.03s**
  - `PYTHONPATH=. python3 -m pytest -q --tb=short` → **767 passed, 12 skipped in 29.20s**
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
- **#1 COMPLETE. #2 COMPLETE. #3 COMPLETE.**
- **#4 ACTIVE (PRIMARY, MANDATORY, heavy, failing-tests-first):**
  - **NEXT uncovered/high-value cell (do now): rebound-short 48h TIME_EXIT with ETH hedge missing ETH bar at exit index** under cap-cut-implied shares + commission_min + entry_next_bar with **explicit per-leg funding reconciliation vs funding-off** (coin short + long ETH hedge; include long-leg funding accounting as applicable) and risk_state settlement traced. Existing stop/48h missing-ETH cap-cut value locks exist (`tests/test_rebound_short_stop_48h_missing_eth_commission_min_cap_cut_shares_20261109.py`) but do not provide the 20261111-style explicit funding-off reconciliation proof this session added for STOP/TARGET — close that reconciliation/trace gap if uncovered, or prove already locked and move immediately to the next truly uncovered combo.
  - After that: funding accrual sign correctness on every leg/exit path not yet explicitly locked (reconciliation proof); liquidation worst-price sequencing/notional/timing/penalty under cap_cut+commission_min+entry_next_bar on uncovered combos; rebound-short final-exit missing-ETH fallback reconciliation on any uncovered cap_cut/commission_min/entry_next_bar path.
  - Ship failing-tests-first regression lock (or defect fix+proof) for the first uncovered case with concrete expected values traced from engine math (fills per leg, PnL per leg, timestamps, hedge notional/side, funding, liquidation penalty where relevant, reconciliation, no look-ahead). **If #4 proven fully locked with concrete evidence, proceed to next campaign immediately — do not idle.**
- **Next campaign (if #4 fully locked):** material guardrail hardening with failing-tests-first proof — cross-leg reconciliation/settlement lock for every terminal path (stop/target/time_exit/liquidation/final_exit) on both legs, or gated-pipeline/provenance guardrail hardening with concrete expected values.
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

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (2026-11-11T13:17:59Z, MANDATORY, HEAVY, NON-OPTIONAL)
```text
CRASH-REBOUND-STRATEGY | 2026-11-11T13:17:59Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

Repo identity/priority (MUST DRIVE ALL WORK): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly bar-by-bar backtest engine only. NEVER claim 20s slicing, spread/L2/order-book impact.

BOTTLENECKS CLEARED (2026-11-11T13:17:59Z): only root `HANDOFF.md` is durable. No duplicate durable handoff docs. No stale `*.lock` outside `.git/`. `_probe_*` and scratch/cache dirs are not blockers. Historical docs (`research_state/gap_analysis.md`, `campaign_artifact_provenance_erratum.md`) must be verified against code+tests before use. Real 283d Hyperliquid BTC/ETH data UNAVAILABLE/UNVERIFIED (fail-closed) — NEVER fabricate. If you see any blocker (duplicate handoff, stale lock, broken gate, contradictory artifact), REMOVE/FIX it FIRST with failing-tests-first evidence before other work.

BLOCKING GATE (re-verified 2026-11-11T13:17:59Z): `PYTHONPATH=. python3 -m pytest -q --tb=short` → **767 passed, 12 skipped in 29.20s**. Run this as your FIRST action; if broken/regressed, fix before anything else. Do not treat prior counts as fresh.

LOCKED (keep ALL anchors green): all previously locked anchors plus 2026-11-11T13:17:59Z `tests/test_rebound_short_stop_target_missing_eth_exit_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py` (2 tests) — rebound-short STOP/TARGET missing ETH bar at exit idx with cap-cut-implied shares (600), commission_min, entry_next_bar, fallback hedge-exit accounting, traced fills/pnls/max_live/settlement, and explicit per-leg funding reconciliation vs funding-off on both legs. Known interpretation: `max_live_coin_notional` can exceed entry-notional cap at pressure points/across rebound leg while reservations record entry-notional cap — do NOT "fix" without concrete failing defect preserving all anchors.

#1 COMPLETE. #2 COMPLETE. #3 COMPLETE. #4 ACTIVE — MATERIAL WORK REQUIRED THIS SESSION.

#4 PRIMARY TARGET (MANDATORY, START HERE, failing-tests-first):
Ship a regression lock (or defect fix + proof) for **rebound-short 48h TIME_EXIT with ETH hedge missing ETH bar at exit index** under cap-cut-implied shares + commission_min + entry_next_bar with **explicit per-leg funding reconciliation vs funding-off** and risk_state settlement traced.

Execution requirements (non-optional):
  1) Identify the exact gap with evidence: `tests/test_rebound_short_stop_48h_missing_eth_commission_min_cap_cut_shares_20261109.py` locks values for stop/48h missing-ETH cap-cut cases but does not provide 20261111-style explicit funding-off reconciliation/delta decomposition. If truly uncovered, add a dated traced test (do not duplicate existing assertions needlessly; prefer a focused reconciliation/trace lock). If already fully locked elsewhere with concrete reconciliation evidence, pick the next truly uncovered #4 combo and state why.
  2) Build deterministic, hand-traced fixture: long target hit → rebound short opens with long ETH hedge. At rebound-short 48h time-exit bar, aligned ETH candle missing/unusable → fallback hedge-exit accounting.
  3) Trace concrete expected values from engine math before asserting: coin short entry/exit fills, coin pnl, hedge entry/size, fallback hedge exit fill, hedge pnl, hourly funding on rebound short coin and on long ETH hedge for held hours, long-leg funding accounting where realized in this flow, total/max_live/settlement, timestamps, no look-ahead.
  4) Run focused test red/green as needed (fix engine only if concrete defect proven), then keep ALL existing anchors green.

AFTER first uncovered cell is locked with concrete evidence:
  - Funding accrual sign correctness on every leg/exit path not yet explicitly locked (reconciliation proof).
  - Liquidation worst-price sequencing/notional/timing/penalty under cap_cut+commission_min+entry_next_bar on uncovered combos.
  - Rebound-short final-exit missing-ETH fallback reconciliation on uncovered cap_cut/commission_min/entry_next_bar paths.
**If #4 becomes fully proven locked with concrete evidence, proceed immediately to next campaign — no idle.**

NEXT CAMPAIGN (only after #4 fully locked): material guardrail hardening with failing-tests-first proof — cross-leg reconciliation/settlement lock for every terminal path (stop/target/time_exit/liquidation/final_exit) on both legs, OR gated-pipeline/provenance guardrail hardening with concrete expected values.

HEAVY-WORK GUARANTEE (ENFORCED): ship >=1 MATERIAL item with concrete evidence this session. Material = spec-fidelity defect fix + failing-tests-first proof, OR failing-tests-first regression lock for an uncovered spec path with concrete traced values, OR material gated-pipeline/provenance guardrail hardening with proof. NO passive re-verification-only work, NO handoff-only edits without material progress, NO speculative refactors, NO idle.

FINAL STEPS:
  - `PYTHONPATH=. python3 -m pytest -q --tb=short` (report exact count; expect >=767 passed, 12 skipped unless legitimately changed by material work).
  - Update ONLY root `HANDOFF.md`: new UTC timestamp, exact commands/results, files changed, shipped material item(s)+concrete evidence, remaining risks, and a new timestamped heavy initial task for the next session. No other handoff files.

SPEC NON-NEGOTIABLES (never regress): hourly funding on every leg/exit; hourly liquidation worst price correct sequencing/notional/timing/penalty; stopped buy never opens rebound short; 8x safety stop; rebound `-9%/48h/+40%` anchored to executed short entry; ETH hedge every leg (336h vol ratio cap 3x), hedge sizing uses `eth_candles[:idx+1]`, entry aligned (no look-ahead); RSI(21)<20 next open deepest-first in spec path; `$5M` 24h volume in all spec-compliant gating paths; 1.25% 24h-volume sizing in spec-compliant path; equal-share cuts old+new across 120% gross cap (cuts only, never top-up); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification and on missing/insufficient required ETH hedge in spec-compliant paths.
```
