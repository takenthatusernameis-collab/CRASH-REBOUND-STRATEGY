# INITIAL TASK MESSAGE — CRASH-REBOUND-STRATEGY (2026-11-25T17:58:28Z)

**Single durable handoff and binding initial task message for the next agentic session.**

## REPOSITORY PRIORITY
Crash-rebound edge adjudication on real-market cross-venue data: OKX, Binance UM, MEXC, and Bitget USDT-perps. `cross_venue=true`; `is_hyperliquid_venue_data=false`; never relabel this evidence as Hyperliquid-native.

## LIVE STATE — RE-DERIVED AT 2026-11-25T17:58:28Z
- **RUNNER:** ALIVE (campaign pid 2934, workers 24737–24740, 4 workers, `--jobs 4 --resume`, `.venv` bootstrapped)
- **ACTION:** NONE_RUNNER_ALIVE
- **GATE C25:** PENDING (16/16 cost_base complete, 14/16 cost_taker, 0/16 cost_taker_funding, 0/16 cost_stress)
- **GATE C26–C32:** PENDING (built/staged, gate-held behind C25)
- **ANCHOR:** OK (cost_base reproduces C24 d15 exactly: OKX 28469.71, Binance UM 47613.34, MEXC 38334.15, Bitget 30234.50)
- **PROGRESS:** real_cells_remaining=26, skipped_unavailable_funding=8, draw_chunks_on_disk=1, in_flight=cost_taker_bitget_2025
- **PACING:** remaining=26, draw_chunks=1, wake_after=8h (>6 cells left; 4 saturated cores at ~1.6 h/cell)
- **SESSION GATE:** 21/21 checks passed — DONE

## BINDING IMMEDIATE ACTION
```bash
bash scripts/next_c25_action.sh   # expects ACTION: NONE_RUNNER_ALIVE
bash scripts/check_c25_anchor.sh   # expects ANCHOR: OK
bash -c 'sleep 540; bash scripts/next_c25_action.sh'   # 600000 ms tool timeout, then END
```
Do not relaunch, kill, reorder, or add CPU-heavy work. Re-arm wakeup at the printed pacing interval (currently `wake_after=8h`).

## HEAVY-WORK CONTRACT — NO IDLE ESCAPE HATCH
While any C25–C32 gate is pending:
- "waiting on the runner", "queue not ready", "another session owns it", "just a status check" are **not valid reasons to stop**
- Do not downgrade to a probe-only read
- Do not start duplicate CPU work
- Do not end before the required bounded wake

**A next session is complete only when it either:**
1. Delivers the full `C25 ACCEPTANCE: PASS` report and durably launches C26 in the same session; OR
2. Performs exactly one bounded wait after a healthy-runner probe and then ends the turn.

## MANDATORY SUCCESSOR CHAIN (C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32)
- C25 PASS → launch C26: `background_process start command="bash scripts/run_c26_durable.sh" persistent=true`
- C26 PASS → verify C27, then launch C27
- C27 PASS → launch C28 (`--direction c28-a`)
- C28 PASS → launch C29 (`--direction c29-a`)
- C29 PASS → launch C30 (`--direction c30-a`)
- C30 PASS → launch C31 (`--direction c31-a`, gated on holdout manifests)
- C31 PASS → launch C32 (`--direction c32-a`)
- C32 PASS → only then may C33 open with fresh `PRE_REGISTERED_BEFORE_COMPUTE` prereg

## BOTTLENECKS REMOVED (DO NOT RE-INTRODUCE)
1. **Duplicate state drift** — campaign state exists only in HANDOFF.md; pointer files contain no state
2. **Stale runner identity** — re-derive from `bash scripts/status_c25.sh` and `bash scripts/next_c25_action.sh` each session
3. **Log bloat** — old per-session re-stamp entries collapsed; update HANDOFF.md only for material state/gate change
4. **Contradictory pointers** — INITIAL_TASK_MESSAGE.md and AGENT_HANDOFF.md are minimal pointers only
5. **Session spin/quota exhaustion** — one ALIVE-runner session = one bounded wait
6. **Fresh-job bootstrap** — `run_c25_durable.sh` self-bootstraps `.venv`
7. **False liveness from pgrep** — status scripts require real Python campaign process
8. **Queue-dryness ambiguity** — C26–C32 are built/staged; `check_queue_readiness.sh` exits 0
9. **Successor-missing** — every C25–C32 campaign has prereg + full implementation
10. **Idle escape hatch** — heavy-work contract makes launches mandatory on each PASS
11. **Dead-runner resume** — `run_c25_durable.sh` refuses duplicates and bootstraps `.venv`
12. **Contradictory C27 readiness label** — gap is CLOSED; header updated

## GUARDRAILS (VIOLATION = INVALID SESSION)
- No cross-venue relabelling as Hyperliquid-native
- No synthetic gap-fill as verified; no spec relaxation to manufacture GO
- No funding fabrication: OKX funding = `UNAVAILABLE_FUNDING` / `OKX_FUNDING_BLOCKED_BY_API_RETENTION`; never zero-fill
- C25 funding disclosure: `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY`
- Do not reduce draw counts (20k/20k/2k floors), edit live prereg/code paths, or kill/duplicate a healthy runner
- Status first: run `bash scripts/status_c25.sh` or `bash scripts/next_c25_action.sh` before any C25 action
- No long foreground sleep past ~900s idle timeout; one bounded wait per session, then end
- No same-data rerun of a closed campaign
- Do not commit unless explicitly asked

## VERIFICATION COMMANDS (RUN IN ORDER)
```bash
bash scripts/next_c25_action.sh
bash scripts/status_c25.sh
bash scripts/check_c25_anchor.sh
bash scripts/check_queue_readiness.sh
PYTHONPATH=. .venv/bin/python scripts/session_gate.py
```
After material handoff changes, `scripts/session_gate.py` must finish with `21/21 checks passed — DONE`.

---
**NEXT SESSION START HERE.** Read `HANDOFF.md` first. It is the single durable handoff and binding timestamped initial task message. This pointer intentionally contains no runner, gate, progress, pacing, or campaign state — re-derive all live state with `bash scripts/next_c25_action.sh` and obey its `ACTION:` line.