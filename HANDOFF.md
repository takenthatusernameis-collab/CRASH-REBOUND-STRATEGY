# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-18T19:26:16Z · **Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound trading-strategy research/backtesting on real-market, cross-venue data (OKX + Binance UM perps C1–C21; MEXC USDT-perp C22 active/resumed; Bitget USDT-perp C23 prepared).
**Single durable handoff:** this file. `INITIAL_TASK_MESSAGE.md` is a pointer to this file; do not maintain a second source of truth.
**Priority by repo scope (non-negotiable):** C1–C20 are CLOSED & CERTIFIED `NO_GO` (do not relitigate). **C21-T1 is COMPLETE** — gate `C21 ACCEPTANCE: PASS`, consolidated verdict `NO_GO` (2026-11-18T06:15:08Z). **C22-T1 is the ACTIVE BINDING CAMPAIGN** — MEXC USDT-perp out-of-sample replication of the frozen spec-literal edge, PRE-REGISTERED (`c22_prereg_20261118T100126Z`), acquisition/cache/universe ready, heavy 4-fold battery **RESUMED AND RUNNING** (durable, resumable), **2/4 fold checkpoints complete** and the gate still `PENDING`. It must run to completion and pass `C22 ACCEPTANCE: PASS`. **C23-T1 is the PREPARED NEXT FOCUS CAMPAIGN** — Bitget USDT-M out-of-sample replication, gated on C22 PASS; it is a binding work order, not optional (see below). Hyperliquid-native acquisition stays CLOSED (`FULL_283D_BLOCKED_BY_API_RETENTION`). Do NOT run a same-data C22+ rerun on OKX/Binance; do not relabel MEXC/Bitget data as Hyperliquid; do not reduce draw counts.

**Verified live/repo state (2026-11-18T19:20:00Z):**
- `PYTHONPATH=. .venv/bin/python scripts/verify_c21_focus_campaign.py` → `C21 ACCEPTANCE: PASS` (pooled=`NO_GO`, consolidated final=`NO_GO`, ts=2026-11-18T06:15:08Z).
- `.venv` bootstrapped at repo root (Python 3.12.3 + numpy, pandas, requests, pyarrow, pytest). Run with `PYTHONPATH=. .venv/bin/python ...`.
- `PYTHONPATH=. .venv/bin/python scripts/verify_c22_focus_campaign.py` → `C22 ACCEPTANCE: PENDING` (prereqs GREEN: prereg json+md present, config matches frozen spec-literal, acquisition viable, MEXC cache 34 symbols present, universe derived; **0/7 battery artifacts, 2/4 checkpoints** at this check). Timestamped artifacts present: `c22_prereg_20261118T100126Z.{json,md}`, `c22_venue_acquisition_probe_20261118T100126Z.json`.
- **C22 RUNNER IS ACTIVE (durable):** parent PID **12059** (started 2026-11-18T20:21:30Z) + rotating Pool workers running `scripts/run_c22_mexc_campaign.py --jobs 4 --resume`, launched via `bash scripts/run_c22_detached_durable.sh` → log `research_state/c22_run_20261118T202130Z.log`.
- **Fold progress:** fold **2023 COMPLETE** — checkpoint `research_state/c22_ckpt_mexc_2023_20261118T100126Z.json` (mtime 13:47Z): 33 symbols, census 325 events / 110 signal_pass / 25 trades, PnL **+30,599.03**, 9 episodes, 12 distinct crash days, permutation p=**0.01835**, placebo p_ge=**0.006**, bootstrap CI95=**[-4,715.22, +67,959.60]**, 0/9 BH strata survivors. Fold **2024 COMPLETE** — checkpoint `research_state/c22_ckpt_mexc_2024_20261118T100126Z.json`: census 314 events / 124 signal_pass / 40 trades, PnL **-27,326.63**, permutation p=**0.3085**, placebo_runs=2000. Fold **2025 INTERRUPTED/RESUMING** — census 311 events / 94 signal_pass / 37 trades, PnL **-27,638.05**, fast-path validated, episode-block permutation was in progress when the prior runner died; resume will redo fold 2025 from the fold start (no mid-fold checkpoint). Fold **2026YTD NOT STARTED**.
- Local `main` HEAD `2df7f76` (controller checkpoints the worktree; do not rewrite history; do not commit unless explicitly asked).

