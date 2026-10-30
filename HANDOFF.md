# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-10-30T05:05:00Z

> SESSION VERIFIED: 2026-10-30T05:05:00Z — `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python -m pytest -q` → **71 passed, 0 failed**. Baseline green. BOTH legs (long crash + rebound short) are non-negotiable per repo name.

## MISSION FOR NEXT SESSION
**DO NOT SKIM. START HERE. IMMEDIATELY EXECUTE STEP 0.**

Repo: **CRASH-REBOUND-STRATEGY**. Mandate: Hyperliquid hourly perps crash-rebound backtester. BOTH legs are non-negotiable — long crash entry AND rebound short must both work correctly.

Source of truth: `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Treat PDF as ground truth.

## VERIFIED CURRENT STATE
- Tests: `python -m pytest -q` → **71 passed, 0 failed**
- RSI trigger default path (RSI<20) tested and enabled; drop-based trigger available via `use_rsi_trigger=False`
- Rebound short fully implemented and tested (hits target/stop/time exit)
- ETH hedge logic implemented in backtest (vol-ratio sizing via `compute_eth_hedge_size`, caps at 3x) with funding applied; hedge PnL tracked in results
- Core modules wired: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`
- End-to-end runner: `scripts/run_backtest.py`

## BOTTLENECKS (current)
**NONE BLOCKING.** Suite passes. No import errors.

## NEXT CAMPAIGN (HEAVY IMPLEMENTATION)

### STEP 0: VERIFY BASELINE (BLOCKING)
```bash
cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY
PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python -m pytest -q
PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python scripts/run_backtest.py
```
Must show **>= 71 passed, 0 failed**.

### PRIORITY 1: VOLUME-BASED SIZING + 120% GROSS CAP WITH EQUAL-SHARE CUTS (2-4h)
**Goal:** Match PDF exactly - 1.25% of 24h volume sizing, 120% gross cap with equal-share cuts.

Tasks:
1. Wire `position_size_by_volume()` and `enable_volume_based_sizing` into signal generation/backtest sizing path. Compute daily volume from candles (quote USD = sum(volume*close) over last 24h).
2. Track gross exposure across positions in backtest; enforce 120% gross cap. When breaching, cut all positions to equal share (use `RiskState.cut_positions_to_cap`).
3. Add tests for volume-based sizing and cap enforcement with equal-share cuts.
4. Ensure all existing tests still pass.

### PRIORITY 2: UNIVERSE/VOLUME FILTERS + REGIME HARDENING (1-2h)
**Goal:** Enforce >=$5M daily volume filter as per spec; tighten regime logic if needed.

Tasks:
1. Ensure RSI trigger path enforces `min_daily_volume_usd` (already implemented) and add tests.
2. Add universe-level filtering helpers if running multi-symbol.

### PRIORITY 3: EXECUTION REALISM (1-2h)
**Goal:** Closer to hourly sim with funding/liquidation checks.

Tasks:
1. Expand funding modeling, add simple liquidation checks.
2. Improve end-to-end runner with detailed reporting.

## SUCCESS CRITERIA
- [ ] Volume-based sizing (1.25% of 24h vol) wired with fallback to risk-based sizing
- [ ] 120% gross cap enforced with equal-share cuts when breached
- [ ] Both legs always functional; hedge PnL contributes to totals
- [ ] All tests pass + new tests added (target >= 75)
- [ ] `scripts/run_backtest.py` runs end-to-end cleanly

## CRITICAL REMINDERS
- **BOTH LEGS NON-NEGOTIABLE**
- **HEAVY WORK REQUIRED** - build, test, wire everything
- **PDF IS TRUTH**
- **DON'T BREAK TESTS**
- **INFER, DON'T ASK**
- **UPDATE HANDOFF AT END**

**START WITH STEP 0 NOW. BEGIN PRIORITY 1.**
