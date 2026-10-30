# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-10-30T02:45:59Z

> SESSION VERIFIED: 2026-10-30T02:45:59Z — `python -m pytest -q` → **58 passed, 0 failed**. Baseline confirmed green. No code changes made this session; handoff is current and accurate. Proceed directly to STEP 0 then CAMPAIGN 1.

## MISSION FOR NEXT SESSION
**DO NOT SKIM. START HERE.**

Repo: CRASH-REBOUND-STRATEGY. Mandate from the name: a Hyperliquid hourly perps crash-rebound backtester where BOTH legs are non-negotiable — long crash entry AND rebound short must both work correctly. Any session that only touches the long leg is off-mission.

Source of truth: `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Treat the PDF as ground truth; every major behavioral change traceable to it. Keep existing tests passing unless the spec explicitly contradicts them — then update tests with clear justification.

## VERIFIED CURRENT STATE
- Tests: `python -m pytest -q` → **58 passed, 0 failed** (rebound-short paths exercised and green)
- Spec extracted: `research_state/strategy_spec.md` (+9% target, 50h/48h exits, ATR(14)*8 stop, 1.25% of 24h vol sizing, 120% gross cap w/ equal-share cuts, ETH hedge per leg, RSI(21h)<20 trigger)
- Gap analysis: `research_state/gap_analysis.md`
- Core modules exist: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/loader.py`
- Rebound-short accounting P0 verified via passing tests (sell-to-open / buy-to-cover PnL signs, stop / target / time_exit)

## BOTTLENECKS REMOVED
1. Unknown spec → extracted
2. Unclear implementation → mapped
3. Rebound-short correctness → covered by passing tests (P0 green); no longer blocking
4. No clear starting point → concrete campaign below

## NEXT AGENTIC SESSION — IMMEDIATE ACTIONS

### STEP 0: VERIFY BASELINE (BLOCKING)
- [ ] Run `python -m pytest -q` → must be green, count >= 58. Record exact count before changes.

### CAMPAIGN 1: TRIGGER ALIGNMENT (immediate focus — 1-2 hours)
**Goal:** Support the PDF's primary trigger (21-hour RSI < 20 on coins with >=$5M vol) while keeping existing drop-based trigger working.

Tasks:
1. Add RSI calculation (21-period, hourly bars) to `src/strategy/crash_rebound.py`.
2. Add volume/liquidity filter `min_daily_volume_usd` (default >=$5M); pass volume data or estimate from candles.
3. Add `detect_crash_rsi()`; make `detect_crash()` configurable to use RSI mode via config flag.
4. Update `StrategyConfig`: `use_rsi_trigger`, `rsi_period` (21), `rsi_threshold` (20), `min_daily_volume_usd` (5_000_000).
5. Add tests for RSI trigger; ensure all existing tests still pass.

**Files:** `src/strategy/crash_rebound.py`, `src/strategy/config.py`, `tests/test_crash_rebound_strategy.py`

### CAMPAIGN 2: ETH HEDGING (2-4 hours) — CRITICAL
**Goal:** Implement ETH hedge for every trade as specified.

Tasks:
1. Design hedge representation in `Signal`/trade structure. PDF: every buy opens a short ETH position of matching risk = coin vol / ETH vol over last 2 weeks, capped at 3x the position; every short gets a long ETH position instead.
2. Add volatility calculation (ATR or realized vol) over ~14 days / ~336 hours.
3. Add hedge sizing logic; track hedge positions in backtest.
4. Update `TradeResult` to include hedge PnL/costs; hedge affects total returns.
5. Model funding on hedge legs (hourly funding) — basic support.
6. Add tests for hedge sizing and PnL contribution.

**Files:** `src/strategy/crash_rebound.py`, `src/strategy/risk.py`, `src/backtest/engine.py`, `tests/`

### CAMPAIGN 3: POSITION SIZING & CAP MANAGEMENT (2-3 hours)
**Goal:** Match PDF's order-book based sizing.

Tasks:
1. Add sizing by `position_size_pct_of_daily_volume` (default 1.25%); need daily volume from candles/data.
2. Implement 120% gross cap on coin positions. When new crashes arrive and cap exceeded, cut existing positions to equal share (old and new) — positions only cut, never topped up.
3. Track total exposure across positions; add to risk/state management.
4. Update backtest to handle position resizing/cuts (with fees/slippage).
5. Add tests for cap and equal-share cuts.

**Files:** `src/strategy/config.py`, `src/strategy/risk.py`, `src/backtest/engine.py`

### CAMPAIGN 4: EXECUTION REALISM & END-TO-END (2-3 hours)
**Goal:** Runnable with realistic assumptions; document how to run.

Tasks:
1. Add funding rate modeling (hourly), configurable rates.
2. Add basic liquidation checks.
3. Support order slicing concept (track in logs).
4. Create `scripts/run_backtest.py` runner that loads data, runs strategy, prints results.
5. Test end-to-end with fixtures.
6. Add minimal README/usage docs.

**Files:** `scripts/`, `src/backtest/`, `README.md` (create minimal if missing)

## IMMEDIATE NEXT ACTION (do this first, no deviation)
```bash
cat research_state/strategy_spec.md
cat research_state/gap_analysis.md

python -c "
from src.strategy.crash_rebound import generate_signal
from src.data.loader import make_fixture_crash_rebound
candles = make_fixture_crash_rebound()
sig = generate_signal(candles)
print(sig)
"
```
Then start **CAMPAIGN 1**. Do not stop until Campaign 1 is complete with tests passing.

## SUCCESS CRITERIA
- [ ] RSI-based trigger implemented and tested (backward compatible)
- [ ] ETH hedge logic implemented with vol-ratio sizing
- [ ] Volume-based position sizing + 120% cap with equal-share cuts
- [ ] All existing tests pass + new tests for added functionality
- [ ] End-to-end backtest runner works with fixtures
- [ ] Assumptions documented in code/comments

## NOTES
- Prioritize by repo name: crash-rebound means BOTH legs.
- Never ask clarifying questions. Infer from PDF. Document assumptions.
- Focus on heavy implementation work. Don't get distracted.
- End of session: update this file with new timestamp, test count, done/blocked, concrete next action.
