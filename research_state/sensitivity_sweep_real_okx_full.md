# Parameter Sensitivity Sweep — Real OKX 283-Day Campaign (Phase J2)

**Generated (UTC):** 2026-11-13T18:39:22.817004+00:00
**Provenance caveat:** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence.

One-factor-at-a-time around the spec baseline. Every run re-executes the full bar-by-bar portfolio simulation from the committed on-disk manifest/cache/universe. No canonical artifact was overwritten; per-run outputs live in `research_state/sweep_runs/`.

**Runs executed:** 17 (baseline + 16 variants)
**Resumed from disk:** 16 run(s) reused
**Wall clock:** 541.37s across 4 workers (sequential-equivalent 15124.92s)
**Inputs:** manifest `research_state/cache/okx_1h_full_20251220_20260928/provenance.json`
Universe `/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY/research_state/universe_okx_full_verified.json` (54 symbols)
Canonical campaign for reference: `research_state/campaign_results_real_okx_full.json` (`results.num_trades=8`, `results.total_pnl=9159.691934882958`)

## Baseline vs variants

| Run | Change | Trades | Total return % | Annualized % | Worst DD % | Win rate | PF | Buy PnL | Short PnL | Runtime s |
|---|---|---|---|---|---|---|---|---|---|---|
| `baseline_spec` | Spec baseline: RSI(21)<20, +9%/50h, short -9%/48h, 1.25% sizing, hedge 3x, 120% cap | 8 | 9.1597 | 22.5995 | -2.0275 | 0.5000 | 5.2335 | 6,171.47 | 2,988.22 | 981.03 |
| `rsi_threshold_15` | RSI(21) crash trigger < 15 (spec 20) | 2 | n/a | n/a | -0.0679 | 0.5000 | 83.0933 | -72.00 | 5,983.03 | 981.33 |
| `rsi_threshold_18` | RSI(21) crash trigger < 18 (spec 20) | 2 | n/a | n/a | -0.0679 | 0.5000 | 83.0933 | -72.00 | 5,983.03 | 1000.48 |
| `rsi_threshold_25` | RSI(21) crash trigger < 25 (spec 20) | 30 | 17.1284 | 8.4547 | -19.1382 | 0.5000 | 1.4960 | -9,683.61 | 26,812.01 | 1040.85 |
| `buy_target_6pct` | Buy target +6% (spec +9%) | 8 | 10.7514 | 148.2089 | -1.9373 | 0.6250 | 5.7137 | 8,141.44 | 2,609.99 | 970.03 |
| `buy_target_12pct` | Buy target +12% (spec +9%) | 8 | n/a | n/a | -2.0275 | 0.5000 | 7.0020 | 12,986.09 | n/a | 928.9 |
| `buy_hold_24h` | Buy max hold 24h (spec 50h) | 8 | 8.9243 | 4.9484 | -0.2457 | 0.7500 | 36.9018 | 5,936.05 | 2,988.22 | 977.66 |
| `buy_hold_72h` | Buy max hold 72h (spec 50h) | 8 | n/a | n/a | -3.9579 | 0.6250 | 3.6301 | 7,750.67 | 2,988.22 | 986.68 |
| `short_target_6pct` | Rebound-short target -6% (spec -9%) | 8 | n/a | n/a | -2.0275 | 0.5000 | 6.1919 | 6,171.47 | 5,061.67 | 975.17 |
| `short_target_12pct` | Rebound-short target -12% (spec -9%) | 8 | 9.1597 | 22.5995 | -2.0275 | 0.5000 | 5.2335 | 6,171.47 | 2,988.22 | 852.11 |
| `short_hold_24h` | Rebound-short max hold 24h (spec 48h) | 8 | n/a | n/a | -2.0275 | 0.5000 | 5.1718 | 6,171.47 | 2,854.71 | 851.72 |
| `short_hold_72h` | Rebound-short max hold 72h (spec 48h) | 8 | n/a | n/a | -2.0275 | 0.5000 | 4.9946 | 6,171.47 | 2,471.30 | 848.2 |
| `eth_hedge_cap_1x` | ETH hedge cap 1x position (spec 3x) | 8 | 6.8062 | 16.5420 | -1.4492 | 0.6250 | 5.2153 | 3,817.99 | 2,988.22 | 855.96 |
| `eth_hedge_cap_2x` | ETH hedge cap 2x position (spec 3x) | 8 | 9.1597 | 22.5995 | -2.0275 | 0.5000 | 5.2335 | 6,171.47 | 2,988.22 | 771.04 |
| `no_rebound_short` | Rebound short disabled (spec enabled) | 8 | n/a | n/a | -2.1870 | 0.5000 | 7.5546 | 15,260.10 | n/a | 538.13 |
| `max_positions_3` | Max concurrent positions 3 (spec 5) | 8 | 9.1597 | 22.5995 | -2.0275 | 0.5000 | 5.2335 | 6,171.47 | 2,988.22 | 790.47 |
| `max_positions_8` | Max concurrent positions 8 (spec 5) | 8 | 9.1597 | 22.5995 | -2.0275 | 0.5000 | 5.2335 | 6,171.47 | 2,988.22 | 775.16 |

## Deltas vs baseline (total return percentage points, trade count)

