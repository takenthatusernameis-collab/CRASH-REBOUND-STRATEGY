# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-21T10:22:00Z · **Repo:** `CRASH-REBOUND-STRATEGY` · **Session-verified (UTC):** 2026-11-21T10:29:19Z — runner **ALIVE** (canonical `scripts/run_c25_cost_fidelity_campaign.py --jobs 4 --resume`, 4 draw workers, launched 2026-11-21T10:17:12Z through the harness background-process runner with `persistent=true`; log `research_state/c25_run_20261121T101712Z.log`), **8/56 real inference cells complete, 48 remaining**, anchor `INCOMPLETE` (8/16 cost_base checked, no MISMATCH), gate `C25 ACCEPTANCE: PENDING`. — crash-rebound trading-strategy research/backtesting on real-market, cross-venue data (OKX, Binance UM, MEXC, Bitget USDT-perps). Real data; `cross_venue=true`; `is_hyperliquid_venue_data=false`; never relabelled as Hyperliquid evidence. **Live priority:** the C25 round-trip cost & realized-funding fidelity campaign. **Do not substitute unrelated work.** C26 is BUILT; **C27 is prereg + acquisition probe only — its implementation is owed on `C26 ACCEPTANCE: PASS`** (`bash scripts/check_queue_readiness.sh` exits 1 until it exists); C28/C29/C30/C31/C32 are built/staged and gate-held, with C32 (next independent USDT-perp venue replication, direction `c32-a`) gate-held behind C31 — the heavy queue does not terminate at C31.

**This is the single durable handoff AND the binding initial task message.** `INITIAL_TASK_MESSAGE.md` and `AGENT_HANDOFF.md` are pointers only; `README.md` points here. The full ordered task list is embedded in section 1 below — do not go looking for state in a second file. Any session that writes campaign state into a second file recreates the state-drift failure this removes.

**ONE-LINE STATUS (re-verified 2026-11-21T10:29:19Z):** `C25` cost/funding fidelity is **RUNNER ALIVE & COMPUTING**, 8/56 real cells done (cost_base: okx 4/4, binance_um 4/4; mexc 0/4, bitget 0/4; cost_taker / cost_taker_funding / cost_stress 0/16 each), **48 real cells remaining** (8 okx funding arms are permanent `UNAVAILABLE_FUNDING` skips, not compute), 4-core box saturated at ~1.62 h/cell → **ETA ~2026-11-24T15:58:00Z (±30%)**. In-flight cell `cost_base/mexc/2023` is at **34/40 draw chunks** (draws checkpoint every 500 subsets in `research_state/c25_draw_ckpts/`), so in-cell progress is visible and a restart loses at most ~500 draws, never a whole cell. **C26 is BUILT; C27 is prereg + probe only (implementation owed on C26 PASS); C28/C29/C30/C31/C32 are built/staged and gate-held.** **DO NOT RELAUNCH. DO NOT KILL. DO NOT REORDER ARMS. DO NOT START ANY C26/C27/C28/C29/C30/C31/C32 CELL.** Whatever `scripts/status_c25.sh` prints is ground truth — never trust a PID written in this file.

---

## READ THIS FIRST — the 60-second version

```bash
bash scripts/next_c25_action.sh     # ONE read-only probe -> one ACTION line + exact next command
```

Then obey the single `ACTION:` line. That is the whole session loop. Everything below is the
detail you need only when the ACTION line tells you to act, or when you must explain a decision.

| `ACTION:` you get | What it means | What you do |
|---|---|---|
| `NONE_RUNNER_ALIVE` | runner healthy, nothing to fix | integrity checks, one bounded wait (§4), end turn |
| `RESUME_C25` | runner dead, gate still PENDING | resume **exactly once**, then re-probe |
| `P0_STOP_ANCHOR_MISMATCH` | cost anchor broke | record evidence, stop, fix cause, resume once |
| `FIX_C25_INTEGRITY` / `FIX_C26_INTEGRITY` | gate FAIL | fix only the failing condition, never force PASS |
| `LAUNCH_C26` | C25 PASS, C26 not running | launch C26 durably, same session |
| `PROBE_AND_LAUNCH_C27` | C25+C26 PASS | build C27 if `check_queue_readiness.sh` still reports it missing, run the probe, then launch C27 |

**Never** invent a status by reading a PID from this file, a log tail, or a stale wakeup. The probe
and the on-disk checkpoints in `research_state/` are the only truth.

---

## 1. INITIAL TASK MESSAGE — NEXT SESSION (2026-11-21T10:22:00Z)

**Repository priority:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication on real-market,
cross-venue data (OKX, Binance UM, MEXC, Bitget USDT-perps). This repository's live priority is the
C25 cost/funding-fidelity campaign; do not substitute unrelated work. The heavy queue is
`C24 → C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32+`; C32 (next-venue replication, direction
`c32-a`) is BUILT and gate-held behind C31 — **"no authorized work" is never a truthful state while
any gate in this chain is PENDING.**

**Do exactly this, in order — do not skip, do not reorder, do not "improve" it:**

0. **Guarantee this session persists — run `goal start`** with objective: *"Drive the crash-rebound
   heavy-work queue (C24→C25→C26→C27→C28→C29→C30→C31→C32) to completion per HANDOFF.md: monitor C25
   with bounded waits, resume-once if the runner dies, launch the mandatory same-session successor on
   each ACCEPTANCE: PASS, and never idle."* Then run `cancel_wakeup list`; if it is empty, arm
   `schedule_wakeup delay=8h` with the monitoring prompt in §4. **Do not treat the wakeup as the
   persistence mechanism** — the durable runner and the git-committed checkpoints are; see §3. Do not
   proceed past step 1 with an empty wakeup list and no active goal.

1. **Run `bash scripts/next_c25_action.sh`.** This single read-only probe is ground truth: it prints
   one `ACTION:` line, the exact next command, the real remaining-cell count, and a remaining-cells-based
   wake interval (90 m / 4 h / 8 h) so the C25→C26 transition is detected within ~1.5 h of PASS instead
   of idling a full wake. It works **with or without `.venv`** (it counts checkpoints in pure bash) and
   it detects `NOT ALIVE` correctly. Never trust a PID or log path written in any file; never build your
   own `ps`/`ls`/log chain.

2. **If `RUNNER: ALIVE`:** do not relaunch, do not kill, do not resume, do not start any
   C26/C27/C28/C29/C30/C31/C32 cell, do not add CPU work. Run `bash scripts/check_c25_anchor.sh`
   (must stay `ANCHOR: INCOMPLETE` or `ANCHOR: OK`; `ANCHOR: MISMATCH` is a P0 integrity stop — record
   evidence, fix the cause, resume once). Then do **one bounded wait** (§4: `sleep 540` with a 600 000 ms
   tool timeout, then re-probe) so this session maps to compute progress instead of spinning, and end the
   turn. Re-arm the wakeup at the PACING interval the probe printed (never hardcode 8 h when it says 90 m/4 h).

3. **If `RUNNER: NOT ALIVE` and the gate is `PENDING`:** resume **exactly once** with
   `background_process start command="bash scripts/run_c25_durable.sh" persistent=true`.
   `run_c25_durable.sh` now **bootstraps `.venv` itself** when it is missing (fresh CI job), so this one
   command is sufficient on the first session of a new job. Never resume twice for the same failure.
   Never `nohup`/`setsid` it yourself.

4. **If the gate prints `C25 ACCEPTANCE: FAIL`:** fix only the failing integrity condition (prereg drift,
   anchor mismatch, draw floors, smoke contamination). Never force PASS.

5. **On `C25 ACCEPTANCE: PASS` (same session):** deliver the full arm × venue × fold cost/funding table,
   per-leg attribution, exit-reason decomposition, BH family, and the consolidated token
   (`C25_REOPENS_C1_C24` or `C25_NO_GO_ROBUST_TO_COST`). State verbatim
   `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY` citing
   `research_state/c25_funding_model_disclosure_20261119T091800Z.json`. Report `okx` as
   `UNAVAILABLE_FUNDING` / `OKX_FUNDING_BLOCKED_BY_API_RETENTION` — never zero-fill, proxy, or retry.
   Then durably launch C26-T1: `background_process start command="bash scripts/run_c26_durable.sh"
   persistent=true`; verify with `bash scripts/status_c26.sh` and
   `PYTHONPATH=. .venv/bin/python scripts/verify_c26_focus_campaign.py`.

