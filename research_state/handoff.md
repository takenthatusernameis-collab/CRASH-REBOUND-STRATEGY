# CRASH-REBOUND-STRATEGY — Durable Session Handoff

**TIMESTAMP:** 2026-10-29T23:48:18Z
**REPO:** CRASH-REBOUND-STRATEGY
**BRANCH:** main
**WORKING TREE:** clean

## Purpose (from repo name)
Backtester for a crash-rebound trading strategy (Hyperliquid hourly perps): buy liquid coins after a crash signal, exit at +9% target or 50h time exit, then open a rebound short; ATR(14)*8 safety stop; 120% gross cap with equal-share cuts; ETH hedge per leg. Spec resolved from `crash-rebound-strategy.pdf` into `research_state/strategy_spec.md`.

## Current verified state
- Tests: **53 passed, 0 failed** (`python3 -m pytest -q`). Bottleneck fixed (generate_signal was missing return).
- `strategy_spec.md`: resolved PDF rules (+9% target, time exits, ATR*8 stop, sizing, 120% cap, ETH hedge context).
- `src/strategy/crash_rebound.py`: ATR-based stop wired; target uses `config.target_pct` (+9%) by default; `generate_signal` returns Signal correctly; `backtest_crash_rebound` convenience added.
- `src/strategy/risk.py`: RiskState/DailyRiskState, gross cap `cut_positions_to_cap`, slippage/commission helpers, ATR.
- `src/backtest/engine.py`: `backtest_simple` with next-bar entry, stop/target/time-exit, look-ahead guard, risk gates; rebound-short logic implemented when long hits +9% target (closes short at -9% target or 48h/time-based; wide stop). Returns `trades` list for multi-leg.
- `src/data/loader.py`: fixtures `make_fixture_crash_rebound()`, `make_fixture_crash_rebound_multi()` (SPY/QQQ/IWM + NO_TRADE).
- `research_state/backtest_smoke.json`: present with prior multi-symbol results.
- Ledger: `research_state/workflow_run_diagnostics.jsonl` tracks runs.

## INITIAL TASK MESSAGE (timestamped 2026-10-29T23:48:18Z) — START HERE, NO DEFERRALS

**PRIORITY 1 — HARDEN REBOUND-SHORT + MULTI-LEG ACCOUNTING (CORE TO "CRASH-REBOUND"):**
Run `python3 -m pytest -q` first (must stay 53 green). Focus on making rebound-short behavior robust and testable:
1. Ensure rebound-short uses correct side conventions for slippage/commission on entry (short entry) and cover (buy to close). Verify pnl math matches spec.
2. Add/strengthen tests for target-hit -> short-open -> short-close paths (target -9%, time-exit 48h, stop case) with concrete fixtures.
3. Make TradeResult/trades accounting unambiguous for multi-leg (r_multiple across both legs or clearly documented). Keep API compatible.
4. Wire config flags (`enable_rebound_short`, `rebound_short_target_pct`, `rebound_short_time_exit_bars`) explicitly in tests.

**Why:** Repo name requires both legs. Current implementation exists but needs hardening/tests to prevent regressions as suite grows.

## NEXT SESSION FOCUS CAMPAIGN (heavy work — must complete in order)
Run `python3 -m pytest -q` after every change; all tests must stay green. Grow suite toward 70+.

1. **[PRIORITY 1] Rebound-short hardening + tests** — Validate slippage/commission for short entry/cover, add multi-leg tests (target -9%, 48h time exit, stop). Ensure TradeResult.r_multiple and trades list correct.
2. **[PRIORITY 2] 120% gross cap with equal-share cuts in multi-trade flow** — Wire `RiskState.cut_positions_to_cap` into engine/multi-symbol flow; when over capacity cut equally (never top up). Add multi-position cap test.
3. **[PRIORITY 3] Align crash trigger to RSI(21h)<20** — Add RSI(21h)<20 trigger path (keep price-based as fallback/configurable). Update `strategy_spec.md` and add tests.
4. **[PRIORITY 4] Expand multi-symbol backtests & fixtures** — Add more liquid-coin fixtures; run multi-symbol backtest; update `research_state/backtest_smoke.json`. Assert non-NO_TRADE produce results.
5. **[PRIORITY 5] Grow test suite toward 70+** — Each item above must add tests; track count, all green.

## Verification gate for end of session
- `python3 -m pytest -q` green (53+)
- Campaign items progressed with tests added; suite count trending to 70+
- This handoff updated with new timestamp and any newly blocked/unblocked items before session end

## Do-not-escalate list
- Do not cancel/force-push/escalate an in-progress run without explicit user direction.
- Workflow-file changes remain blocked by GITHUB_TOKEN scope; commit/push only regular files (`research_state/*`, `src/*`, `tests/*`, `scripts/*`).
