# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-16T11:38:58Z · **Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound strategy research/backtesting, Hyperliquid-native evidence chain.
**Single durable handoff for the next agentic session — read this before doing anything else.**

> **PROGRAM STATE: C1–C19 CLOSED (final verdict `NO_GO`) · C20 IS THE BINDING NEXT FOCUS CAMPAIGN — NOT OPTIONAL.**
> C20 is preregistered and its heavy compute is **already running detached** (`scripts/finish_c20_detached.sh`, SID `22315`, attempt 1). It is **NOT complete** (`C20 ACCEPTANCE: FAIL`, 12 requirements missing). Your job is to drive it to `C20 ACCEPTANCE: PASS`, not to re-plan it. This handoff supersedes prior handoff text.

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-16T11:38:58Z — FINISH C20, MANDATORY HEAVY WORK)

**Repository:** `CRASH-REBOUND-STRATEGY`.
**Priority (from repo name + state):** this repo decides whether the crash-rebound strategy has a real edge. C1–C19 adjudicated the entry rule (`SPEC_LITERAL_NEXT_OPEN`: RSI(21)<20 crash close → buy at next hourly open, no same-bar confirmation gate) and returned `NO_GO` on Hyperliquid-native data. The single remaining decision-relevant question is whether that `NO_GO` replicates out-of-sample on the two independent real cross-venue archives (OKX + Binance UM). That is **C20**, the only binding next focus campaign. Everything else is closed or inadmissible.

**Do this, in order. Do not stop at planning, narrative, or inference-only churn.**

1. **Read this file fully.** Do not re-open C1–C19, do not relabel cross-venue results as Hyperliquid-native evidence, do not relax the spec, and do not substitute narrative for artifacts.
2. **Check the detached C20 worker first — do not start a second one.**
   ```bash
   ps -eo pid,sid,etime,pcpu,cmd | grep -E "finish_c20|run_c20" | grep -v grep
   tail -n 30 /tmp/c20_supervisor.log
   cat /tmp/c20_supervisor_status.json 2>/dev/null
   ```
   - If `finish_c20_detached.sh` **is** alive: **do nothing to it.** It re-launches with `--resume` after every failure and stops only on PASS. Poll only; do not race it with a manual run (duplicates 4 CPU-heavy workers and can corrupt an in-flight artifact).
   - If it is **gone without PASS**, relaunch detached (no timeout):
     ```bash
     setsid nohup bash scripts/finish_c20_detached.sh >/dev/null 2>&1 < /dev/null &
     ```
3. **Acceptance gate — the only accepted terminal state:**
   ```bash
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c20_focus_campaign.py
   ```
   → required output `C20 ACCEPTANCE: PASS` (all 15 requirements). Current baseline: **FAIL, 12 requirements missing** (gate output lists them). Bare "OKX done", "prereg only", or "narrative complete" is **not** accepted.
4. **While it runs, do useful non-racing work only:** read `research_state/c20_prereg_20261116T063500Z.md` (GO/UNDERPOWERED/NO_GO decision rule), and confirm evidence gates are green (step 5). **Do not** launch another compute campaign, re-fetch archives, re-run C1–C19, or edit `scripts/run_c20_cross_venue_campaign.py`.
5. **Hygiene gates (must be green before claiming done):**
   ```bash
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py             # expect 21/21 PASS
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py  # EVIDENCE VERIFIED
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c19_focus_campaign.py # C19 ACCEPTANCE: PASS
   PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest tests/ -q                 # expect 1047 passed, 1 skipped
   ```
6. **When (and only when) the gate prints PASS, update this HANDOFF.md** with a new timestamped **INITIAL TASK MESSAGE** recording: verdict token from `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json`, per-venue and pooled numbers (trades, total PnL, spot/hedge/rebound legs, bootstrap CI, permutation p, placebo p), full artifact list, and explicit statement that C20 is closed. If stalled/exhausted, record the actual blocker and exact log path — do not fake artifacts or downgrade the gate.

**C20 remains the heavy-work obligation until `verify_c20_focus_campaign.py` prints PASS.**

---

## LIVE STATE VERIFIED THIS SESSION (2026-11-16T11:38:58Z)

- **Supervisor running (do not disturb):** `scripts/finish_c20_detached.sh` **PID 22315, SID 22315, PPID 1**, attempt 1 started 2026-11-16T11:27:50Z (`/tmp/c20_supervisor.log`). `run_c20_cross_venue_campaign.py --venues okx binance_um --jobs 4 --resume` active with 4 workers (~93% CPU each). No `/tmp/c20_supervisor_status.json` yet (written on transitions/stall/PASS).
- **C20 gate:** `C20 ACCEPTANCE: FAIL — 12 requirement(s) missing` (c20_artifacts_present, binance_um_census_computed, okx/binance_um episode_edge, okx/binance_um placebo, okx/binance_um battery, okx/binance_um verdict, pooled synthesis, consolidated final). Prereg present: `research_state/c20_prereg_20261116T063500Z.{json,md}` (2 c20-timestamped files). Supervisor log shows OKX campaign+census cached/resuming from prior attempt.
- **Venv:** `/tmp/crs-venv/bin/python` present (no `scipy`, not needed). Bootstrap only if missing: `bash scripts/bootstrap_env.sh /tmp/crs-venv`.
- **Prior verified hygiene (2026-11-16T11:37Z, unchanged code):** `session_gate.py` 21/21, `verify_campaign_evidence.py` EVIDENCE VERIFIED, `verify_c19_focus_campaign.py` PASS, `pytest -q` 1047 passed, 1 skipped. Re-run step 5 before claiming C20 done.
- **Cost/ETA:** ~4–5 h end-to-end with `--jobs 4` (≈38 s/draw); expect PASS ~2026-11-16T16:00Z if uninterrupted. Poll, do not block a turn.

