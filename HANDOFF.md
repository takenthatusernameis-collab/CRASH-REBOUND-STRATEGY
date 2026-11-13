# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Timestamp (UTC):** 2026-11-13T01:19:02Z (supersedes 2026-11-13T01:14:42Z edition)
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Status:** **NO REAL PERFORMANCE EVIDENCE.** Implementation/plumbing complete; **real 283-day spec campaign is BLOCKED** by missing verified, complete, non-synthetic market data for the full window.

**This file is the durable handoff.** Next session must execute the campaign below; do not substitute analysis of fixtures/probes for real evidence.

---

## 0) INITIAL TASK MESSAGE — next agentic work session (inferred from repo name `CRASH-REBOUND-STRATEGY`)

> **Task:** Produce the first REAL performance evidence for the crash-rebound strategy.
> You are resuming `CRASH-REBOUND-STRATEGY`. The strategy code, portfolio engine, provenance gates, and 905 passing tests are done. The ONLY remaining gate is data: a verified, non-synthetic, complete hourly OHLCV archive for Hyperliquid perps meeting the spec universe (≥$5M 24h volume) over `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z` (6792 bars/symbol).
> **Priority order (heavy work, non-optional):** (1) acquire/verify the full-window dataset (see Phase B below; the public API CANNOT supply pre-2026-04-19 hourly data — proven 2026-11-13); (2) derive the spec universe from verified data; (3) run `scripts/run_real_campaign.py` end-to-end and persist full metrics/artifacts; (4) compare vs spec context and update this file with evidence. If full-window data cannot be obtained, say so ONLY after executing every acquisition attempt in Phase B and documenting exact results — do not substitute fixture/probe runs for evidence, and never fabricate or "fill" market data.

---

## 1) Verified current state (facts)

- **Spec:** `research_state/strategy_spec.md`, `crash-rebound-strategy.pdf` (283d window `2025-12-20T00:00:00Z` → `2026-09-28T23:00:00Z`, 6792 hourly bars/symbol, universe = HL perps with ≥$5M 24h volume, one position/coin, buys+shorts capped 120% of vault w/ equal-share cuts, ETH hedges, 20s slicing/order-book impact described in spec).
- **Implementation present:** `src/strategy/*`, `src/backtest/engine.py` (hourly sim, fees/funding/liquidation checks as implemented), `src/data/provenance.py`, `scripts/fetch_hyperliquid_candles.py` (archive/API ingest + provenance, parquet supported), `scripts/run_portfolio.py`, `scripts/run_real_campaign.py` (fail-closed gates), `scripts/run_campaign.py` (fixture smoke only).
- **Test suite green (2026-11-13):** `PYTHONPATH=. python -m pytest -q` → **905 passed, 12 skipped** (parquet tests skip only when pyarrow absent; pyarrow 26.0.1 now installed in this environment).
- **Fixture smoke (NOT evidence):** `python scripts/run_campaign.py` → `research_state/campaign_results.json` with `research_status: "SMOKE_TEST_ONLY"`, `real_market_data=false`, synthetic fixtures.
- **Real full-window run correctly blocked:** `python scripts/run_real_campaign.py` exits non-zero without complete, verified, non-synthetic provenance for the required symbols/window.

## 2) Phase A RESOLVED (2026-11-13) — canonical BTC/ETH archive is DEFINITIVELY SYNTHETIC

- **Evidence:** `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` (sha256 `e0e783f64f0ee18aabc8b490da56d2750396b21b3d99d55d63baf000f757c28c`, matches README) contains BTC with **1 distinct close value (60000.0 flat)** and ETH with **1 distinct close value (3000.0 flat)** across all 6792 bars each; volume is constant (BTC 2e9, ETH 1e9 every bar). Read via pyarrow after installing it (`pip install pyarrow`).
- **Conclusion:** the "verified archive lead" is invalid; the earlier synthetic rejection (`flat_series_all_bars_identical`) was correct. The temp-path provenance was a red herring — the data itself is synthetic. **Phase A is closed as INVALID; do not re-litigate it.**
- **Cached “verified” BTC/ETH dataset remains INVALID for evidence:** `research_state/cache/hyperliquid_verified_283d_btceth/provenance.json` (status:error, synthetic).

## 3) API availability mapped (2026-11-13) — full-window hourly data is NOT obtainable from Hyperliquid public API

