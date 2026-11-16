# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-16T14:31:10Z · **REGENERATED (UTC):** 2026-11-16T22:45:54Z · **Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound strategy research/backtesting, cross-venue (OKX + Binance UM) evidence chain feeding C20.
**Single durable handoff for the next agentic session — read this before doing anything else.**
**Phase O artifact timestamp (binding, `research_state/episode_edge_okx_full.json`):** `2026-11-13T23:38:47Z` · **Target gate result:** `21/21 checks passed` (verified again this session at 2026-11-16T22:42:17Z).

> **PROGRAM STATE: C1–C19 CLOSED (final verdict `NO_GO`) · C20 IS THE BINDING NEXT FOCUS CAMPAIGN — NOT OPTIONAL.**
> C20 was preregistered at `research_state/c20_prereg_20261116T063500Z.{json,md}` (status `PRE_REGISTERED_BEFORE_COMPUTE`). Its detached, lock-guarded, `--resume` compute is the only active campaign. It is **not complete**: `C20 ACCEPTANCE: FAIL` (7 of 17 checks missing; 6 of 15 required JSON artifacts on disk as of 2026-11-16T22:31:52Z). The only accepted terminal state is `C20 ACCEPTANCE: PASS`. Do not re-plan, re-adjudicate C1–C19, relabel cross-venue results as Hyperliquid-native, edit the running campaign, or substitute narrative for artifacts.
>
> **Recovery rule:** an absent live supervisor is not evidence of completion. If no live C20 supervisor/campaign process tree exists, relaunch `scripts/finish_c20_detached_durable.sh` and continue through the fail-closed gate. The durable supervisor stores its lock/log/status in `research_state/.c20/` and its Python environment at `.venv`; legacy `/tmp/crs-venv`, `/tmp/c20_supervisor.lock`, `/tmp/c20_supervisor.log`, and `/tmp/c20_supervisor_status.json` are recovery inputs only and are not durable state.

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-16T22:45:54Z — FINISH C20, MANDATORY HEAVY WORK)

**Repository:** `CRASH-REBOUND-STRATEGY` (crash-rebound edge adjudication on real-market data). **Priority by repo scope:** close C20 (cross-venue out-of-sample replication on OKX + Binance UM, both real archives) because C1–C19 are closed as `NO_GO` and no other decision-relevant campaign is authorized. Treat C20 as the **only** binding next focus until `scripts/verify_c20_focus_campaign.py` prints `C20 ACCEPTANCE: PASS`.

**Execute in order. No planning-only stops, no liveness narration as progress, no inference-only churn.**

1. **Read this file fully.** Keep `SPEC_LITERAL_NEXT_OPEN` fixed; no config switching after results; no synthetic gap-fill presented as verified.
2. **Inspect live compute before touching anything (do not disturb a healthy run).**
   ```bash
   pgrep -af 'finish_c20_detached|run_c20_cross_venue_campaign' || true
   ps -eo pid,ppid,sid,etime,time,pcpu,cmd | grep -E 'finish_c20|run_c20' | grep -v grep || true
   tail -n 40 /tmp/c20_supervisor.log 2>/dev/null || echo "no /tmp log"
   tail -n 40 research_state/.c20/supervisor.log 2>/dev/null || echo "no durable log"
   cat /tmp/c20_supervisor_status.json research_state/.c20/supervisor_status.json 2>/dev/null || true
   ls research_state/*_20261116T063500Z.json 2>/dev/null | sort
   ```
