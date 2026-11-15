# C8-BINANCE — Multi-Year Cross-Venue Robustness, Fragility & Achievable-Power Battery

**Generated (UTC):** 2026-11-15T06:29:02Z
**Venue:** Binance UM (CROSS-VENUE; NOT Hyperliquid evidence)
**Provenance:** Real Binance UM exchange data, non-synthetic; CROSS-VENUE vs Hyperliquid spec; NOT Hyperliquid performance evidence.
**Verdict:** `FRAGILE_NOT_DECISION_GRADE` (CROSS-VENUE; NOT Hyperliquid evidence)

## Headline
- Canonical total PnL: **21994.06** (42 trades)

## A1 — Per-leg attribution (where the PnL comes from)
| Leg | Trades | Total PnL | Mean | Min | Max |
|---|---:|---:|---:|---:|---:|
| buy | 28 | -36077.66 | -1288.49 | -12117.68 | 7016.18 |
| short | 14 | 58071.73 | 4147.98 | -2932.52 | 18998.61 |

- Coin (spot) PnL: **-21092.36** | Hedge PnL: **52912.41** | Rebound-short PnL: **-27185.16** | Rebound hedge PnL: **34626.99**

## A2 — Exit-reason breakdown
| Exit reason | Trades | Total PnL |
|---|---:|---:|
| liquidated | 13 | -46025.89 |
| time_exit | 15 | 9948.23 |
| target_rebound_short | 14 | 58071.73 |

## A3 — Sub-period stability (by calendar year)
| Year | Trades | Total PnL | Win rate |
|---|---:|---:|---:|
| 2023 | 11 | -15387.99 | — |
| 2024 | 15 | -17022.69 | — |
| 2025 | 8 | 42454.00 | — |
| 2026 | 8 | 11950.74 | — |

## A4 — Concentration across episodes
- Episodes with trades: **19**; positive: **7**; negative: **12**
- Gross positive episode PnL: **72330.9**; gross negative: **-50336.84**
- Top-1 episode share of total: **1.7980035204561493**; top-3 sum: **57695.98** (share 2.623252420236294)
- HHI of |episode contrib|: **0.147**

## A5 — Leave-one-out (analytical)
### By year
| Dropped year | Dropped PnL | Remaining total | Sign flipped? |
|---|---:|---:|:---:|
| 2023 | -15387.99 | 37382.06 | no |
| 2024 | -17022.69 | 39016.75 | no |
| 2025 | 42454.0 | -20459.94 | YES |
| 2026 | 11950.74 | 10043.33 | no |

### By episode
| Episode | Episode PnL | Remaining total | Sign flipped? |
|---|---:|---:|:---:|
| 0 | -12117.68 | 34111.74 | no |
| 1 | -1868.14 | 23862.2 | no |
| 2 | 4112.64 | 17881.42 | no |
| 3 | -9080.85 | 31074.91 | no |
| 4 | 3566.03 | 18428.03 | no |
| 5 | -1624.53 | 23618.59 | no |
| 6 | -9992.46 | 31986.53 | no |
| 7 | 4189.06 | 17805.01 | no |
| 8 | -8438.45 | 30432.51 | no |
| 9 | -1156.31 | 23150.37 | no |
| 10 | 7015.8 | 14978.26 | no |
| 11 | -2932.52 | 24926.59 | no |
| 12 | -1174.68 | 23168.74 | no |
| 13 | 39545.41 | -17551.34 | YES |
| 14 | 2767.19 | 19226.88 | no |
| 15 | -312.23 | 22306.29 | no |
| 16 | 11134.77 | 10859.29 | no |
| 17 | -117.94 | 22112.0 | no |
| 18 | -1521.06 | 23515.12 | no |

## A6 — Achievable-power bound
- Episodes: **19**; mean episode PnL: **1157.58**; SD: **10727.85**
- t-stat vs zero: **0.47** (crit 1.96)
- Episodes needed for 95% CI to exclude zero: **329.9**
- Power at n: {'19': 0.0757, '30': 0.0909, '50': 0.1189, '100': 0.1904, '200': 0.3324, '324': 0.493}
- At the observed per-episode mean/SD, ~n episodes are required for the 95% CI of total PnL to exclude zero. The multi-year OKX universe yields ~19 episodes over 3.38y; realistic crash-day counts (~30-50) are far below this, so the cross-venue edge is inherently underpowered on achievable data.

## B — Engine re-runs (real portfolio engine, modified config)
| Variant | Trades | Total PnL | Buy leg | Short leg | Wall s |
|---|---:|---:|---:|---:|---:|
| baseline | 42 | 21994.06 | -36077.66 | 58071.73 | 129.3 |
| slippage_2x | 42 | 10806.37 | -41404.24 | 52210.61 | 125.5 |
| slippage_5x | 42 | -22911.74 | -63098.01 | 40186.27 | 130.3 |
| funding_2x | 42 | 24864.48 | -32599.30 | 57463.77 | 131.2 |
| entry_spec_literal_next_open | 136 | -70309.57 | -115098.77 | 44789.19 | 130.9 |
| rsi_threshold_15 | 5 | -7167.42 | -15622.83 | 8455.40 | 131.6 |
| rsi_threshold_25 | 176 | -11768.10 | -89454.66 | 77686.55 | 127.4 |
| target_pct_5 | 42 | -4582.25 | -30431.18 | 25848.92 | 126.4 |
| target_pct_12 | 42 | 18104.04 | -25082.57 | 43186.61 | 125.3 |
| time_exit_24 | 42 | 6492.25 | -42319.55 | 48811.81 | 124.4 |
| time_exit_72 | 42 | 21234.30 | -36837.42 | 58071.73 | 125.1 |

## Interpretation
The multi-year cross-venue headline of 21994.06 is NOT a decision-grade edge: the core buy leg loses money while the headline total is positive; the entire positive total is carried by the optional rebound-short leg; profit is concentrated in ['2025', '2026'] while ['2023', '2024'] are negative; the episode-mean t-stat (0.47) cannot reject zero; ~329.9 independent episodes would be required for a 95% CI excluding zero, far beyond achievable crash-day counts. The honest cross-venue verdict remains that the strategy's temporal edge is not established; this battery shows it is fragile and not robust to leg decomposition, sub-period, cost, or power limits. CROSS-VENUE Binance UM data only — NOT Hyperliquid performance evidence.

## Reproduction
```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_multiyear_robustness_battery.py --phases A --out multiyear_robustness_battery
```
