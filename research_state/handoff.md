# CRASH-REBOUND-STRATEGY — Durable Session Handoff

**TIMESTAMP:** 2026-10-30T00:50:31Z
**REPO:** CRASH-REBOUND-STRATEGY
**BRANCH:** main
**WORKING TREE:** clean (commits only via checkpoints; no manual large artifacts)
**TEST BASELINE:** 58 passed, 0 failed (`python3 -m pytest -q`)

## Purpose (from repo name)
Backtester for a crash-rebound trading strategy (Hyperliquid hourly perps): buy liquid coins after a crash signal, exit at +9% target or 50h time exit, then open a rebound short; ATR(14)*8 safety stop; 120% gross cap with equal-share cuts; ETH hedge per leg. Spec resolved from `crash-rebound-strategy.pdf` into `research_state/strategy_spec.md`.

## Current verified state
- `strategy_spec.md`: resolved PDF rules (+9% target, 50h/48h exits, ATR*8 stop, sizing, 120% cap, ETH hedge). Notes RSI(21h)<20 trigger and ATR-based stop; implementation still uses price-drop/fallback logic in places.
- `src/strategy/crash_rebound.py`: ATR-based stop wired; target uses `config.target_pct` (+9%) by default; `generate_signal` returns Signal correctly; `backtest_crash_rebound` convenience added.
- `src/strategy/risk.py`: RiskState/DailyRiskState, gross cap `cut_positions_to_cap` (equal-share cuts), slippage/commission helpers, ATR.
- `src/backtest/engine.py`: `backtest_simple` with next-bar entry, stop/target/time-exit, look-ahead guard, risk gates; rebound-short logic implemented when long hits +9% target (closes short at -9% target or 48h/time-based; wide stop). Returns `trades` list for multi-leg with both legs logged.
- `src/data/loader.py`: fixtures `make_fixture_crash_rebound()`, `make_fixture_crash_rebound_multi()` (SPY/QQQ/IWM + NO_TRADE).
- `research_state/backtest_smoke.json`: present with prior multi-symbol results.
- Tests: 58 passing. Rebound-short paths exist but need hardening against sign/convention errors.

## BOTTLENECKS REMOVED / IDENTIFIED (MUST FIX IF HIT)
- **Short slippage/commission convention**: `_slippage_commission_per_share` adds slip+comm when `side=='buy'`, subtracts when not buy. For short entry (sell-to-open) and short cover (buy-to-cover), the code must use the correct sides explicitly. If PnL signs look off, fix in engine with deterministic unit tests proving values.
- **Multi-leg accounting**: `r_multiple` when both legs exist must be unambiguous (ideally total PnL / (total risk allocated) or documented consistently). Do not guess; add assertions that lock the convention.
- **Cap logic not wired**: `cut_positions_to_cap` exists in risk but not obviously enforced across multi-position/multi-symbol flows in engine. Must wire and test.
- **Trigger mismatch**: Spec says RSI(21h)<20; implementation needs alignment (config flag + helper + tests).

## INITIAL TASK MESSAGE (timestamped 2026-10-30T00:50:31Z) — START HERE, NO DEFERRALS

**MANDATORY FIRST STEP (BLOCKING):**
1. `python3 -m pytest -q` — confirm 58 green. If anything regresses, fix before moving to campaign. **Do not proceed until green.**

**PRIORITY 1 — HARDEN CRASH→REBOUND PIPELINE (CORE TO REPO IDENTITY - BOTH LEGS MANDATORY):**
The repo name demands BOTH legs (long crash entry + rebound short). Treat as non-negotiable. Strengthen aggressively:
1. **Short math correctness:** Explicitly verify short entry uses correct side for slippage/commission; verify cover uses correct side. Add unit tests for PnL on short entry/cover with known fills (prove numbers). Test with concrete prices/costs.
2. **Multi-leg lifecycle:** Tests for target-hit → short-open → close paths: (a) short hits -9% target, (b) 48h/time-exit, (c) stop hit. Assert `trades` contains both legs with correct direction/qty/pnl/r_multiple. Add assertions for accounting across both legs.
3. **Config plumbing:** Explicitly exercise `enable_rebound_short`, `rebound_short_target_pct`, `rebound_short_time_exit_bars`, `rebound_short_stop_pct` in tests (enable/disable paths).
4. **Accounting clarity:** Make TradeResult/trades unambiguous for multi-leg. If r_multiple needs adjustment for total risk, fix with tests; keep API backward compatible.

## NEXT SESSION FOCUS CAMPAIGN (HEAVY WORK — COMPLETE IN ORDER, NO SKIPPING)
Run `python3 -m pytest -q` after EVERY change. All tests must stay green. Grow suite toward 70+ with concrete, behavior-asserting tests. **Do heavy work; do not do trivial-only passes.**

### P0: Rebound-short hardening (CONTINUE - HIGHEST PRIORITY)
- [ ] Add precise short PnL tests with explicit expected values (entry/exit prices + costs). Cover both entry and cover.
- [ ] Verify trades list structure is stable and documented via assertions (both legs present when rebound occurs).
- [ ] Ensure short uses correct convention (sell-to-open on entry, buy-to-cover on exit) with slippage/commission applied correctly.
- [ ] Test edge cases: short stopped immediately? time exit boundary (exactly 48h).
- Target: +4-6 behavior tests.

### P1: 120% gross cap with equal-share cuts in multi-trade flow
- [ ] Wire `RiskState.cut_positions_to_cap` through engine/multi-symbol path when combined gross > 120% of equity (equal-share reduction, never top-up).
- [ ] Track gross exposure correctly across multiple open positions/trades.
- [ ] Add multi-position cap test with assertions on sizes/gross before/after cuts.
- [ ] Ensure risk checks interact correctly with cap logic (blocked vs cut behavior).
- Target: +2-4 tests.

### P2: Align crash trigger to RSI(21h)<20
- [ ] Implement RSI(21h)<20 trigger path in `src/strategy/crash_rebound.py` (add helper). Keep existing price-based as fallback/configurable via config flag.
- [ ] Update `research_state/strategy_spec.md` to reflect implementation state.
- [ ] Add tests for RSI trigger firing and fallback behavior.
- [ ] Make trigger selection explicit via config.
- Target: +2-4 tests.

### P3: Expand multi-symbol fixtures/backtests
- [ ] Add liquid-coin style fixtures (more symbols/cases), run multi-symbol backtest.
- [ ] Update `research_state/backtest_smoke.json` with new results; assert non-NO_TRADE symbols produce trades/legs where expected.
- [ ] Add tests exercising multi-symbol flows.
- Target: +1-3 tests.

### P4: Systematic suite growth to 70+
- [ ] For each item above add focused behavior tests; track count explicitly.
- [ ] Prefer behavior tests over smoke-only assertions.
- [ ] Keep all tests green throughout.
- Target: reach >= 70 total, with clear behavior coverage.

## VERIFICATION GATE (END OF SESSION — MANDATORY)
- `python3 -m pytest -q` green with count >= 58 and trending to 70+ (record exact count in handoff if changed).
- All campaign items touched have corresponding tests added/passing.
- Update this handoff: new timestamp, test count, what was done/blocked, concrete next action for subsequent session.
- No uncommitted large experimental artifacts outside `research_state/*`, `src/*`, `tests/*`, `scripts/*`.

## DO-NOT-ESCALATE LIST
- Do not cancel/force-push/escalate in-progress runs without explicit user direction.
- Workflow-file changes remain blocked by GITHUB_TOKEN scope; commit/push only regular files (`research_state/*`, `src/*`, `tests/*`, `scripts/*`).
