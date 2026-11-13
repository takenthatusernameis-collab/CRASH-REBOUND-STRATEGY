# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-13T00:29:50Z
**HEAD audited:** `61cbca8` (HEAD, `chore(kilo): checkpoint agent session`; base worktree clean aside from this handoff refresh). CELL 14 engine fix (risk_state settles total_pnl = coin + hedge on liq/stop/target, engine.py:350/:402/:457) is IN CODE; the enshrining test `tests/test_long_leg_liquidation_hedge_completeness.py:146` (`rs.realized_pnl == res.total_pnl`) and 2 stale coin-only assertions in `tests/test_long_liquidation_precedes_stop_and_target_same_bar_*_eth_hedge_20261111.py:189` and `tests/test_long_stop_target_missing_eth_exit_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py:193` were corrected to `total_pnl` (CORRECTION, not a regression). CELL 14 is now FIXED + GATE GREEN.
**Gate at this HEAD:** last verified 2026-11-13T00:29:50Z at HEAD `61cbca8` (`PYTHONPATH=. python3 -m pytest -q --tb=short` → **905 passed, 12 skipped in 35.34s**, GREEN). No production/test-code changes since; next session must re-run at its HEAD/worktree and report exact count.
**Checkpoint note:** Bottleneck audit 2026-11-13T00:29:50Z — single durable handoff is root `HANDOFF.md` only, no `*.lock` outside `.git/`, no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT artifacts, no multi-session contention, placeholder real-data blocker unchanged (real 283d campaign NOT RUN). CELL 14 remains fixed; STEP 2 CELL 15 is the next mandatory heavy item.

**Single canonical durable handoff: ONLY this root `HANDOFF.md`.** `README.md` points here. Do not create or trust any other TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoff file.

## INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (2026-11-13T00:29:50Z, MANDATORY, HEAVY, NON-OPTIONAL)
```text
CRASH-REBOUND-STRATEGY | 2026-11-13T00:29:50Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

REPO IDENTITY / PRIORITY (DRIVES ALL WORK): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to crash-rebound-strategy.pdf / research_state/strategy_spec.md. Hourly bar-by-bar backtest engine only. NEVER claim 20s slicing, spread/L2/order-book impact. Mission: RSI(21)<20 crash trigger → rebound short (+9% target, +40% stop, -9% target, 48h) with ETH hedge every leg, equal-share cap cuts, strict no look-ahead, fail-closed gates.

STEP 0 — GATE (NON-NEGOTIABLE, RUN FIRST):
  PYTHONPATH=. python3 -m pytest -q --tb=short
  Last verified 2026-11-13T00:22:47Z at HEAD e4bedfd, base worktree clean: 905 passed, 12 skipped in 35.94s, GREEN.
  Re-run at your HEAD/worktree and report the exact count. If broken or regressed, fix before ANYTHING else.
  Fresh env deps: python -m pip install --break-system-packages pytest numpy pandas requests (Python 3.12).

STEP 1 — CELL 14 (RISK-STATE SETTLEMENT DROPS ETH HEDGE ON LIQ/STOP): FIXED — COMPLETE. DO NOT RE-OPEN WITHOUT A CONCRETE FAILING DEFECT.
  DEFECT (RESOLVED): src/backtest/engine.py settles the risk ledger with COIN-ONLY pnl on long-leg liquidation and stop exits, silently dropping the ETH hedge credit.
    - Liq:  risk_state.apply_trade(..., pnl, ...) at src/backtest/engine.py:350. Hedge is computed at :331-343 and total at :352.
    - Stop: risk_state.apply_trade(..., pnl, ...) at src/backtest/engine.py:402. Hedge is computed at :381-395 and total at :404.
    - Correct paths: target :457 (total_pnl), time-exit :748 (total_pnl_result), rebound branches :547/:581/:613/:644 (short_pnl + rebound_hedge_pnl), loop-else final :677 (LOCKED, do not touch).
  SHIPPED FIX (do not revert): engine.py:350/:402/:457 settle total_pnl = coin + hedge on liq/stop/target. Corrected assertions: tests/test_long_leg_liquidation_hedge_completeness.py:146 (rs.realized_pnl == res.total_pnl), tests/test_long_liquidation_precedes_stop_and_target_same_bar_*_eth_hedge_20261111.py:189, tests/test_long_stop_target_missing_eth_exit_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py:193.
  Re-probe invariant holds: risk_state.realized_pnl == res.total_pnl on liq/stop/target. Continue to STEP 2 CELL 15. Do NOT invent a new gap or re-litigate CELL 14.

STEP 2 — CONTINUE THE FINITE CAMPAIGN TOP-DOWN (do not stop after CELL 14):
  CELL 15 — Long-leg risk_state attribution vs portfolio master reconciliation under MIXED exits (liq + stop + target + time-exit + loop-else final). Per-leg funding must reconcile to the runner master risk_state using rebound_short_pnl / rebound_hedge_pnl. Cite existing coverage or ship a new dated test.
  CELL 16 — Hedge exit-fallback fidelity on EVERY exit path. Locked fallback = hedge entry + re-applied exit slippage/commission when the aligned ETH bar is missing. Prove parity vs the aligned-bar path on liq, stop, target, time-exit, rebound-short exits: delta must equal exactly the re-applied exit slippage/commission, zero PnL drift otherwise.
  CELL 17 — Funding-hours boundary audit across all exit branches: off-by-one invariance at boundary bars for BOTH legs; short_bars_max=48 boundary; final-exit hours; no double-charge, no dropped hour.
  CELL 18 — No-look-ahead audit of hedge sizing windows: on a fixture where the next bar is a large jump, prove no admitted hedge notional or entry price changes when future bars are truncated (locked: eth_candles[:idx+1], vol-ratio cap 3x).

METHOD FOR EVERY ITEM (NON-NEGOTIABLE):
  1) GAP PROOF — cite concrete evidence (grep -rn over tests/ + consumers, or a repro script output).
  2) TRACE FIRST — deterministic hand-traced fixtures with exact expected values (write them down before coding).
  3) SHIP — dated failing-tests-first (red→green). Preserve every anchor in LOCKED SEMANTICS. Mutation-verify non-vacuous.
  4) VERIFY — targeted test + full gate with exact count.
  5) CONTINUE down the campaign until exhausted with evidence.

BOTTLENECKS (audit 2026-11-13T00:29:50Z): CLEARED. Single durable handoff = root HANDOFF.md only. No *.lock outside .git/. No contradictory handoff artifacts. Working tree clean except this handoff refresh. Gate GREEN (905/12, 35.34s at 61cbca8). No multi-session contention; nothing idle-blocked. CELL 14 is FIXED (engine.py:350/:402/:457 settle total_pnl; tests corrected; gate green) — no active code blocker remains. The only open campaign items are CELL 15→18 (STEP 2).

DATA BLOCKER — CONFIRMED REAL, DO NOT TRY TO UNBLOCK: the tracked 6792-bar BTC/ETH under research_state/cache/hyperliquid_verified_283d_btceth/ are PLACEHOLDERS (provenance per-symbol status:"error", synthetic_check.is_synthetic:true, reason flat_series_all_bars_identical, 1/6792 distinct signatures, summary.ready_for_real_campaign:false). The coverage report's observed_min_24h_usd_volume is placeholder-derived and is NOT real evidence — never cite it as a campaign result. Fabricating or promoting is forbidden. The 283d real-data campaign stays NOT RUN. This blocks ONLY real-data runs; all spec-unit and engine tests run on fixtures and remain fully executable.
```

