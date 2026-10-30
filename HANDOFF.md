# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-10-30T02:38:30Z

## MISSION FOR NEXT SESSION
**DO NOT SKIM. START HERE.**

You have a working codebase (all 58 tests pass). The PDF spec has been extracted and gaps analyzed. Your job is to close the biggest gaps between implementation and the published Hyperliquid crash-rebound strategy so the backtest becomes spec-faithful and runnable end-to-end.

**Single most important instruction:** Treat the PDF (`crash-rebound-strategy.pdf`) as ground truth. Every major behavioral change must be traceable to it. Keep existing tests passing unless the spec explicitly requires behavior that contradicts them - in that case, update tests with clear justification.

## CURRENT STATE (Verified)
- Tests: `python -m pytest -v` → **58 passed**
- Strategy spec: `research_state/strategy_spec.md` (extracted from PDF)
- Gap analysis: `research_state/gap_analysis.md` (PDF vs code)
- Core modules exist: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/loader.py`

## BLOCKERS REMOVED
1. **Unknown spec** → Extracted to `research_state/strategy_spec.md`
2. **Unclear implementation** → Mapped in `research_state/gap_analysis.md`
3. **No clear starting point** → Concrete campaign below

## HEAVY WORK CAMPAIGN (Execute in order - do not skip)

### CAMPAIGN 1: Trigger Alignment (1-2 hours)
**Goal:** Support the PDF's primary trigger (21-hour RSI < 20 on coins with >=$5M vol) while keeping existing drop-based trigger working.

Tasks:
1. Add RSI calculation to `src/strategy/crash_rebound.py` (or new module). Need 21-period RSI (hourly bars per PDF).
2. Add volume/liquidity filter: `min_daily_volume_usd` (default >=$5M). Need to pass volume data or estimate from candles.
3. Add `detect_crash_rsi()` function; make `detect_crash()` configurable to use RSI mode via config flag.
4. Update `StrategyConfig` with `use_rsi_trigger`, `rsi_period` (21), `rsi_threshold` (20), `min_daily_volume_usd` (5_000_000).
5. Add tests for RSI trigger. Ensure all existing tests still pass.

**Files:** `src/strategy/crash_rebound.py`, `src/strategy/config.py`, `tests/test_crash_rebound_strategy.py`

### CAMPAIGN 2: ETH Hedging (2-4 hours) - CRITICAL
**Goal:** Implement ETH hedge for every trade as specified.

Tasks:
1. Design hedge representation in `Signal` or trade structure. PDF says: "Every buy opens a short ETH position of matching risk: coin's volatility divided by ETH's over the last two weeks, capped at three times the position. Every short gets a long ETH position instead."
2. Need volatility calculation (ATR or realized vol) over ~14 days / ~336 hours. Add to strategy.
3. Add hedge sizing logic. Track hedge positions in backtest.
4. Update `TradeResult` to include hedge PnL/costs. Hedge affects total returns.
5. Model funding on hedge legs (hourly funding) - at least basic support.
6. Add tests for hedge sizing and PnL contribution.

**Files:** `src/strategy/crash_rebound.py`, `src/strategy/risk.py`, `src/backtest/engine.py`, `tests/`

### CAMPAIGN 3: Position Sizing & Cap Management (2-3 hours)
**Goal:** Match PDF's order-book based sizing.

Tasks:
1. Add support for sizing by `position_size_pct_of_daily_volume` (default 1.25%). Need daily volume from candles/data.
2. Implement 120% gross cap on coin positions. When new crashes arrive and cap exceeded, cut existing positions to equal share (old and new) - positions only cut, never topped up.
3. Track total exposure across positions. Add to risk/state management.
4. Update backtest to handle position resizing/cuts (with fees/slippage as PDF states).
5. Add tests for cap and equal-share cuts.

**Files:** `src/strategy/config.py`, `src/strategy/risk.py`, `src/backtest/engine.py`

### CAMPAIGN 4: Execution Realism & End-to-End (2-3 hours)
**Goal:** Make it runnable with realistic assumptions and document how to run.

Tasks:
1. Add funding rate modeling (hourly) - can start simple with configurable rates
2. Add liquidation checks (basic)
3. Support order slicing concept (at least track in logs)
4. Create a simple runner script: `scripts/run_backtest.py` that loads data, runs strategy, prints results
5. Test with fixtures and ensure end-to-end works
6. Update README or add usage docs if helpful

**Files:** `scripts/`, `src/backtest/`, `README.md` (if exists, else create minimal)

## IMMEDIATE NEXT ACTION (Do this first, no deviation)
```bash
# 1. Read the full spec and gap analysis
cat research_state/strategy_spec.md
cat research_state/gap_analysis.md

# 2. Understand current behavior
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
- [ ] Any assumptions documented in code/comments

## NOTES
- Repo name is CRASH-REBOUND-STRATEGY - prioritize spec fidelity above all
- Never ask clarifying questions. Infer from PDF. Document assumptions.
- Focus on heavy implementation work. Don't get distracted.
- The rebound short logic is already well-implemented - build around it.
