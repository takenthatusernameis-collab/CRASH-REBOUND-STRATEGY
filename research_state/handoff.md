# CRASH-REBOUND-STRATEGY — SINGLE DURABLE HANDOFF (START HERE)
**TIMESTAMP:** 2026-10-30T02:37:21Z
**REPO:** CRASH-REBOUND-STRATEGY
**BRANCH:** main
**WORKING TREE:** clean
**TEST BASELINE:** 58 passed, 0 failed (`/usr/share/miniconda/bin/python -m pytest -q`)

## Mission (from repo name)
Implement and harden a Hyperliquid hourly perps crash-rebound backtester.
**MANDATE — BOTH LEGS ARE NON-NEGOTIABLE:** long crash entry AND rebound short must both work correctly. Any session that only touches the long leg is off-mission.

Source of truth: `crash-rebound-strategy.pdf` → resolved in `research_state/strategy_spec.md`.

## Verified current state
- `research_state/strategy_spec.md`: PDF rules extracted (+9% target, 50h/48h exits, ATR(14)*8 stop, 1.25% of 24h vol sizing, 120% gross cap with equal-share cuts, ETH hedge per leg, RSI(21h)<20 trigger).
- `src/strategy/crash_rebound.py`: ATR-based stop wired; target uses `config.target_pct` (+9%). Trigger still price-drop based with fallback.
- `src/strategy/risk.py`: `RiskState`/`DailyRiskState`, `cut_positions_to_cap` exists, ATR helpers present.
- `src/backtest/engine.py`: `backtest_simple` with next-bar entry, stop/target/time-exit, look-ahead guard, risk gates; rebound short opens when long hits +9% target; returns `trades` with multi-leg entries.
- `src/data/loader.py`: fixtures for crash-rebound scenarios.
- Tests: 58 passing. Rebound-short paths exercised by existing tests.

## Bottlenecks to remove (priority order)
1. **Short slippage/commission convention (P0)** - `_slippage_commission_per_share` for short entry (sell-to-open) vs cover (buy-to-cover) unverified. PnL signs must be correct.
2. **Multi-leg r_multiple accounting (P0)** - `total_risk = risk * shares * 2.0` is a hack. Define correct convention and fix.
3. **120% gross cap not enforced (P1)** - `cut_positions_to_cap` exists but not wired in multi-position/multi-symbol flows.
4. **Trigger mismatch (P2)** - PDF requires RSI(21h)<20; implement with flag + fallback and sync spec.
5. **Coverage/trade structure assertions (P3)** - Need stronger behavior tests proving both legs and correct accounting.

## NEXT AGENTIC SESSION — IMMEDIATE ACTIONS (DO NOT DEVIATE)

### STEP 0: VERIFY BASELINE (BLOCKING)
- [ ] Run: `/usr/share/miniconda/bin/python -m pytest -q` — record exact count. Must be green before changes.

### P0: LOCK REBOUND-SHORT CORRECTNESS (BLOCKING)
- [ ] **Audit**: Trace `_slippage_commission_per_share` usage in `src/backtest/engine.py` for short entry (`sell`) and cover (`buy`). Write explicit comment documenting convention.
- [ ] **Tests**: Add behavior tests with zero slippage/commission proving `PnL_short = (short_entry_px - short_exit_px) * shares`. Test sell-to-open and buy-to-cover.
- [ ] **Trades**: Assert `trades` contains both legs with correct `side`/`entry`/`exit`/`pnl`/`reason` on rebound.
- [ ] **Fix**: Correct any sign/convention bugs if found.
- [ ] **r_multiple**: Replace hack with correct definition (document in code). Add tests.
**Goal:** Trust in both legs + correct accounting. Add +4-6 behavior tests.

### P1: ENFORCE 120% GROSS CAP
- [ ] **Wire**: Enforce `RiskState.cut_positions_to_cap` in engine/multi-symbol flows when combined gross > 120% of equity (equal-share cuts, never top-up).
- [ ] **Track**: Ensure gross exposure tracked correctly across positions.
- [ ] **Tests**: Add multi-position cap test asserting pre/post sizes and gross.
**Goal:** Add +2-4 tests.

### P2: ALIGN TO RSI(21h)<20 TRIGGER
- [ ] **Implement**: Add RSI(21h)<20 trigger in `src/strategy/crash_rebound.py` behind config flag, keep price-based fallback.
- [ ] **Sync**: Update `research_state/strategy_spec.md` to reflect implementation.
- [ ] **Tests**: Add tests for RSI trigger and fallback.
**Goal:** Add +2-4 tests.

### P3: EXPAND FIXTURES & RAISE COVERAGE
- [ ] **Fixtures**: Expand `make_fixture_crash_rebound_multi()` / add liquid-coin style cases.
- [ ] **Smoke**: Update `research_state/backtest_smoke.json` with results.
- [ ] **Tests**: Add behavior tests for multi-symbol paths.
**Goal:** Reach >= 70 total tests with behavior assertions.

## VERIFICATION GATE (END OF SESSION — MANDATORY)
- [ ] `/usr/share/miniconda/bin/python -m pytest -q` green, count >= 58 (target >= 70). Record count.
- [ ] Both legs exercised; P0 behavior tests pass.
- [ ] Update this file with new timestamp, test count, done/blocked, concrete next action.
- [ ] Only commit changes under `research_state/*`, `src/*`, `tests/*`, `scripts/*`. No workflow edits.

## NOTES
- Prioritize by repo name: crash-rebound means BOTH legs. Do not stop at long-only.
- Infer from PDF via `research_state/strategy_spec.md` if needed; do not ask clarifying questions.
- Avoid malformed `edit` calls (must include `filePath`, `oldString`, `newString`).
- Keep changes minimal, testable, and correctness-first.
