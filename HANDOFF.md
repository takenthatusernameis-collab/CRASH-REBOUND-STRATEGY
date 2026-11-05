# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-11-05T19:56:43Z

## SINGLE CANONICAL HANDOFF
Only this root `HANDOFF.md` is durable. Do **not** create/read any other handoff file.

## CURRENT VERIFIED STATUS — 2026-11-05T19:56:43Z (supersedes prior state)
- **Items 1–5 DONE/GREEN (do not reopen):** RSI(21)<20 primary trigger ON, ETH hedge on every leg (vol-ratio capped 3x), volume-based sizing ON (1.25% 24h vol), >=$5M volume filter on all trigger/universe paths, equal-share cap cuts across old+new via `RiskState.apply_cap_cuts()`, funding/liquidation checks correct.
- **Item 6a/6b DONE/GREEN (code + tests + fixture wiring):** `src/metrics/campaign_metrics.py` full suite (Sharpe, Sortino, max drawdown series **with timestamps** + max DD timestamp, Calmar, win rate, profit factor, monthly/weekly, trade attribution, exposure), robust to empty/no-trade runs. `scripts/run_campaign.py` exports fixture-smoke `campaign_metrics.json/.csv` and embeds metrics in `campaign_results.json` with explicit provenance (`fixture_smoke_test` / `real_market_data=false` / `performance_evidence=false`) — **NOT real Hyperliquid performance evidence**.
- **Data/provenance pipeline + hard gates (GREEN):** `scripts/fetch_hyperliquid_candles.py` fetches/ingests hourly OHLCV (Hyperliquid public `candleSnapshot` API or verified `--source archive --input-archive`), chunks, normalizes, writes per-symbol cache + `research_state/cache/hyperliquid/provenance.json` (source/URL/method, request params, counts, first/last timestamps, hashes, coverage %, gap report). **Never fabricates bars.** Supports `--universe-file`; hardened archive ingest (dir/file auto-discovery; JSON symbol map; CSV with `symbol` column) with provenance metadata. `src/data/provenance.py` + `require_verified_provenance()` enforce 283-day hourly coverage/gap checks and refuse real runs. `scripts/run_real_campaign.py` is **hard-gated** (refuses without complete verified manifest); accepts `--universe-file` + `--min-symbols`; outputs real-marked artifacts with `manifest_sha256`, source/window, symbols loaded/complete, coverage summary, universe-filter policy. `scripts/derive_verified_universe.py` derives verifiable `universe_verified.json` from local verified caches only (max rolling 24h close*volume USD proxy, default >=$5M), `performance_evidence=false`. (No real run executed: blocked.)
- **2026-11-05T19:56:43Z HEAVY DELIVERABLE SHIPPED (item 6c still data-blocked): Funding sign/side correctness hardening** in `src/backtest/engine.py`.
  - Clarified/fixed `_apply_funding_pnl` convention (returns signed component: +cost, -benefit) and applied consistently as `pnl -= funding` across all legs/paths.
  - Fixed rebound-hedge (long) funding which previously used `+=` with a cost-positive return (inverted economics) and fixed the last-bar rebound-hedge branch that subtracted + used missing `side`.
  - Fixed missing `side=` on remaining hedge funding calls (ensures correct long/short economics). All funding call sites now pass `side`.
  - Spec/behavior intent preserved: positive funding rate => longs pay / shorts receive; hourly funding across legs; stopped buy never opens rebound short (target branch only). **No fixture substitution; no performance claims.**
  - **Validation:** `tests/test_crash_rebound_strategy.py tests/test_real_campaign_pipeline.py tests/test_archive_universe_hardening.py` → **61 passed**. Full suite `PYTHONPATH=. python -m pytest tests/ -q` → **114 passed, 0 failed**.

