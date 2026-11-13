# Placebo / Null & Bootstrap — Real OKX 283d (post-Phase L)

**Generated (UTC):** 2026-11-13T20:54:59.279838+00:00
**Seed:** 20261113
**Provenance caveat:** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence.

## Canonical baseline (compared)
- Trades: 8, total PnL: **9159.691935** (mean/trade 1144.961492)
- Canonical sha256: `57973b0c4a0d68c783cd4dffd1c6817d20ad4613bee6e2e28939f9b497d2f9b8`

## Gate-preserving proof ($5M trailing-24h gate NOT relaxed)
All placebo candidates drawn from J1 census events with volume_gate_pass=true and trailing_24h_volume_usd >= 5,000,000; $5M gate NOT relaxed. Per-event exits simulated via generate_signal+backtest_simple on cached bars with canonical StrategyConfig.
- **Volume-pass pool:** n=11, all_volume_gate_pass=True, all_trailing_24h>=5M=True, bounce_confirmed=11, regime_min_price_ok=11
- **Bounce-confirmed pool:** n=11, all_volume_gate_pass=True, all_trailing_24h>=5M=True, bounce_confirmed=11, regime_min_price_ok=11

## Per-event exit-model null (matched k=8 draws, bootstrap)
| Pool | sim-ok N | trials | real total PnL | null mean | null p05 | null p95 | P(null >= real) | real percentile (<=) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| volume_pass (187 events) | 11 | 2000 | 9159.69 | 232103.21 | 55419.94 | 443209.97 | 0.9865 | 0.0135 |
| bounce_confirmed (39 events) | 11 | 2000 | 9159.69 | 236055.20 | 45811.89 | 464286.46 | 0.9850 | 0.0150 |

**Interpretation note:** per-event independent exit simulation (no portfolio cap/occupancy/admission interactions). Complementary to, not replacement for, a full-portfolio placebo. Canonical 9159.69 remains the compared real outcome.

## Symbol-block bootstrap (whole-symbol resampling, dependence-aware)
- Symbols (5): AVAX, BCH, ETH, LINK, SOL
- Symbol trade counts: {'AVAX': 1, 'BCH': 2, 'ETH': 1, 'LINK': 1, 'SOL': 3}
- Trials: 2000, seed: 20261113
- 95% CI total PnL: [-2026.39, 19249.18]
- P(total PnL > 0): 0.9420
- Mean/median: 9152.98 / 9159.69

## Trade-level bootstrap (reference recompute)
- Trials 10000, 95% CI [-930.66, 19152.38], P(>0)=0.9633. Reference recompute; canonical Phase L artifact remains authoritative for that analysis.

## Limitations
- Per-event exit-model null is independent per-event simulation (no portfolio cap/occupancy interaction across concurrent positions); complementary to, not replacement for, full-portfolio placebo.
- n=8 realized trades and 5 traded symbols remain severely underpowered regardless of bootstrap method.
- Bounce-confirmed pool (n=39 events, 11 sim-ok) overlaps with signal-admission logic; interpretation must account for selection funnel.
- Cross-venue OKX cache; NOT Hyperliquid performance evidence.
