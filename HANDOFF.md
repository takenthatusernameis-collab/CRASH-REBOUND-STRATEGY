# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-13T03:29:05Z
**Supersedes:** 2026-11-13T03:04:38Z edition (data-acquisition blocker resolved this session; campaign advanced to real evidence on OKX real data).
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).

> **READ FIRST — INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (inferred from repo name `CRASH-REBOUND-STRATEGY`, 2026-11-13T03:29:05Z):**
>
> **Objective:** Produce the first **spec-relevant, multi-coin REAL performance evidence** for the crash-rebound strategy, and reconcile the one remaining provenance bottleneck.
>
> **What changed since the last handoff (do NOT re-do):**
> - The prior "sole blocker" (no real full-window hourly data obtainable) is **RESOLVED**. Real, non-synthetic **OKX 1H** OHLCV was acquired for **62 altcoins + BTC/ETH** across the full spec window `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z` (6792 bars/symbol, gap_count=0, non-flat, varied signatures). Provenance manifest: `research_state/cache/okx_1h_full_20251220_20260928/provenance.json` (`all_complete=true`, `ready_for_real_campaign=true`, 62/62 symbols `status=ok`). Archive: `research_state/archives/okx_1h_full_20251220_20260928/`. Acquisition script: `scripts/acquire_exchange_archive.py` (OKX `history-candles`, deterministic, idempotent).
> - **Canonical full-evidence BTC/ETH campaign is DONE** (only BTC/ETH clear the strict whole-window-min volume gate): `research_state/campaign_results_real_okx_btceth.json` → `research_status=REAL_MARKET_RUN`, `performance_evidence=true`, `real_market_data=true`, 2 trades, total_pnl ≈ +1646, Sharpe 0.77, Sortino 3.43, maxDD -240, win_rate 0.5, profit_factor 7.85. Both exits were `time_exit` (RSI<20 crash signals are rare on BTC/ETH in this window).
> - **Real alt behavior captured (NOT spec evidence):** `scripts/run_real_alts_percode_simulation.py` runs all 62 alts + ETH through the real engine with the spec point-in-time (≥$5M trailing-24h at decision) filter → `research_state/campaign_results_real_okx_alts_percode.json` (honestly labeled `REAL_DATA_PERCODE_SIMULATION`, `performance_evidence=false`). **Result: 7 real trades, total_pnl ≈ +9281, win_rate 0.57, profit_factor 5.55, Sharpe 0.70, Sortino 1.27, maxDD -1970.** Includes a `target_rebound_short` (BCH) and a real `liquidated` exit (SOL) — proving the rebound-short and liquidation paths fire on real data. This proves the strategy trades meaningfully on real alt data (vs only 2 BTC/ETH trades).
>
> **Sole remaining bottleneck (the heavy work for this session):**
> The manifest volume gate `volume_filter_ok` requires **EVERY hourly bar's trailing-24h USD volume ≥ $5M across the whole 283-day window** (`analyze_symbol_volume_coverage` in `scripts/fetch_hyperliquid_candles.py`; consumed by `validate_symbol_volume_coverage` in `scripts/run_real_campaign.py`). Even liquid alts (SOL, XRP, DOGE) dip below $5M in some hours, so **only BTC/ETH clear it** — this blocks a spec-relevant multi-alt **full-evidence** campaign. The spec's actual rule is **point-in-time** ("coins that traded ≥ $5M in last 24h" at decision), which the engine already enforces per bar via `StrategyConfig.min_daily_volume_usd` + `generate_signal`. The whole-window-min manifest gate is stricter than the spec.
>
> **Mandatory campaign (execute in order; heavy, non-optional):**
> 1. **Reconcile the volume gate to the spec (Phase E — THE task):** Distinguish **universe membership** from **per-trade eligibility**. Add `universe_membership_ok = (peak rolling-24h USD volume ≥ $5M)` (spec universe filter) alongside the existing all-bars `volume_filter_ok`. Make the campaign universe gate accept `universe_membership_ok` for admission while the per-decision-bar `generate_signal` continues to enforce point-in-time ≥$5M eligibility (no look-ahead, no relaxation of per-trade filtering). **Add failing-first tests** proving: (a) an alt with peak ≥$5M but some sub-$5M hours is admitted as a universe member; (b) a symbol with peak <$5M is excluded; (c) no trade opens during a sub-$5M bar. This is a spec-faithful correction, NOT a gate weakening — do not remove the all-bars flag or the per-trade filter.
> 2. **Run the full-universe real campaign as evidence (Phase F):** After Phase E + `PYTHONPATH=. pytest -q` is green, run `PYTHONPATH=. python scripts/run_real_campaign.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file <derived_universe>` and persist `performance_evidence=true` artifacts.
> 3. **Full metrics + spec comparison (Phase G):** equity curve, returns, Sharpe, Sortino, max DD (value + timestamps), Calmar, win rate, profit factor, monthly/weekly, trade/leg attribution (buys/shorts/hedges), exposure/cap utilization, funding/fee/liquidation impacts; compare vs spec (+81.2% total, +115.2%/yr, -5.4% worst DD, 85 trades: 73 buys/71% win, 12 shorts/83% win) with evidence-based attribution (cross-venue OKX basis must be stated).
> 4. **Harden & update (Phase H):** keep `pytest -q` green (currently 916 passed / 1 skipped); update this HANDOFF with resolved/unresolved items, exact commands, artifact paths, gaps.
>
> **Hard prohibitions:** Do **not** fabricate/synthesize/"fill" data. Do **not** relabel the per-code alt simulation or partial runs as spec evidence. Do **not** remove the all-bars `volume_filter_ok` flag or the per-trade point-in-time volume filter (the reconciliation ADDS `universe_membership_ok`; it does not delete safety). Do **not** re-litigate closed Phase A (canonical archive proven synthetic). Do **not** declare blockage without attempting Phase E.
>
> **This file is the durable handoff.** Continue this campaign; do not treat fixture/probe/partial-only work as evidence.

