# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-13T06:09:27Z
**Supersedes:** 2026-11-13T04:20:00Z (Phase E done, Phase F/G artifacts not yet recorded).
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).

> **READ FIRST — INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (inferred from repo `CRASH-REBOUND-STRATEGY`, 2026-11-13T06:09:27Z):**
>
> **Objective:** Turn the existing full-universe real OKX campaign run into **decision-grade, evidence-backed performance analysis and spec comparison**, and harden the pipeline so results are reproducible and cannot be misinterpreted as Hyperliquid-spec-equivalent evidence.
>
> **Current state (do NOT re-do acquisition or re-fabricate):**
> - **Real data present (non-synthetic):** OKX 1H archive `research_state/archives/okx_1h_full_20251220_20260928/` for 62 alts, window `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z` (6792 bars/symbol, gap_count=0), provenance `research_state/cache/okx_1h_full_20251220_20260928/provenance.json` (`all_complete=true`, `ready_for_real_campaign=true`, manifest sha256 `53ad860b...`).
> - **Phase E COMPLETE (spec-faithful volume-gate reconciliation):** universe membership/admission = peak rolling-24h USD volume ≥ $5M over target window (`universe_membership_ok`/`observed_max_24h_usd_volume`) distinct from per-trade eligibility = trailing-24h ≥ $5M at decision bar (enforced unchanged). `volume_filter_ok` (all-bars) retained. Admission/manifest validation accepts peak evidence for spec members; per-trade gates unchanged. Tests: `tests/test_universe_membership_vs_percode_20261113.py` (+ related volume-intent/threshold/derive tests green as of prior session).
> - **Phase F artifacts EXIST (full-universe gated real run):**
>   - Universe: `research_state/universe_okx_full_verified.json` (generated 2026-11-13T05:16:36Z, `min_24h_volume_usd=5,000,000`, 54 selected symbols incl. ETH: AAVE,ADA,ALGO,APT,ARB,AVAX,AXS,BCH,BONK,CHZ,COMP,CRV,DASH,DOGE,DOT,ENJ,ETC,ETH,FET,FIL,FLOW,GALA,HBAR,ICP,INJ,JTO,JUP,KSM,LDO,LINK,LTC,NEAR,OP,ORDI,PEPE,RENDER,SAND,SATS,SEI,SHIB,SNX,SOL,STX,SUI,SUSHI,TIA,TRX,UNI,WIF,WLD,XLM,XRP,XTZ,ZEC).
>   - Campaign: `research_state/campaign_results_real_okx_full.json` (2026-11-13T05:31:58Z, `run_type=real_market_campaign`, `research_status=REAL_MARKET_RUN`, `real_market_data=true`, `performance_evidence=true`, `fabricated_data=false`, `partial_universe_not_evidence=false`, 54 symbols loaded/complete, `num_trades=8`, `total_pnl=9159.6919`).
>   - Metrics: `research_state/campaign_results_real_okx_full_metrics.json` (+ CSV) — `equity_start=100000`, `equity_final=109159.6919`, gross/net pnl `9159.69/8141.29`, fees `aum 2.15 + profit_share 1016.26 = 1018.40`, `equity_total_return_pct=9.1597`, `equity_annualized_return_pct=22.5995`, `equity_max_drawdown_pct=-2.0275` (val `-2091.61`, ts `1769551200000`), `sharpe 0.6258`, `sortino 1.2618`, `calmar 4.3793`, `win_rate 0.5`, `profit_factor 5.2335`, trades 8 (wins/losses 4/4), legs: buy trades 8 (wins 4, pnl share 81.36%, total_pnl 7452.75) + short trades 1 (target_rebound_short, pnl 2988.22 attributed in by-leg but leg_breakdown shows short total_pnl 0/wins 0 — **investigate/report this attribution inconsistency from artifacts as-is**), exit reasons: `time_exit 6, liquidated 1, target_rebound_short 1`, symbols traded: SOL(3), BCH(2), ETH(1), LINK(1), AVAX(1). Monthly: 4 positive / 3 negative / 0 flat (7 buckets). **Venue limitation:** OKX 1H archive used as real exchange data; strategy spec/test basis is Hyperliquid — cross-venue differences must be stated in any evidence claim.
>
> **Mandatory next campaign (heavy, evidence-first; execute in order):**
> 1. **Phase G+ — Spec-vs-actual performance analysis (primary):**
>    - Produce a durable analysis artifact (e.g. `research_state/real_okx_full_spec_comparison.md` and/or JSON summary) comparing realized OKX full-run metrics to spec targets: spec Hyperliquid test (2025-12-20..2026-09-28, 283d) `+81.2% total`, `+115.2%/yr`, `-5.4% worst DD`, `6/10 months gain`, `85 trades (73 buys 71% win, 12 shorts 83% win)`; rebound short ~27% profit contribution. Contrast with actual (9.16% total, 22.60% ann., -2.03% DD, 8 trades, 4/3 months, 54-symbol universe). Do **not** claim equivalence.
>    - **Explain divergence with evidence only:** quantify trade frequency gap (8 vs 85), universe actually traded vs admitted (5 traded of 54), leg/exit mix, exposure/gross-cap utilization if derivable from `equity_curve`/trades, and any data/venue/timing/signal differences observable in artifacts/code. Investigate and document the short-leg attribution discrepancy noted above (by-leg shows short pnl +2988.22 but `leg_breakdown` short total_pnl 0) by tracing metric computation in code/artifacts — fix only if clearly a metrics bug (test-first), else document.
>    - Include explicit statements: "Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; not Hyperliquid performance evidence."
> 2. **Phase H — Reproducibility & hardening:**
>    - Confirm full test suite is green (`PYTHONPATH=. python3 -m pytest -q`) and record outcome. A prior attempt in this session was started but not confirmed to completion here; treat as **unknown/pending verification** until run to completion.
>    - Verify derive/campaign commands are reproducible from on-disk manifest/cache/universe and that `volume_filter_ok` (all-bars) and per-trade point-in-time gates remain enforced; no gate bypass, no synthetic/fabricated data paths.
>    - If any metrics/attribution bug is found, add failing-first regression tests and fix minimally.
> 3. **Phase I — Update this HANDOFF** with exact commands run, test counts, artifact paths/hashes, analysis conclusions, and the next highest-value heavy work (e.g. sensitivity/reruns, Hyperliquid-native data acquisition plan if required for true spec parity — but **do not invent data**; any acquisition must be real/provenanced per `DATA_REQUEST_283D_HYPERLIQUID.md`).
>
> **Canonical commands/artifacts (on disk):**
> - Derive universe: `PYTHONPATH=. python scripts/derive_verified_universe.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --output research_state/universe_okx_full_verified.json`
> - Real campaign: `PYTHONPATH=. python scripts/run_real_campaign.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --output-prefix campaign_results_real_okx_full`
> - Key artifacts: `research_state/universe_okx_full_verified.json`, `research_state/campaign_results_real_okx_full.json`, `research_state/campaign_results_real_okx_full_metrics.{json,csv}`, `research_state/cache/okx_1h_full_20251220_20260928/provenance.json`, archives in `research_state/archives/okx_1h_full_20251220_20260928/`.
>
> **Hard prohibitions:** Do **not** fabricate/synthesize/"fill" data. Do **not** relabel per-code/partial/BTC-only runs as full spec evidence. Do **not** remove `volume_filter_ok` (all-bars) or per-trade point-in-time volume filter. Do **not** re-acquire data already on disk. Do **not** claim Hyperliquid performance parity from OKX data. Do **not** re-litigate closed Phase A.
>
> **This file is the durable handoff.** Next agent must start with Phase G+ analysis from existing real artifacts and leave an updated, evidence-backed handoff.

---
