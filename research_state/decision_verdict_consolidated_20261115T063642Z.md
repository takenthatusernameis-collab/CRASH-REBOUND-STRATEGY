# Consolidated Decision Verdict — Crash-Rebound Strategy (C8)

**Generated (UTC):** 2026-11-15T06:36:42Z
**Scope:** C1–C7 complete; C8 steps 2a/2b complete; C8 step 4 (Hyperliquid-native operator archive) not available.
**Verdict:** **NO_GO** (cross-venue edge not established; Hyperliquid-native evidence absent). `GO` is possible only if a verified Hyperliquid-native archive later clears all stop/go criteria under C6-T3 + C7 batteries.

## Executive summary

Cross-venue multi-year evidence (OKX, Binance UM; 2023-01-01..2026-09-28, ~3.38y, ~32,808 hourly bars/symbol) produces positive point estimates but **fails decision-grade validation**:

- **Dependence-aware inference (C6-T3):** OKX and Binance episode-block bootstrap 95% CIs straddle zero; temporal/permutation/placebo signals are weak/underpowered. Verdict: `underpowered` on both venues.
- **Robustness/fragility (C7):** on both venues the **core buy leg is negative** while totals are carried by the optional rebound-short leg; results are concentrated (notably 2025 / single episodes can flip sign), and cost/entry stress can flip totals negative (OKX grid: slippage 5× and spec-literal next-open negative; buy leg negative in all 11 variants). Verdict: `FRAGILE_NOT_DECISION_GRADE` on both venues.
- **Fragility appears venue-universal across the two independent cross-venue chains, not OKX-specific.**
- **No Hyperliquid-native decision-grade evidence exists.** Public Hyperliquid retention is a decaying partial tail (~3,876/6,792 bars at last probes); retained partial chain yielded 0 confirmed signals/0 trades on canonical path. Placeholder parquet is non-evidence.

**Cross-venue evidence is NOT Hyperliquid evidence** (`is_hyperliquid_venue_data=false` binding). Do not quote PDF +115%/yr or cross-venue annualized returns as validated edge.

## Evidence map (artifacts)

| Track | Artifact(s) | Key facts |
|---|---|---|
| OKX multi-year campaign (canonical, cross-venue) | `research_state/campaign_results_real_okx_multiyear.json` | 42 trades; +18,220.86 PnL; +18.22%; +5.07%/yr; max DD −33.57%; Sharpe 0.10; win 50%; PF 1.33; 19 episodes / 23 crash days |
| Binance UM multi-year campaign (cross-venue) | `research_state/campaign_results_real_binance_um_multiyear.json` | 42 trades; +21,994.06 PnL; +21.99%; +6.03%/yr; max DD −32.41%; Sharpe 0.10; win 48%; PF 1.37; 19 episodes / 23 crash days |
| OKX C6-T3 episode edge | `research_state/episode_edge_okx_multiyear.{json,md}` (2026-11-15T00:35:31Z, sha e.g. inputs in artifact) | Verdict `underpowered`; episode-block bootstrap 95% CI **[−50,660.49, +99,295.03]**, P(>0)=0.6649; temporal-edge permutation p=0.1000 (canonical percentile 90%) |
| OKX C6-T3 placebo | `research_state/placebo_portfolio_okx_multiyear.{json,md}` (2026-11-15T00:35:50Z) | Verdict `underpowered`; p(placebo ≥ canonical)=0.4000; P(total>0)=0.90 (placebo mean/median positive but wide) |
| OKX C7 robustness | `research_state/multiyear_robustness_battery_full_20261115T011700Z.{json,md}`, `research_state/multiyear_robustness_grid_20261115T013200Z.{json,md}` | Verdict **`FRAGILE_NOT_DECISION_GRADE`**; buy leg **−27,836.64** (30), short **+46,057.50** (12); components coin −28,557.90 / hedge +59,980.18 / rebound-short −25,157.11 / rebound-hedge +30,426.71; exits liq −44,947.31 (12), time +17,110.67 (18), target_rebound_short +46,057.50 (12); sub-period 2023 −17,994 / 2024 −15,575 / 2025 +42,630 / 2026 +9,160; LOO drop-2025 → −24,409.53 (sign flip), drop-ep14 → −11,286; t=0.477; ~320 episodes for CI>0; power 7.6% @ n=19. Grid (11 variants): baseline +18,220.86; slippage 5× **−13,976.73**; funding 2× +21,266.94; spec-literal next-open **−55,057.45** (113 trades); RSI25 +14,608.93; RSI15 **−8,703.37** (6); target 5% +5,983.67; target 12% +12,449.16; time 24h +2,182.33; time 72h +20,827.22; slippage 2× +8,846.58. **Buy leg negative in every variant.** |
| Binance C6-T3 episode edge (C8-2a) | `research_state/episode_edge_binance_um_multiyear.{json,md}` (2026-11-15T06:05:21Z) | Verdict `underpowered`; episode-block bootstrap 95% CI **[−57,363.40, +122,139.16]**, P(>0)=0.65425 (n_episodes=19); temporal-edge permutation p_null_ge_canonical=0.1850 (200 draws, seed 20261114) |
| Binance C7 robustness (C8-2b) | `research_state/multiyear_robustness_battery_binance_um.{json,md}` (2026-11-15T06:29:02Z) | Verdict **`FRAGILE_NOT_DECISION_GRADE`**; buy leg **−36,077.66** (28), short **+58,071.73** (14); total +21,994.06; (full per-leg/sub-period/LOEO/cost-stress details in artifact) — confirms buy-leg-negative, short-leg-carried fragility on independent venue |
| OKX 283d canonical (cross-venue) | `research_state/campaign_results_real_okx_full.json`, `episode_edge_okx_full.json` | 8 trades; +9,159.69; 4 crash episodes / 5 days; `underpowered` (prior, shorter window) |
| Hyperliquid status | `research_state/hyperliquid_retention_probe.json` (2026-11-15T00:42:24Z), `research_state/hyperliquid_acquisition_status.json` | Max ~3,874/6,792 bars; earliest 2026-04-20T14:00Z; verdict `FULL_283D_BLOCKED_BY_API_RETENTION`; partial chain 24×3,885 bars, 11 RSI crashes / 0 confirmed signals, 4 crash days; **no Hyperliquid-native campaign evidence** |
| Archives/provenance | `research_state/archives/okx_1h_multiyear_20230101_20260928/SOURCE.json`, `.../binance_um_1h_multiyear_20230101_20260928/SOURCE.json` | Real, gap-free, `fabricated_data=false`, `is_hyperliquid_venue_data=false` |