| Run | Δ total return (pp) | Δ annualized (pp) | Δ worst DD (pp) | Δ trades | Moves result? |
|---|---|---|---|---|---|
| `rsi_threshold_15` | n/a | n/a | 1.9596 | -6 | yes |
| `rsi_threshold_18` | n/a | n/a | 1.9596 | -6 | yes |
| `rsi_threshold_25` | 7.9687 | -14.1448 | -17.1107 | +22 | yes |
| `buy_target_6pct` | 1.5917 | 125.6093 | 0.0902 | +0 | yes |
| `buy_target_12pct` | n/a | n/a | 0.0000 | +0 | no (immaterial) |
| `buy_hold_24h` | -0.2354 | -17.6511 | 1.7818 | +0 | no (immaterial) |
| `buy_hold_72h` | n/a | n/a | -1.9304 | +0 | no (immaterial) |
| `short_target_6pct` | n/a | n/a | 0.0000 | +0 | no (immaterial) |
| `short_target_12pct` | 0.0000 | 0.0000 | 0.0000 | +0 | no (immaterial) |
| `short_hold_24h` | n/a | n/a | 0.0000 | +0 | no (immaterial) |
| `short_hold_72h` | n/a | n/a | 0.0000 | +0 | no (immaterial) |
| `eth_hedge_cap_1x` | -2.3535 | -6.0576 | 0.5783 | +0 | yes |
| `eth_hedge_cap_2x` | 0.0000 | 0.0000 | 0.0000 | +0 | no (immaterial) |
| `no_rebound_short` | n/a | n/a | -0.1595 | +0 | no (immaterial) |
| `max_positions_3` | 0.0000 | 0.0000 | 0.0000 | +0 | no (immaterial) |
| `max_positions_8` | 0.0000 | 0.0000 | 0.0000 | +0 | no (immaterial) |

## Spec-locked knobs (not swept — rejected by design)

`StrategyConfig` refuses to treat these as free parameters when volume-based sizing is enabled, so a mutated value is a spec bypass attempt. They are recorded, not run:

| Knob | Value | Error |
|---|---|---|
| `position_size_0p5pct` | `{"position_size_pct_of_daily_volume": 0.5}` | ValueError: position_size_pct_of_daily_volume 0.5 is not the spec 1.25% of 24h volume; volume-based sizing is not a free parameter in spec-compliant paths |
| `position_size_2p0pct` | `{"position_size_pct_of_daily_volume": 2.0}` | ValueError: position_size_pct_of_daily_volume 2.0 is not the spec 1.25% of 24h volume; volume-based sizing is not a free parameter in spec-compliant paths |

## Which knobs move results, which do not

**Material knobs** (|Δ total return| ≥ 0.5pp, any trade-count change, or |Δ total PnL| ≥ 1% of capital when return is not derivable), ranked:

- `rsi_threshold_25` (RSI(21) crash trigger < 25 (spec 20)): Δ return +7.9687pp, Δ trades +22, Δ PnL +7968.71
- `no_rebound_short` (Rebound short disabled (spec enabled)): Δ return n/a, Δ trades +0, Δ PnL +6100.41
- `buy_target_12pct` (Buy target +12% (spec +9%)): Δ return n/a, Δ trades +0, Δ PnL +3826.40
- `rsi_threshold_15` (RSI(21) crash trigger < 15 (spec 20)): Δ return n/a, Δ trades -6, Δ PnL -3248.67
- `rsi_threshold_18` (RSI(21) crash trigger < 18 (spec 20)): Δ return n/a, Δ trades -6, Δ PnL -3248.67
- `eth_hedge_cap_1x` (ETH hedge cap 1x position (spec 3x)): Δ return -2.3535pp, Δ trades +0, Δ PnL -2353.48
- `short_target_6pct` (Rebound-short target -6% (spec -9%)): Δ return n/a, Δ trades +0, Δ PnL +2073.44
- `buy_target_6pct` (Buy target +6% (spec +9%)): Δ return +1.5917pp, Δ trades +0, Δ PnL +1591.74
- `buy_hold_72h` (Buy max hold 72h (spec 50h)): Δ return n/a, Δ trades +0, Δ PnL +1579.21

**Immaterial knobs** (|Δ total return| < 0.5pp and identical trade count):

- `short_hold_72h` (Rebound-short max hold 72h (spec 48h)): Δ return n/a, Δ trades +0
- `buy_hold_24h` (Buy max hold 24h (spec 50h)): Δ return -0.2354pp, Δ trades +0
- `short_hold_24h` (Rebound-short max hold 24h (spec 48h)): Δ return n/a, Δ trades +0
- `short_target_12pct` (Rebound-short target -12% (spec -9%)): Δ return +0.0000pp, Δ trades +0
- `eth_hedge_cap_2x` (ETH hedge cap 2x position (spec 3x)): Δ return +0.0000pp, Δ trades +0
- `max_positions_3` (Max concurrent positions 3 (spec 5)): Δ return +0.0000pp, Δ trades +0
- `max_positions_8` (Max concurrent positions 8 (spec 5)): Δ return +0.0000pp, Δ trades +0


## Caveats

- Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence.
- Single-factor variation only: no interaction effects are measured; a knob that is immaterial alone may matter conditional on another.
- Horizon is the realized-trade horizon, not the full 283-day window (no trades in the final ~4 months).
- Per-run full result JSON is retained under research_state/sweep_runs/ for audit.
