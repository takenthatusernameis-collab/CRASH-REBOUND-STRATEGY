# C14 Decision Verdict — Hyperliquid-Native Broad-Universe Power Escalation

**Generated (UTC):** 2026-11-16T02:15:00Z
**Campaign:** C14 — broad-universe native power escalation (Ironflow HF, CC BY 4.0, node-derived, NOT venue candleSnapshot)
**Verdict:** `UNDERPOWERED`

---

## Executive Summary

C14 executed the full pre-registered inference battery on the widest available Hyperliquid-native evidence base (197 symbols, 113 selected at $5M gate, 283-day window). The canonical campaign produced **7 trades** (total PnL +8,914) from **9 signal-gate events** across **3 dependence-clustered episodes** on **4 distinct crash days**. The episode-block bootstrap 95% CI for total PnL **spans zero** at the observed 3 episodes (−1,144 to +17,547), and the conditional temporal-edge permutation yields **p = 0.03595**. The placebo exact-enumeration p-value is **0.4444**. With only 3 effective independent episodes (max 4 achievable from this archive), the evidence does not meet the pre-registered GO criteria (CI excluding zero + permutation p < 0.05). Verdict: **UNDERPOWERED**.

---

## Priors Referenced (Do Not Relitigate)

1. **C11.3** — `decision_verdict_hyperliquid_native_20261115T155318Z` — `NO_GO/FRAGILE_NOT_DECISION_GRADE`
2. **C12** — `decision_verdict_hyperliquid_native_c12_20261115T181500Z` — `NO_DECISION_GRADE_GO`
3. **C13** — `decision_verdict_hyperliquid_native_c13_20261115T203734Z` — `UNDERPOWERED` (10 episodes / 5 symbols / 283d)
4. **C10 cross-venue** — `decision_verdict_consolidated_20261115T122636Z` — `NO_GO` (0/7, `is_hyperliquid_venue_data=false`)
5. **FINAL consolidated** — `decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z` — `NO_GO`

---

## C14 Evidence Stems (All Provenance-Consistent, Non-Synthetic)

| Artifact | Path | Key Metrics |
|---|---|---|
| Prereg | `hyperliquid_native_c14_prereg_20261116T001200Z.json` | seed 20261116, min_draws 100, draws 20000, rsi20/t9 |
| Intake | `archive_intake_validation_20261116T001129Z.json` | ACCEPT_AS_EVIDENCE_CANDIDATE, 174 accepted symbols |
| Archive | `archives/hyperliquid_ironflow_wide_20261115T214900Z/` | 197 parquet, SOURCE.md non-synthetic attestation |
| Cache | `cache/hyperliquid_ironflow_wide_20261115T234000Z/` | provenance.json real_market_data_intended=true |
| Universe | `universe_hyperliquid_ironflow_wide_20261115T225100Z.json` | selected_count=113, $5M gate, 283d, real/non-synthetic |
| Campaign | `campaign_results_real_hyperliquid_ironflow_wide_20261116T001200Z.json` | 7 trades, PnL +8914.33, buy +11736.94 / short −2822.60 |
| Census | `crash_event_census_hyperliquid_ironflow_wide_20261116T001200Z.json` | 661 events, 235 vol-pass, 71 bounce, 119 regime, **9 signal-pass, 7 trades** |
| Placebo | `placebo_portfolio_hyperliquid_ironflow_wide_20261116T001200Z.json` | exact enumeration, 36 runs (choose 7 of 9), p_ge=0.4444 |
| Episode-edge | `episode_edge_hyperliquid_ironflow_wide_20261116T001200Z.json` | 20000 draws, seed 20261116, config-matched rsi20/t9 |

---

## Dependence-Aware Inference

### Episode Clustering (98h single-linkage)
- **Episodes:** 3 | **Distinct crash days:** 4 | **Symbols:** 4 (BCH, BTC, ETH, SOL)
- **Largest episode:** 5 events (55.6% share) on 2026-01-31
- **Effective independent sample:** 7 trades / 3 episodes / 4 symbols / 4 crash days

