# C16 Acquisition Attempt — Hyperliquid-native extension (evidenced)

- **Campaign:** C16 (heavy acquisition/re-probe)
- **Generated (UTC):** 2026-11-16T03:44:39Z
- **Objective:** obtain/identify verified Hyperliquid-native hourly OHLCV extending to **≥2023-01-01** or adding **≥1 independent crash episode** beyond C14 (target n≥4) under unchanged spec ($5M rolling-24h, native perps, gap-free hourly, SHA256+non-synthetic/provenance).

## Baseline (read, fixed)
- `HANDOFF.md`, `research_state/c15_data_request_stem_20261116T024001Z.md`, `research_state/c15_acquisition_attempt_20261116T024001Z.{md,json}`, `research_state/c15_decision_verdict_hyperliquid_native_c15_20261116T024001Z.{md,json}`
- `research_state/crash_event_census_hyperliquid_ironflow_wide_20261116T001200Z.json` (C14: 283d 2025-12-20..2026-09-28, 197/113 @ $5M, 3 episodes, 4 crash days, 7 trades, CI [−1144,+17547] spans 0, p_perm=0.03595, p_placebo=0.4444 — UNDERPOWERED)
- `research_state/episode_edge_hyperliquid_ironflow_wide_20261116T001200Z.json`
- Constraints fixed: native Hyperliquid perps only, hourly gap-free, per-symbol SHA256 + non-synthetic/provenance, `spec_compliant_volume_threshold=true` ($5M), unchanged RSI/sizing/exits/hedge, `is_hyperliquid_venue_data=true` only for native. No cross-venue relabeling, no synthetic gap-fill as verified, no spec relaxation, no inference on exhausted C14.

## T1 — Source discovery & concrete acquisition attempts

### 1) HuggingFace Ironflow native candles (public dataset metadata)
- **Commands:** `curl -s https://huggingface.co/api/datasets/ironflow/hyperliquid-candles-1h`; `curl -s 'https://huggingface.co/api/datasets?author=ironflow&limit=50'`. (`datasets`/`huggingface_hub` libs not installed in env; HF API used for command-level evidence.)
- **Observed (HF API):** `ironflow/hyperliquid-candles-1h`, CC BY 4.0, lastModified `2026-11-13T07:20:50Z`, sha `5177a7f...`; description states "25 May 2025 to 31 October 2026: 3,642,453 candles across 799 markets" (466 perps incl. HIP-3 builders + 333 spot). Data files `data/2025-05.parquet`..`data/2026-10.parquet` only. Author datasets: candles, trades, liquidations, funding, open-interest, outcomes. No other hyperliquid candles dataset in author inventory.
- **Local state:** widest native ingest already present `research_state/archives/hyperliquid_ironflow_wide_20261115T214900Z` (207 symbol parquet files; C14 verified scope 197-file/113-symbol @ $5M).
- **Outcome:** `NOT_ACQUIRABLE_FOR_EXTENSION_TARGET` — starts 2025-05-25 (HF), cannot reach ≥2023-01-01 and no evidence of history adding episodes beyond C14.

### 2) Hyperliquid public API retention (live re-probe)
- **Command:** `PYTHONPATH=. python3 scripts/probe_hyperliquid_blocker.py --limit 10 --out research_state/hyperliquid_retention_probe_c16_20261116T034225Z.json --json`
- **Artifact:** `research_state/hyperliquid_retention_probe_c16_20261116T034225Z.json` (generated 2026-11-16T03:44:23Z)
- **Observed:** target 2025-12-20..2026-09-28 (6792 hourly bars); `full_window_served=false`; `max_bars_returned=3848`; `missing_early_bars_vs_expected=2944`; `earliest_served_start_utc=2026-04-21T16:00:00Z`; verdict `FULL_283D_BLOCKED_BY_API_RETENTION`; 26/235 perps pass $5M gate (10 probed, all partial).
- **Outcome:** `BLOCKED_API_RETENTION_MOVING_TAIL` — moving tail only, cannot supply spec prefix or multiyear history.

### 3) Repo/env/credential inventory
- **Commands:** `ls research_state/archives`; `ls scripts`; `env | rg -i 'HF|HUGGING|HYPER|IRON|API_KEY|TOKEN|AWS|S3|ARCHIVE'`; `python3 -c 'import datasets/huggingface_hub'`.
- **Observed:** Native archives present: `hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet`, `hyperliquid_ironflow_1h_20251220_20260928`, `hyperliquid_ironflow_wide_20261115T214900Z`. Cross-venue multiyear archives exist (OKX/Binance) but **not usable as Hyperliquid-native evidence**. Acquisition/validation hooks present: `scripts/fetch_hyperliquid_candles.py`, `scripts/probe_hyperliquid_blocker.py`, `scripts/validate_hyperliquid_archive_intake.py`, `scripts/derive_verified_universe.py`. No matching env credentials/storage hooks found; HF client libs absent.
- **Outcome:** `NO_ADDITIONAL_VIABLE_NATIVE_PATH_FOUND_LOCALLY`.

## T2 — Intake/validation/next campaign
- No extended or episode-adding native archive acquired; **no intake staged, no validation run, no C16 inference/battery executed**.

## Conclusion (evidenced)
- **Extended native archive ≥2023-01-01 acquirable:** **NO**.
- **≥1 additional independent crash episode beyond C14 acquirable from probed native sources:** **NO** (no evidence of such history in reachable native sources).
- **Status:** `BLOCKED_EVIDENCED_DATA_REQUIRED` (C14 remains UNDERPOWERED: 3 episodes/4 days/7 trades).
- **Exhaustion:** all probed viable native paths re-checked with command-level proof (live API tail, HF Ironflow candles metadata/inventory, local archives/scripts/env). No spec relaxation, no cross-venue relabeling, no synthetic gap-fill, no inference-only churn.

## Minimum external deliverable to unblock
- Operator-supplied **verified Hyperliquid-native hourly OHLCV perp** archive extending to **≥2023-01-01** or adding **≥1 independent crash episode** beyond C14 (n≥4, CI excluding zero feasible) with per-file SHA256/manifest, SOURCE/provenance, coverage metadata, non-synthetic attestation, gap-free hourly bars.
- Stage under `research_state/archives/<source>/...`, validate with `scripts/validate_hyperliquid_archive_intake.py` and derivation/verification scripts before evidence claims. On validated intake that meets criteria: pre-register and execute decision-grade C16 campaign under spec defaults and update handoff.

*Machine-command evidence only; no market data fabricated. Canonical C1–C14 artifacts unchanged.*
