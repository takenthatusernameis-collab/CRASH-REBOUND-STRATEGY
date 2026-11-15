# Hyperliquid Archive Intake Validation — 2026-11-15T22:42:54Z

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
| `window_coverage` | fail | ARK: non-hourly gap/duplicate step of 10800s; AXS: starts late: 2026-01-18T03:00:00Z > 2025-12-20T00:00:00Z; AZTEC: starts late: 2026-02-12T08:00:00Z > 2025-12-20T00:00:00Z; BLAST: non-hourly gap/duplicate step of 7200s; BOME: non-hourly gap/duplicate step of 10800s; CASHCAT: starts late: 2026-07-11T04:00:00Z > 2025-12-20T00:00:00Z; CHILLGUY: ends early: 2026-05-25T09:00:00Z < 2026-09-28T23:00:00Z; CHIP: starts late: 2026-04-22T02:00:00Z > 2025-12-20T00:00:00Z |
| `synthetic_free` | pass | no flat/constant-close series detected |
| `volume_floor` | fail | below floor: 0G: 28233.134649996668, 2Z: 50244.965682998896, AAVE: 931248.0785999465, ACE: 16356.309960998064, ADA: 934525.9361399824, AERO: 112301.01370999907, AIXBT: 58271.20882399581, ALGO: 72833.52756000066 |
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
