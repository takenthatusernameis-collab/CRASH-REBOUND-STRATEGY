# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-12T12:30:00Z
**HEAD at audit:** `6191079 chore(kilo): checkpoint agent session` (working tree clean at audit except handoff update in progress).
**Single canonical durable handoff: ONLY this root `HANDOFF.md`.** Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT variants). `scripts/controller_progress.py`, dated/session-named tests, `__pycache__`, `.pytest_cache`, root `_probe_*`/`_trace_*`/`_debug_*`/`leak_check.py`/`trace_leak.py`, and `tmp_qfv3jj4/` are implementation/tests/scratch, NOT handoffs.

## SESSION AUDIT (2026-11-12T12:30:00Z) — BOTTLENECKS CLEARED, GATE GREEN
- **Durable handoff audit (verified):** only root `HANDOFF.md` is durable (`README.md` points here; not a handoff). No TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoff files outside `.git`.
- **Lock/blocker audit (verified):** no `*.lock` files outside `.git/`. No contradictory artifacts.
- **Handoff staleness reconciled:** refreshed from prior `99fb03e`/`12:20Z` state to current HEAD `6191079` with re-verified evidence.
- **Test-residue noise CLEARED:** removed leftover `research_state/.test_derive_vol_*` directories (9 found; deleted). None remain.
- **Real-data blocker — CONFIRMED REAL, DO NOT "UNBLOCK":** tracked `research_state/cache/hyperliquid_verified_283d_btceth/candles/{BTC,ETH}.json` are 6792-bar placeholders: `provenance.json` reports `status:"error"`, `synthetic_check.is_synthetic:true`, `reason:"flat_series_all_bars_identical"` (1 distinct signature/6792 bars), absurd volume (~1e15 USD). Fabricating/promoting violates fail-closed rules. **283d real-data campaign stays NOT RUN.** Blocks only real-data runs; engine/spec/fee-accounting work is unblocked.

## LAST VERIFIED GATE (HEAD `6191079`, AFTER BOTTLENECK CLEANUP)
- `PYTHONPATH=. python3 -m pytest -q --tb=short` → **798 passed, 12 skipped in 42.47s** (2026-11-12T12:30:00Z). **MANDATORY FIRST ACTION next session:** re-run at current HEAD and report exact count. Fix before any other work if broken/regressed.

## PRIMARY PROVABLE GAP — VAULT FEE STRUCTURE (UNIMPLEMENTED / UNTESTED)
Spec truth (`research_state/strategy_spec.md:62`): *"Management/fees as described: 2% a year on assets and 10% of remaining profit (typical vault fee structure mentioned)."*
- **Proof of absence (re-run before starting):** `grep -rniE 'management_fee|mgmt_fee|performance_fee|profit_fee|high.water|vault_fee' src scripts tests --include='*.py'` → **0 matches**. `find tests -maxdepth 1 -iname '*fee*' -o -iname '*vault*'` → none. No module in `src/metrics/` or `src/strategy/` applies 2%/yr AUM charge or 10% profit share. This is a bounded, hand-tracable accounting gap requiring NEW code + deterministic traced tests (not re-verification).

