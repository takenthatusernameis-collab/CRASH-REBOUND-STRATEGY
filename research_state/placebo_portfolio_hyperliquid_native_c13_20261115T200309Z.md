# Full-Portfolio Crash-Rebound Placebo — Real Hyperliquid (Ironflow node-derived, native)

**Generated (UTC):** 2026-11-15T20:04:12.406135+00:00
**Seed:** 20261115
**Mode:** random_draws:200_seed:20261115
**Config (config-matched real engine):** RSI<25, target 9.0
**Provenance caveat:** Real Hyperliquid (Ironflow node-derived, native) data, non-synthetic; node-derived (Ironflow HF, CC BY 4.0), NOT the venue's own candleSnapshot; Hyperliquid-native evidence (not cross-venue).

## What this fixes

The per-event null sizes each trade at 1.25% of 24h volume with **no portfolio gross cap** (desired notionals up to $7.29M), while the canonical portfolio caps gross exposure at **$120k** (120% of $100k). Comparing the portfolio PnL to that uncapped per-event null is a sizing artifact, not evidence. This placebo runs the **real portfolio engine** with the same gates, sizing, cap, occupancy, hedge, fees, funding and liquidation.

## Canonical baseline (must reproduce exactly)

- Trades: **17**, total PnL: **23244.224035**
- Canonical artifact sha256: `72d98f0d1664ed4c53020ac37ec34ded2cd13257e4b3489c4eec43db56caf9a5`
- Admitted keys: BTC:1028, BTC:1150, BTC:2342, BTC:3956, ETH:763, ETH:885, ETH:1028, ETH:1562, ETH:3577, HYPE:5022, SOL:723, SOL:884, SOL:1028, SOL:1565, ZEC:467, ZEC:885, ZEC:1028
- Memoized replay: 17 trades, PnL 23244.224035 — exact match.

## Placebo design (gate-preserving)

All 33 signal-gate-passing events are the only bars where a spec-compliant trade can open. The canonical run admitted 17. Every 17-of-33 subset is run with the other signals masked, preserving the $5M trailing-24h volume gate, bounce/regime gates, 1.25% volume sizing, 120% gross cap, equal-share cuts, max positions, ETH hedge, fees, funding and liquidation. This is an **seeded Monte Carlo** over C(33,17)=1166803110 subsets.

## Result

- Placebo runs: **200**
- Placebo total PnL: mean **16174.90**, median **17753.11**, p05 **-5959.77**, p95 **33351.89**, min **-13836.15**, max **41794.31**
- Canonical 23244.22 percentile: **0.6800** (P(placebo >= canonical) = **0.3200**, P(>) = 0.3200)
- P(placebo total PnL > 0): **0.8750**
- 95% placebo interval: [-8535.90, 35076.30]
- Trade-count distribution: {'12': 59, '11': 55, '10': 22, '13': 52, '8': 1, '9': 3, '14': 6, '16': 1, '15': 1}
- Symbol frequency: {'BTC': 199, 'ETH': 200, 'SOL': 200, 'ZEC': 184, 'HYPE': 119}

## Per-event null reconciliation

The per-event null is **not** a portfolio null. It sizes each trade at 1.25% of 24h volume with no gross cap (desired notionals up to $7.29M), while the canonical portfolio caps gross at $120k. Its mean is a sizing artifact; the exact full-portfolio placebo above is the valid comparison.

## Interpretation

The canonical 17-trade portfolio result sits at percentile **0.6800** of the full-portfolio placebo distribution (P(placebo >= canonical) = **0.3200**). It is **not distinguishable** from the admission/cap/occupancy outcome of a random 17-of-33 gate-passing subset; the sample remains **`underpowered` / not decision-grade**.

## Limitations

- Conditions on the observed 33 signal-gate events and 17 canonical trades; it tests admission/cap/occupancy selection, not the temporal crash-rebound edge versus random event times.
- Only 5 traded symbols and 33 gate-passing events remain; the placebo cannot create statistical power that the sample does not contain.
- Memoized generate_signal is exact for the run config/data (verified by exact canonical replay) but is not a general accelerator for other configs.