6. **On `C26 ACCEPTANCE: PASS` (same session, mandatory successor):** **C27 has a prereg but NO
   implementation** (`scripts/run_c27_campaign.py`, `run_c27_durable.sh`, `status_c27.sh`,
   `verify_c27_focus_campaign.py`, `tests/test_c27_campaign.py` do not exist). Run
   `bash scripts/check_queue_readiness.sh` to see the machine-readable gap, then **build the C27
   implementation first** (model it on C28: direction/venue-parametric, prereg-frozen arms
   `path_base` / `cost_taker_funding` / `path_intrabar_combined`, folds 2023/2024/2025/2026YTD,
   20k/20k/2k floors, hard-refuse unless the C26 consolidated verdict exists), then run
   `PYTHONPATH=. .venv/bin/python scripts/probe_c27_venue_acquisition.py`, confirm
   `research_state/c27_prereg_20261119T215721Z.{json,md}` (`prereg_status: PRE_REGISTERED_BEFORE_COMPUTE`,
   sha pinned) matches the probe verdict, and only then durably launch C27. If the probe returns
   `ACQUISITION_BLOCKED_BY_API_RETENTION`, record the consolidated C27 verdict with that token and move to
   the new-pre-registered-hypothesis path — never a same-data rerun or frozen-signal parameter search.
   **Do not pretend C27 is launchable: C28–C32 are all gated behind it, so an unbuilt C27 stalls the
   entire heavy queue.**

7. **On `C27 ACCEPTANCE: PASS` (same session, mandatory successor):** C28 is **BUILT** (direction `c28-a`,
   Portfolio-Level Cross-Venue Capital Allocation & Correlation Fidelity; prereg
   `c28_prereg_20261121T013400Z.{json,md}`). Verify with `bash scripts/status_c28.sh --direction c28-a`
   (must show `PRE_REGISTERED_BEFORE_COMPUTE` + `C28 ACCEPTANCE: PENDING`) and
   `PYTHONPATH=. .venv/bin/python scripts/verify_c28_focus_campaign.py --direction c28-a`. Then durably
   launch: `background_process start command="bash scripts/run_c28_durable.sh --direction c28-a" persistent=true`.
   The C28 runner hard-refuses (SystemExit, exit 1) unless
   `research_state/c27_decision_verdict_CONSOLIDATED_20261119T215721Z.json` exists — if you see that
   refusal, C27 has not PASSed; fix C27 first, do not force. **C28 may NOT run any cell until
   `C27 ACCEPTANCE: PASS`.**

8. **On `C28 ACCEPTANCE: PASS` (same session, mandatory successor):** C29 is **STAGED** (direction
   `c29-a`, strict temporal OOS holdout on the newest never-scored window; prereg
   `c29_prereg_20261121T031907Z.{json,md}`). Verify with `bash scripts/status_c29.sh --direction c29-a` +
   `scripts/verify_c29_focus_campaign.py --direction c29-a`. Then durably launch:
   `background_process start command="bash scripts/run_c29_durable.sh --direction c29-a" persistent=true`.
   The C29 runner hard-refuses unless
   `research_state/c28_decision_verdict_CONSOLIDATED_20261121T013400Z.json` exists. **C29 may NOT run
   any cell until `C28 ACCEPTANCE: PASS`.**

9. **On `C29 ACCEPTANCE: PASS` (same session, mandatory successor):** C30 is **BUILT** (direction `c30-a`,
   Execution-Realism Stress: 3× empirical slippage + venue taker commission; prereg
   `c30_prereg_20261121T051754Z.{json,md}`, `PRE_REGISTERED_BEFORE_COMPUTE`, sha-pinned). Verify with
   `bash scripts/status_c30.sh --direction c30-a` (must show `PRE_REGISTERED_BEFORE_COMPUTE` +
   `C30 ACCEPTANCE: PENDING`) and `PYTHONPATH=. .venv/bin/python scripts/verify_c30_focus_campaign.py
   --direction c30-a`. Then durably launch:
   `background_process start command="bash scripts/run_c30_durable.sh --direction c30-a" persistent=true`.
   The C30 runner hard-refuses unless
   `research_state/c29_decision_verdict_CONSOLIDATED_20261121T031907Z.json` exists. **C30 may NOT run
   any cell until `C29 ACCEPTANCE: PASS`.**

10. **On `C30 ACCEPTANCE: PASS` (same session, mandatory successor):** C31 is **BUILT** (direction
    `c31-a`, strict temporal OOS holdout on the newest never-scored window 2026-09-29 → 2026-11-21;
    prereg `c31_prereg_20261121T052233Z.{json,md}`, `PRE_REGISTERED_BEFORE_COMPUTE`, sha-pinned). Verify
    with `bash scripts/status_c31.sh --direction c31-a` (must show `PRE_REGISTERED_BEFORE_COMPUTE` +
    `C31 ACCEPTANCE: PENDING`) and `PYTHONPATH=. .venv/bin/python scripts/verify_c31_focus_campaign.py
    --direction c31-a`. Then durably launch:
    `background_process start command="bash scripts/run_c31_durable.sh --direction c31-a" persistent=true`.
    The C31 runner hard-refuses unless `research_state/c30_decision_verdict_CONSOLIDATED_20261121T051754Z.json`
    exists **and** the per-venue holdout-window archive manifests
    `research_state/cache/<venue>_1h_multiyear_20260929_20261121` are acquired — if you see that refusal,
    C30 has not PASSed or the manifests are missing; fix C30 / acquire manifests first, do not force.
    **C31 may NOT run any cell until `C30 ACCEPTANCE: PASS`.**

11. **On `C31 ACCEPTANCE: PASS` (same session, mandatory successor — the queue never dries out):** C32 is
    **BUILT** (direction `c32-a`, Next Independent USDT-Perp Venue Replication Beyond C27; prereg
    `c32_prereg_20261121T061508Z.{json,md}`, `PRE_REGISTERED_BEFORE_COMPUTE`, sha256
    `b914c314e2b1fa78902fb6f9ac3f05fe0fcc9dd0cb98795838b952d4ae3515d8`). Verify with
    `bash scripts/status_c32.sh --direction c32-a` (must show `PRE_REGISTERED_BEFORE_COMPUTE` +
    `C32 ACCEPTANCE: PENDING`) and `PYTHONPATH=. .venv/bin/python scripts/verify_c32_focus_campaign.py
    --direction c32-a`. Then durably launch:
    `background_process start command="bash scripts/run_c32_durable.sh --direction c32-a" persistent=true`.
    The C32 runner hard-refuses unless `research_state/c31_decision_verdict_CONSOLIDATED_20261121T061508Z.json`
    exists. **C32 may NOT run any cell until `C31 ACCEPTANCE: PASS`.** On `C32 ACCEPTANCE: PASS`, open C33
    with a fresh `PRE_REGISTERED_BEFORE_COMPUTE` prereg anchored on the completed C24–C32 evidence.

**Explicit directions are present (this section). Do not build C33 speculatively.** C33 is legitimate
only after `C32 ACCEPTANCE: PASS`, with a fresh prereg anchored on real C24–C32 evidence — never a
same-data rerun, never a frozen-signal parameter search, never a prereg written before its anchor exists.

**Runner-integrity note (fixed 2026-11-21T05:20:32Z):** the C28 and C29 runners previously crashed before
any cell ran (latent `_arms_for` `KeyError: 'c28-a'/'c29-a'` from resolving arms through the prereg, plus
a `TypeError` from passing the phantom `per_venue_cap_pct` kwarg to `StrategyConfig`). Both are fixed;
`_arms_for` now reads `DIRECTION_ARM_CONFIG`, and `per_venue_cap_pct` is recorded descriptive-only (the
hourly engine enforces `gross_cap_pct`). Regression tests live in `tests/test_c28_campaign.py` /
`tests/test_c29_campaign.py`. If you ever see `KeyError: 'cXX-a'` or a `per_venue_cap_pct` `TypeError`,
the working tree regressed — restore from git and re-run the campaign test subset.

**No-avoidance rule (binding):** `C24 → C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32+` is the heavy queue.
No session may idle, declare "no authorized work", substitute a frozen-signal parameter search, retry
closed data acquisitions, zero-fill funding, reduce draw counts (20k/2k/2k floors), or relaunch a finished
campaign (C20/C22/C23/C24 are PASS and closed). A `PENDING` gate is not a blocker — it means the heavy
battery must keep running.

---

## 2. VERIFIED LIVE STATE — 2026-11-21T10:29:19Z

Re-verify before acting; this block is stale the moment you read it. All read-only, in order:

```bash
bash scripts/next_c25_action.sh              # ONE probe: runner + gate + anchor + remaining + pacing + ACTION
bash scripts/status_c25.sh                   # runner + per-cell + in-flight draw chunks + artifacts + gate
bash scripts/eta_c25.sh                      # progress, per-cell cost, ETA (needs .venv)
bash scripts/check_c25_anchor.sh             # early cost_base vs C24 d15 anchor (needs .venv)
PYTHONPATH=. .venv/bin/python scripts/verify_c25_focus_campaign.py
PYTHONPATH=. .venv/bin/python scripts/verify_c26_focus_campaign.py
bash scripts/status_c28.sh --direction c28-a   # C28 (built; PENDING until C27 PASS)
bash scripts/status_c29.sh --direction c29-a   # C29 (staged; PENDING until C28 PASS)
bash scripts/status_c30.sh --direction c30-a   # C30 (built; PENDING until C29 PASS)
bash scripts/status_c31.sh --direction c31-a   # C31 (built; PENDING until C30 PASS + holdout manifests)
bash scripts/status_c32.sh --direction c32-a   # C32 (built; PENDING until C31 PASS)
```

Observed at verification time (2026-11-21T10:29:19Z):

- **C25 RUNNER: ALIVE.** `scripts/status_c25.sh` prints `RUNNER: ALIVE`; the canonical process is
  `.venv/bin/python scripts/run_c25_cost_fidelity_campaign.py --jobs 4 --resume` with 4 draw workers,
  launched 2026-11-21T10:17:12Z through the harness background-process runner (`persistent=true`), teeing to
  `research_state/c25_run_20261121T101712Z.log`. `.venv` is present (bootstrapped this session, Python 3.12.3,
  numpy 2.5.5 / pandas 3.1.1). **The previous handoff's "PID 3103" belonged to a job that has since ended;
  it is dead. Never trust a written PID — run `status_c25.sh`.**
- **Cells:** `cost_base 8/16` (okx 4/4, binance_um 4/4, mexc 0/4, bitget 0/4), `cost_taker 0/16`,
  `cost_taker_funding 0/16`, `cost_stress 0/16`. **8 real cells DONE, 48 remaining**, 8 okx funding skips
  (`UNAVAILABLE_FUNDING`). In-flight `cost_base/mexc/2023` at **34/40 draw chunks**. Next cells:
  `cost_base/mexc/2023` (in flight), `mexc/2024`, `mexc/2025`, `mexc/2026YTD`.
- **ETA:** `eta_c25.sh` → 48 real cells left, median 1.44 h/cell → **77.6 h ≈ 2026-11-24T15:58:00Z (±30%)**.
  In-flight-aware conservative estimate is higher; the in-flight cell is healthy (chunks advancing), so
  **do NOT kill**. The 4-core box is saturated; no mid-run acceleration, restart, or extra CPU work is
  permitted while the runner is alive.
- **Anchor:** `ANCHOR: INCOMPLETE` (8/16 cost_base cells; okx EXACT 28,469.71, binance_um EXACT 47,613.34,
  mexc/bitget INCOMPLETE — **no MISMATCH**). `ANCHOR: MISMATCH` would be a P0 integrity stop.
- **Gates:** `C25 ACCEPTANCE: PENDING`. `C26 ACCEPTANCE: PENDING` (blocked on C25).
  `C28 ACCEPTANCE: PENDING` (blocked on C27; runner hard-refuses until
  `c27_decision_verdict_CONSOLIDATED_20261119T215721Z.json` exists). `C29 ACCEPTANCE: PENDING` (blocked on
  C28; 32 cells; runner hard-refuses until `c28_decision_verdict_CONSOLIDATED_20261121T013400Z.json`
  exists). `C30 ACCEPTANCE: PENDING` (blocked on C29; 32 cells; runner hard-refuses until
  `c29_decision_verdict_CONSOLIDATED_20261121T031907Z.json` exists). `C31 ACCEPTANCE: PENDING` (blocked on
  C30; 32 cells + 4 holdout-window manifests; runner hard-refuses until
  `c30_decision_verdict_CONSOLIDATED_20261121T051754Z.json` exists and
  `research_state/cache/<venue>_1h_multiyear_20260929_20261121` per venue are acquired).
  `C32 ACCEPTANCE: PENDING` (blocked on C31; runner hard-refuses until
  `c31_decision_verdict_CONSOLIDATED_20261121T061508Z.json` exists).
- **Tests:** campaign subset
  `tests/test_c28_campaign.py tests/test_c29_campaign.py tests/test_c30_campaign.py tests/test_c31_campaign.py tests/test_c32_campaign.py`
  → campaign tests pass (last green 2026-11-21T06:24Z). Full `pytest -q` last green 2026-11-20T17:37:22Z →
  1100 passed, 1 skipped; do not re-run every session (competes with the 4 cores).
- **C24:** `C24 ACCEPTANCE: PASS`, consolidated `C24_REOPENS_C1_C23`, all 80 cells done, runner exited,
  6 verdict artifacts present. **Do not relaunch.**
- `.venv` is bootstrapped at repo root (Python 3.12.3). Use `PYTHONPATH=. .venv/bin/python ...`.
  `scripts/bootstrap_env.sh` is idempotent and takes <1 min on a warm image; `run_c25_durable.sh` calls it
  automatically when `.venv/bin/python` is missing.

---

## 3. PERSISTENCE MODEL — corrected 2026-11-21T10:22:00Z (read before trusting any runner)

The previous handoff claimed the `background_process ... persistent=true` runner was "the only durable
mechanism". That is **half wrong**, and the wrong half caused a stalled job:

1. **A runner is job-scoped, not machine-scoped.** The controller (`.github/workflows/main.yml`) starts one
   GitHub Actions job with a **355-minute cutoff** (`timeout-minutes: 360`). Inside that job it runs up to
   1000 sequential `kilo` sessions (900 s idle timeout each). A `persistent=true` runner survives session
   boundaries **inside that job only**. When the job ends, the container is destroyed and the runner dies.
2. **A new job is a fresh container:** fresh checkout, **no `.venv`** (it is gitignored), **no runner**. The
   first session of every job must therefore bootstrap the venv and resume the runner once. This is normal,
   not a failure — do not "fix" it, do not treat it as a crash, do not skip the resume.
3. **The real cross-job durability is git.** The controller commits the worktree after each session
   (`chore(kilo): checkpoint agent session`) and pushes it. The runner's checkpoints live in
   `research_state/` (`c25_ckpt_*` per completed cell, `c25_draw_ckpts/c25_partial_perm_*_chunkNNNNN.json`
   every 500 draws) and are committed, so a dead runner costs at most the uncommitted tail of one chunk.
   Verify with `git log --oneline -5` — if the newest checkpoint commit is old, the previous sessions did
   not persist and you must resume before anything else.
4. **`schedule_wakeup` is session-scoped and routinely lost** when the 900 s idle watchdog kills the process
   before it fires. Arm it as a convenience (step 0), never as the source of truth. The controller's
   sequential sessions are the actual loop: a session that ends is followed by another session with the
   same prompt.
5. **Do not spin sessions.** If the runner is ALIVE and nothing needs fixing, do **one bounded wait** (§4)
   and end. Ending instantly in a tight loop burns the model quota and produces the upstream rate-limit
   failures ("Sign up for free to continue", HTTP 429) that have already killed controller loops in this
   repository's diagnostics ledger.

---

## 4. MONITORING PROTOCOL (never poll, never idle, never spin)

- **Session entry:** `goal start` → `bash scripts/next_c25_action.sh` → obey the `ACTION:` line.
- **If `RUNNER: ALIVE`:** run `check_c25_anchor.sh`; then do exactly one bounded wait:
  `bash -c 'sleep 540; bash scripts/next_c25_action.sh'` with a **600 000 ms** tool timeout. Never sleep past
  the 900 s idle timeout. Then end the turn. Do not loop `sleep` inside one turn.
- **If `RUNNER: NOT ALIVE` and gate PENDING:** resume once, re-probe, then one bounded wait, then end.
- **Pacing tiers come from the probe, never from a constant:** 90 m when ≤2 real cells remain, 4 h when ≤6,
  8 h otherwise. The probe prints `PACING:` with the exact `wake_after`.
- **Cell-in-permutation is not a hang.** A cell that has no cell checkpoint yet shows up as
  `in-flight draw chunks: N/40` in `status_c25.sh`. If the chunk count is unchanged across two consecutive
  sessions while the runner is ALIVE, it is still a long cell — keep waiting; do **not** kill.
- **One session in four** may additionally run `PYTHONPATH=. .venv/bin/python -m pytest -q` (~74 s) to catch
  wiring rot. Do not run it every session (it competes for the 4 cores).
- **Escalation:** if `check_c25_anchor.sh` ever prints `ANCHOR: MISMATCH`, stop the battery, record the
  evidence, fix the cause, resume once. Never relax floors, never edit the prereg, never force a verdict.

