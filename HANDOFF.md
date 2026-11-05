# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-11-05T20:42:46Z

## SINGLE CANONICAL HANDOFF
Only this root `HANDOFF.md` is durable. Do **not** create/read any other handoff file.

## CURRENT VERIFIED STATUS — 2026-11-05T20:42:00Z (supersedes prior state)
- **Items 1–5 DONE/GREEN (do not reopen):** RSI(21)<20 primary trigger ON (`use_rsi_trigger=True` in `src/strategy/config.py:19`), ETH hedge on every leg (vol-ratio capped 3x, `compute_eth_hedge_size` in `src/strategy/crash_rebound.py:31`), volume-based sizing ON (1.25% 24h vol, `enable_volume_based_sizing=True` in config.py:55), >=$5M volume filter on all trigger/universe paths (`min_daily_volume_usd=5_000_000`), equal-share cap cuts across old+new via `RiskState.apply_cap_cuts()` (`src/strategy/risk.py:102`), funding/liquidation checks correct (`src/backtest/engine.py:62`,`_check_liquidation`).
- **Item 6a/6b DONE/GREEN:** `src/metrics/campaign_metrics.py` full suite. `scripts/run_campaign.py` exports fixture-smoke artifacts with explicit provenance (`fixture_smoke_test` / `real_market_data=false` / `performance_evidence=false`).
- **Data/provenance pipeline + hard gates (GREEN):** `scripts/fetch_hyperliquid_candles.py` fetches/ingests hourly OHLCV (Hyperliquid public `candleSnapshot` API or `--source archive --input-archive`), chunks, normalizes, writes per-symbol cache + provenance.json. Never fabricates bars. `src/data/provenance.py` + `require_verified_provenance()` enforce 283-day coverage/gap checks and refuse real runs. `scripts/run_real_campaign.py` hard-gated. `scripts/derive_verified_universe.py` derives verifiable `universe_verified.json` from local verified caches only.
- **Prior heavy deliverable (kept green):** Funding sign/side correctness hardening in `src/backtest/engine.py` (2026-11-05T19:56Z session). Full suite green.
- **2026-11-05T20:05:00Z HEAVY DELIVERABLE SHIPPED:** Explicit PARTIAL-NOT-EVIDENCE gated mode for `run_real_campaign.py` + regression tests. `--allow-partial-not-evidence` runs only on verified COMPLETE SUBSET; never sets `performance_evidence=true`.
- **Full suite `PYTHONPATH=. python -m pytest tests/ -q` → 116 passed, 0 failed.**

## ITEM 6c — REAL 283-DAY HYPERLIQUID CAMPAIGN (BLOCKED BY VERIFIED DATA)
- **Target:** `2025-12-20T00:00:00Z → 2026-09-28T23:00:00Z` (283 days, **6792 hourly bars/symbol**), spec-relevant universe (>= $5M 24h vol, documented/verified).
- **Blocker evidence:** Public `candleSnapshot` (BTC/ETH, `1h`, full target range) returned **4094/6792** bars, `first=2026-04-11T10:00:00Z`, `last=2026-09-28T23:00:00Z`. Early window `2025-12-20→2026-04-11` missing. `all_complete=false`, `ready_for_real_campaign=false`. Default gate refuses. **No parquet/verified archive found in accessible filesystem scan.**
- **Manifest:** `research_state/cache/hyperliquid/provenance.json` shows BTC/ETH `status=incomplete`, `coverage.complete_for_target_window=false`, `summary.all_complete=false`.
- **Non-evidence debug path** (`--allow-partial-not-evidence`) exists but does **not** satisfy 6c success criteria; never report as campaign performance.
- **Scheduled retry:** wakeup `wku_23bf07632001TU4QRRom82oP9K` due **2026-11-06T02:05:05Z** (re-probe Hyperliquid public API for full 283-day coverage).

## BOTTLENECK REMOVAL — PARALLEL HEAVY WORK (no idle waiting)
ITEM 6c is data-blocked; the data bottleneck must **not** idle the session. Every session ships >=1 heavy deliverable. When data is unavailable, execute the non-data-dependent heavy-work track below in parallel with the data retry.

