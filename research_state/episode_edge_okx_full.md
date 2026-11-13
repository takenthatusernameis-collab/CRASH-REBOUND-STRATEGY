# Phase O — Crash-Episode Dependence Audit & Conditional Temporal-Edge Test

**Generated (UTC):** 2026-11-13T23:30:04Z
**Status:** `0.1500` permutation p; effective sample **4 episodes / 5 crash days**.
**Provenance:** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence.

## Why this phase exists

Phase M's exact full-portfolio placebo conditions on the observed gate-passing events and
varies only which of them are admitted, so it cannot test whether the *timing* of the
crashes carries edge. Phase O measures the dependence structure that the trade-level
statistics assumed away and then tests timing directly.

## Episode clustering (the binding constraint)

- Gate-passing events: **11**
- Distinct symbols: **5**
- Distinct crash days: **5**
- Crash episodes (linked at 98h): **4**
- Largest episode share of events: **36.4%** (4/11)

| Episode | Window (UTC) | Events | Symbols | Distinct days |
|---|---|---|---|---|
| 0 | 2026-01-19T02:00:00Z .. 2026-01-20T19:00:00Z | 4 | ETH, SOL | 2 |
| 1 | 2026-01-25T20:00:00Z .. 2026-01-25T20:00:00Z | 2 | LINK, SOL | 1 |
| 2 | 2026-01-31T18:00:00Z .. 2026-01-31T21:00:00Z | 4 | AVAX, BCH, SOL | 1 |
| 3 | 2026-05-18T08:00:00Z .. 2026-05-18T08:00:00Z | 1 | BCH | 1 |

**Finding:** 11 gate-passing events collapse into 4 crash episodes over 5 distinct crash days; the largest episode holds 4 of 11 events (36.4%). Trade-level and event-level independence assumptions therefore overstate the effective sample.

## Conditional temporal-edge permutation test

- Mode: `deterministic_draws:40`
- Eligible real crash bars (RSI(21)<20 census): **342**
- Draws evaluated: **40** of 2298336768 possible
- Null total PnL: mean **5234.44**, median **4858.36**, p05 **-250.37**, p95 **10948.12**
- Canonical total PnL: **9159.69** at the **85.00%** percentile of crash-day-timed alternatives
- **p(placebo >= canonical) = 0.1500** (6/40)

Read: this is the first test in the chain that varies *when* the crashes happen while
holding the crash-day calendar fixed. A high p means the canonical PnL is explained by
which crash days occurred, not by the strategy's timing skill.

## Episode-block bootstrap (dependence-aware power)

- Episode blocks: **4**
- Bootstrap total PnL 95% CI: **[-4083.95, 24411.99]**
- P(total PnL > 0): **0.8754**

| Independent episodes | Bootstrap mean | 95% CI low | 95% CI high | CI excludes 0 |
|---|---|---|---|---|
| 2 | 4574.95 | -3939.94 | 16322.66 | False |
| 3 | 6756.83 | -4011.95 | 19363.00 | False |
| 4 | 9166.14 | -4083.95 | 24411.99 | False |

**Read:** the sample contains only 4 independent crash episodes. Resampling trades as independent
understates variance because trades inside an episode co-move.

## Verdict

Temporal edge is **not established**: p(placebo >= canonical) = **0.1500**. The effective independent sample is **4 episodes / 5 crash days**, far below the power requirement. Verdict remains **`underpowered`** / not decision-grade.

## Reproduction

```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_episode_edge_okx.py
```
