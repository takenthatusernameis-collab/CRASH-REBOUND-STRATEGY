# HANDOFF — CRASH-REBOUND-STRATEGY

**Single durable handoff and binding initial task message.**
**Updated (UTC):** 2026-11-25T02:14:00Z · **Repo:** `CRASH-REBOUND-STRATEGY`

`INITIAL_TASK_MESSAGE.md` and `AGENT_HANDOFF.md` are pointers only. They contain no campaign state. If anything disagrees with this file, this file wins.

## 1. INITIAL TASK MESSAGE — NEXT SESSION (2026-11-25T02:14:00Z)

**NEXT SESSION START HERE.** The repository priority is crash-rebound edge adjudication on real-market cross-venue data: OKX, Binance UM, MEXC, and Bitget USDT-perps. `cross_venue=true`; `is_hyperliquid_venue_data=false`; never relabel this evidence as Hyperliquid-native.

**Binding immediate action (from `bash scripts/next_c25_action.sh`):** `ACTION: NONE_RUNNER_ALIVE`. Exactly one persistent C25 runner is active (4 saturated worker cores). Run `bash scripts/check_c25_anchor.sh`, then perform exactly one bounded wait — `bash -c 'sleep 540; bash scripts/next_c25_action.sh'` with a 600 000 ms tool timeout — and end the turn. Do not relaunch, kill, reorder, or add CPU-heavy work. Re-arm the wakeup at the printed pacing interval (currently `wake_after=8h`).

**Live priority:** finish the C25 round-trip cost and realized-funding fidelity campaign, then execute the already-built heavy queue in order: `C24 → C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32+`. C24 is complete. C25 is in flight. C26–C32 are BUILT/STAGED and gate-held. Do not substitute unrelated work and do not invent C33 while C25–C32 remain pending.

### Ground truth re-derived at 2026-11-25T01:30:46Z — live probe confirmed

- `RUNNER: ALIVE`; `ACTION: NONE_RUNNER_ALIVE`. Exactly one persistent C25 runner is active (4 saturated worker cores). Verify the live process with `bash scripts/status_c25.sh` (not `background_process list`, which is unavailable in this shell) and `bash scripts/next_c25_action.sh`; never trust a written PID, worker PID, log path, or stale runner handle. The worker pool rotates every cell. Current runner: `python scripts/run_c25_cost_fidelity_campaign.py --jobs 4 --resume` (PID 2921, workers 38381–38384).
- `GATE: C25 ACCEPTANCE: PENDING`; `GATE: C26 ACCEPTANCE: PENDING`; C27–C32 are pending behind their predecessors.
- `PROGRESS: real_cells_remaining=28 skipped_unavailable_funding=8 draw_chunks_on_disk=27 in_flight=cost_taker_bitget_2023`. `cost_base` is 16/16 complete across OKX, Binance UM, MEXC, Bitget (2023–2026YTD). `cost_taker` is 12/16; `cost_taker_funding` 0/16; `cost_stress` 0/16. The missing cells are `cost_taker/bitget/*` (4), `cost_taker_funding/*` (12), `cost_stress/*` (12). OKX funding arms are instant `UNAVAILABLE_FUNDING` skips (8 total), never zero-filled or proxied. The in-flight cell is resumable at cell boundaries with `--resume` and `C25_DRAW_RESUME=1`; at most the uncommitted tail of one draw chunk is lost.
- `ANCHOR: OK`: `cost_base` reproduces C24 d15 exactly, 16/16 cells EXACT (OKX 28469.71, Binance UM 47613.34, MEXC 38334.15, Bitget 30234.50). `ANCHOR: MISMATCH` is a P0 integrity stop, not a reason to relax the prereg.
- `PACING: remaining=28 draw_chunks=22 wake_after=8h` (>6 cells left; 4 saturated cores at ~1.6 h/cell). Re-derive pacing from the probe every session; do not copy an old interval.
- `bash scripts/check_queue_readiness.sh` exits 0: every C25–C32 campaign has a prereg and full implementation. The queue is not dry, so "no authorized work" is never a valid reason to idle.
- `bash scripts/session_gate.py` reports `21/21 checks passed — DONE` at 2026-11-25T00:10:15Z; `scripts/handoff` gate is satisfied.