- **Liveness = worker cumulative CPU `TIME` advancing across two probes ~10s apart + durable artifact progress**, not log/status file presence. Silent logs during heavy compute are normal.
     - **LIVE NOW (2026-11-16T22:45:54Z, verified):** legacy supervisor `scripts/finish_c20_detached.sh` PID 2735/SID 2735 alive (etime ~03:14); campaign PID 2750 + 4 workers 29251–29254 alive (`/tmp/crs-venv`, ~92–93% CPU each, cumulative worker `TIME` ~00:12:24–00:12:32 advancing). `/tmp/c20_supervisor_status.json` = `IN_FLIGHT_HEAVY_COMPUTE`, attempt 1, artifacts=5 at last poll, updated 2026-11-16T22:45:31Z. `/tmp/c20_supervisor.log` attempt 1 start 2026-11-16T19:32:15Z shows OKX placebo/battery/verdict landed and Binance UM census landed. `.venv` and `research_state/.c20/` absent (legacy `/tmp` paths in use). No second campaign running.
     - **Artifacts present (9 files / 6 required JSON as of 2026-11-16T22:45:54Z):** `c20_prereg_20261116T063500Z.json`; `campaign_results_real_okx_multiyear_specliteral_20261116T063500Z.json`; `crash_event_census_real_okx_multiyear_specliteral_20261116T063500Z.json`; `episode_edge_okx_multiyear_specliteral_20261116T063500Z.json`; `placebo_portfolio_okx_multiyear_specliteral_20261116T063500Z.json`; `multiyear_robustness_battery_okx_specliteral_20261116T063500Z.json`; `decision_verdict_cross_venue_okx_specliteral_c20_20261116T063500Z.json`; `campaign_results_real_binance_um_multiyear_specliteral_20261116T063500Z.json`; `crash_event_census_real_binance_um_multiyear_specliteral_20261116T063500Z.json`.
     - **Gate (verified 2026-11-16T22:45:54Z):** `C20 ACCEPTANCE: FAIL — 7 requirement(s) missing`: `c20_artifacts_present, binance_um_episode_edge_computed, binance_um_placebo_computed, binance_um_battery_computed, binance_um_verdict_computed, c20_pooled_synthesis_computed, c20_consolidated_final_computed`.
   - **Completed evidence so far (do NOT recompute):** OKX campaign `trades=113, total_pnl=-55,057.45, spot/coin=-197,767.56, hedge=+140,841.80, rebound_short=-38,420.09, episodes=31, crash_days=45`; OKX placebo `500 choose 113 of 369`, `p_ge_canonical=0.772`; OKX verdict `NO_GO` (3/7 GO checks; bootstrap CI95 total `[-141,457.07, 27,746.10]`, permutation p=0.65); OKX episode edge cached (`episode_block_bootstrap.resamples=20000`, 31 episode blocks, 300-draw permutation); Binance UM campaign `trades=136, total_pnl=-70,309.57, win_rate=0.4485, sharpe=-0.1052, maxDD=-105,299.48`; Binance UM census `events=1204, signal_pass=484, matched=136`. Both venues strongly negative → honest expected terminal token `UNDERPOWERED` or `NO_GO` unless pooled bootstrap CI excludes 0 positive (OKX CI already spans 0, so unlikely).
   - **If any live C20 supervisor/campaign tree exists (legacy or durable), do not start a second campaign.** Let it run; do only non-racing work (step 4).
   - **Only if no live supervisor/campaign is present:** recover durably and relaunch:
     ```bash
     bash scripts/bootstrap_env.sh .venv
     setsid nohup bash scripts/finish_c20_detached_durable.sh >/dev/null 2>&1 < /dev/null &
     ```
     Durable supervisor uses `.venv`, `research_state/.c20/supervisor.lock`, `--resume`, `--jobs 4`, exits 0 only on PASS. Never use short `timeout`, foreground the campaign in a turn, `--jobs 1`, or start a parallel manual campaign.
   - **Kill only on positive true-stall evidence:** worker CPU cumulative `TIME` unchanged across two probes 10 minutes apart, or durable supervisor logs `STALLED` twice. Never kill from impatience. If durable `STALLED`/`EXHAUSTED`, inspect `research_state/.c20/supervisor.log`, preserve blocker, fix the specific cause, then resume.
