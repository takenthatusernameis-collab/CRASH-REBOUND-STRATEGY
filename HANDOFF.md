# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Timestamp (UTC):** 2026-11-13T01:14:42Z
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Status:** **NO REAL PERFORMANCE EVIDENCE.** Implementation/plumbing complete; **real 283-day spec campaign is BLOCKED** by missing verified, complete, non-synthetic market data for the required universe/provenance gates.

**This file is the durable handoff.** Next session must execute the campaign below; do not substitute analysis of fixtures/probes for real evidence.

---

## 1) Verified current state (facts)

- **Spec:** `research_state/strategy_spec.md`, `crash-rebound-strategy.pdf` (283d window `2025-12-20T00:00:00Z` → `2026-09-28T23:00:00Z`, 6792 hourly bars/symbol, universe = HL perps with ≥$5M 24h volume, one position/coin, buys+shorts capped 120% of vault w/ equal-share cuts, ETH hedges, 20s slicing/order-book impact described in spec).
- **Implementation present:** `src/strategy/*`, `src/backtest/engine.py` (hourly sim, fees/funding/liquidation checks as implemented), `src/data/provenance.py`, `scripts/fetch_hyperliquid_candles.py` (archive/API ingest + provenance, parquet supported), `scripts/run_portfolio.py`, `scripts/run_real_campaign.py` (fail-closed gates), `scripts/run_campaign.py` (fixture smoke only).
- **Fixture smoke (NOT evidence):** `python scripts/run_campaign.py` → `research_state/campaign_results.json` with `research_status: "SMOKE_TEST_ONLY"`, `real_market_data=false`, synthetic fixtures.
- **Real run correctly blocked:** `python scripts/run_real_campaign.py` exits non-zero without complete, verified, non-synthetic provenance for the required symbols/window.
- **Cached “verified” BTC/ETH dataset is INVALID for evidence:** `research_state/cache/hyperliquid_verified_283d_btceth/provenance.json` shows BTC/ETH `status:"error"`, `synthetic_check.is_synthetic=true` (`flat_series_all_bars_identical`, 1/6792 distinct signatures) despite 6792-bar coverage; source recorded as temp path `/home/runner/work/_temp/kilo-tmp/tmp67sjtviy/archive.parquet`. Gap report `research_state/candle_coverage_gap_report.json` / `research_state/candle_coverage_gap_report_verified_btceth_283d.json` reflect this fail-closed state.
- **Potential unexploited lead (must be verified, not assumed):** canonical archived parquet exists at `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` (119K, BTC+ETH, schema `symbol,timestamp_ms,open,high,low,close,volume`) with `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.README.json` claiming 6792/6792 coverage, sha256, and persisted from a discovered source. **Do not trust claims without re-ingest + synthetic/integrity checks passing from this canonical path.** Even if valid, BTC/ETH alone ≠ spec’s full ≥$5M universe campaign.
- **Workspace hygiene (done this session):** root-level `_probe/_debug/_trace/_repro/_verify_*`, `trace_leak.py`, `leak_check.py`, and temp dirs moved to `scratch/probes_2026-11/` to remove clutter; no code/strategy changes made.

---

## 2) Critical blockers (priority order)

1. **No verified, non-synthetic, provenance-approved 283-day dataset for the SPEC-RELEVANT UNIVERSE** (all HL perps meeting ≥$5M 24h volume per spec, with documented symbol selection) covering `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z` (6792 bars, gap_count=0, integrity OK, no look-ahead). **This is the sole blocker to real evidence.**
2. **BTC/ETH canonical archive lead unresolved:** `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` must be re-ingested from its canonical path and proven non-synthetic/valid; current cache marks equivalent-looking data synthetic (temp-path provenance). Resolve discrepancy with evidence.
3. **Universe derivation/reconciliation missing:** spec requires coins with ≥$5M 24h volume over the window; `research_state/universe_verified.json`/scripts like `derive_verified_universe.py` must be grounded in verified data, not assumed.
4. **Execution-realism gap (known, non-blocking for first real hourly run but must be reported):** implementation is hourly-bar simplified (slippage/funding/liquidation proxies as configured); spec’s 20s slicing + L2 order-book impact not reproduced. Any real result must state this limitation explicitly.

**DO NOT FABRICATE, SYNTHESIZE, OR “FILL” MARKET DATA. DO NOT mark 283d campaign complete without verified provenance and a gated real run.**

---

## 3) Next focus campaign — HEAVY, ORDERED, NON-OPTIONAL

### Phase A — Resolve BTC/ETH archive lead (immediate, concrete)
1. Inspect & validate canonical archive in-place (no temp copies as source of truth):
   - Confirm schema/content stats for BTC,ETH: 6792 bars each, full timestamp coverage, non-flat OHLCV, sane ranges, volume presence.
   - Record SHA256 and compare to `...verified.README.json`.
2. Re-ingest from canonical path into a clean cache with provenance (example; adjust paths/flags per script help):
   - `PYTHONPATH=. python scripts/fetch_hyperliquid_candles.py --source archive --input-archive research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet --symbols BTC,ETH --start 2025-12-20T00:00:00Z --end 2026-09-28T23:00:00Z`
