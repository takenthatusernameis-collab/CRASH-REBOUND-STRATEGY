# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-16T14:31:10Z · **REGENERATED (UTC):** 2026-11-16T20:39:26Z · **Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound strategy research/backtesting, Hyperliquid-native evidence chain.
**Single durable handoff for the next agentic session — read this before doing anything else.**

> **PROGRAM STATE: C1–C19 CLOSED (final verdict `NO_GO`) · C20 IS THE BINDING NEXT FOCUS CAMPAIGN — NOT OPTIONAL.**
> C20 was preregistered at `research_state/c20_prereg_20261116T063500Z.{json,md}`. Its detached, lock-guarded, `--resume` compute is the only active campaign. It is **not complete**: the current gate is `C20 ACCEPTANCE: FAIL` (11 of 17 checks missing; 5 of 15 JSON artifacts on disk). The only accepted terminal state is `C20 ACCEPTANCE: PASS`. Do not re-plan, re-adjudicate C1–C19, relabel cross-venue results as Hyperliquid-native, edit the running campaign, or substitute narrative for artifacts.
>
> **Recovery rule:** an absent live supervisor is not evidence of completion. Relaunch `scripts/finish_c20_detached_durable.sh` and continue through the fail-closed gate. The durable supervisor stores its lock/log/status in `research_state/.c20/` and its Python environment at `.venv`; the legacy `/tmp/crs-venv`, `/tmp/c20_supervisor.lock`, `/tmp/c20_supervisor.log`, and `/tmp/c20_supervisor_status.json` paths are recovery inputs only and are not durable state.

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-16T20:39:26Z — FINISH C20, MANDATORY HEAVY WORK)

**Repository:** `CRASH-REBOUND-STRATEGY` (crash-rebound edge adjudication on real-market data).
**Priority:** C1–C19 adjudicated `SPEC_LITERAL_NEXT_OPEN` and returned consolidated `NO_GO`. The only remaining decision-relevant question is out-of-sample cross-venue replication on the two independent real archives (OKX + Binance UM). That is **C20**, the sole binding next focus campaign. Everything else is closed or inadmissible.

**Execute in order. Do not stop at planning, liveness narration, or inference-only churn.**

1. **Read this file fully.** Keep `SPEC_LITERAL_NEXT_OPEN` fixed; no config switching after results; no synthetic gap-fill presented as verified.
2. **Inspect both supervisor generations before touching anything.**
   ```bash
   pgrep -af 'finish_c20_detached|run_c20_cross_venue_campaign' || true
   ps -eo pid,ppid,sid,etime,time,pcpu,cmd | grep -E 'finish_c20|run_c20' | grep -v grep || true
   tail -n 40 /tmp/c20_supervisor.log 2>/dev/null || true
   tail -n 40 research_state/.c20/supervisor.log 2>/dev/null || true
   cat /tmp/c20_supervisor_status.json research_state/.c20/supervisor_status.json 2>/dev/null || true
   ls research_state/*_20261116T063500Z.json 2>/dev/null | wc -l
   ```
   - **Liveness = CPU-time advancement + new durable artifacts, not log lines or status-file presence.** Campaign logs can remain silent while an artifact is in flight. Probe twice about 10 seconds apart and confirm worker cumulative `TIME` advances.
   - A healthy legacy `/tmp` supervisor (for example PID 2735 in the previous checkpoint) owns `/tmp/c20_supervisor.lock`. **Do not start a second campaign while that tree is alive**, even after switching the durable handoff to `research_state/.c20/`.
   - If neither a live supervisor nor a live campaign is present, bootstrap and relaunch the durable supervisor:
     ```bash
     bash scripts/bootstrap_env.sh .venv
     setsid nohup bash scripts/finish_c20_detached_durable.sh >/dev/null 2>&1 < /dev/null &
     ```
     The durable script uses `.venv`, `research_state/.c20/supervisor.lock`, `--resume`, `--jobs 4`, exits 0 only on PASS, and automatically bootstraps `.venv` when needed. Never use a short `timeout`, foreground campaign, `--jobs 1`, or a parallel manual campaign.
   - **Kill only on positive true-stall evidence:** worker CPU time stops advancing across two 10-minute probes, or the active supervisor logs `STALLED` twice. Never kill on impatience. If a durable supervisor is `STALLED`/`EXHAUSTED`, inspect `research_state/.c20/supervisor.log`, preserve the actual blocker, then resume only after removing the specific cause.
