# C17 Acquisition Attempt — Hyperliquid-native extension (evidenced re-probe)

- **Campaign:** C17 (heavy acquisition/re-probe)
- **Generated (UTC):** 2026-11-16T04:38:40Z
- **Objective:** obtain/identify verified Hyperliquid-native hourly OHLCV extending to **≥2023-01-01** or adding **≥1 independent crash episode** beyond C14 (target n≥4) under unchanged spec ($5M rolling-24h, native perps, gap-free hourly, SHA256+non-synthetic/provenance).

## Baseline (read, fixed)
- `HANDOFF.md`, `research_state/c16_acquisition_attempt_20261116T034439Z.{md,json}`, `research_state/hyperliquid_retention_probe_c16_20261116T034225Z.json`, `research_state/c15_decision_verdict_hyperliquid_native_c15_20261116T024001Z.{md,json}`
- `research_state/crash_event_census_hyperliquid_ironflow_wide_20261116T001200Z.json` (C14: 283d 2025-12-20..2026-09-28, 197/113 @ $5M, 3 episodes, 4 crash days, 7 trades, CI [−1144,+17547] spans 0, p_perm=0.03595, p_placebo=0.4444 — UNDERPOWERED)
- `research_state/episode_edge_hyperliquid_ironflow_wide_20261116T001200Z.json`
- Constraints fixed: native Hyperliquid perps only, hourly gap-free, per-symbol SHA256 + non-synthetic/provenance, `spec_compliant_volume_threshold=true` ($5M), unchanged RSI/sizing/exits/hedge, `is_hyperliquid_venue_data=true` only for native. No cross-venue relabeling, no synthetic gap-fill as verified, no spec relaxation, no inference on exhausted C14.

## T1 — Source discovery & concrete acquisition attempts

### 1) HuggingFace Ironflow native candles (public dataset metadata re-probe)
- **Commands:** `curl -sS https://huggingface.co/api/datasets/ironflow/hyperliquid-candles-1h`; `curl -sS 'https://huggingface.co/api/datasets?search=hyperliquid+candles+1h&limit=20'`
- **Observed:** `ironflow/hyperliquid-candles-1h` only match; lastModified `2026-11-13T07:20:50Z`, sha `5177a7f7...`; data files `data/2025-05.parquet`..`data/2026-10.parquet` (no earlier/later additions vs C16).
- **Local state:** widest native ingest already present `research_state/archives/hyperliquid_ironflow_wide_20261115T214900Z` (207 files; C14 scope 197/113 @ $5M).
- **Outcome:** `NOT_ACQUIRABLE_FOR_EXTENSION_TARGET` — unchanged, cannot reach ≥2023-01-01 or add pre-C14 episodes.

### 2) Hyperliquid public API retention (live re-probe)
- **Command:** `PYTHONPATH=. python3 scripts/probe_hyperliquid_blocker.py --limit 10 --out research_state/hyperliquid_retention_probe_c17_20261116T043840Z.json --json`
- **Artifact:** `research_state/hyperliquid_retention_probe_c17_20261116T043840Z.json` (generated 2026-11-16T04:39:02Z)
- **Observed:** target 2025-12-20..2026-09-28 (6792 hourly bars); `full_window_served=false`; `max_bars_returned=3847`; `missing_early_bars_vs_expected=2945`; `earliest_served_start_utc=2026-04-21T17:00:00Z`; verdict `FULL_283D_BLOCKED_BY_API_RETENTION`; 26/235 perps pass $5M gate (10 probed, all partial).
- **Outcome:** `BLOCKED_API_RETENTION_MOVING_TAIL`.

### 3) Repo/env/credential inventory
- **Commands:** `git status --short` (clean); `ls research_state/archives`; `env | grep -Ei 'HF|HUGGING|HYPER|IRON|API_KEY|TOKEN|AWS|S3|GCS|AZURE|ARCHIVE|BUCKET'`; `python3 -c 'import datasets, huggingface_hub'`.
- **Observed:** no new native archives (only prior Hyperliquid/Ironflow + cross-venue OKX/Binance not usable as native evidence). No matching env credentials/storage hooks for Hyperliquid-native historical extension; HF client libs absent.
- **Outcome:** `NO_ADDITIONAL_VIABLE_NATIVE_PATH_FOUND_LOCALLY`.

## T2 — Intake/validation/next campaign
- No extended or episode-adding native archive acquired; **no intake staged, no validation run, no C17 inference/battery executed**.

## Conclusion (evidenced)
- **Extended native archive ≥2023-01-01 acquirable:** **NO**.
- **≥1 additional independent crash episode beyond C14 acquirable:** **NO** (from probed/reachable native sources).
- **Status:** `BLOCKED_EVIDENCED_DATA_REQUIRED` (C14 remains UNDERPOWERED: 3 episodes/4 days/7 trades).
- **Exhaustion:** re-probed live API, HF dataset/search, and local repo/env; no change since C16. No spec relaxation, no cross-venue relabeling, no synthetic gap-fill, no inference-only churn.

## Minimum external deliverable to unblock
- Operator-supplied **verified Hyperliquid-native hourly OHLCV perp** archive extending to **≥2023-01-01** or adding **≥1 independent crash episode** beyond C14 (n≥4, CI excluding zero feasible) with per-file SHA256/manifest, SOURCE/provenance, coverage metadata, non-synthetic attestation, gap-free hourly bars.
- Stage under `research_state/archives/<source>/...`, validate with `scripts/validate_hyperliquid_archive_intake.py` and derivation/verification scripts before evidence claims. On validated intake meeting criteria: pre-register and execute decision-grade next campaign under spec defaults and update handoff.

*Machine-command evidence only; no market data fabricated. Canonical C1–C14 artifacts unchanged.*
