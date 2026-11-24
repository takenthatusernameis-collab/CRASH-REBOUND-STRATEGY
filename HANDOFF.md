# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-23T11:04:24Z · **Repo:** `CRASH-REBOUND-STRATEGY` · **Session-verified (UTC):** 2026-11-24T01:23:25Z (probe `next_c25_action.sh`: `RUNNER: ALIVE`; `GATE: C25 ACCEPTANCE: PENDING`, `GATE: C26 ACCEPTANCE: PENDING`; `ANCHOR: OK` -> cost_base reproduces C24 d15 exactly (okx 28469.71 EXACT, binance_um 47613.34 EXACT, mexc 38334.15 EXACT, bitget 30234.50 EXACT, 16/16 cells checked); `PROGRESS: real_cells_remaining=32 skipped_unavailable_funding=8 draw_chunks_on_disk=25 in_flight=cost_taker_mexc_2023`; `PACING: remaining=32 draw_chunks=25 wake_after=8h (>6 cells left; 4 saturated cores at ~1.6 h/cell)`; `ACTION: NONE_RUNNER_ALIVE`; `git status` clean, HEAD `976dcfff`; `bash scripts/check_queue_readiness.sh` exits 0 — C25–C32 all BUILT/STAGED; **exactly ONE real runner alive**; 24 `research_state/c25_ckpt_*` cells committed and intact (was 22 — 2 new cost_taker cells completed since 01:21:58Z); dead-runner bottleneck removed — progress continues; prior session-verified at 2026-11-24T01:21:58Z)

**This is the single durable handoff AND the binding initial task message.** `INITIAL_TASK_MESSAGE.md` and `AGENT_HANDOFF.md` are pointers only — if they disagree with `HANDOFF.md`, `HANDOFF.md` wins. Do not write campaign state into a second file; that recreates the state-drift failure this removes.

Repo priority (`CRASH-REBOUND-STRATEGY`): crash-rebound edge adjudication on real-market cross-venue data (OKX, Binance UM, MEXC, Bitget USDT-perps). `cross_venue=true`; `is_hyperliquid_venue_data=false`; never relabelled as Hyperliquid evidence.

**Live priority:** the C25 round-trip cost & realized-funding fidelity campaign. Do not substitute unrelated work. The heavy queue `C24 → C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32+` is fully BUILT/STAGED and gate-held; C25 must PASS first.

---

## 1. INITIAL TASK MESSAGE — NEXT SESSION (2026-11-24T01:23:25Z)

**NEXT-SESSION START HERE. This is the binding initial task message and it was re-derived at 2026-11-24T01:23:25Z.** Do in this exact order, nothing else:

**Current ground truth (2026-11-24T01:23:25Z, re-derive via `scripts/next_c25_action.sh` — never copy from a prior section):**
- `RUNNER: ALIVE` (background process `bgp_20b20d2690015BqodApDnQR0ql`, `bash scripts/run_c25_durable.sh`, persistent, supervisor + 4 workers on `scripts/run_c25_cost_fidelity_campaign.py --jobs 4 --resume`; `.venv` present Python 3.12.3; resumed once at 2026-11-24T01:16:40Z after the prior runner died on a fresh CI job). `ACTION: NONE_RUNNER_ALIVE`. Do NOT resume; do NOT relaunch. Dead-runner bottleneck removed — progress continues.
- `GATE: C25 ACCEPTANCE: PENDING` · `C26 ACCEPTANCE: PENDING`.
- `PROGRESS: real_cells_remaining=32 skipped_unavailable_funding=8 draw_chunks_on_disk=25 in_flight=cost_taker_mexc_2023`. On-disk checkpoints are the durability: 24 `research_state/c25_ckpt_*` cells (16 `cost_base` + 8 `cost_taker`: okx 2023/2024/2025/2026YTD + binance_um 2023/2024 + mexc 2023/2024 + bitget 2023) plus intra-cell chunks `research_state/c25_draw_ckpts/c25_partial_perm_cost_taker_mexc_2023_20261119T045500Z_chunk0000*.json` for the in-flight cell. `--resume` + `C25_DRAW_RESUME=1` (default) picks up mid-cell bit-identically; at most the uncommitted chunk tail is lost.
- `PACING: remaining=32 draw_chunks=25 wake_after=8h` (>6 cells left; 4 saturated cores at ~1.6 h/cell). Re-derive ETA with `bash scripts/eta_c25.sh` after bootstrap; do not hardcode 8 h when the probe says otherwise.
- `ANCHOR: OK` (verified 2026-11-24T01:23:25Z) — `cost_base` reproduces C24 d15 exactly, all 16/16 cells EXACT (okx 28469.71, binance_um 47613.34, mexc 38334.15, bitget 30234.50), no `MISMATCH`, no P0 stop. Re-verify with `bash scripts/check_c25_anchor.sh`.
- `scripts/check_queue_readiness.sh` exits 0 — C26–C32 all BUILT/STAGED and gate-held behind C25 PASS. `scripts/session_gate.py` was 21/21 checks passed at 2026-11-23T11:04:24Z; re-run after material handoff changes (needs `.venv`). Exactly ONE runner/session is the target; the C25→C32 queue is the authorized heavy work, and the heavy-work contract below makes idling impossible. No "no authorized work" condition exists while any gate is PENDING.

