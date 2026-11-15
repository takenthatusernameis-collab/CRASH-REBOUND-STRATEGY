# Consolidated Decision Verdict — C11.3 Final (Native Hyperliquid + Cross-Venue OKX/Binance)

**Generated (UTC):** 2026-11-15T15:56:35Z
**Scope:** C1–C10 complete (cross-venue OKX + Binance UM); **C11.3 COMPLETE** (Hyperliquid-native 283d Ironflow node-derived archive verified and full C6-T1, C6-T3, C7, and C10.2 battery executed).
**Supersedes for C11.3 additions:** cites and finalizes `research_state/decision_verdict_consolidated_20261115T122636Z.md`, `research_state/decision_verdict_consolidated_20261115T064738Z.md`, and `research_state/decision_verdict_consolidated_20261115T063642Z.md`. Do not overwrite prior canonical stems.
**Provenance:**
- **Native Hyperliquid chain (`is_hyperliquid_venue_data=true`, `is_hyperliquid_evidence=true`):** Real Hyperliquid 1h OHLCV (`ironflow/hyperliquid-candles-1h`, CC BY 4.0, 5 symbols `BTC/ETH/HYPE/SOL/ZEC`, `2025-12-20T00:00:00Z .. 2026-09-28T23:00:00Z`, 6,792 hourly bars/symbol) verified in `research_state/archives/hyperliquid_ironflow_1h_20251220_20260928/hyperliquid_native_1h_20251220_20260928.parquet`. Node-derived from Ironflow HF (NOT Hyperliquid `candleSnapshot` REST API).
- **Cross-venue chains (`is_hyperliquid_venue_data=false`):** OKX 283d & multi-year (`2023-01-01 .. 2026-09-28`) and Binance UM multi-year (`2023-01-01 .. 2026-09-28`).

## 1. C11.3 Native Hyperliquid Artifacts (Completed This Session)
- **C6-T1 Reconciled Crash Census:**
  - `research_state/crash_event_census_hyperliquid_ironflow_native_20261115T155226Z.{json,md}` (`sha256: 47bb04b9ebb0bc54440d90bd007892a99675dd6f72be79e3a721e29c7b074b73`)
  - `research_state/campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json` (`sha256: f90d18eed27263b1edf918346865b6fb1f4be849e5a8ba39750d1971c7470665`)
  - Reconciles all **43** RSI(21)<20 crash events and all **6** canonical portfolio trades (`matched=6`, `unexplained=0`; `36 bounce_not_confirmed`, `1 one_position_per_coin`, `6 trade_opened`).
- **C6-T3 Crash-Episode Dependence & Conditional Permutation:**
  - `research_state/episode_edge_hyperliquid_native_20261115T155318Z.{json,md}`
  - **3 episodes**, **4 distinct crash days**, **3 traded symbols** (`BTC`, `ETH`, `SOL`). Episode totals: `Ep 0 = +$3,446.47`, `Ep 1 = -$381.22`, `Ep 2 = +$1,227.25`.
  - Episode-block bootstrap (20,000 resamples): 95% CI **`[-1,143.66, +10,339.42]`**, `P(total>0) = 0.9624`.
  - Conditional temporal-edge permutation (200 draws, 43 eligible RSI<20 bars): null mean `+$1,882.19`, observed `+$4,292.50` at 92.0th percentile, **`p_null_ge_canonical = 0.0800`**, **`verdict = underpowered`**.
- **C10.2-HL Exact Full-Portfolio Placebo:**
  - `research_state/placebo_portfolio_hyperliquid_native_20261115T155625Z.{json,md}`
  - Exact enumeration of all $\binom{7}{6} = 7$ subsets of gate-passing signals (`mode = exact_enumeration:7_choose_6_of_7`).
  - Placebo distribution: mean `+$4,211.38`, median `+$4,414.12`, 95% CI `[+2,751.97, +5,278.71]`, `P(placebo > 0) = 1.0000`.
  - Canonical `+$4,292.50` sits at the 42.86th percentile (**`p_ge_canonical = 0.7143`**, 5/7 subsets >= canonical), **`verdict = underpowered`**.
