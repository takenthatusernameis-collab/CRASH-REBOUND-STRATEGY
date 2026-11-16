# C15 Data Request Stem — Hyperliquid-native episode/power extension

- **Generated (UTC):** 2026-11-16T02:40:01Z
- **Campaign:** C15 (evidenced hard blocker on extension)
- **Context:** C14 COMPLETE/UNDERPOWERED on widest available verified Hyperliquid-native Ironflow archive (283d spec window 2025-12-20..2026-09-28, 197 perps ingested / 113 @ $5M). Result: 3 effective episodes / 4 crash days / 7 trades; bootstrap 95% CI [−1144,+17547] spans zero (first CI exclusion at n=4, archive max 4); permutation p=0.03595; placebo p=0.4444. C1–C13 consolidated FINAL `NO_GO` unchanged.

## What is needed
A **verified Hyperliquid-native** hourly OHLCV archive extending history to **≥2023-01-01** (multiyear parity) or otherwise providing enough additional independent crash episodes to reach **n≥4+** (CI-excluding-zero feasible) under spec defaults:
- Native perps only (Hyperliquid-native; no HIP-3 dex / spot unless explicitly scoped and labeled). `is_hyperliquid_venue_data=true` only for native artifacts.
- Hourly bars, complete gap-free coverage for the extended window, per-symbol/per-file SHA256, non-synthetic attestation + SOURCE/provenance manifest.
- Must pass `scripts/validate_hyperliquid_archive_intake.py` and derive universe at $5M rolling-24h gate (`spec_compliant_volume_threshold=true`) without relaxing RSI/spec defaults.

## Why current sources are insufficient (evidenced)
- **Hyperliquid public API (candleSnapshot):** moving retention tail only — earliest served 2026-04-21T15:00:00Z, 3849/6792 bars max for spec window, 2943 early bars missing; cannot supply multiyear history. Evidence: `research_state/hyperliquid_retention_probe.json`, `research_state/c15_acquisition_attempt_20261116T024001Z.md`.
- **Ironflow `ironflow/hyperliquid-candles-1h` (HF, only native candles dataset found):** timestamp range **2025-05-25T14:00:00Z..2026-10-31T23:00:00Z** (3,641,742 rows) — covers spec window but **does not reach ≥2023-01-01**. Same source already fully ingested for C14. Evidence: `research_state/c15_acquisition_attempt_20261116T024001Z.md`.

## Requested delivery
1. Archive directory (parquet/json per-symbol) + SOURCE.md + MANIFEST/provenance with sha256s and window/symbol coverage.
2. Attestation that data is Hyperliquid-native, non-synthetic, and not relabeled cross-venue.
3. Enough history/symbols to plausibly add ≥1 independent crash episode beyond C14’s 3 (target n≥4) under unchanged spec.
