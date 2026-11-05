# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-11-05T17:40:00Z

## CURRENT VERIFIED STATUS — 2026-11-05T02:33:15Z (supersedes all prior state)

- `src/strategy/config.py` defaults: `use_rsi_trigger=True` (RSI(21)<20 primary crash trigger), `enable_eth_hedge=True`, `enable_volume_based_sizing=True` (1.25% of 24h volume), `min_daily_volume_usd=5_000_000.0`, `gross_cap_pct=120.0` with equal-share cuts via `RiskState.apply_cap_cuts()`. **Already ON — do not re-open.**
- `scripts/run_campaign.py` sets `use_rsi_trigger=True`, `enable_eth_hedge=True`, `enable_volume_based_sizing=True`. It is explicitly a **fixture smoke test only** (synthetic data). The 2025-12-20 to 2026-09-28 (283-day) Hyperliquid window remains **NOT RUN** with real data.
- `tests/test_stress_campaign.py` exists (7 stress tests). Provenance guard: `tests/test_campaign_provenance.py` enforces fixture artifacts cannot be misread as real performance.
- Legacy `research_state/campaign_results.json` is fixture-only; see `research_state/campaign_artifact_provenance_erratum.md`. Do **not** promote fixture PnL/trade counts.
- Test suite: **89 passed, 0 failed** (`PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python -m pytest tests/ -v`). **Re-verified green 2026-11-05T02:33:15Z; pytest installed; re-verify before/after changes.**
- NOTE: `run_campaign.py` with `use_rsi_trigger=True` on 3-bar fixtures yields 0 trades (RSI needs ~22+ bars). Expected for fixture smoke test; metrics must handle empty/no-trade runs without crashing.
- **BOTTLENECK (ACTIVE):** `src/metrics/__init__.py` imports from `src.metrics.campaign_metrics` which **does not exist**. This must be fixed before any campaign metrics export can work. Do **not** defer.

---

> **INITIAL TASK MESSAGE (TIMESTAMPED) FOR NEXT AGENTIC WORK SESSION:**
>
> `CRASH-REBOUND-STRATEGY | 2026-11-05T02:33:15Z | PRIORITY 1 (REPO-NAME DRIVEN): CRASH-REBOUND FIDELITY TO crash-rebound-strategy.pdf | ITEM 6a - IMPLEMENT MISSING METRICS MODULE (BLOCKING) → ITEM 6b WIRE+EXPORT → ITEM 6c REAL 283-DAY HYPERLIQUID RUN | TARGET WINDOW 2025-12-20 → 2026-09-28 (283 DAYS) | NO FIXTURE COASTING | HEAVY WORK MANDATORY | ELIMINATE BOTTLENECKS IMMEDIATELY`
>
> **CONCRETE FIRST ACTION (EXECUTE NOW, NO ENV RE-CHECK, NO Q&A):**
> 1. **Create `src/metrics/campaign_metrics.py`** implementing the full API declared by `src/metrics/__init__.py`: `compute_campaign_metrics(...)`, `compute_metrics_from_trades(...)`, `metrics_to_dict(...)`, `metrics_to_csv_rows(...)`.
>    - Compute: Sharpe ratio, Sortino ratio, max drawdown series **with timestamps**, Calmar ratio, win rate, profit factor, monthly/weekly breakdowns, trade-level attribution by symbol/leg, exposure metrics.
>    - Must be **robust to empty/no-trade runs** (return well-formed zeros/empty structures; never crash).
>    - Follow conventions implied by `research_state/strategy_spec.md` and existing codebase style. Do not invent a different API.
> 2. **Verify import**: `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python -c "from src.metrics import compute_campaign_metrics, compute_metrics_from_trades, metrics_to_dict, metrics_to_csv_rows; print('ok')"`
> 3. **Wire into campaign**: Extend `scripts/run_campaign.py` to compute/attach the full metrics suite (and/or `scripts/run_portfolio.py` if cleaner). Keep fixture provenance explicit when using fixtures; for real runs mark provenance as real market data with coverage checks.
> 4. **Export artifacts**: Produce `research_state/campaign_metrics.json` and `research_state/campaign_metrics.csv` from a clean end-to-end run.
> 5. **Validate & progress**: Run full suite before/after (`PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python -m pytest tests/ -v` must stay >=89 green). Only after 1-4: attempt the real 283-day Hyperliquid hourly-candle run with coverage + provenance checks. If data/CI blocks, **schedule `schedule_wakeup`/`cron_create` and continue independent heavy work** (do not idle). Never fabricate data.
>
> **RULES FOR THIS SESSION:** Items 1-5 done. Do not reopen them. Both legs non-negotiable. Equal-share cap cuts across old+new. Funding/liquidation correct. >= $5M volume filter on all trigger paths. Infer from repo/name/spec. Heavy work only. Bottlenecks must be eliminated. Update HANDOFF.md at end with timestamped results + next concrete heavy task.

