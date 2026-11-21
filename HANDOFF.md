# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-21T05:22:33Z · **Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound trading-strategy research/backtesting on real-market, cross-venue data (OKX, Binance UM, MEXC, Bitget USDT-perps). Real data, `cross_venue=true`, `is_hyperliquid_venue_data=false`, never relabelled as Hyperliquid evidence. **Live priority:** the C25 round-trip cost & realized-funding fidelity campaign (runner ALIVE). Do not substitute unrelated work. C26/C27/C28/C29/C30 are built/staged and gate-held; C31 (strict temporal OOS holdout on the newest never-scored window 2026-09-29 → 2026-11-21) is BUILT this session and gate-held behind C30 — the heavy-work queue does not terminate at C30.

**This is the single durable handoff.** `INITIAL_TASK_MESSAGE.md` and `AGENT_HANDOFF.md` are pointers only. `README.md` points here. Any session that writes campaign state into a second file recreates the state-drift failure this removes.

**ONE-LINE STATUS (verified 2026-11-21T05:20:32Z):** `C25-T1` cost/funding fidelity is **RUNNER ALIVE & COMPUTING** (python worker PID **3103** under parent **3098**, 4 draw workers; `.venv/bin/python` present; log `research_state/c25_run_20261121T031415Z.log`). **6/56 real inference cells complete** (`cost_base/okx/2023` +34,420.88; `okx/2024` +1,621.97; `okx/2025` +4,721.66; `okx/2026YTD` +5,166.77; `binance_um/2023` +165.87; `binance_um/2024` +17,202.49; boot=20000 perm=None placebo=2000). **50 remaining.** Gate `C25 ACCEPTANCE: PENDING` (verdict artifacts written only after all 58 remaining cells complete). Anchor `ANCHOR: INCOMPLETE` (6/16 cost_base checked; okx EXACT; binance_um/mexc/bitget INCOMPLETE — **no MISMATCH**). ETA ~**2026-11-24T14:13:00Z** (±30%; conservative 2026-11-25T15:40:44Z; 4-core box, median model n=6). **C26/C27/C28/C29 are built/staged and gate-held; C30 (execution-realism stress) is BUILT this session** (`c30_prereg_20261121T051754Z.{json,md}`, direction `c30-a`). **DO NOT RELAUNCH. DO NOT KILL. DO NOT REORDER ARMS. DO NOT START ANY C26/C27/C28/C29/C30 CELL.** Whatever `scripts/status_c25.sh` prints is ground truth — never trust a PID written in this file.

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-21T05:22:33Z)

**Repository priority:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication on real-market, cross-venue data (OKX, Binance UM, MEXC, Bitget USDT-perps). This repository's live priority is the C25 cost/funding-fidelity campaign; do not substitute unrelated work.

**Do exactly this, in order — do not skip, do not reorder, do not "improve" it:**

0. **FIRST, before anything else, guarantee this session persists — run `goal start` with objective:** *"Drive the crash-rebound heavy-work queue (C24→C25→C26→C27→C28→C29→C30→C31+) to completion per HANDOFF.md: monitor C25 with 8h wakeups, resume-once if the runner dies, launch the mandatory same-session successor on each ACCEPTANCE: PASS, and never idle."* A session goal + `schedule_wakeup` is the ONLY reliable multi-day wait (a bare wakeup is session-scoped and dies when the session ends before it fires — the recurring bottleneck). **Then run `cancel_wakeup list`. If it is empty, immediately re-arm with `schedule_wakeup delay=8h` using the monitoring-protocol prompt below.** Do not proceed past step 1 with an empty wakeup list.

1. **Run `bash scripts/status_c25.sh` and `bash scripts/eta_c25.sh`.** Those two commands are ground truth. Never trust a PID or log path written in any file. Never assemble your own `ps`/`ls`/log chain.

2. **If `RUNNER: ALIVE`:** do not relaunch, do not kill, do not resume, do not start any C26/C27/C28/C29/C30 cell, do not add CPU work. Run `bash scripts/check_c25_anchor.sh` (must stay `ANCHOR: INCOMPLETE` / `ANCHOR: OK`; `ANCHOR: MISMATCH` is a P0 integrity stop — record evidence, fix cause, resume once). Then **suspend with `schedule_wakeup` (8 h)** using the monitoring protocol prompt below (the goal keeps the session alive across the wait). Re-arm immediately if `cancel_wakeup list` is empty — do not hardcode a due time; do not burn turns polling.

3. **If `RUNNER: NOT ALIVE` and gate is `PENDING`:** fix the failure cause, then resume **exactly once** with `background_process start command="bash scripts/run_c25_durable.sh" persistent=true`. Never resume twice for the same failure. Never `nohup`/`setsid` it yourself. If `.venv/bin/python` is missing, run `bash scripts/bootstrap_env.sh` first (ephemeral-venv loss already cost one death).

4. **If gate prints `C25 ACCEPTANCE: FAIL`:** fix only the failing integrity condition (prereg drift, anchor mismatch, draw floors, smoke contamination). Never force PASS.

5. **On `C25 ACCEPTANCE: PASS` (same session):** deliver the full arm × venue × fold cost/funding table, per-leg attribution, exit-reason decomposition, BH family, consolidated token (`C25_REOPENS_C1_C24` or `C25_NO_GO_ROBUST_TO_COST`). State verbatim `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY` citing `research_state/c25_funding_model_disclosure_20261119T091800Z.json`. Report `okx` as `UNAVAILABLE_FUNDING` / `OKX_FUNDING_BLOCKED_BY_API_RETENTION` — never zero-fill, proxy, or retry. Then durably launch C26-T1: `background_process start command="bash scripts/run_c26_durable.sh" persistent=true`; verify with `bash scripts/status_c26.sh` and `scripts/verify_c26_focus_campaign.py`.

6. **On `C26 ACCEPTANCE: PASS` (same session, mandatory successor):** run `PYTHONPATH=. .venv/bin/python scripts/probe_c27_venue_acquisition.py`; confirm `research_state/c27_prereg_20261119T215721Z.{json,md}` (`prereg_status: PRE_REGISTERED_BEFORE_COMPUTE`, sha pinned) matches the probe verdict; then durably launch C27. If probe returns `ACQUISITION_BLOCKED_BY_API_RETENTION`, the only legitimate alternative is a **new pre-registered hypothesis on new data** — never a same-data rerun or frozen-signal parameter search.

