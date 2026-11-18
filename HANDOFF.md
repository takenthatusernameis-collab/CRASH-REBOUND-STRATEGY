# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-18T23:27:00Z · **Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound trading-strategy research/backtesting on real-market, cross-venue data (OKX + Binance UM perps C1–C21; MEXC USDT-perp C22 complete; Bitget USDT-perp C23 ACTIVE & RUNNING).
**Single durable handoff:** this file. `INITIAL_TASK_MESSAGE.md` is a pointer to this file; do not maintain a second source of truth.
**Priority by repo scope (non-negotiable):** C1–C20 are CLOSED & CERTIFIED `NO_GO` (do not relitigate). **C21-T1 is COMPLETE** — gate `C21 ACCEPTANCE: PASS`, consolidated verdict `NO_GO` (2026-11-18T06:15:08Z). **C22-T1 is COMPLETE** — gate `C22 ACCEPTANCE: PASS`, consolidated verdict `NO_GO` (MEXC out-of-sample replication; 4/4 fold checkpoints present, 7/7 battery artifacts present). **C23-T1 is the ACTIVE BINDING CAMPAIGN** — Bitget USDT-M out-of-sample replication of the frozen spec-literal edge, PRE-REGISTERED (`c23_prereg_20261118T202301Z`), acquisition/cache/universe ready, heavy 4-fold battery RUNNING (durable, resumable). **Fold 2023 checkpoint is COMPLETE; fold 2024 is IN PROGRESS; 2025/2026YTD not started. Gate `C23 ACCEPTANCE: PENDING` (0/7 battery artifacts).** It must run to completion and pass `C23 ACCEPTANCE: PASS`. Hyperliquid-native acquisition stays CLOSED (`FULL_283D_BLOCKED_BY_API_RETENTION`). Do NOT run a same-data C22+ rerun on OKX/Binance; do not relabel MEXC/Bitget data as Hyperliquid; do not reduce draw counts. After C23 PASS, report per-fold/pooled/power curve and STOP — no further campaign is authorized beyond C23.

**Verified live/repo state (2026-11-18T23:23:50Z):**
- `bash scripts/status_c23.sh` (read-only, one-shot; ONLY status command you need) → `RUNNER: ALIVE`, `2023: DONE`, `2024/2025/2026YTD: pending`, battery `0/7`, `C23 ACCEPTANCE: PENDING`.
- `PYTHONPATH=. .venv/bin/python scripts/verify_c23_focus_campaign.py` → `C23 ACCEPTANCE: PENDING` (prereqs GREEN: prereg json+md present, config matches frozen spec-literal, acquisition viable, Bitget cache 34 symbols present / 33 selected, universe derived; **0/7 battery artifacts**).
- `PYTHONPATH=. .venv/bin/python scripts/verify_c22_focus_campaign.py` → `C22 ACCEPTANCE: PASS` (mexc consolidated `NO_GO`). C22 runner NOT alive — campaign complete.
- `PYTHONPATH=. .venv/bin/python -m pytest tests/test_c23_campaign_20261118.py -q` → **12 passed** (Bitget normalization/pagination, prereg schema/frozen config, gate PENDING→PASS and FAIL-on-drift/mismatch/Hyperliquid-mislabel).
- `.venv` bootstrapped at repo root (Python 3.12.3 + numpy, pandas, requests, pyarrow, pytest 9.2.0). Run with `PYTHONPATH=. .venv/bin/python ...`.
- **C23 RUNNER IS ACTIVE (durable):** parent PID **25897** (started 2026-11-18T22:21:55Z) + 4 rotating Pool workers running `scripts/run_c23_bitget_campaign.py --jobs 4 --resume`, launched via `bash scripts/run_c23_detached_durable.sh` → log `research_state/c23_run_20261118T222155Z.log`.
- **Fold evidence (recorded):** fold **2023 COMPLETE** — census events=348 signal_pass=108 trades=24 matched=24 unexplained=41; fast-path validated pnl=**+28,706.32**, diff=0.00e+00; trades=24 pnl=+28,706.32 eps=9 perm_p=0.0229, 2,000 placebo runs; **0/9 BH strata survivors**; checkpoint `research_state/c23_ckpt_bitget_2023_20261118T202301Z.json`. Fold **2024 IN PROGRESS** — census 36 trades matched=36, pnl=**-30,939.60**, fast-path validated 3x diff=0.00e+00, per-fold permutation/placebo phase running. Folds 2025, 2026YTD NOT STARTED.
- Observed pace: fold 2023 took ~46 min (22:21:55 → 23:07:45). Expect folds 2024 → ~23:54Z, 2025 → ~00:40Z, 2026YTD → ~01:26Z, then battery artifacts written (they are emitted ONLY after all 4 folds finish).
- **Mid-campaign rule:** fold 2023 is positive but has 0/9 BH strata survivors — a single fold is NOT a result. No token may be claimed before `c23_decision_verdict_CONSOLIDATED_20261118T202301Z.json` exists. 7/7 artifacts + gate PASS is the only completion signal.
- Local `main` HEAD `d556aee` (controller checkpoints the worktree; do not rewrite history; do not commit unless explicitly asked).

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-18T23:27:00Z — C23-T1 ACTIVE, FOLD 2023 DONE, 2024 IN PROGRESS; MONITOR/RESUME → COMPLETE → VERIFY GATE → STOP)

