# Hyperliquid exploratory fragility audit — next-open (NOT EVIDENCE)

- **Generated (UTC):** 2026-11-14T17:48:16Z
- **Label:** `NOT_EVIDENCE_FRAGILITY` — `performance_evidence=false`, `canonical_baseline_changed=false`
- **Chain:** `research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z` (same retained partial aligned chain; real, non-synthetic). Baseline: `campaign_results_real_hyperliquid_exploratory_next_open_20261114T162212Z.json`.

## Bounded variants (8 configs, spec-literal next-open path kept opt-in)
| Variant | Trades | Total PnL | Δ vs baseline | Max DD | BTC PnL | Non-BTC PnL |
|---|---:|---:|---:|---:|---:|---:|
| V0_baseline_spec_literal | 2 | -2670.76 | 0.00 | -3230.116863449931 | -3230.12 | 559.36 |
| V1_no_eth_hedge | 2 | -7945.88 | -5275.13 | -9990.339461044698 | -9990.34 | 2044.45 |
| V2_no_rebound_short | 2 | -2670.76 | 0.00 | -3230.116863449931 | -3230.12 | 559.36 |
| V3_cap_100 | 2 | -2132.90 | 537.85 | -2692.2646195416137 | -2692.26 | 559.36 |
| V4_cap_150 | 2 | -3477.54 | -806.78 | -4036.8952293124094 | -4036.90 | 559.36 |
| V5_exit_wider_tp12_50h | 2 | -2670.76 | 0.00 | -3230.116863449931 | -3230.12 | 559.36 |
| V6_exit_narrow_tp6_30h | 2 | 2113.00 | 4783.75 | 0.0 | 1472.11 | 640.89 |
| V7_exit_wider_tp15_72h | 2 | -3244.45 | -573.70 | -3244.4527554229862 | -3230.12 | -14.34 |

## Dominant-loss attribution
- Baseline total PnL: **-2670.76** (BCH 559.36, BTC -3230.12).
- The single **BTC liquidation** (2026-06-02T15:00Z entry → 2026-06-04T00:00Z, liquidated, total_pnl -3230.12) dominates the baseline loss; BTC contribution equals ~100% of baseline loss magnitude.
- PnL range across variants: [-7945.88, 2113.00], trades range: [2, 2]. All variants negative total PnL: False.

## Interpretation
- Results are fragile and path-dependent around one dominant BTC liquidation episode under portfolio/hedge/cap/exit constraints; no variant rescues performance or provides evidence.
- Bounded audit only (8 configs, same chain). NOT a search/optimization. Verdict remains `UNDERPOWERED_NOT_EVIDENCE`; `performance_evidence=false`.