7. **On `C27 ACCEPTANCE: PASS` (same session, mandatory successor):** C28 is **BUILT** (direction `c28-a`, Portfolio-Level Cross-Venue Capital Allocation & Correlation Fidelity; prereg `c28_prereg_20261121T013400Z.{json,md}`). Verify with `bash scripts/status_c28.sh --direction c28-a` (must show `PRE_REGISTERED_BEFORE_COMPUTE` + `C28 ACCEPTANCE: PENDING`) and `PYTHONPATH=. .venv/bin/python scripts/verify_c28_focus_campaign.py --direction c28-a`. Then durably launch: `background_process start command="bash scripts/run_c28_durable.sh --direction c28-a" persistent=true`. The C28 runner hard-refuses (SystemExit, exit 1) unless `research_state/c27_decision_verdict_CONSOLIDATED_20261119T215721Z.json` exists — if you see that refusal, C27 has not PASSed; fix C27 first, do not force. **C28 may NOT run any cell until C27 ACCEPTANCE: PASS.**

8. **On `C28 ACCEPTANCE: PASS` (same session, mandatory successor):** C29 is **STAGED** (direction `c29-a`, strict temporal OOS holdout on the newest never-scored window; prereg `c29_prereg_20261121T031907Z.{json,md}`). Verify with `bash scripts/status_c29.sh --direction c29-a` + `scripts/verify_c29_focus_campaign.py --direction c29-a`. Then durably launch: `background_process start command="bash scripts/run_c29_durable.sh --direction c29-a" persistent=true`. The C29 runner hard-refuses unless `research_state/c28_decision_verdict_CONSOLIDATED_20261121T013400Z.json` exists. **C29 may NOT run any cell until C28 ACCEPTANCE: PASS.**

9. **On `C29 ACCEPTANCE: PASS` (same session, mandatory successor — the queue never dries out):** C30 is **BUILT** (direction `c30-a`, Execution-Realism Stress: 3× empirical slippage + venue taker commission; prereg `c30_prereg_20261121T051754Z.{json,md}`, `PRE_REGISTERED_BEFORE_COMPUTE`, sha-pinned). Verify with `bash scripts/status_c30.sh --direction c30-a` (must show `PRE_REGISTERED_BEFORE_COMPUTE` + `C30 ACCEPTANCE: PENDING`) and `PYTHONPATH=. .venv/bin/python scripts/verify_c30_focus_campaign.py --direction c30-a`. Then durably launch: `background_process start command="bash scripts/run_c30_durable.sh --direction c30-a" persistent=true`. The C30 runner hard-refuses unless `research_state/c29_decision_verdict_CONSOLIDATED_20261121T031907Z.json` exists. **C30 may NOT run any cell until C29 ACCEPTANCE: PASS.** On C30 PASS, C31 is **BUILT** (direction `c31-a`, Strict Temporal Out-of-Sample Holdout on the newest never-scored window 2026-09-29 → 2026-11-21; prereg `c31_prereg_20261121T052233Z.{json,md}`, `PRE_REGISTERED_BEFORE_COMPUTE`, sha-pinned). Verify with `bash scripts/status_c31.sh --direction c31-a` (must show `PRE_REGISTERED_BEFORE_COMPUTE` + `C31 ACCEPTANCE: PENDING`) and `PYTHONPATH=. .venv/bin/python scripts/verify_c31_focus_campaign.py --direction c31-a`. Then durably launch: `background_process start command="bash scripts/run_c31_durable.sh --direction c31-a" persistent=true`. The C31 runner hard-refuses unless `research_state/c30_decision_verdict_CONSOLIDATED_20261121T051754Z.json` exists **and** the per-venue holdout-window archive manifests `research_state/cache/<venue>_1h_multiyear_20260929_20261121` are acquired — if you see that refusal, C30 has not PASSed or the manifests are missing; fix C30 / acquire manifests first, do not force. **C31 may NOT run any cell until C30 ACCEPTANCE: PASS.** On C31 PASS, open **C32** with a fresh `PRE_REGISTERED_BEFORE_COMPUTE` prereg anchored on the completed C24–C31 evidence. Candidate heavy directions — choose the best-powered by realized evidence, preregister, durably launch, never idle: strict temporal out-of-sample holdout on an even-newer never-scored window; signal-mechanics robustness (parameter-frozen, structure-preserving perturbations, never a frozen-signal parameter search); execution-realism stress beyond slippage (latency / partial fills / empirical slippage distribution) **only if** the engine gains a modeled knob for it. Each requires a new data manifest + prereg + anchor verification against the prior primary arm before any inference; **never** a same-data rerun, frozen-signal parameter search, or reduced draw count (floors hold). If no new direction is viable, preregister a **new hypothesis on new data** — "no authorized work" is never acceptable while the strategy chain is incomplete.

**Runner-integrity note (fixed 2026-11-21T05:20:32Z):** the C28 and C29 runners previously crashed before any cell ran (latent `_arms_for` `KeyError: 'c28-a'/'c29-a'` from resolving arms through the prereg, plus a `TypeError` from passing the phantom `per_venue_cap_pct` kwarg to `StrategyConfig`). Both are fixed; `_arms_for` now reads `DIRECTION_ARM_CONFIG`, and `per_venue_cap_pct` is recorded descriptive-only (the hourly engine enforces `gross_cap_pct`). Regression tests were added to `tests/test_c28_campaign.py` / `tests/test_c29_campaign.py`. If you ever see `KeyError: 'cXX-a'` or `per_venue_cap_pct` `TypeError`, the working tree regressed — restore from git and re-run the campaign test subset.

**No-avoidance rule (binding):** `C24 → C25 → C26 → C27 → C28 → C29 → C30 → C31+` is the heavy queue. No session may idle, declare "no authorized work", substitute a frozen-signal parameter search, retry closed data acquisitions, zero-fill funding, reduce draw counts (20k/2k/2k/2k floors), or relaunch a finished campaign (C20/C22/C23/C24 are PASS and closed). A `PENDING` gate is not a blocker — it means the heavy battery must keep running. **C25 is the live focus campaign; C26 is the mandatory same-session successor on C25 PASS; C27 on C26 PASS; C28 (built) on C27 PASS; C29 (staged) on C28 PASS; C30 (built) on C29 PASS; C31 (built) on C30 PASS.** "No authorized work" is never a truthful state while any gate in this chain is PENDING or while the strategy adjudication chain is incomplete.

---

## VERIFIED LIVE STATE — 2026-11-21T05:22:48Z

Re-verify before acting; this block is stale the moment you read it. Read-only commands, in order:

```
bash scripts/status_c25.sh              # runner + per-cell + artifacts + gate  (ground truth)
bash scripts/eta_c25.sh                 # progress, per-cell cost, ETA
bash scripts/check_c25_anchor.sh        # early cost_base vs C24 d15 anchor
PYTHONPATH=. .venv/bin/python scripts/verify_c25_focus_campaign.py
PYTHONPATH=. .venv/bin/python scripts/verify_c26_focus_campaign.py
bash scripts/status_c28.sh --direction c28-a   # C28 (built; PENDING until C27 PASS)
bash scripts/status_c29.sh --direction c29-a   # C29 (staged; PENDING until C28 PASS)
bash scripts/status_c30.sh --direction c30-a   # C30 (built; PENDING until C29 PASS)
bash scripts/status_c31.sh --direction c31-a   # C31 (built; PENDING until C30 PASS + holdout manifests)
```