## Stop/Go criteria mapping (7 criteria)

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | Hyperliquid-native real-data coverage sufficient for spec window / decision-grade sampling | **FAIL** | Retention probe blocks full 283d; partial chain has 0 confirmed signals; no operator archive ingested (`ACCEPT_AS_EVIDENCE_CANDIDATE` absent). |
| 2 | Dependence-aware edge excludes zero with adequate power (episode-block bootstrap / permutation) | **FAIL (underpowered)** | OKX CI [−50.7k,+99.3k] P>0 0.665, perm p 0.10; Binance CI [−57.4k,+122.1k] P>0 0.654, perm p 0.185. Neither CI excludes zero; n=19 episodes far below ~320 needed (OKX C7). |
| 3 | Portfolio/placebo does not explain away but edge is distinguishable and robust | **FAIL (underpowered/inconclusive)** | OKX placebo p(placebo≥canonical)=0.40 (wide). No decisive separation. |
| 4 | Core (buy-leg) economics positive and not dominated by optional short leg | **FAIL** | OKX buy −27,837 vs short +46,058; Binance buy −36,078 vs short +58,072. Buy leg negative on both venues and in every OKX grid variant. |
| 5 | Stability across sub-periods / not driven by single year or episode | **FAIL** | OKX: 2023/2024 negative, 2025 +42.6k; drop-2025 flips total to −24.4k; drop episode 14 flips to −11.3k. Concentrated gains. |
| 6 | Robust to reasonable cost/funding/entry/parameter stress | **FAIL** | OKX: slippage 5× → −13.98k; spec-literal next-open → −55.06k (113 trades); RSI15 → −8.70k. Buy leg negative across all 11 configs. |
| 7 | Cross-venue result transferable to Hyperliquid as validated edge | **FAIL** | Evidence is `CROSS_VENUE_MULTIYEAR_NOT_HYPERLIQUID` (`is_hyperliquid_venue_data=false`); microstructure/liquidity/funding/venue mechanics differ. Cannot be promoted to Hyperliquid edge. |

**Overall:** 0/7 pass for a positive/GO claim. Cross-venue verdict is **NO_GO / edge not established and fragile**.

## Decision

- **`NO_GO`** on claiming a validated crash-rebound edge from available evidence.
- **Fragility is not OKX-specific:** Binance UM reproduces the same qualitative failure mode (underpowered dependence-aware inference; buy-leg negative, short-leg-carried, fragile totals).
- **Only positive path:** ingest a verified Hyperliquid-native archive (operator-supplied) that passes `scripts/validate_hyperliquid_archive_intake.py` with `ACCEPT_AS_EVIDENCE_CANDIDATE`, then run canonical Hyperliquid campaign + C6-T3 + C7 batteries and re-evaluate all 7 criteria on Hyperliquid-native data.

## Prohibitions / caveats (binding)

- Do not relabel cross-venue (OKX/Binance) results as Hyperliquid evidence.
- Do not fabricate, synthesize, or interpolate data; do not treat placeholder parquet as evidence.
- Do not quote PDF +115%/yr or cross-venue +5.07%/+6.03%/yr as validated edge.
- Do not relax the $5M volume floor or spec-literal opt-in defaults.
- Canonical artifacts above are fixed; do not overwrite without a new stem and documented reason.

## Reproduction (C8 commands executed/required)

```bash
# C8-2a (completed): Binance C6-T3
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_episode_edge_okx_multiyear.py \
  --cache-dir research_state/cache/binance_um_1h_multiyear_20230101_20260928 \
  --universe research_state/universe_binance_um_multiyear_verified.json \
  --census research_state/crash_event_census_real_binance_um_multiyear.json \
  --campaign research_state/campaign_results_real_binance_um_multiyear.json \
  --venue-label "Binance UM" --out episode_edge_binance_um_multiyear

# C8-2b (completed): Binance C7
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_multiyear_robustness_battery.py --phases A B \
  --cache-dir research_state/cache/binance_um_1h_multiyear_20230101_20260928 \
  --universe research_state/universe_binance_um_multiyear_verified.json \
  --campaign research_state/campaign_results_real_binance_um_multiyear.json \
  --census research_state/crash_event_census_real_binance_um_multiyear.json \
  --episode-edge research_state/episode_edge_binance_um_multiyear.json \
  --venue-label "Binance UM" --phase-label "C8-BINANCE" \
  --out multiyear_robustness_battery_binance_um
```

*End of consolidated verdict (C8).*
