# INITIAL TASK MESSAGE — POINTER ONLY (2026-11-21T07:17:22Z)

**This file is not a source of truth.** The single durable handoff and the full
binding timestamped initial task message (steps 0–10, monitoring protocol,
guardrails) live inline in `HANDOFF.md`.

Read `HANDOFF.md`, then run `bash scripts/status_c25.sh` and `bash scripts/eta_c25.sh`.

Per the handoff, step 0 is to start a session goal (so the session persists across
8h wakeups) and confirm `cancel_wakeup list` is non-empty. Do not relaunch, kill,
reorder, or start any C26/C27/C28/C29/C30/C31/C32 cell. The heavy queue is
`C24 → C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32+`; C28/C29/C30/C31 are
built/staged and gate-held; C32 is built and gate-held behind C31.