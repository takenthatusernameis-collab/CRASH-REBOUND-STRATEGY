# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-16T14:31:10Z · **REGENERATED (UTC):** 2026-11-16T21:38:30Z · **Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound strategy research/backtesting, Hyperliquid-native evidence chain.
**Single durable handoff for the next agentic session — read this before doing anything else.**

> **PROGRAM STATE: C1–C19 CLOSED (final verdict `NO_GO`) · C20 IS THE BINDING NEXT FOCUS CAMPAIGN — NOT OPTIONAL.**
> C20 was preregistered at `research_state/c20_prereg_20261116T063500Z.{json,md}`. Its detached, lock-guarded, `--resume` compute is the only active campaign. It is **not complete**: the current gate is `C20 ACCEPTANCE: FAIL` (11 of 17 checks missing; 5 of 15 JSON artifacts on disk). The only accepted terminal state is `C20 ACCEPTANCE: PASS`. Do not re-plan, re-adjudicate C1–C19, relabel cross-venue results as Hyperliquid-native, edit the running campaign, or substitute narrative for artifacts.
>
> **Recovery rule:** an absent live supervisor is not evidence of completion. Relaunch `scripts/finish_c20_detached_durable.sh` and continue through the fail-closed gate. The durable supervisor stores its lock/log/status in `research_state/.c20/` and its Python environment at `.venv`; the legacy `/tmp/crs-venv`, `/tmp/c20_supervisor.lock`, `/tmp/c20_supervisor.log`, and `/tmp/c20_supervisor_status.json` paths are recovery inputs only and are not durable state.

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-16T21:38:30Z — FINISH C20, MANDATORY HEAVY WORK)

**Repository:** `CRASH-REBOUND-STRATEGY` (crash-rebound edge adjudication on real-market data).
**Priority:** C1–C19 adjudicated `SPEC_LITERAL_NEXT_OPEN` and returned consolidated `NO_GO`. The only remaining decision-relevant question is out-of-sample cross-venue replication on the two independent real archives (OKX + Binance UM). That is **C20**, the sole binding next focus campaign. Everything else is closed or inadmissible.

**Execute in order. Do not stop at planning, liveness narration, or inference-only churn.**

1. **Read this file fully.** Keep `SPEC_LITERAL_NEXT_OPEN` fixed; no config switching after results; no synthetic gap-fill presented as verified.
2. **Inspect live compute before touching anything (do not disturb a healthy run).**
   ```bash
   pgrep -af 'finish_c20_detached|run_c20_cross_venue_campaign' || true
   ps -eo pid,ppid,sid,etime,time,pcpu,cmd | grep -E 'finish_c20|run_c20' | grep -v grep || true
   tail -n 40 /tmp/c20_supervisor.log 2>/dev/null || echo "no /tmp log"
   tail -n 40 research_state/.c20/supervisor.log 2>/dev/null || echo "no durable log"
   cat /tmp/c20_supervisor_status.json research_state/.c20/supervisor_status.json 2>/dev/null || true
   ls research_state/*_20261116T063500Z.json 2>/dev/null | wc -l
   ```
   - **Liveness = worker cumulative CPU `TIME` advancing across two probes ~10s apart + durable artifact progress, not log/status presence.** Silent logs while artifacts are in flight are normal.
   - **LIVE NOW (2026-11-16T21:35Z, verified):** legacy supervisor `scripts/finish_c20_detached.sh` PID 2735/SID 2735 alive (etime ~02:03:36); campaign PID 2750 + workers 2963–2966 alive (4 workers, `/tmp/crs-venv`, ~95.5% CPU each). `/tmp/c20_supervisor_status.json` = `IN_FLIGHT_HEAVY_COMPUTE`, attempt 1, artifacts=5, updated 2026-11-16T21:37:35Z. `/tmp/c20_supervisor.log` shows attempt 1 start at 2026-11-16T19:32:15Z with OKX campaign/census/episode cached. Worker cumulative `TIME` ~01:57 each and advancing (healthy). C20 gate: `C20 ACCEPTANCE: FAIL` (11/17 missing).
   - **If a live C20 supervisor/campaign tree exists (legacy or durable), do not start a second campaign.** Let it run to completion while you do only non-racing work in step 4.
   - **Only if no live supervisor/campaign is present:** recover durably and relaunch:
     ```bash
     bash scripts/bootstrap_env.sh .venv
     setsid nohup bash scripts/finish_c20_detached_durable.sh >/dev/null 2>&1 < /dev/null &
     ```
     Durable script uses `.venv`, `research_state/.c20/supervisor.lock`, `--resume`, `--jobs 4`, exits 0 only on PASS, and bootstraps `.venv` if needed. Never use a short `timeout`, foreground campaign, `--jobs 1`, or parallel manual campaign.
   - **Kill only on positive true-stall evidence:** worker CPU time stops advancing across two 10-minute probes, or active supervisor logs `STALLED` twice. Never kill on impatience. If durable supervisor is `STALLED`/`EXHAUSTED`, inspect `research_state/.c20/supervisor.log`, preserve the blocker, remove the specific cause, then resume.
