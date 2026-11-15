# Hyperliquid Archive Intake Validation — 2026-11-15T06:44:06Z

**Verdict:** `REJECT_NOT_EVIDENCE`
**is_market_data:** `False` · **is_evidence:** `False` · **performance_evidence:** `False`

Archive: `/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY/research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet`
Requested window: `2025-12-20T00:00:00Z` .. `2026-09-28T23:00:00Z` (6792 expected hourly bars/symbol)

## Gate results

| Check | Status | Detail |
|---|---|---|
| `archive_present` | pass | 2 symbol(s) loaded, layout=parquet_file |
| `placeholder_not_evidence` | fail | known placeholder parquet detected; never evidence |
| `source_provenance` | pass | provenance documents=1; declares_hyperliquid=True; declares_fixture_or_synthetic=False |
| `symbol_universe` | pass | 2 symbol(s) >= min_symbols 2: ['BTC', 'ETH'] |
| `window_coverage` | pass | all symbols cover the full hourly window with no gaps |
| `synthetic_free` | fail | BTC: flat_series_all_bars_identical (1/6792); ETH: flat_series_all_bars_identical (1/6792) |
| `volume_floor` | pass | all symbols >= $5,000,000 trailing-24h USD volume |
| `checksum_integrity` | pass | checksums verified |

## Built-in self-test (fail-closed proof)

All expectations met: **True** (4 cases)

| Case | Opt-in | Expected | Actual | Pass |
|---|---|---|---|---|
| `flat_full_window_fixture_without_optin` | False | `REJECT_NOT_EVIDENCE` | `REJECT_NOT_EVIDENCE` | True |
| `flat_full_window_fixture_with_optin` | True | `ACCEPT_FIXTURE_NON_EVIDENCE` | `ACCEPT_FIXTURE_NON_EVIDENCE` | True |
| `truncated_varying_fixture_with_optin` | True | `REJECT_NOT_EVIDENCE` | `REJECT_NOT_EVIDENCE` | True |
| `committed_placeholder_parquet` | True | `REJECT_NOT_EVIDENCE` | `REJECT_NOT_EVIDENCE` | True |

## Caveats

- Intake validation only: proves the archive is structurally usable as evidence input, NOT that the strategy is profitable. Never relabel OKX, partial snapshots, dry-run fixtures, or the placeholder parquet as Hyperliquid evidence.
- A fixture acceptance is plumbing-only: `is_market_data=false`, `is_evidence=false`.
- A truncated window is never fixture-tolerable; only synthetic/volume/checksum gaps may be waived by the explicit opt-in flag.
- This validator does not run a backtest and makes no profitability claim.
