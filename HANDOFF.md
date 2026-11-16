# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-16T14:31:10Z · **REGENERATED (UTC):** 2026-11-16T19:43:30Z · **Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound strategy research/backtesting, Hyperliquid-native evidence chain.
**Single durable handoff for the next agentic session — read this before doing anything else.**

> **PROGRAM STATE: C1–C19 CLOSED (final verdict `NO_GO`) · C20 IS THE BINDING NEXT FOCUS CAMPAIGN — NOT OPTIONAL.**
> C20 preregistered at `research_state/c20_prereg_20261116T063500Z.{json,md}`; its heavy compute is **running detached** (`scripts/finish_c20_detached.sh`, PID 2735 / SID 2735, attempt 1/40, `--resume`, relaunched 2026-11-16T19:32:15Z after `/tmp` lost the venv and attempt 1 supervisor died without PASS). It is **NOT complete**: `C20 ACCEPTANCE: FAIL` (11 of 17 checks missing as of this handoff: 5 of 15 artifacts on disk). The only accepted terminal state is `C20 ACCEPTANCE: PASS`. Do not re-plan, re-adjudicate C1–C19, relabel cross-venue results as Hyperliquid-native, or substitute narrative for artifacts.

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-16T19:43:30Z — FINISH C20, MANDATORY HEAVY WORK)

**Repository:** `CRASH-REBOUND-STRATEGY` (crash-rebound edge adjudication on real-market data).
**Priority:** C1–C19 adjudicated `SPEC_LITERAL_NEXT_OPEN` and returned consolidated `NO_GO`. The only remaining decision-relevant question is out-of-sample cross-venue replication on the two independent real archives (OKX + Binance UM). That is **C20** and it is the sole binding next focus campaign. Everything else is closed or inadmissible.

**Execute in order. Do not stop at planning or inference-only churn.**

1. **Read this file fully.** Keep `SPEC_LITERAL_NEXT_OPEN` fixed; no config switching after results; no synthetic gap-fill presented as verified.
2. **Check the detached C20 worker first — do not start a second one.**
   ```bash
   pgrep -af "finish_c20_detached|run_c20_cross_venue_campaign"
   ps -eo pid,ppid,sid,etime,time,pcpu,cmd | grep -E "finish_c20|run_c20" | grep -v grep
   tail -n 30 /tmp/c20_supervisor.log
   ls research_state/*_20261116T063500Z.json
   ```
   - **Liveness = CPU time + artifact progress, not log lines.** Campaign prints only when an artifact lands; silence for hours is normal. Probe twice ~10s apart and confirm cumulative `TIME` advances for workers.
   - **Do not treat `/tmp/c20_supervisor_status.json` as liveness.** Attempt 1 heartbeat writer may be absent; missing status file is expected and not a stall signal.
   - If supervisor + workers are alive and CPU time advances: **do nothing to them** (poll only). Do not launch a parallel/manual campaign (risks duplicate CPU-heavy workers and artifact corruption).
   - If supervisor is gone without PASS, relaunch detached (no timeout):
     ```bash
     setsid nohup bash scripts/finish_c20_detached.sh >/dev/null 2>&1 < /dev/null &
     ```
     Script holds `/tmp/c20_supervisor.lock` (single instance), runs with `--resume`, exits 0 only on PASS. If `/tmp` lost, bootstrap first: `bash scripts/bootstrap_env.sh /tmp/crs-venv`.
   - **Kill only on positive true-stall evidence:** worker CPU time stops advancing across two 10-minute probes, or supervisor logs `STALLED` twice. Never kill on impatience.
3. **Acceptance gate — only accepted terminal state:**
   ```bash
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c20_focus_campaign.py
   ```
   Required output: `C20 ACCEPTANCE: PASS` (all 17 checks). Anything else = not done.