---

## 1) Verified current state (facts, 2026-11-13T03:29:05Z)

- **Spec:** `research_state/strategy_spec.md`, `crash-rebound-strategy.pdf` (283d window `2025-12-20T00:00:00Z`→`2026-09-28T23:00:00Z`, 6792 hourly bars/symbol, universe = perps with ≥$5M 24h volume, one position/coin, buys+shorts capped 120% of vault w/ equal-share cuts, ETH hedge every leg, hourly funding/liquidation, 20s slicing/order-book impact described in spec).
- **Implementation present:** `src/strategy/*`, `src/backtest/engine.py`, `src/data/provenance.py`, `scripts/fetch_hyperliquid_candles.py`, `scripts/acquire_exchange_archive.py`, `scripts/run_portfolio.py`, `scripts/run_real_campaign.py` (fail-closed gates), `scripts/run_campaign.py` (fixture smoke), `scripts/run_real_alts_percode_simulation.py`.
- **Test suite green:** `PYTHONPATH=. python -m pytest -q` → **916 passed, 1 skipped**.
- **Real data (NEW, non-synthetic):** OKX 1H archive for 62 alts + BTC/ETH, full window, provenance manifest `research_state/cache/okx_1h_full_20251220_20260928/provenance.json` (all_complete=true, ready_for_real_campaign=true). BTC/ETH also in `research_state/cache/okx_smoke/provenance.json`.
- **Canonical BTC/ETH real campaign DONE:** `research_state/campaign_results_real_okx_btceth.json` (REAL_MARKET_RUN, performance_evidence=true).
- **Alt per-code simulation (real data, NOT evidence):** `research_state/campaign_results_real_okx_alts_percode.json` (REAL_DATA_PERCODE_SIMULATION).

## 2) Phase A RESOLVED — canonical BTC/ETH archive is DEFINITIVELY SYNTHETIC (do not re-litigate)

- `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` (sha256 `e0e783f6…`) has BTC 1 distinct close (60000.0 flat), ETH 1 distinct close (3000.0 flat), constant volume — synthetic. Invalid for evidence.
- `research_state/cache/hyperliquid_verified_283d_btceth/provenance.json` (status:error, synthetic) — invalid.

## 3) Data acquisition — RESOLVED this session (2026-11-13)

- Hyperliquid public API `candleSnapshot` `1h` earliest candle = `2026-04-19T00:00:00Z` (first ~119 days unavailable). Cannot supply the full window.
- **OKX public REST `GET /api/v5/market/history-candles` (`bar=1H`) supplies the full window** (no key). `scripts/acquire_exchange_archive.py` downloaded 62 alts + BTC/ETH, 6792/6792 bars each, gap_count=0, `synthetic_check.is_synthetic=false`, `SOURCE.json` written, `all_complete=true`.
- **Venue basis:** OKX candles are REAL exchange-published OHLCV but are **cross-venue proxies** for the Hyperliquid-denominated spec. Document this whenever comparing to spec targets. This is the acceptable real-data path in this environment.

## 4) Volume-gate bottleneck (THE remaining blocker)

- `analyze_symbol_volume_coverage` (fetch script) computes per-bar trailing-24h USD volume (`volume*close`) and sets `volume_filter_ok = (bars_passing == bars_checked)` → requires EVERY bar ≥ $5M.
- `validate_symbol_volume_coverage` (run_real_campaign) fails the whole run if any universe symbol's `volume_filter_ok` is false.
- Result: only BTC (min24h $6.67M) and ETH ($7.49M) pass. All 62 alts fail (e.g. SOL min $1.26M, XRP $1.81M, DOGE $1.81M) despite mean 24h volumes of $40–80M.
- Spec universe is **point-in-time** (≥$5M at decision); engine already enforces this per bar. The whole-window-min manifest gate is over-strict relative to spec.

## 5) Next focus campaign — HEAVY, ORDERED, NON-OPTIONAL

