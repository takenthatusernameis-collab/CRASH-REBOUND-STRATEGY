# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-11-05T17:48:56Z

## CURRENT VERIFIED STATUS — 2026-11-05T17:48:56Z (supersedes all prior state)

- Items 1–5 remain **done/green** (RSI primary trigger ON, ETH hedge on every leg, volume-based sizing ON 1.25% 24h vol, >=$5M volume filter on trigger/universe paths, equal-share cap cuts across old+new, funding/liquidation checks). **Do not reopen.**
- **ITEM 6a/6b COMPLETE (2026-11-05T17:47Z):** `src/metrics/campaign_metrics.py` implemented with the full API expected by `src/metrics/__init__.py`: `compute_campaign_metrics(...)`, `compute_metrics_from_trades(...)`, `metrics_to_dict(...)`, `metrics_to_csv_rows(...)`.
  - Computes: Sharpe, Sortino, max drawdown **series with timestamps** + max DD timestamp, Calmar, win rate, profit factor, monthly/weekly breakdowns, trade-level attribution by symbol/leg, exposure metrics.
  - **Robust to empty/no-trade runs** (returns well-formed zeros/empty structures; no crash). Verified by smoke + fixture E2E.
- **Wired + exported (fixture smoke only):** `scripts/run_campaign.py` computes/attaches metrics and writes `research_state/campaign_metrics.json` + `research_state/campaign_metrics.csv` (and `campaign_results.json` with embedded metrics). All artifacts remain explicitly `fixture_smoke_test`/synthetic provenance — **NOT real Hyperliquid performance evidence**. E2E run completed cleanly at 2026-11-05T17:47:14Z.
- **Validation:** `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python -m pytest tests/ -v` → **89 passed, 0 failed** (re-verified 2026-11-05T17:47Z). Metrics import OK.
- **ITEM 6c REAL 283-DAY RUN — BLOCKED BY DATA (concrete evidence, 2026-11-05T17:47Z):** Target window 2025-12-20 → 2026-09-28 (283 days), Hyperliquid hourly candles. Blockers found in workspace:
  - No verified real-market OHLCV dataset/cache present (searched `*hyperliquid*`; none; `research_state/` has no candle cache). `src/data/loader.py` provides loaders/validation but no fetched/verified 283-day dataset.
  - `scripts/run_campaign.py` is intentionally fixture-only and must not silently substitute toy fixtures/static candidate lists; real run requires independently verified, complete hourly cache with coverage + provenance checks.
  - No network/data-fetch path or credentials/provenance manifest for Hyperliquid historical candles in repo; fabricating/substituting data is prohibited.
  - **Status:** `target_historical_window 2025-12-20→2026-09-28 (283d) = NOT_RUN`. Do not claim performance.

---

> **INITIAL TASK MESSAGE (TIMESTAMPED) FOR NEXT AGENTIC WORK SESSION:**
>
> `CRASH-REBOUND-STRATEGY | 2026-11-05T17:48:56Z | PRIORITY 1 (REPO-NAME DRIVEN): CRASH-REBOUND FIDELITY TO crash-rebound-strategy.pdf | ITEM 6c - REAL 283-DAY HYPERLIQUID RUN (DATA-GATED) → BUILD VERIFIED DATA PIPELINE/PROVENANCE + COVERAGE CHECKS, THEN EXECUTE | TARGET WINDOW 2025-12-20 → 2026-09-28 (283 DAYS) | NO FIXTURE COASTING | NO FABRICATED DATA | HEAVY WORK MANDATORY | ELIMINATE BOTTLENECKS IMMEDIATELY`
>
> **CONCRETE FIRST ACTION (EXECUTE NOW, NO ENV RE-CHECK, NO Q&A):**
> 1. **Create a verifiable Hyperliquid hourly-candle acquisition + provenance path** for the 283-day window (2025-12-20 → 2026-09-28). Add `scripts/fetch_hyperliquid_candles.py` (or equivalent) that:
>    - Fetches/ingests hourly OHLCV per symbol from a documented, verifiable source (Hyperliquid public candle API or a user-supplied verified archive path). Support `--source`, `--cache-dir`, `--start`, `--end`, `--symbols`/universe, `--dry-run`.
>    - Writes `research_state/cache/hyperliquid/{SYMBOL}.json` (or csv) and a machine-readable **provenance manifest** `research_state/cache/hyperliquid/provenance.json` (source URL/method, fetch time, request params, symbol list, per-symbol row counts, first/last timestamps, hash/checksum, coverage %, gap report). **No silent static list as "real data".**
> 2. **Add coverage/provenance validation** (loader/script): enforce 283-day hourly coverage expectations, gap detection, non-finite/look-ahead checks, and refuse to run the real campaign if coverage/provenance is incomplete; emit a concrete gap report under `research_state/`.
> 3. **Run the real campaign** once verified data exists: produce `research_state/campaign_results_real.json` + real `campaign_metrics.json/.csv` **marked `real_market_data=true` with provenance reference** (keep fixture artifacts clearly separate). Include trade count, PnL, drawdown series w/ timestamps, and coverage summary.
> 4. **If data/CI/network blocks fetching in this environment:** document the exact blocker with evidence, generate a deterministic "data request + verification checklist" artifact, and **schedule `schedule_wakeup`/`cron_create`** (goal context) to retry; meanwhile do independent heavy work: add tests for provenance/coverage validation, harden metrics edge cases, or add a real-run CLI path guarded by provenance checks. **Do not idle. Never fabricate data.**
> 5. **Validate & handoff:** Keep `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python -m pytest tests/ -v` >=89 green. Update this `HANDOFF.md` with timestamped results + next concrete heavy task.
>
> **RULES:** Items 1–5 and 6a/6b done. Both legs non-negotiable. Equal-share cap cuts across old+new. Funding/liquidation correct. >=$5M volume filter on all trigger paths. PDF/spec is truth. Heavy work only. No coasting on fixtures.

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

(END OF DURABLE HANDOFF - 2026-11-05T17:44:57Z)