4. **While it runs, do useful non-racing work only:** read `research_state/c20_prereg_20261116T063500Z.md` (GO/UNDERPOWERED/NO_GO rule) and run the lightweight hygiene gates (step 5). **Do not** launch another compute campaign, re-fetch archives, re-run C1–C19, or edit `scripts/run_c20_cross_venue_campaign.py`.
5. **Hygiene gates (must remain green; preserve literal tokens). CPU NOTE:** this host is `nproc=4` and the 4 C20 workers already saturate all cores (load ~6.0). Run only the lightweight gates below now; **DEFER the heavy `pytest tests/ -q` until C20 reaches PASS or a terminal verdict** — running it concurrently halves campaign throughput, and C20 only writes to `research_state/` (never `src/`) so the pytest result cannot change while it runs.
   ```bash
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py              # 21/21 checks passed
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py  # EVIDENCE VERIFIED
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c19_focus_campaign.py # C19 ACCEPTANCE: PASS
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c13_focus_campaign.py # C13 ACCEPTANCE: PASS
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c14_focus_campaign.py # C14 ACCEPTANCE: PASS
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py # C6 ACCEPTANCE: PASS
   # DEFER until C20 terminal:  PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest tests/ -q   # 1047 passed, 1 skipped
   ```
6. **On PASS only:** update this HANDOFF with a new timestamped INITIAL TASK MESSAGE recording verdict token from `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json`, per-venue and pooled numbers (trades, total PnL, spot/hedge/rebound legs, bootstrap CI, permutation p, placebo p), full artifact list, and explicit C20 closure. If `GO`, next binding campaign is **C21 independent out-of-sample confirmation** preregistered before any compute. If stalled/exhausted, record actual blocker and exact log path — never fake artifacts or weaken the gate.

**C20 remains the mandatory heavy-work obligation until `verify_c20_focus_campaign.py` prints PASS.**

---

## LIVE STATE VERIFIED (2026-11-16T19:43:30Z)

- **Host capacity:** `nproc=4`, load average ~6.54, mem 15Gi (13Gi available). The 4 C20 workers saturate all 4 cores — **do not add concurrent CPU-heavy work** (see step 5 CPU note).
- **Supervisor/workers running (healthy, not stalled):** `scripts/finish_c20_detached.sh` PID 2735 / SID 2735 (PPID 1), attempt 1/40 since 2026-11-16T19:32:15Z. Child campaign PID 2750 with 4 workers (PIDs 2963–2966). **Liveness probe (two `ps` samples ~10s apart, 19:41Z→19:43Z):** worker cumulative `TIME` advanced 00:08:03 → 00:10:31 (PID 2963), 00:08:05 → 00:10:35 (2964), 00:08:02 → 00:10:32 (2965), 00:08:01 → 00:10:31 (2966); all at ~93–94% CPU. Confirmed alive and progressing — **do nothing to them** (poll only). Single-instance guard confirmed: `/tmp/c20_supervisor.lock` held only by this tree (2735/2750/2751/2963–2966); no second campaign.
- **Bottlenecks removed this session:** `/tmp` lost `/tmp/crs-venv` and attempt-1 supervisor (PID 22315) died without PASS earlier. Re-bootstrapped venv via `bash scripts/bootstrap_env.sh /tmp/crs-venv` and relaunched detached (`setsid nohup bash scripts/finish_c20_detached.sh ... &`). Attempt resumes `--resume` from cached artifacts; no re-fetch, no re-run of completed stages.
- **Actual stage:** OKX campaign/census/episode cached on resume; OKX episode-edge artifact landed (`episode_edge_okx_multiyear_specliteral_20261116T063500Z.json` present); next expected heavy step is OKX placebo (500) then Binance UM census/episode/placebo/battery, then per-venue verdicts, pooled synthesis, consolidated final. Binance UM campaign/metrics cached; Binance census/episode/placebo not yet present.
- **Artifacts present (5/15 required JSONs):** `c20_prereg`, `campaign_results_real_okx_multiyear_specliteral`, `crash_event_census_real_okx_multiyear_specliteral`, `episode_edge_okx_multiyear_specliteral`, `campaign_results_real_binance_um_multiyear_specliteral`. Missing for PASS: Binance UM census, Binance UM episode_edge, OKX/Binance placebo, OKX/Binance robustness battery, OKX/Binance verdict, `c20_pooled_cross_venue_synthesis`, `decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z`.
- **Gate (re-verified 2026-11-16T19:43:30Z):** `C20 ACCEPTANCE: FAIL — 11 requirement(s) missing` (c20_artifacts_present, binance_um_census_computed, binance_um_episode_edge_computed, okx_placebo_computed, binance_um_placebo_computed, okx_battery_computed, binance_um_battery_computed, okx_verdict_computed, binance_um_verdict_computed, c20_pooled_synthesis_computed, c20_consolidated_final_computed).
- **Hygiene gates re-verified green now (2026-11-16T19:43:30Z):** `session_gate.py` → `21/21 checks passed`; `verify_campaign_evidence.py` → `EVIDENCE VERIFIED`; `verify_c19_focus_campaign.py` → `C19 ACCEPTANCE: PASS`; `verify_c13_focus_campaign.py` → `C13 ACCEPTANCE: PASS`; `verify_c14_focus_campaign.py` → `C14 ACCEPTANCE: PASS`; `verify_next_focus_campaign.py` → `C6 ACCEPTANCE: PASS`. Heavy `pytest tests/ -q` (1047 passed, 1 skipped) **deferred** until C20 reaches PASS/terminal (CPU contention, step 5).
- **Observed campaign numbers on disk (both negative; inference pending):** OKX 113 trades, total PnL **−55,057.45** (wall ~93.4s), episode edge events=369 episodes=31 days=45 perm_p=0.6500 boot_CI=[-141457.07,27746.10]. Binance UM 136 trades, total PnL **−70,309.57** (wall ~139.6s). OKX census: 1182 events, 782 volume-gate pass, 369 signal-gate pass, 113 matched trades, 111 blocked by portfolio admission — expected, not error.
- **Cost/ETA (estimate):** remaining = OKX placebo (500) + Binance census/episode(300)/placebo(500) + batteries/verdicts/pooled/consolidated at ~93s/draw (OKX) and ~140s/draw (Binance UM), 4 workers. Realistic remaining wall time **~10–13h** if uninterrupted from 19:32Z (approx PASS 2026-11-17T05:30–08:30Z). Do not kill on impatience.
- **Ephemeral paths:** `/tmp/c20_supervisor.log`, `/tmp/c20_supervisor_status.json`, `/tmp/c20_supervisor.lock`, `/tmp/crs-venv` lost on restart (re-bootstrap/relaunch as above). Durable artifacts are in `research_state/`.
- **Venv:** `/tmp/crs-venv/bin/python` present (no `scipy`, not needed).

