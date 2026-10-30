# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-10-30T04:39:17Z

> SESSION VERIFIED: 2026-10-30T04:39:17Z — `python -m pytest -q` → **63 passed, 0 failed**. Baseline green. Bottlenecks removed. BOTH legs (long crash + rebound short) are non-negotiable per repo name.

## MISSION FOR NEXT SESSION
**DO NOT SKIM. START HERE. IMMEDIATELY EXECUTE STEP 0.**

Repo: **CRASH-REBOUND-STRATEGY**. Mandate: Hyperliquid hourly perps crash-rebound backtester. BOTH legs are non-negotiable — long crash entry AND rebound short must both work correctly. Any session touching only long leg is off-mission.

Source of truth: `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Treat PDF as ground truth; trace major behavioral changes to it. Keep passing tests passing unless spec explicitly contradicts and justification is documented.

## VERIFIED CURRENT STATE
- Tests: `python -m pytest -q` → **63 passed, 0 failed** (rebound-short paths exercised)
- Spec: `research_state/strategy_spec.md` (+9% target, 50h/48h exits, ATR(14)*8 stop, 1.25% of 24h vol sizing, 120% gross cap w/ equal-share cuts, ETH hedge per leg, RSI(21h)<20 trigger, >=$5M vol)
- Gap analysis: `research_state/gap_analysis.md`
- Core modules: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/loader.py`
- Working features: drop-based/RSI trigger scaffolding, rebound-short fully implemented and tested, ATR stops, next-bar entry, risk gating, slippage/commission

## BOTTLENECKS (current)
**NONE BLOCKING.** Suite collects and passes. No import errors. Config complete. NameErrors fixed. Previous bottlenecks cleared.

## NEXT AGENTIC SESSION — HEAVY IMPLEMENTATION CAMPAIGN

### STEP 0: VERIFY BASELINE (BLOCKING - MUST DO FIRST)
```bash
cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY
python -m pytest -q
cat research_state/strategy_spec.md | head -80
cat research_state/gap_analysis.md | head -60
```
Must show **>= 63 passed, 0 failed**. Do not proceed if not green.

### CAMPAIGN 1: MAKE RSI TRIGGER DEFAULT + HARDEN (Priority 1 - 1-2h)
**Goal:** Make PDF's primary trigger (RSI(21)<20 on >=$5M vol) the default path. Drop-based remains available via flag.

**Status:** `use_rsi_trigger` exists in config and `detect_crash_rsi` implemented, but default is True already? Let us check - config shows `use_rsi_trigger: bool = True` (line ~70 in config). Good. But need to ensure it's actually used everywhere and tested.

Tasks (do ALL):
1. Verify `generate_signal` passes `use_rsi_trigger` from config (it does). Ensure RSI path is exercised.
2. Add comprehensive tests for RSI trigger in `tests/test_crash_rebound_strategy.py`: RSI below threshold triggers, above threshold doesn't, insufficient candles returns False, volume filter behavior.
3. Ensure drop-based path (`use_rsi_trigger=False`) still works - add explicit test.
4. Validate `min_daily_volume_usd` filter logic is correct for both raw volume and volume*price estimation.
5. All tests pass.

Files: `src/strategy/crash_rebound.py`, `src/strategy/config.py`, `tests/test_crash_rebound_strategy.py`

### CAMPAIGN 2: WIRE ETH HEDGE INTO BACKTEST (Priority 1 - CRITICAL, 2-4h)
**Goal:** Every trade hedged with ETH as specified. Hedge PnL MUST contribute to total returns. BOTH legs of main trade + hedges must be coherent.

**Status:** `compute_eth_hedge_size` exists, `TradeResult` has hedge fields added. Not wired into `backtest_simple`.

Tasks (do ALL - this is heavy):
1. In `backtest_simple`, when entering long crash leg: compute hedge size using `compute_eth_hedge_size(coin_candles, eth_candles, coin_position_value, config)`. If `config.enable_eth_hedge` and valid, open short ETH hedge at entry. Track hedge entry price/value.
2. When rebound short opens (after long hits target), also open long ETH hedge for that leg? Or hedge per leg as specified - "every trade hedged with ETH" means each leg hedged. Need to be precise per spec. Read spec again carefully.
3. Close hedges when corresponding leg closes. Apply slippage/commission on hedge entries/exits.
4. Apply hourly funding on hedge legs using `config.funding_rate_pct_per_hour`. Funding = notional * rate * hours_held (or per bar). Track funding costs.
5. Add hedge PnL to total PnL. Update r-multiple accounting to be sensible (or just report total PnL including hedges).
6. Handle missing `eth_candles` gracefully (skip hedging or use fallback).
7. Add tests: hedge sizing logic, hedge direction correctness (long coin -> short ETH hedge), hedge PnL signs, funding applied.
8. All existing tests must still pass.

