# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-17T05:41:10Z · **Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound strategy research/backtesting; real-market, cross-venue (OKX + Binance UM) evidence chain feeding C20.
**Single durable handoff for the next agentic session — read this before doing anything else.**
**Phase O artifact timestamp (binding, `research_state/episode_edge_okx_full.json`):** `2026-11-13T23:38:47Z` · **Session done-gate:** `scripts/session_gate.py` = `21/21 checks passed` (re-verified 2026-11-17T05:40:55Z, green).

> **PROGRAM STATE: C1–C20 COMPLETE. FINAL VERDICT `NO_GO`. C20 ACCEPTANCE: PASS (independently re-verified 2026-11-17T05:40:55Z; 15/15 required JSON artifacts on disk; consolidated final `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json` supersedes `..._20261116T054500Z.json`, token `NO_GO`, `research_program_complete: true`).**
> **The C20 durable supervisor exited cleanly at 2026-11-17T05:39:45Z with `C20 ACCEPTANCE: PASS` (artifacts=15, attempts=1, run_rc=0). There is NO live supervisor/campaign process now (verified `pgrep -af 'finish_c20_detached|run_c20'` = none).**
>
> **⚠ STALE-STATE CORRECTION (supersedes the prior handoff's live-state block):** the previous handoff (2026-11-17T05:38:35Z) recorded C20 as *in-flight with 10/15 artifacts* and instructed the next session to "monitor the live supervisor / relaunch `scripts/finish_c20_detached_durable.sh` if dead." That state is **obsolete**. C20 finished PASS ~1 minute later. **Do NOT relaunch the C20 supervisor/campaign — it already passed.** Relaunching now would be a spurious rival campaign (guardrail violation) and a `--resume` would only re-print cached PASS. There is nothing to wait for.
>
> **NEXT SESSION'S REAL JOB: CLOSURE CERTIFICATION of the NO_GO result — not a new same-data campaign.** See the timestamped INITIAL TASK MESSAGE below.

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-17T05:41:10Z — CLOSE C1–C20 WITH VERIFIED NO_GO; MANDATORY HEAVY WORK)

**Repository:** `CRASH-REBOUND-STRATEGY` (crash-rebound edge adjudication on real-market data). **Priority by repo scope:** the research program C1–C20 is **complete with a `NO_GO` verdict on all venues**. No decision-relevant research campaign remains authorized. **Do not invent a same-data campaign, do not relabel cross-venue results as Hyperliquid-native, do not relax the prereg, do not fabricate artifacts.** The binding obligation is to **certify and document the closure** with real, verifiable work.

**Execute in order. No planning-only stops, no liveness narration as progress, no inference-only churn, no handoff-refresh-as-progress.**

**BOTTOM LINE UP FRONT (verified 2026-11-17T05:40:55Z):**
- `scripts/verify_c20_focus_campaign.py` → `C20 ACCEPTANCE: PASS — full cross-venue spec-literal campaign complete (pooled=NO_GO)`.
- All 15 C20 artifacts present (`research_state/*_20261116T063500Z.json`). Final `decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json`: token `NO_GO`, `research_program_complete=true`, supersedes C1–C19 final.
- All gates green: session_gate `21/21 checks passed`, `verify_campaign_evidence.py` `EVIDENCE VERIFIED`, C19/C13/C14/C6/C20 all `ACCEPTANCE: PASS`.
- **The only deferred heavy work is now UNBLOCKED** (C20 released the 4 vCPUs): the full `pytest tests/ -q` suite (last known `1047 passed, 1 skipped`). This is the mandatory non-avoidance task below.

1. **Read this file fully.** Do not re-plan C1–C20. Do not start a rival campaign. Preserve literal gate tokens (listed in GUARDRAILS).
2. **Confirm the terminal state before any heavy step (read-only probes).**
   ```bash
   pgrep -af 'finish_c20_detached|run_c20' || echo "no C20 procs (expected)"
   cat research_state/.c20/supervisor_status.json 2>/dev/null   # state=PASS expected
   ls research_state/*_20261116T063500Z.json | wc -l           # 15 expected
   ```
   If `state` is anything other than `PASS`, or `<15` artifacts, STOP and re-run the gate (step 4) and record the actual failure — do not assume PASS.