## NEXT FOCUS CAMPAIGN (FINITE, ORDERED, HEAVY — SHIP ≥1 MATERIAL ITEM/SESSION)
Work top-down. For each cell: **prove gap** (cite search), **hand-trace expected values from spec math**, write dated failing test, make it green. Continue until exhausted with file evidence. Do NOT stop after one cell if more uncovered cells remain.
1. **VAULT AUM FEE (2%/yr) — implement + lock.** Add pure, testable accrual (e.g. `src/metrics/vault_fees.py`): per-bar fee = `equity * 0.02 * (hours_elapsed / 8760)` using campaign bar spacing (hourly). Deterministic fixtures; exact accrual over known horizons (1h, 24h, 8760h); never charge non-positive equity.
2. **PROFIT SHARE (10% above HWM) — implement + lock.** 10% of equity increase over prior peak (high-water mark); no charge when equity ≤ HWM; HWM updates only on new peaks; document and lock spec-faithful ordering with AUM fee via traced values.
3. **FEE × METRICS RECONCILIATION — lock.** Ensure `campaign_metrics` gross/net account for fees without double counting; `total_pnl`/attribution/leg_breakdown reconcile net-of-fee; CSV/JSON surfaces expose fee components with concrete expected values.
4. **FEE EDGE CASES — lock.** Empty/zero-equity campaign, single-bar, loss-only path (HWM never exceeded → zero profit share), exact HWM-equality boundary, sub-hourly/irregular spacing guard, non-finite guard.
5. **ONLY IF 1–4 EXHAUSTED WITH EVIDENCE:** return to engine/portfolio reconciliation cells that remain provably uncovered (prove by file search first; 2026-11-12 portfolio both-hedged loop-exit and all `cap_cut+commission_min+entry_next_bar` terminal families are already locked — do not re-litigate). Otherwise ship gated-pipeline/provenance fail-closed hardening with concrete expected values. Still failing-tests-first.

**No-idle rule:** passive re-verification or handoff-only edit without a material test/fix is NOT work. If a probed cell is already locked, cite file evidence and move to next.

## IMPLEMENTATION STATUS (EVIDENCE-BACKED)
- **Core/spec-compliant:** RSI(21)<20 crash trigger, $5M 24h volume enforcement, 1.25% 24h-volume sizing, ETH hedge vol-ratio (336h) capped 3x with no-look-ahead, rebound short after +9% target (stop +40%, target -9%, 48h), 8x spec safety stop, 120% gross-cap equal-share cuts (cuts only), portfolio bar-by-bar deepest-first admission, hourly funding + liquidation at worst price.
- **Runners/gating:** `scripts/run_portfolio.py` (per-bar gating/reservation/cap-cut), `run_real_campaign.py` (fail-closed provenance/verified gates), engine fail-closed when `require_eth_hedge=True` and no usable hedge.
- **Engine sequencing (`src/backtest/engine.py`):** liquidation > stop > target > time-exit; `hours_held_short = sidx - short_start_idx + 1`; time-exit at `>= short_bars_max` (default 48). Hedge exit fallback when aligned ETH bar missing at exit index: use `hedge_info['entry']` and re-apply exit slippage/commission.
- **NOT IMPLEMENTED (campaign above):** vault management fee (2%/yr AUM) and profit share (10% above HWM) — confirmed 0 references.

