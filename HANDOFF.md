# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-10-30T06:40:41Z

> SESSION SNAPSHOT: 2026-10-30T06:40:41Z — `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python -m pytest -q` → **76 passed, 0 failed**. Baseline VERIFIED GREEN.
> `python scripts/run_backtest.py` → runs clean (exit: time_exit, PnL: -5.4620).
>
> INITIAL TASK (NEXT SESSION): Execute FOCUS CAMPAIGN PRIORITY 2 — universe/volume filters + regime hardening (>= $5M daily volume enforced rigorously across all trigger paths; multi-symbol universe filtering helpers; regime_ok review against PDF). Do NOT deviate; run tests after each change. BOTH LEGS NON-NEGOTIABLE.
> MANDATE: Hyperliquid hourly perps crash-rebound backtester. **BOTH LEGS ARE NON-NEGOTIABLE** — long crash entry AND rebound short MUST both function correctly. Every trade hedged with ETH. PDF is source of truth.

## BOTTLENECK REMOVALS (READ BEFORE WORKING)
- **EDIT TOOL REQUIRES `filePath`:** Repeated session failures came from malformed edit calls missing `filePath`. Always pass `filePath`, `oldString`, `newString` explicitly. Never omit `filePath`.
- **SINGLE CANONICAL HANDOFF:** `research_state/handoff.md` is RETIRED/SUPERSEDED. The only durable handoff is root `HANDOFF.md`. Do not create or read a second handoff file. Duplicate handoffs caused divergent sessions.
- **TESTS ARE THE GATE:** Baseline is 76 passed / 0 failed. Every change must keep tests green. Do not commit unless tests pass.

## IMMEDIATE ACTION (DO NOT DEVIATE)
**STEP 0 - VERIFY BASELINE (BLOCKING, <2 MIN)**
```bash
cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY
PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python -m pytest -q
PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python scripts/run_backtest.py
```
**REQUIREMENT:** Must show >= 76 passed, 0 failed.

## CRITICAL CONTEXT
- **Source of truth:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`
- **Core modules:** `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `scripts/run_backtest.py`
- **State:** RSI trigger (RSI<20) default enabled; drop-based trigger available via `use_rsi_trigger=False`. Rebound short fully implemented. ETH hedge logic implemented with vol-ratio sizing (capped 3x), funding applied. Volume-based sizing wired (`enable_volume_based_sizing` uses 1.25% of 24h volume with fallback). Gross cap/enforcement with **equal-share cuts across ALL positions** (old + new) via `RiskState.apply_cap_cuts()` / `cut_positions_to_cap()` with equal-share logic; backtest applies cuts when adding positions.

## COMPLETED (THIS SESSION)
- [x] Wired volume-based sizing in `src/strategy/crash_rebound.py` (`position_size_by_volume` + `_daily_volume_usd`); falls back to risk-based sizing if missing/invalid.
- [x] Enhanced `RiskState` with `open_position_notionals` tracking and **equal-share cut logic for ALL positions**; added `apply_cap_cuts()` to persist cuts to existing positions.
- [x] Updated backtest engine to track notionals and apply equal-share cuts on breach (old+new); pass notional on trade close/open.
- [x] **PRIORITY 1 DONE — multi-position cap enforcement wired end-to-end:** engine now calls `risk_state.apply_cap_cuts(capital, config, all_notionals)` on gross-cap breach so equal-share cuts persist to ALL open positions (old + new) in risk_state, and the new entry is sized to its cut share (no top-up). Added `tests/test_crash_rebound_strategy.py::test_engine_applies_equal_share_cuts_to_existing_positions` integration test proving existing positions are included in the cut call and state gross_exposure reflects the persisted cut.
- [x] Added tests: volume-based sizing, volume calc, gross cap equal-share cuts, multi-position all-cut, RSI volume filter; all green.
- [x] Verified both legs functional; ETH hedge intact.
- [x] Baseline reverified: **76 passed, 0 failed**; `scripts/run_backtest.py` runs clean.

## REMAINING / NEXT PRIORITIES (FOCUS CAMPAIGN)

### PRIORITY 2: UNIVERSE/VOLUME FILTERS + REGIME HARDENING [ACTIVE - 45-90min]
**Goal:** Enforce >=$5M daily volume filter rigorously across all trigger paths; tighten regime logic per PDF spec.

**Tasks:**
1. Wire `min_daily_volume_usd >= $5M` filter into every crash-trigger path (`detect_crash` drop path currently applies volume spike only; `detect_crash_rsi` applies it) so no sub-$5M coin can generate a signal.
2. Add multi-symbol universe filtering helpers (>= $5M daily 24h volume) and consider wiring into backtest runner / signal generation across symbols.
3. Review `regime_ok()` against PDF expectations (avoid downtrend / price above fast MA); add tests covering regime block and pass.
4. Add integration test: sub-$5M coin produces no signal; >= $5M coin with valid crash does.

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
- [ ] **>= $5M daily volume filter enforced on all trigger paths**
- [ ] Tests >= 76 passing, 0 failures
- [ ] Clean run of `scripts/run_backtest.py`

## CRITICAL REMINDERS
- **BOTH LEGS NON-NEGOTIABLE**
- **HEAVY WORK REQUIRED** - Build, test, wire everything
- **PDF IS TRUTH** - `crash-rebound-strategy.pdf` and `research_state/strategy_spec.md`
- **DON'T BREAK TESTS** - Run frequently
- **INFER, DON'T ASK**
- **UPDATE HANDOFF AT END**