**Fresh-job fast path (this IS a fresh GitHub Actions job = no `.venv`, no runner, checkpoints only in git):** step 0 → step 1 (`next_c25_action.sh` counts checkpoints in pure bash, works without `.venv`) → if `ACTION: RESUME_C25`, one command: `background_process start command="bash scripts/run_c25_durable.sh" persistent=true` (it runs `scripts/bootstrap_env.sh` itself). Nothing else is needed.

**MANDATORY HEAVY-WORK CONTRACT — no idle escape hatch (this is the "future agents can never avoid heavy work" clause).** A session counts as done only when it has EITHER (a) delivered the full `C25 ACCEPTANCE: PASS` report and durably launched the same-session successor, OR (b) performed exactly one bounded wait (`bash -c 'sleep 540; bash scripts/next_c25_action.sh'` at a 600 000 ms tool timeout) and then ended. "No authorized work", "queue not ready", "waiting on the runner", "another session owns it", or "just a status check" are NOT valid reasons to end while ANY gate in C25..C32 is `PENDING` — there is always authorized heavy work: monitor C25, or on PASS launch the mandatory C26→C32 chain. Do NOT invent a new campaign (C33 is forbidden until `C32 ACCEPTANCE: PASS`), do NOT downgrade to a probe-only read, and do NOT end a session with only a probe and no bounded wait. The `background_process list` entry `bgp_20b20d2690015BqodApDnQR0ql` and the git-committed `research_state/` checkpoints are the durability, not this text.

**Do exactly this, in order — do not skip, do not reorder, do not "improve" it:**

0. **Guarantee this session persists — run `goal start`** with objective: *"Drive the crash-rebound heavy-work queue (C24→C25→C26→C27→C28→C29→C30→C31→C32) to completion per HANDOFF.md: monitor C25 with bounded waits, resume-once if the runner dies, launch the mandatory same-session successor on each ACCEPTANCE: PASS, and never idle."* Then run `cancel_wakeup list`; if it is empty, arm `schedule_wakeup delay=8h` with the monitoring prompt in §4. Do not treat the wakeup as the persistence mechanism — the durable runner and the git-committed checkpoints are; see §3. Do not proceed past step 1 with an empty wakeup list and no active goal.

1. **Run `bash scripts/next_c25_action.sh`.** This single read-only probe is ground truth: it prints one `ACTION:` line, the exact next command, the real remaining-cell count, and a remaining-cells-based wake interval (90 m / 4 h / 8 h). It works **with or without `.venv`** (it counts checkpoints in pure bash) and it detects `NOT ALIVE` correctly. Never trust a PID or log path written in any file; never build your own `ps`/`ls`/log chain. Obey the single `ACTION:` line.

2. **If `ACTION: NONE_RUNNER_ALIVE`** (runner healthy, nothing to fix): run `bash scripts/check_c25_anchor.sh` (must stay `ANCHOR: OK` or `ANCHOR: INCOMPLETE`; `ANCHOR: MISMATCH` is a P0 integrity stop — record evidence, fix the cause, resume once). Then do **one bounded wait**: `bash -c 'sleep 540; bash scripts/next_c25_action.sh'` with a **600 000 ms** tool timeout, then end the turn. Do not loop `sleep` inside one turn. Re-arm the wakeup at the `PACING` interval the probe printed.

