# Operator Archive Request v2 — Hyperliquid-Native Multi-Year Validation (C5-T2)

**Request timestamp (UTC):** 2026-11-14T22:10:03Z
**Supersedes:** `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` (v1, handoff 2026-11-13T12:29:00Z)
**Status:** OPEN

---

## Target Window (binding C4-T2 requirement)

| Field | Value |
|-------|-------|
| Start (UTC) | `2023-12-20T17:19:21Z` |
| End (UTC) | `2026-09-28T23:00:00Z` |
| Duration | **1,013.2 days** (~2.78 years) |
| Hourly bars/symbol | **≥ 24,319** |
| Episode rate (observed) | 0.012355 episodes/day |
| Power target | **80%** (≥10 independent crash episodes + episode-block bootstrap 95% CI excluding 0 + crash-day permutation p<0.05 + full-portfolio placebo p<0.05) |

**Critical statement:** The 283-day spec window (2025-12-20..2026-09-28) provides only **0.33% probability** of achieving ≥10 independent crash episodes (C3-T3 power sensitivity). The multi-year window (1,013.2 days) is the **binding 80%-power requirement** — **283 days is 2.78× too short**. No session may relabel the 283-day partial run or OKX cross-venue data as Hyperliquid performance evidence.

---

## Requirements (machine-checkable)

| Requirement | Predicate |
|-------------|-----------|
| Minimum symbols | ≥ 24 symbols with complete coverage |
| Minimum distinct crash days | ≥ 10 calendar days with RSI(21)<20 events across universe |
| Provenance | **Hyperliquid-native only** — documented API source, extraction method, extraction timestamp, no synthetic generation |
| Per-file SHA256 | Required for every symbol file, recorded in provenance manifest |
| Non-synthetic | `fabricated_data == false` in provenance; no fabricated/interpolated candles |
| Volume gate | Trailing 24h volume ≥ $5M USD (spec-compliant, point-in-time) |
| Archive format | Parquet or CSV per symbol with columns: `timestamp, open, high, low, close, volume` |
| Source documentation | `SOURCES.md` sidecar inside archive directory recording origin, extraction method, extraction timestamp, any transformations |

---

## Acceptance Predicates (all must pass)

1. **archive_exists** — archive directory/file exists on disk at declared path
2. **provenance_documented** — `SOURCES.md` sidecar present with Hyperliquid-native origin, extraction method, timestamp
3. **full_window_coverage** — every required symbol has ≥ 24,319 hourly bars covering 2023-12-20T17:19:21Z .. 2026-09-28T23:00:00Z inclusive
4. **min_symbols_met** — ≥ 24 symbols with complete coverage
5. **min_crash_days_met** — ≥ 10 distinct calendar days with RSI(21)<20 crash events across universe
6. **non_synthetic** — no fabricated/synthetic/interpolated candles; `provenance.fabricated_data == false`
7. **per_file_sha256_recorded** — SHA256 for each symbol file recorded in provenance manifest
8. **volume_gate_satisfied** — all symbols pass trailing 24h ≥ $5M at decision points

---

## Executable Command Sequence (run from repo root with venv)

