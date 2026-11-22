# INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (REFRESHED 2026-11-22T14:49:30Z)

**Repository:** `CRASH-REBOUND-STRATEGY` — crash-rebound trading strategy research/backtesting on real-market cross-venue data (OKX, Binance UM, MEXC, Bitget USDT-perps).

**SOURCE OF TRUTH:** `HANDOFF.md` is the single durable handoff and the binding initial task message (section 1). This file is a pointer only — if this file and `HANDOFF.md` disagree, `HANDOFF.md` wins.

**LIVE PRIORITY:** The **C25 round-trip cost & realized-funding fidelity campaign** — runner **ALIVE** (PID 3106, supervisor 2889, 4 workers R), 16/56 real cells complete, **40 remaining** (8 okx `UNAVAILABLE_FUNDING` skips), `cost_base 16/16` done [okx/binance_um/mexc/bitget 4/4 each], anchor **OK** (all 16/16 cost_base EXACT: okx 28469.71, binance_um 47613.34, mexc 38334.15, bitget 30234.50), in-flight `cost_taker_okx_2023` at **30/40 draw chunks on disk** (runner advancing, advanced 6→30 since 2026-11-22T07:48:24Z), gate `C25 ACCEPTANCE: PENDING`. Verified via `bash scripts/next_c25_action.sh` at 14:49Z → `ACTION: NONE_RUNNER_ALIVE`. ETA **~2026-11-25T07:31:34Z (±30%, median n=16)**. `PACING: remaining=40 wake_after=8h`.

**HEAVY QUEUE (fully built/staged, gate-held):**
```
C24 (PASS) → C25 (IN FLIGHT, 40 cells) → C26 (BUILT) → C27 (BUILT) → C28 (BUILT) → C29 (STAGED) → C30 (BUILT) → C31 (BUILT) → C32 (BUILT) → C33+
```

**BINDING WORKFLOW — DO EXACTLY THIS:**

```bash
# 0. Start persistent goal (prevents session spin)
goal start --objective "Drive C25→C26→C27→C28→C29→C30→C31→C32 queue to completion: monitor C25 with bounded waits, resume-once if runner dies, launch mandatory same-session successor on each PASS, never idle"

# 1. Single ground-truth probe (reads checkpoints in pure bash; works without venv)
bash scripts/next_c25_action.sh
```

**OBEY THE `ACTION:` LINE IT PRINTS.** Current expected output: `ACTION: NONE_RUNNER_ALIVE` (runner healthy, nothing to fix).

**IF `ACTION: NONE_RUNNER_ALIVE`:**
```bash
# 2. Verify anchor integrity (must stay OK/INCOMPLETE; MISMATCH = P0 stop)
bash scripts/check_c25_anchor.sh

# 3. ONE BOUNDED WAIT (9 min, 600000 ms tool timeout) — maps session to compute progress
bash -c 'sleep 540; bash scripts/next_c25_action.sh'
# Then END TURN. Do not loop. Do not edit HANDOFF.md for cosmetic timestamps.
```

**IF `ACTION: RESUME_C25` (runner dead, gate PENDING):**
```bash
# Resume EXACTLY ONCE (run_c25_durable.sh self-bootstraps .venv on fresh job)
background_process start command="bash scripts/run_c25_durable.sh" persistent=true
# Then re-probe: bash scripts/next_c25_action.sh → should print NONE_RUNNER_ALIVE
# Then steps 2–3 above.
```

**GUARDRAILS (NEVER VIOLATE):**
- Do NOT kill/restart/relaunch the runner while ALIVE
- Do NOT start C26/C27/C28/C29/C30/C31/C32 — C25 must PASS first
- Do NOT reduce draw floors (20k/20k/2k/2k) or edit live campaign prereg/code
- Do NOT zero-fill OKX funding → report `UNAVAILABLE_FUNDING` / `OKX_FUNDING_BLOCKED_BY_API_RETENTION`
- Do NOT substitute unrelated work, frozen-signal searches, or same-data reruns
- Do NOT idle — a `PENDING` gate means the heavy battery keeps running
- The only bottleneck is compute (~40 cells at ~1.6 h/cell on 4 saturated cores) — **not fixable mid-run**

**VERIFICATION COMMANDS (run anytime for ground truth):**
```bash
bash scripts/next_c25_action.sh      # ACTION + remaining + pacing
bash scripts/status_c25.sh           # runner + per-cell + draw chunks
bash scripts/check_c25_anchor.sh     # cost_base vs C24 d15 anchor
bash scripts/check_queue_readiness.sh # all C25–C32 verified (exits 0)
```

**THIS IS A POINTER ONLY.** Read `HANDOFF.md` for full detail, campaign specs, gate tokens, and the complete 11-step launch chain. The probe is your only decision input — obey it. Explicit directions are present for the whole queue; do not build C33 speculatively (C33 opens only after `C32 ACCEPTANCE: PASS`). No sessions are blocked.