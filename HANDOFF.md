# CRASH-REBOUND-STRATEGY — Durable Handoff for Next Agentic Session

**Timestamp:** 2026-11-13T01:13:28Z
**Session Status:** BLOCKED — Real verified data unavailable; only synthetic fixtures runnable.

---

## Repository Context
**CRASH-REBOUND-STRATEGY** — Crash-rebound trading strategy for Hyperliquid perpetuals (altcoins).
Spec: RSI(21)<20 crash trigger → buy next hourly open → sell at +9% or 50h max → if +9% hit fast, short same coin for -9%/48h with long ETH hedge. Every trade hedged with ETH (coin_vol/ETH_vol capped at 3x). Position size = 1.25% of coin's 24h USD volume. Buys+shorts capped at 120% of vault with equal-share cuts.

---

## Current State (Verified Facts)

| Component | Status | Evidence |
|-----------|--------|----------|
| Strategy implementation | **Complete** | `src/strategy/crash_rebound.py`, `config.py`, `risk.py` |
| Backtest engine (hourly, fees, funding, liquidation) | **Complete** | `src/backtest/engine.py` |
| Portfolio simulation (multi-symbol, gross cap, same-bar reservation) | **Complete** | `scripts/run_portfolio.py` |
| Real-campaign runner (fail-closed provenance gates) | **Complete** | `scripts/run_real_campaign.py` |
| Data ingestion + provenance (archive + API) | **Complete** | `scripts/fetch_hyperliquid_candles.py`, `src/data/provenance.py` |
| **Verified 283-day Hyperliquid data (2025-12-20 → 2026-09-28)** | **MISSING** | `research_state/cache/hyperliquid_verified_283d_btceth/provenance.json` — both BTC & ETH: `synthetic_check.is_synthetic=true`, `status="error"`, flat series (1 distinct signature / 6792 bars) |
| Hyperliquid API historical coverage | **Incomplete** | API returns only 4094/6792 bars (2026-04-11 onward); see `research_state/candle_coverage_gap_report.json` |
| Fixture/smoke test | **Runs** | `python scripts/run_campaign.py` → `research_state/campaign_results.json` (`research_status: "SMOKE_TEST_ONLY"`) |
| Real evidence campaign | **BLOCKED** | `python scripts/run_real_campaign.py` exits non-zero with concrete provenance errors |

---

## Single Critical Bottleneck (Must Resolve Before Any Real Progress)

**OBTAIN A VERIFIED, NON-FABRICATED 283-DAY HOURLY OHLCV ARCHIVE FOR HYPERLIQUID PERPETUALS**

- **Target window (spec):** `2025-12-20T00:00:00Z` → `2026-09-28T23:00:00Z` (inclusive hourly, **6792 bars per symbol**)
- **Minimum symbols:** BTC + ETH (for plumbing validation); full campaign requires universe with ≥$5M 24h volume and documented symbol selection
- **Acceptable forms:** Directory of `<SYMBOL>.json` or `<SYMBOL>.csv` (OHLCV + timestamps mapping to hourly bars covering full window)
- **Verification checklist (ALL must pass):**
  1. Source documented (origin, extraction method, time, transformations)
  2. Coverage: 6792/6792 bars, first=2025-12-20T00:00:00Z, last=2026-09-28T23:00:00Z, gap_count=0
  3. Integrity: non-finite/invalid OHLC checks pass; SHA256 recorded
  4. No look-ahead/leakage: timestamps monotonic
  5. Provenance manifest generated via:
     ```
     PYTHONPATH=. python scripts/fetch_hyperliquid_candles.py --source archive --input-archive <ARCHIVE_PATH> --symbols BTC,ETH,... --start 2025-12-20T00:00:00Z --end 2026-09-28T23:00:00Z
     ```
     Must yield `summary.all_complete=true` and `ready_for_real_campaign=true`
  6. Real run executes:
     ```
     PYTHONPATH=. python scripts/run_real_campaign.py --manifest research_state/cache/hyperliquid/provenance.json
     ```
     Outputs `campaign_results_real.json` with `real_market_data=true`, `performance_evidence=true`

**DO NOT FABRICATE DATA.** The pipeline explicitly rejects synthetic/flat series. The current cache is a placeholder only.

---

## Next Heavy Action Campaign (When Unblocked)

1. **Ingest verified archive** → validate provenance (`fetch_hyperliquid_candles.py`)
2. **Execute real 283-day campaign** (`run_real_campaign.py`)
3. **Compute full metrics suite:** Sharpe/Sortino/max DD series w/ timestamps/Calmar/win rate/profit factor/monthly-weekly/attribution/exposure
4. **Compare vs spec context** (+81.2% total, +115.2%/yr, -5.4% worst drop, 85 trades: 73 buys 71% win, 12 shorts 83% win)
5. **Update HANDOFF.md** with real results + provenance reference

---

## If Data Remains Unavailable

- Do NOT run `run_real_campaign.py` (it will correctly block)
- Do NOT fabricate/fudge data (provenance gates will reject)
- Document the blocker explicitly in any status report
- The only runnable path is `run_campaign.py` (fixture smoke test only, `SMOKE_TEST_ONLY`)

---

## Key Files for Next Session

- `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` — detailed data request + verification checklist
- `research_state/cache/hyperliquid_verified_283d_btceth/provenance.json` — current (synthetic) provenance evidence
- `scripts/fetch_hyperliquid_candles.py` — ingestion + provenance generation
- `scripts/run_real_campaign.py` — gated real runner
- `src/data/provenance.py` — verification logic (complete_symbol_subset, require_verified_provenance)

---

**This handoff is the single durable signal. The next agent must not avoid the data acquisition task. No other work produces real evidence.**