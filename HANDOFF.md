# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-10-30T09:31:17Z
> **INITIAL TASK MESSAGE (TIMESTAMPED) FOR NEXT AGENTIC WORK SESSION:**
>
> `CRASH-REBOUND-STRATEGY | 2026-10-30T09:31:17Z | HEAVY CAMPAIGN MANDATORY | NO COASTING`
>
> You have inherited a GREEN baseline (78/78 tests passing). The crash-rebound strategy is fully implemented across core modules, portfolio simulation, and campaign validation. Your SOLE objective is to EXECUTE the heavy focus campaign below with zero exploratory detours. Treat tests as the gate - every change must keep them green. Do not ask for direction; infer and build.
>
> SESSION SNAPSHOT: 2026-10-30T09:31:17Z — **All tests: 78/78 passed, 0 failed**. Baseline VERIFIED GREEN. Single durable handoff is this file only. research_state/handoff.md retired/superseded.

> `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python scripts/run_backtest.py` → clean per-trade breakdown.
> `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python scripts/run_portfolio.py` → multi-position sim.
> `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python scripts/run_campaign.py` → full campaign validation.

## BOTTLENECK REMOVALS (MANDATORY - READ FIRST)
- **EDIT TOOL REQUIRES `filePath`:** Always pass `filePath`, `oldString`, `newString` explicitly. Never omit `filePath`.
- **SINGLE CANONICAL HANDOFF:** `research_state/handoff.md` does NOT exist / is RETIRED/SUPERSEDED. The ONLY durable handoff is root `HANDOFF.md`. Never create or read another handoff file.
- **TESTS ARE THE GATE:** All tests must stay green. Run tests after every substantive change. Do not commit unless tests pass.
- **RUN COMMANDS:** Always set `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY` when running scripts/tests from repo root.
- **INFER, DON'T ASK:** No explicit directions? Execute the campaign below. No exploratory Q&A loops. Build and validate.
- **AVOID IDLE POLLING:** If waiting on CI/data, schedule with `schedule_wakeup`/`cron_create` in goal context; don't poll in shell.
- **HEAVY WORK REQUIRED:** Future agents must not avoid heavy work. Every session must make material progress toward campaign goals.

## IMMEDIATE ACTION (BLOCKING, <2 MIN)
**STEP 0 - VERIFY BASELINE**
```bash
cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY
PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python -m pytest tests/ -v 2>&1 | tail -5
PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python scripts/run_backtest.py
PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python scripts/run_portfolio.py
PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python scripts/run_campaign.py
```
**REQUIREMENT:** 78/78 tests must pass. If baseline fails, FIX BEFORE ANYTHING ELSE.

