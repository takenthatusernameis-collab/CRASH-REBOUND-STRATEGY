# Hyperliquid Archive Intake Validation — 2026-11-15T22:48:49Z

**Verdict:** `REJECT_NOT_EVIDENCE`
**is_market_data:** `False` · **is_evidence:** `False` · **performance_evidence:** `False`

Archive: `/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY/research_state/archives/hyperliquid_ironflow_wide_20261115T214900Z`
Requested window: `2025-12-20T00:00:00Z` .. `2026-09-28T23:00:00Z` (6792 expected hourly bars/symbol)

## Gate results

| Check | Status | Detail |
|---|---|---|
| `archive_present` | pass | 197 symbol(s) loaded, layout=dir_parquet |
| `placeholder_not_evidence` | pass | not the committed placeholder parquet |
| `source_provenance` | pass | provenance documents=2; declares_hyperliquid=True; declares_fixture_or_synthetic=True |
| `symbol_universe` | pass | 197 symbol(s) >= min_symbols 24: ['0G', '2Z', 'AAVE', 'ACE', 'ADA', 'AERO', 'AIXBT', 'ALGO', 'ALT', 'ANIME', 'APE', 'APEX', 'APT', 'AR', 'ARB', 'ARK', 'ASTER', 'ATOM', 'AVAX', 'AVNT', 'AXS', 'AZTEC', 'BABY', 'BANANA', 'BCH', 'BERA', 'BIGTIME', 'BIO', 'BLAST', 'BLUR', 'BNB', 'BOME', 'BRETT', 'BSV', 'BTC', 'CAKE', 'CASHCAT', 'CC', 'CELO', 'CFX', 'CHILLGUY', 'CHIP', 'COMP', 'CRV', 'DASH', 'DOGE', 'DOOD', 'DOT', 'DYDX', 'DYM', 'EIGEN', 'ENA', 'ENS', 'ETC', 'ETH', 'ETHFI', 'FARTCOIN', 'FET', 'FIL', 'FOGO', 'FTT', 'FXS', 'GALA', 'GAS', 'GMT', 'GMX', 'GOAT', 'GRAM', 'GRASS', 'GRIFFAIN', 'HBAR', 'HEMI', 'HMSTR', 'HYPE', 'HYPER', 'ICP', 'IMX', 'INIT', 'INJ', 'IO', 'IOTA', 'IP', 'JTO', 'JUP', 'KAITO', 'KAS', 'KBONK', 'KFLOKI', 'KLUNC', 'KNEIRO', 'KPEPE', 'KSHIB', 'LAYER', 'LDO', 'LINEA', 'LINK', 'LIT', 'LTC', 'MANTA', 'MAV', 'MAVIA', 'ME', 'MEGA', 'MELANIA', 'MEME', 'MERL', 'MET', 'MEW', 'MINA', 'MNT', 'MON', 'MOODENG', 'MORPHO', 'MOVE', 'NEAR', 'NEO', 'NIL', 'NOT', 'NXPC', 'OM', 'ONDO', 'OP', 'ORDI', 'PAXG', 'PENDLE', 'PENGU', 'PEOPLE', 'PNUT', 'POL', 'POLYX', 'PONS', 'POPCAT', 'PROMPT', 'PROVE', 'PUMP', 'PURR', 'PYTH', 'RENDER', 'RESOLV', 'REZ', 'RSR', 'RUNE', 'S', 'SAGA', 'SAND', 'SCR', 'SEI', 'SKR', 'SKY', 'SNX', 'SOL', 'SOPH', 'SPX', 'STABLE', 'STBL', 'STRK', 'STX', 'SUI', 'SUPER', 'SUSHI', 'SYRUP', 'TAO', 'TIA', 'TNSR', 'TON', 'TRB', 'TRUMP', 'TRX', 'TST', 'TURBO', 'UMA', 'UNI', 'USELESS', 'USTC', 'USUAL', 'VINE', 'VIRTUAL', 'VVV', 'W', 'WCT', 'WIF', 'WLD', 'WLFI', 'XAI', 'XLM', 'XMR', 'XPL', 'XRP', 'YGG', 'YZY', 'ZEC', 'ZEN', 'ZEREBRO', 'ZETA', 'ZK', 'ZORA', 'ZRO'] |
| `series_integrity` | pass | every symbol is strictly hourly with no gaps/duplicate steps |
| `window_span` | pass | all 6792 hourly slots covered by the union of 197 symbols |
| `coverage_filter` | fail | dropped: ARK:0.66, BLAST:0.54, CASHCAT:0.28, CHILLGUY:0.55, CHIP:0.57, DOOD:0.66, FTT:0.51, FXS:0.06 |
| `synthetic_free` | pass | no flat/constant-close series detected |
| `volume_floor` | fail | below floor: 2Z: peak_24h_usd=4864490.803991997, ALT: peak_24h_usd=3342617.7528359992, APEX: peak_24h_usd=3656625.9674600014, ATOM: peak_24h_usd=3715951.572046003, BIGTIME: peak_24h_usd=762030.2260849996, BRETT: peak_24h_usd=2234084.019320001, BSV: peak_24h_usd=3445571.0812999937, CELO: peak_24h_usd=2678082.4176999987 |
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
