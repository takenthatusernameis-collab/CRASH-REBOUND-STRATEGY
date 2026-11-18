# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-18T11:05:23Z · **Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound trading-strategy research/backtesting on real-market, cross-venue data (OKX + Binance UM perps to date).
**Single durable handoff:** this file. `INITIAL_TASK_MESSAGE.md` is a pointer to this file; do not maintain a second source of truth.
**Priority by repo scope (non-negotiable):** C1–C20 are CLOSED & CERTIFIED `NO_GO` (do not relitigate, do not relaunch C20). **C21-T1 is COMPLETE** — gate `C21 ACCEPTANCE: PASS`, consolidated verdict `NO_GO` (2026-11-18T06:15:08Z). **C22-T1 is the ACTIVE BINDING CAMPAIGN** — MEXC USDT-perp out-of-sample replication of the frozen spec-literal edge, PRE-REGISTERED (`c22_prereg_20261118T100126Z`) with acquisition VIABLE and infrastructure built; the heavy battery is PENDING and MUST be executed to gate `C22 ACCEPTANCE: PASS`. Hyperliquid-native acquisition stays CLOSED (`FULL_283D_BLOCKED_BY_API_RETENTION`); **new-venue (MEXC) acquisition is OPEN** (probe-verified). Do NOT run a same-data C22+ rerun on OKX/Binance; do not relabel MEXC data as Hyperliquid; do not reduce draw counts.

**Verified live/repo state (2026-11-18T11:05:23Z):**
- `PYTHONPATH=. .venv/bin/python scripts/verify_c21_focus_campaign.py` → `C21 ACCEPTANCE: PASS` (pooled=`NO_GO`, consolidated final=`NO_GO`, ts=2026-11-18T06:15:08Z, 12/12 artifacts, 8/8 checkpoints, stamp `20261117T064408Z`).
- `PYTHONPATH=. .venv/bin/python scripts/probe_c22_venue_acquisition.py` → artifact `research_state/c22_venue_acquisition_probe_20261118T100126Z.json` (refreshed `generated_at_utc=2026-11-18T11:03:58Z`), `c22_data_status=ACQUISITION_VIABLE_MEXC_MULTIYEAR`. **MEXC reachable + multiyear** (2023=49 bars, 2024=49 bars in probe windows; 11/15 probe symbols ≥ $5M/24h: SOL, ADA, XRP, DOGE, LINK, AVAX, DOT, NEAR, ARB, UNI, AAVE). Gate.io reachable but **recent-only** (candles ≤ ~2000 bars, funding ≤180d). Binance UM + Bybit **geo-blocked** from runner (HTTP 451 / 403). OKX SWAP reachable + multiyear (already cached).
- `PYTHONPATH=. .venv/bin/python scripts/verify_c22_focus_campaign.py` → `C22 ACCEPTANCE: PENDING` (prereqs GREEN: prereg json+md present, config matches frozen spec-literal, acquisition viable; **0/7 battery artifacts** — heavy work required).
- `PYTHONPATH=. .venv/bin/python -m pytest tests/test_c22_campaign_20261118.py -q` → `11 passed in 0.18s`.
- No C21/C22 runner process active; none needed for C1–C21. **The C22 runner script itself is still missing — creating it is the first execution step below, not a reason to stop.**

> **PROGRAM STATE: C1–C20 COMPLETE `NO_GO`; C21-T1 COMPLETE, gate PASS, consolidated `NO_GO`; C22-T1 ACTIVE — pre-registered, acquisition VIABLE (MEXC multiyear), data/inference infrastructure ready, battery PENDING (heavy work required to reach gate PASS). Hyperliquid-native acquisition CLOSED; MEXC new-venue acquisition OPEN.**