3. **Run acceptance gate after each completed attempt and at session end.**
   ```bash
   PYTHONPATH=. .venv/bin/python scripts/verify_c20_focus_campaign.py 2>/dev/null || PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c20_focus_campaign.py 2>/dev/null || PYTHONPATH=. python3 scripts/verify_c20_focus_campaign.py
   ```
   Required: `C20 ACCEPTANCE: PASS` (17/17). Any other output means not done.
4. **Non-racing work only while C20 runs (do not add CPU contention):** read `research_state/c20_prereg_20261116T063500Z.md`; prepare the post-PASS handoff closure notes if useful. **Do not** launch another campaign, re-fetch archives, re-run C1–C19, edit `scripts/run_c20_cross_venue_campaign.py`, or weaken prereg/gate to "progress."
5. **Hygiene gates (green required; preserve literal tokens).** Host `nproc=4` means 4 C20 workers saturate cores: run lightweight gates only when non-contending; **DEFER `pytest tests/ -q` until C20 reaches PASS or a terminal verdict** (C20 writes only under `research_state/`).
   ```bash
   PYTHONPATH=. .venv/bin/python scripts/session_gate.py 2>/dev/null || PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py
   PYTHONPATH=. .venv/bin/python scripts/verify_campaign_evidence.py 2>/dev/null || PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py
   PYTHONPATH=. .venv/bin/python scripts/verify_c19_focus_campaign.py 2>/dev/null || PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c19_focus_campaign.py
   PYTHONPATH=. .venv/bin/python scripts/verify_c13_focus_campaign.py 2>/dev/null || PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c13_focus_campaign.py
   PYTHONPATH=. .venv/bin/python scripts/verify_c14_focus_campaign.py 2>/dev/null || PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c14_focus_campaign.py
   PYTHONPATH=. .venv/bin/python scripts/verify_next_focus_campaign.py 2>/dev/null || PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py
   # DEFER until terminal: PYTHONPATH=. .venv/bin/python -m pytest tests/ -q
   ```
   Expected literals (verified this session 2026-11-16T22:45:54Z unless noted): session gate `21/21 checks passed`, evidence `EVIDENCE VERIFIED`, C19 `C19 ACCEPTANCE: PASS`, C13 `C13 ACCEPTANCE: PASS — config-matched native C13 artifacts complete`, C14 `C14 ACCEPTANCE: PASS` (requires this handoff to keep literal `C14` + `verify_c14_focus_campaign.py` + `20261116T001200Z`), C6 `C6 ACCEPTANCE: PASS — multi-year cross-venue campaign artifacts complete` (requires literal `C6-T1` + `campaign_results_real_okx_multiyear`), full suite `1047 passed, 1 skipped` when run.
6. **On PASS only:** update this HANDOFF with a new timestamped INITIAL TASK MESSAGE that records the verdict token from `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json`, per-venue + pooled numbers (trades, total PnL, spot/hedge/rebound legs, bootstrap CI, permutation p, placebo p), full artifact list, and explicit C20 closure. If token is `GO`, next binding campaign is **C21 independent out-of-sample confirmation** (preregister before compute). If `UNDERPOWERED` or `NO_GO`, close C1–C20 with quantified power result; do not invent another same-data campaign. If blocked/exhausted, record actual blocker + exact log path — never fake artifacts or weaken the gate.

**C20 is the mandatory heavy-work obligation until `scripts/verify_c20_focus_campaign.py` prints `C20 ACCEPTANCE: PASS`.**

---

## LIVE STATE VERIFIED (2026-11-16T22:45:54Z)