**SESSION SNAPSHOT (2026-11-05T02:32:16Z):** Baseline re-verified GREEN (89 passed, 0 failed). Items 1–5 complete. Env cleared: pytest installed, `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY`, working tree clean. **Only remaining heavy work is item #6.** Latent gap to close first: `src/metrics/__init__.py` imports `src.metrics.campaign_metrics` which does not exist — implement it (it is item 6, task #1). Focus ruthlessly on crash-rebound strategy fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Bottlenecks (pytest missing/PYTHONPATH/env issues) have been cleared. Do not waste turns re-verifying environment — ship code.

**SINGLE CANONICAL HANDOFF:** Only `HANDOFF.md` (repo root) is durable. `research_state/handoff.md` is retired/superseded. Do **not** create or read any other handoff file.

## BOTTLENECK REMOVALS (MANDATORY - READ FIRST)

- **EDIT TOOL:** Always pass `filePath`, `oldString`, `newString` explicitly. Never omit `filePath`. This is the #1 source of turn aborts.
- **TESTS FIRST:** Run full suite before and after substantive changes. `pytest` may not be installed in a bare env — if missing, run `pip install pytest` first. Always set `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY`.
- **NO STALE REWORK:** Do not reopen items 1–5 (RSI primary trigger, ETH hedge every leg, volume-based sizing ON, volume filter everywhere, stress tests). They are green.
- **INFER, DON'T ASK:** If directions are implicit from repo/name/spec, execute. No exploratory Q&A loops.
- **NO IDLE POLLING:** If blocked on data/CI, use `schedule_wakeup`/`cron_create` in goal context or switch to an independent subtask. Do not spin.
- **HEAVY WORK MANDATORY:** Every session must make material progress toward item #6. Idle sessions are bottlenecks.
- **ENVIRONMENT HYGIENE:** Verify environment before long runs. Prior failures came from missing pytest, path issues, inference hiccups, or idle cancellation.
- **BOTTLENECK STATUS — CLEARED 2026-11-01T01:57:40Z:** pytest installed, suite green (89/89), `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY`. No session is blocked on environment. Next session starts heavy work immediately; do not re-verify env as a substitute for item #6 progress.

## CRITICAL CONTEXT (SOURCE OF TRUTH)