---

## 5. BOTTLENECK REGISTER (what is removed, what remains, what is forbidden)

Removed already (do not re-add):

1. **State drift across duplicate handoffs — removed 2026-11-19T22:40Z.** `HANDOFF.md` is the only
   state-bearing file; `AGENT_HANDOFF.md` and `INITIAL_TASK_MESSAGE.md` are pointers.
2. **Multi-day monitoring blindness — removed.** `scripts/eta_c25.sh` self-calibrates from completed
   checkpoints; `status_c25.sh` now also prints in-flight draw-chunk progress.
3. **Late anchor detection — removed.** `scripts/check_c25_anchor.sh` compares every `cost_base` cell and
   venue total against C24 d15 the moment a checkpoint lands.
4. **Same-session C25→C26 transition — hard-coded in step 5.** No idle gap between PASS and launch.
5. **Queue-dryness — removed.** C26 built, C27 staged, C28 built, C29 staged, C30 built, C31 built, C32
   built (direction `c32-a`, gate-held behind C31).
6. **Stale PID/log state drift — removed.** The VERIFIED LIVE STATE block reads one verified state; the
   handoff now states explicitly that the previous PID was dead.
7. **`INITIAL_TASK_MESSAGE.md` carried duplicate state — removed 2026-11-20T01:53:10Z.** Pointer-only.
8. **Handoff bloat from repetitive session logs — removed.** One clean handoff: header, task message,
   verified state, persistence model, protocol, bottleneck register, guardrails, campaign record.
9. **Handoff vs repository drift on C28 — removed.** C28 is recorded as BUILT + gate-held with exact
   artifacts, arms, tokens, launch command.
10. **C28 gate documented but not enforced — removed.** `scripts/run_c28_campaign.py` raises `SystemExit`
    (exit 1) unless `research_state/c27_decision_verdict_CONSOLIDATED_20261119T215721Z.json` exists.
11. **C28/C29 runners crashed before any cell ran — removed 2026-11-21T05:20:32Z.** Arm-resolution
    `KeyError` and the phantom `per_venue_cap_pct` kwarg; fixed with `DIRECTION_ARM_CONFIG` and
    descriptive-only `per_venue_cap_pct`; regression tests added.
12. **C30 next focus campaign absent — removed 2026-11-21T05:20:32Z.** C30 BUILT (direction `c30-a`,
    Execution-Realism Stress), gate-held behind C29.
13. **Recurring empty wakeup at session start — root cause addressed 2026-11-21T05:20:32Z.** Wakeups are
    session-scoped; the durable mechanism is the runner + git checkpoints (§3).
14. **C31 next focus campaign built 2026-11-21T05:22:33Z.** Direction `c31-a`, strict temporal OOS holdout
    on 2026-09-29 → 2026-11-21, gate-held behind C30 + per-venue holdout manifests.
15. **C32 next focus campaign built 2026-11-21T06:15:08Z.** Direction `c32-a`, next independent USDT-perp
    venue replication beyond C27, gate-held behind C31. C33 opens only on `C32 ACCEPTANCE: PASS`.
16. **Multi-script gate-reasoning overhead — removed 2026-11-21T08:26:16Z.** `scripts/next_c25_action.sh`
    collapses the probes into one read-only `ACTION:` line.
17. **C25→C26 transition latency (up to a full 8 h wake) — removed 2026-11-21T08:26:16Z.** Pacing derives
    `wake_after` from remaining cells (90 m / 4 h / 8 h).
18. **Session-scoped wakeup loss — documented 2026-11-21T08:26:16Z.** The controller's 900 s idle watchdog
    kills sessions; the runner and the git checkpoints are the persistence.
19. **Queue-dryness re-checked 2026-11-21T08:26:16Z — not triggered.** C25 in flight (48 cells) and C26–C32
    built/staged/gate-held: months of runway. Explicit directions are present, so no speculative C33.
20. **`next_c25_action.sh` reported `NONE_RUNNER_ALIVE` for a DEAD runner — removed 2026-11-21T10:22:00Z
    (THIS SESSION).** The probe matched the substring `*ALIVE*`, and the status line `RUNNER: NOT ALIVE`
    contains `ALIVE`, so every fresh session that found a dead runner was told to do nothing. That is a
    **queue-stalling** bug: the heavy battery could not resume after any job boundary. Fixed: dead-runner
    detection runs first and matches the explicit `NOT ALIVE` token; the probe now prints
    `ACTION: RESUME_C25` when the runner is dead.
21. **Probe pacing collapsed to `wake_after=0s` without a venv — removed 2026-11-21T10:22:00Z
    (THIS SESSION).** The probe derived `remaining` from `eta_c25.sh`, which exits 1 when `.venv` is
    missing (true on the first session of every fresh job). It then defaulted `remaining=0` → "no real cells
    left; act in this turn", hiding a 48-cell backlog and pushing the session into a false "work is done"
    state. Fixed: remaining cells are counted from on-disk checkpoints in pure bash, so pacing and the
    resume decision work with or without a venv.
22. **Fresh-job resume required two commands and a manual bootstrap — removed 2026-11-21T10:22:00Z
    (THIS SESSION).** `run_c25_durable.sh` exited 1 when `.venv/bin/python` was missing, so the documented
    one-line resume failed on the first session of every job. Fixed: the launcher now runs
    `scripts/bootstrap_env.sh` itself and then starts the campaign.
23. **In-flight cell looked like a hang — removed 2026-11-21T10:22:00Z (THIS SESSION).** `status_c25.sh`
    only counted completed cell checkpoints, so a healthy runner on a long permutation cell read as
    `0/16 cells` for hours. It now prints `in-flight draw chunks: N/40 (arm/venue/fold)` from
    `research_state/c25_draw_ckpts/`; the probe prints the same. A session can no longer mistake progress
    for a hang and kill a healthy runner.
24. **Session spin / quota exhaustion — removed 2026-11-21T10:22:00Z (THIS SESSION).** Sessions that find
    the runner ALIVE and nothing to fix previously ended immediately; the controller then launched another
    session, and another, burning the model quota until upstream 429s killed the loop. The protocol now
    requires exactly one bounded wait (`sleep 540`, 600 s tool timeout) per such session, so sessions map
    to compute progress instead of spinning.
25. **C27 was prereg-only while C28–C32 are gated behind it — found 2026-11-21T10:22:00Z (THIS SESSION).**
    `research_state/c27_prereg_20261119T215721Z.{json,md}` exists and names `verify_c27_focus_campaign.py`
    as a required artifact, but no C27 runner/status/verifier/tests exist. A session reaching `C26
    ACCEPTANCE: PASS` would be instructed to "durably launch C27" and would stall with no campaign to run,
    blocking C28–C32 for the rest of the queue. The gap is now machine-detected by
    `scripts/check_queue_readiness.sh` (exit 1 until C27 has a full implementation) and step 6 requires
    building C27 before launching it.
26. **Queue-readiness was invisible — removed 2026-11-21T10:22:00Z (THIS SESSION).**
    `scripts/check_queue_readiness.sh` audits prereg + runner + durable launcher + status + verifier +
    tests for every campaign C25–C32 in one read-only command, so a missing successor is found before its
    predecessor gate PASSes rather than after. Run it at the start of any session that is asked to launch a
    successor.
27. **Every successor launcher exited 1 on a fresh job — removed 2026-11-21T10:30:00Z (THIS SESSION).**
    `run_c26/c28/c29/c30/c31/c32_durable.sh` all had the same `missing venv -> exit 1` guard that C25 had,
    so the first session after any job boundary could not launch the successor with the documented one-line
    command. All six now run `scripts/bootstrap_env.sh` themselves and then start, exactly like
    `run_c25_durable.sh`. A job boundary no longer blocks a PASS→launch transition.

Remaining bottleneck — **compute, and it is not fixable mid-run**:

- 20k conditional-permutation portfolio replays per cell cost **~1.44 h** + 2k placebo **~0.18 h** =
  **~1.62 h/cell** on 4 saturated cores; **48 cells left** → `eta_c25.sh` self-calibrates to **77.6 h
  (~2026-11-24T15:58:00Z ±30%)**.
- The live process has already imported the engine, so editing `src/backtest/engine.py`,
  `scripts/run_portfolio.py`, or `scripts/run_c20_cross_venue_campaign.py` **cannot** speed it up; a restart
  would gamble the campaign.
- Draw floors (20k/20k/2k/2k) are prereg-bound and **must not be reduced**. Running C25 and C26
  concurrently is forbidden (sequential adjudication chain) and would only split 4 cores.
- Any acceleration is a **separate, pre-registered, anchor-verified campaign after C25/C26** — never a
  mid-run edit, restart, or "quick fix".