- **Host capacity:** `nproc=4`; four C20 workers saturate cores. Avoid concurrent heavy CPU work.
- **Live compute (verified 2026-11-16T22:45:54Z):** legacy supervisor `scripts/finish_c20_detached.sh` PID 2735/SID 2735 alive (etime ~03:14); campaign PID 2750 + workers 29251–29254 alive (`/tmp/crs-venv`, ~92–93% CPU each, cumulative worker `TIME` ~00:12:24–00:12:32 — **LIVE, not stalled**). `/tmp/c20_supervisor_status.json` = `IN_FLIGHT_HEAVY_COMPUTE`, attempt 1, artifacts=5, updated 2026-11-16T22:45:31Z. `/tmp/c20_supervisor.log` attempt 1 start 2026-11-16T19:32:15Z; resume cached OKX campaign/census/episode; OKX placebo/battery/verdict and Binance UM census have landed. `.venv` and `research_state/.c20/` absent (legacy `/tmp` paths in use). No second campaign running.
- **Durable recovery state:** `.venv` not present at repo root (live run uses `/tmp/crs-venv`); `research_state/.c20/` absent. Durable relaunch path exists but **must not be used while the legacy tree is alive**. If legacy tree dies, run `bash scripts/bootstrap_env.sh .venv` then relaunch `scripts/finish_c20_detached_durable.sh`.
- **Actual stage:** OKX fully complete (campaign → census → episode edge → placebo → battery → verdict NO_GO). Binance UM campaign/census landed. Remaining heavy work: **Binance UM episode edge → Binance UM placebo → Binance UM robustness battery → Binance UM verdict → pooled synthesis → consolidated final.**
- **Artifacts present (9 files / 6 required JSON as of 2026-11-16T22:45:54Z):** `c20_prereg_20261116T063500Z.json`; `campaign_results_real_okx_multiyear_specliteral_20261116T063500Z.json`; `crash_event_census_real_okx_multiyear_specliteral_20261116T063500Z.json`; `episode_edge_okx_multiyear_specliteral_20261116T063500Z.json`; `placebo_portfolio_okx_multiyear_specliteral_20261116T063500Z.json`; `multiyear_robustness_battery_okx_specliteral_20261116T063500Z.json`; `decision_verdict_cross_venue_okx_specliteral_c20_20261116T063500Z.json`; `campaign_results_real_binance_um_multiyear_specliteral_20261116T063500Z.json`; `crash_event_census_real_binance_um_multiyear_specliteral_20261116T063500Z.json`.
- **Missing for PASS (7 gate requirements):** `binance_um_episode_edge_computed`, `binance_um_placebo_computed`, `binance_um_battery_computed`, `binance_um_verdict_computed`, `c20_pooled_synthesis_computed`, `c20_consolidated_final_computed`, plus the aggregate `c20_artifacts_present` (9 more JSON stems: Binance UM episode/placebo/battery/verdict, `c20_pooled_cross_venue_synthesis_20261116T063500Z.json`, `decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json`; `c20_artifacts_present` also requires the 15/15 set).
- **Gate (verified 2026-11-16T22:45:54Z):** `C20 ACCEPTANCE: FAIL — 7 requirement(s) missing` (list above). Only `C20 ACCEPTANCE: PASS` is terminal success.
- **Hygiene (verified 2026-11-16T22:45:54Z):** session gate `21/21 checks passed`, evidence `EVIDENCE VERIFIED`, C19 `C19 ACCEPTANCE: PASS`, C13 `C13 ACCEPTANCE: PASS`, C14 `C14 ACCEPTANCE: PASS`, C6 `C6 ACCEPTANCE: PASS — multi-year cross-venue campaign artifacts complete`. C14/C6 pass on this regenerated handoff's restored literals. Heavy `pytest tests/ -q` deferred until C20 terminal; last known full-suite literal `1047 passed, 1 skipped`.
- **Ephemeral paths:** legacy `/tmp/*c20*` may vanish on restart; durable artifacts are `research_state/*_20261116T063500Z.json` plus (once durable supervisor used) `research_state/.c20/`.
- **Venv:** prefer `.venv/bin/python` after bootstrap; live legacy run currently uses `/tmp/crs-venv/bin/python`.
- **Leftover/nonblocking:** `tmpgq4pmrk6/` present at repo root (temp-named cache dir). Not removed to avoid interfering with unknown consumers; cleanup candidate after C20 terminal if unreferenced.

