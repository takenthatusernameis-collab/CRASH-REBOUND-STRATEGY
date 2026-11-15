# Hyperliquid-native C12 inference (2026-11-15T18:15:00Z)

**Provenance (binding):** Real Hyperliquid-native, **node-derived (Ironflow HF, CC BY 4.0), NOT venue `candleSnapshot`** (`is_hyperliquid_venue_data=true`). 283d window 2025-12-20T00:00:00Z–2026-09-28T23:00:00Z. No synthetic/fabricated data.

**Method:** Real-engine campaign grid + crash-event census alignment per config. Dependence-aware episode-block bootstrap (98h episodes, 20k resamples, seed 20261115) over observed trade episode PnL blocks for spot/hedge/rebound/total. Canonical anchor reuses C11.3 episode-edge/placebo artifacts; non-anchor configs: parameterized engine permutation/placebo runners were not available for non-canonical RSI/target in existing scripts, so inference here provides census alignment + episode-bootstrap CIs with explicit underpowered labeling (no GO claim).

## Grid summary

| Config | RSI | Tgt | Trades | Episodes | Crash days | Spot PnL | Hedge PnL | Rebound PnL | Total PnL | Spot CI95 (ep-boot) | Total CI95 (ep-boot) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| anchor_20_9 | 20 | 9 | 6 | 3 | 4 | -3968.80 | 8261.31 | 0.00 | 4292.50 | [-32409, 26247] | [-1144, 10339] |
| c12_20_5 | 20 | 5 | 6 | 3 | 4 | -12104.27 | 17304.32 | -2710.00 | 7596.40 | [-32409, 1841] | [3682, 10339] |
| c12_22_9 | 22 | 9 | 6 | 3 | 4 | -3968.80 | 8261.31 | 0.00 | 4292.50 | [-32409, 26247] | [-1144, 10339] |
| c12_22_5 | 22 | 5 | 6 | 3 | 4 | -12104.27 | 17304.32 | -2710.00 | 7596.40 | [-32409, 1841] | [3682, 10339] |
| c12_25_9 | 25 | 9 | 17 | 10 | 11 | 6836.44 | 4762.24 | 11904.32 | 23244.22 | [-42839, 56387] | [-22800, 79979] |
| c12_25_5 | 25 | 5 | 17 | 10 | 11 | -17462.39 | 17159.13 | -15138.93 | -3596.44 | [-53444, 16113] | [-27390, 15395] |
| c12_30_9 | 30 | 9 | 57 | 19 | 31 | -65465.79 | 25822.09 | -6896.95 | -11453.31 | [-146016, 12312] | [-71683, 59746] |
| c12_30_5 | 30 | 5 | 58 | 19 | 32 | -86408.96 | 47863.20 | -33838.60 | -32741.08 | [-159893, -17186] | [-75300, 3362] |

### anchor_20_9 (RSI 20, target 9)
- Trades 6, episodes 3 (sizes [2, 1, 3]), crash days 4. Census: events 43, signal-gate 7, blocks {'trade_opened': 6, 'bounce_not_confirmed': 36, 'one_position_per_coin': 1}.
- Spot ep-bootstrap: obs -3968.80, CI95 [-32408.77, 26247.32], P(>0)=0.371 (n_ep=3).
- Hedge ep-bootstrap: obs 8261.31, CI95 [-27390.97, 42748.19], P(>0)=0.629 (n_ep=3).
- Rebound ep-bootstrap: obs 0.00, CI95 [0.00, 0.00], P(>0)=0.000 (n_ep=3).
- Total ep-bootstrap: obs 4292.50, CI95 [-1143.66, 10339.42], P(>0)=0.962 (n_ep=3).
- **Note:** UNDERPOWERED/FRAGILE: dependence-aware inference limited by small episode/trade count on 283d native window; CIs/permutation/placebo (where available) should be interpreted as non-decision-grade.
- **Note:** HEDGE_MASKED_TOTAL: spot coin PnL negative while total positive (ETH hedge/rebound drive headline); no spot-alpha claim.
- **Note:** CANONICAL_ANCHOR: reuse C11.3 inference artifacts; canonical verdict remains NO_GO/FRAGILE_NOT_DECISION_GRADE (0/7).
- Existing inference refs: {"episode_edge": {"path": "research_state/episode_edge_hyperliquid_native_20261115T155318Z.json", "permutation_p": null, "bootstrap_ci_total": {"mean": 4276.815875497696, "median": 4292.5031215663475, "p05": 464.8118139721046, "p95": 8120.1944291605905, "ci_low_pnl_2p5": -1143.656974215468, "ci_high_pnl_97p5": 10339.416948567261, "prob_total_pnl_gt_0": 0.9624}, "n_episodes": 3}, "placebo": {"path": "research_state/placebo_portfolio_hyperliquid_native_20261115T155625Z.json", "p_ge_canonical": 0.7142857142857143, "runs": 7}, "robustness": {"path": "research_state/multiyear_robustness_battery_hyperliquid_native_20261115T155522Z.json"}}

