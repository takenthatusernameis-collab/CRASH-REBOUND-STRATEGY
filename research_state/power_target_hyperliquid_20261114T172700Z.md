# Hyperliquid power / sample-size closure (NOT EVIDENCE)

- **Generated (UTC):** 2026-11-14T17:27:00Z
- **Label:** `NOT_EVIDENCE_POWER_ANALYSIS` — `performance_evidence=false`
- **Basis (real, non-synthetic, partial):** retained aligned chain `hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z` (24 symbols × 3885 bars, 2026-04-20T03:00Z..2026-09-28T23:00Z, ~161.875 days). Census `hyperliquid_universe_snapshot_census_20261114T125249Z.json` (11 RSI crashes, 0 canonical confirmed signals, 4 distinct crash days). Exploratory spec-literal next-open funnel/campaign `..._20261114T162212Z` (29 crash hours → 11 volume-pass → 8 spec-literal signals → 2 trades / 2 episodes, PnL -2670.76). NOT the 283-day spec window and NOT performance evidence.

## Observed base rates
| Quantity | Value |
|---|---:|
| Retained window | 161.875 days, 24 symbols, 93,240 bars |
| Census RSI(21)<20 events | 11 |
| Canonical confirmed signals | 0 |
| Distinct crash days (census) | 4 (2026-05-28, 2026-06-02, 2026-06-05, 2026-06-24) |
| Crash days / calendar day | 0.02471 |
| RSI crash events / symbol-day | 0.002832 |
| Spec-literal funnel | 29 → 11 (vol-pass) → 0 (same-bar) → 5 (next-bar) → 8 signals → 2 trades |
| Traded episodes (exploratory) | 2 (from 2 crash days; conversion 0.5 per crash day) |
| Traded episodes / calendar day | 0.01236 |
| Episode PnLs | [+559.36 (BCH), -3230.12 (BTC, liquidated)] |
| Mean episode PnL | -1335.38 USD (n=2, unstable) |
| Sample SD (diagnostic, n=2) | 2679.56 USD — **unstable, dominated by one liquidation; caveat, not a reliable estimator** |

## Binding target (decision memo)
`research_state/decision_memo_okx_full.md` (2026-11-14T16:26Z): **≥10 independent crash episodes** with **episode-block bootstrap 95% CI excluding 0** + **crash-day permutation p < 0.05** + **full-portfolio placebo p < 0.05**.

## Power closure
### Calendar time (same 24-symbol universe, observed rates)
- Expected traded episodes in 283 days: ~3.50; **P(≥10 episodes in 283d, Poisson) ≈ 0.0019**.
- Days for E[N]=10 at 0.01236 episodes/day: **~809 days** (~26.6 months) beyond/beyond-observed rate; ~648 additional days beyond the observed 161.9-day window.
- **Conclusion:** the 283-day spec window at the observed 24-symbol rate is insufficient in expectation for the ≥10-episode count floor.

### Symbol scaling (hold 283 days, independence assumption — optimistic bound)
- Symbols needed for E[N]=10 in 283 days (independence): **~195** (24 × 10 / 3.50).
- Feasibility: recent probes show 31-32 symbols pass the $5M gate and crash days cluster across symbols (4 shared crash days), breaking independence. **Not feasible as an independence plan; bound only.**

### Episode-block bootstrap CI-width projection (diagnostic, not a forecast)
Using sigma_hat = 2679.56 USD/episode (n=2, unstable; for scaling illustration only), normal-approx 95% half-width ≈ 1.96·sigma_hat/sqrt(n):

| Episodes (n) | 95% half-width (USD, diagnostic) |
|---:|---:|
| 2 | 3714 |
| 4 | 2627 |
| 10 | 1661 |
| 20 | 1175 |
| 50 | 743 |

Interpretation: even under this very uncertain variance, excluding 0 at n=10 needs |mean| > ~1661 USD; observed mean is -1335 USD (negative, n=2). The projection shows **≥10 episodes is necessary but not sufficient** given observed instability — no detectability/edge claim is supported.

## Reconciliation with memo target
- **Required:** ≥10 independent crash episodes + episode-block bootstrap 95% CI excluding 0 + crash-day permutation p<0.05 + full-portfolio placebo p<0.05.
- **Current:** 2 traded episodes / 4 crash days / 2 trades, total PnL -2670.76 (exploratory, NOT evidence). All inference criteria NOT_APPLICABLE/NOT_RUN due to underpower.
- **Gap:** 8 more traded episodes for the count floor alone; at observed rates neither the 283-day window nor the current liquid symbol set can plausibly deliver this (independence broken by shared crash days). Regime change cannot be assumed.
- **Verdict:** `UNDERPOWERED` — retained partial chain cannot close the memo's GO criteria; only a verified full 283-day Hyperliquid-native archive plus sufficient realized episodes can.

## Assumptions & caveats
- Poisson crash-day arrival at lambda=0.02471/day (4/161.875) and 0.5 traded-episode conversion per crash day — highly uncertain at n=4.
- Symbol scaling assumes similar per-symbol rates and independence; shared crash days violate independence (optimistic bound).
- Episode PnL distribution unknown/unstable (n=2, one liquidation). No claim of positive edge; projections are detectability illustrations only.
