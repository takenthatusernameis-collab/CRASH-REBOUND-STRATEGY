# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-11-05T18:48:49Z

## SINGLE CANONICAL HANDOFF
Only this root `HANDOFF.md` is durable. Do **not** create/read any other handoff file.

## CURRENT VERIFIED STATUS — 2026-11-05T18:48:49Z (supersedes prior state)
- **Items 1–5 DONE/GREEN (do not reopen):** RSI(21)<20 primary trigger ON, ETH hedge on every leg (vol-ratio capped 3x), volume-based sizing ON (1.25% 24h vol), >=$5M volume filter on all trigger/universe paths, equal-share cap cuts across old+new via `RiskState.apply_cap_cuts()`, funding/liquidation checks correct.
- **Item 6a/6b DONE/GREEN (code + tests + fixture wiring):** `src/metrics/campaign_metrics.py` implements full suite (Sharpe, Sortino, max drawdown series **with timestamps** + max DD timestamp, Calmar, win rate, profit factor, monthly/weekly breakdowns, trade-level attribution by symbol/leg, exposure metrics), robust to empty/no-trade runs. `scripts/run_campaign.py` computes/exports `research_state/campaign_metrics.json` + `.csv` and embeds metrics in `campaign_results.json`. **Fixture smoke provenance remains explicit** (`fixture_smoke_test` / `real_market_data=false` / `performance_evidence=false` / target 283d `NOT_RUN`) — **NOT real Hyperliquid performance evidence**.
- **Data pipeline + provenance gates ADDED (2026-11-05):**
  - `scripts/fetch_hyperliquid_candles.py`: fetches/ingests hourly OHLCV (Hyperliquid public `candleSnapshot` API or verified `--source archive --input-archive`), chunks large windows, normalizes, writes per-symbol cache (`research_state/cache/hyperliquid/candles/<SYM>.json`) and machine-readable provenance manifest `research_state/cache/hyperliquid/provenance.json` (source/URL/method, request params, per-symbol row counts, first/last timestamps, hashes, coverage %, gap report). **No silent static list as real data; never fabricates bars.**
  - `src/data/provenance.py` + `require_verified_provenance()`: enforces 283-day hourly coverage expectations, gap detection, and refuses real campaign if coverage/provenance incomplete; raises concrete `ProvenanceError`.
  - `scripts/run_real_campaign.py`: **hard-gated** real runner; refuses without complete verified manifest; outputs `research_state/campaign_results_real.json` + `_real_metrics.json/.csv` marked `real_market_data=true`, `performance_evidence=true`, `fabricated_data=false`, with provenance ref/coverage summary. (Not run: blocked.)
  - `tests/test_real_data_provenance.py` added (manifest missing/fabricated/incomplete/gap/complete acceptance + expected bars). Coverage/gap logic smoke-verified.
  - **`tests/test_real_campaign_pipeline.py` ADDED (this session):** run_real_campaign gating rejects incomplete manifest (exit 2), accepts complete verified manifest; archive-ingest CSV/JSON normalization + missing-file errors; `analyze_coverage` gap-edge detection + exact-window completeness; equity-curve/DD-series fidelity (deterministic max-drawdown series with timestamps, calmar, win rate, profit factor); no-trade equity-curve drawdown.
  - Artifacts: `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` (checklist), `research_state/candle_coverage_gap_report.json`, `research_state/cache/hyperliquid/provenance.json` (incomplete probe). Large incomplete API candle payloads intentionally removed.
- **Validation:** `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python -m pytest tests/ -q` → **106 passed, 0 failed** (2026-11-05T18:48:49Z). Baseline was 95; +11 pipeline/hardening tests.
- **ITEM 6c REAL 283-DAY RUN — STILL BLOCKED BY VERIFIED DATA (concrete evidence):** Target `2025-12-20T00:00:00Z → 2026-09-28T23:00:00Z` (283 days, **6792 hourly bars/symbol**). Hyperliquid public `info` `candleSnapshot` (BTC/ETH) returned only `2026-04-11T10:00:00Z→2026-09-28T23:00:00Z` = **4094/6792** bars (no gaps in returned slice; missing early window 2025-12-20→2026-04-11). `scripts/run_real_campaign.py` correctly refuses (exit 2) citing incomplete provenance. **`target_historical_window 283d = NOT_RUN`. No data fabricated/substituted.**
- **Retry scheduled:** `schedule_wakeup` wku_1ad0d11c0001U0vd179KSn1Qve due 2026-11-05T22:51:17Z (4h) to re-attempt public-API fetch; if still incomplete, keep 6c blocked and continue heavy independent engineering.

---

