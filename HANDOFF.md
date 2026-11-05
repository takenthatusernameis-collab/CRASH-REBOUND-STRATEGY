# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-11-05T21:46:11Z

## SINGLE CANONICAL HANDOFF
Only this root `HANDOFF.md` is durable. Do **not** create/read any other handoff file. This file is the sole source of next-session direction.

## CURRENT VERIFIED STATUS — 2026-11-05T21:43:10Z (supersedes all prior state)
- **Items 1–5 DONE/GREEN (do not reopen):** RSI(21)<20 primary trigger ON (`use_rsi_trigger=True`, `src/strategy/config.py:19`), ETH hedge on every leg (vol-ratio capped 3x, `compute_eth_hedge_size` in `src/strategy/crash_rebound.py:31`), volume-based sizing ON (1.25% 24h vol, `enable_volume_based_sizing=True`), >=$5M volume filter on all trigger/universe paths (`min_daily_volume_usd=5_000_000`), equal-share cap cuts across old+new via `RiskState.apply_cap_cuts()` (`src/strategy/risk.py:102`), funding/liquidation checks correct.
- **Item 6a/6b DONE/GREEN:** `src/metrics/campaign_metrics.py` full suite. `scripts/run_campaign.py` exports fixture-smoke artifacts with explicit provenance (`fixture_smoke_test` / `real_market_data=false` / `performance_evidence=false`).
- **Data/provenance pipeline + hard gates (GREEN):** `scripts/fetch_hyperliquid_candles.py` (API/archive ingest, chunks, normalizes, provenance; never fabricates). `src/data/provenance.py` + `require_verified_provenance()` enforce 283-day coverage/gap checks and refuse real runs. `scripts/run_real_campaign.py` hard-gated. `scripts/derive_verified_universe.py` derives verifiable `universe_verified.json` from local verified caches only.
- **Prior deliverables shipped (retain):** long-leg/hedge funding fixes + regressions; rebound short *coin-leg* funding on liquidation/stop/target/time-exit/final-exit paths (`src/backtest/engine.py`) + `test_rebound_short_coin_funding_applied`; portfolio ordering by deepest crash first (RSI severity, drop fallback) in `scripts/run_portfolio.py`; deterministic e2e `test_e2e_archive_to_manifest_universe_and_gate` (archive→manifest→incomplete→gate refuses; synthetic non-evidence).
- **Full suite `PYTHONPATH=. python -m pytest tests/ -q` → 121 passed, 0 failed (verified 2026-11-05T21:43Z).** Git working tree clean before this handoff update.

## ITEM 6c — REAL 283-DAY HYPERLIQUID CAMPAIGN (BLOCKED BY VERIFIED DATA)
- **Target window:** `2025-12-20T00:00:00Z → 2026-09-28T23:00:00Z` (283 days, **6792 hourly bars/symbol**), spec-relevant universe (>= $5M 24h vol, documented/verified). Non-fabricated; checksums/provenance required.
- **Blocker evidence (re-probed 2026-11-05T21:43Z, this session):** Hyperliquid public `candleSnapshot` (BTC/ETH, `1h`, full target range `start=1766188800000 end=1790636400000`) returned **4090/6792** bars, `first=2026-04-11T14:00:00+00:00`, `last=2026-09-28T23:00:00+00:00`, `complete=False`. Early window `2025-12-20→2026-04-11` missing. `research_state/cache/hyperliquid/provenance.json` shows BTC/ETH `status=incomplete`, `complete_for_target_window=false`, `all_complete=false`, `ready_for_real_campaign=false`. Default gate refuses. **No verified parquet/archive covering full 283-day window found in accessible filesystem scan.**
- **Non-evidence debug path** (`--allow-partial-not-evidence`) exists but does **not** satisfy 6c; never report as campaign performance.
- **Scheduled retry:** wakeup `wku_0357bb0fbc012vvabNPsVaGhdW` due **2026-11-06T02:58Z** — re-probe Hyperliquid public API for full 283-day coverage; if complete, ingest→verify→derive universe→run real campaign; if not, append evidence and execute heavy non-data track (no idle).

## BOTTLENECK REMOVAL — MANDATORY NON-IDLE CAMPAIGN (FUTURE AGENTS MUST DO HEAVY WORK)
ITEM 6c is data-blocked; **idleness is not acceptable**. Each session MUST ship >=1 heavy, reviewable deliverable (code/tests/artifacts/evidence), chosen by leverage:
1. **Verified 283-day ingest/provenance completion** (only with real, documented, checksummed data).
2. **A real 283-day campaign run with evidence** (gate-passing, `real_market_data=true`, `performance_evidence=true`).
3. **Real metrics artifacts** from a gate-passing run.
4. **Material gated-pipeline/tests/universe/spec hardening** (test-first, deterministic, no fabrication, no fixture substitution for performance evidence).

