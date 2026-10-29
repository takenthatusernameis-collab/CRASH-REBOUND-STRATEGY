# CRASH-REBOUND-STRATEGY — Durable Session Handoff

**TIMESTAMP:** 2026-10-29T22:44:12Z
**REPO:** CRASH-REBOUND-STRATEGY
**BRANCH:** main
**WORKING TREE:** clean, up to date with origin/main

## Purpose (from repo name)
Backtester for a crash-rebound trading strategy (Hyperliquid hourly perps): buy liquid coins after a crash signal, exit at +9% target or 50h time exit, then optionally open a rebound short; ATR(14)*8 safety stop; 120% gross cap with equal-share cuts; ETH hedge per leg. Spec resolved from `crash-rebound-strategy.pdf` into `research_state/strategy_spec.md`.

## Current verified state
- Tests: **53 passed** (`python3 -m pytest -q`, 0.62s). Was 51; +2 tests (ATR stop breach -> stopped; multi-symbol fixtures).
- `strategy_spec.md`: resolved PDF rules (RSI<20/21h trigger context, +9% target, 50h/48h exits, ATR*8 stop, 1.25% of daily vol sizing, 120% cap w/ equal cuts, ETH hedge).
- `src/strategy/crash_rebound.py`: ATR-based stop wired (`atr`/`safety_stop_price`, fallback `low*0.999`); target prefers `config.target_pct` (+9%).
- `src/strategy/risk.py`: `RiskState`/`DailyRiskState`, gross cap `cut_positions_to_cap` (equal cuts), slippage/commission, ATR.
- `src/backtest/engine.py`: `backtest_simple` with next-bar entry, stop/target/time-exit, look-ahead guard, risk gates.
- `src/data/loader.py`: fixtures `make_fixture_crash_rebound()` + `make_fixture_crash_rebound_multi()` (SPY/QQQ/IWM + NO_TRADE).
- `research_state/backtest_smoke.json`: multi_symbol SPY/QQQ/IWM all `time_exit` (small negative pnl in short fixtures); NO_TRADE no signal. Aggregate: 3 symbols tested, 3 signals.
- `research_state/run_40845157948_jobs.json`: job `kilo` **completed/success** (2026-10-29T13:50:39Z -> 19:41:45Z).
- Ledger `research_state/workflow_run_diagnostics.jsonl`: run #40845157948 appended as success and **committed+pushed to origin/main** (commit `4c62f0e`). Previous cancelled runs 40898202894 / 40406455865 / 40590666345 noted.
- Bottleneck removed: previous `handoff.md` was corrupted (every character interleaved with `**TIMESTAMP:** 2026-10-29T21:50:00Z`), making it unreadable. This file is now clean and durable.

## Immediate unfinished item
- **RESOLVED.** Run #40845157948 ledger record + handoff committed and pushed to origin/main via `python3 scripts/finalize_run.py 40845157948` (commit `4c62f0e`, pushed). No outstanding immediate item.

## INITIAL TASK MESSAGE (timestamped 2026-10-29T22:44:12Z)
Start immediately with campaign item 1 (rebound-short logic). Run `python3 -m pytest -q` first to confirm 53 green, then implement short-open on +9% target hit, close at -9% or 48h. Add tests; keep suite green and grow toward 70+. Do not defer or substitute low-effort checkpoints.

## NEXT SESSION FOCUS CAMPAIGN (heavy work — do not defer)
The next agentic session must work through this campaign in order. Each item is concrete and verifiable; do not skip or substitute with low-effort checkpoints. Items must add tests; run `python3 -m pytest -q` after every change; all must stay green.

1. **Implement rebound-short logic** (PDF rule, strategy_spec.md item 4): when a buy exits at +9% target fast, open a short on the same coin; close short at -9% or after 48h, whichever first. Add to `crash_rebound.py`/`engine.py` and cover with tests. Gate: short only opened when buy hit +9% target fast.

2. **Enforce 120% gross cap with equal-share cuts in multi-trade flow** (strategy_spec.md item 3): wire `RiskState.cut_positions_to_cap` into the engine/multi-symbol flow so open positions are cut equally when over capacity (never topped up). Add a multi-position cap test.

3. **Align crash trigger to RSI(21h) < 20** (strategy_spec.md item 1): current implementation uses price-drop detection + rebound candle confirmation. Add RSI(21h) trigger option/alignment; keep params matching PDF (+9% target, 50h). Document the switch in `strategy_spec.md`.

4. **Expand multi-symbol backtests & fixtures** (strategy_spec.md item 5): add more liquid-coin fixtures beyond SPY/QQQ/IWM; run multi-symbol backtest; update `research_state/backtest_smoke.json`. Assert all non-NO_TRADE symbols produce a result.

5. **Grow test suite toward 70+.** Current 53. Each campaign item above must add tests. Run `python3 -m pytest -q` after every change; all must stay green.

## Verification gate for end of session
- `python3 -m pytest -q` green
- Each campaign item above adds tests; test suite grows toward 70+
- This handoff updated with new timestamp and any newly blocked/unblocked items before session end

## Do-not-escalate list
- Do not cancel/force-push/escalate an in-progress run without explicit user direction.
- Workflow-file changes remain blocked by GITHUB_TOKEN scope; commit/push only regular files (`research_state/*`, `src/*`, `tests/*`, `scripts/*`).