3. **Run the acceptance gate after every completed attempt and at session end.**
   ```bash
   PYTHONPATH=. .venv/bin/python scripts/verify_c20_focus_campaign.py
   ```
   Required output: `C20 ACCEPTANCE: PASS` (all 17 checks). Anything else = not done. The gate verifies both venues end-to-end, both inference batteries, pooled synthesis, the consolidated final, and the C20 handoff reference.
4. **Do useful non-racing work only while C20 runs:** read `research_state/c20_prereg_20261116T063500Z.md` and run the lightweight hygiene gates in step 5. **Do not** launch another compute campaign, re-fetch archives, re-run C1–C19, edit `scripts/run_c20_cross_venue_campaign.py`, or alter the prereg/gate to make progress appear complete.
5. **Hygiene gates (must remain green; preserve literal tokens). CPU NOTE:** this host has `nproc=4`; the four C20 workers saturate all cores. Run only the lightweight gates below while C20 runs; **DEFER heavy `pytest tests/ -q` until C20 reaches PASS or a terminal verdict**, because concurrent pytest halves campaign throughput and C20 writes only to `research_state/`, never `src/`.
   ```bash
   PYTHONPATH=. .venv/bin/python scripts/session_gate.py              # 21/21 checks passed
   PYTHONPATH=. .venv/bin/python scripts/verify_campaign_evidence.py  # EVIDENCE VERIFIED
   PYTHONPATH=. .venv/bin/python scripts/verify_c19_focus_campaign.py # C19 ACCEPTANCE: PASS
   PYTHONPATH=. .venv/bin/python scripts/verify_c13_focus_campaign.py # C13 ACCEPTANCE: PASS
   PYTHONPATH=. .venv/bin/python scripts/verify_c14_focus_campaign.py # C14 ACCEPTANCE: PASS
   PYTHONPATH=. .venv/bin/python scripts/verify_next_focus_campaign.py # C6 ACCEPTANCE: PASS
   # DEFER until C20 terminal:  PYTHONPATH=. .venv/bin/python -m pytest tests/ -q   # 1047 passed, 1 skipped
   ```
6. **On PASS only:** update this HANDOFF with a new timestamped INITIAL TASK MESSAGE recording the verdict token from `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json`, per-venue and pooled numbers (trades, total PnL, spot/hedge/rebound legs, bootstrap CI, permutation p, placebo p), the full artifact list, and explicit C20 closure. If the token is `GO`, the next binding campaign is **C21 independent out-of-sample confirmation**, preregistered before any compute. If the token is `UNDERPOWERED` or `NO_GO`, close C1–C20 with the quantified power result and do not invent another same-data campaign. If blocked or exhausted, record the actual blocker and exact log path — never fake artifacts or weaken the gate.

**C20 remains the mandatory heavy-work obligation until `verify_c20_focus_campaign.py` prints `C20 ACCEPTANCE: PASS`.**

---

## LIVE STATE VERIFIED (2026-11-16T20:39:26Z)