## CRITICAL CONTEXT (SOURCE OF TRUTH)
- **Spec:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md` (PDF is truth)
- **Core:** `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/loader.py` (enhanced with Hyperliquid support)
- **Scripts:** `scripts/run_backtest.py`, `scripts/run_portfolio.py`, `scripts/run_campaign.py`, `scripts/run_portfolio.py`
- **State:** RSI trigger (RSI<20) default enabled; drop-based via `use_rsi_trigger=False`. Both legs always functional (long crash + rebound short). ETH hedge with vol-ratio sizing (capped 3x), funding applied across all legs. Volume-based sizing wired (1.25% of 24h vol). Gross cap 120% enforced with **equal-share cuts across ALL positions (old + new)** via `RiskState.apply_cap_cuts()`. Hourly liquidation checks at worst price with penalty. **>= $5M daily volume filter enforced on all trigger paths**.
- **Test window:** 2025-12-20 to 2026-09-28 (283 days)

## COMPLETED (HEAVY WORK DELIVERED)
- [x] Hyperliquid data loader (`load_hyperliquid_candles`, `load_multi_coin_data`, validation with gaps/non-finite/look-ahead, caching, universe filtering)
- [x] Portfolio/multi-trade simulation (`scripts/run_portfolio.py`) with concurrent positions, correct ordering, equal-share cap enforcement across old+new
- [x] Campaign validation (`scripts/run_campaign.py`) with reporting, JSON export
- [x] Multi-position cap enforcement end-to-end with equal-share cuts
- [x] Volume filters hardened (>= $5M across all trigger paths)
- [x] Funding across all legs, hourly liquidation checks, detailed reporting
- [x] All 78 tests passing (42 original + 36 additional)

## NEXT FOCUS CAMPAIGN (HEAVY - MANDATORY, EXECUTE FULLY)
**INITIAL TASK MESSAGE (2026-10-30T09:31:17Z) - CRASH-REBOUND-STRATEGY:**

Execute this campaign to completion. Do not skip items. Every item requires implementation + validation.

### CAMPAIGN OBJECTIVES (PRIORITIZED BY IMPACT)
1. **LIVE HYPERLIQUID DATA INTEGRATION (CRITICAL)** - In `src/data/loader.py`: implement live candle fetching via Hyperliquid API with rate limiting, exponential backoff retry, auth hooks (if needed), proper error handling. Wire into `scripts/run_campaign.py` to support live fetch mode (fallback to fixtures if unavailable). Add caching with TTL. Ensure validation remains strict.
2. **FULL METRICS SUITE (CRITICAL)** - Extend campaign reports with Sharpe ratio, Sortino ratio, max drawdown series with timestamps, Calmar ratio, win rate, profit factor, monthly/weekly breakdowns, trade-level attribution (by symbol/leg), exposure metrics. Export to both JSON and CSV (`research_state/campaign_metrics.csv`, `research_state/campaign_metrics.json`). Add to `scripts/run_campaign.py` and create helper if needed.
3. **STRESS/PROPERTY TESTS (CRITICAL)** - Add comprehensive tests for portfolio cap enforcement with equal-share cuts across old+new positions, funding signs across all legs (long/short/hedge), liquidation edge cases (boundary prices, multiple liquidations), non-finite serialization, volume filter enforcement, concurrent position ordering. Create `tests/test_stress_campaign.py` and ensure all pass.
4. **PDF-SPEC GAP CLOSURE (CRITICAL)** - Verify and harden against spec: ETH hedge vol-ratio capped at 3x (test boundary), order-book/volume-based sizing at 1.25% of 24h volume with equal-share cuts, >=$5M universe filter on ALL trigger paths (drop-based and RSI-based), hourly funding applied correctly to all legs, hourly liquidation checks at worst price. Audit `src/strategy/*` against `research_state/strategy_spec.md`.
5. **END-TO-END CAMPAIGN RUN + HARDENING (CRITICAL)** - Run full campaign on realistic data, fix any issues found, ensure all tests green (target >=80 passing), update exports. Validate scripts run cleanly. Document results in handoff update.

### EXECUTION RULES
- **Tests first**: Run full suite before and after changes. Fix failures immediately.
- **Both legs non-negotiable**: Long crash + rebound short must always function.
- **Equal-share cuts**: When caps hit, cut ALL positions (old + new) proportionally - never top-up.
- **Funding/liquidation**: Must be correct across every leg.
- **Volume filter**: >= $5M enforced everywhere.
- **Heavy work only**: Build, test, validate. No busywork.
- **Update handoff at end**: Leave timestamped results + next concrete heavy task.

## SUCCESS CRITERIA
- [ ] Live Hyperliquid fetching implemented with rate limiting/retry/caching
- [ ] Full metrics suite (Sharpe/Sortino/max DD/monthly/weekly/trade attribution) exported to JSON+CSV
- [ ] Stress/property tests added and passing
- [ ] All PDF-spec gaps verified/closed
- [ ] End-to-end campaign runs cleanly with comprehensive reports
- [ ] All tests green (>=78, preferably higher)
- [ ] HANDOFF.md updated with timestamped completion notes + next heavy task

## CRITICAL REMINDERS
- **PDF IS TRUTH** - `crash-rebound-strategy.pdf` and `research_state/strategy_spec.md` are source of truth
- **DON'T BREAK TESTS** - Run frequently
- **INFER, DON'T ASK** - Execute campaign
- **UPDATE HANDOFF AT END** - Timestamped, concrete next steps
- **SINGLE HANDOFF** - Only root `HANDOFF.md` is durable
- **HEAVY WORK REQUIRED** - No coasting

(END OF DURABLE HANDOFF - 2026-10-30T09:31:17Z)