```bash
# Prerequisites
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python -c "import pytest,numpy,pandas,requests,pyarrow; print('env_ok')"  # expect exit 0, prints 'env_ok'

# Step 1 — Ingest operator-supplied archive (adjust <ARCHIVE_PATH> and <SYMBOL_LIST>)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/fetch_hyperliquid_candles.py \
  --source archive \
  --input-archive <ARCHIVE_PATH> \
  --symbols <SYMBOL_LIST> \
  --start 2023-12-20T17:19:21Z \
  --end 2026-09-28T23:00:00Z \
  --cache-dir research_state/cache/hyperliquid_1h_full_20231220_20260928

# Step 2 — Verify provenance completeness & non-synthetic integrity (HARD GATE)
PYTHONPATH=. /tmp/crs-venv/bin/python -c "
import json,sys
p='research_state/cache/hyperliquid_1h_full_20231220_20260928/provenance.json'
m=json.load(open(p))
ok = (m.get('summary',{}).get('all_complete') is True and
      m.get('summary',{}).get('ready_for_real_campaign') is True and
      m.get('fabricated_data') is not True)
print('all_complete=', m.get('summary',{}).get('all_complete'))
print('ready_for_real_campaign=', m.get('summary',{}).get('ready_for_real_campaign'))
print('fabricated_data=', m.get('fabricated_data'))
sys.exit(0 if ok else 1)
"
# Expect: all_complete=True, ready_for_real_campaign=True, fabricated_data=False, exit 0

# Step 3 — Derive/confirm verified Hyperliquid universe (≥$5M 24h volume, spec-consistent)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/derive_verified_universe.py \
  --manifest research_state/cache/hyperliquid_1h_full_20231220_20260928/provenance.json \
  --cache-dir research_state/cache/hyperliquid_1h_full_20231220_20260928 \
  --output research_state/universe_hyperliquid_full_verified.json
# Expect: exit 0; universe lists only symbols with verified complete coverage & min_24h_volume_usd >= 5000000

# Step 4 — Execute gated Hyperliquid-native real campaign
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_real_campaign.py \
  --manifest research_state/cache/hyperliquid_1h_full_20231220_20260928/provenance.json \
  --cache-dir research_state/cache/hyperliquid_1h_full_20231220_20260928 \
  --universe-file research_state/universe_hyperliquid_full_verified.json \
  --output-prefix campaign_results_real_hyperliquid_full \
  --apply-vault-fees
# Expect: exit 0; output 'REAL run complete: ...'; artifacts with real_market_data=true, performance_evidence=true, fabricated_data=false

# Step 5 — Post-run verification & evidence reporting
PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest -q -rs
sha256sum research_state/campaign_results_real_hyperliquid_full*.json research_state/universe_hyperliquid_full_verified.json

# Step 6 — Gates (must pass for decision-grade)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                  # expect 21/21
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py      # expect 4/4
```

---

## Pass/Fail Rules

| Step | Pass Condition |
|------|----------------|
| Prereqs | exit 0 && prints `env_ok` |
| Ingest (Step 1) | exit 0; completes without synthetic/unverified/temp-path rejection |
| Provenance (Step 2) | prints `all_complete=True`, `ready_for_real_campaign=True`, `fabricated_data=False` (or absent/false); exit 0 |
| Universe (Step 3) | exit 0; universe file lists only symbols with verified complete coverage & spec-compliant volume; `min_24h_volume_usd >= 5000000` |
| Campaign (Step 4) | exit 0; output states `REAL run complete: ...`; script refuses incomplete/unverified/synthetic inputs (non-zero) |
| Verify (Step 5) | tests green; artifacts present and hash-recorded; conclusions cite Hyperliquid-native provenance |
| Gates (Step 6) | `session_gate.py` 21/21 checks passed; `verify_campaign_evidence.py` 4/4 evidence verified |

---

## References

- **C4-T2 Multi-Year Validation Protocol:** `research_state/multi_year_validation_protocol_20261114T203040Z.{json,md}` — `NO_GO`; 80% power needs 1,013.2 days / 24,319 bars/symbol
- **C4-T1 Intake Validator:** `research_state/archive_intake_validation_20261114T202957Z.{json,md}` — placeholder `REJECT_NOT_EVIDENCE`; self-test 4/4; flat fixture accepted only as `ACCEPT_FIXTURE_NON_EVIDENCE`
- **C3-T3 Power Sensitivity:** `research_state/power_sensitivity_20261114T182832Z.{json,md}` — 283d 0.33%, 2y 41.51%, pooled 22.32%
- **Data Request v1 (superseded):** `research_state/DATA_REQUEST_283D_HYPERLIQUID.md`

---

## Update to DATA_REQUEST_283D_HYPERLIQUID.md

This v2 request **supersedes** the 283-day runbook. The v1 file remains as historical record; all future operator data acquisition follows this v2 specification. When operator archive arrives, it must first pass C4-T1 (`ACCEPT_AS_EVIDENCE_CANDIDATE`) and then the C5-T1 orchestrator (`scripts/run_full_validation_campaign.py`).