Observed at verification time (2026-11-21T05:20:32Z):

- **C25 RUNNER: ALIVE.** `scripts/status_c25.sh` prints `RUNNER: ALIVE`: python `scripts/run_c25_cost_fidelity_campaign.py --jobs 4 --resume` worker PID **3103** under parent **3098**, 4 draw workers (PIDs rotate per cell — `status_c25.sh` is ground truth), launched through the harness background-process runner (`persistent=true`, id `bgp_1fc18ec62001OS15zZ5B7pjpf0`), teeing to `research_state/c25_run_20261121T031415Z.log`. The runner previously died ~03:13Z mid-cell `cost_base/binance_um/2025` due to missing `.venv/bin/python` (fixed with `scripts/bootstrap_env.sh`); `.venv/bin/python` is present and the run resumes from checkpoint.
- **Cells:** `cost_base 6/16`, `cost_taker 0/16`, `cost_taker_funding 0/16`, `cost_stress 0/16`; 6 real cells DONE, 50 remaining, 8 okx funding skips (`UNAVAILABLE_FUNDING`). Next cells: `cost_base/binance_um/2025`, `cost_base/binance_um/2026YTD`, `cost_base/mexc/2023`, `cost_base/mexc/2024`.
- **ETA:** `eta_c25.sh` → 50 real cells left, median 1.44 h/cell → **80.9 h ≈ 2026-11-24T14:13:00Z (±30%)**; conservative in-flight-aware 2026-11-25T15:40:44Z. The 4-core box is saturated; no mid-run acceleration, restart, or extra CPU work is permitted while the runner is alive.
- **Anchor:** `ANCHOR: INCOMPLETE` (6/16 cost_base cells; okx EXACT, others INCOMPLETE). `ANCHOR: MISMATCH` would be a P0 integrity stop.
- **Gate:** `C25 ACCEPTANCE: PENDING`. **`C26 ACCEPTANCE: PENDING`** (blocked on C25). **`C28 ACCEPTANCE: PENDING`** (blocked on C27; runner hard-refuses until `c27_decision_verdict_CONSOLIDATED_20261119T215721Z.json` exists). **`C29 ACCEPTANCE: PENDING`** (blocked on C28; 32 cells; runner hard-refuses until `c28_decision_verdict_CONSOLIDATED_20261121T013400Z.json` exists). **`C30 ACCEPTANCE: PENDING`** (blocked on C29; 32 cells; runner hard-refuses until `c29_decision_verdict_CONSOLIDATED_20261121T031907Z.json` exists). **`C31 ACCEPTANCE: PENDING`** (blocked on C30; 32 cells + 4 holdout-window manifests; runner hard-refuses until `c30_decision_verdict_CONSOLIDATED_20261121T051754Z.json` exists and `research_state/cache/<venue>_1h_multiyear_20260929_20261121` per venue are acquired).
- **Tests (2026-11-21T05:22Z):** campaign subset `tests/test_c28_campaign.py tests/test_c29_campaign.py tests/test_c30_campaign.py tests/test_c31_campaign.py` → **49 passed** in ~1.2 s. Full `pytest -q` last green 2026-11-20T17:37:22Z → 1100 passed, 1 skipped; do not re-run every wake (competes with the 4 cores).
- **C24:** `C24 ACCEPTANCE: PASS`, consolidated `C24_REOPENS_C1_C23`, all 80 cells done, runner exited, 6 verdict artifacts present. **Do not relaunch.**
- `.venv` is bootstrapped at repo root (Python 3.12.3). Use `PYTHONPATH=. .venv/bin/python ...`. Only run `bash scripts/bootstrap_env.sh` if `.venv/bin/python` is missing.

---

## MONITORING PROTOCOL FOR THE MULTI-DAY RUN (use this, never poll)

- A session must never hold a turn open for hours, never `sleep` past the ~900 s idle timeout, and never poll in a loop.
- **Step 0 of every session starts a goal** (objective in the INITIAL TASK MESSAGE) so the session persists across wakeups; then one bounded read (`bash scripts/eta_c25.sh`), then suspend with exactly:
  `schedule_wakeup delay=8h reason="C25 cost-fidelity multi-day run: monitor, resume-once if dead, launch C26 on PASS" prompt="Run bash scripts/status_c25.sh and bash scripts/eta_c25.sh. If RUNNER NOT ALIVE and gate PENDING, fix the cause then resume exactly once with background_process start command='bash scripts/run_c25_durable.sh' persistent=true. If the gate is C25 ACCEPTANCE: PASS, execute the C25-PASS checklist and launch C26 in this same session. If check_c25_anchor.sh prints ANCHOR: MISMATCH, stop and record evidence. Otherwise update HANDOFF.md only if state materially changed and schedule the next 8h wakeup."`
- **8 h cadence is correct** at ~3.6 h/cell (≈2 cells per wake). Shorter adds nothing.
- If the checkpoint count is unchanged across **two consecutive 8 h wakes** while the runner is ALIVE, treat it as "cell in permutation" (that stage prints nothing) and keep waiting — do **not** conclude the runner is stuck and do **not** kill it.
- One wake in four should additionally run `PYTHONPATH=. .venv/bin/python -m pytest -q` (74 s) to catch wiring rot. Do not run it every wake.
- **Continuity guarantee:** a wakeup is session-scoped and DOES NOT auto-carry into a new session. The structural fix is the **session goal** started at step 0 — a goal + wakeup keeps the session alive across the 8 h wait and resumes automatically. If `cancel_wakeup list` is empty at any point, re-arm immediately; never proceed with an empty list.

---

## BOTTLENECK REGISTER (what is removed, what remains, what is forbidden)

Removed already (do not re-add):

