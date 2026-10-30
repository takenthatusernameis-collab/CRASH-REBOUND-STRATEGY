# CRASH-REBOUND-STRATEGY — Durable Session Handoff
**TIMESTAMP:** 2026-10-30T01:42:35Z
**REPO:** CRASH-REBOUND-STRATEGY
**BRANCH:** main
**WORKING TREE:** clean
**TEST BASELINE:** 58 passed, 0 failed (`/usr/share/miniconda/bin/python -m pytest -q`)

## Purpose (from repo name)
Backtester for a crash-rebound trading strategy (Hyperliquid hourly perps): buy liquid coins after a crash signal, exit at +9% target or 50h time exit, then open a rebound short; ATR(14)*8 safety stop; 120% gross cap with equal-share cuts; ETH hedge per leg. Spec resolved from `crash-rebound-strategy.pdf` into `research_state/strategy_spec.md`.

**Repo-name mandate — BOTH LEGS ARE NON-NEGOTIABLE:** long crash entry AND rebound short. Any session that only touches the long leg is off-mission.

## Current verified state
- `strategy_spec.md`: resolved PDF rules (+9% target, 50h/48h exits, ATR*8 stop, sizing, 120% cap, ETH hedge). Notes RSI(21h)<20 trigger; implementation still uses price-drop/fallback logic in places.
- `src/strategy/crash_rebound.py`: ATR-based stop wired; target uses `config.target_pct` (+9%) by default.
- `src/strategy/risk.py`: RiskState/DailyRiskState, gross cap `cut_positions_to_cap` (equal-share cuts), slippage/commission helpers, ATR.
- `src/backtest/engine.py`: `backtest_simple` with next-bar entry, stop/target/time-exit, look-ahead guard, risk gates; rebound-short logic implemented when long hits +9% target (closes short at -9% target or 48h/time-based; wide stop). Returns `trades` list for multi-leg with both legs logged.
- `src/data/loader.py`: fixtures `make_fixture_crash_rebound()`, `make_fixture_crash_rebound_multi()`.
- Tests: 58 passing. Rebound-short paths exist and are tested.

## BOTTLENECKS TO REMOVE (IN ORDER - MUST RESOLVE)
1. **Short slippage/commission convention** (`src/backtest/engine.py`) - `_slippage_commission_per_share` usage for short entry (sell-to-open) and cover (buy-to-cover) is unverified. Lock convention with explicit tests.
2. **Multi-leg accounting** (`src/backtest/engine.py`) - `r_multiple` uses `total_risk = risk * shares * 2.0` as hack. Define correct convention and fix with tests.
3. **Cap logic not wired** (`src/backtest/engine.py`, `src/strategy/risk.py`) - `cut_positions_to_cap` exists but not enforced across multi-position/multi-symbol flows. Wire with tests.
4. **Trigger mismatch** (`src/strategy/crash_rebound.py`, `research_state/strategy_spec.md`) - Spec requires RSI(21h)<20; align implementation with flag + fallback.
5. **Tool constraint** - Avoid malformed `edit` calls (must include `filePath`, `oldString`, `newString`).

## SINGLE DURABLE HANDOFF MESSAGE FOR NEXT AGENTIC SESSION (START HERE — NO DEFERRALS)
**TIMESTAMP:** 2026-10-30T01:42:35Z
**FOCUS CAMPAIGN:** CRASH-REBOUND-STRATEGY — HARDEN BOTH LEGS TO MATCH MANDATE (CORRECTNESS BEFORE EXPANSION)

### MANDATORY FIRST STEP (BLOCKING)
1. Run tests: `/usr/share/miniconda/bin/python -m pytest -q` — confirm 58 green and record exact count. **Do not proceed until green.**

### P0 — LOCK REBOUND-SHORT CORRECTNESS (BLOCKING, BOTH LEGS) [HIGHEST PRIORITY]
- [ ] **Audit convention**: Trace `_slippage_commission_per_share` and engine usage for short entry (`side='sell'`) and cover (`side='buy'`). Document expected PnL formula in code comments if clarifying.
- [ ] **Precise short PnL tests**: Add behavior tests with explicit prices/costs proving PnL = (short_entry_px - short_exit_px)*shares with correct slippage/commission. Cover sell-to-open and buy-to-cover.
- [ ] **Trades structure**: Assert `trades` contains both legs with correct `side`/`entry`/`exit`/`pnl`/`reason` when rebound occurs.
- [ ] **Fix if off**: Correct signs/convention if tests fail.
- [ ] **Fix multi-leg r_multiple**: Replace hack with correct convention (based on risk per leg or total risk definition). Add tests.
**Target:** +4-6 behavior tests. Unblock trust in rebound leg.

### P1 — ENFORCE 120% GROSS CAP WITH EQUAL-SHARE CUTS
- [ ] **Wire cap**: Enforce `RiskState.cut_positions_to_cap` in engine/multi-symbol flows when combined gross > 120% of equity (equal-share reduction, never top-up).
- [ ] **Track gross**: Correctly track gross exposure across open positions/trades.
- [ ] **Tests**: Add multi-position cap test asserting sizes/gross before/after cuts.
**Target:** +2-4 tests.

### P2 — ALIGN CRASH TRIGGER TO RSI(21h)<20
- [ ] **RSI helper**: Add RSI(21h)<20 trigger path in `src/strategy/crash_rebound.py` with config flag; keep price-based as fallback.
- [ ] **Spec sync**: Update `research_state/strategy_spec.md` to reflect implementation state.
- [ ] **Tests**: Add tests for RSI trigger firing and fallback behavior.
**Target:** +2-4 tests.

### P3 — MULTI-SYMBOL FIXTURES & COVERAGE TO >=70
- [ ] **Expand fixtures**: Add liquid-coin style cases and run multi-symbol backtest.
- [ ] **Smoke results**: Update `research_state/backtest_smoke.json`; assert non-NO_TRADE produce trades/legs as expected.
- [ ] **Multi-symbol tests**: Add behavior tests.
- [ ] **Grow suite**: Add focused behavior tests for above. Prefer behavior assertions over smoke-only.
**Target:** >= 70 total tests.

### VERIFICATION GATE (END OF SESSION — MANDATORY)
- [ ] `/usr/share/miniconda/bin/python -m pytest -q` green with exact count recorded (must be >= 58 and trending to >= 70).
- [ ] Both legs exercised in relevant tests; P0 items have passing behavior tests.
- [ ] Update this handoff with new timestamp, test count, what was done/blocked, concrete next action.
- [ ] No uncommitted large experimental artifacts outside `research_state/*`, `src/*`, `tests/*`, `scripts/*`.

### DO-NOT-ESCALATE
- Do not cancel/force-push/escalate in-progress runs without explicit user direction.
- Workflow-file changes remain blocked by GITHUB_TOKEN scope; commit/push only regular files.
