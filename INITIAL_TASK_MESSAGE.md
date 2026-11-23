# INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (BINDING, 2026-11-23T00:45:24Z)

**Repository:** `CRASH-REBOUND-STRATEGY` — crash-rebound trading strategy research/backtesting on real-market cross-venue data (OKX, Binance UM, MEXC, Bitget USDT-perps). `cross_venue=true`; `is_hyperliquid_venue_data=false`; never relabelled as Hyperliquid evidence.

**SOURCE OF TRUTH:** `HANDOFF.md` is the single durable handoff. This file is the binding initial task message (HANDOFF.md §1). If they disagree, `HANDOFF.md` wins.

**LIVE PRIORITY:** The **C25 round-trip cost & realized-funding fidelity campaign**. The heavy queue `C24 → C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32+` is fully BUILT/STAGED and gate-held; C25 must PASS first. No sessions are blocked, no inefficient sessions, no "no authorized work" condition.

**CURRENT GROUND TRUTH (2026-11-23T00:45:24Z — re-derive via `bash scripts/next_c25_action.sh`):**
- `RUNNER: ALIVE` (supervisor, 4 workers R at ~95–97% CPU; `run_c25_cost_fidelity_campaign.py --jobs 4 --resume`). Worker PIDs respawn per cell; do not record them.
- `GATE: C25 ACCEPTANCE: PENDING` · `C26 ACCEPTANCE: PENDING`
- `ANCHOR: OK` — all 16/16 `cost_base` EXACT vs C24 d15 (okx 28469.71, binance_um 47613.34, mexc 38334.15, bitget 30234.50), no `MISMATCH`, no P0 stop.
- `cost_base 16/16` done (okx/binance_um/mexc/bitget 4/4 each). `cost_taker` 3/16 done: `okx_2023`, `okx_2024`, `okx_2025` cell checkpoints on disk.
- In-flight: `cost_taker_okx_2026` (2026YTD) at **35/40 draw chunks** on disk. `real_cells_remaining=37` (8 permanent okx funding skips `UNAVAILABLE_FUNDING` / `OKX_FUNDING_BLOCKED_BY_API_RETENTION`).
- `PACING: remaining=37 draw_chunks=35 wake_after=8h` (>6 cells left; 4 saturated cores at ~1.6 h/cell). Re-derive ETA with `bash scripts/eta_c25.sh` (`.venv` present); do not hardcode 8 h when the probe says otherwise.
- `scripts/check_queue_readiness.sh` exits 0 — C26–C32 all BUILT/STAGED and gate-held behind C25 PASS.

---

**DO EXACTLY THIS, IN ORDER — DO NOT SKIP, DO NOT REORDER, DO NOT "IMPROVE" IT:**

### 0. GUARANTEE PERSISTENCE
```
goal start
```
**Objective:** *"Drive the crash-rebound heavy-work queue (C24→C25→C26→C27→C28→C29→C30→C31→C32) to completion per HANDOFF.md: monitor C25 with bounded waits, resume-once if the runner dies, launch the mandatory same-session successor on each ACCEPTANCE: PASS, and never idle."*

Then `cancel_wakeup list`; if empty, arm `schedule_wakeup delay=8h` with the monitoring prompt from §4 below. The wakeup is a convenience; the durable runner and git-committed checkpoints are the real persistence. **Do not proceed past step 1 with an empty wakeup list and no active goal.**

### 1. RUN THE SINGLE SOURCE-OF-TRUTH PROBE
```
bash scripts/next_c25_action.sh
```
This read-only probe prints **one `ACTION:` line**, the exact next command, the real remaining-cell count, and a remaining-cells-based wake interval (90 m / 4 h / 8 h). It works with or without `.venv` (counts checkpoints in pure bash) and detects `NOT ALIVE` correctly. **Obey the single `ACTION:` line.** Never trust a PID or log path written in any file; never build your own `ps`/`ls`/log chain.

### 2. IF `ACTION: NONE_RUNNER_ALIVE` (RUNNER HEALTHY, NOTHING TO FIX)
```
bash scripts/check_c25_anchor.sh
```
Must stay `ANCHOR: OK` or `ANCHOR: INCOMPLETE`; `ANCHOR: MISMATCH` is a P0 integrity stop — record evidence, fix the cause, resume once.