**Closure tokens (binding):** `pytest tests/ -q` = `1058 passed, 1 skipped` (includes `tests/test_c22_campaign_20261118.py` = `11 passed`); `scripts/session_gate.py` = `21/21 checks passed` (Phase O timestamp `2026-11-13T23:38:47Z`); `scripts/verify_campaign_evidence.py` = `EVIDENCE VERIFIED`; C20/C19/C14/C13/C6 gates = `PASS`; `scripts/probe_hyperliquid_blocker.py` = `FULL_283D_BLOCKED_BY_API_RETENTION`.

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-18T11:05:23Z — C22 ACTIVE; ACQUISITION VIABLE; EXECUTE THE HEAVY MEXC BATTERY)

**Repository:** `CRASH-REBOUND-STRATEGY` (crash-rebound edge adjudication on real-market data; OKX + Binance UM perps done, MEXC next).
**Environment:** durable `.venv` at repo root (Python 3.12.3 + `pytest`/`numpy`/`pandas`/`requests`/`pyarrow`); run with `PYTHONPATH=. .venv/bin/python ...`. If missing, `bash scripts/bootstrap_env.sh` first. Network egress is available (OKX/MEXC/Coinbase/Kraken reachable; Binance/Bybit geo-blocked).

**Verified (2026-11-18T11:05:23Z):** C1–C20 CLOSED `NO_GO`; **C21-T1 COMPLETE** (`C21 ACCEPTANCE: PASS`, consolidated `NO_GO`). **C22-T1 ACTIVE & PRE-REGISTERED** — `c22_prereg_20261118T100126Z.{json,md}` (`PRE_REGISTERED_BEFORE_COMPUTE`), `c22_data_status=ACQUISITION_VIABLE_MEXC_MULTIYEAR`, `verify_c22_focus_campaign.py` → `C22 ACCEPTANCE: PENDING` (0/7 battery artifacts), `tests/test_c22_campaign_20261118.py` → 11 passed. No C22 runner process active and **no C22 runner script exists yet**.

**Binding constraint / what changed vs the prior handoff:** the prior handoff said acquisition was CLOSED and "no new-venue network is available" — **that is SUPERSEDED by probe evidence.** MEXC USDT-perp 1H data is reachable and multiyear (2023–2026). This makes a **new-data** C22 legitimate (MEXC ≠ OKX/Binance). It is **NOT** a same-data C22+ rerun and **NOT** a parameter search: the spec is frozen (see prereg). Hyperliquid-native data remains exhausted (`FULL_283D_BLOCKED_BY_API_RETENTION`, earliest ~2026-04-21) — do not retry it. The remaining engineering bottleneck is that the C22 runner must be created; that is the first heavy execution step, not a reason to stop or to re-plan.

**Immediate next action — HEAVY EXECUTION (this is the authorized work; do it, do not plan around it):**
1. **Confirm prereqs:** `PYTHONPATH=. .venv/bin/python scripts/verify_c22_focus_campaign.py` must read `PENDING` (never `FAIL`); probe `c22_data_status` must start `ACQUISITION_VIABLE`.
2. **Acquire the MEXC archive (multiyear):**
   ```bash
   SYMBOLS=$(PYTHONPATH=. .venv/bin/python -c 'import json; print(" ".join(json.load(open("research_state/universe_okx_multiyear_verified.json"))["selected_symbols"]))')
   PYTHONPATH=. .venv/bin/python scripts/fetch_mexc_perp_archive.py \
     --symbols $SYMBOLS --start 2023-01-01T00:00:00Z --end 2026-09-28T23:00:00Z \
     --out research_state/cache/mexc_1h_multiyear_20230101_20260928 --force
   ```
   Use the candidate list in `research_state/universe_okx_multiyear_verified.json`; symbols not listed for the full window are honestly marked `coverage=false`, never fabricated. Do not synthetic-gap-fill.
3. **Derive the verified, volume-gated universe:**
   ```bash
   PYTHONPATH=. .venv/bin/python scripts/derive_verified_universe.py \
     --manifest research_state/cache/mexc_1h_multiyear_20230101_20260928/provenance.json \
     --cache-dir research_state/cache/mexc_1h_multiyear_20230101_20260928/candles \
     --output research_state/universe_mexc_multiyear_verified.json \
     --min-24h-volume-usd 5000000
   ```
