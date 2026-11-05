# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-11-05T18:54:05Z

## SINGLE CANONICAL HANDOFF
Only this root `HANDOFF.md` is durable. Do **not** create/read any other handoff file.

## CURRENT VERIFIED STATUS — 2026-11-05T18:54:05Z (supersedes prior state)
- **Items 1–5 DONE/GREEN (do not reopen):** RSI(21)<20 primary trigger ON, ETH hedge on every leg (vol-ratio capped 3x), volume-based sizing ON (1.25% 24h vol), >=$5M volume filter on all trigger/universe paths, equal-share cap cuts across old+new via `RiskState.apply_cap_cuts()`, funding/liquidation checks correct.
- **Item 6a/6b DONE/GREEN (code + tests + fixture wiring):** `src/metrics/campaign_metrics.py` implements full suite (Sharpe, Sortino, max drawdown series **with timestamps** + max DD timestamp, Calmar, win rate, profit factor, monthly/weekly breakdowns, trade-level attribution by symbol/leg, exposure metrics), robust to empty/no-trade runs. `scripts/run_campaign.py` computes/exports `research_state/campaign_metrics.json` + `.csv` and embeds metrics in `campaign_results.json`. **Fixture smoke provenance remains explicit** (`fixture_smoke_test` / `real_market_data=false` / `performance_evidence=false` / target 283d `NOT_RUN`) — **NOT real Hyperliquid performance evidence**.
- **Data pipeline + provenance gates + hardening (2026-11-05):**
  - `scripts/fetch_hyperliquid_candles.py`: fetches/ingests hourly OHLCV (Hyperliquid public `candleSnapshot` API or verified `--source archive --input-archive`), chunks large windows, normalizes, writes per-symbol cache and `research_state/cache/hyperliquid/provenance.json` (source/URL/method, request params, counts, first/last timestamps, hashes, coverage %, gap report). **No silent static list as real data; never fabricates bars.** Hardened: robust symbol parsing accepts comma/semicolon/space-separated symbols.
  - `src/data/provenance.py` + `require_verified_provenance()`: enforces 283-day hourly coverage expectations, gap detection, and refuses real campaign if coverage/provenance incomplete; raises concrete `ProvenanceError`.
  - `scripts/run_real_campaign.py`: **hard-gated** real runner; refuses without complete verified manifest; outputs `research_state/campaign_results_real.json` + `_real_metrics.json/.csv` marked `real_market_data=true`, `performance_evidence=true`, `fabricated_data=false`, with `manifest_sha256`, source, target window, symbols loaded/complete, per-symbol coverage summary, and explicit `universe_filter_policy` (`min_daily_volume_usd` + applied-in paths). (Not run: blocked.)
  - `tests/test_real_data_provenance.py` + `tests/test_real_campaign_pipeline.py`: gating rejects incomplete manifest (exit 2); archive-ingest CSV/JSON normalization + missing-file errors; `analyze_coverage` gap-edge + exact-window completeness; equity-curve/DD-series fidelity; **gated integration passes only with complete verified manifest+caches** (tmp deterministic OHLCV exercising pipeline wiring; not repo evidence); symbol parsing normalization; provenance rejects incomplete symbol status.
  - Artifacts: `research_state/DATA_REQUEST_283D_HYPERLIQUID.md`, `research_state/candle_coverage_gap_report.json`, `research_state/cache/hyperliquid/provenance.json` (fresh probe manifest, incomplete).
- **Validation (2026-11-05T18:54:00Z):** `PYTHONPATH=. python -m pytest tests/ -q` → **109 passed, 0 failed** (baseline 106; +3 hardening/integration tests this session).
- **ITEM 6c REAL 283-DAY RUN — STILL BLOCKED BY VERIFIED DATA (concrete evidence, re-probed 2026-11-05T18:53:21Z):** Target `2025-12-20T00:00:00Z → 2026-09-28T23:00:00Z` (283 days, **6792 hourly bars/symbol**). Fresh public-API probe (`scripts/fetch_hyperliquid_candles.py --symbols BTC,ETH --start 2025-12-20T00:00:00Z --end 2026-09-28T23:00:00Z`) returned `BTC,ETH: incomplete 0/6792` / `Empty candles list` across chunked requests; manifest `research_state/cache/hyperliquid/provenance.json` records `all_complete=false`, `ready_for_real_campaign=false`. Prior session probe showed partial recent slice (4094/6792 starting 2026-04-11) — in all cases **full target window is not verifiably available via public API in this environment**. `scripts/run_real_campaign.py` correctly refuses (exit 2). **`target_historical_window 283d = NOT_RUN`. No data fabricated/substituted.** No verified archive found in workspace.

---

