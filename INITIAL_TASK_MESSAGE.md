# INITIAL TASK MESSAGE — CRASH-REBOUND-STRATEGY (POINTER ONLY)

**Single durable handoff:** `HANDOFF.md`. It is the binding timestamped initial task message for the next agentic session and the source of all campaign state (runner, gate, progress, pacing). This file intentionally contains no campaign state.

Read `HANDOFF.md` first. Re-derive all runner, gate, progress, and pacing state with `bash scripts/next_c25_action.sh`; do not use stale values from any pointer file. If anything disagrees with `HANDOFF.md`, that file wins.