3. **MANDATORY HEAVY WORK — run the deferred full test suite (now unblocked).** C20 no longer saturates the host, so this is safe and required for closure certification:
   ```bash
   PYTHONPATH=. .venv/bin/python -m pytest tests/ -q
   ```
   Expected literal: `1047 passed, 1 skipped`. If the count differs or any test fails, record the exact summary line + failing node ids and fix the specific regression (do not weaken tests). This run is the proof that the NO_GO program left the codebase green.
4. **Re-run the acceptance/hygiene gates and confirm green (literal tokens must match).**
   ```bash
   PY=.venv/bin/python; [ -x "$PY" ] || PY=python3
   PYTHONPATH=. $PY scripts/session_gate.py
   PYTHONPATH=. $PY scripts/verify_campaign_evidence.py
   PYTHONPATH=. $PY scripts/verify_c20_focus_campaign.py
   PYTHONPATH=. $PY scripts/verify_c19_focus_campaign.py
   PYTHONPATH=. $PY scripts/verify_c13_focus_campaign.py
   PYTHONPATH=. $PY scripts/verify_c14_focus_campaign.py
   PYTHONPATH=. $PY scripts/verify_next_focus_campaign.py   # C6
   PYTHONPATH=. $PY scripts/probe_hyperliquid_blocker.py
   ```
   Expected literals: session gate `21/21 checks passed`; evidence `EVIDENCE VERIFIED`; C20 `C20 ACCEPTANCE: PASS`; C19 `C19 ACCEPTANCE: PASS`; C13 `C13 ACCEPTANCE: PASS`; C14 `C14 ACCEPTANCE: PASS`; C6 `C6 ACCEPTANCE: PASS`.
5. **Produce the closure record.** Ensure a human-readable consolidated-final memo exists alongside the JSON (only `.json` is present now): if `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.md` is absent, create it from the JSON — record token `NO_GO`, per-venue + pooled numbers, and the power statement. Do not alter the JSON. Do not fabricate a `GO`.
6. **Report closure.** Update this HANDOFF only with a new timestamped note that records the pytest summary line and gate literals observed, and states C1–C20 closed `NO_GO`. **Do not relabel this as a new campaign. Do not commit unless explicitly asked.**

**If the operator later wants a NEW research direction** (e.g., a different hypothesis or a new venue/window), that requires a **new prereg + new data** and explicit authorization — Hyperliquid moving-tail acquisition is exhausted (`research_state/hyperliquid_retention_probe_next_20261116T054408Z.json`, earliest ~2026-04-21). It is NOT something to auto-invent in this closure session.

**Terminal success for this session = full pytest green + all gates green + closure memo recorded. Until then the session has not completed its job.**

---

## NEXT FOCUS — NO-AVOIDANCE BINDING (2026-11-17T05:41:10Z)

Future agents **cannot avoid heavy work**: because the research program is complete (`NO_GO`), the only accepted progress is **closure certification** — (a) the full `pytest tests/ -q` run to the `1047 passed, 1 skipped` literal, and (b) all acceptance/hygiene gates re-verified green with their literal tokens. Reading, planning, rewriting this file, refreshing timestamps, or "monitoring" an already-exited supervisor is **not** progress.

- **No new same-data research campaign is authorized.** C1–C20 are closed `NO_GO`; re-running exhausted data is churn and is rejected.
- **Do NOT relaunch `scripts/finish_c20_detached_durable.sh`** — C20 is PASS; relaunching is a spurious rival campaign.
- **Do NOT commit** unless the operator explicitly asks.
- **If the operator authorizes a new direction:** preregister before compute (`research_state/c2x_prereg_*.{json,md}`, status `PRE_REGISTERED_BEFORE_COMPUTE`), acquire new data (Hyperliquid tail exhausted → new venue/window), and treat it as a fresh binding campaign. Until that authorization exists, the binding obligation is closure certification above.

## LIVE STATE VERIFIED (2026-11-17T05:40:55Z)

