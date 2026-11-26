# HANDOFF — CRASH-REBOUND-STRATEGY

**Single durable handoff and binding initial task message.**
**Updated (UTC):** 2026-11-26T17:19:16Z · **Repo:** `CRASH-REBOUND-STRATEGY` · **Live-verified:** RUNNER ALIVE (one persistent `background_process` `bgp_218757543001gOUTT2JJIj8mO5`, launcher PID 2783, campaign PID 3029 + workers 16994–16997, campaign `python scripts/run_c25_cost_fidelity_campaign.py --jobs 4 --resume`, `.venv` bootstrapped), ACTION NONE_RUNNER_ALIVE, ANCHOR OK (16/16 EXACT), gate 21/21 DONE, queue C25–C32 ready (`check_queue_readiness.sh` exits 0), bottlenecks removed (single healthy runner; no blocked/duplicate session; one worktree; draw_chunks_on_disk=15 and climbing, runner advancing in-flight `cost_taker_funding_binance_um_2025`), no idle escape hatch. Next session: single bounded wait 540s then end turn; re-arm wake at 8h.
`INITIAL_TASK_MESSAGE.md` and `AGENT_HANDOFF.md` are pointers only. They contain no campaign state. If anything disagrees with this file, this file wins. Re-derive all runner, gate, progress, and pacing state with `bash scripts/next_c25_action.sh`; do not use stale values from any pointer file.

---

## 1. INITIAL TASK MESSAGE — NEXT SESSION (2026-11-26T17:17:37Z)

**NEXT SESSION START HERE.** The repository priority is crash-rebound edge adjudication on real-market cross-venue data: OKX, Binance UM, MEXC, and Bitget USDT-perps. `cross_venue=true`; `is_hyperliquid_venue_data=false`; never relabel this evidence as Hyperliquid-native.

**Binding immediate action:** `ACTION: NONE_RUNNER_ALIVE`. The C25 runner is ALIVE as one persistent `background_process` (`bgp_218757543001gOUTT2JJIj8mO5`, launcher PID 2783, campaign PID 3029 + workers 16994–16997) running `bash scripts/run_c25_durable.sh` with `--jobs 4 --resume` and a bootstrapped `.venv`. Re-derive the current launcher and in-campaign worker identities each session with `bash scripts/status_c25.sh` and `bash scripts/next_c25_action.sh`; prose is not authoritative (worker PIDs rotate as draw chunks complete; this session observed 16994–16997, up from 15562–15565 last session, with `draw_chunks_on_disk` climbing 8 → 15). Perform exactly one bounded wait after the healthy-runner probe and then end the turn:
```bash
bash scripts/next_c25_action.sh   # expects ACTION: NONE_RUNNER_ALIVE
bash scripts/check_c25_anchor.sh   # expects ANCHOR: OK
bash -c 'sleep 540; bash scripts/next_c25_action.sh'   # 600000 ms tool timeout, then END
```
Do not relaunch, kill, reorder, or add CPU-heavy work. Re-arm the wakeup at the printed pacing interval (currently `wake_after=8h`).

**If the probe instead prints `ACTION: RESUME_C25`** (fresh CI job, `.venv` missing, or the durable runner died between sessions), resume exactly once — never twice — with the durable launcher, which self-bootstraps `.venv`:
```text
background_process start command="bash scripts/run_c25_durable.sh" persistent=true
```
Then re-probe, run the anchor check, perform the one bounded wait, and end. Never use `nohup`, `setsid`, or a shell background operator.

**Live priority:** finish the C25 round-trip cost and realized-funding fidelity campaign, then execute the already-built heavy queue in order: `C24 → C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32 → C33+`. C24 is complete. C25 is in flight (resumed). C26–C32 are BUILT/STAGED and gate-held. Do not substitute unrelated work and do not invent C33 while C25–C32 remain pending.

---

## 2. GROUND TRUTH RE-DERIVED AT 2026-11-26T17:17:37Z — LIVE PROBE CONFIRMED