## MATERIAL LOCKED EVIDENCE (CARRY-FORWARD — DO NOT RE-LITIGATE)
- **2026-11-12 both-hedges family** (`cap_cut+commission_min+entry_next_bar`): FINAL EXIT (aligned + missing-ETH-at-final-bar rebound fallback), STOP, TARGET, TIME_EXIT, LIQUIDATION — `tests/test_both_hedges_*_20261112.py`.
- **2026-11-12 portfolio runner both-hedged rebound loop-else final exit** — `tests/test_portfolio_both_hedges_rebound_loop_exit_cap_cut_max_live_20261112.py` (per-leg PnL/funding, max_live reservation 6540 vs 6000 entry, equal-share cut 6000 each, risk_state settlement 1166.4, final-state release).
- **Stopped-buy-never-opens-rebound (portfolio E2E, real engine)** — `tests/test_portfolio_stopped_buy_real_engine_e2e.py`.
- **2026-11-11:** 48th-bar liq/stop/target precedence & boundaries; RSI-trigger batch/sequential cuts; heterogeneous commission_min; deterministic tie-break; no top-up; settlement reconciliation; no-look-ahead (#3); 1.25% sizing bypass fixed/locked.
- **Locked semantics:** `max_live_coin_notional` may exceed entry-notional cap at pressure/rebound while reservations record entry-notional cap (do NOT "fix" without a concrete failing defect). Overall `exit_reason` may stay `target_rebound_short` while short-leg trade reason differs (assert per-leg). Loop-else final exit applies `short_pnl` only to risk_state; portfolio runner reconciles `total_pnl` (all legs) into master risk_state.

## CRITICAL CONTEXT
- Spec truth: `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Test window 2025-12-20→2026-09-28 (283d), 6792 hourly bars/symbol.
- Core: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/{loader,provenance,streaming_ingest}.py`, `src/metrics/campaign_metrics.py`.
- Runners/guards: `scripts/run_portfolio.py`, `run_real_campaign.py`, `run_campaign.py`, `derive_verified_universe.py`, `fetch_hyperliquid_candles.py`, `generate_candle_coverage_gap_report.py`.

## RULES (NON-NEGOTIABLE — VIOLATION = SESSION FAILURE)
- Each session ships ≥1 material item with concrete evidence (dated test + gate count + traced values).
- Spec is truth: both legs, ETH hedge every leg, funding/liquidation on every leg/exit path, $5M gating, 1.25% sizing in spec paths, equal-share cuts old+new, stopped buy never opens rebound short.
- `backtest_simple` is low-level executor (signal assumed). Spec-compliant gating lives in `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners.
- Fail-closed: missing provenance/verification on real path → reject. Never fabricate data or results.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (2026-11-12T12:30:00Z, MANDATORY, HEAVY, NON-OPTIONAL)
```text
CRASH-REBOUND-STRATEGY | 2026-11-12T12:30:00Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

Repo identity/priority (DRIVES ALL WORK): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to crash-rebound-strategy.pdf / research_state/strategy_spec.md. Hourly bar-by-bar backtest engine only. NEVER claim 20s slicing, spread/L2/order-book impact. Mission: RSI(21)<20 crash trigger → rebound short (+9% target, +40% stop, -9% target, 48h) with ETH hedge every leg, equal-share cap cuts, no look-ahead, fail-closed gates.

NO EXPLICIT NEW DIRECTION → YOU OWN THE FINITE CAMPAIGN (MANDATORY): User gave no feature/direction. The single highest-value, PROVABLY-UNCOVERED spec surface is VAULT FEE STRUCTURE (spec: 2%/yr on assets + 10% of remaining profit). ZERO implementation/tests (prove: `grep -rniE 'management_fee|mgmt_fee|performance_fee|profit_fee|high.water|vault_fee' src scripts tests --include='*.py'` → 0; `find tests -maxdepth 1 -iname '*fee*' -o -iname '*vault*'` → none). Execute cells 1→4 in order in HANDOFF.md NEXT FOCUS CAMPAIGN: (1) 2%/yr AUM accrual, (2) 10% profit share above HWM, (3) fee×metrics reconciliation, (4) fee edge cases. Do NOT stop after one cell. Do NOT end with passive re-verification or handoff-only edit.

BOTTLENECKS (audit 2026-11-12T12:30:00Z, HEAD 6191079): CLEARED. Single durable handoff = root HANDOFF.md only. No *.lock outside .git/. No contradictory handoff files. .test_derive_vol_* residue removed.

DATA BLOCKER — CONFIRMED REAL, DO NOT TRY TO UNBLOCK: tracked 6792-bar BTC/ETH under research_state/cache/hyperliquid_verified_283d_btceth/ are PLACEHOLDER (provenance status=error, synthetic_check.is_synthetic=true, flat_series_all_bars_identical, 1 distinct/6792, ~1e15 USD volume). NOT a false bottleneck. 283d campaign stays NOT RUN. Blocks ONLY real-data runs — fee work unblocked.

BLOCKING GATE (RUN FIRST): `PYTHONPATH=. python3 -m pytest -q --tb=short`
  - Last verified (2026-11-12T12:30:00Z, HEAD 6191079): 798 passed, 12 skipped in 42.47s.
  - Re-run NOW at current HEAD; report exact count. If broken/regressed, fix before ANYTHING else.

GAP PROOF (MANDATORY FIRST STEP): run the grep/find above and cite concrete absence. If a fee surface somehow exists, document and move to next uncovered campaign cell. Then proceed to cell 1.

LOCKED SEMANTICS (assert per traced engine behavior — zero regression):
  - max_live_coin_notional may exceed entry-notional cap at pressure/rebound while reservations record entry-notional cap — do NOT 'fix' without a concrete failing defect preserving anchors.
  - Overall exit_reason may remain target_rebound_short while short-leg trade reason differs in traces — assert per-leg trade reasons.
  - Sequencing: liquidation > stop > target > time-exit. hours_held_short = sidx - short_start_idx + 1; time-exit at >= short_bars_max (default 48).
  - Hedge exit fallback when aligned ETH bar unavailable: engine uses hedge entry and re-applies exit slippage/commission. Hedge sizing from eth_candles[:idx+1], vol-ratio cap 3x, no look-ahead.
  - Loop-else final exit: engine applies short_pnl only to risk_state; portfolio runner reconciles total_pnl (all legs) into master risk_state.

COVERED — DO NOT RE-LITIGATE WITHOUT CONCRETE FAILING EVIDENCE: #1–#4 complete; both-hedges FINAL EXIT/STOP/TARGET/TIME_EXIT/LIQUIDATION under cap_cut+commission_min+entry_next_bar; portfolio both-hedged rebound loop-else final exit (test_portfolio_both_hedges_rebound_loop_exit_cap_cut_max_live_20261112.py); stopped-buy-never-opens-rebound E2E.

EXECUTION (NON-NEGOTIABLE):
  1) GAP PROOF: grep/find; cite file absence for fees.
  2) TRACE FIRST (red): deterministic hand-traced fixtures from spec math (AUM fee = equity * 0.02 * hours/8760; profit share = 10% * max(0, equity - HWM)); assert exact expected values, ordering, and metric reconciliation.
  3) SHIP: dated failing-tests-first tests tests/test_*202611*.py (red→green). Add pure fee module under src/metrics/. Fix existing code ONLY where a concrete defect is proven; preserve all anchors.
  4) VERIFY: targeted test(s) + full gate `PYTHONPATH=. python3 -m pytest -q --tb=short` (exact count). Keep all anchors green.
  5) CONTINUE down cells 1→4 until exhausted with evidence; then ship other MATERIAL guardrails (only with prior file-search proof of a real gap).