- **C7-HL Full Robustness, Fragility & Achievable-Power Battery (Phases A + B):**
  - `research_state/multiyear_robustness_battery_hyperliquid_native_20261115T155522Z.{json,md}`
  - **Leg decomposition:** Spot `coin_pnl = -$3,968.80` (LOSS), `hedge_pnl = +$8,261.31` (ETH short hedge gain), `rebound_short_pnl = $0.00` (0 trades at `target_pct=9%`), net `total_pnl = +$4,292.50`.
  - **Phase B Stress & Sensitivity (10 variants):**
    - `baseline` (RSI<20, target 9%): 6 trades, `+$4,292.50` (`buy = +$4,292.50`, `short = $0.00`; spot = `-$3,968.80`, hedge = `+$8,261.31`).
    - `slippage_2x` (10 bps): 6 trades, `+$3,425.05`.
    - `slippage_5x` (25 bps): 6 trades, **`-$891.35` (NEGATIVE)**.
    - `funding_2x` (2 bps/hr): 6 trades, `+$4,423.81`.
    - `rsi_threshold_15` (RSI<15): 1 trade, **`-$3,266.48` (NEGATIVE)**.
    - `rsi_threshold_25` (RSI<25): **17 trades**, total **`+$23,244.22` (+23.24%)**, with `buy_leg = -$7,084.54`, `hedge_leg = $0.00`, **`short_leg = +$30,328.77` (5 rebound-short trades)**.
    - `target_pct_5` (RSI<20, rebound target 5%): **6 trades**, total **`+$7,596.40` (+7.60%)**, with `buy_leg = +$4,673.72` and **`short_leg = +$2,922.68` (3 rebound-short trades)**.
    - `target_pct_12`: 6 trades, `+$4,292.50` (`short = $0.00`).
    - `time_exit_24`: 6 trades, `+$3,083.41`.
    - `time_exit_72`: 6 trades, `+$1,260.18`.
  - **Verdict:** **`FRAGILE_NOT_DECISION_GRADE`**.

## 2. Integrated Evaluation vs 7 Stop/Go Criteria (C11.3 Update)

| # | Criterion | Status | Evidence (Native Hyperliquid + Cross-Venue) |
|---|---|---|---|
| 1 | Hyperliquid-native real-data coverage for spec window | **PASS (Ironflow node-derived)** | Full 283d (`2025-12-20 .. 2026-09-28`, 6,792 bars/symbol, 5 symbols) verified via Ironflow HF CC BY 4.0 archive; 43/43 crash events and 6/6 trades reconciled (`unexplained=0`). |
| 2 | Dependence-aware edge excludes zero with adequate power | **FAIL (underpowered)** | Native: 3 episodes, 4 crash days; episode-bootstrap 95% CI `[-1,143.66, +10,339.42]`, temporal permutation `p = 0.0800`. OKX/Binance multi-year & pooled 38 episodes also span zero. |
| 3 | Portfolio/placebo distinguishes edge and is robust | **FAIL (underpowered)** | Native exact full-portfolio placebo (all 7 subsets of 6-of-7 gate events): `p_ge_canonical = 0.7143` (canonical 42.9th percentile). OKX (`p = 0.4000`) and Binance (`p = 0.4150`) multi-year placebos likewise sit near median. |
| 4 | Core spot (buy-leg) economics positive, not dominated by hedge/short | **FAIL (native & cross-venue)** | Native RSI<20 spot `coin_pnl = -$3,968.80` (loss); headline `+$4,292.50` is solely from `+$8,261.31` ETH hedge PnL. Even at `rsi_threshold_25` (+$23,244.22 total), spot buy leg loses `-$7,084.54` while rebound-short earns `+$30,328.77`. OKX buy `-27,837` vs short `+46,058`; Binance buy `-36,078` vs short `+58,072`. |
| 5 | Stability across sub-periods / not single cluster or year | **FAIL** | Native: 6/6 trades occur in Jan 2026 across 3 episodes; 0 trades in the remaining 8 months; dropping Ep 0 removes 80.3% of PnL (`+$846.03` left). OKX/Binance: profits concentrated in single years/episodes; LOO flips sign. |
| 6 | Robust to cost/funding/entry/parameter stress | **FAIL** | Native: 5x slippage turns PnL negative (`-$891.35`); `RSI<15` loses `-$3,266.48`; spot leg negative across all RSI<20 runs. OKX/Binance: 5x slippage and spec-literal next-open turn PnL deeply negative. |
| 7 | Cross-venue result transferable to Hyperliquid as validated edge | **FAIL** | Cross-venue OKX/Binance spot losses confirmed on native Hyperliquid (`-$3,968.80` spot PnL under RSI<20). No unconditional GO. |