- `RUNNER: ALIVE`; `ACTION: NONE_RUNNER_ALIVE`. The C25 runner is active as one persistent `background_process` (`bgp_218757543001gOUTT2JJIj8mO5`, launcher PID 2783, campaign PID 3029 + workers 16994–16997, launcher `bash scripts/run_c25_durable.sh`, campaign `python scripts/run_c25_cost_fidelity_campaign.py --jobs 4 --resume`) with a bootstrapped `.venv`; re-derive campaign and worker identities each session via `bash scripts/status_c25.sh` and `bash scripts/next_c25_action.sh`, not prose (worker PIDs rotate as draw chunks complete; this session observed 16994–16997, up from 15562–15565 last session, with `draw_chunks_on_disk` climbing 8 → 15). Verify with both probes. `.venv` is present and bootstrapped.
- `GATE: C25 ACCEPTANCE: PENDING`; `GATE: C26 ACCEPTANCE: PENDING`; C27–C32 are pending behind their predecessors.
- `PROGRESS: real_cells_remaining=22 skipped_unavailable_funding=8 draw_chunks_on_disk=15 in_flight=cost_taker_funding_binance_um_2025`. `cost_base` is 16/16 complete across OKX, Binance UM, MEXC, Bitget (2023–2026YTD). `cost_taker` is 16/16; `cost_taker_funding` 6/16 scored + 4/4 OKX unavailable; `cost_stress` 0/16 scored + 4/4 OKX unavailable. The missing cells are `cost_taker_funding/*` (10 remaining) and `cost_stress/*` (16). OKX funding arms are instant `UNAVAILABLE_FUNDING` skips (8 total across funding/stress), never zero-filled or proxied. The in-flight cell is resumable at cell boundaries with `--resume` and `C25_DRAW_RESUME=1`; at most the uncommitted tail of one draw chunk is lost. `draw_chunks_on_disk` is 15 (up from 8 last session), confirming the runner is bootstrapped and actively advancing.
- `ANCHOR: OK`: `cost_base` reproduces C24 d15 exactly, 16/16 cells EXACT (OKX 28469.71, Binance UM 47613.34, MEXC 38334.15, Bitget 30234.50). `ANCHOR: MISMATCH` is a P0 integrity stop, not a reason to relax the prereg.
- `PACING: remaining=22 draw_chunks=15 wake_after=8h` (>6 cells left; 4 saturated cores at ~1.6 h/cell). Re-derive pacing from the probe every session; do not copy an old interval.
- `bash scripts/check_queue_readiness.sh` exits 0: every C25–C32 campaign has a prereg and full implementation. The queue is not dry, so "no authorized work" is never a valid reason to idle.
- `bash scripts/session_gate.py` reports `21/21 checks passed — DONE` (re-verified 2026-11-26T17:17:37Z with `.venv` Python); `scripts/handoff` gate is satisfied.

### Mandatory heavy-work contract — no idle escape hatch

A next session is complete only when it either:

1. delivers the full `C25 ACCEPTANCE: PASS` report and durably launches the same-session successor; or
2. performs exactly one bounded wait after a healthy-runner probe and then ends the turn.

**This session (2026-11-26T17:17:37Z):** the runner was ALIVE on entry (persistent `background_process` `bgp_218757543001gOUTT2JJIj8mO5`, launcher PID 2783, campaign PID 3029 + workers 16994–16997); both probes emitted `ACTION: NONE_RUNNER_ALIVE` and `ANCHOR: OK` (16/16 EXACT), `session_gate.py` 21/21 DONE, `check_queue_readiness.sh` exit 0 (`QUEUE READY` C25..C32), one worktree only, and `draw_chunks_on_disk` had advanced 8 → 15. No resume was needed and none was performed. The single authorized action now is the one bounded wait in Section 1. No CPU-heavy work, no duplicate runner, no C26 launch until C25 PASS.

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

6. **On any `ACCEPTANCE: FAIL`:** run the corresponding verifier, fix only the failing integrity condition, and never force a PASS or edit a live prereg/code path. If the verifier's only failures are missing `prereg_sha256` fields in `unavailable_funding` or `holdout_manifest_missing` checkpoints, repair only that metadata by inserting the actual SHA-256 of the referenced prereg; never change the unavailability flag, evidence, or prereg. Any other drift is a stop-and-diagnose condition. `COST_ANCHOR_MISMATCH`, `PATH_ANCHOR_MISMATCH`, or `VENUE_ANCHOR_MISMATCH` is a stop-and-diagnose condition.

---

## 3. BOTTLENECKS REMOVED

