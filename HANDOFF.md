# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-10-30T03:38:39Z

> SESSION VERIFIED: 2026-10-30T03:38:39Z — `python -m pytest -q` → **58 passed, 0 failed**. Baseline green. Bottlenecks removed (see below). Next session starts at STEP 0 then CAMPAIGN 1.

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

## BOTTLENECKS REMOVED (this session)
1. **Test suite uncollectable** — `src/strategy/config.py:91` `DEFAULT_CONFIG = StrategyConfig()` raised `AttributeError: 'StrategyConfig' object has no attribute 'risk_per_trade_pct'` (also `max_positions`, `max_daily_loss_pct`, `gross_cap_pct` referenced in `__post_init__` but never declared). Added all four fields with spec-aligned defaults (`risk_per_trade_pct=1.0`, `max_positions=5`, `max_daily_loss_pct=3.0`, `gross_cap_pct=120.0`).
2. **NameError on signal generation** — `src/strategy/crash_rebound.py:295` called nonexistent `position_size_shares()`; replaced with imported `size_by_risk(entry, stop, capital, config.risk_per_trade_pct)`.
3. **AttributeError in backtest entry gate** — `src/backtest/engine.py:68` read `check.approved_size`; `RiskCheck` exposes `size_shares`. Fixed to `check.size_shares`.
4. `python -m pytest -q` now collects and passes **58/58**. Suite is no longer blocked.

## NEXT AGENTIC SESSION — IMMEDIATE ACTIONS

### STEP 0: VERIFY BASELINE (BLOCKING)
- [ ] Run `python -m pytest -q` → must be green, count >= 58. Record exact count before changes.

### CAMPAIGN 1: TRIGGER ALIGNMENT TO PDF PRIMARY TRIGGER (immediate focus — 1-2 hours)
**Goal:** Make the PDF's primary trigger (21-hour RSI < 20 on coins with >=$5M vol) the default path, while keeping the existing drop-based trigger available via config flag so no test regresses.

**RSI/volume support already exists** (`detect_crash_rsi`, `detect_crash(use_rsi_trigger=...)`, config fields `use_rsi_trigger`, `rsi_period`, `rsi_threshold`, `min_daily_volume_usd`) but is not default and untested.

Tasks:
1. Flip `StrategyConfig.use_rsi_trigger` default to `True` (PDF primary trigger). Keep `crash_pct_drop`/`volume_spike_mult` path reachable via `use_rsi_trigger=False`.
2. Add tests for RSI trigger: `detect_crash_rsi` below/above threshold, insufficient data → False, volume filter rejects <$5M est. vol.
3. Add tests proving drop-based path still works with `use_rsi_trigger=False`.
4. Update `generate_signal` `config_used` to record `use_rsi_trigger` (already present) — verify.
5. Ensure all existing tests still pass (58/58 baseline must hold).

**Files:** `src/strategy/config.py`, `src/strategy/crash_rebound.py`, `tests/test_crash_rebound_strategy.py`

### CAMPAIGN 2: ETH HEDGING WIRED INTO BACKTEST (2-4 hours) — CRITICAL
**Goal:** Every trade hedged with ETH as specified; hedge PnL contributes to total returns.

**`compute_eth_hedge_size` exists but is unused; `TradeResult` has no hedge fields.**

Tasks:
1. Add hedge fields to `TradeResult` (`hedge_pnl`, `hedge_side`, `hedge_size`, `hedge_entry`, `hedge_exit`).
2. In `backtest_simple`, on long entry open short ETH hedge of `compute_eth_hedge_size(...)`; on rebound short open long ETH hedge; close hedge when leg closes; include hedge PnL in total.
3. Model hourly funding on hedge legs (config `funding_rate_pct_per_hour`, configurable).
4. Add tests for hedge sizing (vol ratio, 3x cap) and hedge PnL contribution sign/direction.
5. All tests pass.

**Files:** `src/backtest/engine.py`, `src/strategy/risk.py`, `src/strategy/crash_rebound.py`, `tests/`

### CAMPAIGN 3: POSITION SIZING & CAP MANAGEMENT (2-3 hours)
**Goal:** Match PDF's order-book sizing: 1.25% of 24h volume, 120% gross cap with equal-share cuts (positions only cut, never topped up).

**`position_size_by_volume` and `RiskState.cut_positions_to_cap` exist but are unused in the backtest.**

Tasks:
1. Wire volume-based sizing into `generate_signal`/`backtest_simple` using daily volume from candles (`position_size_by_volume`).
2. Implement 120% gross cap on coin positions; on new crashes exceeding cap, cut existing + new positions to equal share.
3. Track total exposure across positions in backtest state; apply cuts with fees/slippage.
4. Add tests for cap and equal-share cuts.
5. All tests pass.

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
python -m pytest -q
# must print 58 passed, 0 failed
cat research_state/strategy_spec.md
cat research_state/gap_analysis.md
```
Then start **CAMPAIGN 1**. Do not stop until Campaign 1 is complete with tests passing.

## SUCCESS CRITERIA
- [ ] RSI-based trigger is default and tested (drop-based still available via flag)
- [ ] ETH hedge logic wired into backtest with vol-ratio sizing and funding
- [ ] Volume-based position sizing + 120% cap with equal-share cuts wired into backtest
- [ ] All existing tests pass + new tests for added functionality
- [ ] End-to-end backtest runner works with fixtures
- [ ] Assumptions documented in code/comments

## NOTES
- Prioritize by repo name: crash-rebound means BOTH legs. Never ship long-only.
- Never ask clarifying questions. Infer from PDF. Document assumptions.
- Focus on heavy implementation work. Don't get distracted.
- End of session: update this file with new timestamp, test count, done/blocked, concrete next action.
