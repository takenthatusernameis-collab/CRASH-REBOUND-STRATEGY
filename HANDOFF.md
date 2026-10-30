# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-10-30T08:32:47Z

> SESSION SNAPSHOT: 2026-10-30T08:32:47Z — Crash-rebound-strategy tests: **42/42 passed, 0 failed**. Baseline VERIFIED GREEN.
> `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python scripts/run_backtest.py` → runs clean with detailed per-trade breakdown.

> **INITIAL TASK (NEXT SESSION — MANDATORY HEAVY WORK): EXECUTE THE NEXT FOCUS CAMPAIGN TO COMPLETION.**
> **PRIORITIZE BY REPO NAME: CRASH-REBOUND-STRATEGY.** Do NOT coast. Ship heavy work: real Hyperliquid data integration + end-to-end multi-trade portfolio simulation, hardened capital/risk accounting, and full campaign validation. **BOTH LEGS NON-NEGOTIABLE (long crash + rebound short).** ETH hedge intact. Equal-share gross cap enforcement MUST remain correct across ALL positions (old+new), never top-up.

> **IMMEDIATE FIRST STEP (BLOCKING — PRIORITY A):** Implement the Hyperliquid data loader (`src/data/loader.py`) supporting multi-coin hourly candles/volumes with >=$5M 24h volume filter, caching/fixtures for offline runs, and validation (gaps, non-finite, look-ahead safety). Wire `passes_universe_filter`/`filter_universe` everywhere. Add tests. Only after A is green, proceed to B (portfolio/multi-trade simulation) then C (campaign validation).

## BOTTLENECK REMOVALS (READ BEFORE WORKING)
- **EDIT TOOL REQUIRES `filePath`:** Always pass `filePath`, `oldString`, `newString` explicitly. Never omit `filePath`.
- **SINGLE CANONICAL HANDOFF:** `research_state/handoff.md` is RETIRED/SUPERSEDED. The only durable handoff is root `HANDOFF.md`. Do not create or read a second handoff file.
- **TESTS ARE THE GATE:** All crash-rebound strategy tests pass. Every change must keep tests green. Do not commit unless tests pass.
- **RUN COMMANDS:** Always set `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY` when running scripts/tests from repo root.
- **INFER, DON'T ASK:** No explicit directions? Build the campaign and execute heavy work. No exploratory Q&A loops.
- **AVOID IDLE POLLING:** If waiting on CI/data, schedule with `schedule_wakeup`/`cron_create` in goal context; don't poll in shell.

## IMMEDIATE ACTION (DO NOT DEVIATE)
**STEP 0 - VERIFY BASELINE (BLOCKING, <2 MIN)**
```bash
cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY
PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python -c "from tests import test_crash_rebound_strategy; import inspect; tests=[n for n,o in inspect.getmembers(test_crash_rebound_strategy) if inspect.isfunction(o) and n.startswith('test_')]; [getattr(test_crash_rebound_strategy,t)() for t in tests]; print('ALL PASSED:', len(tests))"
PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python scripts/run_backtest.py
```
**REQUIREMENT:** Must show all tests passed. If baseline fails, FIX BEFORE ANYTHING ELSE.

## CRITICAL CONTEXT
- **Source of truth:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`
- **Core modules:** `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/loader.py`, `scripts/run_backtest.py`
- **State:** RSI trigger (RSI<20) default enabled; drop-based trigger available via `use_rsi_trigger=False`. Rebound short fully implemented. ETH hedge logic implemented with vol-ratio sizing (capped 3x), funding applied across all legs. Volume-based sizing wired. Gross cap/enforcement with **equal-share cuts across ALL positions (old + new)** via `RiskState.apply_cap_cuts()` / `cut_positions_to_cap()` with equal-share logic. Hourly liquidation checks at worst price with penalty.
- **Test window (Hyperliquid):** 2025-12-20 to 2026-09-28 (283 days).

## NEXT FOCUS CAMPAIGN (HEAVY WORK - DO NOT DEFER)
**PRIORITY A: REAL DATA INTEGRATION (BLOCKING — START HERE)**
- [ ] **Hyperliquid data loader:** Implement robust loader for Hyperliquid hourly candles/volumes (extend `src/data/loader.py`). Must support multi-coin universe with >=$5M 24h volume filter. Add caching/fixtures for offline runs.
- [ ] **Universe filtering:** Wire `passes_universe_filter`/`filter_universe` everywhere (drop-based + RSI paths). Enforce $5M minimum daily volume on all triggers. Add tests.
- [ ] **Data validation:** Add checks for gaps, non-finite values, look-ahead safety. Fail fast with clear errors.

**PRIORITY B: PORTFOLIO/MULTI-TRADE SIMULATION (BLOCKING)**
- [ ] **Multi-position runner:** Extend backtest to run across full universe over time with concurrent positions, hourly stepping, correct ordering (deepest crash first per spec). Create `scripts/run_portfolio.py` or extend `run_backtest.py`.
- [ ] **Capital accounting:** Track vault equity, margin/free margin, fees/funding across all legs, realize PnL correctly. Audit for double-counting.
- [ ] **Cap enforcement:** Verify equal-share cuts in portfolio context with old+new positions simultaneously; never top-up. Add regression tests.
- [ ] **Hedges:** Ensure every coin position gets correct ETH hedge (vol-ratio, capped 3x) at all times. Funding applied to hedges.

**PRIORITY C: CAMPAIGN VALIDATION & HARDENING (BLOCKING)**
- [ ] **Full campaign run:** Create `scripts/run_campaign.py` to run full test window (2025-12-20 to 2026-09-28) with detailed reporting (trades, legs, funding, liquidations, drawdowns, per-coin, per-month).
- [ ] **Metrics:** Compute total return, annualized, max drawdown, Sharpe/Sortino if feasible, win rates, rebound-short contribution, per-month. Export JSON/CSV.
- [ ] **Stress tests:** Edge cases (multiple simultaneous crashes, cap saturation, liquidation scenarios, gaps).
- [ ] **Tests:** Add comprehensive tests for portfolio cap enforcement, multi-position ordering, funding across all legs in portfolio mode. Keep all tests green.

## COMPLETED (PREVIOUS SESSION)
- [x] **PRIORITY 1 DONE:** Multi-position cap enforcement wired end-to-end with equal-share cuts across ALL positions (old + new) in risk_state; added integration test.
- [x] **PRIORITY 2 DONE:** Volume filters hardened - enforced `min_daily_volume_usd >= $5M` across ALL trigger paths (drop-based and RSI-based). Added multi-symbol universe filtering helpers.
- [x] **PRIORITY 3 DONE - EXECUTION REALISM:** Funding across all legs, hourly liquidation checks at worst price, detailed reporting in run_backtest.py; all 42 tests passing.

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
- **BOTH LEGS NON-NEGOTIABLE** - Long crash + rebound short must both function.
- **HEAVY WORK REQUIRED** - Don't coast. Build and validate the full campaign. Future agents must not avoid heavy work.
- **PDF IS TRUTH** - `crash-rebound-strategy.pdf` and `research_state/strategy_spec.md` are source of truth.
- **DON'T BREAK TESTS** - Run frequently. All changes must keep tests green.
- **INFER, DON'T ASK** - No explicit directions needed; execute the campaign above.
- **UPDATE HANDOFF AT END** - Leave a clear, timestamped handoff with next heavy task.
- **SINGLE HANDOFF** - Only root `HANDOFF.md` is durable.
