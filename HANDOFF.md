# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-10-30T05:44:00Z

> SESSION SNAPSHOT: 2026-10-30T05:44:00Z — `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python -m pytest -q` → **75 passed, 0 failed**. Baseline VERIFIED GREEN.
>
> MANDATE: Hyperliquid hourly perps crash-rebound backtester. **BOTH LEGS ARE NON-NEGOTIABLE** — long crash entry AND rebound short MUST both function correctly. Every trade hedged with ETH. PDF is source of truth.

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
- **State:** RSI trigger (RSI<20) default enabled; drop-based trigger available via `use_rsi_trigger=False`. Rebound short fully implemented. ETH hedge logic implemented with vol-ratio sizing (capped 3x), funding applied. **Volume-based sizing wired** (`enable_volume_based_sizing` uses 1.25% of 24h volume with fallback). **Gross cap/enforcement** with equal-share cuts supported via `RiskState.cut_positions_to_cap()` and backtest tracking.

## COMPLETED (THIS SESSION)
- [x] Wired volume-based sizing in `src/strategy/crash_rebound.py` (`position_size_by_volume` + `_daily_volume_usd`); falls back to risk-based sizing if missing/invalid.
- [x] Enhanced `RiskState` with `open_position_notionals` tracking and equal-share cut logic; `check_position` updated for cap handling.
- [x] Updated backtest engine to track notionals and apply equal-share cuts on breach (old+new); pass notional on trade close/open.
- [x] Added tests: volume-based sizing, volume calc, gross cap equal-share cuts, RSI volume filter; all green.
- [x] Verified both legs functional; ETH hedge intact.

## REMAINING / NEXT PRIORITIES
### PRIORITY 1: HARDEN MULTI-POSITION GROSS CAP [CRITICAL - 1-2h]
**Goal:** Ensure equal-share cuts are applied across ALL positions when cap breached (including when adding positions across multiple entries). Current implementation cuts proportionally on new entry sizing; consider enforcing cuts on existing positions in state/backtest flow.

**Tasks:**
1. When breaching cap, apply `cut_positions_to_cap` to full set of open notionals and persist adjusted sizes for existing positions if tracked.
2. Add tests for multi-position gross cap scenarios.

### PRIORITY 2: UNIVERSE/VOLUME FILTERS + REGIME HARDENING [HIGH - 1h]
**Goal:** Enforce >=$5M daily volume filter rigorously; tighten regime logic.

**Tasks:**
1. Ensure RSI trigger path enforces `min_daily_volume_usd` (implemented) - add/strengthen tests.
2. Add helpers for multi-symbol universe filtering (>= $5M daily volume). Wire into backtest runner if needed.
3. Review regime logic.

### PRIORITY 3: EXECUTION REALISM [MEDIUM-HIGH - 1-2h]
**Goal:** Closer to hourly sim with funding/liquidation checks.

**Tasks:**
1. Expand funding modeling across all legs.
2. Add simple hourly liquidation checks at worst price of each hour.
3. Enhance `scripts/run_backtest.py` with detailed reporting.

## SUCCESS CRITERIA
- [ ] Volume-based sizing works end-to-end
- [ ] 120% gross cap enforced with equal-share cuts (all positions) - never top-up
- [ ] Both legs ALWAYS functional
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
