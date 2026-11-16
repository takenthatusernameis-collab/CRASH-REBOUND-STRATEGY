# C15 Acquisition Attempt — Hyperliquid-native window extension (evidenced)

- **Campaign:** C15 (active heavy)
- **Generated (UTC):** 2026-11-16T02:40:01Z
- **Goal:** extend verified Hyperliquid-native 1h evidence beyond 2025-12-20 toward **≥2023-01-01** to reach n≥4 independent crash episodes (CI-excluding-zero feasible) with $5M/spec defaults unchanged.

## T1 attempts (executed)

### 1) HuggingFace Ironflow native candles probe
- **Source:** `ironflow/hyperliquid-candles-1h` (CC BY 4.0), node-derived Hyperliquid-native perps (publisher compares hour-by-hour with Hyperliquid candleSnapshot). Verified native; not venue candleSnapshot endpoint.
- **Commands:**
  - `PYTHONPATH=. /tmp/crs-venv/bin/python -c "from datasets import load_dataset; ds=load_dataset('ironflow/hyperliquid-candles-1h',split='train'); print(ds.column_names,len(ds)); print(min(ds['timestamp']),max(ds['timestamp']))"`
  - `PYTHONPATH=. /tmp/crs-venv/bin/python -c "from huggingface_hub import HfApi; print([d.id for d in HfApi().list_datasets(author='ironflow')])"`
- **Observed:** datasets by author = ['ironflow/hyperliquid-liquidations', 'ironflow/hyperliquid-funding', 'ironflow/hyperliquid-candles-1h', 'ironflow/hyperliquid-open-interest', 'ironflow/hyperliquid-trades', 'ironflow/hyperliquid-outcomes']; search('hyperliquid candles') = ['ironflow/hyperliquid-candles-1h']; rows=3,641,742; columns=['timestamp', 'market', 'coin', 'dex', 'market_class', 'open', 'high', 'low', 'close', 'volume', 'trades']; **timestamp range 2025-05-25T14:00:00Z .. 2026-10-31T23:00:00Z**.
- **Outcome:** `NOT_ACQUIRABLE_FOR_EXTENSION_TARGET`. Covers 2025-12-20..2026-09-28 spec window but **cannot reach ≥2023-01-01** (earliest 2025-05-25). Same source already ingested as widest C14 archive `research_state/archives/hyperliquid_ironflow_wide_20261115T214900Z` (197 files, 113 selected @ $5M).

### 2) Hyperliquid public API retention probe (read-only)
- **Command:** `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py`
- **Artifact:** `research_state/hyperliquid_retention_probe.json` (generated 2026-11-16T02:29:56Z)
- **Observed:** full_window_served=False; expected_hourly_bars=6792; max_bars_returned=3849; missing_early_bars=2943; earliest_served_start_utc=2026-04-21T15:00:00Z; perps 26/235 passing gate probed=26.
- **Outcome:** `BLOCKED_API_RETENTION_MOVING_TAIL`. Cannot supply spec prefix or multiyear history.

## Conclusion (T3 evidenced hard blocker)
- **Extended native archive ≥2023-01-01 acquirable:** **NO**.
- **Reason:** No verified Hyperliquid-native hourly OHLCV source covering ≥2023-01-01 is reachable (API moving tail from ~2026-04-21; Ironflow candles start 2025-05-25). C14 already exhausted the widest available native 283d window (197-file/113-symbol, 3 episodes / 4 days / 7 trades — UNDERPOWERED).
- **T2 (full battery on extended native):** not executed (no extended native evidence).
- **Required to unblock:** operator-supplied verified Hyperliquid-native hourly OHLCV archive(s) extending history to ≥2023-01-01 (or enough additional independent crash episodes to reach n≥4 with CI excluding zero) with per-file provenance/SOURCE, intake-validated via `scripts/validate_hyperliquid_archive_intake.py`, $5M/spec defaults preserved, `is_hyperliquid_venue_data=true` only for native. See `research_state/c15_data_request_stem_20261116T024001Z.md`.

*Acquisition-attempt evidence only; no market data fabricated. Cross-venue OKX/Binance not relabeled Hyperliquid. Canonical C1–C14 artifacts unchanged.*