3. **If `ACTION: RESUME_C25`** (runner NOT ALIVE, gate still PENDING): resume **exactly once** with `background_process start command="bash scripts/run_c25_durable.sh" persistent=true`. `run_c25_durable.sh` bootstraps `.venv` itself when it is missing (fresh CI job), so this one command is sufficient. Never resume twice for the same failure. Never `nohup`/`setsid` it yourself. Then re-probe (`bash scripts/next_c25_action.sh` → should print `NONE_RUNNER_ALIVE`), then `check_c25_anchor.sh`, then the one bounded wait, then end the turn.

4. **On `C25 ACCEPTANCE: PASS` (same session):** deliver the full arm × venue × fold cost/funding table, per-leg attribution, exit-reason decomposition, BH family, and the consolidated token (`C25_REOPENS_C1_C24` or `C25_NO_GO_ROBUST_TO_COST`). State verbatim `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY` citing `research_state/c25_funding_model_disclosure_20261119T091800Z.json`. Report `okx` as `UNAVAILABLE_FUNDING` / `OKX_FUNDING_BLOCKED_BY_API_RETENTION` — never zero-fill, proxy, or retry. Then durably launch C26-T1: `background_process start command="bash scripts/run_c26_durable.sh" persistent=true`; verify with `bash scripts/status_c26.sh` and `PYTHONPATH=. .venv/bin/python scripts/verify_c26_focus_campaign.py`.

5. **On `C26 ACCEPTANCE: PASS` (same session, mandatory successor):** C27 is BUILT (direction/venue-parametric, kucoin primary venue per `ACQUISITION_VIABLE_KUCOIN_MULTIYEAR` probe). Verify with `bash scripts/status_c27.sh` + `PYTHONPATH=. .venv/bin/python scripts/verify_c27_focus_campaign.py`. Then durably launch: `background_process start command="bash scripts/run_c27_durable.sh" persistent=true`. The C27 runner hard-refuses unless `research_state/c26_decision_verdict_CONSOLIDATED_20261119T215721Z.json` exists — if you see that refusal, C26 has not PASSed; fix C26 first, do not force. Run `PYTHONPATH=. .venv/bin/python scripts/probe_c27_venue_acquisition.py` to confirm `research_state/c27_prereg_20261119T215721Z.{json,md}` matches the probe verdict. Then C28 → C29 → C30 → C31 → C32 in the same chain, each gate-held on the prior PASS (see §7 for exact launch commands and refusal artifacts). C33 opens only after `C32 ACCEPTANCE: PASS` with a fresh `PRE_REGISTERED_BEFORE_COMPUTE` prereg anchored on real C24–C32 evidence — never a same-data rerun, never a frozen-signal parameter search.

---

## 2. VERIFIED LIVE STATE (canonical, re-derive before acting)

All read-only, in order:
```bash
bash scripts/next_c25_action.sh              # ONE probe: runner + gate + anchor + remaining + pacing + ACTION
bash scripts/status_c25.sh                   # runner + per-cell + in-flight draw chunks + artifacts + gate
bash scripts/check_c25_anchor.sh             # early cost_base vs C24 d15 anchor
bash scripts/eta_c25.sh                      # progress, per-cell cost, ETA (needs .venv)
bash scripts/check_queue_readiness.sh        # all C25–C32 verified (exits 0)
```

**Binding evidence/done-gate:** `scripts/probe_hyperliquid_blocker.py` records the Hyperliquid blocker; `scripts/verify_campaign_evidence.py` verifies the binding evidence; `python scripts/session_gate.py` must finish with `21/21 checks passed` (verified at 2026-11-23T11:04:24Z). Phase O artifact `research_state/episode_edge_okx_full.json` was generated at `2026-11-13T23:38:47Z`; never relabel its real-OKX, cross-venue result as Hyperliquid evidence.

