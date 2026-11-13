# Parameter Sensitivity Sweep — Real OKX 283-Day Campaign (Phase J2)

**Generated (UTC):** 2026-11-13T19:06:48.063304+00:00
**Provenance caveat:** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence.

One-factor-at-a-time around the spec baseline. Every run re-executes the full bar-by-bar portfolio simulation from the committed on-disk manifest/cache/universe. No canonical artifact was overwritten; per-run outputs live in `research_state/sweep_runs/`.

**Runs executed:** 9 (baseline + 8 variants)
**Resumed from disk:** 1 run(s) reused
**Wall clock:** 1623.1s across 4 workers (sequential-equivalent 7403.35s)
**Inputs:** manifest `research_state/cache/okx_1h_full_20251220_20260928/provenance.json`
Universe `/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY/research_state/universe_okx_full_verified.json` (54 symbols)
Canonical campaign for reference: `research_state/campaign_results_real_okx_full.json` (`results.num_trades=8`, `results.total_pnl=9159.691934882958`)

## Baseline vs variants

| Run | Change | Trades | Total return % | Annualized % | Worst DD % | Win rate | PF | Buy PnL | Short PnL | Runtime s |
|---|---|---|---|---|---|---|---|---|---|---|
| `baseline_spec` | Spec baseline: RSI(21)<20, +9%/50h, short -9%/48h, 1.25% sizing, hedge 3x, 120% cap | 8 | 9.1597 | 22.5995 | -2.0275 | 0.5000 | 5.2335 | 6,171.47 | 2,988.22 | 981.03 |
| `rsi18_maxpos8` | RSI<18 with max 8 concurrent positions | 2 | n/a | n/a | -0.0679 | 0.5000 | 83.0933 | -72.00 | 5,983.03 | 799.43 |
| `rsi25_maxpos3` | RSI<25 with max 3 concurrent positions | 25 | 19.3620 | 50.9041 | -16.6177 | 0.5200 | 1.6400 | -7,450.04 | 26,812.01 | 800.38 |
| `rsi25_maxpos8` | RSI<25 with max 8 concurrent positions | 33 | 23.4387 | 11.4160 | -18.3393 | 0.5455 | 1.6788 | -7,975.68 | 31,414.42 | 801.77 |
| `rsi18_maxpos3` | RSI<18 with max 3 concurrent positions | 2 | n/a | n/a | -0.0679 | 0.5000 | 83.0933 | -72.00 | 5,983.03 | 813.75 |
| `rsi25_target12` | RSI<25 with +12% buy target | 30 | 18.1932 | 8.9598 | -18.9986 | 0.5000 | 1.5269 | -2,868.99 | 21,062.22 | 799.42 |
| `rsi25_target6` | RSI<25 with +6% buy target | 30 | -1.2092 | -0.6226 | -20.9023 | 0.5667 | 0.9648 | -8,587.64 | 7,378.42 | 800.6 |
| `rsi15_maxpos3` | RSI<15 with max 3 concurrent positions | 2 | n/a | n/a | -0.0679 | 0.5000 | 83.0933 | -72.00 | 5,983.03 | 800.82 |
| `rsi15_maxpos8` | RSI<15 with max 8 concurrent positions | 2 | n/a | n/a | -0.0679 | 0.5000 | 83.0933 | -72.00 | 5,983.03 | 806.15 |

## Deltas vs baseline (total return percentage points, trade count)

| Run | Δ total return (pp) | Δ annualized (pp) | Δ worst DD (pp) | Δ trades | Moves result? |
|---|---|---|---|---|---|
| `rsi18_maxpos8` | n/a | n/a | 1.9596 | -6 | yes |
| `rsi25_maxpos3` | 10.2023 | 28.3046 | -14.5902 | +17 | yes |
| `rsi25_maxpos8` | 14.2791 | -11.1835 | -16.3118 | +25 | yes |
| `rsi18_maxpos3` | n/a | n/a | 1.9596 | -6 | yes |
| `rsi25_target12` | 9.0335 | -13.6397 | -16.9711 | +22 | yes |
| `rsi25_target6` | -10.3689 | -23.2221 | -18.8748 | +22 | yes |
| `rsi15_maxpos3` | n/a | n/a | 1.9596 | -6 | yes |
| `rsi15_maxpos8` | n/a | n/a | 1.9596 | -6 | yes |

## Spec-locked knobs (not swept — rejected by design)

`StrategyConfig` refuses to treat these as free parameters when volume-based sizing is enabled, so a mutated value is a spec bypass attempt. They are recorded, not run:

| Knob | Value | Error |
|---|---|---|
| `position_size_0p5pct` | `{"position_size_pct_of_daily_volume": 0.5}` | ValueError: position_size_pct_of_daily_volume 0.5 is not the spec 1.25% of 24h volume; volume-based sizing is not a free parameter in spec-compliant paths |
| `position_size_2p0pct` | `{"position_size_pct_of_daily_volume": 2.0}` | ValueError: position_size_pct_of_daily_volume 2.0 is not the spec 1.25% of 24h volume; volume-based sizing is not a free parameter in spec-compliant paths |

## Which knobs move results, which do not

**Material knobs** (|Δ total return| ≥ 0.5pp, any trade-count change, or |Δ total PnL| ≥ 1% of capital when return is not derivable), ranked:

- `rsi25_maxpos8` (RSI<25 with max 8 concurrent positions): Δ return +14.2790pp, Δ trades +25, Δ PnL +14279.05
- `rsi25_target6` (RSI<25 with +6% buy target): Δ return -10.3689pp, Δ trades +22, Δ PnL -10368.92
- `rsi25_maxpos3` (RSI<25 with max 3 concurrent positions): Δ return +10.2023pp, Δ trades +17, Δ PnL +10202.28
- `rsi25_target12` (RSI<25 with +12% buy target): Δ return +9.0335pp, Δ trades +22, Δ PnL +9033.54
- `rsi18_maxpos8` (RSI<18 with max 8 concurrent positions): Δ return n/a, Δ trades -6, Δ PnL -3248.67
- `rsi18_maxpos3` (RSI<18 with max 3 concurrent positions): Δ return n/a, Δ trades -6, Δ PnL -3248.67
- `rsi15_maxpos3` (RSI<15 with max 3 concurrent positions): Δ return n/a, Δ trades -6, Δ PnL -3248.67
- `rsi15_maxpos8` (RSI<15 with max 8 concurrent positions): Δ return n/a, Δ trades -6, Δ PnL -3248.67

**Immaterial knobs** (|Δ total return| < 0.5pp and identical trade count):

- none


## Caveats

- Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence.
- Single-factor variation only: no interaction effects are measured; a knob that is immaterial alone may matter conditional on another.
- Horizon is the realized-trade horizon, not the full 283-day window (no trades in the final ~4 months).
- Per-run full result JSON is retained under research_state/sweep_runs/ for audit.