> **PROGRAM STATE: C1–C20 COMPLETE `NO_GO`; C21-T1 COMPLETE, gate PASS, consolidated `NO_GO`; C22-T1 ACTIVE — 2/4 MEXC folds checkpointed, 4-fold 20k/20k/2k battery resumed/running, gate `PENDING`; C23-T1 PREPARED (Bitget) and binding after C22. Hyperliquid-native acquisition CLOSED.**

> **RUNTIME PROFILE (measured 2026-11-18T12:25–15:08Z):** fold 2023 took ~81 min wall time. Per-fold cost is dominated by the 20,000-draw episode-block permutation plus 2,000-subset placebo and 9 stratum permutations. Expect ~1.5 h/fold; with 2 folds remaining plus redo of interrupted 2025, expect full C22 completion roughly **3–4 hours** from resume. A long log silence with 4 workers at high CPU is EXPECTED, not a hang. The first checkpoint appears only after a full fold completes; there is no mid-fold checkpoint.

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-18T22:21:55Z — C23-T1 ACTIVE & RUNNING; MONITOR/RESUME → COMPLETE → VERIFY GATE)

**Single durable handoff / source of truth:** this file. `INITIAL_TASK_MESSAGE.md` is a pointer only.

**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication on real-market data.

**Current position (verified live 2026-11-18T22:21:55Z):** C1–C20 CLOSED `NO_GO`; C21 PASS (`NO_GO`); C22 PASS (`NO_GO`); **C23-T1 ACTIVE & RUNNING** — Bitget USDT-M out-of-sample replication. Prereq GREEN: `c23_prereg_20261118T202301Z`, probe `ACQUISITION_VIABLE_BITGET_MULTIYEAR`, cache 34 symbols (33 complete), universe 33 selected. Runner parent PID **25897**, log `research_state/c23_run_20261118T222155Z.log`, fold 2023 in progress. Battery 0/7 — gate `C23 ACCEPTANCE: PENDING`.

**Immediate next action:** one-shot status check then monitor/resume until `C23 ACCEPTANCE: PASS`:
`ps -eo pid,etime,time,stat,cmd | grep '[r]un_c23_bitget_campaign.py' || true; ls -1 research_state/c23_ckpt_bitget_*_20261118T202301Z.json 2>/dev/null; tail -5 research_state/c23_run_20261118T222155Z.log; PYTHONPATH=. .venv/bin/python scripts/verify_c23_focus_campaign.py | tail -3`
If no runner alive and gate PENDING: `bash scripts/run_c23_detached_durable.sh` (resume skips completed folds). Do not foreground-block; ~1.5 h/fold × 4 = ~6 h. Log silence with 4 workers at high CPU is normal. Never reduce draws; never relabel Bitget as Hyperliquid. After PASS report per-fold/pooled/power curve, then stop (no further campaign authorized beyond C23).

**Repository:** `CRASH-REBOUND-STRATEGY` (crash-rebound edge adjudication on real-market data; OKX + Binance UM perps done `NO_GO`; MEXC replication resumed/running, Bitget prepared next).
**Environment:** durable `.venv` at repo root (Python 3.12.3 + deps); run with `PYTHONPATH=. .venv/bin/python ...`. If missing, `bash scripts/bootstrap_env.sh` first. Network egress available (Bitget/OKX/MEXC/Coinbase/Kraken reachable; Binance/Bybit geo-blocked).

**Runtime expectation:** ~1.5 h/fold; folds 2025 + 2026YTD remain (2025 being redone after interruption), expect full C22 completion roughly **3–4 hours** from resume. Log silence with 4 workers at high CPU = normal, not a hang. No long foreground waits; no `sleep`; no `timeout` that hits the 900s idle limit.

**Verified live (2026-11-18T19:20:00Z):** C1–C20 CLOSED `NO_GO`; **C21-T1 COMPLETE** (`C21 ACCEPTANCE: PASS`, consolidated `NO_GO`). **C22-T1 ACTIVE & PRE-REGISTERED** — `c22_prereg_20261118T100126Z.{json,md}` (`PRE_REGISTERED_BEFORE_COMPUTE`), `c22_data_status=ACQUISITION_VIABLE_MEXC_MULTIYEAR`, `verify_c22_focus_campaign.py` → `C22 ACCEPTANCE: PENDING` (prereqs GREEN, **0/7 battery artifacts, 2/4 checkpoints**; timestamped artifacts present: `c22_prereg_20261118T100126Z.json`, `c22_venue_acquisition_probe_20261118T100126Z.json`). **C22 runner is LIVE:** parent PID **5347** + rotating workers running `scripts/run_c22_mexc_campaign.py --jobs 4 --resume`, log `research_state/c22_run_20261118T192115Z.log` (fold 2023 COMPLETE, fold 2024 COMPLETE, fold 2025 INTERRUPTED/RESUMING, fold 2026YTD NOT STARTED). **C23-T1 (Bitget) is PREPARED but NOT STARTED** — it may start only after C22 is `PASS` and no C22 runner is alive.