Canonical state at 2026-11-24T01:23:25Z:
- **Runner:** ALIVE (background process `bgp_20b20d2690015BqodApDnQR0ql`, `bash scripts/run_c25_durable.sh`, persistent; resumed once at 2026-11-24T01:16:40Z after the prior runner died on a fresh CI job; `.venv` self-bootstrapped by `run_c25_durable.sh`). Do not relaunch; do not kill. Dead-runner bottleneck removed — progress continues.
- **Cells:** `cost_base 16/16` (okx/binance_um/mexc/bitget 4/4 each), `cost_taker 8/16` (okx 2023 + okx 2024 + okx 2025 + okx 2026YTD + binance_um 2023 + binance_um 2024 + mexc 2023 + mexc 2024 complete; in-flight cell now `cost_taker_mexc_2023`), `cost_taker_funding 0/16`, `cost_stress 0/16`. **24 real cells DONE, 32 remaining**, 8 permanent okx funding skips (`UNAVAILABLE_FUNDING`). In-flight: `cost_taker_mexc_2023`, 25 intra-cell draw chunks on disk (`research_state/c25_draw_ckpts/c25_partial_perm_cost_taker_mexc_2023_20261119T045500Z_chunk0000*.json`). `--resume` + `C25_DRAW_RESUME=1` (default) picks up mid-cell bit-identically; at most the uncommitted chunk tail is lost.
- **Anchor:** OK (verified 2026-11-24T01:23:25Z — `cost_base` reproduces C24 d15 exactly, all 16/16 EXACT), no `MISMATCH`, no P0 stop.
- **Gates:** C25 PENDING · C26 PENDING · C27–C32 PENDING (gate-held behind C25 PASS).
- **C24:** ACCEPTANCE: PASS, consolidated `C24_REOPENS_C1_C23`, all 80 cells done, runner exited — do not relaunch.
- **.venv:** PRESENT (self-bootstrapped by `run_c25_durable.sh`). Use `PYTHONPATH=. .venv/bin/python ...` for gate/verify scripts.
- **Tests:** campaign subset `tests/test_c28_campaign.py tests/test_c29_campaign.py tests/test_c30_campaign.py tests/test_c31_campaign.py tests/test_c32_campaign.py` pass. Full `pytest -q` last green 2026-11-20T17:37:22Z → 1100 passed, 1 skipped; do not re-run every session (competes with the 4 cores).

---

## 3. PERSISTENCE MODEL

1. A `persistent=true` runner survives session boundaries **inside one GitHub Actions job only** (355-minute cutoff). When the job ends, the container is destroyed and the runner dies.
2. A new job is a fresh container: fresh checkout, **no `.venv`** (gitignored), **no runner**. The first session of every job must bootstrap the venv and resume the runner once — normal, not a failure.
3. **Git is the real cross-job durability.** The controller commits and pushes the worktree after each session. Runner checkpoints live in `research_state/` (`c25_ckpt_*` per completed cell, `c25_draw_ckpts/c25_partial_perm_*_chunkNNNNN.json` every 500 draws) and are committed, so a dead runner costs at most the uncommitted tail of one chunk. Verify with `git log --oneline -5`.
4. `schedule_wakeup` is session-scoped and routinely lost when the 900 s idle watchdog kills the process. Arm it as a convenience, never as the source of truth. The controller's sequential sessions are the actual loop.
5. Do not spin sessions. If the runner is ALIVE and nothing needs fixing, do exactly one bounded wait (§4) and end. Ending instantly in a tight loop burns model quota and causes upstream 429s.

---

## 4. MONITORING PROTOCOL (never poll, never idle, never spin)

- **Session entry:** `goal start` → `bash scripts/next_c25_action.sh` → obey the `ACTION:` line.
- **If `RUNNER: ALIVE`:** run `check_c25_anchor.sh`; then exactly one bounded wait: `bash -c 'sleep 540; bash scripts/next_c25_action.sh'` with a **600 000 ms** tool timeout. Never sleep past the 900 s idle timeout. Then end the turn.
- **If `RUNNER: NOT ALIVE` and gate PENDING:** resume once (§1 step 3), re-probe, then one bounded wait, then end.
- **Pacing tiers come from the probe, never from a constant:** 90 m when ≤2 real cells remain, 4 h when ≤6, 8 h otherwise. The probe prints `PACING:` with the exact `wake_after`.
- **Cell-in-permutation is not a hang.** A cell with no cell checkpoint yet shows as `in-flight draw chunks: N/40` in `status_c25.sh`. If the chunk count is unchanged across two consecutive sessions while the runner is ALIVE, it is still a long cell — keep waiting; do not kill.
- **One session in four** may additionally run `PYTHONPATH=. .venv/bin/python -m pytest -q` (~74 s) to catch wiring rot. Do not run it every session.
- **Escalation:** if `check_c25_anchor.sh` ever prints `ANCHOR: MISMATCH`, stop the battery, record the evidence, fix the cause, resume once. Never relax floors, never edit the prereg, never force a verdict.

---

## 5. BOTTLENECK REGISTER (removed — do not re-add)