## ITEM 6c — REAL 283-DAY HYPERLIQUID CAMPAIGN (BLOCKED BY VERIFIED DATA)
- **Target:** `2025-12-20T00:00:00Z → 2026-09-28T23:00:00Z` (283 days, **6792 hourly bars/symbol**), spec-relevant universe (>= $5M 24h vol, documented/verified).
- **Fresh public-API probes 2026-11-05T19:56Z (this session):**
  - BTC: `4094/6792` (60.276796%), observed `2026-04-11T10:00:00Z → 2026-09-28T23:00:00Z`, `gap_count=0` in returned slice, `first_timestamp != target start` ⇒ `complete_for_target_window=false`.
  - BTC,ETH probe: manifest `research_state/cache/hyperliquid/provenance.json` (`generated_at_utc=2026-11-05T19:56:30.899097+00:00`) → BTC/ETH both `4094/6792`, `summary.all_complete=false`, `ready_for_real_campaign=false`, `symbols_complete=0`.
  - **Full target window not verifiably available via public API in this environment.** No parquet/verified archive found in workspace/system search.
- **Gating confirmed:** `PYTHONPATH=. python scripts/run_real_campaign.py --manifest research_state/cache/hyperliquid/provenance.json --min-symbols 1` exits 2: “Real campaign blocked by provenance/coverage validation…” (BTC/ETH incomplete, 0/2 complete). **`target_historical_window 283d = NOT_RUN`. No data fabricated/substituted.**
- **Scheduled retry:** `schedule_wakeup` **`wku_1ad413206001IwXmTnORrybZWm`** due **2026-11-06T01:48:13.442Z** to re-probe public API and proceed only if verified-complete; otherwise record evidence + ship material hardening.

---

> **INITIAL TASK MESSAGE (TIMESTAMPED, SINGLE, NEXT AGENTIC SESSION) — EXECUTE HEAVY WORK:**
>
> `CRASH-REBOUND-STRATEGY | 2026-11-05T19:56:43Z | MISSION (repo name): crash-rebound fidelity to crash-rebound-strategy.pdf | ITEM 6c UNBLOCK+EXECUTE REAL 283-DAY HYPERLIQUID CAMPAIGN (2025-12-20T00:00:00Z→2026-09-28T23:00:00Z, 6792 hourly bars/symbol, VERIFIED PROVENANCE, ZERO GAPS, spec-relevant >=$5M 24h-vol universe) | NO FIXTURES | NO FABRICATED DATA | DATA STILL BLOCKED (public API BTC/ETH 4094/6792 @ 2026-11-05T19:56Z, runner refuses) | RETRY WAKEUP wku_1ad413206001IwXmTnORrybZWm @ 2026-11-06T01:48:13Z | Funding sign/side hardened + 114 tests green`
>
> **DO THIS IN ORDER (infer; do not ask). Every session MUST ship >=1 heavy deliverable.**
> 1. **OBTAIN/INGEST VERIFIED 283-DAY DATA (highest leverage):** Secure a **verifiable, non-fabricated** hourly OHLCV archive covering the full target window (`6792/6792` bars/symbol, zero gaps, documented source/extraction/checksums) for the spec-relevant universe. Ingest:
>    - Dir of per-symbol files or multi-symbol container (JSON symbol map / CSV with `symbol` col):
>      `PYTHONPATH=. python scripts/fetch_hyperliquid_candles.py --source archive --input-archive <ARCHIVE> [--universe-file <U.json>|--symbols <...>] --start 2025-12-20T00:00:00Z --end 2026-09-28T23:00:00Z`
>    - Gate: `research_state/cache/hyperliquid/provenance.json` → `summary.all_complete=true`, `ready_for_real_campaign=true`, `6792/6792`, `gap_count=0` per required symbol. Follow `research_state/DATA_REQUEST_283D_HYPERLIQUID.md`.
> 2. **DERIVE/VERIFY UNIVERSE (>= $5M 24h vol, spec):** From verified local caches+manifest:
>    `PYTHONPATH=. python scripts/derive_verified_universe.py --manifest research_state/cache/hyperliquid/provenance.json --cache-dir research_state/cache/hyperliquid --min-24h-volume-usd 5000000 --output research_state/universe_verified.json [--require-complete-manifest]`
>    Review selected symbols/report; document method (rolling 24h close*volume proxy) and exchange-snapshot limits.
> 3. **RUN REAL 283-DAY CAMPAIGN (only when gate passes):**
>    `PYTHONPATH=. python scripts/run_real_campaign.py --manifest research_state/cache/hyperliquid/provenance.json [--universe-file research_state/universe_verified.json] --min-symbols <N>`
>    Produce `research_state/campaign_results_real.json` + `campaign_results_real_metrics.json/.csv` with `real_market_data=true`, `performance_evidence=true`, `manifest_sha256`, provenance/coverage, symbols loaded, universe filter policy, trade count/PnL, **max drawdown series with timestamps**, Sharpe/Sortino/Calmar/win rate/profit factor/monthly-weekly/attribution/exposure. Keep fixture artifacts separate.
> 4. **IF STILL DATA-BLOCKED (no verified archive): DO NOT IDLE.** Re-probe public API; append concrete evidence to this HANDOFF and update gap/provenance artifacts. `schedule_wakeup`/`cron_create` next retry. **Ship >=1 heavy deliverable now** (pick unfinished/highest-value): (a) add/validate parquet ingestion if `pyarrow` appears OR robust NDJSON/large-file streaming ingest with bounded memory + provenance; (b) explicit **partial-universe “NOT_EVIDENCE_PARTIAL_UNIVERSE”** real-run mode that writes clearly marked non-evidence artifacts and **never** sets `performance_evidence=true` unless full gate+policy satisfied; (c) deterministic end-to-end test: archive dir auto-discovery → manifest → universe derivation → gated real-run on verified-like tmp data (all non-evidence); (d) spec-audit of crash/rebound mechanics vs `crash-rebound-strategy.pdf` with failing tests first if any fidelity gap found (do not regress items 1–5/6a-6b). **Never claim performance.**
> 5. **VALIDATE + HANDOFF:** `PYTHONPATH=. python -m pytest tests/ -q` must stay green (>=114). Update **only** root `HANDOFF.md` with timestamp, evidence, artifacts, and next concrete heavy task.

