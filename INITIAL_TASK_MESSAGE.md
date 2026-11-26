# INITIAL TASK MESSAGE — POINTER ONLY (2026-11-26T20:08:11Z)

The single durable handoff and binding timestamped initial task message is `HANDOFF.md`. Read Section 1 there first.

This file intentionally contains no campaign state. If anything disagrees with `HANDOFF.md`, that file wins. Re-derive runner, gate, progress, and pacing state with `bash scripts/next_c25_action.sh`.