- Probed `https://api.hyperliquid.xyz/info` `candleSnapshot` directly:
  - `1h` interval: **earliest available candle = `1776528000000` = 2026-04-19T00:00:00Z**; all probes before that (2025-12-20, 2026-03-16, 2026-03-28, 2026-04-04/12 partial) return rows=0 or only from that floor. The spec window's first ~119 days of hourly bars are unavailable via the public API.
  - `1d` interval: full window available (283 daily bars, `1766188800000..1790553600000`) — but the spec requires hourly bars; daily data cannot substitute (no fabrication/approximation allowed).
- **Consequence:** the full 283-day hourly campaign cannot be sourced from the public API in this environment. Acquisition must come from a user-supplied/verifiable archive (see Phase B).

## 4) Real-data partial-window plumbing validation DONE (NOT evidence)

- Ingested real API data: `PYTHONPATH=. python scripts/fetch_hyperliquid_candles.py --source hyperliquid_api --symbols BTC ETH --start 2026-04-19T00:00:00Z --end 2026-09-28T23:00:00Z --cache-dir research_state/cache/hyperliquid_api_partial_20260419_20260928` → BTC/ETH **3912/3912 bars each, status ok, synthetic_check.is_synthetic=false**, manifest `summary.all_complete=true`, `ready_for_real_campaign=true` (for this sub-window only).
- Ran sanctioned partial-not-evidence pipeline: `python scripts/run_real_campaign.py --manifest research_state/cache/hyperliquid_api_partial_20260419_20260928/provenance.json --cache-dir research_state/cache/hyperliquid_api_partial_20260419_20260928 --allow-partial-not-evidence --window-start 2026-04-19T00:00:00Z --window-end 2026-09-28T23:00:00Z --output-prefix campaign_results_real_partial_btceth`
  → `research_state/campaign_results_real_partial_btceth.json`: `research_status: "NOT_EVIDENCE_PARTIAL_UNIVERSE"`, `real_market_data: true`, `performance_evidence: false`, **0 trades** (total_pnl 0, equity flat 100k, vault AUM fee -0.228).
- **0 trades is genuine strategy behavior, not a bug:** config is RSI(21)<20.0 crash trigger + rebound-confirmation candle + regime gate. On the real sub-window BTC min RSI = 17.38 (only 6/3891 bars < 20) and ETH min RSI = 20.61 (0 bars < 20); none of the RSI<20 bars also satisfied the rebound-confirmation/regime gates. Verified by direct RSI computation over the fetched candles.
- **These outputs are plumbing validation ONLY** — not spec evidence, not comparable to spec targets. Full-window data remains the sole gate.

## 5) Remaining critical blockers (priority order)

1. **No verified, non-synthetic, provenance-approved 283-day dataset for the SPEC-RELEVANT UNIVERSE** (all HL perps meeting ≥$5M 24h volume per spec, with documented symbol selection) covering `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z` (6792 bars, gap_count=0, integrity OK, no look-ahead). **This is the sole blocker to real evidence.** Public API cannot supply it (Section 3); a verifiable user-supplied archive is required.
2. **Universe derivation/reconciliation:** spec requires coins with ≥$5M 24h volume over the window; `research_state/universe_verified.json` / `scripts/derive_verified_universe.py` must be grounded in verified full-window data, not assumed.
3. **Execution-realism gap (known, non-blocking for a first real run but must be reported):** implementation is hourly-bar simplified (slippage/funding/liquidation proxies as configured); spec's 20s slicing + L2 order-book impact not reproduced. Any real result must state this limitation explicitly (already surfaced in `execution_realism` block of outputs).

**DO NOT FABRICATE, SYNTHESIZE, OR “FILL” MARKET DATA. DO NOT mark 283d campaign complete without verified provenance and a gated real run. Do not weaken gates (no bypassing `--allow-partial-not-evidence` semantics, no synthetic data relabeled as real).**

---

## 6) Next focus campaign — HEAVY, ORDERED, NON-OPTIONAL

### Phase B — Obtain/ingest VERIFIED full-universe 283-day data (the real gate; the only remaining work)
1. **Exhaust acquisition attempts, documenting each with exact output:**
   - Ask user for a verifiable hourly OHLCV archive covering `2025-12-20..2026-09-28` for the spec universe (see `research_state/DATA_REQUEST_283D_HYPERLIQUID.md`).
   - Check any provided archive passes: schema `symbol,timestamp_ms,open,high,low,close,volume`; 6792/6792 bars/symbol; non-flat OHLCV; real-looking volumes; checksums recorded.
   - Re-verify the public API floor (already proven 2026-04-19) and record it — do not re-probe endlessly.
