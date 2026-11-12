# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-12T14:10:00Z
**HEAD at audit:** `a4d8964 chore(kilo): checkpoint agent session` (working tree modified by this session: `scripts/run_campaign.py`, `scripts/run_real_campaign.py`, `tests/test_vault_fees_export_wiring_20261112.py` [new]; vault-fee core `src/metrics/vault_fees.py`, `src/metrics/campaign_metrics.py` and `tests/test_vault_fees_20261112.py`/`tests/test_vault_fees_metrics_integration_20261112.py` committed at a4d8964; no commit requested).
**Single canonical durable handoff: ONLY this root `HANDOFF.md`.** Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT variants). `scripts/controller_progress.py`, dated/session-named tests, `__pycache__`, `.pytest_cache`, root `_probe_*`/`_trace_*`/`_debug_*`/`leak_check.py`/`trace_leak.py`, and `tmp_qfv3jj4/` are implementation/tests/scratch, NOT handoffs.

## SESSION AUDIT (2026-11-12T14:05:00Z) — VAULT FEE CAMPAIGN CELLS 1–4 SHIPPED
- **Durable handoff audit (verified):** only root `HANDOFF.md` is durable (`README.md` points here). No TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoff files outside `.git`.
- **Lock/blocker audit (verified):** no `*.lock` files outside `.git/`. No contradictory artifacts.
- **Test-residue hygiene (verified):** `find research_state -maxdepth 1 -type d -name '.test_derive_vol_*' | wc -l` → **0**.
- **GAP PROOF (executed this session):** `grep -rniE 'management_fee|mgmt_fee|performance_fee|profit_fee|high.water|vault_fee' src scripts tests --include='*.py'` → **0** before implementation; `find tests -maxdepth 1 -iname '*fee*' -o -iname '*vault*'` → **0**. Spec mandates 2%/yr AUM + 10% of remaining profit above HWM — previously absent.
- **Real-data blocker — CONFIRMED REAL, DO NOT "UNBLOCK":** tracked `research_state/cache/hyperliquid_verified_283d_btceth/candles/{BTC,ETH}.json` are 6792-bar placeholders (`provenance.json`: `status:"error"`, `synthetic_check.is_synthetic:true`, `flat_series_all_bars_identical`, 1 distinct/6792). Fabricating/promoting forbidden. **283d real-data campaign stays NOT RUN.** Blocks only real-data runs.

## LAST VERIFIED GATE (2026-11-12T14:10:00Z, working tree)
- `PYTHONPATH=. python3 -m pytest -q --tb=short` → **823 passed, 12 skipped in 42.96s** (baseline 816 passed + 7 new vault-fee-export tests, zero regressions).
- New targeted: `tests/test_vault_fees_export_wiring_20261112.py` (7 passed), plus existing vault fee tests green.
- **MANDATORY FIRST ACTION next session:** re-run full gate at current HEAD/worktree and report exact count. Fix before any other work if broken/regressed.

