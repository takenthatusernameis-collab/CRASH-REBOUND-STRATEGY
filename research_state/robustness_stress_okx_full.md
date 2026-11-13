# Exact Robustness Stress / Power Analysis — Real OKX 283d

**Generated (UTC):** 2026-11-13T21:12:30.898987+00:00
**Seed:** 20261113
**Provenance caveat:** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence.

This is a **stress test**, not evidence of edge. It re-runs the exact full-portfolio engine (same gates, sizing, 120% gross cap, occupancy, ETH hedge, fees, funding, liquidation) after removing a symbol or a trade, and projects how much data would be needed for the bootstrap CI to exclude zero. The verdict remains **`underpowered`**.

## Canonical baseline (must reproduce exactly)

- Trades: **8**, total PnL: **9159.691935**
- Full 11-signal replay: 8 trades, PnL 9159.691935
- Canonical artifact sha256: `57973b0c4a0d68c783cd4dffd1c6817d20ad4613bee6e2e28939f9b497d2f9b8`

## Leave-one-symbol-out (exact engine re-run)

| Excluded | Total PnL | Δ vs canonical | Trades | All-signal keys masked |
|---|---:|---:|---:|---|
| AVAX | 9493.49 | +333.80 | 7 | 1 |
| BCH | 10583.22 | +1423.53 | 6 | 3 |
| ETH | 9281.33 | +121.63 | 7 | 1 |
| LINK | 10796.53 | +1636.84 | 7 | 1 |
| SOL | 3495.11 | -5664.59 | 5 | 5 |

- All LOO runs positive: **True**; min **3495.11**, max **10796.53**.

## Leave-one-trade-out (exact engine re-run)

| Excluded signal | Total PnL | Δ vs canonical | Trades |
|---|---:|---:|---:|
| AVAX:1026 | 9493.49 | +333.80 | 7 |
| BCH:1026 | 13154.73 | +3995.03 | 8 |
| BCH:3584 | 9231.70 | +72.00 | 7 |
| ETH:763 | 9281.33 | +121.63 | 7 |
| LINK:884 | 10796.53 | +1636.84 | 7 |
| SOL:722 | 9404.14 | +244.45 | 8 |
| SOL:884 | 8449.44 | -710.25 | 7 |
| SOL:1028 | 7485.96 | -1673.73 | 7 |

- All LOTO runs positive: **True**; min **7485.96**, max **13154.73**.

## Concentration-adjusted inference

- Top symbol: **SOL** (34.60% of gross |PnL|); raw share of total 50.95%.
- Top trade: **AVAX** @ 1769886000000 (PnL 3499.37, 25.95% of gross |PnL|).
- Absolute-PnL HHI: **0.2517**; effective symbols: **3.97**.
- Simple PnL without top symbol: **4492.58**; without top trade: **5660.32**.

## Power projection (bootstrap + analytic normal)

| Level | Observed n | Mean | SD | First n with bootstrap CI > 0 | n for 80% power | n for 95% power |
|---|---:|---:|---:|---:|---:|---:|
| Trade | 8 | 1144.96 | 1955.96 | 10 | 22.91 | 37.92 |
| Symbol | 5 | 1831.94 | 2693.12 | 8 | 16.96 | 28.09 |

The projection assumes future trades/symbols are drawn from the observed distribution. It is a sample-size calculation, not evidence that the edge is real.

## Expanding-window / refit walk-forward

| Prefix | Bars | Canonical PnL | Trades | Block PnL | Block trades |
|---|---:|---:|---:|---:|---:|
| 5% | 340 | 0.00 | 0 | 0.00 | 0 |
| 10% | 679 | 0.00 | 0 | 0.00 | 0 |
| 15% | 1019 | 1070.36 | 4 | 1070.36 | 4 |
| 20% | 1358 | 9231.70 | 7 | 8161.33 | 3 |
| 25% | 1698 | 9231.70 | 7 | 0.00 | 0 |
| 30% | 2038 | 9231.70 | 7 | 0.00 | 0 |
| 35% | 2377 | 9231.70 | 7 | 0.00 | 0 |
| 40% | 2717 | 9231.70 | 7 | 0.00 | 0 |
| 45% | 3056 | 9231.70 | 7 | 0.00 | 0 |
| 50% | 3396 | 9231.70 | 7 | 0.00 | 0 |
| 60% | 4075 | 9159.69 | 8 | -72.00 | 1 |
| 70% | 4754 | 9159.69 | 8 | 0.00 | 0 |
| 80% | 5434 | 9159.69 | 8 | 0.00 | 0 |
| 90% | 6113 | 9159.69 | 8 | 0.00 | 0 |
| 100% | 6792 | 9159.69 | 8 | 0.00 | 0 |

| Prefix | Best knobs | In-sample PnL | OOS block PnL | Canonical OOS block PnL |
|---|---|---:|---:|---:|
| 10% | {'max_positions': 3, 'time_exit_max_bars': 24, 'rebound_short_target_pct': 6} | 0.00 | 653.15 | 1070.36 |
| 15% | {'max_positions': 3, 'time_exit_max_bars': 50, 'rebound_short_target_pct': 6} | 1070.36 | 10234.77 | 8161.33 |
| 50% | {'max_positions': 3, 'time_exit_max_bars': 50, 'rebound_short_target_pct': 6} | 11305.14 | -72.00 | -72.00 |

Skipped blocks (no new trades to evaluate):
- 5%: next block has no new trades; out-of-sample not evaluable
- 20%: next block has no new trades; out-of-sample not evaluable
- 25%: next block has no new trades; out-of-sample not evaluable
- 30%: next block has no new trades; out-of-sample not evaluable
- 35%: next block has no new trades; out-of-sample not evaluable
- 40%: next block has no new trades; out-of-sample not evaluable
- 45%: next block has no new trades; out-of-sample not evaluable
- 60%: next block has no new trades; out-of-sample not evaluable
- 70%: next block has no new trades; out-of-sample not evaluable
- 80%: next block has no new trades; out-of-sample not evaluable
- 90%: next block has no new trades; out-of-sample not evaluable

- Refit OOS total (evaluable blocks only): **10815.92** (2 positive / 1 negative; 3 evaluable / 11 skipped).
- Canonical incremental total: **9159.69**.
- Refit scope: execution/portfolio knobs only; signal generation fixed at spec config.

## Interpretation

This stress test cannot upgrade the verdict. A result that survives every leave-one-out re-run and a refit walk-forward is more credible than one that does not, but it is still an 8-trade, 5-symbol, cross-venue OKX sample. The canonical remains **`underpowered`** until Hyperliquid-native evidence meets the GO criteria in `research_state/decision_memo_okx_full.md`.

## Limitations

- 8 trades across 5 symbols is a very small sample; LOO/LOTO re-runs cannot create information the sample does not contain.
- The bootstrap/power projection assumes future trades and symbols are drawn from the observed distribution; it is a sample-size calculation, not evidence of edge.
- The refit walk-forward varies execution/portfolio knobs only; signal generation is fixed at the canonical spec config (RSI<20, 9% target, 8x safety stop).
- Expanding-window prefixes start at bar 0 and preserve RSI warmup; trades that open in a block but do not exit by the block end are not counted.
- Cross-venue OKX cache; NOT Hyperliquid performance evidence.
