# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-12T23:30:00Z
**HEAD at audit:** `23b454f chore(kilo): checkpoint agent session`; working tree clean (`git status --short` empty).
**Gate re-verified at current HEAD/worktree (2026-11-12T23:30:00Z):** `PYTHONPATH=. python3 -m pytest -q --tb=short` → **905 passed, 12 skipped in 34.86s**, GREEN. Count unchanged from the prior audit, so the previous session's claim holds and nothing regressed across the checkpoint commits.
**Single canonical durable handoff: ONLY this root `HANDOFF.md`.** Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT variants). `scripts/controller_progress.py`, dated/session-named tests, `__pycache__`, `.pytest_cache`, root `_probe_*`/`_trace_*`/`_debug_*`/`leak_check.py`/`trace_leak.py`, and `tmp_qfv3jj4/`/`tmpxps3dfx2/` are implementation/tests/scratch, NOT handoffs.

## SESSION AUDIT (2026-11-12T23:30:00Z) — GATE GREEN, DEFECT RE-CONFIRMED AT CURRENT HEAD, BLOCKERS RE-AUDITED

This pass was an **AUDIT + CAMPAIGN-REFOCUS** pass (no material code/test change shipped). Every claim below was executed at HEAD `23b454f`, not inherited.

### CELL 14 RE-PROBED AT CURRENT HEAD — STILL A CONFIRMED, REPRODUCIBLE DEFECT (NOT YET FIXED)
**CELL 14 IS A REAL BUG.** Not a coverage question. The stale note's repro was re-run against the live tree and reproduces exactly. Do NOT re-derive; execute the ordered fix steps below.

**DEFECT:** `src/backtest/engine.py` settles the **risk ledger with the COIN-only `pnl`** on both the liquidation and stop exits, silently dropping the ETH hedge leg. `TradeResult.total_pnl` is correct; only `risk_state.realized_pnl` is wrong.
- Liq branch: `risk_state.apply_trade(..., pnl, ...)` at `src/backtest/engine.py:350`; `total_pnl_result = pnl + hedge_pnl_total` at `:352`; returned at `:365`.
- Stop branch: `risk_state.apply_trade(..., pnl, ...)` at `src/backtest/engine.py:402`; `total_pnl_result = pnl + hedge_pnl_total` at `:404`; returned at `:417`.
- Hedge is fully computed BEFORE each call — liq at `:334-346`, stop at `:386-399` — so `hedge_pnl_total` is already in scope; the fix is a one-token change per branch, no reordering.
- CORRECT paths for comparison: target settles `total_pnl` at `:457`; time-exit settles `total_pnl_result` at `:748`; loop-else final settles `short_pnl` at `:677` (locked, runner reconciles — do NOT touch).
- Rebound-short branches already settle correctly (`short_pnl + rebound_hedge_pnl`) at `:547`, `:581`, `:613`, `:644`. The two long-leg branches are the only offenders.

**PROOF (executed 2026-11-12T23:30:00Z, fixtures from `tests/test_long_leg_liquidation_hedge_completeness.py`, `_cfg(funding_rate_pct_per_hour=0.01)`, entry 100, shares 1.0, signal_idx 5):**
```
liq_bar=8  exit=liquidated coin=-7.54 hedge=+1.9066 total_pnl=-5.6334 realized_pnl=-7.54   match=False
liq_bar=10 exit=liquidated coin=-7.56 hedge=+1.0733 total_pnl=-6.4867 realized_pnl=-7.56   match=False
stop       exit=stopped    coin=-5.04 hedge=+1.9066 total_pnl=-3.1334 realized_pnl=-5.04   match=False
```
`total_pnl` includes the hedge; `realized_pnl` equals coin-only. Funding moves the coin-only realized figure (e.g. -7.54 → -7.56) while the +1.9/+1.07 hedge credit is dropped entirely.
- **Invariant violated:** on any fully-closed long trade, `risk_state.realized_pnl == res.total_pnl` (coin + hedge).
- **Why the gate stays green:** `tests/test_long_leg_liquidation_hedge_completeness.py:146` asserts `rs.realized_pnl == res.pnl` — it **enshrines the bug**. Other liq/stop tests use `funding_rate_pct_per_hour=0.0` and/or assert only `isinstance(total_pnl,(int,float))`. The loop-else final-exit test asserting `realized == 2*total_pnl` passes because that path settles `short_pnl` and the runner reconciles — a different, locked path.
- **Risk:** any portfolio/equity figure derived from the risk ledger understates long-leg outcomes by the hedge credit on liquidation/stop exits; the discrepancy scales with funding rate and held hours, so it is non-trivial.

