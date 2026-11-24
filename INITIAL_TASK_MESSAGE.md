# INITIAL TASK MESSAGE — NEXT SESSION (2026-11-24T16:39:41Z)

**This file is a pointer only.** The single durable handoff AND the binding timestamped initial task message live in `HANDOFF.md` §1. If this file ever disagrees with `HANDOFF.md`, `HANDOFF.md` wins.

---

## REPO PRIORITY: CRASH-REBOUND-STRATEGY

Crash-rebound edge adjudication on real-market cross-venue data (OKX, Binance UM, MEXC, Bitget USDT-perps). `cross_venue=true`; `is_hyperliquid_venue_data=false`; never relabelled as Hyperliquid evidence.

**LIVE PRIORITY:** C25 round-trip cost & realized-funding fidelity campaign (heavy queue `C24 → C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32+`, all BUILT/STAGED and gate-held behind C25 PASS).

---

## CURRENT GROUND TRUTH (re-derive via `bash scripts/next_c25_action.sh` — never copy from this file)

- **RUNNER:** ALIVE (`bgp_20d3d97fb0013wmMTI4NYjO6R5`, verify via `background_process list`; python supervisor + **dynamic 4-worker pool whose PIDs rotate every cell** — never hardcode worker pids; `run_c25_durable.sh` → `run_c25_cost_fidelity_campaign.py --jobs 4 --resume`, persistent). `ACTION: NONE_RUNNER_ALIVE`. Do NOT resume; do NOT relaunch.
- **GATES:** `C25 ACCEPTANCE: PENDING` · `C26 ACCEPTANCE: PENDING` · `C27–C32 PENDING` (gate-held).
- **PROGRESS:** `real_cells_remaining=30` `skipped_unavailable_funding=8` `draw_chunks_on_disk=5` `in_flight=cost_taker_mexc_2025`. 26 `research_state/c25_ckpt_*` cells committed (16 `cost_base` + 10 `cost_taker`: okx 2023–2026YTD + binance_um 2023–2026YTD + mexc 2023/2024; `cost_taker_mexc_2025` in-flight at 5/40 draw chunks). `--resume` + `C25_DRAW_RESUME=1` resumes bit-identically at cell boundaries.
- **PACING:** `remaining=30` `draw_chunks=5` `wake_after=8h` (>6 cells left; 4 saturated cores at ~1.6 h/cell). Re-derive ETA with `bash scripts/eta_c25.sh` after bootstrap.
- **ANCHOR:** OK (verified 2026-11-24T16:38:52Z — `cost_base` reproduces C24 d15 exactly, all 16/16 cells EXACT: okx 28469.71, binance_um 47613.34, mexc 38341.15, bitget 30234.50). Re-verify with `bash scripts/check_c25_anchor.sh`.
- **QUEUE READINESS:** `bash scripts/check_queue_readiness.sh` exits 0 — C26–C32 all BUILT/STAGED and gate-held behind C25 PASS. `bash scripts/session_gate.py` → `21/21 checks passed — DONE` (2026-11-24T12:50:48Z).

---

## MANDATORY HEAVY-WORK CONTRACT — NO IDLE ESCAPE HATCH

A session counts as done **only** when it has EITHER:
- (a) delivered the full `C25 ACCEPTANCE: PASS` report and durably launched the same-session successor, OR
- (b) performed **exactly one bounded wait** (`bash -c 'sleep 540; bash scripts/next_c25_action.sh'` at 600 000 ms tool timeout) and then ended.

"No authorized work", "queue not ready", "waiting on the runner", "another session owns it", or "just a status check" are **NOT valid reasons to end** while ANY gate in C25..C32 is `PENDING`. There is always authorized heavy work: monitor C25, or on PASS launch the mandatory C26→C32 chain. Do NOT invent C33 (forbidden until `C32 ACCEPTANCE: PASS`); do NOT downgrade to a probe-only read with no bounded wait.

---

## DO EXACTLY THIS, IN ORDER — DO NOT SKIP, REORDER, OR "IMPROVE"

### 0. GUARANTEE PERSISTENCE
```bash
goal start --objective "Drive the crash-rebound heavy-work queue (C24→C25→C26→C27→C28→C29→C30→C31→C32) to completion per HANDOFF.md: monitor C25 with bounded waits, resume-once if the runner dies, launch the mandatory same-session successor on each ACCEPTANCE: PASS, and never idle."
cancel_wakeup list
# If empty: schedule_wakeup delay=8h prompt="Monitor C25: bash scripts/next_c25_action.sh; if ACTION: NONE_RUNNER_ALIVE run check_c25_anchor.sh then bounded wait; if ACTION: RESUME_C25 resume once then bounded wait; on C25 PASS launch C26 per HANDOFF.md §1 step 4."
```

### 1. RUN THE SINGLE SOURCE-OF-TRUTH PROBE
```bash
bash scripts/next_c25_action.sh
```
This prints **one `ACTION:` line**, the exact next command, real remaining-cell count, and pacing interval. Works with or without `.venv`. **Obey it.**

