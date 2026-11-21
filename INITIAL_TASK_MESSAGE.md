# INITIAL TASK MESSAGE — NEXT SESSION (2026-11-21T11:28:56Z)

**Repository:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication on real-market, cross-venue data (OKX, Binance UM, MEXC, Bitget USDT-perps). **Live priority:** C25 cost/funding-fidelity campaign (IN FLIGHT, RUNNER ALIVE, 8/56 cells done, 48 remaining, ETA ~2026-11-24T17:05:57Z ±30%). Heavy queue: `C24 → C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32+` (C26–C32 BUILT/STAGED, gate-held). **No authorized work is never a truthful state while any gate is PENDING.**

---

## DO THIS IN ORDER — NO SKIP, NO REORDER, NO "IMPROVEMENT"

0. **`goal start`** with objective: *"Drive the crash-rebound heavy-work queue (C24→C25→C26→C27→C28→C29→C30→C31→C32) to completion per HANDOFF.md: monitor C25 with bounded waits, resume-once if runner dies, launch mandatory same-session successor on each ACCEPTANCE: PASS, never idle."* Then `cancel_wakeup list`; if empty → `schedule_wakeup delay=8h` with monitoring prompt below. **Wakeup ≠ persistence** — the runner + git-committed checkpoints are. Do not proceed past step 1 with empty wakeup list and no active goal.

1. **`bash scripts/next_c25_action.sh`** — single read-only probe. Obey the `ACTION:` line exactly. It prints the exact next command, real remaining-cell count, and pacing interval (90 m / 4 h / 8 h from remaining cells). Works with or without `.venv`. Detects `NOT ALIVE` correctly.

2. **If `ACTION: NONE_RUNNER_ALIVE` (expected — runner is ALIVE):**
   - `bash scripts/check_c25_anchor.sh` (must be `ANCHOR: INCOMPLETE` or `ANCHOR: OK`; `MISMATCH` = P0 stop)
   - **One bounded wait:** `bash -c 'sleep 540; bash scripts/next_c25_action.sh'` with **600 000 ms tool timeout**. Never sleep past 900 s idle timeout.
   - End turn. Re-arm wakeup at the PACING interval the probe printed (never hardcode 8 h).

3. **If `ACTION: RESUME_C25` (runner dead, gate PENDING):**
   - Resume **exactly once**: `background_process start command="bash scripts/run_c25_durable.sh" persistent=true` (self-bootstraps `.venv` if missing)
   - Re-probe, then one bounded wait, then end.

4. **If `ACTION: P0_STOP_ANCHOR_MISMATCH`:** Record evidence, fix cause, resume once. Never relax floors, never edit prereg, never force PASS.

5. **On `C25 ACCEPTANCE: PASS` (same session, mandatory):**
   - Deliver full arm×venue×fold cost/funding table, per-leg attribution, exit-reason decomposition, BH family, consolidated token (`C25_REOPENS_C1_C24` or `C25_NO_GO_ROBUST_TO_COST`).
   - State verbatim: `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY` citing `research_state/c25_funding_model_disclosure_20261119T091800Z.json`.
   - Report `okx` as `UNAVAILABLE_FUNDING` / `OKX_FUNDING_BLOCKED_BY_API_RETENTION` — never zero-fill, proxy, or retry.
   - Launch C26: `background_process start command="bash scripts/run_c26_durable.sh" persistent=true`; verify with `status_c26.sh` + `verify_c26_focus_campaign.py`.

6. **On `C26 ACCEPTANCE: PASS` (same session, mandatory):** C27 is BUILT (kucoin primary, `ACQUISITION_VIABLE_KUCOIN_MULTIYEAR`). Verify `status_c27.sh` (`PRE_REGISTERED_BEFORE_COMPUTE` + `C27 ACCEPTANCE: PENDING`) + `verify_c27_focus_campaign.py`. Launch: `background_process start command="bash scripts/run_c27_durable.sh" persistent=true`. Runner refuses unless `c26_decision_verdict_CONSOLIDATED_20261119T215721Z.json` exists — if refusal, fix C26 first.