- **Host capacity:** `nproc=4`. C20 workers have exited, so all 4 cores are free; the full pytest suite is safe to run now.
- **C20:** PASS. Supervisor `research_state/.c20/supervisor_status.json` = `state: PASS`, `artifacts: 15`, `updated_at_utc: 2026-11-17T05:39:45Z`. Supervisor log final line: `[2026-11-17T05:39:45Z] C20 ACCEPTANCE: PASS (artifacts=15, attempts=1, run_rc=0)`. No live `finish_c20`/`run_c20` processes. `research_state/.c20/supervisor.lock` remains as a zero-byte stale lockfile (harmless; proc gone).
- **Artifacts:** 15/15 `research_state/*_20261116T063500Z.json` present. The 5 newest (Binance UM placebo/battery/verdict, pooled synthesis, consolidated final) are **untracked** in git (`git status --short`) — leave uncommitted unless asked.
- **Consolidated final (C1–C20):** `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json` — token `NO_GO`, `research_program_complete: true`, supersedes `..._20261116T054500Z.json` (also `NO_GO`). Pooled total PnL `-125,367.02`, bootstrap 95% CI `[-140,619.14, -110,114.9]`, `prob_pooled_total_gt_0=0.0`, go checks `6/14`, effective sample `trades=249, episodes=67, distinct_crash_days=98`.
- **Per-venue (both `NO_GO`):** OKX `trades=113, total_pnl=-55,057.45` (coin `-197,767.56`, hedge `+140,841.80`, rebound_short `-38,420.09`), episodes=31, crash_days=45, events=369. Binance UM `trades=136, total_pnl=-70,309.57` (coin `-214,779.38`, hedge `+135,812.12`, rebound_short `-38,036.67`), episodes=36, crash_days=53, events=484. Both venues strongly negative → `NO_GO` is the honest terminal.
- **Hygiene (re-verified 2026-11-17T05:40:55Z):** session gate `21/21 checks passed`, evidence `EVIDENCE VERIFIED`, C19/C13/C14/C6/C20 `ACCEPTANCE: PASS`. Full `pytest tests/ -q` deferred under C20 load; now unblocked, last known literal `1047 passed, 1 skipped`.
- **Ephemeral paths:** legacy `/tmp/*c20*` are recovery-only; durable artifacts are `research_state/*_20261116T063500Z.json` plus `research_state/.c20/`.
- **Venv:** `.venv/bin/python` is the active interpreter.

## BOTTLENECKS REMOVED / UNBLOCKED (2026-11-17T05:41:10Z)

1. **Stale in-flight state removed:** the prior handoff claimed C20 was in-flight (10/15) and told the next session to relaunch a dead supervisor. That instruction would have caused a spurious rival-campaign relaunch of an already-passed campaign, or an indefinite wait for a supervisor that exited cleanly. This handoff corrects it: **C20 PASS, do not relaunch, nothing to wait for.**
2. **Deferred heavy work unblocked:** C20 was saturating all 4 vCPUs, which is why `pytest tests/ -q` was deferred. C20 has exited; the full suite is now runnable and is the mandatory closure-certification task.
3. **No blocked/inefficient sessions to kill:** only this session runs; the C20 supervisor tree (PID 2916 + campaign 2931 + workers 3273–3276) has exited normally. No duplicate supervisors, no stale `/tmp` locks, no rival campaign.
4. **Explicit direction resolved:** the binding direction (finish C20) is fulfilled; the explicit program rule for `NO_GO` is "close C1–C20 with quantified power result; do not invent another same-data campaign." This handoff follows it and does not fabricate a new campaign.
5. **Gate consistency:** `C20 ACCEPTANCE: PASS` matches 15/15 artifacts and the consolidated final `NO_GO`; all other gates green.
6. **Carry-forward controls:** no cross-venue relabeling as Hyperliquid; no synthetic gap-fill; no spec relaxation; no commit unless asked; no rival campaign; no fabricated `GO`.

## C20 SPEC & DECISION RULES (prereg `c20_prereg_20261116T063500Z`, PRE_REGISTERED_BEFORE_COMPUTE) — COMPLETE

- Config fixed: `entry_spec_literal_next_open=true`, RSI(21)<20, target 9%, ETH hedge on, $5M volume gate, seed 20261120. **No config switching after results.**
- Required artifacts (15, all present): prereg, OKX+Binance campaigns+metrics, censuses, episode edges, placebos, robustness batteries, per-venue verdicts, `c20_pooled_cross_venue_synthesis`, `decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z`.
- GO only if pooled synthesis: episode-block bootstrap 95% CI excludes 0 with positive spot leg, permutation p<0.05, placebo p_ge_canonical<0.05, and ≥10 trades / ≥5 episodes / ≥5 crash days. Result: pooled `NO_GO` (CI spans 0, both venues negative) → honest terminal `NO_GO`.
- C20 is cross-venue (`is_hyperliquid_venue_data=false`) — **never** Hyperliquid performance evidence.

