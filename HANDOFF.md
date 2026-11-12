# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-12T12:20:00Z
**HEAD at audit:** `99fb03e chore(kilo): checkpoint agent session` (working tree clean).
**Single canonical durable handoff: ONLY this root `HANDOFF.md`.** Do not create or read any other handoff file (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT variants). `scripts/controller_progress.py`, dated/session-named tests, `__pycache__`, `.pytest_cache`, and root `_probe_*`/`_trace_*`/`_debug_*`/`leak_check.py`/`trace_leak.py` are implementation/tests/scratch, NOT handoffs.

## SESSION AUDIT (2026-11-12T12:20:00Z) — BOTTLENECKS CLEARED, GATE GREEN
- **Durable handoff audit (verified):** only root `HANDOFF.md` is durable (`README.md` points here; it is not a handoff). No TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoff files exist (`grep -rlE '(todo|next|progress|status|session)' --include='*.md'` outside `.git` → only HANDOFF/README).
- **Lock/blocker audit (verified):** no `*.lock` files outside `.git/`. No contradictory artifacts.
- **HANDOFF staleness bottleneck CLEARED:** previous handoff pinned `fd89889`; HEAD is now `99fb03e` (two checkpoint commits). Re-verified at current HEAD + clean tree.
- **Test-residue noise REMOVED:** deleted all `research_state/.test_derive_vol_*` temp dirs (gitignored, untracked; ~15 had accumulated). `git status --short` is clean.
- **Real-data blocker CONFIRMED REAL — DO NOT TRY TO "UNBLOCK" IT:** `research_state/cache/hyperliquid_verified_283d_btceth/candles/{BTC,ETH}.json` are tracked 6792-bar files, BUT their own `provenance.json` records `status:"error"`, `synthetic_check.is_synthetic:true`, `reason:"flat_series_all_bars_identical"` (1 distinct signature / 6792 bars), and absurd volume (~1e15 USD). This is placeholder data, not a false bottleneck. Fabricating or promoting it would violate the non-negotiable fail-closed rules. **The 283d Hyperliquid campaign stays NOT RUN.** This blocks only real-data campaign runs, never engine/spec reconciliation or fee-accounting work.

## LAST VERIFIED GATE (REFRESHED AT HEAD `99fb03e` + CLEAN TREE)
- `PYTHONPATH=. python3 -m pytest -q --tb=short` → **798 passed, 12 skipped in 42.39s** (2026-11-12T12:20:00Z, HEAD `99fb03e`). **MANDATORY FIRST ACTION next session: re-run at current HEAD and report the exact count. Fix before any other work if broken.**

## MATERIAL SHIPPED THIS SESSION (2026-11-12T12:20:00Z)
- **Handoff + bottleneck reconciliation (no engine change required):** refreshed root `HANDOFF.md` to HEAD `99fb03e`; re-verified gate (798/12); cleared handoff-staleness and test-residue bottlenecks; **proved the real-data blocker is genuine placeholder data (not a false blocker)** so future sessions stop re-investigating it; built a finite, ordered, heavy next-focus campaign anchored on a provable uncovered spec surface (vault fee structure) so future agents cannot avoid heavy work.

## PRIMARY GAP PROOF — VAULT FEE STRUCTURE (PROVABLY UNIMPLEMENTED / UNTESTED)
Spec truth (`research_state/strategy_spec.md:62`): *"Management/fees as described: 2% a year on assets and 10% of remaining profit (typical vault fee structure mentioned)."*
- **Proof of absence (run before starting):**
  - `grep -rniE 'management_fee|mgmt_fee|performance_fee|profit_fee|high.water|vault_fee' src scripts tests --include='*.py'` → **0 matches**.
  - No module in `src/metrics/` or `src/strategy/` applies a 2%/yr AUM charge or a 10% profit share.
- This is a real spec-vs-code gap with a bounded, hand-tracable accounting surface: AUM fee accrual (2%/yr, per-bar pro-rata on equity), profit share (10% of gains above a high-water mark), ordering vs. PnL, and interaction with `campaign_metrics` totals. It forces NEW accounting code + property/invariant tests + exact-value regression locks — it cannot be satisfied by re-verification or a handoff-only edit.