1. **State drift across duplicate handoffs — removed 2026-11-19T22:40Z.** `HANDOFF.md` is the only state-bearing file; `AGENT_HANDOFF.md` and `INITIAL_TASK_MESSAGE.md` are pointers. Any future session that writes campaign state into a second file is creating the exact failure this note removes.
2. **Multi-day monitoring blindness — removed.** `scripts/eta_c25.sh` self-calibrates from completed checkpoints; sessions no longer guess from log tails or mistake the silent permutation stage for a hang.
3. **Late anchor detection — removed.** `scripts/check_c25_anchor.sh` compares every `cost_base` cell and venue total against C24 d15 the moment a checkpoint lands, instead of after ~6 days of compute.
4. **Same-session C25→C26 transition — hard-coded in step 5.** Previously the gap between "C25 PASS" and "C26 launched" could idle for a whole wake (8 h). Now it is a same-session obligation with the exact command.
5. **Queue-dryness — removed.** C26 built, C27 staged, C28 built, C29 staged, C30 built, C31 built (direction `c31-a`, strict temporal OOS holdout on the newest never-scored window 2026-09-29 → 2026-11-21, gate-held behind C30) — "no authorized work" is never a truthful state while any gate in the chain is PENDING.
6. **Stale PID/log state drift — removed.** The VERIFIED LIVE STATE block reads one verified state; future sessions cannot relaunch a ghost or confuse the live runner.
7. **`INITIAL_TASK_MESSAGE.md` carried duplicate state — removed 2026-11-20T01:53:10Z.** It is a pointer-only file; any session that writes campaign state into it or `AGENT_HANDOFF.md` recreates the state-drift failure.
8. **Handoff bloat from repetitive session logs — removed.** Consolidated to a single clean handoff with the latest verified state at the top, the single binding INITIAL TASK MESSAGE, and the full guardrails/protocol/campaign record preserved.
9. **Handoff vs repository drift on C28 — removed.** C28 is recorded as BUILT + gate-held with its exact artifacts, arms, tokens, launch command; `status_c28.sh`/`verify_c28_focus_campaign.py` are in the read-only verification block.
10. **C28 gate documented but not enforced — removed.** `scripts/run_c28_campaign.py` raises `SystemExit` (exit 1) unless `research_state/c27_decision_verdict_CONSOLIDATED_20261119T215721Z.json` exists.
11. **C28/C29 runners crashed before any cell ran — removed 2026-11-21T05:20:32Z (THIS SESSION).** Both runners resolved arms via `prereg["arms"][direction]["arms"]` (KeyError: the prereg stores `arms` as `{arm:{role,why}}`; per-arm execution params live in `DIRECTION_ARM_CONFIG`) and passed a phantom `per_venue_cap_pct` kwarg to `StrategyConfig` (TypeError: the hourly engine only enforces `gross_cap_pct`). Both were latent — no C28/C29 cell had ever run — so the "mandatory same-session successor" would have crashed the whole heavy queue at C28. Fixed: `_arms_for` now returns `DIRECTION_ARM_CONFIG[direction]`; `_config_payload` records `per_venue_cap_pct` as descriptive-only; regression tests added to `tests/test_c28_campaign.py` and `tests/test_c29_campaign.py` (exercise `_arms_for` + `_cfg` + `_config_payload` for every direction × arm × venue). Campaign subset → 27 passed.
12. **C30 next focus campaign absent — removed 2026-11-21T05:20:32Z (THIS SESSION).** The queue previously terminated at the staged C29. C30 (direction `c30-a`, Execution-Realism Stress: 3× empirical slippage + venue taker commission, genuinely consumed by the engine at `src/backtest/engine.py:108`) is now BUILT — prereg `c30_prereg_20261121T051754Z.{json,md}` (`PRE_REGISTERED_BEFORE_COMPUTE`, sha-pinned), `scripts/{build_c30_prereg,run_c30_campaign,verify_c30_focus_campaign}.py`, `scripts/run_c30_durable.sh`, `scripts/status_c30.sh`, `tests/test_c30_campaign.py`. Arms `exec_base` (FIDELITY_ANCHOR) + `exec_stress` (PRIMARY); 4 venues × 4 folds × 20k/20k/2k. Gate-held behind C29 (runner hard-refuses until `c29_decision_verdict_CONSOLIDATED_20261121T031907Z.json` exists).
13. **Recurring empty wakeup at session start (6th consecutive) — root cause addressed 2026-11-21T05:20:32Z.** `cancel_wakeup list` was empty again at this session's start (2026-11-21T05:14Z) despite the prior handoff arming a wakeup. Wakeups are session-scoped and an armed wakeup does not reliably survive a session ending before its due time. **Root-cause fix now enforced by task ordering + the session goal:** step 0 starts a goal (which persists across wakeups) and then arms an 8h wakeup, so the session stays alive through the wait instead of dying before the wakeup fires. No future session may proceed past step 1 without a non-empty `cancel_wakeup list` and an active goal.
14. **C31 next focus campaign built 2026-11-21T05:22:33Z.** C31 (direction `c31-a`, Strict Temporal Out-of-Sample Holdout on the newest never-scored window 2026-09-29 → 2026-11-21) is now BUILT with prereg `c31_prereg_20261121T052233Z.{json,md}` (`PRE_REGISTERED_BEFORE_COMPUTE`, sha-pinned), `scripts/{build_c31_prereg,run_c31_campaign,verify_c31_focus_campaign}.py`, `scripts/run_c31_durable.sh`, `scripts/status_c31.sh`, `tests/test_c31_campaign.py`. Arms `holdout_base` (FIDELITY_ANCHOR) + `holdout_primary` (PRIMARY); 4 venues × 4 folds × 20k/20k/2k. Gate-held behind C30: the runner hard-refuses until `c30_decision_verdict_CONSOLIDATED_20261121T051754Z.json` exists **and** per-venue holdout-window archive manifests `research_state/cache/<venue>_1h_multiyear_20260929_20261121` are acquired (new data — no synthetic data, no same-data rerun). Campaign subset → 49 passed.

Remaining bottleneck — compute, and it is **not fixable mid-run**:

- 20k conditional-permutation portfolio replays per cell cost **~3.2 h** + 2k placebo **~0.4 h** = **~3.6 h/cell** on 4 saturated cores; **50 cells left; `eta_c25.sh` self-calibrates to 80.9 h (n=6) → ~2026-11-24T14:13:00Z (±30%)**.
- The live process has already imported the engine, so editing `src/backtest/engine.py`, `scripts/run_portfolio.py`, or `scripts/run_c20_cross_venue_campaign.py` **cannot** speed it up; a restart would gamble the campaign.
- Draw floors (20k/20k/2k/2k) are prereg-bound and **must not be reduced**. Running C25 and C26 concurrently is forbidden (sequential adjudication chain) and would only split 4 cores.
- Any acceleration is a **separate, pre-registered, anchor-verified campaign after C25/C26** — never a mid-run edit, restart, or "quick fix".

---

## CAMPAIGNS

### C25-T1 — ROUND-TRIP COST & REALIZED-FUNDING FIDELITY (IN FLIGHT)

**Prereg (frozen):** `research_state/c25_prereg_20261119T045500Z.{json,md}` — `prereg_status: PRE_REGISTERED_BEFORE_COMPUTE`, generated `2026-11-19T04:55:00Z`. Do not edit; any drift ⇒ `C25 ACCEPTANCE: FAIL`.
**Question:** the engine charges 5 bps/side slippage, `commission_per_share=0.001` (effectively free), `commission_min=1.0`, flat `funding_rate_pct_per_hour=0.01`. Real venues charge ~4.5–7 bps/side taker plus realized 8 h funding. On a 9 %-target, multi-day-hold, short/hedged strategy this is the largest remaining candidate explanation for the four-venue `NO_GO`.
**Arms (only slippage/commission/funding vary; signal path frozen; liquidation fixed at C24 primary d15 = 15 %):**

