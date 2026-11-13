# Data Request & Verification Checklist — Hyperliquid-Native 283-Day Campaign (ITEM 6c / Phase J3)

**Handoff timestamp (UTC):** 2026-11-13T12:29:00Z
**Target window (spec, Hyperliquid):** `2025-12-20T00:00:00Z` → `2026-09-28T23:00:00Z` (283 days, hourly, 6792 bars/symbol, inclusive bounds).
**Status:** **FULL 283d `NOT_RUN` — VERIFIED HYPERLIQUID-NATIVE DATASET FOR THE FULL TARGET WINDOW IS UNAVAILABLE IN THIS ENVIRONMENT. PARTIAL 163d API WINDOW `NOT_EVIDENCE` RUN COMPLETE. No data fabricated. No OKX data relabeled as Hyperliquid.**

## Provenance/cross-venue caveat (mandatory)
Real OKX exchange data exists on disk for this repo and produced cross-venue research artifacts (see `HANDOFF.md`), but it is **NOT Hyperliquid performance evidence** and must never be relabeled. This document governs a Hyperliquid-native acquisition/verification campaign only. If verified Hyperliquid-native data for the full window is unavailable, the campaign remains `NOT_RUN`.

## Concrete blocker evidence (recorded)
- **Current probe (2026-11-13T21:46Z):** Hyperliquid public `info` API `candleSnapshot` for BTC over the full target range returned **3,900** hourly bars, first `2026-04-19T12:00:00Z`, last `2026-09-28T23:00:00Z`; the early **2,892** bars (2025-12-20..2026-04-19T11:00Z) are not served. The public API retains only the latest ~3,900 hourly bars. See `research_state/hyperliquid_acquisition_status.json`.
- **Partial run (NOT_EVIDENCE):** the available window `2026-04-19T12:00Z..2026-09-28T23:00Z` was acquired for 24 symbols; 12 had complete 3,900-bar coverage. `scripts/run_real_campaign.py --allow-partial-not-evidence` produced **0 trades / 0 PnL**; the crash census found **8 RSI(21)<20 events / 0 confirmed signals** across 12 symbols / 46,800 bars. Artifacts: `research_state/campaign_results_real_hyperliquid_partial_20260419_20260928.json`, `research_state/hyperliquid_partial_crash_census_20260419_20260928.json`. The partial run uses the bare symbol list `research_state/universe_hyperliquid_partial_20260419_20260928.json`; `scripts/derive_verified_universe.py` intentionally refuses the incomplete partial manifest, so do not treat that refusal as a new blocker for the NOT_EVIDENCE pipeline run.
- `scripts/run_real_campaign.py` **refuses to run** a full-evidence campaign without complete, verified, non-synthetic provenance meeting gates (exit non-zero). This fail-closed behavior is required. Partial runs are explicitly marked `performance_evidence=false` and must never be cited as spec evidence.

---

## HYPERLIQUID NATIVE ACQUISITION RUNBOOK

This runbook is executable step-by-step. Every step states command, pass/fail check, and artifact. Execute from repo root with the project venv (e.g. `PYTHONPATH=. /tmp/crs-venv/bin/python ...` after `bash scripts/bootstrap_env.sh`) and `PYTHONPATH=.` set. Do not fabricate data, do not synthesize candles, and do not relabel OKX artifacts as Hyperliquid.

### Prerequisites
- **Command:** `test -x /tmp/crs-venv/bin/python && PYTHONPATH=. /tmp/crs-venv/bin/python -c "import pytest,numpy,pandas,requests,pyarrow; print('env_ok')"` (or run `bash scripts/bootstrap_env.sh` first)
- **Pass/fail:** exit 0 and prints `env_ok`.
- **Artifact:** terminal evidence; `/tmp/venv_h` environment.

### Step 1 — Obtain verified Hyperliquid-native source archive (external, required)
- **Command (operator action, not automatable in this environment):** obtain a user-supplied, verifiable archive of **Hyperliquid-native** hourly OHLCV candles for the full target window `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z` (6792 bars/symbol) for the required universe (spec-relevant symbols with documented provenance/volume evidence; at minimum BTC/ETH for plumbing validation). Record origin, extraction method, extraction time, and any transformations in `research_state/archives/hyperliquid_1h_full_20251220_20260928/SOURCE.md` (or equivalent sidecar) inside the archive.
- **Pass/fail:** archive exists on disk, is Hyperliquid-native (documented source), covers full window for intended symbols, and is non-synthetic. **If unavailable, STOP here: campaign = `NOT_RUN` (do not proceed, do not fabricate).**
- **Artifact:** archive directory/file path (e.g. `research_state/archives/hyperliquid_1h_full_20251220_20260928/`) plus source documentation sidecar.