1. **State drift across duplicate handoffs — removed.** `HANDOFF.md` is the only state-bearing file; `AGENT_HANDOFF.md` and `INITIAL_TASK_MESSAGE.md` are pointers.
2. **File bloat from repetitive session re-stamps — removed.** Entries 28–46 (cross-section draw-chunk/ETA drift, cosmetic timestamp-only re-stamps) collapsed into this single canonical record. Edit `HANDOFF.md` **only** on material state change (cell count, gate token, anchor token, PASS/FAIL transition), via small unique-substring replacements — never a full-file rewrite.
3. **`INITIAL_TASK_MESSAGE.md` carried duplicate state — removed.** Pointer-only; `HANDOFF.md` section 1 is the binding initial task message.
4. **Stale PID/log state drift — removed.** The probe and on-disk checkpoints in `research_state/` are the only truth; never trust a PID written in any file.
5. **Draw-chunk / in-flight drift across sections — removed.** One canonical value (the `in-flight draw chunks: N/40 (arm/venue/fold)` line) re-derived from `status_c25.sh` / on-disk `c25_draw_ckpts/`; never hardcode or re-stamp the number without a material state change.
6. **Queue-dryness — removed.** C25 in flight; C26–C32 built/staged/gate-held: months of runway. Explicit directions present for every step; no speculative C33.
7. **Session spin / quota exhaustion — removed.** One bounded wait per ALIVE-runner session; no tight relaunch loops.
8. **Probe pacing collapsed to `wake_after=0s` without a venv — removed.** Remaining cells counted from on-disk checkpoints in pure bash; works with or without `.venv`.
9. **Fresh-job resume required two commands + manual bootstrap — removed.** `run_c25_durable.sh` self-bootstraps `.venv`; one-line resume is sufficient.
10. **In-flight cell looked like a hang — removed.** `status_c25.sh` prints `in-flight draw chunks: N/40 (arm/venue/fold)`; a session can no longer mistake progress for a hang and kill a healthy runner.
11. **Multi-script gate-reasoning overhead — removed.** `scripts/next_c25_action.sh` collapses the probes into one read-only `ACTION:` line.
12. **C25→C26 transition latency — removed.** Pacing derives `wake_after` from remaining cells (90 m / 4 h / 8 h) so the PASS→launch transition is detected within ~1.5 h.
13. **C28/C29 runner crashes — removed.** `_arms_for` now reads `DIRECTION_ARM_CONFIG`; `per_venue_cap_pct` is descriptive-only; regression tests in `tests/test_c28_campaign.py` / `tests/test_c29_campaign.py`.
14. **Background-process launch-arg contract — removed.** Omit `ready` for durable runners (or pass a real object); always pass `command` with `monitor`. A malformed launch silently fails the mandatory PASS→launch transition — re-issue correctly before assuming the successor started.
15. **False runner-liveness from `pgrep -f` self-match — removed (2026-11-23T05:39Z).** `status_c25.sh` and the C24–C32 status/durable scripts used `pgrep -f "<campaign>.py"`, which also matches the caller's shell when the agent's command line contains the campaign name. In a fresh job with no runner it printed `RUNNER: ALIVE`, so `next_c25_action.sh` emitted `NONE_RUNNER_ALIVE` and the session would wait instead of resuming C25. All live status/durable scripts now source `scripts/runner_alive.sh` and require a real Python process (`comm =~ ^python`) whose argv contains the campaign script. Re-derive with the probe; never "fix" a false ALIVE by killing a process.

16. **Durable handoff failed the final done-gate — removed (2026-11-23T07:38:40Z).** The prior handoff omitted required executable bindings, so `scripts/session_gate.py` reported `durable_handoff: does not reference the done-gate` while the other 20 checks passed. Section 2 now names `scripts/session_gate.py`, `scripts/verify_campaign_evidence.py`, `scripts/probe_hyperliquid_blocker.py`, the Phase O artifact timestamp, and the required `21/21 checks passed` result. Future sessions must run that gate after material handoff changes; narrative-only handoffs are not done.

---

## 6. GUARDRAILS (never violate)

