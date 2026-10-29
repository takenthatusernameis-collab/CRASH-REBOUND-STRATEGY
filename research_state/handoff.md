# CRASH-REBOUND-STRATEGY — Durable Session Handoff

**TIMESTAMP:** 2026-10-29T23:45:25Z
**REPO:** CRASH-REBOUND-STRATEGY
**BRANCH:** main
**WORKING TREE:** clean, up to date with origin/main

## Purpose (from repo name)
Backtester for a crash-rebound trading strategy (Hyperliquid hourly perps): buy liquid coins after a crash signal, exit at +9% target or 50h time exit, then open a rebound short; ATR(14)*8 safety stop; 120% gross cap with equal-share cuts; ETH hedge per leg. Spec resolved from `crash-rebound-strategy.pdf` into `research_state/strategy_spec.md`.

## Current verified state
- Tests: **46 passed, 7 failed** (`python3 -m pytest -q`). Bottleneck: `generate_signal` returns None on crash-rebound fixture after recent engine rewrite — fix before Priority 1.
- `strategy_spec.md`: resolved PDF rules (RSI<20/21h trigger context, +9% target, 50h/48h exits, ATR*8 stop, 1.25% of daily vol sizing, 120% cap w/ equal cuts, ETH hedge).
- `src/strategy/crash_rebound.py`: ATR-based stop wired (`atr`/`safety_stop_price`, fallback `low*0.999`); target prefers `config.target_pct` (+9%).
- `src/strategy/risk.py`: `RiskState`/`DailyRiskState`, gross cap `cut_positions_to_cap` (equal cuts), slippage/commission, ATR.
- `src/backtest/engine.py`: `backtest_simple` with next-bar entry, stop/target/time-exit, look-ahead guard, risk gates.
- `src/data/loader.py`: fixtures `make_fixture_crash_rebound()` + `make_fixture_crash_rebound_multi()` (SPY/QQQ/IWM + NO_TRADE).
- `research_state/backtest_smoke.json`: multi_symbol SPY/QQQ/IWM all `time_exit` (small negative pnl in short fixtures); NO_TRADE no signal. Aggregate: 3 symbols tested, 3 signals.
- Ledger `research_state/workflow_run_diagnostics.jsonl`: run #40845157948 committed+pushed to origin/main (commit `4c62f0e`).
- Bottleneck removed: previous handoff was corrupted (interleaved timestamps) — now clean and durable. Run #40845157948 resolved; no blocked sessions remain.

## INITIAL TASK MESSAGE (timestamped 2026-10-29T22:46:59Z) — START HERE, NO DEFERRALS

**PRIORITY 1 — IMPLEMENT REBOUND-SHORT LOGIC (CORE TO "CRASH-REBOUND"):**
Run `python3 -m pytest -q` first to confirm 53 green. Implement the full rebound-short flow per `research_state/strategy_spec.md`: when a buy trade exits at +9% target (fast/target hit), immediately open a short on the same coin/symbol; close the short at -9% (target for short, i.e. entry_short*(1-0.09)) or after 48h, whichever comes first. Wire through `src/strategy/crash_rebound.py` and/or `src/backtest/engine.py` (choose the cleanest place that matches existing patterns). Add concrete tests covering target-hit -> short-open -> short-close (by -9% or 48h). Do **not** defer to "later" — this is the missing half of the strategy name. Keep suite green.

**Why this is Priority 1:** The repo name is CRASH-REBOUND-STRATEGY. The crash/buy half is implemented. The rebound-short half is NOT implemented. Without it, the strategy is incomplete by definition. This is the single highest-leverage item — do not substitute with lower-priority campaign items.

## NEXT SESSION FOCUS CAMPAIGN (heavy work — must complete in order; each item requires code + tests)
Do not substitute with low-effort checkpoints. Run `python3 -m pytest -q` after every change; all tests must stay green. Grow suite toward 70+.

1. **[PRIORITY 1] Rebound-short logic (PDF §"Exit - Rebound short")** — When buy exits at +9% target fast, open short on same coin; close at -9% or after 48h. Gate: only when buy hit +9% target. Add tests.
2. **[PRIORITY 2] 120% gross cap with equal-share cuts in multi-trade flow** — Wire `RiskState.cut_positions_to_cap` into engine/multi-symbol flow; when over capacity cut equally (never top up). Add multi-position cap test.
3. **[PRIORITY 3] Align crash trigger to RSI(21h)<20** — Add RSI(21h)<20 trigger option/path to match PDF (keep existing price-based as fallback or make configurable). Update `strategy_spec.md` to reflect final alignment.
4. **[PRIORITY 4] Expand multi-symbol backtests & fixtures** — Add more liquid-coin fixtures beyond SPY/QQQ/IWM; run multi-symbol backtest; update `research_state/backtest_smoke.json`. Assert non-NO_TRADE produce results.
5. **[PRIORITY 5] Grow test suite toward 70+** — Each item above must add tests; track count, all green.

## Verification gate for end of session
- `python3 -m pytest -q` green
- Campaign items progressed with tests added; suite count >= previous (53) and trending to 70+
- This handoff updated with new timestamp and any newly blocked/unblocked items before session end

## Do-not-escalate list
- Do not cancel/force-push/escalate an in-progress run without explicit user direction.
- Workflow-file changes remain blocked by GITHUB_TOKEN scope; commit/push only regular files (`research_state/*`, `src/*`, `tests/*`, `scripts/*`).