### 2. IF `ACTION: NONE_RUNNER_ALIVE` (runner healthy)
```bash
bash scripts/check_c25_anchor.sh   # must stay ANCHOR: OK or ANCHOR: INCOMPLETE; MISMATCH = P0 stop
bash -c 'sleep 540; bash scripts/next_c25_action.sh'   # 600 000 ms timeout, then end turn
```
Re-arm wakeup at the `PACING` interval the probe printed.

### 3. IF `ACTION: RESUME_C25` (runner NOT ALIVE, gate PENDING)
```bash
background_process start command="bash scripts/run_c25_durable.sh" persistent=true
# Self-bootstraps .venv; one command sufficient. Never resume twice.
bash scripts/next_c25_action.sh   # should print NONE_RUNNER_ALIVE
bash scripts/check_c25_anchor.sh
bash -c 'sleep 540; bash scripts/next_c25_action.sh'   # bounded wait, then end turn
```

### 4. ON `C25 ACCEPTANCE: PASS` (SAME SESSION — MANDATORY SUCCESSOR)
- Deliver full arm × venue × fold cost/funding table, per-leg attribution, exit-reason decomposition, BH family, consolidated token (`C25_REOPENS_C1_C24` or `C25_NO_GO_ROBUST_TO_COST`).
- State verbatim: `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY` citing `research_state/c25_funding_model_disclosure_20261119T091800Z.json`.
- Report `okx` as `UNAVAILABLE_FUNDING` / `OKX_FUNDING_BLOCKED_BY_API_RETENTION` — **never zero-fill, proxy, or retry**.
- Durably launch C26-T1:
```bash
background_process start command="bash scripts/run_c26_durable.sh" persistent=true
bash scripts/status_c26.sh
PYTHONPATH=. .venv/bin/python scripts/verify_c26_focus_campaign.py
```

### 5. ON `C26 ACCEPTANCE: PASS` (SAME SESSION — MANDATORY CHAIN)
C27 (kucoin primary venue per `ACQUISITION_VIABLE_KUCOIN_MULTIYEAR` probe):
```bash
bash scripts/status_c27.sh
PYTHONPATH=. .venv/bin/python scripts/verify_c27_focus_campaign.py
background_process start command="bash scripts/run_c27_durable.sh" persistent=true
PYTHONPATH=. .venv/bin/python scripts/probe_c27_venue_acquisition.py  # confirm prereg matches verdict
```
Then C28 → C29 → C30 → C31 → C32 in the same chain, each gate-held on the prior PASS (see `HANDOFF.md` §7 for exact launch commands and refusal artifacts). **C33 opens only after `C32 ACCEPTANCE: PASS`** with a fresh `PRE_REGISTERED_BEFORE_COMPUTE` prereg anchored on real C24–C32 evidence — never a same-data rerun, never a frozen-signal parameter search.

---

## VERIFICATION COMMANDS (read-only, in order)
```bash
bash scripts/next_c25_action.sh              # ONE probe: runner + gate + anchor + remaining + pacing + ACTION
bash scripts/status_c25.sh                   # runner + per-cell + in-flight draw chunks + artifacts + gate
bash scripts/check_c25_anchor.sh             # early cost_base vs C24 d15 anchor
bash scripts/eta_c25.sh                      # progress, per-cell cost, ETA (needs .venv)
bash scripts/check_queue_readiness.sh        # all C25–C32 verified (exits 0)
bash scripts/session_gate.py                 # 21/21 checks passed — DONE (after material handoff changes)
```

---

## GUARDRAILS (NEVER VIOLATE)
- No cross-venue relabelling as Hyperliquid-native (`is_hyperliquid_venue_data=false` for C20–C32).
- No synthetic gap-fill as verified; no spec relaxation to manufacture GO.
- **No funding fabrication:** `okx` funding = `UNAVAILABLE_FUNDING` / `OKX_FUNDING_BLOCKED_BY_API_RETENTION` — never zero-fill, never proxy.
- **Funding model honesty:** C25 reports `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY` citing the disclosure JSON.
- **Do not reduce draw counts** (20k/20k/2k/2k floors). Do not edit live campaign prereg or code path.
- **Status first:** `bash scripts/status_c25.sh` (or `next_c25_action.sh`) before any C25 action.
- **Do not kill or duplicate the runner.** Durable launchers self-bootstrap `.venv`.
- **No long foreground sleep** past ~900 s idle timeout: one bounded wait per session, then end.
- No same-data rerun of a closed campaign.
- Do not commit unless explicitly asked (controller checkpoints the worktree).
- Preserve literal gate tokens verbatim (see `HANDOFF.md` §6 full list).

---

**NEXT SESSION START HERE. Read `HANDOFF.md` for the full ordered task list, bottleneck register, monitoring protocol, persistence model, and the C26–C32 launch chain.**