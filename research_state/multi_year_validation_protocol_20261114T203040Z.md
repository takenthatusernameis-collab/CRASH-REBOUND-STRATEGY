# Multi-Year Validation Protocol — 2026-11-14T20:30:40Z

**Label:** `NOT_EVIDENCE_VALIDATION_PROTOCOL` — protocol and power calculation, NOT performance evidence.

## Decision lock

**Current verdict: `NO_GO`.** Retained Hyperliquid window is a partial 161-day window with only 4 distinct crash days and 2 traded episodes; the power floor is >=10 independent crash episodes. No achievable API window can reach the floor, and no cross-venue, partial, dry-run, or synthetic artifact may be promoted to evidence.

Continue only with: an operator-supplied, C4-T1-validated, Hyperliquid-native archive covering at least the duration computed below (>=10 independent crash episodes), ingested through the DATA_REQUEST runbook.

## Power calculation (executed, not asserted)

Observed traded-episode rate: **0.012355/calendar day** (2 episodes / 161.9 retained days, 24 symbols).
Observed crash-day rate: **0.024710/day** (4 crash days).

| Target power | Required duration (traded-episode rate) | Required duration (crash-day rate) |
|---|---|---|
| 80% | 1013.2 d (2.78 y) | 506.6 d (1.39 y) |
| 90% | 1149.8 d (3.15 y) | 574.9 d (1.58 y) |
| 95% | 1271.1 d (3.48 y) | 635.6 d (1.74 y) |

**Archive requirement at 80% power:** >= 10 independent crash episodes; >= 1013.2 days (2.78 years); >= 24319 hourly bars/symbol × 24 symbols = 583656 bars.

The spec window is 283 days; 80% power needs a materially longer archive. That is the quantitative reason a multi-year operator archive is required.

## Protocol summary

- Primary endpoint: `episode_level_net_pnl` — two-sided 95% episode-block bootstrap CI on the mean episode PnL; GO if bootstrap 95% CI excludes 0 in the positive direction.
- Clustering: Collapse all crash signals within 72h on the same UTC crash day into one episode; an episode counts once regardless of how many symbols fired. Independence requires distinct crash days.
- Bootstrap: 10000 resamples over crash-day blocks; permutation: 10000 resamples; placebo: full-portfolio placebo over all signal-gate events.
- Multiplicity: Holm-Bonferroni across episode_level_net_pnl, episode_win_rate, max_drawdown.

## Reproduce

```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/build_multi_year_validation_protocol.py
```

Script sha256: `e76f5784df3ece72e66e1e0c951c17bed823415c3bae6114325e5d3fdecc6cee`

**Verdict:** `NO_GO` — `STRATEGY_UNDERPOWERED` until every GO criterion is met.
