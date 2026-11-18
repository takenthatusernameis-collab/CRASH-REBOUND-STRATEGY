# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-18T13:42:27Z · **Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound trading-strategy research/backtesting on real-market, cross-venue data (OKX + Binance UM perps to date).
**Single durable handoff:** this file. `INITIAL_TASK_MESSAGE.md` is a pointer to this file; do not maintain a second source of truth.
**Priority by repo scope (non-negotiable):** C1–C20 are CLOSED & CERTIFIED `NO_GO` (do not relitigate, do not relaunch C20). **C21-T1 is COMPLETE** — gate `C21 ACCEPTANCE: PASS`, consolidated verdict `NO_GO` (2026-11-18T06:15:08Z). **C22-T1 is the ACTIVE BINDING CAMPAIGN** — MEXC USDT-perp out-of-sample replication of the frozen spec-literal edge, PRE-REGISTERED (`c22_prereg_20261118T100126Z`), acquisition VIABLE, data/inference infrastructure ready, and the heavy 4-fold battery **LAUNCHED AND RUNNING** (durable, resumable) as of this timestamp; it must run to completion and pass `C22 ACCEPTANCE: PASS`. Hyperliquid-native acquisition stays CLOSED (`FULL_283D_BLOCKED_BY_API_RETENTION`); **new-venue (MEXC) acquisition is OPEN/complete** (probe-verified, cache+universe present). Do NOT run a same-data C22+ rerun on OKX/Binance; do not relabel MEXC data as Hyperliquid; do not reduce draw counts.

**Verified live/repo state (2026-11-18T13:42:27Z):**
- `PYTHONPATH=. .venv/bin/python scripts/verify_c21_focus_campaign.py` → `C21 ACCEPTANCE: PASS` (pooled=`NO_GO`, consolidated final=`NO_GO`, ts=2026-11-18T06:15:08Z).
- `PYTHONPATH=. .venv/bin/python scripts/verify_c22_focus_campaign.py` → `C22 ACCEPTANCE: PENDING` (prereqs GREEN: prereg json+md present, config matches frozen spec-literal, acquisition viable, MEXC cache 34 symbols present, universe derived; **0/7 battery artifacts, 0/4 checkpoints** at this check). Timestamped artifacts present: `c22_prereg_20261118T100126Z.json`, `c22_venue_acquisition_probe_20261118T100126Z.json`.
- `PYTHONPATH=. .venv/bin/python -m pytest tests/test_c22_campaign_20261118.py -q` → `11 passed in 0.32s` (last run 2026-11-18T13:05Z).
- **C22 RUNNER IS ACTIVE (durable):** PID **21734** (Sl, etime ~01:16) + 4 workers **27728–27731** (R) running `scripts/run_c22_mexc_campaign.py --jobs 4 --resume`, launched 2026-11-18T12:25:33Z via `bash scripts/run_c22_detached_durable.sh` → log `research_state/c22_run_20261118T122533Z.log`. Fold 2023 episode-block permutation (20,000 draws, fast-path validated) in progress; log shows census=325 events, 110 signal_pass, 25 trades, PnL=+30,599. Prior "RUNNING PID 18746" claim was stale and is superseded.
- Local `main` HEAD `cdd58b7` (this session refreshed durable handoff pointers/state only; controller checkpoints the worktree; do not rewrite history).

> **PROGRAM STATE: C1–C20 COMPLETE `NO_GO`; C21-T1 COMPLETE, gate PASS, consolidated `NO_GO`; C22-T1 ACTIVE & RUNNING — pre-registered, acquisition/cache/universe/runner/gate ready, heavy 4-fold battery in progress (durable, resumable) and NOT YET COMPLETE (gate `PENDING`). Hyperliquid-native acquisition CLOSED; MEXC new-venue acquisition/data READY.**

