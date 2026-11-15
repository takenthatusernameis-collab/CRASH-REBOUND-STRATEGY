# C7-HYPERLIQUID-NATIVE — Multi-Year Robustness, Fragility & Achievable-Power Battery (Hyperliquid-native)

**Generated (UTC):** 2026-11-15T15:56:49Z
**Venue:** Hyperliquid (Ironflow node-derived, native) (Hyperliquid-native)
**Provenance:** Real Hyperliquid (Ironflow node-derived, native) data, non-synthetic; node-derived (Ironflow HF, CC BY 4.0), NOT the venue's own candleSnapshot; Hyperliquid-native evidence (not cross-venue).
**Verdict:** `FRAGILE_NOT_DECISION_GRADE` (Hyperliquid-native)

## Headline
- Canonical total PnL: **4292.50** (6 trades)

## A1 — Per-leg attribution (where the PnL comes from)
| Leg | Trades | Total PnL | Mean | Min | Max |
|---|---:|---:|---:|---:|---:|
| buy | 6 | 4292.50 | 715.42 | -1091.74 | 3568.09 |

- Coin (spot) PnL: **-3968.80** | Hedge PnL: **8261.31** | Rebound-short PnL: **0.00** | Rebound hedge PnL: **0.00**

## A2 — Exit-reason breakdown
| Exit reason | Trades | Total PnL |
|---|---:|---:|
| liquidated | 2 | 2476.34 |
| time_exit | 4 | 1816.16 |

## A3 — Sub-period stability (by calendar year)
| Year | Trades | Total PnL | Win rate |
|---|---:|---:|---:|
| 2026 | 6 | 4292.50 | — |

## A4 — Concentration across episodes
- Episodes with trades: **3**; positive: **2**; negative: **1**
- Gross positive episode PnL: **4673.72**; gross negative: **-381.22**
- Top-1 episode share of total: **0.8029050226832354**; top-3 sum: **4292.5** (share 1.0)
- HHI of |episode contrib|: **0.5295**

## A5 — Leave-one-out (analytical)
### By year
| Dropped year | Dropped PnL | Remaining total | Sign flipped? |
|---|---:|---:|:---:|
| 2026 | 4292.5 | 0 | YES |

### By episode
| Episode | Episode PnL | Remaining total | Sign flipped? |
|---|---:|---:|:---:|
| 0 | 3446.47 | 846.03 | no |
| 1 | -381.22 | 4673.72 | no |
| 2 | 1227.25 | 3065.25 | no |

## A6 — Achievable-power bound
- Episodes: **3**; mean episode PnL: **1430.83**; SD: **1569.27**
- t-stat vs zero: **1.579** (crit 1.96)
- Episodes needed for 95% CI to exclude zero: **4.6**
- Power at n: {'19': 0.978, '30': 0.9988, '50': 1.0, '100': 1.0, '200': 1.0, '324': 1.0}
- At the observed per-episode mean/SD, ~n episodes are required for the 95% CI of total PnL to exclude zero across achievable multi-year crash-day counts.

## B — Engine re-runs (real portfolio engine, modified config)
| Variant | Trades | Total PnL | Buy leg | Short leg | Wall s |
|---|---:|---:|---:|---:|---:|
| baseline | 6 | 4292.50 | 4292.50 | 0.00 | 0.4 |
| slippage_2x | 6 | 3425.05 | 3425.05 | 0.00 | 0.4 |
| slippage_5x | 6 | -891.35 | -891.35 | 0.00 | 0.4 |
| funding_2x | 6 | 4423.81 | 4423.81 | 0.00 | 0.4 |
| rsi_threshold_15 | 1 | -3266.48 | -3266.48 | 0.00 | 0.4 |
| rsi_threshold_25 | 17 | 23244.22 | -7084.54 | 30328.77 | 0.4 |
| target_pct_5 | 6 | 7596.40 | 4673.72 | 2922.68 | 0.4 |
| target_pct_12 | 6 | 4292.50 | 4292.50 | 0.00 | 0.4 |
| time_exit_24 | 6 | 3083.41 | 3083.41 | 0.00 | 0.4 |
| time_exit_72 | 6 | 1260.18 | 1260.18 | 0.00 | 0.4 |

## Interpretation
The multi-year headline of 4292.50 (Hyperliquid-native) is NOT a decision-grade edge: spot coin leg is negative (-3968.80) and total is positive (+8261.31 ETH hedge pnl masks the spot loss); the episode-mean t-stat (1.579) cannot reject zero; ~4.6 independent episodes would be required for a 95% CI excluding zero, far beyond achievable crash-day counts. The honest verdict remains that the strategy's temporal edge is not established; this battery shows it is fragile and not robust to leg decomposition, sub-period, cost, or power limits.

## Reproduction
```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_multiyear_robustness_battery.py --phases A B --cache-dir research_state/cache/hyperliquid_ironflow_native_20251220_20260928 --universe research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json --campaign research_state/campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json --census research_state/crash_event_census_hyperliquid_ironflow_native_20261115T155226Z.json --episode-edge research_state/episode_edge_hyperliquid_native_20261115T155318Z.json --venue-label 'Hyperliquid (Ironflow node-derived, native)' --phase-label 'C7-HYPERLIQUID-NATIVE' --out multiyear_robustness_battery_hyperliquid_native_20261115T155522Z
```
