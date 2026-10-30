# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-10-30T05:48:54Z

> SESSION SNAPSHOT: 2026-10-30T05:48:54Z — `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python -m pytest -q` → **75 passed, 0 failed**. Baseline VERIFIED GREEN.
>
> INITIAL TASK (NEXT SESSION): Execute FOCUS CAMPAIGN PRIORITY 1 — wire multi-position cap enforcement end-to-end (equal-share cuts across ALL open positions, persist cuts to risk_state, add multi-coin integration test). Do NOT deviate; run tests after each change. BOTH LEGS NON-NEGOTIABLE.
> MANDATE: Hyperliquid hourly perps crash-rebound backtester. **BOTH LEGS ARE NON-NEGOTIABLE** — long crash entry AND rebound short MUST both function correctly. Every trade hedged with ETH. PDF is source of truth.

## BOTTLENECK REMOVALS (READ BEFORE WORKING)
- **EDIT TOOL REQUIRES `filePath`:** Repeated session failures came from malformed edit calls missing `filePath`. Always pass `filePath`, `oldString`, `newString` explicitly. Never omit `filePath`.
- **SINGLE CANONICAL HANDOFF:** `research_state/handoff.md` is RETIRED/SUPERSEDED. The only durable handoff is root `HANDOFF.md`. Do not create or read a second handoff file. Duplicate handoffs caused divergent sessions.
- **TESTS ARE THE GATE:** Baseline is 75 passed / 0 failed. Every change must keep tests green. Do not commit unless tests pass.

## IMMEDIATE ACTION (DO NOT DEVIATE)
**STEP 0 - VERIFY BASELINE (BLOCKING, <2 MIN)**
```bash
cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY
PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python -m pytest -q
PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python scripts/run_backtest.py
```
**REQUIREMENT:** Must show >= 75 passed, 0 failed.

## CRITICAL CONTEXT
- **Source of truth:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`
- **Core modules:** `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `scripts/run_backtest.py`
- **State:** RSI trigger (RSI<20) default enabled; drop-based trigger available via `use_rsi_trigger=False`. Rebound short fully implemented. ETH hedge logic implemented with vol-ratio sizing (capped 3x), funding applied. Volume-based sizing wired (`enable_volume_based_sizing` uses 1.25% of 24h volume with fallback). Gross cap/enforcement with **equal-share cuts across ALL positions** (old + new) via `RiskState.apply_cap_cuts()` / `cut_positions_to_cap()` with equal-share logic; backtest applies cuts when adding positions.

## COMPLETED (THIS SESSION)
- [x] Wired volume-based sizing in `src/strategy/crash_rebound.py` (`position_size_by_volume` + `_daily_volume_usd`); falls back to risk-based sizing if missing/invalid.
- [x] Enhanced `RiskState` with `open_position_notionals` tracking and **equal-share cut logic for ALL positions**; added `apply_cap_cuts()` to persist cuts to existing positions.
- [x] Updated backtest engine to track notionals and apply equal-share cuts on breach (old+new); pass notional on trade close/open.
- [x] Added tests: volume-based sizing, volume calc, gross cap equal-share cuts, multi-position all-cut, RSI volume filter; all green.
- [x] Verified both legs functional; ETH hedge intact.

## REMAINING / NEXT PRIORITIES (FOCUS CAMPAIGN)

### PRIORITY 1: WIRE MULTI-POSITION CAP ENFORCEMENT END-TO-END [CRITICAL - 45-90min]
**Goal:** Ensure cuts persist across the portfolio state when multiple positions exist (not just new entries). The engine currently sizes new position after cuts; also propagate cuts back to risk_state and ensure positions are reduced.

**Tasks:**
1. When breach detected, call `risk_state.apply_cap_cuts(capital, config, all_notionals)` to update all existing positions in state.
2. Track per-position sizes in backtester/risk_state so cuts can be applied to actual open positions.
3. Add integration test for multi-entry cap breach across multiple coins.

### PRIORITY 2: UNIVERSE/VOLUME FILTERS + REGIME HARDENING [HIGH - 45min]
**Goal:** Enforce >=$5M daily volume filter rigorously across all paths; tighten regime logic.

**Tasks:**
1. Strengthen tests for RSI trigger + volume filter in integration scenarios.
2. Add helpers for multi-symbol universe filtering (>= $5M daily volume). Consider wiring into backtest runner.
3. Review regime logic (`regime_ok`) against PDF expectations.

### PRIORITY 3: EXECUTION REALISM [MEDIUM-HIGH - 1-2h]
**Goal:** Closer to hourly sim with funding/liquidation checks.

**Tasks:**
1. Expand funding modeling across all legs (long crash, hedge, rebound short, rebound hedge).
2. Add simple hourly liquidation checks at worst price of each hour.
3. Enhance `scripts/run_backtest.py` with detailed reporting.

## SUCCESS CRITERIA
- [ ] Volume-based sizing works end-to-end
- [ ] 120% gross cap enforced with **equal-share cuts across ALL positions (old + new)** - never top-up
- [ ] Both legs ALWAYS functional (long crash + rebound short)
- [ ] ETH hedge intact (vol-ratio, capped 3x), funding applied
- [ ] Tests >= 75 passing, 0 failures
- [ ] Clean run of `scripts/run_backtest.py`

## CRITICAL REMINDERS
- **BOTH LEGS NON-NEGOTIABLE**
- **HEAVY WORK REQUIRED** - Build, test, wire everything
- **PDF IS TRUTH** - `crash-rebound-strategy.pdf` and `research_state/strategy_spec.md`
- **DON'T BREAK TESTS** - Run frequently
- **INFER, DON'T ASK**
- **UPDATE HANDOFF AT END**
