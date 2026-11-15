# Native C13 Verdict — Hyperliquid Crash-Rebound (RSI 25 / Target 9%)

**Verdict token: `UNDERPOWERED`** (not `GO`, not `NO_GO` — decision-grade thresholds not met under adequate effective N)

**Generated:** 2026-11-15T20:37:34Z
**Lead hypothesis:** `rsi_threshold 25`, `target_pct 9` (pre-registered in C13 prereg)
**Prereg:** `research_state/hyperliquid_native_c13_prereg_20261115T185721Z.json` + `.md` (prereg validation: PASS)
**Episode-edge artifact:** `research_state/episode_edge_hyperliquid_native_c13_20261115T200200Z.json` (200 draws, seed 20261115, config-matched canonical replay 17 trades / +23,244.22)
**Placebo artifact:** `research_state/placebo_portfolio_hyperliquid_native_c13_20261115T200309Z.json` (200 runs, seed 20261115, config-matched)
**Provenance caveat:** Hyperliquid-native, node-derived (Ironflow HF, CC BY 4.0), NOT venue `candleSnapshot`; `is_hyperliquid_venue_data=true`, `fabricated_data=false`, `synthetic_data=false`.

---

## Dependence-aware evidence (C13 pre-registered methods)

### Episode-block bootstrap (20,000 resamples, seed 20261115)
- **Effective independent sample:** 10 episodes, 17 trades, 5 symbols, 12 distinct crash days
- **Observed total PnL:** +23,244.22
- **Bootstrap CI95 (total PnL):** [−22,799.52, +79,978.91] — **spans 0**
- **P(total > 0):** 0.803
- **Power extrapolation:** CI excludes 0 only at n_episodes ≈ 37+ (far beyond observed 10); **first_size_excluding_zero: null** within observed range
- **Verdict per prereg:** UNDERPOWERED (effective N < pre-registered minimum for GO; CI95 spans 0)

### Temporal-edge permutation (200 deterministic draws, seed 20261115)
- **Null distribution:** mean +5,726.37, median +3,322.94, stdev 10,028.67
- **Canonical percentile (≤):** 0.915
- **p(null ≥ canonical):** 0.085 (17/200 draws)
- **Interpretation:** Not significant at α=0.05; canonical result is at the 91.5th percentile of the timing-null — consistent with timing luck.

### Full-portfolio placebo (200 random subsets of 17-from-33, seed 20261115)
- **Canonical total PnL:** +23,244.22 (17 trades)
- **Placebo summary (n=200):** mean +16,174.90, median +17,753.11, stdev 12,125.00
- **p_ge_canonical:** 0.32 (64/200 subsets ≥ canonical)
- **p_gt_canonical:** 0.32
- **Canonical percentile (≤):** 0.68
- **P(total > 0):** 0.875
- **Placebo CI95:** [−8,535.90, +35,076.30] — **spans 0**
- **Interpretation:** Canonical subset is not extreme in the placebo distribution (68th percentile); a random 17-of-33 subset frequently matches or exceeds it.

---

## Leg separation (required — no hedge-masked claims)

| Leg | Canonical PnL | Share of total |
|-----|--------------|----------------|
| Spot (long) | **−3,968.80** | negative |
| ETH hedge (short) | **+8,261.31** | positive |
| Rebound short | **+11,904.32** | positive |
| **Total** | **+23,244.22** | — |

**Key finding:** The positive total is **hedge-masked** — spot leg is deeply negative (−3,968.80). The rebound short (+11,904.32) and ETH hedge (+8,261.31) drive the aggregate. Per C13 prereg and hard prohibitions: **never flip to GO from hedge-masked totals or point PnL**.

---

## Pre-registered decision rule mapping

| Criterion | Threshold (prereg) | Observed | Met? |
|-----------|-------------------|----------|------|
| Episode-edge bootstrap CI95 excludes 0 on total PnL | Yes (GO) | **No** (spans 0) | ❌ |
| Effective episodes ≥ 5 | Yes (GO minimum) | 10 episodes | ✅ |
| Effective trades ≥ 10 | Yes (GO minimum) | 17 trades | ✅ |
| Permutation p(null ≥ canonical) < 0.05 | Yes (GO) | 0.085 | ❌ |
| Placebo p_ge_canonical < 0.05 | Yes (GO) | 0.32 | ❌ |
| Spot leg CI95 excludes 0 (positive) | Required for GO | Spot deeply negative | ❌ |

**Result:** No GO criterion is satisfied. The result is **UNDERPOWERED** — the 283-day native window yields 10 episodes / 17 trades / 12 crash days, which is structurally insufficient for decision-grade inference (CI95 spans 0, permutation and placebo not extreme).

---

## Verdict statement

**`UNDERPOWERED`** — The pre-registered, decision-grade native validation of the C12 lead (`rsi_threshold 25`, `target_pct 9`) does **not** produce a validated GO. The evidence is consistent with timing luck (permutation p=0.085, placebo p_ge=0.32), the bootstrap CI95 spans zero, and the positive total PnL is hedge-masked (spot negative). The canonical `RSI(21)<20` configuration remains **NO_GO** (C11.3). C12 `c12_25_9` was hypothesis-generating only (`NO_DECISION_GRADE_GO`); C13 does not validate it.

---

## Traceability (gate-enforced)

- **Prereg:** `hyperliquid_native_c13_prereg_20261115T185721Z.json` / `.md`
- **Episode-edge:** `episode_edge_hyperliquid_native_c13_20261115T200200Z.json`
- **Placebo:** `placebo_portfolio_hyperliquid_native_c13_20261115T200309Z.json`
- **Seed binding:** 20261115 (both artifacts)
- **SHA binding:** campaign `72d98f0d1664ed4c53020ac37ec34ded2cd13257e4b3489c4eec43db56caf9a5`, census `3e03b6909614c17163b754d3e66c7b894dd6c0adf07db73070a6ed62e3a83c6e` (both artifacts)
- **Config-matched canonical replay:** 17 trades, +23,244.224 (verified in both artifacts)
- **Effective N reported:** 17 trades / 10 episodes / 12 distinct crash days / 5 symbols

---

## Consolidated verdict update

The consolidated verdict (`research_state/decision_verdict_consolidated_20261115T155318Z.md`) should be updated to reflect that C13 native validation yields **UNDERPOWERED** for the `rsi 25 / target 9` lead, and the canonical `RSI(21)<20` remains **NO_GO**. No GO claim is warranted at this stage.