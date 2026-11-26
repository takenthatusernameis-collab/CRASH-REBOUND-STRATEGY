# INITIAL TASK MESSAGE — CRASH-REBOUND-STRATEGY (2026-11-26T05:30:25Z)

**Single durable handoff:** `HANDOFF.md` is the binding timestamped initial task message for the next agentic session and the source of all campaign state (runner, gate, progress, pacing). This file is a pointer only; if anything disagrees with `HANDOFF.md`, that file wins.

**Repo priority:** Crash-rebound edge adjudication on real-market cross-venue data: OKX, Binance UM, MEXC, Bitget USDT-perps. `cross_venue=true`; `is_hyperliquid_venue_data=false`; never relabel evidence as Hyperliquid-native.

---

## BINDING IMMEDIATE ACTION FOR NEXT SESSION

**Runner state:** `RUNNER: ALIVE` · `ACTION: NONE_RUNNER_ALIVE`
C25 runner resumed this session (2026-11-26T05:14:43Z) as one persistent `background_process` running `bash scripts/run_c25_durable.sh --jobs 4 --resume` with bootstrapped `.venv`. If a fresh job finds it dead, the probe prints `ACTION: RESUME_C25` — resume once with the durable launcher.

**Gate state:** `C25 ACCEPTANCE: PENDING` · `C26 ACCEPTANCE: PENDING` · C27–C32 pending behind predecessors
**Progress:** 23 real cells remaining, 8 skipped (unavailable funding), 11 draw chunks on disk, in-flight: `cost_taker_funding_binance_um_2024`
**Anchor:** OK — `cost_base` reproduces C24 d15 exactly (16/16 cells EXACT)
**Pacing:** `wake_after=8h` (re-derive from probe each session)

---

## EXACT SEQUENCE NEXT SESSION MUST EXECUTE

```bash
# 0. Guarantee persistence (run once per session)
goal start "Drive crash-rebound heavy queue C25→C32 to completion; monitor C25 with bounded waits; resume once if runner dies; launch mandatory successors on PASS; never idle"

# 1. Single entry probe (read-only, works without .venv)
bash scripts/next_c25_action.sh
# Expects: ACTION: NONE_RUNNER_ALIVE (or RESUME_C25 on a fresh job)

# 2. If ACTION: NONE_RUNNER_ALIVE (current state)
bash scripts/check_c25_anchor.sh          # expects ANCHOR: OK
bash -c 'sleep 540; bash scripts/next_c25_action.sh'   # 600000 ms timeout, then END TURN

# 3. Re-arm wakeup at probe's printed pacing interval (currently 8h)
#    cancel_wakeup list; if empty, schedule_wakeup with delay=8h
```

**Do not:** relaunch, kill, reorder, or add CPU-heavy work. One bounded wait, then end turn.

---

## HEAVY-WORK CONTRACT — NO IDLE ESCAPE HATCH

While any C25–C32 gate is pending, these are **not valid stop reasons**:
- "waiting on the runner"
- "queue not ready"  (C26–C32 are BUILT/STAGED, gate-held — `check_queue_readiness.sh` exits 0)
- "another session owns it"
- "just a status check"

A session is complete only when it either:
1. Delivers full `C25 ACCEPTANCE: PASS` report and durably launches C26 in the same session, OR
2. Performs exactly one bounded wait after healthy-runner probe and ends turn.

**On each PASS, launch mandatory successor in same session:**
- C25 PASS → `background_process start command="bash scripts/run_c26_durable.sh" persistent=true`
- C26 PASS → verify C27, then `background_process start command="bash scripts/run_c27_durable.sh" persistent=true`
- C27 PASS → `background_process start command="bash scripts/run_c28_durable.sh --direction c28-a" persistent=true`
- C28 PASS → `background_process start command="bash scripts/run_c29_durable.sh --direction c29-a" persistent=true`
- C29 PASS → `background_process start command="bash scripts/run_c30_durable.sh --direction c30-a" persistent=true`
- C30 PASS → C31 (needs holdout manifests) → `background_process start command="bash scripts/run_c31_durable.sh --direction c31-a" persistent=true`
- C31 PASS → `background_process start command="bash scripts/run_c32_durable.sh --direction c32-a" persistent=true`
- C32 PASS → only then may C33 open with fresh `PRE_REGISTERED_BEFORE_COMPUTE` prereg

---

## GUARDRAILS (NON-NEGOTIABLE)

- No cross-venue relabelling as Hyperliquid-native (`is_hyperliquid_venue_data=false` for C20–C32)
- No synthetic gap-fill as verified; no spec relaxation to manufacture GO; `SPEC_LITERAL_NEXT_OPEN` fixed
- No funding fabrication: OKX funding = `UNAVAILABLE_FUNDING` / `OKX_FUNDING_BLOCKED_BY_API_RETENTION`; never zero-fill/proxy
- C25 funding disclosure: `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY` (per-trade funding = C26 only)
- Do not reduce draw counts (20k/20k/2k floors), edit live prereg/code paths, or kill/duplicate a healthy runner
- Status first: `bash scripts/status_c25.sh` or `bash scripts/next_c25_action.sh` before any C25 action
- One bounded wait per session (≤900s idle timeout); then end
- No same-data rerun of closed campaign; C33 requires C32 PASS + fresh prereg + new evidence
- Do not commit unless explicitly asked; controller checkpoints worktree

---

## VERIFICATION CHECKLIST (run in order)

```bash
bash scripts/next_c25_action.sh
bash scripts/status_c25.sh
bash scripts/check_c25_anchor.sh
bash scripts/check_queue_readiness.sh
PYTHONPATH=. .venv/bin/python scripts/session_gate.py   # must print: 21/21 checks passed — DONE
```

After any material handoff change, `session_gate.py` must finish with `21/21 checks passed — DONE`.

---

**Updated:** 2026-11-26T05:30:25Z
**Source of truth:** `HANDOFF.md` (this file is a pointer only)