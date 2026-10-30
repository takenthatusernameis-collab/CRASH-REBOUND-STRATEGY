# CRASH-REBOUND-STRATEGY — Durable Session Handoff
**TIMESTAMP:** 2026-10-30T01:33:36Z
**REPO:** CRASH-REBOUND-STRATEGY
**BRANCH:** main
**WORKING TREE:** clean (commits only via checkpoints; no manual large artifacts)
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

## BOTTLENECKS / KNOWN ISSUES (FIX IF HIT)
- **Short slippage/commission convention**: `_slippage_commission_per_share` adds slip+comm when `side=='buy'`, subtracts when not buy. For short entry (sell-to-open) engine currently passes `'sell'` side (subtracts costs) and for cover passes `'buy'` (adds costs). Verify with explicit unit tests and lock behavior.
- **Multi-leg accounting**: `r_multiple` when both legs exist uses `total_risk = risk * shares * 2.0` as a rough hack - must be fixed with clear convention and tests.
- **Cap logic not wired**: `cut_positions_to_cap` exists in risk but not enforced across multi-position/multi-symbol flows in engine. Must wire and test.
- **Trigger mismatch**: Spec says RSI(21h)<20; implementation needs alignment (config flag + helper + tests).
- **Tool constraint**: Avoid malformed `edit` calls (must include `filePath`, `oldString`, `newString`).

## SINGLE DURABLE HANDOFF MESSAGE FOR NEXT AGENTIC SESSION (START HERE — NO DEFERRALS)
**TIMESTAMP:** 2026-10-30T01:33:36Z
**FOCUS CAMPAIGN:** CRASH-REBOUND-STRATEGY — HARDEN BOTH LEGS TO MATCH REPO MANDATE

### MANDATORY FIRST STEP (BLOCKING)
1. Run tests: `/usr/share/miniconda/bin/python -m pytest -q` — confirm 58 green. **Do not proceed until green.**

### P0 — REBOUND-SHORT HARDENING (HIGHEST PRIORITY, BOTH LEGS MANDATORY)
- [ ] **Precise short PnL tests**: Add behavior tests with explicit expected values for short entry/cover with known prices/costs (prove PnL = (short_entry_px - short_exit_px)*shares with correct slippage/commission application). Cover sell-to-open entry and buy-to-cover exit.
- [ ] **Verify trades structure**: Assert `trades` contains both legs with correct `side`/`entry`/`exit`/`pnl`/`reason` when rebound occurs.
- [ ] **Short convention lock**: Explicitly test `_slippage_commission_per_share` behavior and engine usage for short paths; fix if signs off.
- [ ] **Edge cases**: Short stopped immediately, time-exit boundary (exactly 48h), target hit paths.
**Target:** +4-6 behavior tests.

### P1 — 120% GROSS CAP WITH EQUAL-SHARE CUTS
- [ ] **Wire cap logic**: Enforce `RiskState.cut_positions_to_cap` in engine/multi-symbol flows when combined gross > 120% of equity (equal-share reduction, never top-up).
- [ ] **Track gross exposure**: Correctly track across multiple open positions/trades.
- [ ] **Tests**: Add multi-position cap test with assertions on sizes/gross before/after cuts.
**Target:** +2-4 tests.

### P2 — ALIGN CRASH TRIGGER TO RSI(21h)<20
- [ ] **Implement RSI helper**: Add RSI(21h)<20 trigger path in `src/strategy/crash_rebound.py` with config flag; keep price-based as fallback.
- [ ] **Update spec**: Reflect implementation state in `research_state/strategy_spec.md`.
- [ ] **Tests**: Add tests for RSI trigger firing and fallback behavior.
**Target:** +2-4 tests.

### P3 — MULTI-SYMBOL FIXTURES & BACKTESTS
- [ ] **Expand fixtures**: Add liquid-coin style cases, run multi-symbol backtest.
- [ ] **Update smoke results**: Update `research_state/backtest_smoke.json` with new results; assert non-NO_TRADE produce trades/legs as expected.
- [ ] **Tests**: Add multi-symbol behavior tests.
**Target:** +1-3 tests.

### P4 — GROW SUITE TO 70+
- [ ] Add focused behavior tests for all items above. Prefer behavior assertions over smoke-only.
- [ ] Keep all tests green throughout. Run `/usr/share/miniconda/bin/python -m pytest -q` after every change.
**Target:** >= 70 total tests.

### VERIFICATION GATE (END OF SESSION — MANDATORY)
- [ ] `/usr/share/miniconda/bin/python -m pytest -q` green with count >= 58 and trending to 70+ (record exact count).
- [ ] All campaign items touched have corresponding passing tests.
- [ ] Update this handoff with new timestamp, test count, what was done/blocked, concrete next action.
- [ ] No uncommitted large experimental artifacts outside `research_state/*`, `src/*`, `tests/*`, `scripts/*`.

### DO-NOT-ESCALATE
- Do not cancel/force-push/escalate in-progress runs without explicit user direction.
- Workflow-file changes remain blocked by GITHUB_TOKEN scope; commit/push only regular files.