**If data is still blocked, do not report “waiting”. Do track 4 now.** Parallel heavy-work backlog (execute in order of risk/leverage):

### Data track (execute on retry/wakeup or if verified archive appears)
1. Re-probe Hyperliquid public API for full 283-day coverage (BTC/ETH + universe candidates). If verified-complete, ingest via `scripts/fetch_hyperliquid_candles.py --source archive --input-archive <ARCHIVE> --start 2025-12-20T00:00:00Z --end 2026-09-28T23:00:00Z` (or API if it serves full window). Gate requires `6792/6792`, `gap_count=0`, `all_complete=true`, `ready_for_real_campaign=true`, documented source/checksums.
2. Derive/verify universe: `scripts/derive_verified_universe.py --manifest ... --cache-dir ... --min-24h-volume-usd 5000000 --output research_state/universe_verified.json`. Review symbols/report; document method and exchange-snapshot limits.
3. Run real campaign (only when gate passes): `scripts/run_real_campaign.py --manifest ... [--universe-file ...] --min-symbols <N>` → `research_state/campaign_results_real.json` + `campaign_results_real_metrics.json/.csv` with `real_market_data=true`, `performance_evidence=true`, `manifest_sha256`, provenance/coverage, symbols/universe policy, trade count/PnL, **max drawdown series with timestamps**, Sharpe/Sortino/Calmar/win rate/profit factor/monthly-weekly/attribution/exposure. Keep fixture artifacts separate. **Never use `--allow-partial-not-evidence` to satisfy 6c.**

### Non-data heavy-work track (DO NOW when data-blocked; test-first)
1. **Spec-fidelity audit vs `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`:** buy safety stop **8x usual hourly range** (avg |high-low|/prev close over last 14h) + median ~15% sanity; ETH hedge sizing timing/2-week vol lookback fidelity; 120% cap equal-share cuts under concurrent opens (old+new, never top up); stopped buy never opens rebound short (verify all paths); rebound-short coin funding on *all* exit paths; volume sizing semantics (1.25% 24h vol; 20s slicing not simulated hourly — document simplification explicitly); one position per coin; no look-ahead hourly worst-price liquidation/fees/spread/order-book-impact assumptions. Add failing tests first; fix only true spec gaps; do not regress items 1–5/6a–6b.
2. **Deterministic end-to-end pipeline tests (synthetic/non-evidence, clearly marked):** tmp chain covering `archive (CSV w/ symbol col, JSON map, NDJSON if supported) → fetch/ingest manifest → derive universe → default gate refuses incomplete → partial-not-evidence marks correctly → complete verified-like tmp data produces evidence-marked run in tmp repo`. Cover multi-symbol/ETH hedge alignment where feasible. These tests prove pipeline correctness, **not market performance**.
3. **Universe derivation hardening:** align with spec's 24h-volume semantics and Hyperliquid snapshot limits; add verified-cache e2e tests; make method/limitations explicit in artifacts.
4. **Robust ingest:** parquet/NDJSON/streaming or bounded-memory large-file ingest + provenance checksums if formats/libs appear; keep gates strict; no fabrication.
5. **Campaign runner completeness (test-first):** rebound-short legs + ETH hedges with real-data-compatible paths, eth_candles alignment, per-symbol/per-leg attribution, deterministic outputs, timestamps preserved for DD series.

## INITIAL TASK MESSAGE (TIMESTAMPED, SINGLE, NEXT AGENTIC SESSION) — EXECUTE HEAVY WORK

`CRASH-REBOUND-STRATEGY | 2026-11-05T21:46:11Z | MISSION (repo name priority): crash-rebound strategy fidelity to crash-rebound-strategy.pdf | ITEM 6c = UNBLOCK + EXECUTE REAL 283-DAY HYPERLIQUID CAMPAIGN (2026-09-28T23:00:00Z back 283 days = 2025-12-20T00:00:00Z, 6792 hourly bars/symbol, VERIFIED PROVENANCE, ZERO GAPS, spec-relevant >=$5M 24h-vol universe) | BLOCKER (re-probed 2026-11-05T21:43Z): Hyperliquid candleSnapshot BTC/ETH full-window returns 4090/6792 bars, first=2026-04-11T14:00:00+00:00 last=2026-09-28T23:00:00+00:00, early window missing; cache provenance all_complete=false, ready_for_real_campaign=false; default gate refuses; no verified full archive in filesystem | RETRY WAKEUP wku_0357bb0fbc012vvabNPsVaGhdW due 2026-11-06T02:58Z | 121 tests green | DO NOT IDLE: ship >=1 heavy deliverable this session (verified ingest/provenance, real 283d run+evidence, real metrics, or material test-first pipeline/spec hardening) | PARTIAL-NOT-EVIDENCE IS NOT SPEC EVIDENCE`