3. **Hard acceptance:** resulting provenance/manifest shows `summary.all_complete=true`, `ready_for_real_campaign=true` (or equivalent gates), `complete_for_target_window=true`, `gap_count==0`, and **no synthetic/flat-series rejection** for BTC,ETH. If still rejected, document exact failing check from `src/data/provenance.py` and fix only if it’s a provenance/path-handling bug (not by weakening integrity/synthetic detection). If data truly flat, declare archive invalid.
4. If BTC/ETH pass: run a **plumbing-validation real portfolio run on BTC,ETH only** via `scripts/run_real_campaign.py` with that manifest. Label outputs clearly as **BTC/ETH-only validation, NOT full spec campaign/universe**. Save/commit artifacts with provenance refs.

### Phase B — Obtain/ingest VERIFIED full-universe 283-day data (the real gate)
1. Locate or acquire a **verifiable, non-fabricated** hourly OHLCV archive for all required Hyperliquid perp symbols (≥$5M 24h volume per spec) for the exact 283d window. Acceptable: user-supplied archive, documented export, or another verifiable source — **with origin, extraction time/method, and checksums recorded**. See `research_state/DATA_REQUEST_283D_HYPERLIQUID.md`.
2. Derive/reconcile the spec universe from verified data (document criteria, symbol list, volume evidence) → update `research_state/universe_verified.json` with provenance.
3. Ingest full universe (`fetch_hyperliquid_candles.py --source archive ...`), produce passing provenance (`all_complete=true`, `ready_for_real_campaign=true`, all symbols complete, no synthetic flags).
4. **Do not proceed to claims without this.** If unavailable in-environment, produce a concrete acquisition artifact: exact missing inputs, required format, and commands to run once provided (but treat acquisition+ingest as the blocking work, not a stopping point for preparation).

### Phase C — Execute real 283-day campaign & full analysis (once Phase B passes)
1. Run: `PYTHONPATH=. python scripts/run_real_campaign.py --manifest <verified_manifest>`
2. Produce **full metrics** with timestamps/series (not summaries only): equity curve, returns, Sharpe, Sortino, max drawdown (value + start/trough/end timestamps), Calmar, win rate, profit factor, monthly & weekly breakdowns, trade/leg attribution (buys vs rebound shorts vs hedges), exposure/gross-cap utilization, liquidation/funding/fee impacts as available.
3. Persist machine-readable + human-readable outputs under `research_state/` (e.g. `campaign_results_real.json`, metrics CSV/JSON, plots if feasible) with explicit `real_market_data=true`, `performance_evidence=true`, provenance/manifest hash/path, symbol universe, and execution-realism limitations.
4. Compare vs spec context (+81.2% total, +115.2%/yr, -5.4% worst DD, 85 trades: 73 buys/71% win, 12 shorts/83% win) — attribute differences (data/universe/execution model/parameterization) with evidence.
5. Update this `HANDOFF.md`: mark blockers resolved/unresolved with evidence, record exact commands run, artifact paths, and remaining gaps.

### Phase D — Validation hardening (parallel/after C as appropriate)
- Run/extend tests: `PYTHONPATH=. pytest -q` (and targeted suites) especially around portfolio reservation/cap cuts, same-bar edge cases, hedge sizing, exits, liquidation/funding accounting.
- Ensure `run_real_campaign.py`/provenance gates cannot be bypassed; add/adjust tests only if they reflect spec-correct, evidence-backed behavior.

---

## 4) Key commands & files

- Inspect/ingest: `PYTHONPATH=. python scripts/fetch_hyperliquid_candles.py --help`
- Gated real run: `PYTHONPATH=. python scripts/run_real_campaign.py --manifest <provenance.json>`
- Fixture smoke (not evidence): `PYTHONPATH=. python scripts/run_campaign.py`
- Portfolio sim: `PYTHONPATH=. python scripts/run_portfolio.py`
- Tests: `PYTHONPATH=. pytest -q`
- Provenance/gates: `src/data/provenance.py`
- Data request/checklist: `research_state/DATA_REQUEST_283D_HYPERLIQUID.md`
- Canonical BTC/ETH archive lead: `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` (+ README)
- Invalid cached “verified”: `research_state/cache/hyperliquid_verified_283d_btceth/provenance.json`
- Prior artifacts (fixture): `research_state/campaign_results.json`, `research_state/campaign_metrics.*`

## 5) Definition of “significant progress” for next session
- **Minimum:** Phase A completed with a definitive, evidence-backed outcome (BTC/ETH canonical archive validated & ingested to passing provenance + BTC/ETH-only real plumbing run, OR proven invalid with failing checks documented and remediated if bug).
- **Target:** Phase B completed (verified full-universe data + passing provenance) and Phase C real campaign executed with full metrics/artifacts.
- **Unacceptable:** further probe-script churn, fixture-only reporting presented as progress, or declaring blockage without actively attempting Phase A against the canonical archived parquet and documenting exact results.

*End of handoff.*