### Phase E — Reconcile volume gate to spec (with tests) — PRIMARY
1. In `scripts/fetch_hyperliquid_candles.py::analyze_symbol_volume_coverage`, add `universe_membership_ok = (max rolling-24h USD volume >= $5M)` (peak, not all-bars). Keep `volume_filter_ok` (all-bars) unchanged for strict callers.
2. In `scripts/run_real_campaign.py::validate_symbol_volume_coverage`, admit a symbol to the universe when `universe_membership_ok` is true (spec membership), while per-trade eligibility stays enforced by `generate_signal` (point-in-time). Do not relax per-trade filtering.
3. Add failing-first tests (new file, e.g. `tests/test_universe_membership_vs_percode_20261113.py`): (a) peak≥$5M + some sub-$5M hours → admitted; (b) peak<$5M → excluded; (c) no trade opens on a sub-$5M bar; (d) all-bars flag still present/true only when every bar passes.
4. `PYTHONPATH=. pytest -q` must stay green (916+ passed).
5. Document the change in this HANDOFF with before/after semantics and the spec citation.

### Phase F — Full-universe real campaign as EVIDENCE (once E green)
1. Derive the universe: `PYTHONPATH=. python scripts/derive_verified_universe.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --output research_state/universe_okx_full_verified.json` (update it to use `universe_membership_ok` per Phase E).
2. Run: `PYTHONPATH=. python scripts/run_real_campaign.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --apply-vault-fees`.
3. Persist `campaign_results_real_okx_full.json` (+ metrics JSON/CSV) with `real_market_data=true`, `performance_evidence=true`, provenance hash, universe, cross-venue limitation.

### Phase G — Full metrics + spec comparison
- equity curve, returns, Sharpe, Sortino, max DD (value + start/trough/end timestamps), Calmar, win rate, profit factor, monthly & weekly breakdowns, trade/leg attribution (buys vs rebound shorts vs hedges), exposure/gross-cap utilization, liquidation/funding/fee impacts.
- Compare vs spec (+81.2% total, +115.2%/yr, -5.4% worst DD, 85 trades: 73 buys/71% win, 12 shorts/83% win); attribute differences (cross-venue OKX basis, execution model, universe) with evidence.

### Phase H — Hardening & handoff update
- `PYTHONPATH=. pytest -q` green; ensure gates cannot be bypassed; update this file.

## 6) Key commands & files

- Acquire OKX archive: `python scripts/acquire_exchange_archive.py --venues okx --symbols <...> --start 2025-12-20T00:00:00Z --end 2026-09-28T23:00:00Z --out research_state/archives/<name>`
- Ingest archive → provenance: `PYTHONPATH=. python scripts/fetch_hyperliquid_candles.py --source archive --input-archive research_state/archives/<name> --symbols <...> --start 2025-12-20T00:00:00Z --end 2026-09-28T23:00:00Z --cache-dir <cache>`
- Derive universe: `PYTHONPATH=. python scripts/derive_verified_universe.py --manifest <provenance.json> --cache-dir <cache> --output <universe.json> --require-complete-manifest --verify-cache-sha256`
- Gated real run: `PYTHONPATH=. python scripts/run_real_campaign.py --manifest <provenance.json> --cache-dir <cache> [--universe-file <u.json>] [--apply-vault-fees]`
- Alt per-code sim (real data, NOT evidence): `python scripts/run_real_alts_percode_simulation.py`
- Fixture smoke (not evidence): `python scripts/run_campaign.py`
- Tests: `PYTHONPATH=. pytest -q`

**Artifacts:**
- Full OKX archive (62 alts): `research_state/archives/okx_1h_full_20251220_20260928/` (+ `SOURCE.json`)
- Provenance manifest (62 alts): `research_state/cache/okx_1h_full_20251220_20260928/provenance.json`
- BTC/ETH provenance: `research_state/cache/okx_smoke/provenance.json`
- BTC/ETH real evidence: `research_state/campaign_results_real_okx_btceth.json` (+ `_metrics.json/.csv`)
- Alt per-code sim: `research_state/campaign_results_real_okx_alts_percode.json` (+ `_metrics.csv`)
- Strict BTC/ETH universe file: `research_state/universe_btceth_strict.json`
- Invalid synthetic (Phase A, do not use): `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet`, `research_state/cache/hyperliquid_verified_283d_btceth/`
- Prior fixture smoke (not evidence): `research_state/campaign_results.json`, `research_state/campaign_metrics.*`

## 7) Definition of "significant progress" for next session

- **Minimum:** Phase E implemented with failing-first tests proving universe-membership vs per-code distinction, `pytest -q` green, and this HANDOFF updated with the exact diff/semantics.
- **Target:** Phase E + Phase F done → full-universe OKX campaign with `performance_evidence=true` and full metrics (Phase G).
- **Unacceptable:** re-acquiring data already on disk, re-litigating closed Phase A, presenting the per-code alt sim or BTC/ETH-only run as the full spec campaign, or weakening/removing the all-bars or per-trade volume filters.

*End of handoff.*