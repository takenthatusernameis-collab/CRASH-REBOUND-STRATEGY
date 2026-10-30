# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-10-30T05:39:32Z

> SESSION SNAPSHOT: 2026-10-30T05:39:32Z — `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python -m pytest -q` → **71 passed, 0 failed**. Baseline VERIFIED GREEN.
>
> MANDATE: Hyperliquid hourly perps crash-rebound backtester. **BOTH LEGS ARE NON-NEGOTIABLE** — long crash entry AND rebound short MUST both function correctly. Every trade hedged with ETH. PDF is source of truth.

## IMMEDIATE ACTION (DO NOT DEVIATE)
**STEP 0 - VERIFY BASELINE (BLOCKING, <2 MIN)**
```bash
cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY
PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python -m pytest -q
PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python scripts/run_backtest.py
```
**REQUIREMENT:** Must show >= 71 passed, 0 failed. If anything fails, FIX IT BEFORE MOVING ON.

## CRITICAL CONTEXT
- **Source of truth:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md` (treat PDF as ground truth)
- **Core modules:** `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `scripts/run_backtest.py`
- **Current state:** RSI trigger (RSI<20) default enabled; drop-based trigger available via `use_rsi_trigger=False`. Rebound short fully implemented. ETH hedge logic implemented with vol-ratio sizing (capped 3x), funding applied. All tests green.

## HEAVY IMPLEMENTATION CAMPAIGN (PRIORITIZED - EXECUTE IN ORDER)

### PRIORITY 1: VOLUME-BASED SIZING + 120% GROSS CAP WITH EQUAL-SHARE CUTS [CRITICAL - 3-5h]
**Goal:** Match PDF exactly - position size = 1.25% of 24h volume; 120% gross cap with equal-share cuts (never top-up, only cut).

**Tasks (MUST COMPLETE ALL):**
1. **Wire volume-based sizing:** In `src/strategy/crash_rebound.py`, when `config.enable_volume_based_sizing` is True, compute size using `position_size_by_volume(entry_price, daily_volume_usd, config.position_size_pct_of_daily_volume)`. Compute `daily_volume_usd` via `_daily_volume_usd(candles, lookback=24)`. Fall back to risk-based sizing if volume data missing/invalid.
2. **Enforce gross cap in signal generation:** Ensure sizing respects gross cap considering existing exposure. When cap would be breached, apply equal-share cuts to ALL positions (old + new) via `RiskState.cut_positions_to_cap()`. Track notional across positions.
3. **Backtest gross exposure tracking:** In `src/backtest/engine.py`, properly track/update `risk_state.gross_exposure` and `risk_state.open_positions` across multi-position scenarios. Enforce 120% gross cap (config.gross_cap_pct). When breached, cut all positions to equal share - NO top-ups.
4. **Add comprehensive tests:** Add tests for volume-based sizing and gross cap enforcement with equal-share cuts. Ensure new tests are added (target >= 75 total passing).
5. **Regression check:** All existing 71 tests MUST still pass.

### PRIORITY 2: UNIVERSE/VOLUME FILTERS + REGIME HARDENING [HIGH - 1-2h]
**Goal:** Enforce >=$5M daily volume filter rigorously; harden regime logic.

**Tasks:**
1. **Volume filter enforcement:** Ensure RSI trigger path enforces `min_daily_volume_usd` (already implemented in `detect_crash_rsi`) - add/strengthen tests to verify rejection when volume < $5M.
2. **Universe filtering helpers:** Add helpers for multi-symbol universe filtering (>= $5M daily volume). Wire into backtest runner if needed.
3. **Regime hardening:** Review and tighten regime logic if gaps found. Both legs must remain functional.

### PRIORITY 3: EXECUTION REALISM [MEDIUM-HIGH - 1-2h]
**Goal:** Closer to hourly sim with funding/liquidation checks.

**Tasks:**
1. **Expand funding modeling:** Review funding application across all legs (long crash + hedge + rebound short + hedge). Ensure correct convention.
2. **Liquidation checks:** Add simple hourly liquidation checks at worst price of each hour as per spec.
3. **Runner improvements:** Enhance `scripts/run_backtest.py` with detailed reporting (trades, legs, hedge PnL, totals).

## SUCCESS CRITERIA (MUST ALL BE MET)
- [ ] **Volume-based sizing wired:** `enable_volume_based_sizing` works end-to-end; uses 1.25% of 24h volume; falls back gracefully
- [ ] **120% gross cap enforced:** Cap enforced across positions with equal-share cuts when breached; old positions cut, never topped up
- [ ] **Both legs ALWAYS functional:** Long crash + rebound short both work correctly under all changes
- [ ] **ETH hedge intact:** Hedge PnL contributes to totals; vol-ratio sizing (capped 3x) working
- [ ] **Tests expanded:** >= 75 tests passing, 0 failures (add tests for new functionality)
- [ ] **Clean run:** `scripts/run_backtest.py` runs end-to-end cleanly with detailed output
- [ ] **No regressions:** All existing functionality preserved

## CRITICAL REMINDERS
- **BOTH LEGS NON-NEGOTIABLE** - Never break crash buy OR rebound short
- **HEAVY WORK REQUIRED** - Build, test, wire everything. Don't just read.
- **PDF IS TRUTH** - When in doubt, check `crash-rebound-strategy.pdf` and `research_state/strategy_spec.md`
- **DON'T BREAK TESTS** - Run tests frequently, fix immediately
- **INFER, DON'T ASK** - Make reasonable assumptions aligned with spec
- **UPDATE HANDOFF AT END** - Leave clear state for next session with updated timestamp

**START WITH STEP 0 NOW. BEGIN PRIORITY 1 IMMEDIATELY. NO EXCUSES.**