---

## 6. GUARDRAILS (never violate)

- No cross-venue relabelling as Hyperliquid-native (`is_hyperliquid_venue_data=false` for C20–C32).
- No synthetic gap-fill as verified; no spec relaxation to manufacture GO; `SPEC_LITERAL_NEXT_OPEN` fixed;
  C20–C32 configs frozen to their preregs.
- **No funding fabrication:** `okx` funding does not exist beyond a 33-day window
  (`OKX_FUNDING_BLOCKED_BY_API_RETENTION`) — report `UNAVAILABLE_FUNDING`, never zero-fill, never proxy from
  another venue, never cache the 1-month tail as multiyear.
- **Funding model honesty:** C25 reports `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY` and cites
  `research_state/c25_funding_model_disclosure_20261119T091800Z.json`; per-trade funding is C26 only.
- **Do not reduce draw counts** (20k/20k/2k/2k floors). **Do not edit a live campaign's prereg or code
  path.** The C28/C29/C30/C31/C32 runners are fixed and frozen — do not reintroduce the
  `prereg["arms"][direction]["arms"]` arm lookup or the `per_venue_cap_pct` kwarg.
- **Status first:** `bash scripts/status_c25.sh` (or `next_c25_action.sh`) before any C25 action; the
  runner's real identity is whatever it prints.
- **Do not kill or duplicate the runner.** Long campaigns must be launched through the harness
  background-process tool with `persistent=true`. `run_c25_durable.sh` refuses to start a duplicate.
  All durable launchers (`run_c25/c26/c28/c29/c30/c31/c32_durable.sh`) self-bootstrap `.venv` when it is
  missing, so a fresh job needs no manual bootstrap step.
- **No long foreground sleep** past the ~900 s idle timeout: one bounded wait per session, then end.
- No same-data rerun of a closed campaign. Only new data + new prereg + explicit authorization justifies a
  new campaign.
- Do not edit completed artifacts or `scripts/run_c20_cross_venue_campaign.py`.
- No silent baseline change. C1–C23 `NO_GO` is superseded by C24; it stands until a later pre-registered
  campaign contradicts it with full evidence.
- **No idle sessions:** the binding queue is `C24 → C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32+`.
- Do not commit unless explicitly asked (the controller checkpoints the worktree; do not rewrite history).
- Preserve literal gate tokens verbatim: `C21/C22/C23 ACCEPTANCE: PASS`, `C24 ACCEPTANCE: PASS`,
  `C25 ACCEPTANCE: PENDING|PASS|FAIL`, `C26 ACCEPTANCE: PENDING|PASS|FAIL`,
  `C27 ACCEPTANCE: PENDING|PASS|FAIL`, `C28 ACCEPTANCE: PENDING|PASS|FAIL`,
  `C29 ACCEPTANCE: PENDING|PASS|FAIL`, `C30 ACCEPTANCE: PENDING|PASS|FAIL`,
  `C31 ACCEPTANCE: PENDING|PASS|FAIL`, `C32 ACCEPTANCE: PENDING|PASS|FAIL`,
  `FIDELITY_ANCHOR_REPRODUCED`, `COST_ANCHOR_REPRODUCED`, `PATH_ANCHOR_REPRODUCED`,
  `ALLOC_ANCHOR_REPRODUCED`, `HOLDOUT_ANCHOR_REPRODUCED`, `EXEC_ANCHOR_REPRODUCED`,
  `VENUE_ANCHOR_REPRODUCED`, `C24_REOPENS_C1_C23`, `C25_REOPENS_C1_C24`, `C25_NO_GO_ROBUST_TO_COST`,
  `C26_REOPENS_C1_C25`, `C26_NO_GO_ROBUST_TO_PATH`, `C28_REOPENS_C1_C27`, `C28_NO_GO_ROBUST_TO_AXIS`,
  `C29_REOPENS_C1_C28`, `C29_NO_GO_ROBUST_TO_HOLDOUT`, `C30_REOPENS_C1_C29`,
  `C30_NO_GO_ROBUST_TO_EXECUTION`, `C31_REOPENS_C1_C30`, `C31_NO_GO_ROBUST_TO_HOLDOUT`,
  `C32_REOPENS_C1_C31`, `C32_NO_GO_ROBUST_TO_VENUE`, `C25_UNDERPOWERED`, `C26_UNDERPOWERED`,
  `C29_UNDERPOWERED`, `C30_UNDERPOWERED`, `C32_UNDERPOWERED`, `COST_ANCHOR_MISMATCH`,
  `PATH_ANCHOR_MISMATCH`, `VENUE_ANCHOR_MISMATCH`, `UNAVAILABLE_FUNDING`,
  `OKX_FUNDING_BLOCKED_BY_API_RETENTION`, `FULL_283D_BLOCKED_BY_API_RETENTION`,
  `VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY`, `PRE_REGISTERED_BEFORE_COMPUTE`, and
  `MISMATCH` / `ANCHOR: OK` / `ANCHOR: INCOMPLETE` from `check_c25_anchor.sh`.

---

## 7. CAMPAIGNS

### C25-T1 — ROUND-TRIP COST & REALIZED-FUNDING FIDELITY (IN FLIGHT)

**Prereg (frozen):** `research_state/c25_prereg_20261119T045500Z.{json,md}` —
`prereg_status: PRE_REGISTERED_BEFORE_COMPUTE`, generated `2026-11-19T04:55:00Z`. Do not edit; any drift ⇒
`C25 ACCEPTANCE: FAIL`.
**Question:** the engine charges 5 bps/side slippage, `commission_per_share=0.001` (effectively free),
`commission_min=1.0`, flat `funding_rate_pct_per_hour=0.01`. Real venues charge ~4.5–7 bps/side taker plus
realized 8 h funding. On a 9 %-target, multi-day-hold, short/hedged strategy this is the largest remaining
candidate explanation for the four-venue `NO_GO`.
**Arms (only slippage/commission/funding vary; signal path frozen; liquidation fixed at C24 primary d15 = 15 %):**

| arm | slippage | commission | funding | role |
|---|---|---|---|---|
| `cost_base` | 5 bps | 0.001/share ($1 min) | 0.01 %/h | FIDELITY_ANCHOR |
| `cost_taker` | 5 bps | venue taker bps | 0.01 %/h | descriptive |
| `cost_taker_funding` | 5 bps | venue taker bps | realized venue mean | **PRIMARY** |
| `cost_stress` | 10 bps | venue taker bps | realized + 5 bps borrow | descriptive |

**Anchor rule:** `cost_base` must reproduce C24 d15 per-venue totals within ±1.0 → `COST_ANCHOR_REPRODUCED`,
else `COST_ANCHOR_MISMATCH` → `C25_UNDERPOWERED`.
**Funding inputs (real, never zero-filled):** binance_um 132,577 rows / 32 symbols → 0.0005717 %/h;
mexc 1,568 rows / 8 symbols → 0.0004581 %/h; bitget 3,944 rows / 33 symbols → 0.0007211 %/h. `okx` has
**no** realized funding history → `UNAVAILABLE_FUNDING`; artifact
`research_state/c25_okx_funding_retention_probe_20261119T101402Z.json`. Funding arms run on 3 venues,
satisfying the prereg availability clause.
**Decision rules:** `C25_REOPENS_C1_C24` requires, under `cost_taker_funding`: pooled > 0 AND CI95 lower > 0
AND ≥1 BH survivor in the 16-test venue×fold family AND ≥3/4 folds positive AND ≥3/4 venues positive.
Otherwise `C25_NO_GO_ROBUST_TO_COST`. Gate tokens: `C25 ACCEPTANCE: PENDING|PASS|FAIL`.
**Scripts:** `run_c25_cost_fidelity_campaign.py`, `run_c25_durable.sh` (self-bootstraps), `status_c25.sh`
(now reports in-flight draw chunks), `eta_c25.sh`, `check_c25_anchor.sh`, `verify_c25_focus_campaign.py`,
`build_c25_prereg.py`, `probe_c25_funding_acquisition.py`, `probe_c25_okx_funding_retention.py`,
`fetch_funding_history.py`, `run_c25_okx_funding_durable.sh` (guard only), `tests/test_c25_campaign.py`.
**Status (2026-11-21T10:29:19Z):** 8/56 real cells complete, 48 remaining, ETA **~2026-11-24T15:58:00Z
(±30%)**, anchor `INCOMPLETE` (8/16; okx EXACT 28469.71, binance_um EXACT 47613.34), gate `PENDING`. Runner
healthy; in-flight `cost_base/mexc/2023` at 34/40 draw chunks. One-line decision:
`bash scripts/next_c25_action.sh` → `ACTION: NONE_RUNNER_ALIVE`.