> **INITIAL TASK MESSAGE (TIMESTAMPED) FOR NEXT AGENTIC WORK SESSION:**
>
> `CRASH-REBOUND-STRATEGY | 2026-11-05T18:48:49Z | PRIORITY 1 (REPO-NAME): CRASH-REBOUND FIDELITY TO crash-rebound-strategy.pdf | ITEM 6c UNBLOCK + EXECUTE REAL 283-DAY HYPERLIQUID RUN (2025-12-20→2026-09-28, 6792 hourly bars/symbol) WITH VERIFIED PROVENANCE/COVERAGE | NO FIXTURES | NO FABRICATED DATA | HEAVY WORK MANDATORY — ELIMINATE BOTTLENECKS`
>
> **EXECUTE NOW (no re-verifying env, no Q&A):**
> 1. **Unblock verified data (primary path):** Obtain a **verifiable, non-fabricated** hourly OHLCV archive for the full target window (`6792/6792` bars/symbol, zero gaps, documented source/checksums) for the spec-relevant universe (>= $5M 24h vol; symbol selection documented). Ingest via:
>    `PYTHONPATH=. python scripts/fetch_hyperliquid_candles.py --source archive --input-archive <ARCHIVE_PATH> --symbols <UNIVERSE> --start 2025-12-20T00:00:00Z --end 2026-09-28T23:00:00Z`
>    Require `research_state/cache/hyperliquid/provenance.json` → `summary.all_complete=true`, `ready_for_real_campaign=true`. Follow `research_state/DATA_REQUEST_283D_HYPERLIQUID.md`. Re-attempt public API per scheduled wakeup (due ~2026-11-05T22:51:17Z) — if still 4094/6792, data remains blocked in this env.
> 2. **Execute real campaign (gated):** `PYTHONPATH=. python scripts/run_real_campaign.py --manifest research_state/cache/hyperliquid/provenance.json` → produce `research_state/campaign_results_real.json` + `campaign_results_real_metrics.json/.csv` with `real_market_data=true`, `performance_evidence=true`, provenance ref, coverage summary, trade count/PnL, and **max drawdown series with timestamps** (+ full metrics). Keep fixture artifacts separate.
> 3. **If still data-blocked in this environment:** record concrete evidence; **schedule `schedule_wakeup`/`cron_create`** (goal context) for retry; **do heavy independent work now (do NOT idle):** (a) harden real-run to accept a verified universe list + per-symbol `min_daily_volume_usd` coverage provenance checks; (b) add tests for `run_real_campaign` gating / archive-ingest normalization / gap-edge cases; (c) add equity-curve/DD-series fidelity tests using deterministic verified-like fixtures marked `real_market_data_intended=false` in tests only; (d) improve `scripts/fetch_hyperliquid_candles.py` alternative documented sources **only if verifiable** (no fabrication). Never claim performance.
> 4. **Validate & handoff:** keep tests >=106 green: `PYTHONPATH=. python -m pytest tests/ -q`. Update this `HANDOFF.md` (timestamped, evidence, next concrete heavy task). Only root `HANDOFF.md`.

**RULES:** Items 1–5, 6a/6b done. 6c blocked by verified data — unblock or do parallel heavy engineering; **never fabricate data, never coast on fixtures**. PDF/spec is truth. Both legs non-negotiable. Equal-share cuts across old+new. Funding/liquidation correct. >=$5M volume filter everywhere. Ship >=1 heavy deliverable per session (verified-data ingest/provenance, real 283-day run + evidence, real metrics artifacts, or material gated-pipeline/tests/coverage hardening).

## BOTTLENECK REMOVALS / GUARDRAILS (MANDATORY)
- **EDIT TOOL:** always pass `filePath`, `oldString`, `newString` explicitly.
- **NO STALE REWORK:** do not reopen items 1–5 or 6a/6b.
- **INFER, DON'T ASK.** Repo name ⇒ crash-rebound fidelity is the mission.
- **NO IDLE:** if blocked on data/CI, schedule wakeup and do independent heavy work.
- **HEAVY-WORK GUARDRAIL:** every session must ship >=1 of: verified-data ingest/provenance completion, a real 283-day run with evidence, real metrics artifacts, or material gated-pipeline/tests/coverage hardening. Shipping none = bottleneck.
- **SINGLE HANDOFF:** only root `HANDOFF.md`.
- **NO FABRICATION:** never mark `NOT_RUN` complete without verified provenance; never substitute fixtures/static lists as real market data.

## CRITICAL CONTEXT (SOURCE OF TRUTH)
- **Spec:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md` (PDF truth). Test window 2025-12-20→2026-09-28 (283d).
- **Core:** `src/strategy/*`, `src/backtest/engine.py`, `src/data/{loader,provenance}.py`, `src/metrics/campaign_metrics.py`
- **Runners:** `scripts/run_campaign.py` (fixture smoke, explicit provenance), `scripts/fetch_hyperliquid_candles.py`, `scripts/run_real_campaign.py` (gated real)
- **Mechanics:** RSI(21)<20 primary (fallback drop via `use_rsi_trigger=False`), both legs (long crash + rebound short), ETH hedge every leg vol-ratio capped 3x, funding all legs, hourly worst-price liquidation+penalty, >=$5M vol filter all trigger paths, vol sizing ON 1.25% 24h vol, gross cap 120% equal-share cuts across ALL positions (old+new).

## SUCCESS CRITERIA (ITEM 6c)
- [ ] Verified 283-day hourly dataset ingested; provenance manifest complete (`6792/6792`, gaps=0, documented source, checksums).
- [ ] `run_real_campaign.py` executes cleanly; `campaign_results_real.json` + real metrics JSON/CSV written with `real_market_data=true`/provenance ref/coverage summary and full metrics incl. max DD series w/ timestamps.
- [ ] Tests remain green (>=106).
- [ ] `HANDOFF.md` updated with timestamped results + next concrete heavy task (or concrete blocker evidence + scheduled retry + parallel heavy work done).
