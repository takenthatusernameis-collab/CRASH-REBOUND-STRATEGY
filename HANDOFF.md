# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-12T19:16:39Z
**HEAD at audit:** `4914d84 chore: capture completed workflow run diagnostics` (working tree: 2 new untracked dated test files added this session — CELL 4b + 4d; **no commit requested**).
**Single canonical durable handoff: ONLY this root `HANDOFF.md`.** Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT variants). `scripts/controller_progress.py`, dated/session-named tests, `__pycache__`, `.pytest_cache`, root `_probe_*`/`_trace_*`/`_debug_*`/`leak_check.py`/`trace_leak.py`, and `tmp_qfv3jj4/` are implementation/tests/scratch, NOT handoffs.

## SESSION AUDIT (2026-11-12T19:16:39Z) — GATE RE-VERIFIED GREEN (876 passed, 12 skipped)
- **Durable handoff audit (verified):** only root `HANDOFF.md` is durable (`README.md` points here). No TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoff files outside `.git`.
- **Lock/blocker audit (verified):** no `*.lock` files outside `.git/`. No contradictory handoff artifacts. `.test_derive_vol_*` residue is 0. Bottlenecks CLEARED — nothing idle-blocked; no multi-session contention.
- **Real-data blocker — CONFIRMED REAL, DO NOT "UNBLOCK":** tracked `research_state/cache/hyperliquid_verified_283d_btceth/candles/{BTC,ETH}.json` are 6792-bar placeholders (`research_state/cache/hyperliquid_verified_283d_btceth/provenance.json`: per-symbol `status:"error"`, `synthetic_check.is_synthetic:true`, `flat_series_all_bars_identical`, 1 distinct/6792; `ready_for_real_campaign:false`). Fabricating/promoting forbidden. **283d real-data campaign stays NOT RUN.** Blocks only real-data runs. All spec-unit and engine tests run on fixtures and remain fully executable.
- **Test-env note (verified):** system `python3` had NO pytest; installed `pytest numpy pandas requests` per `.github/workflows/strategy-tests.yml` (`python -m pip install --break-system-packages`). Gate command below is the canonical one.

## LAST VERIFIED GATE (2026-11-12T19:16:39Z, working tree = HEAD + 2 new test files)
- `PYTHONPATH=. python3 -m pytest -q --tb=short` → **876 passed, 12 skipped in 35.03s** (baseline 870 → 876; +6 new tests, zero regressions).
- **MANDATORY FIRST ACTION next session:** re-run full gate at current HEAD/worktree and report exact count. Fix before any other work if broken/regressed.

## MATERIAL SHIPPED THIS SESSION (CELL 4, TRACED, mutation-verified — NOT yet committed)
- **Cell 4d (LONG LIQUIDATION vs FUNDING same-bar ordering — DONE):** `tests/test_long_liquidation_funding_same_bar_ordering_20261112.py` (3 tests). Gap proof (file-search verified): the long-liq branch in `src/backtest/engine.py` computes `hours_held_liq = idx - start_idx + 1` and subtracts `_apply_funding_pnl(entry_px*shares, hours_held_liq, rate, 'long')` in the SAME branch as the penalty; existing liq tests assert the penalty but NOT the funding delta / per-hour boundary. Locked traced values: entry=100, liq threshold 94.0 (maint 5%+buffer 1%), rate 0.01%/h, penalty 0.5%: liq at ENTRY bar → hours=1 → funding 0.01 → pnl -10.51; liq one bar later → hours=2 → funding 0.02 → pnl -10.52; cross-case delta = exactly one hour (0.01). **Mutation-verified non-vacuous:** setting `hours_held_liq=0` fails all 3 (restore clean, `git diff src/` empty).
- **Cell 4b (8x SPEC SAFETY STOP × rebound-short same-bar sequencing — DONE):** `tests/test_engine_spec_safety_stop_same_bar_rebound_short_sequencing_20261112.py` (3 tests). Gap proof (file-search verified): same-bar sequencing locks exist for a PLAIN stop (`test_long_same_bar_stop_target_sequencing_20261108.py`) and for the SHORT leg (`test_rebound_short_attribution_and_risk_state_20261107.py`), but none drives the SPEC 8x safety stop (`use_spec_safety_stop=True`, stop=entry*(1-8*range_ratio)) through a same-bar stop+target collision. Locked invariant: the spec safety stop sits structurally below the 6% liq threshold, so a same-bar stop+target collision resolves to LIQUIDATION (worst price) and a liquidated/stopped buy NEVER opens a rebound short; if a stop is above liq (wide-range case) the STOP beats target on the same bar, still no rebound short; control case (target only) still opens the rebound short. Traced: stop 86.0 (<94) + low 85 + high 110 → liquidated @85.0, bars 2, no short; stop 96.0 (>94) + low 95 + high 110 → stopped @96.0, hours 2, funding 0.02, pnl -4.02, no short; stop 96.0 + low 98 + high 110 → target_rebound_short (control).