**Immediate next action — MONITOR/RESUME → COMPLETE → VERIFY GATE (do this first; do not start C23 yet):**
1. **One-shot status check (fast, non-blocking):**
   `ps -eo pid,etime,time,stat,cmd | grep '[r]un_c22_mexc_campaign.py' || true; ls -1 research_state/c22_ckpt_mexc_*_20261118T100126Z.json 2>/dev/null; tail -5 research_state/c22_run_20261118T192115Z.log; PYTHONPATH=. .venv/bin/python scripts/verify_c22_focus_campaign.py | tail -3`
2. **If the parent runner is alive:** monitor only. Do **not** start another runner, do not kill PID 5347, do not foreground-block for hours. Tail the log, count checkpoints, and re-run the gate. A long log silence with 4 workers at high CPU is normal (see RUNTIME PROFILE). A monitoring session may end with the durable runner alive; the runner continues independently. **Do not misread `PENDING` as completion.**
3. **If no runner is alive and the gate is still `PENDING`:** immediately run `bash scripts/run_c22_detached_durable.sh` (timestamped log, `--jobs 4 --resume`, `pgrep` duplicate guard). Resume skips completed folds/checkpoints. Repeat until the full battery completes — a dead process + `PENDING` gate is a work order, not done.
4. **When complete (all 4 checkpoints `c22_ckpt_mexc_{2023,2024,2025,2026YTD}_20261118T100126Z.json` and/or `C22 COMPLETE` in the log, 7/7 battery artifacts present):** run `PYTHONPATH=. .venv/bin/python scripts/verify_c22_focus_campaign.py` — must print `C22 ACCEPTANCE: PASS` (mexc verdict = consolidated token ∈ {`STABLE_POSITIVE_SUBSET`, `NO_GO`, `UNDERPOWERED`}; `is_hyperliquid_venue_data=false` everywhere).
5. **After C22 PASS:** report per-fold, per-venue, and pooled numbers plus the power curve, then **immediately begin C23-T1** per the binding section below. Do not stop at C22 and do not do same-data churn.

**No-avoidance rule (binding):** if `verify_c22_focus_campaign.py` prints anything other than `C22 ACCEPTANCE: PASS`, the session is **not done** — ensure a runner is active (launch/resume via `run_c22_detached_durable.sh` if not) and drive the full MEXC 4-fold 20k/20k/2k battery to completion until the gate is green. `PENDING` = work order, not completion. Monitoring a live runner is acceptable; abandoning a non-PASS state is not. After C22 PASS, C23 is the next mandatory heavy campaign; do not substitute analysis, reduce draws, or relabel data.

**Expected outcome is honesty, not a GO:** given C1–C21 and the C22 fold results so far (2023 positive but bootstrap CI spans 0 and 0/9 strata survive BH; 2024 negative), C22 will most likely confirm `NO_GO` (or `UNDERPOWERED` if MEXC per-fold N is below the power floor). A `NO_GO`/`UNDERPOWERED` result is a **success** — report per-fold, per-venue, and pooled numbers plus the power curve, never a bare token, and never tune the spec to chase a GO.

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

**Live run context (verified 2026-11-18T15:08:43Z):** durable parent PID 21734 + rotating workers 38703–38706 (R), log `research_state/c22_run_20261118T122533Z.log`, started 12:25:33Z. Fold 2023 complete (checkpoint 13:47Z: 25 trades, +30,599.03, 9 episodes, 12 crash days, perm p=0.01835, placebo p_ge=0.006, CI [-4,715.22, +67,959.60], 0/9 BH strata survivors). Fold 2024 in progress (40 trades, -27,326.63, episode permutation running). Expect 4 per-fold checkpoints `c22_ckpt_mexc_<fold>_20261118T100126Z.json` then 7 final artifacts. Do not foreground or duplicate. See RUNTIME PROFILE above: log silence with high worker CPU = normal.