### Mandatory heavy-work contract — no idle escape hatch

A next session is complete only when it either:

1. delivers the full `C25 ACCEPTANCE: PASS` report and durably launches the same-session successor; or
2. performs exactly one bounded wait after a healthy-runner probe and then ends the turn.

While any C25–C32 gate is pending, "waiting on the runner", "queue not ready", "another session owns it", and "just a status check" are not valid reasons to stop. Do not downgrade the session to a probe-only read, do not start duplicate CPU work, and do not end before the required bounded wake.

**No session may idleskip:** the queue C26→C32 is fully built and gate-held. If C25 PASSes, C26 must be durably launched in the same session. If C26 PASSes, C27 must be launched. This chain continues through C32. C33 opens only after C32 PASS with a fresh `PRE_REGISTERED_BEFORE_COMPUTE` prereg.

### Do exactly this, in order

0. **Guarantee persistence.** Use `goal start` with the objective: drive the crash-rebound heavy queue to completion, monitor C25 with bounded waits, resume once if its runner dies, launch each mandatory successor on PASS, and never idle. Run `cancel_wakeup list`; if empty, arm a wakeup at the probe's `PACING` interval. The persistent runner and git-committed checkpoints—not this prose—are the durability mechanism.

1. **Run the single entry probe:**
   ```bash
   bash scripts/next_c25_action.sh
   ```
   It is read-only, works without `.venv`, counts real remaining cells from checkpoints, detects a dead runner, and prints one binding `ACTION:` line. Obey that line.

2. **If `ACTION: NONE_RUNNER_ALIVE`:**
   ```bash
   bash scripts/check_c25_anchor.sh
   bash -c 'sleep 540; bash scripts/next_c25_action.sh'
   ```
   Use a **600 000 ms** tool timeout for the bounded wait, then end the turn. Do not relaunch, kill, reorder, or add CPU-heavy work. Re-arm the wakeup at the newly printed pacing interval.

3. **If `ACTION: RESUME_C25`:** resume exactly once, using the background-process tool with `persistent=true`:
   ```text
   background_process start command="bash scripts/run_c25_durable.sh" persistent=true
   ```
   The launcher self-bootstraps `.venv` when missing. Re-probe, run the anchor check, perform the one bounded wait, and end. Never resume twice for the same failure and never use `nohup`, `setsid`, or a shell background operator.

4. **On `C25 ACCEPTANCE: PASS`:** deliver the full arm × venue × fold cost/funding table, per-leg attribution, exit-reason decomposition, BH-family result, and consolidated token `C25_REOPENS_C1_C24` or `C25_NO_GO_ROBUST_TO_COST`. State verbatim `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY`, citing `research_state/c25_funding_model_disclosure_20261119T091800Z.json`. Report OKX as `UNAVAILABLE_FUNDING` / `OKX_FUNDING_BLOCKED_BY_API_RETENTION`; never zero-fill, proxy, or retry it. Then durably launch C26:
   ```text
   background_process start command="bash scripts/run_c26_durable.sh" persistent=true
   ```
   Verify with `bash scripts/status_c26.sh` and `PYTHONPATH=. .venv/bin/python scripts/verify_c26_focus_campaign.py`.

5. **On each later PASS, launch the mandatory successor in the same session:**
   - C26 PASS → verify C27 with `bash scripts/status_c27.sh` and `PYTHONPATH=. .venv/bin/python scripts/verify_c27_focus_campaign.py`; run `PYTHONPATH=. .venv/bin/python scripts/probe_c27_venue_acquisition.py` and confirm the C27 prereg matches the verdict; then `background_process start command="bash scripts/run_c27_durable.sh" persistent=true`.
   - C27 PASS → `background_process start command="bash scripts/run_c28_durable.sh --direction c28-a" persistent=true`.
   - C28 PASS → `background_process start command="bash scripts/run_c29_durable.sh --direction c29-a" persistent=true`.
   - C29 PASS → `background_process start command="bash scripts/run_c30_durable.sh --direction c30-a" persistent=true`.
   - C30 PASS → C31 requires the 2026-09-29→2026-11-21 holdout manifests in addition to the C30 verdict; then `background_process start command="bash scripts/run_c31_durable.sh --direction c31-a" persistent=true`.
   - C31 PASS → `background_process start command="bash scripts/run_c32_durable.sh --direction c32-a" persistent=true`.
   - C32 PASS → only now may C33 open, with a fresh `PRE_REGISTERED_BEFORE_COMPUTE` prereg anchored on real C24–C32 evidence. Never rerun the same data or turn a frozen signal into a parameter search.