## PRIOR SHIPPED (TRACED, committed on a5bac9b or earlier — DO NOT RE-LITIGATE)
- Cell 2 fee config surface (38 tests) `tests/test_vault_fees_config_surface_20261112.py`.
- Cell 3 fee elapsed-hours `src/metrics/vault_fees.py::elapsed_hours_from_timestamps` + `campaign_metrics.py` `fee_use_timestamp_hours` + `--fee-hours-from-timestamps` (both runners) + real-runner knob-drop fix; `tests/test_vault_fees_elapsed_hours_20261112.py` (9 tests).
- Vault fee core `src/metrics/vault_fees.py` + opt-in reconciliation; cell 1 fee export wiring; both-hedges FINAL EXIT/STOP/TARGET/TIME_EXIT/LIQUIDATION family; portfolio both-hedged rebound loop-else final exit; stopped-buy-never-opens-rebound E2E.

## NEXT FOCUS CAMPAIGN (FINITE, ORDERED, HEAVY — SHIP ≥1 MATERIAL ITEM/SESSION)
Repo name priority: **CRASH-REBOUND-STRATEGY** → crash→rebound fidelity to spec with auditable accounting. Execute top-down. For each cell: **prove gap** (cite search/consumer), **trace expected values**, write dated failing test, make it green, mutation-verify non-vacuous, run full gate.

1. **CELL 5 — CONTINUE PROBING UNCOVERED SPEC-ACCOUNTING/GUARDRAIL GAPS (file-search proof required):** candidates NOT yet proven (do not assume; cite `grep -rn` of tests/ and consumers): (a) hourly FUNDING on the ETH hedge leg when the hedge exits via the loop-else FINAL EXIT (not stop/target/time/liq) — is there a test asserting hedge-leg funding on the loop-else final-exit path at the last bar? (b) liquidation at the 48h rebound-short boundary: does funding accrue for the full 48h AND the liquidation penalty on the same boundary bar (interaction of `hours_held_short` cap with liq)? (c) equal-share cap cuts when a rebound-short admission coexists with an existing long that is mid-flight on the SAME bar (reservation overlay vs actual cap cut precedence). For each: prove presence/absence, trace exact values, dated failing test, green. If a candidate is already covered, cite the file and move on.
2. **CELL 6 — ONLY IF 5 EXHAUSTED WITH EVIDENCE:** gated-pipeline / provenance fail-closed hardening with concrete expected values (e.g. missing/insufficient ETH hedge rejection messages, provenance status=error rejection on the real path), tests-first with traced values.

**No-idle rule:** passive re-verification or handoff-only edit without a material test/fix is NOT work. If a probed cell is already covered, cite file evidence and move to next.

## IMPLEMENTATION STATUS (EVIDENCE-BACKED)
- **Core/spec-compliant:** RSI(21)<20 crash trigger, $5M 24h volume enforcement, 1.25% 24h-volume sizing, ETH hedge vol-ratio (336h) capped 3x with no-look-ahead, rebound short after +9% target (stop +40%, target -9%, 48h), 8x spec safety stop, 120% gross-cap equal-share cuts, portfolio bar-by-bar deepest-first admission, hourly funding + liquidation at worst price.
- **Vault fees:** pure 2%/yr AUM + 10% profit-above-HWM in `src/metrics/vault_fees.py`; opt-in reconciliation in `compute_campaign_metrics`. Default outputs unchanged.
- **Runners/gating:** `scripts/run_portfolio.py`, `run_real_campaign.py` (fail-closed provenance/verified gates), engine fail-closed when `require_eth_hedge=True` and no usable hedge.