3. **Run the acceptance gate after every completed attempt and at session end.**
   ```bash
   PYTHONPATH=. .venv/bin/python scripts/verify_c20_focus_campaign.py 2>/dev/null || PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c20_focus_campaign.py 2>/dev/null || PYTHONPATH=. python3 scripts/verify_c20_focus_campaign.py
   ```
   Required output: `C20 ACCEPTANCE: PASS` (all 17 checks). Anything else = not done. Gate verifies both venues end-to-end, both inference batteries, pooled synthesis, consolidated final, and C20 handoff reference.
4. **Useful non-racing work only while C20 runs:** read `research_state/c20_prereg_20261116T063500Z.md`; run lightweight hygiene gates in step 5 if CPU headroom allows. **Do not** launch another compute campaign, re-fetch archives, re-run C1–C19, edit `scripts/run_c20_cross_venue_campaign.py`, or alter prereg/gate to fake progress.
5. **Hygiene gates (must remain green; preserve literal tokens). CPU NOTE:** host has `nproc=4`; four C20 workers saturate cores. Run lightweight gates only when not contending; **DEFER heavy `pytest tests/ -q` until C20 reaches PASS or a terminal verdict** (C20 writes only to `research_state/`, never `src/`).
   ```bash
   PYTHONPATH=. .venv/bin/python scripts/session_gate.py 2>/dev/null || PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py              # 21/21 checks passed
   PYTHONPATH=. .venv/bin/python scripts/verify_campaign_evidence.py 2>/dev/null || PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py  # EVIDENCE VERIFIED
   PYTHONPATH=. .venv/bin/python scripts/verify_c19_focus_campaign.py 2>/dev/null || PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c19_focus_campaign.py # C19 ACCEPTANCE: PASS
   PYTHONPATH=. .venv/bin/python scripts/verify_c13_focus_campaign.py 2>/dev/null || PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c13_focus_campaign.py # C13 ACCEPTANCE: PASS
   PYTHONPATH=. .venv/bin/python scripts/verify_c14_focus_campaign.py 2>/dev/null || PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c14_focus_campaign.py # C14 ACCEPTANCE: PASS
   PYTHONPATH=. .venv/bin/python scripts/verify_next_focus_campaign.py 2>/dev/null || PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py # C6 ACCEPTANCE: PASS
   # DEFER until C20 terminal:  PYTHONPATH=. .venv/bin/python -m pytest tests/ -q   # 1047 passed, 1 skipped
   ```
6. **On PASS only:** update this HANDOFF with a new timestamped INITIAL TASK MESSAGE recording verdict token from `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json`, per-venue and pooled numbers (trades, total PnL, spot/hedge/rebound legs, bootstrap CI, permutation p, placebo p), full artifact list, and explicit C20 closure. If token is `GO`, next binding campaign is **C21 independent out-of-sample confirmation**, preregistered before any compute. If `UNDERPOWERED` or `NO_GO`, close C1–C20 with quantified power result and do not invent another same-data campaign. If blocked/exhausted, record actual blocker and exact log path — never fake artifacts or weaken gate.