**RULES (non-negotiable):** Items 1–5, 6a/6b done — no rework. Infer; don't ask. **Heavy-work guardrail:** every session ships >=1 of verified-data ingest/provenance completion, a real 283-day run with evidence, real metrics artifacts, or material gated-pipeline/tests/universe/spec hardening. No fabrication, no fixture substitution for real market evidence, no idle waiting. PDF/spec is truth. Both legs non-negotiable. ETH hedge every leg. Funding/liquidation correct. >=$5M volume filter everywhere. Equal-share cuts across old+new. Edit tool requires `filePath`, `oldString`, `newString`.

## CRITICAL CONTEXT (SOURCE OF TRUTH)
- **Spec:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Test window 2025-12-20→2026-09-28 (283d), **6792 hourly bars/symbol**.
- **Core:** `src/strategy/*`, `src/backtest/engine.py`, `src/data/{loader,provenance}.py`, `src/metrics/campaign_metrics.py`
- **Runners/tools:** `scripts/run_campaign.py` (fixture smoke), `scripts/fetch_hyperliquid_candles.py` (API/archive ingest + provenance + archive auto-discovery + multi-symbol containers), `scripts/derive_verified_universe.py` (local verified-cache 24h-vol universe derivation), `scripts/run_real_campaign.py` (gated real, `--universe-file`, `--min-symbols`)
- **Mechanics:** RSI(21)<20 primary (fallback drop via `use_rsi_trigger=False`), both legs (long crash + rebound short), ETH hedge every leg vol-ratio capped 3x, funding all legs (positive rate: longs pay, shorts receive), hourly worst-price liquidation+penalty, >=$5M vol filter all trigger paths, vol sizing ON 1.25% 24h vol, gross cap 120% equal-share cuts across ALL positions (old+new). Stopped buy never opens rebound short.

## SUCCESS CRITERIA (ITEM 6c)
- [ ] Verified 283-day hourly dataset ingested; provenance manifest complete (`6792/6792`, gaps=0, documented source, checksums) for required universe.
- [ ] `universe_verified.json` (or equivalent verified universe evidence) derived/reconciled with >=$5M 24h vol policy and documented.
- [ ] `run_real_campaign.py` executes cleanly; `campaign_results_real.json` + real metrics JSON/CSV written with `real_market_data=true`/`manifest_sha256`/provenance+coverage summary and full metrics incl. max DD series w/ timestamps.
- [ ] Tests remain green (>=114).
- [ ] `HANDOFF.md` updated with timestamped results + next concrete heavy task (or concrete blocker evidence + scheduled retry + parallel heavy work done).
