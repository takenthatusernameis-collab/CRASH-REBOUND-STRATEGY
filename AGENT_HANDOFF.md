# Agent Handoff — POINTER ONLY (2026-11-21T10:22:00Z)

**This file is not a source of truth.** The single durable handoff and the
current timestamped initial task message live in `HANDOFF.md`.

Read `HANDOFF.md`, then run `bash scripts/next_c25_action.sh` (the single read-only
entry probe — it prints one `ACTION:` line, the exact next command, the remaining
cell count, and the pacing interval). It works with or without `.venv` and it
correctly detects a dead runner (`NOT ALIVE` → `ACTION: RESUME_C25`).

Per the handoff, step 0 is to start a session goal and confirm `cancel_wakeup list`
is non-empty. Do not relaunch, kill, reorder, or start any C26/C27/C28/C29/C30/C31/C32
cell while C25 is in flight. The heavy queue is
`C24 → C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32+`; C28/C29/C30/C31/C32 are
built/staged and gate-held. See `HANDOFF.md` for the full ordered task list,
monitoring protocol, persistence model, bottleneck register, and guardrails.