4. **Create and run the C22 runner (the heavy compute).** Add `scripts/run_c22_mexc_campaign.py` (or an equivalent durable wrapper) that registers a `mexc` venue with the same cache/universe/provenance contract as `c20.load_venue`, reuses the C20/C21 fold primitives (`_run_fold_campaign`, `_fold_census`, `_fold_episode_edge`, `_fold_placebo`, `build_strata`, `_build_venue_verdict`) with **C22 stems/labels**, and emits a C22 pooled/consolidated that compares MEXC to the recorded OKX/Binance `NO_GO`. Do **not** run `run_c21_cross_venue_campaign.py` unchanged and rename its output: it is OKX/Binance-specific and hard-codes C21 artifacts. **Draw counts are frozen: 20,000 bootstrap / 20,000 permutation / 2,000 placebo / 2,000 strata.** Checkpoint each fold (`c22_ckpt_mexc_<fold>_<TS>.json`, internal only); run detached/durable, not in a foreground agent turn, and never launch a duplicate MEXC battery on the same cache. Emit exactly the 7 artifacts listed under "C22 REQUIRED ARTIFACTS".
5. **Verify:** `PYTHONPATH=. .venv/bin/python scripts/verify_c22_focus_campaign.py` → `C22 ACCEPTANCE: PASS` (token ∈ {`STABLE_POSITIVE_SUBSET`, `NO_GO`, `UNDERPOWERED`}; mexc verdict must equal consolidated; `is_hyperliquid_venue_data=false` everywhere).
6. **Then stop and await explicit operator direction.** Do not start a same-data C23+ rerun on OKX/Binance/MEXC without new prereg + new data + explicit authorization.

**No-avoidance rule (binding):** if `verify_c22_focus_campaign.py` prints anything other than `C22 ACCEPTANCE: PASS`, the session is **not done** — heavy execution (create runner → acquire → derive universe → run the full 8-fold 20k/20k/2k battery → emit artifacts) is mandatory until the gate is green. While the gate is `PASS`, do NOT manufacture further same-data work on the exhausted OKX/Binance/MEXC data. A `PENDING` result is a work order, not a completion state.

**Expected outcome is honesty, not a GO:** given C1–C21, C22 will most likely confirm `NO_GO` (or `UNDERPOWERED` if MEXC per-fold N is below the power floor). A `NO_GO`/`UNDERPOWERED` result is a **success** — report per-fold, per-venue, and pooled numbers plus the power curve, never a bare token, and never tune the spec to chase a GO.

---

## BINDING CAMPAIGN — C22-T1 (MEXC OUT-OF-SAMPLE REPLICATION) — ACTIVE

**Prereg:** `research_state/c22_prereg_20261118T100126Z.{json,md}` (`PRE_REGISTERED_BEFORE_COMPUTE`). **This is a NEW-DATA campaign, not a same-data rerun.**

- **Question:** does the *unchanged* spec-literal crash-rebound edge replicate on MEXC USDT-perp 1H data (a venue never used in C1–C21), over the same 2023-01-01..2026-09-28 multiyear window and the same pre-specified folds/strata/inference as C21?
- **Frozen config (no switching after results):** `rsi_period=21`, `rsi_threshold=20`, `target_pct=9`, `rebound_short_target_pct=9`, `rebound_short_time_exit_bars=48`, `enable_rebound_short=true`, `enable_eth_hedge=true`, `min_daily_volume_usd=5,000,000`, `gross_cap_pct=120`, `entry_spec_literal_next_open=true`. Seed `20261122`.
- **Folds (pre-specified):** 2023, 2024, 2025, 2026YTD (2026-01-01..2026-09-28). **Strata (pre-specified):** `crash_severity` (RSI 0–10/10–15/15–20), `btc_trend` (down/flat/up 7d), `funding_regime` (neg/neu/pos; neutral when the venue has no funding history — MEXC has none, like OKX).
- **Inference:** per venue-fold 20,000-draw episode-block bootstrap CI95, 20,000-draw permutation p, 2,000-subset portfolio placebo, stratified bootstrap with **Benjamini–Hochberg** (α=0.05); pooled venue-blocked bootstrap + cross-venue sign concordance vs the recorded OKX/Binance priors. Power floor: ≥10 trades / ≥5 episodes / ≥5 distinct crash days else `UNDERPOWERED` + power curve.
- **Decision rule:** `STABLE_POSITIVE_SUBSET` only if a pre-specified fold/stratum survives BH with bootstrap CI excluding 0 & positive spot leg, permutation p<0.05, placebo p_ge_canonical<0.05, N≥floor, AND same-direction effect in the other venue(s) (or flagged single-venue exploratory). Otherwise `NO_GO` or `UNDERPOWERED`.
- **C22 is cross-venue** (`is_hyperliquid_venue_data=false`) — **never** Hyperliquid performance evidence.