### SECONDARY GAP (same cell, ship after the fix)
The portfolio trade record (`scripts/run_portfolio.py:391-412`) omits `rebound_short_pnl` / `rebound_hedge_pnl`, so per-leg funding reconciliation at the portfolio layer cannot be asserted. Additive exposure only; no behavior change.

## MANDATORY NEXT SESSION — CELL 14 FIX (ORDERED, HEAVY)

1. **Fix the liq branch:** `src/backtest/engine.py:350` — `risk_state.apply_trade(..., pnl, ...)` → `risk_state.apply_trade(..., pnl + hedge_pnl_total, ...)`. Hedge is in scope from `:334-346`.
2. **Fix the stop branch:** `src/backtest/engine.py:402` — identical change. Hedge in scope from `:386-399`.
3. **Correct the enshrining assertion:** `tests/test_long_leg_liquidation_hedge_completeness.py:146` `rs.realized_pnl == res.pnl` → `rs.realized_pnl == res.total_pnl`. This is a CORRECTION (the old assertion encoded the bug), not a regression.
4. **Add a dated red→green test** `tests/test_long_liquidation_stop_risk_state_hedge_funding_settlement_20261112.py` proving `realized_pnl == total_pnl` on liq AND stop with `funding_rate_pct_per_hour=0.01` (use the exact traces above). Must FAIL before steps 1–2, PASS after.
5. **Mutation-verify non-vacuous:** revert fix 1 alone → the liq case FAILS; revert fix 2 alone → the stop case FAILS; restore. Both changes must be load-bearing independently.
6. **Additive:** expose `rebound_short_pnl` / `rebound_hedge_pnl` in the portfolio trade record (`scripts/run_portfolio.py:391-412`) and assert per-leg funding reconciliation at portfolio level.
7. **Do NOT touch** the loop-else final-exit settlement (`src/backtest/engine.py:677`) or the portfolio runner's `total_pnl` reconciliation — locked semantics.
8. **Gate:** full `PYTHONPATH=. python3 -m pytest -q --tb=short`. Expect 905 + new tests; the corrected `test_long_leg_liquidation_hedge_completeness` must stay green under the corrected assertion.

