# Full-Portfolio Crash-Rebound Placebo — Hyperliquid Exploratory Spec-Literal Next-Open

**Generated (UTC):** 2026-11-14T18:20:23.955129+00:00
**Mode:** exact_enumeration:28_subsets
**Label:** `NOT_EVIDENCE_PLACEBO`
**Provenance caveat:** Exploratory full-portfolio placebo on the retained PARTIAL aligned Hyperliquid chain; real fetched candles, non-synthetic; NOT the 283-day spec window and NOT performance evidence. Never use for validation or capital allocation. Canonical exploratory baseline is unchanged.

## What this fixes

C1 closed the exploratory spec-literal next-open adjudication (8 signals -> 2 trades, total PnL -$2,671) and recorded the episode audit as NOT_APPLICABLE (n=2 < 10). This placebo runs the **real portfolio engine** on the retained PARTIAL Hyperliquid chain under the same gates, sizing, 120% gross cap, ETH hedge, fees, funding and liquidation, varying only which of the volume-passing crash-rebound signal bars are admitted. It isolates admission/cap/occupancy selection, not the temporal edge versus random event times.

## Canonical baseline (must reproduce exactly)

- Trades: **2**, total PnL: **-2670.756788**
- Canonical campaign artifact sha256: `6d2a934f0270e58bf3e400abda42c8eed5aba2f461c94760ef83987cdd91d686`
- Memoized replay: 2 trades, PnL -2670.756788 — exact match.

## Placebo design (gate-preserving)

All 8 RSI(21)<20 bars passing the trailing-24h >= $5M volume gate are the only bars where a spec-compliant trade can open. The canonical run admitted 2 (rest blocked by ETH hedge/120% cap/ETH availability). Every 2-of-n subset is run with the other signals masked, preserving every gate and the portfolio engine. With n=8 and k=2 there are C(n,2)=28 subsets, so this is an **exact enumeration**, not a Monte Carlo estimate.

## Result

- Placebo runs: **28**
- Placebo total PnL: mean **-2901.08**, median **-3086.07**, p05 **-3278.34**, p95 **-2550.39**, min **-3287.69**, max **559.36**
- Canonical -2670.76 percentile: **0.8929** (P(placebo <= canonical) = **0.8929**, P(>=) = 0.1429)
- P(placebo total PnL > 0): **0.0357**
- 95% placebo interval: [-3287.69, -1523.74]
- Trade-count distribution: {'1': 16, '2': 12}
- Symbol frequency: {'BTC': 27, 'BCH': 13}

## Interpretation

The canonical exploratory -2670.76 result sits at percentile 0.8929 of the exact full-portfolio placebo distribution. With only 2 independent crash episodes traded (C1-T1), this remains **`underpowered` / not decision-grade**; the placebo cannot create statistical power the sample does not contain. **Not** validation, **not** capital-allocation evidence.

## Limitations

- Conditions on the observed volume-passing crash-rebound signal bars on the retained PARTIAL chain; tests admission/cap/occupancy selection, not the temporal crash-rebound edge versus random event times.
- Only 2 independent crash episodes traded (C1-T1); the placebo cannot create statistical power the sample does not contain.
- Memoized generate_signal is exact for the exploratory config/data (verified by exact canonical replay) but is not a general accelerator for other configs.
- Retained PARTIAL window, NOT the 283-day spec window; NEVER Hyperliquid performance evidence.