### c12_20_5 (RSI 20, target 5)
- Trades 6, episodes 3 (sizes [2, 1, 3]), crash days 4. Census: events 43, signal-gate 7, blocks {'trade_opened': 6, 'bounce_not_confirmed': 36, 'one_position_per_coin': 1}.
- Spot ep-bootstrap: obs -12104.27, CI95 [-32408.77, 1840.93], P(>0)=0.038 (n_ep=3).
- Hedge ep-bootstrap: obs 17304.32, CI95 [-261.94, 42748.19], P(>0)=0.962 (n_ep=3).
- Rebound ep-bootstrap: obs -2710.00, CI95 [-8129.99, 0.00], P(>0)=0.000 (n_ep=3).
- Total ep-bootstrap: obs 7596.40, CI95 [3681.75, 10339.42], P(>0)=1.000 (n_ep=3).
- **Note:** UNDERPOWERED/FRAGILE: dependence-aware inference limited by small episode/trade count on 283d native window; CIs/permutation/placebo (where available) should be interpreted as non-decision-grade.
- **Note:** HEDGE_MASKED_TOTAL: spot coin PnL negative while total positive (ETH hedge/rebound drive headline); no spot-alpha claim.

### c12_22_9 (RSI 22, target 9)
- Trades 6, episodes 3 (sizes [2, 1, 3]), crash days 4. Census: events 76, signal-gate 7, blocks {'trade_opened': 6, 'bounce_not_confirmed': 69, 'one_position_per_coin': 1}.
- Spot ep-bootstrap: obs -3968.80, CI95 [-32408.77, 26247.32], P(>0)=0.371 (n_ep=3).
- Hedge ep-bootstrap: obs 8261.31, CI95 [-27390.97, 42748.19], P(>0)=0.629 (n_ep=3).
- Rebound ep-bootstrap: obs 0.00, CI95 [0.00, 0.00], P(>0)=0.000 (n_ep=3).
- Total ep-bootstrap: obs 4292.50, CI95 [-1143.66, 10339.42], P(>0)=0.962 (n_ep=3).
- **Note:** UNDERPOWERED/FRAGILE: dependence-aware inference limited by small episode/trade count on 283d native window; CIs/permutation/placebo (where available) should be interpreted as non-decision-grade.
- **Note:** HEDGE_MASKED_TOTAL: spot coin PnL negative while total positive (ETH hedge/rebound drive headline); no spot-alpha claim.

### c12_22_5 (RSI 22, target 5)
- Trades 6, episodes 3 (sizes [2, 1, 3]), crash days 4. Census: events 76, signal-gate 7, blocks {'trade_opened': 6, 'bounce_not_confirmed': 69, 'one_position_per_coin': 1}.
- Spot ep-bootstrap: obs -12104.27, CI95 [-32408.77, 1840.93], P(>0)=0.038 (n_ep=3).
- Hedge ep-bootstrap: obs 17304.32, CI95 [-261.94, 42748.19], P(>0)=0.962 (n_ep=3).
- Rebound ep-bootstrap: obs -2710.00, CI95 [-8129.99, 0.00], P(>0)=0.000 (n_ep=3).
- Total ep-bootstrap: obs 7596.40, CI95 [3681.75, 10339.42], P(>0)=1.000 (n_ep=3).
- **Note:** UNDERPOWERED/FRAGILE: dependence-aware inference limited by small episode/trade count on 283d native window; CIs/permutation/placebo (where available) should be interpreted as non-decision-grade.
- **Note:** HEDGE_MASKED_TOTAL: spot coin PnL negative while total positive (ETH hedge/rebound drive headline); no spot-alpha claim.

### c12_25_9 (RSI 25, target 9)
- Trades 17, episodes 10 (sizes [1, 2, 3, 4, 1, 2, 1, 1, 1, 1]), crash days 11. Census: events 202, signal-gate 33, blocks {'trade_opened': 17, 'bounce_not_confirmed': 169, 'one_position_per_coin': 16}.
- Spot ep-bootstrap: obs 6836.44, CI95 [-42838.86, 56387.04], P(>0)=0.607 (n_ep=10).
- Hedge ep-bootstrap: obs 4762.24, CI95 [-41961.96, 48905.30], P(>0)=0.592 (n_ep=10).
- Rebound ep-bootstrap: obs 11904.32, CI95 [-6854.13, 39558.14], P(>0)=0.775 (n_ep=10).
- Total ep-bootstrap: obs 23244.22, CI95 [-22799.52, 79978.91], P(>0)=0.803 (n_ep=10).
- **Note:** UNDERPOWERED/FRAGILE: dependence-aware inference limited by small episode/trade count on 283d native window; CIs/permutation/placebo (where available) should be interpreted as non-decision-grade.
- **Note:** POSITIVE_SPOT_IN_SAMPLE: spot coin PnL positive in this sample; requires dependence-aware validation and is not GO by itself.