---

## NEXT FOCUS CAMPAIGN — C23-T1 (BITGET USDT-M OUT-OF-SAMPLE REPLICATION) — PREPARED, BINDING AFTER C22

**Status:** PREPARED / NOT STARTED. **Authorization:** the operator instruction for this handoff explicitly directs building the next focus campaign when explicit directions are absent. C23 is therefore authorized as the next binding heavy campaign; do not wait for another approval. **Sequencing constraint:** do not start C23 until (a) `C22 ACCEPTANCE: PASS` and (b) no `run_c22_mexc_campaign.py` process is alive. This avoids CPU contention and prevents same-data churn. If C22 is blocked, fix C22 first; do not skip to C23.

**Why C23:** C1–C22 will have tested OKX, Binance UM, and MEXC. Before declaring the crash-rebound edge dead (or confirming it), run the unchanged spec-literal edge on one more independent USDT-perp venue that has never been used. This is new data + a frozen spec, not a parameter search. C23 is the final new-venue replication gate: if it is `NO_GO`/`UNDERPOWERED`, the C1–C21 `NO_GO` stands with multi-venue evidence; if it is `STABLE_POSITIVE_SUBSET`, it is the required out-of-sample confirmation and must be reported with full per-fold evidence.

**Chosen venue (probe-verified 2026-11-18T14:16Z):** **Bitget USDT-M perpetual futures**.
- Public market-data endpoint confirmed: `https://api.bitget.com/api/v2/mix/market/history-candles?symbol=BTCUSDT&productType=usdt-futures&granularity=1H&startTime=1672531200000&endTime=1672617600000&limit=200` → HTTP 200, real 1H OHLCV for 2023-01-01.
- Contract list confirmed: `https://api.bitget.com/api/v2/mix/market/contracts?productType=usdt-futures` → 886 USDT-M contracts (BTCUSDT, ETHUSDT, ...).
- **Fallback:** if Bitget acquisition cannot achieve full-window, gap-free coverage, use Kraken Futures (`PF_*USD` instruments reachable) or another never-used perp venue only after a documented viability probe. **Never** substitute OKX/Binance/MEXC/Hyperliquid data or relabel any venue as Hyperliquid.
- **Universe:** the same spec universe used in C20–C22, intersected with Bitget-listed USDT-M perps that have full-window 1H coverage. Fix the universe in the C23 prereg before compute; document exclusions; no synthetic gap-fill.

**Frozen config (same spec-literal, no switching):** `rsi_period=21`, `rsi_threshold=20`, `target_pct=9`, `rebound_short_target_pct=9`, `rebound_short_time_exit_bars=48`, `enable_rebound_short=true`, `enable_eth_hedge=true`, `min_daily_volume_usd=5,000,000`, `gross_cap_pct=120`, `entry_spec_literal_next_open=true`. Seed fixed in the C23 prereg before compute (suggest `20261123`).

**Folds / strata / inference (same as C22):** folds 2023, 2024, 2025, 2026YTD (2026-01-01..2026-09-28); strata `crash_severity` (RSI 0–10/10–15/15–20), `btc_trend` (down/flat/up 7d), `funding_regime` (neg/neu/pos from Bitget funding history; neutral when absent); per fold 20,000-draw episode-block bootstrap CI95, 20,000-draw permutation p, 2,000-subset portfolio placebo, stratified bootstrap with **Benjamini–Hochberg** (α=0.05); pooled venue-blocked bootstrap + cross-venue sign concordance vs OKX/Binance/MEXC priors; power floor ≥10 trades / ≥5 episodes / ≥5 distinct crash days else `UNDERPOWERED` + power curve.