### C26-T1 — INTRABAR PATH & PER-TRADE FUNDING FIDELITY (BUILT, NOT LAUNCHED)

**Status:** BUILT. Prereg `c26_prereg_20261119T121500Z` (`PRE_REGISTERED_BEFORE_COMPUTE`); engine flags
`intrabar_adverse_first` / `per_trade_funding` exist with default `False` (C20–C25 baseline unchanged);
campaign, durable launcher, status, gate, and `tests/test_c26_campaign.py` all present and passing.
**No C26 cell may run until `C25 ACCEPTANCE: PASS`.**
**Why:** C25 applies funding as one venue-mean scalar and prices every fill at next open on 1 h bars. Two
gaps remain, both able to flip the sign: (a) funding per trade/symbol/timestamp instead of a venue mean;
(b) intrabar path — when a 1 h bar touches both stop and target (or liquidation), the within-bar order
decides the exit.
**Arms:** `path_base` (FIDELITY_ANCHOR, must reproduce C25 `cost_taker_funding` within ±1.0 →
`PATH_ANCHOR_REPRODUCED`), `path_funding_trade`, `path_intrabar_adverse_first`, `path_intrabar_combined`
(**PRIMARY**). 4 venues × 4 folds × 20k/20k/2k.
**Tokens:** `C26_REOPENS_C1_C25` / `C26_NO_GO_ROBUST_TO_PATH`; gate `C26 ACCEPTANCE: PENDING|PASS|FAIL`.
**Launch (only after C25 PASS):** `background_process start command="bash scripts/run_c26_durable.sh"
persistent=true`; monitor with `scripts/status_c26.sh` + `scripts/verify_c26_focus_campaign.py`. Budget the
same **~1.6 h/cell, ~3.5 days** (56 real cells, 8 okx funding skips).

### C27-T1 — NEXT INDEPENDENT USDT-PERP VENUE REPLICATION (PREREG + PROBE ONLY — NOT IMPLEMENTED, NOT LAUNCHED)

**Status:** prereg + acquisition probe written; **implementation missing** — `scripts/run_c27_campaign.py`,
`scripts/run_c27_durable.sh`, `scripts/status_c27.sh`, `scripts/verify_c27_focus_campaign.py` and
`tests/test_c27_campaign.py` do **not** exist. `bash scripts/check_queue_readiness.sh` exits 1 until they
do. Build them on `C26 ACCEPTANCE: PASS` (model on C28), then launch. Launch is blocked on
`C26 ACCEPTANCE: PASS` and on the stage-0 probe returning `ACQUISITION_VIABLE_*`.
**Staged artifacts:** `scripts/probe_c27_venue_acquisition.py`;
`research_state/c27_prereg_20261119T215721Z.{json,md}` (`prereg_status: PRE_REGISTERED_BEFORE_COMPUTE`;
Bybit primary candidate, fallback named by the probe; signal path frozen to the spec-literal values
including `liquidation_maint_margin_pct=14.0`, `liquidation_buffer_pct=1.0`, `liquidation_distance_pct=15.0`;
arms `path_base` (FIDELITY_ANCHOR) / `cost_taker_funding` (**PRIMARY**) / `path_intrabar_combined`
(DESCRIPTIVE); 4 folds × 20k/20k/2k).
**Mandate:** after `C26 ACCEPTANCE: PASS` (whatever the token), the same session must build the C27
implementation, run the probe, confirm the prereg matches its `ACQUISITION_VIABLE_*` verdict (or record
`*_BLOCKED_BY_API_RETENTION`), and durably launch the campaign. If no new venue is viable, the only
legitimate alternative is a **new pre-registered hypothesis on new data** — never a same-data rerun or
frozen-signal parameter search.
**Contingency (C27 blocked):** if the probe returns `ACQUISITION_BLOCKED_BY_API_RETENTION`, record the
consolidated C27 verdict artifact with that literal token (do **not** fabricate a PASS), then proceed to the
new-prereg path. C28 does not consume C27 data (its anchor is the C25/C26 primary arm), but its runner's
existence check on the C27 consolidated verdict is what unblocks it — never edit that check to force progress.
**Hyperliquid-native stays CLOSED:** `FULL_283D_BLOCKED_BY_API_RETENTION`.
**C27 is not the end of the queue.** On `C27 ACCEPTANCE: PASS` the same session opens C28 (built), then C29
(staged), then C30 (built), C31 (built), C32 (built). The heavy-work queue does not terminate at C27.

### C28-T1 — PORTFOLIO-LEVEL CROSS-VENUE CAPITAL ALLOCATION & CORRELATION FIDELITY (BUILT, GATE-HELD, NOT LAUNCHED)

**Status:** BUILT. Prereg `research_state/c28_prereg_20261121T013400Z.{json,md}`
(`PRE_REGISTERED_BEFORE_COMPUTE`, direction `c28-a`); `scripts/{build_c28_prereg,run_c28_campaign,
verify_c28_focus_campaign}.py`, `scripts/run_c28_durable.sh`, `scripts/status_c28.sh`,
`tests/test_c28_campaign.py` all present. **Runner fixed this session** (arm resolution + phantom kwarg).
**No C28 cell may run until `C27 ACCEPTANCE: PASS`.** The runner hard-refuses (SystemExit, exit 1) unless
`research_state/c27_decision_verdict_CONSOLIDATED_20261119T215721Z.json` exists.
**Why:** C25/C26 adjudicate cost/funding and intrabar-path fidelity per venue on 4 venues × 4 folds. C28-A
asks the portfolio-level successor question: does the pooled GO survive cross-venue capital constraints and
venue return correlation when all viable venues share a fixed gross budget? Allocation weights vary; signal,
cost, funding, liquidation frozen at C25/C26 primary. (The enforced allocation axis is the pooled
`gross_cap_pct`; per-venue caps are recorded descriptive-only because the hourly engine does not model
per-venue caps.)
**Arms:** `alloc_base` (FIDELITY_ANCHOR, must reproduce prior primary-arm per-venue/per-fold PnL within ±1.0
→ `ALLOC_ANCHOR_REPRODUCED`), `alloc_correlation` (**PRIMARY**). 4 venues × 4 folds × 20k/20k/2k.
**Tokens:** `C28_REOPENS_C1_C27` / `C28_NO_GO_ROBUST_TO_AXIS`; gate `C28 ACCEPTANCE: PENDING|PASS|FAIL`.
**Launch (only after C27 PASS):** `background_process start command="bash scripts/run_c28_durable.sh
--direction c28-a" persistent=true`; monitor with `scripts/status_c28.sh --direction c28-a` +
`scripts/verify_c28_focus_campaign.py --direction c28-a`.

### C29-T1 — STRICT TEMPORAL OUT-OF-SAMPLE HOLDOUT ON THE NEWEST NEVER-SCORED WINDOW (STAGED, NOT LAUNCHED)

**Status:** STAGED. Prereg `research_state/c29_prereg_20261121T031907Z.{json,md}`
(`PRE_REGISTERED_BEFORE_COMPUTE`, direction `c29-a`); `scripts/{build_c29_prereg,run_c29_campaign,
verify_c29_focus_campaign}.py`, `scripts/run_c29_durable.sh`, `scripts/status_c29.sh`,
`tests/test_c29_campaign.py` all present. **Runner fixed this session** (arm resolution + phantom kwarg).
**No C29 cell may run until `C28 ACCEPTANCE: PASS`.** The runner hard-refuses (SystemExit, exit 1) unless
`research_state/c28_decision_verdict_CONSOLIDATED_20261121T013400Z.json` exists.
**Why:** C24–C28 adjudicate margin/liquidation, cost/funding, intrabar path, next-venue replication, and
portfolio-level allocation — all on the same multiyear 2023–2026YTD window. C29 scores a strict temporal
holdout on the newest never-scored window, the most heavily powered candidate by realized evidence.
**Direction `c29-a` (holdout):** signal path frozen at C25/C26 primary; cost/funding/liquidation frozen at
C25 primary; 4 venues × 4 folds × 20k/20k/2k. One fold is held out as the strictest temporal OOS test; the
remaining 3 folds train/anchor.
**Arms:** `holdout_base` (FIDELITY_ANCHOR, must reproduce prior primary-arm per-venue/per-fold PnL within
±1.0 → `HOLDOUT_ANCHOR_REPRODUCED`), `holdout_primary` (**PRIMARY**, strict OOS on the held-out newest
window).
**Tokens:** `C29_REOPENS_C1_C28` / `C29_NO_GO_ROBUST_TO_HOLDOUT`; gate `C29 ACCEPTANCE: PENDING|PASS|FAIL`.
**Launch (only after C28 PASS):** `background_process start command="bash scripts/run_c29_durable.sh
--direction c29-a" persistent=true`; monitor with `scripts/status_c29.sh --direction c29-a` +
`scripts/verify_c29_focus_campaign.py --direction c29-a`. Budget ~1.6 h/cell, ~3.5 days (56 real cells,
8 okx funding skips). C30 is the standing successor on C29 PASS.