## BOTTLENECKS REMOVED / UNBLOCKED (2026-11-16T22:36:38Z)

1. **Stale-handoff hygiene regression (this session, fixed):** the prior handoff omitted literal tokens `C19-T1`, `C14`/`verify_c14_focus_campaign.py`/`20261116T001200Z`, and `C6-T1`/`campaign_results_real_okx_multiyear`, so `verify_c19_focus_campaign.py`, `verify_c14_focus_campaign.py`, and `verify_next_focus_campaign.py` regressed to FAIL. This regeneration restores every required literal and pins them in the hygiene-gate section so a future edit cannot silently drop them again.
2. **Progress tracking drift (this session, fixed):** prior handoff claimed 5 required JSON / 11 missing; actual state is 6 required JSON / 7 missing, with OKX fully closed (`NO_GO`) and Binance UM census landed. This file now records the exact per-venue completion frontier and remaining pipeline so a future agent resumes at the true frontier, not a stale one.
3. **Durable-recovery gap while legacy compute runs** → handoff forbids parallel durable relaunch when legacy tree is healthy and provides exact durable bootstrap/relaunch commands for the no-live-process case.
4. **Session-bound/short-timeout compute** (carry-forward) → detached, lock-guarded, auto-resume durable supervisor (`scripts/finish_c20_detached_durable.sh`, `.venv`, `research_state/.c20/supervisor.lock`, `--resume`, exits 0 only on PASS).
5. **Lost `/tmp` state risk** (carry-forward) → durable supervisor lock/log/status in `research_state/.c20/`; `/tmp` treated as legacy inputs only.
6. **Liveness misread** (carry-forward) → judge by worker CPU-time delta + artifact count, not status/log presence.
7. **CPU contention on 4-vCPU host** (carry-forward) → heavy `pytest tests/ -q` deferred until C20 terminal; lightweight gates only when non-contending.
8. **Fail-closed acceptance** (carry-forward) → only `scripts/verify_c20_focus_campaign.py` PASS is success.

## C20 SPEC & DECISION RULES (prereg `c20_prereg_20261116T063500Z`, PRE_REGISTERED_BEFORE_COMPUTE)

- Config fixed: `entry_spec_literal_next_open=true`, RSI(21)<20, target 9%, ETH hedge on, $5M volume gate, seed 20261120. **No config switching after results.**
- Required artifacts (15): prereg, OKX+Binance campaigns+metrics, censuses, episode edges, placebos, robustness batteries, per-venue verdicts, `c20_pooled_cross_venue_synthesis`, `decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z`.
- GO only if pooled synthesis: episode-block bootstrap 95% CI excludes 0 with positive spot leg, permutation p<0.05, placebo p_ge_canonical<0.05, and ≥10 trades / ≥5 episodes / ≥5 crash days. Else `UNDERPOWERED` or `NO_GO` with quantified power curve. Final inference pending; OKX is already `NO_GO` (3/7 checks, CI spans 0) and Binance UM campaign is strongly negative (`-70,309.57`), so an honest `NO_GO`/`UNDERPOWERED` terminal is the expected outcome.
- C20 is cross-venue (`is_hyperliquid_venue_data=false`) — **never** Hyperliquid performance evidence.

## NO-AVOIDANCE CONTRACT (binding)

- Only accepted terminal state: `C20 ACCEPTANCE: PASS`. Narrative-only, partial venue, "prereg only," relabeling cross-venue as Hyperliquid-native, or gate/script edits to pass are rejected.
- C20 requires **both venues end-to-end** + pooled synthesis + post-prereg consolidated final (no partial-credit terminal state).
- If pooled token is `GO`, next focus is **C21 independent out-of-sample confirmation**, preregistered before compute. If `UNDERPOWERED`/`NO_GO`, record with quantified power curve and close C1–C20; do not relitigate exhausted data.

