# Agent Handoff — POINTER ONLY (2026-11-25T18:21:28Z)

This file is not a source of truth and intentionally contains no campaign state.

Read `INITIAL_TASK_MESSAGE.md` first. It is the single durable handoff and the binding timestamped initial task message for the next agentic session. Re-derive all runner, gate, progress, and pacing state with `bash scripts/next_c25_action.sh`; do not use stale values from any pointer file.