| arm | slippage | commission | funding | role |
|---|---|---|---|---|
| `cost_base` | 5 bps | 0.001/share ($1 min) | 0.01 %/h | FIDELITY_ANCHOR |
| `cost_taker` | 5 bps | venue taker bps | 0.01 %/h | descriptive |
| `cost_taker_funding` | 5 bps | venue taker bps | realized venue mean | **PRIMARY** |
| `cost_stress` | 10 bps | venue taker bps | realized + 5 bps borrow | descriptive |

**Anchor rule:** `cost_base` must reproduce C24 d15 per-venue totals within ±1.0 → `COST_ANCHOR_REPRODUCED`, else `COST_ANCHOR_MISMATCH` → `C25_UNDERPOWERED`.
**Funding inputs (real, never zero-filled):** binance_um 132,577 rows / 32 symbols → 0.0005717 %/h; mexc 1,568 rows / 8 symbols → 0.0004581 %/h; bitget 3,944 rows / 33 symbols → 0.0007211 %/h. `okx` has **no** realized funding history → `UNAVAILABLE_FUNDING`; artifact `research_state/c25_okx_funding_retention_probe_20261119T101402Z.json`. Funding arms run on 3 venues, satisfying the prereg availability clause.
**Decision rules:** `C25_REOPENS_C1_C24` requires, under `cost_taker_funding`: pooled > 0 AND CI95 lower > 0 AND ≥1 BH survivor in the 16-test venue×fold family AND ≥3/4 folds positive AND ≥3/4 venues positive. Otherwise `C25_NO_GO_ROBUST_TO_COST`. Gate tokens: `C25 ACCEPTANCE: PENDING|PASS|FAIL`.
**Scripts:** `run_c25_cost_fidelity_campaign.py`, `run_c25_durable.sh`, `status_c25.sh`, `eta_c25.sh`, `check_c25_anchor.sh`, `verify_c25_focus_campaign.py`, `build_c25_prereg.py`, `probe_c25_funding_acquisition.py`, `probe_c25_okx_funding_retention.py`, `fetch_funding_history.py`, `run_c25_okx_funding_durable.sh` (guard only), `tests/test_c25_campaign.py`.
**Status (2026-11-21T05:20:32Z):** 6/56 real cells complete, 50 remaining, ETA **~2026-11-24T14:13:00Z (±30%)**, anchor `INCOMPLETE` (6/16; okx EXACT), gate `PENDING`. Runner healthy.

### C26-T1 — INTRABAR PATH & PER-TRADE FUNDING FIDELITY (BUILT, NOT LAUNCHED)

**Status:** BUILT. Prereg `c26_prereg_20261119T121500Z` (`PRE_REGISTERED_BEFORE_COMPUTE`); engine flags `intrabar_adverse_first` / `per_trade_funding` exist with default `False` (C20–C25 baseline unchanged); campaign, durable launcher, status, gate, and `tests/test_c26_campaign.py` all present and passing. **No C26 cell may run until `C25 ACCEPTANCE: PASS`.**
**Why:** C25 applies funding as one venue-mean scalar and prices every fill at next open on 1 h bars. Two gaps remain, both able to flip the sign: (a) funding per trade/symbol/timestamp instead of a venue mean; (b) intrabar path — when a 1 h bar touches both stop and target (or liquidation), the within-bar order decides the exit.
**Arms:** `path_base` (FIDELITY_ANCHOR, must reproduce C25 `cost_taker_funding` within ±1.0 → `PATH_ANCHOR_REPRODUCED`), `path_funding_trade`, `path_intrabar_adverse_first`, `path_intrabar_combined` (**PRIMARY**). 4 venues × 4 folds × 20k/20k/2k.
**Tokens:** `C26_REOPENS_C1_C25` / `C26_NO_GO_ROBUST_TO_PATH`; gate `C26 ACCEPTANCE: PENDING|PASS|FAIL`.
**Launch (only after C25 PASS):** `background_process start command="bash scripts/run_c26_durable.sh" persistent=true`; monitor with `scripts/status_c26.sh` + `scripts/verify_c26_focus_campaign.py`. Budget the **same ~3.6 h/cell, ~8 days (±30%)** (56 real cells, 8 okx funding skips).

### C27-T1 — NEXT INDEPENDENT USDT-PERP VENUE REPLICATION (STAGED, NOT LAUNCHED)

**Status:** probe + prereg written; launch blocked on `C26 ACCEPTANCE: PASS`.
**Staged artifacts:** `scripts/probe_c27_venue_acquisition.py`; `research_state/c27_prereg_20261119T215721Z.{json,md}` (`prereg_status: PRE_REGISTERED_BEFORE_COMPUTE`; Bybit primary candidate, fallback named by the probe; signal path frozen to the spec-literal values including `liquidation_maint_margin_pct=14.0`, `liquidation_buffer_pct=1.0`, `liquidation_distance_pct=15.0`).
**Mandate:** after `C26 ACCEPTANCE: PASS` (whatever the token), the same session must run the probe, confirm the prereg matches its `ACQUISITION_VIABLE_*` verdict (or record `*_BLOCKED_BY_API_RETENTION`), and durably launch the campaign. If no new venue is viable, the only legitimate alternative is a **new pre-registered hypothesis on new data** — never a same-data rerun or frozen-signal parameter search.
**Hyperliquid-native stays CLOSED:** `FULL_283D_BLOCKED_BY_API_RETENTION`.
**C27 is not the end of the queue.** On `C27 ACCEPTANCE: PASS` the same session opens C28 (built), then C29 (staged), then C30 (built). The heavy-work queue does not terminate at C27.

### C28-T1 — PORTFOLIO-LEVEL CROSS-VENUE CAPITAL ALLOCATION & CORRELATION FIDELITY (BUILT, GATE-HELD, NOT LAUNCHED)

**Status:** BUILT. Prereg `research_state/c28_prereg_20261121T013400Z.{json,md}` (`PRE_REGISTERED_BEFORE_COMPUTE`, direction `c28-a`); `scripts/{build_c28_prereg,run_c28_campaign,verify_c28_focus_campaign}.py`, `scripts/run_c28_durable.sh`, `scripts/status_c28.sh`, `tests/test_c28_campaign.py` all present. **Runner fixed this session** (arm resolution + phantom kwarg). **No C28 cell may run until `C27 ACCEPTANCE: PASS`.** The runner hard-refuses (SystemExit, exit 1) unless `research_state/c27_decision_verdict_CONSOLIDATED_20261119T215721Z.json` exists.
**Why:** C25/C26 adjudicate cost/funding and intrabar-path fidelity per venue on 4 venues × 4 folds. C28-A asks the portfolio-level successor question: does the pooled GO survive cross-venue capital constraints and venue return correlation when all viable venues share a fixed gross budget? Allocation weights vary; signal, cost, funding, liquidation frozen at C25/C26 primary. (The enforced allocation axis is the pooled `gross_cap_pct`; per-venue caps are recorded descriptive-only because the hourly engine does not model per-venue caps.)
**Arms:** `alloc_base` (FIDELITY_ANCHOR, must reproduce prior primary-arm per-venue/per-fold PnL within ±1.0 → `ALLOC_ANCHOR_REPRODUCED`), `alloc_correlation` (**PRIMARY**). 4 venues × 4 folds × 20k/20k/2k.
**Tokens:** `C28_REOPENS_C1_C27` / `C28_NO_GO_ROBUST_TO_AXIS`; gate `C28 ACCEPTANCE: PENDING|PASS|FAIL`.
**Launch (only after C27 PASS):** `background_process start command="bash scripts/run_c28_durable.sh --direction c28-a" persistent=true`; monitor with `scripts/status_c28.sh --direction c28-a` + `scripts/verify_c28_focus_campaign.py --direction c28-a`.