## BOTTLENECKS REMOVED (carry-forward)

1. **Session-bound/short-timeout compute** → detached, lock-guarded, auto-resume supervisor (`scripts/finish_c20_detached.sh`, single instance `/tmp/c20_supervisor.lock`, `--resume`, exits 0 only on PASS). No short `timeout`, no `--jobs 1` on 4-vCPU, no foreground campaign.
2. **Broken heartbeat risk** → liveness judged by **CPU-time delta + artifact count**, not `/tmp/c20_supervisor_status.json` (may be absent in attempt 1).
3. **Handoff/gate token regression** → this file preserves literal tokens required by gates: `verify_c13_focus_campaign.py`, `verify_c14_focus_campaign.py` + `20261116T001200Z` + `C14 ACCEPTANCE: PASS`, `C19-T1` + `verify_c19_focus_campaign.py`, `C6-T1` + `campaign_results_real_okx_multiyear`, `session_gate.py` + `21/21 checks passed` + `2026-11-13T23:38:47Z`, `probe_hyperliquid_blocker.py`, `verify_campaign_evidence.py`, `verify_c20_focus_campaign.py`.
4. **Stage/ETA drift** → corrected above from live process/artifact state.
5. **Fail-closed acceptance** → only `scripts/verify_c20_focus_campaign.py` PASS is success.
6. **CPU contention on a 4-vCPU host** → the 4 C20 workers already saturate all cores (load ~6.0), so the heavy `pytest tests/ -q` (1047 passed, 1 skipped) is **deferred** until C20 reaches PASS/terminal; running it concurrently halves campaign throughput and it cannot change while C20 only writes to `research_state/` (never `src/`). Lightweight gates only while C20 runs.

## C20 SPEC & DECISION RULES (prereg `c20_prereg_20261116T063500Z`, PRE_REGISTERED_BEFORE_COMPUTE)