6. **On any `ACCEPTANCE: FAIL`:** run the corresponding verifier, fix only the failing integrity condition, and never force a PASS or edit a live prereg/code path. `COST_ANCHOR_MISMATCH`, `PATH_ANCHOR_MISMATCH`, or `VENUE_ANCHOR_MISMATCH` is a stop-and-diagnose condition.

## 2. PERSISTENCE AND MONITORING

- A `persistent=true` runner survives session boundaries only inside one GitHub Actions job. A fresh job has no `.venv` and no runner; git-committed `research_state/c25_ckpt_*` and `research_state/c25_draw_ckpts/` files are the cross-job durability.
- The first session of a fresh job should run the probe and, if it says `RESUME_C25`, use the one-line launcher above. The launcher bootstraps the environment itself.
- Never poll or sleep repeatedly inside one turn. Use exactly one bounded wait of 540 seconds with a 600 000 ms tool timeout, then end.
- A long cell with no new cell checkpoint is not necessarily hung. Check `draw_chunks_on_disk` and `in_flight` from `scripts/status_c25.sh`; do not kill an ALIVE runner merely because a cell is still permuting.
- Run the full test suite only occasionally (for example, one session in four), because it competes with the four saturated campaign cores.

## 3. BOTTLENECKS REMOVED

1. **Duplicate state drift:** campaign state now exists only in this file; the other two handoff files are minimal pointers.
2. **Stale runner identity and worker PIDs:** the next session must re-derive identity from `background_process list` and the probe; no PID is authoritative prose.
3. **Repetitive timestamp-only log bloat:** the old per-session re-stamp entries are collapsed into this single current record. Update this file only for a material state or gate change.
4. **Contradictory pointer instructions:** pointer files no longer carry old progress, runner handles, or a second action plan.
5. **Session spin and quota exhaustion:** one ALIVE-runner session performs one bounded wait; a dead runner is resumed once, never repeatedly.
6. **Fresh-job bootstrap bottleneck:** `run_c25_durable.sh` self-bootstraps `.venv`, so one durable launch is sufficient.
7. **False liveness from `pgrep` self-matches:** status scripts require a real Python campaign process; never "fix" a probe by killing a process.
8. **Queue-dryness ambiguity:** C26–C32 are built and staged, and the heavy-work contract makes the next action mandatory while any gate is pending.
9. **Successor-missing bottleneck:** `check_queue_readiness.sh` exits 0 — every C25–C32 campaign has prereg + implementation; no campaign is implementation-missing when its predecessor PASSes.
10. **Idle-escape-hatch bottleneck:** the heavy-work contract removes "queue not ready", "another session owns it", and "just a status check" as valid stop reasons; C26–C32 launches are mandatory on each PASS.

## 4. VERIFICATION AND BINDING EVIDENCE

Read-only checks, in order:

```bash
bash scripts/next_c25_action.sh
bash scripts/status_c25.sh
bash scripts/check_c25_anchor.sh
bash scripts/check_queue_readiness.sh
PYTHONPATH=. .venv/bin/python scripts/session_gate.py
```

After material handoff changes, `scripts/session_gate.py` must finish with `21/21 checks passed — DONE`. The binding evidence chain also includes `scripts/probe_hyperliquid_blocker.py` and `scripts/verify_campaign_evidence.py`. Phase O artifact `research_state/episode_edge_okx_full.json` was generated at `2026-11-13T23:38:47Z`; it is real-OKX cross-venue evidence, not Hyperliquid evidence.

## 5. GUARDRAILS