Files: `src/backtest/engine.py`, `src/strategy/crash_rebound.py`, `src/strategy/risk.py`, `tests/`

### CAMPAIGN 3: VOLUME-BASED SIZING + 120% GROSS CAP WITH EQUAL-SHARE CUTS (Priority 1 - 2-3h)
**Goal:** Match PDF exactly - 1.25% of 24h volume sizing, 120% gross cap with equal-share cuts (cut positions, never top up).

**Status:** `position_size_by_volume` exists, `RiskState.cut_positions_to_cap` exists. Not wired into backtest/generate_signal.

Tasks (do ALL):
1. Add daily volume estimation from candles to sizing path. Use last 24 bars or sum of volume * price? Config says "1.25% of coin's 24h volume" - need to interpret as 1.25% of 24h volume in quote currency (USD). Compute from candles.
2. Wire volume-based sizing: if `config.enable_volume_based_sizing` True, use `position_size_by_volume(entry_price, daily_volume_usd, config.position_size_pct_of_daily_volume)`. Also consider risk-based as fallback? Or per spec prefer volume-based.
3. Track gross exposure across all open positions in backtest state (sum of |position_value| or per spec definition).
4. When adding new position would breach 120% gross cap, cut ALL positions (existing + new conceptually) to equal share so total = 120% cap. "Equal-share cuts" - distribute the cap equally.
5. Implement in backtest - need to track portfolio state across multiple trades/signals.
6. Add tests for cap enforcement and equal-share cuts.
7. All tests pass.

Files: `src/strategy/risk.py`, `src/strategy/crash_rebound.py`, `src/backtest/engine.py`, `tests/`

### CAMPAIGN 4: EXECUTION REALISM + RUNNER (Priority 2 - 2-3h)
**Goal:** Runnable end-to-end with realistic assumptions.

Tasks:
1. Add funding rate modeling throughout (hourly) - especially for hedges and any holding costs.
2. Add basic liquidation checks (price moves against position beyond threshold).
3. Create `scripts/run_backtest.py` that loads data (use fixtures or CSV), runs strategy with both legs enabled, prints detailed results including hedge PnL.
4. Add minimal README with usage.
5. Test end-to-end.
6. Document assumptions in code.

Files: `scripts/run_backtest.py`, `README.md`, `src/backtest/engine.py`

## IMMEDIATE NEXT ACTION (EXECUTE NOW)
```bash
cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY
python -m pytest -q  # MUST be 63 passed, 0 failed
```
Then read `research_state/strategy_spec.md` fully and `research_state/gap_analysis.md`. Start **CAMPAIGN 1** immediately. Do not ask questions - infer from PDF and existing codebase patterns. Prioritize heavy implementation.

## SUCCESS CRITERIA
- [ ] RSI(21)<20 default trigger tested and working; drop-based still available via `use_rsi_trigger=False`
- [ ] ETH hedge wired for every trade leg with vol-ratio sizing, 3x cap, funding applied; hedge PnL in totals
- [ ] Volume-based sizing (1.25% of 24h vol) + 120% gross cap with equal-share cuts wired
- [ ] ALL existing tests pass + new tests for added functionality (target: grow test count meaningfully)
- [ ] End-to-end `scripts/run_backtest.py` works
- [ ] Both legs always functional

## CRITICAL REMINDERS
- **BOTH LEGS NON-NEGOTIABLE** - long crash AND rebound short must both work
- **HEAVY WORK REQUIRED** - build, test, wire everything. No stubs.
- **PDF IS TRUTH** - match spec precisely
- **DON'T BREAK TESTS** - add, don't remove passing tests
- **INFER, DON'T ASK** - make reasonable assumptions, document them
- **UPDATE HANDOFF AT END** - new timestamp, test count, done/blocked, concrete next action

**START WITH STEP 0 NOW. BEGIN CAMPAIGN 1.**