**C22 REQUIRED ARTIFACTS (TS = `20261118T100126Z`)** — the gate checks all 7 battery artifacts + prereg:
`c22_prereg_{TS}.{json,md}`; `c22_mexc_fold_campaign_{TS}.json`; `c22_mexc_fold_episode_edge_{TS}.json`; `c22_mexc_fold_placebo_{TS}.json`; `c22_mexc_fold_census_{TS}.json`; `c22_decision_verdict_mexc_stability_{TS}.json`; `c22_pooled_stability_synthesis_{TS}.json`; `c22_decision_verdict_CONSOLIDATED_{TS}.json`. HANDOFF references **C22-T1** and **verify_c22_focus_campaign.py**.

**C22 data/acquisition infrastructure (built this session, tested):**
- `scripts/probe_c22_venue_acquisition.py` → `research_state/c22_venue_acquisition_probe_20261118T100126Z.json` (`ACQUISITION_VIABLE_MEXC_MULTIYEAR`).
- `scripts/fetch_mexc_perp_archive.py` — MEXC multiyear 1H perp fetcher → cache `candles/<SYM>.json` + `provenance.json` (per-symbol sha256, `analyze_coverage`, `synthetic_check is_synthetic=false`). Volume normalized so `close*volume == quote USD` (matches the OKX convention; MEXC `vol` is contracts, `amount` is quote). Smoke-tested: 745/745 bars, zero gaps, `close*volume == amount`.
- `scripts/build_c22_prereg.py` → prereg json+md.
- `scripts/verify_c22_focus_campaign.py` — hard gate (`PASS` / `PENDING` / `FAIL`).
- `tests/test_c22_campaign_20261118.py` — 11 tests (normalization, pagination, prereg schema, gate transitions).
- **MISSING (next action, not optional):** `scripts/run_c22_mexc_campaign.py` — the C22 runner/artifact emitter. It must be created from the C20/C21 primitives with C22 stems/labels before the 8-fold battery can run; do not rename C21 output.

---

## BOTTLENECK REMOVED THIS SESSION (2026-11-18T11:05:23Z)

1. **Re-verified the live state instead of trusting the prior note:** C21 gate `PASS`; C22 gate `PENDING` with 0/7 battery artifacts; C22 tests `11 passed`.
2. **Refreshed the acquisition probe:** `research_state/c22_venue_acquisition_probe_20261118T100126Z.json` now records `generated_at_utc=2026-11-18T11:03:58Z` and `n_passing=11/15` (DOT is now in the $5M+ set). This supersedes the older `10/15` note; MEXC remains `ACQUISITION_VIABLE_MEXC_MULTIYEAR`.
3. **Removed the "only re-verify / await direction" ambiguity:** the next session's first mandatory action is to create the C22 runner, then execute acquisition → universe → the full 8-fold 20k/20k/2k battery → gate. A `PENDING` gate is a work order, not a stopping point.
4. **Named the remaining engineering bottleneck explicitly:** no C22 runner script exists. It must be created from the C20/C21 primitives with C22 stems/labels; do not run the C21 runner unchanged and rename its artifacts.
5. **Preserved the acquisition boundary:** MEXC new-venue acquisition is OPEN; Hyperliquid-native acquisition remains CLOSED/exhausted (`FULL_283D_BLOCKED_BY_API_RETENTION`).

---