## MATERIAL SHIPPED THIS SESSION (TRACED)
- **`src/metrics/vault_fees.py` (new, pure/deterministic):** `compute_aum_fee` = `equity * annual_rate * (hours/8760)` (default 2%/yr), capped to equity, non-positive/equity/hours/rate guarded; `compute_profit_share` = 10% of `max(0, equity - HWM)` (default), no charge at/below HWM; `accrue_vault_fees` applies per-step AUM fee on gross, then profit share on post-AUM equity above prior HWM, HWM updates only on new post-fee net peaks. Fail-safe for non-finite inputs.
- **`tests/test_vault_fees_20261112.py` (new, dated):** hand-traced 1h/24h/8760h AUM accrual; no charge on non-positive equity/hours/rate/extreme-cap; profit share above HWM only; ordering/HWM traced over multi-step series (including `120k->118k net, 130k charges only excess above 118k HWM`); edge cases (empty, zero, single-bar, loss-only, exact HWM equality, non-finite, custom initial HWM).
- **`src/metrics/campaign_metrics.py` (integration, opt-in, no double counting):** `_attach_vault_fee_metrics` adds `aum_fee_total`, `profit_share_total`, `vault_fee_total`, `gross_total_pnl`, `net_total_pnl`, `gross_final_equity`, `net_final_equity`, `vault_hwm_final` when `apply_vault_fees=True` (or fee-context kwargs). Existing trade aggregates/CSV shape unchanged by default.
- **`tests/test_vault_fees_metrics_integration_20261112.py` (new):** reconciliation against `accrue_vault_fees` on trade-derived and equity-curve series, base metrics unchanged, CSV rows include fee keys, disabled-by-default preserves shape, empty/loss-only cases.
- **`scripts/run_campaign.py` + `scripts/run_real_campaign.py` (cell 1 fee export wiring — SHIPPED):** explicit opt-in `--apply-vault-fees` flag (default off, preserves anchored result schemas) plus `--capital`; both now call `compute_campaign_metrics(..., initial_capital=<capital>, apply_vault_fees=<flag>, fee_hours_per_step=1.0)` so vault fee components (`aum_fee_total`, `profit_share_total`, `vault_fee_total`, `gross_total_pnl`, `net_total_pnl`, `gross_final_equity`, `net_final_equity`, `vault_hwm_final`) flow into campaign JSON/CSV outputs only when enabled. `build_parser()` extracted for testability; `--help` exits cleanly before any file/provenance I/O.
- **`tests/test_vault_fees_export_wiring_20261112.py` (new, dated):** 7 tests — default metric shape excludes fee keys (no regression); opt-in metrics reconcile exactly to `accrue_vault_fees` (hand-traced anchor: 1h AUM on 100k = 2000/8760; net = gross − total_fees); CSV rows emit fee keys; `build_campaign_export` carries fee metrics when present, omits when absent; both CLIs expose `--apply-vault-fees` default off.

## PRIMARY PROVABLE GAP — NEXT CAMPAIGN
Vault fee accounting core + opt-in metrics reconciliation (cell 1) are implemented and locked; **fee export wiring into `run_campaign.py`/`run_real_campaign.py` is now shipped** (opt-in `--apply-vault-fees`, default off). Remaining fee-surface work is integration depth (prove need by file search before changing): there is still no CLI/config flag surfacing fee knobs (`aum_rate_annual`, `profit_share_rate`, `fee_hours_per_step`) in the runners, and no hourly equity-curve accrual reconciliation hardening tied to `run_portfolio_simulation`. This is lower-risk wiring (not new accounting math) and must preserve existing anchored result schemas unless a concrete consumer defect is proven.

## NEXT FOCUS CAMPAIGN (FINITE, ORDERED, HEAVY — SHIP ≥1 MATERIAL ITEM/SESSION)
Repo name priority: **CRASH-REBOUND-STRATEGY** → crash→rebound fidelity to spec with auditable accounting. Execute top-down. For each cell: **prove gap** (cite search/consumer), **trace expected values**, write dated failing test, make it green.

1. ~~FEE EXPORT WIRING (DONE this session)~~ — opt-in `--apply-vault-fees`/`--capital` in `run_campaign.py`/`run_real_campaign.py` shipped with traced tests (`tests/test_vault_fees_export_wiring_20261112.py`), default outputs unchanged. Do not re-litigate.
2. **FEE CONFIG SURFACE:** expose `aum_rate_annual`, `profit_share_rate`, `fee_hours_per_step` as explicit parameters/config (CLI flags in `run_campaign.py`/`run_real_campaign.py` and pass-through to `compute_campaign_metrics`) with validation and traced defaults (2%/yr, 10%, 1h) and deterministic tests; fail-closed on invalid values (negative/NaN/non-finite rejected, no silent substitution). Prove current absence by file search first.
3. **FEE × PORTFOLIO EQUITY-CURVE RECONCILIATION HARDENING:** prove whether `run_portfolio_simulation` equity curve timestamps/granularity are the correct fee-accrual series for hourly AUM (hourly bars) and lock with a traced integration test (no look-ahead, correct step count/hours). Do not guess; cite code path (`src/backtest/engine.py`, `scripts/run_portfolio.py` equity_curve construction).
4. **ONLY IF 1–3 EXHAUSTED WITH EVIDENCE:** probe for other provably uncovered spec-accounting gaps (e.g. any untested interaction of fees with reported drawdown/equity-curve consumers) via file-search proof; otherwise ship gated-pipeline/provenance fail-closed hardening with concrete expected values. Tests-first.