- **Host capacity:** `nproc=4`. Four C20 workers can saturate all cores — **do not add concurrent CPU-heavy work**.
- **Observed at this checkpoint:** legacy supervisor `scripts/finish_c20_detached.sh` PID 2735 / SID 2735 and campaign PIDs 2750, 2963–2966 were alive; workers had roughly 01:03 CPU time each at ~95.4% CPU. That tree is healthy evidence of liveness, not a reason to launch a parallel campaign.
- **Durable recovery:** `.venv` and `research_state/.c20/` were absent at this checkpoint; the next session must create them via `bootstrap_env.sh` / the durable supervisor. This is not a stall by itself.
- **Actual stage:** OKX campaign/census/episode cached and landed; Binance UM campaign landed. The remaining heavy work is Binance UM census/episode, both placebos, both robustness batteries, both per-venue verdicts, pooled synthesis, and consolidated final.
- **Artifacts present (5/15 required JSONs):** `c20_prereg`, OKX campaign, OKX census, OKX episode-edge, Binance UM campaign.
- **Missing for PASS:** Binance UM census, Binance UM episode-edge, OKX/Binance placebos, OKX/Binance robustness batteries, OKX/Binance verdicts, `c20_pooled_cross_venue_synthesis`, `decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z`.
- **Gate:** `C20 ACCEPTANCE: FAIL` (11 of 17 checks missing as of this handoff) — only `scripts/verify_c20_focus_campaign.py` → `C20 ACCEPTANCE: PASS` is terminal success.
- **Hygiene gates:** previously green this campaign cycle (`session_gate.py` 21/21 checks passed, `verify_campaign_evidence.py` EVIDENCE VERIFIED, `verify_c19/c13/c14/next_focus` PASS). Not rerun in this handoff-only session to avoid CPU contention. Heavy `pytest tests/ -q` (1047 passed, 1 skipped) remains deferred until C20 is terminal.
- **Observed campaign numbers on disk (inference pending):** OKX 113 trades, total PnL −55,057.45, episode edge events=369 episodes=31 days=45 perm_p=0.6500 boot_CI=[-141457.07,27746.10]. Binance UM 136 trades, total PnL −70,309.57.
- **Ephemeral paths:** legacy `/tmp` files may vanish on restart; do not treat their absence as a stall. Durable artifacts are the `research_state/*_20261116T063500Z.json` files; durable supervisor state is `research_state/.c20/`.
- **Venv:** use `.venv/bin/python` after `bash scripts/bootstrap_env.sh .venv`; the legacy `/tmp/crs-venv/bin/python` is not durable.

## BOTTLENECKS REMOVED (carry-forward)

1. **Session-bound/short-timeout compute** → detached, lock-guarded, auto-resume durable supervisor (`scripts/finish_c20_detached_durable.sh`, `.venv`, `research_state/.c20/supervisor.lock`, `--resume`, exits 0 only on PASS). No short `timeout`, no `--jobs 1` on a 4-vCPU host, no foreground campaign.
2. **Lost `/tmp` state after restart** → durable supervisor lock/log/status live in `research_state/.c20/`; `/tmp` paths are treated as legacy inputs only. A missing `.venv` is repaired by one bootstrap command.
3. **Broken heartbeat interpretation** → liveness is judged by **CPU-time delta + artifact count**, not by a status file. Missing legacy status is expected and is not a stall signal.
4. **Handoff/gate token regression** → this file preserves literal tokens required by gates: `verify_c13_focus_campaign.py`, `verify_c14_focus_campaign.py` + `20261116T001200Z` + `C14 ACCEPTANCE: PASS`, `C19-T1` + `verify_c19_focus_campaign.py`, `C6-T1` + `campaign_results_real_okx_multiyear`, `session_gate.py` + `21/21 checks passed` + `2026-11-13T23:38:47Z`, `probe_hyperliquid_blocker.py`, `verify_campaign_evidence.py`, `verify_c20_focus_campaign.py`.
5. **Stage/ETA drift** → corrected from the live process and artifact state; no estimated completion time is treated as progress.
6. **Fail-closed acceptance** → only `scripts/verify_c20_focus_campaign.py` PASS is success; narrative, partial venue, or gate edits are rejected.
7. **CPU contention on a 4-vCPU host** → the four C20 workers saturate all cores, so heavy `pytest tests/ -q` is deferred until C20 reaches PASS/terminal. Lightweight gates only while C20 runs.

## C20 SPEC & DECISION RULES (prereg `c20_prereg_20261116T063500Z`, PRE_REGISTERED_BEFORE_COMPUTE)

- Config fixed: `entry_spec_literal_next_open=true`, RSI(21)<20, target 9%, ETH hedge on, $5M volume gate, seed 20261120. **No config switching after results.**
- Required artifacts (15): prereg, OKX+Binance campaigns+metrics, censuses, episode edges, placebos, robustness batteries, per-venue verdicts, `c20_pooled_cross_venue_synthesis`, `decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z`.
- GO only if pooled synthesis: episode-block bootstrap 95% CI excludes 0 with positive spot leg, permutation p<0.05, placebo p_ge_canonical<0.05, and ≥10 trades / ≥5 episodes / ≥5 crash days. Else `UNDERPOWERED` or `NO_GO` with quantified power curve. Compute it; current on-disk campaigns are negative and final inference is pending.
- C20 is cross-venue (`is_hyperliquid_venue_data=false`) — **never** Hyperliquid performance evidence.