> **RUNTIME PROFILE (measured 2026-11-18T13:08–13:42Z, use to size waits — do NOT relaunch):** per-fold cost is dominated by the 20,000-draw episode-block permutation (`_fold_episode_edge`), NOT the campaign/census. C21 reference per-fold `temporal_edge_permutation.wall_seconds` at `--jobs 4`: OKX 130–535s, Binance-UM 200–746s per fold (4 folds × 2 venues). C22 MEXC is a SINGLE venue, 4 folds, same 20k-draw fast-path-validated permutation, so expect ~1–4 hours total for the full 4-fold battery + strata (9 perms × 4 folds) + placebo. Fold 2023 (110 signal keys, 25 trades) has been in its 20k-draw episode permutation for ~70+ min as of 13:42Z (workers running, healthy); the first checkpoint `c22_ckpt_mexc_2023_20261118T100126Z.json` will appear only after the full fold (campaign+census+episode+placebo+strata) completes. A multi-hour wall time with 0 checkpoints early on is EXPECTED, not a hang.

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-18T13:42:27Z — C22 RUNNING; MONITOR/RESUME → COMPLETE → VERIFY GATE)

**Repository:** `CRASH-REBOUND-STRATEGY` (crash-rebound edge adjudication on real-market data; OKX + Binance UM perps done, MEXC replication in progress).
**Environment:** durable `.venv` at repo root (Python 3.12.3 + deps); run with `PYTHONPATH=. .venv/bin/python ...`. If missing, `bash scripts/bootstrap_env.sh` first. Network egress available (OKX/MEXC/Coinbase/Kraken reachable; Binance/Bybit geo-blocked).

**Verified live (2026-11-18T13:42:27Z):** C1–C20 CLOSED `NO_GO`; **C21-T1 COMPLETE** (`C21 ACCEPTANCE: PASS`, consolidated `NO_GO`). **C22-T1 ACTIVE & PRE-REGISTERED** — `c22_prereg_20261118T100126Z.{json,md}` (`PRE_REGISTERED_BEFORE_COMPUTE`), `c22_data_status=ACQUISITION_VIABLE_MEXC_MULTIYEAR`, `verify_c22_focus_campaign.py` → `C22 ACCEPTANCE: PENDING` (prereqs GREEN, **0/7 battery artifacts, 0/4 checkpoints**; timestamped artifacts present: `c22_prereg_20261118T100126Z.json`, `c22_venue_acquisition_probe_20261118T100126Z.json`). **C22 runner is LIVE (no duplicate):** PID **21734** (Sl, etime ~01:16) + 4 workers **27728–27731** (R) running `scripts/run_c22_mexc_campaign.py --jobs 4 --resume`, log `research_state/c22_run_20261118T122533Z.log` (launched 12:25:33Z). Fold 2023 episode-block permutation in progress: census=325 events, 110 signal_pass, 25 trades, PnL=+30,599 (fast-path validated). Prior "RUNNING PID 18746" claim stale/superseded.

**Binding constraint / state:**
1. **Battery is running, not finished.** 0/7 artifacts and 0/4 checkpoints at 13:42Z; gate remains `PENDING` until the full MEXC 4-fold 20k/20k/2k battery completes.
2. **Durable launcher exists and must be used for (re)start:** `bash scripts/run_c22_detached_durable.sh` — timestamped log, `nohup --jobs 4 --resume`, and `pgrep` duplicate guard (refuses if a runner is alive). Never start a duplicate MEXC battery on the same cache.
3. **Prereqs complete:** MEXC cache `research_state/cache/mexc_1h_multiyear_20230101_20260928/` (34 symbols, 203 MB), universe `research_state/universe_mexc_multiyear_verified.json`, runner `scripts/run_c22_mexc_campaign.py`, gate `scripts/verify_c22_focus_campaign.py`.
4. **This is new-data work (authorized).** MEXC is a venue never used in C1–C21; frozen config/folds/strata/inference from prereg are binding. No same-data rerun on OKX/Binance/MEXC under a new label.

