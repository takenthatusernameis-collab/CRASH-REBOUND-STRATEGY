# Hyperliquid-Native Decision Verdict — C11.3 Complete Native Battery (2025-12-20 .. 2026-09-28)

**Generated (UTC):** 2026-11-15T15:56:30Z
**Phase:** C11.3 (Hyperliquid-Native Canonical Campaign + Dependence-Aware Inference + Full Robustness & Placebo Battery)
**Provenance:** Real Hyperliquid-native 1h OHLCV (`ironflow/hyperliquid-candles-1h`, CC BY 4.0, `research_state/archives/hyperliquid_ironflow_1h_20251220_20260928/hyperliquid_native_1h_20251220_20260928.parquet`), non-synthetic. **`is_hyperliquid_evidence=true`, `is_hyperliquid_venue_data=true`, `cross_venue=false`** for all C11.3 native artifacts. Node-derived from Ironflow HF mirror (NOT Hyperliquid `candleSnapshot` REST endpoint), covering all 6,792 hourly bars per symbol across `BTC`, `ETH`, `HYPE`, `SOL`, `ZEC` (`2025-12-20T00:00:00Z .. 2026-09-28T23:00:00Z`, 283.0 days).

## 1. Native Artifacts & SHA-256 Provenance
1. **Native Crash-Event Census (`C6-T1` / `C11.3`):**
   - `research_state/crash_event_census_hyperliquid_ironflow_native_20261115T155226Z.json` (`sha256: 47bb04b9ebb0bc54440d90bd007892a99675dd6f72be79e3a721e29c7b074b73`)
   - `research_state/crash_event_census_hyperliquid_ironflow_native_20261115T155226Z.md`
   - `research_state/campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json` (`sha256: f90d18eed27263b1edf918346865b6fb1f4be849e5a8ba39750d1971c7470665`)
2. **Native Crash-Episode Dependence Audit & Conditional Temporal-Edge Permutation (`C6-T3` / `C11.3`):**
   - `research_state/episode_edge_hyperliquid_native_20261115T155318Z.json`
   - `research_state/episode_edge_hyperliquid_native_20261115T155318Z.md`
   - Episode-block bootstrap: 20,000 resamples (`seed=20261115`); conditional crash-day temporal permutation: 200 draws (`seed=20261115`).
3. **Native Exact Full-Portfolio Placebo (`C10.2-HL` / `C11.3`):**
   - `research_state/placebo_portfolio_hyperliquid_native_20261115T155625Z.json`
   - `research_state/placebo_portfolio_hyperliquid_native_20261115T155625Z.md`
   - Exact enumeration over all $\binom{7}{6} = 7$ subsets of the 7 signal-gate-passing events (`mode=exact_enumeration:7_choose_6_of_7`).
4. **Native Multi-Year Robustness, Fragility & Achievable-Power Battery (`C7-HL` / `C11.3`):**
   - `research_state/multiyear_robustness_battery_hyperliquid_native_20261115T155522Z.json`
   - `research_state/multiyear_robustness_battery_hyperliquid_native_20261115T155522Z.md`
   - Phase A (analytical attribution, sub-period, episode concentration, LOO, achievable power) + Phase B (10 real portfolio-engine config variants).

## 2. Core Native Findings (C11.3)
- **Gate Filtering Funnel (43 events -> 7 signal-gate -> 6 trades):**
  - Out of **43** native crash events (`RSI(21) < 20` across 5 symbols over 283d):
    - **36 blocked by `bounce_not_confirmed`**, **1 blocked by `one_position_per_coin`**.
    - **6 trades opened** across 3 symbols (`BTC`, `ETH`, `SOL`):
      1. `2026-01-19T04:00:00Z` `SOL` buy (`entry=19.330000`, `exit=21.071700`, `exit_reason=liquidated`, `coin_pnl=+475.29`, `hedge_pnl=+1851.76`, `total_pnl=+2327.04`, `+12.01%` on trade capital)
      2. `2026-01-19T05:00:00Z` `ETH` buy (`entry=2805.290000`, `exit=3057.964600`, `exit_reason=liquidated`, `coin_pnl=+691.99`, `hedge_pnl=+1536.06`, `total_pnl=+2228.05`, `+11.10%`)
      3. `2026-01-20T19:00:00Z` `SOL` buy (`entry=20.550000`, `exit=18.700000`, `exit_reason=time_exit`, `coin_pnl=-345.30`, `hedge_pnl=+445.56`, `total_pnl=+100.27`, `-7.94%` on coin, positive only due to ETH hedge)
      4. `2026-01-25T20:00:00Z` `SOL` buy (`entry=20.580000`, `exit=18.810000`, `exit_reason=time_exit`, `coin_pnl=-332.97`, `hedge_pnl=-48.25`, `total_pnl=-381.22`, `-8.08%`)
      5. `2026-01-31T20:00:00Z` `ETH` buy (`entry=2285.440000`, `exit=2083.160000`, `exit_reason=liquidated`, `coin_pnl=-532.56`, `hedge_pnl=+2536.57`, `total_pnl=+2004.01`, `-7.53%` on coin, positive only due to ETH hedge)
      6. `2026-01-31T20:00:00Z` `BTC` buy (`entry=84517.850000`, `exit=77533.310000`, `exit_reason=time_exit`, `coin_pnl=-1925.25`, `hedge_pnl=+1939.67`, `total_pnl=+14.42`, `-0.16%` on coin, positive only due to ETH hedge)
