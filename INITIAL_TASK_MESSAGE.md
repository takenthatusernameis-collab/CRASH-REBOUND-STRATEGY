# INITIAL TASK MESSAGE — POINTER ONLY (2026-11-21T10:22:00Z)

**This file is not a source of truth.** The single durable handoff and the full
binding timestamped initial task message (steps 0–11, persistence model,
monitoring protocol, guardrails) live inline in `HANDOFF.md`.

Read `HANDOFF.md`, then run `bash scripts/next_c25_action.sh` — the single read-only
entry probe. It prints one `ACTION:` line, the exact next command, the real
remaining-cell count, and the pacing interval. It works with or without `.venv`
and it correctly reports a dead runner (`NOT ALIVE` → `ACTION: RESUME_C25`).

Per the handoff, step 0 is to start a session goal (so the session persists across
wakeups) and confirm `cancel_wakeup list` is non-empty. The durable persistence is
the runner plus the git-committed checkpoints, not the wakeup.

Do not relaunch, kill, reorder, or start any C26/C27/C28/C29/C30/C31/C32 cell while
C25 is in flight. The heavy queue is
`C24 → C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32+`; C28/C29/C30/C31/C32 are
built/staged and gate-held, and C32 is built and gate-held behind C31. See
`HANDOFF.md` for the full ordered task list, monitoring protocol, bottleneck
register, and guardrails.