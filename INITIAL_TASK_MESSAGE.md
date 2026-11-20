# INITIAL TASK MESSAGE — NEXT SESSION (2026-11-20T03:52:56Z — C25 RUNNER ALIVE, 1/56 REAL CELLS, ETA ~2026-11-28T10:02:11Z ±30% — DO NOT RELAUNCH)

**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication on real-market, cross-venue data (OKX, Binance UM, MEXC, Bitget USDT-perps). Real data, `cross_venue=true`, `is_hyperliquid_venue_data=false`, never relabelled as Hyperliquid evidence.

**Current position:** C1–C20 closed `NO_GO`. C21/C22/C23-T1 complete (`PASS`), each consolidated `NO_GO`. **C24-T1 complete: `C24 ACCEPTANCE: PASS`, `C24_REOPENS_C1_C23`** (d15 pooled **+144,651.69**, CI95 [+117,408.41, +173,074.50], prob>0 = 1.0; C1–C23 `NO_GO` superseded). **C25-T1 in flight** (1/56 real cells; 8 okx funding cells are instant `UNAVAILABLE_FUNDING` skips; ETA ~2026-11-28T10:02:11Z ±30%). **C26-T1 built, not launched. C27-T1 probe + prereg staged, not launched.**

**Do exactly this, in order — do not skip, do not reorder, do not "improve" it:**

1. **Run `bash scripts/status_c25.sh` and `bash scripts/eta_c25.sh`.** Those two commands are the truth. Do not assemble your own `ps`/`ls`/log chain. Never trust a PID or log path written in any file; whatever `status_c25.sh` prints is ground truth.

2. **If `RUNNER: ALIVE`:** do not relaunch, do not kill, do not resume, do not start any C26/C27 cell, do not add any CPU work. Do:
   - `bash scripts/check_c25_anchor.sh` → must stay `ANCHOR: OK` / `ANCHOR: INCOMPLETE`. If `ANCHOR: MISMATCH`, that is a P0 integrity stop: record the evidence, stop the battery, fix the cause, resume once. Never relax floors or edit the prereg.
   - then **suspend with `schedule_wakeup` (8 h)** using the exact prompt in the monitoring protocol below. Do not burn turns polling.

3. **If `RUNNER: NOT ALIVE` and the gate is `PENDING`:** fix the failure cause first, then resume **exactly once**:
   `background_process start command="bash scripts/run_c25_durable.sh" persistent=true` (its duplicate guard no-ops if a runner is already up). Never resume twice for the same failure. Never `nohup`/`setsid` it yourself — a runner started inside a turn dies with the turn.

4. **If the gate prints `C25 ACCEPTANCE: FAIL`:** fix only the failing integrity condition (prereg drift, anchor mismatch, draw floors, smoke contamination). Never force PASS.

5. **On `C25 ACCEPTANCE: PASS` (do all of this in that same session, then go to step 6):**
   a. Deliver the full arm × venue × fold cost/funding table, per-leg attribution, exit-reason decomposition, BH family, and the consolidated token (`C25_REOPENS_C1_C24` or `C25_NO_GO_ROBUST_TO_COST`).
   b. State, verbatim, `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY` and cite `research_state/c25_funding_model_disclosure_20261119T091800Z.json`. Never claim per-trade funding (that is C26).
   c. Report `okx` as `UNAVAILABLE_FUNDING` / `OKX_FUNDING_BLOCKED_BY_API_RETENTION`. Never zero-fill, proxy, or retry it.
   d. **Immediately and durably launch C26-T1:** `background_process start command="bash scripts/run_c26_durable.sh" persistent=true`, then verify with `bash scripts/status_c26.sh` and `scripts/verify_c26_focus_campaign.py`. Do not idle, do not claim "no authorized work", do not do a same-data parameter search.

6. **On `C26 ACCEPTANCE: PASS` (same session, mandatory successor):** run the staged stage-0 probe `PYTHONPATH=. .venv/bin/python scripts/probe_c27_venue_acquisition.py`; confirm the prereg `research_state/c27_prereg_20261119T215721Z.{json,md}` (`prereg_status: PRE_REGISTERED_BEFORE_COMPUTE`, sha pinned) still matches the probe verdict; then durably launch the C27 campaign. If the probe returns `ACQUISITION_BLOCKED_BY_API_RETENTION`, the only legitimate alternative is a **new pre-registered hypothesis on new data** — never a same-data rerun or a frozen-signal parameter search.

**No-avoidance rule (binding):** `C24 → C25 → C26 → C27` is the heavy queue. No session may idle, declare "no authorized work", substitute a frozen-signal parameter search, retry closed data acquisitions, zero-fill funding, reduce draw counts, or relaunch a finished campaign (C20/C22/C23/C24 are PASS and closed). A `PENDING` gate is not a blocker: it means the heavy battery must keep running. **C25 is the live focus campaign; C26 is the mandatory same-session successor on C25 PASS; C27 is the mandatory same-session successor on C26 PASS.** "No authorized work" is never a truthful state while any gate in this chain is PENDING.

---
**MONITORING PROTOCOL FOR THE MULTI-DAY RUN (use this, never poll)**

- A session must never hold a turn open for hours, never `sleep` past the ~900 s idle timeout, and never poll in a loop.
- One bounded read (`bash scripts/eta_c25.sh`), then schedule and suspend with exactly:
  `schedule_wakeup delay=8h reason="C25 tick" prompt="Run bash scripts/status_c25.sh and bash scripts/eta_c25.sh. If RUNNER NOT ALIVE and gate PENDING, fix the cause then resume exactly once with background_process start command='bash scripts/run_c25_durable.sh' persistent=true. If the gate is C25 ACCEPTANCE: PASS, execute the C25-PASS checklist and launch C26 in this same session. If check_c25_anchor.sh prints ANCHOR: MISMATCH, stop and record evidence. Otherwise update HANDOFF.md only if state materially changed and schedule the next 8h wakeup."`
- **8 h cadence is correct** at ~3.6 h/cell (≈2 cells per wake). Shorter adds nothing.
- If the checkpoint count is unchanged across **two consecutive 8 h wakes** while the runner is ALIVE, treat it as "cell in permutation" (that stage prints nothing) and keep waiting — do **not** conclude the runner is stuck and do **not** kill it.
- One wake in four should additionally run `PYTHONPATH=. .venv/bin/python -m pytest -q` (74 s) to catch wiring rot. Do not run it every wake; it competes with the 4 cores.