### C30-T1 — EXECUTION-REALISM STRESS: SLIPPAGE & TAKER-FEE FIDELITY (BUILT, GATE-HELD, NOT LAUNCHED)

**Status:** BUILT 2026-11-21T05:20:32Z. Prereg `research_state/c30_prereg_20261121T051754Z.{json,md}`
(`prereg_status: PRE_REGISTERED_BEFORE_COMPUTE`, direction `c30-a`, sha256
`8c040333d71ce03a59550dba9d1211c119aac929bd875d331e452148639f7541`);
`scripts/{build_c30_prereg,run_c30_campaign,verify_c30_focus_campaign}.py`,
`scripts/run_c30_durable.sh`, `scripts/status_c30.sh`, `tests/test_c30_campaign.py` all present (campaign
subset 27 passed). **No C30 cell may run until `C29 ACCEPTANCE: PASS`.** The runner hard-refuses (SystemExit,
exit 1) unless `research_state/c29_decision_verdict_CONSOLIDATED_20261121T031907Z.json` exists.
**Why:** C24–C29 adjudicate margin, cost/funding, intrabar path, next-venue replication, portfolio
allocation and a strict temporal holdout — all at 5 bps base slippage. C30 asks whether the edge survives a
harsher execution-realism axis: 3× empirical slippage (15 bps/side) plus full venue taker commission, with
signal/funding/liquidation frozen at C25/C26 primary. This is the honest upper bound on execution friction
the hourly engine can model (order slicing / L2 impact remain documented non-simulated limitations; only
`slippage_pct` — consumed per side at `src/backtest/engine.py:108` — and per-share/min commission vary).
**Arms:** `exec_base` (FIDELITY_ANCHOR: 5 bps slippage, $0.001/share, flat 0.01 %/h funding; must reproduce
the C29 primary-arm per-venue/per-fold PnL within ±1.0 → `EXEC_ANCHOR_REPRODUCED`), `exec_stress`
(**PRIMARY**: 15 bps/side slippage + venue taker bps commission). 4 venues × 4 folds × 20k/20k/2k.
**Tokens:** `C30_REOPENS_C1_C29` / `C30_NO_GO_ROBUST_TO_EXECUTION`; gate
`C30 ACCEPTANCE: PENDING|PASS|FAIL`; `C30_UNDERPOWERED`.
**Launch (only after C29 PASS):** `background_process start command="bash scripts/run_c30_durable.sh
--direction c30-a" persistent=true`; monitor with `scripts/status_c30.sh --direction c30-a` +
`scripts/verify_c30_focus_campaign.py --direction c30-a`. Budget ~1.6 h/cell, ~3.5 days. C31 is the
standing successor on C30 PASS.

### C31-T1 — STRICT TEMPORAL OUT-OF-SAMPLE HOLDOUT ON THE NEWEST NEVER-SCORED WINDOW (BUILT, GATE-HELD, NOT LAUNCHED)

**Status:** BUILT 2026-11-21T05:22:33Z. Prereg `research_state/c31_prereg_20261121T052233Z.{json,md}`
(`prereg_status: PRE_REGISTERED_BEFORE_COMPUTE`, direction `c31-a`, sha256
`04df7a2ca7c02bc79b391a6214254f2212b249a37a772b70d6158e73538ef7b0`);
`scripts/{build_c31_prereg,run_c31_campaign,verify_c31_focus_campaign}.py`,
`scripts/run_c31_durable.sh`, `scripts/status_c31.sh`, `tests/test_c31_campaign.py` all present (campaign
subset 49 passed). **No C31 cell may run until `C30 ACCEPTANCE: PASS`.** The runner hard-refuses (SystemExit,
exit 1) unless `research_state/c30_decision_verdict_CONSOLIDATED_20261121T051754Z.json` exists **and**
per-venue holdout-window archive manifests `research_state/cache/<venue>_1h_multiyear_20260929_20261121`
are acquired.
**Why:** C24–C30 adjudicate margin/liquidation, cost/funding, intrabar path, next-venue replication,
portfolio allocation, execution-realism stress and a strict temporal holdout on the archived multiyear
window (2023–2026YTD, ending 2026-09-28). C31 asks whether the edge survives forward in time on the newest
never-scored real data window (2026-09-29 → 2026-11-21) that no C1-C30 cell has ever scored — the
best-powered candidate by realized evidence for a forward-time generalization test. Signal path, cost and
funding frozen at C25/C26 primary; liquidation fixed at C24 primary d15; draw floors intact.
**Arms:** `holdout_base` (FIDELITY_ANCHOR: C30 primary-arm model re-run on archived folds; must reproduce
C30 primary per-venue/per-fold PnL within ±1.0 → `HOLDOUT_ANCHOR_REPRODUCED`), `holdout_primary`
(**PRIMARY**: strict temporal OOS holdout on 2026-09-29 → 2026-11-21). 4 venues × 4 folds × 20k/20k/2k.
`holdout_primary` cells are recorded `holdout_manifest_missing` until the per-venue archive manifest for
2026-09-29 → 2026-11-21 is acquired (new data; no synthetic data).
**Tokens:** `C31_REOPENS_C1_C30` / `C31_NO_GO_ROBUST_TO_HOLDOUT`; gate `C31 ACCEPTANCE: PENDING|PASS|FAIL`;
`C31_UNDERPOWERED`.
**Launch (only after C30 PASS + holdout manifests acquired):** `background_process start command="bash
scripts/run_c31_durable.sh --direction c31-a" persistent=true`; monitor with `scripts/status_c31.sh
--direction c31-a` + `scripts/verify_c31_focus_campaign.py --direction c31-a`. Budget ~1.6 h/cell,
~3.5 days. C32 is the standing successor on C31 PASS.

### C32-T1 — NEXT INDEPENDENT USDT-PERP VENUE REPLICATION BEYOND C27 (BUILT, GATE-HELD, NOT LAUNCHED)

**Status:** BUILT 2026-11-21T06:15:08Z. Prereg `research_state/c32_prereg_20261121T061508Z.{json,md}`
(`prereg_status: PRE_REGISTERED_BEFORE_COMPUTE`, direction `c32-a`, sha256
`b914c314e2b1fa78902fb6f9ac3f05fe0fcc9dd0cb98795838b952d4ae3515d8`);
`scripts/{build_c32_prereg,run_c32_campaign,verify_c32_focus_campaign}.py`,
`scripts/run_c32_durable.sh`, `scripts/status_c32.sh`, `tests/test_c32_campaign.py` all present.
**No C32 cell may run until `C31 ACCEPTANCE: PASS`.** The runner hard-refuses (SystemExit, exit 1) unless
`research_state/c31_decision_verdict_CONSOLIDATED_20261121T061508Z.json` exists.

**Why:** C24–C31 adjudicate margin/liquidation, cost/funding, intrabar-path, next-venue replication (C27),
portfolio-level allocation, execution-realism stress, forward-time holdout and strict temporal OOS holdout —
all on the same four venues over the archived multiyear window and the newest never-scored forward window.
C32 extends the venue-replication axis to a new independent USDT-perp venue that no C1-C31 cell has ever
scored. A venue-level replication on independent exchange data is the strongest possible external-validity
test — if the edge survives on a venue with a different order book, fee structure and funding mechanism, the
NO_GO conclusion from C1-C31 is genuinely challenged.

**Direction `c32-a` (next_venue_replication):** signal path frozen at C24/C25/C26/C31 sentinel; cost/funding/
liquidation frozen at C25/C26 primary; 4 venues × 4 folds × 20k/20k/2k.

**Arms:** `venue_base` (FIDELITY_ANCHOR: C31 primary-arm model re-run on the archived multiyear folds; must
reproduce the C31 primary-arm per-venue/per-fold PnL within ±1.0 → `VENUE_ANCHOR_REPRODUCED`),
`venue_primary` (**PRIMARY**: next-venue replication on a venue no C1-C31 cell has scored). 4 venues × 4
folds × 20k/20k/2k.

**Tokens:** `C32_REOPENS_C1_C31` / `C32_NO_GO_ROBUST_TO_VENUE`; gate `C32 ACCEPTANCE: PENDING|PASS|FAIL`;
`C32_UNDERPOWERED`.

