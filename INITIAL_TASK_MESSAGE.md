# INITIAL TASK MESSAGE — NEXT SESSION (2026-11-19T20:22:57Z — C25 RUNNER ALIVE & COMPUTING, 0/64 CELLS IN FLIGHT, DO NOT RELAUNCH; C26 BUILT, NOT LAUNCHED — AWAITING `C25 ACCEPTANCE: PASS`)

**Single durable handoff / source of truth:** `HANDOFF.md`. This file is a pointer only. Do not maintain a second source of truth here.

**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication on real-market, cross-venue data (OKX + Binance UM perps C1–C21; MEXC USDT-perp C22 COMPLETE; Bitget USDT-perp C23 COMPLETE; four-venue execution-model adjudication C24 COMPLETE; cost/funding fidelity C25 RUNNER ALIVE & COMPUTING, 0/64 CELLS IN FLIGHT; C26 path fidelity BUILT, NOT LAUNCHED).

**Priority by repo scope (non-negotiable):** C1–C20 CLOSED & CERTIFIED `NO_GO` (do not relitigate). **C21-T1 COMPLETE** — `C21 ACCEPTANCE: PASS`, consolidated `NO_GO`. **C22-T1 COMPLETE** — `C22 ACCEPTANCE: PASS`, consolidated `NO_GO`. **C23-T1 COMPLETE** — `C23 ACCEPTANCE: PASS`, consolidated `NO_GO`. **C24-T1 GATE PASS** — `C24 ACCEPTANCE: PASS`, consolidated `C24_REOPENS_C1_C23` (d15 pooled +144,651.69, prereg rule met over all 16 cells; C1–C23 `NO_GO` superseded, C24-T2 authorized). All 80 cells done, 6 verdict artifacts written, runner exited. **C25-T1 RUNNER ALIVE & COMPUTING (DO NOT RELAUNCH)** — PID 3901 + 4 workers, `--jobs 4 --resume`, launched ~17:24Z (~2h 12m uptime), 0/64 cells complete (first cell `cost_base/okx/2023` in progress). Gate `C25 ACCEPTANCE: PENDING`. **C26-T1 BUILT, NOT LAUNCHED** — launch only after `C25 ACCEPTANCE: PASS`.

**Verified live state (2026-11-19T20:22:57Z):**
- **C25 RUNNER: ALIVE** (PID 3901 + 4 workers, `run_c25_cost_fidelity_campaign.py --jobs 4 --resume`, ~2h 12m uptime). `bash scripts/status_c25.sh` → `RUNNER: ALIVE`, all 64 cells pending (first cell `cost_base/okx/2023` in progress, log `research_state/c25_run_20261119T172418Z.log`). Gate `C25 ACCEPTANCE: PENDING`. Do NOT relaunch, do NOT kill, do NOT resume. Monitor only. Resume exactly once only if it dies: `bash scripts/run_c25_durable.sh` (persistent=true).
- **C26-T1:** BUILT, NOT LAUNCHED. Prereg `c26_prereg_20261119T121500Z` written; arms `path_base` (anchor, `PATH_ANCHOR_REPRODUCED`), `path_funding_trade`, `path_intrabar_adverse_first`, `path_intrabar_combined` (PRIMARY); 4 venues × 4 folds × 20k/20k/2k; tokens `C26_REOPENS_C1_C25` / `C26_NO_GO_ROBUST_TO_PATH`. Launch only after `C25 ACCEPTANCE: PASS` via `bash scripts/run_c26_durable.sh` (persistent=true).

**Immediate next action (in order — do not skip, do not reorder):**
1. `bash scripts/status_c25.sh` (read-only truth) then `PYTHONPATH=. .venv/bin/python scripts/verify_c25_focus_campaign.py`.
2. Runner is ALIVE (PID 3901): do NOT relaunch, do NOT kill, do NOT start C26 cells. Monitor C25 to completion with bounded waits (`sleep 300` + `tail -5` newest log) or `schedule_wakeup`.
3. On `C25 ACCEPTANCE: PASS`: deliver cost/funding table + consolidated token (`C25_REOPENS_C1_C24` or `C25_NO_GO_ROBUST_TO_COST`), state `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY` citing `research_state/c25_funding_model_disclosure_20261119T091800Z.json`, then **immediately durably launch C26-T1** — do not idle, do not claim no authorized work.
4. If runner dies and gate still PENDING: fix the failure cause, resume exactly once (`bash scripts/run_c25_durable.sh` persistent=true). If gate FAIL: fix only the failing integrity condition; never relax draw floors to force PASS.

**No-avoidance rule (binding):** `C24 → C25 → C26` is the heavy queue. No session may idle, claim "no authorized work", substitute a frozen-signal parameter search, retry OKX funding (`OKX_FUNDING_BLOCKED_BY_API_RETENTION`), zero-fill funding, or reduce draw counts. After `C25 ACCEPTANCE: PASS` the next session MUST durably launch C26-T1 (it is pre-built). C26 is the last same-data fidelity axis; no session may avoid it.

**Full binding context, arm definitions, decision rules, C25/C26 specs, guardrails and execution order:** `HANDOFF.md`.