**EXECUTE IN ORDER (infer; do not ask). Every session MUST ship >=1 heavy deliverable.**
1. **OBTAIN/INGEST VERIFIED 283-DAY DATA (highest leverage):** Secure a verifiable, non-fabricated hourly OHLCV archive covering the full target window (`6792/6792` bars/symbol, zero gaps, documented source/extraction/checksums) for the spec-relevant universe. Ingest via `fetch_hyperliquid_candles.py --source archive --input-archive <ARCHIVE> --symbols <...> --start 2025-12-20T00:00:00Z --end 2026-09-28T23:00:00Z`. Gate: `research_state/cache/hyperliquid/provenance.json` → `summary.all_complete=true`, `ready_for_real_campaign=true`, `6792/6792`, `gap_count=0`. Follow `research_state/DATA_REQUEST_283D_HYPERLIQUID.md`.
2. **DERIVE/VERIFY UNIVERSE (>= $5M 24h vol, spec):** `derive_verified_universe.py --manifest ... --cache-dir ... --min-24h-volume-usd 5000000 --output research_state/universe_verified.json`. Review/report; document method + exchange-snapshot limits.
3. **RUN REAL 283-DAY CAMPAIGN (only when gate passes):** `run_real_campaign.py --manifest ... [--universe-file ...] --min-symbols <N>`. Produce real results + metrics with `real_market_data=true`, `performance_evidence=true`, `manifest_sha256`, provenance/coverage, full metrics incl. max DD series w/ timestamps. Keep fixture artifacts separate. **Never use `--allow-partial-not-evidence` to satisfy 6c.**
4. **IF STILL DATA-BLOCKED: DO NOT IDLE/WAIT.** Re-probe public API (chunk if needed); append concrete evidence (counts, first/last, errors) to this HANDOFF; update gap/provenance artifacts; keep retry scheduled. **Then ship >=1 heavy deliverable now** from non-data track: spec-fidelity audit+tests, deterministic e2e pipeline tests, universe derivation hardening+tests, robust ingest, or campaign runner completeness — all test-first, all non-fabricated. **Never claim performance.**
5. **VALIDATE + HANDOFF:** `PYTHONPATH=. python -m pytest tests/ -q` must stay green (>=121). Update **only** root `HANDOFF.md` with timestamp, concrete evidence, artifacts/commits, and the next heavy task.

## RULES (non-negotiable)
- Items 1–5, 6a/6b done — no rework. Infer; don't ask.
- **Heavy-work guardrail:** every session ships >=1 of (a) verified-data ingest/provenance completion, (b) real 283-day run with evidence, (c) real metrics artifacts, or (d) material gated-pipeline/tests/universe/spec hardening. No fabrication, no fixture substitution for real market evidence, no idle waiting, no partial-not-evidence misuse as spec evidence.
- PDF/spec is truth. Both legs non-negotiable. ETH hedge every leg. Funding/liquidation correct. >=$5M volume filter everywhere. Equal-share cuts across old+new. Stopped buy never opens rebound short.

## CRITICAL CONTEXT (SOURCE OF TRUTH)
- **Spec:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Test window 2025-12-20→2026-09-28 (283d), **6792 hourly bars/symbol**.
- **Core:** `src/strategy/*`, `src/backtest/engine.py`, `src/data/{loader,provenance}.py`, `src/metrics/campaign_metrics.py`
- **Runners/tools:** `scripts/run_campaign.py` (fixture smoke), `scripts/fetch_hyperliquid_candles.py` (API/archive ingest + provenance), `scripts/derive_verified_universe.py` (local verified-cache 24h-vol universe), `scripts/run_real_campaign.py` (gated real, `--universe-file`, `--min-symbols`, `--allow-partial-not-evidence` **NOT performance evidence**)
- **Mechanics:** RSI(21)<20 primary (fallback drop via `use_rsi_trigger=False`), both legs (long crash + rebound short), ETH hedge every leg vol-ratio capped 3x, funding all legs (positive rate: longs pay, shorts receive), hourly worst-price liquidation+penalty, >=$5M vol filter all trigger paths, vol sizing ON 1.25% 24h vol, gross cap 120% equal-share cuts across ALL positions (old+new). Stopped buy never opens rebound short.

## SUCCESS CRITERIA (ITEM 6c)
- [ ] Verified 283-day hourly dataset ingested; provenance manifest complete (`6792/6792`, gaps=0, documented source, checksums) for required universe.
- [ ] `universe_verified.json` (or equivalent verified universe evidence) derived/reconciled with >=$5M 24h vol policy and documented.
- [ ] `run_real_campaign.py` (default mode, no partial flag) executes cleanly; real results + metrics written with `real_market_data=true`/`performance_evidence=true`/`manifest_sha256`/provenance+coverage and full metrics incl. max DD series w/ timestamps.
- [ ] Tests remain green (>=121).
- [ ] `HANDOFF.md` updated with timestamped results + next concrete heavy task (or concrete blocker evidence + scheduled retry + parallel heavy work done).