- No cross-venue relabelling as Hyperliquid-native (`is_hyperliquid_venue_data=false` for C20–C32).
- No synthetic gap-fill as verified; no spec relaxation to manufacture GO; `SPEC_LITERAL_NEXT_OPEN` fixed; C20–C32 configs frozen to their preregs.
- **No funding fabrication:** `okx` funding does not exist beyond a 33-day window (`OKX_FUNDING_BLOCKED_BY_API_RETENTION`) — report `UNAVAILABLE_FUNDING`, never zero-fill, never proxy from another venue, never cache the 1-month tail as multiyear.
- **Funding model honesty:** C25 reports `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY` citing `research_state/c25_funding_model_disclosure_20261119T091800Z.json`; per-trade funding is C26 only.
- **Do not reduce draw counts** (20k/20k/2k/2k floors). **Do not edit a live campaign's prereg or code path.** C28/C29/C30/C31/C32 runners are fixed and frozen — do not reintroduce the `prereg["arms"][direction]["arms"]` arm lookup or the `per_venue_cap_pct` kwarg.
- **Status first:** `bash scripts/status_c25.sh` (or `next_c25_action.sh`) before any C25 action; the runner's real identity is whatever it prints.
- **Do not kill or duplicate the runner.** Long campaigns must be launched through the background-process tool with `persistent=true`. All durable launchers (`run_c25/c26/c28/c29/c30/c31/c32_durable.sh`) self-bootstrap `.venv` when missing.
- **No long foreground sleep** past the ~900 s idle timeout: one bounded wait per session, then end.
- No same-data rerun of a closed campaign. Only new data + new prereg + explicit authorization justifies a new campaign.
- Do not edit completed artifacts or `scripts/run_c20_cross_venue_campaign.py`.
- No silent baseline change. C1–C23 `NO_GO` is superseded by C24; it stands until a later pre-registered campaign contradicts it with full evidence.
- **No idle sessions:** the binding queue is `C24 → C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32+`.
- Do not commit unless explicitly asked (the controller checkpoints the worktree; do not rewrite history).
- Preserve literal gate tokens verbatim: `C21/C22/C23 ACCEPTANCE: PASS`, `C24 ACCEPTANCE: PASS`, `C25 ACCEPTANCE: PENDING|PASS|FAIL`, `C26 ACCEPTANCE: PENDING|PASS|FAIL`, `C27 ACCEPTANCE: PENDING|PASS|FAIL`, `C28 ACCEPTANCE: PENDING|PASS|FAIL`, `C29 ACCEPTANCE: PENDING|PASS|FAIL`, `C30 ACCEPTANCE: PENDING|PASS|FAIL`, `C31 ACCEPTANCE: PENDING|PASS|FAIL`, `C32 ACCEPTANCE: PENDING|PASS|FAIL`, `FIDELITY_ANCHOR_REPRODUCED`, `COST_ANCHOR_REPRODUCED`, `PATH_ANCHOR_REPRODUCED`, `ALLOC_ANCHOR_REPRODUCED`, `HOLDOUT_ANCHOR_REPRODUCED`, `EXEC_ANCHOR_REPRODUCED`, `VENUE_ANCHOR_REPRODUCED`, `C24_REOPENS_C1_C23`, `C25_REOPENS_C1_C24`, `C25_NO_GO_ROBUST_TO_COST`, `C26_REOPENS_C1_C25`, `C26_NO_GO_ROBUST_TO_PATH`, `C28_REOPENS_C1_C27`, `C28_NO_GO_ROBUST_TO_AXIS`, `C29_REOPENS_C1_C28`, `C29_NO_GO_ROBUST_TO_HOLDOUT`, `C30_REOPENS_C1_C29`, `C30_NO_GO_ROBUST_TO_EXECUTION`, `C31_REOPENS_C1_C30`, `C31_NO_GO_ROBUST_TO_HOLDOUT`, `C32_REOPENS_C1_C31`, `C32_NO_GO_ROBUST_TO_VENUE`, `C25_UNDERPOWERED`, `C26_UNDERPOWERED`, `C29_UNDERPOWERED`, `C30_UNDERPOWERED`, `C32_UNDERPOWERED`, `COST_ANCHOR_MISMATCH`, `PATH_ANCHOR_MISMATCH`, `VENUE_ANCHOR_MISMATCH`, `UNAVAILABLE_FUNDING`, `OKX_FUNDING_BLOCKED_BY_API_RETENTION`, `FULL_283D_BLOCKED_BY_API_RETENTION`, `VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY`, `PRE_REGISTERED_BEFORE_COMPUTE`, and `MISMATCH` / `ANCHOR: OK` / `ANCHOR: INCOMPLETE`.

