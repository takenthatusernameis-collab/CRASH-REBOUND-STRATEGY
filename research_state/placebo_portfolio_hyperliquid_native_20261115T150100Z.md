# C6-T3 — Full-Portfolio Placebo (OKX Multi-Year, Cross-Venue)

**Generated (UTC):** 2026-11-15T17:12:45.546034+00:00
**Provenance:** Real OKX exchange data, non-synthetic; CROSS-VENUE vs Hyperliquid spec; NOT Hyperliquid performance evidence.
**Mode:** `deterministic_seeded_draws:200_choose_42_of_55` (exact enumeration infeasible; deterministic seeded subset)
**Verdict:** `underpowered`

## Canonical
- Trades: **42**, total PnL: **18220.855824**
- Replay: 42 trades, 18220.855824

## Placebo
- Pool signal-gate events: **55**, choose_k (canonical admitted): **42**
- Runs: **200**, seed: 20261115
- Mean: **16162.67**, median: **15736.05**, p05: **-1736.92**, p95: **37251.48**
- Canonical percentile: **61.50%**, p(placebo>=canonical): **0.3850**
- P(placebo>0): **0.9300**

## Limitation
- C(55,42) is infeasible to enumerate exactly; deterministic seeded random subsets used (documented seed and count).
- Tests admission/cap/occupancy selection within the observed gate-passing pool, not temporal crash timing.
- CROSS-VENUE OKX; NOT Hyperliquid performance evidence.

## Reproduction
```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_okx_multiyear.py --draws 200 --seed 20261115
```