- **Total Portfolio Result & Leg Decomposition:**
  - Total portfolio PnL: **`+$4,292.50`** (`+4.2925%` on $100,000 initial capital over 283 days, ~5.54% annualized, below T-bill risk-free rate).
  - **Critical Leg Decomposition:**
    - **Spot Coin PnL: `-$3,968.80` (LOSS)** across all 6 trades (3 winning trades, 3 losing trades; spot crash-rebound entries after bounced RSI<20 bars lost money on net!).
    - **ETH Hedge PnL: `+$8,261.31` (GAIN)** from the mandatory ETH short hedge (`entry_spec=next_open`).
    - **Rebound-Short PnL: `$0.00` (0 trades)** at the canonical `target_pct=9.0%` (no post-bounce rebound retraced 9% within 50h to trigger `rebound_short`). Only at `target_pct=5.0%` did 3 rebound-shorts trigger (`+$2,922.68` short leg + `+$4,673.72` spot leg = `+$7,596.40` total).
- **C6-T3 Episode Dependence & Conditional Permutation:**
  - The 7 signal-gate events cluster into **3 crash episodes** across **4 distinct crash days** (`2026-01-19`, `2026-01-20`, `2026-01-25`, `2026-01-31`) and 3 symbols (`BTC`, `ETH`, `SOL`):
    - Episode 0 (`2026-01-19T03:00Z .. 2026-01-20T19:00Z`, 3 events, 3 trades): **`+$3,446.47`**
    - Episode 1 (`2026-01-25T20:00:00Z`, 1 event, 1 trade): **`-$381.22`**
    - Episode 2 (`2026-01-31T20:00:00Z`, 3 events, 3 trades): **`+$1,227.25`**
  - **Episode-block bootstrap (20,000 resamples):** 95% CI **`[-1,143.66, +10,339.42]`** (spans zero), mean `+$4,276.82`, median `+$4,292.50`, `P(total PnL > 0) = 0.9624`. Minimum episodes for 95% CI to exclude zero: **4** (only 3 observed).
  - **Conditional temporal-edge permutation (200 draws across 43 eligible crash bars):** Null mean `+$1,882.19`, median `+$1,838.72`; observed `+$4,292.50` sits at the **92.0th percentile** (`p_null_ge_canonical = 0.0800`, 16/200), which does **not** meet the `p < 0.05` significance threshold (`verdict = underpowered`).
- **C10.2 Full-Portfolio Placebo (Exact Enumeration of all $\binom{7}{6} = 7$ subsets):**
  - Across all 7 exact 6-of-7 subsets of gate-passing signals, portfolio total PnL ranges from `+$2,588.65` to `+$5,385.47` (mean `+$4,211.38`, median `+$4,414.12`, 95% CI `[+2,751.97, +5,278.71]`, `P(placebo > 0) = 1.0000`).
  - Canonical `+$4,292.50` sits at the **42.86th percentile** (`p_ge_canonical = 0.7143`, 5 of 7 subsets beat or match canonical). Canonical trade admission has **zero** distinguishing alpha over omitting any one of the 7 gate-passing signals (`verdict = underpowered`).