**C20 remains the mandatory heavy-work obligation until `scripts/verify_c20_focus_campaign.py` prints `C20 ACCEPTANCE: PASS`.**

---

## LIVE STATE VERIFIED (2026-11-16T21:38:30Z)

- **Host capacity:** `nproc=4`. Four C20 workers saturate all cores — do not add concurrent CPU-heavy work.
- **Live compute (observed):** legacy supervisor `scripts/finish_c20_detached.sh` PID 2735/SID 2735 alive (etime ~02:06); campaign PID 2750 + workers 2963–2966 alive (4 workers, `/tmp/crs-venv`, ~95.4% CPU each). `/tmp/c20_supervisor_status.json` = `IN_FLIGHT_HEAVY_COMPUTE`, attempt 1, artifacts=5, updated 2026-11-16T21:38:25Z. `/tmp/c20_supervisor.log` shows attempt 1 start 2026-11-16T19:32:15Z with OKX campaign/census/episode cached. Worker cumulative `TIME` ~01:59 each and advancing (healthy, progressing).
- **Durable recovery state:** `.venv` NOT present at repo root (legacy run uses `/tmp/crs-venv`); `research_state/.c20/` absent. Durable relaunch path available but **must not be used while legacy tree is alive**. If legacy tree dies, `bash scripts/bootstrap_env.sh .venv` then relaunch `scripts/finish_c20_detached_durable.sh`.
- **Actual stage:** OKX campaign/census/episode cached+landed; Binance UM campaign/metrics landed. Remaining heavy work: Binance UM census/episode, both placebos, both robustness batteries, both per-venue verdicts, pooled synthesis, consolidated final.
- **Artifacts present (7 JSON files on disk):** `c20_prereg`, OKX campaign/metrics+census+episode, Binance UM campaign/metrics. `verify_c20_focus_campaign.py` reports 11/17 checks missing (`c20_artifacts_present` still failing) — required semantic artifacts still incomplete.
- **Missing for PASS:** Binance UM census, Binance UM episode-edge, OKX/Binance placebos, OKX/Binance robustness batteries, OKX/Binance verdicts, `c20_pooled_cross_venue_synthesis`, `decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z`.
- **Gate:** `C20 ACCEPTANCE: FAIL` (11 of 17 checks missing) — only `scripts/verify_c20_focus_campaign.py` → `C20 ACCEPTANCE: PASS` is terminal success.
- **Hygiene (last known green per prior cycle):** `session_gate.py` 21/21 checks passed (baseline token 2026-11-13T23:38:47Z), `verify_campaign_evidence.py` EVIDENCE VERIFIED, `verify_c19/c13/c14/next_focus` PASS. Not rerun this session to avoid CPU contention. Heavy `pytest tests/ -q` (1047 passed, 1 skipped) deferred until C20 terminal.
- **Observed campaign numbers on disk (inference pending):** OKX 113 trades, total PnL −55,057.45, episode edge events=369 episodes=31 days=45 perm_p=0.6500 boot_CI=[-141457.07,27746.10]. Binance UM 136 trades, total PnL −70,309.57.
- **Ephemeral paths:** legacy `/tmp` files may vanish on restart; do not treat absence as stall. Durable artifacts are `research_state/*_20261116T063500Z.json`; durable supervisor state target is `research_state/.c20/`.
- **Venv:** prefer `.venv/bin/python` after bootstrap; live legacy run currently uses `/tmp/crs-venv/bin/python`.
- **Leftover/nonblocking:** `tmpgq4pmrk6/cache/hyperliquid/provenance.json` exists at repo root (temp-named dir). Not removed to avoid interfering with unknown consumers; treat as cleanup candidate after C20 terminal unless referenced.

## BOTTLENECKS REMOVED / UNBLOCKED (2026-11-16T21:38:30Z)