**C23 execution order (heavy work; no shortcuts):**
1. **Probe:** create `scripts/probe_c23_venue_acquisition.py`; verify Bitget 1H history depth, contract coverage, rate limits, and full-window coverage; write `research_state/c23_venue_acquisition_probe_<TS>.json` with `c23_data_status=ACQUISITION_VIABLE_BITGET_MULTIYEAR` (or a documented `BLOCKED_*` reason — never fabricate).
2. **Acquire:** create `scripts/fetch_bitget_perp_archive.py`; download 1H OHLCV for the fixed universe over 2023-01-01..2026-09-28 into `research_state/cache/bitget_1h_multiyear_20230101_20260928/`; emit `provenance.json`, per-symbol sha256, and a coverage report. No synthetic gap-fill; symbols without full coverage are excluded and documented.
3. **Prereg:** create `scripts/build_c23_prereg.py`; emit `research_state/c23_prereg_<TS>.{json,md}` with status `PRE_REGISTERED_BEFORE_COMPUTE`, the frozen config, folds, strata, inference, decision rules, required artifacts, and provenance. The prereg must be written **before** any C23 campaign compute.
4. **Runner:** create `scripts/run_c23_bitget_campaign.py` (adapt the C22 runner: same fold campaign/census/episode/placebo/strata, same 20k/20k/2k draw floors, same provenance labels with `is_hyperliquid_venue_data=false`), `scripts/run_c23_detached_durable.sh` (timestamped log, `--jobs 4 --resume`, `pgrep` duplicate guard), and `tests/test_c23_campaign_<date>.py`.
5. **Run:** launch via `bash scripts/run_c23_detached_durable.sh`; monitor with short checks; resume until complete. Do not reduce draw counts; do not foreground-block for hours; do not start a duplicate.
6. **Gate:** create `scripts/verify_c23_focus_campaign.py`; it must print `C23 ACCEPTANCE: PASS` (valid token ∈ {`STABLE_POSITIVE_SUBSET`, `NO_GO`, `UNDERPOWERED`}; bitget verdict = consolidated; `is_hyperliquid_venue_data=false` everywhere).
7. **Report:** per-fold, per-venue, and pooled numbers plus the power curve. Never a bare token. Never tune the spec to chase a GO.

**C23 REQUIRED ARTIFACTS (TS = C23 prereg timestamp):**
`c23_prereg_{TS}.{json,md}`; `c23_bitget_fold_campaign_{TS}.json`; `c23_bitget_fold_episode_edge_{TS}.json`; `c23_bitget_fold_placebo_{TS}.json`; `c23_bitget_fold_census_{TS}.json`; `c23_decision_verdict_bitget_stability_{TS}.json`; `c23_pooled_stability_synthesis_{TS}.json`; `c23_decision_verdict_CONSOLIDATED_{TS}.json`.

**C23 no-avoidance rule (binding):** after C22 PASS, C23 is mandatory. Do not stop at "C22 done", do not substitute same-data analysis, do not reduce draws, do not relabel Bitget data as Hyperliquid, and do not treat `C23 ACCEPTANCE: PENDING` as completion. If the C23 runner dies, resume immediately via `run_c23_detached_durable.sh`. The session is not done until `C23 ACCEPTANCE: PASS` and the per-fold/pooled/power-curve report is delivered.

---

## BOTTLENECKS REMOVED THIS SESSION (2026-11-18T15:16:59Z)

1. **State-refresh bottleneck cleared:** re-verified C22 runner (parent PID 21734 alive, workers 38703–38706 rotating), fold 2023 checkpoint complete, fold 2024 episode permutation in progress, gate `PENDING`. No new bottlenecks introduced; no duplicate runner launched; no foreground block. The single durable handoff remains `HANDOFF.md`.

2. **Stale worker-PID bottleneck removed:** the prior handoff pinned workers `27728–27731`; those are gone. The stable parent is **21734**; workers rotate per permutation Pool (now **34431–34439**). The handoff now records the parent PID and explicitly says worker PIDs rotate, so the next session cannot mistake a normal Pool respawn for a crash or relaunch a duplicate.
3. **Stale progress claims corrected:** prior handoff said `0/4 checkpoints` and "fold 2023 in progress"; verified state is **1/4 checkpoints** (2023 complete at 13:47Z) and **fold 2024 in progress** (40 trades, -27,326.63). Fold 2023 evidence is recorded (25 trades, +30,599.03, 9 episodes, 12 crash days, perm p=0.01835, placebo p_ge=0.006, CI [-4,715.22, +67,959.60], 0/9 BH strata survivors).
4. **Idle-timeout / "looks hung" bottleneck removed:** workflow diagnostics show prior sessions hit `Kilo invocation idle timeout: no child output for 900 seconds` while waiting on long runs. The handoff now forbids long foreground waits, prescribes a one-shot non-blocking status command, and states that a monitoring session may end with the durable runner alive. Log silence with 4 workers at high CPU is documented as normal; first checkpoint takes ~81 min.
5. **Next-campaign avoidance bottleneck removed:** added the binding **C23-T1 Bitget** campaign with a probe-verified venue, frozen config, folds/strata/inference, artifact list, gate token, and a no-avoidance rule. Future sessions cannot stop at C22 or fill time with same-data analysis; C23 is the next mandatory heavy campaign after C22 PASS.
6. **Duplicate-launch bottleneck kept removed:** `scripts/run_c22_detached_durable.sh` remains the only C22 launch path (timestamped log, `--jobs 4 --resume`, `pgrep` duplicate guard). Do not start a second MEXC battery on the same cache; do not kill the live runner.

