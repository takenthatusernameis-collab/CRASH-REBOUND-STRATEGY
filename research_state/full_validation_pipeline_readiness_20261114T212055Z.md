# C5-T1 Full Validation Pipeline — Dry Run (2026-11-14T21:20:56Z)

**Mode:** dry-run-fixture (synthetic fixture, temp out-dir)
**performance_evidence:** false · **is_market_data:** false · **is_evidence:** false
**Overall:** PASS

## Steps

| Step | Status | Detail |
|---|---|---|
| `dry_run_full_synthetic_fixture` | PASS | opt-in=ACCEPT_FIXTURE_NON_EVIDENCE is_market_data=False is_evidence=False perf_evidence=False no-optin=REJECT_NOT_EVIDENCE |
| `dry_run_truncated_fixture` | PASS | verdict=REJECT_NOT_EVIDENCE (must be REJECT_NOT_EVIDENCE) |
| `dry_run_flat_synthetic_fixture` | PASS | no-optin=REJECT_NOT_EVIDENCE opt-in=ACCEPT_FIXTURE_NON_EVIDENCE perf_evidence=False |
| `dry_run_placeholder_parquet_negative` | PASS | placeholder_exists=True verdict=REJECT_NOT_EVIDENCE (must be REJECT_NOT_EVIDENCE even with --allow-synthetic-fixture) |
| `dry_run_negative_test_rejects_bad_inputs` | PASS | truncated_rejected=True placeholder_rejected=True |
| `dry_run_canonical_pointer_protected` | PASS | hyperliquid_exploratory_next_open_latest.json not written by dry run |

## Negative tests

- Placeholder parquet rejected: **True**
- Truncated fixture rejected: **True**
- Flat fixture not evidence: **True**

## Fixtures (temp out-dir: `/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY/research_state/tmp_c5_dryrun_20261114T212055Z`)
- Full synthetic: `/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY/research_state/tmp_c5_dryrun_20261114T212055Z/fixture_full_synthetic`
- Truncated synthetic: `/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY/research_state/tmp_c5_dryrun_20261114T212055Z/fixture_truncated_synthetic`
- Flat synthetic: `/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY/research_state/tmp_c5_dryrun_20261114T212055Z/fixture_flat_full`

## Canonical pointer protection
- hyperliquid_exploratory_next_open_latest.json: **not written**

This is a plumbing-only dry run. No Hyperliquid market data was used. No canonical artifact was overwritten.