**Launch (only after C31 PASS):** `background_process start command="bash scripts/run_c32_durable.sh
--direction c32-a" persistent=true`; monitor with `scripts/status_c32.sh --direction c32-a` +
`scripts/verify_c32_focus_campaign.py --direction c32-a`. Budget ~1.6 h/cell, ~3.5 days. C33 is the standing
successor on C32 PASS, with a fresh `PRE_REGISTERED_BEFORE_COMPUTE` prereg anchored on C24–C32 evidence.

---

## 8. CLOSED CAMPAIGN RECORD (history — do not relitigate)

### C24-T1 — MARGIN / LIQUIDATION FIDELITY ADJUDICATION (COMPLETE, CLOSED)

`C24 ACCEPTANCE: PASS`; consolidated `C24_REOPENS_C1_C23`; all 80 cells done; runner exited; 6 verdict
artifacts (`c24_decision_verdict_{base_6,d10,d15,d30,noliq,CONSOLIDATED}_20261119T013154Z.json`); prereg
`c24_prereg_20261119T013154Z` (sha256 `3c0d0b12e139ed2ed264e44964c23639110b2c5a4c0b79ade99ec1f69af30dcb`).
**Do not relaunch.**
Anchor: the 6 % forced-liquidation arm reproduced C20/C22/C23 exactly (okx −54,799.23 | binance_um
−70,071.41 | mexc −49,760.24 | bitget −58,129.33) → `FIDELITY_ANCHOR_REPRODUCED`.
Arm pooled totals: `base_6` −232,760.19 · `d10` −61,002.11 · **`d15` +144,651.69 (PRIMARY)** · `d30`
+417,169.70 · `noliq` +539,745.52.
d15 venue totals: okx 28,469.71 · binance_um 47,613.33 · mexc 38,334.16 · bitget 30,234.49.
d15 per-cell PnL / perm_p / placebo p_ge (20k/20k/2k):
okx 2023 34,420.88 / 0.335 / 0.0675 · okx 2024 −23,054.83 / 0.6149 / 0.923 · okx 2025 5,538.89 / 0.53815 /
0.699 · okx 2026YTD 11,564.77 / 0.5756 / 0.3595 ·
binance_um 2023 38,752.19 / 0.4906 / 0.0635 · 2024 −15,387.90 / 0.71625 / 0.7845 · 2025 18,273.31 / 0.4923 /
0.662 · 2026YTD 5,975.73 / 1.0 / 0.4115 ·
mexc 2023 34,300.42 / 0.06135 / 0.0915 · 2024 −15,455.09 / 0.79765 / 0.7775 · 2025 15,567.16 / 0.4654 /
0.64 · 2026YTD 3,921.67 / 1.0 / 0.4065 ·
bitget 2023 35,797.29 / 0.1283 / 0.047 · 2024 −29,720.46 / 0.6564 / 0.9665 · 2025 21,116.87 / 0.2552 /
0.647 · 2026YTD 3,040.79 / 0.75 / 0.422.
**No d15 cell has perm_p < 0.01; one placebo p_ge = 0.047 (bitget/2023) ≤ 0.05 — watch item, not a verdict.**
The verdict is the prereg rule over all 16 cells, never a partial read.

### Earlier campaigns

- **C21-T1 (`20261117T064408Z`):** `PASS`, consolidated `NO_GO`.
- **C22-T1 — MEXC OOS replication (`20261118T100126Z`):** `PASS`, consolidated `NO_GO`. 2023: 25 trades,
  +30,599.03, perm p=0.01835, placebo p_ge=0.006, CI95 [−4,715.22, +67,959.60]; 2024: 40 trades,
  −27,326.63, perm p=0.3085. A single positive fold is not a result.
- **C23-T1 — Bitget OOS replication (`20261118T202301Z`):** `PASS`, consolidated `NO_GO`. 2023 +28,706.32
  (24 trades, perm_p 0.0229, 0/9 BH) · 2024 −30,939.60 · 2025 −32,710.19 · 2026YTD −23,185.86. Pooled
  **−58,129.33**, prob>0 = 0.0, BH survivors 0/36.
- **C20 cross-venue reference (spec-literal, full multiyear):** OKX 113 trades, −55,057.45; Binance UM 136
  trades, −70,309.57 → pooled `NO_GO`. Use as a sanity check on any new-venue result: a wildly divergent
  sign is a red flag, not a discovery.
- **C1–C21 closed** `NO_GO`; C1–C23 `NO_GO` is **superseded** by C24. C14 native is underpowered
  (7 trades / 3 episodes).
- **Closed data acquisitions:** Hyperliquid-native `FULL_283D_BLOCKED_BY_API_RETENTION`; OKX realized
  funding `OKX_FUNDING_BLOCKED_BY_API_RETENTION`. Do not retry either.

---

## 9. QUICK REFERENCE — PATHS

- Handoff/state: `HANDOFF.md` (single durable handoff), `INITIAL_TASK_MESSAGE.md` + `AGENT_HANDOFF.md`
  (pointers), `README.md`, `research_state/strategy_spec.md`.
- C25 ops: `scripts/next_c25_action.sh` (**single entry probe — run this first**), `scripts/status_c25.sh`
  (includes in-flight draw chunks), `scripts/eta_c25.sh`, `scripts/check_c25_anchor.sh`,
  `scripts/run_c25_durable.sh` (self-bootstraps), `scripts/verify_c25_focus_campaign.py`.
- Queue ops: `scripts/check_queue_readiness.sh` (**read-only C25–C32 artifact audit; exit 1 while C27 is
  unimplemented — run before any successor launch**).
- C25 artifacts: `research_state/c25_prereg_20261119T045500Z.json`,
  `research_state/c25_ckpt_{arm}_{venue}_{fold}_20261119T045500Z.json`,
  `research_state/c25_draw_ckpts/c25_partial_perm_{arm}_{venue}_{fold}_*_chunkNNNNN.json`,
  `research_state/c25_decision_verdict_{arm,CONSOLIDATED}_20261119T045500Z.json`, run log
  `research_state/c25_run_20261121T101712Z.log`.
- C26: `scripts/run_c26_path_fidelity_campaign.py`, `scripts/run_c26_durable.sh`, `scripts/status_c26.sh`,
  `scripts/verify_c26_focus_campaign.py`, `tests/test_c26_campaign.py`,
  `research_state/c26_prereg_20261119T121500Z.{json,md}`.
- C27: `scripts/probe_c27_venue_acquisition.py`, `research_state/c27_prereg_20261119T215721Z.{json,md}`.
- C28 (BUILT, direction c28-a): `scripts/build_c28_prereg.py`, `scripts/run_c28_campaign.py`,
  `scripts/run_c28_durable.sh`, `scripts/status_c28.sh`, `scripts/verify_c28_focus_campaign.py`,
  `tests/test_c28_campaign.py`, `research_state/c28_prereg_20261121T013400Z.{json,md}`.
- C29 (STAGED, direction c29-a): `scripts/build_c29_prereg.py`, `scripts/run_c29_campaign.py`,
  `scripts/run_c29_durable.sh`, `scripts/status_c29.sh`, `scripts/verify_c29_focus_campaign.py`,
  `tests/test_c29_campaign.py`, `research_state/c29_prereg_20261121T031907Z.{json,md}`. Launch only after
  C28 PASS.
- C30 (BUILT, direction c30-a): `scripts/build_c30_prereg.py`, `scripts/run_c30_campaign.py`,
  `scripts/run_c30_durable.sh`, `scripts/status_c30.sh`, `scripts/verify_c30_focus_campaign.py`,
  `tests/test_c30_campaign.py`, `research_state/c30_prereg_20261121T051754Z.{json,md}`. Launch only after
  C29 PASS.
- C31 (BUILT, direction c31-a): `scripts/build_c31_prereg.py`, `scripts/run_c31_campaign.py`,
  `scripts/run_c31_durable.sh`, `scripts/status_c31.sh`, `scripts/verify_c31_focus_campaign.py`,
  `tests/test_c31_campaign.py`, `research_state/c31_prereg_20261121T052233Z.{json,md}`. Requires holdout
  archive manifest `<venue>_1h_multiyear_20260929_20261121` per venue. Launch only after C30 PASS +
  manifests acquired.
- C32 (BUILT, direction c32-a): `scripts/build_c32_prereg.py`, `scripts/run_c32_campaign.py`,
  `scripts/run_c32_durable.sh`, `scripts/status_c32.sh`, `scripts/verify_c32_focus_campaign.py`,
  `tests/test_c32_campaign.py`, `research_state/c32_prereg_20261121T061508Z.{json,md}`. Launch only after
  C31 PASS.