**Immediate next action — MONITOR/RESUME → COMPLETE → VERIFY GATE:**
1. **Check if runner is alive:** `ps -eo pid,etime,time,stat,cmd | grep '[r]un_c22_mexc_campaign.py'`. If alive, **do not start another** — monitor only.
2. **Monitor progress:** tail `research_state/c22_run_20261118T122533Z.log`; watch for per-fold completion and `C22 COMPLETE`. Checkpoints appear as `research_state/c22_ckpt_mexc_<fold>_20261118T100126Z.json` for folds `2023`, `2024`, `2025`, `2026YTD`. First checkpoint is hours away — a long log silence with 4 workers at high CPU is normal, not a hang (see RUNTIME PROFILE above).
3. **If no runner is alive and gate is still PENDING:** immediately run `bash scripts/run_c22_detached_durable.sh` (resume skips completed folds/artifacts). Repeat until a run reaches completion — do not treat a dead process + `PENDING` gate as done.
4. **When complete (all 4 folds/checkpoints done, `C22 COMPLETE` logged or 7/7 artifacts present):** run `PYTHONPATH=. .venv/bin/python scripts/verify_c22_focus_campaign.py` — must print `C22 ACCEPTANCE: PASS` (token ∈ {`STABLE_POSITIVE_SUBSET`, `NO_GO`, `UNDERPOWERED`}; mexc verdict = consolidated; `is_hyperliquid_venue_data=false` everywhere).
5. **After PASS:** report per-fold, per-venue, and pooled numbers plus the power curve, then stop and await explicit operator direction. Do not start same-data C23+ without new prereg + new data + explicit authorization.

**No-avoidance rule (binding):** if `verify_c22_focus_campaign.py` prints anything other than `C22 ACCEPTANCE: PASS`, the session is **not done** — ensure a runner is active (launch/resume via `run_c22_detached_durable.sh` if not) and drive the full MEXC 4-fold 20k/20k/2k battery to completion until the gate is green. `PENDING` = work order, not completion. Monitoring a live runner is acceptable; abandoning a non-PASS state is not.

**Expected outcome is honesty, not a GO:** given C1–C21, C22 will most likely confirm `NO_GO` (or `UNDERPOWERED` if MEXC per-fold N is below the power floor). A `NO_GO`/`UNDERPOWERED` result is a **success** — report per-fold, per-venue, and pooled numbers plus the power curve, never a bare token, and never tune the spec to chase a GO.

---

## BINDING CAMPAIGN — C22-T1 (MEXC OUT-OF-SAMPLE REPLICATION) — ACTIVE, RUNNING

**Prereg:** `research_state/c22_prereg_20261118T100126Z.{json,md}` (`PRE_REGISTERED_BEFORE_COMPUTE`). **NEW-DATA campaign, not a same-data rerun.**

- **Question:** does the *unchanged* spec-literal crash-rebound edge replicate on MEXC USDT-perp 1H data (venue never used in C1–C21), over 2023-01-01..2026-09-28 with the same pre-specified folds/strata/inference as C21?
- **Frozen config (no switching):** `rsi_period=21`, `rsi_threshold=20`, `target_pct=9`, `rebound_short_target_pct=9`, `rebound_short_time_exit_bars=48`, `enable_rebound_short=true`, `enable_eth_hedge=true`, `min_daily_volume_usd=5,000,000`, `gross_cap_pct=120`, `entry_spec_literal_next_open=true`. Seed `20261122`.
- **Folds:** 2023, 2024, 2025, 2026YTD (2026-01-01..2026-09-28). **Strata:** `crash_severity` (RSI 0–10/10–15/15–20), `btc_trend` (down/flat/up 7d), `funding_regime` (neg/neu/pos; neutral when absent — MEXC has none).
- **Inference:** per fold 20,000-draw episode-block bootstrap CI95, 20,000-draw permutation p, 2,000-subset portfolio placebo, stratified bootstrap with **Benjamini–Hochberg** (α=0.05); pooled venue-blocked bootstrap + cross-venue sign concordance vs recorded OKX/Binance priors. Power floor: ≥10 trades / ≥5 episodes / ≥5 distinct crash days else `UNDERPOWERED` + power curve.
- **Decision rule:** `STABLE_POSITIVE_SUBSET` only if a pre-specified fold/stratum survives BH with bootstrap CI excluding 0 & positive spot leg, permutation p<0.05, placebo p_ge_canonical<0.05, N≥floor, AND same-direction effect in other venue(s) (or flagged single-venue exploratory). Otherwise `NO_GO` or `UNDERPOWERED`.
- **C22 is cross-venue** (`is_hyperliquid_venue_data=false`) — never Hyperliquid performance evidence.

