# INITIAL TASK MESSAGE — 2026-11-19T13:22:26Z (C24 COMPLETE `C24 ACCEPTANCE: PASS`, consolidated `C24_REOPENS_C1_C23`; C25 RUNNER ALIVE & DURABLE, 64 CELLS IN FLIGHT; C26 BUILT, NOT LAUNCHED — AWAITING `C25 ACCEPTANCE: PASS`)

**Single durable handoff / source of truth:** `HANDOFF.md` — read it in full before acting. Do not maintain a second source of truth here. This file is a pointer only.

**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication on real-market, cross-venue data (OKX, Binance UM, MEXC C22, Bitget C23; four-venue execution-model adjudication C24 COMPLETE; cost/funding C25 RUNNING; path fidelity C26 BUILT, NOT LAUNCHED).

**Current position (verified live 2026-11-19T12:15:27Z):** C1–C20 CLOSED `NO_GO`; C21/C22/C23-T1 COMPLETE (`PASS`, `NO_GO`). **C24-T1 GATE PASS: `C24 ACCEPTANCE: PASS`, consolidated `C24_REOPENS_C1_C23` — d15 pooled +144,651.69, prereg rule met over all 16 cells; C1–C23 `NO_GO` superseded. All 80 cells done, 6 verdict artifacts written, runner exited. Tests 17 passed.**
**C25-T1 RUNNER ALIVE & DURABLE:** PID 31466 + 4 workers (launched ~11:21Z, `--jobs 4 --resume`, persistent). 64 cells pending across 4 arms × 4 venues × 4 folds. Gate `C25 ACCEPTANCE: PENDING`. **Do not relaunch or kill.** Monitor with `bash scripts/status_c25.sh` and `PYTHONPATH=. .venv/bin/python scripts/verify_c25_focus_campaign.py`.
**C26-T1 (INTRABAT PATH & PER-TRADE FUNDING FIDELITY) — BUILT, NOT LAUNCHED:** prereg `c26_prereg_20261119T121500Z` written; arms `path_base` (anchor, `PATH_ANCHOR_REPRODUCED`), `path_funding_trade`, `path_intrabar_adverse_first`, `path_intrabar_combined` (PRIMARY); 4 venues × 4 folds × 20k/20k/2k; tokens `C26_REOPENS_C1_C25` / `C26_NO_GO_ROBUST_TO_PATH`. Campaign, durable launcher, status probe, gate and tests all present and passing. Launch only after `C25 ACCEPTANCE: PASS` via `bash scripts/run_c26_durable.sh` (persistent=true).

**Immediate next action (in order — do not skip, do not reorder):**
1. `bash scripts/status_c25.sh` (read-only truth) then `PYTHONPATH=. .venv/bin/python scripts/verify_c25_focus_campaign.py`.
2. If `RUNNER: ALIVE`: do not relaunch, do not kill, do not start C26 cells. Monitor C25 to completion with bounded waits (`sleep 300` + `tail -5` newest log) or `schedule_wakeup`.
3. If `RUNNER: NOT ALIVE` and gate PENDING: resume exactly once with `bash scripts/run_c25_durable.sh` via harness background-process tool with `persistent=true`.
4. On `C25 ACCEPTANCE: PASS`: deliver cost/funding table + consolidated token (`C25_REOPENS_C1_C24` or `C25_NO_GO_ROBUST_TO_COST`), state `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY` citing `research_state/c25_funding_model_disclosure_20261119T091800Z.json`, then **immediately durably launch C26-T1** — do not idle, do not claim no authorized work.
5. If a gate is `FAIL`: fix only the failing integrity condition; never relax draw floors to force PASS.

**No-avoidance rule (binding):** `C24 → C25 → C26` is the heavy queue. No session may idle, claim "no authorized work", substitute a frozen-signal parameter search, retry OKX funding, zero-fill funding, or reduce draw counts. After `C25 ACCEPTANCE: PASS` the next session MUST durably launch C26-T1 (it is pre-built).

Full binding context, arm definitions, decision rules, C25/C26 specs, guardrails and execution order: `HANDOFF.md`.