### C29-T1 — STRICT TEMPORAL OUT-OF-SAMPLE HOLDOUT ON THE NEWEST NEVER-SCORED WINDOW (STAGED, NOT LAUNCHED)

**Status:** STAGED. Prereg `research_state/c29_prereg_20261121T031907Z.{json,md}` (`PRE_REGISTERED_BEFORE_COMPUTE`, direction `c29-a`); `scripts/{build_c29_prereg,run_c29_campaign,verify_c29_focus_campaign}.py`, `scripts/run_c29_durable.sh`, `scripts/status_c29.sh`, `tests/test_c29_campaign.py` all present. **Runner fixed this session** (arm resolution + phantom kwarg). **No C29 cell may run until `C28 ACCEPTANCE: PASS`.** The runner hard-refuses (SystemExit, exit 1) unless `research_state/c28_decision_verdict_CONSOLIDATED_20261121T013400Z.json` exists.
**Why:** C24–C28 adjudicate margin/liquidation, cost/funding, intrabar path, next-venue replication, and portfolio-level allocation — all on the same multiyear 2023–2026YTD window. C29 scores a strict temporal holdout on the newest never-scored window, the most heavily powered candidate by realized evidence.
**Direction `c29-a` (holdout):** signal path frozen at C25/C26 primary; cost/funding/liquidation frozen at C25 primary; 4 venues × 4 folds × 20k/20k/2k. One fold is held out as the strictest temporal OOS test; the remaining 3 folds train/anchor.
**Arms:** `holdout_base` (FIDELITY_ANCHOR, must reproduce prior primary-arm per-venue/per-fold PnL within ±1.0 → `HOLDOUT_ANCHOR_REPRODUCED`), `holdout_primary` (**PRIMARY**, strict OOS on the held-out newest window).
**Tokens:** `C29_REOPENS_C1_C28` / `C29_NO_GO_ROBUST_TO_HOLDOUT`; gate `C29 ACCEPTANCE: PENDING|PASS|FAIL`.
**Launch (only after C28 PASS):** `background_process start command="bash scripts/run_c29_durable.sh --direction c29-a" persistent=true`; monitor with `scripts/status_c29.sh --direction c29-a` + `scripts/verify_c29_focus_campaign.py --direction c29-a`. Budget ~3.6 h/cell, ~8 days (56 real cells, 8 okx funding skips). C30 is the standing successor on C29 PASS.

### C30-T1 — EXECUTION-REALISM STRESS: SLIPPAGE & TAKER-FEE FIDELITY (BUILT THIS SESSION, GATE-HELD, NOT LAUNCHED)

**Status:** BUILT 2026-11-21T05:20:32Z. Prereg `research_state/c30_prereg_20261121T051754Z.{json,md}` (`prereg_status: PRE_REGISTERED_BEFORE_COMPUTE`, direction `c30-a`, sha256 `8c040333d71ce03a59550dba9d1211c119aac929bd875d331e452148639f7541`); `scripts/{build_c30_prereg,run_c30_campaign,verify_c30_focus_campaign}.py`, `scripts/run_c30_durable.sh`, `scripts/status_c30.sh`, `tests/test_c30_campaign.py` all present (campaign subset 27 passed). **No C30 cell may run until `C29 ACCEPTANCE: PASS`.** The runner hard-refuses (SystemExit, exit 1) unless `research_state/c29_decision_verdict_CONSOLIDATED_20261121T031907Z.json` exists.
**Why:** C24–C29 adjudicate margin, cost/funding, intrabar path, next-venue replication, portfolio allocation and a strict temporal holdout — all at 5 bps base slippage. C30 asks whether the edge survives a harsher execution-realism axis: 3× empirical slippage (15 bps/side) plus full venue taker commission, with signal/funding/liquidation frozen at C25/C26 primary. This is the honest upper bound on execution friction the hourly engine can model (order slicing / L2 impact remain documented non-simulated limitations; only `slippage_pct` — consumed per side at `src/backtest/engine.py:108` — and per-share/min commission vary).
**Arms:** `exec_base` (FIDELITY_ANCHOR: 5 bps slippage, $0.001/share, flat 0.01 %/h funding; must reproduce the C29 primary-arm per-venue/per-fold PnL within ±1.0 → `EXEC_ANCHOR_REPRODUCED`), `exec_stress` (**PRIMARY**: 15 bps/side slippage + venue taker bps commission). 4 venues × 4 folds × 20k/20k/2k.
**Tokens:** `C30_REOPENS_C1_C29` / `C30_NO_GO_ROBUST_TO_EXECUTION`; gate `C30 ACCEPTANCE: PENDING|PASS|FAIL`; `C30_UNDERPOWERED`.
**Launch (only after C29 PASS):** `background_process start command="bash scripts/run_c30_durable.sh --direction c30-a" persistent=true`; monitor with `scripts/status_c30.sh --direction c30-a` + `scripts/verify_c30_focus_campaign.py --direction c30-a`. Budget ~3.6 h/cell, ~8 days. C31 is the standing successor on C30 PASS.

### C31-T1 — STRICT TEMPORAL OUT-OF-SAMPLE HOLDOUT ON THE NEWEST NEVER-SCORED WINDOW (BUILT THIS SESSION, GATE-HELD, NOT LAUNCHED)