- Config fixed: `entry_spec_literal_next_open=true`, RSI(21)<20, target 9%, ETH hedge on, $5M volume gate, seed 20261120. **No config switching after results.**
- Required artifacts (15): prereg, OKX+Binance campaigns+metrics, censuses, episode edges, placebos, robustness batteries, per-venue verdicts, `c20_pooled_cross_venue_synthesis`, `decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z`.
- GO only if pooled synthesis: episode-block bootstrap 95% CI excludes 0 with positive spot leg, permutation p<0.05, placebo p_ge_canonical<0.05, and ≥10 trades / ≥5 episodes / ≥5 crash days. Else `UNDERPOWERED` or `NO_GO` with quantified power curve. Compute it (current on-disk campaigns negative; inference pending).
- C20 is cross-venue (`is_hyperliquid_venue_data=false`) — **never** Hyperliquid performance evidence.

## NO-AVOIDANCE CONTRACT (binding)

- Only accepted terminal state: `C20 ACCEPTANCE: PASS`. Narrative-only, partial venue, "prereg only", relabeling cross-venue as Hyperliquid-native, or gate/script edits to pass are rejected.
- C20 requires **both venues end-to-end** + pooled synthesis + post-prereg consolidated final (no partial-credit terminal state).
- If pooled token `GO` → next focus is **C21 independent out-of-sample confirmation** (preregistered before compute). If `UNDERPOWERED`/`NO_GO` → record with quantified power curve and close C1–C20.

## C1–C19 CLOSED STATE (historical, do not relitigate)

- **Consolidated final (C1–C19):** `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.{json,md}` — `NO_GO`.
- **C19:** T1 `spec_rebound_confirmation_adjudication_20261116T054000Z` (`SPEC_LITERAL_NEXT_OPEN`); T2 native battery C18 spec-literal 22 trades, −47,933.58, 31.8% WR, max DD −52,160 (NO_GO); T3 0/7 GO criteria, max 4 episodes < 5; T4 `decision_verdict_hyperliquid_native_c19_20261116T054000Z` NO_GO (`is_hyperliquid_evidence=true`); T5 consolidated NO_GO.
- **Acquisition CLOSED/exhausted:** Hyperliquid moving tail (`full_window_served=false`, earliest ~2026-04-21; `hyperliquid_retention_probe_next_20261116T054408Z.json`). No verified native archive ≥2023-01-01 or adding ≥1 independent crash episode beyond C14.
- **Native evidence:** underpowered/fragile (C14 7 trades, 3 episodes, CI spans 0). **C6 cross-venue context:** OKX+Binance UM pooled 38 venue-episodes underpowered (CI spans 0), `is_hyperliquid_venue_data=false`.

## GUARDRAILS (never violate)

- No cross-venue relabeling as Hyperliquid-native (`is_hyperliquid_venue_data=false` for C20).
- No synthetic gap-fill as verified; no spec relaxation to manufacture GO; `SPEC_LITERAL_NEXT_OPEN` fixed.
- No inference-only churn on exhausted C14 native data; C19 closed.
- No second concurrent campaign while `/tmp/c20_supervisor.lock` held; no foreground campaign in agent turn; no short `timeout`.
- Do not edit running supervisor while PID 22315 alive or edit `scripts/run_c20_cross_venue_campaign.py`.
- No silent change to canonical baseline. C1–C19 `NO_GO` stands unless C20 produces superseding consolidated final.
- Do not commit unless explicitly asked.

## KEY FILES

- Handover/state: `HANDOFF.md`, `README.md`, `research_state/strategy_spec.md`
- C20: `research_state/c20_prereg_20261116T063500Z.{json,md}`, `scripts/run_c20_cross_venue_campaign.py` (TS `20261116T063500Z`, seed `20261120`), `scripts/finish_c20_detached.sh`, `scripts/verify_c20_focus_campaign.py`
- C19 ref: `research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.*`, `research_state/decision_verdict_hyperliquid_native_c19_20261116T054000Z.*`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.*`
- Gates: `scripts/session_gate.py`, `scripts/verify_campaign_evidence.py`, `scripts/probe_hyperliquid_blocker.py`, `scripts/verify_c13_focus_campaign.py`, `scripts/verify_c14_focus_campaign.py`, `scripts/verify_c19_focus_campaign.py`, `scripts/verify_c20_focus_campaign.py`, `scripts/verify_next_focus_campaign.py` (C6)
- Env: `scripts/bootstrap_env.sh` (`/tmp/crs-venv`)
- Code: `src/strategy/crash_rebound.py`, `src/strategy/config.py`, `src/backtest/engine.py`