**Overall:** 1/7 pass (Criterion 1: native data coverage achieved), **0/7 pass for a positive/GO claim on the canonical RSI(21)<20 long-only spot specification**.

## 3. Decision
- **`NO_GO`** on claiming a validated edge for the canonical `RSI(21) < 20` long crash-rebound strategy with `+9%` target (`decision_verdict_hyperliquid_native_20261115T155318Z.md`).
- **Why the canonical strategy failed on native Hyperliquid:** Buying RSI(21)<20 crashes on Hyperliquid (`BTC`, `ETH`, `SOL`) enters after the initial bounce bar and suffers from continued drift/liquidation risk on spot (`-$3,968.80` spot loss), while the mandatory ETH short hedge (`+9%` target never hit on ETH at `RSI<20` in this window) merely offsets the spot drawdown to produce `+$4,292.50` (`+4.29%` over 283d).
- **Major Actionable Discovery from Native Robustness Battery (`C7-HL`):** In the exact same native Hyperliquid dataset, **rebound mean-reversion after sharp crashes is strong when the rebound-short leg is allowed to trigger at `target_pct=5%` (`+$2,922.68` across 3 trades at `RSI<20`, `+$7,596.40` combined portfolio PnL) or when the crash filter is `RSI(21) < 25` (`+$30,328.77` rebound-short PnL across 5 trades, `+$23,244.22` combined portfolio PnL, +23.24% in 283d)**. Furthermore, spot entries at `RSI(21) < 25` with `target_pct=5%` turn positive (`+$4,673.72` spot PnL at `RSI<20, target=5%`).

## 4. Binding Prohibitions & Reproduction Commands
- Do not relabel cross-venue (OKX/Binance) artifacts as Hyperliquid-native evidence.
- Accurately describe Hyperliquid 283d artifacts (`is_hyperliquid_venue_data=true`) as **Ironflow node-derived Hyperliquid candles (CC BY 4.0)**, not `candleSnapshot` REST snapshots.
- Do not overwrite canonical or C11.3 artifacts; use new timestamped stems.

```bash
# C11.3 Full Native Hyperliquid Reproduction Suite
TS=$(date -u +%Y%m%dT%H%M%SZ)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/build_crash_event_census.py \
  --cache-dir research_state/cache/hyperliquid_ironflow_native_20251220_20260928 \
  --universe research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json \
  --campaign research_state/campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json \
  --out "research_state/crash_event_census_hyperliquid_ironflow_native_${TS}"

PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_episode_edge_okx_multiyear.py \
  --draws 200 --seed 20261115 \
  --cache-dir research_state/cache/hyperliquid_ironflow_native_20251220_20260928 \
  --universe research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json \
  --census "research_state/crash_event_census_hyperliquid_ironflow_native_${TS}.json" \
  --campaign research_state/campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json \
  --venue-label "Hyperliquid (Ironflow node-derived, native)" \
  --out "episode_edge_hyperliquid_native_${TS}"

PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_binance_um_multiyear.py \
  --cache-dir research_state/cache/hyperliquid_ironflow_native_20251220_20260928 \
  --universe research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json \
  --census "research_state/crash_event_census_hyperliquid_ironflow_native_${TS}.json" \
  --campaign research_state/campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json \
  --venue-label "Hyperliquid (Ironflow node-derived, native)" \
  --draws 200 --seed 20261115 --jobs 4 \
  --out "placebo_portfolio_hyperliquid_native_${TS}"

PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_multiyear_robustness_battery.py \
  --phases A B \
  --variants baseline slippage_2x slippage_5x funding_2x rsi_threshold_15 rsi_threshold_25 target_pct_5 target_pct_12 time_exit_24 time_exit_72 \
  --cache-dir research_state/cache/hyperliquid_ironflow_native_20251220_20260928 \
  --universe research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json \
  --campaign research_state/campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json \
  --census "research_state/crash_event_census_hyperliquid_ironflow_native_${TS}.json" \
  --episode-edge "research_state/episode_edge_hyperliquid_native_${TS}.json" \
  --venue-label "Hyperliquid (Ironflow node-derived, native)" \
  --phase-label "C7-HYPERLIQUID-NATIVE" \
  --out "multiyear_robustness_battery_hyperliquid_native_${TS}"
```

*End of consolidated verdict (C11.3 final).*