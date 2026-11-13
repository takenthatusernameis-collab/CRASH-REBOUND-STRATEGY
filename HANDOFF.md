# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-13T04:20:00Z
**Supersedes:** 2026-11-13T04:04:39Z edition (Phase E volume-gate reconciliation implemented; full-universe real evidence campaign unblocked but not yet executed).
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).

> **READ FIRST — INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (inferred from repo name `CRASH-REBOUND-STRATEGY`, 2026-11-13T04:20:00Z):**
>
> **Objective:** Produce the first **spec-relevant, multi-coin REAL performance evidence** for the crash-rebound strategy on the verified full OKX 1H archive (62 alts + ETH context), now that the volume-gate bottleneck is resolved.
>
> **What changed since the last handoff (do NOT re-do):**
> - **Phase E COMPLETE (spec-faithful volume-gate reconciliation, 2026-11-13):** Distinguished **universe membership/admission** (point-in-time spec: peak rolling-24h USD volume ≥ $5M over target window) from **per-trade eligibility** (trailing-24h ≥ $5M at each decision bar, enforced unchanged by `generate_signal`/engine).
>   - `scripts/fetch_hyperliquid_candles.py::analyze_symbol_volume_coverage`: now reports `observed_max_24h_usd_volume` and `universe_membership_ok` (peak >= threshold) **in addition** to existing `volume_filter_ok` (all-bars, every bar >= threshold). `volume_filter_ok` is NOT removed.
>   - `scripts/run_real_campaign.py::validate_symbol_volume_coverage`: admits a symbol when `universe_membership_ok`/peak >= threshold (spec universe member) even if some bars are sub-$5M (all-bars false). Strict/all-bars path unchanged. Fails closed when no membership evidence or peak < threshold. Does **not** relax per-trade filtering.
>   - `src/data/provenance.py::_validate_symbol_volume_evidence`: accepts peak/universe-membership evidence for spec-floor validation (enables `require_verified_provenance`/`--require-complete-manifest` flows for admitted members) while remaining fail-closed on sub-peak, missing/unverified evidence, or sub-spec intent; all-bars case still requires observed_min >= floor. This is admission/manifest validation only — **not** permission to trade on sub-$5M bars.
>   - Failing-first tests added: `tests/test_universe_membership_vs_percode_20261113.py` (9 passed) proves: peak>=5M with some sub-$5M bars => `universe_membership_ok` true / `volume_filter_ok` false and admitted; peak<$5M excluded; all-bars case keeps both flags true; legacy all-bars manifests still pass; **no trade eligibility on a sub-$5M decision bar even for an admitted universe member** (`passes_universe_filter`/per-trade trailing-24h gate rejects). Existing volume-intent/threshold/derive tests remain green.
> - **Real data on disk (non-synthetic):** OKX 1H archive for 62 alts, full window `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z` (6792 bars/symbol, gap_count=0) at `research_state/archives/okx_1h_full_20251220_20260928/` with provenance `research_state/cache/okx_1h_full_20251220_20260928/provenance.json` (`all_complete=true`, `ready_for_real_campaign=true`).
> - **Evidence so far (limited/not full spec campaign):** `research_state/campaign_results_real_okx_btceth.json` (BTC/ETH-only, `REAL_MARKET_RUN`, `performance_evidence=true`, 2 trades). `research_state/campaign_results_real_okx_alts_percode.json` is **NOT** spec evidence (`REAL_DATA_PERCODE_SIMULATION`, `performance_evidence=false`) but shows 7 real alt trades / +9281 PnL / rebound-short + liquidation paths fire.
>
> **Mandatory campaign (execute in order; heavy, non-optional):**
> 1. **Phase F — Full-universe real campaign as EVIDENCE:**
>    - Derive universe from the full OKX manifest/cache using `universe_membership_ok`/peak semantics (spec admission) while preserving per-trade point-in-time filtering: `PYTHONPATH=. python scripts/derive_verified_universe.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --output research_state/universe_okx_full_verified.json [--require-complete-manifest --verify-cache-sha256]`. If derive logic still keys off all-bars fields, update it minimally and test-first to admit peak-members (without weakening per-trade gates or synthetic/coverage checks).
>    - Run gated campaign: `PYTHONPATH=. python scripts/run_real_campaign.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --output-prefix campaign_results_real_okx_full [--apply-vault-fees]`.
>    - Persist artifacts with `real_market_data=true`, `performance_evidence=true` (only if full gated run succeeds), provenance hash, universe, and cross-venue limitation stated (`campaign_results_real_okx_full.json` + metrics).
> 2. **Phase G — Full metrics + spec comparison:** equity curve, returns, Sharpe, Sortino, max DD (value + start/trough/end timestamps), Calmar, win rate, profit factor, monthly & weekly breakdowns, trade/leg attribution (buys vs rebound shorts vs hedges), exposure/gross-cap utilization, liquidation/funding/fee impacts. Compare vs spec (+81.2% total, +115.2%/yr, -5.4% worst DD, 85 trades: 73 buys/71% win, 12 shorts/83% win) with evidence-based attribution (cross-venue OKX basis must be stated).
> 3. **Phase H — Hardening & handoff update:** keep `pytest -q` green; ensure gates cannot be bypassed; update this file with exact commands, artifact paths, results, and any remaining gaps.
>
> **Hard prohibitions:** Do **not** fabricate/synthesize/"fill" data. Do **not** relabel per-code/partial/BTC-only runs as full spec evidence. Do **not** remove `volume_filter_ok` (all-bars) or per-trade point-in-time volume filter. Do **not** re-acquire data already on disk. Do **not** re-litigate closed Phase A. Venue basis: OKX is real exchange data but cross-venue vs Hyperliquid spec — state this in evidence.
>
> **This file is the durable handoff.** Continue this campaign; do not treat fixture/probe/partial-only work as evidence.

---
