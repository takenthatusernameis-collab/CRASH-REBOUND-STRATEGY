# Agent Handoff — POINTER ONLY (2026-11-21T08:21:37Z)

**This file is not a source of truth.** The single durable handoff and the
current timestamped initial task message live in `HANDOFF.md`.

Read `HANDOFF.md`, then run `bash scripts/status_c25.sh` and `bash scripts/eta_c25.sh`.

Per the handoff, step 0 is to start a session goal (so the session persists across
8h wakeups) and confirm `cancel_wakeup list` is non-empty. Do not relaunch, kill,
reorder, or start any C26/C27/C28/C29/C30 cell. The heavy queue is
`C24 → C25 → C26 → C27 → C28 → C29 → C30 → C31+`; C28/C29/C30/C31/C32 are
built/staged and gate-held (their runners were fixed this session). See `HANDOFF.md` for the full
ordered task list, monitoring protocol, bottleneck register, and guardrails.