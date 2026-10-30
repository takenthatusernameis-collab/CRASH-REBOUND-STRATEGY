# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-10-30T07:25:00Z

> SESSION SNAPSHOT: 2026-10-30T07:25:00Z — Crash-rebound-strategy tests: **42/42 passed, 0 failed**. Baseline VERIFIED GREEN.
> `python scripts/run_backtest.py` → runs clean with detailed per-trade breakdown.
>
> **INITIAL TASK (NEXT SESSION — MANDATORY HEAVY WORK): ALL PRIORITIES COMPLETE.** Focus on broader integration testing, paper trading validation, or live data integration as needed. BOTH LEGS NON-NEGOTIABLE (long crash + rebound short). ETH hedge intact. Equal-share gross cap enforcement MUST remain correct.
> MANDATE: Hyperliquid hourly perps crash-rebound backtester. **BOTH LEGS ARE NON-NEGOTIABLE** — long crash entry AND rebound short MUST both function correctly. Every trade hedged with ETH. PDF is source of truth.

## BOTTLENECK REMOVALS (READ BEFORE WORKING)
- **EDIT TOOL REQUIRES `filePath`:** Always pass `filePath`, `oldString`, `newString` explicitly. Never omit `filePath`.
- **SINGLE CANONICAL HANDOFF:** `research_state/handoff.md` is RETIRED/SUPERSEDED. The only durable handoff is root `HANDOFF.md`. Do not create or read a second handoff file.
- **TESTS ARE THE GATE:** All crash-rebound strategy tests pass. Every change must keep tests green. Do not commit unless tests pass.

## IMMEDIATE ACTION (DO NOT DEVIATE)
**STEP 0 - VERIFY BASELINE (BLOCKING, <2 MIN)**
```bash
cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY
PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python -c "from tests import test_crash_rebound_strategy; import inspect; tests=[n for n,o in inspect.getmembers(test_crash_rebound_strategy) if inspect.isfunction(o) and n.startswith('test_')]; [getattr(test_crash_rebound_strategy,t)() for t in tests]; print('ALL PASSED:', len(tests))"
PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python scripts/run_backtest.py
```
**REQUIREMENT:** Must show all tests passed.

## CRITICAL CONTEXT
- **Source of truth:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`
- **Core modules:** `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `scripts/run_backtest.py`
- **State:** RSI trigger (RSI<20) default enabled; drop-based trigger available via `use_rsi_trigger=False`. Rebound short fully implemented. ETH hedge logic implemented with vol-ratio sizing (capped 3x), funding applied. Volume-based sizing wired. Gross cap/enforcement with **equal-share cuts across ALL positions** (old + new) via `RiskState.apply_cap_cuts()` / `cut_positions_to_cap()` with equal-share logic.

## COMPLETED (THIS SESSION)
- [x] **PRIORITY 1 DONE:** Multi-position cap enforcement wired end-to-end with equal-share cuts across ALL positions (old + new) in risk_state; added integration test.
- [x] **PRIORITY 2 DONE:** Volume filters hardened - enforced `min_daily_volume_usd >= $5M` across ALL trigger paths (drop-based and RSI-based). Added multi-symbol universe filtering helpers (`passes_universe_filter`, `filter_universe`).
- [x] **PRIORITY 3 DONE - EXECUTION REALISM:**
  - [x] **FUNDING ACROSS ALL LEGS:** Expanded funding modeling to cover long crash leg, crash hedge (short), rebound short leg, and rebound hedge (long). Applied funding by hours held using `config.funding_rate_pct_per_hour` with correct sign convention per leg.
  - [x] **HOURLY LIQUIDATION CHECKS:** Added hourly liquidation checks at worst price of each hour for long and short positions. On liquidation, force exit at worst price with liquidation penalty and mark `exit_reason='liquidated'`.
  - [x] **DETAILED REPORTING:** Enhanced `scripts/run_backtest.py` with detailed reporting: per-trade breakdown, hedge details, totals.
  - [x] **TESTS:** Added tests for funding across legs and liquidation triggering; all 42 crash-rebound strategy tests passing.

## REMAINING / NEXT PRIORITIES
All specified priorities complete. Focus areas for future sessions: integration testing with real data if available, parameter optimization/tuning, live trading safeguards and monitoring.

## SUCCESS CRITERIA
- [x] Volume-based sizing works end-to-end
- [x] 120% gross cap enforced with **equal-share cuts across ALL positions (old + new)** - never top-up
- [x] Both legs ALWAYS functional (long crash + rebound short)
- [x] ETH hedge intact (vol-ratio, capped 3x), funding applied
- [x] **>= $5M daily volume filter enforced on all trigger paths**
- [x] **Funding modeled across ALL legs with correct signs**
- [x] **Hourly liquidation checks implemented and tested**
- [x] **run_backtest.py has detailed per-trade reporting**
- [x] Tests: **42/42 crash-rebound strategy tests passing, 0 failures**
- [x] Clean run of `scripts/run_backtest.py`

## CRITICAL REMINDERS
- **BOTH LEGS NON-NEGOTIABLE**
- **HEAVY WORK REQUIRED** - Build, test, wire everything
- **PDF IS TRUTH** - `crash-rebound-strategy.pdf` and `research_state/strategy_spec.md`
- **DON'T BREAK TESTS** - Run frequently
- **INFER, DON'T ASK**
- **UPDATE HANDOFF AT END**
