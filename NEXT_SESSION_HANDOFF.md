# CRASH-REBOUND-STRATEGY — Next Session Handoff
**Timestamp**: 2026-11-09T17:30:29Z
**Session Status**: All tests pass (693 passed, 12 skipped). **CRITICAL BLOCKER** for real campaign: no verified market data.

---

## Project Overview
This repo implements the "Crash Rebound Strategy" (Hyperliquid hourly perps) from `crash-rebound-strategy.pdf`:
- **Universe**: Altcoins with ≥$5M 24h volume (~26-80 coins)
- **Crash Trigger**: 21h RSI < 20 → buy next hourly open
- **Buy Exit**: +9% target OR 50h time exit; safety stop at 8× usual hourly range
- **Rebound Short**: If buy hits +9%, short same coin (target -9%, max 48h, stop +40%)
- **ETH Hedge**: Every leg, vol-ratio sized, capped 3×
- **Gross Cap**: 120% vault, equal-share cuts when new positions arrive
- **Simulation**: Hourly bar (fees, slippage, funding, liquidation). **Spec gap**: 20s order slicing & L2 book impact NOT simulated.

---

## Current State — What Works
| Component | Status |
|-----------|--------|
| Strategy logic (`src/strategy/crash_rebound.py`) | Complete, spec-aligned |
| Backtest engine (`src/backtest/engine.py`) | Complete |
| Data provenance (`src/data/provenance.py`) | Complete, strict gates |
| Data loader (`src/data/loader.py`) | Complete |
| Streaming ingest (`src/data/streaming_ingest.py`) | Complete |
| Campaign runner (`scripts/run_real_campaign.py`) | Complete, refuses unverified data |
| Archive ingestion (`scripts/fetch_hyperliquid_candles.py`) | Complete |
| Test suite (705 tests) | **All passing** |

---

## Critical Blocker: No Verified Market Data
**The real campaign CANNOT RUN** because verified data for the full 283-day window (2025-12-20 → 2026-09-28, 6792 hourly bars) is unavailable.

| Source | Coverage | Status |
|--------|----------|--------|
| Hyperliquid public API | ~60% (4078/6792 bars) for BTC/ETH only | **Incomplete** — API doesn't serve full history |
| `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` | 100% bars but **synthetic** (flat series: 1 distinct signature / 6792 bars) | **Rejected** by provenance — correctly detected as fabricated |

The provenance system (`require_verified_provenance`) correctly blocks the run:
```
BLOCKER: Verified 283-day Hyperliquid dataset unavailable for 2025-12-20→2026-09-28.
Do NOT fabricate data. Provide a verified archive via scripts/fetch_hyperliquid_candles.py --source archive --input-archive <path>.
```

---

## Next Focus Campaign — Heavy Work Required
Since real data acquisition may be environment-limited, the next session **must** execute one of these high-impact tracks. No "light" work — pick a track and drive it to completion.

### Track A: Real Data Acquisition (Highest Value)
**Objective**: Obtain or construct a verified archive with real market data for ≥5 coins with ≥$5M 24h volume over the full 283-day window.
- **Actions**:
  1. Source real Hyperliquid historical data (commercial API, data vendor, or full-node archive)
  2. Ingest via `scripts/fetch_hyperliquid_candles.py --source archive --input-archive <real_data.parquet>`
  3. Verify provenance manifest shows `ready_for_real_campaign: true` with ≥5 complete symbols
  4. Run `scripts/run_real_campaign.py` → produce `research_state/campaign_results_real.json` with `performance_evidence: true`
- **Success Criteria**: Real campaign completes, outputs metrics matching PDF (~+81% over 283d, 85 trades, 71% buy win rate, 83% short win rate)

### Track B: Spec-Compliant Execution Realism (High Value)
**Objective**: Close the documented simulation gaps vs. the PDF spec.
- **Gaps to Implement**:
  1. **20s order slicing**: Simulate intra-hour slice execution (never >50% resting book per slice, ~20s between slices)
  2. **L2 order-book impact**: Replace `slippage_pct` proxy with actual book depth simulation
  3. **Spread modeling**: Separate spread from slippage (currently folded together)
- **Files to Modify**: `src/backtest/engine.py`, `src/strategy/config.py` (execution realism fields), `scripts/run_real_campaign.py` (metadata)
- **Success Criteria**: Backtest produces results with `execution_model: "sub_hourly_slicing_l2_impact"` and documented realism markers

### Track C: Full Universe Pipeline Hardening (Medium Value)
**Objective**: Harden the multi-coin universe pipeline for production-scale runs (26-80 coins).
- **Actions**:
  1. Implement `derive_verified_universe.py` to auto-discover ≥$5M volume coins from verified archives
  2. Stress-test portfolio engine with 20+ concurrent symbols (gross cap cuts, ETH hedge contention, funding accounting)
  3. Add circuit breakers: daily loss halt, max gross exposure alerts, liquidation cascade guards
  4. Optimize RSI cache (`_rsi` with per-symbol prefix cache) for O(n) scanner
- **Files**: `scripts/derive_verified_universe.py`, `scripts/run_portfolio.py`, `src/strategy/crash_rebound.py`
- **Success Criteria**: `test_stress_campaign.py` passes with 20+ symbols, no look-ahead, correct cap-cut mechanics

### Track D: Campaign Resume & Checkpointing (Operational Value)
**Objective**: Make 283-day runs resumable after interruption.
- **Actions**:
  1. Implement checkpointing in `run_portfolio_simulation` (persist equity curve, open positions, risk state per bar)
  2. Add `--resume-from-bar` to `run_real_campaign.py`
  3. Verify idempotency: resume produces bit-identical results
- **Files**: `scripts/run_portfolio.py`, `scripts/run_real_campaign.py`, `src/backtest/engine.py`
- **Success Criteria**: Kill/restart mid-campaign → identical final results

---

## Immediate Next Step for Next Agent
**DO NOT** start with exploration. **DO** pick a track above and execute.

**Recommended Track**: **A** (if real data accessible) or **B** (if data-locked). Track A unlocks the actual strategy validation; Track B closes the biggest spec-compliance gap.

**Commands to verify current state**:
```bash
# Verify tests still pass
cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY
python -m pytest tests/ -x --tb=short

# Check data status
cat research_state/cache/hyperliquid/provenance.json | jq '.summary'

# Attempt real campaign (will block)
python scripts/run_real_campaign.py --cache-dir research_state/cache/hyperliquid
```

**Environment Notes**:
- Python 3.12.3, pytest 9.2.0
- `pyarrow` now installed (needed for parquet ingestion)
- Repo root: `/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY`
- All source in `src/`, scripts in `scripts/`, tests in `tests/`

---

## Handoff Protocol
The next agent **must**:
1. Read this file first
2. Pick ONE track (A/B/C/D) and announce it in the first response
3. Execute heavy work — no cosmetic changes, no "let me look around"
4. Report concrete progress (files changed, tests added/passing, artifacts produced) at session end

**No exceptions. No avoidance. Ship the track.**