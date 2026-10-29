# CRASH-REBOUND-STRATEGY — Durable Session Handoff

**TIMESTAMP:** 2026-10-29T23:54:30Z
**REPO:** CRASH-REBOUND-STRATEGY
**BRANCH:** main
**WORKING TREE:** clean (uncommitted changes only to tests/ as needed)
**TEST BASELINE:** 58 passed, 0 failed (`python3 -m pytest -q`)

## Purpose (from repo name)
Backtester for a crash-rebound trading strategy (Hyperliquid hourly perps): buy liquid coins after a crash signal, exit at +9% target or 50h time exit, then open a rebound short; ATR(14)*8 safety stop; 120% gross cap with equal-share cuts; ETH hedge per leg. Spec resolved from `crash-rebound-strategy.pdf` into `research_state/strategy_spec.md`.

## Current verified state
- `strategy_spec.md`: resolved PDF rules (+9% target, time exits, ATR*8 stop, sizing, 120% cap, ETH hedge context). Needs alignment to RSI(21h)<20 trigger.
- `src/strategy/crash_rebound.py`: ATR-based stop wired; target uses `config.target_pct` (+9%) by default; `generate_signal` returns Signal correctly; `backtest_crash_rebound` convenience added.
- `src/strategy/risk.py`: RiskState/DailyRiskState, gross cap `cut_positions_to_cap` (equal-share cuts), slippage/commission helpers, ATR.
- `src/backtest/engine.py`: `backtest_simple` with next-bar entry, stop/target/time-exit, look-ahead guard, risk gates; rebound-short logic implemented when long hits +9% target (closes short at -9% target or 48h/time-based; wide stop). Returns `trades` list for multi-leg with both legs logged.
- `src/data/loader.py`: fixtures `make_fixture_crash_rebound()`, `make_fixture_crash_rebound_multi()` (SPY/QQQ/IWM + NO_TRADE).
- `research_state/backtest_smoke.json`: present with prior multi-symbol results.
- Tests: 58 passing (grew from 53). Added comprehensive rebound-short tests (slippage/commission, target hit, stop, time exit, disabled).

## INITIAL TASK MESSAGE (timestamped 2026-10-29T23:54:30Z) — START HERE, NO DEFERRALS

**MANDATORY FIRST STEP (BLOCKING):**
1. `python3 -m pytest -q` — confirm 58 green. If anything regresses, fix before moving to campaign. **Do not proceed until green.**

**PRIORITY 1 — HARDEN CRASH→REBOUND PIPELINE (CORE TO REPO IDENTITY - BOTH LEGS MANDATORY):**
The repo name demands BOTH legs (long crash entry + rebound short). Treat as non-negotiable. Strengthen aggressively:
1. **Short math correctness:** Explicitly verify short entry uses correct side for slippage/commission; verify cover uses correct side. Add unit tests for PnL on short entry/cover with known fills (prove numbers).
2. **Multi-leg lifecycle:** Tests for target-hit → short-open → close paths: (a) short hits -9% target, (b) 48h/time-exit, (c) stop hit. Assert `trades` contains both legs with correct direction/qty/pnl/r_multiple. Add assertions for accounting across both legs.
3. **Config plumbing:** Explicitly exercise `enable_rebound_short`, `rebound_short_target_pct`, `rebound_short_time_exit_bars`, `rebound_short_stop_pct` in tests.
4. **Accounting clarity:** Make TradeResult/trades unambiguous for multi-leg (document/assert r_multiple across both legs). Keep API backward compatible.

**BOTTLENECKS TO REMOVE (if present):**
- If short/cover slippage conventions are unclear, fix in engine with tests proving correct PnL sign/convention.
- If multi-leg r_multiple calculation looks off under short leg, correct with concrete assertions.
- Do not skip failing cases - fix root cause.

## NEXT SESSION FOCUS CAMPAIGN (HEAVY WORK — COMPLETE IN ORDER, NO SKIPPING)
Run `python3 -m pytest -q` after EVERY change. All tests must stay green. Grow suite toward 70+ with concrete, behavior-asserting tests. **Do heavy work; do not do trivial-only passes.**

### P0: Rebound-short hardening (IN PROGRESS/CONTINUE)
- [ ] Add more precise short PnL tests with explicit expected values (entry/exit prices + costs).
- [ ] Verify trades list structure is stable and documented via assertions.
- [ ] Ensure short uses sell-to-open with correct cost application on entry and buy-to-cover on exit.
- Target: +2-4 more behavior tests.

### P1: 120% gross cap with equal-share cuts in multi-trade flow
- [ ] Wire `RiskState.cut_positions_to_cap` through engine/multi-symbol path when combined gross > 120% of equity (equal-share reduction, never top-up).
- [ ] Track gross exposure correctly across multiple open positions/trades.
- [ ] Add multi-position cap test with assertions on sizes/gross before/after cuts.
- [ ] Ensure risk checks interact correctly with cap logic.

### P2: Align crash trigger to RSI(21h)<20
- [ ] Implement RSI(21h)<20 trigger path in `src/strategy/crash_rebound.py` (or add helper). Keep existing price-based as fallback/configurable.
- [ ] Update `research_state/strategy_spec.md` to match actual implementation/intent.
- [ ] Add tests for RSI trigger firing and fallback behavior.
- [ ] Make trigger selection explicit via config.

### P3: Expand multi-symbol fixtures/backtests
- [ ] Add liquid-coin style fixtures (more symbols/cases), run multi-symbol backtest.
- [ ] Update `research_state/backtest_smoke.json` with new results; assert non-NO_TRADE symbols produce trades/legs.
- [ ] Add tests exercising multi-symbol flows.

### P4: Systematic suite growth to 70+
- [ ] For each item above add focused behavior tests; track count explicitly.
- [ ] Prefer behavior tests over smoke-only assertions.
- [ ] Keep all tests green throughout.

## VERIFICATION GATE (END OF SESSION — MANDATORY)
- `python3 -m pytest -q` green with count >= 58 and trending to 70+ (record exact count in handoff if changed).
- All campaign items touched have corresponding tests added/passing.
- Update this handoff: new timestamp, test count, what was done/blocked, concrete next action for subsequent session.
- No uncommitted large experimental artifacts outside `research_state/*`, `src/*`, `tests/*`, `scripts/*`.

## DO-NOT-ESCALATE LIST
- Do not cancel/force-push/escalate in-progress runs without explicit user direction.
- Workflow-file changes remain blocked by GITHUB_TOKEN scope; commit/push only regular files (`research_state/*`, `src/*`, `tests/*`, `scripts/*`).