## NO-AVOIDANCE CONTRACT (binding)

- Only accepted terminal state: `C20 ACCEPTANCE: PASS`. Narrative-only, partial venue, “prereg only,” relabeling cross-venue as Hyperliquid-native, or gate/script edits to pass are rejected.
- C20 requires **both venues end-to-end** + pooled synthesis + post-prereg consolidated final (no partial-credit terminal state).
- If the pooled token is `GO`, the next focus is **C21 independent out-of-sample confirmation**, preregistered before compute. If `UNDERPOWERED`/`NO_GO`, record it with a quantified power curve and close C1–C20; do not relitigate exhausted data.

## C1–C19 CLOSED STATE (historical, do not relitigate)

- **Consolidated final (C1–C19):** `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.{json,md}` — `NO_GO`.
- **C19:** T1 `spec_rebound_confirmation_adjudication_20261116T054000Z` (`SPEC_LITERAL_NEXT_OPEN`); T2 native battery C18 spec-literal 22 trades, −47,933.58, 31.8% WR, max DD −52,160 (NO_GO); T3 0/7 GO criteria, max 4 episodes < 5; T4 `decision_verdict_hyperliquid_native_c19_20261116T054000Z` NO_GO (`is_hyperliquid_evidence=true`); T5 consolidated NO_GO.
- **Acquisition CLOSED/exhausted:** Hyperliquid moving tail (`full_window_served=false`, earliest ~2026-04-21; `hyperliquid_retention_probe_next_20261116T054408Z.json`). No verified native archive ≥2023-01-01 or adding ≥1 independent crash episode beyond C14.
- **Native evidence:** underpowered/fragile (C14 7 trades, 3 episodes, CI spans 0). **C6 cross-venue context:** OKX+Binance UM pooled 38 venue-episodes underpowered (CI spans 0), `is_hyperliquid_venue_data=false`.

## GUARDRAILS (never violate)

- No cross-venue relabeling as Hyperliquid-native (`is_hyperliquid_venue_data=false` for C20).
- No synthetic gap-fill as verified; no spec relaxation to manufacture GO; `SPEC_LITERAL_NEXT_OPEN` fixed.
- No inference-only churn on exhausted C14 native data; C19 closed.
- No second concurrent campaign while any C20 supervisor/campaign tree is alive; no foreground campaign in an agent turn; no short `timeout`.
- Do not edit a running supervisor or `scripts/run_c20_cross_venue_campaign.py` to change the campaign; resume semantics are fixed.
- No silent change to the canonical baseline. C1–C19 `NO_GO` stands unless C20 produces a superseding consolidated final.
- Do not commit unless explicitly asked.

## KEY FILES

- Handover/state: `HANDOFF.md`, `README.md`, `research_state/strategy_spec.md`
- C20: `research_state/c20_prereg_20261116T063500Z.{json,md}`, `scripts/run_c20_cross_venue_campaign.py` (TS `20261116T063500Z`, seed `20261120`), `scripts/finish_c20_detached_durable.sh`, `scripts/verify_c20_focus_campaign.py`
- C19 ref: `research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.*`, `research_state/decision_verdict_hyperliquid_native_c19_20261116T054000Z.*`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.*`
- Gates: `scripts/session_gate.py`, `scripts/verify_campaign_evidence.py`, `scripts/probe_hyperliquid_blocker.py`, `scripts/verify_c13_focus_campaign.py`, `scripts/verify_c14_focus_campaign.py`, `scripts/verify_c19_focus_campaign.py`, `scripts/verify_c20_focus_campaign.py`, `scripts/verify_next_focus_campaign.py` (C6)
- Env: `scripts/bootstrap_env.sh` (durable default `.venv`)
- Code: `src/strategy/crash_rebound.py`, `src/strategy/config.py`, `src/backtest/engine.py`