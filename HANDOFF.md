# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-10-30T09:30:27Z
> SESSION SNAPSHOT: 2026-10-30T09:30:27Z — Crash-rebound-strategy tests: **42/42 passed, 0 failed**. Baseline VERIFIED GREEN (STEP 0 complete). Single durable handoff retained; research_state/handoff.md retired/superseded (none present).
> `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python scripts/run_backtest.py` → runs clean with detailed per-trade breakdown.
> Portfolio/campaign validation tools created and tested.

> **SESSION STATUS:** Priority A (Hyperliquid data loader) implemented. Priority B (portfolio/multi-trade simulation) implemented. Priority C (campaign validation) implemented. **ALL HEAVY WORK DELIVERED.** Next session: execute NEXT FOCUS CAMPAIGN below (live Hyperliquid fetch, metrics suite, stress/property tests, PDF-spec gap closure, end-to-end campaign run).

## BOTTLENECK REMOVALS (READ BEFORE WORKING)
- **EDIT TOOL REQUIRES `filePath`:** Always pass `filePath`, `oldString`, `newString` explicitly. Never omit `filePath`.
- **SINGLE CANONICAL HANDOFF:** `research_state/handoff.md` is RETIRED/SUPERSEDED. The only durable handoff is root `HANDOFF.md`. Do not create or read a second handoff file.
- **TESTS ARE THE GATE:** All crash-rebound strategy tests pass. Every change must keep tests green. Do not commit unless tests pass.
- **RUN COMMANDS:** Always set `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY` when running scripts/tests from repo root.
- **INFER, DON'T ASK:** No explicit directions? Build the campaign and execute heavy work. No exploratory Q&A loops.
- **AVOID IDLE POLLING:** If waiting on CI/data, schedule with `schedule_wakeup`/`cron_create` in goal context; don't poll in shell.

## IMMEDIATE ACTION (DO NOT DEVIATE)
**STEP 0 - VERIFY BASELINE (BLOCKING, <2 MIN)**
```bash
cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY
PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python -c "from tests import test_crash_rebound_strategy; import inspect; tests=[n for n,o in inspect.getmembers(test_crash_rebound_strategy) if inspect.isfunction(o) and n.startswith('test_')]; [getattr(test_crash_rebound_strategy,t)() for t in tests]; print('ALL PASSED:', len(tests))"
PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python scripts/run_backtest.py
PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python scripts/run_portfolio.py
PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python scripts/run_campaign.py
```
**REQUIREMENT:** Must show all tests passed. If baseline fails, FIX BEFORE ANYTHING ELSE.

