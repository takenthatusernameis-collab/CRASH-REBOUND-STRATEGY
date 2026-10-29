# CRASH-REBOUND-STRATEGY — Durable Session Handoff

**TIMESTAMP:** 2026-10-29T23:51:00Z
**REPO:** CRASH-REBOUND-STRATEGY
**BRANCH:** main
**WORKING TREE:** clean
**TEST BASELINE:** 53 passed, 0 failed (`python3 -m pytest -q`)

## Purpose (from repo name)
Backtester for a crash-rebound trading strategy (Hyperliquid hourly perps): buy liquid coins after a crash signal, exit at +9% target or 50h time exit, then open a rebound short; ATR(14)*8 safety stop; 120% gross cap with equal-share cuts; ETH hedge per leg. Spec resolved from `crash-rebound-strategy.pdf` into `research_state/strategy_spec.md`.

## Current verified state
- `strategy_spec.md`: resolved PDF rules (+9% target, time exits, ATR*8 stop, sizing, 120% cap, ETH hedge context).
- `src/strategy/crash_rebound.py`: ATR-based stop wired; target uses `config.target_pct` (+9%) by default; `generate_signal` returns Signal correctly; `backtest_crash_rebound` convenience added.
- `src/strategy/risk.py`: RiskState/DailyRiskState, gross cap `cut_positions_to_cap`, slippage/commission helpers, ATR.
- `src/backtest/engine.py`: `backtest_simple` with next-bar entry, stop/target/time-exit, look-ahead guard, risk gates; rebound-short logic implemented when long hits +9% target (closes short at -9% target or 48h/time-based; wide stop). Returns `trades` list for multi-leg.
- `src/data/loader.py`: fixtures `make_fixture_crash_rebound()`, `make_fixture_crash_rebound_multi()` (SPY/QQQ/IWM + NO_TRADE).
- `research_state/backtest_smoke.json`: present with prior multi-symbol results.
- Ledger: `research_state/workflow_run_diagnostics.jsonl` tracks runs.

## INITIAL TASK MESSAGE (timestamped 2026-10-29T23:51:00Z) — START HERE, NO DEFERRALS

**MANDATORY FIRST STEP (BLOCKING):**
1. `python3 -m pytest -q` — confirm 53 green. If anything regresses, fix before moving to campaign.

**PRIORITY 1 — HARDEN CRASH→REBOUND PIPELINE (CORE TO REPO IDENTITY):**
The repo name demands BOTH legs (long crash entry + rebound short). Treat this as non-negotiable:
1. **Short math correctness:** Verify short entry uses correct side for slippage/commission; verify cover uses correct side. Add explicit unit tests for PnL on short entry/cover with known fills.
2. **Multi-leg lifecycle:** Add tests for target-hit -> short-open -> close paths: (a) short hits -9% target, (b) 48h/time-exit, (c) stop hit. Assert `trades` contains both legs with correct direction/qty/pnl/r_multiple.
3. **Config plumbing:** Explicitly exercise `enable_rebound_short`, `rebound_short_target_pct`, `rebound_short_time_exit_bars` in tests (do not leave untested).
4. **Accounting clarity:** Make TradeResult/trades unambiguous for multi-leg (document or assert r_multiple across both legs). Keep API backward compatible.

**Why:** Both legs are the defining behavior. Strengthen before expanding scope.

## NEXT SESSION FOCUS CAMPAIGN (HEAVY WORK — COMPLETE IN ORDER, NO SKIPPING)
Run `python3 -m pytest -q` after EVERY change. All tests must stay green. Grow suite toward 70+ with concrete, behavior-asserting tests.

1. **[P0] Rebound-short hardening + tests** (immediate) — Slippage/commission for short/cover, lifecycle tests above, config flags, multi-leg accounting. Target: +3-6 tests.
2. **[P1] 120% gross cap with equal-share cuts in multi-trade flow** — Wire `RiskState.cut_positions_to_cap` through engine/multi-symbol path when combined gross > 120% of equity (equal-share reduction, never top-up). Add multi-position cap test with assertions on sizes/gross.
3. **[P2] Align crash trigger to RSI(21h)<20** — Implement RSI(21h)<20 trigger path; keep existing price-based as fallback/configurable. Update `research_state/strategy_spec.md` to match. Add tests for RSI trigger firing and fallback.
4. **[P3] Expand multi-symbol fixtures/backtests** — Add liquid-coin fixtures, run multi-symbol backtest, update `research_state/backtest_smoke.json` with new results; assert non-NO_TRADE symbols produce trades/legs.
5. **[P4] Systematic suite growth to 70+** — For each item above add focused tests; track count explicitly. Prefer behavior tests over smoke-only assertions.

## BOTTLENECK REMOVAL RULES
- If multiple items blocked, do P0 first (rebound-short) before cap/RSI/fixtures.
- If engine and risk logic conflict on multi-leg, fix engine accounting first (tests will reveal). Do not paper over with skips.
- Keep changes minimal and compatible; do not refactor unrelated modules.

## VERIFICATION GATE (END OF SESSION — MANDATORY)
- `python3 -m pytest -q` green with count >= 53 and trending to 70+ (record count in handoff if changed)
- All campaign items touched have corresponding tests added/passing
- Update this handoff: new timestamp, test count, what was done/blocked, and concrete next action for subsequent session
- No uncommitted large experimental artifacts outside `research_state/*`, `src/*`, `tests/*`, `scripts/*`

## DO-NOT-ESCALATE LIST
- Do not cancel/force-push/escalate in-progress runs without explicit user direction.
- Workflow-file changes remain blocked by GITHUB_TOKEN scope; commit/push only regular files (`research_state/*`, `src/*`, `tests/*`, `scripts/*`).
