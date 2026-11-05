# Data Request & Verification Checklist — Real 283-Day Hyperliquid Campaign (ITEM 6c)

**Timestamp:** 2026-11-05T18:41:20Z (handoff session)
**Target window (spec):** `2025-12-20T00:00:00Z` → `2026-09-28T23:00:00Z` (283 days, hourly)
**Required bars per symbol:** `6792` hourly candles (inclusive hourly bounds; see `src/data/provenance.expected_hourly_bars`).
**Status:** **NOT_RUN — VERIFIED DATA UNAVAILABLE IN THIS ENVIRONMENT. No data fabricated.**

## Concrete blocker evidence (2026-11-05)
- Hyperliquid public `info` API `candleSnapshot` (BTC/ETH, `1h`, requested full target range) returned data only from `2026-04-11T10:00:00Z` to `2026-09-28T23:00:00Z` with `4094/6792` bars, `gap_count=0` within that returned slice but **incomplete for target window** (missing early window coverage). See `research_state/candle_coverage_gap_report.json` and `research_state/cache/hyperliquid/provenance.json` (manifest records request params, counts, coverage; large candle payloads intentionally not retained).
- `scripts/run_real_campaign.py` **refuses to run** without a complete, verified provenance manifest (exit non-zero). This is correct behavior.

## What is needed (verified, non-fabricated)
Provide a user-supplied, verifiable archive of hourly OHLCV candles for the full target window for the required symbol universe (at minimum BTC/ETH for plumbing validation; for a real campaign, the spec-relevant universe with >=$5M 24h volume and documented symbol selection/provenance).

Acceptable archive forms (ingested by `scripts/fetch_hyperliquid_candles.py --source archive --input-archive <path>`):
- Directory containing `<SYMBOL>.json` or `<SYMBOL>.csv` per symbol
- Files must contain OHLCV + timestamps; timestamps must map to hourly bars covering the full target window

## Verification checklist (must pass before any real run)
1. **Source documented:** archive origin, extraction method, time of extraction, and any transformations recorded.
2. **Coverage:** for each symbol, `6792/6792` hourly bars, `first==2025-12-20T00:00:00Z`, `last==2026-09-28T23:00:00Z`, `gap_count==0` (or explicit, reviewed gaps — default gate requires zero gaps).
3. **Integrity:** non-finite/invalid OHLC checks pass; checksums/hashes recorded in provenance.
4. **No look-ahead/leakage:** timestamps monotonic; campaign uses only data available at decision time.
5. **Provenance manifest:** generate with
   `PYTHONPATH=. python scripts/fetch_hyperliquid_candles.py --source archive --input-archive <ARCHIVE_PATH> --symbols <...> --start 2025-12-20T00:00:00Z --end 2026-09-28T23:00:00Z`
   Manifest `research_state/cache/hyperliquid/provenance.json` must show `summary.all_complete=true` and `ready_for_real_campaign=true`.
6. **Real run (gated):**
   `PYTHONPATH=. python scripts/run_real_campaign.py --manifest research_state/cache/hyperliquid/provenance.json`
   Outputs `research_state/campaign_results_real.json` + `campaign_results_real_metrics.json/.csv` with `real_market_data=true`, `performance_evidence=true`, provenance reference, coverage summary.
7. **Never mark `NOT_RUN` as complete** without steps 1–6 satisfied with verified data.

## Next heavy action when unblocked
- Ingest verified archive → validate provenance → execute real 283-day run → compute full metrics (Sharpe/Sortino/max DD series w/ timestamps/Calmar/win rate/profit factor/monthly-weekly/attribution/exposure) → compare/report vs spec context (with provenance) → update `HANDOFF.md`.