## C1–C19 CLOSED STATE (historical, do not relitigate)

- **C19 (`C19-T1`):** T1 `spec_rebound_confirmation_adjudication_20261116T054000Z` (`SPEC_LITERAL_NEXT_OPEN`); T2 native battery C18 spec-literal 22 trades, −47,933.58, 31.8% WR, max DD −52,160 (NO_GO); T3 0/7 GO criteria, max 4 episodes < 5; T4 `decision_verdict_hyperliquid_native_c19_20261116T054000Z` NO_GO (`is_hyperliquid_evidence=true`); T5 consolidated NO_GO. Gate: `scripts/verify_c19_focus_campaign.py`.
- **C14 (`20261116T001200Z`):** C14 episode edge `research_state/episode_edge_hyperliquid_ironflow_wide_20261116T001200Z.{json,md}`; native C14 underpowered/fragile (7 trades, 3 episodes, CI spans 0). Gate: `scripts/verify_c14_focus_campaign.py`.
- **C13:** config-matched native C13 artifacts complete. Gate: `scripts/verify_c13_focus_campaign.py`.
- **C6 (`C6-T1`):** cross-venue context OKX+Binance UM pooled 38 venue-episodes underpowered (CI spans 0), `campaign_results_real_okx_multiyear`, `is_hyperliquid_venue_data=false`. Gate: `scripts/verify_next_focus_campaign.py`.
- **Acquisition CLOSED/exhausted:** Hyperliquid moving tail (`full_window_served=false`, earliest ~2026-04-21; `hyperliquid_retention_probe_next_20261116T054408Z.json`).

## GUARDRAILS (never violate)

- No cross-venue relabeling as Hyperliquid-native (`is_hyperliquid_venue_data=false` for C20).
- No synthetic gap-fill as verified; no spec relaxation to manufacture GO; `SPEC_LITERAL_NEXT_OPEN` fixed.
- No inference-only churn on exhausted C14 native data; C1–C20 closed.
- **Do not relaunch `scripts/finish_c20_detached_durable.sh` — C20 is PASS.** No rival/duplicate campaign; no foreground campaign in an agent turn; no short `timeout`.
- **Do not invent a same-data C21+ campaign.** A new direction needs new prereg + new data + explicit operator authorization.
- Do not edit a completed campaign's artifacts or `scripts/run_c20_cross_venue_campaign.py` to change results; resume semantics are fixed.
- No silent change to canonical baseline. C1–C20 `NO_GO` stands.
- **Do not commit unless explicitly asked.**
- Preserve literal gate tokens: `INITIAL TASK MESSAGE`, `session_gate.py`, `21/21 checks passed`, `2026-11-13T23:38:47Z`, `probe_hyperliquid_blocker.py`, `verify_campaign_evidence.py`, `C19-T1`, `verify_c19_focus_campaign.py`, `C14`, `verify_c14_focus_campaign.py`, `20261116T001200Z`, `C6-T1`, `campaign_results_real_okx_multiyear`, `C13`, `verify_c13_focus_campaign.py`, `C20`, `verify_c20_focus_campaign.py`.

## KEY FILES

- Handover/state: `HANDOFF.md`, `README.md`, `research_state/strategy_spec.md`
- C20: `research_state/c20_prereg_20261116T063500Z.{json,md}`, `research_state/c20_pooled_cross_venue_synthesis_20261116T063500Z.json`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json`, `scripts/run_c20_cross_venue_campaign.py` (TS `20261116T063500Z`, seed `20261120`), `scripts/finish_c20_detached_durable.sh`, `scripts/verify_c20_focus_campaign.py`
- C19 ref: `research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.*`, `research_state/decision_verdict_hyperliquid_native_c19_20261116T054000Z.*`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.*`
- Gates: `scripts/session_gate.py`, `scripts/verify_campaign_evidence.py`, `scripts/probe_hyperliquid_blocker.py`, `scripts/verify_c13_focus_campaign.py`, `scripts/verify_c14_focus_campaign.py`, `scripts/verify_c19_focus_campaign.py`, `scripts/verify_c20_focus_campaign.py`, `scripts/verify_next_focus_campaign.py` (C6)
- Env: `scripts/bootstrap_env.sh` (durable default `.venv`)
- Code: `src/strategy/crash_rebound.py`, `src/strategy/config.py`, `src/backtest/engine.py`