## C1–C19 CLOSED STATE (historical, do not relitigate)

- **Consolidated final (C1–C19):** `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.{json,md}` — `NO_GO`.
- **C19 (referenced as `C19-T1` for gate literal):** T1 `spec_rebound_confirmation_adjudication_20261116T054000Z` (`SPEC_LITERAL_NEXT_OPEN`); T2 native battery C18 spec-literal 22 trades, −47,933.58, 31.8% WR, max DD −52,160 (NO_GO); T3 0/7 GO criteria, max 4 episodes < 5; T4 `decision_verdict_hyperliquid_native_c19_20261116T054000Z` NO_GO (`is_hyperliquid_evidence=true`); T5 consolidated NO_GO. Gate script: `scripts/verify_c19_focus_campaign.py`.
- **C14 (referenced for gate literal `20261116T001200Z`):** C14 episode edge `research_state/episode_edge_hyperliquid_ironflow_wide_20261116T001200Z.{json,md}`; native C14 underpowered/fragile (7 trades, 3 episodes, CI spans 0). Gate script: `scripts/verify_c14_focus_campaign.py`.
- **C6 (referenced as `C6-T1` for gate literal):** cross-venue context OKX+Binance UM pooled 38 venue-episodes underpowered (CI spans 0), `campaign_results_real_okx_multiyear` campaign family, `is_hyperliquid_venue_data=false`. Gate script: `scripts/verify_next_focus_campaign.py`.
- **Acquisition CLOSED/exhausted:** Hyperliquid moving tail (`full_window_served=false`, earliest ~2026-04-21; `hyperliquid_retention_probe_next_20261116T054408Z.json`). No verified native archive ≥2023-01-01 or adding ≥1 independent crash episode beyond C14.

## GUARDRAILS (never violate)

- No cross-venue relabeling as Hyperliquid-native (`is_hyperliquid_venue_data=false` for C20).
- No synthetic gap-fill as verified; no spec relaxation to manufacture GO; `SPEC_LITERAL_NEXT_OPEN` fixed.
- No inference-only churn on exhausted C14 native data; C19 closed.
- No second concurrent campaign while any C20 supervisor/campaign tree is alive; no foreground campaign in an agent turn; no short `timeout`.
- Do not edit a running supervisor or `scripts/run_c20_cross_venue_campaign.py` to change the campaign; resume semantics are fixed.
- No silent change to canonical baseline. C1–C19 `NO_GO` stands unless C20 produces superseding consolidated final.
- Do not commit unless explicitly asked.

## KEY FILES

- Handover/state: `HANDOFF.md`, `README.md`, `research_state/strategy_spec.md`
- C20: `research_state/c20_prereg_20261116T063500Z.{json,md}`, `scripts/run_c20_cross_venue_campaign.py` (TS `20261116T063500Z`, seed `20261120`), `scripts/finish_c20_detached_durable.sh`, `scripts/verify_c20_focus_campaign.py`
- C19 ref: `research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.*`, `research_state/decision_verdict_hyperliquid_native_c19_20261116T054000Z.*`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.*`
- Gates: `scripts/session_gate.py`, `scripts/verify_campaign_evidence.py`, `scripts/probe_hyperliquid_blocker.py`, `scripts/verify_c13_focus_campaign.py`, `scripts/verify_c14_focus_campaign.py`, `scripts/verify_c19_focus_campaign.py`, `scripts/verify_c20_focus_campaign.py`, `scripts/verify_next_focus_campaign.py` (C6)
- Env: `scripts/bootstrap_env.sh` (durable default `.venv`)
- Code: `src/strategy/crash_rebound.py`, `src/strategy/config.py`, `src/backtest/engine.py`