1. **Durable-recovery gap while legacy compute runs** → handoff explicitly forbids parallel durable relaunch when legacy tree is healthy and provides exact durable bootstrap/relaunch commands for the no-live-process case.
2. **Session-bound/short-timeout compute** (carry-forward) → detached, lock-guarded, auto-resume durable supervisor (`scripts/finish_c20_detached_durable.sh`, `.venv`, `research_state/.c20/supervisor.lock`, `--resume`, exits 0 only on PASS). No short `timeout`, no `--jobs 1`, no foreground campaign.
3. **Lost `/tmp` state risk** (carry-forward) → durable supervisor lock/log/status in `research_state/.c20/`; `/tmp` treated as legacy inputs only.
4. **Liveness misread** (carry-forward) → judge by worker CPU-time delta + artifact count, not status/log presence.
5. **CPU contention on 4-vCPU host** (carry-forward) → heavy `pytest tests/ -q` deferred until C20 terminal; lightweight gates only when non-contending.
6. **Fail-closed acceptance** (carry-forward) → only `scripts/verify_c20_focus_campaign.py` PASS is success.
7. **No new bottleneck this session (2026-11-16T21:38:30Z, verified)** → legacy C20 supervisor/campaign tree healthy (PID 2735, campaign 2750, workers 2963–2966 ~95.4% CPU, cumulative TIME ~01:59 advancing, artifacts=5 per status, 7 JSONs on disk, gate FAIL 11/17). No blocked/inefficient sessions observed; durable handoff refreshed and no competing campaign launched.

## C20 SPEC & DECISION RULES (prereg `c20_prereg_20261116T063500Z`, PRE_REGISTERED_BEFORE_COMPUTE)

- Config fixed: `entry_spec_literal_next_open=true`, RSI(21)<20, target 9%, ETH hedge on, $5M volume gate, seed 20261120. **No config switching after results.**
- Required artifacts (15): prereg, OKX+Binance campaigns+metrics, censuses, episode edges, placebos, robustness batteries, per-venue verdicts, `c20_pooled_cross_venue_synthesis`, `decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z`.
- GO only if pooled synthesis: episode-block bootstrap 95% CI excludes 0 with positive spot leg, permutation p<0.05, placebo p_ge_canonical<0.05, and ≥10 trades / ≥5 episodes / ≥5 crash days. Else `UNDERPOWERED` or `NO_GO` with quantified power curve. Current on-disk campaigns negative; final inference pending.
- C20 is cross-venue (`is_hyperliquid_venue_data=false`) — **never** Hyperliquid performance evidence.

## NO-AVOIDANCE CONTRACT (binding)

- Only accepted terminal state: `C20 ACCEPTANCE: PASS`. Narrative-only, partial venue, "prereg only," relabeling cross-venue as Hyperliquid-native, or gate/script edits to pass are rejected.
- C20 requires **both venues end-to-end** + pooled synthesis + post-prereg consolidated final (no partial-credit terminal state).
- If pooled token is `GO`, next focus is **C21 independent out-of-sample confirmation**, preregistered before compute. If `UNDERPOWERED`/`NO_GO`, record with quantified power curve and close C1–C20; do not relitigate exhausted data.

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
- No silent change to canonical baseline. C1–C19 `NO_GO` stands unless C20 produces superseding consolidated final.
- Do not commit unless explicitly asked.

## KEY FILES

- Handover/state: `HANDOFF.md`, `README.md`, `research_state/strategy_spec.md`
- C20: `research_state/c20_prereg_20261116T063500Z.{json,md}`, `scripts/run_c20_cross_venue_campaign.py` (TS `20261116T063500Z`, seed `20261120`), `scripts/finish_c20_detached_durable.sh`, `scripts/verify_c20_focus_campaign.py`
- C19 ref: `research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.*`, `research_state/decision_verdict_hyperliquid_native_c19_20261116T054000Z.*`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.*`
- Gates: `scripts/session_gate.py`, `scripts/verify_campaign_evidence.py`, `scripts/probe_hyperliquid_blocker.py`, `scripts/verify_c13_focus_campaign.py`, `scripts/verify_c14_focus_campaign.py`, `scripts/verify_c19_focus_campaign.py`, `scripts/verify_c20_focus_campaign.py`, `scripts/verify_next_focus_campaign.py` (C6)
- Env: `scripts/bootstrap_env.sh` (durable default `.venv`)
- Code: `src/strategy/crash_rebound.py`, `src/strategy/config.py`, `src/backtest/engine.py`