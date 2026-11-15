# C10.2 — Full-Portfolio Placebo (Hyperliquid (Ironflow node-derived, native) Multi-Year, Hyperliquid-native)

**Generated (UTC):** 2026-11-15T15:56:38.337353+00:00
**Provenance:** Real Hyperliquid (Ironflow node-derived, native) data, non-synthetic; node-derived (Ironflow HF, CC BY 4.0), NOT the venue's own candleSnapshot; Hyperliquid-native evidence (not cross-venue).
**Mode:** `exact_enumeration:7_choose_6_of_7` (exact enumeration infeasible; deterministic seeded subset)
**Verdict:** `underpowered`
**is_hyperliquid_venue_data:** true

## Canonical
- Trades: **6**, total PnL: **4292.503122**
- Replay: 6 trades, 4292.503122

## Placebo
- Pool signal-gate events: **7**, choose_k (canonical admitted): **6**
- Runs: **7**, seed: 20261115
- Mean: **4211.38**, median: **4414.12**, p05: **2915.29**, p95: **5171.94**
- Canonical percentile: **0.4286**, p(placebo>=canonical): **0.7143**
- P(placebo>0): **1.0000**

## Limitation
- Exact enumeration over all 7 subsets; no Monte Carlo error.
- Tests admission/cap/occupancy selection within the observed gate-passing pool, not temporal crash timing.
- Hyperliquid-native (Ironflow node-derived) cache; NOT cross-venue.

## Reproduction
```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_binance_um_multiyear.py --cache-dir research_state/cache/hyperliquid_ironflow_native_20251220_20260928 --universe research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json --census research_state/crash_event_census_hyperliquid_ironflow_native_20261115T155226Z.json --campaign research_state/campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json --venue-label 'Hyperliquid (Ironflow node-derived, native)' --draws 200 --seed 20261115 --jobs 4 --out placebo_portfolio_hyperliquid_native_20261115T155625Z
```
