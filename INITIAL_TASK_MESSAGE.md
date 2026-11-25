# INITIAL TASK MESSAGE — NEXT SESSION (2026-11-25T04:48:21Z)

The binding initial task message is `HANDOFF.md` §1. This pointer intentionally contains no runner, gate, progress, or pacing state.

**Current authoritative state (from HANDOFF.md updated 2026-11-25T04:48:21Z):**

- **Repository priority:** Crash-rebound edge adjudication on real-market cross-venue data (OKX, Binance UM, MEXC, Bitget USDT-perps). `cross_venue=true`; `is_hyperliquid_venue_data=false`.
- **C25 status:** `RUNNER: ALIVE` (resumed at 2026-11-25T04:32:xxZ; `.venv` bootstrapped). `ACTION: NONE_RUNNER_ALIVE`.
- **Gates:** `C25 ACCEPTANCE: PENDING`; `C26 ACCEPTANCE: PENDING`; C27–C32 pending behind predecessors.
- **Progress:** `real_cells_remaining=28 skipped_unavailable_funding=8 draw_chunks_on_disk=34 in_flight=cost_taker_bitget_2023`. `cost_base` 16/16 complete; `cost_taker` 12/16; `cost_taker_funding` 0/16; `cost_stress` 0/16.
- **Anchor:** `OK` — `cost_base` reproduces C24 d15 exactly (OKX 28469.71, Binance UM 47613.34, MEXC 38334.15, Bitget 30234.50).
- **Pacing:** `remaining=28 draw_chunks=34 wake_after=8h` (>6 cells left; 4 saturated cores at ~1.6 h/cell).

**Binding immediate action (from `bash scripts/next_c25_action.sh`):** `ACTION: NONE_RUNNER_ALIVE`.

**Do exactly this, in order:**

1. `bash scripts/next_c25_action.sh` → confirms `ACTION: NONE_RUNNER_ALIVE`
2. `bash scripts/check_c25_anchor.sh` → confirms `ANCHOR: OK`
3. One bounded wait (600 000 ms tool timeout):
   ```bash
   bash -c 'sleep 540; bash scripts/next_c25_action.sh'
   ```
4. End the turn. **Do not** relaunch, kill, reorder, or add CPU-heavy work.
5. Re-arm the wakeup at the newly printed `PACING` interval (currently `wake_after=8h`).
**Heavy-work contract (no idle escape hatch):** While any C25–C32 gate is pending, "waiting on the runner", "queue not ready", and "just a status check" are not valid reasons to stop. The queue C26→C32 is fully built and gate-held. On `C25 ACCEPTANCE: PASS`, C26 **must** be durably launched in the same session (`background_process start command="bash scripts/run_c26_durable.sh" persistent=true`), then C27, ..., through C32. C33 opens only after C32 PASS with a fresh `PRE_REGISTERED_BEFORE_COMPUTE` prereg.

**Verification checks (run in order if needed):**
```bash
bash scripts/next_c25_action.sh
bash scripts/status_c25.sh
bash scripts/check_c25_anchor.sh
bash scripts/check_queue_readiness.sh
PYTHONPATH=. .venv/bin/python scripts/session_gate.py
```
After material handoff changes, `scripts/session_gate.py` must finish with `21/21 checks passed — DONE`.
