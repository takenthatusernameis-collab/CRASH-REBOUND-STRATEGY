# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-10-30T06:51:30Z

> SESSION SNAPSHOT: 2026-10-30T06:51:30Z — `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python -m pytest -q` → **76 passed, 0 failed**. Baseline VERIFIED GREEN.
> `python scripts/run_backtest.py` → runs clean (exit: time_exit, PnL: -5.4620).
>
> **INITIAL TASK (NEXT SESSION — MANDATORY HEAVY WORK): EXECUTE FOCUS CAMPAIGN PRIORITY 3 — EXECUTION REALISM.**
> DO NOT do trivial refactors. DO NOT stop at reading. You MUST implement ALL tasks below with tests passing after each change. BOTH LEGS NON-NEGOTIABLE (long crash + rebound short). ETH hedge intact. Equal-share gross cap enforcement MUST remain correct.
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
- [x] **PRIORITY 2 PARTIAL — volume filters hardening:** Enforced `min_daily_volume_usd >= $5M` across ALL trigger paths (drop-based and RSI-based). Updated fixtures to meet volume requirements. Added multi-symbol universe filtering helpers (`passes_universe_filter`, `filter_universe`) in `src/strategy/crash_rebound.py`. Added integration tests for sub-$5M rejection.
- [x] Added tests: volume-based sizing, volume calc, gross cap equal-share cuts, multi-position all-cut, RSI volume filter; all green.
- [x] Verified both legs functional; ETH hedge intact.
- [x] Baseline reverified: **76 passed, 0 failed**; `scripts/run_backtest.py` runs clean.

## REMAINING / NEXT PRIORITIES (FOCUS CAMPAIGN)

### PRIORITY 2: UNIVERSE/VOLUME FILTERS + REGIME HARDENING [DONE - 45-90min]
**Goal:** Enforce >=$5M daily volume filter rigorously across all trigger paths; tighten regime logic per PDF spec.

**Tasks:**
1. [x] Wire `min_daily_volume_usd >= $5M` filter into every crash-trigger path (`detect_crash` drop path currently applies volume spike only; `detect_crash_rsi` applies it) so no sub-$5M coin can generate a signal.
2. [x] Add multi-symbol universe filtering helpers (>= $5M daily 24h volume) and consider wiring into backtest runner / signal generation across symbols.
3. [x] Review `regime_ok()` against PDF expectations (avoid downtrend / price above fast MA); add tests covering regime block and pass.
4. [x] Add integration test: sub-$5M coin produces no signal; >= $5M coin with valid crash does.

### PRIORITY 3: EXECUTION REALISM [MEDIUM-HIGH - 2-3h] — MANDATORY
**Goal:** Closer to hourly sim with funding/liquidation checks. NO SHORTCUTS.

**Tasks (ALL REQUIRED):**
1. [ ] **FUNDING ACROSS ALL LEGS:** Expand funding modeling to cover long crash leg, crash hedge (short), rebound short leg, and rebound hedge (long). Apply funding by hours held using `config.funding_rate_pct_per_hour` with correct sign convention per leg (long pays if positive rate per current convention; short receives). Track funding PnL separately in results and ensure totals remain correct.
2. [ ] **HOURLY LIQUIDATION CHECKS:** Add simple hourly liquidation checks at worst price of each hour. For longs, liquidate if `low` breaches maintenance margin threshold (implement a conservative configurable check e.g. using stop/maint margin assumption or config `liquidation_buffer_pct`); for shorts if `high` breaches. On liquidation, force exit at worst price with liquidation penalty (configurable) and mark `exit_reason='liquidated'`. Do NOT skip - implement even if conservative.
3. [ ] **DETAILED REPORTING:** Enhance `scripts/run_backtest.py` with detailed reporting: per-trade breakdown (side, entry/exit, PnL, funding, fees), hedge details, gross exposure, total PnL, win rate, trade counts by leg, and summary stats. Make it immediately useful for debugging.
4. [ ] **TESTS:** Add at least 2 new tests covering funding across legs and liquidation triggering; keep ALL existing tests green.

## SUCCESS CRITERIA
- [ ] Volume-based sizing works end-to-end
- [ ] 120% gross cap enforced with **equal-share cuts across ALL positions (old + new)** - never top-up
- [ ] Both legs ALWAYS functional (long crash + rebound short)
- [ ] ETH hedge intact (vol-ratio, capped 3x), funding applied
- [ ] **>= $5M daily volume filter enforced on all trigger paths**
- [ ] **Funding modeled across ALL legs with correct signs**
- [ ] **Hourly liquidation checks implemented and tested**
- [ ] **run_backtest.py has detailed per-trade reporting**
- [ ] Tests >= 78 passing, 0 failures (add >= 2 new tests)
- [ ] Clean run of `scripts/run_backtest.py`

## CRITICAL REMINDERS
- **BOTH LEGS NON-NEGOTIABLE**
- **HEAVY WORK REQUIRED** - Build, test, wire everything
- **PDF IS TRUTH** - `crash-rebound-strategy.pdf` and `research_state/strategy_spec.md`
- **DON'T BREAK TESTS** - Run frequently
- **INFER, DON'T ASK**
- **UPDATE HANDOFF AT END**
