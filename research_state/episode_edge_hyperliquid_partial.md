# Phase O (Hyperliquid partial) — Crash-Episode Dependence Audit & Conditional Temporal-Edge Test

**Generated (UTC):** 2026-11-14T12:56:00Z
**Status:** `NOT_APPLICABLE_NO_EPISODES` — the partial window produced zero trades.
**Provenance:** Hyperliquid public-API PARTIAL window (aligned 2026-04-20T03:00:00Z..2026-09-28T23:00:00Z, 24 complete symbols x 3885 bars). NOT the 283-day spec window and NOT performance evidence.

## Why this phase exists

Phase M's exact full-portfolio placebo conditions on the observed gate-passing events and
varies only which of them are admitted, so it cannot test whether the *timing* of the crashes
carries edge. Phase O measures the dependence structure that the trade-level statistics
assumed away and then tests timing directly. On OKX this is what collapsed 11 events into
4 crash episodes and produced p(placebo >= canonical)=0.15 with an episode-block bootstrap
CI that spans zero.

## Basis (this session's partial run)

| Artifact | Value |
|---|---|
| Census (`hyperliquid_universe_snapshot_census_20261114T125249Z.json`) | 24 symbols / 93,240 bars / **11 RSI(21)<20 events** / **0 confirmed signals** |
| Partial campaign (`campaign_results_real_hyperliquid_universe_snapshot_20261114T125249Z.json`) | **0 trades**, total PnL **0.0**, `performance_evidence=false`, `research_status=NOT_EVIDENCE_PARTIAL_UNIVERSE` |

## Episode clustering (the binding constraint)

- Gate-passing events: **0**
- Distinct symbols: **0**
- Distinct crash days: **0**
- Crash episodes (linked at 98h): **0**

**Finding:** The partial window produced zero confirmed rebound signals and therefore zero
trades. There are no crash episodes to cluster, no distinct crash days, and no episode-level
PnL to bootstrap. The episode-aware audit is vacuous on this data: it can neither support nor
refute an edge.

## Conditional temporal-edge permutation test

- Mode: **not run**
- Reason: The permutation requires a canonical trade set to sit at a percentile of the null
  distribution. With zero trades there is no canonical PnL and no admissible draw. Running it
  would manufacture a p-value from an empty trade set, which is exactly the
  per-event-null-as-portfolio-test prohibition. It is recorded as NOT RUN rather than
  reported as a significant or non-significant result.

## Episode-block bootstrap

- Mode: **not run**
- 95% CI: n/a (no episodes to resample)

## Go criteria check (Hyperliquid-native)

| Criterion | Result |
|---|---|
| Full 283-day Hyperliquid window acquired with verified provenance | **false** (API retention: 3886/6792 bars) |
| >= 10 independent crash episodes with positive episode-level bootstrap CI | **false** (0 episodes) |
| Trade bootstrap 95% CI excludes 0 | **false** (0 trades) |
| Episode-block bootstrap 95% CI excludes 0 | **false** (not evaluable) |
| Crash-day-conditioned permutation p < 0.05 | **false** (not run; no trades) |
| Full-portfolio placebo p < 0.05 | **false** (not evaluable) |
| Worst drawdown within mandate | **not evaluable** (0 trades) |

## Verdict

`HYPERLIQUID_EPISODE_AUDIT_NOT_APPLICABLE; FULL_283D_BLOCKED_BY_API_RETENTION; STRATEGY_UNDERPOWERED`

## Limitations

1. Zero-signal partial window; the rare-event strategy simply did not fire in 3885 bars x 24 symbols.
2. The 11 RSI(21)<20 census events did not convert to confirmed signals under the spec gates
   (volume, bounce, regime/price, one-position-per-coin).
3. This is a pipeline and power-reality check, not evidence about strategy profitability on Hyperliquid.
4. A longer Hyperliquid-native history is required before any episode-aware inference is possible.