2. Derive/reconcile the spec universe from verified data (document criteria, symbol list, volume evidence) → update `research_state/universe_verified.json` with provenance.
3. Ingest full universe: `PYTHONPATH=. python scripts/fetch_hyperliquid_candles.py --source archive --input-archive <path> --symbols <...> --start 2025-12-20T00:00:00Z --end 2026-09-28T23:00:00Z` → produce passing provenance (`summary.all_complete=true`, `ready_for_real_campaign=true`, all symbols complete, no synthetic flags).
4. **Do not proceed to claims without this.** If acquisition fails, document precisely what is missing (format, symbols, window) — but keep Phase C prepared (commands ready to fire the moment data lands).

### Phase C — Execute real 283-day campaign & full analysis (once Phase B passes)
1. Run: `PYTHONPATH=. python scripts/run_real_campaign.py --manifest <verified_manifest>`
2. Produce **full metrics** with timestamps/series (not summaries only): equity curve, returns, Sharpe, Sortino, max drawdown (value + start/trough/end timestamps), Calmar, win rate, profit factor, monthly & weekly breakdowns, trade/leg attribution (buys vs rebound shorts vs hedges), exposure/gross-cap utilization, liquidation/funding/fee impacts as available.
3. Persist machine-readable + human-readable outputs under `research_state/` (e.g. `campaign_results_real.json`, metrics CSV/JSON, plots if feasible) with explicit `real_market_data=true`, `performance_evidence=true`, provenance/manifest hash/path, symbol universe, and execution-realism limitations.
4. Compare vs spec context (+81.2% total, +115.2%/yr, -5.4% worst DD, 85 trades: 73 buys/71% win, 12 shorts/83% win) — attribute differences (data/universe/execution model/parameterization) with evidence.
5. Update this `HANDOFF.md`: mark blockers resolved/unresolved with evidence, record exact commands run, artifact paths, and remaining gaps.

### Phase D — Validation hardening (parallel/after C as appropriate)
- Run/extend tests: `PYTHONPATH=. pytest -q` (currently 905 passed / 12 skipped) especially around portfolio reservation/cap cuts, same-bar edge cases, hedge sizing, exits, liquidation/funding accounting.
- Ensure `run_real_campaign.py`/provenance gates cannot be bypassed; add/adjust tests only if they reflect spec-correct, evidence-backed behavior.
- Note: pyarrow 26.0.1 is installed in this environment (was missing; parquet ingest/tests now active).

---

## 7) Key commands & files

- Inspect/ingest: `PYTHONPATH=. python scripts/fetch_hyperliquid_candles.py --help`
- Gated real run: `PYTHONPATH=. python scripts/run_real_campaign.py --manifest <provenance.json>`
- Fixture smoke (not evidence): `PYTHONPATH=. python scripts/run_campaign.py`
- Portfolio sim: `PYTHONPATH=. python scripts/run_portfolio.py`
- Tests: `PYTHONPATH=. pytest -q`
- Provenance/gates: `src/data/provenance.py`
- Data request/checklist: `research_state/DATA_REQUEST_283D_HYPERLIQUID.md`
- Invalid canonical archive (proven synthetic): `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` (+ README)
- Invalid cached “verified”: `research_state/cache/hyperliquid_verified_283d_btceth/provenance.json`
- Real partial-window manifest (valid, non-synthetic): `research_state/cache/hyperliquid_api_partial_20260419_20260928/provenance.json`
- Partial-not-evidence run output: `research_state/campaign_results_real_partial_btceth.json`
- Prior artifacts (fixture): `research_state/campaign_results.json`, `research_state/campaign_metrics.*`

## 8) Definition of “significant progress” for next session
- **Minimum:** Phase B acquisition attempt executed and documented with exact evidence (either verified full-window data ingested to passing provenance, OR a precise, reproducible record of every acquisition attempt and why each failed).
- **Target:** Phase B completed (verified full-universe data + passing provenance) and Phase C real campaign executed with full metrics/artifacts.
- **Unacceptable:** further probe-script churn, fixture-only or partial-window-only reporting presented as progress, re-litigating the closed Phase A, or declaring blockage without actively attempting Phase B acquisition and documenting exact results.

*End of handoff.*