**Single durable handoff / source of truth:** this file. `INITIAL_TASK_MESSAGE.md` is a pointer only.

**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication on real-market data.

**Current position (verified live 2026-11-18T23:23:50Z):** C1–C20 CLOSED `NO_GO`; C21 PASS (`NO_GO`); C22 PASS (`NO_GO`); **C23-T1 ACTIVE & RUNNING** — Bitget USDT-M out-of-sample replication. Prereq GREEN: `c23_prereg_20261118T202301Z`, probe `ACQUISITION_VIABLE_BITGET_MULTIYEAR`, cache 34 symbols (33 selected), universe 33 selected. Runner parent PID **25897** alive with 4 workers, log `research_state/c23_run_20261118T222155Z.log`. Fold 2023 checkpoint DONE (24 trades, +28,706.32, 9 episodes, perm_p=0.0229, 0/9 BH survivors); fold 2024 in progress (36 trades, -30,939.60 in census). Battery 0/7 — gate `C23 ACCEPTANCE: PENDING`.

**Immediate next action (one command, read-only, non-blocking):**
`bash scripts/status_c23.sh`
Read the `RUNNER:` / fold ckpt / `battery:` / gate lines and act:
- Runner ALIVE → **do not relaunch, do not kill, do not foreground-wait**. Finish the turn, schedule a wakeup ~40–45 min out (`schedule_wakeup`), and re-run the same one-shot command. Folds complete one at a time; ~46 min/fold observed.
- Runner NOT ALIVE and gate PENDING → `bash scripts/run_c23_detached_durable.sh` (resume skips completed folds; if all 4 checkpoints exist, resume only rebuilds artifacts, which is cheap).
- Gate PASS → proceed to the report (step 7 below), then STOP.
Log silence with 4 workers at high CPU is EXPECTED, not a hang (fold 2024's log went quiet for >15 min during the permutation phase). No long foreground `sleep`; no `timeout` near the 900 s idle limit.

**Repository:** `CRASH-REBOUND-STRATEGY` (crash-rebound edge adjudication on real-market data; OKX + Binance UM done `NO_GO`; MEXC replication complete `NO_GO`; Bitget running).
**Environment:** durable `.venv` at repo root (Python 3.12.3 + deps); run with `PYTHONPATH=. .venv/bin/python ...`. If missing, `bash scripts/bootstrap_env.sh` first. Network egress available (Bitget/OKX/MEXC/Coinbase/Kraken reachable; Binance/Bybit geo-blocked).

**Runtime expectation:** 3 folds remain (2024 mid-flight, 2025, 2026YTD) at ~46 min/fold → full C23 completion roughly **2026-11-19T01:20–01:45Z** from this handoff, plus a few minutes for artifact synthesis. If a fold checkpoint is absent ~40 min past its projected time AND the runner is dead, resume immediately; if the runner is alive, wait — Pool phase silence is normal.

**Verified live (2026-11-18T23:23:50Z):** C1–C20 CLOSED `NO_GO`; **C21-T1 COMPLETE** (`C21 ACCEPTANCE: PASS`, consolidated `NO_GO`). **C22-T1 COMPLETE** (`C22 ACCEPTANCE: PASS`, consolidated `NO_GO`, mexc=NO_GO). **C23-T1 ACTIVE & RUNNING** (Bitget) — prereg `c23_prereg_20261118T202301Z`, probe `c23_venue_acquisition_probe_20261118T202301Z` (`ACQUISITION_VIABLE_BITGET_MULTIYEAR`), cache 34 symbols (33 complete), universe `universe_bitget_multiyear_verified.json` (33 selected, real_market_data=true). **Fold 2023 ckpt present**, fold 2024 in progress. **Battery artifacts: 0/7 present** — gate `C23 ACCEPTANCE: PENDING`.

**Immediate next action:** `bash scripts/status_c23.sh`, then monitor/resume until `C23 ACCEPTANCE: PASS`. Expected completion ~01:30Z.

**Key tokens:** `C22 ACCEPTANCE: PASS` (consolidated `NO_GO`), `C23 ACCEPTANCE: PENDING` → must reach `PASS`, `c23_prereg_20261118T202301Z`, `run_c23_detached_durable.sh`, `status_c23.sh`, `verify_c23_focus_campaign.py`, `tests/test_c23_campaign_20261118.py`.

**Priority by repo scope (non-negotiable):** C1–C20 CLOSED & CERTIFIED `NO_GO`. C21-T1 COMPLETE (`PASS`, consolidated `NO_GO`). C22-T1 COMPLETE (`PASS`, consolidated `NO_GO`). **C23-T1 is the ACTIVE BINDING CAMPAIGN** — must run to completion and pass `C23 ACCEPTANCE: PASS`; a positive fold 2023 alone is not a result. Hyperliquid-native acquisition stays CLOSED. Do NOT reduce draw counts; do NOT relabel Bitget data as Hyperliquid.

Full binding context, fold evidence, no-avoidance rules, guardrails, and execution order: `HANDOFF.md`.

---

## BINDING CAMPAIGN — C22-T1 (MEXC OUT-OF-SAMPLE REPLICATION) — COMPLETE

**Status:** COMPLETE — gate `C22 ACCEPTANCE: PASS`, consolidated verdict `NO_GO`. C22 runner NOT alive. Do not relaunch.
**Prereg:** `research_state/c22_prereg_20261118T100126Z.{json,md}` (`PRE_REGISTERED_BEFORE_COMPUTE`).
**Fold results (recorded):** 2023: 25 trades, PnL +30,599.03, 9 episodes, 12 crash days, perm p=0.01835, placebo p_ge=0.006, CI95=[-4,715.22, +67,959.60], 0/9 BH strata survivors. 2024: 40 trades, PnL -27,326.63, perm p=0.3085. 2025/2026YTD completed per final artifacts.
**C22 REQUIRED ARTIFACTS (TS = `20261118T100126Z`)** — all 7 battery artifacts + prereg present:
`c22_prereg_{TS}.{json,md}`; `c22_mexc_fold_campaign_{TS}.json`; `c22_mexc_fold_episode_edge_{TS}.json`; `c22_mexc_fold_placebo_{TS}.json`; `c22_mexc_fold_census_{TS}.json`; `c22_decision_verdict_mexc_stability_{TS}.json`; `c22_pooled_stability_synthesis_{TS}.json`; `c22_decision_verdict_CONSOLIDATED_{TS}.json`.

---

## NEXT FOCUS CAMPAIGN — C23-T1 (BITGET USDT-M OUT-OF-SAMPLE REPLICATION) — ACTIVE & RUNNING, BINDING

**Status:** ACTIVE & RUNNING (launched 2026-11-18T22:21:55Z; as of 2026-11-18T23:23Z fold 2023 DONE, fold 2024 IN PROGRESS, 2025/2026YTD pending). **Authorization:** the operator instruction for this handoff explicitly directs building the next focus campaign when explicit directions are absent; C23 was built and is now the binding heavy campaign. Do not wait for another approval. **Sequencing constraint:** C22 is PASS and no `run_c22_mexc_campaign.py` process is alive, so C23 may run (no CPU contention, no same-data churn).

**Why C23:** C1–C22 have tested OKX, Binance UM, and MEXC. Before declaring the crash-rebound edge dead (or confirming it), run the unchanged spec-literal edge on one more independent never-used USDT-perp venue (Bitget USDT-M). New data + a frozen spec, not a parameter search. C23 is the final new-venue replication gate: if it is `NO_GO`/`UNDERPOWERED`, the C1–C22 `NO_GO` stands with multi-venue evidence; if it is `STABLE_POSITIVE_SUBSET`, it is the required out-of-sample confirmation and must be reported with full per-fold evidence.

**Chosen venue (probe-verified 2026-11-18T20:23Z):** **Bitget USDT-M perpetual futures**.
- Public market-data endpoint confirmed: `https://api.bitget.com/api/v2/mix/market/history-candles?symbol=BTCUSDT&productType=usdt-futures&granularity=1H&startTime=1672531200000&endTime=1672617600000&limit=200` → HTTP 200, real 1H OHLCV for 2023-01-01.
- Contract list confirmed: `https://api.bitget.com/api/v2/mix/market/contracts?productType=usdt-futures` → 890 USDT-M contracts (BTCUSDT, ETHUSDT, ...).
- **Universe:** 33 selected symbols, real_market_data=true, full-window 1H coverage 2023-01-01..2026-09-28 (MINA excluded — incomplete coverage, never fabricated). Cache: `research_state/cache/bitget_1h_multiyear_20230101_20260928/` with provenance.json + per-symbol sha256.

**Frozen config (same spec-literal, no switching):** `rsi_period=21`, `rsi_threshold=20`, `target_pct=9`, `rebound_short_target_pct=9`, `rebound_short_time_exit_bars=48`, `enable_rebound_short=true`, `enable_eth_hedge=true`, `min_daily_volume_usd=5,000,000`, `gross_cap_pct=120`, `entry_spec_literal_next_open=true`. Seed fixed `20261123` in the C23 prereg (written before compute).

**Folds / strata / inference (same as C22):** folds 2023, 2024, 2025, 2026YTD (2026-01-01..2026-09-28); strata `crash_severity` (RSI 0–10/10–15/15–20), `btc_trend` (down/flat/up 7d), `funding_regime` (neg/neu/pos from Bitget funding history; neutral when absent); per fold 20,000-draw episode-block bootstrap CI95, 20,000-draw permutation p, 2,000-subset portfolio placebo, stratified bootstrap with **Benjamini–Hochberg** (α=0.05); pooled venue-blocked bootstrap + cross-venue sign concordance vs OKX/Binance/MEXC priors; power floor ≥10 trades / ≥5 episodes / ≥5 distinct crash days else `UNDERPOWERED` + power curve.

**C23 execution order (heavy work; no shortcuts):**
1. **Probe:** done — `scripts/probe_c23_venue_acquisition.py` → `research_state/c23_venue_acquisition_probe_20261118T202301Z.json` (`ACQUISITION_VIABLE_BITGET_MULTIYEAR`).
2. **Acquire:** done — `scripts/fetch_bitget_perp_archive.py`; cache `research_state/cache/bitget_1h_multiyear_20230101_20260928/` with provenance.json, per-symbol sha256, coverage report. No synthetic gap-fill.
3. **Prereg:** done — `scripts/build_c23_prereg.py` → `research_state/c23_prereg_20261118T202301Z.{json,md}` (`PRE_REGISTERED_BEFORE_COMPUTE`), written before compute.
4. **Runner:** `scripts/run_c23_bitget_campaign.py` (adapted C22 runner: same fold campaign/census/episode/placebo/strata, same 20k/20k/2k draw floors, `is_hyperliquid_venue_data=false`), `scripts/run_c23_detached_durable.sh` (timestamped log, `--jobs 4 --resume`, `pgrep` duplicate guard), `scripts/status_c23.sh` (read-only one-shot status). Launched and ACTIVE.
5. **Run:** IN PROGRESS — fold 2023 DONE (`c23_ckpt_bitget_2023_20261118T202301Z.json`: 24 trades, +28,706.32, 9 episodes, perm_p=0.0229, 0/9 BH strata survivors); fold 2024 running its 20k permutation/2k placebo phase (census 36 trades, -30,939.60, fast-path diff 0.00e+00); 2025 and 2026YTD pending. Observed pace ~46 min/fold → expected full completion **2026-11-19T01:20–01:45Z**. Monitor with `bash scripts/status_c23.sh`; resume until complete. Do not reduce draw counts; do not foreground-block for hours; do not start a duplicate.
6. **Gate:** `scripts/verify_c23_focus_campaign.py` — must print `C23 ACCEPTANCE: PASS` (valid token ∈ {`STABLE_POSITIVE_SUBSET`, `NO_GO`, `UNDERPOWERED`}; bitget verdict = consolidated; `is_hyperliquid_venue_data=false` everywhere). Regression coverage: `tests/test_c23_campaign_20261118.py` (12 tests, PASS today).
7. **Report:** per-fold, per-venue, and pooled numbers plus the power curve. Never a bare token. Never tune the spec to chase a GO. A positive single fold (2023: +28,706.32 with 0/9 BH survivors) is NOT a result — only the consolidated artifact + gate count.

**C23 REQUIRED ARTIFACTS (TS = `20261118T202301Z`):**
`c23_prereg_{TS}.{json,md}`; `c23_bitget_fold_campaign_{TS}.json`; `c23_bitget_fold_episode_edge_{TS}.json`; `c23_bitget_fold_placebo_{TS}.json`; `c23_bitget_fold_census_{TS}.json`; `c23_decision_verdict_bitget_stability_{TS}.json`; `c23_pooled_stability_synthesis_{TS}.json`; `c23_decision_verdict_CONSOLIDATED_{TS}.json`.

**C23 no-avoidance rule (binding):** C23 is mandatory to completion. Do not stop at "C22 done", do not substitute same-data analysis, do not reduce draws, do not relabel Bitget data as Hyperliquid, and do not treat `C23 ACCEPTANCE: PENDING` as completion. If the C23 runner dies, resume immediately via `run_c23_detached_durable.sh`. The session is not done until `C23 ACCEPTANCE: PASS` and the per-fold/pooled/power-curve report is delivered. After C23 PASS, stop — no further campaign authorized beyond C23.

---

## BOTTLENECKS REMOVED THIS SESSION (2026-11-18T23:27:00Z)

1. **Status-check bottleneck removed:** added `scripts/status_c23.sh` — one read-only command printing UTC time, runner liveness (parent + workers), per-fold checkpoint state, newest log tail, battery count, and the gate token. Replaces four hand-assembled shell invocations that invited stale-PID mistakes and duplicate relaunches.
2. **"Is it hung?" bottleneck removed with evidence:** fold 2023 completed in ~46 min (not ~81 min); fold 2024's log went quiet >15 min while its 20k permutation/2k placebo phase ran. The handoff now records the observed pace and the expected completion window (2026-11-19T01:20–01:45Z) so a quiet log is not misdiagnosed as a crash.
3. **Missing C23 regression coverage removed:** added `tests/test_c23_campaign_20261118.py` (12 tests: Bitget normalization/pagination, prereg schema/frozen config, gate PENDING→PASS and FAIL on config drift, blocked acquisition, verdict mismatch, Hyperliquid mislabel). Passing today, so gate stability is verifiable without touching live artifacts.
4. **Premature-conclusion bottleneck removed:** fold 2023 is positive (+28,706.32) but has 0/9 BH strata survivors and is one of four folds; HANDOFF states explicitly that only the consolidated artifact + gate token count, preventing a future session from reporting a GO from a single fold.
5. **Stale-state bottleneck removed:** refreshed all verified live facts (fold 2023 checkpoint, fold 2024 in-flight census, HEAD `d556aee`, 0/7 artifacts), replacing the previous "2023 in progress, 0 checkpoints, HEAD 2df7f76" snapshot.
6. **Resume-cost bottleneck documented:** if the runner dies after all 4 fold checkpoints exist, `run_c23_detached_durable.sh` rebuilds only the 7 artifacts from cached checkpoints — cheap, not a 4-fold re-run. This removes hesitation about resuming late in the campaign.
7. **Duplicate-launch bottleneck kept removed:** `scripts/run_c23_detached_durable.sh` remains the only launch path (`pgrep` guard, `--jobs 4 --resume`, timestamped log). Do not start a second Bitget battery; do not kill the live runner.

---

## BOTTLENECKS REMOVED IN PRIOR SESSIONS (selected)

- **2026-11-18T21:24Z:** C22-T1 reached `C22 ACCEPTANCE: PASS` (consolidated `NO_GO`); 4/4 fold checkpoints present; C22 runner not alive; C23 prerequisites all GREEN; C23 runner launched (parent PID 20442 earlier run; current live runner PID 25897).
- **2026-11-18T19:20:00Z:** C22 runner confirmed active (parent PID 21734); fold 2023 complete, fold 2024 in progress, gate `PENDING`.
- **2026-11-18T15:16:59Z:** state-refresh bottleneck cleared; stale worker-PID bottleneck removed; stale progress claims corrected; idle-timeout bottleneck removed; next-campaign avoidance bottleneck removed (C23 binding added); duplicate-launch bottleneck kept removed.
- **2026-11-18T12:03:58Z:** created `scripts/run_c22_mexc_campaign.py`; completed MEXC multiyear acquisition (34 symbols) and derived `universe_mexc_multiyear_verified.json`.
- **2026-11-18T10:10:23Z:** removed stale "acquisition CLOSED/no network" + do-nothing paralysis with probe evidence `ACQUISITION_VIABLE_MEXC_MULTIYEAR`; built MEXC fetch/prereg/gate/tests.

**Remaining/open:** C23 heavy battery must complete (~1.5–2 h remaining: folds 2024/2025/2026YTD then artifact synthesis) and pass `C23 ACCEPTANCE: PASS`; then report per-fold/pooled/power curve and STOP. If a runner dies before PASS, resume immediately via `run_c23_detached_durable.sh`. Do not invent same-data follow-on work on exhausted data. After C23 PASS there is no authorized campaign — the correct terminal state is the evidence report, not a new probe.

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
- **Status first:** run `bash scripts/status_c23.sh` before any C23 action; do not hand-assemble `ps`/`ls`/gate chains and do not treat a stale PID from this document as ground truth.
- **Do NOT relaunch `scripts/finish_c20_detached_durable.sh` (C20 PASS).** No duplicate C22/C23 battery while runner active; no foreground campaign in an agent turn; no short `timeout`; no long foreground `sleep` that will hit the 900s idle timeout.
- No same-data C23+ rerun of C21/C22 without new prereg + new data + explicit authorization. C22 is legitimate only because MEXC is new data; C23 is legitimate only because Bitget is new data and its prereg is written before compute.
- Do not edit completed campaign artifacts or `scripts/run_c20_cross_venue_campaign.py`.
- No silent change to canonical baseline. C1–C22 `NO_GO` stands unless C23 produces a pre-registered contradiction with full evidence.
- Do not commit unless explicitly asked (controller checkpoints worktree; do not rewrite history).
- Preserve literal gate tokens: `INITIAL TASK MESSAGE`, `session_gate.py`, `21/21 checks passed`, `2026-11-13T23:38:47Z`, `probe_hyperliquid_blocker.py`, `FULL_283D_BLOCKED_BY_API_RETENTION`, `verify_campaign_evidence.py`, `C19-T1`, `verify_c19_focus_campaign.py`, `C14`, `verify_c14_focus_campaign.py`, `20261116T001200Z`, `C6-T1`, `campaign_results_real_okx_multiyear`, `C13`, `verify_c13_focus_campaign.py`, `C20`, `verify_c20_focus_campaign.py`, `C21-T1`, `verify_c21_focus_campaign.py`, `C22-T1`, `verify_c22_focus_campaign.py`, `fetch_mexc_perp_archive.py`, `probe_c22_venue_acquisition.py`, `c22_prereg_20261118T100126Z`, `ACQUISITION_VIABLE_MEXC_MULTIYEAR`, `C23-T1`, `verify_c23_focus_campaign.py`, `fetch_bitget_perp_archive.py`, `probe_c23_venue_acquisition.py`, `status_c23.sh`, `tests/test_c23_campaign_20261118.py`.

---

## KEY FILES

- Handover/state: `HANDOFF.md` (single durable handoff), `README.md`, `research_state/strategy_spec.md`.
- **C22 (COMPLETE, `NO_GO`, PASS):** `research_state/c22_prereg_20261118T100126Z.{json,md}`, `research_state/c22_venue_acquisition_probe_20261118T100126Z.json`, `scripts/probe_c22_venue_acquisition.py`, `scripts/fetch_mexc_perp_archive.py`, `scripts/build_c22_prereg.py`, `scripts/verify_c22_focus_campaign.py`, `tests/test_c22_campaign_20261118.py`, `scripts/run_c22_mexc_campaign.py`, `scripts/run_c22_detached_durable.sh`. Cache: `research_state/cache/mexc_1h_multiyear_20230101_20260928/` (34 symbols, 203 MB). Universe: `research_state/universe_mexc_multiyear_verified.json`. Checkpoints: `research_state/c22_ckpt_mexc_<fold>_20261118T100126Z.json`. Artifacts: `research_state/c22_*_20261118T100126Z.json`.
- **C23 (ACTIVE & RUNNING, binding):** `research_state/c23_prereg_20261118T202301Z.{json,md}`, `research_state/c23_venue_acquisition_probe_20261118T202301Z.json`, `scripts/probe_c23_venue_acquisition.py`, `scripts/fetch_bitget_perp_archive.py`, `scripts/build_c23_prereg.py`, `scripts/verify_c23_focus_campaign.py`, `scripts/run_c23_bitget_campaign.py`, `scripts/run_c23_detached_durable.sh`, `scripts/status_c23.sh` (read-only status), `tests/test_c23_campaign_20261118.py` (12 tests). Cache: `research_state/cache/bitget_1h_multiyear_20230101_20260928/` (34 symbols cached, 33 selected). Universe: `research_state/universe_bitget_multiyear_verified.json`. Live log: `research_state/c23_run_20261118T222155Z.log` (parent PID 25897 + rotating workers). Checkpoints: `research_state/c23_ckpt_bitget_<fold>_20261118T202301Z.json` (2023 present; 2024 next). Artifacts (written after all 4 folds): `research_state/c23_*_20261118T202301Z.json`.
- C21 (complete, `NO_GO`, PASS): `research_state/c21_prereg_20261117T064408Z.{json,md}`, `scripts/run_c21_cross_venue_campaign.py`, `scripts/verify_c21_focus_campaign.py`, `scripts/run_c21_detached_durable.sh`, `research_state/c21_*_20261117T064408Z*`.
- C20: `research_state/c20_prereg_20261116T063500Z.{json,md}`, `research_state/c20_pooled_cross_venue_synthesis_20261116T063500Z.json`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json`, `scripts/run_c20_cross_venue_campaign.py`, `scripts/verify_c20_focus_campaign.py`.
- Acquisition: `scripts/acquire_exchange_archive.py`, `scripts/fetch_hyperliquid_candles.py`, `scripts/derive_verified_universe.py`.
- Gates: `scripts/session_gate.py`, `scripts/verify_campaign_evidence.py`, `scripts/probe_hyperliquid_blocker.py`, `scripts/verify_c13_focus_campaign.py`, `scripts/verify_c14_focus_campaign.py`, `scripts/verify_c19_focus_campaign.py`, `scripts/verify_c20_focus_campaign.py`, `scripts/verify_c21_focus_campaign.py`, `scripts/verify_c22_focus_campaign.py`, `scripts/verify_c23_focus_campaign.py`, `scripts/verify_next_focus_campaign.py` (C6).
- Env: `scripts/bootstrap_env.sh`.
- Code: `src/strategy/crash_rebound.py`, `src/strategy/config.py`, `src/backtest/engine.py`, `src/data/loader.py`.
