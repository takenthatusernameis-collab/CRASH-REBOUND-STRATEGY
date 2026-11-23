# INITIAL TASK MESSAGE — NEXT SESSION (2026-11-23T14:14:49Z)

**This file is not a source of truth.** The single durable handoff AND the binding timestamped initial task message live in `HANDOFF.md` §1.

Next session, do exactly this and nothing else:

1. `goal start` (objective is quoted in `HANDOFF.md` §1 step 0), then `cancel_wakeup list`.
2. `bash scripts/next_c25_action.sh` — the single read-only source of truth. Obey its one `ACTION:` line; never build your own `ps`/`ls`/log chain.
3. If `ACTION: NONE_RUNNER_ALIVE` → `bash scripts/check_c25_anchor.sh`, then exactly one bounded wait `bash -c 'sleep 540; bash scripts/next_c25_action.sh'` (600000 ms tool timeout), then end the turn.
4. If `ACTION: RESUME_C25` → resume exactly once: `background_process start command="bash scripts/run_c25_durable.sh" persistent=true` (self-bootstraps `.venv`).
5. On any `ACCEPTANCE: PASS` → launch the mandatory same-session successor per `HANDOFF.md` §1 steps 4–5 and §7.

**Live priority:** C25 round-trip cost & realized-funding fidelity campaign (heavy queue `C24 → C25 → … → C32+`, all BUILT/STAGED and gate-held behind C25 PASS). Repo priority `CRASH-REBOUND-STRATEGY`: crash-rebound edge adjudication on real-market cross-venue data (OKX, Binance UM, MEXC, Bitget USDT-perps); `cross_venue=true`; `is_hyperliquid_venue_data=false`; never relabelled as Hyperliquid evidence.

**Current ground truth (2026-11-23T14:14:49Z):**
- `RUNNER: NOT ALIVE` — fresh CI job at ~13:43Z killed the prior runner and removed the gitignored `.venv`; on-disk `research_state/c25_ckpt_*` (22 cells) + 19 `c25_draw_ckpts/c25_partial_perm_cost_taker_binance_um_2025_*_chunk0000{00..18}.json` are committed and intact. Resume ONCE via `background_process start command="bash scripts/run_c25_durable.sh" persistent=true`; it self-bootstraps `.venv`.
- `GATE: C25 ACCEPTANCE: PENDING` · `C26 ACCEPTANCE: PENDING`
- `PROGRESS: real_cells_remaining=34 draw_chunks_on_disk=19 in_flight=cost_taker_binance_um_2025`
- `ANCHOR: OK` (last verified 2026-11-23T11:04:24Z) — all 16/16 cost_base EXACT vs C24 d15 (okx 28469.71, binance_um 47613.34, mexc 38334.15, bitget 30234.50); re-verify with `bash scripts/check_c25_anchor.sh` after bootstrap.
- `PACING: remaining=34 draw_chunks=19 wake_after=8h` (>6 cells left; 4 saturated cores at ~1.6 h/cell)
- `.venv` absent (Python 3.12.3 once bootstrapped); `scripts/check_queue_readiness.sh` exits 0; `scripts/session_gate.py` 21/21 passed at 2026-11-23T11:04:24Z (re-run after bootstrap).
- Exactly ONE runner/session is the target; NO blocked/duplicate/inefficient sessions to remove.

Read `HANDOFF.md` for the full ordered task list, ground truth, monitoring protocol, persistence model, bottleneck register, guardrails, and the C26–C32 launch chain.