**C22 REQUIRED ARTIFACTS (TS = `20261118T100126Z`)** — gate checks all 7 battery artifacts + prereg:
`c22_prereg_{TS}.{json,md}`; `c22_mexc_fold_campaign_{TS}.json`; `c22_mexc_fold_episode_edge_{TS}.json`; `c22_mexc_fold_placebo_{TS}.json`; `c22_mexc_fold_census_{TS}.json`; `c22_decision_verdict_mexc_stability_{TS}.json`; `c22_pooled_stability_synthesis_{TS}.json`; `c22_decision_verdict_CONSOLIDATED_{TS}.json`.

**Live run context (verified 2026-11-18T13:42:27Z):** durable run PID 21734 + workers 27728–27731 (R, etime ~01:16), log `research_state/c22_run_20261118T122533Z.log`, started 12:25:33Z, fold 2023 episode permutation in progress (census=325, signal_pass=110, trades=25, PnL=+30,599). Expect 4 per-fold checkpoints `c22_ckpt_mexc_<fold>_20261118T100126Z.json` then 7 final artifacts. Do not foreground or duplicate. See RUNTIME PROFILE above: first checkpoint is hours away; log silence with high worker CPU = normal.

---

## BOTTLENECK REMOVED THIS SESSION (2026-11-18T13:42:27Z)

1. **Live state re-verified (no guesswork):** `ps` confirms runner PID 21734 + 4 workers (27728–27731, R, etime ~01:16) active; log `research_state/c22_run_20261118T122533Z.log` shows fold 2023 census=325 events, 110 signal_pass, 25 trades, PnL=+30,599 (fast-path validated); `verify_c22_focus_campaign.py` → `C22 ACCEPTANCE: PENDING` (prereqs green, 0/7 battery, 0/4 checkpoints; 2 prereg/probe artifacts present). No duplicate runner, no relaunch.
2. **"Looks hung / relaunch / avoid heavy work" bottleneck kept removed:** runtime profile (measured) recorded — 20k-draw episode-block permutation dominates (C21 ref 130–746s/fold; C22 single-venue ~1–4h). Fold 2023 in episode permutation ~70+ min at 13:42Z with no checkpoint yet is EXPECTED, not a hang; first checkpoint appears only after full fold. Duplicate-guarded durable launcher `scripts/run_c22_detached_durable.sh` and per-fold `--resume` checkpoints remain the continuity mechanism.
3. **Durable handoff refreshed as single source of truth:** `HANDOFF.md` and `INITIAL_TASK_MESSAGE.md` (pointer) updated with current timestamp, exact PIDs/worker states, gate/artifact counts, log evidence, runtime expectation, and binding monitor/resume → complete → gate-PASS instructions so the next session cannot avoid the heavy in-progress campaign or misread `PENDING` as completion.

---

## BOTTLENECKS REMOVED IN PRIOR SESSIONS (selected)

