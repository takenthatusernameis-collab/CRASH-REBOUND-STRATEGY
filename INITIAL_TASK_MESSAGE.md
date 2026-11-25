# INITIAL TASK MESSAGE — POINTER ONLY (2026-11-25T05:30:07Z)

Read `HANDOFF.md` first. It is the single durable handoff and binding timestamped initial task message for the next agentic session.

This pointer intentionally contains no runner, gate, progress, pacing, or campaign state. Re-derive all live state with `bash scripts/next_c25_action.sh` and obey its `ACTION:` line.