## BOTTLENECK AUDIT (2026-11-13T00:29:50Z)
- **Single durable handoff:** only root `HANDOFF.md`; `README.md` points here. No TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoff files exist outside `.git/`.
- **Locks/contention:** no `*.lock` outside `.git/`; no uncommitted production/test changes; no multi-session contention. The only intended worktree change is this `HANDOFF.md` update. Only ignored `__pycache__`/`.pytest_cache` residue exists. CELL 14 is FIXED (no open defect).
- **Stale artifact neutralized:** `research_state/gap_analysis.md` is banner-marked SUPERSEDED. Authoritative spec is `research_state/strategy_spec.md`. Do not re-litigate its old MISSING rows.
- **Stale remote branches (NOT blockers):** `origin/fix/campaign-fixture-provenance-20261030` and `origin/fix/campaign-integrity-and-exposure-accounting-20261030` are ~1040 commits behind `main`. Do not merge/rebase or treat their diffs as current gaps.
- **Real-data blocker — CONFIRMED REAL, DO NOT "UNBLOCK":** the tracked 6792-bar BTC/ETH cache files are placeholders as described above. Fabricating/promoting is forbidden. The 283d real-data campaign stays NOT RUN.
- **Test env:** deps present. Fresh env: `python -m pip install --break-system-packages pytest numpy pandas requests` (Python 3.12, per `.github/workflows/strategy-tests.yml`).

## PRIOR SHIPPED (DO NOT RE-LITIGATE WITHOUT CONCRETE FAILING EVIDENCE)
- **CELL 11 — ETH hedge excluded from 120% gross cap:** `tests/test_hedge_excluded_from_120pct_gross_cap_20261112.py` (1, mutation-verified); implementation already correct.
- **CELL 12 — Bounce-confirmation gate for rebound-short entry:** `src/backtest/engine.py` consults `rebound_short_require_bounce_confirm` over `candles[:idx+1]`; `tests/test_rebound_short_requires_bounce_confirmation_20261112.py` (6, mutation-verified).
- **CELL 13 — Portfolio bounce-gated rebound-short admission under 120% cap:** additive `max_live_coin_notional` in the trade record; `tests/test_portfolio_bounce_gated_rebound_short_under_120pct_cap_20261112.py` (4, mutation-verified).
- **CELL 1/2/3/4/5/6/7/8/9/10 — EXHAUSTED WITH EVIDENCE.** Short form: fee export wiring; vault-fee core (2%/yr AUM capped to equity, 10% profit-above-HWM) + opt-in reconciliation + config surface (38) + elapsed-hours (9); spec safety-stop × rebound-short same-bar sequencing (3); liquidation-vs-funding same-bar ordering (3); rebound-short liq at 48th bar; equal-share cuts with same-bar rebound admission + mid-flight long; annual/positive-month reporting (3) and equity reporting (6); volume-gating spec edges; provenance observed_min fail-closed (8) and related surfaces; real-campaign fail-closed gating and $5M derivation; engine fail-closed when `require_eth_hedge=True`.

