# C7 — Multi-Year Cross-Venue Robustness, Fragility & Achievable-Power Battery

**Generated (UTC):** 2026-11-15T01:19:15Z
**Provenance:** Real OKX exchange data, non-synthetic; CROSS-VENUE vs Hyperliquid spec; NOT Hyperliquid performance evidence.
**Verdict:** `FRAGILE_NOT_DECISION_GRADE` (CROSS-VENUE; NOT Hyperliquid evidence)

## Headline
- Canonical total PnL: **18220.86** (42 trades)

## A1 — Per-leg attribution (where the PnL comes from)
| Leg | Trades | Total PnL | Mean | Min | Max |
|---|---:|---:|---:|---:|---:|
| buy | 30 | -27836.64 | -927.89 | -12052.17 | 6853.54 |
| short | 12 | 46057.50 | 3838.12 | -1454.10 | 12431.03 |

- Coin (spot) PnL: **-28557.90** | Hedge PnL: **59980.18** | Rebound-short PnL: **-25157.11** | Rebound hedge PnL: **30426.71**

## A2 — Exit-reason breakdown
| Exit reason | Trades | Total PnL |
|---|---:|---:|
| liquidated | 12 | -44947.31 |
| time_exit | 18 | 17110.67 |
| target_rebound_short | 12 | 46057.50 |

## A3 — Sub-period stability (by calendar year)
| Year | Trades | Total PnL | Win rate |
|---|---:|---:|---:|
| 2023 | 11 | -17994.43 | — |
| 2024 | 14 | -15574.79 | — |
| 2025 | 9 | 42630.39 | — |
| 2026 | 8 | 9159.69 | — |

## A4 — Concentration across episodes
- Episodes with trades: **19**; positive: **9**; negative: **10**
- Gross positive episode PnL: **64519.79**; gross negative: **-46298.93**
- Top-1 episode share of total: **1.6193745384582032**; top-3 sum: **44715.64** (share 2.454091178569728)
- HHI of |episode contrib|: **0.12**

## A5 — Leave-one-out (analytical)
### By year
| Dropped year | Dropped PnL | Remaining total | Sign flipped? |
|---|---:|---:|:---:|
| 2023 | -17994.43 | 36215.29 | no |
| 2024 | -15574.79 | 33795.65 | no |
| 2025 | 42630.39 | -24409.53 | YES |
| 2026 | 9159.69 | 9061.16 | no |

### By episode
| Episode | Episode PnL | Remaining total | Sign flipped? |
|---|---:|---:|:---:|
| 0 | -12052.17 | 30273.03 | no |
| 1 | -1157.88 | 19378.73 | no |
| 2 | 2062.86 | 16158.0 | no |
| 3 | -10451.56 | 28672.42 | no |
| 4 | 3604.32 | 14616.54 | no |
| 5 | -1594.58 | 19815.43 | no |
| 6 | -9372.24 | 27593.1 | no |
| 7 | 3786.7 | 14434.15 | no |
| 8 | -8145.91 | 26366.76 | no |
| 9 | -248.77 | 18469.62 | no |
| 10 | 7047.92 | 11172.94 | no |
| 11 | 2728.26 | 15492.6 | no |
| 12 | -1233.85 | 19454.71 | no |
| 13 | 4581.67 | 13639.19 | no |
| 14 | 29506.39 | -11285.53 | YES |
| 15 | 3040.34 | 15180.52 | no |
| 16 | -1969.97 | 20190.83 | no |
| 17 | 8161.33 | 10059.52 | no |
| 18 | -72.0 | 18292.86 | no |

## A6 — Achievable-power bound
- Episodes: **19**; mean episode PnL: **958.99**; SD: **8756.16**
- t-stat vs zero: **0.477** (crit 1.96)
- Episodes needed for 95% CI to exclude zero: **320.3**
- Power at n: {'19': 0.0765, '30': 0.0921, '50': 0.121, '100': 0.1947, '200': 0.3407, '324': 0.5046}
- At the observed per-episode mean/SD, ~n episodes are required for the 95% CI of total PnL to exclude zero. The multi-year OKX universe yields ~19 episodes over 3.38y; realistic crash-day counts (~30-50) are far below this, so the cross-venue edge is inherently underpowered on achievable data.

## Interpretation
The multi-year cross-venue headline of 18220.86 is NOT a decision-grade edge: the core buy leg loses money while the headline total is positive; the entire positive total is carried by the optional rebound-short leg; profit is concentrated in ['2025', '2026'] while ['2023', '2024'] are negative; the episode-mean t-stat (0.477) cannot reject zero; ~320.3 independent episodes would be required for a 95% CI excluding zero, far beyond achievable crash-day counts. The honest cross-venue verdict remains that the strategy's temporal edge is not established; this battery shows it is fragile and not robust to leg decomposition, sub-period, cost, or power limits. CROSS-VENUE OKX data only — NOT Hyperliquid performance evidence.

## Reproduction
```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_multiyear_robustness_battery.py --phases A --out multiyear_robustness_battery
```