- **2026-11-18T12:22:19Z:** corrected phantom "running PID 18746" claim; added `scripts/run_c22_detached_durable.sh`; clarified 4-fold MEXC scope and launch/resume order.
- **2026-11-18T12:03:58Z:** push/reconciliation resolved (remote=local 0ef8556 at the time); created `scripts/run_c22_mexc_campaign.py`; completed MEXC multiyear acquisition (34 symbols) and derived `universe_mexc_multiyear_verified.json`.
- **2026-11-18T11:05:23Z:** re-verified live state; refreshed acquisition probe (`n_passing=11/15`); removed "await direction" ambiguity.
- **2026-11-18T10:10:23Z:** removed stale "acquisition CLOSED/no network" + do-nothing paralysis with probe evidence `ACQUISITION_VIABLE_MEXC_MULTIYEAR`; built MEXC fetch/prereg/gate/tests.
- **C21:** serial-strata bottleneck reduced (4-way pool + fail-closed fast path), durable launcher/checkpoints; gate reached `C21 ACCEPTANCE: PASS`.

**Remaining/open:** C22 heavy battery must complete (hours) and pass `C22 ACCEPTANCE: PASS`; if runner dies before PASS, resume immediately via `run_c22_detached_durable.sh`. Do not invent same-data follow-on work on exhausted data.

---

## C20 CROSS-VENUE REFERENCE NUMBERS (verified, sanity-check C22)

From `research_state/timing_okx.json` / `timing_binance_um.json` (C20 spec-literal, full multiyear, `SPEC_LITERAL_NEXT_OPEN`):
- **OKX:** `num_trades=113`, `total_pnl=-55057.45`
- **Binance UM:** `num_trades=136`, `total_pnl=-70309.57`
Both negative → C20 pooled `NO_GO`. C22 MEXC fold results should be broadly consistent in sign; a wildly divergent result is a red flag to investigate, not to accept.

---

## C1–C21 CLOSED STATE (historical, do not relitigate)

- **C21 (`20261117T064408Z`):** gate `C21 ACCEPTANCE: PASS`; consolidated `NO_GO`. `scripts/verify_c21_focus_campaign.py`, prereg `c21_prereg_20261117T064408Z.{json,md}`, artifacts/checkpoints in `research_state/c21_*_20261117T064408Z*`.
- **C20 (`20261116T063500Z`):** pooled `NO_GO`. `scripts/verify_c20_focus_campaign.py`.
- **C19 (`C19-T1`):** T1 `spec_rebound_confirmation_adjudication_20261116T054000Z` (`SPEC_LITERAL_NEXT_OPEN`); T2–T5 NO_GO. `scripts/verify_c19_focus_campaign.py`.
- **C14 (`20261116T001200Z`):** native underpowered/fragile (7 trades, 3 episodes). `scripts/verify_c14_focus_campaign.py`.
- **C13:** config-matched native complete. `scripts/verify_c13_focus_campaign.py`.
- **C6 (`C6-T1`):** OKX+Binance UM pooled underpowered, `campaign_results_real_okx_multiyear`, `is_hyperliquid_venue_data=false`. `scripts/verify_next_focus_campaign.py`.
- **Hyperliquid-native acquisition CLOSED/exhausted:** `FULL_283D_BLOCKED_BY_API_RETENTION` (tail ~2026-04-21). `scripts/probe_hyperliquid_blocker.py`.

---

## GUARDRAILS (never violate)