### Step 2 — Ingest archive and generate verified provenance manifest
- **Command (example):**
  `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/fetch_hyperliquid_candles.py --source archive --input-archive research_state/archives/hyperliquid_1h_full_20251220_20260928 --symbols BTC ETH --start 2025-12-20T00:00:00Z --end 2026-09-28T23:00:00Z --cache-dir research_state/cache/hyperliquid_1h_full_20251220_20260928`
  (Adjust `--symbols`/`--universe-file` to the verified Hyperliquid universe; use `--allow-partial` only for non-evidence debugging — never for spec evidence.)
- **Pass/fail:** exit 0; command completes without synthetic/unverified/temp-path rejection.
- **Artifact:** `research_state/cache/hyperliquid_1h_full_20251220_20260928/provenance.json` and per-symbol cached candles under the cache dir.

### Step 3 — Verify provenance completeness and non-synthetic integrity (hard gate)
- **Command:**
  `PYTHONPATH=. /tmp/crs-venv/bin/python - <<'PY'
import json,sys
p='research_state/cache/hyperliquid_1h_full_20251220_20260928/provenance.json'
m=json.load(open(p))
ok = m.get('summary',{}).get('all_complete') is True and m.get('summary',{}).get('ready_for_real_campaign') is True
print('all_complete=', m.get('summary',{}).get('all_complete'))
print('ready_for_real_campaign=', m.get('summary',{}).get('ready_for_real_campaign'))
print('fabricated_data=', m.get('fabricated_data'))
# fail if not ready or fabricated
sys.exit(0 if ok and m.get('fabricated_data') is not True else 1)
PY`
- **Pass/fail:** prints `all_complete= True`, `ready_for_real_campaign= True`, `fabricated_data= False` (or absent/false) and exits 0. If any check fails, campaign remains `NOT_RUN`.
- **Artifact:** verified `provenance.json` with `summary.all_complete=true` and `summary.ready_for_real_campaign=true`.

### Step 4 — Derive/confirm verified Hyperliquid universe (>= $5M 24h volume, point-in-time spec-consistent)
- **Command (example):**
  `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/derive_verified_universe.py --manifest research_state/cache/hyperliquid_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/hyperliquid_1h_full_20251220_20260928 --output research_state/universe_hyperliquid_full_verified.json`
- **Pass/fail:** exit 0; universe file lists only symbols with verified complete coverage and spec-compliant volume evidence; `min_24h_volume_usd >= 5000000` reflected.
- **Artifact:** `research_state/universe_hyperliquid_full_verified.json`.

### Step 5 — Execute gated Hyperliquid-native real campaign
- **Command:**
  `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_real_campaign.py --manifest research_state/cache/hyperliquid_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/hyperliquid_1h_full_20251220_20260928 --universe-file research_state/universe_hyperliquid_full_verified.json --output-prefix campaign_results_real_hyperliquid_full --apply-vault-fees`
- **Pass/fail:** exit 0 and output states `REAL run complete: ...`; script refuses incomplete/unverified/synthetic inputs (non-zero) so a passing run implies gates satisfied.
- **Artifact:** `research_state/campaign_results_real_hyperliquid_full.json` and `_metrics.json`/`.csv` with `real_market_data=true`, `performance_evidence=true`, `fabricated_data=false`, and provenance reference. Use a distinct prefix; never overwrite OKX canonical artifacts.

### Step 6 — Post-run verification, metrics, and evidence reporting
- **Command(s):**
  - `PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest -q -rs`
  - `sha256sum research_state/campaign_results_real_hyperliquid_full*.json research_state/universe_hyperliquid_full_verified.json`
  - Record coverage, universe, trade/metric outputs (Sharpe/Sortino/max DD with timestamps/Calmar/win rate/profit factor/monthly-weekly/attribution/exposure as produced), and compare vs Hyperliquid spec with provenance.
- **Pass/fail:** tests green (recorded counts), artifacts present and hash-recorded, conclusions cite Hyperliquid-native provenance; if Step 1–5 could not be satisfied, report remains `NOT_RUN` with blocker evidence (no fabricated results).
- **Artifact:** updated `HANDOFF.md` with commands, observed results, hashes, conclusions, and explicit `NOT_RUN` or completed status.

## Decision rule
- **Run permitted:** only when Steps 2–4 pass with `all_complete=true`, `ready_for_real_campaign=true`, non-synthetic, Hyperliquid-native, full 6792-bar coverage, and spec volume gates satisfied.
- **Otherwise:** `NOT_RUN`. Never fabricate data, never mark partial/unverified as spec evidence, never relabel OKX as Hyperliquid.