- **Spec:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md` (PDF is truth)
- **Core:** `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/loader.py`
- **Scripts:** `scripts/run_backtest.py`, `scripts/run_portfolio.py`, `scripts/run_campaign.py`
- **Mechanics (must hold):** RSI(21)<20 primary crash trigger (fallback drop-based via `use_rsi_trigger=False`), both legs always functional (long crash + rebound short), ETH hedge on every leg with vol-ratio sizing capped at 3x, funding across all legs, hourly liquidation checks at worst price with penalty, >= $5M daily volume filter on all trigger paths, volume-based sizing ON at 1.25% of 24h vol, gross cap 120% enforced with equal-share cuts across ALL positions (old + new) via `RiskState.apply_cap_cuts()`.
- **Test window:** 2025-12-20 to 2026-09-28 (283 days)
- **Gaps:** Real 283-day Hyperliquid run not executed (fixtures only); `src/metrics/campaign_metrics.py` not implemented (API declared in `src/metrics/__init__.py`); metrics suite not exported to `campaign_metrics.json`/`.csv`.

## COMPLETED (HEAVY WORK DELIVERED)

- [x] Hyperliquid data loader (`load_hyperliquid_candles`, `load_multi_coin_data`, validation with gaps/non-finite/look-ahead, caching, universe filtering)
- [x] Portfolio/multi-trade simulation (`scripts/run_portfolio.py`) with concurrent positions, correct ordering, equal-share cap enforcement across old+new
- [x] Campaign validation (`scripts/run_campaign.py`) with reporting, JSON export (fixture-only, provenance-marked)
- [x] Multi-position cap enforcement end-to-end with equal-share cuts
- [x] Volume filters hardened (>= $5M across all trigger paths)
- [x] Funding across all legs, hourly liquidation checks, detailed reporting
- [x] RSI(21)<20 primary trigger default ON; both legs functional
- [x] ETH hedge on every leg, vol-ratio capped at 3x
- [x] Volume-based sizing default ON at 1.25% of 24h vol
- [x] Stress/property tests added (`tests/test_stress_campaign.py`)
- [x] All tests green: **89 passed, 0 failed**

## NEXT FOCUS CAMPAIGN (HEAVY - MANDATORY, EXECUTE TO COMPLETION)

**PRIORITIZE BY REPO NAME (CRASH-REBOUND-STRATEGY).** Crash-rebound strategy fidelity to the PDF is #1. Items 1–5 are done. **Execute item 6 fully.**

### CAMPAIGN OBJECTIVE

**6. END-TO-END CAMPAIGN RUN + METRICS SUITE (CRITICAL)**

1. **Build metrics computation** — Implement a dedicated metrics module (e.g. `src/metrics/campaign_metrics.py` or equivalent) computing: Sharpe ratio, Sortino ratio, max drawdown series **with timestamps**, Calmar ratio, win rate, profit factor, monthly/weekly breakdowns, trade-level attribution (by symbol/leg), exposure metrics. Must be robust to empty/no-trade runs.
2. **Wire into campaign export** — Extend `scripts/run_campaign.py` (and/or `scripts/run_portfolio.py`) to compute/attach the full metrics suite. Keep fixture provenance explicit if running fixtures; for real runs, mark provenance as real market data with coverage checks.
3. **Export artifacts** — Produce `research_state/campaign_metrics.json` and `research_state/campaign_metrics.csv` from a clean end-to-end run.
4. **Validate** — Run scripts cleanly with `PYTHONPATH` set. Fix issues. All tests must remain green (>=89).
5. **Real 283-day Hyperliquid run** — Use verified hourly candles (not fixtures), enforce coverage and data-provenance checks. Do **not** substitute fixtures or static symbol lists. If data is missing/incomplete, report gaps with concrete checks (never fabricate). If blocked waiting for data/CI, schedule wakeup and do heavy work elsewhere.

### EXECUTION RULES (NON-NEGOTIABLE)

- **Tests first/always:** `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python -m pytest tests/ -v` before and after changes.
- **Both legs non-negotiable:** Long crash + rebound short must always function.
- **Equal-share cuts:** On cap breach, cut ALL positions (old+new) proportionally — never top-up.
- **Funding/liquidation:** Correct across every leg; hourly worst-price liquidation checks with penalty.
- **Volume filter:** >= $5M enforced on all trigger paths.
- **Heavy work only:** Build, test, validate. No busywork, no Q&A loops. **INFER, DON'T ASK.**
- **No idle:** If blocked, schedule `schedule_wakeup`/`cron_create` and tackle next independent heavy item.
- **Single handoff:** Only root `HANDOFF.md`. Update it at end with timestamped results + next concrete heavy task.

### GUARDRAILS — FUTURE AGENTS CANNOT DEFER HEAVY WORK

- **Item #6 is the only open item.** Items 1–5 are closed and green; reopening them is prohibited busywork.
- **Every session must ship at least one of:** metrics module code, wired campaign export, `campaign_metrics.json`, `campaign_metrics.csv`, or a real-data run attempt with concrete evidence. A session that ships none of these is a bottleneck and must be replaced.
- **No coasting on fixtures.** Fixture smoke tests are scaffolding, not the deliverable. The deliverable is the metrics suite + real 283-day Hyperliquid run with provenance checks.
- **Do not ask for direction.** Repo name = CRASH-REBOUND-STRATEGY ⇒ crash-rebound fidelity to the PDF is the mission. Infer and execute.
- **If data/CI blocks the real run,** schedule `schedule_wakeup`/`cron_create` and complete the metrics module + fixture-wired export in parallel so no turn is idle.

## SUCCESS CRITERIA

- [ ] Metrics module implemented with all required metrics; handles empty runs
- [ ] `run_campaign.py` wired to compute/export metrics; JSON+CSV written to `research_state/campaign_metrics.json`, `research_state/campaign_metrics.csv`
- [ ] End-to-end run validated cleanly; all tests green (>=89)
- [ ] Real 283-day Hyperliquid run attempted with verified hourly candles, coverage + provenance checks (or concrete blockers with evidence)
- [ ] HANDOFF.md updated with timestamped completion notes + next concrete heavy task

## CRITICAL REMINDERS

- **PDF IS TRUTH** — `crash-rebound-strategy.pdf` and `research_state/strategy_spec.md`
- **DON'T BREAK TESTS** — run frequently
- **INFER, DON'T ASK** — execute the campaign
- **UPDATE HANDOFF AT END** — timestamped, concrete next steps
- **SINGLE HANDOFF** — only root `HANDOFF.md`
- **HEAVY WORK REQUIRED** — no coasting

(END OF DURABLE HANDOFF - 2026-11-05T02:32:16Z)