## BOTTLENECK AUDIT (2026-11-12T23:30:00Z) — CLEARED, NOTHING IDLE-BLOCKED
- **Single durable handoff:** only root `HANDOFF.md`; `README.md` points here. No TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoff files exist outside `.git/`.
- **Locks/contention:** no `*.lock` outside `.git/`. Working tree clean. No multi-session contention; nothing idle-blocked.
- **Stale artifact neutralized:** `research_state/gap_analysis.md` carries a **SUPERSEDED** banner (historical only; authoritative spec = `research_state/strategy_spec.md`). Do not re-litigate finished work from it. Its "MISSING" rows (ETH hedge, volume sizing) are long-since implemented — treat any re-read of it as a trap.
- **Stale remote branches (NOT blockers):** `origin/fix/campaign-fixture-provenance-20261030` and `origin/fix/campaign-integrity-and-exposure-accounting-20261030` are ~1040 commits behind `main` and superseded. Do NOT merge/rebase or treat their diffs as current gaps.
- **Real-data blocker — CONFIRMED REAL, DO NOT "UNBLOCK":** `research_state/cache/hyperliquid_verified_283d_btceth/candles/{BTC,ETH}.json` are 6792-bar placeholders (provenance `status:"error"`, `synthetic_check.is_synthetic:true`, `reason:"flat_series_all_bars_identical"`, 1 distinct signature / 6792 bars, `summary.ready_for_real_campaign:false`, `all_complete:false`). The placeholder closes are constant (BTC 60000, volume 2e9; ETH volume constant) yet the coverage report records `observed_min_24h_usd_volume` of 1.2e14–2.88e15 USD and `volume_filter_ok:true` — **placeholder-derived volume is NOT real evidence and must never be cited as a campaign result.** Fabricating/promoting is forbidden. The 283d real-data campaign stays NOT RUN. This blocks ONLY real-data runs; all spec-unit and engine tests run on fixtures and are fully executable.
- **Test env:** deps present. If missing in a fresh environment, `python -m pip install --break-system-packages pytest numpy pandas requests` (per `.github/workflows/strategy-tests.yml`, Python 3.12, `PYTHONPATH=.`).
- **Uncommitted residue to ignore (scratch, not handoff):** root `_probe_*`/`_trace_*`/`_debug_*`/`leak_check.py`/`trace_leak.py`, `tmp_qfv3jj4/`, `tmpxps3dfx2/`, `.pytest_cache`, `__pycache__`.

## PRIOR SHIPPED (VERIFIED INTACT AT THIS HEAD — DO NOT RE-LITIGATE)
- **CELL 11 — ETH hedge excluded from 120% gross cap:** `tests/test_hedge_excluded_from_120pct_gross_cap_20261112.py` (1, mutation-verified); implementation already correct (`engine.py:246-269`, `run_portfolio.py` reservation reads hedges excluded).
- **CELL 12 — Bounce-confirmation gate for rebound-short entry:** `src/backtest/engine.py:466-484` consults `rebound_short_require_bounce_confirm` via `confirm_rebound(candles[:idx+1], ...)` with no look-ahead; default `False` preserves anchors. `tests/test_rebound_short_requires_bounce_confirmation_20261112.py` (6, mutation-verified).
- **CELL 13 — Portfolio-level bounce-gated rebound-short admission under 120% cap:** additive `max_live_coin_notional` in the trade record (`scripts/run_portfolio.py:403`); `tests/test_portfolio_bounce_gated_rebound_short_under_120pct_cap_20261112.py` (4, mutation-verified).
- **CELL 5/6/7/8/9/10 — EXHAUSTED WITH EVIDENCE.** Details and file lists are in prior revisions of this file's git history; the short form: fee export wiring; vault-fee core (2%/yr AUM capped to equity, 10% profit-above-HWM) + opt-in reconciliation + config surface (38) + elapsed-hours (9); spec safety-stop × rebound-short same-bar sequencing (3); liquidation-vs-funding same-bar ordering (3); rebound-short liq at 48th bar; equal-share cuts with same-bar rebound admission + mid-flight long; annual/positive-month reporting (3) and equity reporting (6), both mutation-verified; volume-gating spec edges (`>= $5M` inclusive, missing volume fail-closed excluded, one-position-per-coin); provenance `observed_min_24h_usd_volume` fail-closed (8) plus remaining provenance surfaces covered by existing tests; `run_real_campaign.py` fail-closed gating and `derive_verified_universe.py` $5M floor both proven end-to-end; engine fail-closed when `require_eth_hedge=True` and no usable hedge.