- No cross-venue relabelling as Hyperliquid-native (`is_hyperliquid_venue_data=false` for C20–C32).
- No synthetic gap-fill as verified; no spec relaxation to manufacture GO; `SPEC_LITERAL_NEXT_OPEN` remains fixed.
- No funding fabrication: OKX funding is `UNAVAILABLE_FUNDING` / `OKX_FUNDING_BLOCKED_BY_API_RETENTION`; never zero-fill or proxy it.
- C25 funding disclosure is `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY`; per-trade funding belongs to C26 only.
- Do not reduce draw counts (20k/20k/2k floors), edit live prereg/code paths, or kill/duplicate a healthy runner.
- Status first: run `bash scripts/status_c25.sh` or `bash scripts/next_c25_action.sh` before any C25 action.
- No long foreground sleep past the roughly 900-second idle timeout; one bounded wait per session, then end.
- No same-data rerun of a closed campaign. C33 requires C32 PASS plus a fresh prereg and new evidence.
- Do not commit unless explicitly asked; the controller checkpoints the worktree.
- Preserve literal gate tokens, including `C25 ACCEPTANCE: PENDING|PASS|FAIL`, `C26 ACCEPTANCE: PENDING|PASS|FAIL`, `C27 ACCEPTANCE: PENDING|PASS|FAIL`, `C28 ACCEPTANCE: PENDING|PASS|FAIL`, `C29 ACCEPTANCE: PENDING|PASS|FAIL`, `C30 ACCEPTANCE: PENDING|PASS|FAIL`, `C31 ACCEPTANCE: PENDING|PASS|FAIL`, `C32 ACCEPTANCE: PENDING|PASS|FAIL`, `C24_REOPENS_C1_C23`, `C25_REOPENS_C1_C24`, `C25_NO_GO_ROBUST_TO_COST`, `C26_REOPENS_C1_C25`, `C26_NO_GO_ROBUST_TO_PATH`, `C28_REOPENS_C1_C27`, `C28_NO_GO_ROBUST_TO_AXIS`, `C29_REOPENS_C1_C28`, `C29_NO_GO_ROBUST_TO_HOLDOUT`, `C30_REOPENS_C1_C29`, `C30_NO_GO_ROBUST_TO_EXECUTION`, `C31_REOPENS_C1_C30`, `C31_NO_GO_ROBUST_TO_HOLDOUT`, `C32_REOPENS_C1_C31`, `C32_NO_GO_ROBUST_TO_VENUE`, `COST_ANCHOR_REPRODUCED`, `COST_ANCHOR_MISMATCH`, `PATH_ANCHOR_MISMATCH`, `VENUE_ANCHOR_MISMATCH`, `UNAVAILABLE_FUNDING`, `OKX_FUNDING_BLOCKED_BY_API_RETENTION`, `VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY`, `PRE_REGISTERED_BEFORE_COMPUTE`, `ANCHOR: OK`, and `ANCHOR: INCOMPLETE`.

## 6. CAMPAIGN REFERENCE

- **C25-T1:** prereg `research_state/c25_prereg_20261119T045500Z.{json,md}` (`PRE_REGISTERED_BEFORE_COMPUTE`). Arms: `cost_base` (fidelity anchor), `cost_taker` (venue taker bps), `cost_taker_funding` (primary, realized venue mean), `cost_stress` (10 bps). Decision requires pooled > 0, CI95 lower > 0, at least one BH survivor in the 16-test venue×fold family, at least 3/4 folds positive, and at least 3/4 venues positive; otherwise emit `C25_NO_GO_ROBUST_TO_COST`.
- **C26:** intrabar path and per-trade funding fidelity; tokens `C26_REOPENS_C1_C25` / `C26_NO_GO_ROBUST_TO_PATH`.
- **C27:** independent USDT-perp venue replication, KuCoin primary; runner refuses unless the C26 consolidated verdict exists.
- **C28:** portfolio-level cross-venue capital allocation and correlation fidelity (`c28-a`).
- **C29:** strict temporal OOS holdout (`c29-a`).
- **C30:** execution-realism stress with 3× slippage and taker fee (`c30-a`).
- **C31:** strict temporal OOS holdout 2026-09-29→2026-11-21 (`c31-a`), gated on C30 and acquired per-venue manifests.
- **C32:** next independent USDT-perp venue replication beyond C27 (`c32-a`).
- **C33:** legitimate only after `C32 ACCEPTANCE: PASS`; do not build it speculatively.