**No-idle rule:** passive re-verification or handoff-only edit without a material test/fix is NOT work. If a probed cell is already covered, cite file evidence and move to next.

## IMPLEMENTATION STATUS (EVIDENCE-BACKED)
- **Core/spec-compliant:** RSI(21)<20 crash trigger, $5M 24h volume enforcement, 1.25% 24h-volume sizing, ETH hedge vol-ratio (336h) capped 3x with no-look-ahead, rebound short after +9% target (stop +40%, target -9%, 48h), 8x spec safety stop, 120% gross-cap equal-share cuts, portfolio bar-by-bar deepest-first admission, hourly funding + liquidation at worst price.
- **Vault fees (NEW):** pure 2%/yr AUM accrual + 10% profit-above-HWM accounting in `src/metrics/vault_fees.py`; opt-in reconciliation in `compute_campaign_metrics` with gross/net/fee components; traced tests locked. Default metric outputs unchanged.
- **Runners/gating:** `scripts/run_portfolio.py`, `run_real_campaign.py` (fail-closed provenance/verified gates), engine fail-closed when `require_eth_hedge=True` and no usable hedge.
- **Engine sequencing (`src/backtest/engine.py`):** liquidation > stop > target > time-exit; `hours_held_short = sidx - short_start_idx + 1`; time-exit at `>= short_bars_max` (default 48). Hedge exit fallback when aligned ETH bar missing: use `hedge_info['entry']` and re-apply exit slippage/commission.

## MATERIAL LOCKED EVIDENCE (CARRY-FORWARD — DO NOT RE-LITIGATE)
- **2026-11-12 both-hedges family** (`cap_cut+commission_min+entry_next_bar`): FINAL EXIT/STOP/TARGET/TIME_EXIT/LIQUIDATION — `tests/test_both_hedges_*_20261112.py`.
- **2026-11-12 portfolio runner both-hedged rebound loop-else final exit** — `tests/test_portfolio_both_hedges_rebound_loop_exit_cap_cut_max_live_20261112.py`.
- **2026-11-12 vault fees accounting/reconciliation** — `tests/test_vault_fees_20261112.py`, `tests/test_vault_fees_metrics_integration_20261112.py`, `src/metrics/vault_fees.py`.
- **2026-11-12 vault fee export wiring (cell 1)** — `scripts/run_campaign.py` (`--apply-vault-fees`/`--capital`, `build_parser()`), `scripts/run_real_campaign.py` (`--apply-vault-fees`), `tests/test_vault_fees_export_wiring_20261112.py` (7 passed); default outputs unchanged.
- **Stopped-buy-never-opens-rebound (portfolio E2E, real engine)** — `tests/test_portfolio_stopped_buy_real_engine_e2e.py`.
- **Locked semantics:** `max_live_coin_notional` may exceed entry-notional cap at pressure/rebound while reservations record entry-notional cap. Overall `exit_reason` may stay `target_rebound_short` while short-leg trade reason differs (assert per-leg). Loop-else final exit applies `short_pnl` only to risk_state; portfolio runner reconciles `total_pnl` into master risk_state.

## CRITICAL CONTEXT
- Spec truth: `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Test window 2025-12-20→2026-09-28 (283d), 6792 hourly bars/symbol.
- Core: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/{loader,provenance,streaming_ingest}.py`, `src/metrics/{campaign_metrics,vault_fees}.py`.
- Runners/guards: `scripts/run_portfolio.py`, `run_real_campaign.py`, `run_campaign.py`, `derive_verified_universe.py`, `fetch_hyperliquid_candles.py`, `generate_candle_coverage_gap_report.py`.

