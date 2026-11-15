# C10.2 — Full-Portfolio Placebo (Binance UM Multi-Year, Cross-Venue)

**Generated (UTC):** 2026-11-15T12:26:21.844233+00:00
**Provenance:** Real Binance UM exchange data, non-synthetic; CROSS-VENUE vs Hyperliquid spec; NOT Hyperliquid performance evidence.
**Mode:** `deterministic_seeded_draws:200_choose_42_of_64` (exact enumeration infeasible; deterministic seeded subset)
**Verdict:** `underpowered`
**is_hyperliquid_venue_data:** false

## Canonical
- Trades: **42**, total PnL: **21994.064361**
- Replay: 42 trades, 21994.064361

## Placebo
- Pool signal-gate events: **64**, choose_k (canonical admitted): **42**
- Runs: **200**, seed: 20261114
- Mean: **18950.05**, median: **19201.18**, p05: **-2969.56**, p95: **40497.29**
- Canonical percentile: **0.5850**, p(placebo>=canonical): **0.4150**
- P(placebo>0): **0.9350**

## Limitation
- Exact enumeration infeasible; deterministic seeded random subsets used (documented seed and count).
- Tests admission/cap/occupancy selection within the observed gate-passing pool, not temporal crash timing.
- CROSS-VENUE Binance UM; NOT Hyperliquid performance evidence.

## Reproduction
```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_binance_um_multiyear.py --draws 200 --seed 20261114 --out placebo_portfolio_binance_um_multiyear
```