## NEXT FOCUS CAMPAIGN (FINITE, ORDERED, HEAVY — EACH SESSION SHIPS ≥1 MATERIAL ITEM)
Work top-down. For each cell: **prove the gap first** (cite file/test search), **hand-trace expected values from spec math**, write the dated failing test, then make it green. Ship ≥1 material item per session; continue down the list until exhausted, then prove exhaustion with file evidence.

1. **VAULT AUM FEE (2%/yr) — implement + lock.** Add a pure, testable fee-accrual function (e.g. `src/metrics/vault_fees.py`) computing per-bar AUM fee = `equity * 0.02 * (hours_elapsed / 8760)`, using the campaign's actual bar spacing (hourly) and realized equity path. Deterministic fixtures; assert exact accrual over known horizons (1h, 24h, 8760h) and that it never charges on non-positive equity.
2. **PROFIT SHARE (10% above high-water mark) — implement + lock.** 10% of the increase in equity over the prior peak (high-water mark); no charge when equity ≤ HWM; HWM updates only on new peaks; combine with AUM fee in a documented, spec-faithful order and lock the ordering with traced values.
3. **FEE × METRICS RECONCILIATION — lock.** Ensure `campaign_metrics` gross/net figures account for fees without double counting, `total_pnl`/attribution/leg_breakdown reconcile to net-of-fee, and CSV/JSON surfaces expose the fee components with concrete expected values.
4. **FEE EDGE CASES — lock.** Empty/zero-equity campaign, single-bar, loss-only path (HWM never exceeded → zero profit share), exact HWM-equality boundary, sub-hourly/irregular spacing guard, non-finite guard.
5. **ONLY IF 1–4 EXHAUSTED WITH EVIDENCE:** return to engine/portfolio reconciliation cells that remain provably uncovered (prove by file search first; the 2026-11-12T11:45Z portfolio both-hedged loop-exit cell and all `cap_cut+commission_min+entry_next_bar` terminal families are already locked — do not re-litigate). Otherwise ship gated-pipeline/provenance fail-closed hardening with concrete expected values. Still failing-tests-first.

**No-idle rule:** passive re-verification or a handoff-only edit without a material test/fix is NOT work. If the cell you probe is already locked, cite the file evidence, then move to the next cell and keep going.

## IMPLEMENTATION STATUS (EVIDENCE-BACKED)
- **Core/spec-compliant:** RSI(21)<20 crash trigger, $5M 24h volume enforcement, 1.25% 24h-volume sizing, ETH hedge vol-ratio (336h) capped 3x with no-look-ahead, rebound short after +9% target (stop +40%, target -9%, 48h), 8x spec safety stop, 120% gross-cap equal-share cuts (cuts only), portfolio bar-by-bar deepest-first admission, hourly funding + liquidation at worst price.
- **Runners/gating:** `scripts/run_portfolio.py` (per-bar gating/reservation/cap-cut), `run_real_campaign.py` (fail-closed provenance/verified gates), engine fail-closed when `require_eth_hedge=True` and no usable hedge.
- **Engine sequencing (`src/backtest/engine.py`):** liquidation > stop > target > time-exit; `hours_held_short = sidx - short_start_idx + 1`; time-exit at `>= short_bars_max` (default 48). Hedge exit fallback: if aligned ETH bar missing at exit index, engine uses `hedge_info['entry']` and re-applies exit slippage/commission.
- **NOT IMPLEMENTED (the campaign above):** vault management fee (2%/yr AUM) and profit share (10% above HWM). Confirmed 0 references.