## NEXT FOCUS CAMPAIGN (FINITE, ORDERED, HEAVY — SHIP ≥1 MATERIAL ITEM/SESSION)
Repo name priority: **CRASH-REBOUND-STRATEGY** → crash→rebound fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md` with auditable accounting. Execute top-down. For each item: **prove gap** (cite `grep -rn` over `tests/` and consumers), **trace expected values first**, write dated failing test, make it green, mutation-verify, run the full gate.

1. **CELL 14 — RISK-STATE SETTLEMENT DROPS THE ETH HEDGE LEG ON LIQUIDATION/STOP (CONFIRMED DEFECT — FIX FIRST, UNSTARTED).** Steps above. Highest priority: it is a correctness bug, not hardening.
2. **CELL 15 — LONG-LEG `risk_state` ATTRIBUTION vs PORTFOLIO MASTER RECONCILIATION UNDER MIXED EXITS.** After CELL 14, the engine's per-leg ledger should equal `total_pnl` on every closed long path. Prove that at portfolio level: a book mixing liq, stop, target, time-exit, and loop-else final exit must reconcile to the runner's master `risk_state` with per-leg funding attributed (use `rebound_short_pnl`/`rebound_hedge_pnl` from CELL 14 step 6). If reconciliation already holds, cite the exact test and move on.
3. **CELL 16 — HEDGE EXIT-FALLBACK FIDELITY ON EVERY EXIT PATH.** Locked fallback = use hedge entry and re-apply exit slippage/commission when the aligned ETH bar is missing. Prove parity between the aligned-bar and fallback paths on liq, stop, target, time-exit, and rebound-short exits (delta must equal exactly the re-applied exit slippage/commission, with zero PnL drift otherwise). Cite coverage; do not invent a new gap if proven.
4. **CELL 17 — FUNDING-HOURS BOUNDARY AUDIT ACROSS ALL EXIT BRANCHES.** `hours_held = idx - start_idx + 1` on liq/stop/target/time-exit; `short_bars_max` (48) boundary on the rebound short; final-exit hours. Prove off-by-one invariance at the boundary bars for both funding legs; assert no branch double-charges or drops an hour.
5. **CELL 18 — NO-LOOK-AHEAD AUDIT OF HEDGE SIZING WINDOWS.** Locked: hedge sizing uses `eth_candles[:idx+1]` (336h vol ratio, cap 3x) and entry aligned to the same bar. Prove on a fixture where the next bar is a large jump that no admitted hedge notional or entry price changes when future bars are truncated.

**No-idle rule:** passive re-verification or a handoff-only edit without a material test/fix is NOT work. If a cell is already covered, cite the file evidence and move to the next.

## IMPLEMENTATION STATUS (EVIDENCE-BACKED)
- **Core/spec-compliant:** RSI(21)<20 crash trigger; $5M 24h volume enforcement; 1.25% 24h-volume sizing; ETH hedge vol-ratio (336h) capped 3x with no look-ahead; rebound short after +9% target (stop +40%, target -9%, 48h); 8x spec safety stop; 120% gross-cap equal-share cuts; portfolio bar-by-bar deepest-first admission; hourly funding + liquidation at worst price (long low, short high).
- **Reporting:** Sharpe/Sortino/Calmar/win-rate/profit-factor/monthly/weekly, per-leg attribution, exposure; per-year + months-gain counts; equity `equity_*` fields (all additive; anchored aggregates unchanged).
- **Provenance/gating:** fail-closed `observed_min_24h_usd_volume` when the spec floor is required; summary contradiction rejection; temp-path rejection; synthetic_check missing rejection; request_params intent validation (`src/data/provenance.py`).
- **Vault fees:** pure 2%/yr AUM (capped to equity) + 10% profit-above-HWM (`src/metrics/vault_fees.py`), opt-in reconciliation, default outputs unchanged.
- **Runners/gating:** `scripts/run_portfolio.py`, `run_real_campaign.py` (fail-closed provenance/verified gates), engine fail-closed when `require_eth_hedge=True`.

## LOCKED SEMANTICS (assert per traced engine behavior — zero regression)
- `max_live_coin_notional` may exceed the entry-notional cap at pressure/rebound while reservations record the entry-notional cap. Do NOT "fix" without a concrete failing defect that preserves all anchors.
- Overall `exit_reason` may remain `target_rebound_short` while the short-leg trade reason differs — assert per-leg trade reasons.
- Sequencing: liquidation > stop > target > time-exit. `hours_held_short = sidx - short_start_idx + 1`; time-exit at `>= short_bars_max` (default 48).
- Long-leg liq funding: `hours_held_liq = idx - start_idx + 1`, subtracted in the SAME branch as the penalty (cell 4d lock).
- Hedge exit fallback when the aligned ETH bar is unavailable: use the hedge entry and re-apply exit slippage/commission. Hedge sizing from `eth_candles[:idx+1]`, vol-ratio cap 3x, no look-ahead.
- Loop-else final exit (`engine.py:677`): the engine applies `short_pnl` only to risk_state; the portfolio runner reconciles `total_pnl` (all legs) into the master risk_state. Do not change.
- Vault fees: AUM = equity * rate * hours/8760 per step (capped to equity); profit share = 10% * max(0, equity_after_aum - HWM), HWM on post-fee net peaks; opt-in metrics reconciliation must not alter default trade aggregates.
- Reporting: `annual_breakdown`/`annual_trade_counts`/`positive_months`/`negative_months`/`flat_months`/`total_months` and equity `equity_*` are ADDITIVE; `win_rate`/`monthly`/`weekly`/exposure and anchored per-trade `sharpe_ratio`/`sortino_ratio`/`calmar_ratio` must be unchanged.
- `backtest_simple` is a low-level executor (signal assumed). Spec-compliant gating lives in `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners.
- Fail-closed: missing provenance/verification on the real path → reject. Never fabricate data or results.

