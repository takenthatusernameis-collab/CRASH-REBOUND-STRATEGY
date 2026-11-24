# INITIAL TASK MESSAGE — NEXT SESSION (2026-11-24T02:10:10Z)

**This file is not a source of truth.** The single durable handoff AND the binding timestamped initial task message live in `HANDOFF.md` §1.

Next session, do exactly this and nothing else:

1. `goal start` (objective is quoted in `HANDOFF.md` §1 step 0), then `cancel_wakeup list`.
2. `bash scripts/next_c25_action.sh` — the single read-only source of truth. Obey its one `ACTION:` line; never build your own `ps`/`ls`/log chain.
3. If `ACTION: NONE_RUNNER_ALIVE` → `bash scripts/check_c25_anchor.sh`, then exactly one bounded wait `bash -c 'sleep 540; bash scripts/next_c25_action.sh'` (600000 ms tool timeout), then end the turn.
4. If `ACTION: RESUME_C25` → resume exactly once: `background_process start command="bash scripts/run_c25_durable.sh" persistent=true` (self-bootstraps `.venv`).
5. On any `ACCEPTANCE: PASS` → launch the mandatory same-session successor per `HANDOFF.md` §1 steps 4–5 and §7.

**Live priority:** C25 round-trip cost & realized-funding fidelity campaign (heavy queue `C24 → C25 → … → C32+`, all BUILT/STAGED and gate-held behind C25 PASS). Repo priority `CRASH-REBOUND-STRATEGY`: crash-rebound edge adjudication on real-market cross-venue data (OKX, Binance UM, MEXC, Bitget USDT-perps); `cross_venue=true`; `is_hyperliquid_venue_data=false`; never relabelled as Hyperliquid evidence.

**Current ground truth (2026-11-24T02:10:10Z, re-derive via `scripts/next_c25_action.sh` — never copy from a prior section):**
- `RUNNER: ALIVE` (background process `bgp_20b20d2690015BqodApDnQR0ql`, pid 2766, `bash scripts/run_c25_durable.sh`, persistent, supervisor + 4 workers on `scripts/run_c25_cost_fidelity_campaign.py --jobs 4 --resume`; `.venv` present Python 3.12.3). `ACTION: NONE_RUNNER_ALIVE`. Do NOT resume; do NOT relaunch. Campaign advanced to 24 checkpoint cells; 24 `research_state/c25_ckpt_*` cells committed and intact (16 `cost_base` + 8 `cost_taker`: okx 2023/2024/2025/2026YTD + binance_um 2023/2024 + mexc 2023/2024 + bitget 2023).
- `GATE: C25 ACCEPTANCE: PENDING` · `C26 ACCEPTANCE: PENDING`.
- `PROGRESS: real_cells_remaining=32 skipped_unavailable_funding=8 draw_chunks_on_disk=28 in_flight=cost_taker_mexc_2023`. On-disk checkpoints are the durability: 24 `research_state/c25_ckpt_*` cells (16 `cost_base` + 8 `cost_taker`: okx 2023/2024/2025/2026YTD + binance_um 2023/2024 + mexc 2023/2024 + bitget 2023) plus 30 intra-cell chunks `research_state/c25_draw_ckpts/c25_partial_perm_cost_taker_mexc_2023_20261119T045500Z_chunk0000{00..29}.json` for the in-flight cell. `--resume` + `C25_DRAW_RESUME=1` (default) picks up mid-cell bit-identically; at most the uncommitted chunk tail is lost.
- `PACING: remaining=32 draw_chunks=28 wake_after=8h` (>6 cells left; 4 saturated cores at ~1.6 h/cell). Re-derive ETA with `bash scripts/eta_c25.sh` after bootstrap; do not hardcode 8 h when the probe says otherwise.
- `ANCHOR: OK` (verified 2026-11-24T01:49:06Z) — all 16/16 cost_base EXACT vs C24 d15 (okx 28469.71, binance_um 47613.34, mexc 38334.15, bitget 30234.50), no `MISMATCH`, no P0 stop. Re-verify with `bash scripts/check_c25_anchor.sh` immediately after resume bootstraps `.venv`.
- `scripts/check_queue_readiness.sh` exits 0 — C26–C32 all BUILT/STAGED and gate-held behind C25 PASS. Exactly ONE runner/session is the target; the C25→C32 queue is the authorized heavy work, and the heavy-work contract below makes idling impossible. No "no authorized work" condition exists while any gate is PENDING.

Read `HANDOFF.md` for the full ordered task list, ground truth, monitoring protocol, persistence model, bottleneck register, guardrails, and the C26–C32 launch chain.

(End of file - total 23 lines)