NO-IDLE / CONTINUATION: passive re-verification or handoff-only edit without material test/fix is NOT work. Each session ships ≥1 material item.

FINAL STEPS (MANDATORY):
  - Report exact commands/results and files changed.
  - Update ONLY root HANDOFF.md: new UTC timestamp, bottleneck audit, shipped material item(s)+concrete traced evidence, full-gate count, remaining risks, and a new timestamped heavy initial task for the next session.

SPEC NON-NEGOTIABLES: hourly funding on every leg/exit; hourly liquidation at worst price, correct sequencing/notional/timing/penalty; stopped buy never opens rebound short; 8x safety stop; rebound -9%/48h/+40% anchored to executed short entry; ETH hedge every leg (336h vol ratio cap 3x), hedge sizing eth_candles[:idx+1], entry aligned; RSI(21)<20 next open deepest-first; $5M 24h volume in all spec gating; 1.25% 24h-volume sizing in spec path; equal-share cuts old+new across 120% gross cap (cuts only, never top-up); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification and on missing/insufficient required ETH hedge.
```

---

**END OF HANDOFF — THIS IS THE ONLY DURABLE CONTEXT. NEXT SESSION MUST EXECUTE THE INITIAL TASK ABOVE OR FAIL. (2026-11-12T12:30:00Z)**