> **INITIAL TASK MESSAGE (TIMESTAMPED) FOR NEXT AGENTIC WORK SESSION:**
>
> `CRASH-REBOUND-STRATEGY | 2026-11-05T18:54:05Z | MISSION (REPO-NAME): CRASH-REBOUND FIDELITY TO crash-rebound-strategy.pdf | HEAVY WORK REQUIRED | ITEM 6c = UNBLOCK + EXECUTE REAL 283-DAY HYPERLIQUID CAMPAIGN (2025-12-20T00:00:00Z→2026-09-28T23:00:00Z, 6792 hourly bars/symbol, VERIFIED PROVENANCE, ZERO GAPS) | NO FIXTURES | NO FABRICATED DATA | IF DATA STILL BLOCKED: SCHEDULE RETRY + SHIP MATERIAL PIPELINE/UNIVERSE/COVERAGE HARDENING NOW (NO IDLE)`
>
> **EXECUTE IN ORDER (infer; do not ask):**
> 1. **UNBLOCK VERIFIED DATA (highest leverage):** Locate/provide a **verifiable, non-fabricated** hourly OHLCV archive for the full target window (`6792/6792` bars/symbol, zero gaps, documented source/checksums/extraction) for the spec-relevant universe (>= $5M 24h vol; document symbol selection). Ingest:
>    `PYTHONPATH=. python scripts/fetch_hyperliquid_candles.py --source archive --input-archive <ARCHIVE_PATH> --symbols <UNIVERSE_OR_PER_FILE> --start 2025-12-20T00:00:00Z --end 2026-09-28T23:00:00Z`
>    Gate: `research_state/cache/hyperliquid/provenance.json` → `summary.all_complete=true`, `ready_for_real_campaign=true`, coverage 6792/6792, gaps=0 per required symbol. Follow `research_state/DATA_REQUEST_283D_HYPERLIQUID.md`. Re-probe public API only if useful; if still incomplete, keep 6c blocked with concrete evidence.
> 2. **RUN REAL 283-DAY CAMPAIGN (only when gate passes):**
>    `PYTHONPATH=. python scripts/run_real_campaign.py --manifest research_state/cache/hyperliquid/provenance.json --min-symbols <N>`
>    Produce `research_state/campaign_results_real.json` + `campaign_results_real_metrics.json/.csv` with `real_market_data=true`, `performance_evidence=true`, `manifest_sha256`, provenance/coverage summary, symbols loaded, universe filter policy, trade count/PnL, **max drawdown series with timestamps** and full metrics (Sharpe/Sortino/Calmar/win rate/profit factor/monthly-weekly/attribution/exposure). Keep fixture artifacts separate.
> 3. **IF STILL DATA-BLOCKED (this env): DO NOT IDLE.** Record concrete evidence (manifest + probe output). In a goal context call `schedule_wakeup`/`cron_create` for retry. **Ship >=1 heavy deliverable now:** (a) wire `run_real_campaign.py` to accept `--universe-file` / verified symbol universe + document >=$5M volume-universe provenance expectations; (b) enforce/load only complete symbols while reporting partial-universe state (and gate `--min-symbols` appropriately); (c) add deterministic tests for manifest hash/export fields, partial-universe handling, and equity/DD parity on verified-like tmp data marked non-evidence; (d) add a clear ingest path for multi-coin verified archives if missing. **Never claim performance.**
> 4. **VALIDATE + HANDOFF:** `PYTHONPATH=. python -m pytest tests/ -q` must stay green (>=109). Update this root `HANDOFF.md` with timestamp, evidence, artifacts, and the next concrete heavy task. Only root `HANDOFF.md`.

**RULES (non-negotiable):** Items 1–5, 6a/6b done — no rework. Infer; don't ask. **Heavy-work guardrail:** every session ships >=1 of verified-data ingest/provenance completion, a real 283-day run with evidence, real metrics artifacts, or material gated-pipeline/tests/universe hardening. No fabrication, no fixture substitution for real market evidence, no idle waiting. PDF/spec is truth. Both legs non-negotiable. ETH hedge every leg. Funding/liquidation correct. >=$5M volume filter everywhere. Equal-share cuts across old+new. Edit tool requires `filePath`, `oldString`, `newString`.

## BOTTLENECK REMOVALS / GUARDRAILS (MANDATORY)
- **EDIT TOOL:** always pass `filePath`, `oldString`, `newString` explicitly.
- **NO STALE REWORK:** do not reopen items 1–5 or 6a/6b.
- **INFER, DON'T ASK.** Repo name ⇒ crash-rebound fidelity is the mission.
- **NO IDLE:** if blocked on data/CI, schedule wakeup and do independent heavy work.
- **HEAVY-WORK GUARDRAIL:** every session must ship >=1 heavy deliverable (see above). Shipping none = bottleneck.
- **SINGLE HANDOFF:** only root `HANDOFF.md`.
- **NO FABRICATION:** never mark `NOT_RUN` complete without verified provenance; never substitute fixtures/static lists as real market data.

## CRITICAL CONTEXT (SOURCE OF TRUTH)
- **Spec:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md` (PDF truth). Test window 2025-12-20→2026-09-28 (283d), **6792 hourly bars/symbol**.
- **Core:** `src/strategy/*`, `src/backtest/engine.py`, `src/data/{loader,provenance}.py`, `src/metrics/campaign_metrics.py`
- **Runners:** `scripts/run_campaign.py` (fixture smoke, explicit provenance), `scripts/fetch_hyperliquid_candles.py` (API/archive ingest + provenance), `scripts/run_real_campaign.py` (gated real)
- **Mechanics:** RSI(21)<20 primary (fallback drop via `use_rsi_trigger=False`), both legs (long crash + rebound short), ETH hedge every leg vol-ratio capped 3x, funding all legs, hourly worst-price liquidation+penalty, >=$5M vol filter all trigger paths, vol sizing ON 1.25% 24h vol, gross cap 120% equal-share cuts across ALL positions (old+new).

## SUCCESS CRITERIA (ITEM 6c)
- [ ] Verified 283-day hourly dataset ingested; provenance manifest complete (`6792/6792`, gaps=0, documented source, checksums) for required universe.
- [ ] `run_real_campaign.py` executes cleanly; `campaign_results_real.json` + real metrics JSON/CSV written with `real_market_data=true`/`manifest_sha256`/provenance+coverage summary and full metrics incl. max DD series w/ timestamps.
- [ ] Tests remain green (>=109).
- [ ] `HANDOFF.md` updated with timestamped results + next concrete heavy task (or concrete blocker evidence + scheduled retry + parallel heavy work done).