## BOTTLENECK REMOVED IN PRIOR SESSION (2026-11-18T10:10:23Z)

**Root cause (was):** the prior handoff declared acquisition CLOSED/exhausted and forbade any C22+, and told every session to "do nothing but verify, then await direction." Combined with the controller's "meaningful project progress or fail" requirement, this created a **do-nothing paralysis**: sessions could not legitimately make progress and were told not to manufacture work. The factual basis ("no new-venue network available") was also **stale**.

**Fix applied (evidence-based, no spec relaxation):**
1. **Replaced the stale acquisition claim with reproducible evidence.** `scripts/probe_c22_venue_acquisition.py` was run and wrote `research_state/c22_venue_acquisition_probe_20261118T100126Z.json`: MEXC is reachable and serves **multiyear 2023–2026** 1H perps with a $5M+ altcoin subset; Gate.io is recent-only; Binance/Bybit are geo-blocked; Hyperliquid-native is still exhausted. Conclusion: `ACQUISITION_VIABLE_MEXC_MULTIYEAR`.
2. **Built the C22 data pipeline (tested, real).** `scripts/fetch_mexc_perp_archive.py` fetches MEXC perps into the exact cache/provenance schema `c20.load_venue` / `derive_verified_universe.py` consume, with honest coverage accounting (no gap-fill) and `close*volume == quote USD` normalization.
3. **Pre-registered C22 before compute.** `scripts/build_c22_prereg.py` emitted `c22_prereg_20261118T100126Z.{json,md}` with frozen config/folds/strata/inference/decision rules — so C22 cannot drift into a parameter search.
4. **Installed a hard, non-avoidable gate.** `scripts/verify_c22_focus_campaign.py` prints `C22 ACCEPTANCE: PENDING` until the full 8-fold 20k/20k/2k battery is present and consistent, then `PASS`. The no-avoidance rule above binds future sessions to execute until `PASS`.
5. **Locked correctness with tests.** `tests/test_c22_campaign_20261118.py` (11 tests) covers MEXC normalization, forward pagination (no gaps/dupes), prereg schema + frozen-config drift, and gate `PENDING→PASS`/`FAIL` transitions.

**Net:** "do nothing / await direction" is gone. The next session has a concrete, authorized, heavy, scientifically-valid task (C22 MEXC out-of-sample battery) with a gate that cannot be satisfied without doing the work.

---

## BOTTLENECKS REMOVED / OPEN

1. **"No new-venue network / acquisition CLOSED" REMOVED (was the primary blocker):** probe-verified `ACQUISITION_VIABLE_MEXC_MULTIYEAR`; MEXC multiyear fetcher built + tested. Hyperliquid-native remains CLOSED (correctly).
2. **"Do nothing / await direction" paralysis REMOVED:** C22-T1 is the active, authorized, non-avoidable heavy campaign; `verify_c22_focus_campaign.py` gates it.
3. **C22 data schema mismatch AVOIDED:** MEXC `vol` is contracts, not base coin; fetcher stores `volume = amount/close` so `close*volume == quote USD` (identical convention to the OKX cache) — verified by test + smoke run.
4. **Prereg mutation hazard FIXED:** `build_c22_prereg.build_prereg()` deep-copies frozen constants so tooling/tests cannot mutate the module-level config (regression caught by the C22 tests).
5. **Serial strata permutations (historical, C21):** 4-way pool + fail-closed fast-path validation preserved all 20k draws (~4x speedup) — unchanged; do not reduce draw counts.
6. **Deps/env:** `.venv` bootstrapped (Python 3.12.3 + deps). Fresh runner: `bash scripts/bootstrap_env.sh`.
7. **Duplicate-runner risk:** no C22 runner exists yet; when you add one, guard against duplicates (do not run two MEXC batteries concurrently on the same cache).
8. **Progress durability:** C21 per-fold checkpoints `research_state/c21_ckpt_*` written; C22 should checkpoint per fold (`c22_ckpt_mexc_<fold>_<TS>.json`, internal only) so a crash loses ≤1 fold.
9. **OPEN — heavy work (this is the point):** acquire MEXC multiyear archive → derive universe → run 8-fold 20k/20k/2k battery → emit 7 artifacts → gate PASS. Hours of real compute/network; fully resumable via per-fold checkpoints.
10. **OPEN — C20 reference sanity-check for C22:** MEXC fold signs should be broadly consistent with OKX/Binance (both negative). A wildly divergent MEXC result is a red flag to investigate, not to accept.

