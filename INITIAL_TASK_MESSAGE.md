# INITIAL TASK MESSAGE — NEXT SESSION (2026-11-24T03:49:23Z)

**This file is not a source of truth.** The single durable handoff AND the
binding timestamped initial task message live in `HANDOFF.md` §1. If this file
ever disagrees with `HANDOFF.md`, `HANDOFF.md` wins. Do NOT copy volatile
ground-truth numbers (pids, per-cell counts, draw-chunk counts, gate tokens) into
this file — they drift and recreate the state-drift bottleneck. Re-derive them
from the probe below.

Next session, do exactly this and nothing else:

1. `goal start` (objective quoted in `HANDOFF.md` §1 step 0), then `cancel_wakeup list`.
2. `bash scripts/next_c25_action.sh` — the single read-only source of truth. It
   prints one `ACTION:` line, the exact next command, the real remaining-cell
   count, and the pacing interval. It works with or without `.venv`. Obey its one
   `ACTION:` line; never build your own `ps`/`ls`/log chain.
3. `ACTION: NONE_RUNNER_ALIVE` → `bash scripts/check_c25_anchor.sh`, then exactly
   one bounded wait `bash -c 'sleep 540; bash scripts/next_c25_action.sh'`
   (600000 ms tool timeout), then end the turn.
4. `ACTION: RESUME_C25` → resume exactly once:
   `background_process start command="bash scripts/run_c25_durable.sh" persistent=true`
   (self-bootstraps `.venv`), re-probe, then one bounded wait, then end the turn.
5. On any `ACCEPTANCE: PASS` → launch the mandatory same-session successor per
   `HANDOFF.md` §1 steps 4–5 and §7.

**Live priority:** C25 round-trip cost & realized-funding fidelity campaign (heavy
queue `C24 → C25 → … → C32+`, all BUILT/STAGED and gate-held behind C25 PASS).
Repo priority `CRASH-REBOUND-STRATEGY`: crash-rebound edge adjudication on
real-market cross-venue data (OKX, Binance UM, MEXC, Bitget USDT-perps);
`cross_venue=true`; `is_hyperliquid_venue_data=false`; never relabelled as
Hyperliquid evidence.

**Heavy-work contract (no idle escape hatch):** a session is done only after it
EITHER delivers `C25 ACCEPTANCE: PASS` and durably launches the same-session
successor, OR performs exactly one bounded wait and then ends. "No authorized
work", "queue not ready", "waiting on the runner", "another session owns it", or
"just a status check" are NOT valid reasons to end while ANY gate in C25..C32 is
`PENDING`. Do not invent a new campaign (C33 is forbidden until
`C32 ACCEPTANCE: PASS`); do not downgrade to a probe-only read with no bounded
wait.

Read `HANDOFF.md` for the full ordered task list, ground truth, monitoring
protocol, persistence model, bottleneck register, guardrails, and the C26–C32
launch chain.