# HANDOFF — CRASH-REBOUND-STRATEGY
**Timestamp:** 2026-11-13T01:10:06Z
**Session Objective:** Unblock the real 283-day campaign by acquiring verified Hyperliquid hourly candles.

---

## REPOSITORY STATE (do not re-implement — already complete)

- **Strategy** (`src/strategy/crash_rebound.py`): Spec-compliant crash-rebound with RSI(21)<20 trigger, +9%/50h buy exit, optional -9%/48h rebound short, ETH hedge on every leg (vol-ratio, cap 3x), 1.25% daily volume sizing, 120% gross cap with equal-share cuts.
- **Backtest Engine** (`src/backtest/engine.py`): Hourly bar simulation with fees, funding, slippage proxy, hourly worst-price liquidation checks, no look-ahead.
- **Risk Management** (`src/strategy/risk.py`): Daily loss halt, position caps, equal-share cut logic.
- **Data/Provenance** (`src/data/`): Loader, streaming ingest, provenance manifest with SHA256, coverage analysis, synthetic detection (flat series), volume coverage analysis.
- **Real Campaign Runner** (`scripts/run_real_campaign.py`): **Hard gates** — refuses fixture/synthetic data, requires complete verified provenance manifest, emits `real_market_data=true`, `performance_evidence=true` artifacts.
- **Data Fetcher** (`scripts/fetch_hyperliquid_candles.py`): Ingests user-supplied verified archives (JSON/CSV/Parquet/NDJSON), writes per-symbol caches, emits provenance manifest with `summary.ready_for_real_campaign`.

---

## THE BLOCKER (concrete, verified, non-negotiable)

| Item | Status |
|------|--------|
| Target window | 2025-12-20T00:00:00Z → 2026-09-28T23:00:00Z (283 days, 6792 hourly bars) |
| Hyperliquid public API | Returns **only 2026-04-11 → 2026-09-28** (4094 bars) — **early window missing** |
| Current cache (`research_state/cache/hyperliquid_verified_283d_btceth/`) | **SYNTHETIC PLACEHOLDER** — constant OHLCV, `synthetic_check.is_synthetic=true`, `manifest_status=error` |
| `universe_verified.json` | **0 selected symbols** — BTC/ETH both `excluded_reason: manifest_status:error` |
| `run_real_campaign.py` | **EXITS NON-ZERO** — hard gate refuses incomplete/unverified data |

**Evidence:** `research_state/DATA_REQUEST_283D_HYPERLIQUID.md`, `research_state/universe_verified.json`, `research_state/candle_coverage_gap_report.json`.

---

## NEXT AGENT MISSION — SINGLE DURABLE TASK

**ACQUIRE A VERIFIED ARCHIVE OF REAL HYPERLIQUID HOURLY CANDLES FOR THE FULL 283-DAY TARGET WINDOW.**

### Minimum Acceptable Delivery
- **Symbols:** At minimum **BTC and ETH** (for plumbing validation); ideally the full spec universe (~26-80 symbols with ≥$5M 24h volume).
- **Format:** Directory of per-symbol files (`<SYMBOL>.json` or `<SYMBOL>.csv`) or multi-symbol container (JSON/CSV/Parquet/NDJSON).
- **Content per bar:** `timestamp` (ISO or ms), `open`, `high`, `low`, `close`, `volume` (base coin volume, per Hyperliquid perp convention).
- **Coverage:** **6792/6792 bars**, `first == 2025-12-20T00:00:00Z`, `last == 2026-09-28T23:00:00Z`, `gap_count == 0`.
- **Integrity:** No flat/constant series, non-finite OHLC checks pass.
- **Provenance:** Documented source, extraction method, extraction timestamp, any transformations.

### Ingestion & Validation Commands (run after archive delivery)
```bash
# 1. Ingest archive → write caches + provenance manifest
PYTHONPATH=. python scripts/fetch_hyperliquid_candles.py \
  --source archive \
  --input-archive <ARCHIVE_PATH> \
  --symbols BTC ETH <OTHER_SYMBOLS...> \
  --start 2025-12-20T00:00:00Z \
  --end 2026-09-28T23:00:00Z

# 2. Verify manifest shows ready_for_real_campaign=true
cat research_state/cache/hyperliquid/provenance.json | jq '.summary'

# 3. Execute REAL campaign (gated, produces evidence artifacts)
PYTHONPATH=. python scripts/run_real_campaign.py \
  --manifest research_state/cache/hyperliquid/provenance.json

# 4. Verify output
cat research_state/campaign_results_real.json | jq '.research_status, .real_market_data, .performance_evidence, .results.num_trades, .results.total_pnl'
```

### Success Criteria
- `provenance.json` → `summary.all_complete=true`, `ready_for_real_campaign=true`
- `campaign_results_real.json` → `research_status="REAL_MARKET_RUN"`, `real_market_data=true`, `performance_evidence=true`, `num_trades > 0`
- Full metrics computed (Sharpe, Sortino, max DD series w/ timestamps, Calmar, win rate, profit factor, monthly/weekly breakdown, trade attribution, exposure metrics)

---

## WHAT NOT TO DO
- ❌ Do NOT fabricate/synthesize/generate placeholder data — synthetic_check will detect and reject it.
- ❌ Do NOT run `run_real_campaign.py` without a complete verified manifest — it exits non-zero by design.
- ❌ Do NOT modify the hard gates — they exist to prevent false evidence.
- ❌ Do NOT mark `NOT_RUN` as complete without steps 1–6 in DATA_REQUEST_283D_HYPERLIQUID.md satisfied.

---

## CONTEXT FOR DATA ACQUISITION
- Hyperliquid public `info` API `candleSnapshot` endpoint has limited historical depth.
- Possible sources: Hyperliquid team/data partners, verified community archives, data vendors with Hyperliquid perp history, or self-hosted indexer snapshots.
- The archive must be **verifiable** (SHA256, documented origin) — downstream gates enforce this.

---

**This handoff is the single durable directive. The codebase is complete. The only path forward is real data acquisition.**