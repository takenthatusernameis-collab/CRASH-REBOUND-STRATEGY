# INITIAL TASK MESSAGE — NEXT SESSION (2026-11-19T22:24Z — C25 RUNNER ALIVE, 1/56 REAL CELLS DONE, ETA ~2026-11-28, DO NOT RELAUNCH)

**Single durable handoff / source of truth:** `HANDOFF.md`. This file is a pointer only — do not maintain a second source of truth here.

**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication on real-market, cross-venue data (OKX, Binance UM, MEXC, Bitget USDT-perps). Real data, `cross_venue=true`, `is_hyperliquid_venue_data=false`; never Hyperliquid performance evidence. Prioritize the `C24 → C25 → C26 → C27` heavy queue above all else; no session may idle or declare "no authorized work."

**Position:** C1–C20 closed `NO_GO`; C21/C22/C23-T1 complete (`PASS`), consolidated `NO_GO`. **C24-T1 complete — `C24 ACCEPTANCE: PASS`, `C24_REOPENS_C1_C23`** (d15 pooled +144,651.69, CI95 [+117,408.41, +173,074.50], prereg rule met over all 16 cells; C1–C23 `NO_GO` superseded). **C25-T1 in flight** — cost/funding fidelity, `cost_base/okx/2023` done (+34,420.88), 1 of 56 real inference cells, gate `C25 ACCEPTANCE: PENDING`, ETA ~2026-11-28 (±30 %). **C26-T1 built, blocked on C25 PASS.** **C27-T1 staged** (probe + prereg at `research_state/c27_prereg_20261119T215721Z.{json,md}`, NOT launched — launch only after `C26 ACCEPTANCE: PASS`).

**Do exactly this, in order:**

1. `bash scripts/status_c25.sh` then `bash scripts/eta_c25.sh` — these two are the truth. Do not assemble your own `ps`/`ls`/log chain.

2. **Runner ALIVE (current state):** do **not** relaunch, kill, resume, or start any C26 cell.
   - Optionally run `bash scripts/check_c25_anchor.sh` → must eventually print `ANCHOR: OK`. `ANCHOR: MISMATCH` is a P0 integrity stop: record the evidence, stop the battery, fix the cause, resume once. Never relax floors or edit the prereg.
   - Then suspend with `schedule_wakeup` at 6–12 h intervals (each cell takes ~3.6 h on this 4-core box). Do not poll in a loop and do not hold a turn open past the ~900 s idle timeout.

3. **Runner NOT ALIVE and gate PENDING:** fix the failure cause first, then resume exactly once:
   `background_process start command="bash scripts/run_c25_durable.sh" persistent=true` (its duplicate guard no-ops if a runner is already up). Never resume twice for the same failure.

4. **Gate prints `C25 ACCEPTANCE: FAIL`:** fix only the failing integrity condition (prereg drift, anchor mismatch, draw floors, smoke contamination). Never force PASS.

5. **On `C25 ACCEPTANCE: PASS` (do all of this in that same session):**
   a. Deliver the full arm × venue × fold cost/funding table, per-leg attribution, exit-reason decomposition, BH family and the consolidated token (`C25_REOPENS_C1_C24` or `C25_NO_GO_ROBUST_TO_COST`).
   b. State, verbatim, `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY` and cite `research_state/c25_funding_model_disclosure_20261119T091800Z.json`. Never claim per-trade funding (that is C26).
   c. Report `okx` as `UNAVAILABLE_FUNDING` / `OKX_FUNDING_BLOCKED_BY_API_RETENTION`. Never zero-fill, proxy, or retry it.
   d. **Immediately and durably launch C26-T1:** `background_process start command="bash scripts/run_c26_durable.sh" persistent=true`, then verify with `scripts/status_c26.sh` and `scripts/verify_c26_focus_campaign.py`. Do not idle, do not claim "no authorized work", do not do a same-data parameter search.

6. **On `C26 ACCEPTANCE: PASS` (same session):** run `scripts/probe_c27_venue_acquisition.py` (stage-0, returns `ACQUISITION_VIABLE_*` / `*_BLOCKED_BY_API_RETENTION`), then write `c27_prereg_<TS>.{json,md}` with `prereg_status: PRE_REGISTERED_BEFORE_COMPUTE` **before any compute**, then durably launch C27-T1. If no new venue is viable, the only legitimate alternative is a new pre-registered hypothesis on new data — never a same-data rerun or a frozen-signal parameter search.

**No-avoidance rule (binding):** `C24 → C25 → C26 → C27` is the heavy queue. No idling, no "no authorized work", no frozen-signal parameter search, no same-data rerun, no retry of closed acquisitions (`FULL_283D_BLOCKED_BY_API_RETENTION`, `OKX_FUNDING_BLOCKED_BY_API_RETENTION`), no zero-filled funding, no reduced draw counts. A `PENDING` gate is not a blocker: it means the heavy battery must keep running.

**Full binding context — verified state, measured throughput/ETA, arm definitions, decision rules, monitoring protocol and guardrails:** `HANDOFF.md`.