## NEXT FOCUS CAMPAIGN (FINITE, ORDERED, HEAVY — SHIP ≥1 MATERIAL ITEM/SESSION)
Repo-name priority: **CRASH-REBOUND-STRATEGY** → crash→rebound fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md` with auditable accounting. Execute top-down.

1. **CELL 14 — RISK-STATE SETTLEMENT DROPS THE ETH HEDGE LEG ON LIQUIDATION/STOP (CONFIRMED DEFECT — FIXED/COMPLETE).** engine.py:350/:402/:457 settle total_pnl = coin + hedge; tests corrected to total_pnl; gate 905/12 GREEN. Shipped at HEAD e4bedfd. Do not re-open.
2. **CELL 15 — LONG-LEG `risk_state` ATTRIBUTION vs PORTFOLIO MASTER RECONCILIATION UNDER MIXED EXITS (NEXT ACTIVE ITEM).** After CELL 14, the engine's per-leg ledger equals `total_pnl` on every closed long path. Prove that at portfolio level: a book mixing liq, stop, target, time-exit, and loop-else final exit reconciles to the runner's master `risk_state` with per-leg funding attributed. Cite the exact test if already covered; otherwise ship a new dated test (red→green).
3. **CELL 16 — HEDGE EXIT-FALLBACK FIDELITY ON EVERY EXIT PATH.** Prove parity between aligned-bar and fallback paths on liq, stop, target, time-exit, and rebound-short exits: delta must equal exactly re-applied exit slippage/commission, zero PnL drift otherwise. Cite coverage; do not invent a gap if proven.
4. **CELL 17 — FUNDING-HOURS BOUNDARY AUDIT ACROSS ALL EXIT BRANCHES.** `hours_held = idx - start_idx + 1` on liq/stop/target/time-exit; `short_bars_max` (48) boundary on rebound short; final-exit hours. Prove off-by-one invariance at boundary bars for both funding legs; no double-charge, no dropped hour.
5. **CELL 18 — NO-LOOK-AHEAD AUDIT OF HEDGE SIZING WINDOWS.** Locked: hedge sizing uses `eth_candles[:idx+1]` (336h vol ratio, cap 3x), entry aligned to same bar. Prove on a fixture with a large next-bar jump that no admitted hedge notional or entry price changes when future bars are truncated.

**No-idle rule:** passive re-verification or a handoff-only edit without a material test/fix is NOT work. If a cell is already covered, cite the exact file/test evidence and move to the next.

## LOCKED SEMANTICS (assert per traced engine behavior — zero regression)
- `max_live_coin_notional` may exceed the entry-notional cap at pressure/rebound while reservations record the entry-notional cap. Do not "fix" without a concrete failing defect preserving all anchors.
- Overall `exit_reason` may remain `target_rebound_short` while the short-leg trade reason differs — assert per-leg trade reasons.
- Sequencing: liquidation > stop > target > time-exit. `hours_held_short = sidx - short_start_idx + 1`; time-exit at `>= short_bars_max` (default 48).
- Long-leg liq funding: `hours_held_liq = idx - start_idx + 1`, subtracted in the SAME branch as the penalty (cell 4d lock).
- Hedge exit fallback when the aligned ETH bar is unavailable: use the hedge entry and re-apply exit slippage/commission. Hedge sizing from `eth_candles[:idx+1]`, vol-ratio cap 3x, no look-ahead.
- Loop-else final exit (`engine.py:677`): the engine applies `short_pnl` only to risk_state; the portfolio runner reconciles `total_pnl` (all legs) into the master risk_state. Do not change.
- Vault fees: AUM = equity * rate * hours/8760 per step (capped to equity); profit share = 10% * max(0, equity_after_aum - HWM), HWM on post-fee net peaks; opt-in metrics reconciliation must not alter default trade aggregates.
- Reporting: `annual_breakdown`/`annual_trade_counts`/`positive_months`/`negative_months`/`flat_months`/`total_months` and equity `equity_*` are ADDITIVE; `win_rate`/`monthly`/`weekly`/exposure and anchored per-trade `sharpe_ratio`/`sortino_ratio`/`calmar_ratio` must be unchanged.
- `backtest_simple` is a low-level executor (signal assumed). Spec-compliant gating lives in `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners.
- Fail-closed: missing provenance/verification on the real path → reject. Never fabricate data or results.

## CRITICAL CONTEXT
- Spec truth: `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Test window 2025-12-20→2026-09-28 (283d), 6792 hourly bars/symbol.
- Core: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/{loader,provenance,streaming_ingest}.py`, `src/metrics/{campaign_metrics,vault_fees}.py`.
- Runners/guards: `scripts/run_portfolio.py`, `run_real_campaign.py`, `run_campaign.py`, `derive_verified_universe.py`, `fetch_hyperliquid_candles.py`, `generate_candle_coverage_gap_report.py`.

## RULES (NON-NEGOTIABLE — VIOLATION = SESSION FAILURE)
- Each session ships ≥1 material item with concrete evidence (dated test + gate count + traced values).
- Spec is truth: both legs, ETH hedge every leg, funding/liquidation on every leg and exit path, $5M gating, 1.25% sizing in spec paths, equal-share cuts old+new, stopped buy never opens rebound short.
- Fail-closed: missing provenance/verification on the real path → reject. Never fabricate data or results.
- Do not commit unless the user explicitly asks.

**END OF HANDOFF — THIS IS THE ONLY DURABLE CONTEXT. NEXT SESSION MUST EXECUTE THE INITIAL TASK ABOVE OR FAIL. (2026-11-13T00:29:50Z)**