- No cross-venue relabeling as Hyperliquid-native (`is_hyperliquid_venue_data=false` for C20/C21/C22).
- No synthetic gap-fill as verified; no spec relaxation to manufacture GO; `SPEC_LITERAL_NEXT_OPEN` fixed; C22 config frozen to prereg.
- No post-hoc stratum/fold invention; folds/strata fixed in preregs.
- **Do not reduce draw counts** (20k/20k/2k floors).
- No inference-only churn on exhausted C14 native data; C1–C21 closed.
- **Do NOT relaunch `scripts/finish_c20_detached_durable.sh` (C20 PASS).** No duplicate C22 battery while runner active; no foreground campaign in an agent turn; no short `timeout`.
- No same-data C23+ rerun of C21/C22 without new prereg + new data + explicit authorization. C22 is legitimate only because MEXC is new data.
- Do not edit completed campaign artifacts or `scripts/run_c20_cross_venue_campaign.py`.
- No silent change to canonical baseline. C1–C21 `NO_GO` stands unless C22 produces a pre-registered contradiction with full evidence.
- Do not commit unless explicitly asked (controller checkpoints worktree; do not rewrite history).
- Preserve literal gate tokens: `INITIAL TASK MESSAGE`, `session_gate.py`, `21/21 checks passed`, `2026-11-13T23:38:47Z`, `probe_hyperliquid_blocker.py`, `FULL_283D_BLOCKED_BY_API_RETENTION`, `verify_campaign_evidence.py`, `C19-T1`, `verify_c19_focus_campaign.py`, `C14`, `verify_c14_focus_campaign.py`, `20261116T001200Z`, `C6-T1`, `campaign_results_real_okx_multiyear`, `C13`, `verify_c13_focus_campaign.py`, `C20`, `verify_c20_focus_campaign.py`, `C21-T1`, `verify_c21_focus_campaign.py`, `C22-T1`, `verify_c22_focus_campaign.py`, `fetch_mexc_perp_archive.py`, `probe_c22_venue_acquisition.py`, `c22_prereg_20261118T100126Z`, `ACQUISITION_VIABLE_MEXC_MULTIYEAR`.

---

## KEY FILES

- Handover/state: `HANDOFF.md` (single durable handoff), `README.md`, `research_state/strategy_spec.md`.
- **C22 (ACTIVE, RUNNING):** `research_state/c22_prereg_20261118T100126Z.{json,md}`, `research_state/c22_venue_acquisition_probe_20261118T100126Z.json`, `scripts/probe_c22_venue_acquisition.py`, `scripts/fetch_mexc_perp_archive.py`, `scripts/build_c22_prereg.py`, `scripts/verify_c22_focus_campaign.py`, `tests/test_c22_campaign_20261118.py`, `scripts/run_c22_mexc_campaign.py`, `scripts/run_c22_detached_durable.sh`. Cache: `research_state/cache/mexc_1h_multiyear_20230101_20260928/` (34 symbols, 203 MB, 32808 hourly bars/symbol target); universe: `research_state/universe_mexc_multiyear_verified.json`. Live log: `research_state/c22_run_20261118T122533Z.log` (PID 21734 + workers 27728–27731). Checkpoints: `research_state/c22_ckpt_mexc_<fold>_20261118T100126Z.json`. Artifacts (on completion): `research_state/c22_*_20261118T100126Z.json`.
- C21 (complete, `NO_GO`, PASS): `research_state/c21_prereg_20261117T064408Z.{json,md}`, `scripts/run_c21_cross_venue_campaign.py`, `scripts/verify_c21_focus_campaign.py`, `scripts/run_c21_detached_durable.sh`, `research_state/c21_*_20261117T064408Z*`.
- C20: `research_state/c20_prereg_20261116T063500Z.{json,md}`, `research_state/c20_pooled_cross_venue_synthesis_20261116T063500Z.json`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json`, `scripts/run_c20_cross_venue_campaign.py`, `scripts/verify_c20_focus_campaign.py`.
- Acquisition: `scripts/acquire_exchange_archive.py`, `scripts/fetch_hyperliquid_candles.py`, `scripts/derive_verified_universe.py`.
- Gates: `scripts/session_gate.py`, `scripts/verify_campaign_evidence.py`, `scripts/probe_hyperliquid_blocker.py`, `scripts/verify_c13_focus_campaign.py`, `scripts/verify_c14_focus_campaign.py`, `scripts/verify_c19_focus_campaign.py`, `scripts/verify_c20_focus_campaign.py`, `scripts/verify_c21_focus_campaign.py`, `scripts/verify_c22_focus_campaign.py`, `scripts/verify_next_focus_campaign.py` (C6).
- Env: `scripts/bootstrap_env.sh`.
- Code: `src/strategy/crash_rebound.py`, `src/strategy/config.py`, `src/backtest/engine.py`, `src/data/loader.py`.