Then **exactly one bounded wait** (600 000 ms tool timeout):
```
bash -c 'sleep 540; bash scripts/next_c25_action.sh'
```
Do not loop `sleep` inside one turn. Re-arm the wakeup at the `PACING` interval the probe printed. End the turn.

### 3. IF `ACTION: RESUME_C25` (RUNNER NOT ALIVE, GATE STILL PENDING)
Resume **exactly once**:
```
background_process start command="bash scripts/run_c25_durable.sh" persistent=true
```
`run_c25_durable.sh` bootstraps `.venv` itself when missing (fresh CI job), so this one command is sufficient. Never resume twice for the same failure. Never `nohup`/`setsid` it yourself.

Then re-probe (`bash scripts/next_c25_action.sh` → should print `NONE_RUNNER_ALIVE`), then `check_c25_anchor.sh`, then the one bounded wait, then end the turn.

### 4. ON `C25 ACCEPTANCE: PASS` (SAME SESSION — MANDATORY SUCCESSOR LAUNCH)
Deliver the full arm × venue × fold cost/funding table, per-leg attribution, exit-reason decomposition, BH family, and the consolidated token (`C25_REOPENS_C1_C24` or `C25_NO_GO_ROBUST_TO_COST`). State verbatim `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY` citing `research_state/c25_funding_model_disclosure_20261119T091800Z.json`. Report `okx` as `UNAVAILABLE_FUNDING` / `OKX_FUNDING_BLOCKED_BY_API_RETENTION` — **never zero-fill, proxy, or retry**.

Then durably launch C26-T1:
```
background_process start command="bash scripts/run_c26_durable.sh" persistent=true
```
Verify with `bash scripts/status_c26.sh` and `PYTHONPATH=. .venv/bin/python scripts/verify_c26_focus_campaign.py`.

### 5. ON `C26 ACCEPTANCE: PASS` (SAME SESSION — MANDATORY CHAIN CONTINUES)
C27 is BUILT (direction/venue-parametric, kucoin primary venue per `ACQUISITION_VIABLE_KUCOIN_MULTIYEAR` probe). Verify with `bash scripts/status_c27.sh` + `PYTHONPATH=. .venv/bin/python scripts/verify_c27_focus_campaign.py`. Then durably launch:
```
background_process start command="bash scripts/run_c27_durable.sh" persistent=true
```
The C27 runner hard-refuses unless `research_state/c26_decision_verdict_CONSOLIDATED_20261119T215721Z.json` exists — if you see that refusal, C26 has not PASSed; fix C26 first, do not force. Run `PYTHONPATH=. .venv/bin/python scripts/probe_c27_venue_acquisition.py` to confirm `research_state/c27_prereg_20261119T215721Z.{json,md}` matches the probe verdict.

Then C28 → C29 → C30 → C31 → C32 in the same chain, each gate-held on the prior PASS (see HANDOFF.md §7 for exact launch commands and refusal artifacts). C33 opens only after `C32 ACCEPTANCE: PASS` with a fresh `PRE_REGISTERED_BEFORE_COMPUTE` prereg anchored on real C24–C32 evidence — **never a same-data rerun, never a frozen-signal parameter search**.

---

**MONITORING PROTOCOL (NEVER POLL, NEVER IDLE, NEVER SPIN):**
- Session entry: `goal start` → `bash scripts/next_c25_action.sh` → obey the `ACTION:` line.
- If `RUNNER: ALIVE`: run `check_c25_anchor.sh`; then exactly one bounded wait: `bash -c 'sleep 540; bash scripts/next_c25_action.sh'` with **600 000 ms** tool timeout. Never sleep past the 900 s idle timeout. End the turn.
- If `RUNNER: NOT ALIVE` and gate PENDING: resume once (step 3), re-probe, then one bounded wait, end.
- Pacing tiers come from the probe, never from a constant: 90 m when ≤2 real cells remain, 4 h when ≤6, 8 h otherwise.
- Cell-in-permutation is not a hang. A cell with no cell checkpoint yet shows as `in-flight draw chunks: N/40` in `status_c25.sh`. If the chunk count is unchanged across two consecutive sessions while the runner is ALIVE, it is still a long cell — keep waiting; do not kill.
- One session in four may additionally run `PYTHONPATH=. .venv/bin/python -m pytest -q` (~74 s) to catch wiring rot. Do not run it every session.
- Escalation: if `check_c25_anchor.sh` ever prints `ANCHOR: MISMATCH`, stop the battery, record the evidence, fix the cause, resume once. Never relax floors, never edit the prereg, never force a verdict.