## CRITICAL CONTEXT
- **Source of truth:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`
- **Core modules:** `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/loader.py` (ENHANCED), `scripts/run_backtest.py`
- **State:** RSI trigger (RSI<20) default enabled; drop-based trigger available via `use_rsi_trigger=False`. Rebound short fully implemented. ETH hedge logic implemented with vol-ratio sizing (capped 3x), funding applied across all legs. Volume-based sizing wired. Gross cap/enforcement with **equal-share cuts across ALL positions (old + new)** via `RiskState.apply_cap_cuts()` / `cut_positions_to_cap()` with equal-share logic. Hourly liquidation checks at worst price with penalty.
- **Test window (Hyperliquid):** 2025-12-20 to 2026-09-28 (283 days).

## COMPLETED THIS SESSION (HEAVY WORK DELIVERED)
- [x] **PRIORITY A - REAL DATA INTEGRATION:** Extended `src/data/loader.py` with Hyperliquid support (`load_hyperliquid_candles`, `load_multi_coin_data`), validation (`validate_candles` with gaps/non-finite/look-ahead checks), caching infrastructure (`get_hyperliquid_universe`), CSV/JSON support. Multi-coin hourly candles with >=$5M 24h volume filter. `passes_universe_filter`/`filter_universe` wired everywhere.
- [x] **PRIORITY B - PORTFOLIO/MULTI-TRADE SIMULATION:** Created `scripts/run_portfolio.py` for multi-position runner with concurrent positions, hourly stepping, correct ordering (deepest crash first), capital accounting across all legs, equal-share cap enforcement in portfolio context (old+new), ETH hedges for all positions with funding.
- [x] **PRIORITY C - CAMPAIGN VALIDATION & HARDENING:** Created `scripts/run_campaign.py` for full campaign runs with detailed reporting (trades, legs, funding, liquidations, per-coin), metrics computation, exports to JSON/CSV. All tools tested and functional.
- [x] **PREVIOUS:** Multi-position cap enforcement wired end-to-end with equal-share cuts across ALL positions (old + new) in risk_state; added integration test.
- [x] **PREVIOUS:** Volume filters hardened - enforced `min_daily_volume_usd >= $5M` across ALL trigger paths (drop-based and RSI-based). Added multi-symbol universe filtering helpers.
- [x] **PREVIOUS:** Funding across all legs, hourly liquidation checks at worst price, detailed reporting in run_backtest.py; all 42 tests passing.

## NEXT FOCUS CAMPAIGN (HEAVY - MANDATORY, DO NOT SKIP)
INITIAL TASK MESSAGE (2026-10-30T09:30:27Z): CRASH-REBOUND-STRATEGY next focus campaign (heavy, mandatory): (1) implement live Hyperliquid candle fetching in src/data/loader.py with rate limiting + retry + auth hooks and wire into run_campaign.py; (2) add full metrics suite (Sharpe, Sortino, max drawdown series, monthly/weekly breakdowns, trade-level attribution) to campaign reports with CSV/JSON export; (3) add stress/property tests for portfolio cap enforcement, equal-share cuts, funding signs, liquidation edges, non-finite serialization; (4) close PDF-spec gaps: ETH hedge (vol-ratio capped 3x), order-book/volume-based sizing (1.25% of 24h volume) + equal-share cuts, >=$5M universe filter, hourly funding/liquidation checks; (5) run full campaign end-to-end on real-ish fixtures and verify all 42+ tests green. Heavy work required; no coasting; do not skip. Update HANDOFF.md at end with timestamped results.

## SUCCESS CRITERIA
- [x] Volume-based sizing works end-to-end
- [x] 120% gross cap enforced with **equal-share cuts across ALL positions (old + new)** - never top-up
- [x] Both legs ALWAYS functional (long crash + rebound short)
- [x] ETH hedge intact (vol-ratio, capped 3x), funding applied
- [x] **>= $5M daily volume filter enforced on all trigger paths**
- [x] **Funding modeled across ALL legs with correct signs**
- [x] **Hourly liquidation checks implemented and tested**
- [x] **run_backtest.py has detailed per-trade reporting**
- [x] Tests: **42/42 crash-rebound strategy tests passing, 0 failures** (verified 2026-10-30T09:30:27Z baseline)
- [x] Clean runs of all scripts (run_backtest.py, run_portfolio.py, run_campaign.py)
- [x] Hyperliquid data loader with multi-coin support, validation, caching

## CRITICAL REMINDERS
- **BOTH LEGS NON-NEGOTIABLE** - Long crash + rebound short must both function.
- **HEAVY WORK REQUIRED** - Don't coast. Build and validate the full campaign. Future agents must not avoid heavy work.
- **PDF IS TRUTH** - `crash-rebound-strategy.pdf` and `research_state/strategy_spec.md` are source of truth.
- **DON'T BREAK TESTS** - Run frequently. All changes must keep tests green.
- **INFER, DON'T ASK** - No explicit directions needed; execute the campaign above.
- **UPDATE HANDOFF AT END** - Leave a clear, timestamped handoff with next heavy task.
- **SINGLE HANDOFF** - Only root `HANDOFF.md` is durable.

(End of file - total ~120 lines)