**Data track (highest leverage, retried on wakeup):**
1. Re-probe Hyperliquid public API for full 283-day coverage; if verified-complete, ingest via `fetch_hyperliquid_candles.py --source archive --input-archive <ARCHIVE> --start 2025-12-20T00:00:00Z --end 2026-09-28T23:00:00Z`, gate requires `6792/6792`, `gap_count=0`, `all_complete=true`, `ready_for_real_campaign=true`.
2. Derive/verify universe: `derive_verified_universe.py --manifest ... --cache-dir ... --min-24h-volume-usd 5000000 --output research_state/universe_verified.json`.
3. Run real campaign: `run_real_campaign.py --manifest ... [--universe-file ...] --min-symbols <N>` → `campaign_results_real.json` + real metrics with `performance_evidence=true`.

**Non-data parallel heavy-work track (execute NOW, regardless of data retry):**
1. **Spec-fidelity audit vs `crash-rebound-strategy.pdf`** (`research_state/strategy_spec.md`): diff implementation against PDF mechanics (RSI trigger, volume sizing, ETH hedge every leg, 120% cap/equal-share cuts, funding/liquidation hourly, stop rules, rebound short, time exits). Write failing tests first for any fidelity gap; do not regress items 1–5/6a–6b.
2. **Deterministic full e2e test** (archive dir/CSV+symbol col/JSON map → fetch manifest → derive universe → default gate refuses incomplete / partial-not-evidence marks correctly / complete verified-like tmp data can produce evidence-marked real run in tmp repo) — all non-evidence, in repo.
3. **Universe derivation hardening:** align with spec's 24h-volume semantics, document exchange snapshot limits, add verified-cache e2e tests.
4. **Parquet/NDJSON/streaming ingest** if libs appear, or robust bounded-memory large-file ingest + provenance.

## INITIAL TASK MESSAGE (TIMESTAMPED, SINGLE, NEXT AGENTIC SESSION) — EXECUTE HEAVY WORK

`CRASH-REBOUND-STRATEGY | 2026-11-05T20:42:46Z | MISSION (repo name): crash-rebound strategy fidelity to crash-rebound-strategy.pdf | ITEM 6c UNBLOCK+EXECUTE REAL 283-DAY HYPERLIQUID CAMPAIGN (2025-12-20T00:00:00Z→2026-09-28T23:00:00Z, 6792 hourly bars/symbol, VERIFIED PROVENANCE, ZERO GAPS, spec-relevant >=$5M 24h-vol universe) | DATA BLOCKED (public API re-probed 2026-11-05T20:03Z: BTC/ETH candleSnapshot 4094/6792 bars, first=2026-04-11T10:00:00Z last=2026-09-28T23:00:00Z, gap_count=0 within slice, incomplete for target window; all_complete=false, ready_for_real_campaign=false, default gate refuses) | RETRY WAKEUP `wku_23bf07632001TU4QRRom82oP9K` due 2026-11-06T02:05:05Z | 116 tests green | PARTIAL-NOT-EVIDENCE MODE EXISTS BUT IS NOT SPEC EVIDENCE | BOTTLENECK REMOVED: no idle-waiting — ship heavy work every session regardless of API retry`