### c12_25_5 (RSI 25, target 5)
- Trades 17, episodes 10 (sizes [1, 2, 3, 4, 1, 2, 1, 1, 1, 1]), crash days 11. Census: events 202, signal-gate 33, blocks {'trade_opened': 17, 'bounce_not_confirmed': 169, 'one_position_per_coin': 16}.
- Spot ep-bootstrap: obs -17462.39, CI95 [-53443.54, 16112.88], P(>0)=0.168 (n_ep=10).
- Hedge ep-bootstrap: obs 17159.13, CI95 [-13608.38, 52602.16], P(>0)=0.843 (n_ep=10).
- Rebound ep-bootstrap: obs -15138.93, CI95 [-34797.40, 621.76], P(>0)=0.027 (n_ep=10).
- Total ep-bootstrap: obs -3596.44, CI95 [-27390.23, 15394.83], P(>0)=0.398 (n_ep=10).
- **Note:** UNDERPOWERED/FRAGILE: dependence-aware inference limited by small episode/trade count on 283d native window; CIs/permutation/placebo (where available) should be interpreted as non-decision-grade.

### c12_30_9 (RSI 30, target 9)
- Trades 57, episodes 19 (sizes [1, 6, 7, 5, 4, 5, 2, 3, 1, 1, 2, 4, 2, 4, 3, 1, 2, 2, 2]), crash days 31. Census: events 671, signal-gate 148, blocks {'trade_opened': 57, 'bounce_not_confirmed': 523, 'one_position_per_coin': 79, 'portfolio_admission': 12}.
- Spot ep-bootstrap: obs -65465.79, CI95 [-146015.96, 12312.50], P(>0)=0.049 (n_ep=19).
- Hedge ep-bootstrap: obs 25822.09, CI95 [-34584.85, 84557.71], P(>0)=0.806 (n_ep=19).
- Rebound ep-bootstrap: obs -6896.95, CI95 [-45957.46, 32578.62], P(>0)=0.361 (n_ep=19).
- Total ep-bootstrap: obs -11453.31, CI95 [-71682.79, 59746.04], P(>0)=0.354 (n_ep=19).
- **Note:** UNDERPOWERED/FRAGILE: dependence-aware inference limited by small episode/trade count on 283d native window; CIs/permutation/placebo (where available) should be interpreted as non-decision-grade.

### c12_30_5 (RSI 30, target 5)
- Trades 58, episodes 19 (sizes [2, 6, 7, 5, 4, 5, 2, 3, 1, 1, 2, 4, 2, 4, 3, 1, 2, 2, 2]), crash days 32. Census: events 671, signal-gate 148, blocks {'trade_opened': 58, 'bounce_not_confirmed': 523, 'one_position_per_coin': 80, 'portfolio_admission': 10}.
- Spot ep-bootstrap: obs -86408.96, CI95 [-159892.91, -17185.70], P(>0)=0.007 (n_ep=19).
- Hedge ep-bootstrap: obs 47863.20, CI95 [-3451.97, 100085.18], P(>0)=0.966 (n_ep=19).
- Rebound ep-bootstrap: obs -33838.60, CI95 [-78335.51, 7181.81], P(>0)=0.057 (n_ep=19).
- Total ep-bootstrap: obs -32741.08, CI95 [-75299.74, 3361.78], P(>0)=0.040 (n_ep=19).
- **Note:** UNDERPOWERED/FRAGILE: dependence-aware inference limited by small episode/trade count on 283d native window; CIs/permutation/placebo (where available) should be interpreted as non-decision-grade.

## Lead assessment
- **best_total_in_sample:** c12_25_9 (rsi 25, target 9) total +23244.22 but driven by positive spot (+6836.44) + rebound (+11904.32) + small hedge (+4762.24) across 17 trades / 10 episodes / 11 crash days; episode-block bootstrap CIs must be consulted—discovery/hypothesis-generating, not validated GO.
- **hedge_masked_configs:** c12_20_5/c12_22_5 totals positive but spot deeply negative and rebound negative (hedge-masked).
- **negative_configs:** c12_25_5 and all rsi30 configs negative total with large negative spot.
- **canonical:** anchor_20_9 remains NO_GO/FRAGILE_NOT_DECISION_GRADE (0/7) per C11.3 refs.

**Caveat:** All C12 configs are discovery on a 283d/low-episode native sample. Episode-block bootstrap CIs that span 0 or rest on few episodes are **underpowered / not decision-grade**. No GO claim from hedge-masked totals or in-sample point estimates.