### Episode-Block Bootstrap (20,000 resamples, seed 20261116)
- **Observed total PnL:** +8,914.33
- **95% CI:** [−1,143.66, +17,547.24] — **spans zero**
- **P(total PnL > 0):** 0.96385
- **Power curve (episodes required for 95% CI excluding zero):**
  - n=2: CI [−762, +11,698] — includes zero
  - n=3: CI [−1,144, +17,547] — includes zero ← **observed**
  - **n=4: CI [+2,303, +20,994] — first size excluding zero**
  - n=5: CI [+4,324, +24,440]
  - n≥4 all exclude zero (extrapolation basis: observed episode-total PnL resampled with replacement)
- **Maximum episodes achievable from C14 archive:** 4 (one additional distinct crash day beyond observed 4)

### Conditional Temporal-Edge Permutation (20,000 draws, seed 20261116)
- **Eligible real RSI<20 crash bars:** 661
- **Observed event slots:** 9 (per-symbol multiplicity preserved: BCH=2, BTC=1, ETH=2, SOL=4)
- **Null distribution:** mean +2,560.72, median +2,475.77, stdev 2,739.52
- **Canonical percentile:** 96.40%
- **p(null ≥ canonical):** **0.03595** (719/20000)
- **Mode:** deterministic seeded subset (astronomical distinct draws: 487,687,200)

### Placebo (Exact Enumeration)
- **Mode:** exact enumeration (choose 7 of 9 signal-gate events)
- **Runs:** 36 (mathematically complete, more rigorous than Monte Carlo)
- **p(canonical ≥ observed):** **0.4444**
- **P(total > 0):** 1.0

### Leg Separation (Spot Buy / ETH Hedge / Rebound Short)
- **Buy legs:** 6 trades, +11,736.94 PnL
- **Rebound short legs:** 1 trade (BCH), −2,822.60 PnL
- **Net:** +8,914.33

---

## Power Curve Summary

| Episodes (n) | 95% CI Low | 95% CI High | Excludes Zero? | Within Observed? |
|---|---|---|---|---|
| 2 | −762 | +11,698 | No | Yes |
| **3 (observed)** | **−1,144** | **+17,547** | **No** | **Yes** |
| **4** | **+2,303** | **+20,994** | **Yes** | No |
| 5 | +4,324 | +24,440 | Yes | No |
| 10 | +13,901 | +45,053 | Yes | No |
| 20 | +36,435 | +81,472 | Yes | No |
| 40 | +86,756 | +150,484 | Yes | No |

**Interpretation:** The observed 3 episodes are insufficient for a decision-grade CI excluding zero. One additional independent episode (n=4) would cross the threshold, but the C14 archive yields at most 4 distinct crash days (4 episodes max). The strategy is **underpowered** on the widest available native universe.

---

## Verdict Token

**`UNDERPOWERED`** — Full battery executed on widest available native universe (197 symbols, 113 selected, 283d). Evidence does not meet pre-registered GO criteria (CI excluding zero + permutation p < 0.05). Power curve quantified: 4 episodes required for CI exclusion; maximum achievable from C14 archive is 4 episodes. Explicit data request: additional independent crash episodes/window extension required for decision-grade inference.

---

## Reproduction

```bash
# Episode-edge (C14 bound)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_episode_edge_okx_multiyear.py \
  --draws 20000 --seed 20261116 \
  --cache-dir research_state/cache/hyperliquid_ironflow_wide_20261115T234000Z \
  --universe research_state/universe_hyperliquid_ironflow_wide_20261115T225100Z.json \
  --census research_state/crash_event_census_hyperliquid_ironflow_wide_20261116T001200Z.json \
  --campaign research_state/campaign_results_real_hyperliquid_ironflow_wide_20261116T001200Z.json \
  --venue-label Hyperliquid \
  --out episode_edge_hyperliquid_ironflow_wide_20261116T001200Z

# Gate verification
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c14_focus_campaign.py
```