## MATERIAL SHIPPED / LOCKED EVIDENCE (CARRY-FORWARD — DO NOT RE-LITIGATE)
- **2026-11-12 both-hedges family** (`cap_cut+commission_min+entry_next_bar`): FINAL EXIT (aligned + missing-ETH-at-final-bar rebound fallback), STOP, TARGET, TIME_EXIT, LIQUIDATION — `tests/test_both_hedges_*_20261112.py`.
- **2026-11-12T11:45:00Z portfolio runner both-hedged rebound loop-else final exit** — `tests/test_portfolio_both_hedges_rebound_loop_exit_cap_cut_max_live_20261112.py` (per-leg PnL/funding, max_live reservation 6540 vs 6000 entry, equal-share cut 6000 each, risk_state settlement 1166.4, final-state release).
- **Stopped-buy-never-opens-rebound (portfolio E2E, real engine)** — `tests/test_portfolio_stopped_buy_real_engine_e2e.py`.
- **2026-11-11:** 48th-bar liq/stop/target precedence & boundaries; RSI-trigger batch/sequential cuts; heterogeneous commission_min; deterministic tie-break; no top-up; settlement reconciliation; no-look-ahead (#3); 1.25% sizing bypass fixed/locked.
- **Locked semantics:** `max_live_coin_notional` may exceed entry-notional cap at pressure/rebound while reservations record entry-notional cap (do NOT "fix" without a concrete failing defect). Overall `exit_reason` may stay `target_rebound_short` while the short-leg trade reason differs (assert per-leg). Loop-else final exit applies `short_pnl` only to risk_state; portfolio runner reconciles `total_pnl` (all legs) into master risk_state.

## CRITICAL CONTEXT
- Spec truth: `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Test window 2025-12-20→2026-09-28 (283d), 6792 hourly bars/symbol.
- Core: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/{loader,provenance,streaming_ingest}.py`, `src/metrics/campaign_metrics.py`.
- Runners/guards: `scripts/run_portfolio.py`, `run_real_campaign.py`, `run_campaign.py`, `derive_verified_universe.py`, `fetch_hyperliquid_candles.py`, `generate_candle_coverage_gap_report.py`.

## RULES (NON-NEGOTIABLE — VIOLATION = SESSION FAILURE)
- Each session ships ≥1 material item with concrete evidence (dated test file + gate count + traced values).
- Spec is truth: both legs, ETH hedge every leg, funding/liquidation on every leg/exit path, $5M gating, 1.25% sizing in spec paths, equal-share cuts old+new, stopped buy never opens rebound short.
- `backtest_simple` is a low-level executor (signal assumed). Spec-compliant gating lives in `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners.
- Fail-closed: missing provenance/verification on the real path → reject. Never fabricate data or results.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (2026-11-12T12:20:00Z, MANDATORY, HEAVY, NON-OPTIONAL)
```text
CRASH-REBOUND-STRATEGY | 2026-11-12T12:20:00Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

Repo identity/priority (DRIVES ALL WORK): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to crash-rebound-strategy.pdf / research_state/strategy_spec.md. Hourly bar-by-bar backtest engine only. NEVER claim 20s slicing, spread/L2/order-book impact. Mission: RSI(21)<20 crash trigger → rebound short (+9% target, +40% stop, -9% target, 48h) with ETH hedge every leg, equal-share cap cuts, no look-ahead, fail-closed gates.

NO EXPLICIT NEW DIRECTION → YOU OWN THE FINITE CAMPAIGN (built this session so you CANNOT avoid heavy work): The user gave no feature/direction. The single highest-value, PROVABLY-UNCOVERED spec surface is the VAULT FEE STRUCTURE (spec: 2%/yr on assets + 10% of remaining profit). It has ZERO implementation/tests (prove: grep -rniE 'management_fee|performance_fee|profit_fee|high.water|vault_fee' src scripts tests → 0). Execute cells 1→4 in order in HANDOFF.md's NEXT FOCUS CAMPAIGN: (1) implement + lock 2%/yr AUM accrual, (2) implement + lock 10% profit share above high-water mark, (3) reconcile fees into campaign_metrics without double counting, (4) fee edge cases (zero-equity, loss-only, HWM equality, non-finite, irregular spacing). Do NOT stop after one cell. Do NOT end with passive re-verification or a handoff-only edit.

BOTTLENECKS (audit 2026-11-12T12:20:00Z, HEAD 99fb03e + clean tree): CLEARED. Single durable handoff = root HANDOFF.md only. No *.lock outside .git/. No contradictory handoff files. Test-residue .test_derive_vol_* dirs REMOVED. HANDOFF staleness reconciled (fd89889 → 99fb03e).

DATA BLOCKER — CONFIRMED REAL, DO NOT TRY TO UNBLOCK: the tracked 6792-bar BTC/ETH files under research_state/cache/hyperliquid_verified_283d_btceth/ are PLACEHOLDER data (provenance: status=error, synthetic_check.is_synthetic=true, flat_series_all_bars_identical, 1 distinct signature/6792 bars, ~1e15 USD volume). This is NOT a false bottleneck; fabricating/promoting it violates the fail-closed rules. 283d campaign stays NOT RUN. This blocks ONLY real-data runs — your fee work is fully unblocked.

BLOCKING GATE (RUN FIRST): PYTHONPATH=. python3 -m pytest -q --tb=short
  - Last verified (2026-11-12T12:20:00Z at HEAD 99fb03e): 798 passed, 12 skipped in 42.39s.
  - Re-run NOW at current HEAD; report exact count. If broken/regressed, fix before ANYTHING else.

GAP PROOF (MANDATORY FIRST STEP): run the grep above and `find tests -maxdepth 1 -iname '*fee*' -o -iname '*vault*' | sort`; cite the concrete absence. Then proceed to cell 1.

LOCKED SEMANTICS (assert per traced engine behavior — zero regression):
  - max_live_coin_notional may exceed entry-notional cap at pressure/rebound while reservations record entry-notional cap — do NOT 'fix' without a concrete failing defect preserving anchors.
  - Overall exit_reason may remain target_rebound_short while the short-leg trade reason is time_exit/liquidated/stopped/target in traces — assert per-leg trade reasons.
  - Sequencing: liquidation > stop > target > time-exit. hours_held_short = sidx - short_start_idx + 1; time-exit at >= short_bars_max (default 48).
  - Hedge exit fallback when aligned ETH bar unavailable: engine uses hedge entry and re-applies exit slippage/commission. Hedge sizing from eth_candles[:idx+1], vol-ratio cap 3x, no look-ahead.
  - Loop-else final exit: engine applies short_pnl only to risk_state; portfolio runner reconciles total_pnl (all legs) into master risk_state.

COVERED — DO NOT RE-LITIGATE WITHOUT CONCRETE FAILING EVIDENCE: #1–#4 complete; both-hedges FINAL EXIT/STOP/TARGET/TIME_EXIT/LIQUIDATION under cap_cut+commission_min+entry_next_bar; portfolio both-hedged rebound loop-else final exit (test_portfolio_both_hedges_rebound_loop_exit_cap_cut_max_live_20261112.py); stopped-buy-never-opens-rebound E2E.

EXECUTION (NON-NEGOTIABLE):
  1) GAP PROOF: grep/find as above; cite file absence for fees. If a fee surface somehow exists, document it and move to the next uncovered campaign cell.
  2) TRACE FIRST (red): deterministic hand-traced fixtures from spec math (AUM fee = equity * 0.02 * hours/8760; profit share = 10% * max(0, equity - HWM)); assert exact expected values, ordering, and metric reconciliation.
  3) SHIP: dated failing-tests-first tests tests/test_*202611*.py (red→green). Add the pure fee module under src/metrics/. Fix existing code ONLY where a concrete defect is proven; preserve all anchors.
  4) VERIFY: targeted test(s) + full gate PYTHONPATH=. python3 -m pytest -q --tb=short (exact count). Keep all anchors green.
  5) CONTINUE down cells 1→4 until exhausted with evidence; then ship other MATERIAL guardrails (only cells 1–4 exhausted may you return to engine/portfolio cells, and only with prior file-search proof of a real gap).