7. **On `C27 ACCEPTANCE: PASS` (same session, mandatory):** C28 BUILT (`c28-a`). Verify `status_c28.sh --direction c28-a` + `verify_c28_focus_campaign.py --direction c28-a`. Launch: `background_process start command="bash scripts/run_c28_durable.sh --direction c28-a" persistent=true`. Runner refuses unless `c27_decision_verdict_CONSOLIDATED_20261119T215721Z.json` exists.

8. **On `C28 ACCEPTANCE: PASS` (same session, mandatory):** C29 STAGED (`c29-a`). Verify `status_c29.sh --direction c29-a` + `verify_c29_focus_campaign.py --direction c29-a`. Launch: `background_process start command="bash scripts/run_c29_durable.sh --direction c29-a" persistent=true`. Runner refuses unless `c28_decision_verdict_CONSOLIDATED_20261121T013400Z.json` exists.

9. **On `C29 ACCEPTANCE: PASS` (same session, mandatory):** C30 BUILT (`c30-a`, 3× slippage + venue taker). Verify `status_c30.sh --direction c30-a` + `verify_c30_focus_campaign.py --direction c30-a`. Launch: `background_process start command="bash scripts/run_c30_durable.sh --direction c30-a" persistent=true`. Runner refuses unless `c29_decision_verdict_CONSOLIDATED_20261121T031907Z.json` exists.

10. **On `C30 ACCEPTANCE: PASS` (same session, mandatory):** C31 BUILT (`c31-a`, forward-time holdout 2026-09-29 → 2026-11-21). Verify `status_c31.sh --direction c31-a` + `verify_c31_focus_campaign.py --direction c31-a`. Launch: `background_process start command="bash scripts/run_c31_durable.sh --direction c31-a" persistent=true`. Runner refuses unless `c30_decision_verdict_CONSOLIDATED_20261121T051754Z.json` exists **and** per-venue holdout manifests `research_state/cache/<venue>_1h_multiyear_20260929_20261121` acquired.

11. **On `C31 ACCEPTANCE: PASS` (same session, mandatory — queue never dries out):** C32 BUILT (`c32-a`, next independent USDT-perp venue). Verify `status_c32.sh --direction c32-a` + `verify_c32_focus_campaign.py --direction c32-a`. Launch: `background_process start command="bash scripts/run_c32_durable.sh --direction c32-a" persistent=true`. Runner refuses unless `c31_decision_verdict_CONSOLIDATED_20261121T061508Z.json` exists. On `C32 ACCEPTANCE: PASS`, open C33 with fresh `PRE_REGISTERED_BEFORE_COMPUTE` prereg anchored on C24–C32 evidence.

---

## GUARDRAILS (NEVER VIOLATE)

- **No funding fabrication:** `okx` = `UNAVAILABLE_FUNDING` / `OKX_FUNDING_BLOCKED_BY_API_RETENTION` — never zero-fill, proxy, or cache 1-month tail as multiyear.
- **Funding model honesty:** C25 cites `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY` + disclosure artifact.
- **No draw-count reduction** (20k/20k/2k/2k floors prereg-bound).
- **No live campaign prereg/code edits.** C28–C32 runners frozen — do not reintroduce `prereg["arms"][direction]["arms"]` lookup or `per_venue_cap_pct` kwarg.
- **Status first:** `bash scripts/next_c25_action.sh` before any C25 action.
- **No kill/duplicate runner.** Long campaigns via harness `background_process` with `persistent=true`. All durable launchers self-bootstrap `.venv`.
- **No idle sessions:** binding queue is `C24 → C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32+`.
- **No same-data rerun.** Only new data + new prereg + explicit authorization justifies new campaign.
- **Preserve literal gate tokens verbatim** (see HANDOFF.md §6).
- **Do not commit unless explicitly asked** (controller checkpoints worktree).

---

## MONITORING PROMPT (for wakeup)

> Run `bash scripts/next_c25_action.sh` → obey `ACTION:` line. If `NONE_RUNNER_ALIVE`: `check_c25_anchor.sh` → one bounded wait (`sleep 540`, 600s timeout) → end. If `RESUME_C25`: resume once → re-probe → bounded wait → end. Re-arm wakeup at probe's PACING interval.

---

**The probe is ground truth. The runner + git checkpoints are durability. One bounded wait per session maps to compute progress. The heavy queue has months of runway — do not idle, do not substitute, do not avoid.**