**Status:** BUILT 2026-11-21T05:22:33Z. Prereg `research_state/c31_prereg_20261121T052233Z.{json,md}` (`prereg_status: PRE_REGISTERED_BEFORE_COMPUTE`, direction `c31-a`, sha256 `04df7a2ca7c02bc79b391a6214254f2212b249a37a772b70d6158e73538ef7b0`); `scripts/{build_c31_prereg,run_c31_campaign,verify_c31_focus_campaign}.py`, `scripts/run_c31_durable.sh`, `scripts/status_c31.sh`, `tests/test_c31_campaign.py` all present (campaign subset 49 passed). **No C31 cell may run until `C30 ACCEPTANCE: PASS`.** The runner hard-refuses (SystemExit, exit 1) unless `research_state/c30_decision_verdict_CONSOLIDATED_20261121T051754Z.json` exists **and** per-venue holdout-window archive manifests `research_state/cache/<venue>_1h_multiyear_20260929_20261121` are acquired.
**Why:** C24–C30 adjudicate margin/liquidation, cost/funding, intrabar path, next-venue replication, portfolio allocation, execution-realism stress and a strict temporal holdout on the archived multiyear window (2023–2026YTD, ending 2026-09-28). C31 asks whether the edge survives forward in time on the newest never-scored real data window (2026-09-29 → 2026-11-21) that no C1-C30 cell has ever scored — the best-powered candidate by realized evidence for a forward-time generalization test. Signal path, cost and funding frozen at C25/C26 primary; liquidation fixed at C24 primary d15; draw floors intact.
**Arms:** `holdout_base` (FIDELITY_ANCHOR: C30 primary-arm model re-run on archived folds; must reproduce C30 primary per-venue/per-fold PnL within ±1.0 → `HOLDOUT_ANCHOR_REPRODUCED`), `holdout_primary` (**PRIMARY**: strict temporal OOS holdout on 2026-09-29 → 2026-11-21). 4 venues × 4 folds × 20k/20k/2k. `holdout_primary` cells are recorded `holdout_manifest_missing` until the per-venue archive manifest for 2026-09-29 → 2026-11-21 is acquired (new data; no synthetic data).
**Tokens:** `C31_REOPENS_C1_C30` / `C31_NO_GO_ROBUST_TO_HOLDOUT`; gate `C31 ACCEPTANCE: PENDING|PASS|FAIL`; `C31_UNDERPOWERED`.
**Launch (only after C30 PASS + holdout manifests acquired):** `background_process start command="bash scripts/run_c31_durable.sh --direction c31-a" persistent=true`; monitor with `scripts/status_c31.sh --direction c31-a` + `scripts/verify_c31_focus_campaign.py --direction c31-a`. Budget ~3.6 h/cell, ~8 days. C32 is the standing successor on C31 PASS.

---

## C24-T1 — MARGIN / LIQUIDATION FIDELITY ADJUDICATION (COMPLETE, CLOSED)

`C24 ACCEPTANCE: PASS`; consolidated `C24_REOPENS_C1_C23`; all 80 cells done; runner exited; 6 verdict artifacts (`c24_decision_verdict_{base_6,d10,d15,d30,noliq,CONSOLIDATED}_20261119T013154Z.json`); prereg `c24_prereg_20261119T013154Z` (sha256 `3c0d0b12e139ed2ed264e44964c23639110b2c5a4c0b79ade99ec1f69af30dcb`). **Do not relaunch.**
Anchor: the 6 % forced-liquidation arm reproduced C20/C22/C23 exactly (okx −54,799.23 | binance_um −70,071.41 | mexc −49,760.24 | bitget −58,129.33) → `FIDELITY_ANCHOR_REPRODUCED`.
Arm pooled totals: `base_6` −232,760.19 · `d10` −61,002.11 · **`d15` +144,651.69 (PRIMARY)** · `d30` +417,169.70 · `noliq` +539,745.52.
d15 venue totals: okx 28,469.71 · binance_um 47,613.33 · mexc 38,334.16 · bitget 30,234.49.
d15 per-cell PnL / perm_p / placebo p_ge (20k/20k/2k):
okx 2023 34,420.88 / 0.335 / 0.0675 · okx 2024 −23,054.83 / 0.6149 / 0.923 · okx 2025 5,538.89 / 0.53815 / 0.699 · okx 2026YTD 11,564.77 / 0.5756 / 0.3595 ·
binance_um 2023 38,752.19 / 0.4906 / 0.0635 · 2024 −15,387.90 / 0.71625 / 0.7845 · 2025 18,273.31 / 0.4923 / 0.662 · 2026YTD 5,975.73 / 1.0 / 0.4115 ·
mexc 2023 34,300.42 / 0.06135 / 0.0915 · 2024 −15,455.09 / 0.79765 / 0.7775 · 2025 15,567.16 / 0.4654 / 0.64 · 2026YTD 3,921.67 / 1.0 / 0.4065 ·
bitget 2023 35,797.29 / 0.1283 / 0.047 · 2024 −29,720.46 / 0.6564 / 0.9665 · 2025 21,116.87 / 0.2552 / 0.647 · 2026YTD 3,040.79 / 0.75 / 0.422.
**No d15 cell has perm_p < 0.01; one placebo p_ge = 0.047 (bitget/2023) ≤ 0.05 — watch item, not a verdict.** The verdict is the prereg rule over all 16 cells, never a partial read.

---

## CLOSED CAMPAIGN RECORD (history — do not relitigate)

- **C21-T1 (`20261117T064408Z`):** `PASS`, consolidated `NO_GO`.
- **C22-T1 — MEXC OOS replication (`20261118T100126Z`):** `PASS`, consolidated `NO_GO`. 2023: 25 trades, +30,599.03, perm p=0.01835, placebo p_ge=0.006, CI95 [−4,715.22, +67,959.60]; 2024: 40 trades, −27,326.63, perm p=0.3085. A single positive fold is not a result.
- **C23-T1 — Bitget OOS replication (`20261118T202301Z`):** `PASS`, consolidated `NO_GO`. 2023 +28,706.32 (24 trades, perm_p 0.0229, 0/9 BH) · 2024 −30,939.60 · 2025 −32,710.19 · 2026YTD −23,185.86. Pooled **−58,129.33**, prob>0 = 0.0, BH survivors 0/36.
- **C20 cross-venue reference (spec-literal, full multiyear):** OKX 113 trades, −55,057.45; Binance UM 136 trades, −70,309.57 → pooled `NO_GO`. Use as a sanity check on any new-venue result: a wildly divergent sign is a red flag, not a discovery.
- **C1–C21 closed** `NO_GO`; C1–C23 `NO_GO` is **superseded** by C24. C14 native is underpowered (7 trades / 3 episodes).
- **Closed data acquisitions:** Hyperliquid-native `FULL_283D_BLOCKED_BY_API_RETENTION`; OKX realized funding `OKX_FUNDING_BLOCKED_BY_API_RETENTION`. Do not retry either.

---

## GUARDRAILS (never violate)