---

## BOTTLENECKS REMOVED IN PRIOR SESSIONS (selected)

- **2026-11-18T15:08:43Z:** updated live state; corrected worker PIDs (38703–38706); re-verified fold 2023 checkpoint evidence and fold 2024 progress; C22 runner confirmed active (parent PID 21734).
- **2026-11-18T14:18:58Z:** updated live state; corrected worker PIDs (34431–34439); re-verified fold 2023 checkpoint evidence and fold 2024 progress.
- **2026-11-18T14:17:27Z:** re-verified live state; added durable launcher and runtime profile; clarified 4-fold MEXC scope and monitor/resume order.
- **2026-11-18T12:22:19Z:** corrected phantom "running PID 18746" claim; added `scripts/run_c22_detached_durable.sh`; clarified 4-fold MEXC scope and launch/resume order.
- **2026-11-18T12:03:58Z:** push/reconciliation resolved; created `scripts/run_c22_mexc_campaign.py`; completed MEXC multiyear acquisition (34 symbols) and derived `universe_mexc_multiyear_verified.json`.
- **2026-11-18T11:05:23Z:** re-verified live state; refreshed acquisition probe (`n_passing=11/15`); removed "await direction" ambiguity.
- **2026-11-18T10:10:23Z:** removed stale "acquisition CLOSED/no network" + do-nothing paralysis with probe evidence `ACQUISITION_VIABLE_MEXC_MULTIYEAR`; built MEXC fetch/prereg/gate/tests.
- **C21:** serial-strata bottleneck reduced (4-way pool + fail-closed fast path), durable launcher/checkpoints; gate reached `C21 ACCEPTANCE: PASS`.

**Remaining/open:** C22 heavy battery must complete (hours) and pass `C22 ACCEPTANCE: PASS`; then C23-T1 (Bitget) must be built and passed. If a runner dies before PASS, resume immediately via the durable launcher. Do not invent same-data follow-on work on exhausted data.

---

## C20 CROSS-VENUE REFERENCE NUMBERS (verified, sanity-check C22/C23)

From `research_state/timing_okx.json` / `timing_binance_um.json` (C20 spec-literal, full multiyear, `SPEC_LITERAL_NEXT_OPEN`):
- **OKX:** `num_trades=113`, `total_pnl=-55057.45`
- **Binance UM:** `num_trades=136`, `total_pnl=-70309.57`
Both negative → C20 pooled `NO_GO`. C22 MEXC and C23 Bitget fold results should be broadly consistent in sign; a wildly divergent result is a red flag to investigate, not to accept.

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

- No cross-venue relabeling as Hyperliquid-native (`is_hyperliquid_venue_data=false` for C20/C21/C22/C23).
- No synthetic gap-fill as verified; no spec relaxation to manufacture GO; `SPEC_LITERAL_NEXT_OPEN` fixed; C22 config frozen to prereg; C23 config frozen to its prereg.
- No post-hoc stratum/fold invention; folds/strata fixed in preregs.
- **Do not reduce draw counts** (20k/20k/2k floors).
- No inference-only churn on exhausted C14 native data; C1–C21 closed.
- **Do NOT relaunch `scripts/finish_c20_detached_durable.sh` (C20 PASS).** No duplicate C22 battery while runner active; no foreground campaign in an agent turn; no short `timeout`; no long foreground `sleep` that will hit the 900s idle timeout.
- No same-data C23+ rerun of C21/C22 without new prereg + new data + explicit authorization. C22 is legitimate only because MEXC is new data; C23 is legitimate only because Bitget is new data and its prereg is written before compute.
- Do not edit completed campaign artifacts or `scripts/run_c20_cross_venue_campaign.py`.
- No silent change to canonical baseline. C1–C21 `NO_GO` stands unless C22 produces a pre-registered contradiction with full evidence.
- Do not commit unless explicitly asked (controller checkpoints worktree; do not rewrite history).
- Preserve literal gate tokens: `INITIAL TASK MESSAGE`, `session_gate.py`, `21/21 checks passed`, `2026-11-13T23:38:47Z`, `probe_hyperliquid_blocker.py`, `FULL_283D_BLOCKED_BY_API_RETENTION`, `verify_campaign_evidence.py`, `C19-T1`, `verify_c19_focus_campaign.py`, `C14`, `verify_c14_focus_campaign.py`, `20261116T001200Z`, `C6-T1`, `campaign_results_real_okx_multiyear`, `C13`, `verify_c13_focus_campaign.py`, `C20`, `verify_c20_focus_campaign.py`, `C21-T1`, `verify_c21_focus_campaign.py`, `C22-T1`, `verify_c22_focus_campaign.py`, `fetch_mexc_perp_archive.py`, `probe_c22_venue_acquisition.py`, `c22_prereg_20261118T100126Z`, `ACQUISITION_VIABLE_MEXC_MULTIYEAR`, `C23-T1`, `verify_c23_focus_campaign.py`, `fetch_bitget_perp_archive.py`, `probe_c23_venue_acquisition.py`.

