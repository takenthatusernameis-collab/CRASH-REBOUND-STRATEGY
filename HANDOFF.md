# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-10-30T18:49:10Z

## CURRENT VERIFIED STATUS — 2026-10-30 (supersedes stale state statements below)

- `src/strategy/config.py` defaults: `use_rsi_trigger=True` (RSI(21)<20 primary crash trigger), `enable_eth_hedge=True`, `enable_volume_based_sizing=True` (1.25% of 24h volume), `min_daily_volume_usd=5_000_000.0`, `gross_cap_pct=120.0` with equal-share cuts via `RiskState.apply_cap_cuts()`. **These are already ON; do not treat them as open bottlenecks.**
- `scripts/run_campaign.py` already runs `use_rsi_trigger=True`, `enable_eth_hedge=True`, `enable_volume_based_sizing=True`. It is a **fixture smoke test only**, not a real Hyperliquid historical campaign. The 2025-12-20 to 2026-09-28 (283-day) window remains **NOT RUN**.
- `tests/test_stress_campaign.py` exists with 7 stress tests (equal-share cuts, funding across legs, liquidation edge, volume filter all paths, ETH hedge 3x cap boundary, RSI primary trigger, metrics structure).
- `committed `research_state/campaign_results.json` is a legacy fixture artifact; not real-data or 283-day result. See `research_state/campaign_artifact_provenance_erratum.md`.
- `scripts/run_campaign.py` emits explicit fixture-only provenance; `tests/test_campaign_provenance.py` asserts exported JSON cannot be mistaken for market performance evidence.
- Do not promote fixture PnL or trade counts. The genuine 283-day run requires verified hourly Hyperliquid candles, coverage and data-provenance checks; do not fill gaps with fixtures or static symbol lists.
- Test suite: **89 passed, 0 failed** (`PYTHONPATH=... python -m pytest tests/ -v`). Do not claim 78.

---
> **INITIAL TASK MESSAGE (TIMESTAMPED) FOR NEXT AGENTIC WORK SESSION:**
>
> `CRASH-REBOUND-STRATEGY | 2026-10-30T18:49:10Z | METRICS SUITE + END-TO-END CAMPAIGN RUN | REAL 283-DAY HYPERLIQUID WINDOW (2025-12-20 TO 2026-09-28) | NO COASTING | HEAVY WORK MANDATORY`

SESSION SNAPSHOT: 2026-10-30T18:49:10Z — Baseline VERIFIED GREEN (89 passed, 0 failed). All campaign items 1–5 (RSI primary trigger, ETH hedge every leg, volume-based sizing ON, volume filter everywhere, stress tests) are implemented and passing. Remaining heavy work: campaign item #6 — end-to-end campaign run with metrics suite exported to `research_state/campaign_metrics.json` + `.csv`, then the real 283-day Hyperliquid run with verified hourly candles.

Single durable handoff is this file only. `research_state/handoff.md` retired/superseded. Never create or read another handoff file.

## BOTTLENECK REMOVALS (MANDATORY - READ FIRST)

- **STALE HANDOFF CLAIMS REMOVED:** `enable_volume_based_sizing=False` default and `run_campaign.py` drop-based trigger were already fixed (both True/RSI). Do not re-open them as tasks. Do not re-file already-green items.
- **EDIT TOOL REQUIRES `filePath`:** Always pass `filePath`, `oldString`, `newString` explicitly. Never omit `filePath`.
- **SINGLE CANONICAL HANDOFF:** Only root `HANDOFF.md` is durable. `research_state/handoff.md` does NOT exist / is RETIRED/SUPERSEDED.
- **TESTS ARE THE GATE:** All tests must stay green. Run tests after every substantive change. Do not commit unless tests pass.
- **RUN COMMANDS:** Always set `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY` when running scripts/tests from repo root.
- **INFER, DON'T ASK:** No explicit directions? Execute the campaign below. No exploratory Q&A loops. Build and validate.
- **AVOID IDLE POLLING:** If waiting on CI/data, schedule with `schedule_wakeup`/`cron_create` in goal context; don't poll in shell.
- **HEAVY WORK REQUIRED:** Future agents must not avoid heavy work. Every session must make material progress toward campaign goals.
- **NO COASTING:** Idle sessions are bottlenecks. If blocked on data/CI, schedule a wakeup and switch to the next independent campaign item.

## CRITICAL CONTEXT (SOURCE OF TRUTH)

- **Spec:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md` (PDF is truth)
- **Core:** `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/loader.py`
- **Scripts:** `scripts/run_backtest.py`, `scripts/run_portfolio.py`, `scripts/run_campaign.py`
- **State:** RSI trigger (RSI<20) default enabled; drop-based via `use_rsi_trigger=False`. Both legs always functional (long crash + rebound short). ETH hedge with vol-ratio sizing (capped 3x), funding applied across all legs. Volume-based sizing wired (1.25% of 24h vol, default ON). Gross cap 120% enforced with equal-share cuts across ALL positions (old + new) via `RiskState.apply_cap_cuts()`. Hourly liquidation checks at worst price with penalty. **>= $5M daily volume filter enforced on all trigger paths**.
- **Test window:** 2025-12-20 to 2026-09-28 (283 days)
- **Known gaps vs PDF spec** (see `research_state/gap_analysis.md`): real 283-day Hyperliquid run not executed (fixtures only); metrics suite (Sharpe/Sortino/max drawdown/Calmar/win rate/profit factor/monthly-weekly breakdowns/trade attribution/exposure) not yet exported to `campaign_metrics.json`/`.csv`.

