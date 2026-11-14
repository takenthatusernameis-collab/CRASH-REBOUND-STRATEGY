# Execution-Friction Stress (Hyperliquid, retained chain) — 2026-11-14T20:46:32Z

**Label:** `NOT_EVIDENCE_EXECUTION_FRICTION` — `performance_evidence=false`, `canonical_baseline_changed=false`.

Chain: `research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z` · capital $100,000 · trailing-24h floor $5,000,000

| Variant | Trades | Total PnL | Δ vs baseline | Max DD | Win rate |
|---|---|---|---|---|---|
| `baseline` | 2 | -2670.7568 | 0.0000 | -3230.1169 | 0.5000 |
| `slippage_2x` | 2 | -3050.8566 | -380.0999 | -3423.8330 | 0.5000 |
| `slippage_4x` | 2 | -3811.0720 | -1140.3153 | -3811.0720 | 0.0000 |
| `slippage_10x` | 2 | -5062.6130 | -2391.8562 | -5062.6130 | 0.0000 |
| `fee_min_10x` | 2 | -2734.0903 | -63.3335 | -3257.1646 | 0.5000 |
| `funding_3x` | 2 | -2437.7892 | 232.9676 | -3462.4088 | 0.5000 |
| `liquidation_stress` | 2 | -501.7676 | 2168.9892 | -1061.1277 | 0.5000 |
| `no_eth_hedge` | 2 | -7945.8847 | -5275.1279 | -9990.3395 | 0.5000 |
| `combined_stress` | 2 | -1310.8787 | 1359.8781 | -1738.6120 | 0.5000 |

**Range:** total PnL -7945.8847 .. -501.7676; all variants negative: True.

## Caveats

- Execution-friction stress on the retained PARTIAL aligned Hyperliquid chain using the opt-in exploratory spec-literal next-open path. Real fetched candles, non-synthetic, but NOT the 283-day spec window and NOT performance evidence. Fragility check only: never promote to evidence, never change the canonical default, never use for validation or capital allocation.
- Hourly bar simulation only: 20s order slicing and L2 book impact are NOT modeled.
- The no-ETH-hedge variant is a structural fragility probe, not a spec configuration.