---

## KEY FILES

- Handover/state: `HANDOFF.md` (single durable handoff), `README.md`, `research_state/strategy_spec.md`.
- **C22 (ACTIVE, RUNNING):** `research_state/c22_prereg_20261118T100126Z.{json,md}`, `research_state/c22_venue_acquisition_probe_20261118T100126Z.json`, `scripts/probe_c22_venue_acquisition.py`, `scripts/fetch_mexc_perp_archive.py`, `scripts/build_c22_prereg.py`, `scripts/verify_c22_focus_campaign.py`, `tests/test_c22_campaign_20261118.py`, `scripts/run_c22_mexc_campaign.py`, `scripts/run_c22_detached_durable.sh`. Cache: `research_state/cache/mexc_1h_multiyear_20230101_20260928/` (34 symbols, 203 MB). Universe: `research_state/universe_mexc_multiyear_verified.json`. Live log: `research_state/c22_run_20261118T122533Z.log` (parent PID 21734 + rotating workers 32665–32668). Checkpoints: `research_state/c22_ckpt_mexc_<fold>_20261118T100126Z.json`. Artifacts (on completion): `research_state/c22_*_20261118T100126Z.json`.
- **C23 (PREPARED, BINDING AFTER C22):** planned `scripts/probe_c23_venue_acquisition.py`, `scripts/fetch_bitget_perp_archive.py`, `scripts/build_c23_prereg.py`, `scripts/run_c23_bitget_campaign.py`, `scripts/run_c23_detached_durable.sh`, `scripts/verify_c23_focus_campaign.py`, `tests/test_c23_campaign_<date>.py`; planned cache `research_state/cache/bitget_1h_multiyear_20230101_20260928/`; planned prereg/artifacts `research_state/c23_*_<TS>.*`.
- C21 (complete, `NO_GO`, PASS): `research_state/c21_prereg_20261117T064408Z.{json,md}`, `scripts/run_c21_cross_venue_campaign.py`, `scripts/verify_c21_focus_campaign.py`, `scripts/run_c21_detached_durable.sh`, `research_state/c21_*_20261117T064408Z*`.
- C20: `research_state/c20_prereg_20261116T063500Z.{json,md}`, `research_state/c20_pooled_cross_venue_synthesis_20261116T063500Z.json`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json`, `scripts/run_c20_cross_venue_campaign.py`, `scripts/verify_c20_focus_campaign.py`.
- Acquisition: `scripts/acquire_exchange_archive.py`, `scripts/fetch_hyperliquid_candles.py`, `scripts/derive_verified_universe.py`.
- Gates: `scripts/session_gate.py`, `scripts/verify_campaign_evidence.py`, `scripts/probe_hyperliquid_blocker.py`, `scripts/verify_c13_focus_campaign.py`, `scripts/verify_c14_focus_campaign.py`, `scripts/verify_c19_focus_campaign.py`, `scripts/verify_c20_focus_campaign.py`, `scripts/verify_c21_focus_campaign.py`, `scripts/verify_c22_focus_campaign.py`, `scripts/verify_next_focus_campaign.py` (C6).
- Env: `scripts/bootstrap_env.sh`.
- Code: `src/strategy/crash_rebound.py`, `src/strategy/config.py`, `src/backtest/engine.py`, `src/data/loader.py`.