## RULES (NON-NEGOTIABLE — VIOLATION = SESSION FAILURE)
- Each session ships ≥1 material item with concrete evidence (dated test + gate count + traced values).
- Spec is truth: both legs, ETH hedge every leg, funding/liquidation on every leg/exit path, $5M gating, 1.25% sizing in spec paths, equal-share cuts old+new, stopped buy never opens rebound short.
- `backtest_simple` is low-level executor (signal assumed). Spec-compliant gating lives in `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners.
- Fail-closed: missing provenance/verification on real path → reject. Never fabricate data or results.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (2026-11-12T14:10:00Z, MANDATORY, HEAVY, NON-OPTIONAL)
```text
CRASH-REBOUND-STRATEGY | 2026-11-12T14:10:00Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

Repo identity/priority (DRIVES ALL WORK): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to crash-rebound-strategy.pdf / research_state/strategy_spec.md. Hourly bar-by-bar backtest engine only. NEVER claim 20s slicing, spread/L2/order-book impact. Mission: RSI(21)<20 crash trigger → rebound short (+9% target, +40% stop, -9% target, 48h) with ETH hedge every leg, equal-share cap cuts, no look-ahead, fail-closed gates.

NO EXPLICIT NEW DIRECTION → YOU OWN THE FINITE CAMPAIGN (MANDATORY): Continue NEXT FOCUS CAMPAIGN in HANDOFF.md (top-down). Cell 1 (fee export wiring: opt-in --apply-vault-fees/--capital in run_campaign.py/run_real_campaign.py, default outputs unchanged) is SHIPPED and locked (tests/test_vault_fees_export_wiring_20261112.py, 7 passed; full gate 823 passed, 12 skipped). Execute cell 2 next:

  CELL 2 — FEE CONFIG SURFACE: expose aum_rate_annual, profit_share_rate, fee_hours_per_step as explicit parameters/config (CLI flags in run_campaign.py/run_real_campaign.py, pass-through to compute_campaign_metrics) with validation and traced defaults (2%/yr, 10%, 1h) and deterministic tests; fail-closed on invalid values (negative/NaN/non-finite rejected, no silent substitution). Prove current absence by file search (grep run_campaign.py/run_real_campaign.py for apply_vault_fees/aum_rate/profit_share/fee_hours; confirm none exposed as CLI/config knobs) before changing.

  CELL 3 — FEE × PORTFOLIO EQUITY-CURVE RECONCILIATION HARDENING: prove whether run_portfolio_simulation equity_curve timestamps/granularity are the correct fee-accrual series for hourly AUM (hourly bars) and lock with a traced integration test (no look-ahead, correct step count/hours). Cite code path (src/backtest/engine.py, scripts/run_portfolio.py equity_curve construction). Do not guess.

  CELL 4 — ONLY IF 2–3 EXHAUSTED WITH EVIDENCE: probe other provably uncovered spec-accounting gaps via file-search proof; otherwise ship gated-pipeline/provenance fail-closed hardening with concrete expected values. Tests-first.

Do NOT stop after one cell. Do NOT end with passive re-verification or handoff-only edit. Each session ships ≥1 material item with dated test + gate count + traced values.

BOTTLENECKS (audit 2026-11-12T14:10:00Z): CLEARED. Single durable handoff = root HANDOFF.md only. No *.lock outside .git/. No contradictory handoff files. `.test_derive_vol_*` residue is 0. Working tree modified (uncommitted): scripts/run_campaign.py, scripts/run_real_campaign.py, tests/test_vault_fees_export_wiring_20261112.py [new]. HEAD a4d8964. No commit requested.

DATA BLOCKER — CONFIRMED REAL, DO NOT TRY TO UNBLOCK: tracked 6792-bar BTC/ETH under research_state/cache/hyperliquid_verified_283d_btceth/ are PLACEHOLDER (provenance status=error, synthetic_check.is_synthetic=true, flat_series_all_bars_identical, 1 distinct/6792, ~1e15 USD volume). NOT a false bottleneck. 283d campaign stays NOT RUN. Blocks ONLY real-data runs.