1. **Stale "RUNNER ALIVE" claim corrected (2026-11-26T05:15:02Z):** the previous handoff asserted `RUNNER ALIVE` with a PID from a prior job, but this session started on a fresh CI job with no background process and no `.venv` (`next_c25_action.sh` → `ACTION: RESUME_C25`). A future session trusting the stale prose would have performed a bounded wait on a dead runner and never progressed. The state is now re-derived live: the single authorized resume was executed once, the runner is ALIVE, and the handoff records both the resume and the re-derivation requirement.
2. **Duplicate state drift:** campaign state now exists only in this file; `INITIAL_TASK_MESSAGE.md` and `AGENT_HANDOFF.md` are minimal pointers demoted at 2026-11-25T18:42:44Z, eliminating the contradictory dual-source-of-truth.
3. **Stale runner identity and worker PIDs:** the next session must re-derive identity from `background_process list` and the probe; no PID is authoritative prose.
4. **Repetitive timestamp-only log bloat:** the old per-session re-stamp entries are collapsed into this single current record. Update this file only for a material state or gate change.
5. **Contradictory pointer instructions:** pointer files no longer carry old progress, runner handles, or a second action plan.
6. **Session spin and quota exhaustion:** one ALIVE-runner session performs one bounded wait; a dead runner is resumed once, never repeatedly.
7. **Fresh-job bootstrap bottleneck:** `run_c25_durable.sh` self-bootstraps `.venv`, so one durable launch is sufficient even on a fresh CI job (proven again this session: launch → bootstrap → ALIVE).
8. **False liveness from `pgrep` self-matches:** status scripts require a real Python campaign process; never "fix" a probe by killing a process.
9. **Queue-dryness ambiguity:** C26–C32 are built and staged, and the heavy-work contract makes the next action mandatory while any gate is pending.
10. **Successor-missing bottleneck:** `check_queue_readiness.sh` exits 0 — every C25–C32 campaign has prereg + full implementation; no campaign is implementation-missing when its predecessor PASSes.
11. **Idle-escape-hatch bottleneck:** the heavy-work contract removes "queue not ready", "another session owns it", and "just a status check" as valid stop reasons; C26–C32 launches are mandatory on each PASS.
12. **Dead-runner resume bottleneck:** `run_c25_durable.sh` refuses duplicates and bootstraps `.venv`, so a dead runner is recovered by exactly one durable launch, not by repeated probe-only sessions.
13. **Contradictory C27 readiness label (removed 2026-11-25T05:17:30Z):** `check_queue_readiness.sh` still printed `C27 (PREREG ONLY -- no implementation)` in its header while simultaneously reporting every C27 artifact `ok`. A future session could read that stale label and stall on a phantom gap. The header and the stale "why this exists" comment now state the gap is CLOSED; the C27 branch is retained only as a regression guard. No prereg or campaign code path was touched.
14. **Unavailable-funding checkpoint metadata bottleneck (removed 2026-11-26T02:36:40Z):** the first C25 funding cells wrote valid `UNAVAILABLE_FUNDING` checkpoints without `prereg_sha256`, so the verifier reported false prereg drift and blocked the queue. The four OKX `cost_taker_funding` checkpoints now carry the actual C25 prereg SHA-256 `b1e22b36d074eed3aa2577edccd744343d1e8673c102257b7890a554504f2b6e`; no prereg, runner code, unavailability flag, or evidence was changed. The verifier is back to `C25 ACCEPTANCE: PENDING` with the runner ALIVE. Step 6 generalizes the metadata-only repair for any successor with the same missing-field signature.
15. **No blocked or inefficient sessions (re-verified 2026-11-26T09:32:53Z):** `background_process list` shows exactly one persistent runner (`bgp_21647048f001N8p0SKkj9juxoP`, status ready) and no duplicate/stale sessions; `ps` shows one campaign process tree (PID 3294 + 4 workers 37502–37505) and one worktree; the single campaign is advancing (`draw_chunks_on_disk=85`, up from 33, workers saturated). No blocked session required intervention. Do not spawn a second runner or a parallel campaign — that would create the duplicate-session bottleneck this entry guards against.
16. **Stale duplicate handoff bottleneck (removed 2026-11-26T07:37:18Z):** `HANDOFF_20261126T063050Z.md` was an obsolete second durable handoff with contradictory state (27 missing cells and a direct-run instruction). It is deleted so `HANDOFF.md` is the only durable source; `AGENT_HANDOFF.md` and `INITIAL_TASK_MESSAGE.md` are timestamped pointers with no campaign state.
17. **Stale duplicate handoff bottleneck (removed 2026-11-26T09:32:53Z):** `HANDOFF_20261126T073940Z.md` was a later-but-still-stale second durable handoff that labeled C25 `IN FLIGHT (BOTTLENECK)` and, at its line 77, instructed a direct `python scripts/run_c25_cost_fidelity_campaign.py --jobs 4 --resume` run. A future session following that line would have launched a SECOND parallel campaign against the already-ALIVE durable runner, creating the exact duplicate-session bottleneck this file guards against. It is deleted; `HANDOFF.md` is again the only durable source. The binding launch path is the durable `background_process start command="bash scripts/run_c25_durable.sh" persistent=true`, never a direct-run shell command.
18. **Fresh CI job dead-runner recovery (re-verified 2026-11-26T15:25:05Z):** this session started on a fresh CI job with no background process and no `.venv` (`next_c25_action.sh` → `ACTION: RESUME_C25`). Exactly one durable resume was executed via `background_process start command="bash scripts/run_c25_durable.sh" persistent=true`; the launcher self-bootstrapped `.venv` and the runner is now ALIVE. The handoff records both the resume and the re-derivation requirement. A future session trusting stale prose (e.g., the previous `RUNNER ALIVE` claim from a different job) would have performed a bounded wait on a dead runner and never progressed. Re-derive state live every session.
19. **No blocked or inefficient sessions (re-verified 2026-11-26T15:41:16Z):** `background_process list` shows exactly one persistent runner (`bgp_218757543001gOUTT2JJIj8mO5`, status running, launcher PID 2783) and no duplicate/stale sessions; `status_c25.sh` shows one campaign process tree (PID 3029 + workers 3038–3041) and one worktree; both probes agree `ACTION: NONE_RUNNER_ALIVE`, `ANCHOR: OK` (16/16 EXACT), `session_gate.py` 21/21 DONE, `check_queue_readiness.sh` exit 0. No blocked session required intervention. Do not spawn a second runner or a parallel campaign — that would create the duplicate-session bottleneck this entry guards against. The next focus campaign (C26 path/per-trade-funding fidelity) is BUILT and gate-held behind C25 PASS, so a future agent can never legitimately avoid heavy work.
20. **No blocked or inefficient sessions (re-verified 2026-11-26T15:45:40Z):** `background_process list` shows exactly one persistent runner (`bgp_218757543001gOUTT2JJIj8mO5`, status running, launcher PID 2783) and no duplicate/stale sessions; `ps` shows one campaign process tree (launcher 2783 → campaign PID 3029 + workers 5986–5989) and `git worktree list` shows exactly one worktree; both probes agree `ACTION: NONE_RUNNER_ALIVE`, `ANCHOR: OK` (16/16 EXACT), `session_gate.py` 21/21 DONE, `check_queue_readiness.sh` exit 0 (`QUEUE READY` for C25..C32). No blocked session required intervention, so no bottleneck removal was needed this session. Do not spawn a second runner or a parallel campaign — that would create the duplicate-session bottleneck this entry guards against. The next focus campaign (C26 path/per-trade-funding fidelity) is BUILT and gate-held behind C25 PASS, so a future agent can never legitimately avoid heavy work.
21. **No blocked or inefficient sessions (re-verified 2026-11-26T17:13:12Z):** `background_process list` shows exactly one persistent runner (`bgp_218757543001gOUTT2JJIj8mO5`, status running, launcher PID 2783) and no duplicate/stale sessions; `ps` shows one campaign process tree (launcher 2783 → campaign PID 3029 + workers 15562–15565, rotated from 5986–5989 as draw chunks completed) and `git worktree list` shows exactly one worktree; both probes agree `ACTION: NONE_RUNNER_ALIVE`, `ANCHOR: OK` (16/16 EXACT), `session_gate.py` 21/21 DONE, `check_queue_readiness.sh` exit 0 (`QUEUE READY` for C25..C32), and `draw_chunks_on_disk` advanced 8 → 15. No blocked session required intervention, so no bottleneck removal was needed this session. Do not spawn a second runner or a parallel campaign — that would create the duplicate-session bottleneck this entry guards against. The next focus campaign (C26 path/per-trade-funding fidelity) is BUILT and gate-held behind C25 PASS, so a future agent can never legitimately avoid heavy work.
22. **No blocked or inefficient sessions (re-verified 2026-11-26T17:14:36Z):** `ps` shows one campaign process tree (launcher 2783 → campaign PID 3029 + workers 16994–16997, rotated from 5986–5989 as draw chunks completed) and `git worktree list` shows exactly one worktree; both probes agree `ACTION: NONE_RUNNER_ALIVE`, `ANCHOR: OK` (16/16 EXACT), `session_gate.py` 21/21 DONE, `check_queue_readiness.sh` exit 0 (`QUEUE READY` for C25..C32), and `draw_chunks_on_disk` advanced 8 → 15. No blocked session required intervention, so no bottleneck removal was needed this session. Do not spawn a second runner or a parallel campaign — that would create the duplicate-session bottleneck this file guards against. The next focus campaign (C26 path/per-trade-funding fidelity) is BUILT and gate-held behind C25 PASS, so a future agent can never legitimately avoid heavy work.
23. **No blocked or inefficient sessions (re-verified 2026-11-26T17:17:37Z):** `ps` shows one campaign process tree (launcher 2783 → campaign PID 3029 + workers 16994–16997) and `git worktree list` shows exactly one worktree; both probes agree `ACTION: NONE_RUNNER_ALIVE`, `ANCHOR: OK` (16/16 EXACT), `session_gate.py` 21/21 DONE, `check_queue_readiness.sh` exit 0 (`QUEUE READY` for C25..C32), and `draw_chunks_on_disk` advanced 8 → 15. No blocked session required intervention, so no bottleneck removal was needed this session. Do not spawn a second runner or a parallel campaign — that would create the duplicate-session bottleneck this entry guards against. The next focus campaign (C26 path/per-trade-funding fidelity) is BUILT and gate-held behind C25 PASS, so a future agent can never legitimately avoid heavy work.

---

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

---

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

---

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
