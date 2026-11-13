# Full-Portfolio Crash-Rebound Placebo — Real OKX 283d

**Generated (UTC):** 2026-11-13T20:54:10.875695+00:00
**Seed:** 20261113
**Mode:** exact_enumeration:165_subsets
**Provenance caveat:** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence.

## What this fixes

The per-event null sizes each trade at 1.25% of 24h volume with **no portfolio gross cap** (desired notionals up to $7.29M), while the canonical portfolio caps gross exposure at **$120k** (120% of $100k). Comparing the 8-trade portfolio PnL to that uncapped per-event null is a sizing artifact, not evidence. This placebo runs the **real portfolio engine** with the same gates, sizing, cap, occupancy, hedge, fees, funding and liquidation.

## Canonical baseline (must reproduce exactly)

- Trades: **8**, total PnL: **9159.691935**
- Canonical artifact sha256: `57973b0c4a0d68c783cd4dffd1c6817d20ad4613bee6e2e28939f9b497d2f9b8`
- Admitted keys: AVAX:1026, BCH:1026, BCH:3584, ETH:763, LINK:884, SOL:722, SOL:884, SOL:1028
- Memoized replay: 8 trades, PnL 9159.691935 — exact match.

## Placebo design (gate-preserving)

All 11 signal-gate-passing events are the only bars where a spec-compliant trade can open. The canonical run admitted 8; 3 were blocked by one-position-per-coin. Every 8-of-11 subset is run with the other signals masked, preserving the $5M trailing-24h volume gate, bounce/regime gates, 1.25% volume sizing, 120% gross cap, equal-share cuts, max positions, ETH hedge, fees, funding and liquidation. With n=11 and k=8 there are C(11,8)=165 subsets, so this is an **exact enumeration**, not a Monte Carlo estimate.

## Result

- Placebo runs: **165**
- Placebo total PnL: mean **8746.21**, median **9287.25**, p05 **5807.36**, p95 **11360.11**, min **3988.13**, max **11795.92**
- Canonical 9159.69 percentile: **0.4545** (P(placebo >= canonical) = **0.5515**, P(>) = 0.5455)
- P(placebo total PnL > 0): **1.0000**
- 95% placebo interval: [4114.36, 11521.55]
- Trade-count distribution: {'6': 81, '5': 20, '7': 58, '8': 6}
- Symbol frequency: {'BCH': 164, 'ETH': 120, 'LINK': 120, 'SOL': 165, 'AVAX': 120}

## Per-event null reconciliation

The per-event null is **not** a portfolio null. It sizes each trade at 1.25% of 24h volume with no gross cap (desired notionals up to $7.29M), while the canonical portfolio caps gross at $120k. Its mean (~$232k) is a sizing artifact; the exact full-portfolio placebo above is the valid comparison.

## Interpretation

The canonical 8-trade portfolio result sits near the middle of the exact full-portfolio placebo distribution. It is **not distinguishable from the admission/cap/occupancy outcome of a random 8-of-11 gate-passing subset**. This is consistent with the per-event null and the symbol-block bootstrap: the sample remains **`underpowered` / not decision-grade**. The +9.16% return must not be presented as validated edge.

## Limitations

- Conditions on the observed 11 signal-gate events and 8 canonical trades; it tests admission/cap/occupancy selection, not the temporal crash-rebound edge versus random event times.
- Only 5 traded symbols and 11 gate-passing events remain; the placebo cannot create statistical power that the sample does not contain.
- Memoized generate_signal is exact for the canonical config/data (verified by exact canonical replay) but is not a general accelerator for other configs.
- Cross-venue OKX cache; NOT Hyperliquid performance evidence.