## COVERED — DO NOT RE-LITIGATE WITHOUT CONCRETE FAILING EVIDENCE
CELL 1 fee export wiring; vault fee core + opt-in reconciliation + HWM dip/recover no-double-charge + AUM-capped-to-equity; CELL 2 fee config surface (38); CELL 3 fee elapsed-hours (9); CELL 4b spec safety-stop × rebound-short same-bar sequencing (3); CELL 4d liquidation-vs-funding same-bar ordering (3); CELL 5 (a)(b)(c); CELL 6 annual/positive-month reporting (3); CELL 7 equity reporting (6); CELL 8 volume-gating spec edges; CELL 9 provenance observed_min fail-closed (8) + remaining surfaces; CELL 10 runner gating integration; CELL 11 hedge excluded from 120% cap; CELL 12 bounce-confirmation gate; CELL 13 portfolio bounce-gated rebound-short admission; both-hedges FINAL EXIT/STOP/TARGET/TIME_EXIT/LIQUIDATION family; portfolio both-hedged rebound loop-else final exit; stopped-buy-never-opens-rebound E2E; one-position-per-coin; `.test_derive_vol_*` fixture cleanup.

## CRITICAL CONTEXT
- Spec truth: `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Test window 2025-12-20→2026-09-28 (283d), 6792 hourly bars/symbol.
- `research_state/gap_analysis.md` is SUPERSEDED (historical only) — do not treat its "MISSING" rows as work.
- Core: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/{loader,provenance,streaming_ingest}.py`, `src/metrics/{campaign_metrics,vault_fees}.py`.
- Runners/guards: `scripts/run_portfolio.py`, `run_real_campaign.py`, `run_campaign.py`, `derive_verified_universe.py`, `fetch_hyperliquid_candles.py`, `generate_candle_coverage_gap_report.py`.

## RULES (NON-NEGOTIABLE — VIOLATION = SESSION FAILURE)
- Each session ships ≥1 material item with concrete evidence (dated test + gate count + traced values).
- Spec is truth: both legs, ETH hedge every leg, funding/liquidation on every leg and exit path, $5M gating, 1.25% sizing in spec paths, equal-share cuts old+new, stopped buy never opens rebound short.
- Fail-closed: missing provenance/verification on the real path → reject. Never fabricate data or results.
- Do not commit unless the user explicitly asks.

## INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (2026-11-12T23:30:00Z, MANDATORY, HEAVY, NON-OPTIONAL)
```text
CRASH-REBOUND-STRATEGY | 2026-11-12T23:30:00Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

REPO IDENTITY / PRIORITY (DRIVES ALL WORK): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to crash-rebound-strategy.pdf / research_state/strategy_spec.md. Hourly bar-by-bar backtest engine only. NEVER claim 20s slicing, spread/L2/order-book impact. Mission: RSI(21)<20 crash trigger → rebound short (+9% target, +40% stop, -9% target, 48h) with ETH hedge every leg, equal-share cap cuts, strict no look-ahead, fail-closed gates.

STEP 0 — GATE (NON-NEGOTIABLE, RUN FIRST):
  PYTHONPATH=. python3 -m pytest -q --tb=short
  Last verified 2026-11-12T23:30:00Z at HEAD 23b454f, working tree clean: 905 passed, 12 skipped in 34.86s, GREEN.
  Re-run at your HEAD/worktree and report the exact count. If broken or regressed, fix before ANYTHING else.
  Fresh env deps: python -m pip install --break-system-packages pytest numpy pandas requests (Python 3.12, per .github/workflows/strategy-tests.yml).

STEP 1 — CELL 14 IS A CONFIRMED DEFECT. FIX IT. NOT OPTIONAL, NOT HARDENING.
  DEFECT: src/backtest/engine.py settles the risk ledger with COIN-ONLY pnl on the long-leg liquidation and stop exits, silently dropping the ETH hedge credit.
    - Liq:  risk_state.apply_trade(..., pnl, ...) at src/backtest/engine.py:350 (hedge computed at :334-346, total at :352, returned :365)
    - Stop: risk_state.apply_trade(..., pnl, ...) at src/backtest/engine.py:402 (hedge computed at :386-399, total at :404, returned :417)
    - Correct for comparison: target :457 (total_pnl), time-exit :748 (total_pnl_result), rebound branches :547/:581/:613/:644 (short_pnl + rebound_hedge_pnl), loop-else final :677 (LOCKED, do not touch).
  INVARIANT VIOLATED: on any fully-closed long trade, risk_state.realized_pnl must equal res.total_pnl (coin + hedge).
  PROOF (executed 2026-11-12T23:30:00Z with tests/test_long_leg_liquidation_hedge_completeness.py fixtures, _cfg(funding_rate_pct_per_hour=0.01), entry 100, shares 1.0, signal_idx 5):
    liq_bar=8  exit=liquidated coin=-7.54 hedge=+1.9066 total_pnl=-5.6334 realized_pnl=-7.54  match=False
    liq_bar=10 exit=liquidated coin=-7.56 hedge=+1.0733 total_pnl=-6.4867 realized_pnl=-7.56  match=False
    stop       exit=stopped    coin=-5.04 hedge=+1.9066 total_pnl=-3.1334 realized_pnl=-5.04  match=False
  ENSHRINING TEST TO CORRECT: tests/test_long_leg_liquidation_hedge_completeness.py:146 asserts rs.realized_pnl == res.pnl — change to == res.total_pnl (CORRECTION, not a regression).
  ORDERED FIX:
    1) src/backtest/engine.py:350 → risk_state.apply_trade(..., pnl + hedge_pnl_total, ...)
    2) src/backtest/engine.py:402 → same → pnl + hedge_pnl_total
    3) Correct tests/test_long_leg_liquidation_hedge_completeness.py:146 to rs.realized_pnl == res.total_pnl
    4) Add tests/test_long_liquidation_stop_risk_state_hedge_funding_settlement_20261112.py: liq AND stop, funding_rate_pct_per_hour=0.01, exact traces above. RED before 1-2, GREEN after.
    5) Mutation-verify: revert fix 1 alone → liq case FAILS; revert fix 2 alone → stop case FAILS; restore. Both must be independently load-bearing.
    6) Additive: expose rebound_short_pnl / rebound_hedge_pnl in the portfolio trade record (scripts/run_portfolio.py:391-412); assert per-leg funding reconciliation at portfolio level.
  DO NOT TOUCH: loop-else final-exit settlement (engine.py:677) or the portfolio runner total_pnl reconciliation — LOCKED SEMANTICS.
  GATE: full PYTHONPATH=. python3 -m pytest -q --tb=short, exact count. Expect 905 + new tests; corrected test_long_leg_liquidation_hedge_completeness stays green under the corrected assertion.
  IF somehow already fixed at your HEAD: re-probe the exact repro FIRST, then cite the file/line that fixed it and move to CELL 15. Do NOT invent a new gap.

STEP 2 — CONTINUE THE FINITE CAMPAIGN TOP-DOWN (do not stop after CELL 14):
  CELL 15 — Long-leg risk_state attribution vs portfolio master reconciliation under MIXED exits (liq + stop + target + time-exit + loop-else final). Per-leg funding must reconcile to the runner master risk_state using the newly exposed rebound_short_pnl / rebound_hedge_pnl. Cite existing coverage or ship a new dated test.
  CELL 16 — Hedge exit-fallback fidelity on EVERY exit path. Locked fallback = hedge entry + re-applied exit slippage/commission when the aligned ETH bar is missing. Prove parity vs the aligned-bar path on liq, stop, target, time-exit, rebound-short exits: delta must equal exactly the re-applied exit slippage/commission, zero PnL drift otherwise.
  CELL 17 — Funding-hours boundary audit across all exit branches: off-by-one invariance at boundary bars for BOTH legs; short_bars_max=48 boundary; final-exit hours; no double-charge, no dropped hour.
  CELL 18 — No-look-ahead audit of hedge sizing windows: on a fixture where the next bar is a large jump, prove no admitted hedge notional or entry price changes when future bars are truncated (locked: eth_candles[:idx+1], vol-ratio cap 3x).

METHOD FOR EVERY ITEM (NON-NEGOTIABLE):
  1) GAP PROOF — cite concrete evidence (grep -rn over tests/ + consumers, or a repro script output).
  2) TRACE FIRST — deterministic hand-traced fixtures with exact expected values (write them down before coding).
  3) SHIP — dated failing-tests-first (red→green). Preserve every anchor in LOCKED SEMANTICS. Mutation-verify non-vacuous.
  4) VERIFY — targeted test + full gate `PYTHONPATH=. python3 -m pytest -q --tb=short` with exact count.
  5) CONTINUE down the campaign until exhausted with evidence.

BOTTLENECKS (audit 2026-11-12T23:30:00Z): CLEARED. Single durable handoff = root HANDOFF.md only. No *.lock outside .git/. No contradictory handoff artifacts. Working tree clean at HEAD 23b454f. Gate GREEN (905/12). Nothing idle-blocked; no multi-session contention. Stale research_state/gap_analysis.md is banner-marked SUPERSEDED (historical only; its MISSING rows are long-implemented — do not re-litigate). Stale origin/fix/campaign-* branches are ~1040 commits behind main and are NOT blockers.

DATA BLOCKER — CONFIRMED REAL, DO NOT TRY TO UNBLOCK: the tracked 6792-bar BTC/ETH under research_state/cache/hyperliquid_verified_283d_btceth/ are PLACEHOLDERS (provenance per-symbol status:"error", synthetic_check.is_synthetic:true, reason flat_series_all_bars_identical, 1/6792 distinct signatures, summary.ready_for_real_campaign:false). The coverage report's observed_min_24h_usd_volume (1.2e14–2.88e15 USD) is placeholder-derived and is NOT real evidence — never cite it as a campaign result. Fabricating or promoting is forbidden. The 283d real-data campaign stays NOT RUN. This blocks ONLY real-data runs; all spec-unit and engine tests run on fixtures and remain fully executable.

LOCKED SEMANTICS (assert per traced engine behavior — zero regression):
  - max_live_coin_notional may exceed the entry-notional cap at pressure/rebound while reservations record the entry-notional cap — do NOT 'fix' without a concrete failing defect preserving all anchors.
  - Overall exit_reason may remain target_rebound_short while the short-leg trade reason differs — assert per-leg trade reasons.
  - Sequencing: liquidation > stop > target > time-exit. hours_held_short = sidx - short_start_idx + 1; time-exit at >= short_bars_max (default 48).
  - Long-leg liq funding: hours_held_liq = idx - start_idx + 1, subtracted in the SAME branch as the penalty (cell 4d lock).
  - Hedge exit fallback when the aligned ETH bar is unavailable: use the hedge entry and re-apply exit slippage/commission. Hedge sizing from eth_candles[:idx+1], vol-ratio cap 3x, no look-ahead.
  - Loop-else final exit: engine applies short_pnl only to risk_state; the portfolio runner reconciles total_pnl into the master risk_state.
  - Vault fees: AUM = equity * rate * hours/8760 per step (capped to equity); profit share = 10% * max(0, equity_after_aum - HWM), HWM on post-fee net peaks; opt-in metrics reconciliation must not alter default trade aggregates.
  - Reporting: annual_breakdown/annual_trade_counts/positive_months/negative_months/flat_months/total_months and equity equity_* are ADDITIVE; win_rate/monthly/weekly/exposure and anchored per-trade sharpe_ratio/sortino_ratio/calmar_ratio unchanged.
  - backtest_simple is a low-level executor (signal assumed). Spec-compliant gating lives in generate_signal/filter_universe/passes_universe_filter/gated wrappers/runners. Fail-closed: missing provenance/verification on the real path → reject. Never fabricate data or results.

COVERED — DO NOT RE-LITIGATE WITHOUT CONCRETE FAILING EVIDENCE: CELL 1 fee export wiring; vault fee core + opt-in reconciliation + HWM dip/recover no-double-charge + AUM-capped-to-equity; CELL 2 fee config surface (38); CELL 3 fee elapsed-hours (9); CELL 4b spec safety-stop × rebound-short same-bar sequencing (3); CELL 4d liquidation-vs-funding same-bar ordering (3); CELL 5 (a)(b)(c) all covered; CELL 6 annual/positive-month reporting (3, mutation-verified); CELL 7 equity reporting (6, mutation-verified); CELL 8 volume-gating spec edges; CELL 9 provenance observed_min fail-closed (8) + remaining surfaces; CELL 10 end-to-end runner gating integration; CELL 11 hedge excluded from 120% cap; CELL 12 bounce-confirmation gate for rebound-short entry; CELL 13 portfolio bounce-gated rebound-short admission under 120% cap; both-hedges FINAL EXIT/STOP/TARGET/TIME_EXIT/LIQUIDATION family; portfolio both-hedged rebound loop-else final exit; stopped-buy-never-opens-rebound E2E; one-position-per-coin; .test_derive_vol_* fixture cleanup.

FINAL STEPS (MANDATORY): report exact commands/results and files changed. Update ONLY root HANDOFF.md: new UTC timestamp, bottleneck audit, shipped material item(s) with traced evidence, full-gate count, remaining risks, and a new timestamped heavy initial task for the next session.

NO-IDLE / CONTINUATION: passive re-verification or a handoff-only edit without a material test/fix is NOT work. Each session ships >= 1 material item with a dated test, gate count, and traced values. Do not stop after one cell.

SPEC NON-NEGOTIABLES: hourly funding on every leg/exit; hourly liquidation at worst price with correct sequencing/notional/timing/penalty; stopped buy never opens rebound short; 8x safety stop; rebound -9%/48h/+40% anchored to the executed short entry; ETH hedge every leg (336h vol ratio cap 3x), sizing eth_candles[:idx+1], entry aligned; RSI(21)<20 next open deepest-first; $5M 24h volume in all spec gating; 1.25% 24h-volume sizing in spec path; equal-share cuts old+new across the 120% gross cap (cuts only, never top-up); one position per coin; strict no look-ahead. Fail-closed on missing provenance/verification and on missing/insufficient required ETH hedge.
```

---

**END OF HANDOFF — THIS IS THE ONLY DURABLE CONTEXT. NEXT SESSION MUST EXECUTE THE INITIAL TASK ABOVE OR FAIL. (2026-11-12T23:30:00Z)**