- **C7 Full Fragility & Robustness Battery (Phase A + Phase B):**
  - **Spot vs. Hedge Masking:** Spot coin PnL is negative (`-$3,968.80`), and 3 of 6 trades (`SOL` Jan 20, `ETH` Jan 31, `BTC` Jan 31) have negative spot PnL and only turn positive at the portfolio level because the short ETH hedge gained during the market decline.
  - **Cost Stress (Phase B):** Baseline `+$4,292.50` drops to `+$3,425.05` at 2x slippage (10 bps) and turns **negative (`-$891.35`)** at 5x slippage (25 bps).
  - **Parameter Sensitivity (Phase B):**
    - Tightening RSI threshold to `< 15` (`rsi_threshold_15`) yields **1 trade and `-$3,266.48`**.
    - Shortening `time_exit` to 24h yields `+$3,083.41`; extending to 72h drops to `+$1,260.18`.
    - **Notable Sensitivity Observation (`rsi_threshold_25`):** Widening the crash threshold to `RSI(21) < 25` produces **17 trades** (12 buy, 5 rebound-short) where the spot buy leg loses `-$7,084.54`, the ETH hedge contributes `+$2,915.45`, and the rebound-short leg captures `+$30,328.77` (`+29.3%` total PnL), and lowering `target_pct` to `5.0%` (`target_pct_5`) triggers 3 rebound-shorts (`+$2,922.68`) alongside the spot recovery (`+$4,673.72`, total `+$7,596.40`).
  - **Battery Verdict:** `FRAGILE_NOT_DECISION_GRADE`.

## 3. Evaluation Against the 7 Stop/Go Criteria (Native Hyperliquid Window)
1. **Criterion 1 (Hyperliquid-native real-data coverage):** **PASS (with Ironflow node-derived provenance caveat)** — Full 283-day window (`2025-12-20 .. 2026-09-28`, 6,792 hourly bars/symbol, 5 symbols) verified from real Hyperliquid node candles archived via Ironflow HF (`CC BY 4.0`), with 6/6 trades and 43/43 crash events reconciled to the cent (`unexplained=0`).
2. **Criterion 2 (Dependence-aware edge excludes zero with adequate power):** **FAIL (`underpowered`)** — Episode-block 95% CI is `[-1,143.66, +10,339.42]` (includes 0), conditional permutation `p = 0.0800` (>= 0.05), and only 3 episode blocks / 4 distinct crash days occurred in 283 days.
3. **Criterion 3 (Full-portfolio placebo distinguishes edge):** **FAIL (`underpowered`)** — Exact full-portfolio placebo (`p_ge_canonical = 0.7143`) shows the canonical portfolio sits squarely inside the distribution of random 6-of-7 gate-passing subsets.
4. **Criterion 4 (Core spot buy-leg economics positive, not masked by hedge):** **FAIL** — Spot coin PnL is **negative (`-$3,968.80`)**; the `+$4,292.50` headline total is entirely manufactured by the `+$8,261.31` ETH hedge PnL. Furthermore, at `rsi_threshold_25` where rebound-shorts trigger (`+$30,328.77`), the spot buy leg loses `-$7,084.54`.
5. **Criterion 5 (Stability across crash episodes / sub-periods):** **FAIL** — All 6 trades occur in `2026-Jan` across 3 episodes; dropping Episode 0 drops total PnL by 80.3% (to `+$846.03`), and one episode (`Episode 1`, `SOL` Jan 25) is negative (`-$381.22`). Outside January 2026 (8 months of the 283d window), 0 trades triggered.
6. **Criterion 6 (Robust to cost / parameter stress):** **FAIL** — 5x slippage turns total PnL negative (`-$891.35`), `RSI < 15` loses `-$3,266.48`, and spot leg is negative across baseline, `rsi_threshold_15`, and `rsi_threshold_25`.
7. **Criterion 7 (Validated edge transferable as GO):** **FAIL** — 0/7 criteria pass for an unconditional strategy GO.

## 4. Decision Verdict
- **Overall Verdict on Canonical RSI(21)<20 Strategy in Native Window:** **`NO_GO` / `FRAGILE_NOT_DECISION_GRADE` (`underpowered`)**. The canonical `RSI(21) < 20` crash-rebound portfolio does **not** generate positive spot alpha on native Hyperliquid (`-$3,968.80` spot PnL vs `+$8,261.31` ETH hedge PnL) and lacks statistical power (`3` episodes, permutation `p = 0.0800`, placebo `p = 0.7143`).
- **Actionable Native Discovery for Next Focus Campaign (C12):** Native Hyperliquid data reveals that while strict `RSI(21) < 20` spot entries bounce weakly or get liquidated, **`RSI(21) < 25` crash rebounds exhibit strong short-term mean reversion (`+$30,328.77` rebound-short PnL across 5 trades, or `+$4,673.72` spot PnL at `target_pct=5%`)**. The next focus campaign (C12) must test the native Hyperliquid short-the-oversized-crash-rebound (and `target_pct=5%` long) specification across `rsi_threshold` in `[20, 22, 25, 30]`.