## MATERIAL LOCKED EVIDENCE (CARRY-FORWARD — DO NOT RE-LITIGATE)
- **2026-11-12 liquidation funding same-bar ordering (cell 4d)** — `tests/test_long_liquidation_funding_same_bar_ordering_20261112.py` (3 tests; mutation-verified).
- **2026-11-12 spec safety stop × rebound-short same-bar sequencing (cell 4b)** — `tests/test_engine_spec_safety_stop_same_bar_rebound_short_sequencing_20261112.py` (3 tests).
- **2026-11-12 vault fees accounting/reconciliation** — `tests/test_vault_fees_20261112.py`, `tests/test_vault_fees_metrics_integration_20261112.py`, `src/metrics/vault_fees.py`.
- **2026-11-12 vault fee config surface (cell 2)** — `tests/test_vault_fees_config_surface_20261112.py` (38 tests).
- **2026-11-12 vault fee elapsed-hours (cell 3)** — `src/metrics/vault_fees.py::elapsed_hours_from_timestamps`, `campaign_metrics.py::_attach_vault_fee_metrics` (`fee_use_timestamp_hours`), `tests/test_vault_fees_elapsed_hours_20261112.py`.
- **2026-11-12 both-hedges family** (`cap_cut+commission_min+entry_next_bar`): FINAL EXIT/STOP/TARGET/TIME_EXIT/LIQUIDATION — `tests/test_both_hedges_*_20261112.py`.
- **2026-11-12 portfolio runner both-hedged rebound loop-else final exit** — `tests/test_portfolio_both_hedges_rebound_loop_exit_cap_cut_max_live_20261112.py`.
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

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (2026-11-12T19:16:39Z, MANDATORY, HEAVY, NON-OPTIONAL)
```text
CRASH-REBOUND-STRATEGY | 2026-11-12T19:16:39Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

Repo identity/priority (DRIVES ALL WORK): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to crash-rebound-strategy.pdf / research_state/strategy_spec.md. Hourly bar-by-bar backtest engine only. NEVER claim 20s slicing, spread/L2/order-book impact. Mission: RSI(21)<20 crash trigger → rebound short (+9% target, +40% stop, -9% target, 48h) with ETH hedge every leg, equal-share cap cuts, no look-ahead, fail-closed gates.

NO EXPLICIT NEW DIRECTION → YOU OWN THE FINITE CAMPAIGN (MANDATORY): Continue NEXT FOCUS CAMPAIGN in HANDOFF.md (top-down). Shipped this session (NOT yet committed): cell 4d liquidation-vs-funding same-bar ordering (tests/test_long_liquidation_funding_same_bar_ordering_20261112.py, 3, mutation-verified) and cell 4b spec-safety-stop × rebound-short same-bar sequencing (tests/test_engine_spec_safety_stop_same_bar_rebound_short_sequencing_20261112.py, 3). Full gate last verified 876 passed, 12 skipped in 35.03s (HEAD 4914d84 + 2 new test files). Execute CELL 5 now:

  CELL 5 — CONTINUE PROBING UNCOVERED SPEC-ACCOUNTING/GUARDRAIL GAPS: For EACH candidate below, FIRST prove presence/absence via file search (cite grep -rn of tests/ and consumers/), then trace exact expected values, write a dated failing test, make green, mutation-verify:
    (a) ETH hedge-leg FUNDING on the loop-else FINAL EXIT path (not stop/target/time/liq) — does a test assert hedge funding at the last-bar final exit? grep engine.py loop-else final-exit hedge funding + tests/test_both_hedges_final_exit_*.py; if no funding assertion on that path, add a dated failing test with traced values.
    (b) Rebound-short LIQUIDATION at the 48h boundary — interaction of the 48h `hours_held_short` cap with the liquidation penalty on the same boundary bar. grep engine.py short-loop liq branch + `rebound_short_time_exit_bars`; if unproven, add a dated failing test (liq on the 48th bar: full 48h funding + penalty) with traced values.
    (c) Equal-share cap cuts when a rebound-short admission coexists with an existing mid-flight long on the SAME bar (reservation overlay vs actual cap cut precedence). grep portfolio runner reservation/apply_cap_cuts paths + tests/test_portfolio_*reservation*.py; if unproven, add a dated failing test with traced values.
  If a candidate is already covered, cite the file evidence and move on; do NOT re-litigate anchored behavior. If all are covered, ship gated-pipeline/provenance fail-closed hardening with concrete expected values (tests-first).

Do NOT stop after one cell. Do NOT end with passive re-verification or handoff-only edit. Each session ships ≥1 material item with dated test + gate count + traced values.

BOTTLENECKS (audit 2026-11-12T19:16:39Z): CLEARED. Single durable handoff = root HANDOFF.md only. No *.lock outside .git/. No contradictory handoff files. `.test_derive_vol_*` residue is 0. No commit requested. All gaps are explicit campaign cells with proof-of-absence requirements. Nothing is idle-blocked; the only hard blocker is real data, which is NOT a bottleneck to fix.

DATA BLOCKER — CONFIRMED REAL, DO NOT TRY TO UNBLOCK: tracked 6792-bar BTC/ETH under research_state/cache/hyperliquid_verified_283d_btceth/ are PLACEHOLDER (provenance per-symbol status=error, synthetic_check.is_synthetic=true, flat_series_all_bars_identical, 1 distinct/6792, ready_for_campaign=false). NOT a false bottleneck. 283d campaign stays NOT RUN. Blocks ONLY real-data runs. All spec-unit and engine tests run on fixtures and remain fully executable.

BLOCKING GATE (RUN FIRST): `PYTHONPATH=. python3 -m pytest -q --tb=short`
  - Last verified (2026-11-12T19:16:39Z, HEAD 4914d84 + 2 new test files): 876 passed, 12 skipped in 35.03s.
  - Re-run NOW at current HEAD/worktree; report exact count. If broken/regressed, fix before ANYTHING else.
  - Test env: install deps first if missing — `python -m pip install --break-system-packages pytest numpy pandas requests` (per .github/workflows/strategy-tests.yml).

GAP PROOF (MANDATORY): before each change, prove the specific uncovered integration/guardrail (grep/read consumer paths) and cite evidence. Do not "improve" anchored behavior without a concrete failing defect.

LOCKED SEMANTICS (assert per traced engine behavior — zero regression):
  - max_live_coin_notional may exceed entry-notional cap at pressure/rebound while reservations record entry-notional cap — do NOT 'fix' without a concrete failing defect preserving anchors.
  - Overall exit_reason may remain target_rebound_short while short-leg trade reason differs — assert per-leg trade reasons.
  - Sequencing: liquidation > stop > target > time-exit. hours_held_short = sidx - short_start_idx + 1; time-exit at >= short_bars_max (default 48).
  - Long-leg liq funding: hours_held_liq = idx - start_idx + 1, subtracted in the SAME branch as the penalty (cell 4d lock). Spec 8x safety stop sits below the 6% liq threshold → same-bar stop+target collision resolves to liquidation and never opens a rebound short (cell 4b lock).
  - Hedge exit fallback when aligned ETH bar unavailable: engine uses hedge entry and re-applies exit slippage/commission. Hedge sizing from eth_candles[:idx+1], vol-ratio cap 3x, no look-ahead.
  - Loop-else final exit: engine applies short_pnl only to risk_state; portfolio runner reconciles total_pnl (all legs) into master risk_state.
  - Vault fees (locked): AUM = equity * rate * hours/8760 per step; profit share = 10% * max(0, equity_after_aum - HWM), HWM on post-fee net peaks; opt-in metrics reconciliation must not alter default trade aggregates. Fee hours: flat fee_hours_per_step (default 1.0) unless fee_use_timestamp_hours=True (elapsed hours between equity-curve timestamps).

COVERED — DO NOT RE-LITIGATE WITHOUT CONCRETE FAILING EVIDENCE: cell 1 fee export wiring; vault fee core + opt-in metrics reconciliation; cell 2 fee config surface (38 tests); cell 3 fee elapsed-hours reconciliation + real-runner knob-drop fix; cell 4b spec safety-stop × rebound-short same-bar sequencing (3 tests); cell 4d liquidation-vs-funding same-bar ordering (3 tests); both-hedges FINAL EXIT/STOP/TARGET/TIME_EXIT/LIQUIDATION under cap_cut+commission_min+entry_next_bar; portfolio both-hedged rebound loop-else final exit; stopped-buy-never-opens-rebound E2E; (a) time-exit hedge funding; (c) no-top-up cap cuts; .test_derive_vol_* fixture cleanup.

EXECUTION (NON-NEGOTIABLE):
  1) GAP PROOF: cite concrete absence/need.
  2) TRACE FIRST (red): deterministic hand-traced fixtures with exact expected values.
  3) SHIP: dated failing-tests-first tests (red→green). Preserve all anchors. Mutation-verify non-vacuous.
  4) VERIFY: targeted + full gate `PYTHONPATH=. python3 -m pytest -q --tb=short` (exact count).
  5) CONTINUE down campaign until exhausted with evidence.

NO-IDLE / CONTINUATION: passive re-verification or handoff-only edit without material test/fix is NOT work. Each session ships ≥1 material item.

FINAL STEPS (MANDATORY):
  - Report exact commands/results and files changed.
  - Update ONLY root HANDOFF.md: new UTC timestamp, bottleneck audit, shipped material item(s)+concrete traced evidence, full-gate count, remaining risks, and a new timestamped heavy initial task for the next session.

SPEC NON-NEGOTIABLES: hourly funding on every leg/exit; hourly liquidation at worst price, correct sequencing/notional/timing/penalty; stopped buy never opens rebound short; 8x safety stop; rebound -9%/48h/+40% anchored to executed short entry; ETH hedge every leg (336h vol ratio cap 3x), hedge sizing eth_candles[:idx+1], entry aligned; RSI(21)<20 next open deepest-first; $5M 24h volume in all spec gating; 1.25% 24h-volume sizing in spec path; equal-share cuts old+new across 120% gross cap (cuts only, never top-up); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification and on missing/insufficient required ETH hedge.
```

---

**END OF HANDOFF — THIS IS THE ONLY DURABLE CONTEXT. NEXT SESSION MUST EXECUTE THE INITIAL TASK ABOVE OR FAIL. (2026-11-12T19:16:39Z)**