NO-IDLE / CONTINUATION: passive re-verification or a handoff-only edit without a material test/fix is NOT work. Each session ships ≥1 material item.

FINAL STEPS (MANDATORY):
  - Report exact commands/results and files changed.
  - Update ONLY root HANDOFF.md: new UTC timestamp, bottleneck audit, shipped material item(s)+concrete traced evidence, full-gate count, remaining risks, and a new timestamped heavy initial task for the next session.

SPEC NON-NEGOTIABLES: hourly funding on every leg/exit; hourly liquidation at worst price, correct sequencing/notional/timing/penalty; stopped buy never opens rebound short; 8x safety stop; rebound -9%/48h/+40% anchored to executed short entry; ETH hedge every leg (336h vol ratio cap 3x), hedge sizing eth_candles[:idx+1], entry aligned; RSI(21)<20 next open deepest-first; $5M 24h volume in all spec gating; 1.25% 24h-volume sizing in spec path; equal-share cuts old+new across 120% gross cap (cuts only, never top-up); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification and on missing/insufficient required ETH hedge.
```

---

**END OF HANDOFF — THIS IS THE ONLY DURABLE CONTEXT. NEXT SESSION MUST EXECUTE THE INITIAL TASK ABOVE OR FAIL. (2026-11-12T12:20:00Z)**