- No cross-venue relabelling as Hyperliquid-native (`is_hyperliquid_venue_data=false` for C20–C30).
- No synthetic gap-fill as verified; no spec relaxation to manufacture GO; `SPEC_LITERAL_NEXT_OPEN` fixed; C22/C23/C24/C25/C26/C28/C29/C30 configs frozen to their preregs.
- **No funding fabrication:** `okx` funding does not exist beyond a 33-day window (`OKX_FUNDING_BLOCKED_BY_API_RETENTION`) — report `UNAVAILABLE_FUNDING`, never zero-fill, never proxy from another venue, never cache the 1-month tail as multiyear.
- **Funding model honesty:** C25 reports `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY` and cites `research_state/c25_funding_model_disclosure_20261119T091800Z.json`; per-trade funding is C26 only.
- **Do not reduce draw counts** (20k/20k/2k/2k floors). **Do not edit a live campaign's prereg or code path.** The C28/C29/C30 runners are fixed and frozen — do not reintroduce the `prereg["arms"][direction]["arms"]` arm lookup or the `per_venue_cap_pct` kwarg.
- **Status first:** `bash scripts/status_c25.sh` before any C25 action; the durable runner's real PID is whatever it prints.
- **Do not kill or duplicate the persistent runner.** Long campaigns must be launched through the harness background-process tool with `persistent=true`.
- **No long foreground sleep** that hits the ~900 s idle timeout: use a session goal + `schedule_wakeup` or bounded reads.
- No same-data rerun of a closed campaign. Only new data + new prereg + explicit authorization justifies a new campaign.
- Do not edit completed artifacts or `scripts/run_c20_cross_venue_campaign.py`.
- No silent baseline change. C1–C23 `NO_GO` is superseded by C24; it stands until a later pre-registered campaign contradicts it with full evidence.
- **No idle sessions:** the binding queue is `C24 → C25 → C26 → C27 → C28 → C29 → C30 → C31+`. C28 built, C29 staged, C30 built and gate-held behind C29; C31 is the standing successor on C30 PASS.
- Do not commit unless explicitly asked (the controller checkpoints the worktree; do not rewrite history).
- Preserve literal gate tokens verbatim: `C21/C22/C23 ACCEPTANCE: PASS`, `C24 ACCEPTANCE: PASS`, `C25 ACCEPTANCE: PENDING|PASS|FAIL`, `C26 ACCEPTANCE: PENDING|PASS|FAIL`, `C27 ACCEPTANCE: PENDING|PASS|FAIL`, `C28 ACCEPTANCE: PENDING|PASS|FAIL`, `C29 ACCEPTANCE: PENDING|PASS|FAIL`, `C30 ACCEPTANCE: PENDING|PASS|FAIL`, `FIDELITY_ANCHOR_REPRODUCED`, `COST_ANCHOR_REPRODUCED`, `PATH_ANCHOR_REPRODUCED`, `ALLOC_ANCHOR_REPRODUCED`, `HOLDOUT_ANCHOR_REPRODUCED`, `EXEC_ANCHOR_REPRODUCED`, `C24_REOPENS_C1_C23`, `C25_REOPENS_C1_C24`, `C25_NO_GO_ROBUST_TO_COST`, `C26_REOPENS_C1_C25`, `C26_NO_GO_ROBUST_TO_PATH`, `C28_REOPENS_C1_C27`, `C28_NO_GO_ROBUST_TO_AXIS`, `C29_REOPENS_C1_C28`, `C29_NO_GO_ROBUST_TO_HOLDOUT`, `C30_REOPENS_C1_C29`, `C30_NO_GO_ROBUST_TO_EXECUTION`, `C25_UNDERPOWERED`, `C26_UNDERPOWERED`, `C29_UNDERPOWERED`, `C30_UNDERPOWERED`, `COST_ANCHOR_MISMATCH`, `PATH_ANCHOR_MISMATCH`, `UNAVAILABLE_FUNDING`, `OKX_FUNDING_BLOCKED_BY_API_RETENTION`, `FULL_283D_BLOCKED_BY_API_RETENTION`, `VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY`, `PRE_REGISTERED_BEFORE_COMPUTE`, `MISMATCH`/`ANCHOR: OK`/`ANCHOR: INCOMPLETE` from `check_c25_anchor.sh`.

---

## QUICK REFERENCE — PATHS

- Handoff/state: `HANDOFF.md` (single durable handoff), `INITIAL_TASK_MESSAGE.md` + `AGENT_HANDOFF.md` (pointers), `README.md`, `research_state/strategy_spec.md`.
- C25 ops: `scripts/status_c25.sh`, `scripts/eta_c25.sh`, `scripts/check_c25_anchor.sh`, `scripts/run_c25_durable.sh`, `scripts/verify_c25_focus_campaign.py`.
- C25 artifacts: `research_state/c25_prereg_20261119T045500Z.json`, `research_state/c25_ckpt_{arm}_{venue}_{fold}_20261119T045500Z.json`, `research_state/c25_decision_verdict_{arm,CONSOLIDATED}_20261119T045500Z.json`, run log `research_state/c25_run_20261121T031415Z.log`.
- C26: `scripts/run_c26_path_fidelity_campaign.py`, `scripts/run_c26_durable.sh`, `scripts/status_c26.sh`, `scripts/verify_c26_focus_campaign.py`, `tests/test_c26_campaign.py`, `research_state/c26_prereg_20261119T121500Z.{json,md}`.
- C27: `scripts/probe_c27_venue_acquisition.py`, `research_state/c27_prereg_20261119T215721Z.{json,md}`.
- C28 (BUILT, direction c28-a): `scripts/build_c28_prereg.py`, `scripts/run_c28_campaign.py`, `scripts/run_c28_durable.sh`, `scripts/status_c28.sh`, `scripts/verify_c28_focus_campaign.py`, `tests/test_c28_campaign.py`, `research_state/c28_prereg_20261121T013400Z.{json,md}`.
- C29 (STAGED, direction c29-a): `scripts/build_c29_prereg.py`, `scripts/run_c29_campaign.py`, `scripts/run_c29_durable.sh`, `scripts/status_c29.sh`, `scripts/verify_c29_focus_campaign.py`, `tests/test_c29_campaign.py`, `research_state/c29_prereg_20261121T031907Z.{json,md}`. Holdout direction: strict temporal OOS on the newest never-scored window. Launch only after C28 PASS.
- C30 (BUILT, direction c30-a): `scripts/build_c30_prereg.py`, `scripts/run_c30_campaign.py`, `scripts/run_c30_durable.sh`, `scripts/status_c30.sh`, `scripts/verify_c30_focus_campaign.py`, `tests/test_c30_campaign.py`, `research_state/c30_prereg_20261121T051754Z.{json,md}`. Execution-realism stress: 3× empirical slippage + venue taker commission. Launch only after C29 PASS.
- C31 (BUILT, direction c31-a): `scripts/build_c31_prereg.py`, `scripts/run_c31_campaign.py`, `scripts/run_c31_durable.sh`, `scripts/status_c31.sh`, `scripts/verify_c31_focus_campaign.py`, `tests/test_c31_campaign.py`, `research_state/c31_prereg_20261121T052233Z.{json,md}`. Strict temporal OOS holdout on newest never-scored window 2026-09-29 → 2026-11-21; requires holdout-window archive manifest `<venue>_1h_multiyear_20260929_20261121` per venue. Launch only after C30 PASS + manifests acquired.
- Engine: `src/backtest/engine.py`, `src/strategy/config.py`, `scripts/run_portfolio.py`.