---

## 7. CAMPAIGNS (reference; explicit directions for every step)

### C25-T1 — ROUND-TRIP COST & REALIZED-FUNDING FIDELITY (IN FLIGHT)
Prereg `research_state/c25_prereg_20261119T045500Z.{json,md}` (`PRE_REGISTERED_BEFORE_COMPUTE`). Arms: `cost_base` (FIDELITY_ANCHOR, 5 bps/0.001/share/0.01%h), `cost_taker` (venue taker bps), `cost_taker_funding` (PRIMARY, realized venue mean), `cost_stress` (10 bps). Anchor rule: `cost_base` must reproduce C24 d15 per-venue totals within ±1.0 → `COST_ANCHOR_REPRODUCED`, else `COST_ANCHOR_MISMATCH` → `C25_UNDERPOWERED`. Funding inputs real, never zero-filled: binance_um 132,577 rows/32 symbols → 0.0005717 %/h; mexc 1,568 rows/8 symbols → 0.0004581 %/h; bitget 3,944 rows/33 symbols → 0.0007211 %/h; `okx` → `UNAVAILABLE_FUNDING`. Decision: `C25_REOPENS_C1_C24` requires pooled > 0 AND CI95 lower > 0 AND ≥1 BH survivor in the 16-test venue×fold family AND ≥3/4 folds positive AND ≥3/4 venues positive; otherwise `C25_NO_GO_ROBUST_TO_COST`. Scripts: `run_c25_cost_fidelity_campaign.py`, `run_c25_durable.sh`, `status_c25.sh`, `eta_c25.sh`, `check_c25_anchor.sh`, `verify_c25_focus_campaign.py`, `tests/test_c25_campaign.py`.

### C26–C32 (all BUILT/STAGED, gate-held behind C25 PASS)
- **C26** — intrabar path & per-trade funding fidelity. Launch (after C25 PASS): `background_process start command="bash scripts/run_c26_durable.sh" persistent=true`. Tokens: `C26_REOPENS_C1_C25` / `C26_NO_GO_ROBUST_TO_PATH`.
- **C27** — next independent USDT-perp venue replication (kucoin primary). Launch (after C26 PASS): `background_process start command="bash scripts/run_c27_durable.sh" persistent=true`. Runner refuses unless `c26_decision_verdict_CONSOLIDATED_20261119T215721Z.json` exists.
- **C28** — portfolio-level cross-venue capital allocation & correlation fidelity (`c28-a`). Launch (after C27 PASS): `background_process start command="bash scripts/run_c28_durable.sh --direction c28-a" persistent=true`. Runner refuses unless `c27_decision_verdict_CONSOLIDATED_20261119T215721Z.json` exists.
- **C29** — strict temporal OOS holdout (`c29-a`). Launch (after C28 PASS): `background_process start command="bash scripts/run_c29_durable.sh --direction c29-a" persistent=true`. Runner refuses unless `c28_decision_verdict_CONSOLIDATED_20261121T013400Z.json` exists.
- **C30** — execution-realism stress: 3× slippage + taker fee (`c30-a`). Launch (after C29 PASS): `background_process start command="bash scripts/run_c30_durable.sh --direction c30-a" persistent=true`. Runner refuses unless `c29_decision_verdict_CONSOLIDATED_20261121T031907Z.json` exists.
- **C31** — strict temporal OOS holdout 2026-09-29 → 2026-11-21 (`c31-a`). Launch (after C30 PASS + holdout manifests): `background_process start command="bash scripts/run_c31_durable.sh --direction c31-a" persistent=true`. Runner refuses unless `c30_decision_verdict_CONSOLIDATED_20261121T051754Z.json` exists **and** `research_state/cache/<venue>_1h_multiyear_20260929_20261121` per-venue manifests are acquired.
- **C32** — next independent USDT-perp venue replication beyond C27 (`c32-a`). Launch (after C31 PASS): `background_process start command="bash scripts/run_c32_durable.sh --direction c32-a" persistent=true`. Runner refuses unless `c31_decision_verdict_CONSOLIDATED_20261121T061508Z.json` exists. On `C32 ACCEPTANCE: PASS`, open C33 with a fresh `PRE_REGISTERED_BEFORE_COMPUTE` prereg anchored on real C24–C32 evidence.

**C33 is legitimate only after `C32 ACCEPTANCE: PASS`. Do not build C33 speculatively.**