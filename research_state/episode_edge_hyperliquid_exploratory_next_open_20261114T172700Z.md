# Hyperliquid exploratory episode ledger — spec-literal next-open (NOT EVIDENCE)

- **Generated (UTC):** 2026-11-14T17:27:00Z
- **Label:** `NOT_EVIDENCE_EXPLORATORY_FANOUT` — `performance_evidence=false`, `canonical_baseline_changed=false`
- **Basis:** `research_state/campaign_results_real_hyperliquid_exploratory_next_open_20261114T162212Z.json` (spec-literal next-open, exploratory) on retained partial chain `research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z` (24 symbols × 3885 bars, 2026-04-20T03:00Z..2026-09-28T23:00Z). Real fetched candles, non-synthetic; NOT the 283-day spec window and NOT performance evidence.

## Clustering (98h linkage)
- Rule: single-linkage by entry timestamp proximity within 98h (spec holding horizon).
- Real-engine trades: **2** from **8** spec-literal signals (6 blocked by ETH hedge / 120% gross cap / availability).
- Independent crash episodes: **2** (2 traded crash days out of 4 census crash days 2026-05-28, 2026-06-02, 2026-06-05, 2026-06-24).

## Episodes
| Episode | Crash day | Symbol(s) | Trades | Signals (window) | Episode PnL | Exit | Bars | R |
|---|---|---|---:|---:|---:|---|---:|---:|
| 1 | 2026-05-28 | BCH | 1 | 2 | +559.36 | time_exit | 50 | 0.211 |
| 2 | 2026-06-02 | BTC | 1 | 6 | -3230.12 | liquidated | 34 | -1.358 |

- Total PnL: **-2670.76**; episode PnLs: [+559.36, -3230.12]; positive/negative episodes: 1/1.
- Single BTC liquidation accounts for the entire realized loss magnitude (dominant downside episode).

## Statistical inference (explicit)
- **Episode-block bootstrap:** `NOT_APPLICABLE` (not run). Reason: `n_episodes=2 < 10` (binding target ≥10). Resampling 2 episodes cannot yield a credible 95% CI and would manufacture precision; CI bounds recorded as null.
- **Crash-day permutation:** `NOT_APPLICABLE` (not run). Reason: `n_episodes=2 < 10` and 2 traded crash days; p-value at this sample size is not informative and must not be manufactured (p-value null).
- **Full-portfolio placebo:** `NOT_RUN_THIS_SESSION` (canonical partial campaign 0-trade; retained window underpowered).

## GO criteria check
- Full 283d Hyperliquid window acquired: **false**
- ≥10 independent crash episodes: **false** (2)
- Episode-block bootstrap 95% CI excludes 0: **false** (N/A)
- Crash-day permutation p < 0.05: **false** (N/A)
- Full-portfolio placebo p < 0.05: **false** (not run)
- **Verdict:** `UNDERPOWERED_NOT_EVIDENCE`

## Limitations
- 2 trades / 2 episodes on a 162-day partial retained window — far below ≥10 episode power target.
- Portfolio/path dependent (6/8 signals blocked by constraints); BTC liquidation dominates loss.
- Partial window (3885/6792 bars) under decaying public-API retention; not the 283-day spec window.
- Exploratory, `performance_evidence=false`; no validation or capital-allocation inference permitted.