BLOCKING GATE (RUN FIRST): `PYTHONPATH=. python3 -m pytest -q --tb=short`
  - Last verified (2026-11-12T14:10:00Z, HEAD a4d8964 + session edits): 823 passed, 12 skipped in 42.96s.
  - Re-run NOW at current HEAD/worktree; report exact count. If broken/regressed, fix before ANYTHING else.

GAP PROOF (MANDATORY): before each change, prove the specific uncovered integration/guardrail (grep/read consumer paths) and cite evidence. Do not "improve" anchored behavior without a concrete failing defect.

LOCKED SEMANTICS (assert per traced engine behavior — zero regression):
  - max_live_coin_notional may exceed entry-notional cap at pressure/rebound while reservations record entry-notional cap — do NOT 'fix' without a concrete failing defect preserving anchors.
  - Overall exit_reason may remain target_rebound_short while short-leg trade reason differs — assert per-leg trade reasons.
  - Sequencing: liquidation > stop > target > time-exit. hours_held_short = sidx - short_start_idx + 1; time-exit at >= short_bars_max (default 48).
  - Hedge exit fallback when aligned ETH bar unavailable: engine uses hedge entry and re-applies exit slippage/commission. Hedge sizing from eth_candles[:idx+1], vol-ratio cap 3x, no look-ahead.
  - Loop-else final exit: engine applies short_pnl only to risk_state; portfolio runner reconciles total_pnl (all legs) into master risk_state.
  - Vault fees (new, locked): AUM = equity * 0.02 * hours/8760 per step; profit share = 10% * max(0, equity_after_aum - HWM), HWM on post-fee net peaks; opt-in metrics reconciliation must not alter default trade aggregates.

COVERED — DO NOT RE-LITIGATE WITHOUT CONCRETE FAILING EVIDENCE: cell 1 fee export wiring shipped; vault fee core + opt-in metrics reconciliation (20261112 tests); both-hedges FINAL EXIT/STOP/TARGET/TIME_EXIT/LIQUIDATION under cap_cut+commission_min+entry_next_bar; portfolio both-hedged rebound loop-else final exit; stopped-buy-never-opens-rebound E2E; .test_derive_vol_* fixture cleanup fixed.

EXECUTION (NON-NEGOTIABLE):
  1) GAP PROOF: cite concrete absence/need.
  2) TRACE FIRST (red): deterministic hand-traced fixtures with exact expected values.
  3) SHIP: dated failing-tests-first tests (red→green). Preserve all anchors.
  4) VERIFY: targeted + full gate `PYTHONPATH=. python3 -m pytest -q --tb=short` (exact count).
  5) CONTINUE down campaign until exhausted with evidence.

NO-IDLE / CONTINUATION: passive re-verification or handoff-only edit without material test/fix is NOT work. Each session ships ≥1 material item.

FINAL STEPS (MANDATORY):
  - Report exact commands/results and files changed.
  - Update ONLY root HANDOFF.md: new UTC timestamp, bottleneck audit, shipped material item(s)+concrete traced evidence, full-gate count, remaining risks, and a new timestamped heavy initial task for the next session.

SPEC NON-NEGOTIABLES: hourly funding on every leg/exit; hourly liquidation at worst price, correct sequencing/notional/timing/penalty; stopped buy never opens rebound short; 8x safety stop; rebound -9%/48h/+40% anchored to executed short entry; ETH hedge every leg (336h vol ratio cap 3x), hedge sizing eth_candles[:idx+1], entry aligned; RSI(21)<20 next open deepest-first; $5M 24h volume in all spec gating; 1.25% 24h-volume sizing in spec path; equal-share cuts old+new across 120% gross cap (cuts only, never top-up); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification and on missing/insufficient required ETH hedge.
```

---

**END OF HANDOFF — THIS IS THE ONLY DURABLE CONTEXT. NEXT SESSION MUST EXECUTE THE INITIAL TASK ABOVE OR FAIL. (2026-11-12T14:10:00Z)**