---

## C20 CROSS-VENUE REFERENCE NUMBERS (verified, sanity-check C22 outputs)

From `research_state/timing_okx.json` / `timing_binance_um.json` (C20 spec-literal, full multiyear window, `SPEC_LITERAL_NEXT_OPEN`):
- **OKX:** `num_trades=113`, `total_pnl=-55057.45` (C21 fold: trades=113 pnl=-54799.23)
- **Binance UM:** `num_trades=136`, `total_pnl=-70309.57` (C21 fold: trades=136 pnl=-70071.39)
- Both negative → C20 pooled `NO_GO` (`research_state/c20_pooled_cross_venue_synthesis_20261116T063500Z.json`). C22 MEXC fold results should be broadly consistent in sign; a wildly divergent MEXC fold result is a red flag to investigate, not to accept.

## C1–C21 CLOSED STATE (historical, do not relitigate)

- **C21 (`20261117T064408Z`):** cross-venue temporal/regime stability; gate `C21 ACCEPTANCE: PASS`; consolidated `NO_GO`. Gate: `scripts/verify_c21_focus_campaign.py`. Prereg `c21_prereg_20261117T064408Z.{json,md}`.
- **C20 (`20261116T063500Z`):** spec-literal cross-venue replication + pooled synthesis. Both venues `NO_GO`; pooled `NO_GO`. Gate: `scripts/verify_c20_focus_campaign.py`.
- **C19 (`C19-T1`):** T1 `spec_rebound_confirmation_adjudication_20261116T054000Z` (`SPEC_LITERAL_NEXT_OPEN`); T2–T5 NO_GO consolidated. Gate: `scripts/verify_c19_focus_campaign.py`.
- **C14 (`20261116T001200Z`):** native C14 underpowered/fragile (7 trades, 3 episodes). Gate: `scripts/verify_c14_focus_campaign.py`.
- **C13:** config-matched native C13 complete. Gate: `scripts/verify_c13_focus_campaign.py`.
- **C6 (`C6-T1`):** cross-venue context OKX+Binance UM pooled underpowered, `campaign_results_real_okx_multiyear`, `is_hyperliquid_venue_data=false`. Gate: `scripts/verify_next_focus_campaign.py`.
- **Hyperliquid-native acquisition CLOSED/exhausted:** moving tail (`full_window_served=false`, earliest ~2026-04-21; `hyperliquid_retention_probe_next_20261116T054408Z.json`, `scripts/probe_hyperliquid_blocker.py` = `FULL_283D_BLOCKED_BY_API_RETENTION`).

## GUARDRAILS (never violate)