## COMPLETED (HEAVY WORK DELIVERED)

- [x] Hyperliquid data loader (`load_hyperliquid_candles`, `load_multi_coin_data`, validation with gaps/non-finite/look-ahead, caching, universe filtering)
- [x] Portfolio/multi-trade simulation (`scripts/run_portfolio.py`) with concurrent positions, correct ordering, equal-share cap enforcement across old+new
- [x] Campaign validation (`scripts/run_campaign.py`) with reporting, JSON export (fixture-only)
- [x] Multi-position cap enforcement end-to-end with equal-share cuts
- [x] Volume filters hardened (>= $5M across all trigger paths)
- [x] Funding across all legs, hourly liquidation checks, detailed reporting
- [x] RSI(21)<20 primary crash trigger default ON; price-drop fallback via `use_rsi_trigger=False`
- [x] ETH hedge on every leg, vol-ratio capped at 3x
- [x] Volume-based sizing default ON at 1.25% of 24h vol
- [x] Stress/property tests added (`tests/test_stress_campaign.py`)
- [x] All tests green: **89 passed, 0 failed** (baseline verified 2026-10-30T18:49:10Z)

## NEXT FOCUS CAMPAIGN (HEAVY - MANDATORY, EXECUTE FULLY)

**PRIORITIZED BY REPO NAME (CRASH-REBOUND-STRATEGY) — crash-rebound strategy fidelity to the PDF spec is the #1 priority.**

Items 1–5 are complete and green. Execute item 6 to completion. Do not skip. Every item requires implementation + validation. No coasting.

### CAMPAIGN OBJECTIVE (REMAINING)

**6. END-TO-END CAMPAIGN RUN + METRICS SUITE (CRITICAL)** - Run the full campaign for the test window (2025-12-20 to 2026-09-28, 283 days). Extend campaign reports with Sharpe ratio, Sortino ratio, max drawdown series **with timestamps**, Calmar ratio, win rate, profit factor, monthly/weekly breakdowns, trade-level attribution (by symbol/leg), exposure metrics. Export to JSON + CSV (`research_state/campaign_metrics.json`, `research_state/campaign_metrics.csv`). Fix any issues found; validate scripts run cleanly; all tests green (>=89). Then pursue the real 283-day Hyperliquid run with verified hourly candles (not fixtures), with coverage and data-provenance checks.

### EXECUTION RULES
- **Tests first**: Run full suite before and after changes. Fix failures immediately.
- **Both legs non-negotiable**: Long crash + rebound short must always function.
- **Equal-share cuts**: When caps hit, cut ALL positions (old + new) proportionally - never top-up.
- **Funding/liquidation**: Must be correct across every leg.
- **Volume filter**: >= $5M enforced everywhere.
- **Heavy work only**: Build, test, validate. No busywork.
- **Update handoff at end**: Leave timestamped results + next concrete heavy task.

## SUCCESS CRITERIA

- [ ] RSI(21)<20 primary crash trigger with price-drop fallback; both legs functional; `run_campaign.py` uses `use_rsi_trigger=True`; tests green
- [ ] ETH hedge on every leg, vol-ratio capped at 3x (boundary tested), funding signs correct on long + short legs
- [ ] Volume-based sizing default ON (`enable_volume_based_sizing=True`) at 1.25% of 24h vol; `run_campaign.py` sets it True; equal-share cuts across old+new on cap breach
- [ ] >= $5M volume filter on all trigger paths + campaign/universe selection
- [ ] Stress/property tests added (`tests/test_stress_campaign.py`) and passing (>=89 total)
- [ ] End-to-end campaign run with metrics suite exported to JSON+CSV (`campaign_metrics.json`, `campaign_metrics.csv`)
- [ ] All tests green (>=89)
- [ ] HANDOFF.md updated with timestamped completion notes + next heavy task

## CRITICAL REMINDERS

- **PDF IS TRUTH** - `crash-rebound-strategy.pdf` and `research_state/strategy_spec.md` are source of truth
- **DON'T BREAK TESTS** - Run frequently
- **INFER, DON'T ASK** - Execute campaign
- **UPDATE HANDOFF AT END** - Timestamped, concrete next steps
- **SINGLE HANDOFF** - Only root `HANDOFF.md` is durable
- **HEAVY WORK REQUIRED** - No coasting

(END OF DURABLE HANDOFF - 2026-10-30T18:49:10Z)