**DO THIS IN ORDER (infer; do not ask). Every session MUST ship >=1 heavy deliverable.**
1. **OBTAIN/INGEST VERIFIED 283-DAY DATA (highest leverage):** Secure a verifiable, non-fabricated hourly OHLCV archive covering the full target window (`6792/6792` bars/symbol, zero gaps, documented source/extraction/checksums) for the spec-relevant universe. Ingest via `fetch_hyperliquid_candles.py --source archive --input-archive <ARCHIVE> --symbols <...> --start 2025-12-20T00:00:00Z --end 2026-09-28T23:00:00Z`. Gate: `provenance.json` → `summary.all_complete=true`, `ready_for_real_campaign=true`, `6792/6792`, `gap_count=0`. Follow `research_state/DATA_REQUEST_283D_HYPERLIQUID.md`.
2. **DERIVE/VERIFY UNIVERSE (>= $5M 24h vol, spec):** `derive_verified_universe.py --manifest ... --cache-dir ... --min-24h-volume-usd 5000000 --output research_state/universe_verified.json`. Review symbols/report; document method (rolling 24h close*volume proxy) and exchange-snapshot limits.
3. **RUN REAL 283-DAY CAMPAIGN (only when gate passes):** `run_real_campaign.py --manifest ... [--universe-file ...] --min-symbols <N>`. Produce `campaign_results_real.json` + `campaign_results_real_metrics.json/.csv` with `real_market_data=true`, `performance_evidence=true`, `manifest_sha256`, provenance/coverage, symbols loaded, universe filter policy, trade count/PnL, **max drawdown series with timestamps**, Sharpe/Sortino/Calmar/win rate/profit factor/monthly-weekly/attribution/exposure. Keep fixture artifacts separate. **Never use `--allow-partial-not-evidence` to satisfy 6c.**
4. **IF STILL DATA-BLOCKED (no verified archive): DO NOT IDLE.** Re-probe public API; append concrete evidence to this HANDOFF; update gap/provenance artifacts; schedule next retry. **Ship >=1 heavy deliverable now** from the non-data parallel track: (a) spec-fidelity audit vs `crash-rebound-strategy.pdf` with failing tests first for any gap; (b) deterministic full e2e test (archive → manifest → universe → gate refuses incomplete / partial marks correctly / complete tmp data produces evidence-marked run); (c) universe derivation hardening + verified-cache e2e tests; (d) parquet/NDJSON/streaming or bounded-memory large-file ingest + provenance. **Never claim performance.**
5. **VALIDATE + HANDOFF:** `PYTHONPATH=. python -m pytest tests/ -q` must stay green (>=116). Update **only** root `HANDOFF.md` with timestamp, evidence, artifacts, and next concrete heavy task.

**RULES (non-negotiable):** Items 1–5, 6a/6b done — no rework. Infer; don't ask. **Heavy-work guardrail:** every session ships >=1 of verified-data ingest/provenance completion, a real 283-day run with evidence, real metrics artifacts, or material gated-pipeline/tests/universe/spec hardening. No fabrication, no fixture substitution for real market evidence, no idle waiting, no partial-not-evidence misuse as spec evidence. PDF/spec is truth. Both legs non-negotiable. ETH hedge every leg. Funding/liquidation correct. >=$5M volume filter everywhere. Equal-share cuts across old+new.

## CRITICAL CONTEXT (SOURCE OF TRUTH)
- **Spec:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Test window 2025-12-20→2026-09-28 (283d), **6792 hourly bars/symbol**.
- **Core:** `src/strategy/*`, `src/backtest/engine.py`, `src/data/{loader,provenance}.py`, `src/metrics/campaign_metrics.py`
- **Runners/tools:** `scripts/run_campaign.py` (fixture smoke), `scripts/fetch_hyperliquid_candles.py` (API/archive ingest + provenance), `scripts/derive_verified_universe.py` (local verified-cache 24h-vol universe), `scripts/run_real_campaign.py` (gated real, `--universe-file`, `--min-symbols`, `--allow-partial-not-evidence` **NOT performance evidence**)
- **Mechanics:** RSI(21)<20 primary (fallback drop via `use_rsi_trigger=False`), both legs (long crash + rebound short), ETH hedge every leg vol-ratio capped 3x, funding all legs (positive rate: longs pay, shorts receive), hourly worst-price liquidation+penalty, >=$5M vol filter all trigger paths, vol sizing ON 1.25% 24h vol, gross cap 120% equal-share cuts across ALL positions (old+new). Stopped buy never opens rebound short.

## SUCCESS CRITERIA (ITEM 6c)
- [ ] Verified 283-day hourly dataset ingested; provenance manifest complete (`6792/6792`, gaps=0, documented source, checksums) for required universe.
- [ ] `universe_verified.json` (or equivalent verified universe evidence) derived/reconciled with >=$5M 24h vol policy and documented.
- [ ] `run_real_campaign.py` (default mode, no partial flag) executes cleanly; `campaign_results_real.json` + real metrics JSON/CSV written with `real_market_data=true`/`performance_evidence=true`/`manifest_sha256`/provenance+coverage summary and full metrics incl. max DD series w/ timestamps.
- [ ] Tests remain green (>=116).
- [ ] `HANDOFF.md` updated with timestamped results + next concrete heavy task (or concrete blocker evidence + scheduled retry + parallel heavy work done).