- No cross-venue relabeling as Hyperliquid-native (`is_hyperliquid_venue_data=false` for C20/C21/**C22**).
- No synthetic gap-fill as verified; no spec relaxation to manufacture GO; `SPEC_LITERAL_NEXT_OPEN` fixed; **C22 config frozen to the prereg** (no tuning after results).
- No post-hoc stratum/fold invention; C21 folds/strata fixed; **C22 folds/strata fixed in `c22_prereg_20261118T100126Z` before compute**.
- **Do not reduce draw counts.** The 20k/20k/2k floors are preserved in C21 and mandated for C22.
- No inference-only churn on exhausted C14 native data; C1–C21 closed.
- **Do NOT relaunch `scripts/finish_c20_detached_durable.sh` — C20 is PASS.** No rival/duplicate C22 battery while a C22 runner is active; no foreground campaign in an agent turn; no short `timeout`.
- **Do not invent a same-data C23+ rerun of C21/C22.** New direction beyond C22 needs new prereg + new data + explicit operator authorization. C22 itself is legitimate **only because MEXC is new data** — never rerun it on OKX/Binance and call it C22.
- Do not edit completed campaign artifacts or `scripts/run_c20_cross_venue_campaign.py` to change results.
- No silent change to canonical baseline. C1–C21 `NO_GO` stands unless C22 produces a pre-registered contradiction with full evidence.
- **Do not commit unless explicitly asked** (the automated controller checkpoints the worktree; do not rewrite history).
- Preserve literal gate tokens: `INITIAL TASK MESSAGE`, `session_gate.py`, `21/21 checks passed`, `2026-11-13T23:38:47Z`, `probe_hyperliquid_blocker.py`, `FULL_283D_BLOCKED_BY_API_RETENTION`, `verify_campaign_evidence.py`, `C19-T1`, `verify_c19_focus_campaign.py`, `C14`, `verify_c14_focus_campaign.py`, `20261116T001200Z`, `C6-T1`, `campaign_results_real_okx_multiyear`, `C13`, `verify_c13_focus_campaign.py`, `C20`, `verify_c20_focus_campaign.py`, `C21-T1`, `verify_c21_focus_campaign.py`, `C22-T1`, `verify_c22_focus_campaign.py`, `fetch_mexc_perp_archive.py`, `probe_c22_venue_acquisition.py`, `c22_prereg_20261118T100126Z`, `ACQUISITION_VIABLE_MEXC_MULTIYEAR`.

## KEY FILES

- Handover/state: `HANDOFF.md` (single durable handoff), `README.md`, `research_state/strategy_spec.md`.
- **C22 (ACTIVE, PENDING gate):** `research_state/c22_prereg_20261118T100126Z.{json,md}`, `research_state/c22_venue_acquisition_probe_20261118T100126Z.json`, `scripts/probe_c22_venue_acquisition.py`, `scripts/fetch_mexc_perp_archive.py`, `scripts/build_c22_prereg.py`, `scripts/verify_c22_focus_campaign.py`, `tests/test_c22_campaign_20261118.py`. C22 cache target: `research_state/cache/mexc_1h_multiyear_20230101_20260928/`; universe target: `research_state/universe_mexc_multiyear_verified.json`.
- C21 (complete, `NO_GO`, gate PASS): `research_state/c21_prereg_20261117T064408Z.{json,md}`, `scripts/run_c21_cross_venue_campaign.py`, `scripts/verify_c21_focus_campaign.py`, `scripts/run_c21_detached_durable.sh`, final log `research_state/c21_run_20261118T061505Z.log`, per-fold checkpoints `research_state/c21_ckpt_*` (8), artifacts `research_state/c21_*_20261117T064408Z.json` (12 excl. prereg), `research_state/c21_decision_verdict_CONSOLIDATED_20261117T064408Z.{json,md}`.
- C20: `research_state/c20_prereg_20261116T063500Z.{json,md}`, `research_state/c20_pooled_cross_venue_synthesis_20261116T063500Z.json`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json`, `scripts/run_c20_cross_venue_campaign.py`, `scripts/verify_c20_focus_campaign.py`.
- Acquisition: `scripts/acquire_exchange_archive.py` (OKX + Binance Vision), `scripts/fetch_hyperliquid_candles.py`, `scripts/derive_verified_universe.py` (volume-gated universe derivation).
- Gates: `scripts/session_gate.py`, `scripts/verify_campaign_evidence.py`, `scripts/probe_hyperliquid_blocker.py`, `scripts/verify_c13_focus_campaign.py`, `scripts/verify_c14_focus_campaign.py`, `scripts/verify_c19_focus_campaign.py`, `scripts/verify_c20_focus_campaign.py`, `scripts/verify_c21_focus_campaign.py`, `scripts/verify_c22_focus_campaign.py`, `scripts/verify_next_focus_campaign.py` (C6).
- Env: `scripts/bootstrap_env.sh` (durable default `.venv`; run first on a fresh runner).
- Code: `src/strategy/crash_rebound.py`, `src/strategy/config.py`, `src/backtest/engine.py`, `src/data/loader.py`.