---

**GUARDRAILS (NEVER VIOLATE):**
- No cross-venue relabelling as Hyperliquid-native (`is_hyperliquid_venue_data=false` for C20–C32).
- No synthetic gap-fill as verified; no spec relaxation to manufacture GO; `SPEC_LITERAL_NEXT_OPEN` fixed; C20–C32 configs frozen to their preregs.
- **No funding fabrication:** `okx` funding does not exist beyond a 33-day window (`OKX_FUNDING_BLOCKED_BY_API_RETENTION`) — report `UNAVAILABLE_FUNDING`, never zero-fill, never proxy from another venue, never cache the 1-month tail as multiyear.
- **Funding model honesty:** C25 reports `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY` citing `research_state/c25_funding_model_disclosure_20261119T091800Z.json`; per-trade funding is C26 only.
- **Do not reduce draw counts** (20k/20k/2k/2k floors). **Do not edit a live campaign's prereg or code path.** C28/C29/C30/C31/C32 runners are fixed and frozen.
- **Status first:** `bash scripts/status_c25.sh` (or `next_c25_action.sh`) before any C25 action; the runner's real identity is whatever it prints.
- **Do not kill or duplicate the runner.** Long campaigns must be launched through the background-process tool with `persistent=true`. All durable launchers self-bootstrap `.venv` when missing.
- **No long foreground sleep** past the ~900 s idle timeout: one bounded wait per session, then end.
- No same-data rerun of a closed campaign. Only new data + new prereg + explicit authorization justifies a new campaign.
- Do not edit completed artifacts or `scripts/run_c20_cross_venue_campaign.py`.
- No silent baseline change. C1–C23 `NO_GO` is superseded by C24; it stands until a later pre-registered campaign contradicts it with full evidence.
- **No idle sessions:** the binding queue is `C24 → C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32+`.
- Do not commit unless explicitly asked (the controller checkpoints the worktree; do not rewrite history).
- Preserve literal gate tokens verbatim (see HANDOFF.md §6 for full list).

---

**BOTTLENECKS REMOVED (DO NOT RE-ADD):**
1. State drift across duplicate handoffs — `HANDOFF.md` is the only state-bearing file.
2. File bloat from repetitive session re-stamps — edit `HANDOFF.md` only on material state change via small unique-substring replacements.
3. Stale PID/log state drift — the probe and on-disk checkpoints in `research_state/` are the only truth.
4. Queue-dryness — C25 in flight; C26–C32 built/staged/gate-held: months of runway.
5. Session spin / quota exhaustion — one bounded wait per ALIVE-runner session; no tight relaunch loops.
6. Probe pacing collapsed to `wake_after=0s` without a venv — remaining cells counted from on-disk checkpoints in pure bash.
7. Fresh-job resume required two commands + manual bootstrap — `run_c25_durable.sh` self-bootstraps `.venv`; one-line resume is sufficient.
8. In-flight cell looked like a hang — `status_c25.sh` prints `in-flight draw chunks: N/40 (arm/venue/fold)`.
9. Multi-script gate-reasoning overhead — `scripts/next_c25_action.sh` collapses probes into one read-only `ACTION:` line.
10. C25→C26 transition latency — pacing derives `wake_after` from remaining cells so PASS→launch is detected within ~1.5 h.
11. C28/C29 runner crashes — `_arms_for` now reads `DIRECTION_ARM_CONFIG`; regression tests in place.
12. Background-process launch-arg contract — omit `ready` for durable runners; always pass `command` with `monitor`.

---

**THIS IS THE COMPLETE BINDING INITIAL TASK MESSAGE.** Future agents cannot avoid heavy work: the queue is fully built, gates are explicit, the probe is the single source of truth, and the monitoring protocol enforces progress without idle loops. Read `HANDOFF.md` for the full campaign specifications, gate tokens, and launch chain details.