## BOTTLENECKS REMOVED (carry-forward, 2026-11-16T11:37Z)

1. **Session-bound/short-timeout compute made PASS impossible.** Fixed by killing session-bound run and launching detached, lock-guarded, auto-resume supervisor (`scripts/finish_c20_detached.sh`, SID 22315, PPID 1). Re-runs with `--resume` after failures, exits 0 only on PASS, stall-stops on two no-progress attempts. Single-instance lock `/tmp/c20_supervisor.lock`. If container restarts, `/tmp` is lost but durable `research_state/` artifacts persist — relaunch step 2.
2. **Doomed patterns:** never short `timeout`, never `--jobs 1` on 4-vCPU, never foreground campaign in agent turn. Use supervisor.
3. **No `scipy` required/installed** — do not install.
4. **Fail-closed acceptance:** `scripts/verify_c20_focus_campaign.py` (15 checks) is the only success signal.

---

## C20 SPEC & DECISION RULES (prereg `c20_prereg_20261116T063500Z`, PRE_REGISTERED_BEFORE_COMPUTE)

- Config fixed: `entry_spec_literal_next_open=true`, RSI(21)<20, target 9%, ETH hedge on, $5M volume gate, seed 20261120. **No config switching after results.**
- Required artifacts (15): prereg, OKX+Binance campaigns+metrics, censuses, episode edges, placebos, robustness batteries, per-venue verdicts, `c20_pooled_cross_venue_synthesis`, `decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z`.
- GO only if pooled synthesis: episode-block bootstrap 95% CI excludes 0 with positive spot leg, permutation p<0.05, placebo p_ge_canonical<0.05, and ≥10 trades / ≥5 episodes / ≥5 crash days. Else `UNDERPOWERED` or `NO_GO` with quantified power curve. Compute it — do not assume (both venue campaigns currently negative: OKX −55,057.45, Binance UM −70,309.57, but inference artifacts pending).
- C20 is cross-venue (`is_hyperliquid_venue_data=false`) — **never** Hyperliquid performance evidence.

---

## C1–C19 CLOSED STATE (historical, do not relitigate)

- **Consolidated final (C1–C19):** `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.{json,md}` — `NO_GO`. No validated edge.
- **C19:** T1 spec adjudicated (`SPEC_LITERAL_NEXT_OPEN`) `spec_rebound_confirmation_adjudication_20261116T054000Z`; T2 native battery C18 spec-literal 22 trades, −47,933.58, 31.8% WR, max DD −52,160 (NO_GO); T3 0/7 GO criteria, max 4 episodes < 5; T4 `decision_verdict_hyperliquid_native_c19_20261116T054000Z` NO_GO (`is_hyperliquid_evidence=true`); T5 consolidated NO_GO.
- **Acquisition CLOSED/exhausted:** Hyperliquid `candleSnapshot` moving tail (`full_window_served=false`, earliest ~2026-04-21; probe `hyperliquid_retention_probe_next_20261116T054408Z.json` 3849/6792 bars). No verified native archive ≥2023-01-01 or adding ≥1 independent crash episode beyond C14. Cross-venue not admissible as native.
- **Native evidence:** underpowered/fragile (C14 7 trades, 3 episodes, CI spans 0). **C6 cross-venue context:** OKX+Binance UM pooled 38 venue-episodes underpowered (CI spans 0), `is_hyperliquid_venue_data=false`.

---

## GUARDRAILS (never violate)

- No cross-venue relabeling as Hyperliquid-native (`is_hyperliquid_venue_data=false` for C20).
- No synthetic gap-fill presented as verified; no spec relaxation to manufacture GO; `SPEC_LITERAL_NEXT_OPEN` fixed.
- No inference-only churn on exhausted C14 native data; C19 closed.
- No second concurrent campaign while supervisor holds `/tmp/c20_supervisor.lock`; no foreground campaign in agent turn; no short `timeout`.
- No silent change to canonical baseline or `scripts/run_c20_cross_venue_campaign.py`.
- C1–C19 `NO_GO` stands unless C20 produces a superseding consolidated final.
- Do not commit unless explicitly asked.

## KEY FILES

- Handover/state: `HANDOFF.md`, `README.md`, `research_state/strategy_spec.md`
- C20: `research_state/c20_prereg_20261116T063500Z.{json,md}`, `scripts/run_c20_cross_venue_campaign.py` (TS `20261116T063500Z`, seed `20261120`), `scripts/finish_c20_detached.sh`, `scripts/verify_c20_focus_campaign.py`
- C19 ref: `research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.*`, `research_state/decision_verdict_hyperliquid_native_c19_20261116T054000Z.*`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.*`
- Gates: `scripts/session_gate.py`, `scripts/verify_campaign_evidence.py`, `scripts/probe_hyperliquid_blocker.py`, `scripts/verify_c{13,14,15,19,20}_focus_campaign.py`, `scripts/verify_next_focus_campaign.py`
- Env: `scripts/bootstrap_env.sh` (`/tmp/crs-venv`)
- Code: `src/strategy/crash_rebound.py`, `src/strategy/config.py`, `src/backtest/engine.py`
